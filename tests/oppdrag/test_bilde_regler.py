"""Reglene for bildet direkte mot `oppdrag/bilde.py` og servicen (spec 2.7).

FR-27, NFR-9, NFR-12, AD-2, AD-18. Formatet bestemmes av innholdet, størrelsen
sjekkes før fila åpnes og pikslene før den dekodes. Resultatet er alltid en ny
JPEG uten metadata, snudd etter EXIF, aldri forstørret, høyst 1 600 px, med en
miniatyr på høyst 640 px. `tolk_bildevalg` kaster aldri, og bildet setter aldri
`vesentlig_endret`. Klokka står fast på tirsdag 24.11.2026 kl. 13:00 norsk tid.
"""

from __future__ import annotations

import base64
import struct
from datetime import datetime, timezone

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.feil import Duplikat, RegelBrudd
from app.oppdrag import bilde
from app.oppdrag.bilde import (
    BILDETEKST_FOR_KORT,
    BILDETEKST_FOR_LANG,
    FEIL_FORMAT,
    FOR_MANGE_PIKSLER,
    FOR_STORT,
    MAKS_BYTE,
    MAKS_PIKSLER,
    SKRIV_BILDETEKST,
    behandle,
    fra_beholdt,
    til_beholdt,
)
from app.oppdrag.models import Oppdrag, Oppdragsbilde
from app.oppdrag.service import (
    Bildevalg,
    opprett_oppdrag,
    rediger_oppdrag,
    slett_bilde,
    tolk_bildevalg,
    valider_oppdrag,
)
from tests import bilder

T0 = datetime(2026, 11, 24, 12, 0, tzinfo=timezone.utc)
I_MORGEN_9 = datetime(2026, 11, 25, 8, 0, tzinfo=timezone.utc)
TIDLIGERE = datetime(2026, 11, 1, 10, 0, tzinfo=timezone.utc)

SAMME = {
    "beskrivelse": "Trenger noen som kan måke snø i innkjørselen min i morgen.",
    "tittel": "Måke snø i innkjørselen",
    "kategori": "snomaking",
    "postnummer": "0571",
    "dato": "25.11.2026",
    "klokkeslett": "09:00",
    "tilbud": "belop",
    "belop": "200",
}
TEKST = "Snødekt innkjørsel med en spade"


@pytest.fixture(autouse=True)
def _klokke(sett_na) -> None:
    sett_na(T0)


def feilen(brudd: pytest.ExceptionInfo[RegelBrudd]) -> list[tuple[str, str]]:
    return brudd.value.feil


def er_naer(farge: tuple[int, ...], mal: tuple[int, int, int], toleranse: int = 40) -> bool:
    return all(abs(a - b) <= toleranse for a, b in zip(farge[:3], mal))


# ---------- behandle: formater og resultat (AD-18) ----------


def test_jpeg_med_orientering_og_gps_blir_snudd_og_uten_metadata() -> None:
    """FR-27, NFR-9: 3000×2000 med orientering 6 og GPS blir 1067×1600, uten EXIF og GPS."""
    resultat = behandle(bilder.jpeg(3000, 2000, orientering=6, gps=True))
    assert (resultat.bredde, resultat.hoyde) == (1067, 1600)
    stor, liten = bilder.apne(resultat.bilde), bilder.apne(resultat.miniatyr)
    assert stor.format == liten.format == "JPEG"
    assert stor.size == (1067, 1600)
    assert max(liten.size) <= 640 and liten.size == (427, 640)
    for im in (stor, liten):
        assert not im.getexif()
        assert "exif" not in im.info and "icc_profile" not in im.info
        assert im.mode == "RGB"
    # Orientering 6: venstre (rød) halvdel står øverst etter snuingen.
    assert er_naer(stor.getpixel((533, 100)), bilder.ROD)
    assert er_naer(stor.getpixel((533, 1500)), bilder.BLA)
    # Opplastingen hadde GPS. Resultatet har ingen spor av den.
    assert b"Exif" not in resultat.bilde and b"Exif" not in resultat.miniatyr


