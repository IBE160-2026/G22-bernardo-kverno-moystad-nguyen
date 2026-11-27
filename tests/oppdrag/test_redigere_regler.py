"""Reglene for å redigere og avbryte, direkte mot servicen (spec 2.5).

FR-6, FR-7, FR-8, NFR-5, AD-2, AD-3. `vesentlig_endret` settes til `klokke.na()`
bare når tidspunkt, beløp eller postnummer faktisk endres, også `NULL` ↔ beløp.
`hent_eget_oppdrag` gir `FinnesIkke` for andres og `Konflikt` for feil status.
`avbryt_oppdrag` virker fra `hjelper_valgt` og beholder hjelperen. «database is
locked» gir `Konflikt`. Klokka står fast på tirsdag 24.11.2026 kl. 13:00 norsk tid.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import select
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session
from sqlalchemy.sql.dml import Update

from app.core.feil import FinnesIkke, Konflikt, RegelBrudd
from app.oppdrag.models import Oppdrag
from app.oppdrag.service import (
    KONFLIKT,
    TIDSPUNKTET_ER_PASSERT,
    avbryt_oppdrag,
    detaljer_url,
    hent_eget_oppdrag,
    opprett_oppdrag,
    rediger_oppdrag,
    skjemaverdier_for,
    valider_oppdrag,
)

T0 = datetime(2026, 11, 24, 12, 0, tzinfo=timezone.utc)  # 13:00 norsk tid
I_MORGEN_9 = datetime(2026, 11, 25, 8, 0, tzinfo=timezone.utc)  # 25.11.2026 kl. 09:00 norsk tid
TIDLIGERE = datetime(2026, 11, 1, 10, 0, tzinfo=timezone.utc)

# Felt som gir nøyaktig det lagrede oppdraget fra `lagret` (samme verdier sendt på nytt).
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


@pytest.fixture(autouse=True)
def _klokke(sett_na) -> None:
    sett_na(T0)


@pytest.fixture
def lagret(lag_oppdrag):
    """«Måke snø» i morgen kl. 09:00, 200 kr, 0571, med `vesentlig_endret` satt tidligere."""
    return lag_oppdrag(tidspunkt=I_MORGEN_9, vesentlig_endret=TIDLIGERE)


def les(db: Session, oppdrag_id: int) -> Oppdrag:
    db.expire_all()
    return db.scalars(select(Oppdrag).where(Oppdrag.id == oppdrag_id)).one()


def rediger(db: Session, oppdrag: Oppdrag, **endringer: str) -> None:
    rediger_oppdrag(db, oppdrag.id, oppdragsgiver_id=oppdrag.oppdragsgiver_id, **{**SAMME, **endringer})


# ---------- valider_oppdrag (samme regler som opprett_oppdrag) ----------


def test_valider_oppdrag_gir_feilene_i_samme_rekkefolge_som_utlegging() -> None:
    """FR-6: redigering bruker samme funksjon, så tekstene og rekkefølgen er de samme som i 2.1."""
    tomt = {felt: "" for felt in SAMME}
    with pytest.raises(RegelBrudd) as brudd:
        valider_oppdrag(**tomt)
    assert [felt for felt, _ in brudd.value.feil] == [
        "beskrivelse", "tittel", "kategori", "postnummer", "dato", "klokkeslett", "tilbud",
    ]


def test_valider_oppdrag_normaliserer() -> None:
    gyldig = valider_oppdrag(**{**SAMME, "postnummer": " 0571 ", "klokkeslett": "9", "tilbud": "uten"})
    assert (gyldig.postnummer, gyldig.tidspunkt, gyldig.belop) == ("0571", I_MORGEN_9, None)


def test_opprett_oppdrag_oppforer_seg_som_for(db: Session, lag_bruker) -> None:
    """Invariant 2.1: `opprett_oppdrag` bruker `valider_oppdrag` og lagrer som før."""
    kari = lag_bruker()
    oppdrag_id = opprett_oppdrag(db, oppdragsgiver_id=kari.id, skjema_id="a" * 22, **SAMME)
    oppdrag = les(db, oppdrag_id)
    assert (oppdrag.status, oppdrag.versjon, oppdrag.tidspunkt, oppdrag.belop) == ("apen", 1, I_MORGEN_9, 200)
    assert oppdrag.vesentlig_endret is None
    with pytest.raises(RegelBrudd):
        opprett_oppdrag(db, oppdragsgiver_id=kari.id, skjema_id="b" * 22, **{**SAMME, "dato": "23.11.2026"})


# ---------- skjemaverdier_for og hent_eget_oppdrag ----------


def test_skjemaverdier_for_gir_de_lagrede_verdiene(db: Session, lagret) -> None:
    oppdrag = hent_eget_oppdrag(db, lagret.id, lagret.oppdragsgiver_id, statuser={"apen"})
    assert skjemaverdier_for(oppdrag) == SAMME


def test_skjemaverdier_for_uten_betaling(db: Session, lag_oppdrag) -> None:
    oppdrag = lag_oppdrag(belop=None)
    verdier = skjemaverdier_for(hent_eget_oppdrag(db, oppdrag.id, oppdrag.oppdragsgiver_id, statuser={"apen"}))
    assert (verdier["tilbud"], verdier["belop"]) == ("uten", "")


def test_skjemaverdier_for_passert_tidspunkt(db: Session, lag_oppdrag) -> None:
    """FR-8: et utgått oppdrag viser det gamle tidspunktet i feltene."""
    oppdrag = lag_oppdrag(tidspunkt=datetime(2026, 11, 22, 9, 0, tzinfo=timezone.utc))
    verdier = skjemaverdier_for(hent_eget_oppdrag(db, oppdrag.id, oppdrag.oppdragsgiver_id, statuser={"apen"}))
    assert (verdier["dato"], verdier["klokkeslett"]) == ("22.11.2026", "10:00")


def test_hent_eget_oppdrag_finnes_ikke_og_andres(db: Session, lagret, lag_bruker, lag_oppdrag) -> None:
    """FR-6, FR-9: et oppdrag som ikke finnes, og andres oppdrag (åpent eller ikke), gir `FinnesIkke`."""
    annen = lag_bruker()
    with pytest.raises(FinnesIkke):
        hent_eget_oppdrag(db, 999_999, annen.id, statuser={"apen"})
    with pytest.raises(FinnesIkke):
        hent_eget_oppdrag(db, lagret.id, annen.id, statuser={"apen"})
    avbrutt = lag_oppdrag(status="avbrutt")
    with pytest.raises(FinnesIkke):
        hent_eget_oppdrag(db, avbrutt.id, annen.id, statuser={"apen"})


@pytest.mark.parametrize("status", ["avbrutt", "utfort", "hjelper_valgt"])
def test_hent_eget_oppdrag_feil_status_gir_konflikt(db: Session, lag_oppdrag, status: str) -> None:
    oppdrag = lag_oppdrag(status=status)
    with pytest.raises(Konflikt) as konflikt:
        hent_eget_oppdrag(db, oppdrag.id, oppdrag.oppdragsgiver_id, statuser={"apen"})
    assert (konflikt.value.melding, konflikt.value.til_url) == (KONFLIKT, detaljer_url(oppdrag.id))


def test_hent_eget_oppdrag_hjelper_valgt_kan_avbrytes(db: Session, lag_oppdrag) -> None:
    oppdrag = lag_oppdrag(status="hjelper_valgt")
    assert hent_eget_oppdrag(
        db, oppdrag.id, oppdrag.oppdragsgiver_id, statuser={"apen", "hjelper_valgt"}
    ).er_eier


# ---------- rediger_oppdrag ----------


def test_redigering_lagrer_og_oker_versjon(db: Session, lagret) -> None:
    """FR-6, AD-2: feltene lagres, og `versjon` øker med 1."""
    rediger(db, lagret, tittel="Måke snø og strø", beskrivelse="Måke og strø trappa og innkjørselen.",
            kategori="annet")
    oppdrag = les(db, lagret.id)
    assert (oppdrag.tittel, oppdrag.beskrivelse, oppdrag.kategori) == (
        "Måke snø og strø", "Måke og strø trappa og innkjørselen.", "annet"
    )
    assert (oppdrag.versjon, oppdrag.status) == (2, "apen")


@pytest.mark.parametrize(
    "endring",
    [
        {"dato": "26.11.2026"},
        {"klokkeslett": "10:00"},
        {"belop": "250"},
        {"tilbud": "uten"},
        {"postnummer": "0572"},
    ],
    ids=["dato", "klokkeslett", "belop", "belop-til-uten", "postnummer"],
)
def test_vesentlig_endring_setter_vesentlig_endret(db: Session, lagret, endring: dict) -> None:
    """AD-3, FR-6: tidspunkt, beløp (også 200 → «Uten betaling») og postnummer setter `klokke.na()`."""
    rediger(db, lagret, **endring)
    assert les(db, lagret.id).vesentlig_endret == T0


def test_uten_betaling_til_belop_er_vesentlig(db: Session, lag_oppdrag) -> None:
    """AD-3: `NULL` → beløp er en endring (`IS DISTINCT FROM`)."""
    oppdrag = lag_oppdrag(tidspunkt=I_MORGEN_9, belop=None)
    rediger(db, oppdrag, tilbud="belop", belop="200")
    assert les(db, oppdrag.id).vesentlig_endret == T0


def test_uten_betaling_sendt_pa_nytt_er_ikke_vesentlig(db: Session, lag_oppdrag) -> None:
    """AD-3: `NULL` → `NULL` er ingen endring, også når et beløp står i feltet."""
    oppdrag = lag_oppdrag(tidspunkt=I_MORGEN_9, belop=None, vesentlig_endret=TIDLIGERE)
    rediger(db, oppdrag, tilbud="uten", belop="77")
    assert les(db, oppdrag.id).vesentlig_endret == TIDLIGERE


@pytest.mark.parametrize(
    "endring",
    [
        {"tittel": "Ny tittel på oppdraget"},
        {"beskrivelse": "En helt annen beskrivelse av oppdraget."},
        {"kategori": "hage"},
        {},
        {"postnummer": " 0571 ", "klokkeslett": "9", "belop": " 200 "},
    ],
    ids=["tittel", "beskrivelse", "kategori", "samme-verdier", "samme-verdier-annen-skrivemate"],
)
def test_ikke_vesentlig_endring_beholder_vesentlig_endret(db: Session, lagret, endring: dict) -> None:
    """AD-3: tittel, beskrivelse og kategori, eller samme verdier på nytt, endrer ikke `vesentlig_endret`."""
    rediger(db, lagret, **endring)
    oppdrag = les(db, lagret.id)
    assert oppdrag.vesentlig_endret == TIDLIGERE
    assert oppdrag.versjon == 2


def test_ikke_vesentlig_endring_beholder_null(db: Session, lag_oppdrag) -> None:
    oppdrag = lag_oppdrag(tidspunkt=I_MORGEN_9)
    rediger(db, oppdrag, tittel="Ny tittel på oppdraget")
    assert les(db, oppdrag.id).vesentlig_endret is None


def test_dobbel_innsending_lagrer_to_ganger_men_vesentlig_endret_fra_den_forste(
    db: Session, lagret, sett_na
) -> None:
    """NFR-5: samme gyldige skjema to ganger gir ingen feil; den andre endrer ikke `vesentlig_endret`."""
    rediger(db, lagret, dato="26.11.2026")
    sett_na(T0 + timedelta(seconds=5))
    rediger(db, lagret, dato="26.11.2026")
    oppdrag = les(db, lagret.id)
    assert oppdrag.vesentlig_endret == T0
    assert oppdrag.versjon == 3


def test_utgatt_oppdrag_kan_fa_nytt_tidspunkt(db: Session, lag_oppdrag) -> None:
    """FR-8: `WHERE` har ikke `tidspunkt > nå`, så et utgått oppdrag kan endres."""
    oppdrag = lag_oppdrag(tidspunkt=T0 - timedelta(days=2))
    rediger(db, oppdrag, dato="25.11.2026")
    lagret = les(db, oppdrag.id)
    assert lagret.tidspunkt == I_MORGEN_9
    assert lagret.vesentlig_endret == T0


@pytest.mark.parametrize(
    ("dato", "klokkeslett"), [("22.11.2026", "10:00"), ("24.11.2026", "13:00")], ids=["passert", "lik-naa"]
)
def test_fortsatt_passert_gir_feil_under_nar(db: Session, lag_oppdrag, dato: str, klokkeslett: str) -> None:
    """FR-6: et tidspunkt som ikke er fram i tid, gir «Velg et nytt tidspunkt fram i tid»."""
    oppdrag = lag_oppdrag(tidspunkt=datetime(2026, 11, 22, 9, 0, tzinfo=timezone.utc))
    with pytest.raises(RegelBrudd) as brudd:
        rediger(db, oppdrag, dato=dato, klokkeslett=klokkeslett)
    assert brudd.value.feil == [("nar", "Velg et nytt tidspunkt fram i tid")]
    assert les(db, oppdrag.id).versjon == 1


def test_feil_i_felt_lagrer_ingenting(db: Session, lagret) -> None:
    with pytest.raises(RegelBrudd) as brudd:
        rediger(db, lagret, tittel="", belop="abc")
    assert brudd.value.feil == [("tittel", "Skriv en tittel."),
                                ("belop", "Skriv et beløp fra 1 til 10 000 kr, i hele kroner.")]
    oppdrag = les(db, lagret.id)
    assert (oppdrag.tittel, oppdrag.versjon) == ("Måke snø i innkjørselen", 1)


def test_andres_oppdrag_gir_finnes_ikke(db: Session, lagret, lag_bruker) -> None:
    """FR-6: en annen enn oppdragsgiveren får samme svar som for et oppdrag som ikke finnes."""
    annen = lag_bruker()
    with pytest.raises(FinnesIkke):
        rediger_oppdrag(db, lagret.id, oppdragsgiver_id=annen.id, **{**SAMME, "tittel": "Kapret"})
    with pytest.raises(FinnesIkke):
        rediger_oppdrag(db, 999_999, oppdragsgiver_id=annen.id, **SAMME)
    assert les(db, lagret.id).tittel == "Måke snø i innkjørselen"


def test_tilgang_sjekkes_for_feltfeil(db: Session, lagret, lag_bruker, lag_oppdrag) -> None:
    """Spec 2.5: 404 og `Konflikt` går foran 422, så feltfeil avslører ingenting om andres oppdrag."""
    annen = lag_bruker()
    with pytest.raises(FinnesIkke):
        rediger_oppdrag(db, lagret.id, oppdragsgiver_id=annen.id, **{**SAMME, "tittel": ""})
    avbrutt = lag_oppdrag(status="avbrutt")
    with pytest.raises(Konflikt):
        rediger_oppdrag(db, avbrutt.id, oppdragsgiver_id=avbrutt.oppdragsgiver_id, **{**SAMME, "tittel": ""})


@pytest.mark.parametrize("status", ["avbrutt", "utfort", "hjelper_valgt"])
def test_ikke_apen_gir_konflikt_og_ingen_endring(db: Session, lag_oppdrag, status: str) -> None:
    """FR-6: bare mens Åpen. 0 rader gir `Konflikt`, og ingenting lagres."""
    oppdrag = lag_oppdrag(status=status, tidspunkt=I_MORGEN_9)
    with pytest.raises(Konflikt) as konflikt:
        rediger(db, oppdrag, tittel="Endret etter avbrudd")
    assert konflikt.value.til_url == detaljer_url(oppdrag.id)
    lagret = les(db, oppdrag.id)
    assert (lagret.tittel, lagret.versjon, lagret.status) == ("Måke snø i innkjørselen", 1, status)


# ---------- avbryt_oppdrag (FR-7) ----------


def test_avbryt_fra_apen(db: Session, lagret) -> None:
    avbryt_oppdrag(db, lagret.id, oppdragsgiver_id=lagret.oppdragsgiver_id)
    oppdrag = les(db, lagret.id)
    assert (oppdrag.status, oppdrag.versjon) == ("avbrutt", 2)


def test_avbryt_utgatt(db: Session, lag_oppdrag) -> None:
    """FR-8: et utgått oppdrag kan avbrytes (ingen `ikke_passert`)."""
    oppdrag = lag_oppdrag(tidspunkt=T0 - timedelta(days=2))
    avbryt_oppdrag(db, oppdrag.id, oppdragsgiver_id=oppdrag.oppdragsgiver_id)
    assert les(db, oppdrag.id).status == "avbrutt"


def test_avbryt_fra_hjelper_valgt_beholder_hjelperen(db: Session, lag_oppdrag, lag_bruker) -> None:
    """FR-7: avbrudd fra Hjelper valgt er lov i servicen; `valgt_hjelper_id` beholdes."""
    hjelper = lag_bruker()
    oppdrag = lag_oppdrag(status="hjelper_valgt", valgt_hjelper_id=hjelper.id)
    avbryt_oppdrag(db, oppdrag.id, oppdragsgiver_id=oppdrag.oppdragsgiver_id)
    lagret = les(db, oppdrag.id)
    assert (lagret.status, lagret.valgt_hjelper_id, lagret.versjon) == ("avbrutt", hjelper.id, 2)


@pytest.mark.parametrize("status", ["utfort", "avbrutt"])
def test_avbryt_feil_status_gir_konflikt(db: Session, lag_oppdrag, status: str) -> None:
    oppdrag = lag_oppdrag(status=status)
    with pytest.raises(Konflikt):
        avbryt_oppdrag(db, oppdrag.id, oppdragsgiver_id=oppdrag.oppdragsgiver_id)
    assert les(db, oppdrag.id).status == status


def test_avbryt_andres_gir_finnes_ikke(db: Session, lagret, lag_bruker) -> None:
    with pytest.raises(FinnesIkke):
        avbryt_oppdrag(db, lagret.id, oppdragsgiver_id=lag_bruker().id)
    assert les(db, lagret.id).status == "apen"


def test_avbrutt_kan_ikke_redigeres(db: Session, lagret) -> None:
    """FR-7: etter avbrudd kan oppdraget ikke endres."""
    avbryt_oppdrag(db, lagret.id, oppdragsgiver_id=lagret.oppdragsgiver_id)
    with pytest.raises(Konflikt):
        rediger(db, lagret, tittel="For sent")


# ---------- «database is locked» (AD-2) ----------


def _last(feilmelding: str = "database is locked") -> OperationalError:
    return OperationalError("UPDATE oppdrag ...", {}, sqlite3.OperationalError(feilmelding))


@pytest.fixture
def last_ved_update(db: Session, monkeypatch: pytest.MonkeyPatch):
    """Den betingede `UPDATE`-en på `oppdrag` gir «database is locked», som når låsen ikke ble ledig."""

    def _sett(feilmelding: str = "database is locked") -> None:
        ekte = Session.execute

        def execute(self, statement, *args, **kwargs):
            if isinstance(statement, Update) and statement.table.name == "oppdrag":
                raise _last(feilmelding)
            return ekte(self, statement, *args, **kwargs)

        monkeypatch.setattr(Session, "execute", execute)

    return _sett


def test_last_database_ved_redigering_gir_konflikt(db: Session, lagret, last_ved_update) -> None:
    last_ved_update()
    with pytest.raises(Konflikt) as konflikt:
        rediger(db, lagret, tittel="Låst")
    assert (konflikt.value.melding, konflikt.value.til_url) == (KONFLIKT, detaljer_url(lagret.id))


def test_last_database_ved_avbrudd_gir_konflikt(db: Session, lagret, last_ved_update) -> None:
    last_ved_update()
    with pytest.raises(Konflikt):
        avbryt_oppdrag(db, lagret.id, oppdragsgiver_id=lagret.oppdragsgiver_id)


def test_andre_operationalerror_slipper_gjennom(db: Session, lagret, last_ved_update) -> None:
    last_ved_update("disk I/O error")
    with pytest.raises(OperationalError):
        rediger(db, lagret, tittel="Disk")


def test_merket_kommer_fra_merker_lagt_ut() -> None:
    """AD-3: teksten i merket på utgåtte oppdrag er ordrett fra FR-18."""
    assert TIDSPUNKTET_ER_PASSERT == "Tidspunktet er passert"
