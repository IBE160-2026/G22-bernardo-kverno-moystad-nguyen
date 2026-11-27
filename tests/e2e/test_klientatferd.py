"""Oppførsel som bare kan sjekkes i ekte nettleser (UX-DR3, UX-DR13, UX-DR28, NFR-11).

Testene som var utsatt til T1: «Vis passord» og sendeknappen fra story 1.2, og
`poststed.js` fra story 1.4 (`deferred-work.md`). Menyen ved 360 og 1280 px
kom med T-1 (V3 i retro Epic 1): axe ser ikke en skjult `nav`. Telleren i
`skjema.js` og dobbeltklikk på «Publiser» kom med story 2.1 (NFR-5, UX-DR13, UX-DR28).
«Nytt oppdrag» i to steg under 768 px (`steg.js`), forhåndsvisningen i `skjema.js`
og «Beløp i kr» med CSS `:has` kom med story 2.2 (FR-5, NFR-7, UX-DR13, UX-DR15,
UX-DR16, UX-DR27, UX-DR28).
"""

from __future__ import annotations

import re
from collections.abc import Callable

import pytest
from playwright.sync_api import Page, expect

from ..oppdrag.test_to_steg import kort as kort_fra_serveren
from .conftest import KARI, _logg_inn, fyll_ut_nytt_oppdrag, fyll_ut_steg_1

pytestmark = pytest.mark.e2e

# En lytter på `window` kjører etter lytterne på `document` (vis_passord.js og
# sending.js). Den noterer det skjemaet ser ut som ved innsending, og om
# innsendingen allerede er stoppet, og stopper den selv så siden blir stående.
NOTER_INNSENDING = """() => {
  window.innsendinger = [];
  window.addEventListener("submit", (hendelse) => {
    window.innsendinger.push({
      stoppet: hendelse.defaultPrevented,
      passordtype: document.getElementById("passord").type,
    });
    hendelse.preventDefault();
  });
}"""


def test_vis_passord(page: Page) -> None:
    """UX-DR13: knappen viser og skjuler passordet, og passordet sendes aldri som synlig tekst."""
    page.goto("/logg-inn")
    knapp = page.get_by_role("button", name="Vis passord")
    felt = page.locator("#passord")
    expect(knapp).to_be_visible()
    expect(knapp).to_have_attribute("aria-pressed", "false")
    felt.fill("hemmelig-1")

    knapp.click()
    expect(felt).to_have_attribute("type", "text")
    expect(knapp).to_have_attribute("aria-pressed", "true")

    knapp.click()
    expect(felt).to_have_attribute("type", "password")
    expect(knapp).to_have_attribute("aria-pressed", "false")

    knapp.click()
    expect(felt).to_have_attribute("type", "text")
    page.evaluate(NOTER_INNSENDING)
    page.get_by_role("button", name="Logg inn").click()
    assert page.evaluate("() => window.innsendinger") == [
        {"stoppet": False, "passordtype": "password"}
    ]
    expect(knapp).to_have_attribute("aria-pressed", "false")


def test_sendeknappen_far_aria_disabled_og_stopper_ny_innsending(page: Page) -> None:
    """UX-DR28: `aria-disabled` til svaret kommer, andre innsending stoppes, `pageshow` nullstiller."""
    page.goto("/logg-inn")
    page.evaluate(NOTER_INNSENDING)
    send = page.get_by_role("button", name="Logg inn")
    expect(send).not_to_have_attribute("aria-disabled", "true")

    send.click()
    expect(send).to_have_attribute("aria-disabled", "true")

    # Enter i feltet sender skjemaet på nytt, selv om knappen er aria-disabled.
    page.locator("#epost").press("Enter")
    assert page.evaluate("() => window.innsendinger.map((i) => i.stoppet)") == [False, True]
    expect(send).to_have_attribute("aria-disabled", "true")

    # Som når brukeren kommer tilbake med tilbakeknappen.
    page.evaluate("() => window.dispatchEvent(new PageTransitionEvent('pageshow', { persisted: true }))")
    expect(send).not_to_have_attribute("aria-disabled", "true")
    expect(send).not_to_have_attribute("data-sender", "")

    # Skjemaet er ikke låst: en ny innsending går gjennom og gir aria-disabled igjen.
    page.locator("#epost").press("Enter")
    assert page.evaluate("() => window.innsendinger.map((i) => i.stoppet)") == [False, True, False]
    expect(send).to_have_attribute("aria-disabled", "true")


