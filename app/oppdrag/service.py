"""Regler for oppdrag (FR-5–FR-9, AD-2, AD-3, AD-16).

- `valider_oppdrag`: feltreglene for både utlegging og redigering. Alle
  feltfeil samles i én `RegelBrudd`, i feltrekkefølgen beskrivelse, bilde,
  bildetekst, tittel, kategori, postnummer, dato, klokkeslett, tilbud, beløp
  (NFR-10).
- `tolk_bildevalg` (FR-27, AD-18): ny fil, beholdt bilde (`bilde_beholdt`),
  «Fjern bildet» og en fil som gikk tapt ved utløpt innlogging (AD-7) blir et
  `Bildevalg`. Ruta kaller den før transaksjonen, så et
  stort bilde ikke dekodes mens databasen er låst. Den kaster aldri; en ugyldig
  fil blir `feil`, som `valider_oppdrag` legger inn ved `bilde`.
- `opprett_oppdrag`: innsettingen kjører i `begin_nested()`, også bildet, og en
  `skjema_id` som finnes fra før, gir `Duplikat` til oppdraget som finnes
  (AD-2, NFR-5).
- `rediger_oppdrag` (FR-6, FR-8): bare oppdragsgiveren og bare ved `apen`. Én
  betinget `UPDATE` lagrer endringen, øker `versjon` og setter
  `vesentlig_endret` når tidspunkt, beløp eller postnummer faktisk endres
  (AD-2, AD-3). Etter den lagres, byttes eller slettes bildet, eller
  bildeteksten oppdateres. Bildet setter aldri `vesentlig_endret` (FR-27).
  `hent_eget_oppdrag` og `skjemaverdier_for` gir skjemaet.
- `slett_bilde` sletter bildet til et oppdrag (fjerning nå, sletting av oppdrag
  og konto i 4.5). `hent_bilde` gir én av JPEG-ene etter tilgangsregelen i FR-9.
- `avbryt_oppdrag` (FR-7): `endre_status` fra `apen` eller `hjelper_valgt`.
- `endre_status`: eneste sted `oppdrag.status` endres (AD-2). Én betinget
  `UPDATE` som også øker `versjon`.
- `hent_for_visning`: det malene får vite om et oppdrag, etter tilgangsregelen
  i FR-9, med `BildeInfo` når oppdraget har bilde. Aldri telefon, e-post eller
  fødselsdato (AD-16), og aldri binærdata.
- `utgatt`: eneste definisjon av «tidspunktet er passert» (FR-8, AD-3). Brukes
  av `endre_status`, `ledige_oppdrag` og `merker_lagt_ut`.
- `lagt_ut_av`: radene i «Mine oppdrag» med merkene fra `merker_lagt_ut`, og
  `antall_trenger_handling`: menykroken, som teller radene med minst ett merke
  (FR-8, FR-18, NFR-11, AD-3). Ingenting av dette lagres.
- `ledige_oppdrag`: kortene i oversikten (FR-10, FR-11), med `bildeversjon` når
  oppdraget har bilde, uten å lese binærkolonnene. `erfaring`: fullførte
  oppdrag som hjelper, til oppdragsgiverblokken og profilen (FR-9, FR-21, AR-13).

Funksjonene her committer aldri. Ruta eier transaksjonen (AD-17).
"""

from __future__ import annotations

import secrets
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from sqlalchemy import ColumnElement, case, delete, func, literal, not_, or_, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core import domene, klokke, tid
from app.core.db import UtcDateTime, laas_gir_konflikt
from app.core.feil import Duplikat, FinnesIkke, IngenTilgang, Konflikt, RegelBrudd
from app.core.postnummer import finnes as postnummer_finnes
from app.core.postnummer import normaliser_postnummer, poststed
from app.identity.service import POSTNUMMER_UKJENT, SKRIV_POSTNUMMER
from app.oppdrag import bilde as bildebehandling
from app.oppdrag.bilde import (
    BILDETEKST_FOR_KORT,
    BILDETEKST_FOR_LANG,
    SKRIV_BILDETEKST,
    Bilde,
)
from app.oppdrag.models import Oppdrag, Oppdragsbilde

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
# Ved bildet når en ny fil gikk tapt ved utløpt innlogging (AD-7, FR-27, EXPERIENCE.md § Feiltekster ved felt).
VELG_BILDET_PA_NYTT = "Velg bildet på nytt."
# Handlingsmerket på egne utgåtte oppdrag, ordrett fra FR-18 (EXPERIENCE.md § Merker).
TIDSPUNKTET_ER_PASSERT = "Tidspunktet er passert"

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


