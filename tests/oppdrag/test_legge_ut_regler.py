"""Reglene for å legge ut oppdrag, direkte mot servicen (FR-5, FR-9, NFR-5, NFR-10, AD-16).

Radene i I/O-matrisen i spec 2.1. Klokka står fast på tirsdag 24.11.2026 kl. 13:00
norsk tid.
"""

from __future__ import annotations

import dataclasses
from datetime import datetime, timezone

import pytest
from sqlalchemy import func, select

from app.core.feil import Duplikat, FinnesIkke, IngenTilgang, RegelBrudd
from app.core.tid import (
    DATO_FORMAT,
    KLOKKESLETT_FINNES_IKKE,
    SKRIV_DATO,
    SKRIV_KLOKKESLETT,
    TIDSPUNKT_FOR_LANGT_FRAM,
    TIDSPUNKT_PASSERT,
)
from app.identity.service import POSTNUMMER_UKJENT, SKRIV_POSTNUMMER
from app.oppdrag.models import Oppdrag
from app.oppdrag.service import (
    BELOP_FEIL,
    BESKRIVELSE_FOR_KORT,
    SKRIV_BESKRIVELSE,
    SKRIV_TITTEL,
    TITTEL_FOR_KORT,
    TITTEL_FOR_LANG,
    VELG_KATEGORI,
    VELG_TILBUD,
    OppdragVisning,
    beskrivelse_for_lang,
    detaljer_url,
    hent_for_visning,
    lagt_ut_av,
    opprett_oppdrag,
)

T0 = datetime(2026, 11, 24, 12, 0, tzinfo=timezone.utc)

GYLDIG = {
    "beskrivelse": "Trenger noen som kan måke snø i innkjørselen min i morgen.",
    "tittel": "Måke snø i innkjørselen",
    "kategori": "snomaking",
    "postnummer": "0571",
    "dato": "25.11.2026",
    "klokkeslett": "7",
    "tilbud": "belop",
    "belop": "1000",
}


@pytest.fixture(autouse=True)
def _klokke(sett_na) -> None:
    sett_na(T0)


@pytest.fixture
def kari(lag_bruker):
    return lag_bruker(navn="Kari Nordmann")


_teller = iter(range(10**6))


def opprett(db, eier_id: int, *, skjema_id: str | None = None, **endringer: str) -> int:
    skjema_id = skjema_id or f"skjema-id-for-test-{next(_teller):06d}"
    return opprett_oppdrag(db, oppdragsgiver_id=eier_id, skjema_id=skjema_id, **{**GYLDIG, **endringer})


def feil_for(db, eier_id: int, **endringer: str) -> list[tuple[str, str]]:
    with pytest.raises(RegelBrudd) as brudd:
        opprett(db, eier_id, **endringer)
    return brudd.value.feil


def antall(db) -> int:
    return db.scalar(select(func.count()).select_from(Oppdrag))


# ---------- gyldig ----------


def test_gyldig_oppdrag_lagres_som_apen(db, kari) -> None:
    """FR-5: status Åpen, kategori som kode, tidspunkt i UTC, beløp som heltall."""
    oppdrag_id = opprett(db, kari.id, skjema_id="gyldig-skjema-id-0001")
    db.expire_all()
    oppdrag = db.get(Oppdrag, oppdrag_id)
    assert oppdrag.status == "apen"
    assert oppdrag.kategori == "snomaking"
    assert oppdrag.tidspunkt == datetime(2026, 11, 25, 6, 0, tzinfo=timezone.utc)
    assert oppdrag.belop == 1000
    assert oppdrag.oppdragsgiver_id == kari.id
    assert oppdrag.postnummer == "0571"
    assert oppdrag.versjon == 1
    assert oppdrag.skjema_id == "gyldig-skjema-id-0001"
    assert oppdrag.opprettet == T0
    assert oppdrag.valgt_hjelper_id is None and oppdrag.vesentlig_endret is None


def test_uten_betaling_ignorerer_belop(db, kari) -> None:
    """FR-5: «Uten betaling» lagres som NULL, og et skrevet beløp ignoreres."""
    oppdrag_id = opprett(db, kari.id, tilbud="uten", belop="50")
    assert db.get(Oppdrag, oppdrag_id).belop is None
    oppdrag_id = opprett(db, kari.id, tilbud="uten", belop="abc")
    assert db.get(Oppdrag, oppdrag_id).belop is None