def test_poststed_vises_ved_gyldig_postnummer(page: Page) -> None:
    """UX-DR13: poststedet vises ved fire siffer som finnes, ellers ingenting."""
    page.goto("/registrer")
    postnummer = page.get_by_label("Postnummer")
    sted = page.locator("#postnummer-sted")
    expect(sted).to_have_text("")

    postnummer.fill("5006")
    expect(sted).to_have_text("Bergen")

    # Fire siffer som ikke finnes i registeret.
    postnummer.fill("0000")
    expect(sted).to_have_text("")

    postnummer.fill("5006")
    expect(sted).to_have_text("Bergen")

    postnummer.fill("57")
    expect(sted).to_have_text("")


@pytest.mark.parametrize(
    ("bredde", "synlig", "skjult"),
    [
        (360, ".meny--bunn", ".meny--topp"),
        (767, ".meny--bunn", ".meny--topp"),
        (768, ".meny--topp", ".meny--bunn"),
        (1280, ".meny--topp", ".meny--bunn"),
    ],
    ids=["360px-bunnmeny", "767px-bunnmeny", "768px-topplinje", "1280px-topplinje"],
)
def test_riktig_meny_ved_bredden(
    page: Page,
    logg_inn_som_kari: Callable[[Page], None],
    bredde: int,
    synlig: str,
    skjult: str,
) -> None:
    """NFR-11, UX-DR3: bare bunnmenyen under 768 px, bare topplinjemenyen fra 768 px.

    Skjermlesere finner én «Hovedmeny», med de tre valgene.
    """
    page.set_viewport_size({"width": bredde, "height": 800})
    logg_inn_som_kari(page)
    expect(page.locator(synlig)).to_be_visible()
    expect(page.locator(skjult)).to_be_hidden()
    hovedmeny = page.get_by_role("navigation", name="Hovedmeny")
    expect(hovedmeny).to_have_count(1)
    expect(hovedmeny.get_by_role("link")).to_have_text(["Oppdrag", "Mine oppdrag", "Profil"])


def test_telleren_teller_tegn_og_varsler_ved_grensen(
    page: Page, logg_inn_som_kari: Callable[[Page], None]
) -> None:
    """UX-DR13, AD-10: «e» + kombinerende akutt teller 1; varselet får tekst bare ved 1000 tegn."""
    logg_inn_som_kari(page)
    page.goto("/oppdrag/ny")
    felt = page.get_by_label("Hva trenger du hjelp til?")
    teller = page.locator("#beskrivelse-teller")
    varsel = page.locator("#beskrivelse-varsel")
    expect(teller).to_have_text("0 av 1000 tegn")
    expect(teller).not_to_have_attribute("aria-live", "polite")
    expect(varsel).to_have_attribute("aria-live", "polite")

    felt.fill("e\u0301")
    expect(teller).to_have_text("1 av 1000 tegn")
    felt.fill("  Hei  ")
    expect(teller).to_have_text("3 av 1000 tegn")
    expect(varsel).to_have_text("")

    felt.fill("a" * 999 + "e\u0301")
    expect(teller).to_have_text("1000 av 1000 tegn")
    expect(varsel).to_have_text("1000 av 1000 tegn")

    felt.fill("a" * 1001)
    expect(teller).to_have_text("1001 av 1000 tegn")
    expect(varsel).to_have_text("1000 av 1000 tegn")  # leses ikke opp for hvert tegn

    felt.fill("a" * 999)
    expect(teller).to_have_text("999 av 1000 tegn")
    expect(varsel).to_have_text("")

    # Nettleseren setter verdien uten `input` (tilbakeknappen): `pageshow` retter telleren uten opplesning.
    page.evaluate("""() => {
      document.getElementById("beskrivelse").value = "Fem t";
      window.dispatchEvent(new PageTransitionEvent("pageshow", { persisted: true }));
    }""")
    expect(teller).to_have_text("5 av 1000 tegn")
    expect(varsel).to_have_text("")