def test_png_med_gjennomsiktighet_blir_rgb_jpeg_med_hvit_bakgrunn() -> None:
    resultat = behandle(bilder.png_gjennomsiktig(400, 300))
    stor = bilder.apne(resultat.bilde)
    assert (stor.format, stor.mode, stor.size) == ("JPEG", "RGB", (400, 300))
    assert er_naer(stor.getpixel((5, 5)), (255, 255, 255), 10)
    assert er_naer(stor.getpixel((200, 150)), bilder.ROD)


@pytest.mark.parametrize(
    "data",
    [bilder.webp(), bilder.jpeg(modus="CMYK"), bilder.png(modus="P"), bilder.png(modus="L"),
     bilder.png(modus="LA"), bilder.png(modus="I;16")],
    ids=["webp", "cmyk-jpeg", "png-palett", "png-gra", "png-gra-alfa", "png-16-bit"],
)
def test_andre_formater_og_moduser_blir_rgb_jpeg(data: bytes) -> None:
    resultat = behandle(data)
    stor = bilder.apne(resultat.bilde)
    assert (stor.format, stor.mode, stor.size) == ("JPEG", "RGB", (800, 600))


def test_png_16_bit_med_gjennomsiktighet_blir_rgb_jpeg() -> None:
    """`I;16` med `tRNS` gjøres om til 8 bit før gjennomsiktigheten, så det ikke feiler."""
    data = bilder.png_16_bit_gjennomsiktig(100, 80)
    apnet = bilder.apne(data)
    assert apnet.mode == "I;16" and "transparency" in apnet.info
    stor = bilder.apne(behandle(data).bilde)
    assert (stor.format, stor.mode, stor.size) == ("JPEG", "RGB", (100, 80))


def test_animert_webp_gir_forste_bilde() -> None:
    stor = bilder.apne(behandle(bilder.webp_animert()).bilde)
    assert er_naer(stor.getpixel((200, 150)), bilder.ROD)


def test_lite_bilde_forstorres_ikke() -> None:
    resultat = behandle(bilder.jpeg(300, 200))
    assert (resultat.bredde, resultat.hoyde) == (300, 200)
    assert bilder.apne(resultat.bilde).size == (300, 200)
    assert bilder.apne(resultat.miniatyr).size == (300, 200)


def test_stort_liggende_bilde_blir_1600_og_640() -> None:
    resultat = behandle(bilder.png(4000, 2000))
    assert bilder.apne(resultat.bilde).size == (1600, 800)
    assert bilder.apne(resultat.miniatyr).size == (640, 320)


# ---------- behandle: feil (FR-27, NFR-12) ----------


@pytest.mark.parametrize(
    "data",
    [bilder.TEKST, bilder.SVG, bilder.gif(), bilder.avkuttet_jpeg(), b"", b"\xff\xd8\xff"],
    ids=["tekst", "svg", "gif", "avkuttet-jpeg", "tom", "bare-jpeg-start"],
)
def test_feil_format_gir_formatfeilen(data: bytes) -> None:
    """Formatet bestemmes av innholdet, aldri av filnavn eller Content-Type."""
    with pytest.raises(RegelBrudd) as brudd:
        behandle(data)
    assert feilen(brudd) == [("bilde", FEIL_FORMAT)]


@pytest.mark.parametrize("unntak", [KeyError, IndexError, TypeError, ZeroDivisionError, struct.error])
def test_uventet_feil_i_dekoderen_gir_formatfeilen(monkeypatch: pytest.MonkeyPatch, unntak) -> None:
    """Ødelagt EXIF eller feil i dekoderen gir formatfeilen, ikke 500, og `tolk_bildevalg` kaster ikke."""
    def feiler(*args, **kwargs):
        raise unntak("ødelagt EXIF")

    monkeypatch.setattr(bilde.ImageOps, "exif_transpose", feiler)
    with pytest.raises(RegelBrudd) as brudd:
        behandle(bilder.jpeg(100, 100))
    assert feilen(brudd) == [("bilde", FEIL_FORMAT)]
    assert tolk_bildevalg(bilder.jpeg(100, 100), None, None) == Bildevalg(feil=FEIL_FORMAT)


