"""Ruter for oppdrag: oversikten, «Mine oppdrag», «Nytt oppdrag» og detaljene
(FR-5, FR-9, FR-21 grunnsider, NFR-11, UX-DR10–UX-DR14).

- GET `/oppdrag/ny` viser skjemaet med postnummeret fra profilen og en ny
  `skjema_id`. POST på samme sti legger ut oppdraget i `with db.begin():`. Ved
  `RegelBrudd` vises skjemaet igjen med 422, alle feilene og verdiene, også
  `skjema_id` (NFR-10). Ved suksess: 303 til detaljene med kvitteringen
  «Oppdraget er lagt ut.» (PRG). En `skjema_id` som mangler eller har feil
  form, gir feilsiden med 400.
- Skjemaet er alltid ett `<form>` på én skjerm, med to `section` (`data-steg`)
  og en forhåndsvisning over «Publiser». Under 768 px deler `steg.js` det i to
  steg (story 2.2, FR-5, UX-DR16). Ruta skriver overskriftene og titlene for
  stegene i `data-`-attributter, og startverdiene i forhåndsvisningen med de
  samme reglene som `skjema.js` (UX-DR15). Serveren vet ikke skjermbredden.
- GET `/oppdrag/{id}` viser detaljene etter tilgangsregelen i FR-9. Menyvalget
  er «Mine oppdrag» på eget oppdrag og «Oppdrag» på andres, med
  `aria-current="true"` (underside). Andre enn oppdragsgiveren ser
  oppdragsgiverblokken med erfaringen (UX-DR25).
- GET `/` er oversikten med filtrene som GET-parametre: `kategori` (kode eller
  `alle`), `postnummer` og `vist_postnummer`, som postnummerskjemaet sender
  (FR-10, FR-11, UX-DR24). Adressen bestemmer fokus, fordi serveren bare ser
  URL-en. Et ugyldig postnummer gir 200 med feilen ved feltet, og lista står
  uendret. Fanene i «Mine oppdrag» kommer i 2.4.
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
from app.core.postnummer import finnes as postnummer_finnes
from app.core.postnummer import normaliser_postnummer, poststed
from app.core.render import render, sidetittel, tilbake_url
from app.core.sesjon import Innlogget, innlogget_bruker
from app.identity.service import POSTNUMMER_UKJENT, SKRIV_POSTNUMMER, hent_offentlig_bruker
from app.oppdrag.service import (
    SKRIV_BESKRIVELSE,
    SKRIV_TITTEL,
    VELG_KATEGORI,
    erfaring,
    hent_for_visning,
    lagt_ut_av,
    ledige_oppdrag,
    ny_skjema_id,
    opprett_oppdrag,
)

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


# ---------- oversikten (FR-10, FR-11) ----------

ALLE = "alle"  # «Alle» i kategorifilteret: ingen kategori, men fokus på lenken


def _gyldig_postnummer(verdi: str | None) -> str | None:
    """Fire sifre som finnes i registeret, ellers `None`."""
    nummer = normaliser_postnummer(domene.normaliser_tekst(verdi))
    return nummer if nummer is not None and postnummer_finnes(nummer) else None


def _sted(postnummer: str) -> str:
    """«0571 Oslo». Postnummeret vises alltid med poststed (EXPERIENCE.md § Formater)."""
    return " ".join(del_ for del_ in (postnummer, poststed(postnummer)) if del_)


def antallslinje(antall: int, sted: str, kategori: str | None) -> str:
    """«4 ledige oppdrag i 0571 Oslo», «1 ledig oppdrag …», med kategori «… i Hage i 0571 Oslo»."""
    ord_ = "ledig oppdrag" if antall == 1 else "ledige oppdrag"
    hvor = f"{domene.kategori_tekst(kategori)} i {sted}" if kategori else sted
    return f"{antall} {ord_} i {hvor}"


@router.get("/", name="oppdrag.oversikt", response_class=HTMLResponse)
def oversikt(
    request: Request,
    innlogget: Innlogget = Depends(innlogget_bruker),
    db: Session = Depends(hent_db),
) -> HTMLResponse:
    """Ledige oppdrag i ett postnummer, med kategori- og postnummerfilter (FR-10, FR-11).

    Uten `postnummer` gjelder brukerens eget, fra `Innlogget` (R7). Et tomt
    eller ukjent postnummer gir feilen ved feltet, og lista viser
    `vist_postnummer` (det lista viste før innsendingen), eller eget
    postnummer. En ukjent kategori regnes som «Alle».

    Fokus (UX-DR24, høyst ett `autofocus`): feil i feltet eller innsending fra
    postnummerskjemaet gir feltet, ellers gir `kategori` i adressen den valgte
    kategorilenken, ellers flyttes ikke fokus.
    """
    sporring = request.query_params
    eget = innlogget.postnummer or ""
    kategori_verdi = sporring.get("kategori")
    kategori = kategori_verdi if kategori_verdi in domene.KATEGORIKODER else None

    skrevet = sporring.get("postnummer")
    fra_skjema = "vist_postnummer" in sporring
    postnummer_feil: str | None = None
    if skrevet is None:
        vist = eget
    elif (gyldig := _gyldig_postnummer(skrevet)) is not None:
        vist = gyldig
    else:
        tomt = not domene.normaliser_tekst(skrevet)
        postnummer_feil = SKRIV_POSTNUMMER if tomt else POSTNUMMER_UKJENT
        vist = _gyldig_postnummer(sporring.get("vist_postnummer")) or eget

    if postnummer_feil or fra_skjema:
        fokus = "postnummer"
    elif kategori_verdi is not None:
        fokus = "kategori"
    else:
        fokus = None

    oppdrag = ledige_oppdrag(
        db, postnummer=vist, kategori=kategori, bruker_id=innlogget.bruker_id
    ) if vist else []
    sted = _sted(vist)
    overskrift = f"Ledige oppdrag i {sted}"
    return render(
        request,
        "oppdrag/oversikt.html",
        tittel=f"{domene.kategori_tekst(kategori)} – {overskrift}" if kategori else overskrift,
        aktiv_meny="oppdrag",
        fokus=fokus,
        feil_i_tittel=postnummer_feil is not None,
        overskrift=overskrift,
        sted=sted,
        kategori=kategori,
        oppdrag=oppdrag,
        antallslinje=antallslinje(len(oppdrag), sted, kategori) if oppdrag else None,
        # Den valgte kategorien og feltet viser til antallslinja, eller ved 0 treff
        # til første setning i tomtilstanden (EXPERIENCE.md § Filtrene i oversikten).
        beskrevet_av="antallslinje" if oppdrag else "tom-forste",
        poststed=poststed(vist) or "",
        fra_skjema=fra_skjema,
        # Feltet viser det brukeren skrev, også ved feil (NFR-10).
        postnummer_verdi=vist if skrevet is None or postnummer_feil is None else skrevet,
        postnummer_feil=postnummer_feil,
        vist_postnummer=vist,
        # Lenkene i filtrene har postnummeret bare når lista viser et annet enn eget.
        lenkepostnummer=vist if vist != eget else None,
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

# Overskriften og titlen på én skjerm og i hvert steg, ordrett fra EXPERIENCE.md
# § To steg i nytt oppdrag og § Sidetitler (UX-DR16).
NYTT_OPPDRAG = "Nytt oppdrag"
STEGOVERSKRIFT = {1: "Nytt oppdrag 1 av 2", 2: "Nytt oppdrag 2 av 2"}
STEGTITTEL = {1: "Nytt oppdrag, steg 1 av 2", 2: "Nytt oppdrag, steg 2 av 2"}

# Teksten «Neste» viser når et felt i steg 1 er tomt. Samme tekst som serveren gir.
TOMME_FELT = {
    "beskrivelse": SKRIV_BESKRIVELSE,
    "tittel": SKRIV_TITTEL,
    "kategori": VELG_KATEGORI,
}

TOM = "–"  # tomt felt i forhåndsvisningen (EXPERIENCE.md § Forhåndsvisning)


def stegdata() -> list[tuple[str, str]]:
    """`data-`-attributtene steg.js henter overskrift og `<title>` fra (UX-DR16).

    Uten nummer gjelder én skjerm. «-feil» er titlen med «Feil: » foran.
    """
    data = [("data-overskrift", NYTT_OPPDRAG)]
    data += [(f"data-overskrift-{n}", tekst) for n, tekst in STEGOVERSKRIFT.items()]
    for nokkel, tittel in [("", NYTT_OPPDRAG)] + [(f"-{n}", t) for n, t in STEGTITTEL.items()]:
        data.append((f"data-tittel{nokkel}", sidetittel(tittel)))
        data.append((f"data-tittel{nokkel}-feil", sidetittel(tittel, feil=True)))
    return data


def _kr_fra_sifre(sifre: str) -> str:
    """Som `domene.kr`, men rett fra sifrene, uten `int()`.

    `int()` gir `ValueError` ved over 4300 sifre, og da ville 422-siden blitt en 500.
    skjema.js bruker samme algoritme, så server og klient gir samme tekst.
    """
    sifre = sifre.lstrip("0") or "0"
    forste = len(sifre) % 3 or 3
    grupper = [sifre[:forste]] + [sifre[i : i + 3] for i in range(forste, len(sifre), 3)]
    return domene.NBSP.join(grupper) + f"{domene.NBSP}kr"


def _pris(tilbud: str, belop: str) -> str:
    belop = belop.strip()
    if tilbud == "uten":
        return domene.UTEN_BETALING
    if tilbud != "belop" or not belop:
        return TOM
    sifre = re.sub(r"\s", "", belop)
    if sifre.isascii() and sifre.isdigit():
        return _kr_fra_sifre(sifre)
    return f"{belop}{domene.NBSP}kr"


def forhandsvisning(verdier: dict[str, str], sted: str) -> dict[str, str]:
    """Startverdiene i forhåndsvisningen, med de samme reglene som skjema.js (UX-DR15).

    Ingen tolkning av tid: dato og klokkeslett vises slik brukeren skrev dem
    (AD-9). Bare sifre i beløpet formateres som `kr`; annen tekst vises som den er.
    """
    dato, klokkeslett = verdier["dato"].strip(), verdier["klokkeslett"].strip()
    postnummer = verdier["postnummer"].strip()
    if postnummer:
        sted_tekst = f"{postnummer} {sted}" if sted else postnummer
    else:
        sted_tekst = TOM
    kategori = verdier["kategori"]
    return {
        "kategori": kategori if kategori in domene.KATEGORIKODER else "",
        "tittel": verdier["tittel"].strip() or TOM,
        "tid": f"{dato} kl. {klokkeslett}" if dato and klokkeslett else TOM,
        "sted": sted_tekst,
        "pris": _pris(verdier["tilbud"], verdier["belop"]),
    }


def _vis_skjema(
    request: Request,
    *,
    verdier: dict[str, str],
    feil: list[tuple[str, str]] | None = None,
    status_code: int = 200,
) -> HTMLResponse:
    sted = poststed(verdier["postnummer"]) or ""
    return render(
        request,
        "oppdrag/ny.html",
        tittel=NYTT_OPPDRAG,
        aktiv_meny="mine_oppdrag",
        underside=True,
        fokus="beskrivelse",
        status_code=status_code,
        verdier=verdier,
        poststed=sted,
        forhandsvisning=forhandsvisning(verdier, sted),
        stegdata=stegdata(),
        tomme_felt=TOMME_FELT,
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
    verdier = {felt: "" for felt in SKJEMAFELT}
    verdier["postnummer"] = innlogget.postnummer or ""
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
    """Detaljene for et oppdrag (FR-9). Finnes ikke og ingen tilgang gir samme 404.

    Andre enn oppdragsgiveren får `OffentligBruker` og `Erfaring` for
    oppdragsgiveren til blokken «Lagt ut av …» (UX-DR25). En slettet
    oppdragsgiver vises som «Slettet bruker», uten erfaring og lenke (AD-8).
    """
    if not 1 <= id <= MAKS_ID:
        raise FinnesIkke  # før databasekallet, så store tall ikke gir OverflowError
    oppdrag = hent_for_visning(db, id, innlogget.bruker_id)
    oppdragsgiver = None
    oppdragsgivers_erfaring = None
    if not oppdrag.er_eier:
        oppdragsgiver = hent_offentlig_bruker(db, oppdrag.oppdragsgiver_id)
        if oppdragsgiver is not None and not oppdragsgiver.slettet:
            oppdragsgivers_erfaring = erfaring(db, [oppdragsgiver.id])[oppdragsgiver.id]
    return render(
        request,
        "oppdrag/detaljer.html",
        tittel=oppdrag.tittel,
        aktiv_meny="mine_oppdrag" if oppdrag.er_eier else "oppdrag",
        underside=True,
        oppdrag=oppdrag,
        oppdragsgiver=oppdragsgiver,
        erfaring=oppdragsgivers_erfaring,
        tilbake_url=_tilbake_fra_detaljer(request),
    )
