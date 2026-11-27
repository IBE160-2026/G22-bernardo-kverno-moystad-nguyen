"""Regler for oppdrag (FR-5, FR-9, AD-2, AD-3, AD-16).

- `opprett_oppdrag`: alle feltfeil samles i én `RegelBrudd`, i feltrekkefølgen
  beskrivelse, tittel, kategori, postnummer, dato, klokkeslett, tilbud, beløp
  (NFR-10). Innsettingen kjører i `begin_nested()`, og en `skjema_id` som
  finnes fra før, gir `Duplikat` til oppdraget som finnes (AD-2, NFR-5).
- `endre_status`: eneste sted `oppdrag.status` endres (AD-2). Én betinget
  `UPDATE` som også øker `versjon`.
- `hent_for_visning`: det malene får vite om et oppdrag, etter tilgangsregelen
  i FR-9. Aldri telefon, e-post eller fødselsdato (AD-16).
- `utgatt`: eneste definisjon av «tidspunktet er passert» (FR-8, AD-3). Brukes
  av `endre_status`, `ledige_oppdrag` og merket i «Mine oppdrag» (2.4).
- `ledige_oppdrag`: kortene i oversikten (FR-10, FR-11). `erfaring`: fullførte
  oppdrag som hjelper, til oppdragsgiverblokken og profilen (FR-9, FR-21, AR-13).

Funksjonene her committer aldri. Ruta eier transaksjonen (AD-17).
"""

from __future__ import annotations

import secrets
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from sqlalchemy import ColumnElement, func, not_, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core import domene, klokke, tid
from app.core.feil import Duplikat, FinnesIkke, IngenTilgang, Konflikt, RegelBrudd
from app.core.postnummer import finnes as postnummer_finnes
from app.core.postnummer import normaliser_postnummer, poststed
from app.identity.service import POSTNUMMER_UKJENT, SKRIV_POSTNUMMER
from app.oppdrag.models import Oppdrag

# Feiltekstene står ordrett i EXPERIENCE.md § Feiltekster ved felt (FR-5).
SKRIV_BESKRIVELSE = "Skriv hva du trenger hjelp til."
BESKRIVELSE_FOR_KORT = "Skriv minst 10 tegn."
SKRIV_TITTEL = "Skriv en tittel."
TITTEL_FOR_KORT = "Tittelen må ha minst 3 tegn."
TITTEL_FOR_LANG = "Tittelen kan ha høyst 80 tegn."
VELG_KATEGORI = "Velg en kategori."
VELG_TILBUD = "Velg beløp eller uten betaling."
BELOP_FEIL = "Skriv et beløp fra 1 til 10 000 kr, i hele kroner."
KONFLIKT = "Oppdraget er endret. Last siden på nytt."

TILBUD = frozenset({"belop", "uten"})

# Lovlige statusoverganger (AD-2, PRD §4.0). Andre gir `ValueError`.
OVERGANGER: frozenset[tuple[str, str]] = frozenset(
    {
        ("apen", "hjelper_valgt"),
        ("apen", "avbrutt"),
        ("hjelper_valgt", "apen"),
        ("hjelper_valgt", "utfort"),
        ("hjelper_valgt", "avbrutt"),
    }
)


def beskrivelse_for_lang(antall: int) -> str:
    return f"Beskrivelsen kan ha høyst {domene.BESKRIVELSE_MAKS} tegn. Nå har den {antall}."


def detaljer_url(oppdrag_id: int) -> str:
    """Stien til detaljene, lik `app.url_path_for("oppdrag.detaljer", id=...)`."""
    return f"/oppdrag/{oppdrag_id}"


def utgatt(tidspunkt: Any, *, na: datetime | None = None) -> Any:
    """Om tidspunktet er passert: `tidspunkt <= na` (FR-8, AD-3).

    Eneste definisjon av «utgått». Med en `datetime` gir den `bool`, og med
    kolonnen `Oppdrag.tidspunkt` et SQL-uttrykk, så spørringene og merket i
    «Mine oppdrag» (2.4) bruker samme grense. Uten `na` brukes `klokke.na()`.
    """
    return tidspunkt <= (klokke.na() if na is None else na)


def ikke_utgatt(na: datetime | None = None) -> ColumnElement[bool]:
    """SQL-vilkåret for oppdrag der tidspunktet ikke er passert (`NOT utgatt`)."""
    return not_(utgatt(Oppdrag.tidspunkt, na=na))


