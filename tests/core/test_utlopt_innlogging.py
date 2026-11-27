"""Utløpt innlogging mister ikke utfylt skjema: radene i I/O-matrisen i spec 2.6.

FR-2, FR-3, FR-27, NFR-5, NFR-10, NFR-12, AD-4, AD-5, AD-7, AD-17, UX-DR12, UX-DR27.

Klokka står fast på tirsdag 24.11.2026 kl. 13:00 norsk tid (T0). «Utløpt» betyr at
klokka stilles 7 dager fram etter innloggingen. Kari og Ola er testbrukere med de
samme e-postene som i seed. Hver test sender skjemaet med CSRF-nøkkelen, som er
uavhengig av sesjonen (AD-5). 401-skjemaet sendes som multipart, slik nettleseren
gjør med `enctype="multipart/form-data"`.
"""

from __future__ import annotations

import logging
import re
import secrets
from datetime import datetime, timedelta, timezone

import pytest
from fastapi import Depends, FastAPI, Form
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session
from starlette.requests import Request
from starlette.responses import JSONResponse

from app import lag_app
from app.core import mellomvare
from app.core.config import Settings
from app.core.csrf import MAKS_KROPP
from app.core.feil import NOE_GIKK_GALT
from app.core.mellomvare import handling_for
from app.core.sesjon import (
    FEIL_INNLOGGING,
    FOR_MANGE_FORSOK,
    Innlogget,
    innlogget_bruker,
    offentlig,
)
from app.identity.models import Innloggingsforsok, Sesjon
from app.identity.service import SKRIV_EPOST, SKRIV_PASSORD, hash_sesjonsnokkel
from app.oppdrag.bilde import behandle, til_beholdt
from app.oppdrag.models import Oppdrag, Oppdragsbilde
from app.oppdrag.service import VELG_BILDET_PA_NYTT, avbryt_oppdrag
from tests import bilder

from ..conftest import STANDARD_PASSORD
from ..oppdrag.test_legge_ut import feltfeil
from .test_render import les_side

T0 = datetime(2026, 11, 24, 12, 0, tzinfo=timezone.utc)
UTLOPT = T0 + timedelta(days=7)
KARI_EPOST = "kari@eksempel.no"
OLA_EPOST = "ola@eksempel.no"
CSRF = re.compile(r'name="csrf_token" value="([^"]+)"')
SKJEMA_ID = re.compile(r'name="skjema_id" value="([^"]+)"')
LOGG_INN_IGJEN = "<h1>Du må logge inn igjen.</h1>"
VELG_PA_NYTT_ETTER = "Velg bildet på nytt etter innlogging."
KONFLIKT = "Oppdraget er endret. Last siden på nytt."

# Gyldig «Nytt oppdrag» etter at innloggingen er utløpt (1. desember).
NYTT = {
    "beskrivelse": "Trenger noen som kan måke snø i innkjørselen min på lørdag.",
    "tittel": "Måke snø før helgen",
    "kategori": "snomaking",
    "postnummer": "0571",
    "dato": "05.12.2026",
    "klokkeslett": "7",
    "tilbud": "belop",
    "belop": "300",
}


# ---------- oppsett og hjelpere ----------


@pytest.fixture(autouse=True)
def _klokke(sett_na) -> None:
    sett_na(T0)


@pytest.fixture
def kari(lag_bruker):
    return lag_bruker(navn="Kari Nordmann", epost=KARI_EPOST)


@pytest.fixture
def ola(lag_bruker):
    return lag_bruker(navn="Ola Hansen", epost=OLA_EPOST)


@pytest.fixture
def utlopt(klient: TestClient, kari, logg_inn_som, sett_na) -> dict:
    """Kari åpner «Nytt oppdrag», og innloggingen utløper mens hun skriver.

    Gir CSRF-nøkkelen, `skjema_id` og den gamle sesjonsnøkkelen.
    """
    gammel = logg_inn_som(klient, kari)
    html = klient.get("/oppdrag/ny").text
    sett_na(UTLOPT)
    return {"csrf": CSRF.search(html).group(1), "skjema_id": SKJEMA_ID.search(html).group(1), "gammel": gammel}


def bare_gammel_sesjon(klient: TestClient, gammel: str) -> None:
    """Klienten har bare den utløpte sesjonen igjen (den nye fra 401-siden fjernes)."""
    klient.cookies.delete("sesjon")
    klient.cookies.set("sesjon", gammel)


def multipart(felt: list[tuple[str, str]], filer: list[tuple[str, str, bytes]] = ()) -> tuple[bytes, str]:
    """Kroppen og `Content-Type` for et multipart-skjema, slik nettleseren sender det."""
    grense = "testgrense" + secrets.token_hex(8)
    deler = []
    for navn, verdi in felt:
        deler.append(
            f'--{grense}\r\nContent-Disposition: form-data; name="{navn}"\r\n\r\n'.encode()
            + verdi.encode("utf-8") + b"\r\n"
        )
    for navn, filnavn, data in filer:
        deler.append(
            f'--{grense}\r\nContent-Disposition: form-data; name="{navn}"; filename="{filnavn}"\r\n'
            f"Content-Type: image/jpeg\r\n\r\n".encode() + data + b"\r\n"
        )
    deler.append(f"--{grense}--\r\n".encode())
    return b"".join(deler), f"multipart/form-data; boundary={grense}"


