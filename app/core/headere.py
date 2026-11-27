"""Sikkerhetsheadere på alle svar (AD-5, NFR-12).

`HeaderMellomvare` setter dem på vanlige svar. Feilhåndteringen ligger utenfor
og bruker `med_sikkerhetsheadere` på feilsidene den lager selv, så også de får
headerne.

Alle svar unntatt `/static/` får også `Cache-Control: no-store`, så
tilbakeknappen ikke viser innhold etter utlogging (FR-2). Det gjelder også
feilsidene fra CSRF-sjekken og feilhåndteringen.

Unntak (AD-18, story 2.7): et svar med `Content-Type: image/jpeg` der ruta har
satt `Cache-Control` selv, beholder den, og `no-store` legges ikke til. Bare
bilderutene (`oppdrag.bilde` og `oppdrag.bilde_liten`) gjør det, med `private, max-age=31536000, immutable`, så
et bilde ikke hentes på nytt for hvert kort. Bildet er bare synlig for den som
allerede kunne se det (FR-9), og URL-en har `?v=`. Alle andre svar får `no-store`,
også om ruta har satt en annen `Cache-Control` (FR-2).
"""

from __future__ import annotations

from starlette.types import ASGIApp, Message, Receive, Scope, Send

SIKKERHETSHEADERE: tuple[tuple[bytes, bytes], ...] = (
    (b"content-security-policy", b"frame-ancestors 'none'"),
    (b"x-frame-options", b"DENY"),
    (b"x-content-type-options", b"nosniff"),
    (b"referrer-policy", b"same-origin"),
)
INGEN_BUFFER = (b"cache-control", b"no-store")
BILDETYPE = b"image/jpeg"  # bare bilderutene beholder sin egen Cache-Control (AD-18)
_NAVN = {navn for navn, _ in SIKKERHETSHEADERE}


def med_sikkerhetsheadere(headere: list[tuple[bytes, bytes]], sti: str = "") -> list[tuple[bytes, bytes]]:
    """Headerlista med sikkerhetsheaderne, uten dubletter.

    `no-store` settes på alt unntatt `/static/` og JPEG-svar der ruta har satt
    `Cache-Control` selv (bilderutene, AD-18). Andre svar mister sin egen
    `Cache-Control` og får `no-store` (FR-2).
    """
    statisk = sti.startswith("/static/")
    jpeg = any(n.lower() == b"content-type" and v.lower().startswith(BILDETYPE) for n, v in headere)
    egen_buffer = jpeg and any(n.lower() == INGEN_BUFFER[0] for n, _ in headere)
    navn = _NAVN if statisk or egen_buffer else _NAVN | {INGEN_BUFFER[0]}
    beholdt = [(n, v) for n, v in headere if n.lower() not in navn]
    ingen_buffer = not statisk and not egen_buffer
    return beholdt + list(SIKKERHETSHEADERE) + ([INGEN_BUFFER] if ingen_buffer else [])


class HeaderMellomvare:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_med_headere(melding: Message) -> None:
            if melding["type"] == "http.response.start":
                melding["headers"] = med_sikkerhetsheadere(
                    list(melding.get("headers", [])), scope.get("path", "")
                )
            await send(melding)

        await self.app(scope, receive, send_med_headere)
