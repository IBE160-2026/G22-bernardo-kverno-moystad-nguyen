"""Feilsider: aldri JSON, `detail` eller stack trace (NFR-10, AR-26)."""

from __future__ import annotations

import logging

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.feil import FinnesIkke, IngenTilgang
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
