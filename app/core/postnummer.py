"""Postnumre: eneste tilgang til postnummerlista (AD-1, AD-10).

Kilden er `data/postnumre.tsv`, som er Brings postnummerregister konvertert til
UTF-8 med alle rader og kolonner uendret. Bare postnumre for gateadresser
godtas (Brings kategori G og B). Postboks (P) og service (S) utelates
(PRD §9.2). Postnummer lagres som tekst med fire sifre.

`uv run python -m app.core.postnummer` skriver `app/core/static/postnumre.json`
fra TSV-fila. Fila sjekkes inn, og en test sammenligner de to.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from sqlalchemy import Column, String, Table

from app.core.db import Base

ROT = Path(__file__).resolve().parents[2]
TSV_STI = ROT / "data" / "postnumre.tsv"
JSON_STI = Path(__file__).resolve().parent / "static" / "postnumre.json"

KATEGORIER_FOR_GATEADRESSE = frozenset({"G", "B"})
SMAORD = frozenset({"i", "på", "og", "ved"})

# Tabellen eies av core og skrives bare av migreringen (AD-1).
postnummer_tabell = Table(
    "postnummer",
    Base.metadata,
    Column("nummer", String(4), primary_key=True),
    Column("poststed", String(100), nullable=False),
)


def formater_poststed(navn: str) -> str:
    """Gjør Brings store bokstaver om til vanlig skrivemåte.

    Stor forbokstav i hvert ord og i hvert bindestrek-ledd. Småordene i, på, og
    og ved skrives med små bokstaver når de ikke står først: «MO I RANA» blir
    «Mo i Rana».
    """
    ord_ = navn.strip().lower().split()
    resultat: list[str] = []
    for indeks, ordet in enumerate(ord_):
        if indeks > 0 and ordet in SMAORD:
            resultat.append(ordet)
        else:
            resultat.append("-".join(ledd.capitalize() for ledd in ordet.split("-")))
    return " ".join(resultat)


def les_tsv(sti: Path = TSV_STI) -> list[tuple[str, str]]:
    """Postnumre for gateadresser som `(nummer, poststed)`, sortert på nummer.

    Brukes både av migreringen og av JSON-generatoren.
    """
    rader: list[tuple[str, str]] = []
    with sti.open(encoding="utf-8", newline="") as fil:
        for linje in fil:
            linje = linje.rstrip("\r\n")
            if not linje:
                continue
            nummer, poststed, _kommunenr, _kommune, kategori = linje.split("\t")
            if kategori in KATEGORIER_FOR_GATEADRESSE:
                rader.append((nummer, formater_poststed(poststed)))
    rader.sort()
    return rader


@lru_cache(maxsize=1)
def _register() -> dict[str, str]:
    return dict(les_tsv())


def normaliser_postnummer(verdi: str | None) -> str | None:
    """Fjerner mellomrom rundt. Gir fire sifre, eller `None` hvis formatet er feil."""
    if verdi is None:
        return None
    verdi = verdi.strip()
    if len(verdi) == 4 and verdi.isascii() and verdi.isdigit():
        return verdi
    return None


def finnes(verdi: str | None) -> bool:
    """Om postnummeret finnes og gjelder gateadresser."""
    nummer = normaliser_postnummer(verdi)
    return nummer is not None and nummer in _register()


def poststed(verdi: str | None) -> str | None:
    """Poststedet for et gyldig postnummer, ellers `None`."""
    nummer = normaliser_postnummer(verdi)
    if nummer is None:
        return None
    return _register().get(nummer)


def lag_json() -> str:
    """JSON-teksten for `postnumre.json`: `{nummer: poststed}`, sortert."""
    return json.dumps(dict(les_tsv()), ensure_ascii=False, sort_keys=True, indent=0) + "\n"


def skriv_json(sti: Path = JSON_STI) -> None:
    sti.parent.mkdir(parents=True, exist_ok=True)
    sti.write_text(lag_json(), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    skriv_json()
    print(f"Skrev {JSON_STI.relative_to(ROT).as_posix()} med {len(les_tsv())} postnumre.")
