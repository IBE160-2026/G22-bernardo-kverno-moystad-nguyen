"""«Nytt oppdrag» i to steg og forhåndsvisningen, over HTTP uten JS: radene i
I/O-matrisen i spec 2.2 som ikke trenger nettleser (FR-5, NFR-5, NFR-12, UX-DR13,
UX-DR15, UX-DR16, AR-28).

Serveren rendrer alltid ett skjema på én skjerm: `h1` «Nytt oppdrag», to `section`
med `data-steg` og hver sin `h2`, og forhåndsvisningen rett over «Publiser».
«Neste» og «Tilbake til steg 1» har `hidden`, så de aldri vises uten JS. Tekstene
steg.js bruker, står i `data-`-attributter og er de samme som serveren bruker.
Oppførselen i nettleseren testes i `tests/e2e/test_klientatferd.py`.
"""

from __future__ import annotations

from html.parser import HTMLParser

import pytest
from fastapi.testclient import TestClient

from app.core import domene
from app.core.render import sidetittel
from app.oppdrag.routes import _kr_fra_sifre, forhandsvisning
from app.oppdrag.service import SKRIV_BESKRIVELSE, SKRIV_TITTEL, TITTEL_FOR_KORT, VELG_KATEGORI

from ..core.test_render import les_side
from .test_legge_ut import GYLDIG, antall, attrs, kari, kari_klient, send  # noqa: F401
from .test_legge_ut import _klokke  # noqa: F401  (fast klokke, autouse)

NBSP = " "
TOM = "–"


class Skjemaleser(HTMLParser):
    """Hvilket steg hvert felt og hver knapp ligger i, og teksten i forhåndsvisningen."""

    def __init__(self) -> None:
        super().__init__()
        self.stabel: list[tuple[str, str | None, str | None]] = []  # (tag, steg, data-felt)
        self.felt_i_steg: dict[str, list[str]] = {"1": [], "2": []}
        self.knapper_i_steg: dict[str, list[str]] = {"1": [], "2": []}
        self.forhandsvisning: dict[str, str] = {}
        self.tagger_i_felt: dict[str, list[str]] = {}
        self.overskrifter: list[tuple[str, str]] = []
        self._knapp: str | None = None
        self._overskrift: str | None = None

    def _steg(self) -> str | None:
        return next((s for _, s, _ in reversed(self.stabel) if s), None)

    def handle_starttag(self, tag: str, attrs: list) -> None:
        a = dict(attrs)
        steg = a.get("data-steg") if tag == "section" else None
        gjeldende = steg or self._steg()
        if tag in {"input", "textarea"} and a.get("type") != "hidden" and gjeldende:
            if a["name"] not in self.felt_i_steg[gjeldende]:
                self.felt_i_steg[gjeldende].append(a["name"])
        if tag == "button":
            self._knapp = ""
        if tag in {"h1", "h2"}:
            self._overskrift = ""
        for _, _, felt in self.stabel:
            if felt:
                self.tagger_i_felt.setdefault(felt, []).append(tag)
        if tag not in {"input", "wbr", "br"}:
            self.stabel.append((tag, steg, a.get("data-felt")))
            if a.get("data-felt"):
                self.forhandsvisning[a["data-felt"]] = ""

    def handle_endtag(self, tag: str) -> None:
        if tag == "button" and self._knapp is not None:
            steg = self._steg()
            if steg:
                self.knapper_i_steg[steg].append(self._knapp.strip())
            self._knapp = None
        if tag in {"h1", "h2"} and self._overskrift is not None:
            self.overskrifter.append((tag, self._overskrift.strip()))
            self._overskrift = None
        while self.stabel:
            if self.stabel.pop()[0] == tag:
                break

    def handle_data(self, data: str) -> None:
        if self._knapp is not None:
            self._knapp += data
        if self._overskrift is not None:
            self._overskrift += data
        for _, _, felt in self.stabel:
            if felt:
                self.forhandsvisning[felt] += data


def med_attributt(html: str, tag: str, navn: str) -> dict:
    """Attributtene til første `tag` som har attributtet `navn` (også uten verdi)."""
    return next(a for t, a in les_side(html).tagger if t == tag and navn in a)


def les_skjema(html: str) -> Skjemaleser:
    leser = Skjemaleser()
    leser.feed(html)
    return leser


def kort(html: str) -> dict[str, str]:
    """Teksten i hver `data-felt` i forhåndsvisningen, uten mellomrom rundt."""
    return {felt: tekst.strip() for felt, tekst in les_skjema(html).forhandsvisning.items()}


# ---------- én skjerm uten JS (UX-DR16) ----------


