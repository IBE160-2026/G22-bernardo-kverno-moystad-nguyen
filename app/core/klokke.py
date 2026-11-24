"""Klokka for hele appen (AD-3, AD-9).

Brukes alltid som `klokke.na()` etter `from app.core import klokke`, så testene
kan stille klokka med `sett_na` i `tests/conftest.py`.
"""

from __future__ import annotations

from datetime import datetime, timezone

_overstyrt: datetime | None = None


def na() -> datetime:
    """Nå som aware UTC."""
    if _overstyrt is not None:
        return _overstyrt
    return datetime.now(timezone.utc)


def sett_na(tidspunkt: datetime | None) -> None:
    """Stiller klokka (bare for tester). `None` gir vanlig klokke igjen."""
    global _overstyrt
    if tidspunkt is not None and (tidspunkt.tzinfo is None or tidspunkt.utcoffset() is None):
        raise ValueError("sett_na krever et tidspunkt med tidssone.")
    _overstyrt = None if tidspunkt is None else tidspunkt.astimezone(timezone.utc)