# ---------- bilde (FR-27, AD-18) ----------


@dataclass(frozen=True)
class Bildevalg:
    """Det brukeren valgte for bildet i én innsending (FR-27).

    `ny` er et gyldig bilde som skal lagres: en ny fil, eller det beholdte fra
    forrige innsending. `fjern` er «Fjern bildet». `feil` er feilteksten for en
    ugyldig fil (eller et ugyldig beholdt bilde), som vises ved `bilde`.
    """

    ny: Bilde | None = None
    fjern: bool = False
    feil: str | None = None


INGEN_BILDEVALG = Bildevalg()


def _beholdt(tekst: str | None) -> Bilde | None:
    try:
        return bildebehandling.fra_beholdt(tekst) if (tekst or "").strip() else None
    except RegelBrudd:
        return None


def tolk_bildevalg(
    fil: bytes | None, beholdt: str | None, fjern: str | None, *, tapt: bool = False
) -> Bildevalg:
    """Filfeltet, `bilde_beholdt` og `fjern_bilde` som ett `Bildevalg` (FR-27, AD-18). Kaster aldri.

    En ny fil går foran det beholdte bildet. Er den nye fila ugyldig, gir det
    `feil`, og et gyldig beholdt bilde står fortsatt i `ny`, så det vises igjen.
    Med «Fjern bildet» og uten ny fil brukes ikke det beholdte bildet. All
    behandling skjer i `oppdrag/bilde.py`.

    `tapt=True` betyr at en ny fil gikk tapt fordi innloggingen var utløpt (AD-7,
    story 2.6). Uten ny fil gir det feilen «Velg bildet på nytt.», så ingenting
    lagres, og et gyldig beholdt bilde vises fortsatt.
    """
    fjern_ = bool((fjern or "").strip())
    if fil:
        try:
            return Bildevalg(ny=bildebehandling.behandle(fil), fjern=fjern_)
        except RegelBrudd as brudd:
            return Bildevalg(
                ny=None if fjern_ else _beholdt(beholdt), fjern=fjern_, feil=brudd.feil[0][1]
            )
    if tapt:
        return Bildevalg(
            ny=None if fjern_ else _beholdt(beholdt), fjern=fjern_, feil=VELG_BILDET_PA_NYTT
        )
    if fjern_ or not (beholdt or "").strip():
        return Bildevalg(fjern=fjern_)
    try:
        return Bildevalg(ny=bildebehandling.fra_beholdt(beholdt or ""))
    except RegelBrudd as brudd:
        return Bildevalg(feil=brudd.feil[0][1])


def _sjekk_bildetekst(tekst: str | None, feil: list[tuple[str, str]]) -> str:
    bildetekst = domene.normaliser_tekst(tekst)
    if not bildetekst:
        feil.append(("bildetekst", SKRIV_BILDETEKST))
    elif len(bildetekst) < domene.BILDETEKST_MIN:
        feil.append(("bildetekst", BILDETEKST_FOR_KORT))
    elif len(bildetekst) > domene.BILDETEKST_MAKS:
        feil.append(("bildetekst", BILDETEKST_FOR_LANG))
    return bildetekst


def slett_bilde(db: Session, oppdrag_id: int) -> None:
    """Sletter bildet til et oppdrag, om det har ett (FR-27, AD-2, AD-18).

    Brukes når bildet fjernes ved redigering, og av slettingen av oppdrag og
    konto (4.5), før `oppdrag`-raden slettes. Committer ikke.
    """
    db.execute(delete(Oppdragsbilde).where(Oppdragsbilde.oppdrag_id == oppdrag_id))


