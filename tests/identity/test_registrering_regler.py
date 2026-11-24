"""Reglene for registrering i `identity/service.py` (FR-1, AD-2, AD-6, AD-17, NFR-4, NFR-10).

Testene kaller servicen direkte. HTTP-testene for de samme radene i I/O-matrisen
står i `test_registrering.py`.
"""

from __future__ import annotations

import unicodedata
from datetime import date, datetime, timedelta, timezone

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.feil import RegelBrudd
from app.core.tid import FODSELSDATO_FORMAT, SJEKK_FODSELSDATO, SKRIV_FODSELSDATO
from app.identity import service
from app.identity.models import Bruker, Sesjon
from app.identity.service import (
    EPOST_FORMAT,
    EPOST_I_BRUK,
    NAVN_FOR_LANGT,
    PASSORD_LENGDE,
    POSTNUMMER_UKJENT,
    SKRIV_EPOST,
    SKRIV_NAVN,
    SKRIV_NYTT_PASSORD,
    SKRIV_POSTNUMMER,
    SKRIV_TELEFON,
    TELEFON_FORMAT,
    UNDER_18,
    hash_sesjonsnokkel,
    normaliser_telefon,
    opprett_sesjon,
    registrer,
    sjekk_epostformat,
    sjekk_passord,
)

# Tirsdag 24. november 2026 kl. 13 i Oslo.
T0 = datetime(2026, 11, 24, 12, 0, tzinfo=timezone.utc)

GYLDIG = {
    "navn": "Kari Nordmann",
    "epost": " Kari@X.no ",
    "passord": "hemmelig-1",
    "telefon": "+47 912 34 567",
    "postnummer": "0571",
    "fodselsdato": "03.05.1954",
}


@pytest.fixture(autouse=True)
def _klokke(sett_na) -> None:
    sett_na(T0)


def registrer_med(db: Session, **endringer: str) -> str:
    return registrer(db, **{**GYLDIG, **endringer})


def feil_ved(db: Session, **endringer: str) -> list[tuple[str, str]]:
    with pytest.raises(RegelBrudd) as brudd:
        registrer_med(db, **endringer)
    return brudd.value.feil


def antall_brukere(db: Session) -> int:
    return db.scalar(select(func.count()).select_from(Bruker))


# ---------- gyldig registrering ----------


def test_gyldig_registrering_lagrer_normaliserte_verdier(db: Session) -> None:
    """FR-1, NFR-4: e-post med små bokstaver, telefon som åtte siffer, passord bare som hash."""
    nokkel = registrer_med(db)
    bruker = db.scalars(select(Bruker)).one()
    assert bruker.navn == "Kari Nordmann"
    assert bruker.epost == "kari@x.no"
    assert bruker.telefon == "91234567"
    assert bruker.postnummer == "0571"
    assert bruker.fodselsdato == date(1954, 5, 3)
    assert bruker.opprettet == T0
    assert bruker.slettet_tidspunkt is None
    assert bruker.passord_hash != GYLDIG["passord"]
    assert GYLDIG["passord"] not in bruker.passord_hash
    assert sjekk_passord(GYLDIG["passord"], bruker.passord_hash)

    sesjon = db.scalars(select(Sesjon)).one()
    assert sesjon.bruker_id == bruker.id
    assert sesjon.nokkel == hash_sesjonsnokkel(nokkel)
    assert sesjon.utloper == T0 + timedelta(days=7)


def test_navn_trimmes_og_nfc_normaliseres(db: Session) -> None:
    dekomponert = unicodedata.normalize("NFD", "  Åse Ødegård  ")
    registrer_med(db, navn=dekomponert)
    assert db.scalars(select(Bruker.navn)).one() == "Åse Ødegård"


def test_kontrolltegn_i_navn_blir_mellomrom(db: Session) -> None:
    """NUL ville gitt DataError i Postgres."""
    registrer_med(db, navn="Kari\x00Nordmann\n")
    assert db.scalars(select(Bruker.navn)).one() == "Kari Nordmann"


