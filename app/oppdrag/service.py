"""Regler for oppdrag (FR-5, FR-9, AD-2, AD-3, AD-16).

- `opprett_oppdrag`: alle feltfeil samles i én `RegelBrudd`, i feltrekkefølgen
  beskrivelse, tittel, kategori, postnummer, dato, klokkeslett, tilbud, beløp
  (NFR-10). Innsettingen kjører i `begin_nested()`, og en `skjema_id` som
  finnes fra før, gir `Duplikat` til oppdraget som finnes (AD-2, NFR-5).
- `endre_status`: eneste sted `oppdrag.status` endres (AD-2). Én betinget
  `UPDATE` som også øker `versjon`.
- `hent_for_visning`: det malene får vite om et oppdrag, etter tilgangsregelen
  i FR-9. Aldri telefon, e-post eller fødselsdato (AD-16).

Funksjonene her committer aldri. Ruta eier transaksjonen (AD-17).
"""

from __future__ import annotations

import secrets
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select, update
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
    `tidspunkt > nå` når `ikke_passert` er sann. En overgang som ikke står i
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
        vilkar.append(Oppdrag.tidspunkt > klokke.na())
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