def _lagre_bilde(db: Session, oppdrag_id: int, nytt: Bilde, bildetekst: str, na: datetime) -> None:
    """Setter inn eller bytter bildet til oppdraget."""
    verdier = {
        "bilde": nytt.bilde,
        "miniatyr": nytt.miniatyr,
        "bildetekst": bildetekst,
        "bredde": nytt.bredde,
        "hoyde": nytt.hoyde,
        "opprettet": na,
    }
    resultat = db.execute(
        update(Oppdragsbilde).where(Oppdragsbilde.oppdrag_id == oppdrag_id).values(**verdier)
    )
    if resultat.rowcount == 0:
        db.add(Oppdragsbilde(oppdrag_id=oppdrag_id, **verdier))
        db.flush()


def _har_bilde(db: Session, oppdrag_id: int) -> bool:
    return (
        db.scalar(select(Oppdragsbilde.oppdrag_id).where(Oppdragsbilde.oppdrag_id == oppdrag_id))
        is not None
    )


def hent_bilde(db: Session, oppdrag_id: int, bruker_id: int, *, liten: bool) -> bytes:
    """Den store JPEG-en, eller miniatyren med `liten=True` (FR-9, FR-27, AD-18).

    `hent_for_visning` først, så tilgangsregelen og 404 er de samme som for
    detaljene. Et oppdrag uten bilde gir også `FinnesIkke`. Bare denne
    funksjonen leser en binærkolonne, og bare én.
    """
    oppdrag = hent_for_visning(db, oppdrag_id, bruker_id)
    if oppdrag.bilde is None:
        raise FinnesIkke
    kolonne = Oppdragsbilde.miniatyr if liten else Oppdragsbilde.bilde
    data = db.scalar(select(kolonne).where(Oppdragsbilde.oppdrag_id == oppdrag_id))
    if data is None:
        raise FinnesIkke
    return data


# ---------- valider (FR-5, FR-6, FR-27) ----------


@dataclass(frozen=True)
class GyldigOppdrag:
    """Feltene etter `valider_oppdrag`: normalisert og klare til å lagres.

    `bildetekst` er `None` når oppdraget ikke får eller har et bilde.
    """

    tittel: str
    beskrivelse: str
    kategori: str
    postnummer: str
    tidspunkt: datetime
    belop: int | None
    bildetekst: str | None = None