def test_dobbeltklikk_pa_publiser_gir_ett_oppdrag(
    page: Page, logg_inn_som_kari: Callable[[Page], None], antall_oppdrag: Callable[[str], int]
) -> None:
    """NFR-5, UX-DR28: knappen får `aria-disabled`, andre klikk sender ikke, og databasen får én rad.

    De to klikkene kjøres i samme skript, før navigasjonen starter. Det er det
    verste tilfellet: siden står fortsatt, og andre klikk må stoppes av sending.js.
    """
    tittel = "Dobbeltklikk-testen"
    logg_inn_som_kari(page)
    fyll_ut_nytt_oppdrag(page, tittel=tittel)
    poster: list[str] = []
    page.on("request", lambda r: poster.append(r.url) if r.method == "POST" else None)

    with page.expect_navigation():
        knapp, innsendinger = page.evaluate(
            """() => {
              const innsendinger = [];
              window.addEventListener("submit", (hendelse) => innsendinger.push(hendelse.defaultPrevented));
              const knapp = document.querySelector('.skjema button[type="submit"]');
              knapp.click();
              knapp.click();
              return [knapp.getAttribute("aria-disabled"), innsendinger];
            }"""
        )
    assert knapp == "true"
    assert innsendinger == [False, True]  # andre klikk stoppes i nettleseren
    expect(page.locator("#kvittering")).to_contain_text("Oppdraget er lagt ut.")
    assert len([u for u in poster if u.endswith("/oppdrag/ny")]) == 1
    assert antall_oppdrag(tittel) == 1


# ---------- «Nytt oppdrag» i to steg (story 2.2) ----------

MOBIL = {"width": 360, "height": 800}
NBSP = "\u00a0"
TITTEL_STEG_1 = "Nytt oppdrag, steg 1 av 2 – Nabolagshelten"
TITTEL_STEG_2 = "Nytt oppdrag, steg 2 av 2 – Nabolagshelten"


def poster(page: Page) -> list[str]:
    """Adressene til alle POST-forespørsler siden lista ble laget."""
    liste: list[str] = []
    page.on("request", lambda r: liste.append(r.url) if r.method == "POST" else None)
    return liste


def apne_nytt_oppdrag_mobil(page: Page, logg_inn_som_kari: Callable[[Page], None]) -> None:
    page.set_viewport_size(MOBIL)
    logg_inn_som_kari(page)
    page.goto("/oppdrag/ny")
    expect(page.get_by_role("heading", level=1)).to_have_text("Nytt oppdrag 1 av 2")


def h1(page: Page):
    return page.get_by_role("heading", level=1)


def test_mobil_steg_1_viser_bare_forste_del(page: Page, logg_inn_som_kari: Callable[[Page], None]) -> None:
    """UX-DR16: «Nytt oppdrag 1 av 2», tittelen for steg 1, «Neste», og steg 2 og begge h2 skjult."""
    apne_nytt_oppdrag_mobil(page, logg_inn_som_kari)
    expect(page).to_have_title(TITTEL_STEG_1)
    expect(page.get_by_label("Hva trenger du hjelp til?")).to_be_focused()  # autofocus
    for synlig in ("Hva trenger du hjelp til?", "Tittel"):
        expect(page.get_by_label(synlig)).to_be_visible()
    expect(page.get_by_role("group", name="Kategori")).to_be_visible()
    expect(page.get_by_role("button", name="Neste")).to_be_visible()
    expect(page.get_by_role("link", name="Tilbake", exact=True)).to_be_visible()
    expect(page.locator('[data-steg="2"]')).to_be_hidden()
    expect(page.get_by_role("button", name="Publiser")).to_be_hidden()
    expect(page.get_by_role("heading", level=2)).to_have_count(0)


