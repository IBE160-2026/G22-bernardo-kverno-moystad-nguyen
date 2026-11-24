"""Innlogging og utlogging over HTTP: hver rad i I/O-matrisen i spec 1.2 (FR-2, NFR-5).

Også `Set-Cookie` ved innlogging og utlogging, kvitteringen og fokus (UX-DR22, UX-DR27).
"""

from __future__ import annotations

import re
import time
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from itsdangerous import TimestampSigner, URLSafeTimedSerializer
from sqlalchemy import func, select

from app.core.config import Settings
from app.core.kvittering import KVITTERING_COOKIE
from app.identity.models import Innloggingsforsok, Sesjon
from app.identity.service import hash_sesjonsnokkel

from ..conftest import STANDARD_PASSORD
from ..core.test_render import les_side

T0 = datetime(2026, 11, 24, 12, 0, tzinfo=timezone.utc)


@pytest.fixture
def kari(lag_bruker, sett_na):
    sett_na(T0)
    return lag_bruker(navn="Kari Nordmann", epost="kari@eksempel.no")


def csrf(klient: TestClient) -> str:
    """CSRF-nøkkelen fra innloggingssiden, eller fra profilen når klienten er innlogget."""
    html = klient.get("/logg-inn").text
    if 'name="csrf_token"' not in html:
        html = klient.get("/profil").text
    return re.search(r'name="csrf_token" value="([^"]+)"', html).group(1)


def send_innlogging(klient: TestClient, epost: str, passord: str, neste: str | None = None):
    data = {"csrf_token": csrf(klient), "epost": epost, "passord": passord}
    if neste is not None:
        data["neste"] = neste
    return klient.post("/logg-inn", data=data, follow_redirects=False)


def set_cookies(svar, navn: str) -> list[str]:
    return [c for c in svar.headers.get_list("set-cookie") if c.startswith(f"{navn}=")]


def antall_sesjoner(db, bruker_id: int) -> int:
    return db.scalar(select(func.count()).select_from(Sesjon).where(Sesjon.bruker_id == bruker_id))


# ---------- riktig innlogging ----------


def test_riktig_innlogging_med_neste(klient: TestClient, db, kari) -> None:
    """E-post med store bokstaver og mellomrom godtas; 303 til `neste`; ny sesjon i 7 dager."""
    svar = send_innlogging(klient, " Kari@Eksempel.no ", STANDARD_PASSORD, neste="/profil")
    assert svar.status_code == 303
    assert svar.headers["location"] == "/profil"
    (cookie,) = set_cookies(svar, "sesjon")
    nokkel = re.match(r"sesjon=([^;]+)", cookie).group(1)
    for attributt in ("HttpOnly", "SameSite=lax", "Path=/", "Max-Age=604800"):
        assert attributt.lower() in cookie.lower(), attributt
    assert "secure" not in cookie.lower()
    sesjon = db.scalars(select(Sesjon).where(Sesjon.bruker_id == kari.id)).one()
    assert sesjon.nokkel == hash_sesjonsnokkel(nokkel)
    assert sesjon.utloper == T0 + timedelta(days=7)
    # Innlogget etterpå
    assert klient.get("/profil").status_code == 200


def test_riktig_innlogging_rydder_tellerne(klient: TestClient, db, kari) -> None:
    send_innlogging(klient, "kari@eksempel.no", "feil")
    send_innlogging(klient, "kari@eksempel.no", STANDARD_PASSORD)
    antall = db.scalar(select(func.count()).select_from(Innloggingsforsok))
    assert antall == 0


def test_sesjonscookien_er_secure_i_produksjon(sesjonsfabrikk, kari) -> None:
    from app import lag_app

    settings = Settings(
        _env_file=None, app_env="production", secret_key="x" * 32,
        database_url="postgresql+psycopg://u@localhost/d",
    )
    app = lag_app(settings=settings)
    app.state.sesjonsfabrikk = sesjonsfabrikk
    with TestClient(app, base_url="https://testserver") as klient:
        svar = send_innlogging(klient, "kari@eksempel.no", STANDARD_PASSORD)
    (cookie,) = set_cookies(svar, "sesjon")
    assert "secure" in cookie.lower()


