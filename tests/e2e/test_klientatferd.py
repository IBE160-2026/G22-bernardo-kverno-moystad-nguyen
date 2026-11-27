"""Oppførsel som bare kan sjekkes i ekte nettleser (UX-DR3, UX-DR13, UX-DR28, NFR-11).

Testene som var utsatt til T1: «Vis passord» og sendeknappen fra story 1.2, og
`poststed.js` fra story 1.4 (`deferred-work.md`). Menyen ved 360 og 1280 px
kom med T-1 (V3 i retro Epic 1): axe ser ikke en skjult `nav`. Telleren i
`skjema.js` og dobbeltklikk på «Publiser» kom med story 2.1 (NFR-5, UX-DR13, UX-DR28).
"""

from __future__ import annotations

from collections.abc import Callable

import pytest
from playwright.sync_api import Page, expect

from .conftest import fyll_ut_nytt_oppdrag

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
