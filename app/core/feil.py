"""Feiltyper og feilsider (AR-26, NFR-10).

- `FeilMellomvare` ligger ytterst. Den fanger uventede unntak og viser «Noe gikk
  galt. Prøv igjen om litt.» med 500, uten databasekall og med
  sikkerhetsheaderne. Unntaket logges uten melding og verdier, bare type, sti
  og hvor i koden det skjedde, så ingen personopplysninger havner i loggen.
- Én handler tar alle `HTTPException` (404 «Fant ikke siden», 405 og andre)
  og `RequestValidationError`, så brukeren aldri ser JSON eller `detail`.
- `FinnesIkke` og `IngenTilgang` gir begge 404 og samme side.
- `RegelBrudd` bærer alle feltfeilene i et skjema, i feltrekkefølge. Ruta
  fanger den og viser skjemaet igjen med 422, alle feilene og verdiene (NFR-10).

`Konflikt` og `Duplikat` kommer i storyene som trenger dem.
"""

from __future__ import annotations

import logging
import traceback

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.requests import Request
from starlette.responses import HTMLResponse, Response
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.core.headere import med_sikkerhetsheadere
from app.core.render import render

logger = logging.getLogger(__name__)

FANT_IKKE_SIDEN = "Fant ikke siden"
NOE_GIKK_GALT = "Noe gikk galt. Prøv igjen om litt."
NODSIDE = (
    '<!doctype html><html lang="nb"><head><meta charset="utf-8">'
    "<title>Noe gikk galt – Nabolagshelten</title></head>"
    f'<body><main><h1>{NOE_GIKK_GALT}</h1><p><a href="/logg-inn">Tilbake</a></p></main></body></html>'
)


class RegelBrudd(Exception):
    """Ett eller flere felt bryter reglene (422, AR-26, NFR-10).

    `feil` er `(felt, melding)` i feltrekkefølge, samme form som feiloppsummeringen
    i `render` bruker. Meldingene er faste tekster og inneholder aldri det brukeren skrev.
    """

    def __init__(self, feil: list[tuple[str, str]]) -> None:
        if not feil:
            raise ValueError("RegelBrudd krever minst én feil.")
        super().__init__(f"{len(feil)} regelbrudd")
        self.feil = list(feil)


class FinnesIkke(Exception):
    """Det som ble spurt etter, finnes ikke (404)."""


class IngenTilgang(Exception):
    """Brukeren har ikke tilgang. Vises som 404, likt `FinnesIkke`."""


def feilside(request: Request, status_code: int, headers: dict[str, str] | None = None) -> HTMLResponse:
    """Vennlig feilside. Rendres uten databasekall."""
    if status_code == 404:
        tittel = overskrift = FANT_IKKE_SIDEN
    else:
        tittel, overskrift = "Noe gikk galt", NOE_GIKK_GALT
    return render(
        request,
        "core/feil.html",
        tittel=tittel,
        aktiv_meny=None,
        overskrift=overskrift,
        status_code=status_code,
        headers=headers,
    )


async def _http_feil(request: Request, exc: Exception) -> Response:
    assert isinstance(exc, StarletteHTTPException)
    return feilside(request, exc.status_code, headers=getattr(exc, "headers", None))


async def _valideringsfeil(request: Request, exc: Exception) -> Response:
    logger.warning("Ugyldig forespørsel til %s %s", request.method, request.url.path)
    return feilside(request, 400)


async def _finnes_ikke(request: Request, exc: Exception) -> Response:
    return feilside(request, 404)


def registrer_feilhandlere(app: FastAPI) -> None:
    app.add_exception_handler(StarletteHTTPException, _http_feil)
    app.add_exception_handler(RequestValidationError, _valideringsfeil)
    app.add_exception_handler(FinnesIkke, _finnes_ikke)
    app.add_exception_handler(IngenTilgang, _finnes_ikke)


def logg_uventet_feil(scope: Scope, exc: BaseException) -> None:
    """Logger type, metode, sti og hvor i koden, men aldri unntaksmeldingen,
    kildelinjene eller spørrestrengen, som kan inneholde personopplysninger (AR-30)."""
    stakk = "\n".join(
        f"  {ramme.filename}:{ramme.lineno} i {ramme.name}"
        for ramme in traceback.extract_tb(exc.__traceback__)
    )
    logger.error(
        "Uventet feil %s i %s %s\n%s",
        type(exc).__name__,
        scope.get("method", ""),
        scope.get("path", ""),
        stakk,
    )


class FeilMellomvare:
    """Ytterste mellomvare: uventede unntak blir en vennlig 500-side (NFR-10)."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        svar_startet = False

        async def send_og_merk(melding: Message) -> None:
            nonlocal svar_startet
            if melding["type"] == "http.response.start":
                svar_startet = True
            await send(melding)

        try:
            await self.app(scope, receive, send_og_merk)
        except Exception as exc:
            logg_uventet_feil(scope, exc)
            if svar_startet:
                # Svaret er delvis sendt og kan ikke byttes ut.
                raise
            try:
                svar: Response = feilside(Request(scope), 500)
            except Exception as feil_i_feilside:
                # Siste utvei: fast HTML, så brukeren aldri ser en rå 500 uten headere.
                logg_uventet_feil(scope, feil_i_feilside)
                svar = HTMLResponse(NODSIDE, status_code=500)
            await _send_med_headere(svar, scope, receive, send)


async def _send_med_headere(svar: Response, scope: Scope, receive: Receive, send: Send) -> None:
    async def send_med_headere(melding: Message) -> None:
        if melding["type"] == "http.response.start":
            melding["headers"] = med_sikkerhetsheadere(
                list(melding.get("headers", [])), scope.get("path", "")
            )
        await send(melding)

    await svar(scope, receive, send_med_headere)
