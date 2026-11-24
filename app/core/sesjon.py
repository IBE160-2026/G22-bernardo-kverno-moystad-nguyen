"""Grensesnittet for innlogging, merking av offentlige ruter og sesjonscookien (AD-1, AD-4).

`core` leser og skriver aldri `sesjon`, `bruker` eller `innloggingsforsok`. Den
kaller bare `Autentisering`, som `identity` implementerer og `lag_app()` kobler
inn. Mellomvaren og innloggingsruta når den gjennom `hent_autentisering`.
Ruter får den innloggede brukeren bare gjennom avhengigheten `innlogget_bruker`.
"""

from __future__ import annotations

import unicodedata
from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Any, Protocol, TypeVar, runtime_checkable
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

F = TypeVar("F", bound=Callable[..., Any])


@dataclass(frozen=True)
class Innlogget:
    bruker_id: int
    visningsnavn: str


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


def slett_sesjonscookie(svar: Response, *, secure: bool) -> None:
    """Sletter cookien med samme `Path` og attributter som den ble satt med."""
    svar.delete_cookie(
        SESJON_COOKIE,
        path="/",
        httponly=True,
        samesite="lax",
        secure=secure,
    )
