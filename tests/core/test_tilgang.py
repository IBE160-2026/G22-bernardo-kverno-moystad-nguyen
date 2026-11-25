"""Innlogging kreves (FR-3, AD-4, AR-14, AR-17, NFR-5).

FR-3-testen går gjennom alle ruter i `app.routes` uten innlogging og forventer
303 for GET og 401 for andre metoder, unntatt rutene som er merket `offentlig`.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs, urlsplit

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app.core.sesjon import alle_ruter, er_offentlig, offentlig, trygg_neste
from app.identity.models import Sesjon

from .test_mellomvare import hent_csrf

# Story 1.4 la til `/registrer` (FR-1). Story 1.5 la til `/_test/tilstand`, som
# bare finnes når APP_ENV=test, slik testappen kjører (AD-14). Ingen andre ruter
# er offentlige (FR-3).
OFFENTLIGE = {
    ("GET", "/logg-inn"),
    ("POST", "/logg-inn"),
    ("GET", "/registrer"),
    ("POST", "/registrer"),
    ("POST", "/_test/tilstand"),
}


def ruter_som_krever_innlogging(app: FastAPI) -> list[tuple[str, str]]:
    """(metode, sti) for hver rute som ikke er offentlig, med stiparametre fylt med 1."""
    funnet = []
    for rute in alle_ruter(app.routes):
        metoder = getattr(rute, "methods", None)
        if not metoder:
            continue  # Mount for /static
        stimal = rute.path_format
        parametre = {navn: "1" for navn in rute.param_convertors}
        try:
            sti = stimal.format(**parametre)
        except (KeyError, IndexError) as feil:
            pytest.fail(f"Klarte ikke å bygge stien for {stimal}: {feil}")
        assert "{" not in sti, f"Klarte ikke å bygge stien for {stimal}"
        for metode in sorted(metoder):
            if er_offentlig(rute.endpoint):
                assert (metode, sti) in OFFENTLIGE, f"{metode} {sti} er merket offentlig uten å være i lista"
                continue
            funnet.append((metode, sti))
    return funnet


def test_fr3_alle_ruter_krever_innlogging(app: FastAPI, klient: TestClient) -> None:
    """FR-3: alle ruter som ikke er merket offentlige, avvises uten innlogging."""
    ruter = ruter_som_krever_innlogging(app)
    assert len(ruter) >= 5, ruter
    nokkel = hent_csrf(klient)
    for metode, sti in ruter:
        if metode in ("GET", "HEAD"):
            svar = klient.request(metode, sti, follow_redirects=False)
            assert svar.status_code == 303, (metode, sti, svar.status_code)
            assert svar.headers["location"].startswith("/logg-inn?neste="), (metode, sti)
        else:
            svar = klient.request(metode, sti, data={"csrf_token": nokkel}, follow_redirects=False)
            assert svar.status_code == 401, (metode, sti, svar.status_code)
            assert "Du må logge inn igjen." in svar.text


def test_offentlige_ruter_er_bare_innlogging_og_registrering(app: FastAPI) -> None:
    """FR-3: bare innlogging, registrering og testruta (bare i test) er merket offentlige."""
    offentlige = set()
    for rute in alle_ruter(app.routes):
        if getattr(rute, "methods", None) and er_offentlig(rute.endpoint):
            offentlige |= {(m, rute.path_format) for m in rute.methods}
    assert offentlige == OFFENTLIGE


@pytest.mark.parametrize(
    ("sti", "neste"),
    [
        ("/", "/"),
        ("/profil", "/profil"),
        ("/mine-oppdrag", "/mine-oppdrag"),
        ("/profil/3?x=1", "/profil/3?x=1"),
    ],
)
def test_get_uten_innlogging_gir_303_med_neste(klient: TestClient, sti: str, neste: str) -> None:
    """FR-3: 303 til `/logg-inn?neste=<sti med spørrestreng>`, URL-kodet."""
    svar = klient.get(sti, follow_redirects=False)
    assert svar.status_code == 303
    lokasjon = svar.headers["location"]
    deler = urlsplit(lokasjon)
    assert deler.path == "/logg-inn"
    assert parse_qs(deler.query)["neste"] == [neste]
    if "?" in neste:
        assert "neste=/profil/3%3Fx%3D1" in lokasjon


def test_head_uten_innlogging_gir_303(klient: TestClient) -> None:
    svar = klient.head("/profil", follow_redirects=False)
    assert svar.status_code == 303
    assert svar.headers["location"] == "/logg-inn?neste=/profil"


def test_post_med_x_fragment_uten_innlogging_gir_401_fragment(klient: TestClient) -> None:
    nokkel = hent_csrf(klient)
    svar = klient.post(
        "/logg-ut", data={"csrf_token": nokkel}, headers={"X-Fragment": "1"}, follow_redirects=False
    )
    assert svar.status_code == 401
    assert "Du må logge inn igjen." in svar.text
    assert "<html" not in svar.text


def test_post_til_sti_som_bare_har_get_gir_401_uten_innlogging(klient: TestClient) -> None:
    """Match.PARTIAL: stien finnes bare for GET. Uten innlogging gir POST 401, ikke 405."""
    nokkel = hent_csrf(klient)
    svar = klient.post("/", data={"csrf_token": nokkel}, follow_redirects=False)
    assert svar.status_code == 401
    assert "Du må logge inn igjen." in svar.text


def test_ukjent_sti_uten_innlogging_gir_404(klient: TestClient) -> None:
    assert klient.get("/finnes-ikke", follow_redirects=False).status_code == 404


def test_post_uten_innlogging_gir_401_uten_endring(klient: TestClient, db, lag_bruker) -> None:
    """AR-17: 401 «Du må logge inn igjen.» med lenken «Logg inn». Ingen data endres."""
    bruker = lag_bruker(navn="Hemmelig Hansen")
    db.add(
        Sesjon(
            nokkel="x" * 64,
            bruker_id=bruker.id,
            opprettet=datetime.now(timezone.utc),
            utloper=datetime.now(timezone.utc) + timedelta(days=1),
        )
    )
    db.commit()
    nokkel = hent_csrf(klient)
    svar = klient.post("/logg-ut", data={"csrf_token": nokkel}, follow_redirects=False)
    assert svar.status_code == 401
    assert "<h1>Du må logge inn igjen.</h1>" in svar.text
    assert ">Logg inn</a>" in svar.text
    assert "Hemmelig Hansen" not in svar.text
    assert "<nav" not in svar.text
    assert db.scalar(select(func.count()).select_from(Sesjon)) == 1


def test_401_rendres_uten_database(app: FastAPI, klient: TestClient) -> None:
    """AR-17: 401-siden leser ikke databasen."""
    nokkel = hent_csrf(klient)

    def ingen_database():
        raise AssertionError("401-siden skal ikke bruke databasen")

    app.state.sesjonsfabrikk = ingen_database
    svar = klient.post("/logg-ut", data={"csrf_token": nokkel}, follow_redirects=False)
    assert svar.status_code == 401


def test_get_med_x_fragment_gir_401_fragment(klient: TestClient) -> None:
    """AD-4: forespørsler med `X-Fragment` gir 401 med fragmentet, ikke 303."""
    svar = klient.get("/mine-oppdrag", headers={"X-Fragment": "1"}, follow_redirects=False)
    assert svar.status_code == 401
    assert "Du må logge inn igjen." in svar.text
    assert "<html" not in svar.text
    assert 'href="/logg-inn?neste=/mine-oppdrag"' in svar.text


def test_utlopt_sesjon_behandles_som_uten_innlogging(
    klient: TestClient, lag_bruker, logg_inn_som, sett_na
) -> None:
    na = datetime(2026, 11, 24, 12, 0, tzinfo=timezone.utc)
    sett_na(na)
    logg_inn_som(klient, lag_bruker())
    assert klient.get("/", follow_redirects=False).status_code == 200
    sett_na(na + timedelta(days=7))
    assert klient.get("/", follow_redirects=False).status_code == 303


def test_innlogget_bruker_pa_logg_inn_sendes_til_oversikten(
    klient: TestClient, lag_bruker, logg_inn_som
) -> None:
    logg_inn_som(klient, lag_bruker())
    svar = klient.get("/logg-inn", follow_redirects=False)
    assert svar.status_code == 303
    assert svar.headers["location"] == "/"


@pytest.mark.parametrize(
    "sti", ["/logg-inn", "/", "/profil", "/finnes-ikke"]
)
def test_alle_svar_har_no_store(klient: TestClient, sti: str) -> None:
    """FR-2: tilbakeknappen viser ikke innhold etter utlogging."""
    svar = klient.get(sti, follow_redirects=False)
    assert svar.headers["cache-control"] == "no-store"


def test_innloggede_sider_har_no_store(klient: TestClient, lag_bruker, logg_inn_som) -> None:
    logg_inn_som(klient, lag_bruker())
    for sti in ("/", "/mine-oppdrag", "/profil"):
        svar = klient.get(sti)
        assert svar.status_code == 200
        assert svar.headers.get_list("cache-control") == ["no-store"]


def test_feilsider_fra_csrf_og_feilhandteringen_har_no_store(app: FastAPI, klient: TestClient) -> None:
    """FR-2: også 403 fra CSRF-sjekken og 500 fra feilhåndteringen har `no-store`."""
    svar = klient.post("/logg-inn", data={"csrf_token": "feil"})
    assert svar.status_code == 403
    assert svar.headers.get_list("cache-control") == ["no-store"]

    @app.get("/_test/krasj-no-store")
    @offentlig
    def krasj() -> None:
        raise RuntimeError("krasj")

    with TestClient(app, raise_server_exceptions=False) as feilklient:
        svar = feilklient.get("/_test/krasj-no-store")
    assert svar.status_code == 500
    assert svar.headers.get_list("cache-control") == ["no-store"]


def test_statiske_filer_har_ikke_no_store(klient: TestClient) -> None:
    svar = klient.get("/static/css/app.css")
    assert svar.status_code == 200
    assert "no-store" not in svar.headers.get("cache-control", "")


@pytest.mark.parametrize(
    ("verdi", "forventet"),
    [
        ("/profil", "/profil"),
        ("/profil/3?x=1", "/profil/3?x=1"),
        ("/m%C3%A5ke", "/m%C3%A5ke"),
        (None, "/"),
        ("", "/"),
        ("//evil.no", "/"),
        ("/\\evil.no", "/"),
        ("https://evil.no", "/"),
        ("evil.no", "/"),
        ("/\t/evil.no", "/"),
        ("/\r\nSet-Cookie:x", "/"),
        ("/ mellomrom", "/"),
        ("/logg-ut", "/"),
        ("/logg-inn?neste=/profil", "/"),
        ("/logg-inn/", "/"),
        ("/%2F%2Fevil.no", "/"),
        ("/%5Cevil.no", "/"),
        ("/logg%2Dut", "/"),
        ("/" + "a" * 2048, "/"),
        ("/" + "a" * 2047, "/" + "a" * 2047),
    ],
)
def test_trygg_neste(verdi, forventet) -> None:
    """AD-4: bare lokale stier som begynner med én `/`."""
    assert trygg_neste(verdi) == forventet


def test_trygg_neste_avviser_kodet_crlf_etter_dekoding(klient: TestClient) -> None:
    """`/%0d%0aSet-Cookie:x` i spørrestrengen dekodes til CR/LF og avvises."""
    svar = klient.get("/logg-inn?neste=/%0d%0aSet-Cookie:x")
    assert 'name="neste" value="/"' in svar.text
