"""Passord og e-post behandles bare i `identity/service.py` (NFR-4, AD-6, AR-16)."""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from sqlalchemy import select

from app.identity import service
from app.identity.models import Bruker
from app.identity.service import (
    hash_passord,
    normaliser_epost,
    passord_har_gyldig_lengde,
    sjekk_innloggingsskjema,
    sjekk_passord,
)

ROT = Path(__file__).resolve().parents[2]


def test_hashen_inneholder_ikke_passordet_og_har_testkostnad() -> None:
    """NFR-4: bare bcrypt-hash. Kostnad 4 i test, 12 ellers (AR-29)."""
    hash_ = hash_passord("kari-lokal-1")
    assert "kari-lokal-1" not in hash_
    assert hash_.startswith("$2b$04$")
    assert sjekk_passord("kari-lokal-1", hash_)
    assert not sjekk_passord("kari-lokal-2", hash_)


def test_kostnaden_er_12_utenfor_test(monkeypatch: pytest.MonkeyPatch) -> None:
    class Produksjon:
        test = False

    monkeypatch.setattr(service, "hent_settings", lambda: Produksjon())
    assert service._kostnad() == 12


def test_passord_i_databasen_er_hash(db, lag_bruker) -> None:
    """NFR-4: `passord_hash` inneholder ikke passordet."""
    bruker = lag_bruker(passord="hemmelig-123")
    lagret = db.scalar(select(Bruker.passord_hash).where(Bruker.id == bruker.id))
    assert "hemmelig-123" not in lagret
    assert lagret.startswith("$2b$")


def test_passord_nfc_normaliseres_men_trimmes_ikke() -> None:
    """AD-6: «å» skrevet som én eller to kodepunkter er samme passord; mellomrom teller."""
    hash_ = hash_passord("blåbær-123")
    assert sjekk_passord("blåbær-123", hash_)
    assert not sjekk_passord(" blåbær-123", hash_)
    assert not sjekk_passord("blåbær-123 ", hash_)


def test_langt_passord_over_72_byte_virker() -> None:
    """AD-6: 64 tegn med æøå er over 72 byte i UTF-8, som bcrypt 5 ellers avviser."""
    passord = "æøå" * 21 + "x"
    assert len(passord) == 64 and len(passord.encode("utf-8")) > 72
    hash_ = hash_passord(passord)
    assert sjekk_passord(passord, hash_)
    assert not sjekk_passord(passord[:-1] + "y", hash_)


def test_sjekk_passord_uten_hash_gir_false() -> None:
    assert sjekk_passord("hva-som-helst", None) is False
    assert sjekk_passord("hva-som-helst", "ikke-en-hash") is False


@pytest.mark.parametrize(
    ("inn", "ut"),
    [
        (" Kari@Eksempel.no ", "kari@eksempel.no"),
        ("KARI@EKSEMPEL.NO", "kari@eksempel.no"),
        ("åse@eksempel.no", "åse@eksempel.no"),
        (None, ""),
        ("   ", ""),
    ],
)
def test_normaliser_epost(inn, ut) -> None:
    """AD-6: trim, NFC og små bokstaver."""
    assert normaliser_epost(inn) == ut


@pytest.mark.parametrize(
    ("passord", "gyldig"),
    [("1234567", False), ("12345678", True), ("x" * 64, True), ("x" * 65, False)],
)
def test_passordlengde(passord: str, gyldig: bool) -> None:
    """FR-1: 8–64 tegn (brukes av `app.admin nytt-passord`)."""
    assert passord_har_gyldig_lengde(passord) is gyldig


def test_tomme_felt_i_innloggingsskjemaet() -> None:
    assert sjekk_innloggingsskjema("", "") == [
        ("epost", "Skriv e-postadressen din."),
        ("passord", "Skriv passordet ditt."),
    ]
    assert sjekk_innloggingsskjema("   ", "x") == [("epost", "Skriv e-postadressen din.")]
    assert sjekk_innloggingsskjema("a@b.no", "   ") == [("passord", "Skriv passordet ditt.")]
    assert sjekk_innloggingsskjema("a@b.no", "x") == []


def test_bare_identity_service_kaller_bcrypt() -> None:
    """AD-6: ingen annen kode i app/ kaller bcrypt."""
    funn = []
    for fil in sorted((ROT / "app").rglob("*.py")):
        if fil == ROT / "app" / "identity" / "service.py":
            continue
        if re.search(r"\bbcrypt\b", fil.read_text(encoding="utf-8")):
            funn.append(fil.relative_to(ROT).as_posix())
    assert funn == []
