"""Domeneverdier som brukes av mer enn én slice (AD-10, AR-20).

- `KATEGORIER`: den faste lista fra FR-5 som `(kode, tekst)`, i visningsrekkefølge.
  Database, URL-er og skjemaverdier bruker koden. Bare `kategori_tekst` (og
  Jinja-filteret med samme navn) gir teksten.
- `STATUSER`: statusene fra AD-2 som `(kode, tekst)`.
- Grensene for tittel og beskrivelse (FR-5). Andre grenser ligger i eier-slicen.
- `normaliser_tekst`: tekst fra brukere trimmes og NFC-normaliseres før `len()`.
- `kr`: beløp som «1 000 kr» eller «Uten betaling» (EXPERIENCE.md § Formater).
- `Erfaring`: fullførte oppdrag som hjelper og vurderinger, som oppdragsgiverblokken,
  interessertlista og profilen viser (FR-21, AD-3). `fullforte_tekst` og
  `vurdering_tekst` (og Jinja-filtrene `fullforte` og `vurdering`) gir teksten.
"""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

KATEGORIER: tuple[tuple[str, str], ...] = (
    ("snomaking", "Snømåking"),
    ("hage", "Hage"),
    ("baerehjelp-flytting", "Bærehjelp/flytting"),
    ("dyrepass", "Dyrepass"),
    ("teknologihjelp", "Teknologihjelp"),
    ("annet", "Annet"),
)
KATEGORIKODER: frozenset[str] = frozenset(kode for kode, _ in KATEGORIER)

STATUSER: tuple[tuple[str, str], ...] = (
    ("apen", "Åpen"),
    ("hjelper_valgt", "Hjelper valgt"),
    ("utfort", "Utført"),
    ("avbrutt", "Avbrutt"),
)
STATUSKODER: frozenset[str] = frozenset(kode for kode, _ in STATUSER)

TITTEL_MIN = 3
TITTEL_MAKS = 80
BESKRIVELSE_MIN = 10
BESKRIVELSE_MAKS = 1000

BELOP_MIN = 1
BELOP_MAKS = 10_000

NBSP = " "
UTEN_BETALING = "Uten betaling"

_KATEGORITEKST = dict(KATEGORIER)
_STATUSTEKST = dict(STATUSER)


def kategori_tekst(kode: str) -> str:
    """Teksten for en kategorikode, for eksempel «Bærehjelp/flytting». Ukjent kode gir `ValueError`."""
    try:
        return _KATEGORITEKST[kode]
    except KeyError:
        raise ValueError(f"Ukjent kategori: {kode!r}") from None


def status_tekst(kode: str) -> str:
    """Teksten for en statuskode, for eksempel «Hjelper valgt». Ukjent kode gir `ValueError`."""
    try:
        return _STATUSTEKST[kode]
    except KeyError:
        raise ValueError(f"Ukjent status: {kode!r}") from None


def normaliser_tekst(verdi: str | None) -> str:
    """Trimmet og NFC-normalisert tekst, med linjeskift som `\\n` og uten NUL (AD-10).

    Nettleseren sender linjeskift i et tekstområde som CRLF, men telleren på
    klienten ser bare LF. Med LF her teller server og klient likt. NUL fjernes,
    fordi Postgres avviser det. Felt med bare mellomrom blir tomme.
    """
    tekst = (verdi or "").replace("\x00", "").replace("\r\n", "\n").replace("\r", "\n")
    return unicodedata.normalize("NFC", tekst).strip()


def antall_tegn(verdi: str | None) -> int:
    """Antall kodepunkter etter `normaliser_tekst`, som telleren viser (AD-10)."""
    return len(normaliser_tekst(verdi))


def kr(belop: int | None) -> str:
    """«200 kr», «1 000 kr» eller «Uten betaling». NBSP som tusenskille og før «kr»."""
    if belop is None:
        return UTEN_BETALING
    return f"{belop:,}".replace(",", NBSP) + f"{NBSP}kr"


INGEN_VURDERINGER = "Ingen vurderinger ennå"
INGEN_FULLFORTE = "Ingen fullførte oppdrag ennå"


@dataclass(frozen=True)
class Erfaring:
    """Erfaringen til en bruker som hjelper (FR-21, AD-3). Beregnes ved lesing.

    `fullforte` er antall utførte oppdrag der brukeren var valgt hjelper, og
    `per_kategori` det samme per kategorikode, i rekkefølgen i `KATEGORIER` og
    uten kategorier med 0. `snitt` er `None` og `antall_vurderinger` 0 til
    tilbakemeldingene kommer i Epic 4.
    """

    fullforte: int
    per_kategori: tuple[tuple[str, int], ...]
    snitt: float | None
    antall_vurderinger: int


def fullforte_tekst(antall: int) -> str:
    """«Ingen fullførte oppdrag ennå», «1 fullført oppdrag» eller «12 fullførte oppdrag»."""
    if antall <= 0:
        return INGEN_FULLFORTE
    if antall == 1:
        return "1 fullført oppdrag"
    return f"{antall} fullførte oppdrag"


def vurdering_tekst(erfaring: Erfaring) -> str:
    """«4,3 av 5, 7 vurderinger», «5,0 av 5, 1 vurdering» eller «Ingen vurderinger ennå» (FR-21)."""
    if erfaring.snitt is None or erfaring.antall_vurderinger <= 0:
        return INGEN_VURDERINGER
    # Halvparten rundes opp (4,25 → 4,3), uavhengig av hvordan flyttallet er lagret.
    snitt = str(Decimal(str(erfaring.snitt)).quantize(Decimal("0.1"), ROUND_HALF_UP)).replace(".", ",")
    ord_ = "vurdering" if erfaring.antall_vurderinger == 1 else "vurderinger"
    return f"{snitt} av 5, {erfaring.antall_vurderinger} {ord_}"
