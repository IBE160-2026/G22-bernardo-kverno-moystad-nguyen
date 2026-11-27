"""T1: universell utforming i ekte nettleser (SM-5, NFR-6, NFR-7, UX-DR5, UX-DR31).

Hver side og tilstand fra Epic 1 og story 2.1–2.5 sjekkes
- med axe ved 360 og 1280 px: ingen brudd med `impact` «serious» eller «critical»,
- for vannrett rulling ved 320 px: `scrollWidth <= clientWidth` på `<html>`.

«Nytt oppdrag» står i to steg under 768 px og på én skjerm fra 768 px (story 2.2).
Ved 320 og 360 px sjekkes derfor steg 1, steg 2 og feil i begge steg, og en egen
test sjekker én skjerm ved 768 px (nettbrett, EXPERIENCE.md § T1).

Story 2.5 la til redigering, «Endre tidspunkt», detaljene for et utgått oppdrag,
bekreftelsesdialogen (åpen, fra detaljene og fra raden), bekreftelsessiden uten JS,
kvitteringen etter avbrudd og feilmeldingen etter en konflikt.

Story 2.7 la til oversikten og detaljene med bilde, «Nytt oppdrag» med bildefeil og
med beholdt bilde, og redigering av et oppdrag med bilde (FR-27, UX-DR33).

Ingen regler slås av, og ingen side utelates. Senere stories legger sine nye
sider og tilstander inn i `SIDER` (Definition of Done).
"""

from __future__ import annotations

from collections.abc import Callable

import re

import pytest
from axe_playwright_python.base import AXE_FILE_PATH
from axe_playwright_python.sync_playwright import Axe
from playwright.sync_api import Page, expect

from tests import bilder

from .conftest import OLA, fyll_ut_nytt_oppdrag, fyll_ut_steg_1, trykk_neste_hvis_synlig

pytestmark = pytest.mark.e2e

ALVORLIGE = frozenset({"serious", "critical"})
BREDDER_AXE = (360, 1280)
HOYDE = 800

# axe.min.js leses som UTF-8 (biblioteket bruker ellers systemets tegnsett på Windows).
axe = Axe.from_file(AXE_FILE_PATH)


# ---------- sidene og tilstandene ----------
# Hver funksjon får `page` og hjelperne og ender på siden som skal sjekkes.


def logg_inn_tom(page: Page, h: dict) -> None:
    page.goto("/logg-inn")
    expect(page.get_by_role("heading", level=1)).to_have_text("Logg inn")


def logg_inn_tom_innsending(page: Page, h: dict) -> None:
    page.goto("/logg-inn")
    page.get_by_role("button", name="Logg inn").click()
    expect(page.locator("#feiloppsummering")).to_be_visible()


def logg_inn_logget_ut(page: Page, h: dict) -> None:
    h["logg_inn_som_kari"](page)
    page.goto("/profil")
    page.get_by_role("button", name="Logg ut").click()
    expect(page.locator("#kvittering")).to_contain_text("Du er logget ut.")


def registrer_tom(page: Page, h: dict) -> None:
    page.goto("/registrer")
    expect(page.get_by_role("heading", level=1)).to_have_text("Registrering")


def registrer_tom_innsending(page: Page, h: dict) -> None:
    page.goto("/registrer")
    page.get_by_role("button", name="Opprett konto").click()
    expect(page.locator("#feiloppsummering")).to_be_visible()


def oversikt(page: Page, h: dict) -> None:
    """Ola i 0571 med fire kort (story 2.3). To av dem har bilde (story 2.7)."""
    h["logg_inn_som"](page, OLA)
    expect(page.locator("#antallslinje")).to_have_text("4 ledige oppdrag i 0571 Oslo")


def oversikt_kategori(page: Page, h: dict) -> None:
    """Ola velger «Hage»: ett kort, og fokus på den valgte lenken."""
    h["logg_inn_som"](page, OLA)
    page.get_by_role("link", name="Hage", exact=True).click()
    expect(page.locator("#antallslinje")).to_have_text("1 ledig oppdrag i Hage i 0571 Oslo")


def oversikt_tom_kategori(page: Page, h: dict) -> None:
    """Kari med «Hage»: hennes eget hageoppdrag vises ikke, så lista er tom."""
    h["logg_inn_som_kari"](page)
    page.goto("/?kategori=hage")
    expect(page.get_by_role("link", name="Vis alle kategorier")).to_be_visible()


