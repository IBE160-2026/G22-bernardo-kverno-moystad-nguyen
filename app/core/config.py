"""All konfigurasjon leses her, fra miljøvariabler eller en valgfri `.env` (AD-14, NFR-1).

Ingen annen kode leser `os.environ`. Appen starter uten `.env`: standardverdiene
gir lokal kjøring mot en SQLite-fil. I produksjon stopper oppstarten hvis
`SECRET_KEY` mangler, er standardverdien eller er kortere enn 32 tegn.
"""

from __future__ import annotations

import logging
from functools import lru_cache

from pydantic import ValidationError, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

STANDARD_NOKKEL = "lokal-utvikling-ikke-hemmelig"
MILJOER = ("local", "test", "production")
MINSTE_NOKKELLENGDE = 32


class KonfigFeil(RuntimeError):
    """Konfigurasjonen er ugyldig, og appen skal ikke starte (AD-14)."""


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
    )

    app_env: str = "local"
    database_url: str = "sqlite:///./nabolagshelten.db"
    secret_key: str = STANDARD_NOKKEL
    openrouter_api_key: str = ""
    openrouter_model: str = ""

    @field_validator("database_url")
    @classmethod
    def _bruk_psycopg(cls, verdi: str) -> str:
        # Supabase og Postgres-containere oppgir ofte postgres:// eller postgresql://.
        # SQLAlchemy skal bruke psycopg 3 (AD-13).
        for prefiks in ("postgres://", "postgresql://"):
            if verdi.startswith(prefiks):
                return "postgresql+psycopg://" + verdi[len(prefiks) :]
        return verdi

    @model_validator(mode="after")
    def _sjekk_miljo(self) -> Settings:
        if self.app_env not in MILJOER:
            raise ValueError(
                f"APP_ENV={self.app_env!r} er ukjent. Gyldige verdier: {', '.join(MILJOER)}."
            )
        if self.app_env == "production":
            if self.secret_key == STANDARD_NOKKEL:
                raise ValueError(
                    "SECRET_KEY er standardverdien. Sett en ekte, tilfeldig nøkkel i produksjon."
                )
            if len(self.secret_key) < MINSTE_NOKKELLENGDE:
                raise ValueError(
                    f"SECRET_KEY må ha minst {MINSTE_NOKKELLENGDE} tegn i produksjon."
                )
        return self

    @property
    def produksjon(self) -> bool:
        return self.app_env == "production"

    @property
    def test(self) -> bool:
        return self.app_env == "test"


def les_settings() -> Settings:
    """Leser konfigurasjonen. Ved feil logges en tydelig melding, og `KonfigFeil` kastes."""
    try:
        return Settings()
    except ValidationError as feil:
        meldinger = "; ".join(_kort_melding(e) for e in feil.errors())
        logger.critical("Oppstarten stopper: %s", meldinger)
        raise KonfigFeil(f"Oppstarten stopper: {meldinger}") from None


@lru_cache(maxsize=1)
def hent_settings() -> Settings:
    """Den ene `Settings` for prosessen."""
    return les_settings()


def _kort_melding(feil: dict) -> str:
    melding = str(feil.get("msg", ""))
    return melding.removeprefix("Value error, ")
