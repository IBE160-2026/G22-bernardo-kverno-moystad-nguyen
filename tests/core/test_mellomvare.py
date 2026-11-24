"""Mellomvaren: rekkefølge, sikkerhetsheadere, CSRF/Origin og avspilling av kroppen.

Krav: AD-5, NFR-12, AR-15, AR-29. Sesjonsoppslaget: AD-4.
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone

import pytest
from fastapi import Depends, FastAPI, Form
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from starlette.requests import Request
from starlette.responses import JSONResponse

from app import lag_app
from app.core import klokke
from app.core.csrf import MAKS_KROPP, CsrfMellomvare
from app.core.db import hent_db
from app.core.feil import FeilMellomvare
from app.core.headere import SIKKERHETSHEADERE, HeaderMellomvare
from app.core.mellomvare import SesjonMellomvare
from app.core.sesjon import Innlogget
from app.identity.models import Bruker, Sesjon
from app.identity.service import IdentityAutentisering

SIKKERHETSHEADERE_TEKST = {n.decode(): v.decode() for n, v in SIKKERHETSHEADERE}
CSRF_FELT_MONSTER = re.compile(r'name="csrf_token" value="([^"]+)"')


def hent_csrf(klient: TestClient) -> str:
    """Henter innloggingssiden, så klienten får CSRF-cookien, og gir nøkkelen fra skjemaet."""
    svar = klient.get("/logg-inn")
    treff = CSRF_FELT_MONSTER.search(svar.text)
    assert treff, "Innloggingssiden mangler csrf_token"
    return treff.group(1)


def antall_brukere(db: Session) -> int:
    return db.scalar(select(func.count()).select_from(Bruker))


@pytest.fixture
def testruter(app: FastAPI) -> FastAPI:
    """Ekko- og skriveruter, registrert bare i testene (aldri i lag_app())."""

    @app.post("/_test/ekko")
    async def ekko(request: Request) -> JSONResponse:
        skjema = await request.form()
        felt = {k: v for k, v in skjema.multi_items() if isinstance(v, str)}
        filer = [k for k, v in skjema.multi_items() if not isinstance(v, str)]
        return JSONResponse({"rute": felt, "filer": filer, "state": request.state.skjema})

    @app.post("/_test/form")
    def form_parameter(navn: str = Form()) -> JSONResponse:
        return JSONResponse({"navn": navn})

    @app.post("/_test/skriv")
    def skriv(db: Session = Depends(hent_db)) -> JSONResponse:
        with db.begin():
            db.add(Bruker(navn="Skrevet av testrute", opprettet=klokke.na()))
        return JSONResponse({"ok": True})

    @app.get("/_test/innlogget")
    def innlogget(request: Request) -> JSONResponse:
        bruker = request.state.innlogget
        return JSONResponse({"bruker_id": bruker.bruker_id if bruker else None})

    return app


# ---------- rekkefølge ----------


def test_rekkefolgen_er_feil_headere_csrf_sesjon(app: FastAPI) -> None:
    """AD-5: feilhåndtering → headere → CSRF/Origin → sesjon → ruter."""
    klasser = [m.cls for m in app.user_middleware]
    assert klasser == [FeilMellomvare, HeaderMellomvare, CsrfMellomvare, SesjonMellomvare]


class TellendeAutentisering:
    def __init__(self) -> None:
        self.kall = 0

    def finn_innlogget(self, request: Request) -> Innlogget | None:
        self.kall += 1
        return None


def test_csrf_avviser_for_sesjonsoppslaget(sesjonsfabrikk) -> None:
    """AD-5: CSRF-sjekken skjer før innloggingen, så en avvist POST når aldri sesjonen."""
    teller = TellendeAutentisering()
    app = lag_app(autentisering=teller)
    app.state.sesjonsfabrikk = sesjonsfabrikk
    with TestClient(app) as klient:
        klient.get("/logg-inn")
        assert teller.kall == 1
        svar = klient.post("/logg-inn", data={"csrf_token": "feil"})
    assert svar.status_code == 403
    assert teller.kall == 1


def test_feilside_fra_csrf_far_headere_fordi_headere_ligger_utenfor(klient: TestClient) -> None:
    svar = klient.post("/logg-inn", data={"epost": "a@b.no"})
    assert svar.status_code == 403
    for navn, verdi in SIKKERHETSHEADERE_TEKST.items():
        assert svar.headers[navn] == verdi


# ---------- headere ----------


@pytest.mark.parametrize("sti", ["/logg-inn", "/finnes-ikke", "/static/css/app.css"])
def test_sikkerhetsheadere_pa_get(klient: TestClient, sti: str) -> None:
    svar = klient.get(sti)
    for navn, verdi in SIKKERHETSHEADERE_TEKST.items():
        assert svar.headers.get(navn) == verdi, f"{navn} mangler på {sti}"


def test_sikkerhetsheadere_pa_405(klient: TestClient) -> None:
    nokkel = hent_csrf(klient)
    svar = klient.post("/logg-inn", data={"csrf_token": nokkel})
    assert svar.status_code == 405
    for navn, verdi in SIKKERHETSHEADERE_TEKST.items():
        assert svar.headers[navn] == verdi


def test_sikkerhetsheadere_finnes_bare_en_gang(klient: TestClient) -> None:
    svar = klient.get("/logg-inn")
    for navn in SIKKERHETSHEADERE_TEKST:
        assert len(svar.headers.get_list(navn)) == 1


# ---------- CSRF ----------


def test_csrf_cookie_er_httponly_og_samesite_lax(klient: TestClient) -> None:
    svar = klient.get("/logg-inn")
    cookie = svar.headers["set-cookie"]
    assert cookie.startswith("csrf=")
    assert "HttpOnly" in cookie
    assert "SameSite=Lax" in cookie
    assert "Secure" not in cookie  # bare i produksjon (AD-14)


def test_csrf_cookie_byttes_ikke_nar_den_finnes(klient: TestClient) -> None:
    forste = hent_csrf(klient)
    andre = klient.get("/logg-inn")
    assert "set-cookie" not in andre.headers
    assert CSRF_FELT_MONSTER.search(andre.text).group(1) == forste


def test_gyldig_post_urlencoded_gir_ruta_feltene(klient: TestClient, testruter) -> None:
    """Kroppen spilles av: ruta får feltene selv om mellomvaren har lest den."""
    nokkel = hent_csrf(klient)
    svar = klient.post("/_test/ekko", data={"csrf_token": nokkel, "navn": "Kari Ås"})
    assert svar.status_code == 200
    assert svar.json()["rute"] == {"csrf_token": nokkel, "navn": "Kari Ås"}
    assert svar.json()["state"]["navn"] == "Kari Ås"


def test_gyldig_post_multipart_gir_ruta_feltene(klient: TestClient, testruter) -> None:
    nokkel = hent_csrf(klient)
    svar = klient.post(
        "/_test/ekko",
        data={"csrf_token": nokkel, "beskrivelse": "Måke snø"},
        files={"vedlegg": ("notat.txt", b"innhold", "text/plain")},
    )
    assert svar.status_code == 200
    assert svar.json()["rute"]["beskrivelse"] == "Måke snø"
    assert svar.json()["filer"] == ["vedlegg"]
    assert svar.json()["state"] == {"csrf_token": nokkel, "beskrivelse": "Måke snø"}


def test_fastapi_form_parameter_virker_etter_avspilling(klient: TestClient, testruter) -> None:
    nokkel = hent_csrf(klient)
    svar = klient.post("/_test/form", data={"csrf_token": nokkel, "navn": "Amir"})
    assert svar.status_code == 200
    assert svar.json() == {"navn": "Amir"}


def test_gyldig_post_med_samme_origin(klient: TestClient, testruter) -> None:
    nokkel = hent_csrf(klient)
    svar = klient.post(
        "/_test/ekko",
        data={"csrf_token": nokkel},
        headers={"Origin": "http://testserver", "Sec-Fetch-Site": "same-origin"},
    )
    assert svar.status_code == 200


@pytest.mark.parametrize(
    "data",
    [
        {},  # manglende nøkkel
        {"csrf_token": ""},
        {"csrf_token": "feil-nokkel"},
    ],
    ids=["mangler", "tom", "feil"],
)
def test_post_med_feil_eller_manglende_nokkel_avvises(
    klient: TestClient, testruter, db: Session, data: dict
) -> None:
    hent_csrf(klient)
    for_ = antall_brukere(db)
    svar = klient.post("/_test/skriv", data={**data, "navn": "x"})
    assert svar.status_code == 403
    assert "Noe gikk galt. Prøv igjen om litt." in svar.text
    assert 'href="' in svar.text  # lenke tilbake
    assert antall_brukere(db) == for_


def test_post_uten_csrf_cookie_avvises(klient: TestClient, testruter, db: Session) -> None:
    nokkel = hent_csrf(klient)
    klient.cookies.clear()
    svar = klient.post("/_test/skriv", data={"csrf_token": nokkel})
    assert svar.status_code == 403
    skrevet = select(func.count()).select_from(Bruker).where(Bruker.navn == "Skrevet av testrute")
    assert db.scalar(skrevet) == 0


def test_post_med_forfalsket_cookie_avvises(klient: TestClient, testruter) -> None:
    nokkel = hent_csrf(klient)
    klient.cookies.set("csrf", "forfalsket.signatur")
    svar = klient.post("/_test/ekko", data={"csrf_token": nokkel})
    assert svar.status_code == 403


def test_post_som_ikke_er_skjema_avvises(klient: TestClient, testruter) -> None:
    hent_csrf(klient)
    svar = klient.post("/_test/ekko", json={"csrf_token": "x"})
    assert svar.status_code == 403


@pytest.mark.parametrize(
    "headere",
    [
        {"Origin": "https://angriper.example"},
        {"Origin": "null"},
        {"Sec-Fetch-Site": "cross-site"},
        {"Sec-Fetch-Site": "same-site"},
    ],
    ids=["fremmed-origin", "null-origin", "cross-site", "same-site"],
)
def test_post_fra_annet_nettsted_avvises_selv_med_riktig_nokkel(
    klient: TestClient, testruter, db: Session, headere: dict
) -> None:
    nokkel = hent_csrf(klient)
    for_ = antall_brukere(db)
    svar = klient.post("/_test/skriv", data={"csrf_token": nokkel}, headers=headere)
    assert svar.status_code == 403
    assert "Noe gikk galt. Prøv igjen om litt." in svar.text
    assert antall_brukere(db) == for_


def test_gyldig_post_til_skriverute_lagrer(klient: TestClient, testruter, db: Session) -> None:
    """Kontroll for testene over: skriveruta lagrer når nøkkelen stemmer."""
    nokkel = hent_csrf(klient)
    for_ = antall_brukere(db)
    svar = klient.post("/_test/skriv", data={"csrf_token": nokkel})
    assert svar.status_code == 200
    assert antall_brukere(db) == for_ + 1


def test_for_stor_kropp_avvises(klient: TestClient, testruter) -> None:
    nokkel = hent_csrf(klient)
    svar = klient.post(
        "/_test/ekko", data={"csrf_token": nokkel, "tekst": "x" * (MAKS_KROPP + 1)}
    )
    assert svar.status_code == 413
    assert "Noe gikk galt. Prøv igjen om litt." in svar.text
    for navn, verdi in SIKKERHETSHEADERE_TEKST.items():
        assert svar.headers[navn] == verdi


# ---------- sesjon ----------


def _lag_sesjon(db: Session, *, utloper: datetime, slettet: bool = False) -> int:
    na = datetime(2026, 11, 24, 12, 0, tzinfo=timezone.utc)
    with db.begin():
        bruker = Bruker(
            navn="Kari",
            postnummer="0571",
            opprettet=na,
            slettet_tidspunkt=na if slettet else None,
        )
        db.add(bruker)
        db.flush()
        db.add(Sesjon(nokkel="testnokkel", bruker_id=bruker.id, opprettet=na, utloper=utloper))
    return bruker.id


def test_sesjonsmellomvaren_setter_innlogget(klient, testruter, db, sett_na) -> None:
    """AD-4: mellomvaren slår opp cookien `sesjon` gjennom Autentisering."""
    sett_na(datetime(2026, 11, 24, 12, 0, tzinfo=timezone.utc))
    bruker_id = _lag_sesjon(db, utloper=datetime(2026, 12, 1, 12, 0, tzinfo=timezone.utc))
    klient.cookies.set("sesjon", "testnokkel")
    assert klient.get("/_test/innlogget").json() == {"bruker_id": bruker_id}


def test_utlopt_sesjon_gir_ingen_innlogget(klient, testruter, db, sett_na) -> None:
    utloper = datetime(2026, 12, 1, 12, 0, tzinfo=timezone.utc)
    _lag_sesjon(db, utloper=utloper)
    sett_na(utloper + timedelta(seconds=1))
    klient.cookies.set("sesjon", "testnokkel")
    assert klient.get("/_test/innlogget").json() == {"bruker_id": None}


def test_slettet_bruker_gir_ingen_innlogget(klient, testruter, db, sett_na) -> None:
    sett_na(datetime(2026, 11, 24, 12, 0, tzinfo=timezone.utc))
    _lag_sesjon(db, utloper=datetime(2026, 12, 1, tzinfo=timezone.utc), slettet=True)
    klient.cookies.set("sesjon", "testnokkel")
    assert klient.get("/_test/innlogget").json() == {"bruker_id": None}


def test_ukjent_eller_manglende_sesjon_gir_ingen_innlogget(klient, testruter) -> None:
    assert klient.get("/_test/innlogget").json() == {"bruker_id": None}
    klient.cookies.set("sesjon", "finnes-ikke")
    assert klient.get("/_test/innlogget").json() == {"bruker_id": None}


def test_identity_implementerer_autentisering() -> None:
    from app.core.sesjon import Autentisering

    assert isinstance(IdentityAutentisering(), Autentisering)
