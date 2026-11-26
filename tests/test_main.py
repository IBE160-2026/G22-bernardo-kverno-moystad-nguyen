"""Inngangspunktet `main.py` for uvicorn og Vercel (AD-1, V1 i retro Epic 1).

Feiler importen av `main`, er funksjonen på Vercel død selv om resten av CI er
grønn. `tests/conftest.py` har satt `APP_ENV=test` og `DATABASE_URL` til
test-databasen før importen, så `lag_app()` leser test-konfigurasjonen.
"""

from __future__ import annotations

import importlib

from fastapi import FastAPI


def test_main_gir_appen_med_rutene() -> None:
    """AD-1: `main.app` er en `FastAPI` laget av `lag_app()`, med ruta `identity.logg_inn`."""
    main = importlib.import_module("main")
    try:
        assert isinstance(main.app, FastAPI)
        assert main.app.url_path_for("identity.logg_inn") == "/logg-inn"
    finally:
        main.app.state.motor.dispose()
