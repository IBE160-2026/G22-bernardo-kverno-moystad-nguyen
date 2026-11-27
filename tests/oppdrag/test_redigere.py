"""Redigere oppdrag over HTTP: radene i I/O-matrisen i spec 2.5 om redigering.

FR-6, FR-8, NFR-5, NFR-10, NFR-12, AD-2, AD-3, UX-DR7, UX-DR22, UX-DR27, §4.0. Klokka
står fast på tirsdag 24.11.2026 kl. 13:00 norsk tid, og databasen har testbrukerne og
eksempeloppdragene fra seed: Kari eier «Måke snø i innkjørselen» (Åpen, i morgen kl.
09:00, 200 kr) og det utgåtte «Bære ved opp til tredje etasje». Ola bor i 0571.
Også `Konflikt`-handleren med feilmeldingen og «Last siden på nytt», og at «Tilbake» i
detaljene aldri går til skjemaet (invariant 2.3/2.4).
"""

from __future__ import annotations

import re
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import seed
from app.identity.models import Bruker
from app.oppdrag.models import Oppdrag

from ..core.test_render import les_side
from .test_grunnsider import menyvalg
from .test_legge_ut import attrs, feltfeil

T0 = datetime(2026, 11, 24, 12, 0, tzinfo=timezone.utc)
MAKE = "Måke snø i innkjørselen"
BAERE = "Bære ved opp til tredje etasje"
KONFLIKT = "Oppdraget er endret. Last siden på nytt."
CSRF = re.compile(r'name="csrf_token" value="([^"]+)"')


@pytest.fixture(autouse=True)
def eksempeldata(db: Session, sett_na) -> None:
    sett_na(T0)
    seed.last_eksempeldata(db)
    db.commit()


def hent_testbruker(db: Session, navn: str) -> Bruker:
    return db.scalars(select(Bruker).where(Bruker.epost == f"{navn}@eksempel.no")).one()


def oppdrag_med_tittel(db: Session, tittel: str) -> Oppdrag:
    db.expire_all()
    return db.scalars(select(Oppdrag).where(Oppdrag.tittel == tittel)).one()


def les(db: Session, oppdrag_id: int) -> Oppdrag:
    db.expire_all()
    return db.scalars(select(Oppdrag).where(Oppdrag.id == oppdrag_id)).one()


@pytest.fixture
def som(klient: TestClient, db: Session, logg_inn_som):
    def _som(navn: str) -> TestClient:
        klient.cookies.clear()
        logg_inn_som(klient, hent_testbruker(db, navn))
        return klient

    return _som


@pytest.fixture
def make(db: Session) -> Oppdrag:
    return oppdrag_med_tittel(db, MAKE)


@pytest.fixture
def baere(db: Session) -> Oppdrag:
    return oppdrag_med_tittel(db, BAERE)


def csrf(klient: TestClient) -> str:
    return CSRF.search(klient.get("/profil").text).group(1)


def skjemaverdier(html: str) -> dict[str, str]:
    """Verdiene skjemaet sender: tekstfelt, tekstområdet og valgte radioknapper."""
    verdier = {}
    for tag, a in les_side(html).tagger:
        if tag == "input" and a.get("type") == "text":
            verdier[a["name"]] = a.get("value", "")
        elif tag == "input" and a.get("type") == "radio" and "checked" in a:
            verdier[a["name"]] = a["value"]
    beskrivelse = re.search(r'<textarea[^>]*name="beskrivelse"[^>]*>([^<]*)</textarea>', html)
    verdier["beskrivelse"] = beskrivelse.group(1)
    return verdier


def lagre(klient: TestClient, oppdrag_id: int, *, med_csrf: bool = True, **endringer: str):
    """Henter skjemaet, endrer feltene og sender det."""
    html = klient.get(f"/oppdrag/{oppdrag_id}/rediger").text
    data = {**skjemaverdier(html), **endringer}
    if med_csrf:
        data["csrf_token"] = CSRF.search(html).group(1)
    return klient.post(f"/oppdrag/{oppdrag_id}/rediger", data=data, follow_redirects=False)


