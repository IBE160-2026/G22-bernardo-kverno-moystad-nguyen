"""Sideramme og stilark (UX-DR1, UX-DR2, UX-DR4, AR-27)."""

from __future__ import annotations

import re
from html.parser import HTMLParser
from pathlib import Path

from fastapi.testclient import TestClient

from app.core.render import sidetittel

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
    assert '[tabindex="-1"]:focus' in css
    assert "@media (forced-colors: active)" in css
    assert "outline: none" not in css and "outline:none" not in css
    for forbudt in ("#fff;", "#ffffff", "#000;", "#000000"):
        assert forbudt not in css.lower()


def test_stilarket_bruker_rem_for_tekst() -> None:
    css = CSS.read_text(encoding="utf-8")
    assert "--text-body: 1.125rem;" in css
    assert not re.search(r"font-size:\s*\d+px", css)
