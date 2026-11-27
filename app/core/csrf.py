"""CSRF- og Origin-sjekk som ren ASGI-mellomvare (AD-5, NFR-12).

- Hver forespørsel får en CSRF-nøkkel i `request.state.csrf`. Nøkkelen ligger
  signert (HMAC med `SECRET_KEY`, via itsdangerous) i cookien `csrf`, som er
  uavhengig av sesjonen og bare byttes når den mangler eller er ugyldig.
- Alle skjema har det skjulte feltet `csrf_token` med samme nøkkel.
- POST (og andre metoder som kan endre data) avvises med 403 når
  `Origin` ikke er samme vert som `Host`, når `Sec-Fetch-Site` sier at
  forespørselen kommer fra et annet nettsted, eller når nøkkelen ikke stemmer.
- Mellomvaren leser skjemaet én gang (`application/x-www-form-urlencoded` eller
  `multipart/form-data`), legger tekstfeltene i `request.state.skjema` og
  spiller av kroppen på nytt, så ruta også får feltene.
- Kroppen kan være høyst `MAKS_MULTIPART` for `multipart/form-data` og 1 MB
  ellers, sjekket mot `Content-Length` og under lesing. Over grensen gir 413,
  og ruta kalles ikke. `MAKS_MULTIPART` er én fil på 4 MB pluss ett beholdt
  bilde på 4 MB som base64, med margin, så en for stor fil eller et forfalsket
  `bilde_beholdt` får feltfeilen fra `oppdrag/bilde.py` (AD-18, story 2.7). Over
  grensen sier feilsiden «Bildet er for stort. Velg et bilde på høyst 4 MB.»,
  fordi bare skjemaet med bilde sender multipart. De andre skjemaene kan ikke
  sende mer enn 1 MB.
- Filfelt (AD-18): ikke-tomme filer leses som bytes og legges i
  `request.state.filer` (`dict[str, bytes]`, første ikke-tomme fil per navn).
  Et tomt filfelt gir ingen fil. Filene står aldri i `request.state.skjema`, og
  bare `oppdrag/bilde.py` åpner dem.
"""

from __future__ import annotations

import hmac
import math
import secrets
from urllib.parse import urlsplit

from itsdangerous import BadSignature, URLSafeSerializer
from starlette.datastructures import Headers
from starlette.requests import Request, cookie_parser
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.core.domene import BILDE_MAKS_BYTE
from app.core.feil import feilside

CSRF_COOKIE = "csrf"
CSRF_FELT = "csrf_token"
MAKS_KROPP = 1024 * 1024  # 1 MB, alle kropper unntatt multipart
# Skjema med filfelt (AD-18): én fil og ett beholdt bilde som base64, begge på høyst 4 MB,
# pluss 256 KiB til de andre feltene.
MAKS_MULTIPART = BILDE_MAKS_BYTE + math.ceil(BILDE_MAKS_BYTE * 4 / 3) + 256 * 1024
# Feilsiden for en multipart-kropp over grensen. Samme tekst som `oppdrag/bilde.py` (FR-27).
BILDET_ER_FOR_STORT = "Bildet er for stort. Velg et bilde på høyst 4 MB."
MULTIPART = "multipart/form-data"
TRYGGE_METODER = frozenset({"GET", "HEAD", "OPTIONS", "TRACE"})
SKJEMATYPER = ("application/x-www-form-urlencoded", "multipart/form-data")
GODTATT_SEC_FETCH_SITE = frozenset({"same-origin", "none"})


class _ForStorKropp(Exception):
    pass


class _Frakoblet(Exception):
    """Klienten koblet fra før hele kroppen kom. Ingen rute kalles, og ingen svar sendes."""


