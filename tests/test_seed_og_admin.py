"""Testbrukere og eksempeloppdrag i seed, og `app.admin nytt-passord` (NFR-2, NFR-4, AR-9, AR-29, NFR-5, T-3)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import func, inspect, select

from app import admin, seed
from app.core import tid
from app.core.config import Settings
from app.core.db import Base, lag_motor, url_uten_passord
from app.core.domene import KATEGORIKODER
from app.core.postnummer import finnes
from app.identity.models import Bruker, Innloggingsforsok, Sesjon
from app.identity.service import logg_inn, sjekk_passord
from app.oppdrag.models import Oppdrag, Oppdragsbilde

from .conftest import ROT, STANDARD_PASSORD

# Tirsdag 24. november 2026 kl. 13 i Oslo.
T0 = datetime(2026, 11, 24, 12, 0, tzinfo=timezone.utc)
EIERE = {"kari@eksempel.no", "nora@eksempel.no", "sofie@eksempel.no"}


def test_testbrukerne_oppfyller_nfr2() -> None:
    """NFR-2: minst 6 oppdiktede brukere i 2–3 postnumre som finnes."""
    assert len(seed.TESTBRUKERE) == 6
    postnumre = {t.postnummer for t in seed.TESTBRUKERE}
    assert 2 <= len(postnumre) <= 3
    assert all(finnes(p) for p in postnumre)
    assert len({t.epost for t in seed.TESTBRUKERE}) == 6
    assert all(t.epost.endswith("@eksempel.no") for t in seed.TESTBRUKERE)


def test_seed_to_ganger_gir_seks_brukere_med_hash(db) -> None:
    """NFR-2/NFR-4: seed kan kjøres to ganger, og `passord_hash` inneholder ikke passordet."""
    assert seed.legg_inn_testbrukere(db) == 6
    assert seed.legg_inn_testbrukere(db) == 0
    eposter = [t.epost for t in seed.TESTBRUKERE]
    brukere = db.scalars(select(Bruker).where(Bruker.epost.in_(eposter))).all()
    assert len(brukere) == 6
    for testbruker in seed.TESTBRUKERE:
        bruker = next(b for b in brukere if b.epost == testbruker.epost)
        assert testbruker.passord not in bruker.passord_hash
        assert sjekk_passord(testbruker.passord, bruker.passord_hash)


def test_testbrukerne_star_i_readme() -> None:
    """NFR-2: README har tabellen, merket «bare for lokal testing»."""
    readme = (ROT / "README.md").read_text(encoding="utf-8")
    assert "bare for lokal testing" in readme
    for testbruker in seed.TESTBRUKERE:
        assert testbruker.navn in readme
        assert testbruker.epost in readme
        assert testbruker.passord in readme
    assert "uv run python -m app.admin nytt-passord" in readme


def test_eksempeloppdragene_star_i_readme() -> None:
    """NFR-2: README beskriver eksempeloppdragene, med tittel på hvert av dem."""
    readme = (ROT / "README.md").read_text(encoding="utf-8")
    assert f"{len(seed.EKSEMPELOPPDRAG)} eksempeloppdrag" in readme
    for eksempel in seed.EKSEMPELOPPDRAG:
        assert eksempel.tittel in readme, eksempel.tittel


def test_eksempeloppdragene_oppfyller_nfr2() -> None:
    """NFR-2 (story 2.1): 10–15 oppdrag, bare Kari, Nora og Sofie eier, alle kategorier blant de åpne.

    Minst ett er utgått og minst ett avbrutt, minst ett av Noras ligger i 0571,
    og klokkeslettene er hele timer mellom 9 og 18.
    """
    eksempler = seed.EKSEMPELOPPDRAG
    assert 10 <= len(eksempler) <= 15
    assert {e.eier for e in eksempler} == EIERE
    apne_fram_i_tid = [e for e in eksempler if not e.avbrutt and e.dager > 0]
    assert {e.kategori for e in apne_fram_i_tid} == KATEGORIKODER
    assert any(e.dager < 0 and not e.avbrutt for e in eksempler)  # utgått (FR-8)
    assert any(e.avbrutt for e in eksempler)
    assert any(e.eier == "nora@eksempel.no" and e.postnummer == "0571" for e in eksempler)
    assert all(9 <= e.klokka <= 18 for e in eksempler)
    assert all(finnes(e.postnummer) for e in eksempler)
    assert len({e.tittel for e in eksempler}) == len(eksempler)


def test_eksempeloppdragene_i_databasen(db, sett_na) -> None:
    """NFR-2, AD-2, AD-9: tidspunkt relative til klokka, hele timer i norsk tid, avbrutt gjennom `endre_status`."""
    sett_na(T0)
    seed.last_eksempeldata(db)
    db.commit()
    oppdrag = db.scalars(select(Oppdrag)).all()
    assert len(oppdrag) == len(seed.EKSEMPELOPPDRAG)
    eiere = {b.id: b.epost for b in db.scalars(select(Bruker)).all()}
    assert {eiere[o.oppdragsgiver_id] for o in oppdrag} == EIERE
    for o in oppdrag:
        lokal = o.tidspunkt.astimezone(tid.OSLO)
        assert (lokal.minute, lokal.second) == (0, 0) and 9 <= lokal.hour <= 18, o.tittel
        assert o.opprettet <= T0
        assert o.skjema_id
    avbrutte = [o for o in oppdrag if o.status == "avbrutt"]
    assert avbrutte and all(o.versjon == 2 for o in avbrutte)  # gjennom endre_status
    assert any(o.status == "apen" and o.tidspunkt < T0 for o in oppdrag)  # utgått
    apne = [o for o in oppdrag if o.status == "apen" and o.tidspunkt > T0]
    assert {o.kategori for o in apne} == KATEGORIKODER
    assert all(o.tidspunkt <= T0 + timedelta(days=60) for o in oppdrag)


def test_eksempeloppdragene_har_ett_utfort_med_nora_som_hjelper() -> None:
    """FR-9, story 2.3: ett av Karis oppdrag er passert og utført med Nora som hjelper."""
    utforte = [e for e in seed.EKSEMPELOPPDRAG if e.utfort_av]
    assert len(utforte) == 1
    (utfort,) = utforte
    assert (utfort.eier, utfort.utfort_av, utfort.postnummer) == (
        "kari@eksempel.no", "nora@eksempel.no", "0571",
    )
    assert utfort.dager < 0 and not utfort.avbrutt
    assert utfort.lagt_ut_dager_siden > -utfort.dager


def test_utfort_oppdrag_i_databasen(db, sett_na) -> None:
    """FR-9, AD-2: utført gjennom `endre_status` (apen → hjelper_valgt → utfort), med Nora som
    valgt hjelper, så `erfaring` gir Nora ett fullført oppdrag."""
    from app.oppdrag.service import erfaring

    sett_na(T0)
    seed.last_eksempeldata(db)
    db.commit()
    nora = db.scalar(select(Bruker.id).where(Bruker.epost == "nora@eksempel.no"))
    (utfort,) = db.scalars(select(Oppdrag).where(Oppdrag.status == "utfort")).all()
    assert utfort.tittel == "Bytte lyspære i taket"
    assert utfort.valgt_hjelper_id == nora
    assert utfort.versjon == 3
    assert utfort.tidspunkt < T0
    assert erfaring(db, [nora])[nora].fullforte == 1


def _tell(url: str) -> dict[str, int]:
    motor = lag_motor(url)
    try:
        with motor.connect() as tilkobling:
            return {
                "brukere": tilkobling.scalar(select(func.count()).select_from(Bruker)),
                "oppdrag": tilkobling.scalar(select(func.count()).select_from(Oppdrag)),
                "bilder": tilkobling.scalar(select(func.count()).select_from(Oppdragsbilde)),
            }
    finally:
        motor.dispose()


def test_seed_main_to_ganger_pa_ren_database(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    """NFR-2, invariant 1.5: samme seks brukere og testbrukernes oppdrag byttes ut, ingen andre røres."""
    url = f"sqlite:///{(tmp_path / 'seed.db').as_posix()}"
    settings = Settings(_env_file=None, app_env="local", database_url=url)
    monkeypatch.setattr(seed, "hent_settings", lambda: settings)
    monkeypatch.setattr("app.core.config.hent_settings", lambda: settings)
    assert seed.main() == 0
    assert _tell(url) == {"brukere": 6, "oppdrag": len(seed.EKSEMPELOPPDRAG), "bilder": 4}

    # En annen bruker med eget oppdrag skal stå urørt etter neste seed.
    motor = lag_motor(url)
    try:
        with motor.begin() as tilkobling:
            na = datetime.now(timezone.utc)
            annen = tilkobling.execute(
                Bruker.__table__.insert().values(navn="Annen", epost="annen@eksempel.no", opprettet=na)
            ).inserted_primary_key[0]
            tilkobling.execute(
                Oppdrag.__table__.insert().values(
                    oppdragsgiver_id=annen, tittel="Annens oppdrag", beskrivelse="Beskrivelse her.",
                    kategori="annet", postnummer="0571", tidspunkt=na + timedelta(days=2), belop=None,
                    status="apen", versjon=1, skjema_id="annen-skjema-id-123", opprettet=na,
                )
            )
            gamle_ider = set(tilkobling.scalars(select(Oppdrag.id)).all())
    finally:
        motor.dispose()

    # Andre kjøring feiler ikke på fremmednøkkelen fra `oppdragsbilde` (story 2.7, AD-2).
    assert seed.main() == 0
    assert _tell(url) == {"brukere": 7, "oppdrag": len(seed.EKSEMPELOPPDRAG) + 1, "bilder": 4}
    motor = lag_motor(url)
    try:
        with motor.connect() as tilkobling:
            assert tilkobling.scalar(select(Oppdrag.tittel).where(Oppdrag.oppdragsgiver_id == annen)) == (
                "Annens oppdrag"
            )
            nye_ider = set(tilkobling.scalars(select(Oppdrag.id).where(Oppdrag.oppdragsgiver_id != annen)).all())
    finally:
        motor.dispose()
    assert not nye_ider & gamle_ider  # testbrukernes oppdrag er lagt inn på nytt


def test_url_uten_passord() -> None:
    assert url_uten_passord("postgresql+psycopg://u:hemmelig@h:5432/d") == "postgresql+psycopg://u:***@h:5432/d"


# ---------- admin ----------


def svar(*verdier):
    rest = list(verdier)
    return lambda _ledetekst: rest.pop(0)


def test_admin_nytt_passord(db, sesjonsfabrikk, lag_bruker, capsys) -> None:
    """AR-9: Kari kan logge inn med det nye passordet; gamle sesjoner og tellere er slettet."""
    kari = lag_bruker(epost="kari@eksempel.no")
    nokkel = logg_inn(db, "kari@eksempel.no", STANDARD_PASSORD).nokkel
    logg_inn(db, "kari@eksempel.no", "feil")
    db.commit()
    assert nokkel

    kode = admin.main(
        ["nytt-passord", " Kari@Eksempel.no "],
        sesjonsfabrikk=sesjonsfabrikk,
        les_passord=svar("nytt-passord-9", "nytt-passord-9"),
        spor=svar("ja"),
    )
    assert kode == 0
    db.expire_all()
    assert db.scalar(select(func.count()).select_from(Sesjon).where(Sesjon.bruker_id == kari.id)) == 0
    assert db.scalar(select(func.count()).select_from(Innloggingsforsok)) == 0
    assert logg_inn(db, "kari@eksempel.no", "nytt-passord-9").vellykket
    assert not logg_inn(db, "kari@eksempel.no", STANDARD_PASSORD).vellykket
    utskrift = capsys.readouterr()
    assert "Database: sqlite" in utskrift.out or "Database: postgresql" in utskrift.out
    assert "nytt-passord-9" not in utskrift.out + utskrift.err
    assert "kari@eksempel.no" not in utskrift.out + utskrift.err


@pytest.mark.parametrize(
    ("passord", "bekreftelse", "melding"),
    [
        (("kort", "kort"), "ja", "8–64 tegn"),
        (("        ", "        "), "ja", "bare være mellomrom"),
        (("nytt-passord-9", "annet-passord-9"), "ja", "ikke like"),
        (("nytt-passord-9", "nytt-passord-9"), "nei", "Avbrutt"),
    ],
    ids=["for-kort", "bare-mellomrom", "ulike", "ikke-ja"],
)
def test_admin_endrer_ingenting_ved_feil(
    db, sesjonsfabrikk, lag_bruker, capsys, passord, bekreftelse, melding
) -> None:
    kari = lag_bruker(epost="kari@eksempel.no")
    gammel_hash = kari.passord_hash
    kode = admin.main(
        ["nytt-passord", "kari@eksempel.no"],
        sesjonsfabrikk=sesjonsfabrikk,
        les_passord=svar(*passord),
        spor=svar(bekreftelse),
    )
    assert kode == 1
    utskrift = capsys.readouterr()
    assert melding in utskrift.out + utskrift.err
    assert "Ingenting er endret." in utskrift.out + utskrift.err
    db.expire_all()
    assert db.get(Bruker, kari.id).passord_hash == gammel_hash


def test_admin_ukjent_eller_slettet_bruker(db, sesjonsfabrikk, lag_bruker, capsys) -> None:
    lag_bruker(epost="borte@eksempel.no", slettet_tidspunkt=datetime(2026, 11, 1, tzinfo=timezone.utc))
    for epost in ("ukjent@eksempel.no", "borte@eksempel.no"):
        kode = admin.main(
            ["nytt-passord", epost],
            sesjonsfabrikk=sesjonsfabrikk,
            les_passord=svar("nytt-passord-9", "nytt-passord-9"),
            spor=svar("ja"),
        )
        assert kode == 1
    assert "Fant ingen aktiv bruker" in capsys.readouterr().err


# Tabellene testen under lager fremmede rader i. En ny tabell i `Base.metadata`
# må legges til her, med en fremmed rad i testen (T-3).
TABELLER_MED_FREMMEDE_RADER = {"bruker", "sesjon", "innloggingsforsok", "oppdrag", "oppdragsbilde"}


def test_last_eksempeldata_gir_bare_testbrukerne_og_eksempeloppdragene(
    db, lag_bruker, lag_oppdrag, lag_bilde
) -> None:
    """AR-29, T-3: fremmede rader i hver tabell forsvinner, og bare seed-dataene står igjen."""
    annen = lag_bruker(epost="annen@eksempel.no")
    fremmed = lag_oppdrag(oppdragsgiver=annen, skjema_id="fremmed-skjema-id-1")
    lag_bilde(fremmed)
    logg_inn(db, "annen@eksempel.no", STANDARD_PASSORD)
    logg_inn(db, "annen@eksempel.no", "feil")
    db.commit()
    assert db.scalar(select(func.count()).select_from(Sesjon)) == 1
    assert db.scalar(select(func.count()).select_from(Innloggingsforsok)) == 1

    seed.last_eksempeldata(db)
    seed.last_eksempeldata(db)  # to ganger gir samme resultat
    db.commit()

    assert {t.name for t in Base.metadata.sorted_tables} - {"postnummer"} == TABELLER_MED_FREMMEDE_RADER
    assert db.scalar(select(func.count()).select_from(Sesjon)) == 0
    assert db.scalar(select(func.count()).select_from(Innloggingsforsok)) == 0
    eposter = set(db.scalars(select(Bruker.epost)).all())
    assert eposter == {t.epost for t in seed.TESTBRUKERE}
    skjema_ider = set(db.scalars(select(Oppdrag.skjema_id)).all())
    assert fremmed.skjema_id not in skjema_ider
    assert len(skjema_ider) == len(seed.EKSEMPELOPPDRAG)
    assert db.scalar(select(func.count()).select_from(Oppdrag)) == len(seed.EKSEMPELOPPDRAG)
    assert db.scalar(select(func.count()).select_from(Oppdragsbilde)) == 4  # bare seed-bildene


# ---------- bilder i seed (story 2.7, FR-27, NFR-2) ----------

BILDER_I_SEED = {
    "Måke snø i innkjørselen": "kari@eksempel.no",
    "Mate katten i helgen": "nora@eksempel.no",
    "Flytte sofa ned i kjelleren": "nora@eksempel.no",
    "Klippe hekken": "sofie@eksempel.no",
}


def test_fire_eksempeloppdrag_har_bilde_i_fire_kategorier() -> None:
    """FR-27, NFR-2: fire oppdrag med motiv og bildetekst på 3–120 tegn, i fire kategorier."""
    med_bilde = [e for e in seed.EKSEMPELOPPDRAG if e.bilde]
    assert {e.tittel: e.eier for e in med_bilde} == BILDER_I_SEED
    assert len({e.kategori for e in med_bilde}) == 4
    assert {e.bilde for e in med_bilde} == set(seed.MOTIVER)
    for e in med_bilde:
        assert e.bildetekst and 3 <= len(e.bildetekst) <= 120, e.tittel
        assert not e.avbrutt and e.dager > 0, e.tittel  # åpne, så de vises i oversikten
    # Ola i 0571 ser to kort med bilde (Karis «Måke snø» og Noras «Mate katten»).
    i_0571 = [e for e in med_bilde if e.postnummer == "0571"]
    assert len(i_0571) == 2


def test_bildene_i_seed_er_tegnet_og_behandlet(db, sett_na) -> None:
    """FR-27, AD-18: bildene i databasen er JPEG-er uten EXIF fra `oppdrag/bilde.py`."""
    from tests.bilder import apne

    sett_na(T0)
    seed.last_eksempeldata(db)
    db.commit()
    rader = db.execute(
        select(Oppdrag.tittel, Oppdragsbilde.bildetekst, Oppdragsbilde.bilde, Oppdragsbilde.miniatyr,
               Oppdragsbilde.bredde, Oppdragsbilde.hoyde)
        .join(Oppdragsbilde, Oppdragsbilde.oppdrag_id == Oppdrag.id)
    ).all()
    assert {r.tittel for r in rader} == set(BILDER_I_SEED)
    for rad in rader:
        stor, liten = apne(rad.bilde), apne(rad.miniatyr)
        assert stor.format == liten.format == "JPEG"
        assert stor.size == (rad.bredde, rad.hoyde) and max(stor.size) <= 1600
        assert max(liten.size) <= 640
        assert not stor.getexif() and not liten.getexif()


def test_readme_forteller_om_bildene() -> None:
    """FR-27, NFR-2: README sier hvilke fire som har bilde, og at Kari kan bytte og fjerne det."""
    readme = (ROT / "README.md").read_text(encoding="utf-8")
    for tittel in BILDER_I_SEED:
        assert f"«{tittel}»" in readme, tittel
    assert "Bytt bilde" in readme and "Fjern bildet" in readme


def test_alle_tabellene_i_databasen_finnes_i_metadataen(tilkobling) -> None:
    """T-3: når `app.seed` er importert, kjenner `Base.metadata` hver tabell, så `last_eksempeldata` tømmer alt."""
    tabeller = set(inspect(tilkobling).get_table_names()) - {"alembic_version"}
    assert tabeller == set(Base.metadata.tables)
