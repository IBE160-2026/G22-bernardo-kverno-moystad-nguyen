"""Ruter for registrering, innlogging og utlogging (FR-1, FR-2, UX-DR12, UX-DR22, UX-DR27).

- GET og POST `/registrer` er offentlige. Registreringen kaller
  `service.registrer` direkte, fordi både registrering og innlogging ligger i
  `identity`. Ved `RegelBrudd` vises skjemaet igjen med 422, alle feilene og
  verdiene, men uten passordet (NFR-10). Ved suksess settes sesjonscookien, og
  brukeren sendes til oversikten.

- GET og POST `/logg-inn` er offentlige. Innloggingen går gjennom
  `Autentisering` (AD-4). `neste` bæres som skjult felt og avgjøres bare av
  `trygg_neste`.
- POST `/logg-ut` sletter sesjonen og cookien og sender til innloggingssiden
  med kvitteringen «Du er logget ut.».
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from starlette.requests import Request
from starlette.responses import Response

from app.core.db import hent_db
from app.core.feil import RegelBrudd
from app.core.kvittering import sett_kvittering
from app.core.postnummer import poststed
from app.core.render import render
from app.core.sesjon import (
    SESJON_COOKIE,
    Innloggingsutfall,
    hent_autentisering,
    offentlig,
    sett_sesjonscookie,
    slett_sesjonscookie,
    trygg_neste,
)
from app.identity.service import (
    FEIL_INNLOGGING,
    FOR_MANGE_FORSOK,
    registrer,
    sjekk_innloggingsskjema,
)

router = APIRouter()


def _vis_skjema(
    request: Request,
    *,
    neste: str,
    epost: str = "",
    feil: list[tuple[str, str]] | None = None,
    feltfeil: dict[str, str] | None = None,
    status_code: int = 200,
) -> HTMLResponse:
    return render(
        request,
        "identity/logg_inn.html",
        tittel="Logg inn",
        aktiv_meny=None,
        fokus="epost",
        status_code=status_code,
        neste=neste,
        epost=epost,
        feil=feil or [],
        feltfeil=feltfeil or {},
    )


@router.get("/logg-inn", name="identity.logg_inn", response_class=HTMLResponse)
@offentlig
def vis_logg_inn(request: Request) -> Response:
    if request.state.innlogget is not None:
        return RedirectResponse("/", status_code=303)
    return _vis_skjema(request, neste=trygg_neste(request.query_params.get("neste")))


@router.post("/logg-inn", name="identity.send_logg_inn", response_class=HTMLResponse)
@offentlig
def logg_inn(request: Request, db: Session = Depends(hent_db)) -> Response:
    """FR-2: e-post og passord. Samme melding for feil e-post og feil passord.

    Ved feil vises skjemaet igjen med 422, e-posten beholdt og passordet tømt.
    """
    skjema: dict[str, str] = request.state.skjema
    epost = skjema.get("epost", "")
    passord = skjema.get("passord", "")
    neste = trygg_neste(skjema.get("neste"))

    feltfeil = sjekk_innloggingsskjema(epost, passord)
    if feltfeil:
        return _vis_skjema(
            request,
            neste=neste,
            epost=epost,
            feil=feltfeil,
            feltfeil=dict(feltfeil),
            status_code=422,
        )

    gammel_nokkel = request.cookies.get(SESJON_COOKIE) if request.state.innlogget else None
    with db.begin():
        resultat = hent_autentisering(request).logg_inn(
            db, epost, passord, gammel_nokkel=gammel_nokkel
        )

    if not resultat.vellykket:
        melding = FOR_MANGE_FORSOK if resultat.utfall is Innloggingsutfall.SPERRET else FEIL_INNLOGGING
        return _vis_skjema(request, neste=neste, epost=epost, feil=[("epost", melding)], status_code=422)

    svar = RedirectResponse(neste, status_code=303)
    sett_sesjonscookie(svar, resultat.nokkel, secure=request.app.state.settings.produksjon)
    return svar


# ---------- registrering (FR-1) ----------

# Feltene i skjemaet, i rekkefølgen de vises. Passordet vises aldri igjen.
REGISTRERINGSFELT = ("navn", "epost", "passord", "telefon", "postnummer", "fodselsdato")


def _vis_registrering(
    request: Request,
    *,
    verdier: dict[str, str] | None = None,
    feil: list[tuple[str, str]] | None = None,
    status_code: int = 200,
) -> HTMLResponse:
    verdier = {felt: (verdier or {}).get(felt, "") for felt in REGISTRERINGSFELT if felt != "passord"}
    return render(
        request,
        "identity/registrer.html",
        tittel="Registrering",
        aktiv_meny=None,
        fokus="navn",
        status_code=status_code,
        verdier=verdier,
        poststed=poststed(verdier["postnummer"]) or "",
        feil=feil or [],
        feltfeil=dict(feil or []),
    )


@router.get("/registrer", name="identity.registrer", response_class=HTMLResponse)
@offentlig
def vis_registrer(request: Request) -> Response:
    if request.state.innlogget is not None:
        return RedirectResponse("/", status_code=303)
    return _vis_registrering(request)


@router.post("/registrer", name="identity.send_registrer", response_class=HTMLResponse)
@offentlig
def send_registrer(request: Request, db: Session = Depends(hent_db)) -> Response:
    """FR-1: oppretter kontoen og logger inn, eller viser skjemaet igjen med alle feilene.

    Ved feil: 422, verdiene beholdt, passordet tømt og fokus på feiloppsummeringen.
    Ved suksess: ny sesjon og 303 til oversikten. Innloggede sendes til `/` uten ny konto.
    """
    if request.state.innlogget is not None:
        return RedirectResponse("/", status_code=303)
    skjema: dict[str, str] = request.state.skjema
    verdier = {felt: skjema.get(felt, "") for felt in REGISTRERINGSFELT}
    try:
        with db.begin():
            nokkel = registrer(db, **verdier)
    except RegelBrudd as brudd:
        return _vis_registrering(request, verdier=verdier, feil=brudd.feil, status_code=422)

    svar = RedirectResponse("/", status_code=303)
    sett_sesjonscookie(svar, nokkel, secure=request.app.state.settings.produksjon)
    return svar


@router.post("/logg-ut", name="identity.logg_ut")
def logg_ut(request: Request, db: Session = Depends(hent_db)) -> Response:
    """FR-2: sesjonsraden og cookien slettes, og brukeren får kvitteringen på innloggingssiden."""
    with db.begin():
        hent_autentisering(request).logg_ut(db, request.cookies.get(SESJON_COOKIE))
    svar = RedirectResponse(request.app.url_path_for("identity.logg_inn"), status_code=303)
    slett_sesjonscookie(svar, secure=request.app.state.settings.produksjon)
    sett_kvittering(request, svar, "logget_ut")
    return svar