def send_multipart(klient: TestClient, sti: str, felt, filer=()):
    kropp, type_ = multipart(list(felt.items()) if isinstance(felt, dict) else list(felt), list(filer))
    return klient.post(sti, content=kropp, headers={"Content-Type": type_}, follow_redirects=False)


def send_nytt(klient: TestClient, utlopt: dict, *, filer=(), **endringer: str):
    """Den opprinnelige innsendingen av «Nytt oppdrag», som multipart."""
    felt = {"csrf_token": utlopt["csrf"], "skjema_id": utlopt["skjema_id"], **NYTT, **endringer}
    return send_multipart(klient, "/oppdrag/ny", felt, filer)


def skjemaet(html: str) -> dict:
    return next(a for t, a in les_side(html).tagger if t == "form")


def skjulte_felt(html: str) -> list[tuple[str, str]]:
    return [(a["name"], a.get("value", "")) for t, a in les_side(html).tagger
            if t == "input" and a.get("type") == "hidden"]


def input_med_id(html: str, id_: str) -> dict:
    return next(a for t, a in les_side(html).tagger if t == "input" and a.get("id") == id_)


def logg_inn_pa_401(klient: TestClient, html: str, epost: str, passord: str):
    """Sender 401-skjemaet med de skjulte feltene og innloggingen, til `action`."""
    felt = [*skjulte_felt(html), ("_innlogging_epost", epost), ("_innlogging_passord", passord)]
    return send_multipart(klient, skjemaet(html)["action"], felt)


def sesjonscookie(svar) -> str | None:
    for cookie in svar.headers.get_list("set-cookie"):
        if cookie.startswith("sesjon="):
            return cookie
    return None


def antall(db: Session, modell, *vilkar) -> int:
    db.expire_all()
    return db.scalar(select(func.count()).select_from(modell).where(*vilkar))


def oppdrag_med_tittel(db: Session, tittel: str) -> list[Oppdrag]:
    db.expire_all()
    return list(db.scalars(select(Oppdrag).where(Oppdrag.tittel == tittel)))


# ---------- 401-siden ----------


def test_401_siden_har_feltene_som_skjulte_felt(klient: TestClient, db, utlopt) -> None:
    """AD-7, FR-3: 401 med alle tekstfelt skjult, CSRF én gang, «E-post» i fokus og ingen meny."""
    for_ = antall(db, Oppdrag)
    felt = {"csrf_token": utlopt["csrf"], "skjema_id": utlopt["skjema_id"], **NYTT,
            "bildetekst": "", "fjern_bilde": ""}
    svar = send_multipart(klient, "/oppdrag/ny?fra=mine", felt)
    assert svar.status_code == 401
    html = svar.text
    assert LOGG_INN_IGJEN in html
    assert "<title>Du må logge inn igjen – Nabolagshelten</title>" in html

    skjulte = skjulte_felt(html)
    forventet = [(n, v) for n, v in felt.items() if n != "csrf_token"]
    assert [f for f in skjulte if f[0] != "csrf_token"] == forventet  # samme navn, verdi og rekkefølge
    assert [v for n, v in skjulte if n == "csrf_token"] == [utlopt["csrf"]]

    skjema = skjemaet(html)
    assert skjema["method"] == "post"
    assert skjema["enctype"] == "multipart/form-data"
    assert skjema["action"] == "/oppdrag/ny?fra=mine"
    assert "novalidate" in skjema

    epost = input_med_id(html, "innlogging-epost")
    assert (epost["name"], epost["type"], epost["autocomplete"]) == ("_innlogging_epost", "email", "email")
    assert "autofocus" in epost and epost["value"] == ""
    passord = input_med_id(html, "innlogging-passord")
    assert (passord["name"], passord["type"], passord["autocomplete"]) == (
        "_innlogging_passord", "password", "current-password")
    assert "value" not in passord
    assert html.count("autofocus") == 1
    assert '<label for="innlogging-epost">E-post</label>' in html
    assert '<label for="innlogging-passord">Passord</label>' in html
    assert 'aria-controls="innlogging-passord" data-vis-passord hidden>Vis passord</button>' in html
    assert '<button class="knapp knapp--primar" type="submit">Logg inn</button>' in html
    assert VELG_PA_NYTT_ETTER not in html

    assert "<nav" not in html and "Kari Nordmann" not in html
    assert svar.headers.get_list("cache-control") == ["no-store"]
    assert sesjonscookie(svar) is None
    assert antall(db, Oppdrag) == for_


