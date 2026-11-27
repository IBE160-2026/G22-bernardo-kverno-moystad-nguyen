"""Mellomvaren i fast rekkefølge, registrert på ett sted (AD-5).

Fra ytterst: feilhåndtering → sikkerhetsheadere → CSRF/Origin → sesjon → ruter.
All mellomvare er ren ASGI. `tests/core/test_mellomvare.py` sjekker rekkefølgen.
"""

from __future__ import annotations

import logging
from urllib.parse import quote, urlencode

from sqlalchemy.exc import SQLAlchemyError

from starlette.concurrency import run_in_threadpool
from starlette.datastructures import Headers
from starlette.middleware import Middleware
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response
from starlette.routing import Match
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.core.config import Settings
from app.core.csrf import CSRF_FELT, CsrfMellomvare, _avspilling
from app.core.feil import NOE_GIKK_GALT, FeilMellomvare
from app.core.headere import HeaderMellomvare
from app.core.render import render, render_fragment
from app.core.sesjon import (
    FEIL_INNLOGGING,
    INNLOGGING_PREFIKS,
    SESJON_COOKIE,
    Autentisering,
    Innloggingsprov,
    alle_ruter,
    er_offentlig,
    prov_innlogging,
    sesjonscookie_header,
    trygg_neste,
)

logger = logging.getLogger(__name__)

LESEMETODER = frozenset({"GET", "HEAD"})
INNLOGGING_EPOST = INNLOGGING_PREFIKS + "epost"
INNLOGGING_PASSORD = INNLOGGING_PREFIKS + "passord"
# Merket for filer som ikke kunne bli skjulte felt. Verdien er filfeltenes navn, skilt med komma.
INNLOGGING_FIL = INNLOGGING_PREFIKS + "fil"
# Felt som aldri blir skjulte felt på 401-siden (AD-7). CSRF-nøkkelen skrives av siden selv.
UTELATTE_FELT = frozenset({"passord", CSRF_FELT})
URLENCODED = b"application/x-www-form-urlencoded"