def test_neste_med_tomme_felt_viser_feil_uten_foresporsel(
    page: Page, logg_inn_som_kari: Callable[[Page], None]
) -> None:
    """UX-DR16, UX-DR22, UX-DR27: oppsummering rett etter h1 i fokus, feltfeil og aria-invalid, ingen POST."""
    apne_nytt_oppdrag_mobil(page, logg_inn_som_kari)
    sendt = poster(page)
    page.get_by_label("Hva trenger du hjelp til?").fill("Trenger hjelp med snømåking i morgen.")
    page.get_by_label("Tittel").fill("   ")
    page.get_by_role("button", name="Neste").click()

    oppsummering = page.locator("#feiloppsummering")
    expect(oppsummering).to_be_focused()
    expect(oppsummering.get_by_role("heading", level=2)).to_have_text("Skjemaet har 2 feil")
    expect(oppsummering.get_by_role("link")).to_have_text(["Skriv en tittel.", "Velg en kategori."])
    expect(oppsummering).to_have_attribute("tabindex", "-1")
    expect(oppsummering).not_to_have_attribute("role", re.compile(".+"))
    assert page.evaluate("() => document.querySelector('main h1').nextElementSibling.id") == "feiloppsummering"
    expect(page.locator("#tittel-feil")).to_have_text("Skriv en tittel.")
    expect(page.locator("#kategori-feil")).to_have_text("Velg en kategori.")
    expect(page.get_by_label("Tittel")).to_have_attribute("aria-invalid", "true")
    expect(page.get_by_label("Tittel")).to_have_attribute("aria-describedby", "tittel-feil")
    expect(page.locator("#kategori-hage")).to_have_attribute("aria-invalid", "true")
    expect(page.get_by_label("Hva trenger du hjelp til?")).not_to_have_attribute("aria-invalid", "true")
    expect(page).to_have_title("Feil: " + TITTEL_STEG_1)
    expect(h1(page)).to_have_text("Nytt oppdrag 1 av 2")

    # Lenken i oppsummeringen går til feltet i samme steg.
    oppsummering.get_by_role("link", name="Skriv en tittel.").click()
    expect(page.get_by_label("Tittel")).to_be_focused()

    # Rettet: klientfeilene forsvinner, og steg 2 vises.
    page.get_by_label("Tittel").fill("Måke snø")
    page.locator('label[for="kategori-snomaking"]').click()
    page.get_by_role("button", name="Neste").click()
    expect(h1(page)).to_have_text("Nytt oppdrag 2 av 2")
    expect(page.locator("#feiloppsummering")).to_have_count(0)
    expect(page.locator(".feltfeil")).to_have_count(0)
    expect(page.locator("[aria-invalid]")).to_have_count(0)
    expect(page.get_by_label("Tittel")).not_to_have_attribute("aria-describedby", re.compile(".*"))
    expect(page).to_have_title(TITTEL_STEG_2)
    assert sendt == []


def test_neste_og_tilbake_gir_fokus_til_h1_og_beholder_verdiene(
    page: Page, logg_inn_som_kari: Callable[[Page], None]
) -> None:
    """UX-DR16, UX-DR27: fokus på h1, `<title>` byttes, alt utfylt beholdes, ingen POST."""
    page.set_viewport_size(MOBIL)
    logg_inn_som_kari(page)
    sendt = poster(page)
    fyll_ut_steg_1(page)
    page.get_by_role("button", name="Neste").click()

    expect(h1(page)).to_have_text("Nytt oppdrag 2 av 2")
    expect(h1(page)).to_be_focused()
    expect(page).to_have_title(TITTEL_STEG_2)
    expect(page.locator('[data-steg="1"]')).to_be_hidden()
    expect(page.get_by_role("link", name="Tilbake", exact=True)).to_be_hidden()
    for synlig in ("Postnummer", "Dato", "Klokkeslett"):
        expect(page.get_by_label(synlig)).to_be_visible()
    expect(page.get_by_role("region", name="Slik vises oppdraget for andre.")).to_be_visible()
    expect(page.get_by_role("button", name="Publiser")).to_be_visible()
    expect(page.get_by_role("button", name="Neste")).to_be_hidden()

    page.get_by_role("button", name="Tilbake til steg 1").click()
    expect(h1(page)).to_have_text("Nytt oppdrag 1 av 2")
    expect(h1(page)).to_be_focused()
    expect(page).to_have_title(TITTEL_STEG_1)
    expect(page.get_by_label("Tittel")).to_have_value("Måke snø i innkjørselen")
    expect(page.locator("#kategori-snomaking")).to_be_checked()
    expect(page.get_by_role("button", name="Tilbake til steg 1")).to_be_hidden()
    assert sendt == []


