"""Ruter for oppdrag: oversikten, «Mine oppdrag», «Nytt oppdrag» og detaljene
(FR-5, FR-9, FR-21 grunnsider, NFR-11, UX-DR10–UX-DR14).

- GET `/oppdrag/ny` viser skjemaet med postnummeret fra profilen og en ny
  `skjema_id`. POST på samme sti legger ut oppdraget i `with db.begin():`. Ved
  `RegelBrudd` vises skjemaet igjen med 422, alle feilene og verdiene, også
  `skjema_id` (NFR-10). Ved suksess: 303 til detaljene med kvitteringen
  «Oppdraget er lagt ut.» (PRG). En `skjema_id` som mangler eller har feil
  form, gir feilsiden med 400.
- GET `/oppdrag/{id}` viser detaljene etter tilgangsregelen i FR-9. Menyvalget
  er «Mine oppdrag» på eget oppdrag og «Oppdrag» på andres, med
  `aria-current="true"` (underside).
- Lista i oversikten kommer i 2.3, fanene i «Mine oppdrag» i 2.4.
"""

from __future__ import annotations

import re
from urllib.parse import urlsplit

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from starlette.requests import Request
from starlette.responses import Response

from app.core import domene
from app.core.db import hent_db
from app.core.feil import FinnesIkke, RegelBrudd, feilside
from app.core.kvittering import sett_kvittering
from app.core.postnummer import poststed
from app.core.render import render, tilbake_url
from app.core.sesjon import Innlogget, innlogget_bruker
from app.identity.service import hent_offentlig_bruker
from app.oppdrag.service import hent_for_visning, lagt_ut_av, ny_skjema_id, opprett_oppdrag

router = APIRouter()

MAKS_ID = 2**31 - 1  # største verdi for en heltallskolonne i Postgres

# Feltene i «Nytt oppdrag», i rekkefølgen de vises (FR-5).
SKJEMAFELT = (
    "beskrivelse",
    "tittel",
    "kategori",
    "postnummer",
    "dato",
    "klokkeslett",
    "tilbud",
    "belop",
)
SKJEMA_ID = re.compile(r"[A-Za-z0-9_-]{16,64}")

# Lenkene i feiloppsummeringen går til første felt i gruppen (UX-DR12).
GRUPPELENKER = {
    "nar": "dato",
    "kategori": f"kategori-{domene.KATEGORIER[0][0]}",
    "tilbud": "tilbud-belop",
}


@router.get("/", name="oppdrag.oversikt", response_class=HTMLResponse)
def oversikt(
    request: Request,
    innlogget: Innlogget = Depends(innlogget_bruker),
    db: Session = Depends(hent_db),
) -> HTMLResponse:
    """Oversikten for brukerens eget postnummer, med «+ Legg ut oppdrag» (lista kommer i 2.3)."""
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
    request: Request,
    innlogget: Innlogget = Depends(innlogget_bruker),
    db: Session = Depends(hent_db),
) -> HTMLResponse:
    """Oppdragene brukeren har lagt ut, nyeste først, eller tomtilstanden.

    Grunnversjon før story 2.4, som legger til fanene, gruppene og merkene.
    """
    return render(
        request,
        "oppdrag/mine.html",
        tittel="Mine oppdrag",
        aktiv_meny="mine_oppdrag",
        oppdrag=lagt_ut_av(db, innlogget.bruker_id),
    )


# ---------- nytt oppdrag (FR-5) ----------


def _vis_skjema(
    request: Request,
    *,
    verdier: dict[str, str],
    feil: list[tuple[str, str]] | None = None,
    status_code: int = 200,
) -> HTMLResponse:
    return render(
        request,
        "oppdrag/ny.html",
        tittel="Nytt oppdrag",
        aktiv_meny="mine_oppdrag",
        underside=True,
        fokus="beskrivelse",
        status_code=status_code,
        verdier=verdier,
        poststed=poststed(verdier["postnummer"]) or "",
        antall_tegn=domene.antall_tegn(verdier["beskrivelse"]),
        beskrivelse_maks=domene.BESKRIVELSE_MAKS,
        gruppelenker=GRUPPELENKER,
        feil=feil or [],
        feltfeil=dict(feil or []),
    )


@router.get("/oppdrag/ny", name="oppdrag.ny", response_class=HTMLResponse)
def ny(
    request: Request,
    innlogget: Innlogget = Depends(innlogget_bruker),
    db: Session = Depends(hent_db),
) -> HTMLResponse:
    """Tomt skjema med postnummeret fra profilen og en ny `skjema_id` (FR-5, AD-2)."""
    bruker = hent_offentlig_bruker(db, innlogget.bruker_id)
    verdier = {felt: "" for felt in SKJEMAFELT}
    verdier["postnummer"] = (bruker.postnummer if bruker else None) or ""
    verdier["skjema_id"] = ny_skjema_id()
    return _vis_skjema(request, verdier=verdier)


@router.post("/oppdrag/ny", name="oppdrag.send_ny", response_class=HTMLResponse)
def send_ny(
    request: Request,
    innlogget: Innlogget = Depends(innlogget_bruker),
    db: Session = Depends(hent_db),
) -> Response:
    """Legger ut oppdraget, eller viser skjemaet igjen med alle feilene (FR-5, NFR-5, NFR-10)."""
    skjema: dict[str, str] = request.state.skjema
    skjema_id = skjema.get("skjema_id", "")
    if not SKJEMA_ID.fullmatch(skjema_id):
        return feilside(request, 400)
    verdier = {felt: skjema.get(felt, "") for felt in SKJEMAFELT}
    try:
        with db.begin():
            oppdrag_id = opprett_oppdrag(
                db, oppdragsgiver_id=innlogget.bruker_id, skjema_id=skjema_id, **verdier
            )
    except RegelBrudd as brudd:
        return _vis_skjema(
            request,
            verdier={**verdier, "skjema_id": skjema_id},
            feil=brudd.feil,
            status_code=422,
        )
    svar = RedirectResponse(
        request.app.url_path_for("oppdrag.detaljer", id=oppdrag_id), status_code=303
    )
    sett_kvittering(request, svar, "oppdrag_lagt_ut")
    return svar


# ---------- detaljer (FR-9) ----------


def _tilbake_fra_detaljer(request: Request) -> str:
    """`tilbake_url`, men aldri tilbake til skjemaet som nettopp ble sendt."""
    url = tilbake_url(request)
    if urlsplit(url).path == request.app.url_path_for("oppdrag.ny"):
        return str(request.app.url_path_for("oppdrag.mine"))
    return url


@router.get("/oppdrag/{id:int}", name="oppdrag.detaljer", response_class=HTMLResponse)
def detaljer(
    request: Request,
    id: int,
    innlogget: Innlogget = Depends(innlogget_bruker),
    db: Session = Depends(hent_db),
) -> HTMLResponse:
    """Detaljene for et oppdrag (FR-9). Finnes ikke og ingen tilgang gir samme 404."""
    if not 1 <= id <= MAKS_ID:
        raise FinnesIkke  # før databasekallet, så store tall ikke gir OverflowError
    oppdrag = hent_for_visning(db, id, innlogget.bruker_id)
    return render(
        request,
        "oppdrag/detaljer.html",
        tittel=oppdrag.tittel,
        aktiv_meny="mine_oppdrag" if oppdrag.er_eier else "oppdrag",
        underside=True,
        oppdrag=oppdrag,
        tilbake_url=_tilbake_fra_detaljer(request),
    )