# ---------- navn ----------


@pytest.mark.parametrize("navn", ["K", "K" * 80, unicodedata.normalize("NFD", "é") * 80])
def test_navn_som_godtas(db: Session, navn: str) -> None:
    """1 og 80 tegn godtas. Lengden telles etter NFC, så 80 «é» med kombinerende tegn godtas."""
    registrer_med(db, navn=navn)
    assert antall_brukere(db) == 1


@pytest.mark.parametrize(
    ("navn", "melding"),
    [("", SKRIV_NAVN), ("   ", SKRIV_NAVN), ("\x00", SKRIV_NAVN), ("K" * 81, NAVN_FOR_LANGT)],
)
def test_navn_som_avvises(db: Session, navn: str, melding: str) -> None:
    assert feil_ved(db, navn=navn) == [("navn", melding)]


# ---------- e-post ----------


@pytest.mark.parametrize(
    ("epost", "gyldig"),
    [
        ("kari@x.no", True),
        ("kari.nordmann+test@post.eksempel.no", True),
        ("æøå@eksempel.no", True),
        ("kari@x", False),
        ("kari", False),
        ("@x.no", False),
        ("kari@@x.no", False),
        ("kari@x@y.no", False),
        ("kari @x.no", False),
        ("kari@.no", False),
        ("kari@x.no.", False),
        ("kari\x00@x.no", False),
        ("", False),
        ("a@" + "b" * 316 + ".no", False),  # 321 tegn
        ("a@" + "b" * 315 + ".no", True),  # 320 tegn
    ],
)
def test_sjekk_epostformat(epost: str, gyldig: bool) -> None:
    assert sjekk_epostformat(epost) is gyldig


@pytest.mark.parametrize(
    ("epost", "melding"), [("", SKRIV_EPOST), ("  ", SKRIV_EPOST), ("kari", EPOST_FORMAT)]
)
def test_epost_som_avvises(db: Session, epost: str, melding: str) -> None:
    assert feil_ved(db, epost=epost) == [("epost", melding)]


def test_epost_i_bruk_uavhengig_av_store_bokstaver(db: Session, lag_bruker) -> None:
    """FR-1: `KARI@x.no` finnes som `kari@x.no`; ingen ny rad."""
    lag_bruker(epost="kari@x.no")
    assert feil_ved(db, epost="KARI@x.no") == [("epost", EPOST_I_BRUK)]
    assert antall_brukere(db) == 1


def test_epost_slaas_ikke_opp_med_ugyldig_format(db: Session, monkeypatch) -> None:
    def skal_ikke_kalles(*_args):
        raise AssertionError("e-posten skal ikke slås opp")

    monkeypatch.setattr(service, "_epost_i_bruk", skal_ikke_kalles)
    assert feil_ved(db, epost="kari") == [("epost", EPOST_FORMAT)]


def test_samtidig_registrering_gir_en_rad(db: Session, lag_bruker, monkeypatch) -> None:
    """AD-17: forhåndssjekken passeres, men unik-constrainten stopper den andre innsettingen.

    `IntegrityError` i `begin_nested()` blir e-postfeilen, og transaksjonen kan brukes videre.
    """
    lag_bruker(epost="kari@x.no")
    monkeypatch.setattr(service, "_epost_i_bruk", lambda *_args: False)
    assert feil_ved(db) == [("epost", EPOST_I_BRUK)]
    assert antall_brukere(db) == 1
    assert db.scalars(select(Sesjon)).all() == []
    # Transaksjonen er fortsatt brukbar: en annen e-post går fint.
    registrer_med(db, epost="ola@x.no")
    assert antall_brukere(db) == 2


# ---------- passord ----------


