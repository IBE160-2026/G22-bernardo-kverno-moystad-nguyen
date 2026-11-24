"""Manuell hjelp til brukere (AR-9, AD-6): `uv run python -m app.admin nytt-passord <e-post>`.

Glemt passord er utsatt i v1 (PRD §6.2), så gruppen setter et nytt passord
for hånd. Kommandoen bruker de samme funksjonene som innloggingen
(`hash_passord`, `normaliser_epost`) og sletter brukerens gamle sesjoner og
mislykkede innloggingsforsøk.

- Passordet leses to ganger med `getpass`, aldri som argument, så det ikke
  havner i skallhistorikken. Det må ha 8–64 tegn (FR-1) og ikke bare
  mellomrom, fordi innloggingen regner et slikt passord som tomt.
- Kommandoen virker mot den `DATABASE_URL` som er satt, også produksjon.
  Før den endrer noe, viser den hvilken database den er koblet til (uten
  passord) og krever at du skriver `ja`.
- Verken passord eller e-post skrives ut eller logges.

`slett-konto` kommer i story 4.5.
"""

from __future__ import annotations

import argparse
import getpass
import sys
from collections.abc import Callable, Sequence

from sqlalchemy.orm import Session, sessionmaker

from app.core.config import hent_settings
from app.core.db import lag_motor, lag_sesjonsfabrikk, url_uten_passord
from app.identity.service import PASSORD_MAKS, PASSORD_MIN, passord_har_gyldig_lengde, sett_nytt_passord


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m app.admin", description="Manuell hjelp til brukere.")
    kommandoer = parser.add_subparsers(dest="kommando", required=True)
    nytt = kommandoer.add_parser("nytt-passord", help="Sett nytt passord for en bruker.")
    nytt.add_argument("epost", help="E-postadressen til brukeren.")
    return parser


def nytt_passord(
    epost: str,
    *,
    database_url: str,
    sesjonsfabrikk: sessionmaker[Session] | None = None,
    les_passord: Callable[[str], str] = getpass.getpass,
    spor: Callable[[str], str] = input,
) -> int:
    print(f"Database: {url_uten_passord(database_url)}")
    passord = les_passord("Nytt passord: ")
    if not passord.strip():
        print("Passordet kan ikke bare være mellomrom. Ingenting er endret.", file=sys.stderr)
        return 1
    if not passord_har_gyldig_lengde(passord):
        print(f"Passordet må ha {PASSORD_MIN}–{PASSORD_MAKS} tegn. Ingenting er endret.", file=sys.stderr)
        return 1
    if les_passord("Skriv passordet på nytt: ") != passord:
        print("Passordene er ikke like. Ingenting er endret.", file=sys.stderr)
        return 1
    if spor("Skriv ja for å bytte passordet i denne databasen: ").strip().lower() != "ja":
        print("Avbrutt. Ingenting er endret.")
        return 1

    motor = None
    if sesjonsfabrikk is None:
        motor = lag_motor(database_url)
        sesjonsfabrikk = lag_sesjonsfabrikk(motor)
    try:
        with sesjonsfabrikk() as db, db.begin():
            funnet = sett_nytt_passord(db, epost, passord)
    finally:
        if motor is not None:
            motor.dispose()
    if not funnet:
        print("Fant ingen aktiv bruker med den e-postadressen. Ingenting er endret.", file=sys.stderr)
        return 1
    print("Passordet er byttet. Brukerens gamle innlogginger er slettet.")
    return 0


def main(argv: Sequence[str] | None = None, **kwargs) -> int:
    args = _parser().parse_args(argv)
    if args.kommando == "nytt-passord":
        return nytt_passord(args.epost, database_url=hent_settings().database_url, **kwargs)
    return 2  # pragma: no cover – argparse krever en kjent kommando


if __name__ == "__main__":
    sys.exit(main())
