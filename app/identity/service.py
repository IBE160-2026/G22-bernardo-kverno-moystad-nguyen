"""Regler for konto og innlogging, og implementasjonen av `Autentisering` (AD-4, AD-6, AD-16).

- Passord og e-post behandles bare her: `hash_passord`, `sjekk_passord` og
  `normaliser_epost` (AD-6, AR-16). Ingen annen kode kaller bcrypt.
- Registrering med alle feltfeil samlet i én `RegelBrudd` (FR-1, NFR-10).
- Innlogging med sperre etter 5 mislykkede forsøk per e-post på 15 minutter,
  og sesjoner som varer i høyst 7 dager (FR-2, AD-4, AR-14). Registrering og
  innlogging lager sesjonen med samme funksjon, `opprett_sesjon`.
- Maler får aldri ORM-objekter for `bruker`, bare `OffentligBruker` (AD-16, AR-24).

Funksjonene her committer aldri. Ruta eier transaksjonen (AD-17).
Navn, passord, e-post, telefon, fødselsdato og sesjonsnøkler logges aldri.
"""

from __future__ import annotations

import base64
import hashlib
import secrets
import unicodedata
from dataclasses import dataclass
from datetime import timedelta
from functools import lru_cache

import bcrypt
from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette.requests import Request

from app.core import klokke, tid
from app.core.config import hent_settings
from app.core.feil import RegelBrudd
from app.core.postnummer import finnes as postnummer_finnes
from app.core.postnummer import normaliser_postnummer, poststed
from app.core.sesjon import (  # noqa: F401 (FEIL_INNLOGGING og FOR_MANGE_FORSOK hentes herfra)
    FEIL_INNLOGGING,
    FOR_MANGE_FORSOK,
    SESJON_COOKIE,
    Innlogget,
    Innloggingsresultat,
    Innloggingsutfall,
)
from app.identity.models import Bruker, Innloggingsforsok, Sesjon

SESJON_VARIGHET = timedelta(days=7)
SPERREVINDU = timedelta(minutes=15)
MAKS_MISLYKKEDE = 5
PASSORD_MIN = 8
MAKS_EPOST = 320  # lengden på `bruker.epost` og `innloggingsforsok.epost`
PASSORD_MAKS = 64
BCRYPT_KOSTNAD = 12
BCRYPT_KOSTNAD_TEST = 4
SLETTET_BRUKER = "Slettet bruker"

# `FEIL_INNLOGGING` og `FOR_MANGE_FORSOK` ligger i `core/sesjon.py`, fordi 401-siden
# også viser dem (AD-7). De importeres hit, så de fortsatt kan hentes herfra.
SKRIV_EPOST = "Skriv e-postadressen din."
SKRIV_PASSORD = "Skriv passordet ditt."

# Feiltekstene ved registrering står ordrett i EXPERIENCE.md § Feiltekster ved felt (FR-1).
NAVN_MAKS = 80
TELEFON_SIFRE = 8
SKRIV_NAVN = "Skriv navnet ditt."
NAVN_FOR_LANGT = "Navnet kan ha høyst 80 tegn."
EPOST_FORMAT = "Skriv e-postadressen som navn@eksempel.no."
EPOST_I_BRUK = "Det finnes allerede en konto med denne e-posten."
SKRIV_NYTT_PASSORD = "Skriv et passord."
PASSORD_LENGDE = "Passordet må ha 8–64 tegn."
SKRIV_TELEFON = "Skriv telefonnummeret ditt."
TELEFON_FORMAT = "Skriv et telefonnummer med åtte siffer, for eksempel 912 34 567."
SKRIV_POSTNUMMER = "Skriv postnummeret."
POSTNUMMER_UKJENT = "Finner ikke postnummeret. Sjekk at det har fire siffer."
UNDER_18 = "Du må være minst 18 år for å bruke Nabolagshelten."


# ---------- e-post og passord (AD-6) ----------


def normaliser_epost(epost: str | None) -> str:
    """Trimmer, NFC-normaliserer og gjør om til små bokstaver. Brukes før lagring og oppslag."""
    if epost is None:
        return ""
    return unicodedata.normalize("NFC", epost.strip()).lower()


