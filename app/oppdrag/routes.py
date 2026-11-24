"""Grunnsidene for oppdrag: oversikten og «Mine oppdrag» (FR-21 grunnsider, NFR-11).

Story 1.2 har bare overskrift og tomtilstand. Oppdragene, «+ Legg ut oppdrag»,
postnummerfilteret og fanene kommer i Epic 2 (2.1, 2.3 og 2.4).
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from starlette.requests import Request

from app.core.db import hent_db
from app.core.feil import FinnesIkke
from app.core.render import render
from app.core.sesjon import Innlogget, innlogget_bruker
from app.identity.service import hent_offentlig_bruker

router = APIRouter()


@router.get("/", name="oppdrag.oversikt", response_class=HTMLResponse)
def oversikt(
    request: Request,
    innlogget: Innlogget = Depends(innlogget_bruker),
    db: Session = Depends(hent_db),
) -> HTMLResponse:
    """Oversikten for brukerens eget postnummer (FR-10 kommer i 2.1)."""
    bruker = hent_offentlig_bruker(db, innlogget.bruker_id)
    if bruker is None:
        raise FinnesIkke
    return render(
        request,
        "oppdrag/oversikt.html",
        tittel=f"Ledige oppdrag i {bruker.sted}",
        aktiv_meny="oppdrag",
        sted=bruker.sted,
    )


@router.get("/mine-oppdrag", name="oppdrag.mine", response_class=HTMLResponse)
def mine_oppdrag(
    request: Request, innlogget: Innlogget = Depends(innlogget_bruker)
) -> HTMLResponse:
    """«Mine oppdrag» med tomtilstanden. Fanene og den lange tittelen kommer i 2.4."""
    return render(request, "oppdrag/mine.html", tittel="Mine oppdrag", aktiv_meny="mine_oppdrag")