def test_tekst_trimmes_og_nfc_normaliseres(db, kari) -> None:
    """AD-10: «e» + kombinerende akutt lagres som «é», og mellomrom rundt fjernes."""
    oppdrag_id = opprett(db, kari.id, tittel="  Kafébesøk  ", beskrivelse="  Linje 1\r\nLinje 2 her  ")
    oppdrag = db.get(Oppdrag, oppdrag_id)
    assert oppdrag.tittel == "Kafébesøk"
    assert oppdrag.beskrivelse == "Linje 1\nLinje 2 her"


def test_nul_fjernes_fra_tekst(db, kari) -> None:
    """AD-10: NUL, som Postgres avviser, fjernes før lagring."""
    oppdrag_id = opprett(db, kari.id, tittel="Måke\x00 snø", beskrivelse="Trenger\x00 hjelp med snø i dag.")
    oppdrag = db.get(Oppdrag, oppdrag_id)
    assert "\x00" not in oppdrag.tittel and "\x00" not in oppdrag.beskrivelse
    assert oppdrag.tittel == "Måke snø"


# ---------- lengder ----------


@pytest.mark.parametrize(
    ("tittel", "beskrivelse"),
    [("a" * 3, "b" * 10), ("a" * 80, "b" * 1000), (" " + "é" * 80 + " ", "é" * 1000)],
    ids=["minste", "største", "nfc-og-trim"],
)
def test_lengdene_som_godtas(db, kari, tittel: str, beskrivelse: str) -> None:
    """FR-5: tittel 3–80 og beskrivelse 10–1000 tegn etter trim og NFC."""
    assert opprett(db, kari.id, tittel=tittel, beskrivelse=beskrivelse)


@pytest.mark.parametrize(
    ("felt", "verdi", "forventet"),
    [
        ("tittel", "ab", ("tittel", TITTEL_FOR_KORT)),
        ("tittel", "a" * 81, ("tittel", TITTEL_FOR_LANG)),
        ("tittel", "   ", ("tittel", SKRIV_TITTEL)),
        ("tittel", "", ("tittel", SKRIV_TITTEL)),
        ("beskrivelse", "b" * 9, ("beskrivelse", BESKRIVELSE_FOR_KORT)),
        ("beskrivelse", "b" * 1001, ("beskrivelse", "Beskrivelsen kan ha høyst 1000 tegn. Nå har den 1001.")),
        ("beskrivelse", " \n\t ", ("beskrivelse", SKRIV_BESKRIVELSE)),
        ("beskrivelse", "", ("beskrivelse", SKRIV_BESKRIVELSE)),
    ],
)
def test_lengdene_som_avvises(db, kari, felt: str, verdi: str, forventet: tuple[str, str]) -> None:
    assert feil_for(db, kari.id, **{felt: verdi}) == [forventet]
    assert antall(db) == 0


def test_beskrivelse_for_lang_sier_hvor_lang_den_er() -> None:
    assert beskrivelse_for_lang(1046) == "Beskrivelsen kan ha høyst 1000 tegn. Nå har den 1046."


# ---------- beløp ----------


@pytest.mark.parametrize(
    ("verdi", "forventet"), [("1", 1), ("10 000", 10000), ("10 000", 10000), (" 250 ", 250)]
)
def test_belop_som_godtas(db, kari, verdi: str, forventet: int) -> None:
    """FR-5: hele kroner 1–10 000. Mellomrom, også NBSP, fjernes."""
    assert db.get(Oppdrag, opprett(db, kari.id, belop=verdi)).belop == forventet


@pytest.mark.parametrize(
    "verdi", ["0", "10001", "1,5", "1.5", "abc", "", "  ", "-5", "+5", "١٠٠", "1e3", "000001", "9" * 5000]
)
def test_belop_som_avvises(db, kari, verdi: str) -> None:
    assert feil_for(db, kari.id, belop=verdi) == [("belop", BELOP_FEIL)]


# ---------- valg ----------


@pytest.mark.parametrize("kategori", ["", "Snømåking", "hagearbeid", "SNOMAKING"])
def test_kategori_mangler_eller_er_ukjent(db, kari, kategori: str) -> None:
    """AD-10: kategori godtas bare som kode fra `KATEGORIER`."""
    assert feil_for(db, kari.id, kategori=kategori) == [("kategori", VELG_KATEGORI)]