def test_en_skjerm_har_h1_og_to_h2_i_rekkefolge(kari_klient: TestClient) -> None:
    """UX-DR16: `h1` «Nytt oppdrag», så «Hva trenger du hjelp til?» og «Når og hvor?»."""
    html = kari_klient.get("/oppdrag/ny").text
    assert "<title>Nytt oppdrag – Nabolagshelten</title>" in html
    assert les_skjema(html).overskrifter == [
        ("h1", "Nytt oppdrag"),
        ("h2", "Hva trenger du hjelp til?"),
        ("h2", "Når og hvor?"),
    ]
    assert html.count("<form") == 1
    assert html.count('data-steg="1"') == html.count('data-steg="2"') == 1


def test_feltene_ligger_i_riktig_steg(kari_klient: TestClient) -> None:
    """FR-5, UX-DR16: steg 1 har beskrivelse, tittel og kategori; steg 2 resten og «Publiser»."""
    leser = les_skjema(kari_klient.get("/oppdrag/ny").text)
    assert leser.felt_i_steg == {
        "1": ["beskrivelse", "tittel", "kategori"],
        "2": ["postnummer", "dato", "klokkeslett", "tilbud", "belop"],
    }
    assert leser.knapper_i_steg == {"1": ["Neste"], "2": ["Publiser", "Tilbake til steg 1"]}


def test_skjult_felt_ligger_utenfor_stegene(kari_klient: TestClient) -> None:
    """AD-7: `csrf_token` og `skjema_id` står én gang, og ingen feltnavn begynner med `_`."""
    html = kari_klient.get("/oppdrag/ny").text
    forste_steg = html.index('data-steg="1"')
    for navn in ("csrf_token", "skjema_id"):
        assert html.count(f'name="{navn}"') == 1
        assert html.index(f'name="{navn}"') < forste_steg
    assert 'name="_' not in html


def test_neste_og_tilbake_er_skjult_uten_js(kari_klient: TestClient) -> None:
    """UX-DR16: «Neste» (primær, type=button) og «Tilbake til steg 1» (tekstknapp) har `hidden`."""
    html = kari_klient.get("/oppdrag/ny").text
    neste = med_attributt(html, "button", "data-neste")
    assert neste["type"] == "button" and "hidden" in neste
    assert neste["class"] == "knapp knapp--primar"
    tilbake = med_attributt(html, "button", "data-tilbake-steg")
    assert tilbake["type"] == "button" and "hidden" in tilbake
    assert tilbake["class"] == "tekstknapp"
    publiser = attrs(html, "button", type="submit")
    assert "hidden" not in publiser
    # «Tilbake» øverst vises på én skjerm og i steg 1.
    assert attrs(html, "a", **{"data-vis-i-steg": "1"})["class"] == "tekstknapp"
    overskrifter = [a for t, a in les_side(html).tagger if t == "h2" and "data-kun-en-skjerm" in a]
    assert len(overskrifter) == 2
    assert all("hidden" not in a for a in overskrifter)


def test_tekstene_for_tomme_felt_er_serverens(kari_klient: TestClient) -> None:
    """UX-DR16: «Neste» bruker de samme feiltekstene som `opprett_oppdrag`."""
    html = kari_klient.get("/oppdrag/ny").text
    assert attrs(html, "textarea", name="beskrivelse")["data-tom"] == SKRIV_BESKRIVELSE
    assert attrs(html, "input", name="tittel")["data-tom"] == SKRIV_TITTEL
    assert med_attributt(html, "fieldset", "data-tom")["data-tom"] == VELG_KATEGORI
    assert html.count("data-tom=") == 3


def test_overskrifter_og_titler_for_stegene(kari_klient: TestClient) -> None:
    """UX-DR16, UX-DR2: tekstene steg.js setter, ordrett fra EXPERIENCE.md og laget med `sidetittel`."""
    skjema = attrs(kari_klient.get("/oppdrag/ny").text, "form", method="post")
    assert "data-steg-skjema" in skjema
    assert skjema["data-overskrift"] == "Nytt oppdrag"
    assert skjema["data-overskrift-1"] == "Nytt oppdrag 1 av 2"
    assert skjema["data-overskrift-2"] == "Nytt oppdrag 2 av 2"
    for nokkel, tittel in (("", "Nytt oppdrag"), ("-1", "Nytt oppdrag, steg 1 av 2"),
                           ("-2", "Nytt oppdrag, steg 2 av 2")):
        assert skjema[f"data-tittel{nokkel}"] == sidetittel(tittel)
        assert skjema[f"data-tittel{nokkel}-feil"] == sidetittel(tittel, feil=True)
    assert skjema["data-tittel-1"] == "Nytt oppdrag, steg 1 av 2 – Nabolagshelten"
    assert skjema["data-tittel-2-feil"] == "Feil: Nytt oppdrag, steg 2 av 2 – Nabolagshelten"