def ny_skjema_id() -> str:
    """Engangsnøkkelen i skjemaet «Nytt oppdrag» (AD-2). 22 tegn fra `[A-Za-z0-9_-]`."""
    return secrets.token_urlsafe(16)


# ---------- status (AD-2) ----------


def endre_status(
    db: Session,
    oppdrag_id: int,
    *,
    fra: str | Iterable[str],
    til: str,
    oppdragsgiver_id: int | None = None,
    ikke_passert: bool = False,
) -> None:
    """Endrer status med én betinget `UPDATE` og øker `versjon` (AD-2).

    `WHERE` har `id`, `status IN fra`, eier når `oppdragsgiver_id` er gitt, og
    `NOT utgatt(tidspunkt)` når `ikke_passert` er sann. En overgang som ikke står i
    `OVERGANGER`, gir `ValueError`. Endres ingen rad, leses raden på nytt:
    finnes den ikke, eller har den en annen eier, gir det `FinnesIkke`. Ellers
    har noen endret den, og det gir `Konflikt`.
    """
    fra_ = (fra,) if isinstance(fra, str) else tuple(fra)
    if not fra_:
        raise ValueError("endre_status krever minst én fra-status.")
    for status in fra_:
        if (status, til) not in OVERGANGER:
            raise ValueError(f"Ulovlig statusovergang: {status} → {til}")

    vilkar = [Oppdrag.id == oppdrag_id, Oppdrag.status.in_(fra_)]
    if oppdragsgiver_id is not None:
        vilkar.append(Oppdrag.oppdragsgiver_id == oppdragsgiver_id)
    if ikke_passert:
        vilkar.append(ikke_utgatt())
    resultat = db.execute(
        update(Oppdrag)
        .where(*vilkar)
        .values(status=til, versjon=Oppdrag.versjon + 1)
        .execution_options(synchronize_session="fetch")
    )
    if resultat.rowcount == 1:
        return

    eier = db.scalar(select(Oppdrag.oppdragsgiver_id).where(Oppdrag.id == oppdrag_id))
    if eier is None or (oppdragsgiver_id is not None and eier != oppdragsgiver_id):
        raise FinnesIkke
    raise Konflikt(KONFLIKT, detaljer_url(oppdrag_id))


# ---------- legge ut (FR-5) ----------


def _sjekk_belop(tekst: str | None) -> int | None:
    """Hele kroner 1–10 000. Mellomrom (også NBSP) fjernes; resten må være ASCII-sifre.

    Mer enn fem sifre avvises før `int()`, som ellers gir `ValueError` ved over 4300 sifre.
    """
    verdi = "".join(domene.normaliser_tekst(tekst).split())
    if not verdi or len(verdi) > 5 or not (verdi.isascii() and verdi.isdigit()):
        return None
    belop = int(verdi)
    return belop if domene.BELOP_MIN <= belop <= domene.BELOP_MAKS else None


