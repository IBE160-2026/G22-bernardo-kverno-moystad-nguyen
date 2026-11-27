"""Grensesnittet for innlogging, merking av offentlige ruter og sesjonscookien (AD-1, AD-4).

`core` leser og skriver aldri `sesjon`, `bruker` eller `innloggingsforsok`. Den
kaller bare `Autentisering`, som `identity` implementerer og `lag_app()` kobler
inn. Mellomvaren og innloggingsruta når den gjennom `hent_autentisering`.
Ruter får den innloggede brukeren bare gjennom avhengigheten `innlogget_bruker`.

`prov_innlogging` er den ene innloggingen med e-post og passord. Både `/logg-inn`
og 401-siden i mellomvaren (AD-7) bruker den, så tekstene, sperren og
oppryddingen er like (FR-2, T-6).
"""

from __future__ import annotations

import unicodedata
from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Any, NamedTuple, Protocol, TypeVar, runtime_checkable
from urllib.parse import unquote

from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import Response

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

SESJON_COOKIE = "sesjon"
SESJON_SEKUNDER = 7 * 24 * 60 * 60  # 7 dager, like lenge som raden i `sesjon` (FR-2)
MAKS_NESTE = 2048
UTELATT_NESTE = frozenset({"/logg-inn", "/logg-ut"})
# Feltene på 401-siden (AD-7). Ingen andre skjema har feltnavn som begynner med `_`.
INNLOGGING_PREFIKS = "_innlogging_"

# Tekstene står ordrett i EXPERIENCE.md (FR-2). De ligger her fordi både `/logg-inn`
# og 401-siden i `core` viser dem gjennom `prov_innlogging`.
FEIL_INNLOGGING = "Feil e-post eller passord."
FOR_MANGE_FORSOK = "For mange mislykkede forsøk. Prøv igjen om 15 minutter."

F = TypeVar("F", bound=Callable[..., Any])


@dataclass(frozen=True)
class Innlogget:
    """Den innloggede brukeren, hentet med én spørring per forespørsel (AD-4).

    `postnummer` er med, så oversikten og «Nytt oppdrag» ikke slår opp brukeren
    på nytt (retro R7).
    """

    bruker_id: int
    visningsnavn: str
    postnummer: str | None


class Innloggingsutfall(Enum):
    VELLYKKET = "vellykket"
    FEIL = "feil"  # feil e-post eller passord: samme utfall i begge tilfeller (FR-2)
    SPERRET = "sperret"  # for mange mislykkede forsøk (FR-2, AD-4)


@dataclass(frozen=True)
class Innloggingsresultat:
    utfall: Innloggingsutfall
    nokkel: str | None = None  # sesjonsnøkkelen til cookien, bare ved vellykket innlogging

    @property
    def vellykket(self) -> bool:
        return self.utfall is Innloggingsutfall.VELLYKKET and self.nokkel is not None


@runtime_checkable
class Autentisering(Protocol):
    def finn_innlogget(self, request: Request) -> Innlogget | None:
        """Den innloggede brukeren for forespørselen, eller `None`.

        Leser cookien `sesjon` og slår opp gjennom `request.app.state.sesjonsfabrikk`.
        """
        ...

    def logg_inn(
        self, db: Session, epost: str, passord: str, *, gammel_nokkel: str | None = None
    ) -> Innloggingsresultat:
        """Prøver å logge inn. Committer aldri; ruta eier transaksjonen (AD-17).

        `gammel_nokkel` er sesjonen forespørselen allerede har, som slettes ved
        vellykket innlogging før den nye lages.
        """
        ...

    def logg_ut(self, db: Session, nokkel: str | None) -> None:
        """Sletter sesjonen med denne nøkkelen. Committer aldri (AD-17)."""
        ...

    def sjekk_innloggingsskjema(self, epost: str | None, passord: str | None) -> list[tuple[str, str]]:
        """Feltfeil for tomme felt i innloggingsskjemaet, i feltrekkefølge (FR-2).

        Nøklene er `epost` og `passord`. Ingen databasekall.
        """
        ...


class Innloggingsprov(NamedTuple):
    """Utfallet av `prov_innlogging`: nøkkelen ved vellykket innlogging, ellers feilene."""

    nokkel: str | None
    feil: list[tuple[str, str]]

    @property
    def feltfeil(self) -> dict[str, str]:
        """Feilene som står ved feltene (tomme felt).

        «Feil e-post eller passord.» og sperren står bare i feiloppsummeringen, og
        passordet får da hjelpeteksten «Skriv passordet på nytt.» (FR-2).
        """
        return {
            felt: melding
            for felt, melding in self.feil
            if melding not in (FEIL_INNLOGGING, FOR_MANGE_FORSOK)
        }


