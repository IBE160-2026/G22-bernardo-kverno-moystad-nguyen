"""Dato i norsk tid, tolkning av fødselsdato og oppdragstid, og visning av tidspunkt
(FR-1, FR-5, AD-9, AR-19).

Tabelltester for skrivemåter, tosifret år, 29. februar, grensene ved 18 og 120 år,
grensene for oppdragstid (fram i tid, høyst 12 måneder), sommertid og rundturen.
"""

from __future__ import annotations

import zoneinfo
from datetime import date, datetime, timedelta, timezone

import pytest

from app.core import tid
from app.core.feil import RegelBrudd
from app.core.tid import (
    DATO_FINNES_IKKE,
    DATO_FORMAT,
    FODSELSDATO_FORMAT,
    KLOKKESLETT_FINNES_IKKE,
    KLOKKESLETT_FORMAT,
    SJEKK_FODSELSDATO,
    SKRIV_DATO,
    SKRIV_FODSELSDATO,
    SKRIV_KLOKKESLETT,
    TIDSPUNKT_FOR_LANGT_FRAM,
    TIDSPUNKT_PASSERT,
    er_myndig,
    fyller_ar,
    seneste_tidspunkt,
    skjemaverdier,
    tidligste_fodselsdato,
    tolk_fodselsdato,
    tolk_tidspunkt,
    vis_tidspunkt,
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


def test_europe_oslo_finnes_i_tzdata_pakken() -> None:
    """AD-9: Europe/Oslo løses fra `tzdata`, også uten tidssonedata i operativsystemet (Vercel)."""
    opprinnelig = zoneinfo.TZPATH
    try:
        zoneinfo.reset_tzpath(to=[])
        oslo = zoneinfo.ZoneInfo.no_cache("Europe/Oslo")
    finally:
        zoneinfo.reset_tzpath(to=opprinnelig)
    assert datetime(2026, 11, 24, 12, 0, tzinfo=oslo).utcoffset() == timedelta(hours=1)


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


# ---------- oppdragstid (FR-5, AR-19) ----------

UTC = timezone.utc
# Tirsdag 24. november 2026 kl. 13:00 norsk tid (spec 2.1, I/O-matrisen).
NA = datetime(2026, 11, 24, 12, 0, tzinfo=UTC)
# 1. november 2026, så 14.11.2026 er fram i tid.
NA_TIDLIG = datetime(2026, 11, 1, 12, 0, tzinfo=UTC)


def tidsfeil(dato: str | None, klokkeslett: str | None, na: datetime = NA) -> list[tuple[str, str]]:
    with pytest.raises(RegelBrudd) as brudd:
        tolk_tidspunkt(dato, klokkeslett, na=na)
    return brudd.value.feil


@pytest.mark.parametrize("dato", ["14.11.2026", "14/11/26", "14-11-2026", "14 11 2026", "14.11.26", " 14.11.2026 "])
@pytest.mark.parametrize("klokkeslett", ["07:00", "7", "0700", "7.00", "7:00", "07", " 07:00 "])
def test_skrivemater_gir_samme_tidspunkt(dato: str, klokkeslett: str) -> None:
    """FR-5, AD-9: alle skrivemåtene gir 14.11.2026 kl. 07:00 norsk tid, som er 06:00 UTC."""
    tidspunkt = tolk_tidspunkt(dato, klokkeslett, na=NA_TIDLIG)
    assert tidspunkt == datetime(2026, 11, 14, 6, 0, tzinfo=UTC)
    assert tidspunkt.utcoffset() == timedelta(0)


def test_tosifret_ar_er_alltid_20xx() -> None:
    """AD-9: tosifret år betyr 20xx, også når 19xx ville vært nærmere (ulikt fødselsdato)."""
    assert tolk_tidspunkt("25.11.26", "12:00", na=NA) == datetime(2026, 11, 25, 11, 0, tzinfo=UTC)
    assert tidsfeil("25.11.99", "12:00") == [("nar", TIDSPUNKT_FOR_LANGT_FRAM)]


@pytest.mark.parametrize(
    ("klokkeslett", "forventet"),
    [("0:00", (0, 0)), ("23:59", (23, 59)), ("2359", (23, 59)), ("9.30", (9, 30)), ("12", (12, 0))],
)
def test_klokkeslett_grenser(klokkeslett: str, forventet: tuple[int, int]) -> None:
    tidspunkt = tolk_tidspunkt("14.12.2026", klokkeslett, na=NA)
    lokal = tidspunkt.astimezone(tid.OSLO)
    assert (lokal.hour, lokal.minute) == forventet


@pytest.mark.parametrize(
    "klokkeslett",
    ["700", "24:00", "07:60", "7:5", "07-00", "kl 7", "07:00:00", "٠٧:٠٠", "abc", "7,00", "12345"],
)
def test_klokkeslett_med_feil_format(klokkeslett: str) -> None:
    assert tidsfeil("14.12.2026", klokkeslett) == [("klokkeslett", KLOKKESLETT_FORMAT)]


@pytest.mark.parametrize("dato", ["14.12", "2026.12.14", "14.12.026", "14.12/2026", "i morgen", "14.12.2026."])
def test_dato_med_feil_format(dato: str) -> None:
    assert tidsfeil(dato, "12:00") == [("dato", DATO_FORMAT)]


@pytest.mark.parametrize("dato", ["31.11.2026", "29.02.2027", "00.12.2026", "14.13.2026", "32.12.2026"])
def test_dato_som_ikke_finnes(dato: str) -> None:
    assert tidsfeil(dato, "12:00") == [("dato", DATO_FINNES_IKKE)]


def test_29_februar_i_skuddar_godtas() -> None:
    tidspunkt = tolk_tidspunkt("29.02.28", "12:00", na=datetime(2027, 12, 1, tzinfo=UTC))
    assert tidspunkt == datetime(2028, 2, 29, 11, 0, tzinfo=UTC)


@pytest.mark.parametrize("tom", ["", "   ", None])
def test_tomme_felt_gir_begge_feilene(tom: str | None) -> None:
    """NFR-10: feil i både dato og klokkeslett kommer samtidig, i feltrekkefølge."""
    assert tidsfeil(tom, tom) == [("dato", SKRIV_DATO), ("klokkeslett", SKRIV_KLOKKESLETT)]
    assert tidsfeil("x", "y") == [("dato", DATO_FORMAT), ("klokkeslett", KLOKKESLETT_FORMAT)]


def test_naa_er_passert_og_ett_minutt_etter_godtas() -> None:
    """FR-5: «fram i tid» betyr `> nå`. Tidspunktet lik nå gir feilen under «Når?»."""
    assert tidsfeil("24.11.2026", "13:00") == [("nar", TIDSPUNKT_PASSERT)]
    assert tidsfeil("23.11.2026", "18:00") == [("nar", TIDSPUNKT_PASSERT)]
    assert tolk_tidspunkt("24.11.2026", "13:01", na=NA) == datetime(2026, 11, 24, 12, 1, tzinfo=UTC)


@pytest.mark.parametrize(
    ("dato", "klokkeslett", "melding"),
    [("01.01.0001", "00:00", TIDSPUNKT_PASSERT), ("31.12.9999", "23:59", TIDSPUNKT_FOR_LANGT_FRAM)],
)
def test_ytterste_ar_gir_vanlig_feil(dato: str, klokkeslett: str, melding: str) -> None:
    """År som ikke kan regnes om til UTC, gir feilen under «Når?», ikke `OverflowError`."""
    assert tidsfeil(dato, klokkeslett) == [("nar", melding)]


def test_grensen_ved_12_maneder() -> None:
    """FR-5: samme dato og klokkeslett om ett år godtas; ett minutt etter avvises."""
    assert seneste_tidspunkt(NA) == datetime(2027, 11, 24, 12, 0, tzinfo=UTC)
    assert tolk_tidspunkt("24.11.2027", "13:00", na=NA) == datetime(2027, 11, 24, 12, 0, tzinfo=UTC)
    assert tidsfeil("24.11.2027", "13:01") == [("nar", TIDSPUNKT_FOR_LANGT_FRAM)]


def test_grensen_fra_29_februar_er_1_mars() -> None:
    """Som `fyller_ar`: fra 29.02.2028 kl. 12 er grensen 01.03.2029 kl. 12 norsk tid."""
    na = datetime(2028, 2, 29, 11, 0, tzinfo=UTC)  # kl. 12 i Oslo
    assert seneste_tidspunkt(na) == datetime(2029, 3, 1, 11, 0, tzinfo=UTC)


def test_12_maneder_regnes_i_norsk_tid_over_sommertid() -> None:
    """Fra 1. juli kl. 12 (UTC+2) er grensen 1. juli året etter kl. 12 norsk tid, ikke 12 UTC."""
    na = datetime(2026, 7, 1, 10, 0, tzinfo=UTC)
    assert seneste_tidspunkt(na) == datetime(2027, 7, 1, 10, 0, tzinfo=UTC)


@pytest.mark.parametrize("klokkeslett", ["02:00", "02:30", "02:59"])
def test_klokkeslett_som_ikke_finnes_om_varen(klokkeslett: str) -> None:
    """AD-9: natt til 28.03.2027 stilles klokka fra 02:00 til 03:00. Feilen står ved Klokkeslett."""
    assert tidsfeil("28.03.2027", klokkeslett) == [("klokkeslett", KLOKKESLETT_FINNES_IKKE)]


@pytest.mark.parametrize(
    ("dato", "klokkeslett", "utc"),
    [
        ("28.03.2027", "01:59", datetime(2027, 3, 28, 0, 59, tzinfo=UTC)),
        ("28.03.2027", "03:00", datetime(2027, 3, 28, 1, 0, tzinfo=UTC)),
        # Natt til 31.10.2027 stilles klokka tilbake: 02:30 finnes to ganger, og den første brukes.
        ("31.10.2027", "02:30", datetime(2027, 10, 31, 0, 30, tzinfo=UTC)),
        ("31.10.2027", "01:59", datetime(2027, 10, 30, 23, 59, tzinfo=UTC)),
        ("31.10.2027", "03:00", datetime(2027, 10, 31, 2, 0, tzinfo=UTC)),
    ],
)
def test_sommertid_skiftene(dato: str, klokkeslett: str, utc: datetime) -> None:
    assert tolk_tidspunkt(dato, klokkeslett, na=NA) == utc


@pytest.mark.parametrize(
    ("dato", "klokkeslett", "for_skiftet", "etter_skiftet", "na_etter"),
    [
        ("27.03.2027", "12:00", "Lørdag 27. mars 2027 kl. 12:00", "Lørdag 27. mars kl. 12:00",
         datetime(2027, 4, 1, tzinfo=UTC)),
        ("28.03.2027", "03:30", "Søndag 28. mars 2027 kl. 03:30", "Søndag 28. mars kl. 03:30",
         datetime(2027, 4, 1, tzinfo=UTC)),
        ("15.07.2027", "09:00", "Torsdag 15. juli 2027 kl. 09:00", "Torsdag 15. juli kl. 09:00",
         datetime(2027, 11, 5, tzinfo=UTC)),
        ("31.10.2027", "02:30", "Søndag 31. okt. 2027 kl. 02:30", "Søndag 31. okt. kl. 02:30",
         datetime(2027, 11, 5, tzinfo=UTC)),
    ],
)
def test_rundtur_over_skiftene(
    dato: str, klokkeslett: str, for_skiftet: str, etter_skiftet: str, na_etter: datetime
) -> None:
    """AD-9: tolket før skiftet, vist før og etter skiftet med samme dato og klokkeslett."""
    tidspunkt = tolk_tidspunkt(dato, klokkeslett, na=NA)
    assert vis_tidspunkt(tidspunkt, na=NA) == for_skiftet
    assert vis_tidspunkt(tidspunkt, na=na_etter) == etter_skiftet


# ---------- skjemaverdier (FR-6, AD-9, story 2.5) ----------


@pytest.mark.parametrize(
    ("utc", "dato", "klokkeslett"),
    [
        (datetime(2026, 11, 25, 8, 0, tzinfo=UTC), "25.11.2026", "09:00"),
        (datetime(2027, 1, 4, 23, 30, tzinfo=UTC), "05.01.2027", "00:30"),  # dato i norsk tid
        (datetime(2027, 3, 28, 0, 59, tzinfo=UTC), "28.03.2027", "01:59"),  # før vårskiftet
        (datetime(2027, 3, 28, 1, 0, tzinfo=UTC), "28.03.2027", "03:00"),  # etter vårskiftet
        (datetime(2027, 7, 15, 7, 0, tzinfo=UTC), "15.07.2027", "09:00"),  # sommertid
        (datetime(2027, 10, 31, 0, 30, tzinfo=UTC), "31.10.2027", "02:30"),  # første 02:30 om høsten
        (datetime(2027, 10, 31, 2, 0, tzinfo=UTC), "31.10.2027", "03:00"),  # etter høstskiftet
    ],
)
def test_skjemaverdier_og_rundtur(utc: datetime, dato: str, klokkeslett: str) -> None:
    """AD-9: lagret tidspunkt → «dd.mm.åååå» og «tt:mm» i norsk tid → `tolk_tidspunkt` gir det samme."""
    assert skjemaverdier(utc) == (dato, klokkeslett)
    assert tolk_tidspunkt(dato, klokkeslett, na=NA) == utc


def test_skjemaverdier_andre_av_to_like_timer_tolkes_som_den_forste() -> None:
    """AD-9: andre 02:30 om høsten (fold=1) vises som 02:30, og 02:30 tolkes alltid som den første."""
    andre = datetime(2027, 10, 31, 1, 30, tzinfo=UTC)
    assert skjemaverdier(andre) == ("31.10.2027", "02:30")
    assert tolk_tidspunkt("31.10.2027", "02:30", na=NA) == andre - timedelta(hours=1)


# ---------- visning (FR-5, EXPERIENCE.md § Formater) ----------


@pytest.mark.parametrize(
    ("utc", "forventet"),
    [
        (datetime(2026, 11, 24, 14, 0, tzinfo=UTC), "I dag kl. 15:00"),
        (datetime(2026, 11, 24, 22, 59, tzinfo=UTC), "I dag kl. 23:59"),
        (datetime(2026, 11, 24, 23, 0, tzinfo=UTC), "I morgen kl. 00:00"),
        (datetime(2026, 11, 25, 6, 0, tzinfo=UTC), "I morgen kl. 07:00"),
        (datetime(2026, 11, 26, 6, 0, tzinfo=UTC), "Torsdag 26. nov. kl. 07:00"),
        (datetime(2026, 11, 28, 11, 0, tzinfo=UTC), "Lørdag 28. nov. kl. 12:00"),
        (datetime(2026, 11, 23, 8, 0, tzinfo=UTC), "Mandag 23. nov. kl. 09:00"),
        (datetime(2026, 12, 6, 17, 30, tzinfo=UTC), "Søndag 6. des. kl. 18:30"),
        (datetime(2027, 2, 1, 8, 0, tzinfo=UTC), "Mandag 1. feb. 2027 kl. 09:00"),
    ],
)
def test_vis_tidspunkt(utc: datetime, forventet: str) -> None:
    """«I dag», «I morgen» og ukedag med stor forbokstav; år når det ikke er i år."""
    assert vis_tidspunkt(utc, na=NA) == forventet


def test_vis_tidspunkt_bruker_klokka(sett_na) -> None:
    sett_na(NA)
    assert vis_tidspunkt(datetime(2026, 11, 25, 6, 0, tzinfo=UTC)) == "I morgen kl. 07:00"


@pytest.mark.parametrize(
    ("maned", "forkortet"),
    list(zip(range(1, 13), ["jan.", "feb.", "mars", "apr.", "mai", "juni", "juli", "aug.", "sep.", "okt.", "nov.", "des."])),
)
def test_manedene_forkortes(maned: int, forkortet: str) -> None:
    na = datetime(2030, 6, 1, tzinfo=UTC)
    tekst = vis_tidspunkt(datetime(2030, maned, 15, 10, 0, tzinfo=UTC), na=na)
    assert f" 15. {forkortet} kl. " in tekst
