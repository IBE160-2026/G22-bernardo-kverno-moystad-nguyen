"""Røyktesten (`scripts/roykttest.py`) kjørt mot testappen (AR-1, AD-5, AD-14).

Slik oppdages en endret tekst eller header i CI, og ikke først når
røyktesten feiler etter publisering.
"""

from __future__ import annotations

from collections.abc import Callable

from fastapi.testclient import TestClient

from app.identity.models import Bruker
from scripts import roykttest

TESTAPP_URL = "http://testserver"
MANGLER_SECURE = (
    "GET /logg-inn: cookien csrf mangler Secure. APP_ENV er trolig ikke production"
)


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