class SesjonMellomvare:
    """Innlogging kreves som standard (FR-3, AD-4, AD-7, AR-14).

    - Setter `request.state.innlogget` gjennom `Autentisering`.
    - Finner ruta med `route.matches(scope)`. Ruter merket `offentlig` og
      `/static/` slipper gjennom. Treffer ingen rute, går forespørselen videre
      til 404.
    - Uten innlogging gir GET og HEAD 303 til `/logg-inn?neste=<sti>`, og
      forespørsler med `X-Fragment` gir 401-fragmentet «Du må logge inn igjen.».
      Ruta kalles ikke, så ingen data endres.
    - Andre metoder uten innlogging gir 401-siden «Du må logge inn igjen.» (AD-7):
      alle innsendte tekstfelt som skjulte felt (unntatt `passord`, `csrf_token`
      og felt som begynner med `_`), CSRF-nøkkelen fra `request.state.csrf`,
      feltene `_innlogging_epost` og `_innlogging_passord` og knappen «Logg inn»,
      som sender skjemaet som multipart til samme adresse. Filer kan ikke bli
      skjulte felt. Hadde innsendingen filer, sier siden «Velg bildet på nytt
      etter innlogging.», og merket `_innlogging_fil` har navnene på filfeltene.
      Den første 401-siden rendres uten databasekall og viser aldri innhold fra
      databasen.
    - `_innlogging_*`-feltene fjernes alltid fra `request.state.skjema` og fra
      kroppen, som spilles av på nytt uten dem. Merket blir
      `request.state.tapte_filer`.
    - Kommer 401-skjemaet tilbake uten gyldig sesjon til en rute som krever
      innlogging, logger mellomvaren inn med `prov_innlogging`, den samme som
      `/logg-inn` bruker (FR-2, T-6). Innloggingen har egen transaksjon, som er
      committet før ruta åpner sin (unntak i AD-17). Lykkes den, får forespørselen
      den nye sesjonen i `cookie`-headeren og `request.state.innlogget`, svaret
      får `Set-Cookie` foran rutas egne headere, og ruta behandler innsendingen
      som den nye brukeren. Ellers vises 401-siden igjen med feilen.
    - `Cache-Control: no-store` settes sammen med sikkerhetsheaderne (`core/headere.py`).

    Passord, e-post og feltverdier logges aldri.
    """

    def __init__(self, app: ASGIApp, *, autentisering: Autentisering, secure_cookie: bool = False) -> None:
        self.app = app
        self.autentisering = autentisering
        self.secure_cookie = secure_cookie

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        tilstand = scope.setdefault("state", {})
        if scope.get("path", "").startswith("/static/"):
            # Statiske filer trenger verken databaseoppslag eller innlogging.
            tilstand["innlogget"] = None
            await self.app(scope, receive, send)
            return

        skjema: dict[str, str] = tilstand.get("skjema") or {}
        innlogging = {navn: skjema.pop(navn) for navn in list(skjema) if navn.startswith(INNLOGGING_PREFIKS)}
        tapte_filer = _tapte_filer(innlogging.get(INNLOGGING_FIL, ""))
        tilstand["tapte_filer"] = tapte_filer
        if innlogging:
            scope, receive = await _uten_innloggingsfelt(scope, receive, skjema)

        innlogget = await run_in_threadpool(self.autentisering.finn_innlogget, Request(scope))
        tilstand["innlogget"] = innlogget
        if innlogget is not None or not self._krever_innlogging(scope):
            await self.app(scope, receive, send)
            return

        feil: list[tuple[str, str]] = []
        feltfeil: dict[str, str] = {}
        if INNLOGGING_EPOST in innlogging and scope["method"] not in LESEMETODER and not _er_fragment(scope):
            gammel_nokkel = Request(scope).cookies.get(SESJON_COOKIE)
            try:
                prov = await run_in_threadpool(
                    self._prov_innlogging,
                    scope,
                    innlogging.get(INNLOGGING_EPOST),
                    innlogging.get(INNLOGGING_PASSORD),
                    gammel_nokkel,
                )
            except SQLAlchemyError:
                # For eksempel «database is locked». Skjemaet vises igjen, så innholdet ikke går tapt (AD-7).
                logger.exception("Innloggingen på 401-siden feilet i databasen for %s", scope.get("path", "/"))
                prov = None
            if prov is None:
                feil = [("epost", NOE_GIKK_GALT)]
            elif prov.nokkel is not None:
                scope = _med_sesjonscookie(scope, prov.nokkel)
                innlogget = await run_in_threadpool(self.autentisering.finn_innlogget, Request(scope))
                tilstand["innlogget"] = innlogget
                if innlogget is not None:
                    send = _med_set_cookie_forst(send, sesjonscookie_header(prov.nokkel, secure=self.secure_cookie))
                    await self.app(scope, receive, send)
                    return
                logger.warning("Ny sesjon fra 401-siden ble ikke funnet igjen for %s", scope.get("path", "/"))
                feil = [("epost", FEIL_INNLOGGING)]
            else:
                feil, feltfeil = prov.feil, prov.feltfeil

        svar = self._avvis(
            scope,
            feil=feil,
            feltfeil=feltfeil,
            epost=innlogging.get(INNLOGGING_EPOST, ""),
            tapte_filer=tapte_filer | set(tilstand.get("filer") or {}),
        )
        await svar(scope, receive, send)

    def _prov_innlogging(
        self, scope: Scope, epost: str | None, passord: str | None, gammel_nokkel: str | None
    ) -> Innloggingsprov:
        """Innloggingen i egen sesjon og transaksjon, lukket før ruta åpner sin (AD-17)."""
        with scope["app"].state.sesjonsfabrikk() as db:
            return prov_innlogging(self.autentisering, db, epost, passord, gammel_nokkel=gammel_nokkel)

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
    def _avvis(
        scope: Scope,
        *,
        feil: list[tuple[str, str]],
        feltfeil: dict[str, str],
        epost: str,
        tapte_filer: set[str] | frozenset[str],
    ) -> Response:
        request = Request(scope)
        sti = scope.get("path", "/")
        sporring = scope.get("query_string", b"").decode("latin-1")
        neste = trygg_neste(sti + (f"?{sporring}" if sporring else ""))
        innlogging = "/logg-inn?neste=" + quote(neste, safe="/")
        if _er_fragment(scope):
            return render_fragment(
                request, "core/logg_inn_igjen_fragment.html", status_code=401, innlogging_url=innlogging
            )
        if scope["method"] in LESEMETODER:
            return RedirectResponse(innlogging, status_code=303)
        skjema: dict[str, str] = scope["state"].get("skjema") or {}
        return render(
            request,
            "core/logg_inn_igjen.html",
            tittel="Du må logge inn igjen",
            aktiv_meny=None,
            fokus="epost",
            med_menytall=False,
            status_code=401,
            handling=handling_for(sti, sporring),
            skjulte_felt=[
                (navn, verdi)
                for navn, verdi in skjema.items()
                if navn not in UTELATTE_FELT and not navn.startswith("_")
            ],
            tapte_filer=",".join(sorted(tapte_filer)),
            epost=epost,
            feil=feil,
            feltfeil=feltfeil,
        )