def test_enter_i_steg_1_virker_som_neste_og_publiser_virker_etterpa(
    page: Page, logg_inn_som_kari: Callable[[Page], None], antall_oppdrag: Callable[[str], int]
) -> None:
    """UX-DR16, UX-DR28, akseptansekriterium 1: Enter i Tittel gir steg 2 uten POST. «Publiser»
    er ikke låst etterpå, får `aria-disabled`, og Kari havner på detaljene med kvitteringen."""
    tittel = "Enter-testen"
    page.set_viewport_size(MOBIL)
    logg_inn_som_kari(page)
    sendt = poster(page)
    fyll_ut_steg_1(page, tittel=tittel)
    page.get_by_label("Tittel").press("Enter")
    expect(h1(page)).to_have_text("Nytt oppdrag 2 av 2")
    expect(h1(page)).to_be_focused()
    assert sendt == []
    expect(page.locator("form[data-sender]")).to_have_count(0)

    page.get_by_label("Dato").fill("25.11.2026")
    page.get_by_label("Klokkeslett").fill("07:00")
    page.get_by_label("Beløp", exact=True).check()
    page.get_by_label("Beløp i kr").fill("200")
    with page.expect_navigation():
        deaktivert = page.evaluate(
            """() => {
              const knapp = document.querySelector('.skjema button[type="submit"]');
              knapp.click();
              return knapp.getAttribute("aria-disabled");
            }"""
        )
    assert deaktivert == "true"
    expect(page.locator("#kvittering")).to_contain_text("Oppdraget er lagt ut.")
    expect(page.locator("#kvittering")).to_be_focused()
    assert len([u for u in sendt if u.endswith("/oppdrag/ny")]) == 1
    assert antall_oppdrag(tittel) == 1


def test_serverfeil_viser_steget_med_forste_feil_og_lenken_bytter_steg(
    page: Page, logg_inn_som_kari: Callable[[Page], None]
) -> None:
    """UX-DR16, UX-DR22: tittel `ab` og tom dato gir 422 med steg 1 vist; lenken til datoen bytter steg."""
    page.set_viewport_size(MOBIL)
    logg_inn_som_kari(page)
    fyll_ut_steg_1(page, tittel="ab")
    page.get_by_role("button", name="Neste").click()
    page.get_by_label("Klokkeslett").fill("07:00")
    page.get_by_label("Uten betaling").check()
    with page.expect_response(lambda r: r.request.method == "POST") as svar:
        page.get_by_role("button", name="Publiser").click()
    assert svar.value.status == 422

    oppsummering = page.locator("#feiloppsummering")
    expect(oppsummering.get_by_role("link")).to_have_text(["Tittelen må ha minst 3 tegn.", "Skriv datoen."])
    expect(oppsummering).to_be_focused()
    expect(h1(page)).to_have_text("Nytt oppdrag 1 av 2")
    expect(page).to_have_title("Feil: " + TITTEL_STEG_1)
    expect(page.get_by_label("Tittel")).to_be_visible()
    expect(page.get_by_label("Dato")).to_be_hidden()

    oppsummering.get_by_role("link", name="Skriv datoen.").click()
    expect(h1(page)).to_have_text("Nytt oppdrag 2 av 2")
    expect(page.locator("#dato")).to_be_focused()
    expect(page).to_have_title("Feil: " + TITTEL_STEG_2)
    expect(page.get_by_label("Tittel")).to_be_hidden()