def post_rediger(klient: TestClient, oppdrag_id: int, **data: str):
    return klient.post(
        f"/oppdrag/{oppdrag_id}/rediger", data={"csrf_token": csrf(klient), **data}, follow_redirects=False
    )


GYLDIG = {
    "beskrivelse": "Trenger noen som kan måke snø i innkjørselen min i morgen tidlig.",
    "tittel": MAKE,
    "kategori": "snomaking",
    "postnummer": "0571",
    "dato": "25.11.2026",
    "klokkeslett": "09:00",
    "tilbud": "belop",
    "belop": "200",
}


# ---------- skjemaet ----------


def test_skjemaet_er_utfylt_med_de_lagrede_verdiene(som, make) -> None:
    """FR-6, UX-DR7: h1 og <title> «Rediger «…»», utfylte felt, forhåndsvisning og «Lagre endringer».

    Ingen «Få forslag» (KI), ingen `skjema_id`, ingen steg og ingen `autofocus`. «Mine oppdrag» er
    markert med aria-current="true".
    """
    svar = som("kari").get(f"/oppdrag/{make.id}/rediger")
    assert svar.status_code == 200
    html = svar.text
    assert "<title>Rediger «Måke snø i innkjørselen» – Nabolagshelten</title>" in html
    assert "<h1>Rediger «Måke snø i innkjørselen»</h1>" in html
    assert skjemaverdier(html) == GYLDIG
    assert ">Slik vises oppdraget for andre.</p>" in html
    assert ">Lagre endringer</button>" in html
    for fravaer in ("Få forslag", "skjema_id", "Publiser", "Neste", "Tilbake til steg 1",
                    "data-steg-skjema", "steg.js", "autofocus", 'type="file"', "Bytt bilde"):
        assert fravaer not in html, fravaer
    # Én skjerm med de to h2 (spec 2.5: ingen steg).
    assert ">Hva trenger du hjelp til?</h2>" in html and ">Når og hvor?</h2>" in html
    form = attrs(html, "form", method="post")
    assert form["action"] == f"/oppdrag/{make.id}/rediger" and "novalidate" in form
    for variant in ("topp", "bunn"):
        assert [(h, c) for h, c, _ in menyvalg(html, variant)] == [
            ("/", None), ("/mine-oppdrag", "true"), ("/profil", None),
        ]
    assert 'aria-current="page"' not in html
    side = les_side(html)
    assert [t for t, _ in side.tagger].count("h1") == 1
    assert side.forste_fokuserbare[2] == "Hopp til innholdet"


def test_endre_tidspunkt_gir_autofocus_pa_dato(som, baere) -> None:
    """FR-8, UX-DR27: `?fokus=tidspunkt` gir ett `autofocus`, på «Dato», med de gamle verdiene utfylt."""
    html = som("kari").get(f"/oppdrag/{baere.id}/rediger?fokus=tidspunkt").text
    assert html.count("autofocus") == 1
    assert "autofocus" in attrs(html, "input", name="dato")
    verdier = skjemaverdier(html)
    assert (verdier["dato"], verdier["klokkeslett"]) == ("22.11.2026", "10:00")
    assert "<h1>Rediger «Bære ved opp til tredje etasje»</h1>" in html


def test_ukjent_fokus_gir_ingen_autofocus(som, make) -> None:
    assert "autofocus" not in som("kari").get(f"/oppdrag/{make.id}/rediger?fokus=tittel").text


