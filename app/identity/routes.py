"""Ruter for konto og innlogging (FR-2, UX-DR2).

Story 1.1 har bare GET `/logg-inn`. Innsending og utlogging kommer i story 1.2.
"""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from starlette.requests import Request

from app.core.render import render
from app.core.sesjon import offentlig

router = APIRouter()


@router.get("/logg-inn", name="identity.logg_inn", response_class=HTMLResponse)
@offentlig
def vis_logg_inn(request: Request) -> HTMLResponse:
    return render(request, "identity/logg_inn.html", tittel="Logg inn", aktiv_meny=None)
