"""Regler for oppdrag (FR-5–FR-9, AD-2, AD-3, AD-16).

- `valider_oppdrag`: feltreglene for både utlegging og redigering. Alle
  feltfeil samles i én `RegelBrudd`, i feltrekkefølgen beskrivelse, tittel,
  kategori, postnummer, dato, klokkeslett, tilbud, beløp (NFR-10).
- `opprett_oppdrag`: innsettingen kjører i `begin_nested()`, og en `skjema_id`
  som finnes fra før, gir `Duplikat` til oppdraget som finnes (AD-2, NFR-5).
- `rediger_oppdrag` (FR-6, FR-8): bare oppdragsgiveren og bare ved `apen`. Én
  betinget `UPDATE` lagrer endringen, øker `versjon` og setter
  `vesentlig_endret` når tidspunkt, beløp eller postnummer faktisk endres
  (AD-2, AD-3). `hent_eget_oppdrag` og `skjemaverdier_for` gir skjemaet.
- `avbryt_oppdrag` (FR-7): `endre_status` fra `apen` eller `hjelper_valgt`.
- `endre_status`: eneste sted `oppdrag.status` endres (AD-2). Én betinget
  `UPDATE` som også øker `versjon`.
- `hent_for_visning`: det malene får vite om et oppdrag, etter tilgangsregelen
  i FR-9. Aldri telefon, e-post eller fødselsdato (AD-16).
- `utgatt`: eneste definisjon av «tidspunktet er passert» (FR-8, AD-3). Brukes
  av `endre_status`, `ledige_oppdrag` og `merker_lagt_ut`.
- `lagt_ut_av`: radene i «Mine oppdrag» med merkene fra `merker_lagt_ut`, og
  `antall_trenger_handling`: menykroken, som teller radene med minst ett merke
  (FR-8, FR-18, NFR-11, AD-3). Ingenting av dette lagres.
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

from sqlalchemy import ColumnElement, case, func, literal, not_, or_, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core import domene, klokke, tid
from app.core.db import UtcDateTime, laas_gir_konflikt
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


@dataclass(frozen=True)
class GyldigOppdrag:
    """Feltene etter `valider_oppdrag`: normalisert og klare til å lagres."""

    tittel: str
    beskrivelse: str
    kategori: str
    postnummer: str
    tidspunkt: datetime
    belop: int | None


def valider_oppdrag(
    *,
    beskrivelse: str | None,
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
) -> int:
    """Legger ut et oppdrag med status `apen` og gir id-en (FR-5, AD-2, AD-17).

    Feltene sjekkes av `valider_oppdrag` før innsettingen, så en ny innsending
    med feil viser feilene. Finnes `skjema_id` fra før, gir det `Duplikat` til
    det oppdraget.
    """
    na = klokke.na()
    gyldig = valider_oppdrag(
        beskrivelse=beskrivelse,
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
    """
    dato, klokkeslett = tid.skjemaverdier(oppdrag.tidspunkt)
    return {
        "beskrivelse": oppdrag.beskrivelse,
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
) -> None:
    """Lagrer endringene i et åpent oppdrag (FR-6, FR-8, NFR-5, AD-2, AD-3).

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
    """
    url = detaljer_url(oppdrag_id)
    na = klokke.na()
    with laas_gir_konflikt(KONFLIKT, url):
        try:
            ny = valider_oppdrag(
                beskrivelse=beskrivelse,
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
