"""Sideramme, filtre, menyvalg på undersider og stilark (UX-DR1, UX-DR2, UX-DR4, AR-27, AD-9, AD-10)."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from starlette.requests import Request

from app.core import domene
from app.core.render import miljo, render, sidetittel

ROT = Path(__file__).resolve().parents[2]
CSS = ROT / "app" / "core" / "static" / "css" / "app.css"
DESIGN_MD = (
    ROT
    / "_bmad-output/planning-artifacts/ux-designs/ux-G22-bernardo-kverno-moystad-nguyen-2026-11-07/DESIGN.md"
)


class Sideleser(HTMLParser):
    """Samler elementer, landemerker og første fokuserbare element."""

    def __init__(self) -> None:
        super().__init__()
        self.html_lang: str | None = None
        self.tagger: list[tuple[str, dict]] = []
        self.forste_fokuserbare: tuple[str, dict, str] | None = None
        self._samler_tekst = False
        self._tekst: list[str] = []

    def handle_starttag(self, tag: str, attrs: list) -> None:
        a = dict(attrs)
        self.tagger.append((tag, a))
        if tag == "html":
            self.html_lang = a.get("lang")
        if self.forste_fokuserbare is None and self._fokuserbar(tag, a):
            self.forste_fokuserbare = (tag, a, "")
            self._samler_tekst = True

    def handle_endtag(self, tag: str) -> None:
        if self._samler_tekst and self.forste_fokuserbare and tag == self.forste_fokuserbare[0]:
            t, a, _ = self.forste_fokuserbare
            self.forste_fokuserbare = (t, a, "".join(self._tekst).strip())
            self._samler_tekst = False

    def handle_data(self, data: str) -> None:
        if self._samler_tekst:
            self._tekst.append(data)

    @staticmethod
    def _fokuserbar(tag: str, a: dict) -> bool:
        if "tabindex" in a:
            return int(a["tabindex"]) >= 0
        if tag == "a":
            return "href" in a
        if tag == "input":
            return a.get("type") != "hidden"
        return tag in {"button", "select", "textarea"}


def les_side(html: str) -> Sideleser:
    leser = Sideleser()
    leser.feed(html)
    return leser


def test_sidetittel_monster() -> None:
    assert sidetittel("Logg inn") == "Logg inn – Nabolagshelten"
    assert sidetittel("Registrering", feil=True) == "Feil: Registrering – Nabolagshelten"


def test_logg_inn_har_sideramme(klient: TestClient) -> None:
    """UX-DR2: lang, tittel, landemerker, én h1 og «Hopp til innholdet» først."""
    svar = klient.get("/logg-inn")
    assert svar.status_code == 200
    side = les_side(svar.text)
    assert side.html_lang == "nb"
    assert "<title>Logg inn – Nabolagshelten</title>" in svar.text
    tagger = [t for t, _ in side.tagger]
    assert tagger.count("header") == 1
    assert tagger.count("main") == 1
    assert tagger.count("h1") == 1
    main = next(a for t, a in side.tagger if t == "main")
    assert main.get("tabindex") == "-1"
    assert main.get("id") == "innhold"

    tag, attrs, tekst = side.forste_fokuserbare
    assert (tag, attrs.get("href"), tekst) == ("a", "#innhold", "Hopp til innholdet")


def test_topplinje_uten_innlogging_har_bare_logoen(klient: TestClient) -> None:
    svar = klient.get("/logg-inn")
    topplinje = re.search(r"<header.*?</header>", svar.text, re.S).group(0)
    assert "Nabolagshelten" in topplinje
    assert "<nav" not in svar.text  # ingen meny uten innlogging
    assert "<a " not in topplinje  # ingen lenker til sider som ikke finnes ennå
    assert 'aria-hidden="true"' in topplinje  # logo-ikonet er dekorativt (UX-DR6)


def test_logg_inn_skjema_har_csrf_og_felttyper(klient: TestClient) -> None:
    svar = klient.get("/logg-inn")
    side = les_side(svar.text)
    form = next(a for t, a in side.tagger if t == "form")
    assert form["method"] == "post"
    assert form["action"] == "/logg-inn"
    assert "novalidate" in form
    felt = {a.get("name"): a for t, a in side.tagger if t == "input"}
    assert felt["csrf_token"]["type"] == "hidden" and felt["csrf_token"]["value"]
    assert (felt["epost"]["type"], felt["epost"]["autocomplete"]) == ("email", "email")
    assert (felt["passord"]["type"], felt["passord"]["autocomplete"]) == (
        "password",
        "current-password",
    )
    etiketter = re.findall(r'<label for="(\w+)">([^<]+)</label>', svar.text)
    assert etiketter == [("epost", "E-post"), ("passord", "Passord")]


def test_autoescape_er_pa() -> None:
    from app.core.render import miljo

    assert miljo.autoescape is True
    mal = miljo.from_string("{{ tekst }}")
    assert mal.render(tekst="<script>alert(1)</script>") == "&lt;script&gt;alert(1)&lt;/script&gt;"


# ---------- filtre (AD-9, AD-10) ----------


def test_filteret_tidspunkt(sett_na) -> None:
    """AD-9: `tidspunkt` viser norsk tid med `klokke.na()` som «i dag»."""
    sett_na(datetime(2026, 11, 24, 12, 0, tzinfo=timezone.utc))
    mal = miljo.from_string("{{ t|tidspunkt }}")
    assert mal.render(t=datetime(2026, 11, 25, 6, 0, tzinfo=timezone.utc)) == "I morgen kl. 07:00"
    assert mal.render(t=datetime(2026, 11, 28, 11, 0, tzinfo=timezone.utc)) == "Lørdag 28. nov. kl. 12:00"


@pytest.mark.parametrize(
    ("belop", "forventet"),
    [(None, "Uten betaling"), (1, "1\u00a0kr"), (200, "200\u00a0kr"), (1000, "1\u00a0000\u00a0kr"),
     (10000, "10\u00a0000\u00a0kr")],
)
def test_filteret_kr(belop: int | None, forventet: str) -> None:
    """EXPERIENCE.md § Formater: «1 000 kr» med NBSP som tusenskille og før «kr»."""
    assert miljo.from_string("{{ b|kr }}").render(b=belop) == forventet
    assert domene.kr(belop) == forventet


def test_filtrene_kategori_tekst_og_status_tekst() -> None:
    """AD-10: kategori og status lagres som kode og vises bare med filtrene."""
    mal = miljo.from_string("{{ k|kategori_tekst }} / {{ s|status_tekst }}")
    assert mal.render(k="baerehjelp-flytting", s="hjelper_valgt") == "Bærehjelp/flytting / Hjelper valgt"
    assert [domene.kategori_tekst(kode) for kode, _ in domene.KATEGORIER] == [
        "Snømåking", "Hage", "Bærehjelp/flytting", "Dyrepass", "Teknologihjelp", "Annet",
    ]
    assert [domene.status_tekst(kode) for kode, _ in domene.STATUSER] == [
        "Åpen", "Hjelper valgt", "Utført", "Avbrutt",
    ]
    assert all(kode.isascii() for kode in domene.KATEGORIKODER | domene.STATUSKODER)
    with pytest.raises(ValueError):
        domene.kategori_tekst("Snømåking")
    with pytest.raises(ValueError):
        domene.status_tekst("open")


def test_filtrene_escaper_tekst() -> None:
    """AD-11: filtrene gir vanlig tekst, som autoescape escaper."""
    assert "<" not in miljo.from_string("{{ b|kr }}").render(b=None)


def _request(app, sporring: bytes = b"") -> Request:
    return Request({"type": "http", "method": "GET", "path": "/", "headers": [], "app": app,
                    "query_string": sporring, "state": {}})


def _filterlenke(app, sporring: bytes, mal: str) -> str:
    return miljo.from_string(mal).render(request=_request(app, sporring))


def test_filterlenke_beholder_andre_parametre(app) -> None:
    """AR-27, FR-11: `filterlenke` endrer én parameter og beholder de andre i samme rekkefølge."""
    assert _filterlenke(app, b"postnummer=5006&kategori=hage", "{{ filterlenke(kategori='alle') }}") == (
        "/?postnummer=5006&amp;kategori=alle"
    )
    assert _filterlenke(app, b"", "{{ filterlenke(kategori='hage') }}") == "/?kategori=hage"
    assert _filterlenke(app, b"kategori=hage", "{{ filterlenke(postnummer='5006') }}") == (
        "/?kategori=hage&amp;postnummer=5006"
    )


def test_filterlenke_utelater_none_og_vist_postnummer(app) -> None:
    """AR-27: `None` fjerner parameteren, og `vist_postnummer` følger aldri med."""
    sporring = b"postnummer=5006&kategori=hage&vist_postnummer=0571"
    assert _filterlenke(app, sporring, "{{ filterlenke(postnummer=None) }}") == "/?kategori=hage"
    assert _filterlenke(app, sporring, "{{ filterlenke(kategori=None, postnummer=None) }}") == "/"
    assert "vist_postnummer" not in _filterlenke(app, sporring, "{{ filterlenke() }}")


def test_filterlenke_koder_verdiene(app) -> None:
    """NFR-12: verdier fra adressen kodes i lenken og escapes i HTML."""
    html = _filterlenke(app, b"postnummer=%22%3E%3Cscript%3E", "{{ filterlenke(kategori='hage') }}")
    assert "<script>" not in html and '"' not in html
    assert html == "/?postnummer=%22%3E%3Cscript%3E&amp;kategori=hage"


@pytest.mark.parametrize(
    ("snitt", "antall", "forventet"),
    [(None, 0, "Ingen vurderinger ennå"), (4.3, 7, "4,3 av 5, 7 vurderinger"), (5.0, 1, "5,0 av 5, 1 vurdering"),
     (4.25, 4, "4,2 av 5, 4 vurderinger"), (4.0, 0, "Ingen vurderinger ennå")],
)
def test_filteret_vurdering(snitt: float | None, antall: int, forventet: str) -> None:
    """FR-21, EXPERIENCE.md § Formater: snittet som «4,3 av 5, 7 vurderinger»."""
    erfaring = domene.Erfaring(fullforte=0, per_kategori=(), snitt=snitt, antall_vurderinger=antall)
    assert miljo.from_string("{{ e|vurdering }}").render(e=erfaring) == forventet


@pytest.mark.parametrize(
    ("antall", "forventet"),
    [(0, "Ingen fullførte oppdrag ennå"), (1, "1 fullført oppdrag"), (12, "12 fullførte oppdrag")],
)
def test_filteret_fullforte(antall: int, forventet: str) -> None:
    """FR-21: «Ingen fullførte oppdrag ennå», «1 fullført oppdrag» eller «12 fullførte oppdrag»."""
    assert miljo.from_string("{{ n|fullforte }}").render(n=antall) == forventet


def test_feil_i_tittel_uten_feiloppsummering(app) -> None:
    """UX-DR2: `feil_i_tittel=True` gir «Feil: » i tittelen, men ingen feiloppsummering."""
    request = Request({"type": "http", "method": "GET", "path": "/x", "headers": [], "app": app,
                       "query_string": b"", "state": {"innlogget": object(), "csrf": "n"}})
    html = render(request, "core/feil.html", tittel="T", aktiv_meny=None, feil_i_tittel=True,
                  overskrift="O").body.decode()
    assert "<title>Feil: T – Nabolagshelten</title>" in html
    assert "feiloppsummering" not in html


def test_underside_gir_aria_current_true(app) -> None:
    """UX-DR3: på en underside får menyvalget `aria-current="true"`, og ingen har `"page"`."""
    request = Request({"type": "http", "method": "GET", "path": "/x", "headers": [], "app": app,
                       "query_string": b"", "state": {"innlogget": object(), "csrf": "n"}})
    html = render(request, "core/feil.html", tittel="T", aktiv_meny="profil", underside=True,
                  overskrift="O").body.decode()
    assert 'href="/profil" aria-current="true"' in html
    assert 'aria-current="page"' not in html
    html = render(request, "core/feil.html", tittel="T", aktiv_meny="profil", overskrift="O").body.decode()
    assert 'href="/profil" aria-current="page"' in html


def test_feiloppsummeringen_lenker_gruppefeil_til_forste_felt() -> None:
    """UX-DR12: `meldinger(lenker=...)` sender lenken for «nar» til «dato»."""
    mal = miljo.from_string(
        '{% import "core/makroer.html" as m with context %}{{ m.meldinger(lenker={"nar": "dato"}) }}'
    )
    html = mal.render(feil=[("nar", "Velg et nytt tidspunkt fram i tid"), ("tittel", "Skriv en tittel.")],
                      kvittering=None, fokusmal="feiloppsummering")
    assert '<a href="#dato">Velg et nytt tidspunkt fram i tid</a>' in html
    assert '<a href="#tittel">Skriv en tittel.</a>' in html


# ---------- stilark ----------


def _frontmatter_blokk(navn: str) -> dict[str, str]:
    """Leser en enkel `navn:`-blokk (nøkkel: verdi) fra frontmatter i DESIGN.md."""
    tekst = DESIGN_MD.read_text(encoding="utf-8").split("---")[1]
    blokk = re.search(rf"^{navn}:\n((?:[ ]{{2}}.*\n|\s*#.*\n)+)", tekst, re.M).group(1)
    verdier = {}
    for linje in blokk.splitlines():
        treff = re.match(r"\s+'?([\w-]+)'?:\s*(?:'([^']*)'|([^#\s]+))", linje)
        if treff:
            verdier[treff.group(1)] = treff.group(2) if treff.group(2) is not None else treff.group(3)
    return verdier


def test_stilarket_har_alle_fargetokenene_fra_design_md() -> None:
    """UX-DR1: hver farge i DESIGN.md er en CSS-variabel med samme verdi."""
    css = CSS.read_text(encoding="utf-8").lower()
    farger = _frontmatter_blokk("colors")
    assert len(farger) >= 37  # alle fargene i DESIGN.md per 2026-11-08
    for navn, verdi in farger.items():
        assert f"--color-{navn}: {verdi.lower()};" in css, f"--color-{navn} mangler eller er feil"


def test_stilarket_har_hjorner_og_avstander_fra_design_md() -> None:
    css = CSS.read_text(encoding="utf-8")
    for navn in _frontmatter_blokk("rounded"):
        assert f"--rounded-{navn}:" in css
    for navn in _frontmatter_blokk("spacing"):
        assert f"--spacing-{navn}:" in css


def test_stilarket_har_lyst_tema_systemskrifter_og_fokusring() -> None:
    """UX-DR1 og UX-DR4."""
    css = CSS.read_text(encoding="utf-8")
    assert "color-scheme: light;" in css
    assert "prefers-color-scheme" not in css
    assert "ui-rounded" in css and "system-ui" in css
    assert "@font-face" not in css and "fonts.googleapis" not in css
    assert "--focus-width: 3px;" in css and "--focus-offset: 3px;" in css
    assert "outline: var(--focus-width) solid var(--color-focus);" in css
    assert '[tabindex="-1"]:not(main):focus {' in css  # ring også ved trykk (UX-DR4)
    assert 'main[tabindex="-1"]:focus-visible {' in css  # main bare ved tastatur
    assert "@media (forced-colors: active)" in css
    assert "outline: none" not in css and "outline:none" not in css
    for forbudt in ("#fff;", "#ffffff", "#000;", "#000000"):
        assert forbudt not in css.lower()


def test_stilarket_bruker_rem_for_tekst() -> None:
    css = CSS.read_text(encoding="utf-8")
    assert "--text-body: 1.125rem;" in css
    assert not re.search(r"font-size:\s*\d+px", css)
