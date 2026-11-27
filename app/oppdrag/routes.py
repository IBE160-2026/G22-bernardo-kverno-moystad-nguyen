"""Ruter for oppdrag: oversikten, «Mine oppdrag», «Nytt oppdrag», detaljene,
redigering og avbrudd (FR-5–FR-9, FR-21 grunnsider, NFR-11, UX-DR7, UX-DR10–UX-DR18).

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
  uendret.
- GET `/mine-oppdrag` viser «Oppdrag jeg har lagt ut» som lenkerader med
  statusmerke, handlingsmerker og tidspunkt, sortert etter tidspunkt, og linja
  «N oppdrag trenger at du gjør noe.» med tallet fra menyen (FR-8, FR-18,
  UX-DR9, UX-DR26). Rader med merket «Tidspunktet er passert» har snarveiene
  «Endre tidspunkt» og «Avbryt oppdrag» under en skillelinje (story 2.5). Fanene
  kommer i 3.1.
- GET `/oppdrag/{id}/rediger` viser det samme skjemaet (`skjema.html`) med de
  lagrede verdiene, uten KI, `skjema_id` og steg, og med «Lagre endringer»
  (FR-6, FR-8). `?fokus=tidspunkt` («Endre tidspunkt») gir `autofocus` på
  «Dato». POST lagrer i `with db.begin():` og gir 303 til detaljene med
  «Endringene er lagret.», eller 422 med feilene. `h1` og `<title>` har den
  lagrede tittelen. Bare oppdragsgiveren (andre får 404) og bare ved Åpen
  (ellers `Konflikt`).
- GET `/oppdrag/{id}/avbryt` er bekreftelsessiden uten JS, og POST avbryter
  (FR-7, UX-DR18). Med JS åpner `dialog.js` den samme bekreftelsen som
  `<dialog>`. `fra=mine` er den eneste verdien som godtas, og sender brukeren
  tilbake til «Mine oppdrag» etter avbruddet. Alt annet gir detaljene.
- `Konflikt` gir 303 til detaljene med «Oppdraget er endret. Last siden på
  nytt.» (handleren i `core/feil.py`, §4.0).
- Bilde (story 2.7, FR-27, AD-18): skjemaet er `multipart/form-data`. `send_ny`
  og `send_rediger` gir filen (`request.state.filer["bilde"]`), `bilde_beholdt`
  og `fjern_bilde` til `tolk_bildevalg` før `with db.begin():`, så bildet
  dekodes utenfor transaksjonen. Ruta leser aldri fila selv. Ved 422 får malen
  det gyldige bildet som `bilde_beholdt` (base64) og miniatyren som `data:`-URL.
  Ved redigering vises det lagrede bildet med «Bytt bilde» og «Fjern bildet».
- GET `/oppdrag/{id}/bilde` og `/oppdrag/{id}/bilde/liten` gir JPEG-en og
  miniatyren med samme tilgangsregel og samme 404 som detaljene (FR-9), og med
  `Cache-Control: private, max-age=31536000, immutable`. Malene lenker med
  `?v={versjon}`, så et nytt bilde får ny URL.
"""

from __future__ import annotations

import re
from urllib.parse import urlsplit

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from starlette.requests import Request
from starlette.responses import Response

from app.core import domene, klokke
from app.core.db import hent_db, laas_gir_konflikt
from app.core.feil import FinnesIkke, RegelBrudd, feilside
from app.core.kvittering import sett_kvittering
from app.core.postnummer import finnes as postnummer_finnes
from app.core.postnummer import normaliser_postnummer, poststed
from app.core.render import render, sidetittel, tilbake_url
from app.core.sesjon import Innlogget, innlogget_bruker
from app.identity.service import POSTNUMMER_UKJENT, SKRIV_POSTNUMMER, hent_offentlig_bruker
from app.oppdrag.bilde import miniatyr_data_url, til_beholdt
from app.oppdrag.service import (
    AVBRYTBAR,
    INGEN_BILDEVALG,
    KONFLIKT,
    REDIGERBAR,
    SKRIV_BESKRIVELSE,
    SKRIV_TITTEL,
    TIDSPUNKTET_ER_PASSERT,
    VELG_KATEGORI,
    Bildevalg,
    OppdragVisning,
    avbryt_oppdrag,
    detaljer_url,
    erfaring,
    hent_bilde,
    hent_eget_oppdrag,
    hent_for_visning,
    lagt_ut_av,
    ledige_oppdrag,
    merker_lagt_ut,
    ny_skjema_id,
    opprett_oppdrag,
    rediger_oppdrag,
    skjemaverdier_for,
    tolk_bildevalg,
    utgatt,
)

