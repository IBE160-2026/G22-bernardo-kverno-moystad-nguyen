"""Rendring av sider og fragmenter med ett Jinja-miljø (AR-27, AD-11).

Alle sider rendres med `render`, som legger til tittel, innlogget bruker,
CSRF-nøkkelen, `tilbake_url`, kvitteringen, aktivt menyvalg og fokusmålet. Autoescape er
alltid på. Maler ligger i `app/<slice>/templates/<slice>/` og brukes som
`"identity/logg_inn.html"`. Antallet i menyen kommer i story 2.4.

Undersider (nytt oppdrag, detaljer) gir `underside=True`. Da får menyvalget de
hører til, `aria-current="true"` i stedet for `"page"` (EXPERIENCE.md § Information
Architecture).

Filtrene `tidspunkt`, `kr`, `kategori_tekst`, `status_tekst`, `fullforte` og
`vurdering` er eneste måte maler formaterer tid, beløp, kategori, status og
erfaring på (AD-9, AD-10, FR-21).

`filterlenke(**endringer)` er eneste sted lenkene i filtrene i oversikten
bygges (AR-27, FR-11).

Fokus (UX-DR27): høyst ett fokusmål per side, i rekkefølgen
feiloppsummering > kvittering > sidens eget mål (`fokus`). Malen setter
`autofocus` der `fokusmal` sier.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlencode, urlsplit

from jinja2 import ChoiceLoader, Environment, FileSystemLoader, StrictUndefined, pass_context
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from app.core import domene
from app.core.kvittering import har_kvitteringscookie, les_kvittering, slett_kvittering

APP_MAPPE = Path(__file__).resolve().parents[1]
APPNAVN = "Nabolagshelten"
MENYVALG = (None, "oppdrag", "mine_oppdrag", "profil")


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


# Parametrene filterlenkene bærer videre. `vist_postnummer` (markøren fra
# postnummerskjemaet) og ukjente parametre følger aldri med i lenker fra appen.
FILTERPARAMETRE = ("kategori", "postnummer")


@pass_context
def _filterlenke(context: dict[str, Any], **endringer: str | None) -> str:
    """Relativ lenke til oversikten, `/?…`, bygget fra den gjeldende spørringen (AR-27).

    Bare `kategori` og `postnummer` beholdes, i samme rekkefølge, og nye kommer
    til slutt. En endring med `None` fjerner parameteren. `vist_postnummer` og
    ukjente parametre (for eksempel `utm`) fjernes alltid, så de aldri følger med
    i en lenke som deles. Uten parametre: `/`.
    """
    request: Request = context["request"]
    par = {n: v for n, v in request.query_params.items() if n in FILTERPARAMETRE}
    par.update(endringer)
    par = {n: v for n, v in par.items() if v is not None and n in FILTERPARAMETRE}
    return f"/?{urlencode(par)}" if par else "/"


def _tidspunkt(verdi: datetime) -> str:
    # Importeres her, fordi `tid` importerer `feil`, som importerer denne modulen.
    from app.core.tid import vis_tidspunkt

    return vis_tidspunkt(verdi)


miljo = _lag_miljo()
_maler = Jinja2Templates(env=miljo)
miljo.globals["url_for"] = _url_for
miljo.globals["KATEGORIER"] = domene.KATEGORIER
miljo.globals["filterlenke"] = _filterlenke
miljo.filters["tidspunkt"] = _tidspunkt
miljo.filters["kr"] = domene.kr
miljo.filters["kategori_tekst"] = domene.kategori_tekst
miljo.filters["status_tekst"] = domene.status_tekst
miljo.filters["fullforte"] = domene.fullforte_tekst
miljo.filters["vurdering"] = domene.vurdering_tekst


def sidetittel(tittel: str, *, feil: bool = False) -> str:
    """«Side – Nabolagshelten», med «Feil: » foran ved valideringsfeil (UX-DR2)."""
    return f"{'Feil: ' if feil else ''}{tittel} – {APPNAVN}"


def tilbake_url(request: Request) -> str:
    """`Referer` fra samme nettsted, ellers startsiden for brukeren.

    Aldri siden selv, og aldri en sti som begynner med `//`. Uten innlogging er
    innloggingssiden startsiden, fordi oversikten krever innlogging (FR-3).
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


def fokusmal(*, feil: bool, kvittering: bool, fokus: str | None) -> str | None:
    """Ett fokusmål: feiloppsummering > kvittering > sidens eget mål (UX-DR27)."""
    if feil:
        return "feiloppsummering"
    if kvittering:
        return "kvittering"
    return fokus


def _kontekst(
    request: Request, tittel: str, ctx: dict[str, Any], *, feil_i_tittel: bool = False
) -> dict[str, Any]:
    return {
        "tittel": tittel,
        "sidetittel": sidetittel(tittel, feil=feil_i_tittel or bool(ctx.get("feil"))),
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
    underside: bool = False,
    feil_i_tittel: bool = False,
    status_code: int = 200,
    headers: dict[str, str] | None = None,
    **ctx: Any,
) -> HTMLResponse:
    """Rendrer en hel side med `base.html`.

    `aktiv_meny` er `"oppdrag"`, `"mine_oppdrag"`, `"profil"` eller `None`.
    `underside=True` gir menyvalget `aria-current="true"` i stedet for `"page"`.
    `feil` (i `ctx`) er en liste med `(felt, melding)` til feiloppsummeringen.
    `feil_i_tittel=True` gir «Feil: » i `<title>` uten feiloppsummering, for en
    feil som bare vises ved feltet (filteret i oversikten, FR-11).
    """
    if aktiv_meny not in MENYVALG:
        raise ValueError(f"Ukjent menyvalg: {aktiv_meny!r}")
    kontekst = _kontekst(request, tittel, ctx, feil_i_tittel=feil_i_tittel)
    kontekst.setdefault("feil", [])
    kontekst.setdefault("kvittering", les_kvittering(request))
    kontekst.update(
        aktiv_meny=aktiv_meny,
        fokus=fokus,
        underside=underside,
        fokusmal=fokusmal(
            feil=bool(kontekst["feil"]), kvittering=bool(kontekst["kvittering"]), fokus=fokus
        ),
    )
    svar = _maler.TemplateResponse(
        request, mal, kontekst, status_code=status_code, headers=headers
    )
    if har_kvitteringscookie(request):
        # Kvitteringen vises én gang og slettes i samme svar (UX-DR22).
        slett_kvittering(request, svar)
    return svar


def render_fragment(
    request: Request, mal: str, *, status_code: int = 200, **ctx: Any
) -> HTMLResponse:
    """Rendrer et HTML-fragment uten sideramme (AD-15)."""
    kontekst = {"csrf_token": getattr(request.state, "csrf", ""), **ctx}
    return _maler.TemplateResponse(request, mal, kontekst, status_code=status_code)