def test_tilbake_fra_skjemaet(som, make) -> None:
    """«Tilbake» i skjemaet går til forrige side, og til detaljene når forrige side var skjemaet selv."""
    klient = som("kari")
    sti = f"/oppdrag/{make.id}/rediger"
    html = klient.get(sti, headers={"referer": f"http://testserver/oppdrag/{make.id}"}).text
    assert f'<a class="tekstknapp" href="/oppdrag/{make.id}">Tilbake</a>' in html
    html = klient.get(sti, headers={"referer": "http://testserver/mine-oppdrag"}).text
    assert '<a class="tekstknapp" href="/mine-oppdrag">Tilbake</a>' in html
    svar = klient.post(sti, data={"csrf_token": csrf(klient), **GYLDIG, "tittel": ""},
                       headers={"referer": f"http://testserver{sti}?fokus=tidspunkt"})
    assert f'<a class="tekstknapp" href="/oppdrag/{make.id}">Tilbake</a>' in svar.text


# ---------- lagre ----------


def test_lagre_gir_303_kvittering_og_nye_verdier(som, db: Session, make) -> None:
    """FR-6, UX-DR22: 303 til detaljene, «Endringene er lagret.» i fokus, nye verdier og `versjon` + 1."""
    klient = som("kari")
    svar = lagre(klient, make.id, tittel="Måke snø og strø", belop="250")
    assert svar.status_code == 303
    assert svar.headers["location"] == f"/oppdrag/{make.id}"
    lagret = les(db, make.id)
    assert (lagret.tittel, lagret.belop, lagret.versjon) == ("Måke snø og strø", 250, 2)
    assert lagret.vesentlig_endret == T0
    html = klient.get(svar.headers["location"]).text
    assert "<h1>Måke snø og strø</h1>" in html
    kvittering = attrs(html, "div", id="kvittering")
    assert "autofocus" in kvittering and kvittering["tabindex"] == "-1"
    assert "<span>Endringene er lagret.</span>" in html
    assert html.count("autofocus") == 1
    assert "250 kr" in html
    assert "Endringene er lagret." not in klient.get(svar.headers["location"]).text


def test_lagre_uten_csrf_gir_403_og_ingen_endring(som, db: Session, make) -> None:
    """AD-5: POST uten CSRF-nøkkel avvises, og ingenting lagres."""
    svar = lagre(som("kari"), make.id, med_csrf=False, tittel="Uten nøkkel")
    assert svar.status_code == 403
    assert les(db, make.id).tittel == MAKE


def test_ikke_vesentlig_endring_over_http(som, db: Session, make) -> None:
    """AD-3: samme verdier med annen skrivemåte (« 0571 », «9») setter ikke `vesentlig_endret`."""
    svar = lagre(som("kari"), make.id, postnummer=" 0571 ", klokkeslett="9", kategori="annet")
    assert svar.status_code == 303
    lagret = les(db, make.id)
    assert lagret.vesentlig_endret is None
    assert (lagret.kategori, lagret.versjon) == ("annet", 2)


def test_dobbel_innsending_gir_303_begge_ganger(som, db: Session, make, sett_na) -> None:
    """NFR-5: samme gyldige skjema to ganger gir 303 begge ganger, og `vesentlig_endret` fra den første."""
    klient = som("kari")
    data = {"csrf_token": csrf(klient), **GYLDIG, "dato": "26.11.2026"}
    forste = klient.post(f"/oppdrag/{make.id}/rediger", data=data, follow_redirects=False)
    sett_na(datetime(2026, 11, 24, 12, 0, 5, tzinfo=timezone.utc))
    andre = klient.post(f"/oppdrag/{make.id}/rediger", data=data, follow_redirects=False)
    assert forste.status_code == andre.status_code == 303
    assert forste.headers["location"] == andre.headers["location"] == f"/oppdrag/{make.id}"
    assert les(db, make.id).vesentlig_endret == T0


# ---------- feil (NFR-10) ----------