@pytest.mark.parametrize("neste", ["//evil.no", "/\\evil.no", "https://evil.no", "", "/logg-ut"])
def test_ugyldig_neste_gir_oversikten(klient: TestClient, kari, neste: str) -> None:
    svar = send_innlogging(klient, "kari@eksempel.no", STANDARD_PASSORD, neste=neste)
    assert svar.status_code == 303
    assert svar.headers["location"] == "/"


def test_neste_fra_303_baeres_gjennom_skjemaet(klient: TestClient, kari) -> None:
    """303 → innloggingssiden med `neste` som skjult felt → tilbake dit etter innlogging."""
    svar = klient.get("/profil/3?x=1", follow_redirects=False)
    side = klient.get(svar.headers["location"])
    assert 'name="neste" value="/profil/3?x=1"' in side.text
    svar = send_innlogging(klient, "kari@eksempel.no", STANDARD_PASSORD, neste="/profil/3?x=1")
    assert svar.headers["location"] == "/profil/3?x=1"


def test_ny_innlogging_med_gyldig_sesjon_sletter_den_gamle(klient, db, kari, logg_inn_som) -> None:
    logg_inn_som(klient, kari)
    assert antall_sesjoner(db, kari.id) == 1
    send_innlogging(klient, "kari@eksempel.no", STANDARD_PASSORD)
    assert antall_sesjoner(db, kari.id) == 1


# ---------- feil e-post eller passord ----------


@pytest.mark.parametrize(
    ("epost", "passord"),
    [("ukjent@eksempel.no", STANDARD_PASSORD), ("kari@eksempel.no", "feil-passord")],
    ids=["ukjent-epost", "feil-passord"],
)
def test_feil_epost_eller_passord(klient: TestClient, kari, epost: str, passord: str) -> None:
    """FR-2: samme melding, e-posten beholdt, passordet tømt, «Feil: » i tittelen."""
    svar = send_innlogging(klient, epost, passord)
    assert svar.status_code == 422
    assert "Feil e-post eller passord." in svar.text
    assert "<title>Feil: Logg inn – Nabolagshelten</title>" in svar.text
    assert f'value="{epost}"' in svar.text
    passordfelt = re.search(r'<input id="passord"[^>]*>', svar.text).group(0)
    assert "value=" not in passordfelt
    assert passord not in svar.text
    assert "Skriv passordet på nytt." in svar.text
    assert set_cookies(svar, "sesjon") == []


def test_feil_gir_fokus_pa_feiloppsummeringen(klient: TestClient, kari) -> None:
    """UX-DR22/UX-DR27: feiloppsummeringen får autofocus, aldri role."""
    html = send_innlogging(klient, "kari@eksempel.no", "feil").text
    assert html.count("autofocus") == 1
    oppsummering = re.search(r'<div class="melding melding--feil"[^>]*>', html).group(0)
    assert 'tabindex="-1"' in oppsummering and "autofocus" in oppsummering
    assert "role=" not in oppsummering
    assert "Skjemaet har 1 feil" in html
    assert '<a href="#epost">Feil e-post eller passord.</a>' in html


def test_feiloppsummeringen_kommer_rett_etter_h1(klient: TestClient, kari) -> None:
    html = send_innlogging(klient, "kari@eksempel.no", "feil").text
    etter_h1 = html.split("</h1>", 1)[1].lstrip()
    assert etter_h1.startswith('<div class="melding melding--feil"')


def test_epost_med_html_vises_som_tekst(klient: TestClient, kari) -> None:
    svar = send_innlogging(klient, '"><script>x</script>', "feil")
    assert "<script>x</script>" not in svar.text
    assert "&lt;script&gt;" in svar.text


# ---------- tomme felt ----------


