"""Feilsider: aldri JSON, `detail` eller stack trace (NFR-10, AR-26)."""

from __future__ import annotations

import logging

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.feil import FinnesIkke, IngenTilgang, Konflikt, RegelBrudd
from app.core.sesjon import offentlig
from app.core.headere import SIKKERHETSHEADERE

from .test_mellomvare import hent_csrf

SIKKERHETSHEADERE_TEKST = {n.decode(): v.decode() for n, v in SIKKERHETSHEADERE}


def er_vennlig_html(svar) -> bool:
    return (
        svar.headers["content-type"].startswith("text/html")
        and "detail" not in svar.text
        and "Traceback" not in svar.text
        and '<html lang="nb">' in svar.text
    )


@pytest.fixture
def feilruter(app: FastAPI) -> FastAPI:
    @app.get("/_test/krasj")
    @offentlig
    def krasj() -> None:
        raise RuntimeError("kari@example.no 91234567")  # skal ikke i loggen

    @app.get("/_test/finnes-ikke")
    @offentlig
    def finnes_ikke() -> None:
        raise FinnesIkke

    @app.get("/_test/ingen-tilgang")
    @offentlig
    def ingen_tilgang() -> None:
        raise IngenTilgang

    @app.get("/_test/konflikt")
    @offentlig
    def konflikt() -> None:
        raise Konflikt("Oppdraget er endret. Last siden på nytt.", "/logg-inn")

    @app.get("/_test/tall")
    @offentlig
    def tall(n: int) -> dict:
        return {"n": n}

    return app


def test_ukjent_sti_gir_vennlig_404(klient: TestClient) -> None:
    svar = klient.get("/finnes-ikke")
    assert svar.status_code == 404
    assert er_vennlig_html(svar)
    assert "<title>Fant ikke siden – Nabolagshelten</title>" in svar.text
    assert "<h1>Fant ikke siden</h1>" in svar.text
    assert 'href="/logg-inn">Tilbake</a>' in svar.text  # vei videre


def test_feil_metode_gir_vennlig_405(klient: TestClient, lag_bruker, logg_inn_som) -> None:
    nokkel = hent_csrf(klient)
    logg_inn_som(klient, lag_bruker())
    svar = klient.post("/", data={"csrf_token": nokkel})
    assert svar.status_code == 405
    assert er_vennlig_html(svar)
    assert "Noe gikk galt. Prøv igjen om litt." in svar.text
    assert ">Tilbake</a>" in svar.text
    assert svar.headers["allow"] == "GET"


def test_tilbake_lenken_bruker_referer_fra_samme_nettsted(klient: TestClient) -> None:
    svar = klient.get("/finnes-ikke", headers={"Referer": "http://testserver/logg-inn?neste=/x"})
    assert 'href="/logg-inn?neste=/x">Tilbake</a>' in svar.text
    svar = klient.get("/finnes-ikke", headers={"Referer": "https://angriper.example/side"})
    assert 'href="/logg-inn">Tilbake</a>' in svar.text


@pytest.mark.parametrize(
    "referer",
    ["http://testserver//angriper.example/x", "http://testserver/finnes-ikke"],
    ids=["dobbel-skraastrek", "siden-selv"],
)
def test_tilbake_lenken_gaar_aldri_til_siden_selv_eller_annet_nettsted(
    klient: TestClient, referer: str
) -> None:
    svar = klient.get("/finnes-ikke", headers={"Referer": referer})
    assert 'href="/logg-inn">Tilbake</a>' in svar.text


def test_uventet_feil_gir_vennlig_500_med_headere(
    app: FastAPI, feilruter, caplog: pytest.LogCaptureFixture
) -> None:
    caplog.set_level(logging.ERROR, logger="app.core.feil")
    with TestClient(app, raise_server_exceptions=False) as klient:
        svar = klient.get("/_test/krasj?epost=kari@example.no")
    assert svar.status_code == 500
    assert er_vennlig_html(svar)
    assert "Noe gikk galt. Prøv igjen om litt." in svar.text
    assert ">Tilbake</a>" in svar.text
    for navn, verdi in SIKKERHETSHEADERE_TEKST.items():
        assert svar.headers[navn] == verdi
    # Logges, men uten personopplysninger fra meldingen eller spørrestrengen (AR-30).
    assert "RuntimeError" in caplog.text
    assert "/_test/krasj" in caplog.text
    assert "kari@example.no" not in caplog.text
    assert "91234567" not in caplog.text


