"""Gjør databasen klar lokalt: `uv run python -m app.seed` (NFR-1, AD-14).

Kjører `alembic upgrade head`, som også laster postnumrene. Eksempelbrukere og
eksempeloppdrag kommer i senere stories (NFR-2). Nekter å kjøre i produksjon.
"""

from __future__ import annotations

import sys
from pathlib import Path

from alembic import command
from alembic.config import Config

from app.core.config import hent_settings

ROT = Path(__file__).resolve().parents[1]


def alembic_config() -> Config:
    return Config(str(ROT / "alembic.ini"))


def main() -> int:
    settings = hent_settings()
    if settings.produksjon:
        print("Seed kjøres ikke i produksjon (APP_ENV=production).", file=sys.stderr)
        return 1
    command.upgrade(alembic_config(), "head")
    print(f"Databasen er klar ({_url_uten_passord(settings.database_url)}).")
    return 0


def _url_uten_passord(url: str) -> str:
    from sqlalchemy.engine import make_url

    return make_url(url).render_as_string(hide_password=True)


if __name__ == "__main__":
    sys.exit(main())
