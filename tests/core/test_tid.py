"""Dato i norsk tid og tolkning av fødselsdato (FR-1, AD-9, AR-19).

Tabelltester for skrivemåter, tosifret år, 29. februar og grensene ved 18 og 120 år.
"""

from __future__ import annotations

from datetime import date, datetime, timezone

import pytest

from app.core import tid
from app.core.feil import RegelBrudd
from app.core.tid import (
    FODSELSDATO_FORMAT,
    SJEKK_FODSELSDATO,
    SKRIV_FODSELSDATO,
    er_myndig,
    fyller_ar,
    tidligste_fodselsdato,
    tolk_fodselsdato,
)

I_DAG = date(2026, 11, 24)


def feil_for(tekst: str | None, i_dag: date = I_DAG) -> list[tuple[str, str]]:
    with pytest.raises(RegelBrudd) as brudd:
        tolk_fodselsdato(tekst, i_dag=i_dag)
    return brudd.value.feil


# ---------- «i dag» i Europe/Oslo ----------


@pytest.mark.parametrize(
    ("utc", "forventet"),
    [
        # Vintertid (UTC+1): 23:30 UTC er allerede neste dag i Oslo.
        (datetime(2026, 11, 23, 23, 30, tzinfo=timezone.utc), date(2026, 11, 24)),
        (datetime(2026, 11, 23, 22, 59, tzinfo=timezone.utc), date(2026, 11, 23)),
        # Sommertid (UTC+2): 22:30 UTC er neste dag i Oslo.
        (datetime(2026, 6, 30, 22, 30, tzinfo=timezone.utc), date(2026, 7, 1)),
        (datetime(2026, 6, 30, 21, 59, tzinfo=timezone.utc), date(2026, 6, 30)),
    ],
)
def test_i_dag_er_datoen_i_oslo(sett_na, utc: datetime, forventet: date) -> None:
    """AD-9: «i dag» er datoen i Europe/Oslo, regnet fra `klokke.na()`."""
    sett_na(utc)
    assert tid.i_dag() == forventet


# ---------- skrivemåter ----------


@pytest.mark.parametrize(
    ("tekst", "forventet"),
    [
        ("03.05.1954", date(1954, 5, 3)),
        ("3.5.1954", date(1954, 5, 3)),
        ("03/05/1954", date(1954, 5, 3)),
        ("03-05-1954", date(1954, 5, 3)),
        ("03 05 1954", date(1954, 5, 3)),
        ("  03.05.1954  ", date(1954, 5, 3)),
        ("3.5.54", date(1954, 5, 3)),
        ("03.05.08", date(2008, 5, 3)),  # tosifret år: nyeste dato som ikke er fram i tid
        ("24.11.26", date(2026, 11, 24)),  # i dag er ikke fram i tid
        ("25.11.26", date(1926, 11, 25)),  # i morgen i 2026 er fram i tid, så 1926
        ("01.01.00", date(2000, 1, 1)),
    ],
)
def test_godtatte_skrivemater(tekst: str, forventet: date) -> None:
    """FR-1: `.`, `/`, `-` eller mellomrom; dag og måned med ett eller to siffer; år med to eller fire."""
    assert tolk_fodselsdato(tekst, i_dag=I_DAG) == forventet


@pytest.mark.parametrize(
    "tekst",
    [
        "abc",
        "1954.05.03",  # år først
        "03.05.954",  # tresifret år
        "03.05",
        "03.05.1954.",
        "03.05/1954",  # ulike skilletegn
        "03..05.1954",
        "003.05.1954",
        "03.05.19541",
        "٠٣.٠٥.١٩٥٤",  # arabisk-indiske sifre
        "03.05.1954 kl 12",
    ],
)
def test_formatfeil(tekst: str) -> None:
    assert feil_for(tekst) == [("fodselsdato", FODSELSDATO_FORMAT)]


@pytest.mark.parametrize("tekst", ["", "   ", None])
def test_tomt_felt(tekst: str | None) -> None:
    """Felt med bare mellomrom er tomme."""
    assert feil_for(tekst) == [("fodselsdato", SKRIV_FODSELSDATO)]


@pytest.mark.parametrize(
    "tekst", ["31.02.1990", "29.02.2023", "00.05.1954", "03.13.1954", "03.00.1954", "32.01.1990"]
)
def test_dato_som_ikke_finnes(tekst: str) -> None:
    """En dato som ikke finnes, gir «Sjekk fødselsdatoen.»."""
    assert feil_for(tekst) == [("fodselsdato", SJEKK_FODSELSDATO)]


def test_feltnavnet_kan_overstyres() -> None:
    with pytest.raises(RegelBrudd) as brudd:
        tolk_fodselsdato("x", i_dag=I_DAG, felt="dato")
    assert brudd.value.feil == [("dato", FODSELSDATO_FORMAT)]


# ---------- grensene: fram i tid og 120 år ----------


def test_fram_i_tid_avvises() -> None:
    assert feil_for("25.11.2026") == [("fodselsdato", SJEKK_FODSELSDATO)]
    assert tolk_fodselsdato("24.11.2026", i_dag=I_DAG) == I_DAG


def test_grensen_ved_120_ar() -> None:
    """I dag minus 120 år godtas; én dag før avvises."""
    assert tidligste_fodselsdato(I_DAG) == date(1906, 11, 24)
    assert tolk_fodselsdato("24.11.1906", i_dag=I_DAG) == date(1906, 11, 24)
    assert feil_for("23.11.1906") == [("fodselsdato", SJEKK_FODSELSDATO)]


def test_120_ar_tilbake_fra_29_februar() -> None:
    """1900 var ikke skuddår, så grensen fra 29.02.2020 blir 01.03.1900."""
    assert tidligste_fodselsdato(date(2020, 2, 29)) == date(1900, 3, 1)


def test_tosifret_ar_kan_ikke_gi_over_120() -> None:
    """Tosifret år gir alltid en alder fra 0 til 99 år."""
    assert tolk_fodselsdato("23.11.06", i_dag=I_DAG) == date(2006, 11, 23)


# ---------- 18 år og 29. februar ----------


@pytest.mark.parametrize(
    ("fodselsdato", "ar", "forventet"),
    [
        (date(2008, 2, 29), 2026, date(2026, 3, 1)),
        (date(2008, 2, 29), 2028, date(2028, 2, 29)),
        (date(1990, 5, 3), 2026, date(2026, 5, 3)),
    ],
)
def test_fyller_ar(fodselsdato: date, ar: int, forventet: date) -> None:
    """29. februar fyller år 1. mars i år som ikke er skuddår."""
    assert fyller_ar(fodselsdato, ar) == forventet


@pytest.mark.parametrize(
    ("fodselsdato", "i_dag", "myndig"),
    [
        (date(2008, 11, 24), date(2026, 11, 24), True),  # fyller 18 i dag
        (date(2008, 11, 25), date(2026, 11, 24), False),  # fyller 18 i morgen
        (date(2008, 2, 29), date(2026, 2, 28), False),
        (date(2008, 2, 29), date(2026, 3, 1), True),
        (date(2010, 2, 28), date(2028, 2, 28), True),
        (date(1954, 5, 3), date(2026, 11, 24), True),
    ],
)
def test_er_myndig(fodselsdato: date, i_dag: date, myndig: bool) -> None:
    """FR-1: under 18 år avvises; fyller 18 i dag godtas."""
    assert er_myndig(fodselsdato, i_dag) is myndig