def test_tomme_felt(klient: TestClient, db, kari) -> None:
    """Feltfeil ved feltene og i oppsummeringen; teller ikke som mislykket forsøk."""
    svar = send_innlogging(klient, "  ", "")
    assert svar.status_code == 422
    html = svar.text
    assert "Skjemaet har 2 feil" in html
    assert '<a href="#epost">Skriv e-postadressen din.</a>' in html
    assert '<a href="#passord">Skriv passordet ditt.</a>' in html
    epostfelt = re.search(r'<input id="epost"[^>]*>', html).group(0)
    assert 'aria-invalid="true"' in epostfelt and 'aria-describedby="epost-feil"' in epostfelt
    assert re.search(r'id="epost-feil">\s*<svg[^>]*>.*?</svg>\s*<span>Skriv e-postadressen din.</span>', html, re.S)
    passordfelt = re.search(r'<input id="passord"[^>]*>', html).group(0)
    assert 'aria-invalid="true"' in passordfelt and 'aria-describedby="passord-feil"' in passordfelt
    assert "<title>Feil: Logg inn – Nabolagshelten</title>" in html
    assert db.scalar(select(func.count()).select_from(Innloggingsforsok)) == 0


def test_tom_epost_med_passord(klient: TestClient, kari) -> None:
    html = send_innlogging(klient, "", "noe").text
    assert "Skjemaet har 1 feil" in html
    assert "Skriv e-postadressen din." in html
    assert "Skriv passordet ditt." not in html


# ---------- sperre ----------


def test_sperre_etter_5_feil_og_innlogging_etter_15_minutter(klient, db, kari, sett_na) -> None:
    """FR-2: 5 mislykkede innen 15 min, så riktig passord gir sperre; etter 15 min går det."""
    for _ in range(5):
        assert send_innlogging(klient, "kari@eksempel.no", "feil").status_code == 422
    svar = send_innlogging(klient, "kari@eksempel.no", STANDARD_PASSORD)
    assert svar.status_code == 422
    assert "For mange mislykkede forsøk. Prøv igjen om 15 minutter." in svar.text
    assert set_cookies(svar, "sesjon") == []
    sett_na(T0 + timedelta(minutes=15, seconds=1))
    svar = send_innlogging(klient, "kari@eksempel.no", STANDARD_PASSORD)
    assert svar.status_code == 303
    assert antall_sesjoner(db, kari.id) == 1


# ---------- utlogging ----------


def test_utlogging(klient: TestClient, db, kari) -> None:
    """FR-2: sesjonsraden slettes, cookien fjernes med samme Path, 303 til innloggingen med kvittering."""
    send_innlogging(klient, "kari@eksempel.no", STANDARD_PASSORD)
    assert antall_sesjoner(db, kari.id) == 1
    svar = klient.post("/logg-ut", data={"csrf_token": csrf(klient)}, follow_redirects=False)
    assert svar.status_code == 303
    assert svar.headers["location"] == "/logg-inn"
    assert svar.headers["cache-control"] == "no-store"
    (cookie,) = set_cookies(svar, "sesjon")
    assert "path=/" in cookie.lower()
    assert "max-age=0" in cookie.lower()
    assert "httponly" in cookie.lower() and "samesite=lax" in cookie.lower()
    assert antall_sesjoner(db, kari.id) == 0
    assert set_cookies(svar, KVITTERING_COOKIE)

    side = klient.get("/logg-inn")
    assert side.status_code == 200
    assert "Du er logget ut." in side.text
    # Kvitteringen vises én gang og slettes i samme svar.
    assert any("max-age=0" in c.lower() for c in set_cookies(side, KVITTERING_COOKIE))
    assert "Du er logget ut." not in klient.get("/logg-inn").text

    # Tilbake til en side med innhold gir innloggingen, ikke innholdet.
    assert klient.get("/profil", follow_redirects=False).status_code == 303