def _forbered_passord(passord: str) -> bytes:
    """base64(SHA-256(NFC(passord))). Ingen trim.

    bcrypt 5 avviser passord over 72 byte, og 64 tegn kan bli mer enn det i
    UTF-8. SHA-256 og base64 gir alltid 44 byte (AD-6).
    """
    nfc = unicodedata.normalize("NFC", passord)
    return base64.b64encode(hashlib.sha256(nfc.encode("utf-8")).digest())


def _kostnad() -> int:
    """12 vanligvis, 4 når `APP_ENV=test`, så testene går raskt (AR-29)."""
    return BCRYPT_KOSTNAD_TEST if hent_settings().test else BCRYPT_KOSTNAD


def hash_passord(passord: str) -> str:
    """bcrypt-hash av passordet (NFR-4). Selve passordet lagres aldri."""
    salt = bcrypt.gensalt(rounds=_kostnad())
    return bcrypt.hashpw(_forbered_passord(passord), salt).decode("ascii")


@lru_cache(maxsize=1)
def _dummy_hash() -> str:
    """Hash som ukjente e-poster sjekkes mot, så svartiden ikke avslører om kontoen finnes.

    Lages én gang med `hash_passord`, så den har samme kostnad som ekte hasher.
    """
    return hash_passord(secrets.token_urlsafe(16))


def sjekk_passord(passord: str, passord_hash: str | None) -> bool:
    """Om passordet stemmer med hashen. Uten hash sjekkes det mot dummy-hashen og gir `False`."""
    hash_ = passord_hash or _dummy_hash()
    try:
        stemmer = bcrypt.checkpw(_forbered_passord(passord), hash_.encode("ascii"))
    except ValueError:
        return False
    return stemmer and passord_hash is not None


def passord_har_gyldig_lengde(passord: str) -> bool:
    """8–64 tegn etter NFC, uten trim (FR-1)."""
    return PASSORD_MIN <= len(unicodedata.normalize("NFC", passord)) <= PASSORD_MAKS


def sjekk_innloggingsskjema(epost: str | None, passord: str | None) -> list[tuple[str, str]]:
    """Feltfeil for tomme felt i innloggingsskjemaet, i feltrekkefølge (FR-2, UX-DR12).

    Felt med bare mellomrom er tomme. Passordet trimmes ikke, men et passord
    med bare mellomrom regnes som tomt.
    """
    feil: list[tuple[str, str]] = []
    if not normaliser_epost(epost):
        feil.append(("epost", SKRIV_EPOST))
    if not passord or not passord.strip():
        feil.append(("passord", SKRIV_PASSORD))
    return feil


def hash_sesjonsnokkel(nokkel: str) -> str:
    """SHA-256 (hex) av sesjonsnøkkelen. Tabellen `sesjon` lagrer bare hashen."""
    return hashlib.sha256(nokkel.encode("utf-8")).hexdigest()


# ---------- innlogging (FR-2, AD-4) ----------


def _rydd_gamle_forsok(db: Session) -> None:
    """Sletter alle forsøk eldre enn 15 minutter, for alle e-poster (personvern)."""
    db.execute(delete(Innloggingsforsok).where(Innloggingsforsok.tidspunkt < klokke.na() - SPERREVINDU))


def antall_mislykkede(db: Session, epost: str) -> int:
    return db.scalar(
        select(func.count()).select_from(Innloggingsforsok).where(Innloggingsforsok.epost == epost)
    ) or 0


def _finn_aktiv_bruker(db: Session, epost: str) -> Bruker | None:
    return db.scalars(
        select(Bruker).where(Bruker.epost == epost, Bruker.slettet_tidspunkt.is_(None))
    ).first()


def opprett_sesjon(db: Session, bruker_id: int, gammel_nokkel: str | None = None) -> str:
    """Ny sesjon som varer i 7 dager, og gir nøkkelen til cookien (FR-1, FR-2, AD-4).

    Sletter først alle utløpte sesjoner og sesjonen med `gammel_nokkel`. Tabellen
    lagrer bare hashen av nøkkelen. Brukes av både innlogging og registrering.
    """
    na = klokke.na()
    db.execute(delete(Sesjon).where(Sesjon.utloper <= na))
    if gammel_nokkel:
        db.execute(delete(Sesjon).where(Sesjon.nokkel == hash_sesjonsnokkel(gammel_nokkel)))
    nokkel = secrets.token_urlsafe(32)
    db.add(
        Sesjon(
            nokkel=hash_sesjonsnokkel(nokkel),
            bruker_id=bruker_id,
            opprettet=na,
            utloper=na + SESJON_VARIGHET,
        )
    )
    db.flush()
    return nokkel