def test_minnefeil_slippes_gjennom(monkeypatch: pytest.MonkeyPatch) -> None:
    def tomt_for_minne(*args, **kwargs):
        raise MemoryError

    monkeypatch.setattr(bilde.ImageOps, "exif_transpose", tomt_for_minne)
    with pytest.raises(MemoryError):
        behandle(bilder.jpeg(100, 100))


def test_storrelsen_sjekkes_for_fila_apnes(monkeypatch: pytest.MonkeyPatch) -> None:
    """4 MiB + 1 byte gir «for stort» uten at Pillow åpner fila. Nøyaktig 4 MiB godtas."""
    def apnes_ikke(*args, **kwargs):
        raise AssertionError("fila skulle ikke vært åpnet")

    with monkeypatch.context() as m:
        m.setattr(bilde.Image, "open", apnes_ikke)
        with pytest.raises(RegelBrudd) as brudd:
            behandle(bilder.for_stor())
    assert feilen(brudd) == [("bilde", FOR_STORT)]
    data = bilder.jpeg(100, 100)
    akkurat = data + b"\0" * (MAKS_BYTE - len(data))
    assert len(akkurat) == MAKS_BYTE
    assert behandle(akkurat).bredde == 100


def test_for_mange_piksler_gir_feilen_uten_dekoding(monkeypatch: pytest.MonkeyPatch) -> None:
    """7000×6000 i modus «1» er en liten fil, men 42 MP. Pikslene dekodes aldri."""
    data = bilder.png_mange_piksler(7000, 6000)
    assert len(data) < 100_000

    def dekodes_ikke(*args, **kwargs):
        raise AssertionError("bildet skulle ikke vært dekodet")

    monkeypatch.setattr(bilde.ImageOps, "exif_transpose", dekodes_ikke)
    with pytest.raises(RegelBrudd) as brudd:
        behandle(data)
    assert feilen(brudd) == [("bilde", FOR_MANGE_PIKSLER)]


def test_pikselgrensen_pa_hver_side() -> None:
    """40 000 000 piksler godtas, 40 000 001 avvises."""
    assert MAKS_PIKSLER == 40_000_000
    with pytest.raises(RegelBrudd) as brudd:
        behandle(bilder.png_mange_piksler(40_000_001, 1))
    assert feilen(brudd) == [("bilde", FOR_MANGE_PIKSLER)]
    resultat = behandle(bilder.png_mange_piksler(8000, 5000))
    assert (resultat.bredde, resultat.hoyde) == (1600, 1000)


def test_bombe_over_pillows_grense_gir_for_mange_piksler() -> None:
    """Et bilde over Pillows egen grense (DecompressionBombError ved åpning) får vår melding."""
    with pytest.raises(RegelBrudd) as brudd:
        behandle(bilder.png_mange_piksler(20_000, 10_000))
    assert feilen(brudd) == [("bilde", FOR_MANGE_PIKSLER)]


# ---------- bilde_beholdt (AD-18) ----------


def test_beholdt_bilde_rundtur() -> None:
    forste = behandle(bilder.jpeg(800, 600))
    andre = fra_beholdt(til_beholdt(forste))
    assert (andre.bredde, andre.hoyde) == (800, 600)
    assert bilder.apne(andre.bilde).format == "JPEG"


@pytest.mark.parametrize(
    ("tekst", "melding"),
    [
        ("abc", FEIL_FORMAT),
        ("ikke base64!", FEIL_FORMAT),
        ("blåbær", FEIL_FORMAT),
        (base64.b64encode(bilder.TEKST).decode(), FEIL_FORMAT),
        (base64.b64encode(bilder.SVG).decode(), FEIL_FORMAT),
        (base64.b64encode(bilder.for_stor()).decode(), FOR_STORT),
    ],
    ids=["abc", "tegn", "ikke-ascii", "tekst", "svg", "over-4-mib"],
)
def test_forfalsket_beholdt_bilde_gir_feilen(tekst: str, melding: str) -> None:
    with pytest.raises(RegelBrudd) as brudd:
        fra_beholdt(tekst)
    assert feilen(brudd) == [("bilde", melding)]


