"""Dato, tidspunkt og «i dag» i norsk tid (AD-9).

- «I dag» er datoen i Europe/Oslo, regnet fra `klokke.na()`, så testene kan
  stille klokka med `sett_na`.
- `tolk_fodselsdato` er eneste tolkning av fødselsdato. Den godtar `.`, `/`,
  `-` eller mellomrom mellom tallene, dag og måned med ett eller to siffer og
  år med to eller fire siffer. Tosifret år blir den nyeste datoen som ikke er
  fram i tid (20xx, ellers 19xx), altså en alder fra 0 til 99 år.
- Bursdag 29. februar regnes som 1. mars i år som ikke er skuddår (FR-1).
- `tolk_tidspunkt` er eneste tolkning av oppdragstid (FR-5, AR-19): dato som
  fødselsdatoen (tosifret år betyr alltid 20xx) og klokkeslett som `H`, `HH`,
  `H:MM`, `HH:MM`, `H.MM` eller `HHMM`. Et klokkeslett som ikke finnes når
  klokka stilles fram, avvises. Et som finnes to ganger, tolkes som det første.
- `vis_tidspunkt` er eneste visning av tidspunkt: «I dag kl. 07:00», «I morgen
  kl. 07:00» eller «Lørdag 14. nov. kl. 12:00», med år når det ikke er i år.
- `skjemaverdier` gjør et lagret tidspunkt om til feltene i redigeringsskjemaet
  («25.11.2026», «09:00»), så `tolk_tidspunkt` gir det samme tilbake (FR-6).

`tzdata` er en direkte avhengighet, så `zoneinfo` finner Europe/Oslo også der
operativsystemet ikke har tidssonedata (Vercel, Windows).
"""

from __future__ import annotations

import re
import unicodedata
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

from app.core import klokke
from app.core.feil import RegelBrudd

OSLO = ZoneInfo("Europe/Oslo")
MAKS_ALDER = 120

SKRIV_FODSELSDATO = "Skriv fødselsdatoen din."
FODSELSDATO_FORMAT = "Skriv fødselsdatoen som dd.mm.åååå, for eksempel 03.05.1954."
SJEKK_FODSELSDATO = "Sjekk fødselsdatoen."

# Feiltekstene for oppdragstid står ordrett i EXPERIENCE.md § Feiltekster ved felt (FR-5).
SKRIV_DATO = "Skriv datoen."
DATO_FORMAT = "Skriv datoen som dd.mm.åååå, for eksempel 14.11.2026."
DATO_FINNES_IKKE = "Den datoen finnes ikke. Sjekk dag og måned."
SKRIV_KLOKKESLETT = "Skriv klokkeslettet."
KLOKKESLETT_FORMAT = "Skriv klokkeslettet som tt:mm, for eksempel 07:00."
KLOKKESLETT_FINNES_IKKE = (
    "Klokkeslettet finnes ikke den natten, fordi klokka stilles fram. Velg et annet klokkeslett."
)
TIDSPUNKT_PASSERT = "Velg et nytt tidspunkt fram i tid"
TIDSPUNKT_FOR_LANGT_FRAM = "Velg et tidspunkt høyst 12 måneder fram i tid."

# Samme skilletegn begge steder. Bare ASCII-sifre, så «٣» og lignende avvises.
_DATO = re.compile(r"([0-9]{1,2})([./\- ])([0-9]{1,2})\2([0-9]{4}|[0-9]{2})")
# H, HH, H:MM, HH:MM, H.MM eller HHMM.
_KLOKKESLETT = re.compile(r"([0-9]{1,2})(?:[:.]([0-9]{2}))?|([0-9]{2})([0-9]{2})")

_UKEDAGER = ("Mandag", "Tirsdag", "Onsdag", "Torsdag", "Fredag", "Lørdag", "Søndag")
_MANEDER = ("jan.", "feb.", "mars", "apr.", "mai", "juni", "juli", "aug.", "sep.", "okt.", "nov.", "des.")


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


# ---------- oppdragstid (FR-5, AR-19) ----------


def _tolk_dato(tekst: str | None) -> date:
    verdi = unicodedata.normalize("NFC", tekst or "").strip()
    if not verdi:
        raise RegelBrudd([("dato", SKRIV_DATO)])
    treff = _DATO.fullmatch(verdi)
    if treff is None:
        raise RegelBrudd([("dato", DATO_FORMAT)])
    dag, maned, ar_tekst = int(treff.group(1)), int(treff.group(3)), treff.group(4)
    ar = 2000 + int(ar_tekst) if len(ar_tekst) == 2 else int(ar_tekst)
    try:
        return date(ar, maned, dag)
    except ValueError:
        raise RegelBrudd([("dato", DATO_FINNES_IKKE)]) from None


