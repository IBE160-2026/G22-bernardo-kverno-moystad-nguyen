"""Røyktesten (`scripts/roykttest.py`) kjørt mot testappen (AR-1, AD-5, AD-14).

Slik oppdages en endret tekst eller header i CI, og ikke først når
røyktesten feiler etter publisering.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator

import httpx
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from app import lag_app
from app.core.config import Settings, hent_settings
from app.identity.models import Bruker
from scripts import roykttest

TESTAPP_URL = "http://testserver"
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


def test_roykttesten_mot_testappen_uten_seed(klient: TestClient) -> None:
    """Uten seed avvises Kari med 422. Eneste avvik er manglende `Secure`,
    fordi testappen ikke kjører med APP_ENV=production."""
    assert roykttest.kjor(TESTAPP_URL, klient=klient) == [MANGLER_SECURE]


def test_roykttesten_finner_demokonto(
    klient: TestClient, lag_bruker: Callable[..., Bruker]
) -> None:
    """NFR-2: finnes Kari med seed-passordet, rapporterer røyktesten en demokonto."""
    lag_bruker(epost=roykttest.SEED_EPOST, passord=roykttest.SEED_PASSORD)
    assert roykttest.kjor(TESTAPP_URL, klient=klient) == [
        MANGLER_SECURE,
        "POST /logg-inn: innloggingen lyktes. Det finnes en demokonto i produksjon",
    ]


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
