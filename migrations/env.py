"""Alembic-miljø (AD-13).

URL-en kommer fra `Settings` (`DATABASE_URL`). Testene gir i stedet en åpen
tilkobling i `config.attributes["connection"]`. `render_as_batch=True` gjør at
endringer av kolonner også virker i SQLite.
"""

from __future__ import annotations

from logging.config import fileConfig

from alembic import context

import app.identity.models  # noqa: F401  (registrerer tabellene i metadataen)
from app.core.config import hent_settings
from app.core.db import Base, lag_motor

config = context.config
target_metadata = Base.metadata

tilkobling = config.attributes.get("connection")

if config.config_file_name is not None and tilkobling is None:
    fileConfig(config.config_file_name, disable_existing_loggers=False)


def _kjor(tilkobling) -> None:
    context.configure(
        connection=tilkobling,
        target_metadata=target_metadata,
        render_as_batch=True,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def kjor_migreringer() -> None:
    if tilkobling is not None:
        _kjor(tilkobling)
        return
    motor = lag_motor(hent_settings().database_url)
    try:
        with motor.connect() as ny_tilkobling:
            _kjor(ny_tilkobling)
            ny_tilkobling.commit()
    finally:
        motor.dispose()


if context.is_offline_mode():
    raise SystemExit("Offline-modus brukes ikke. Kjør migreringene mot en database.")

kjor_migreringer()