def test_feil_i_felt_gir_422_med_alle_feil_og_verdiene(som, db: Session, make) -> None:
    """NFR-10: tom tittel og beløp «abc» gir 422, «Feil: » og den lagrede tittelen i <title> og h1."""
    svar = lagre(som("kari"), make.id, tittel="", belop="abc", beskrivelse="Ny beskrivelse som ikke lagres.")
    assert svar.status_code == 422
    html = svar.text
    assert "<title>Feil: Rediger «Måke snø i innkjørselen» – Nabolagshelten</title>" in html
    assert "<h1>Rediger «Måke snø i innkjørselen»</h1>" in html
    assert "<span>Skjemaet har 2 feil</span>" in html
    assert re.findall(r'<li><a href="#([^"]+)">', html) == ["tittel", "belop"]
    assert feltfeil(html, "tittel") == "Skriv en tittel."
    assert feltfeil(html, "belop") == "Skriv et beløp fra 1 til 10 000 kr, i hele kroner."
    verdier = skjemaverdier(html)
    assert (verdier["tittel"], verdier["belop"]) == ("", "abc")
    assert verdier["beskrivelse"] == "Ny beskrivelse som ikke lagres."
    assert "autofocus" in attrs(html, "div", id="feiloppsummering")
    assert html.count("autofocus") == 1
    assert ">Lagre endringer</button>" in html and "skjema_id" not in html
    lagret = les(db, make.id)
    assert (lagret.tittel, lagret.versjon) == (MAKE, 1)


def test_fortsatt_passert_gir_feil_under_nar(som, db: Session, baere) -> None:
    """FR-6, FR-8: lagret uten å endre tidspunktet gir «Velg et nytt tidspunkt fram i tid» under «Når?»."""
    klient = som("kari")
    for endring in ({}, {"dato": "23.11.2026"}):
        svar = lagre(klient, baere.id, **endring)
        assert svar.status_code == 422
        html = svar.text
        assert feltfeil(html, "nar") == "Velg et nytt tidspunkt fram i tid"
        assert '<li><a href="#dato">Velg et nytt tidspunkt fram i tid</a></li>' in html
        for navn, hjelp in (("dato", "dato-hjelp"), ("klokkeslett", "klokkeslett-hjelp")):
            felt = attrs(html, "input", name=navn)
            assert felt["aria-invalid"] == "true"
            assert felt["aria-describedby"] == f"{hjelp} nar-feil"
    assert les(db, baere.id).versjon == 1


# ---------- utgått oppdrag får nytt tidspunkt (FR-8, akseptansekriterium 1) ----------


def test_nytt_tidspunkt_gir_oppdraget_tilbake_i_oversikten(som, db: Session, baere) -> None:
    """FR-8: «Bære ved» får dato i morgen. Merket, snarveiene, menytallet og linja er borte, og Ola ser det."""
    klient = som("kari")
    assert "Tidspunktet er passert" in klient.get(f"/oppdrag/{baere.id}").text
    svar = lagre(klient, baere.id, dato="25.11.2026")
    assert svar.status_code == 303
    html = klient.get(svar.headers["location"]).text
    assert "<span>Endringene er lagret.</span>" in html
    assert "Tidspunktet er passert" not in html and "Endre tidspunkt" not in html
    assert ">Rediger</a>" in html
    mine = klient.get("/mine-oppdrag").text
    assert "handlingsmerke" not in mine and "listerad__handlinger" not in mine
    assert 'class="menytall"' not in mine and "trenger at du gjør noe" not in mine
    assert BAERE in som("ola").get("/").text


# ---------- tilgang og status ----------


@pytest.mark.parametrize("metode", ["GET", "POST"])
def test_andres_oppdrag_gir_samme_404(som, db: Session, make, metode: str) -> None:
    """FR-6, FR-9: Ola får samme 404 som for et oppdrag som ikke finnes, og ingenting endres."""
    klient = som("ola")
    svar = (klient.get(f"/oppdrag/{make.id}/rediger") if metode == "GET"
            else post_rediger(klient, make.id, **{**GYLDIG, "tittel": "Kapret"}))
    finnes_ikke = klient.get("/oppdrag/999999/rediger")
    assert svar.status_code == finnes_ikke.status_code == 404
    assert "<h1>Fant ikke siden</h1>" in svar.text
    assert MAKE not in svar.text
    lagret = les(db, make.id)
    assert (lagret.tittel, lagret.versjon) == (MAKE, 1)