def oversikt_tom(page: Page, h: dict) -> None:
    """Et postnummer uten oppdrag, med «Alle» valgt."""
    h["logg_inn_som"](page, OLA)
    page.goto("/?postnummer=0150")
    expect(page.get_by_role("link", name="Velg et annet postnummer")).to_be_visible()


def oversikt_postnummer_feil(page: Page, h: dict) -> None:
    """Ukjent postnummer: feilen ved feltet, og lista står uendret."""
    h["logg_inn_som"](page, OLA)
    page.get_by_label("Postnummer").fill("9999")
    page.get_by_label("Postnummer").press("Enter")
    expect(page.locator("#postnummer-feil")).to_have_text("Finner ikke postnummeret. Sjekk at det har fire siffer.")


def oppdrag_detaljer_andre(page: Page, h: dict) -> None:
    """Ola åpner Noras oppdrag fra kortet: oppdragsgiverblokken «Lagt ut av Nora Berg»."""
    h["logg_inn_som"](page, OLA)
    page.get_by_role("link", name="Mate katten i helgen").click()
    expect(page.get_by_role("heading", level=2, name="Lagt ut av Nora Berg")).to_be_visible()


def mine_oppdrag(page: Page, h: dict) -> None:
    """Kari med seks lenkerader, merket «Tidspunktet er passert» og tallet 1 i menyen (story 2.4)."""
    h["logg_inn_som_kari"](page)
    page.goto("/mine-oppdrag")
    expect(page.get_by_role("heading", level=1)).to_have_text("Mine oppdrag")
    expect(page.locator(".listerad")).to_have_count(6)
    expect(page.locator(".handlingsmerke")).to_have_count(1)
    expect(page.locator(".handlingsmerke")).to_contain_text("Tidspunktet er passert")
    expect(page.locator(".menytall:visible")).to_have_text("1")


def min_profil(page: Page, h: dict) -> None:
    h["logg_inn_som_kari"](page)
    page.goto("/profil")
    expect(page.get_by_role("button", name="Logg ut")).to_be_visible()


def andres_profil(page: Page, h: dict) -> None:
    h["logg_inn_som_kari"](page)
    page.goto(f"/profil/{h['bruker_id']('ola@eksempel.no')}")
    expect(page.get_by_role("heading", level=1)).to_have_text("Ola Hansen")


def fant_ikke_siden(page: Page, h: dict) -> None:
    h["logg_inn_som_kari"](page)
    svar = page.goto("/finnes-ikke")
    assert svar is not None and svar.status == 404
    expect(page.get_by_role("heading", level=1)).to_have_text("Fant ikke siden")


def logg_inn_igjen_401(page: Page, h: dict) -> None:
    """Sesjonscookien forsvinner mens profilen er åpen, og «Logg ut» gir 401-siden."""
    h["logg_inn_som_kari"](page)
    page.goto("/profil")
    page.context.clear_cookies(name="sesjon")
    page.get_by_role("button", name="Logg ut").click()
    expect(page.get_by_role("heading", level=1)).to_have_text("Du må logge inn igjen.")


def nytt_oppdrag(page: Page, h: dict) -> None:
    """Steg 1 under 768 px, én skjerm fra 768 px."""
    h["logg_inn_som_kari"](page)
    page.get_by_role("link", name="Legg ut oppdrag").click()
    expect(page.get_by_role("heading", level=1)).to_have_text(re.compile(r"^Nytt oppdrag( 1 av 2)?$"))


def nytt_oppdrag_steg_2(page: Page, h: dict) -> None:
    """Steg 2 etter «Neste», med forhåndsvisningen utfylt fra steg 1 (én skjerm fra 768 px)."""
    h["logg_inn_som_kari"](page)
    fyll_ut_steg_1(page)
    trykk_neste_hvis_synlig(page)
    expect(page.get_by_role("button", name="Publiser")).to_be_visible()


