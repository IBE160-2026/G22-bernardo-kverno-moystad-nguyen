"""Profilsidene: egen profil og andres profil (FR-21 grunnversjon, AD-16, AR-24).

Malene får bare `OffentligBruker`, aldri ORM-objektet, så telefon, e-post og
fødselsdato aldri havner i HTML. Erfaring og tilbakemeldinger kommer i story 4.3.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from starlette.requests import Request
from starlette.responses import Response

from app.core.db import hent_db
from app.core.feil import FinnesIkke
from app.core.render import render
from app.core.sesjon import Innlogget, innlogget_bruker
from app.identity.service import hent_offentlig_bruker

router = APIRouter()


@router.get("/profil", name="profil.min", response_class=HTMLResponse)
def min_profil(
    request: Request,
    innlogget: Innlogget = Depends(innlogget_bruker),
    db: Session = Depends(hent_db),
) -> HTMLResponse:
    """Egen profil: navn, postnummer med poststed og «Logg ut» (FR-21, FR-2)."""
    bruker = hent_offentlig_bruker(db, innlogget.bruker_id)
    if bruker is None:
        raise FinnesIkke
    return render(request, "profil/min.html", tittel="Min profil", aktiv_meny="profil", bruker=bruker)


@router.get("/profil/{bruker_id:int}", name="profil.vis", response_class=HTMLResponse)
def vis_profil(
    request: Request,
    bruker_id: int,
    innlogget: Innlogget = Depends(innlogget_bruker),
    db: Session = Depends(hent_db),
) -> Response:
    """Andres profil: navn og postnummer med poststed (FR-21). Ukjent eller slettet id gir 404."""
    if bruker_id == innlogget.bruker_id:
        return RedirectResponse(request.app.url_path_for("profil.min"), status_code=303)
    bruker = hent_offentlig_bruker(db, bruker_id)
    if bruker is None or bruker.slettet:
        raise FinnesIkke
    return render(
        request,
        "profil/vis.html",
        tittel=f"{bruker.visningsnavn} – profil",
        aktiv_meny=None,
        bruker=bruker,
    )