def handling_for(sti: str, sporring: str) -> str:
    """`action` på 401-siden: samme adresse som innsendingen (AD-7).

    Stien kodes på nytt (omvendt skråstrek, `?`, `#` og mellomrom blir `%..`), og har nøyaktig én `/`
    foran, så nettleseren aldri kan lese den som en annen vert.
    """
    return "/" + quote(sti.lstrip("/"), safe="/") + (f"?{sporring}" if sporring else "")


def _er_fragment(scope: Scope) -> bool:
    return Headers(scope=scope).get("x-fragment") is not None


def _tapte_filer(merke: str) -> frozenset[str]:
    """Navnene i merket `_innlogging_fil` (AD-7)."""
    return frozenset(navn.strip() for navn in merke.split(",") if navn.strip())


async def _uten_innloggingsfelt(scope: Scope, receive: Receive, skjema: dict[str, str]) -> tuple[Scope, Receive]:
    """Ny kropp uten `_innlogging_*`-feltene, så ruta aldri kan lese passordet (AD-5, AD-7).

    Kroppen bygges som `application/x-www-form-urlencoded` fra det rensede skjemaet.
    Filene står fortsatt i `request.state.filer`. Den gamle kroppen leses fra
    avspillingen først, så den aldri kommer fram til ruta.
    """
    await receive()
    kropp = urlencode(list(skjema.items())).encode("ascii")
    headere = [
        (navn, verdi) for navn, verdi in scope["headers"] if navn not in (b"content-type", b"content-length")
    ]
    headere += [(b"content-type", URLENCODED), (b"content-length", str(len(kropp)).encode("ascii"))]
    return {**scope, "headers": headere}, _avspilling(kropp, receive)


def _med_sesjonscookie(scope: Scope, nokkel: str) -> Scope:
    """Scopet med den nye sesjonen i `cookie`-headeren.

    `Autentisering.finn_innlogget` og `request.cookies` i ruta ser da samme sesjon.
    De andre cookiene beholdes med sine rå verdier.
    """
    deler: list[str] = []
    andre: list[tuple[bytes, bytes]] = []
    for navn, verdi in scope["headers"]:
        if navn != b"cookie":
            andre.append((navn, verdi))
            continue
        for del_ in verdi.decode("latin-1").split(";"):
            navn_del = del_.split("=", 1)[0].strip()
            if del_.strip() and navn_del != SESJON_COOKIE:
                deler.append(del_.strip())
    deler.append(f"{SESJON_COOKIE}={nokkel}")
    return {**scope, "headers": [*andre, (b"cookie", "; ".join(deler).encode("latin-1"))]}


def _med_set_cookie_forst(send: Send, header: tuple[bytes, bytes]) -> Send:
    """`Set-Cookie` for den nye sesjonen foran rutas egne headere.

    Setter eller sletter ruta selv `sesjon`, kommer dens header sist og gjelder.
    """

    async def send_med_cookie(melding: Message) -> None:
        if melding["type"] == "http.response.start":
            melding = {**melding, "headers": [header, *melding.get("headers", [])]}
        await send(melding)

    return send_med_cookie


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
        Middleware(SesjonMellomvare, autentisering=autentisering, secure_cookie=settings.produksjon),
    ]