def _tolk_klokkeslett(tekst: str | None) -> time:
    verdi = unicodedata.normalize("NFC", tekst or "").strip()
    if not verdi:
        raise RegelBrudd([("klokkeslett", SKRIV_KLOKKESLETT)])
    treff = _KLOKKESLETT.fullmatch(verdi)
    if treff is None:
        raise RegelBrudd([("klokkeslett", KLOKKESLETT_FORMAT)])
    if treff.group(1) is not None:
        timer, minutter = int(treff.group(1)), int(treff.group(2) or 0)
    else:
        timer, minutter = int(treff.group(3)), int(treff.group(4))
    if timer > 23 or minutter > 59:
        raise RegelBrudd([("klokkeslett", KLOKKESLETT_FORMAT)])
    return time(timer, minutter)


def finnes_i_oslo(lokal: datetime) -> bool:
    """Om et naivt klokkeslett finnes i Europe/Oslo (ikke i timen som hoppes over om våren)."""
    aware = lokal.replace(tzinfo=OSLO, fold=0)
    return aware.astimezone(timezone.utc).astimezone(OSLO).replace(tzinfo=None) == lokal


def til_utc(lokal: datetime) -> datetime:
    """Naiv norsk tid til aware UTC. Finnes klokkeslettet to ganger (høst), brukes det første."""
    return lokal.replace(tzinfo=OSLO, fold=0).astimezone(timezone.utc)


def seneste_tidspunkt(na: datetime) -> datetime:
    """Samme dato og klokkeslett i norsk tid om 12 måneder (29.02 blir 01.03). Grensen godtas."""
    lokal = na.astimezone(OSLO)
    dato = fyller_ar(lokal.date(), lokal.year + 1)
    return til_utc(datetime.combine(dato, lokal.time().replace(tzinfo=None)))


def tolk_tidspunkt(dato: str | None, klokkeslett: str | None, *, na: datetime) -> datetime:
    """Oppdragstiden fra feltene «Dato» og «Klokkeslett», som aware UTC (FR-5, AD-9).

    Kaster én `RegelBrudd` med alle feilene: på `dato` og `klokkeslett` når de
    mangler, har feil format eller ikke finnes, ellers på `nar` når tidspunktet
    ikke er fram i tid (`> na`) eller er mer enn 12 måneder fram.
    """
    feil: list[tuple[str, str]] = []
    dato_: date | None = None
    klokkeslett_: time | None = None
    try:
        dato_ = _tolk_dato(dato)
    except RegelBrudd as brudd:
        feil.extend(brudd.feil)
    try:
        klokkeslett_ = _tolk_klokkeslett(klokkeslett)
    except RegelBrudd as brudd:
        feil.extend(brudd.feil)
    if feil:
        raise RegelBrudd(feil)
    assert dato_ is not None and klokkeslett_ is not None

    lokal = datetime.combine(dato_, klokkeslett_)
    try:
        if not finnes_i_oslo(lokal):
            raise RegelBrudd([("klokkeslett", KLOKKESLETT_FINNES_IKKE)])
        tidspunkt = til_utc(lokal)
    except OverflowError:
        # År 1 eller 9999 kan ligge utenfor det `datetime` tåler i UTC.
        passert = dato_ < na.astimezone(OSLO).date()
        raise RegelBrudd([("nar", TIDSPUNKT_PASSERT if passert else TIDSPUNKT_FOR_LANGT_FRAM)]) from None
    if tidspunkt <= na:
        raise RegelBrudd([("nar", TIDSPUNKT_PASSERT)])
    if tidspunkt > seneste_tidspunkt(na):
        raise RegelBrudd([("nar", TIDSPUNKT_FOR_LANGT_FRAM)])
    return tidspunkt


def skjemaverdier(tidspunkt: datetime) -> tuple[str, str]:
    """Et lagret tidspunkt som feltene «Dato» og «Klokkeslett»: «25.11.2026» og «09:00» (AD-9).

    Alltid i norsk tid, så `tolk_tidspunkt` gir det samme tidspunktet tilbake. Det
    gjelder også over sommertidsskiftene, bortsett fra den andre av to like timer om
    høsten (`fold=1`): feltene har ingen tidssone, og et slikt klokkeslett tolkes
    alltid som det første (FR-5).
    """
    lokal = tidspunkt.astimezone(OSLO)
    return f"{lokal:%d.%m.%Y}", f"{lokal:%H:%M}"


def vis_tidspunkt(tidspunkt: datetime, *, na: datetime | None = None) -> str:
    """«I dag kl. 07:00», «I morgen kl. 07:00» eller «Lørdag 14. nov. kl. 12:00» i norsk tid.

    Året tas med når det ikke er inneværende år: «Mandag 1. feb. 2027 kl. 09:00».
    """
    lokal = tidspunkt.astimezone(OSLO)
    i_dag_ = (na or klokke.na()).astimezone(OSLO).date()
    kl = f"kl. {lokal:%H:%M}"
    if lokal.date() == i_dag_:
        return f"I dag {kl}"
    if lokal.date() == i_dag_ + timedelta(days=1):
        return f"I morgen {kl}"
    dato = f"{_UKEDAGER[lokal.weekday()]} {lokal.day}. {_MANEDER[lokal.month - 1]}"
    if lokal.year != i_dag_.year:
        dato += f" {lokal.year}"
    return f"{dato} {kl}"