def valider_oppdrag(
    *,
    beskrivelse: str | None,
    bildevalg: Bildevalg = INGEN_BILDEVALG,
    bildetekst: str | None = None,
    har_lagret_bilde: bool = False,
    tittel: str | None,
    kategori: str | None,
    postnummer: str | None,
    dato: str | None,
    klokkeslett: str | None,
    tilbud: str | None,
    belop: str | None,
    na: datetime | None = None,
) -> GyldigOppdrag:
    """Feltreglene for et oppdrag, felles for utlegging og redigering (FR-5, FR-6, NFR-10).

    Alle feltfeil samles i én `RegelBrudd`. Gruppene «Når?», kategori og «Hva
    tilbyr du?» har egne nøkler (`nar`, `kategori`, `tilbud`). Med «Uten
    betaling» ignoreres beløpet og blir `None`. Tidspunktet må være fram i tid
    regnet fra `na` (uten `na`: `klokke.na()`), så et passert tidspunkt gir
    «Velg et nytt tidspunkt fram i tid» også ved redigering.

    Bildet (FR-27): `bildevalg.feil` står ved `bilde`, rett etter beskrivelsen.
    «Hva viser bildet?» sjekkes bare når det finnes et gyldig bilde: nytt,
    beholdt, eller lagret (`har_lagret_bilde`) uten «Fjern bildet». Ellers
    ignoreres teksten.
    """
    feil: list[tuple[str, str]] = []

    beskrivelse_ = domene.normaliser_tekst(beskrivelse)
    if not beskrivelse_:
        feil.append(("beskrivelse", SKRIV_BESKRIVELSE))
    elif len(beskrivelse_) < domene.BESKRIVELSE_MIN:
        feil.append(("beskrivelse", BESKRIVELSE_FOR_KORT))
    elif len(beskrivelse_) > domene.BESKRIVELSE_MAKS:
        feil.append(("beskrivelse", beskrivelse_for_lang(len(beskrivelse_))))

    if bildevalg.feil:
        feil.append(("bilde", bildevalg.feil))
    bildetekst_: str | None = None
    if bildevalg.ny is not None or (har_lagret_bilde and not bildevalg.fjern):
        bildetekst_ = _sjekk_bildetekst(bildetekst, feil)

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

    tidspunkt: datetime | None = None
    try:
        tidspunkt = tid.tolk_tidspunkt(dato, klokkeslett, na=klokke.na() if na is None else na)
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
    assert tidspunkt is not None and postnummer_ is not None and kategori is not None
    return GyldigOppdrag(
        tittel=tittel_,
        beskrivelse=beskrivelse_,
        kategori=kategori,
        postnummer=postnummer_,
        tidspunkt=tidspunkt,
        belop=belop_,
        bildetekst=bildetekst_,
    )


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
    bildetekst: str | None = None,
    bildevalg: Bildevalg = INGEN_BILDEVALG,
) -> int:
    """Legger ut et oppdrag med status `apen` og gir id-en (FR-5, FR-27, AD-2, AD-17).

    Feltene sjekkes av `valider_oppdrag` før innsettingen, så en ny innsending
    med feil viser feilene. Finnes `skjema_id` fra før, gir det `Duplikat` til
    det oppdraget. Bildet settes inn i samme `begin_nested()`, så en dobbel
    innsending gir én rad i `oppdrag` og én i `oppdragsbilde`.
    """
    na = klokke.na()
    gyldig = valider_oppdrag(
        beskrivelse=beskrivelse,
        bildevalg=bildevalg,
        bildetekst=bildetekst,
        tittel=tittel,
        kategori=kategori,
        postnummer=postnummer,
        dato=dato,
        klokkeslett=klokkeslett,
        tilbud=tilbud,
        belop=belop,
        na=na,
    )
    oppdrag = Oppdrag(
        oppdragsgiver_id=oppdragsgiver_id,
        tittel=gyldig.tittel,
        beskrivelse=gyldig.beskrivelse,
        kategori=gyldig.kategori,
        postnummer=gyldig.postnummer,
        tidspunkt=gyldig.tidspunkt,
        belop=gyldig.belop,
        status="apen",
        versjon=1,
        skjema_id=skjema_id,
        opprettet=na,
    )
    try:
        with db.begin_nested():
            db.add(oppdrag)
            db.flush()
            if bildevalg.ny is not None and gyldig.bildetekst is not None:
                _lagre_bilde(db, oppdrag.id, bildevalg.ny, gyldig.bildetekst, na)
    except IntegrityError:
        # Samme skjema sendt to ganger (AD-2). Brukeren sendes til oppdraget som
        # finnes; tilgangsregelen avgjør hva hen får se.
        funnet = db.scalar(select(Oppdrag.id).where(Oppdrag.skjema_id == skjema_id))
        if funnet is None:
            raise
        raise Duplikat(detaljer_url(funnet)) from None
    return oppdrag.id


# ---------- vise (FR-9, AD-16) ----------


def bildeversjon(versjon: int, opprettet: datetime) -> str:
    """`?v=` i URL-en til bildet: `oppdrag.versjon` og når bildet ble lagret (AD-18).

    `versjon` endres ved hver redigering. Tidspunktet skiller bilder på et oppdrag
    med samme id og versjon, for eksempel når SQLite gjenbruker en id etter ny seed,
    så nettleseren aldri viser et bilde fra bufferen (`immutable`) som hører til et
    slettet oppdrag.
    """
    return f"{versjon}-{int(opprettet.timestamp())}"


@dataclass(frozen=True)
class BildeInfo:
    """Det malene får vite om bildet til et oppdrag, uten binærdata (FR-27, AD-16).

    `versjon` er `bildeversjon(...)` og blir `?v=` i URL-en, så et nytt bilde får ny URL.
    """

    bildetekst: str
    bredde: int
    hoyde: int
    versjon: str


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
    bilde: BildeInfo | None = None

    @property
    def sted(self) -> str:
        """Postnummer med poststed, «0571 Oslo»."""
        return " ".join(del_ for del_ in (self.postnummer, self.poststed) if del_)