def test_serverfeil_bare_i_steg_2_viser_steg_2(page: Page, logg_inn_som_kari: Callable[[Page], None]) -> None:
    """UX-DR16: bare «Hva tilbyr du?» mangler, så steg 2 vises med oppsummeringen i fokus."""
    page.set_viewport_size(MOBIL)
    logg_inn_som_kari(page)
    fyll_ut_steg_1(page)
    page.get_by_role("button", name="Neste").click()
    page.get_by_label("Dato").fill("25.11.2026")
    page.get_by_label("Klokkeslett").fill("07:00")
    page.get_by_role("button", name="Publiser").click()

    oppsummering = page.locator("#feiloppsummering")
    expect(oppsummering.get_by_role("link")).to_have_text(["Velg beløp eller uten betaling."])
    expect(oppsummering).to_be_focused()
    expect(h1(page)).to_have_text("Nytt oppdrag 2 av 2")
    expect(page).to_have_title("Feil: " + TITTEL_STEG_2)
    expect(page.get_by_label("Dato")).to_have_value("25.11.2026")


def test_endret_bredde_bytter_mellom_en_skjerm_og_to_steg(
    page: Page, logg_inn_som_kari: Callable[[Page], None]
) -> None:
    """UX-DR16: steg 2 → 900 px gir én skjerm, → 360 px gir steg 1 igjen. Verdiene beholdes."""
    page.set_viewport_size(MOBIL)
    logg_inn_som_kari(page)
    fyll_ut_steg_1(page)
    page.get_by_role("button", name="Neste").click()
    page.get_by_label("Dato").fill("25.11.2026")

    page.set_viewport_size({"width": 900, "height": 800})
    expect(h1(page)).to_have_text("Nytt oppdrag")
    expect(page).to_have_title("Nytt oppdrag – Nabolagshelten")
    expect(page.get_by_role("heading", level=2)).to_have_text(["Hva trenger du hjelp til?", "Når og hvor?"])
    expect(page.get_by_label("Tittel")).to_be_visible()
    expect(page.get_by_label("Dato")).to_be_visible()
    expect(page.get_by_role("button", name="Neste")).to_be_hidden()
    expect(page.get_by_role("button", name="Tilbake til steg 1")).to_be_hidden()
    expect(page.get_by_role("link", name="Tilbake", exact=True)).to_be_visible()

    page.set_viewport_size(MOBIL)
    expect(h1(page)).to_have_text("Nytt oppdrag 1 av 2")
    expect(page).to_have_title(TITTEL_STEG_1)
    expect(page.get_by_label("Dato")).to_be_hidden()
    expect(page.get_by_label("Tittel")).to_have_value("Måke snø i innkjørselen")
    expect(page.get_by_label("Dato")).to_have_value("25.11.2026")


FORHANDSVISNING = """() => {
  const kort = document.querySelector("[data-forhandsvisning]");
  const tekst = (felt) => kort.querySelector(`[data-felt="${felt}"]`).textContent.trim();
  return {
    kategori: tekst("kategori"), tittel: tekst("tittel"), tid: tekst("tid"), sted: tekst("sted"),
    pris: tekst("pris"), ikon: !!kort.querySelector('[data-felt="kategori"] svg'),
    aktiv: document.activeElement.id,
    live: !!kort.closest("[aria-live]") || kort.querySelectorAll("[aria-live], [role]").length > 0,
  };
}"""


