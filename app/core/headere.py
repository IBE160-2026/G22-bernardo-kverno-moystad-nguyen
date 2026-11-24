"""Sikkerhetsheadere på alle svar (AD-5, NFR-12).

`HeaderMellomvare` setter dem på vanlige svar. Feilhåndteringen ligger utenfor
og bruker `med_sikkerhetsheadere` på feilsidene den lager selv, så også de får
headerne.
"""

from __future__ import annotations

from starlette.types import ASGIApp, Message, Receive, Scope, Send

SIKKERHETSHEADERE: tuple[tuple[bytes, bytes], ...] = (
    (b"content-security-policy", b"frame-ancestors 'none'"),
    (b"x-frame-options", b"DENY"),
    (b"x-content-type-options", b"nosniff"),
    (b"referrer-policy", b"same-origin"),
)
_NAVN = {navn for navn, _ in SIKKERHETSHEADERE}


def med_sikkerhetsheadere(headere: list[tuple[bytes, bytes]]) -> list[tuple[bytes, bytes]]:
    """Headerlista med sikkerhetsheaderne, uten dubletter."""
    beholdt = [(n, v) for n, v in headere if n.lower() not in _NAVN]
    return beholdt + list(SIKKERHETSHEADERE)


class HeaderMellomvare:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_med_headere(melding: Message) -> None:
            if melding["type"] == "http.response.start":
                melding["headers"] = med_sikkerhetsheadere(list(melding.get("headers", [])))
            await send(melding)

        await self.app(scope, receive, send_med_headere)