@dataclass(frozen=True)
class OppdragRad:
    """En rad i «Oppdrag jeg har lagt ut» (FR-18). Ingen personfelt (AD-16).

    `merker` er handlingsmerkene fra `merker_lagt_ut`, i visningsrekkefølge.
    """

    id: int
    tittel: str
    status: str
    tidspunkt: datetime
    merker: tuple[str, ...]


def hent_for_visning(db: Session, oppdrag_id: int, bruker_id: int) -> OppdragVisning:
    """Oppdraget slik brukeren får se det (FR-9).

    Åpne oppdrag kan ses av alle innloggede. Andre statuser kan bare ses av
    oppdragsgiveren og valgt hjelper. Finnes ikke gir `FinnesIkke`, ingen
    tilgang gir `IngenTilgang`. Begge vises som samme 404. Bildet hentes med
    `outerjoin`, uten binærkolonnene (FR-27).
    """
    rad = db.execute(
        select(
            Oppdrag,
            Oppdragsbilde.oppdrag_id.label("bilde_id"),
            Oppdragsbilde.bildetekst,
            Oppdragsbilde.bredde,
            Oppdragsbilde.hoyde,
            Oppdragsbilde.opprettet.label("bilde_opprettet"),
        )
        .outerjoin(Oppdragsbilde, Oppdragsbilde.oppdrag_id == Oppdrag.id)
        .where(Oppdrag.id == oppdrag_id)
    ).first()
    if rad is None:
        raise FinnesIkke
    oppdrag = rad.Oppdrag
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
        bilde=None
        if rad.bilde_id is None
        else BildeInfo(
            bildetekst=rad.bildetekst,
            bredde=rad.bredde,
            hoyde=rad.hoyde,
            versjon=bildeversjon(oppdrag.versjon, rad.bilde_opprettet),
        ),
    )


# ---------- redigere og avbryte (FR-6, FR-7, FR-8, AD-2, AD-3) ----------

REDIGERBAR = frozenset({"apen"})  # FR-6: bare mens oppdraget er Åpent
AVBRYTBAR = frozenset({"apen", "hjelper_valgt"})  # FR-7, OVERGANGER


def hent_eget_oppdrag(
    db: Session, oppdrag_id: int, bruker_id: int, *, statuser: Iterable[str]
) -> OppdragVisning:
    """Brukerens eget oppdrag til redigering eller avbrudd (FR-6, FR-7).

    Finnes ikke, ingen tilgang eller en annen eier gir `FinnesIkke`, altså samme
    404 som for et oppdrag som ikke finnes. En status som ikke står i `statuser`,
    gir `Konflikt` til detaljene, som viser gjeldende status (§4.0).
    """
    try:
        oppdrag = hent_for_visning(db, oppdrag_id, bruker_id)
    except IngenTilgang:
        raise FinnesIkke from None
    if not oppdrag.er_eier:
        raise FinnesIkke
    if oppdrag.status not in frozenset(statuser):
        raise Konflikt(KONFLIKT, detaljer_url(oppdrag_id))
    return oppdrag


def skjemaverdier_for(oppdrag: OppdragVisning) -> dict[str, str]:
    """De lagrede verdiene som feltene i redigeringsskjemaet (FR-6, AD-9).

    Tidspunktet blir «25.11.2026» og «09:00» i norsk tid, også når det er passert
    (FR-8). «Uten betaling» (`belop` er `None`) gir `tilbud="uten"` og tomt beløp.
    `bildetekst` er teksten til det lagrede bildet, eller tom (FR-27).
    """
    dato, klokkeslett = tid.skjemaverdier(oppdrag.tidspunkt)
    return {
        "beskrivelse": oppdrag.beskrivelse,
        "bildetekst": oppdrag.bilde.bildetekst if oppdrag.bilde else "",
        "tittel": oppdrag.tittel,
        "kategori": oppdrag.kategori,
        "postnummer": oppdrag.postnummer,
        "dato": dato,
        "klokkeslett": klokkeslett,
        "tilbud": "uten" if oppdrag.belop is None else "belop",
        "belop": "" if oppdrag.belop is None else str(oppdrag.belop),
    }