@pytest.mark.parametrize("tilbud", ["", "gratis", "BELOP"])
def test_tilbud_mangler(db, kari, tilbud: str) -> None:
    """Uten valg i «Hva tilbyr du?» vises bare den feilen, ikke en feil for beløpet."""
    assert feil_for(db, kari.id, tilbud=tilbud, belop="") == [("tilbud", VELG_TILBUD)]


@pytest.mark.parametrize(
    ("postnummer", "melding"), [("", SKRIV_POSTNUMMER), (" ", SKRIV_POSTNUMMER), ("0000", POSTNUMMER_UKJENT),
                                ("571", POSTNUMMER_UKJENT), ("abcd", POSTNUMMER_UKJENT)]
)
def test_postnummer(db, kari, postnummer: str, melding: str) -> None:
    assert feil_for(db, kari.id, postnummer=postnummer) == [("postnummer", melding)]


def test_annet_postnummer_enn_profilen_godtas(db, kari) -> None:
    assert db.get(Oppdrag, opprett(db, kari.id, postnummer=" 5006 ")).postnummer == "5006"


# ---------- tidspunkt ----------


@pytest.mark.parametrize(
    ("dato", "klokkeslett", "forventet"),
    [
        ("24.11.2026", "13:00", [("nar", TIDSPUNKT_PASSERT)]),
        ("24.11.2027", "13:01", [("nar", TIDSPUNKT_FOR_LANGT_FRAM)]),
        ("28.03.2027", "02:30", [("klokkeslett", KLOKKESLETT_FINNES_IKKE)]),
        ("", "", [("dato", SKRIV_DATO), ("klokkeslett", SKRIV_KLOKKESLETT)]),
        ("i morgen", "07:00", [("dato", DATO_FORMAT)]),
    ],
)
def test_tidspunkt(db, kari, dato: str, klokkeslett: str, forventet: list) -> None:
    """FR-5, AD-9: feilene fra `tolk_tidspunkt` kommer på `dato`, `klokkeslett` eller `nar`."""
    assert feil_for(db, kari.id, dato=dato, klokkeslett=klokkeslett) == forventet


def test_hostnatt_bruker_forste_klokkeslett(db, kari) -> None:
    oppdrag_id = opprett(db, kari.id, dato="31.10.2027", klokkeslett="02:30")
    assert db.get(Oppdrag, oppdrag_id).tidspunkt == datetime(2027, 10, 31, 0, 30, tzinfo=timezone.utc)


def test_grensen_12_maneder_godtas(db, kari) -> None:
    assert opprett(db, kari.id, dato="24.11.2027", klokkeslett="13:00")


# ---------- mange feil (NFR-10) ----------


def test_tom_innsending_gir_alle_feilene_i_feltrekkefolge(db, kari) -> None:
    """NFR-10: tom innsending med forhåndsutfylt postnummer gir seks feil, i feltrekkefølge."""
    tom = {felt: "" for felt in GYLDIG} | {"postnummer": "0571"}
    assert feil_for(db, kari.id, **tom) == [
        ("beskrivelse", SKRIV_BESKRIVELSE),
        ("tittel", SKRIV_TITTEL),
        ("kategori", VELG_KATEGORI),
        ("dato", SKRIV_DATO),
        ("klokkeslett", SKRIV_KLOKKESLETT),
        ("tilbud", VELG_TILBUD),
    ]
    assert antall(db) == 0


def test_alle_felt_feil_samtidig(db, kari) -> None:
    feil = feil_for(
        db, kari.id, beskrivelse="kort", tittel="ab", kategori="x", postnummer="0000",
        dato="24.11.2026", klokkeslett="12:00", tilbud="belop", belop="0",
    )
    assert [f for f, _ in feil] == ["beskrivelse", "tittel", "kategori", "postnummer", "nar", "belop"]


# ---------- dobbel innsending (AD-2, NFR-5) ----------


def test_samme_skjema_id_gir_duplikat_til_samme_oppdrag(db, kari) -> None:
    """NFR-5: andre innsending med samme `skjema_id` gir `Duplikat`, og bare én rad finnes."""
    forste = opprett(db, kari.id, skjema_id="dobbel-skjema-id-0001")
    with pytest.raises(Duplikat) as duplikat:
        opprett(db, kari.id, skjema_id="dobbel-skjema-id-0001")
    assert duplikat.value.til_url == detaljer_url(forste) == f"/oppdrag/{forste}"
    assert antall(db) == 1