def test_ugyldig_id_gir_404(som) -> None:
    klient = som("kari")
    for oppdrag_id in (0, 2**31, 99999999999999999999):
        assert klient.get(f"/oppdrag/{oppdrag_id}/rediger").status_code == 404, oppdrag_id
        assert post_rediger(klient, oppdrag_id, **GYLDIG).status_code == 404, oppdrag_id


@pytest.mark.parametrize("status", ["avbrutt", "utfort", "hjelper_valgt"])
@pytest.mark.parametrize("metode", ["GET", "POST", "POST-med-feil"])
def test_ikke_apen_gir_konflikt_til_detaljene(som, db: Session, make, status: str, metode: str) -> None:
    """FR-6, §4.0: 303 til detaljene med «Oppdraget er endret. Last siden på nytt.», og ingen endring."""
    make.status = status
    db.commit()
    klient = som("kari")
    if metode == "GET":
        svar = klient.get(f"/oppdrag/{make.id}/rediger", follow_redirects=False)
    else:
        tittel = "" if metode == "POST-med-feil" else "Endret etter avbrudd"
        svar = post_rediger(klient, make.id, **{**GYLDIG, "tittel": tittel})
    assert svar.status_code == 303
    assert svar.headers["location"] == f"/oppdrag/{make.id}"
    assert "feilmelding=" in svar.headers["set-cookie"]
    lagret = les(db, make.id)
    assert (lagret.tittel, lagret.versjon, lagret.status) == (MAKE, 1, status)
    html = klient.get(svar.headers["location"]).text
    assert f"<span>{KONFLIKT}</span>" in html


def test_konflikt_viser_feilmeldingen_i_fokus_og_last_siden_pa_nytt(som, db: Session, make) -> None:
    """§4.0, UX-DR22, UX-DR27: feilmeldingen rett etter h1 med autofocus, og «Last siden på nytt»
    (button-secondary) til siden selv. Neste lasting har ikke meldingen."""
    make.status = "avbrutt"
    db.commit()
    klient = som("kari")
    svar = post_rediger(klient, make.id, **GYLDIG)
    html = klient.get(svar.headers["location"]).text
    melding = attrs(html, "div", id="feilmelding")
    assert melding["class"] == "melding melding--feil"
    assert melding["tabindex"] == "-1" and "autofocus" in melding
    assert html.count("autofocus") == 1
    assert html.index("<h1>") < html.index('id="feilmelding"')
    assert 'role="alert"' not in html
    lenke = re.search(r'<a class="knapp knapp--sekundar melding__knapp" href="([^"]+)">Last siden på nytt</a>', html)
    assert lenke and lenke.group(1) == f"/oppdrag/{make.id}"
    igjen = klient.get(lenke.group(1)).text
    assert KONFLIKT not in igjen and "Last siden på nytt" not in igjen
    assert '<span class="skjult-tekst">Status: </span>Avbrutt</span>' in igjen


# ---------- detaljene for eieren og andre (FR-6, FR-7, FR-8) ----------


def handlinger(html: str) -> list[tuple[str, str, str]]:
    """(klasse, href, tekst) for lenkene i `div.handlinger`."""
    blokk = re.search(r'<div class="handlinger">(.*?)</div>', html, re.S)
    if not blokk:
        return []
    return re.findall(r'<a class="([^"]+)" href="([^"]+)"[^>]*>([^<]+)</a>', blokk.group(1))