def rediger_oppdrag(
    db: Session,
    oppdrag_id: int,
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
    bildetekst: str | None = None,
    bildevalg: Bildevalg = INGEN_BILDEVALG,
) -> None:
    """Lagrer endringene i et åpent oppdrag (FR-6, FR-8, FR-27, NFR-5, AD-2, AD-3).

    Feltene sjekkes først med `valider_oppdrag`, så tekstene og rekkefølgen er de
    samme som ved utlegging. Ved feil sjekkes tilgangen før `RegelBrudd`, så 404
    (`FinnesIkke`) og `Konflikt` går foran 422.

    Så kommer én betinget `UPDATE`, første skriving i transaksjonen: `WHERE` har
    id, status `apen` og eier, men ikke `tidspunkt > nå`, fordi et utgått oppdrag
    skal kunne endres (FR-8). Den lagrer feltene, øker `versjon` og setter
    `vesentlig_endret` til `klokke.na()` bare når tidspunkt, beløp eller
    postnummer faktisk endres (AD-3). `IS DISTINCT FROM` gir riktig svar også
    for `NULL` («Uten betaling»). Endres ingen rad, gir det `FinnesIkke` (finnes
    ikke eller annen eier) eller `Konflikt` (status er endret), og ingenting
    lagres. «database is locked» i SQLite gir også `Konflikt`.

    Bildet skrives etter `UPDATE`-en (AD-2): et nytt bilde lagres eller bytter
    det gamle, «Fjern bildet» sletter det, og ellers oppdateres bildeteksten på
    et lagret bilde. Ingenting av dette rører `vesentlig_endret` (FR-27), men
    `versjon` øker alltid, så bildet får ny URL (`?v=`).
    """
    url = detaljer_url(oppdrag_id)
    na = klokke.na()
    with laas_gir_konflikt(KONFLIKT, url):
        har_lagret_bilde = _har_bilde(db, oppdrag_id)
        try:
            ny = valider_oppdrag(
                beskrivelse=beskrivelse,
                bildevalg=bildevalg,
                bildetekst=bildetekst,
                har_lagret_bilde=har_lagret_bilde,
                tittel=tittel,
                kategori=kategori,
                postnummer=postnummer,
                dato=dato,
                klokkeslett=klokkeslett,
                tilbud=tilbud,
                belop=belop,
                na=na,
            )
        except RegelBrudd:
            hent_eget_oppdrag(db, oppdrag_id, oppdragsgiver_id, statuser=REDIGERBAR)
            raise

        vesentlig = or_(
            Oppdrag.tidspunkt != ny.tidspunkt,
            Oppdrag.belop.is_distinct_from(ny.belop),
            Oppdrag.postnummer != ny.postnummer,
        )
        resultat = db.execute(
            update(Oppdrag)
            .where(
                Oppdrag.id == oppdrag_id,
                Oppdrag.status.in_(REDIGERBAR),
                Oppdrag.oppdragsgiver_id == oppdragsgiver_id,
            )
            .values(
                tittel=ny.tittel,
                beskrivelse=ny.beskrivelse,
                kategori=ny.kategori,
                postnummer=ny.postnummer,
                tidspunkt=ny.tidspunkt,
                belop=ny.belop,
                versjon=Oppdrag.versjon + 1,
                vesentlig_endret=case(
                    (vesentlig, literal(na, UtcDateTime())), else_=Oppdrag.vesentlig_endret
                ),
            )
            .execution_options(synchronize_session="fetch")
        )
        if resultat.rowcount == 1:
            if bildevalg.ny is not None and ny.bildetekst is not None:
                _lagre_bilde(db, oppdrag_id, bildevalg.ny, ny.bildetekst, na)
            elif bildevalg.fjern:
                slett_bilde(db, oppdrag_id)
            elif har_lagret_bilde and ny.bildetekst is not None:
                db.execute(
                    update(Oppdragsbilde)
                    .where(Oppdragsbilde.oppdrag_id == oppdrag_id)
                    .values(bildetekst=ny.bildetekst)
                )
            return
        eier = db.scalar(select(Oppdrag.oppdragsgiver_id).where(Oppdrag.id == oppdrag_id))
    if eier is None or eier != oppdragsgiver_id:
        raise FinnesIkke
    raise Konflikt(KONFLIKT, url)


