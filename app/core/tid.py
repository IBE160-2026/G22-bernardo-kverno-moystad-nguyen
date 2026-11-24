"""Dato og «i dag» i norsk tid (AD-9).

- «I dag» er datoen i Europe/Oslo, regnet fra `klokke.na()`, så testene kan
  stille klokka med `sett_na`.
- `tolk_fodselsdato` er eneste tolkning av fødselsdato. Den godtar `.`, `/`,
  `-` eller mellomrom mellom tallene, dag og måned med ett eller to siffer og
  år med to eller fire siffer. Tosifret år blir den nyeste datoen som ikke er
  fram i tid (20xx, ellers 19xx), altså en alder fra 0 til 99 år.
- Bursdag 29. februar regnes som 1. mars i år som ikke er skuddår (FR-1).

`tzdata` er en direkte avhengighet, så `zoneinfo` finner Europe/Oslo også der
operativsystemet ikke har tidssonedata (Vercel, Windows).
"""

from __future__ import annotations

import re
import unicodedata
from datetime import date
from zoneinfo import ZoneInfo

from app.core import klokke
from app.core.feil import RegelBrudd

OSLO = ZoneInfo("Europe/Oslo")
MAKS_ALDER = 120

SKRIV_FODSELSDATO = "Skriv fødselsdatoen din."
FODSELSDATO_FORMAT = "Skriv fødselsdatoen som dd.mm.åååå, for eksempel 03.05.1954."
SJEKK_FODSELSDATO = "Sjekk fødselsdatoen."

# Samme skilletegn begge steder. Bare ASCII-sifre, så «٣» og lignende avvises.
_DATO = re.compile(r"([0-9]{1,2})([./\- ])([0-9]{1,2})\2([0-9]{4}|[0-9]{2})")


def i_dag() -> date:
    """Dagens dato i Europe/Oslo (AD-9)."""
    return klokke.na().astimezone(OSLO).date()


def fyller_ar(fodselsdato: date, ar: int) -> date:
    """Datoen personen har bursdag i året `ar`. 29. februar blir 1. mars i år som ikke er skuddår."""
    try:
        return fodselsdato.replace(year=ar)
    except ValueError:
        return date(ar, 3, 1)


def er_myndig(fodselsdato: date, i_dag: date) -> bool:
    """Om personen har fylt 18 år `i_dag`. Fyller 18 i dag godtas (FR-1)."""
    return fyller_ar(fodselsdato, fodselsdato.year + 18) <= i_dag


def tidligste_fodselsdato(i_dag: date) -> date:
    """Eldste fødselsdato som godtas: i dag minus 120 år (FR-1)."""
    return fyller_ar(i_dag, i_dag.year - MAKS_ALDER)


def tolk_fodselsdato(tekst: str | None, *, i_dag: date, felt: str = "fodselsdato") -> date:
    """Fødselsdatoen fra teksten i skjemaet (FR-1, AD-9).

    Kaster `RegelBrudd` på `felt` med én av tekstene:
    - tomt eller bare mellomrom: «Skriv fødselsdatoen din.»
    - feil format: «Skriv fødselsdatoen som dd.mm.åååå, …»
    - datoen finnes ikke, er fram i tid eller mer enn 120 år tilbake: «Sjekk fødselsdatoen.»
    """
    verdi = unicodedata.normalize("NFC", tekst or "").strip()
    if not verdi:
        raise RegelBrudd([(felt, SKRIV_FODSELSDATO)])
    treff = _DATO.fullmatch(verdi)
    if treff is None:
        raise RegelBrudd([(felt, FODSELSDATO_FORMAT)])
    dag, maned, ar_tekst = int(treff.group(1)), int(treff.group(3)), treff.group(4)
    try:
        if len(ar_tekst) == 2:
            dato = date(2000 + int(ar_tekst), maned, dag)
            if dato > i_dag:
                dato = date(1900 + int(ar_tekst), maned, dag)
        else:
            dato = date(int(ar_tekst), maned, dag)
    except ValueError:
        # Datoen finnes ikke, for eksempel 31.02.1990 eller måned 13.
        raise RegelBrudd([(felt, SJEKK_FODSELSDATO)]) from None
    if dato > i_dag or dato < tidligste_fodselsdato(i_dag):
        raise RegelBrudd([(felt, SJEKK_FODSELSDATO)])
    return dato