# ---------- tolk_bildevalg (kaster aldri) ----------


@pytest.fixture(scope="module")
def gyldig() -> bytes:
    return bilder.jpeg(800, 600)


@pytest.fixture(scope="module")
def beholdt() -> str:
    return til_beholdt(behandle(bilder.png(400, 300)))


def test_ingen_fil_og_ingenting_beholdt(gyldig) -> None:
    assert tolk_bildevalg(None, None, None) == Bildevalg()
    assert tolk_bildevalg(None, "", "") == Bildevalg()
    assert tolk_bildevalg(b"", "  ", None) == Bildevalg()


def test_gyldig_ny_fil(gyldig) -> None:
    valg = tolk_bildevalg(gyldig, None, None)
    assert valg.ny is not None and valg.ny.bredde == 800
    assert (valg.fjern, valg.feil) == (False, None)


def test_ugyldig_ny_fil_gir_feil(gyldig) -> None:
    assert tolk_bildevalg(bilder.TEKST, None, None) == Bildevalg(feil=FEIL_FORMAT)


def test_ny_fil_gar_foran_beholdt(gyldig, beholdt) -> None:
    valg = tolk_bildevalg(gyldig, beholdt, None)
    assert valg.ny is not None and valg.ny.bredde == 800  # ikke det beholdte (400)


def test_ugyldig_ny_fil_beholder_gyldig_beholdt(beholdt) -> None:
    valg = tolk_bildevalg(bilder.SVG, beholdt, None)
    assert valg.feil == FEIL_FORMAT
    assert valg.ny is not None and valg.ny.bredde == 400


def test_ugyldig_ny_fil_gyldig_beholdt_og_fjern(beholdt) -> None:
    """Med «Fjern bildet» brukes ikke det beholdte bildet, men feilen for den nye fila står."""
    assert tolk_bildevalg(bilder.SVG, beholdt, "1") == Bildevalg(fjern=True, feil=FEIL_FORMAT)


def test_beholdt_alene_og_beholdt_fjernet(beholdt) -> None:
    valg = tolk_bildevalg(None, beholdt, None)
    assert valg.ny is not None and valg.feil is None
    assert tolk_bildevalg(None, beholdt, "1") == Bildevalg(fjern=True)


def test_fjern_og_ny_fil(gyldig) -> None:
    valg = tolk_bildevalg(gyldig, None, "1")
    assert valg.ny is not None and valg.fjern is True


def test_forfalsket_beholdt_gir_feil() -> None:
    assert tolk_bildevalg(None, "abc", None) == Bildevalg(feil=FEIL_FORMAT)


def test_ugyldig_fil_og_forfalsket_beholdt_kaster_ikke() -> None:
    assert tolk_bildevalg(bilder.TEKST, "abc", None) == Bildevalg(feil=FEIL_FORMAT)


# ---------- valider_oppdrag med bilde (NFR-10) ----------


def test_bildefeilene_star_rett_etter_beskrivelsen(beholdt) -> None:
    """NFR-10: feltrekkefølgen er beskrivelse, bilde, bildetekst, tittel, …"""
    valg = Bildevalg(ny=fra_beholdt(beholdt), feil=FEIL_FORMAT)
    with pytest.raises(RegelBrudd) as brudd:
        valider_oppdrag(**{**SAMME, "beskrivelse": "", "tittel": ""}, bildevalg=valg, bildetekst="")
    assert feilen(brudd)[:4] == [
        ("beskrivelse", "Skriv hva du trenger hjelp til."),
        ("bilde", FEIL_FORMAT),
        ("bildetekst", SKRIV_BILDETEKST),
        ("tittel", "Skriv en tittel."),
    ]