def opprett_oppdrag(
    db: Session,
    *,
    oppdragsgiver_id: int,
    beskrivelse: str | None,
    tittel: str | None,
    kategori: str | None,
    postnummer: str | None,
    dato: str | None,
    klokkeslett: str | None,
    tilbud: str | None,
    belop: str | None,
    skjema_id: str,
) -> int:
    """Legger ut et oppdrag med status `apen` og gir id-en (FR-5, AD-2, AD-17).

    Alle feltfeil samles i én `RegelBrudd`. Gruppene «Når?», kategori og «Hva
    tilbyr du?» har egne nøkler (`nar`, `kategori`, `tilbud`). Med «Uten
    betaling» ignoreres beløpet og lagres som NULL. Valideringen kjører før
    innsettingen, så en ny innsending med feil viser feilene. Finnes
    `skjema_id` fra før, gir det `Duplikat` til det oppdraget.
    """
    feil: list[tuple[str, str]] = []

    beskrivelse_ = domene.normaliser_tekst(beskrivelse)
    if not beskrivelse_:
        feil.append(("beskrivelse", SKRIV_BESKRIVELSE))
    elif len(beskrivelse_) < domene.BESKRIVELSE_MIN:
        feil.append(("beskrivelse", BESKRIVELSE_FOR_KORT))
    elif len(beskrivelse_) > domene.BESKRIVELSE_MAKS:
        feil.append(("beskrivelse", beskrivelse_for_lang(len(beskrivelse_))))

    tittel_ = domene.normaliser_tekst(tittel)
    if not tittel_:
        feil.append(("tittel", SKRIV_TITTEL))
    elif len(tittel_) < domene.TITTEL_MIN:
        feil.append(("tittel", TITTEL_FOR_KORT))
    elif len(tittel_) > domene.TITTEL_MAKS:
        feil.append(("tittel", TITTEL_FOR_LANG))

    if kategori not in domene.KATEGORIKODER:
        feil.append(("kategori", VELG_KATEGORI))

    postnummer_ = normaliser_postnummer(domene.normaliser_tekst(postnummer))
    if not domene.normaliser_tekst(postnummer):
        feil.append(("postnummer", SKRIV_POSTNUMMER))
    elif postnummer_ is None or not postnummer_finnes(postnummer_):
        feil.append(("postnummer", POSTNUMMER_UKJENT))

    na = klokke.na()
    tidspunkt: datetime | None = None
    try:
        tidspunkt = tid.tolk_tidspunkt(dato, klokkeslett, na=na)
    except RegelBrudd as brudd:
        feil.extend(brudd.feil)

    belop_: int | None = None
    if tilbud not in TILBUD:
        feil.append(("tilbud", VELG_TILBUD))
    elif tilbud == "belop":
        belop_ = _sjekk_belop(belop)
        if belop_ is None:
            feil.append(("belop", BELOP_FEIL))

    if feil:
        raise RegelBrudd(feil)

    oppdrag = Oppdrag(
        oppdragsgiver_id=oppdragsgiver_id,
        tittel=tittel_,
        beskrivelse=beskrivelse_,
        kategori=kategori,
        postnummer=postnummer_,
        tidspunkt=tidspunkt,
        belop=belop_,
        status="apen",
        versjon=1,
        skjema_id=skjema_id,
        opprettet=na,
    )
    try:
        with db.begin_nested():
            db.add(oppdrag)
            db.flush()
    except IntegrityError:
        # Samme skjema sendt to ganger (AD-2). Brukeren sendes til oppdraget som
        # finnes; tilgangsregelen avgjør hva hen får se.
        funnet = db.scalar(select(Oppdrag.id).where(Oppdrag.skjema_id == skjema_id))
        if funnet is None:
            raise
        raise Duplikat(detaljer_url(funnet)) from None
    return oppdrag.id


# ---------- vise (FR-9, AD-16) ----------


@dataclass(frozen=True)
class OppdragVisning:
    """Det malene får vite om et oppdrag. Ingen personfelt (AD-16)."""

    id: int
    tittel: str
    beskrivelse: str
    kategori: str
    postnummer: str
    poststed: str | None
    tidspunkt: datetime
    belop: int | None
    status: str
    oppdragsgiver_id: int
    er_eier: bool

    @property
    def sted(self) -> str:
        """Postnummer med poststed, «0571 Oslo»."""
        return " ".join(del_ for del_ in (self.postnummer, self.poststed) if del_)


@dataclass(frozen=True)
class OppdragRad:
    """En rad i «Mine oppdrag» før story 2.4: bare id og tittel."""

    id: int
    tittel: str


def hent_for_visning(db: Session, oppdrag_id: int, bruker_id: int) -> OppdragVisning:
    """Oppdraget slik brukeren får se det (FR-9).

    Åpne oppdrag kan ses av alle innloggede. Andre statuser kan bare ses av
    oppdragsgiveren og valgt hjelper. Finnes ikke gir `FinnesIkke`, ingen
    tilgang gir `IngenTilgang`. Begge vises som samme 404.
    """
    oppdrag = db.get(Oppdrag, oppdrag_id)
    if oppdrag is None:
        raise FinnesIkke
    if oppdrag.status != "apen" and bruker_id not in (
        oppdrag.oppdragsgiver_id,
        oppdrag.valgt_hjelper_id,
    ):
        raise IngenTilgang
    return OppdragVisning(
        id=oppdrag.id,
        tittel=oppdrag.tittel,
        beskrivelse=oppdrag.beskrivelse,
        kategori=oppdrag.kategori,
        postnummer=oppdrag.postnummer,
        poststed=poststed(oppdrag.postnummer),
        tidspunkt=oppdrag.tidspunkt,
        belop=oppdrag.belop,
        status=oppdrag.status,
        oppdragsgiver_id=oppdrag.oppdragsgiver_id,
        er_eier=oppdrag.oppdragsgiver_id == bruker_id,
    )