def avbryt_oppdrag(db: Session, oppdrag_id: int, *, oppdragsgiver_id: int) -> None:
    """Avbryter et oppdrag fra `apen` eller `hjelper_valgt` (FR-7, AD-2).

    Går gjennom `endre_status`, så en annen eier gir `FinnesIkke` og en annen
    status (`utfort`, `avbrutt`) gir `Konflikt`. `valgt_hjelper_id` beholdes.
    Ingen `ikke_passert`: et utgått oppdrag kan også avbrytes (FR-8).
    «database is locked» i SQLite gir `Konflikt`.
    """
    with laas_gir_konflikt(KONFLIKT, detaljer_url(oppdrag_id)):
        endre_status(
            db,
            oppdrag_id,
            fra=tuple(sorted(AVBRYTBAR)),
            til="avbrutt",
            oppdragsgiver_id=oppdragsgiver_id,
        )


# ---------- «Mine oppdrag» (FR-8, FR-18, NFR-11, AD-3) ----------


def merker_lagt_ut(status: str, tidspunkt: datetime, *, na: datetime) -> tuple[str, ...]:
    """Handlingsmerkene på et eget oppdrag, beregnet ved lesing (FR-8, FR-18, AD-3).

    Foreløpig bare «Tidspunktet er passert»: status `apen` og `utgatt(tidspunkt)`.
    Story 3.5 legger de andre merkene til her, så lista og tallet i menyen alltid
    bruker samme definisjon.
    """
    if status == "apen" and utgatt(tidspunkt, na=na):
        return (TIDSPUNKTET_ER_PASSERT,)
    return ()


def lagt_ut_av(db: Session, bruker_id: int) -> list[OppdragRad]:
    """Oppdragene brukeren har lagt ut, med merker (FR-18, AD-3).

    Sortert etter tidspunkt, tidligste først, så etter når oppdraget ble lagt ut,
    eldste først, og til sist etter id, så rekkefølgen alltid er fast (som FR-10).
    `klokke.na()` leses én gang, så alle radene bruker samme grense.
    """
    na = klokke.na()
    rader = db.execute(
        select(Oppdrag.id, Oppdrag.tittel, Oppdrag.status, Oppdrag.tidspunkt)
        .where(Oppdrag.oppdragsgiver_id == bruker_id)
        .order_by(Oppdrag.tidspunkt, Oppdrag.opprettet, Oppdrag.id)
    ).all()
    return [
        OppdragRad(
            id=rad.id,
            tittel=rad.tittel,
            status=rad.status,
            tidspunkt=rad.tidspunkt,
            merker=merker_lagt_ut(rad.status, rad.tidspunkt, na=na),
        )
        for rad in rader
    ]


def antall_trenger_handling(db: Session, bruker_id: int) -> int:
    """Menykroken `(db, bruker_id) -> int`: antall egne oppdrag med minst ett merke (NFR-11, AD-3).

    Regnes fra `lagt_ut_av`, ikke med en egen `COUNT`, så lista og tallet aldri
    kan vise forskjellig. Et oppdrag med flere merker telles én gang.
    """
    return sum(1 for rad in lagt_ut_av(db, bruker_id) if rad.merker)


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
    # `bildeversjon(...)` når oppdraget har bilde (`?v=` i URL-en til miniatyren), ellers None.
    bildeversjon: str | None = None

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
    sist etter id, så rekkefølgen alltid er fast. Bildet finnes med `outerjoin`
    på `oppdragsbilde`, uten binærkolonnene (FR-27).
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
            Oppdrag.versjon,
            Oppdragsbilde.oppdrag_id.label("bilde_id"),
            Oppdragsbilde.opprettet.label("bilde_opprettet"),
        )
        .outerjoin(Oppdragsbilde, Oppdragsbilde.oppdrag_id == Oppdrag.id)
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
            bildeversjon=None if rad.bilde_id is None else bildeversjon(rad.versjon, rad.bilde_opprettet),
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