@pytest.mark.parametrize("bredde", [360, 1280], ids=["mobil-steg-2", "en-skjerm"])
def test_forhandsvisningen_folger_feltene_uten_opplesning(
    page: Page, logg_inn_som_kari: Callable[[Page], None], bredde: int
) -> None:
    """UX-DR15, akseptansekriterium 2: kortet oppdateres når feltene endres, fokus blir i feltet,
    og kortet har ingen `aria-live`. Poststedet fra poststed.js kommer med."""
    page.set_viewport_size({"width": bredde, "height": 800})
    logg_inn_som_kari(page)
    page.goto("/oppdrag/ny")
    tom = page.evaluate(FORHANDSVISNING)
    assert (tom["kategori"], tom["tittel"], tom["tid"], tom["sted"], tom["pris"], tom["live"]) == (
        "–", "–", "–", "0571 Oslo", "–", False,
    )

    fyll_ut_steg_1(page, tittel="Måke snø")
    if page.get_by_role("button", name="Neste").is_visible():
        page.get_by_role("button", name="Neste").click()
    page.get_by_label("Dato").fill("25.11.2026")
    page.get_by_label("Klokkeslett").fill("7")
    page.get_by_label("Postnummer").fill("5006")
    expect(page.locator("#postnummer-sted")).to_have_text("Bergen")
    page.get_by_label("Beløp", exact=True).check()
    page.get_by_label("Beløp i kr").fill("1000")
    utfylt = page.evaluate(FORHANDSVISNING)
    assert utfylt == {
        "kategori": "Snømåking", "tittel": "Måke snø", "tid": "25.11.2026 kl. 7", "sted": "5006 Bergen",
        "pris": f"1{NBSP}000{NBSP}kr", "ikon": True, "aktiv": "belop", "live": False,
    }

    page.get_by_label("Uten betaling").check()
    assert page.evaluate(FORHANDSVISNING)["pris"] == "Uten betaling"
    page.get_by_label("Postnummer").fill("")
    assert page.evaluate(FORHANDSVISNING)["sted"] == "–"


def test_forhandsvisningen_utenfor_vanlig_tilfelle(page: Page, logg_inn_som_kari: Callable[[Page], None]) -> None:
    """UX-DR15, spec 2.2 Design Notes: annen tekst i beløpet med « kr», mellomrom fjernes fra sifre,
    nuller foran fjernes, og bare dato (uten klokkeslett) gir «–». Samme regler som på serveren."""
    logg_inn_som_kari(page)
    page.goto("/oppdrag/ny")
    page.get_by_label("Beløp", exact=True).check()
    belop = page.get_by_label("Beløp i kr")
    for skrevet, vist in (("abc", f"abc{NBSP}kr"), (" 10 000 ", f"10{NBSP}000{NBSP}kr"),
                          ("0005", f"5{NBSP}kr"), ("1234567", f"1{NBSP}234{NBSP}567{NBSP}kr"), ("  ", "–")):
        belop.fill(skrevet)
        assert page.evaluate(FORHANDSVISNING)["pris"] == vist, skrevet
    page.get_by_label("Dato").fill("25.11.2026")
    assert page.evaluate(FORHANDSVISNING)["tid"] == "–"


def test_forhandsvisningen_etter_422_er_lik_serverens(page: Page, logg_inn_som_kari: Callable[[Page], None]) -> None:
    """UX-DR15: etter 422 (tittel `ab`, beløp `abc`, bare dato) viser kortet det samme etter at JS har
    kjørt som serveren skrev i HTML-en, så siden ikke hopper."""
    logg_inn_som_kari(page)
    fyll_ut_steg_1(page, tittel="ab")
    page.get_by_label("Dato").fill("25.11.2026")
    page.get_by_label("Beløp", exact=True).check()
    page.get_by_label("Beløp i kr").fill("abc")
    with page.expect_response(lambda r: r.request.method == "POST") as svar:
        page.get_by_role("button", name="Publiser").click()
    assert svar.value.status == 422
    fra_serveren = kort_fra_serveren(svar.value.text())
    assert fra_serveren == {"kategori": "Snømåking", "tittel": "ab", "tid": "–", "sted": "0571 Oslo",
                            "pris": f"abc{NBSP}kr"}
    expect(page.locator("#feiloppsummering")).to_be_focused()
    etter_js = page.evaluate(FORHANDSVISNING)
    assert {felt: etter_js[felt] for felt in fra_serveren} == fra_serveren