def nytt_oppdrag_feil(page: Page, h: dict) -> None:
    """Feil i begge steg: tittelen `ab` slipper gjennom «Neste», og steg 2 er tomt.

    Serveren gir feil i tittel (steg 1) og i dato, klokkeslett og «Hva tilbyr du?»
    (steg 2). I to steg vises steg 1, med feiloppsummeringen i fokus.
    """
    h["logg_inn_som_kari"](page)
    fyll_ut_steg_1(page, tittel="ab")
    trykk_neste_hvis_synlig(page)
    page.get_by_role("button", name="Publiser").click()
    expect(page.locator("#feiloppsummering")).to_contain_text("Skjemaet har 4 feil")


def nytt_oppdrag_neste_feil(page: Page, h: dict) -> None:
    """Feiloppsummeringen og feltfeilene som «Neste» lager i nettleseren (bare beskrivelsen er fylt ut).

    På én skjerm finnes ingen «Neste», og siden sjekkes som det tomme skjemaet.
    """
    h["logg_inn_som_kari"](page)
    page.goto("/oppdrag/ny")
    page.get_by_label("Hva trenger du hjelp til?").fill(
        "Trenger noen som kan måke snø i innkjørselen min i morgen."
    )
    neste = page.get_by_role("button", name="Neste")
    if neste.is_visible():
        neste.click()
        expect(page.locator("#feiloppsummering")).to_contain_text("Skjemaet har 2 feil")
        expect(page.locator("#feiloppsummering")).to_be_focused()


def nytt_oppdrag_feil_steg_2(page: Page, h: dict) -> None:
    """Serverfeil bare i steg 2 («Hva tilbyr du?» mangler): mobil viser steg 2 med oppsummeringen."""
    h["logg_inn_som_kari"](page)
    fyll_ut_steg_1(page)
    trykk_neste_hvis_synlig(page)
    page.get_by_label("Dato").fill("25.11.2026")
    page.get_by_label("Klokkeslett").fill("07:00")
    page.get_by_role("button", name="Publiser").click()
    expect(page.locator("#feiloppsummering")).to_contain_text("Skjemaet har 1 feil")
    expect(page.get_by_role("button", name="Publiser")).to_be_visible()


def oppdrag_detaljer(page: Page, h: dict) -> None:
    """Publisert gjennom skjemaet, med kvitteringen «Oppdraget er lagt ut.»."""
    h["logg_inn_som_kari"](page)
    fyll_ut_nytt_oppdrag(page)
    page.get_by_role("button", name="Publiser").click()
    expect(page.locator("#kvittering")).to_contain_text("Oppdraget er lagt ut.")


def mine_oppdrag_tom(page: Page, h: dict) -> None:
    """Ola har ikke lagt ut noen oppdrag (seed)."""
    h["logg_inn_som"](page, OLA)
    page.goto("/mine-oppdrag")
    expect(page.get_by_text("Du har ikke lagt ut noen oppdrag.")).to_be_visible()


MAKE = "Måke snø i innkjørselen"
BAERE = "Bære ved opp til tredje etasje"


def _kari_detaljer(page: Page, h: dict, tittel: str) -> None:
    h["logg_inn_som_kari"](page)
    page.goto("/mine-oppdrag")
    page.get_by_role("link", name=tittel, exact=True).click()
    expect(page.get_by_role("heading", level=1)).to_have_text(tittel)


def rediger_oppdrag(page: Page, h: dict) -> None:
    """Story 2.5: «Rediger» i detaljene gir skjemaet med de lagrede verdiene."""
    _kari_detaljer(page, h, MAKE)
    page.get_by_role("link", name="Rediger", exact=True).click()
    expect(page.get_by_role("heading", level=1)).to_have_text(f"Rediger «{MAKE}»")


def rediger_oppdrag_feil(page: Page, h: dict) -> None:
    """Tom tittel og beløp «abc»: feiloppsummeringen med to feil."""
    rediger_oppdrag(page, h)
    page.get_by_label("Tittel").fill("")
    page.get_by_label("Beløp i kr").fill("abc")
    page.get_by_role("button", name="Lagre endringer").click()
    expect(page.locator("#feiloppsummering")).to_contain_text("Skjemaet har 2 feil")


def endre_tidspunkt(page: Page, h: dict) -> None:
    """«Endre tidspunkt» i raden under «Mine oppdrag» gir skjemaet med fokus i «Dato»."""
    h["logg_inn_som_kari"](page)
    page.goto("/mine-oppdrag")
    page.get_by_role("link", name="Endre tidspunkt").click()
    expect(page.get_by_label("Dato")).to_be_focused()