class CsrfMellomvare:
    def __init__(self, app: ASGIApp, *, secret_key: str, secure_cookie: bool) -> None:
        self.app = app
        self.signerer = URLSafeSerializer(secret_key, salt="csrf")
        self.secure_cookie = secure_cookie

    # ---------- nøkkel og cookie ----------

    def _les_nokkel(self, headere: Headers) -> str | None:
        signert = cookie_parser(headere.get("cookie", "")).get(CSRF_COOKIE)
        if not signert:
            return None
        try:
            nokkel = self.signerer.loads(signert)
        except BadSignature:
            return None
        return nokkel if isinstance(nokkel, str) and nokkel else None

    def _cookie_header(self, nokkel: str) -> tuple[bytes, bytes]:
        verdi = f"{CSRF_COOKIE}={self.signerer.dumps(nokkel)}; Path=/; HttpOnly; SameSite=Lax"
        if self.secure_cookie:
            verdi += "; Secure"
        return (b"set-cookie", verdi.encode("latin-1"))

    # ---------- ASGI ----------

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headere = Headers(scope=scope)
        nokkel = self._les_nokkel(headere)
        ny_nokkel = nokkel is None
        if nokkel is None:
            nokkel = secrets.token_urlsafe(32)
        scope.setdefault("state", {})["csrf"] = nokkel

        async def send_med_cookie(melding: Message) -> None:
            if ny_nokkel and melding["type"] == "http.response.start":
                melding["headers"] = [*melding.get("headers", []), self._cookie_header(nokkel)]
            await send(melding)

        if scope["method"] in TRYGGE_METODER:
            await self.app(scope, receive, send_med_cookie)
            return

        if not self._samme_opphav(headere):
            await self._avvis(scope, receive, send_med_cookie, 403)
            return

        try:
            kropp = await self._les_kropp(headere, receive, _maks_kropp(headere))
        except _ForStorKropp:
            overskrift = BILDET_ER_FOR_STORT if _innholdstype(headere) == MULTIPART else None
            await self._avvis(scope, receive, send_med_cookie, 413, overskrift=overskrift)
            return
        except _Frakoblet:
            return

        # En kropp som ikke er et skjema, har heller ingen CSRF-nøkkel og avvises med 403.
        tolket = await self._tolk_skjema(scope, headere, kropp)
        skjema, filer = tolket if tolket is not None else (None, {})
        innsendt = (skjema or {}).get(CSRF_FELT, "")
        if skjema is None or ny_nokkel or not hmac.compare_digest(innsendt.encode(), nokkel.encode()):
            await self._avvis(scope, receive, send_med_cookie, 403)
            return

        scope["state"]["skjema"] = skjema
        scope["state"]["filer"] = filer
        await self.app(scope, _avspilling(kropp, receive), send_med_cookie)

    # ---------- sjekker ----------

    @staticmethod
    def _samme_opphav(headere: Headers) -> bool:
        """`Origin` mot `Host`. Mangler `Origin`, avgjør `Sec-Fetch-Site`.

        Mangler begge, avgjør CSRF-nøkkelen alene (AD-5).
        """
        opphav = headere.get("origin")
        if opphav is not None:
            vert = headere.get("host", "")
            return opphav != "null" and urlsplit(opphav).netloc.lower() == vert.lower()
        sec_fetch_site = headere.get("sec-fetch-site")
        if sec_fetch_site is not None:
            return sec_fetch_site in GODTATT_SEC_FETCH_SITE
        return True

    @staticmethod
    async def _les_kropp(headere: Headers, receive: Receive, maks: int) -> bytes:
        lengde = headere.get("content-length")
        if lengde is not None and lengde.isdigit() and int(lengde) > maks:
            raise _ForStorKropp
        deler: list[bytes] = []
        storrelse = 0
        mer = True
        while mer:
            melding = await receive()
            if melding["type"] == "http.disconnect":
                raise _Frakoblet
            del_ = melding.get("body", b"")
            storrelse += len(del_)
            if storrelse > maks:
                raise _ForStorKropp
            deler.append(del_)
            mer = melding.get("more_body", False)
        return b"".join(deler)

    @staticmethod
    async def _tolk_skjema(
        scope: Scope, headere: Headers, kropp: bytes
    ) -> tuple[dict[str, str], dict[str, bytes]] | None:
        """Tekstfeltene og filene, eller `None` hvis kroppen ikke er et gyldig skjema.

        `max_part_size` er kroppsgrensen, så et stort tekstfelt (`bilde_beholdt`,
        AD-18) ikke avvises av Starlettes standardgrense på 1 MB per felt. Filene
        leses og lukkes her, og et tomt filfelt (ingen fil valgt) gir ingen fil.
        """
        innholdstype = _innholdstype(headere)
        if innholdstype not in SKJEMATYPER:
            return None
        foresporsel = Request(scope, _avspilling(kropp, None))
        try:
            skjema = await foresporsel.form(max_part_size=MAKS_MULTIPART)
        except Exception:
            return None
        try:
            tekst: dict[str, str] = {}
            filer: dict[str, bytes] = {}
            for navn, verdi in skjema.multi_items():
                if isinstance(verdi, str):
                    tekst[navn] = verdi
                elif navn not in filer:
                    innhold = await verdi.read()
                    if innhold:
                        filer[navn] = innhold
            return tekst, filer
        finally:
            await skjema.close()

    async def _avvis(
        self, scope: Scope, receive: Receive, send: Send, status_code: int, *, overskrift: str | None = None
    ) -> None:
        """Vennlig feilside. Ruta kalles ikke, så ingen data endres."""
        svar = feilside(Request(scope), status_code, overskrift=overskrift)
        await svar(scope, receive, send)


def _innholdstype(headere: Headers) -> str:
    return headere.get("content-type", "").split(";")[0].strip().lower()


def _maks_kropp(headere: Headers) -> int:
    """`MAKS_MULTIPART` for `multipart/form-data`, ellers 1 MB (AD-18)."""
    return MAKS_MULTIPART if _innholdstype(headere) == MULTIPART else MAKS_KROPP


def _avspilling(kropp: bytes, receive: Receive | None) -> Receive:
    """En `receive` som gir den leste kroppen først, og så videre til den ekte."""
    sendt = False

    async def spill_av() -> Message:
        nonlocal sendt
        if not sendt:
            sendt = True
            return {"type": "http.request", "body": kropp, "more_body": False}
        if receive is None:
            return {"type": "http.disconnect"}
        return await receive()

    return spill_av