def test_fokus_i_skjult_del_gar_til_h1_ved_ny_bredde(page: Page, logg_inn_som_kari: Callable[[Page], None]) -> None:
    """WCAG 2.4.3, UX-DR16: fokus i Dato på én skjerm, så 360 px: steg 1 vises, og h1 får fokus, ikke body."""
    page.set_viewport_size({"width": 1280, "height": 800})
    logg_inn_som_kari(page)
    page.goto("/oppdrag/ny")
    page.locator("#dato").focus()
    page.set_viewport_size(MOBIL)
    expect(h1(page)).to_have_text("Nytt oppdrag 1 av 2")
    expect(h1(page)).to_be_focused()
    assert page.evaluate("() => document.activeElement.tagName") == "H1"


def test_forhandsvisningen_viser_html_som_tekst(page: Page, logg_inn_som_kari: Callable[[Page], None]) -> None:
    """NFR-12, AD-11: `<script>` i tittelen står som tekst i kortet; ingen nye elementer."""
    logg_inn_som_kari(page)
    page.goto("/oppdrag/ny")
    page.get_by_label("Tittel").fill("<script>alert(1)</script>")
    tittel = page.locator('[data-felt="tittel"]')
    expect(tittel).to_have_text("<script>alert(1)</script>")
    assert page.evaluate("() => document.querySelectorAll('[data-forhandsvisning] script').length") == 0


@pytest.mark.parametrize("bredde", [360, 1280], ids=["mobil", "en-skjerm"])
def test_belop_i_kr_vises_bare_ved_belop(page: Page, logg_inn_som_kari: Callable[[Page], None], bredde: int) -> None:
    """UX-DR13: «Beløp i kr» skjult til «Beløp» er valgt; fokus blir på radioknappen, og 200 beholdes."""
    page.set_viewport_size({"width": bredde, "height": 800})
    logg_inn_som_kari(page)
    fyll_ut_steg_1(page)
    if page.get_by_role("button", name="Neste").is_visible():
        page.get_by_role("button", name="Neste").click()
    belop = page.get_by_label("Beløp i kr")
    expect(belop).to_be_hidden()

    page.get_by_label("Beløp", exact=True).check()
    expect(belop).to_be_visible()
    expect(page.locator("#tilbud-belop")).to_be_focused()
    belop.fill("200")

    page.get_by_label("Uten betaling").check()
    expect(belop).to_be_hidden()
    page.get_by_label("Beløp", exact=True).check()
    expect(belop).to_be_visible()
    expect(belop).to_have_value("200")


def test_en_skjerm_uten_js(browser, browser_context_args: dict) -> None:
    """UX-DR16, UX-DR13: uten JS står alt på én skjerm, også på 360 px, og «Beløp i kr» virker med CSS."""
    kontekst = browser.new_context(**browser_context_args, java_script_enabled=False, viewport=MOBIL)
    try:
        side = kontekst.new_page()
        _logg_inn(side, KARI)
        side.goto("/oppdrag/ny")
        expect(side).to_have_title("Nytt oppdrag – Nabolagshelten")
        expect(side.get_by_role("heading", level=1)).to_have_text("Nytt oppdrag")
        expect(side.get_by_role("heading", level=2)).to_have_text(["Hva trenger du hjelp til?", "Når og hvor?"])
        expect(side.get_by_role("button", name="Neste")).to_be_hidden()
        expect(side.get_by_role("button", name="Tilbake til steg 1")).to_be_hidden()
        expect(side.get_by_role("button", name="Publiser")).to_be_visible()
        expect(side.get_by_role("region", name="Slik vises oppdraget for andre.")).to_be_visible()
        expect(side.locator('[data-felt="sted"]')).to_have_text("0571 Oslo")

        belop = side.get_by_label("Beløp i kr")
        expect(belop).to_be_hidden()
        side.get_by_label("Beløp", exact=True).check()
        expect(belop).to_be_visible()
        side.get_by_label("Uten betaling").check()
        expect(belop).to_be_hidden()
    finally:
        kontekst.close()