def logg_inn(
    db: Session, epost: str | None, passord: str | None, *, gammel_nokkel: str | None = None
) -> Innloggingsresultat:
    """Logger inn med e-post og passord (FR-2, AD-4).

    - Tomme felt, og e-post over 320 tegn eller med NUL, gir `FEIL` uten
      databasekall og telles ikke.
    - Ved hvert forsøk slettes alle forsøk eldre enn 15 minutter.
    - Har e-posten 5 eller flere forsøk igjen, avvises forsøket som `SPERRET`,
      uten passordsjekk og uten å lagres.
    - Ukjent e-post og feil passord gir samme utfall, og begge kjører bcrypt.
      Begge lagres som mislykket forsøk.
    - Vellykket innlogging sletter forsøkene for e-posten, alle utløpte sesjoner
      og den gamle sesjonen, og lager en ny sesjon som varer i 7 dager.
    """
    normalisert = normaliser_epost(epost)
    if not normalisert or not passord:
        return Innloggingsresultat(Innloggingsutfall.FEIL)
    if len(normalisert) > MAKS_EPOST or "\x00" in normalisert:
        # Ville gitt DataError i Postgres. Kan ikke være en lagret e-post.
        return Innloggingsresultat(Innloggingsutfall.FEIL)

    na = klokke.na()
    _rydd_gamle_forsok(db)
    if antall_mislykkede(db, normalisert) >= MAKS_MISLYKKEDE:
        return Innloggingsresultat(Innloggingsutfall.SPERRET)

    bruker = _finn_aktiv_bruker(db, normalisert)
    # bcrypt kjøres alltid, også for ukjent e-post, så svartiden blir omtrent lik.
    stemmer = sjekk_passord(passord, bruker.passord_hash if bruker else None)
    if bruker is None or not stemmer:
        db.add(Innloggingsforsok(epost=normalisert, tidspunkt=na))
        db.flush()
        return Innloggingsresultat(Innloggingsutfall.FEIL)

    db.execute(delete(Innloggingsforsok).where(Innloggingsforsok.epost == normalisert))
    nokkel = opprett_sesjon(db, bruker.id, gammel_nokkel=gammel_nokkel)
    return Innloggingsresultat(Innloggingsutfall.VELLYKKET, nokkel=nokkel)


# ---------- registrering (FR-1) ----------


def _tekst(verdi: str | None) -> str:
    """Trimmet og NFC-normalisert tekst. Felt med bare mellomrom blir tomme."""
    return unicodedata.normalize("NFC", verdi or "").strip()


def normaliser_navn(navn: str | None) -> str:
    """Trimmet og NFC-normalisert. Kontrolltegn (som NUL, som Postgres avviser) blir mellomrom."""
    uten_kontrolltegn = "".join(
        " " if unicodedata.category(tegn) == "Cc" else tegn for tegn in (navn or "")
    )
    return _tekst(uten_kontrolltegn)


def normaliser_telefon(telefon: str | None) -> str | None:
    """Åtte siffer, eller `None` hvis formatet er feil (FR-1).

    Mellomrom fjernes, så `+47` eller `0047` foran. Resten må være åtte ASCII-sifre.
    "912 34 567", "+47 912 34 567" og "0047 91234567" gir alle "91234567".
    """
    verdi = "".join(_tekst(telefon).split())
    for prefiks in ("+47", "0047"):
        if verdi.startswith(prefiks):
            verdi = verdi[len(prefiks):]
            break
    if len(verdi) == TELEFON_SIFRE and verdi.isascii() and verdi.isdigit():
        return verdi
    return None