def lagt_ut_av(db: Session, bruker_id: int) -> list[OppdragRad]:
    """Oppdragene brukeren har lagt ut, nyeste først (grunnversjon til story 2.4)."""
    rader = db.execute(
        select(Oppdrag.id, Oppdrag.tittel)
        .where(Oppdrag.oppdragsgiver_id == bruker_id)
        .order_by(Oppdrag.opprettet.desc(), Oppdrag.id.desc())
    ).all()
    return [OppdragRad(id=rad.id, tittel=rad.tittel) for rad in rader]


# ---------- oversikten (FR-10, FR-11) ----------


@dataclass(frozen=True)
class OppdragKort:
    """Et kort i oversikten: det kortet viser, og id-en til lenken. Ingen personfelt (AD-16)."""

    id: int
    tittel: str
    kategori: str
    postnummer: str
    poststed: str | None
    tidspunkt: datetime
    belop: int | None

    @property
    def sted(self) -> str:
        """Postnummer med poststed, «0571 Oslo»."""
        return " ".join(del_ for del_ in (self.postnummer, self.poststed) if del_)


def ledige_oppdrag(
    db: Session, *, postnummer: str, kategori: str | None, bruker_id: int
) -> list[OppdragKort]:
    """Åpne oppdrag i postnummeret der tidspunktet ikke er passert (FR-8, FR-10, FR-11).

    Brukerens egne vises ikke. `kategori=None` gir alle kategorier. Sortert
    etter tidspunkt, så etter når oppdraget ble lagt ut, eldste først, og til
    sist etter id, så rekkefølgen alltid er fast.
    """
    vilkar = [
        Oppdrag.status == "apen",
        Oppdrag.postnummer == postnummer,
        Oppdrag.oppdragsgiver_id != bruker_id,
        ikke_utgatt(),
    ]
    if kategori is not None:
        vilkar.append(Oppdrag.kategori == kategori)
    rader = db.execute(
        select(
            Oppdrag.id,
            Oppdrag.tittel,
            Oppdrag.kategori,
            Oppdrag.postnummer,
            Oppdrag.tidspunkt,
            Oppdrag.belop,
        )
        .where(*vilkar)
        .order_by(Oppdrag.tidspunkt, Oppdrag.opprettet, Oppdrag.id)
    ).all()
    sted = poststed(postnummer)
    return [
        OppdragKort(
            id=rad.id,
            tittel=rad.tittel,
            kategori=rad.kategori,
            postnummer=rad.postnummer,
            poststed=sted,
            tidspunkt=rad.tidspunkt,
            belop=rad.belop,
        )
        for rad in rader
    ]


# ---------- erfaring (FR-9, FR-21, AR-13) ----------


def erfaring(db: Session, bruker_ids: Iterable[int]) -> dict[int, domene.Erfaring]:
    """`Erfaring` for hver id: utførte oppdrag der brukeren var valgt hjelper, per kategori.

    Alle id-ene får en verdi, også de uten fullførte oppdrag. Snittet er `None`
    og antallet vurderinger 0 til tilbakemeldingene kommer i Epic 4. Én spørring
    for alle id-ene, så interessertlista (Epic 3) ikke gir én spørring per person.
    """
    ider = sorted(set(bruker_ids))
    tall: dict[int, dict[str, int]] = {bruker_id: {} for bruker_id in ider}
    if ider:
        rader = db.execute(
            select(Oppdrag.valgt_hjelper_id, Oppdrag.kategori, func.count())
            .where(Oppdrag.status == "utfort", Oppdrag.valgt_hjelper_id.in_(ider))
            .group_by(Oppdrag.valgt_hjelper_id, Oppdrag.kategori)
        ).all()
        for hjelper_id, kategori, antall in rader:
            tall[hjelper_id][kategori] = antall
    return {
        bruker_id: domene.Erfaring(
            fullforte=sum(per.values()),
            per_kategori=tuple(
                (kode, per[kode]) for kode, _ in domene.KATEGORIER if per.get(kode)
            ),
            snitt=None,
            antall_vurderinger=0,
        )
        for bruker_id, per in tall.items()
    }
