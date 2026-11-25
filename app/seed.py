"""Gjør databasen klar lokalt: `uv run python -m app.seed` (NFR-1, NFR-2, AD-14).

Kjører `alembic upgrade head`, som også laster postnumrene, og legger inn seks
oppdiktede testbrukere i tre postnumre. Passordene lagres bare som hash, med
`hash_passord` fra identity (NFR-4, AD-6). Seed kan kjøres flere ganger: en
bruker som allerede finnes, røres ikke. Eksempeloppdrag kommer i story 2.1 og
senere. Nekter å kjøre i produksjon (AD-14).

Testbrukerne er bare for lokal testing. Tabellen står også i README.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core import klokke
from app.core.config import hent_settings
from app.core.db import lag_motor, lag_sesjonsfabrikk, url_uten_passord
from app.identity.models import Bruker, Innloggingsforsok, Sesjon
from app.identity.service import hash_passord, normaliser_epost

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


def last_eksempeldata(db: Session) -> None:
    """Nullstiller databasen til testbrukerne og ingenting annet (AR-29, AD-14).

    Brukes av `POST /_test/tilstand` med `seed=1` i T1, gjennom
    `app.state.last_eksempeldata`. Sletter `sesjon`, `innloggingsforsok` og
    `bruker` i den rekkefølgen (fremmednøklene) og legger inn testbrukerne på
    nytt. Senere stories legger til egne tabeller her. Committer ikke.
    """
    db.execute(delete(Sesjon))
    db.execute(delete(Innloggingsforsok))
    db.execute(delete(Bruker))
    legg_inn_testbrukere(db)


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
    finally:
        motor.dispose()
    print(f"Databasen er klar ({url_uten_passord(settings.database_url)}).")
    print(f"Testbrukere: {len(TESTBRUKERE)} ({nye} nye). Se README for e-post og passord.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
