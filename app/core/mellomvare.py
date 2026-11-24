"""Mellomvaren i fast rekkefølge, registrert på ett sted (AD-5).

Fra ytterst: feilhåndtering → sikkerhetsheadere → CSRF/Origin → sesjon → ruter.
All mellomvare er ren ASGI. `tests/core/test_mellomvare.py` sjekker rekkefølgen.
"""

from __future__ import annotations

from starlette.concurrency import run_in_threadpool
from starlette.middleware import Middleware
from starlette.requests import Request
from starlette.types import ASGIApp, Receive, Scope, Send

from app.core.config import Settings
from app.core.csrf import CsrfMellomvare
from app.core.feil import FeilMellomvare
from app.core.headere import HeaderMellomvare
from app.core.sesjon import Autentisering


class SesjonMellomvare:
    """Setter `request.state.innlogget` gjennom `Autentisering` (AD-4).

    Avvisning av forespørsler uten innlogging (303 og 401) kommer i story 1.2.
    """

    def __init__(self, app: ASGIApp, *, autentisering: Autentisering) -> None:
        self.app = app
        self.autentisering = autentisering

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        if scope.get("path", "").startswith("/static/"):
            innlogget = None  # statiske filer trenger ikke databaseoppslag
        else:
            innlogget = await run_in_threadpool(self.autentisering.finn_innlogget, Request(scope))
        scope.setdefault("state", {})["innlogget"] = innlogget
        await self.app(scope, receive, send)


def lag_mellomvare(settings: Settings, autentisering: Autentisering) -> list[Middleware]:
    """Mellomvaren fra ytterst til innerst."""
    return [
        Middleware(FeilMellomvare),
        Middleware(HeaderMellomvare),
        Middleware(
            CsrfMellomvare,
            secret_key=settings.secret_key,
            secure_cookie=settings.produksjon,
        ),
        Middleware(SesjonMellomvare, autentisering=autentisering),
    ]