# ---------- forhåndsvisningen (UX-DR15) ----------


def test_forhandsvisningen_er_tom_ved_get(kari_klient: TestClient) -> None:
    """UX-DR15: tomme felt som «–», postnummeret fra profilen med poststed."""
    html = kari_klient.get("/oppdrag/ny").text
    assert kort(html) == {"kategori": TOM, "tittel": TOM, "tid": TOM, "sted": "0571 Oslo", "pris": TOM}


def test_forhandsvisningen_star_over_publiser_uten_lenke_overskrift_og_aria_live(kari_klient: TestClient) -> None:
    """UX-DR15: `section` med navnet «Slik vises oppdraget for andre.», ingen lenke, ingen
    overskrift, ingen `aria-live`, og tittelen er en `p`."""
    html = kari_klient.get("/oppdrag/ny").text
    start = html.index('<section class="forhandsvisning"')
    slutt = html.index("</section>", start)
    utdrag = html[start:slutt]
    seksjon = attrs(html, "section", **{"class": "forhandsvisning"})
    etikett = seksjon["aria-labelledby"]
    assert f'<p class="forhandsvisning__etikett" id="{etikett}">Slik vises oppdraget for andre.</p>' in utdrag
    for forbudt in ("<a ", "<h1", "<h2", "<h3", "aria-live", "role="):
        assert forbudt not in utdrag, forbudt
    assert '<p class="kort__tittel" data-felt="tittel">' in utdrag
    assert 'class="kort kort--forhandsvisning"' in utdrag
    assert slutt < html.index(">Publiser</button>")
    assert html.index(">Hva tilbyr du?</legend>") < start


def test_forhandsvisningen_etter_422_viser_det_brukeren_skrev(kari_klient: TestClient, db) -> None:
    """UX-DR15, NFR-10: tittel `ab` og tom dato gir 422, og kortet viser verdiene fra skjemaet."""
    svar = send(kari_klient, tittel="ab", dato="", postnummer="5006")
    assert svar.status_code == 422
    assert antall(db) == 0
    html = svar.text
    assert kort(html) == {
        "kategori": "Snømåking", "tittel": "ab", "tid": TOM, "sted": "5006 Bergen", "pris": f"1{NBSP}000{NBSP}kr",
    }
    # Kategoriikonet står i merket, som på detaljene.
    assert "svg" in les_skjema(html).tagger_i_felt["kategori"]


def test_serverfeil_i_begge_steg_listes_i_feltrekkefolge(kari_klient: TestClient) -> None:
    """UX-DR16: feil fra begge steg i én oppsummering; første lenke viser steget (steg.js)."""
    html = send(kari_klient, tittel="ab", dato="").text
    assert "<span>Skjemaet har 2 feil</span>" in html
    assert '<li><a href="#tittel">Tittelen må ha minst 3 tegn.</a></li>' in html
    assert '<li><a href="#dato">Skriv datoen.</a></li>' in html
    assert html.index('href="#tittel"') < html.index('href="#dato"')
    assert "<title>Feil: Nytt oppdrag – Nabolagshelten</title>" in html


def test_serveren_avgjor_uavhengig_av_stegene(kari_klient: TestClient, db) -> None:
    """T-6: tittel `ab` og beløp `abc` slipper gjennom «Neste», og serveren gir samme feil som før."""
    svar = send(kari_klient, tittel="ab", belop="abc")
    assert svar.status_code == 422
    assert f'<li><a href="#tittel">{TITTEL_FOR_KORT}</a></li>' in svar.text
    assert '<li><a href="#belop">Skriv et beløp fra 1 til 10 000 kr, i hele kroner.</a></li>' in svar.text
    assert kort(svar.text)["pris"] == f"abc{NBSP}kr"
    assert antall(db) == 0


def test_ukjent_kategori_gir_feil_og_tomt_merke(kari_klient: TestClient) -> None:
    """En POST rett mot serveren med ukjent kategori gir feilen, ikke en krasj i forhåndsvisningen."""
    svar = send(kari_klient, kategori="finnes-ikke")
    assert svar.status_code == 422
    assert f"<li><a href=\"#kategori-snomaking\">{VELG_KATEGORI}</a></li>" in svar.text
    assert kort(svar.text)["kategori"] == TOM


def test_forhandsvisningen_viser_html_som_tekst(kari_klient: TestClient) -> None:
    """NFR-12: `<script>` i tittelen vises escaped i forhåndsvisningen."""
    skadelig = "<script>alert(1)</script>"
    html = send(kari_klient, tittel=skadelig, beskrivelse="").text
    assert skadelig not in html
    assert '<p class="kort__tittel" data-felt="tittel">&lt;script&gt;alert(1)&lt;/script&gt;</p>' in html
    assert kort(html)["tittel"] == skadelig


