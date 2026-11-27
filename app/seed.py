"""Gjør databasen klar lokalt: `uv run python -m app.seed` (NFR-1, NFR-2, AD-14).

Kjører `alembic upgrade head`, som også laster postnumrene, og legger inn seks
oppdiktede testbrukere i tre postnumre og 13 eksempeloppdrag. Passordene
lagres bare som hash, med `hash_passord` fra identity (NFR-4, AD-6). Seed kan
kjøres flere ganger: en bruker som allerede finnes, røres ikke, og
testbrukernes oppdrag byttes ut, så tidspunktene alltid er relative til
innlastingen. Andre brukere og deres oppdrag røres ikke. Nekter å kjøre i
produksjon (AD-14).

`last_eksempeldata` (bare for test, `POST /_test/tilstand`) tømmer alle
tabellene unntatt `postnummer` og legger inn det samme på nytt.

Testbrukerne og eksempeloppdragene er bare for lokal testing. Tabellene står også i README.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core import klokke, tid
from app.core.config import hent_settings
from app.core.db import Base, lag_motor, lag_sesjonsfabrikk, url_uten_passord
from app.core.postnummer import postnummer_tabell
from app.identity.models import Bruker
from app.identity.service import hash_passord, normaliser_epost
from app.oppdrag.models import Oppdrag
from app.oppdrag.service import endre_status, ny_skjema_id

ROT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Testbruker:
    navn: str
    epost: str
    passord: str
    telefon: str
    postnummer: str
    fodselsdato: date
    rolle: str


# Bare for lokal testing. Oppdiktede personer; passordene er ikke hemmelige.
TESTBRUKERE: tuple[Testbruker, ...] = (
    Testbruker("Kari Nordmann", "kari@eksempel.no", "kari-lokal-1", "41000001", "0571",
               date(1954, 5, 3), "Oppdragsgiver (UJ-1): legger ut oppdrag og velger hjelper."),
    Testbruker("Ola Hansen", "ola@eksempel.no", "ola-lokal-1", "41000002", "0571",
               date(1968, 9, 12), "Hjelper i samme postnummer som Kari: melder interesse og konkurrerer med Amir."),
    Testbruker("Amir Haddad", "amir@eksempel.no", "amir-lokal-1", "41000003", "0572",
               date(2005, 2, 14), "Hjelper (UJ-2): melder interesse, blir valgt og bygger profil."),
    Testbruker("Nora Berg", "nora@eksempel.no", "nora-lokal-1", "41000004", "0572",
               date(1990, 11, 30), "Oppdragsgiver i 0572: oppdrag i et annet postnummer enn Kari."),
    Testbruker("Sofie Lie", "sofie@eksempel.no", "sofie-lokal-1", "41000005", "5006",
               date(1985, 6, 21), "Oppdragsgiver i Bergen: viser at oversikten bare viser eget postnummer."),
    Testbruker("Jonas Dahl", "jonas@eksempel.no", "jonas-lokal-1", "41000006", "5006",
               date(2000, 3, 8), "Hjelper i Bergen: tester postnummerfilteret og andre postnumre."),
)


@dataclass(frozen=True)
class Eksempeloppdrag:
    """Et oppdrag i seed. Tidspunktet er `dager` fra i dag kl. `klokka` norsk tid."""

    eier: str  # e-posten til testbrukeren
    tittel: str
    beskrivelse: str
    kategori: str
    postnummer: str
    dager: int  # negativt: tidspunktet er passert (utgått oppdrag, FR-8)
    klokka: int  # hel time mellom 9 og 18
    belop: int | None  # None: «Uten betaling»
    lagt_ut_dager_siden: int
    avbrutt: bool = False  # avbrytes gjennom `endre_status` etter innsettingen
    # E-posten til hjelperen som utførte oppdraget. Oppdraget går gjennom
    # `endre_status` apen → hjelper_valgt → utfort, med hjelperen som valgt hjelper.
    utfort_av: str | None = None


# Bare for lokal testing. Oppdiktede oppdrag (NFR-2). Bare Kari, Nora og Sofie eier
# oppdrag. Alle seks kategorier finnes blant de åpne, ett er utgått, ett avbrutt og
# ett utført med Nora som hjelper, så oppdragsgiverblokken på Noras oppdrag viser
# «1 fullført oppdrag» (FR-9, story 2.3).
EKSEMPELOPPDRAG: tuple[Eksempeloppdrag, ...] = (
    Eksempeloppdrag("kari@eksempel.no", "Måke snø i innkjørselen",
                    "Trenger noen som kan måke snø i innkjørselen min i morgen tidlig.",
                    "snomaking", "0571", 1, 9, 200, 1),
    Eksempeloppdrag("kari@eksempel.no", "Raking av løv i hagen",
                    "Hagen er full av løv etter stormen. Jeg har river og sekker.",
                    "hage", "0571", 4, 11, 300, 2),
    Eksempeloppdrag("kari@eksempel.no", "Hjelp med nytt nettbrett",
                    "Jeg har fått et nytt nettbrett og trenger hjelp til å komme i gang med e-post og bilder.",
                    "teknologihjelp", "0571", 6, 14, None, 1),
    Eksempeloppdrag("kari@eksempel.no", "Bære ved opp til tredje etasje",
                    "Jeg har fått levert ved i oppkjørselen og trenger hjelp til å bære den opp trappa.",
                    "baerehjelp-flytting", "0571", -2, 10, 400, 6),
    Eksempeloppdrag("kari@eksempel.no", "Lufte hunden mens jeg er bortreist",
                    "Jeg skal på besøk til datteren min og trenger noen som kan lufte Bamse morgen og kveld.",
                    "dyrepass", "0571", 10, 16, 500, 3, avbrutt=True),
    Eksempeloppdrag("nora@eksempel.no", "Mate katten i helgen",
                    "Katten Pus trenger mat og vann lørdag og søndag. Nøkkel avtales når hjelperen er valgt.",
                    "dyrepass", "0571", 3, 12, 250, 1),
    Eksempeloppdrag("nora@eksempel.no", "Flytte sofa ned i kjelleren",
                    "En tung sofa skal ned én trapp til kjelleren. Det trengs to personer.",
                    "baerehjelp-flytting", "0572", 5, 17, 600, 2),
    Eksempeloppdrag("nora@eksempel.no", "Henge opp gardiner",
                    "Jeg trenger hjelp til å henge opp tre gardinstenger. Drill og skruer finnes.",
                    "annet", "0572", 8, 13, 350, 1),
    Eksempeloppdrag("nora@eksempel.no", "Måke trappa før helgen",
                    "Trappa opp til inngangen må måkes og strøs før gjestene kommer på fredag.",
                    "snomaking", "0572", 2, 15, 150, 1),
    Eksempeloppdrag("sofie@eksempel.no", "Klippe hekken",
                    "Hekken mot veien har vokst seg høy og må klippes ned til brysthøyde.",
                    "hage", "5006", 7, 10, 450, 2),
    Eksempeloppdrag("sofie@eksempel.no", "Sette opp skriver",
                    "Ny skriver skal kobles til det trådløse nettet og til PC-en min.",
                    "teknologihjelp", "5006", 3, 18, 200, 1),
    Eksempeloppdrag("sofie@eksempel.no", "Handle og bære opp varer",
                    "Jeg har brukket armen og trenger hjelp til å bære opp ukens varer fra butikken på hjørnet.",
                    "annet", "5006", 1, 16, None, 1),
    Eksempeloppdrag("kari@eksempel.no", "Bytte lyspære i taket",
                    "Lampen i stua henger høyt, og jeg vil ikke gå opp på stigen alene.",
                    "annet", "0571", -5, 12, 150, 8, utfort_av="nora@eksempel.no"),
)


def alembic_config() -> Config:
    return Config(str(ROT / "alembic.ini"))


def legg_inn_testbrukere(db: Session) -> int:
    """Legger inn testbrukerne som mangler. Gir antall nye. Committer ikke."""
    nye = 0
    for testbruker in TESTBRUKERE:
        epost = normaliser_epost(testbruker.epost)
        if db.scalar(select(Bruker.id).where(Bruker.epost == epost)) is not None:
            continue
        db.add(
            Bruker(
                navn=testbruker.navn,
                epost=epost,
                passord_hash=hash_passord(testbruker.passord),
                telefon=testbruker.telefon,
                postnummer=testbruker.postnummer,
                fodselsdato=testbruker.fodselsdato,
                opprettet=klokke.na(),
            )
        )
        nye += 1
    db.flush()
    return nye


def _testbruker_ider(db: Session) -> dict[str, int]:
    eposter = [normaliser_epost(t.epost) for t in TESTBRUKERE]
    rader = db.execute(select(Bruker.epost, Bruker.id).where(Bruker.epost.in_(eposter))).all()
    return {rad.epost: rad.id for rad in rader}


def legg_inn_eksempeloppdrag(db: Session) -> int:
    """Legger inn `EKSEMPELOPPDRAG` for testbrukerne. Gir antallet. Committer ikke.

    Tidspunktene er relative til `klokke.na()`, med hele klokkeslett i norsk
    tid. De avbrutte legges inn som åpne og avbrytes gjennom `endre_status`
    (AD-2), slik appen gjør. De utførte går gjennom `endre_status` til
    `hjelper_valgt`, får hjelperen som `valgt_hjelper_id` og går så til `utfort`.
    """
    na = klokke.na()
    i_dag = na.astimezone(tid.OSLO).date()
    ider = _testbruker_ider(db)
    for nummer, eksempel in enumerate(EKSEMPELOPPDRAG):
        eier_id = ider[normaliser_epost(eksempel.eier)]
        lokal = datetime.combine(i_dag + timedelta(days=eksempel.dager), time(eksempel.klokka))
        oppdrag = Oppdrag(
            oppdragsgiver_id=eier_id,
            tittel=eksempel.tittel,
            beskrivelse=eksempel.beskrivelse,
            kategori=eksempel.kategori,
            postnummer=eksempel.postnummer,
            tidspunkt=tid.til_utc(lokal),
            belop=eksempel.belop,
            status="apen",
            versjon=1,
            skjema_id=ny_skjema_id(),
            # Ulike minutter, så rekkefølgen etter `opprettet` er fast.
            opprettet=na - timedelta(days=eksempel.lagt_ut_dager_siden, minutes=nummer),
        )
        db.add(oppdrag)
        db.flush()
        if eksempel.avbrutt:
            endre_status(db, oppdrag.id, fra="apen", til="avbrutt", oppdragsgiver_id=eier_id)
        if eksempel.utfort_av:
            endre_status(db, oppdrag.id, fra="apen", til="hjelper_valgt", oppdragsgiver_id=eier_id)
            # Valget av hjelper får egen funksjon i Epic 3. Til da settes hjelperen her.
            oppdrag.valgt_hjelper_id = ider[normaliser_epost(eksempel.utfort_av)]
            db.flush()
            endre_status(db, oppdrag.id, fra="hjelper_valgt", til="utfort", oppdragsgiver_id=eier_id)
    return len(EKSEMPELOPPDRAG)


def bytt_ut_eksempeloppdrag(db: Session) -> int:
    """Sletter testbrukernes oppdrag og legger inn `EKSEMPELOPPDRAG` på nytt. Committer ikke.

    Andre brukeres oppdrag røres ikke (invarianten fra story 1.5).
    """
    ider = list(_testbruker_ider(db).values())
    db.execute(delete(Oppdrag).where(Oppdrag.oppdragsgiver_id.in_(ider)))
    return legg_inn_eksempeloppdrag(db)


def last_eksempeldata(db: Session) -> None:
    """Nullstiller databasen til testbrukerne og eksempeloppdragene (AR-29, AD-14, T-3).

    Brukes av `POST /_test/tilstand` med `seed=1` i T1, gjennom
    `app.state.last_eksempeldata`. Tømmer alle tabellene i `Base.metadata`
    unntatt `postnummer`, barn før foreldre, så nye tabeller tømmes uten at
    denne funksjonen endres. Committer ikke.
    """
    for tabell in reversed(Base.metadata.sorted_tables):
        if tabell is not postnummer_tabell:
            db.execute(tabell.delete())
    # Radene er borte, så objekter sesjonen husker, hører ikke til noe lenger.
    db.expunge_all()
    legg_inn_testbrukere(db)
    legg_inn_eksempeloppdrag(db)


def main() -> int:
    settings = hent_settings()
    if settings.produksjon:
        print("Seed kjøres ikke i produksjon (APP_ENV=production).", file=sys.stderr)
        return 1
    command.upgrade(alembic_config(), "head")
    motor = lag_motor(settings.database_url)
    try:
        with lag_sesjonsfabrikk(motor)() as db, db.begin():
            nye = legg_inn_testbrukere(db)
            oppdrag = bytt_ut_eksempeloppdrag(db)
    finally:
        motor.dispose()
    print(f"Databasen er klar ({url_uten_passord(settings.database_url)}).")
    print(f"Testbrukere: {len(TESTBRUKERE)} ({nye} nye). Se README for e-post og passord.")
    print(f"Eksempeloppdrag: {oppdrag} (testbrukernes oppdrag er lagt inn på nytt).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