def sjekk_epostformat(epost: str) -> bool:
    """Om en normalisert e-post har gyldig format (FR-1).

    Nøyaktig én `@`, tekst før, et domene med punktum (ikke først eller sist),
    ingen mellomrom eller kontrolltegn, og høyst 320 tegn.
    """
    if not epost or len(epost) > MAKS_EPOST:
        return False
    if any(tegn.isspace() or unicodedata.category(tegn).startswith("C") for tegn in epost):
        return False
    if epost.count("@") != 1:
        return False
    lokal, domene = epost.split("@")
    return bool(lokal) and "." in domene and not domene.startswith(".") and not domene.endswith(".")


def _epost_i_bruk(db: Session, epost: str) -> bool:
    return db.scalar(select(Bruker.id).where(Bruker.epost == epost).limit(1)) is not None


def registrer(
    db: Session,
    *,
    navn: str | None,
    epost: str | None,
    passord: str | None,
    telefon: str | None,
    postnummer: str | None,
    fodselsdato: str | None,
    gammel_nokkel: str | None = None,
) -> str:
    """Oppretter en konto og logger inn. Gir sesjonsnøkkelen til cookien (FR-1, AD-2, AD-6, AD-17).

    Alle feltfeil samles i én `RegelBrudd`, i feltrekkefølgen navn, e-post,
    passord, telefon, postnummer, fødselsdato (NFR-10). E-posten slås bare opp
    når formatet er gyldig. Unik-constrainten på `bruker.epost` fanger to
    samtidige registreringer: innsettingen kjører i `begin_nested()`, og
    `IntegrityError` blir samme feil som forhåndssjekken gir. Vellykket
    registrering sletter de mislykkede innloggingsforsøkene for e-posten, slik
    innloggingen gjør. Ved feil røres de ikke.
    """
    feil: list[tuple[str, str]] = []

    navn_ = normaliser_navn(navn)
    if not navn_:
        feil.append(("navn", SKRIV_NAVN))
    elif len(navn_) > NAVN_MAKS:
        feil.append(("navn", NAVN_FOR_LANGT))

    epost_ = normaliser_epost(epost)
    if not epost_:
        feil.append(("epost", SKRIV_EPOST))
    elif not sjekk_epostformat(epost_):
        feil.append(("epost", EPOST_FORMAT))
    elif _epost_i_bruk(db, epost_):
        feil.append(("epost", EPOST_I_BRUK))

    # Passordet trimmes ikke, men et passord med bare mellomrom er tomt.
    passord_ = passord or ""
    if not passord_.strip():
        feil.append(("passord", SKRIV_NYTT_PASSORD))
    elif not passord_har_gyldig_lengde(passord_):
        feil.append(("passord", PASSORD_LENGDE))

    telefon_ = normaliser_telefon(telefon)
    if not _tekst(telefon):
        feil.append(("telefon", SKRIV_TELEFON))
    elif telefon_ is None:
        feil.append(("telefon", TELEFON_FORMAT))

    postnummer_ = normaliser_postnummer(_tekst(postnummer))
    if not _tekst(postnummer):
        feil.append(("postnummer", SKRIV_POSTNUMMER))
    elif postnummer_ is None or not postnummer_finnes(postnummer_):
        feil.append(("postnummer", POSTNUMMER_UKJENT))

    i_dag = tid.i_dag()
    fodselsdato_ = None
    try:
        fodselsdato_ = tid.tolk_fodselsdato(fodselsdato, i_dag=i_dag)
    except RegelBrudd as brudd:
        feil.extend(brudd.feil)
    else:
        if not tid.er_myndig(fodselsdato_, i_dag):
            feil.append(("fodselsdato", UNDER_18))

    if feil:
        raise RegelBrudd(feil)

    bruker = Bruker(
        navn=navn_,
        epost=epost_,
        passord_hash=hash_passord(passord_),
        telefon=telefon_,
        postnummer=postnummer_,
        fodselsdato=fodselsdato_,
        opprettet=klokke.na(),
    )
    try:
        with db.begin_nested():
            db.add(bruker)
            db.flush()
    except IntegrityError:
        # En annen registrering med samme e-post kom først (AD-17).
        raise RegelBrudd([("epost", EPOST_I_BRUK)]) from None
    # Som ved vellykket innlogging: mislykkede forsøk med e-posten før
    # registreringen skal ikke telle med i sperren etterpå (FR-2, R2).
    db.execute(delete(Innloggingsforsok).where(Innloggingsforsok.epost == epost_))
    return opprett_sesjon(db, bruker.id, gammel_nokkel=gammel_nokkel)