def test_feil_i_feilsiden_gir_fast_500_med_headere(
    app: FastAPI, feilruter, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Kaster feilsiden selv, sendes en fast side, fortsatt med sikkerhetsheaderne (NFR-10)."""
    from app.core import feil

    def kaster(*args, **kwargs):
        raise RuntimeError("feilsiden virker ikke")

    monkeypatch.setattr(feil, "feilside", kaster)
    with TestClient(app, raise_server_exceptions=False) as klient:
        svar = klient.get("/_test/krasj")
    assert svar.status_code == 500
    assert "Noe gikk galt. Prøv igjen om litt." in svar.text
    assert '<html lang="nb">' in svar.text
    for navn, verdi in SIKKERHETSHEADERE_TEKST.items():
        assert svar.headers[navn] == verdi


@pytest.mark.parametrize("sti", ["/_test/finnes-ikke", "/_test/ingen-tilgang"])
def test_finnes_ikke_og_ingen_tilgang_gir_samme_404(klient: TestClient, feilruter, sti: str) -> None:
    svar = klient.get(sti)
    assert svar.status_code == 404
    assert "<h1>Fant ikke siden</h1>" in svar.text


def test_valideringsfeil_gir_vennlig_side(klient: TestClient, feilruter) -> None:
    svar = klient.get("/_test/tall?n=abc")
    assert svar.status_code == 400
    assert er_vennlig_html(svar)
    assert "Noe gikk galt. Prøv igjen om litt." in svar.text


def test_api_dokumentasjon_er_slatt_av(klient: TestClient) -> None:
    for sti in ("/docs", "/redoc", "/openapi.json"):
        assert klient.get(sti).status_code == 404


def test_regelbrudd_barer_alle_feil_i_rekkefolge() -> None:
    """AR-26, NFR-10: `RegelBrudd` har alle feltfeilene, i rekkefølgen de ble gitt."""
    feil = [("navn", "Skriv navnet ditt."), ("epost", "Skriv e-postadressen din.")]
    brudd = RegelBrudd(feil)
    assert brudd.feil == feil
    assert brudd.feil is not feil  # kopi, så den som kastet, ikke endrer den etterpå
    assert "Skriv" not in str(brudd)  # meldingen har bare antallet


def test_regelbrudd_krever_minst_en_feil() -> None:
    with pytest.raises(ValueError):
        RegelBrudd([])


# ---------- Konflikt (AD-2, §4.0, story 2.5) ----------


def test_konflikt_gir_303_med_feilmeldingen_i_cookien(klient: TestClient, feilruter) -> None:
    """§4.0: `Konflikt` gir 303 til `til_url`, og siden der viser feilmeldingen én gang."""
    svar = klient.get("/_test/konflikt", follow_redirects=False)
    assert svar.status_code == 303
    assert svar.headers["location"] == "/logg-inn"
    cookie = svar.headers["set-cookie"]
    assert cookie.startswith("feilmelding=") and "HttpOnly" in cookie and "Oppdraget" not in cookie
    side = klient.get("/logg-inn")
    assert "<span>Oppdraget er endret. Last siden på nytt.</span>" in side.text
    assert 'href="/logg-inn">Last siden på nytt</a>' in side.text
    assert 'id="feilmelding" tabindex="-1" autofocus' in side.text
    assert side.text.count("autofocus") == 1  # feilmeldingen går foran «E-post»
    assert "Last siden på nytt" not in klient.get("/logg-inn").text


def test_forfalsket_feilmeldingscookie_ignoreres(klient: TestClient) -> None:
    """Bare signerte, faste nøkler gir tekst, så cookien aldri kan vise annen tekst."""
    klient.cookies.set("feilmelding", "konflikt")
    assert 'id="feilmelding"' not in klient.get("/logg-inn").text


def test_laas_gir_konflikt() -> None:
    """AD-2: «database is locked» blir `Konflikt`; andre feil slipper gjennom uendret."""
    import sqlite3

    from sqlalchemy.exc import OperationalError

    from app.core.db import laas_gir_konflikt

    with pytest.raises(Konflikt) as konflikt:
        with laas_gir_konflikt("Oppdraget er endret. Last siden på nytt.", "/oppdrag/1"):
            raise OperationalError("BEGIN IMMEDIATE", {}, sqlite3.OperationalError("database is locked"))
    assert konflikt.value.til_url == "/oppdrag/1"
    with pytest.raises(OperationalError):
        with laas_gir_konflikt("x", "/"):
            raise OperationalError("SELECT 1", {}, sqlite3.OperationalError("disk I/O error"))
    with pytest.raises(ValueError):
        with laas_gir_konflikt("x", "/"):
            raise ValueError("annen feil")


def test_ukjent_feilmelding_gir_valueerror() -> None:
    """Bare faste tekster kan bli feilmeldinger; en ukjent tekst er en programmeringsfeil."""
    from app.core.kvittering import nokkel_for_feilmelding

    assert nokkel_for_feilmelding("Oppdraget er endret. Last siden på nytt.") == "konflikt"
    with pytest.raises(ValueError):
        nokkel_for_feilmelding("Noe annet.")
