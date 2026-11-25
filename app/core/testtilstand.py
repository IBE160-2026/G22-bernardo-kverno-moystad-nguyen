"""`POST /_test/tilstand`: E2E-testene setter tilstanden her (AD-14, AR-29).

Ruta registreres bare når `APP_ENV=test` (`lag_app()`), så i `local` og
`production` gir stien 404. Den er offentlig, fordi T1 nullstiller før
innlogging, men CSRF gjelder som for alle POST.

Feltene (alle valgfrie):
- `klokke`: ISO 8601 med tidssone, eller tom for vanlig klokke.
- `ki`: `mock` eller `feil`. Lagres i `app.state.ki_utgave` til story 5.1.
- `seed=1`: tømmer tabellene og legger inn testbrukerne på nytt, med
  `app.state.last_eksempeldata` som `lag_app()` kobler inn. `core` importerer
  aldri `app.seed` eller en slice (AD-1).

Alle verdiene sjekkes før noe endres. Ukjent felt eller verdi gir 400, og da
er ingenting endret. Ellers 204.
"""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette.requests import Request
from starlette.responses import PlainTextResponse, Response

from app.core import klokke
from app.core.csrf import CSRF_FELT
from app.core.db import hent_db
from app.core.sesjon import offentlig

router = APIRouter()

KI_UTGAVER = frozenset({"mock", "feil"})
FELT = frozenset({"klokke", "ki", "seed", CSRF_FELT})


class _UgyldigTilstand(ValueError):
    pass


def _tolk_klokke(verdi: str) -> datetime | None:
    if verdi == "":
        return None
    try:
        tidspunkt = datetime.fromisoformat(verdi)
    except ValueError:
        raise _UgyldigTilstand("klokke må være ISO 8601 med tidssone, eller tom.") from None
    if tidspunkt.tzinfo is None or tidspunkt.utcoffset() is None:
        raise _UgyldigTilstand("klokke mangler tidssone.")
    return tidspunkt


def _sjekk(skjema: dict[str, str]) -> dict[str, object]:
    """De gyldige endringene, eller `_UgyldigTilstand` før noe er endret."""
    ukjente = sorted(set(skjema) - FELT)
    if ukjente:
        raise _UgyldigTilstand(f"Ukjent felt: {', '.join(ukjente)}.")
    endringer: dict[str, object] = {}
    if "klokke" in skjema:
        endringer["klokke"] = _tolk_klokke(skjema["klokke"].strip())
    if "ki" in skjema:
        if skjema["ki"] not in KI_UTGAVER:
            raise _UgyldigTilstand("ki må være mock eller feil.")
        endringer["ki"] = skjema["ki"]
    if "seed" in skjema:
        if skjema["seed"] != "1":
            raise _UgyldigTilstand("seed må være 1.")
        endringer["seed"] = True
    return endringer


@router.post("/_test/tilstand", name="core.test_tilstand")
@offentlig
def sett_tilstand(request: Request, db: Session = Depends(hent_db)) -> Response:
    try:
        endringer = _sjekk(request.state.skjema)
    except _UgyldigTilstand as feil:
        return PlainTextResponse(str(feil), status_code=400)

    # Klokka først, så testbrukerne får `opprettet` fra den faste klokka.
    if "klokke" in endringer:
        klokke.sett_na(endringer["klokke"])  # type: ignore[arg-type]
    if endringer.get("seed"):
        with db.begin():
            request.app.state.last_eksempeldata(db)
    if "ki" in endringer:
        request.app.state.ki_utgave = endringer["ki"]
    return Response(status_code=204)