def test_kvittering_etter_utlogging_far_fokus(klient: TestClient, kari, logg_inn_som) -> None:
    """UX-DR22/UX-DR27: kvitteringen rett etter h1, med tabindex="-1" og autofocus."""
    logg_inn_som(klient, kari)
    svar = klient.post("/logg-ut", data={"csrf_token": csrf(klient)})
    assert svar.status_code == 200  # fulgte 303 til /logg-inn
    html = svar.text
    etter_h1 = html.split("</h1>", 1)[1].lstrip()
    assert etter_h1.startswith('<div class="melding melding--kvittering" id="kvittering" tabindex="-1" autofocus>')
    assert html.count("autofocus") == 1
    assert "role=" not in html


def signert_kvittering(app, nokkel: str) -> str:
    return URLSafeTimedSerializer(app.state.settings.secret_key, salt="kvittering").dumps(nokkel)


def test_gyldig_kvittering_vises(app, klient: TestClient) -> None:
    """Kontroll for testene under: en riktig signert, fersk kvittering vises."""
    klient.cookies.set(KVITTERING_COOKIE, signert_kvittering(app, "logget_ut"))
    assert "Du er logget ut." in klient.get("/logg-inn").text


def test_forfalsket_eller_ukjent_kvittering_ignoreres(app, klient: TestClient) -> None:
    klient.cookies.set(KVITTERING_COOKIE, "forfalsket")
    assert "melding--kvittering" not in klient.get("/logg-inn").text
    klient.cookies.set(KVITTERING_COOKIE, signert_kvittering(app, "<b>hei</b>"))
    assert "melding--kvittering" not in klient.get("/logg-inn").text


def test_kvittering_eldre_enn_60_sekunder_ignoreres(app, klient: TestClient, monkeypatch) -> None:
    with monkeypatch.context() as m:
        m.setattr(TimestampSigner, "get_timestamp", lambda self: int(time.time()) - 61)
        gammel = signert_kvittering(app, "logget_ut")
    klient.cookies.set(KVITTERING_COOKIE, gammel)
    assert "melding--kvittering" not in klient.get("/logg-inn").text


def test_gyldig_sesjon_overlever_mislykket_innlogging(klient: TestClient, db, kari, logg_inn_som) -> None:
    """En mislykket innlogging fra en innlogget nettleser logger ikke ut den gamle sesjonen."""
    logg_inn_som(klient, kari)
    svar = send_innlogging(klient, "kari@eksempel.no", "feil-passord")
    assert svar.status_code == 422
    assert set_cookies(svar, "sesjon") == []
    assert antall_sesjoner(db, kari.id) == 1
    assert klient.get("/profil", follow_redirects=False).status_code == 200


# ---------- skjemaet ----------


def test_skjemaet_har_epost_som_fokus_og_vis_passord(klient: TestClient) -> None:
    """UX-DR12/UX-DR13: felttyper, autofocus på E-post, «Vis passord» med aria-pressed."""
    html = klient.get("/logg-inn").text
    epostfelt = re.search(r'<input id="epost"[^>]*>', html).group(0)
    assert "autofocus" in epostfelt
    assert html.count("autofocus") == 1
    knapp = re.search(r"<button[^>]*data-vis-passord[^>]*>([^<]*)</button>", html)
    assert knapp and knapp.group(1) == "Vis passord"
    assert 'aria-pressed="false"' in knapp.group(0) and 'aria-controls="passord"' in knapp.group(0)
    assert 'type="button"' in knapp.group(0)
    assert "hidden" in knapp.group(0)  # vises bare med JS
    assert "/static/js/vis_passord.js" in html and "/static/js/sending.js" in html
    side = les_side(html)
    assert [a.get("name") for t, a in side.tagger if t == "input" and a.get("type") == "hidden"] == [
        "csrf_token",
        "neste",
    ]
    # FR-1: lenken til registrering står nederst, etter skjemaet.
    lenke = re.search(r'<a class="tekstknapp" href="/registrer">([^<]*)</a>', html)
    assert lenke and lenke.group(1) == "Registrer deg"
    assert html.index("</form>") < lenke.start()