def test_unntatte_felt_blir_ikke_skjulte_felt(klient: TestClient, utlopt) -> None:
    """AD-7: `passord`, `csrf_token` og `_`-felt står ikke som skjulte felt. E-posten står bare synlig."""
    svar = send_nytt(klient, utlopt, passord="hemmelig-1", _innlogging_epost="kari@eksempel.no",
                     _annet="x")
    assert svar.status_code == 401
    navn = [n for n, _ in skjulte_felt(svar.text)]
    assert "passord" not in navn
    assert navn.count("csrf_token") == 1
    assert not [n for n in navn if n.startswith("_")]
    assert "hemmelig-1" not in svar.text
    assert svar.text.count('name="_innlogging_epost"') == 1
    assert input_med_id(svar.text, "innlogging-epost")["value"] == "kari@eksempel.no"
    # Bare `_innlogging_`-feltene på siden begynner med `_`.
    assert set(re.findall(r'name="(_[^"]*)"', svar.text)) == {"_innlogging_epost", "_innlogging_passord"}


def test_tittelen_vises_som_tekst(klient: TestClient, utlopt) -> None:
    """NFR-12: `"><script>` i tittelen står escapet i `value`."""
    farlig = '"><script>alert(1)</script>'
    svar = send_nytt(klient, utlopt, tittel=farlig)
    assert svar.status_code == 401
    assert "<script>alert(1)</script>" not in svar.text
    assert 'value="&#34;&gt;&lt;script&gt;alert(1)&lt;/script&gt;"' in svar.text
    assert ("tittel", farlig) in skjulte_felt(svar.text)


# ---------- innlogging på 401-siden ----------


def test_riktig_innlogging_legger_ut_oppdraget(klient: TestClient, db, kari, utlopt) -> None:
    """FR-2, AD-7: 303 til detaljene med kvitteringen, ett oppdrag med Kari som eier og ny sesjon."""
    side = send_nytt(klient, utlopt).text
    # Et mislykket forsøk først, som skal ryddes ved vellykket innlogging (AD-4).
    side = logg_inn_pa_401(klient, side, KARI_EPOST, "feil-passord").text
    assert antall(db, Innloggingsforsok, Innloggingsforsok.epost == KARI_EPOST) == 1

    svar = logg_inn_pa_401(klient, side, KARI_EPOST, STANDARD_PASSORD)
    assert svar.status_code == 303
    (oppdrag,) = oppdrag_med_tittel(db, NYTT["tittel"])
    assert oppdrag.oppdragsgiver_id == kari.id
    assert svar.headers["location"] == f"/oppdrag/{oppdrag.id}"

    cookie = sesjonscookie(svar)
    assert cookie is not None
    for attributt in ("httponly", "samesite=lax", "path=/", "max-age=604800"):
        assert attributt in cookie.lower(), attributt
    assert "secure" not in cookie.lower()
    ny = re.match(r"sesjon=([^;]+)", cookie).group(1)
    assert antall(db, Sesjon, Sesjon.nokkel == hash_sesjonsnokkel(ny)) == 1
    assert antall(db, Sesjon, Sesjon.nokkel == hash_sesjonsnokkel(utlopt["gammel"])) == 0
    assert antall(db, Innloggingsforsok, Innloggingsforsok.epost == KARI_EPOST) == 0

    detaljer = klient.get(svar.headers["location"])
    assert detaljer.status_code == 200
    assert "Oppdraget er lagt ut." in detaljer.text


def test_ruta_ser_ikke_innloggingen(app: FastAPI, klient: TestClient, kari, utlopt) -> None:
    """AD-5, AD-7: `request.state.skjema`, `request.form()` og `Form()` har ikke `_innlogging_*`.

    Cookien i forespørselen er den nye nøkkelen, og ruta får Kari som innlogget.
    """

    @app.post("/_test/utlopt-skjema")
    async def skjema_rute(request: Request, innlogget: Innlogget = Depends(innlogget_bruker)) -> JSONResponse:
        form = await request.form()
        return JSONResponse({
            "state": request.state.skjema,
            "form": {k: v for k, v in form.multi_items() if isinstance(v, str)},
            "cookie": request.cookies.get("sesjon"),
            "bruker_id": innlogget.bruker_id,
            "state_bruker_id": request.state.innlogget.bruker_id,
        })

    @app.post("/_test/utlopt-form")
    def form_rute(
        navn: str = Form(),
        passord: str | None = Form(None, alias="_innlogging_passord"),
        innlogget: Innlogget = Depends(innlogget_bruker),
    ) -> JSONResponse:
        return JSONResponse({"navn": navn, "passord": passord, "bruker_id": innlogget.bruker_id})

    felt = {"csrf_token": utlopt["csrf"], "navn": "Kari Ås", "notat": "æøå & = +"}
    side = send_multipart(klient, "/_test/utlopt-skjema", felt)
    assert side.status_code == 401
    svar = logg_inn_pa_401(klient, side.text, KARI_EPOST, STANDARD_PASSORD)
    assert svar.status_code == 200
    data = svar.json()
    assert data["state"] == felt
    assert data["form"] == felt
    assert data["cookie"] == re.match(r"sesjon=([^;]+)", sesjonscookie(svar)).group(1)
    assert data["cookie"] != utlopt["gammel"]
    assert data["bruker_id"] == data["state_bruker_id"] == kari.id

    bare_gammel_sesjon(klient, utlopt["gammel"])  # utløpt igjen
    side = send_multipart(klient, "/_test/utlopt-form", felt)
    assert side.status_code == 401
    svar = logg_inn_pa_401(klient, side.text, KARI_EPOST, STANDARD_PASSORD)
    assert svar.json() == {"navn": "Kari Ås", "passord": None, "bruker_id": kari.id}