def test_duplikat_med_feil_viser_feilene(db, kari) -> None:
    """Valideringen kjører før innsettingen, så en ny innsending med feil gir feilene."""
    opprett(db, kari.id, skjema_id="dobbel-skjema-id-0002")
    with pytest.raises(RegelBrudd):
        opprett(db, kari.id, skjema_id="dobbel-skjema-id-0002", tittel="")


def test_skjema_id_fra_annen_bruker_gir_duplikat(db, kari, lag_bruker) -> None:
    """Spec 2.1: `Duplikat` sender dit, og tilgangsregelen avgjør hva hen får se."""
    forste = opprett(db, kari.id, skjema_id="dobbel-skjema-id-0003")
    with pytest.raises(Duplikat) as duplikat:
        opprett(db, lag_bruker().id, skjema_id="dobbel-skjema-id-0003")
    assert duplikat.value.til_url == detaljer_url(forste)


def test_detaljer_url_er_lik_rutens_sti(app) -> None:
    assert detaljer_url(42) == app.url_path_for("oppdrag.detaljer", id=42)


# ---------- vise (FR-9, AD-16) ----------


def test_hent_for_visning_eget_og_andres(db, kari, lag_bruker, lag_oppdrag) -> None:
    oppdrag = lag_oppdrag(oppdragsgiver=kari, belop=None, kategori="hage")
    eget = hent_for_visning(db, oppdrag.id, kari.id)
    assert eget.er_eier and eget.sted == "0571 Oslo" and eget.belop is None and eget.kategori == "hage"
    andres = hent_for_visning(db, oppdrag.id, lag_bruker().id)
    assert not andres.er_eier and andres.status == "apen"


def test_oppdragvisning_har_ingen_personfelt() -> None:
    """AD-16: malene får aldri telefon, e-post, fødselsdato eller navn.

    Fra story 2.3 har `OppdragVisning` eier-id-en, fordi oppdragsgiverblokken lenker til
    `/profil/{id}` («Se profil»). Id-en er ingen personopplysning, den står i lenken.
    """
    felt = {f.name for f in dataclasses.fields(OppdragVisning)}
    assert felt.isdisjoint({"telefon", "epost", "fodselsdato", "navn", "skjema_id"})
    assert "oppdragsgiver_id" in felt


def test_finnes_ikke(db, kari) -> None:
    with pytest.raises(FinnesIkke):
        hent_for_visning(db, 999_999, kari.id)


@pytest.mark.parametrize("status", ["avbrutt", "utfort", "hjelper_valgt"])
def test_andres_ikke_apne_gir_ingen_tilgang(db, kari, lag_bruker, lag_oppdrag, status: str) -> None:
    """FR-9: bare oppdragsgiveren og valgt hjelper ser oppdrag som ikke er åpne."""
    hjelper = lag_bruker()
    oppdrag = lag_oppdrag(oppdragsgiver=kari, status=status, valgt_hjelper_id=hjelper.id)
    with pytest.raises(IngenTilgang):
        hent_for_visning(db, oppdrag.id, lag_bruker().id)
    assert hent_for_visning(db, oppdrag.id, kari.id).status == status
    assert hent_for_visning(db, oppdrag.id, hjelper.id).status == status


def test_passert_apent_oppdrag_kan_ses_av_andre(db, kari, lag_bruker, lag_oppdrag) -> None:
    oppdrag = lag_oppdrag(oppdragsgiver=kari, tidspunkt=datetime(2026, 11, 1, tzinfo=timezone.utc))
    assert hent_for_visning(db, oppdrag.id, lag_bruker().id).status == "apen"


def test_lagt_ut_av_gir_egne_nyeste_forst(db, kari, lag_oppdrag) -> None:
    a = lag_oppdrag(oppdragsgiver=kari, tittel="A", opprettet=datetime(2026, 11, 1, tzinfo=timezone.utc))
    b = lag_oppdrag(oppdragsgiver=kari, tittel="B", opprettet=datetime(2026, 11, 2, tzinfo=timezone.utc))
    lag_oppdrag(tittel="Andres")
    assert [(r.id, r.tittel) for r in lagt_ut_av(db, kari.id)] == [(b.id, "B"), (a.id, "A")]