def test_detaljer_for_eier_av_apent(som, make) -> None:
    """FR-6, FR-7: «Rediger» og «Avbryt oppdrag» (sekundære) etter beskrivelsen, uten merke."""
    html = som("kari").get(f"/oppdrag/{make.id}").text
    assert handlinger(html) == [
        ("knapp knapp--sekundar", f"/oppdrag/{make.id}/rediger", "Rediger"),
        ("knapp knapp--sekundar", f"/oppdrag/{make.id}/avbryt", "Avbryt oppdrag"),
    ]
    assert html.index('class="beskrivelse"') < html.index('class="handlinger"')
    assert "handlingsmerke" not in html and "knapp--primar" not in html.split("<dialog")[0]


def test_detaljer_for_eier_av_utgatt(som, baere) -> None:
    """FR-8: merket «Tidspunktet er passert», så «Endre tidspunkt» (primær) og «Avbryt oppdrag»."""
    html = som("kari").get(f"/oppdrag/{baere.id}").text
    assert handlinger(html) == [
        ("knapp knapp--primar", f"/oppdrag/{baere.id}/rediger?fokus=tidspunkt", "Endre tidspunkt"),
        ("knapp knapp--sekundar", f"/oppdrag/{baere.id}/avbryt", "Avbryt oppdrag"),
    ]
    beskrivelse = html.index('class="beskrivelse"')
    merke = html.index('class="handlingsmerke"')
    assert beskrivelse < merke < html.index('class="handlinger"')
    assert "Rediger</a>" not in html


@pytest.mark.parametrize("tittel", ["Lufte hunden mens jeg er bortreist", "Bytte lyspære i taket"])
def test_detaljer_for_avbrutt_og_utfort_har_ingen_handlinger(som, db: Session, tittel: str) -> None:
    html = som("kari").get(f"/oppdrag/{oppdrag_med_tittel(db, tittel).id}").text
    assert handlinger(html) == [] and "<dialog" not in html


def test_detaljer_for_andre_har_ingen_handlinger(som, make, baere) -> None:
    """FR-6, FR-7: Ola ser aldri knappene, og detaljene for andre er ellers uendret (invariant 2.3)."""
    html = som("ola").get(f"/oppdrag/{make.id}").text
    assert handlinger(html) == []
    for fravaer in ("Rediger", "Avbryt oppdrag", "Endre tidspunkt", "<dialog", "/rediger", "/avbryt"):
        assert fravaer not in html, fravaer
    assert "Lagt ut av Kari Nordmann" in html


def test_tilbake_i_detaljene_gaar_aldri_til_skjemaet_eller_bekreftelsen(som, make) -> None:
    """Invariant 2.3/2.4: etter lagring eller avbrudd går «Tilbake» til «Mine oppdrag»."""
    klient = som("kari")
    for forrige in (f"/oppdrag/{make.id}/rediger", f"/oppdrag/{make.id}/rediger?fokus=tidspunkt",
                    f"/oppdrag/{make.id}/avbryt", f"/oppdrag/{make.id}/avbryt?fra=mine"):
        html = klient.get(f"/oppdrag/{make.id}", headers={"referer": f"http://testserver{forrige}"}).text
        assert '<a class="tekstknapp" href="/mine-oppdrag">Tilbake</a>' in html, forrige


# ---------- XSS (NFR-12) ----------


def test_tittel_vises_som_tekst_i_skjemaet(som, db: Session, make) -> None:
    """NFR-12: HTML i tittelen vises escaped i <title>, h1 og feltet."""
    skadelig = "<script>alert(1)</script>"
    make.tittel = skadelig
    db.commit()
    html = som("kari").get(f"/oppdrag/{make.id}/rediger").text
    assert skadelig not in html
    assert "<title>Rediger «&lt;script&gt;alert(1)&lt;/script&gt;» – Nabolagshelten</title>" in html
    assert "<h1>Rediger «&lt;script&gt;alert(1)&lt;/script&gt;»</h1>" in html
