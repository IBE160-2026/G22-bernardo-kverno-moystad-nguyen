"""Mellomvaren i fast rekkefølge, registrert på ett sted (AD-5).

Fra ytterst: feilhåndtering → sikkerhetsheadere → CSRF/Origin → sesjon → ruter.
All mellomvare er ren ASGI. `tests/core/test_mellomvare.py` sjekker rekkefølgen.
"""

from __future__ import annotations

from urllib.parse import quote

from starlette.concurrency import run_in_threadpool
from starlette.datastructures import Headers
from starlette.middleware import Middleware
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response
from starlette.routing import Match
from starlette.types import ASGIApp, Receive, Scope, Send

from app.core.config import Settings
from app.core.csrf import CsrfMellomvare
from app.core.feil import FeilMellomvare
from app.core.headere import HeaderMellomvare
from app.core.render import render, render_fragment
from app.core.sesjon import Autentisering, alle_ruter, er_offentlig, trygg_neste

LESEMETODER = frozenset({"GET", "HEAD"})


class SesjonMellomvare:
    """Innlogging kreves som standard (FR-3, AD-4, AR-14).

    - Setter `request.state.innlogget` gjennom `Autentisering`.
    - Finner ruta med `route.matches(scope)`. Ruter merket `offentlig` og
      `/static/` slipper gjennom. Treffer ingen rute, går forespørselen videre
      til 404.
    - Uten innlogging gir GET og HEAD 303 til `/logg-inn?neste=<sti>`. Andre
      metoder, og forespørsler med `X-Fragment`, gir 401 «Du må logge inn igjen.»,
      rendret uten database. Ruta kalles ikke, så ingen data endres.
    - `Cache-Control: no-store` settes sammen med sikkerhetsheaderne (`core/headere.py`).
    """

    def __init__(self, app: ASGIApp, *, autentisering: Autentisering) -> None:
        self.app = app
        self.autentisering = autentisering

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        if scope.get("path", "").startswith("/static/"):
            # Statiske filer trenger verken databaseoppslag eller innlogging.
            scope.setdefault("state", {})["innlogget"] = None
            await self.app(scope, receive, send)
            return

        innlogget = await run_in_threadpool(self.autentisering.finn_innlogget, Request(scope))
        scope.setdefault("state", {})["innlogget"] = innlogget

        if innlogget is None and self._krever_innlogging(scope):
            svar = self._avvis(scope)
            await svar(scope, receive, send)
            return
        await self.app(scope, receive, send)

    @staticmethod
    def _krever_innlogging(scope: Scope) -> bool:
        """Om ruta som treffer, ikke er offentlig. Treffer ingen rute, gir appen 404."""
        delvis = None
        for rute in alle_ruter(scope["app"].router.routes):
            treff, barn = rute.matches(scope)
            if treff is Match.FULL:
                return not er_offentlig(barn.get("endpoint", getattr(rute, "endpoint", None)))
            if treff is Match.PARTIAL and delvis is None:
                delvis = rute
        if delvis is not None:
            # Stien finnes, men ikke for denne metoden (405). Uten innlogging avvises
            # den som om metoden fantes, så svaret ikke avslører mer enn nødvendig.
            return not er_offentlig(getattr(delvis, "endpoint", None))
        return False

    @staticmethod
    def _avvis(scope: Scope) -> Response:
        request = Request(scope)
        fragment = Headers(scope=scope).get("x-fragment") is not None
        sti = scope.get("path", "/")
        sporring = scope.get("query_string", b"").decode("latin-1")
        neste = trygg_neste(sti + (f"?{sporring}" if sporring else ""))
        innlogging = "/logg-inn?neste=" + quote(neste, safe="/")
        if scope["method"] in LESEMETODER and not fragment:
            return RedirectResponse(innlogging, status_code=303)
        if fragment:
            return render_fragment(
                request, "core/logg_inn_igjen_fragment.html", status_code=401, innlogging_url=innlogging
            )
        return render(
            request,
            "core/logg_inn_igjen.html",
            tittel="Du må logge inn igjen",
            aktiv_meny=None,
            status_code=401,
            innlogging_url=innlogging,
        )


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