def test_annen_bruker_far_samme_404_og_legger_ut_som_seg_selv(
    klient: TestClient, db, kari, ola, utlopt, lag_oppdrag
) -> None:
    """AD-7: Ola logger inn på 401-siden. Tilgangsreglene gjelder for Ola, og Ola er innlogget etterpå."""
    karis = lag_oppdrag(oppdragsgiver=kari, tittel="Karis oppdrag", tidspunkt=T0 + timedelta(days=10))
    felt = {"csrf_token": utlopt["csrf"], **NYTT, "tittel": "Endret av Ola"}
    side = send_multipart(klient, f"/oppdrag/{karis.id}/rediger", felt)
    assert side.status_code == 401
    svar = logg_inn_pa_401(klient, side.text, OLA_EPOST, STANDARD_PASSORD)
    assert svar.status_code == 404
    assert sesjonscookie(svar) is not None
    db.expire_all()
    assert db.get(Oppdrag, karis.id).tittel == "Karis oppdrag"
    assert klient.get("/profil").status_code == 200  # Ola er innlogget

    bare_gammel_sesjon(klient, utlopt["gammel"])
    side = send_nytt(klient, utlopt)
    svar = logg_inn_pa_401(klient, side.text, OLA_EPOST, STANDARD_PASSORD)
    assert svar.status_code == 303
    (oppdrag,) = oppdrag_med_tittel(db, NYTT["tittel"])
    assert oppdrag.oppdragsgiver_id == ola.id


@pytest.mark.parametrize("epost", [KARI_EPOST, "ukjent@eksempel.no"], ids=["feil-passord", "ukjent-epost"])
def test_feil_passord_gir_401_igjen(klient: TestClient, db, utlopt, epost: str) -> None:
    """FR-2: «Feil e-post eller passord.» i oppsummeringen, e-posten beholdt og passordet tomt."""
    forste = send_nytt(klient, utlopt).text
    svar = logg_inn_pa_401(klient, forste, epost, "feil-passord")
    assert svar.status_code == 401
    html = svar.text
    assert LOGG_INN_IGJEN in html
    assert "<title>Feil: Du må logge inn igjen – Nabolagshelten</title>" in html
    assert f'<li><a href="#innlogging-epost">{FEIL_INNLOGGING}</a></li>' in html
    assert 'id="feiloppsummering" tabindex="-1" autofocus' in html
    assert html.count("autofocus") == 1
    assert '<p class="hjelpetekst" id="innlogging-passord-hjelp">Skriv passordet på nytt.</p>' in html
    passord = input_med_id(html, "innlogging-passord")
    assert passord["aria-describedby"] == "innlogging-passord-hjelp" and "value" not in passord
    assert input_med_id(html, "innlogging-epost")["value"] == epost
    assert skjulte_felt(html) == skjulte_felt(forste)
    assert antall(db, Innloggingsforsok, Innloggingsforsok.epost == epost) == 1
    assert sesjonscookie(svar) is None
    assert oppdrag_med_tittel(db, NYTT["tittel"]) == []


@pytest.mark.parametrize(
    ("epost", "passord", "forventet"),
    [
        ("", STANDARD_PASSORD, [("epost", SKRIV_EPOST)]),
        ("   ", STANDARD_PASSORD, [("epost", SKRIV_EPOST)]),
        (KARI_EPOST, "", [("passord", SKRIV_PASSORD)]),
        (KARI_EPOST, "   ", [("passord", SKRIV_PASSORD)]),
        ("", "", [("epost", SKRIV_EPOST), ("passord", SKRIV_PASSORD)]),
    ],
)
def test_tomme_felt_gir_feil_ved_feltene(klient: TestClient, db, utlopt, epost, passord, forventet) -> None:
    """FR-2, UX-DR12: tomme felt gir feil ved feltene og telles ikke."""
    forste = send_nytt(klient, utlopt).text
    svar = logg_inn_pa_401(klient, forste, epost, passord)
    assert svar.status_code == 401
    html = svar.text
    for felt, melding in forventet:
        assert feltfeil(html, f"innlogging-{felt}") == melding
        assert input_med_id(html, f"innlogging-{felt}")["aria-invalid"] == "true"
        assert f'<li><a href="#innlogging-{felt}">{melding}</a></li>' in html
    assert antall(db, Innloggingsforsok) == 0
    assert skjulte_felt(html) == skjulte_felt(forste)


