"""Sikkerhetsheadere på alle svar (AD-5, NFR-12).

`HeaderMellomvare` setter dem på vanlige svar. Feilhåndteringen ligger utenfor
og bruker `med_sikkerhetsheadere` på feilsidene den lager selv, så også de får
headerne.

Alle svar unntatt `/static/` får også `Cache-Control: no-store`, så
tilbakeknappen ikke viser innhold etter utlogging (FR-2). Det gjelder også
feilsidene fra CSRF-sjekken og feilhåndteringen.
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
_NAVN = {navn for navn, _ in SIKKERHETSHEADERE}


def med_sikkerhetsheadere(headere: list[tuple[bytes, bytes]], sti: str = "") -> list[tuple[bytes, bytes]]:
    """Headerlista med sikkerhetsheaderne, og `no-store` unntatt for `/static/`, uten dubletter."""
    statisk = sti.startswith("/static/")
    navn = _NAVN if statisk else _NAVN | {INGEN_BUFFER[0]}
    beholdt = [(n, v) for n, v in headere if n.lower() not in navn]
    return beholdt + list(SIKKERHETSHEADERE) + ([] if statisk else [INGEN_BUFFER])


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
