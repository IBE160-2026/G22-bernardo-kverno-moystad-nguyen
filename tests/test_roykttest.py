"""Røyktesten (`scripts/roykttest.py`) kjørt mot apper på test-databasen (AR-1, AD-5, AD-14).

Slik oppdages en endret tekst eller header i CI, og ikke først når
røyktesten feiler etter publisering. Den grønne stien kjøres mot en app med
APP_ENV=production over https (V2 i retro Epic 1).
"""

from __future__ import annotations

from collections.abc import Callable, Iterator

import httpx
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from app import lag_app
from app.core.config import Settings, hent_settings
from app.core.feil import RegelBrudd
from app.identity.models import Bruker
from app.identity.service import EPOST_FORMAT, normaliser_epost, registrer, sjekk_epostformat
from app.seed import TESTBRUKERE
from scripts import roykttest

TESTAPP_URL = "http://testserver"
PRODUKSJON_URL = "https://testserver"
KARI = next(t for t in TESTBRUKERE if t.epost == "kari@eksempel.no")
MANGLER_SECURE = (
    "GET /logg-inn: cookien csrf mangler Secure. APP_ENV er trolig ikke production"
)


@pytest.fixture
def klient(sesjonsfabrikk: sessionmaker[Session]) -> Iterator[TestClient]:
    """Appen med APP_ENV=local mot test-databasen (AD-14).

    Testappen (APP_ENV=test) har `/_test/tilstand`, og der gir GET 405. Røyktesten
    sjekker at stien gir 404, slik den skal utenfor test.
    """
    settings = Settings(
        _env_file=None, app_env="local", database_url=hent_settings().database_url
    )
    app = lag_app(settings=settings)
    app.state.sesjonsfabrikk = sesjonsfabrikk
    with TestClient(app) as klient:
        yield klient


@pytest.fixture
def produksjonsklient(sesjonsfabrikk: sessionmaker[Session]) -> Iterator[TestClient]:
    """Appen med APP_ENV=production over https, mot test-databasen (AD-14, V2).

    Postgres-URL-en trengs bare for at `Settings` skal godta produksjon. Motoren
    kobler aldri til, fordi sesjonsfabrikken byttes til test-databasen. CSRF-cookien
    får `Secure` i produksjon, og klienten sender den bare tilbake over https.
    """
    settings = Settings(
        _env_file=None,
        app_env="production",
        secret_key="x" * 32,
        database_url="postgresql+psycopg://u@h:5432/d",
    )
    app = lag_app(settings=settings)
    app.state.sesjonsfabrikk = sesjonsfabrikk
    try:
        with TestClient(app, base_url=PRODUKSJON_URL) as klient:
            yield klient
    finally:
        app.state.motor.dispose()


def test_roykttesten_er_gronn_mot_produksjonsapp(produksjonsklient: TestClient) -> None:
    """AR-1, AD-14, V2: mot en app med APP_ENV=production over https gir røyktesten ingen avvik."""
    assert roykttest.kjor(PRODUKSJON_URL, klient=produksjonsklient) == []


def test_roykttesten_mot_lokal_app_uten_seed(klient: TestClient) -> None:
    """Røyktest-e-posten avvises med 422. Eneste avvik er manglende `Secure`,
    fordi den lokale appen (APP_ENV=local) ikke kjører med APP_ENV=production."""
    assert roykttest.kjor(TESTAPP_URL, klient=klient) == [MANGLER_SECURE]


def test_roykttesten_taaler_at_kari_finnes(
    klient: TestClient, lag_bruker: Callable[..., Bruker]
) -> None:
    """R1: finnes Kari med seed-passordet fra README, for eksempel registrert av
    hvem som helst etter at registreringen ble åpnet, er røyktesten fortsatt grønn
    (bortsett fra `Secure` i den lokale appen). NFR-2 hviler på
    `test_seed_nekter_i_produksjon`."""
    lag_bruker(epost=KARI.epost, passord=KARI.passord)
    assert roykttest.kjor(TESTAPP_URL, klient=klient) == [MANGLER_SECURE]


def test_roykttest_eposten_kan_ikke_registreres(db: Session) -> None:
    """R1, FR-1: e-posten røyktesten logger inn med, avvises av registreringen
    (`EPOST_FORMAT`), så ingen kan lage kontoen og gjøre publiseringen rød."""
    assert not sjekk_epostformat(normaliser_epost(roykttest.ROYKTTEST_EPOST))
    assert roykttest.ROYKTTEST_EPOST not in {t.epost for t in TESTBRUKERE}
    with pytest.raises(RegelBrudd) as brudd:
        registrer(
            db,
            navn="Røyk Test",
            epost=roykttest.ROYKTTEST_EPOST,
            passord=roykttest.ROYKTTEST_PASSORD,
            telefon="91234567",
            postnummer="0571",
            fodselsdato="03.05.1954",
        )
    assert brudd.value.feil == [("epost", EPOST_FORMAT)]


def test_roykttesten_melder_fra_om_testruta(app: FastAPI) -> None:
    """AD-14: i testappen (APP_ENV=test) finnes `/_test/tilstand`, og røyktesten melder avvik."""
    with TestClient(app) as testklient:
        avvik = roykttest.kjor(TESTAPP_URL, klient=testklient)
    assert "GET /_test/tilstand: status 405, forventet 404" in avvik


class _UtenRegistrering:
    """Testklienten, men `/registrer` svarer 404, som om ruta manglet i publiseringen."""

    def __init__(self, klient: TestClient) -> None:
        self._klient = klient

    def get(self, sti: str, **kwargs):
        if sti == "/registrer":
            return httpx.Response(404, request=httpx.Request("GET", f"{TESTAPP_URL}{sti}"))
        return self._klient.get(sti, **kwargs)

    def post(self, sti: str, **kwargs):
        return self._klient.post(sti, **kwargs)


def test_roykttesten_sjekker_registreringssiden(klient: TestClient) -> None:
    """FR-1, AD-14: røyktesten melder fra når `/registrer` ikke svarer, uten å registrere noen."""
    assert roykttest.kjor(TESTAPP_URL, klient=_UtenRegistrering(klient)) == [
        MANGLER_SECURE,
        "GET /registrer: status 404, forventet 200",
    ]


def test_roykttesten_lager_ingen_kontoer(klient: TestClient, db: Session) -> None:
    """Spec-1-4: røyktesten oppretter aldri kontoer i produksjon."""
    for_ = db.scalar(select(func.count()).select_from(Bruker))
    roykttest.kjor(TESTAPP_URL, klient=klient)
    assert db.scalar(select(func.count()).select_from(Bruker)) == for_