@pytest.mark.parametrize("passord", ["a" * 8, "a" * 64, " " * 3 + "abcde", "æ" * 64])
def test_passord_som_godtas(db: Session, passord: str) -> None:
    """8 og 64 tegn godtas. Passordet trimmes ikke, så «   abcde» har 8 tegn."""
    registrer_med(db, passord=passord)
    assert sjekk_passord(passord, db.scalars(select(Bruker.passord_hash)).one())


@pytest.mark.parametrize(
    ("passord", "melding"),
    [
        ("", SKRIV_NYTT_PASSORD),
        ("        ", SKRIV_NYTT_PASSORD),  # bare mellomrom er tomt
        ("a" * 7, PASSORD_LENGDE),
        ("a" * 65, PASSORD_LENGDE),
        (" " * 30 + "a" * 35, PASSORD_LENGDE),  # 65 tegn med mellomrommene: trimmes ikke
    ],
)
def test_passord_som_avvises(db: Session, passord: str, melding: str) -> None:
    assert feil_ved(db, passord=passord) == [("passord", melding)]


# ---------- telefon ----------


@pytest.mark.parametrize(
    ("telefon", "forventet"),
    [
        ("91234567", "91234567"),
        ("912 34 567", "91234567"),
        ("+47 912 34 567", "91234567"),
        ("0047 91234567", "91234567"),
        (" +4791234567 ", "91234567"),
        ("9123456", None),
        ("+46 91234567", None),
        ("912-34-567", None),
        ("4791234567", None),
        ("+47 +47 91234567", None),
        ("٩١٢٣٤٥٦٧", None),
        ("", None),
        (None, None),
    ],
)
def test_normaliser_telefon(telefon: str | None, forventet: str | None) -> None:
    assert normaliser_telefon(telefon) == forventet


@pytest.mark.parametrize(
    ("telefon", "melding"),
    [
        ("", SKRIV_TELEFON),
        ("   ", SKRIV_TELEFON),
        ("9123456", TELEFON_FORMAT),
        ("912-34-567", TELEFON_FORMAT),
    ],
)
def test_telefon_som_avvises(db: Session, telefon: str, melding: str) -> None:
    assert feil_ved(db, telefon=telefon) == [("telefon", melding)]


# ---------- postnummer ----------


def test_postnummer_med_mellomrom_godtas(db: Session) -> None:
    registrer_med(db, postnummer=" 5006 ")
    assert db.scalars(select(Bruker.postnummer)).one() == "5006"


@pytest.mark.parametrize(
    ("postnummer", "melding"),
    [
        ("", SKRIV_POSTNUMMER),
        ("  ", SKRIV_POSTNUMMER),
        ("9999", POSTNUMMER_UKJENT),
        ("0001", POSTNUMMER_UKJENT),  # postboks (P)
        ("0018", POSTNUMMER_UKJENT),  # service (S)
        ("57", POSTNUMMER_UKJENT),
        ("05711", POSTNUMMER_UKJENT),
    ],
)
def test_postnummer_som_avvises(db: Session, postnummer: str, melding: str) -> None:
    assert feil_ved(db, postnummer=postnummer) == [("postnummer", melding)]


# ---------- fødselsdato og alder ----------


def test_fyller_18_i_dag_godtas(db: Session) -> None:
    registrer_med(db, fodselsdato="24.11.2008")
    assert antall_brukere(db) == 1


def test_fyller_18_i_morgen_avvises(db: Session) -> None:
    assert feil_ved(db, fodselsdato="25.11.2008") == [("fodselsdato", UNDER_18)]


def test_i_dag_er_norsk_dato(db: Session, sett_na) -> None:
    """23:30 UTC 23. november er 24. november i Oslo, så den som fyller 18 den 24., godtas."""
    sett_na(datetime(2026, 11, 23, 23, 30, tzinfo=timezone.utc))
    registrer_med(db, fodselsdato="24.11.2008")
    assert antall_brukere(db) == 1