def oppdrag_detaljer_passert(page: Page, h: dict) -> None:
    """Merket «Tidspunktet er passert», «Endre tidspunkt» (primær) og «Avbryt oppdrag»."""
    _kari_detaljer(page, h, BAERE)
    expect(page.get_by_role("link", name="Endre tidspunkt")).to_be_visible()


def avbryt_dialog_detaljer(page: Page, h: dict) -> None:
    """Dialogen «Avbryte «…»?» åpen over detaljene."""
    _kari_detaljer(page, h, MAKE)
    page.get_by_role("link", name="Avbryt oppdrag").click()
    expect(page.get_by_role("dialog", name=f"Avbryte «{MAKE}»?")).to_be_visible()


def avbryt_dialog_rad(page: Page, h: dict) -> None:
    """Dialogen åpnet fra snarveien i raden under «Mine oppdrag»."""
    h["logg_inn_som_kari"](page)
    page.goto("/mine-oppdrag")
    page.get_by_role("link", name="Avbryt oppdrag").click()
    expect(page.get_by_role("dialog", name=f"Avbryte «{BAERE}»?")).to_be_visible()


def avbryt_bekreftelse(page: Page, h: dict) -> None:
    """Bekreftelsessiden uten JS (GET), åpnet direkte fra lenken."""
    _kari_detaljer(page, h, MAKE)
    page.goto(page.get_by_role("link", name="Avbryt oppdrag").get_attribute("href"))
    expect(page.get_by_role("heading", level=1)).to_have_text(f"Avbryte «{MAKE}»?")


def oppdrag_avbrutt(page: Page, h: dict) -> None:
    """«Ja, avbryt oppdraget» i dialogen: detaljene med kvitteringen og status Avbrutt."""
    avbryt_dialog_detaljer(page, h)
    page.get_by_role("button", name="Ja, avbryt oppdraget").click()
    expect(page.locator("#kvittering")).to_contain_text("Oppdraget er avbrutt.")


def konflikt(page: Page, h: dict) -> None:
    """To faner: avbrutt i den andre, så «Ja, avbryt oppdraget» i den første gir feilmeldingen."""
    avbryt_dialog_detaljer(page, h)
    fane_2 = page.context.new_page()
    try:
        fane_2.goto(page.url)
        fane_2.get_by_role("link", name="Avbryt oppdrag").click()
        fane_2.get_by_role("button", name="Ja, avbryt oppdraget").click()
        expect(fane_2.locator("#kvittering")).to_contain_text("Oppdraget er avbrutt.")
    finally:
        fane_2.close()
    page.get_by_role("button", name="Ja, avbryt oppdraget").click()
    expect(page.locator("#feilmelding")).to_contain_text("Oppdraget er endret. Last siden på nytt.")


# ---------- bilde (story 2.7, FR-27, UX-DR33) ----------


def oversikt_med_bilde(page: Page, h: dict) -> None:
    """Ola i 0571: to av fire kort har miniatyren øverst, og bildene er lastet."""
    h["logg_inn_som"](page, OLA)
    bildene = page.locator("img.kort__bilde")
    expect(bildene).to_have_count(2)
    for nummer in range(2):
        bildene.nth(nummer).scroll_into_view_if_needed()
        expect(bildene.nth(nummer)).to_have_js_property("complete", True)


def oppdrag_detaljer_med_bilde(page: Page, h: dict) -> None:
    """Ola åpner «Mate katten i helgen»: bildet under tittelen, med bildeteksten som alt."""
    h["logg_inn_som"](page, OLA)
    page.get_by_role("link", name="Mate katten i helgen").click()
    expect(page.get_by_role("img", name="Matskål og vannskål på kjøkkengulvet")).to_be_visible()


def _velg_bilde(page: Page, data: bytes, navn: str) -> None:
    page.locator("#bilde").set_input_files(files=[{"name": navn, "mimeType": "image/jpeg", "buffer": data}])