def logg_ut(db: Session, nokkel: str | None) -> None:
    """Sletter sesjonsraden for nøkkelen fra cookien (FR-2)."""
    if nokkel:
        db.execute(delete(Sesjon).where(Sesjon.nokkel == hash_sesjonsnokkel(nokkel)))


def sett_nytt_passord(db: Session, epost: str, passord: str) -> bool:
    """Manuell tilbakestilling (AR-9, AD-6): nytt passord, og gamle sesjoner og forsøk slettes.

    Gir `False` når det ikke finnes en aktiv bruker med e-posten.
    """
    normalisert = normaliser_epost(epost)
    bruker = _finn_aktiv_bruker(db, normalisert) if normalisert else None
    if bruker is None:
        return False
    bruker.passord_hash = hash_passord(passord)
    db.execute(delete(Sesjon).where(Sesjon.bruker_id == bruker.id))
    db.execute(delete(Innloggingsforsok).where(Innloggingsforsok.epost == normalisert))
    db.flush()
    return True


class IdentityAutentisering:
    """`Autentisering` for appen. Sesjonene ligger i tabellen `sesjon` (AD-4).

    Tabellen lagrer `hash_sesjonsnokkel(nokkel)`, aldri selve nøkkelen fra cookien.
    """

    def __init__(self) -> None:
        # Dummy-hashen lages ved oppstart, så første forsøk med ukjent e-post
        # ikke koster to bcrypt-kjøringer og avslører seg på svartiden.
        _dummy_hash()

    def finn_innlogget(self, request: Request) -> Innlogget | None:
        nokkel = request.cookies.get(SESJON_COOKIE)
        if not nokkel:
            return None
        with request.app.state.sesjonsfabrikk() as db:
            rad = db.execute(
                select(Sesjon.bruker_id, Bruker.navn, Bruker.postnummer)
                .join(Bruker, Bruker.id == Sesjon.bruker_id)
                .where(
                    Sesjon.nokkel == hash_sesjonsnokkel(nokkel),
                    Sesjon.utloper > klokke.na(),
                    Bruker.slettet_tidspunkt.is_(None),
                )
            ).first()
        if rad is None:
            return None
        return Innlogget(
            bruker_id=rad.bruker_id, visningsnavn=rad.navn or "", postnummer=rad.postnummer
        )

    def logg_inn(
        self, db: Session, epost: str, passord: str, *, gammel_nokkel: str | None = None
    ) -> Innloggingsresultat:
        return logg_inn(db, epost, passord, gammel_nokkel=gammel_nokkel)

    def logg_ut(self, db: Session, nokkel: str | None) -> None:
        logg_ut(db, nokkel)

    def sjekk_innloggingsskjema(self, epost: str | None, passord: str | None) -> list[tuple[str, str]]:
        return sjekk_innloggingsskjema(epost, passord)


# ---------- personopplysninger i maler (AD-16, AR-24) ----------


@dataclass(frozen=True)
class OffentligBruker:
    """Det maler får vite om en annen bruker: aldri telefon, e-post eller fødselsdato."""

    id: int
    visningsnavn: str
    postnummer: str | None
    poststed: str | None
    slettet: bool

    @property
    def sted(self) -> str:
        """Postnummer med poststed, «0571 Oslo»."""
        return " ".join(del_ for del_ in (self.postnummer, self.poststed) if del_)


def visningsnavn(bruker: Bruker) -> str:
    """Navnet som vises, eller «Slettet bruker» (AD-8)."""
    if bruker.slettet_tidspunkt is not None:
        return SLETTET_BRUKER
    return bruker.navn or ""


def hent_offentlig_bruker(db: Session, bruker_id: int) -> OffentligBruker | None:
    """`OffentligBruker` for id-en, eller `None` hvis brukeren ikke finnes (FR-21)."""
    bruker = db.get(Bruker, bruker_id)
    if bruker is None:
        return None
    slettet = bruker.slettet_tidspunkt is not None
    return OffentligBruker(
        id=bruker.id,
        visningsnavn=visningsnavn(bruker),
        postnummer=None if slettet else bruker.postnummer,
        poststed=None if slettet else poststed(bruker.postnummer),
        slettet=slettet,
    )