def test_sperre_gjelder_innloggingssiden_og_401_siden_sammen(klient: TestClient, db, utlopt) -> None:
    """FR-2, AD-4: 5 feil på 15 minutter, på `/logg-inn` og 401-siden til sammen, gir sperre."""
    side = send_nytt(klient, utlopt).text
    for _ in range(2):
        svar = klient.post("/logg-inn", data={"csrf_token": utlopt["csrf"], "epost": KARI_EPOST,
                                              "passord": "feil"}, follow_redirects=False)
        assert svar.status_code == 422
    for _ in range(3):
        side = logg_inn_pa_401(klient, side, KARI_EPOST, "feil").text
    svar = logg_inn_pa_401(klient, side, KARI_EPOST, STANDARD_PASSORD)
    assert svar.status_code == 401
    assert FOR_MANGE_FORSOK in svar.text
    assert ("tittel", NYTT["tittel"]) in skjulte_felt(svar.text)
    assert sesjonscookie(svar) is None
    assert oppdrag_med_tittel(db, NYTT["tittel"]) == []


def test_gyldig_sesjon_ignorerer_innloggingsfeltene(klient: TestClient, db, kari, utlopt, logg_inn_som) -> None:
    """AD-7: Kari har logget inn i en annen fane. Ingen innlogging og ingen passordsjekk."""
    side = send_nytt(klient, utlopt).text
    logg_inn_som(klient, kari)  # ny sesjon i en annen fane
    svar = logg_inn_pa_401(klient, side, OLA_EPOST, "feil-passord")
    assert svar.status_code == 303
    assert sesjonscookie(svar) is None
    (oppdrag,) = oppdrag_med_tittel(db, NYTT["tittel"])
    assert oppdrag.oppdragsgiver_id == kari.id
    assert antall(db, Innloggingsforsok) == 0


def test_offentlige_ruter_ignorerer_innloggingsfeltene(app: FastAPI, klient: TestClient, db, kari) -> None:
    """AD-7: `_innlogging_*` sendt til en offentlig rute fjernes og ignoreres."""

    @app.post("/_test/utlopt-offentlig")
    @offentlig
    async def ekko(request: Request) -> JSONResponse:
        form = await request.form()
        return JSONResponse({"state": request.state.skjema, "form": dict(form)})

    html = klient.get("/logg-inn").text
    csrf = CSRF.search(html).group(1)
    innlogging = {"_innlogging_epost": KARI_EPOST, "_innlogging_passord": STANDARD_PASSORD,
                  "_innlogging_fil": "bilde"}
    svar = klient.post("/_test/utlopt-offentlig", data={"csrf_token": csrf, "x": "1", **innlogging})
    assert svar.json() == {"state": {"csrf_token": csrf, "x": "1"}, "form": {"csrf_token": csrf, "x": "1"}}
    assert sesjonscookie(svar) is None

    svar = klient.post("/registrer", data={"csrf_token": csrf, **innlogging}, follow_redirects=False)
    assert svar.status_code == 422
    assert "_innlogging" not in svar.text

    svar = klient.post("/logg-inn", data={"csrf_token": csrf, "epost": KARI_EPOST, "passord": STANDARD_PASSORD,
                                          "_innlogging_epost": OLA_EPOST, "_innlogging_passord": "feil"},
                       follow_redirects=False)
    assert svar.status_code == 303
    assert antall(db, Innloggingsforsok) == 0


# ---------- bilde (FR-27, AD-18) ----------


def test_nytt_bilde_ma_velges_pa_nytt(klient: TestClient, db, utlopt) -> None:
    """FR-27, AD-7: teksten over «Logg inn», ingen filfelt, merket `_innlogging_fil`, og 422 etter innlogging."""
    svar = send_nytt(klient, utlopt, bildetekst="Snø i innkjørselen",
                     filer=[("bilde", "bilde.jpg", bilder.jpeg())])
    assert svar.status_code == 401
    html = svar.text
    assert 'type="file"' not in html
    assert ("_innlogging_fil", "bilde") in skjulte_felt(html)
    assert re.search(
        rf'<p class="hjelpetekst">{VELG_PA_NYTT_ETTER}</p>\s*<div class="skjema__knapper">\s*'
        r'<button class="knapp knapp--primar" type="submit">Logg inn</button>', html)

    feil = logg_inn_pa_401(klient, html, KARI_EPOST, "feil-passord")
    assert feil.status_code == 401
    assert VELG_PA_NYTT_ETTER in feil.text
    assert ("_innlogging_fil", "bilde") in skjulte_felt(feil.text)

    svar = logg_inn_pa_401(klient, feil.text, KARI_EPOST, STANDARD_PASSORD)
    assert svar.status_code == 422
    assert sesjonscookie(svar) is not None
    assert feltfeil(svar.text, "bilde") == VELG_BILDET_PA_NYTT
    assert 'value="Snø i innkjørselen"' in svar.text
    assert oppdrag_med_tittel(db, NYTT["tittel"]) == []
    assert "_innlogging" not in svar.text