@pytest.mark.parametrize(
    ("tekst", "melding"),
    [("", SKRIV_BILDETEKST), ("   ", SKRIV_BILDETEKST), ("ab", BILDETEKST_FOR_KORT),
     ("x" * 121, BILDETEKST_FOR_LANG)],
    ids=["tom", "mellomrom", "ab", "121"],
)
def test_bildeteksten_med_gyldig_bilde(beholdt, tekst: str, melding: str) -> None:
    with pytest.raises(RegelBrudd) as brudd:
        valider_oppdrag(**SAMME, bildevalg=Bildevalg(ny=fra_beholdt(beholdt)), bildetekst=tekst)
    assert feilen(brudd) == [("bildetekst", melding)]


def test_bildeteksten_normaliseres_og_grensene_godtas(beholdt) -> None:
    """AD-10: trim og NFC som andre tekstfelt. 3 og 120 tegn godtas."""
    valg = Bildevalg(ny=fra_beholdt(beholdt))
    assert valider_oppdrag(**SAMME, bildevalg=valg, bildetekst="  Sné  ").bildetekst == "Sné"
    assert valider_oppdrag(**SAMME, bildevalg=valg, bildetekst="abc").bildetekst == "abc"
    assert valider_oppdrag(**SAMME, bildevalg=valg, bildetekst="x" * 120).bildetekst == "x" * 120


def test_bildeteksten_ignoreres_uten_bilde() -> None:
    """Uten gyldig bilde sjekkes ikke teksten, heller ikke etter en ugyldig fil."""
    assert valider_oppdrag(**SAMME, bildetekst="x" * 200).bildetekst is None
    with pytest.raises(RegelBrudd) as brudd:
        valider_oppdrag(**SAMME, bildevalg=Bildevalg(feil=FEIL_FORMAT), bildetekst="")
    assert feilen(brudd) == [("bilde", FEIL_FORMAT)]


def test_lagret_bilde_krever_bildetekst_med_mindre_det_fjernes() -> None:
    with pytest.raises(RegelBrudd) as brudd:
        valider_oppdrag(**SAMME, har_lagret_bilde=True, bildetekst="")
    assert feilen(brudd) == [("bildetekst", SKRIV_BILDETEKST)]
    gyldig = valider_oppdrag(**SAMME, har_lagret_bilde=True, bildevalg=Bildevalg(fjern=True), bildetekst="")
    assert gyldig.bildetekst is None


# ---------- lagring: opprett, rediger og slett (AD-2, FR-27) ----------


def antall_bilder(db: Session) -> int:
    return db.scalar(select(func.count()).select_from(Oppdragsbilde))


def les_bilde(db: Session, oppdrag_id: int) -> Oppdragsbilde | None:
    db.expire_all()
    return db.get(Oppdragsbilde, oppdrag_id)


def les(db: Session, oppdrag_id: int) -> Oppdrag:
    db.expire_all()
    return db.get(Oppdrag, oppdrag_id)


def test_opprett_med_bilde_og_dobbel_innsending(db: Session, lag_bruker, gyldig) -> None:
    """NFR-5: samme `skjema_id` og bilde to ganger gir `Duplikat`, og én rad i hver tabell."""
    kari = lag_bruker()
    valg = tolk_bildevalg(gyldig, None, None)
    oppdrag_id = opprett_oppdrag(db, oppdragsgiver_id=kari.id, skjema_id="b" * 22, bildevalg=valg,
                                 bildetekst=TEKST, **SAMME)
    rad = les_bilde(db, oppdrag_id)
    assert (rad.bildetekst, rad.bredde, rad.hoyde, rad.opprettet) == (TEKST, 800, 600, T0)
    with pytest.raises(Duplikat):
        opprett_oppdrag(db, oppdragsgiver_id=kari.id, skjema_id="b" * 22, bildevalg=valg,
                        bildetekst=TEKST, **SAMME)
    assert db.scalar(select(func.count()).select_from(Oppdrag)) == 1
    assert antall_bilder(db) == 1


def test_opprett_uten_bilde_lagrer_ingen_rad(db: Session, lag_bruker) -> None:
    kari = lag_bruker()
    opprett_oppdrag(db, oppdragsgiver_id=kari.id, skjema_id="c" * 22, bildetekst=TEKST, **SAMME)
    assert antall_bilder(db) == 0