def nytt_oppdrag_bildefeil(page: Page, h: dict) -> None:
    """En tekstfil som heter `bilde.jpg`: serveren gir «Velg et bilde i JPEG, PNG eller WebP.»
    ved bildet, og mobil viser steg 1."""
    h["logg_inn_som_kari"](page)
    fyll_ut_steg_1(page)
    _velg_bilde(page, bilder.TEKST, "bilde.jpg")
    page.get_by_label("Hva viser bildet?").fill("Snø i innkjørselen")
    trykk_neste_hvis_synlig(page)
    page.get_by_label("Dato").fill("25.11.2026")
    page.get_by_label("Klokkeslett").fill("07:00")
    page.get_by_label("Uten betaling").check()
    page.get_by_role("button", name="Publiser").click()
    expect(page.locator("#bilde-feil")).to_contain_text("Velg et bilde i JPEG, PNG eller WebP.")
    expect(page.locator("#bilde")).to_be_visible()


def nytt_oppdrag_beholdt_bilde(page: Page, h: dict) -> None:
    """Gyldig bilde uten bildetekst: feilen ved «Hva viser bildet?», og bildet beholdes som
    miniatyr med «Fjern bildet»."""
    h["logg_inn_som_kari"](page)
    fyll_ut_steg_1(page)
    _velg_bilde(page, bilder.jpeg(800, 600), "bilde.jpg")
    trykk_neste_hvis_synlig(page)
    page.get_by_label("Dato").fill("25.11.2026")
    page.get_by_label("Klokkeslett").fill("07:00")
    page.get_by_label("Uten betaling").check()
    page.get_by_role("button", name="Publiser").click()
    expect(page.locator("#bildetekst-feil")).to_contain_text("Skriv hva bildet viser.")
    expect(page.get_by_label("Fjern bildet")).to_be_visible()
    expect(page.locator("img.beholdt-bilde__miniatyr")).to_have_js_property("complete", True)


def rediger_oppdrag_med_bilde(page: Page, h: dict) -> None:
    """«Rediger» på «Måke snø»: det lagrede bildet med «Bytt bilde» og «Fjern bildet»."""
    rediger_oppdrag(page, h)
    expect(page.get_by_label("Bytt bilde")).to_be_visible()
    expect(page.get_by_label("Fjern bildet")).to_be_visible()
    expect(page.get_by_label("Hva viser bildet?")).to_have_value("Snødekt innkjørsel med en spade")


SIDER: dict[str, Callable[[Page, dict], None]] = {
    "logg-inn": logg_inn_tom,
    "logg-inn-tom-innsending": logg_inn_tom_innsending,
    "logg-inn-logget-ut": logg_inn_logget_ut,
    "registrer": registrer_tom,
    "registrer-tom-innsending": registrer_tom_innsending,
    "oversikt": oversikt,
    "mine-oppdrag": mine_oppdrag,
    "profil": min_profil,
    "profil-andre": andres_profil,
    "404": fant_ikke_siden,
    "401": logg_inn_igjen_401,
    # Story 2.1
    "nytt-oppdrag": nytt_oppdrag,
    "nytt-oppdrag-feil": nytt_oppdrag_feil,
    "oppdrag-detaljer": oppdrag_detaljer,
    "mine-oppdrag-tom": mine_oppdrag_tom,
    # Story 2.2
    "nytt-oppdrag-steg-2": nytt_oppdrag_steg_2,
    "nytt-oppdrag-neste-feil": nytt_oppdrag_neste_feil,
    "nytt-oppdrag-feil-steg-2": nytt_oppdrag_feil_steg_2,
    # Story 2.3
    "oversikt-kategori": oversikt_kategori,
    "oversikt-tom-kategori": oversikt_tom_kategori,
    "oversikt-tom": oversikt_tom,
    "oversikt-postnummer-feil": oversikt_postnummer_feil,
    "oppdrag-detaljer-andre": oppdrag_detaljer_andre,
    # Story 2.5
    "rediger-oppdrag": rediger_oppdrag,
    "rediger-oppdrag-feil": rediger_oppdrag_feil,
    "endre-tidspunkt": endre_tidspunkt,
    "oppdrag-detaljer-passert": oppdrag_detaljer_passert,
    "avbryt-dialog-detaljer": avbryt_dialog_detaljer,
    "avbryt-dialog-rad": avbryt_dialog_rad,
    "avbryt-bekreftelse": avbryt_bekreftelse,
    "oppdrag-avbrutt": oppdrag_avbrutt,
    "konflikt": konflikt,
    # Story 2.7
    "oversikt-med-bilde": oversikt_med_bilde,
    "oppdrag-detaljer-med-bilde": oppdrag_detaljer_med_bilde,
    "nytt-oppdrag-bildefeil": nytt_oppdrag_bildefeil,
    "nytt-oppdrag-beholdt-bilde": nytt_oppdrag_beholdt_bilde,
    "rediger-oppdrag-med-bilde": rediger_oppdrag_med_bilde,
}

