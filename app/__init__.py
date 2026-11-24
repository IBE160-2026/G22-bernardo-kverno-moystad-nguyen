"""Nabolagshelten. `lag_app()` setter sammen appen (AD-1, AD-5, AD-14).

Her kobles slicene til `core`: `Autentisering` fra identity (AD-4).
Menykroken blir påkrevd fra story 2.4. Mangler en kobling, starter ikke appen.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.core.config import KonfigFeil, Settings, hent_settings
from app.core.db import lag_motor, lag_sesjonsfabrikk
from app.core.feil import registrer_feilhandlere
from app.core.mellomvare import lag_mellomvare
from app.core.sesjon import Autentisering

logger = logging.getLogger(__name__)

STATIC_MAPPE = Path(__file__).resolve().parent / "core" / "static"

_STANDARD: Any = object()


def _standard_autentisering() -> Autentisering:
    from app.identity.service import IdentityAutentisering

    return IdentityAutentisering()


def lag_app(
    *,
    autentisering: Autentisering | None = _STANDARD,
    settings: Settings | None = None,
) -> FastAPI:
    """Lager appen med mellomvare, feilhandlere, statiske filer og rutene.

    Uten argumenter kobles identity sin `Autentisering` inn. Gis `None` eller et
    objekt som ikke er en `Autentisering`, nekter appen å starte (AD-1).
    """
    settings = settings or hent_settings()

    if autentisering is _STANDARD:
        autentisering = _standard_autentisering()
    if autentisering is None or not isinstance(autentisering, Autentisering):
        melding = "Oppstarten stopper: lag_app() mangler kobling til Autentisering (AD-1, AD-4)."
        logger.critical(melding)
        raise KonfigFeil(melding)

    app = FastAPI(
        title="Nabolagshelten",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
        middleware=lag_mellomvare(settings, autentisering),
    )
    motor = lag_motor(settings.database_url)
    app.state.settings = settings
    app.state.autentisering = autentisering
    app.state.motor = motor
    app.state.sesjonsfabrikk = lag_sesjonsfabrikk(motor)

    registrer_feilhandlere(app)
    app.mount("/static", StaticFiles(directory=STATIC_MAPPE), name="static")

    from app.identity.routes import router as identity_router
    from app.oppdrag.routes import router as oppdrag_router
    from app.profil.routes import router as profil_router

    app.include_router(identity_router)
    app.include_router(oppdrag_router)
    app.include_router(profil_router)
    return app