@pytest.fixture
def lagret(lag_oppdrag, lag_bilde):
    """«Måke snø» i morgen kl. 09:00 med bilde, og `vesentlig_endret` satt tidligere."""
    oppdrag = lag_oppdrag(tidspunkt=I_MORGEN_9, vesentlig_endret=TIDLIGERE)
    lag_bilde(oppdrag, bildetekst=TEKST)
    return oppdrag


def rediger(db: Session, oppdrag: Oppdrag, valg: Bildevalg = Bildevalg(), **endringer: str) -> None:
    rediger_oppdrag(db, oppdrag.id, oppdragsgiver_id=oppdrag.oppdragsgiver_id, bildevalg=valg,
                    **{**SAMME, "bildetekst": TEKST, **endringer})


def test_bytte_bilde_endrer_ikke_vesentlig_endret(db: Session, lagret) -> None:
    """FR-27: nytt bilde, `versjon` + 1, og `vesentlig_endret` er uendret."""
    rediger(db, lagret, tolk_bildevalg(bilder.png(400, 300), None, None), bildetekst="Ny tekst")
    rad = les_bilde(db, lagret.id)
    assert (rad.bredde, rad.hoyde, rad.bildetekst) == (400, 300, "Ny tekst")
    oppdrag = les(db, lagret.id)
    assert (oppdrag.versjon, oppdrag.vesentlig_endret) == (2, TIDLIGERE)


def test_fjerne_bilde_sletter_raden(db: Session, lagret) -> None:
    rediger(db, lagret, Bildevalg(fjern=True), bildetekst="")
    assert les_bilde(db, lagret.id) is None
    assert les(db, lagret.id).vesentlig_endret == TIDLIGERE


def test_bare_bildetekst_oppdateres(db: Session, lagret) -> None:
    for_ = bytes(les_bilde(db, lagret.id).bilde)
    rediger(db, lagret, bildetekst="Innkjørsel full av snø")
    rad = les_bilde(db, lagret.id)
    assert rad.bildetekst == "Innkjørsel full av snø"
    assert bytes(rad.bilde) == for_
    assert les(db, lagret.id).vesentlig_endret == TIDLIGERE


def test_urort_bilde_krever_bildetekst(db: Session, lagret) -> None:
    with pytest.raises(RegelBrudd) as brudd:
        rediger(db, lagret, tittel="Ny tittel", bildetekst="")
    assert feilen(brudd) == [("bildetekst", SKRIV_BILDETEKST)]
    assert les_bilde(db, lagret.id) is not None


def test_fjern_og_ny_fil_erstatter_bildet(db: Session, lagret) -> None:
    rediger(db, lagret, tolk_bildevalg(bilder.png(400, 300), None, "1"))
    assert les_bilde(db, lagret.id).bredde == 400


def test_nytt_bilde_pa_oppdrag_uten_bilde(db: Session, lag_oppdrag) -> None:
    oppdrag = lag_oppdrag(tidspunkt=I_MORGEN_9)
    rediger(db, oppdrag, tolk_bildevalg(bilder.jpeg(), None, None))
    assert les_bilde(db, oppdrag.id).bildetekst == TEKST
    assert les(db, oppdrag.id).vesentlig_endret is None


def test_vesentlig_endring_og_bilde_samtidig(db: Session, lagret) -> None:
    """AD-3 er uendret: et nytt beløp setter `vesentlig_endret` også når bildet byttes."""
    rediger(db, lagret, tolk_bildevalg(bilder.jpeg(), None, None), belop="300")
    assert les(db, lagret.id).vesentlig_endret == T0


def test_slett_bilde(db: Session, lagret, lag_oppdrag) -> None:
    uten = lag_oppdrag()
    slett_bilde(db, uten.id)  # ingen rad: ingenting skjer
    slett_bilde(db, lagret.id)
    assert les_bilde(db, lagret.id) is None
    assert les(db, lagret.id) is not None
