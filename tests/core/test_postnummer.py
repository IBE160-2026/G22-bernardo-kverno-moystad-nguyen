"""Postnumre (AD-1, AD-10, AR-6). Bare gateadresser: Brings kategori G og B (PRD §9.2)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app import lag_app
from app.core import postnummer
from app.core.postnummer import (
    JSON_STI,
    TSV_STI,
    finnes,
    formater_poststed,
    les_tsv,
    normaliser_postnummer,
    poststed,
)


@pytest.mark.parametrize(
    ("verdi", "forventet"),
    [("0571", True), (" 0571 ", True), ("0000", False), ("0001", False), ("8622", True)],
    ids=["gyldig", "mellomrom", "finnes-ikke", "postboks", "mo-i-rana"],
)
def test_finnes(verdi: str, forventet: bool) -> None:
    assert finnes(verdi) is forventet


@pytest.mark.parametrize("verdi", [None, "", "571", "05711", "05 71", "abcd", "٠٥٧١"])
def test_ugyldig_format_finnes_ikke(verdi) -> None:
    assert normaliser_postnummer(verdi) is None
    assert finnes(verdi) is False
    assert poststed(verdi) is None


def test_poststed() -> None:
    assert poststed("0571") == "Oslo"
    assert poststed(" 8622 ") == "Mo i Rana"
    assert poststed("0001") is None


@pytest.mark.parametrize(
    ("bring", "forventet"),
    [
        ("OSLO", "Oslo"),
        ("MO I RANA", "Mo i Rana"),
        ("NES PÅ HEDMARKEN", "Nes på Hedmarken"),
        ("BØ I TELEMARK", "Bø i Telemark"),
        ("ÅLESUND", "Ålesund"),
        ("STOKKE-SANDE", "Stokke-Sande"),
        ("I", "I"),
    ],
)
def test_formater_poststed(bring: str, forventet: str) -> None:
    assert formater_poststed(bring) == forventet


def test_tsv_er_brings_fil_uendret_i_utf8() -> None:
    """AD-10: hele registeret, fem kolonner, UTF-8 og LF."""
    rader = TSV_STI.read_bytes().decode("utf-8").split("\n")
    assert rader[-1] == ""
    rader = rader[:-1]
    assert all(len(r.split("\t")) == 5 for r in rader)
    assert "\r" not in "".join(rader)
    kategorier = {r.split("\t")[4] for r in rader}
    assert kategorier == {"G", "B", "P", "S"}
    assert any("Æ" in r or "Ø" in r or "Å" in r for r in rader)


def test_les_tsv_tar_bare_gateadresser() -> None:
    alle = [r.split("\t") for r in TSV_STI.read_text(encoding="utf-8").splitlines()]
    gate = {r[0] for r in alle if r[4] in ("G", "B")}
    rader = les_tsv()
    assert {n for n, _ in rader} == gate
    assert len(rader) == len(gate) == 3382  # per 2026-11-24
    assert rader == sorted(rader)


def test_postnumre_json_stemmer_med_tsv() -> None:
    """AR-6: den innsjekkede JSON-fila er generert fra TSV-fila og er lik den filtrerte lista."""
    innhold = JSON_STI.read_text(encoding="utf-8")
    assert json.loads(innhold) == dict(les_tsv())
    assert innhold == postnummer.lag_json(), "Kjør `uv run python -m app.core.postnummer`"


def test_manglende_tsv_fil_stopper_oppstarten(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """AR-1, AD-10: følger ikke `data/postnumre.tsv` med (for eksempel i Vercel-funksjonen),
    starter ikke appen. Feilen kommer ved oppstart, ikke ved første postnummeroppslag."""
    monkeypatch.setattr(postnummer, "TSV_STI", tmp_path / "finnes-ikke.tsv")
    postnummer._register.cache_clear()
    try:
        with pytest.raises(FileNotFoundError):
            lag_app()
    finally:
        postnummer._register.cache_clear()


def test_lag_app_laster_postnummerregisteret() -> None:
    """AR-1: registeret ligger i minnet etter oppstart."""
    postnummer._register.cache_clear()
    lag_app()
    assert postnummer._register.cache_info().currsize == 1