def test_tapt_bilde_beholder_et_gyldig_beholdt_bilde(klient: TestClient, db, utlopt) -> None:
    """FR-27: «Velg bildet på nytt.» ved bildet, og et gyldig `bilde_beholdt` vises med «Fjern bildet»."""
    beholdt = til_beholdt(behandle(bilder.jpeg(800, 600)))
    side = send_nytt(klient, utlopt, bilde_beholdt=beholdt, bildetekst="Snø i innkjørselen",
                     filer=[("bilde", "nytt.jpg", bilder.png())])
    svar = logg_inn_pa_401(klient, side.text, KARI_EPOST, STANDARD_PASSORD)
    assert svar.status_code == 422
    assert feltfeil(svar.text, "bilde") == VELG_BILDET_PA_NYTT
    assert "Fjern bildet" in svar.text
    assert 'name="bilde_beholdt"' in svar.text
    assert oppdrag_med_tittel(db, NYTT["tittel"]) == []


def test_beholdt_bilde_folger_med_og_lagres(klient: TestClient, db, utlopt) -> None:
    """AD-7, AD-18: `bilde_beholdt` (over 1 MB som base64) er et skjult felt, gir ikke 413 og lagres."""
    beholdt = til_beholdt(behandle(bilder.stoy_jpeg(1450, 1450)))
    assert len(beholdt) > MAKS_KROPP  # ville gitt 413 som urlencoded
    side = send_nytt(klient, utlopt, bilde_beholdt=beholdt, bildetekst="Snø i innkjørselen")
    assert side.status_code == 401
    assert ("bilde_beholdt", beholdt) in skjulte_felt(side.text)
    assert VELG_PA_NYTT_ETTER not in side.text
    svar = logg_inn_pa_401(klient, side.text, KARI_EPOST, STANDARD_PASSORD)
    assert svar.status_code == 303
    (oppdrag,) = oppdrag_med_tittel(db, NYTT["tittel"])
    bilde = db.get(Oppdragsbilde, oppdrag.id)
    assert bilde is not None and bilde.bildetekst == "Snø i innkjørselen"


# ---------- invarianter fra 1.2, 2.1, 2.5 og 2.7 (T-6) ----------


def test_invariant_1_2_get_og_fragment_er_uendret(klient: TestClient, db, utlopt) -> None:
    """FR-3, AD-4: GET gir 303 med `neste`, og `X-Fragment` gir fragmentet uten innlogging."""
    svar = klient.get("/oppdrag/ny?x=1", follow_redirects=False)
    assert svar.status_code == 303
    assert svar.headers["location"] == "/logg-inn?neste=/oppdrag/ny%3Fx%3D1"

    svar = klient.post(
        "/oppdrag/ny",
        data={"csrf_token": utlopt["csrf"], "_innlogging_epost": KARI_EPOST,
              "_innlogging_passord": STANDARD_PASSORD},
        headers={"X-Fragment": "1"},
        follow_redirects=False,
    )
    assert svar.status_code == 401
    assert "<html" not in svar.text
    assert 'href="/logg-inn?neste=/oppdrag/ny"' in svar.text
    assert sesjonscookie(svar) is None
    assert antall(db, Innloggingsforsok) == 0


def test_utlogging_uten_gyldig_sesjon(klient: TestClient, db, utlopt) -> None:
    """AD-4, FR-2: `/logg-ut` er offentlig. Cookien slettes, og innloggingssiden sier «Du er logget ut.»."""
    svar = klient.post("/logg-ut", data={"csrf_token": utlopt["csrf"]}, follow_redirects=False)
    assert svar.status_code == 303
    assert svar.headers["location"] == "/logg-inn"
    assert "max-age=0" in sesjonscookie(svar).lower()
    assert "Du er logget ut." in klient.get("/logg-inn").text
    # CSRF gjelder fortsatt (AD-5).
    assert klient.post("/logg-ut", data={"csrf_token": "feil"}).status_code == 403


def test_invariant_2_1_dobbel_innsending_gir_ett_oppdrag(klient: TestClient, db, utlopt) -> None:
    """AD-2, NFR-5: `skjema_id` følger med, så andre innsending gir `Duplikat` til oppdraget som finnes."""
    side = send_nytt(klient, utlopt).text
    forste = logg_inn_pa_401(klient, side, KARI_EPOST, STANDARD_PASSORD)
    assert forste.status_code == 303
    andre = logg_inn_pa_401(klient, side, KARI_EPOST, STANDARD_PASSORD)  # 401-skjemaet på nytt
    assert andre.status_code == 303
    assert andre.headers["location"] == forste.headers["location"]
    originalen = send_nytt(klient, utlopt)  # originalen på nytt, nå innlogget
    assert originalen.status_code == 303
    assert originalen.headers["location"] == forste.headers["location"]
    assert len(oppdrag_med_tittel(db, NYTT["tittel"])) == 1