# «Nytt oppdrag» på én skjerm ved 768 px (nettbrett): de samme tilstandene som i to steg.
SIDER_EN_SKJERM = ("nytt-oppdrag", "nytt-oppdrag-steg-2", "nytt-oppdrag-feil")


@pytest.fixture
def hjelpere(logg_inn_som_kari, logg_inn_som, bruker_id) -> dict:
    return {"logg_inn_som_kari": logg_inn_som_kari, "logg_inn_som": logg_inn_som, "bruker_id": bruker_id}


def alvorlige_brudd(page: Page) -> list[str]:
    """axe-brudd med impact «serious» eller «critical», én linje per element."""
    resultat = axe.run(page)
    linjer = []
    for brudd in resultat.response["violations"]:
        if brudd.get("impact") not in ALVORLIGE:
            continue
        for node in brudd["nodes"]:
            selektor = " ".join(str(del_) for del_ in node["target"])
            linjer.append(f"{brudd['id']} ({brudd['impact']}): {selektor} – {brudd['help']}")
    return linjer


RULLING = "() => [document.documentElement.scrollWidth, document.documentElement.clientWidth]"


def test_axe_og_rulling_fanger_bevisst_brudd(page: Page) -> None:
    """Kanari for akseptansekriterium 3: sjekkene i T1 kan faktisk feile."""
    page.set_viewport_size({"width": 320, "height": 640})
    page.set_content(
        '<!doctype html><html lang="nb"><head><title>Kanari</title></head><body><main>'
        '<h1>Kanari</h1><input type="text"><div style="width: 400px">bred</div>'
        "</main></body></html>"
    )
    brudd = alvorlige_brudd(page)
    assert any(linje.startswith("label (critical)") for linje in brudd), brudd
    scroll, klient = page.evaluate(RULLING)
    assert scroll > klient, (scroll, klient)


@pytest.mark.parametrize("bredde", BREDDER_AXE, ids=lambda b: f"{b}px")
@pytest.mark.parametrize("side", list(SIDER))
def test_axe_ingen_alvorlige_brudd(page: Page, hjelpere: dict, side: str, bredde: int) -> None:
    """NFR-6, SM-5: ingen brudd «serious» eller «critical» ved 360 og 1280 px."""
    page.set_viewport_size({"width": bredde, "height": HOYDE})
    SIDER[side](page, hjelpere)
    brudd = alvorlige_brudd(page)
    assert not brudd, f"axe fant brudd på «{side}» ved {bredde} px:\n" + "\n".join(brudd)


@pytest.mark.parametrize("side", SIDER_EN_SKJERM)
def test_nytt_oppdrag_pa_en_skjerm_ved_768(page: Page, hjelpere: dict, side: str) -> None:
    """NFR-6, UX-DR16, SM-5: fra 768 px står «Nytt oppdrag» på én skjerm, uten brudd i axe."""
    page.set_viewport_size({"width": 768, "height": HOYDE})
    SIDER[side](page, hjelpere)
    expect(page.get_by_role("heading", level=1)).to_have_text("Nytt oppdrag")
    expect(page.get_by_role("heading", level=2, name="Når og hvor?")).to_be_visible()
    expect(page.get_by_role("button", name="Neste")).to_be_hidden()
    brudd = alvorlige_brudd(page)
    assert not brudd, f"axe fant brudd på «{side}» på én skjerm ved 768 px:\n" + "\n".join(brudd)


@pytest.mark.parametrize("side", list(SIDER))
def test_ingen_vannrett_rulling_ved_320(page: Page, hjelpere: dict, side: str) -> None:
    """NFR-7, UX-DR31: ingen vannrett rulling ved 320 px."""
    page.set_viewport_size({"width": 320, "height": 640})
    SIDER[side](page, hjelpere)
    scroll, klient = page.evaluate(RULLING)
    assert scroll <= klient, (
        f"Vannrett rulling på «{side}» ved 320 px: scrollWidth {scroll} > clientWidth {klient}"
    )