TOMT = {"kategori": "", "tittel": "", "dato": "", "klokkeslett": "", "postnummer": "", "tilbud": "", "belop": ""}


@pytest.mark.parametrize(
    ("endringer", "sted", "forventet"),
    [
        ({}, "", {"kategori": "", "tittel": TOM, "tid": TOM, "sted": TOM, "pris": TOM}),
        (
            {"kategori": "snomaking", "tittel": "Måke snø", "dato": "25.11.2026", "klokkeslett": "7",
             "postnummer": "5006", "tilbud": "belop", "belop": "1000"},
            "Bergen",
            {"kategori": "snomaking", "tittel": "Måke snø", "tid": "25.11.2026 kl. 7", "sted": "5006 Bergen",
             "pris": f"1{NBSP}000{NBSP}kr"},
        ),
        ({"tilbud": "uten", "belop": "1000"}, "", {"pris": "Uten betaling"}),
        ({"tilbud": "belop", "belop": " 10 000 "}, "", {"pris": f"10{NBSP}000{NBSP}kr"}),
        ({"tilbud": "belop", "belop": "0"}, "", {"pris": f"0{NBSP}kr"}),
        ({"tilbud": "belop", "belop": "1,5"}, "", {"pris": f"1,5{NBSP}kr"}),
        ({"tilbud": "belop", "belop": "   "}, "", {"pris": TOM}),
        ({"tilbud": "", "belop": "200"}, "", {"pris": TOM}),
        ({"tilbud": "noe-annet", "belop": "200"}, "", {"pris": TOM}),
        ({"dato": "25.11.2026"}, "", {"tid": TOM}),
        ({"klokkeslett": "07:00"}, "", {"tid": TOM}),
        ({"postnummer": "9999"}, "", {"sted": "9999"}),
        ({"tittel": "   "}, "", {"tittel": TOM}),
        ({"kategori": "finnes-ikke"}, "", {"kategori": ""}),
    ],
    ids=["tom", "utfylt", "uten-betaling", "mellomrom-i-belop", "null", "annen-tekst", "bare-mellomrom",
         "ingen-tilbud", "ukjent-tilbud", "bare-dato", "bare-klokkeslett", "uten-poststed", "tom-tittel",
         "ukjent-kategori"],
)
def test_reglene_for_forhandsvisningen(endringer: dict, sted: str, forventet: dict) -> None:
    """Spec 2.2, Design Notes: de samme reglene som skjema.js, så siden ikke hopper når JS starter."""
    resultat = forhandsvisning(TOMT | endringer, sted)
    assert {k: resultat[k] for k in forventet} == forventet


@pytest.mark.parametrize("belop", [0, 1, 7, 99, 100, 999, 1000, 10_000, 123_456, 1_000_000, 12_345_678])
def test_kr_fra_sifre_er_lik_domene_kr(belop: int) -> None:
    """Forhåndsvisningen formaterer sifrene uten `int()`, men likt med filteret `kr`."""
    assert _kr_fra_sifre(str(belop)) == domene.kr(belop)
    assert _kr_fra_sifre("000" + str(belop)) == domene.kr(belop)


def test_belop_med_5000_sifre_gir_422_ikke_500(kari_klient: TestClient, db) -> None:
    """NFR-10, invariant fra 2.1: et svært langt beløp gir feilen ved feltet, også i forhåndsvisningen."""
    svar = send(kari_klient, tilbud="belop", belop="9" * 5000)
    assert svar.status_code == 422
    assert '<li><a href="#belop">Skriv et beløp fra 1 til 10 000 kr, i hele kroner.</a></li>' in svar.text
    assert kort(svar.text)["pris"].endswith(f"999{NBSP}kr")
    assert antall(db) == 0


def test_ett_autofocus_og_ingen_maxlength(kari_klient: TestClient) -> None:
    """Invariant fra 2.1: ett `autofocus` (beskrivelsen), ingen `maxlength`, telleren står der."""
    html = kari_klient.get("/oppdrag/ny").text
    assert html.count("autofocus") == 1
    assert "autofocus" in attrs(html, "textarea", name="beskrivelse")
    assert "maxlength" not in html
    assert '<p class="teller" id="beskrivelse-teller">0 av 1000 tegn</p>' in html


def test_gyldig_innsending_gir_fortsatt_en_rad(kari_klient: TestClient, db) -> None:
    """Invariant fra 2.1: skjemaet med to deler sendes som før, og gir én rad og 303."""
    svar = send(kari_klient, **GYLDIG)
    assert svar.status_code == 303
    assert antall(db) == 1