def test_invariant_2_5_konflikt_og_avbrudd_via_401(
    klient: TestClient, db, kari, utlopt, lag_oppdrag
) -> None:
    """AD-2, FR-7: avbrutt i en annen fane gir `Konflikt` med ny sesjon. Avbrudd via 401 virker."""
    oppdrag = lag_oppdrag(oppdragsgiver=kari, tittel="Avbrytes", tidspunkt=T0 + timedelta(days=10))
    side = send_multipart(klient, f"/oppdrag/{oppdrag.id}/avbryt", {"csrf_token": utlopt["csrf"], "fra": "mine"})
    assert side.status_code == 401
    avbryt_oppdrag(db, oppdrag.id, oppdragsgiver_id=kari.id)  # i en annen fane
    db.commit()
    svar = logg_inn_pa_401(klient, side.text, KARI_EPOST, STANDARD_PASSORD)
    assert svar.status_code == 303
    assert svar.headers["location"] == f"/oppdrag/{oppdrag.id}"
    assert sesjonscookie(svar) is not None
    assert KONFLIKT in klient.get(svar.headers["location"]).text

    annet = lag_oppdrag(oppdragsgiver=kari, tittel="Avbrytes via 401", tidspunkt=T0 + timedelta(days=10))
    bare_gammel_sesjon(klient, utlopt["gammel"])
    side = send_multipart(klient, f"/oppdrag/{annet.id}/avbryt", {"csrf_token": utlopt["csrf"], "fra": "mine"})
    svar = logg_inn_pa_401(klient, side.text, KARI_EPOST, STANDARD_PASSORD)
    assert svar.status_code == 303
    assert svar.headers["location"] == "/mine-oppdrag"
    assert "Oppdraget er avbrutt." in klient.get("/mine-oppdrag").text
    db.expire_all()
    assert db.get(Oppdrag, annet.id).status == "avbrutt"


def test_invariant_2_7_csrf_for_sesjon_og_bilde_krever_innlogging(
    klient: TestClient, db, kari, utlopt, lag_oppdrag, lag_bilde
) -> None:
    """AD-5, AD-18: multipart med fil uten CSRF gir 403, og bildet gir 303 uten sesjon."""
    oppdrag = lag_oppdrag(oppdragsgiver=kari)
    lag_bilde(oppdrag)
    felt = {"skjema_id": utlopt["skjema_id"], **NYTT}
    svar = send_multipart(klient, "/oppdrag/ny", felt, [("bilde", "bilde.jpg", bilder.jpeg())])
    assert svar.status_code == 403
    svar = klient.get(f"/oppdrag/{oppdrag.id}/bilde", follow_redirects=False)
    assert svar.status_code == 303
    assert svar.headers["location"].startswith("/logg-inn?neste=")


# ---------- etter gjennomgang: produksjon, feil i databasen, adressen og logging ----------


def test_sesjonscookien_er_secure_i_produksjon_etter_401(sesjonsfabrikk, kari, logg_inn_som, sett_na) -> None:
    """AD-4, AD-14: cookien som mellomvaren setter etter innlogging på 401-siden, er `Secure` i produksjon."""
    settings = Settings(
        _env_file=None, app_env="production", secret_key="x" * 32,
        database_url="postgresql+psycopg://u@localhost/d",
    )
    app = lag_app(settings=settings)
    app.state.sesjonsfabrikk = sesjonsfabrikk
    with TestClient(app, base_url="https://testserver") as klient:
        logg_inn_som(klient, kari)
        html = klient.get("/oppdrag/ny").text
        sett_na(UTLOPT)
        utlopt = {"csrf": CSRF.search(html).group(1), "skjema_id": SKJEMA_ID.search(html).group(1)}
        side = send_nytt(klient, utlopt)
        assert side.status_code == 401
        svar = logg_inn_pa_401(klient, side.text, KARI_EPOST, STANDARD_PASSORD)
    assert svar.status_code == 303
    assert "secure" in sesjonscookie(svar).lower()


def test_feil_i_databasen_ved_innlogging_beholder_skjemaet(
    klient: TestClient, db, utlopt, monkeypatch, caplog
) -> None:
    """AD-7, NFR-10: «database is locked» under innloggingen gir 401-siden igjen med feltene, ikke 500."""

    def last(*args, **kwargs):
        raise OperationalError("BEGIN IMMEDIATE", {}, Exception("database is locked"))

    side = send_nytt(klient, utlopt).text
    monkeypatch.setattr(mellomvare, "prov_innlogging", last)
    with caplog.at_level(logging.ERROR, logger="app.core.mellomvare"):
        svar = logg_inn_pa_401(klient, side, KARI_EPOST, STANDARD_PASSORD)
    assert svar.status_code == 401
    assert f'<li><a href="#innlogging-epost">{NOE_GIKK_GALT}</a></li>' in svar.text
    assert skjulte_felt(svar.text) == skjulte_felt(side)
    assert input_med_id(svar.text, "innlogging-epost")["value"] == KARI_EPOST
    assert sesjonscookie(svar) is None
    assert oppdrag_med_tittel(db, NYTT["tittel"]) == []
    assert any(post.exc_info for post in caplog.records)
    assert STANDARD_PASSORD not in caplog.text and KARI_EPOST not in caplog.text