router = APIRouter()

MAKS_ID = 2**31 - 1  # største verdi for en heltallskolonne i Postgres

# Feltene i «Nytt oppdrag», i rekkefølgen de vises (FR-5).
SKJEMAFELT = (
    "beskrivelse",
    "bildetekst",
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
    "bilde": "bilde",
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
    """«Oppdrag jeg har lagt ut»: lenkerader etter tidspunkt, eller tomtilstanden (FR-18).

    Merkene kommer fra `lagt_ut_av` (AD-3). Linja «N oppdrag trenger at du gjør
    noe.» bruker `meny_antall`, som `render` henter fra menykroken med rutas
    sesjon, så linja og menyen viser samme tall med én telling per forespørsel.
    Fanene kommer i 3.1, og til da har `<title>` allerede fanenavnet
    (EXPERIENCE.md § Sidetitler). Gruppene og de andre merkene kommer i 3.5.
    Rader med merket «Tidspunktet er passert» får snarveiene og en dialog hver (2.5).
    """
    return render(
        request,
        "oppdrag/mine.html",
        tittel="Mine oppdrag: Oppdrag jeg har lagt ut",
        aktiv_meny="mine_oppdrag",
        oppdrag=lagt_ut_av(db, innlogget.bruker_id),
        # Rader med dette merket får snarveiene «Endre tidspunkt» og «Avbryt oppdrag» (FR-8).
        passert_merke=TIDSPUNKTET_ER_PASSERT,
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


def _bildefelt(
    request: Request, valg: Bildevalg, oppdrag: OppdragVisning | None = None
) -> dict:
    """Det filfeltet trenger: miniatyren, `bilde_beholdt` og om det finnes et bilde (FR-27).

    Et gyldig bilde fra innsendingen (`valg.ny`) vises som `data:`-URL og følger
    med som `bilde_beholdt`. Ellers vises det lagrede bildet ved redigering, med
    «Fjern bildet» krysset av hvis brukeren krysset den av.
    """
    if valg.ny is not None:
        return {
            "src": miniatyr_data_url(valg.ny),
            "beholdt": til_beholdt(valg.ny),
            "finnes": True,
            "fjern_valgt": False,
        }
    if oppdrag is not None and oppdrag.bilde is not None:
        src = request.app.url_path_for("oppdrag.bilde_liten", id=oppdrag.id)
        return {
            "src": f"{src}?v={oppdrag.bilde.versjon}",
            "beholdt": None,
            "finnes": True,
            "fjern_valgt": valg.fjern,
        }
    return {"src": None, "beholdt": None, "finnes": False, "fjern_valgt": False}


def _vis_skjema(
    request: Request,
    *,
    verdier: dict[str, str],
    feil: list[tuple[str, str]] | None = None,
    status_code: int = 200,
    bildevalg: Bildevalg = INGEN_BILDEVALG,
) -> HTMLResponse:
    """«Nytt oppdrag»: to steg under 768 px, `skjema_id` og «Publiser» (FR-5, UX-DR16)."""
    sted = poststed(verdier["postnummer"]) or ""
    return render(
        request,
        "oppdrag/skjema.html",
        tittel=NYTT_OPPDRAG,
        aktiv_meny="mine_oppdrag",
        underside=True,
        fokus="beskrivelse",
        status_code=status_code,
        skjema_handling=request.app.url_path_for("oppdrag.send_ny"),
        knappetekst="Publiser",
        skjema_id=verdier["skjema_id"],
        to_steg=True,
        **_skjemakontekst(verdier, sted, feil, _bildefelt(request, bildevalg)),
    )


def _skjemakontekst(
    verdier: dict[str, str], sted: str, feil: list[tuple[str, str]] | None, bildefelt: dict
) -> dict:
    """Det skjemaet trenger, felles for «Nytt oppdrag» og redigering (FR-5, FR-6, FR-27)."""
    return {
        "verdier": verdier,
        "bildefelt": bildefelt,
        "bildetekst_antall": domene.antall_tegn(verdier["bildetekst"]),
        "bildetekst_maks": domene.BILDETEKST_MAKS,
        "poststed": sted,
        "forhandsvisning": forhandsvisning(verdier, sted),
        "stegdata": stegdata(),
        "tomme_felt": TOMME_FELT,
        "antall_tegn": domene.antall_tegn(verdier["beskrivelse"]),
        "beskrivelse_maks": domene.BESKRIVELSE_MAKS,
        "gruppelenker": GRUPPELENKER,
        "feil": feil or [],
        "feltfeil": dict(feil or []),
    }


def _bildevalg(request: Request) -> Bildevalg:
    """Filfeltet `bilde`, `bilde_beholdt` og `fjern_bilde` fra mellomvaren (AD-5, AD-18)."""
    skjema: dict[str, str] = request.state.skjema
    filer: dict[str, bytes] = getattr(request.state, "filer", {})
    return tolk_bildevalg(filer.get("bilde"), skjema.get("bilde_beholdt"), skjema.get("fjern_bilde"))


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
    """Legger ut oppdraget, eller viser skjemaet igjen med alle feilene (FR-5, FR-27, NFR-5, NFR-10).

    Bildet tolkes før transaksjonen (`tolk_bildevalg`), og et gyldig bilde vises
    igjen ved 422 (AD-18).
    """
    skjema: dict[str, str] = request.state.skjema
    skjema_id = skjema.get("skjema_id", "")
    if not SKJEMA_ID.fullmatch(skjema_id):
        return feilside(request, 400)
    verdier = {felt: skjema.get(felt, "") for felt in SKJEMAFELT}
    valg = _bildevalg(request)
    try:
        with db.begin():
            oppdrag_id = opprett_oppdrag(
                db,
                oppdragsgiver_id=innlogget.bruker_id,
                skjema_id=skjema_id,
                bildevalg=valg,
                **verdier,
            )
    except RegelBrudd as brudd:
        return _vis_skjema(
            request,
            verdier={**verdier, "skjema_id": skjema_id},
            feil=brudd.feil,
            status_code=422,
            bildevalg=valg,
        )
    svar = RedirectResponse(
        request.app.url_path_for("oppdrag.detaljer", id=oppdrag_id), status_code=303
    )
    sett_kvittering(request, svar, "oppdrag_lagt_ut")
    return svar


# ---------- detaljer (FR-9) ----------

# Skjemaene og bekreftelsene «Tilbake» i detaljene aldri skal gå til (spec 2.1 og 2.5).
_SKJEMASTIER = re.compile(r"/oppdrag/(ny|[0-9]+/rediger|[0-9]+/avbryt)")


def _tilbake_fra_detaljer(request: Request, *, er_eier: bool = False) -> str:
    """`tilbake_url`, men aldri tilbake til et skjema eller en bekreftelse som nettopp ble sendt.

    Etter «Nytt oppdrag», redigering og avbrudd går «Tilbake» til «Mine oppdrag». Det
    gjør den også på eget oppdrag når `tilbake_url` faller tilbake til `/`, for eksempel
    når forrige side var detaljene selv (avbrudd eller `Konflikt` fra dialogen).
    """
    url = tilbake_url(request)
    if _SKJEMASTIER.fullmatch(urlsplit(url).path) or (er_eier and url == "/"):
        return str(request.app.url_path_for("oppdrag.mine"))
    return url


def _sjekk_id(id: int) -> None:
    if not 1 <= id <= MAKS_ID:
        raise FinnesIkke  # før databasekallet, så store tall ikke gir OverflowError


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

    Oppdragsgiveren ser handlingene etter beskrivelsen når status er Åpen
    (FR-6, FR-7, FR-8): «Rediger» og «Avbryt oppdrag», eller merkene fra
    `merker_lagt_ut` med «Endre tidspunkt» og «Avbryt oppdrag» når `utgatt`
    sier at tidspunktet er passert (AD-3).
    """
    _sjekk_id(id)
    oppdrag = hent_for_visning(db, id, innlogget.bruker_id)
    oppdragsgiver = None
    oppdragsgivers_erfaring = None
    if not oppdrag.er_eier:
        oppdragsgiver = hent_offentlig_bruker(db, oppdrag.oppdragsgiver_id)
        if oppdragsgiver is not None and not oppdragsgiver.slettet:
            oppdragsgivers_erfaring = erfaring(db, [oppdragsgiver.id])[oppdragsgiver.id]
    na = klokke.na()
    return render(
        request,
        "oppdrag/detaljer.html",
        tittel=oppdrag.tittel,
        aktiv_meny="mine_oppdrag" if oppdrag.er_eier else "oppdrag",
        underside=True,
        oppdrag=oppdrag,
        oppdragsgiver=oppdragsgiver,
        erfaring=oppdragsgivers_erfaring,
        tilbake_url=_tilbake_fra_detaljer(request, er_eier=oppdrag.er_eier),
        kan_endres=oppdrag.er_eier and oppdrag.status in REDIGERBAR,
        passert=bool(utgatt(oppdrag.tidspunkt, na=na)),
        merker=merker_lagt_ut(oppdrag.status, oppdrag.tidspunkt, na=na) if oppdrag.er_eier else (),
    )


# ---------- bildet (FR-9, FR-27, AD-18) ----------

# Bildet kan ligge i nettleserens buffer, men bare for den som allerede kunne se det
# (AD-18). `core/headere.py` beholder en `Cache-Control` som ruta har satt selv.
BILDEBUFFER = "private, max-age=31536000, immutable"


def _bildesvar(db: Session, id: int, innlogget: Innlogget, *, liten: bool) -> Response:
    _sjekk_id(id)
    data = hent_bilde(db, id, innlogget.bruker_id, liten=liten)
    return Response(data, media_type="image/jpeg", headers={"Cache-Control": BILDEBUFFER})


@router.get("/oppdrag/{id:int}/bilde", name="oppdrag.bilde", response_class=Response)
def bilde(
    id: int,
    innlogget: Innlogget = Depends(innlogget_bruker),
    db: Session = Depends(hent_db),
) -> Response:
    """Bildet i detaljene, høyst 1 600 px (FR-9, FR-27). Ingen tilgang gir samme 404 som detaljene."""
    return _bildesvar(db, id, innlogget, liten=False)


@router.get("/oppdrag/{id:int}/bilde/liten", name="oppdrag.bilde_liten", response_class=Response)
def bilde_liten(
    id: int,
    innlogget: Innlogget = Depends(innlogget_bruker),
    db: Session = Depends(hent_db),
) -> Response:
    """Miniatyren på kortet og i skjemaet, høyst 640 px (FR-9, FR-10, FR-27)."""
    return _bildesvar(db, id, innlogget, liten=True)


# ---------- redigere (FR-6, FR-8) ----------


def _tilbake_fra_redigering(request: Request, id: int) -> str:
    """`tilbake_url`, men detaljene når forrige side var skjemaet selv (etter en 422)."""
    rediger = str(request.app.url_path_for("oppdrag.rediger", id=id))
    referer = urlsplit(request.headers.get("referer", "")).path
    url = tilbake_url(request)
    if referer == rediger or urlsplit(url).path == rediger:
        return str(request.app.url_path_for("oppdrag.detaljer", id=id))
    return url


def _vis_redigering(
    request: Request,
    oppdrag: OppdragVisning,
    *,
    verdier: dict[str, str],
    fokus: str | None = None,
    feil: list[tuple[str, str]] | None = None,
    status_code: int = 200,
    bildevalg: Bildevalg = INGEN_BILDEVALG,
) -> HTMLResponse:
    """Skjemaet fra «Nytt oppdrag» uten KI, `skjema_id` og steg, med «Lagre endringer» (FR-6).

    `h1` og `<title>` har den lagrede tittelen, også ved 422 når tittelfeltet er
    endret, så siden ikke skifter navn før endringen er lagret.
    """
    sted = poststed(verdier["postnummer"]) or ""
    return render(
        request,
        "oppdrag/skjema.html",
        tittel=f"Rediger «{oppdrag.tittel}»",
        aktiv_meny="mine_oppdrag",
        underside=True,
        fokus=fokus,
        status_code=status_code,
        skjema_handling=request.app.url_path_for("oppdrag.send_rediger", id=oppdrag.id),
        knappetekst="Lagre endringer",
        skjema_id=None,
        to_steg=False,
        tilbake_url=_tilbake_fra_redigering(request, oppdrag.id),
        **_skjemakontekst(verdier, sted, feil, _bildefelt(request, bildevalg, oppdrag)),
    )


@router.get("/oppdrag/{id:int}/rediger", name="oppdrag.rediger", response_class=HTMLResponse)
def rediger(
    request: Request,
    id: int,
    innlogget: Innlogget = Depends(innlogget_bruker),
    db: Session = Depends(hent_db),
) -> HTMLResponse:
    """Skjemaet med de lagrede verdiene, også et passert tidspunkt (FR-6, FR-8).

    `?fokus=tidspunkt` gir `autofocus` på «Dato» («Endre tidspunkt»). Ellers
    flyttes ikke fokus (EXPERIENCE.md § Fokus og opplesning).
    """
    _sjekk_id(id)
    oppdrag = hent_eget_oppdrag(db, id, innlogget.bruker_id, statuser=REDIGERBAR)
    fokus = "dato" if request.query_params.get("fokus") == "tidspunkt" else None
    return _vis_redigering(request, oppdrag, verdier=skjemaverdier_for(oppdrag), fokus=fokus)


@router.post("/oppdrag/{id:int}/rediger", name="oppdrag.send_rediger", response_class=HTMLResponse)
def send_rediger(
    request: Request,
    id: int,
    innlogget: Innlogget = Depends(innlogget_bruker),
    db: Session = Depends(hent_db),
) -> Response:
    """Lagrer endringene, eller viser skjemaet igjen med alle feilene (FR-6, FR-27, NFR-5, NFR-10).

    Bildet tolkes før transaksjonen, som i `send_ny`.
    """
    _sjekk_id(id)
    skjema: dict[str, str] = request.state.skjema
    verdier = {felt: skjema.get(felt, "") for felt in SKJEMAFELT}
    valg = _bildevalg(request)
    try:
        with db.begin():
            rediger_oppdrag(
                db, id, oppdragsgiver_id=innlogget.bruker_id, bildevalg=valg, **verdier
            )
    except RegelBrudd as brudd:
        with laas_gir_konflikt(KONFLIKT, detaljer_url(id)):
            oppdrag = hent_eget_oppdrag(db, id, innlogget.bruker_id, statuser=REDIGERBAR)
        return _vis_redigering(
            request, oppdrag, verdier=verdier, feil=brudd.feil, status_code=422, bildevalg=valg
        )
    svar = RedirectResponse(request.app.url_path_for("oppdrag.detaljer", id=id), status_code=303)
    sett_kvittering(request, svar, "endringer_lagret")
    return svar


# ---------- avbryte (FR-7, UX-DR18) ----------

FRA_MINE = "mine"  # eneste godtatte verdi av `fra`; alt annet gir detaljene


def _fra(verdi: str | None) -> str | None:
    return FRA_MINE if verdi == FRA_MINE else None


@router.get("/oppdrag/{id:int}/avbryt", name="oppdrag.avbryt", response_class=HTMLResponse)
def avbryt(
    request: Request,
    id: int,
    innlogget: Innlogget = Depends(innlogget_bruker),
    db: Session = Depends(hent_db),
) -> HTMLResponse:
    """Bekreftelsessiden uten JS: «Avbryte «…»?» med «Ja, avbryt oppdraget» og «Behold oppdraget» (FR-7).

    Samme innhold som dialogen. «Behold oppdraget» går tilbake til «Mine oppdrag»
    med `fra=mine`, ellers til detaljene.
    """
    _sjekk_id(id)
    oppdrag = hent_eget_oppdrag(db, id, innlogget.bruker_id, statuser=AVBRYTBAR)
    fra = _fra(request.query_params.get("fra"))
    behold = (
        request.app.url_path_for("oppdrag.mine")
        if fra
        else request.app.url_path_for("oppdrag.detaljer", id=id)
    )
    return render(
        request,
        "oppdrag/avbryt.html",
        tittel=f"Avbryte «{oppdrag.tittel}»?",
        aktiv_meny="mine_oppdrag",
        underside=True,
        oppdrag=oppdrag,
        fra=fra,
        behold_url=str(behold),
    )


@router.post("/oppdrag/{id:int}/avbryt", name="oppdrag.send_avbryt", response_class=HTMLResponse)
def send_avbryt(
    request: Request,
    id: int,
    innlogget: Innlogget = Depends(innlogget_bruker),
    db: Session = Depends(hent_db),
) -> Response:
    """Avbryter oppdraget og gir 303 med «Oppdraget er avbrutt.» (FR-7, NFR-5).

    Til «Mine oppdrag» med `fra=mine`, ellers til detaljene. En annen eier gir
    404, og en status som ikke kan avbrytes, gir `Konflikt` til detaljene, også
    ved dobbel innsending: «bare første teller; den andre får «Oppdraget er endret.
    Last siden på nytt.»» (EXPERIENCE.md UJ-1, spec 2.5 «To faner», NFR-5).
    """
    _sjekk_id(id)
    fra = _fra(request.state.skjema.get("fra"))
    with db.begin():
        avbryt_oppdrag(db, id, oppdragsgiver_id=innlogget.bruker_id)
    til = (
        request.app.url_path_for("oppdrag.mine")
        if fra
        else request.app.url_path_for("oppdrag.detaljer", id=id)
    )
    svar = RedirectResponse(til, status_code=303)
    sett_kvittering(request, svar, "oppdrag_avbrutt")
    return svar