def prov_innlogging(
    autentisering: Autentisering,
    db: Session,
    epost: str | None,
    passord: str | None,
    *,
    gammel_nokkel: str | None = None,
) -> Innloggingsprov:
    """Den ene innloggingen med e-post og passord (FR-2, AD-4, T-6).

    Sjekker tomme felt uten databasekall, logger så inn i `with db.begin():` og
    velger meldingen. Brukes av `/logg-inn` og av 401-siden i mellomvaren (AD-7),
    så tekstene, sperren og oppryddingen er de samme. Sjekker passordet og bruker databasen,
    så asynkron kode kjører den i `run_in_threadpool`.
    """
    feil = autentisering.sjekk_innloggingsskjema(epost, passord)
    if feil:
        return Innloggingsprov(None, feil)
    with db.begin():
        resultat = autentisering.logg_inn(db, epost or "", passord or "", gammel_nokkel=gammel_nokkel)
    if resultat.vellykket:
        return Innloggingsprov(resultat.nokkel, [])
    melding = FOR_MANGE_FORSOK if resultat.utfall is Innloggingsutfall.SPERRET else FEIL_INNLOGGING
    return Innloggingsprov(None, [("epost", melding)])


def hent_autentisering(request: Request) -> Autentisering:
    """`Autentisering` som `lag_app()` koblet inn."""
    return request.app.state.autentisering


def innlogget_bruker(request: Request) -> Innlogget:
    """Avhengighet for ruter som krever innlogging (AD-4).

    Mellomvaren slipper aldri en forespørsel uten innlogging fram til en rute
    som ikke er offentlig. Skjer det likevel, svarer vi 401 i stedet for å
    fortsette uten bruker.
    """
    innlogget = getattr(request.state, "innlogget", None)
    if innlogget is None:
        raise HTTPException(status_code=401)
    return innlogget


def offentlig(endepunkt: F) -> F:
    """Merker en rute som offentlig, altså tilgjengelig uten innlogging (AD-4).

    Brukes under rute-dekoratoren:

        @router.get("/logg-inn", name="identity.logg_inn")
        @offentlig
        def vis_logg_inn(...): ...
    """
    endepunkt.er_offentlig = True  # type: ignore[attr-defined]
    return endepunkt


def er_offentlig(endepunkt: Callable[..., Any] | None) -> bool:
    return bool(getattr(endepunkt, "er_offentlig", False))


def alle_ruter(ruter: Iterable[Any]) -> Iterator[Any]:
    """Rutene i appen som en flat liste, i samme rekkefølge som ruteren prøver dem.

    FastAPI 0.165 legger en inkludert router inn som én rute som velger blant
    sine egne ruter (med prefiks). `effective_route_contexts()` gir dem enkeltvis,
    hver med `matches`, `endpoint`, `methods` og `path_format`. Brukes av
    mellomvaren og av FR-3-testen, så de ser de samme rutene.
    """
    for rute in ruter:
        kontekster = getattr(rute, "effective_route_contexts", None)
        if callable(kontekster):
            yield from kontekster()
        else:
            yield rute


def trygg_neste(verdi: str | None) -> str:
    """Den lokale stien brukeren skal til etter innlogging, ellers `/` (FR-2, AD-4).

    Godtas bare når verdien begynner med én `/` (ikke `//`), ikke har `\\`,
    kontrolltegn eller mellomrom, er høyst 2048 tegn og ikke peker til
    `/logg-inn` eller `/logg-ut`. Dette er den eneste funksjonen som avgjør `neste`.
    """
    if not verdi or len(verdi) > MAKS_NESTE:
        return "/"
    if not verdi.startswith("/") or verdi.startswith("//"):
        return "/"
    for tegn in verdi:
        if tegn == "\\" or tegn.isspace() or unicodedata.category(tegn).startswith("C"):
            return "/"
    sti = unquote(verdi.split("?", 1)[0].split("#", 1)[0])
    if sti.rstrip("/") in UTELATT_NESTE or sti.startswith("//") or "\\" in sti:
        return "/"
    return verdi


def sett_sesjonscookie(svar: Response, nokkel: str, *, secure: bool) -> None:
    """HttpOnly, `SameSite=Lax`, `Secure` i produksjon, `Path=/` og 7 dager (AD-4)."""
    svar.set_cookie(
        SESJON_COOKIE,
        nokkel,
        max_age=SESJON_SEKUNDER,
        path="/",
        httponly=True,
        samesite="lax",
        secure=secure,
    )


def sesjonscookie_header(nokkel: str, *, secure: bool) -> tuple[bytes, bytes]:
    """`Set-Cookie` for sesjonen som rå ASGI-header, med attributtene fra `sett_sesjonscookie`.

    Brukes av mellomvaren etter innlogging på 401-siden (AD-7).
    """
    svar = Response()
    sett_sesjonscookie(svar, nokkel, secure=secure)
    return next((navn, verdi) for navn, verdi in svar.raw_headers if navn == b"set-cookie")


def slett_sesjonscookie(svar: Response, *, secure: bool) -> None:
    """Sletter cookien med samme `Path` og attributter som den ble satt med."""
    svar.delete_cookie(
        SESJON_COOKIE,
        path="/",
        httponly=True,
        samesite="lax",
        secure=secure,
    )
