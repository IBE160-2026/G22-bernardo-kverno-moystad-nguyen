"""Rendring av sider og fragmenter med ett Jinja-miljø (AR-27, AD-11).

Alle sider rendres med `render`, som legger til tittel, innlogget bruker,
CSRF-nøkkelen og `tilbake_url`. Autoescape er alltid på. Maler ligger i
`app/<slice>/templates/<slice>/` og brukes som `"identity/logg_inn.html"`.
Kvittering og antallet i menyen kommer i senere stories.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from jinja2 import ChoiceLoader, Environment, FileSystemLoader, StrictUndefined, pass_context
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

APP_MAPPE = Path(__file__).resolve().parents[1]
APPNAVN = "Nabolagshelten"


def _lag_miljo() -> Environment:
    malmapper = sorted(p for p in APP_MAPPE.glob("*/templates") if p.is_dir())
    return Environment(
        loader=ChoiceLoader([FileSystemLoader(str(m), encoding="utf-8") for m in malmapper]),
        autoescape=True,
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )


@pass_context
def _url_for(context: dict[str, Any], name: str, /, **path_params: Any) -> str:
    """Relativ sti til en rute eller en statisk fil (`url_for('static', path=...)`).

    Stien er relativ, så lenkene virker bak Vercel sin proxy uten å vite om
    skjemaet er http eller https.
    """
    request: Request = context["request"]
    return str(request.app.url_path_for(name, **path_params))


miljo = _lag_miljo()
_maler = Jinja2Templates(env=miljo)
miljo.globals["url_for"] = _url_for


def sidetittel(tittel: str, *, feil: bool = False) -> str:
    """«Side – Nabolagshelten», med «Feil: » foran ved valideringsfeil (UX-DR2)."""
    return f"{'Feil: ' if feil else ''}{tittel} – {APPNAVN}"


def tilbake_url(request: Request) -> str:
    """`Referer` fra samme nettsted, ellers startsiden for brukeren.

    Aldri siden selv, og aldri en sti som begynner med `//`. Uten innlogging er
    innloggingssiden startsiden, fordi oversikten krever innlogging og ikke
    finnes før story 1.2.
    """
    referer = request.headers.get("referer")
    if referer:
        deler = urlsplit(referer)
        vert = request.headers.get("host")
        if deler.netloc and deler.netloc == vert and deler.path.startswith("/"):
            sti = deler.path + (f"?{deler.query}" if deler.query else "")
            denne = request.url.path + (f"?{request.url.query}" if request.url.query else "")
            if not sti.startswith("//") and sti != denne:
                return sti
    if getattr(request.state, "innlogget", None) is not None:
        return "/"
    return "/logg-inn"


def _kontekst(request: Request, tittel: str, ctx: dict[str, Any]) -> dict[str, Any]:
    return {
        "tittel": tittel,
        "sidetittel": sidetittel(tittel, feil=bool(ctx.get("feil"))),
        "innlogget": getattr(request.state, "innlogget", None),
        "csrf_token": getattr(request.state, "csrf", ""),
        "tilbake_url": tilbake_url(request),
        **ctx,
    }


def render(
    request: Request,
    mal: str,
    *,
    tittel: str,
    aktiv_meny: str | None,
    fokus: str | None = None,
    status_code: int = 200,
    headers: dict[str, str] | None = None,
    **ctx: Any,
) -> HTMLResponse:
    """Rendrer en hel side med `base.html`."""
    kontekst = _kontekst(request, tittel, ctx)
    kontekst.update(aktiv_meny=aktiv_meny, fokus=fokus)
    return _maler.TemplateResponse(
        request, mal, kontekst, status_code=status_code, headers=headers
    )


def render_fragment(
    request: Request, mal: str, *, status_code: int = 200, **ctx: Any
) -> HTMLResponse:
    """Rendrer et HTML-fragment uten sideramme (AD-15)."""
    kontekst = {"csrf_token": getattr(request.state, "csrf", ""), **ctx}
    return _maler.TemplateResponse(request, mal, kontekst, status_code=status_code)
