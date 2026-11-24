"""Grensesnittet for innlogging, og merking av offentlige ruter (AD-1, AD-4).

`core` leser og skriver aldri `sesjon` eller `bruker`. Den kaller bare
`Autentisering`, som `identity` implementerer og `lag_app()` kobler inn.
`logg_inn` og `logg_ut` legges til grensesnittet i story 1.2.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Protocol, TypeVar, runtime_checkable

from starlette.requests import Request

SESJON_COOKIE = "sesjon"

F = TypeVar("F", bound=Callable[..., Any])


@dataclass(frozen=True)
class Innlogget:
    bruker_id: int
    visningsnavn: str


@runtime_checkable
class Autentisering(Protocol):
    def finn_innlogget(self, request: Request) -> Innlogget | None:
        """Den innloggede brukeren for forespørselen, eller `None`.

        Leser cookien `sesjon` og slår opp gjennom `request.app.state.sesjonsfabrikk`.
        """
        ...


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
