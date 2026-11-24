"""Røyktesten (`scripts/roykttest.py`) kjørt mot testappen (AR-1, AD-5, AD-14).

Slik oppdages en endret tekst eller header i CI, og ikke først når
røyktesten feiler etter publisering.
"""

from __future__ import annotations

from collections.abc import Callable

import httpx
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

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