@pytest.mark.parametrize(
    ("i_dag_utc", "godtatt"),
    [
        (datetime(2026, 2, 28, 12, 0, tzinfo=timezone.utc), False),
        (datetime(2026, 3, 1, 12, 0, tzinfo=timezone.utc), True),
    ],
)
def test_fodt_29_februar(db: Session, sett_na, i_dag_utc: datetime, godtatt: bool) -> None:
    """Født 29.02.2008 fyller 18 den 1. mars 2026."""
    sett_na(i_dag_utc)
    if godtatt:
        registrer_med(db, fodselsdato="29.02.2008")
        assert antall_brukere(db) == 1
    else:
        assert feil_ved(db, fodselsdato="29.02.2008") == [("fodselsdato", UNDER_18)]


@pytest.mark.parametrize(
    ("fodselsdato", "melding"),
    [
        ("", SKRIV_FODSELSDATO),
        ("abc", FODSELSDATO_FORMAT),
        ("1954.05.03", FODSELSDATO_FORMAT),
        ("31.02.1990", SJEKK_FODSELSDATO),
        ("25.11.2026", SJEKK_FODSELSDATO),  # fram i tid
        ("23.11.1906", SJEKK_FODSELSDATO),  # i dag minus 120 år minus én dag
        ("03.12.08", UNDER_18),  # tosifret år blir 2008, ikke 1908
    ],
)
def test_fodselsdato_som_avvises(db: Session, fodselsdato: str, melding: str) -> None:
    assert feil_ved(db, fodselsdato=fodselsdato) == [("fodselsdato", melding)]


@pytest.mark.parametrize("fodselsdato", ["3.5.54", "03-05-1954", "24.11.1906"])
def test_fodselsdato_som_godtas(db: Session, fodselsdato: str) -> None:
    registrer_med(db, fodselsdato=fodselsdato)
    assert antall_brukere(db) == 1


# ---------- flere feil ----------


def test_alle_feil_samles_i_feltrekkefolge(db: Session, lag_bruker) -> None:
    """NFR-10: alle feilene kommer samtidig, i rekkefølgen feltene står i skjemaet."""
    lag_bruker(epost="kari@x.no")
    feil = feil_ved(
        db,
        navn=" ",
        epost="kari@x.no",
        passord="kort",
        telefon="123",
        postnummer="9999",
        fodselsdato="01.01.2015",
    )
    assert feil == [
        ("navn", SKRIV_NAVN),
        ("epost", EPOST_I_BRUK),
        ("passord", PASSORD_LENGDE),
        ("telefon", TELEFON_FORMAT),
        ("postnummer", POSTNUMMER_UKJENT),
        ("fodselsdato", UNDER_18),
    ]
    assert antall_brukere(db) == 1


def test_manglende_felt_gir_skriv_feil(db: Session) -> None:
    with pytest.raises(RegelBrudd) as brudd:
        registrer(
            db, navn=None, epost=None, passord=None, telefon=None, postnummer=None, fodselsdato=None
        )
    assert [felt for felt, _ in brudd.value.feil] == [
        "navn",
        "epost",
        "passord",
        "telefon",
        "postnummer",
        "fodselsdato",
    ]


# ---------- opprett_sesjon ----------


def test_opprett_sesjon_sletter_gammel_og_utlopte(db: Session, lag_bruker, sett_na) -> None:
    """Felles for innlogging og registrering: 7 dager, bare hashen lagres."""
    bruker = lag_bruker()
    sett_na(T0 - timedelta(days=8))
    utlopt = opprett_sesjon(db, bruker.id)
    sett_na(T0 - timedelta(days=1))
    gammel = opprett_sesjon(db, bruker.id)
    sett_na(T0)
    ny = opprett_sesjon(db, bruker.id, gammel_nokkel=gammel)
    nokler = set(db.scalars(select(Sesjon.nokkel)))
    assert nokler == {hash_sesjonsnokkel(ny)}
    assert hash_sesjonsnokkel(utlopt) not in nokler
    assert ny not in nokler