def test_ny_sesjon_som_ikke_finnes_gir_feilmelding(
    app: FastAPI, klient: TestClient, db, utlopt, monkeypatch, caplog
) -> None:
    """AD-7: finnes ikke den nye sesjonen igjen, vises 401-siden med «Feil e-post eller passord.» og feltene."""
    side = send_nytt(klient, utlopt).text
    monkeypatch.setattr(app.state.autentisering, "finn_innlogget", lambda request: None)
    with caplog.at_level(logging.WARNING, logger="app.core.mellomvare"):
        svar = logg_inn_pa_401(klient, side, KARI_EPOST, STANDARD_PASSORD)
    assert svar.status_code == 401
    assert f'<li><a href="#innlogging-epost">{FEIL_INNLOGGING}</a></li>' in svar.text
    assert skjulte_felt(svar.text) == skjulte_felt(side)
    assert sesjonscookie(svar) is None
    assert oppdrag_med_tittel(db, NYTT["tittel"]) == []
    assert caplog.records
    assert STANDARD_PASSORD not in caplog.text and KARI_EPOST not in caplog.text


@pytest.mark.parametrize(
    ("sti", "sporring", "forventet"),
    [
        ("/oppdrag/ny", "", "/oppdrag/ny"),
        ("/oppdrag/ny", "fra=mine", "/oppdrag/ny?fra=mine"),
        ("/\\evil.no", "", "/%5Cevil.no"),  # %5C dekodet
        ("//evil.no", "", "/evil.no"),
        ("/a?b", "x=1", "/a%3Fb?x=1"),  # %3F dekodet
        ("/a b#c", "", "/a%20b%23c"),
    ],
)
def test_handling_kodes_pa_nytt_og_har_en_skrastrek(sti: str, sporring: str, forventet: str) -> None:
    """AD-7: `action` er samme adresse, kodet på nytt, så nettleseren aldri leser den som en annen vert."""
    assert handling_for(sti, sporring) == forventet


def test_passord_og_epost_logges_aldri(klient: TestClient, utlopt, caplog) -> None:
    """Konvensjonen Logging, NFR-9: verken passord eller e-post havner i loggen."""
    with caplog.at_level(logging.DEBUG):
        side = send_nytt(klient, utlopt).text
        feil = logg_inn_pa_401(klient, side, KARI_EPOST, "feil-passord-123")
        assert feil.status_code == 401
        svar = logg_inn_pa_401(klient, feil.text, KARI_EPOST, STANDARD_PASSORD)
        assert svar.status_code == 303
    for hemmelig in ("feil-passord-123", STANDARD_PASSORD, KARI_EPOST):
        assert hemmelig not in caplog.text


# ---------- redigering via 401-siden (FR-6, FR-27) ----------


def test_redigering_via_401_lagres(klient: TestClient, db, kari, utlopt, lag_oppdrag) -> None:
    """FR-6, AD-7: Kari redigerer sitt eget oppdrag, innloggingen utløper, og endringene lagres etter innlogging."""
    oppdrag = lag_oppdrag(oppdragsgiver=kari, tittel="Gammel tittel", tidspunkt=T0 + timedelta(days=10))
    side = send_multipart(klient, f"/oppdrag/{oppdrag.id}/rediger", {"csrf_token": utlopt["csrf"], **NYTT})
    assert side.status_code == 401
    svar = logg_inn_pa_401(klient, side.text, KARI_EPOST, STANDARD_PASSORD)
    assert svar.status_code == 303
    assert svar.headers["location"] == f"/oppdrag/{oppdrag.id}"
    db.expire_all()
    lagret = db.get(Oppdrag, oppdrag.id)
    assert (lagret.tittel, lagret.belop) == (NYTT["tittel"], 300)
    assert "Endringene er lagret." in klient.get(svar.headers["location"]).text


def test_tapt_bilde_ved_redigering_beholder_det_lagrede(
    klient: TestClient, db, kari, utlopt, lag_oppdrag, lag_bilde
) -> None:
    """FR-27, AD-7: et nytt bilde som gikk tapt ved redigering, gir 422 med «Velg bildet på nytt.»,
    og det lagrede bildet og oppdraget er uendret."""
    oppdrag = lag_oppdrag(oppdragsgiver=kari, tittel="Gammel tittel", tidspunkt=T0 + timedelta(days=10))
    lag_bilde(oppdrag)
    db.expire_all()
    for_ = db.get(Oppdragsbilde, oppdrag.id).bilde
    felt = {"csrf_token": utlopt["csrf"], **NYTT, "bildetekst": "Snødekt innkjørsel med en spade"}
    side = send_multipart(klient, f"/oppdrag/{oppdrag.id}/rediger", felt,
                          [("bilde", "nytt.jpg", bilder.png())])
    assert side.status_code == 401
    assert VELG_PA_NYTT_ETTER in side.text
    svar = logg_inn_pa_401(klient, side.text, KARI_EPOST, STANDARD_PASSORD)
    assert svar.status_code == 422
    assert feltfeil(svar.text, "bilde") == VELG_BILDET_PA_NYTT
    db.expire_all()
    assert db.get(Oppdragsbilde, oppdrag.id).bilde == for_
    assert db.get(Oppdrag, oppdrag.id).tittel == "Gammel tittel"
