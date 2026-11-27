"""Oppførsel som bare kan sjekkes i ekte nettleser (UX-DR3, UX-DR13, UX-DR28, NFR-11).

Testene som var utsatt til T1: «Vis passord» og sendeknappen fra story 1.2, og
`poststed.js` fra story 1.4 (`deferred-work.md`). Menyen ved 360 og 1280 px
kom med T-1 (V3 i retro Epic 1): axe ser ikke en skjult `nav`. Telleren i
`skjema.js` og dobbeltklikk på «Publiser» kom med story 2.1 (NFR-5, UX-DR13, UX-DR28).
«Nytt oppdrag» i to steg under 768 px (`steg.js`), forhåndsvisningen i `skjema.js`
og «Beløp i kr» med CSS `:has` kom med story 2.2 (FR-5, NFR-7, UX-DR13, UX-DR15,
UX-DR16, UX-DR27, UX-DR28). Fokus i oversikten (`fokus.js`), klikk på kortflaten og
kolonnene ved 360, 768 og 1280 px kom med story 2.3 (FR-10, FR-11, UX-DR5, UX-DR21, UX-DR24).
Klikk på radflaten i «Mine oppdrag», merket som brytes, og tallet i menyen ved 360 og
1280 px kom med story 2.4 (FR-18, NFR-6, NFR-7, NFR-11, UX-DR3, UX-DR9, UX-DR10).
Bekreftelsesdialogen (`dialog.js`), bekreftelsessiden uten JS, «Endre tidspunkt» med fokus i
«Dato», to faner med feilmeldingen og akseptansekriteriene kom med story 2.5 (FR-6, FR-7,
FR-8, NFR-7, NFR-8, AR-28, UX-DR18, §4.0).
Bildet (`bilde.js`): skalering før innsending, forhåndsvisningen, «Hva viser bildet?» som
vises når en fil er valgt, innsending mens skaleringen pågår, og bilde uten JS kom med
story 2.7 (FR-27, AR-28, AD-18, SM-5, NFR-7, UX-DR33).
Utløpt innlogging mens «Nytt oppdrag» er utfylt, med og uten JS, kom med story 2.6
(FR-2, FR-3, AD-7, SM-5, NFR-6, NFR-7).
"""

from __future__ import annotations

import re
from collections.abc import Callable

import pytest
from playwright.sync_api import Page, expect

from tests import bilder

from ..oppdrag.test_to_steg import kort as kort_fra_serveren
from .conftest import AMIR, KARI, OLA, _logg_inn, fyll_ut_nytt_oppdrag, fyll_ut_steg_1

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
    # Fra story 2.4 har «Mine oppdrag» tallet og den skjulte teksten («, 1 trenger handling»).
    expect(hovedmeny.get_by_role("link")).to_contain_text(["Oppdrag", "Mine oppdrag", "Profil"])
    expect(hovedmeny.get_by_role("link")).to_have_count(3)


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


# ---------- oversikten (story 2.3) ----------


def beskrevet_av(locator) -> list[str]:
    return (locator.get_attribute("aria-describedby") or "").split()


def test_fokus_etter_kategori_og_postnummer_pa_mobil(page: Page) -> None:
    """FR-11, UX-DR24: Amir velger «Hage», skriver 5006 og trykker Enter.

    Fokus står først på «Hage» og så i postnummerfeltet. Antallslinja (ved 0 treff
    tomtilstandens første setning) er knyttet til begge, og Hage er fortsatt valgt.
    """
    page.set_viewport_size(MOBIL)
    _logg_inn(page, AMIR)
    page.get_by_role("link", name="Hage", exact=True).click()
    hage = page.get_by_role("link", name="Hage", exact=True)
    expect(hage).to_be_focused()
    expect(hage).to_have_attribute("aria-current", "true")
    assert beskrevet_av(hage) == ["tom-forste"]  # ingen hageoppdrag i 0572
    expect(page.locator("#tom-forste")).to_have_text("Ingen ledige oppdrag i 0572 Oslo akkurat nå.")

    felt = page.get_by_label("Postnummer")
    felt.fill("5006")
    felt.press("Enter")
    expect(page.get_by_role("heading", level=1)).to_have_text("Ledige oppdrag i 5006 Bergen")
    felt = page.get_by_label("Postnummer")
    expect(felt).to_be_focused()
    expect(page.locator("#antallslinje")).to_have_text("1 ledig oppdrag i Hage i 5006 Bergen")
    assert "antallslinje" in beskrevet_av(felt)
    hage = page.get_by_role("link", name="Hage", exact=True)
    expect(hage).to_have_attribute("aria-current", "true")
    assert beskrevet_av(hage) == ["antallslinje"]
    assert "vist_postnummer=" in page.url and "kategori=hage" in page.url


def test_vis_gir_fokus_i_feltet(page: Page) -> None:
    """FR-11: også «Vis» gir fokus i feltet og knytter antallslinja til det."""
    _logg_inn(page, OLA)
    page.get_by_label("Postnummer").fill("5006")
    page.get_by_role("button", name="Vis").click()
    expect(page.get_by_role("heading", level=1)).to_have_text("Ledige oppdrag i 5006 Bergen")
    expect(page.get_by_label("Postnummer")).to_be_focused()
    assert "antallslinje" in beskrevet_av(page.get_by_label("Postnummer"))


def test_ukjent_postnummer_gir_fokus_i_feltet_med_feilen(page: Page) -> None:
    _logg_inn(page, OLA)
    page.get_by_label("Postnummer").fill("9999")
    page.get_by_label("Postnummer").press("Enter")
    felt = page.get_by_label("Postnummer")
    expect(felt).to_be_focused()
    expect(felt).to_have_value("9999")
    expect(felt).to_have_attribute("aria-invalid", "true")
    expect(page).to_have_title("Feil: Ledige oppdrag i 0571 Oslo – Nabolagshelten")
    expect(page.locator("#antallslinje")).to_have_text("4 ledige oppdrag i 0571 Oslo")


def test_velg_et_annet_postnummer_markerer_innholdet(page: Page) -> None:
    """FR-10, UX-DR21: lenken gir fokus i postnummerfeltet med innholdet markert."""
    _logg_inn(page, OLA)
    page.goto("/?postnummer=0150")
    page.get_by_role("link", name="Velg et annet postnummer").click()
    felt = page.get_by_label("Postnummer")
    expect(felt).to_be_focused()
    assert page.evaluate(
        "() => [document.activeElement.selectionStart, document.activeElement.selectionEnd]"
    ) == [0, 4]
    page.keyboard.type("5006")
    expect(felt).to_have_value("5006")


def test_velg_et_annet_postnummer_uten_js_hopper_til_feltet(browser, browser_context_args: dict) -> None:
    """UX-DR21: uten JS er lenken et hopp til `#postnummer`."""
    kontekst = browser.new_context(**browser_context_args, java_script_enabled=False)
    try:
        side = kontekst.new_page()
        _logg_inn(side, OLA)
        side.goto("/?postnummer=0150")
        side.get_by_role("link", name="Velg et annet postnummer").click()
        assert side.url.endswith("#postnummer")
    finally:
        kontekst.close()


def test_vis_alle_kategorier_gir_fokus_pa_alle(page: Page) -> None:
    """FR-11: «Vis alle kategorier» i tomtilstanden velger «Alle» og gir den fokus."""
    _logg_inn(page, KARI)
    page.goto("/?kategori=hage")
    page.get_by_role("link", name="Vis alle kategorier").click()
    alle = page.get_by_role("link", name="Alle", exact=True)
    expect(alle).to_be_focused()
    expect(alle).to_have_attribute("aria-current", "true")
    expect(page.locator("#antallslinje")).to_have_text("1 ledig oppdrag i 0571 Oslo")


def test_klikk_pa_kortflaten_apner_detaljene(page: Page) -> None:
    """UX-DR5: hele kortet er én lenke; et klikk på prisen nederst åpner detaljene."""
    _logg_inn(page, OLA)
    kort = page.locator(".kort--lenke").filter(has_text="Mate katten i helgen")
    # Musa trykker midt på prisen. Lenkens ::after ligger over, så det er lenken som får klikket
    # (Playwright sin `click()` på prisen ville nektet, nettopp fordi lenken dekker den).
    # Kortet har bilde øverst (story 2.7), så prisen kan ligge under skjermkanten.
    kort.locator(".pris").scroll_into_view_if_needed()
    boks = kort.locator(".pris").bounding_box()
    assert boks is not None
    page.mouse.click(boks["x"] + boks["width"] / 2, boks["y"] + boks["height"] / 2)
    expect(page.get_by_role("heading", level=1)).to_have_text("Mate katten i helgen")
    expect(page.get_by_role("heading", level=2, name="Lagt ut av Nora Berg")).to_be_visible()


def test_klikk_pa_bildet_i_kortet_apner_detaljene(page: Page) -> None:
    """UX-DR5, FR-27: miniatyren er en del av trykkflaten, og kortet har ingen annen lenke."""
    _logg_inn(page, OLA)
    kort = page.locator(".kort--lenke").filter(has_text="Mate katten i helgen")
    expect(kort.locator("a")).to_have_count(1)
    bilde = kort.locator("img.kort__bilde")
    bilde.scroll_into_view_if_needed()
    boks = bilde.bounding_box()
    assert boks is not None
    page.mouse.click(boks["x"] + boks["width"] / 2, boks["y"] + boks["height"] / 2)
    expect(page.get_by_role("heading", level=1)).to_have_text("Mate katten i helgen")


@pytest.mark.parametrize(("bredde", "kolonner"), [(360, 1), (768, 2), (1280, 3)], ids=["360px", "768px", "1280px"])
def test_kortene_star_i_kolonner(page: Page, bredde: int, kolonner: int) -> None:
    """UX-DR8, NFR-6: 1, 2 og 3 kolonner ved 360, 768 og 1280 px."""
    page.set_viewport_size({"width": bredde, "height": 800})
    _logg_inn(page, OLA)
    venstre = page.evaluate(
        "() => [...new Set([...document.querySelectorAll('.kortliste > li')]"
        ".map((li) => Math.round(li.getBoundingClientRect().left)))].length"
    )
    assert venstre == kolonner


# ---------- «Mine oppdrag» (story 2.4: FR-18, NFR-6, NFR-7, NFR-11, UX-DR3, UX-DR9) ----------


@pytest.mark.parametrize("bredde", [360, 1280], ids=["360px", "1280px"])
def test_klikk_pa_radflaten_apner_detaljene(page: Page, bredde: int) -> None:
    """UX-DR9: hele lenkedelen av raden er lenken; et klikk på tidspunktet eller på pila ›,
    utenfor tittelen, åpner detaljene. Lenken heter bare tittelen og beskrives av merkelinja
    og tidspunktet."""
    page.set_viewport_size({"width": bredde, "height": 800})
    _logg_inn(page, KARI)
    page.goto("/mine-oppdrag")
    rad = page.locator(".listerad").filter(has_text="Bære ved opp til tredje etasje")
    # Lenkedelen; snarveiene under skillelinja (story 2.5) er egne lenker utenfor den.
    lenke = rad.locator(".listerad__hoved").get_by_role("link")
    expect(lenke).to_have_accessible_name("Bære ved opp til tredje etasje")
    expect(lenke).to_have_accessible_description(
        # Skjult tekst er absolutt plassert, så navneberegningen legger mellomrom rundt den
        # («passert .»). Det endrer ikke opplesningen.
        re.compile(r"^Status:\s*Åpen\s*Må gjøres:\s*Tidspunktet er passert\s*\.\s*Søndag 22\. nov\. kl\. 10:00$")
    )
    # Musa trykker midt på tidspunktet og midt på pila. Lenkens ::after ligger over tidspunktet,
    # og pila har pointer-events: none, så lenken får begge klikkene.
    for del_ in (".listerad__tid", ".listerad__pil"):
        page.goto("/mine-oppdrag")
        boks = rad.locator(del_).bounding_box()
        assert boks is not None, del_
        page.mouse.click(boks["x"] + boks["width"] / 2, boks["y"] + boks["height"] / 2)
        expect(page.get_by_role("heading", level=1)).to_have_text("Bære ved opp til tredje etasje")
    mine = page.get_by_role("navigation", name="Hovedmeny").get_by_role("link", name=re.compile("^Mine oppdrag"))
    expect(mine).to_have_attribute("aria-current", "true")


def test_handlingsmerket_brytes_uten_a_klippes(page: Page) -> None:
    """UX-DR10, NFR-7: ved 320 px og stor tekst brytes merket over flere linjer og holder seg i raden."""
    page.set_viewport_size({"width": 320, "height": 800})
    _logg_inn(page, KARI)
    page.goto("/mine-oppdrag")
    page.add_style_tag(content=".handlingsmerke { font-size: 2rem; }")
    merke = page.locator(".handlingsmerke")
    rad = page.locator(".listerad").filter(has=merke)
    m, r = merke.bounding_box(), rad.bounding_box()
    assert m is not None and r is not None
    assert m["height"] > 60  # mer enn én linje
    assert m["x"] >= r["x"] and m["x"] + m["width"] <= r["x"] + r["width"] + 0.5
    bredde, klient = page.evaluate(RULLING_HTML)
    assert bredde <= klient


RULLING_HTML = "() => [document.documentElement.scrollWidth, document.documentElement.clientWidth]"


@pytest.mark.parametrize(
    ("bredde", "meny"), [(360, ".meny--bunn"), (1280, ".meny--topp")], ids=["360px-bunnmeny", "1280px-topplinje"]
)
def test_tallet_i_menyen_syns_og_leses_opp(page: Page, bredde: int, meny: str) -> None:
    """NFR-11, UX-DR3, SM-5: «1» syns ved «Mine oppdrag», og lenken heter «Mine oppdrag, 1 trenger handling».

    I bunnmenyen står tallet øverst til høyre på ikonet, i topplinjen etter teksten.
    """
    page.set_viewport_size({"width": bredde, "height": 800})
    _logg_inn(page, KARI)
    tall = page.locator(f"{meny} .menytall")
    expect(tall).to_be_visible()
    expect(tall).to_have_text("1")
    hovedmeny = page.get_by_role("navigation", name="Hovedmeny")
    # Mellomrommet før kommaet kommer fra navneberegningen rundt skjult tekst (se over).
    lenke = hovedmeny.get_by_role("link", name=re.compile(r"^Mine oppdrag\s?, 1 trenger handling$"))
    expect(lenke).to_have_count(1)
    lenkeboks, tallboks = lenke.bounding_box(), tall.bounding_box()
    assert lenkeboks is not None and tallboks is not None
    assert tallboks["x"] + tallboks["width"] <= lenkeboks["x"] + lenkeboks["width"]
    if meny == ".meny--bunn":
        ikon = page.locator(".meny--bunn .meny__valg[href='/mine-oppdrag'] .meny__ikon").bounding_box()
        assert ikon is not None
        assert tallboks["y"] < ikon["y"] + ikon["height"] / 2  # øverst på ikonet
        assert tallboks["x"] > ikon["x"] + ikon["width"] / 2  # til høyre på ikonet
    else:
        tekst = page.locator(".meny--topp .meny__valg[href='/mine-oppdrag'] > span").first.bounding_box()
        assert tekst is not None
        assert tallboks["x"] >= tekst["x"] + tekst["width"]  # etter teksten


# ---------- redigere og avbryte (story 2.5: FR-6, FR-7, FR-8, NFR-7, NFR-8, UX-DR18, §4.0) ----------

MAKE = "Måke snø i innkjørselen"
BAERE = "Bære ved opp til tredje etasje"


def _detaljer(page: Page, tittel: str) -> None:
    page.goto("/mine-oppdrag")
    page.get_by_role("link", name=tittel, exact=True).click()
    expect(page.get_by_role("heading", level=1)).to_have_text(tittel)


@pytest.mark.parametrize("bredde", [360, 1280], ids=["360px", "1280px"])
def test_dialogen_holder_fokus_og_gir_det_tilbake(page: Page, bredde: int) -> None:
    """UX-DR18, NFR-7: fokus på spørsmålet, Tab og Shift+Tab går rundt i dialogen, og Esc og
    «Behold oppdraget» lukker og gir fokus tilbake til lenken. Et klikk på sløret lukker ikke."""
    page.set_viewport_size({"width": bredde, "height": 800})
    _logg_inn(page, KARI)
    _detaljer(page, MAKE)
    lenke = page.get_by_role("link", name="Avbryt oppdrag")
    lenke.click()
    dialog = page.get_by_role("dialog", name=f"Avbryte «{MAKE}»?")
    expect(dialog).to_be_visible()
    expect(dialog).to_have_accessible_description("Det kan ikke angres.")
    sporsmal = dialog.get_by_role("heading", level=2)
    expect(sporsmal).to_be_focused()
    ja = dialog.get_by_role("button", name="Ja, avbryt oppdraget")
    behold = dialog.get_by_role("button", name="Behold oppdraget")
    page.keyboard.press("Tab")
    expect(ja).to_be_focused()
    page.keyboard.press("Tab")
    expect(behold).to_be_focused()
    page.keyboard.press("Tab")
    expect(ja).to_be_focused()  # rundt til første
    page.keyboard.press("Shift+Tab")
    expect(behold).to_be_focused()  # rundt til siste
    page.keyboard.press("Escape")
    expect(dialog).to_be_hidden()
    expect(lenke).to_be_focused()

    lenke.click()
    expect(sporsmal).to_be_focused()
    page.keyboard.press("Shift+Tab")
    expect(behold).to_be_focused()  # fra spørsmålet bakover til siste knapp
    page.mouse.click(5, 5)  # sløret
    expect(dialog).to_be_visible()
    behold.click()
    expect(dialog).to_be_hidden()
    expect(lenke).to_be_focused()
    expect(page.get_by_role("heading", level=1)).to_have_text(MAKE)  # ingenting er avbrutt


def test_dialogen_ruller_inne_i_seg_ved_lav_skjerm(page: Page) -> None:
    """UX-DR18, NFR-6: ved 320 × 240 px og stor tekst kan begge knappene nås, og dialogen gjør ikke siden bredere."""
    page.set_viewport_size({"width": 320, "height": 240})
    _logg_inn(page, KARI)
    _detaljer(page, MAKE)
    page.add_style_tag(content="html { font-size: 200%; }")
    for_dialog = page.evaluate(RULLING_HTML)
    page.get_by_role("link", name="Avbryt oppdrag").click()
    dialog = page.get_by_role("dialog")
    boks = dialog.bounding_box()
    assert boks is not None and boks["height"] <= 240 and boks["x"] >= 0 and boks["x"] + boks["width"] <= 320
    behold = dialog.get_by_role("button", name="Behold oppdraget")
    behold.scroll_into_view_if_needed()
    expect(behold).to_be_in_viewport()
    assert page.evaluate(RULLING_HTML) == for_dialog  # dialogen gjør ikke siden bredere


def test_bekreftelse_i_dialogen_gir_kvitteringen_i_fokus(page: Page) -> None:
    """FR-7, UX-DR27: «Ja, avbryt oppdraget» gir detaljene med «Oppdraget er avbrutt.» i fokus."""
    _logg_inn(page, KARI)
    _detaljer(page, MAKE)
    page.get_by_role("link", name="Avbryt oppdrag").click()
    page.get_by_role("button", name="Ja, avbryt oppdraget").click()
    expect(page.locator("#kvittering")).to_contain_text("Oppdraget er avbrutt.")
    expect(page.locator("#kvittering")).to_be_focused()
    expect(page.locator(".statusmerke")).to_contain_text("Avbrutt")
    expect(page.get_by_role("link", name="Avbryt oppdrag")).to_have_count(0)


def test_avbryte_fra_raden_gir_mine_oppdrag(page: Page) -> None:
    """Spec 2.5, beslutning 1, akseptansekriterium 2: snarveien heter «Avbryt oppdrag» og beskrives av
    tittelen; etter bekreftelsen står Kari i «Mine oppdrag» med kvitteringen i fokus."""
    _logg_inn(page, KARI)
    page.goto("/mine-oppdrag")
    snarvei = page.get_by_role("link", name="Avbryt oppdrag")
    expect(snarvei).to_have_accessible_name("Avbryt oppdrag")
    expect(snarvei).to_have_accessible_description(BAERE)
    expect(page.get_by_role("link", name="Endre tidspunkt")).to_have_accessible_description(BAERE)
    snarvei.click()
    page.get_by_role("button", name="Ja, avbryt oppdraget").click()
    expect(page.get_by_role("heading", level=1)).to_have_text("Mine oppdrag")
    expect(page.locator("#kvittering")).to_be_focused()
    rad = page.locator(".listerad").filter(has_text=BAERE)
    expect(rad.locator(".statusmerke")).to_contain_text("Avbrutt")
    expect(page.locator(".listerad__handlinger")).to_have_count(0)


def test_uten_js_gir_lenken_bekreftelsessiden(browser, browser_context_args: dict) -> None:
    """AR-28: uten JS følges «Avbryt oppdrag» til bekreftelsessiden, og POST derfra avbryter."""
    kontekst = browser.new_context(**browser_context_args, java_script_enabled=False)
    try:
        side = kontekst.new_page()
        _logg_inn(side, KARI)
        side.goto("/mine-oppdrag")
        side.get_by_role("link", name="Avbryt oppdrag").click()
        expect(side).to_have_title(f"Avbryte «{BAERE}»? – Nabolagshelten")
        expect(side.get_by_role("heading", level=1)).to_have_text(f"Avbryte «{BAERE}»?")
        expect(side.get_by_text("Det kan ikke angres.")).to_be_visible()
        side.get_by_role("link", name="Behold oppdraget").click()
        expect(side.get_by_role("heading", level=1)).to_have_text("Mine oppdrag")
        side.get_by_role("link", name="Avbryt oppdrag").click()
        side.get_by_role("button", name="Ja, avbryt oppdraget").click()
        expect(side.get_by_role("heading", level=1)).to_have_text("Mine oppdrag")
        expect(side.locator("#kvittering")).to_contain_text("Oppdraget er avbrutt.")
    finally:
        kontekst.close()


@pytest.mark.parametrize("bredde", [360, 1280], ids=["360px", "1280px"])
def test_endre_tidspunkt_gir_fokus_i_dato(page: Page, bredde: int) -> None:
    """FR-8, UX-DR27: «Endre tidspunkt» i raden og i detaljene gir fokus i «Dato», med verdien utfylt.

    Redigering står på én skjerm på alle bredder (ingen steg).
    """
    page.set_viewport_size({"width": bredde, "height": 800})
    _logg_inn(page, KARI)
    page.goto("/mine-oppdrag")
    page.get_by_role("link", name="Endre tidspunkt").click()
    dato = page.get_by_label("Dato")
    expect(dato).to_be_focused()
    expect(dato).to_have_value("22.11.2026")
    expect(page.get_by_role("heading", level=2, name="Når og hvor?")).to_be_visible()
    expect(page.get_by_role("button", name="Neste")).to_have_count(0)
    _detaljer(page, BAERE)
    page.get_by_role("link", name="Endre tidspunkt").click()
    expect(page.get_by_label("Dato")).to_be_focused()


def test_nytt_tidspunkt_gir_oppdraget_tilbake(page: Page) -> None:
    """Akseptansekriterium 1 (FR-8): «Endre tidspunkt», dato i morgen og «Lagre endringer» gir
    «Endringene er lagret.», merket og tallet i menyen er borte, og Ola ser oppdraget."""
    _logg_inn(page, KARI)
    page.goto("/mine-oppdrag")
    page.get_by_role("link", name="Endre tidspunkt").click()
    page.get_by_label("Dato").fill("25.11.2026")
    page.get_by_role("button", name="Lagre endringer").click()
    expect(page.locator("#kvittering")).to_contain_text("Endringene er lagret.")
    expect(page.locator("#kvittering")).to_be_focused()
    expect(page.locator(".handlingsmerke")).to_have_count(0)
    expect(page.locator(".menytall")).to_have_count(0)
    page.get_by_role("link", name="Tilbake").click()
    expect(page.get_by_role("heading", level=1)).to_have_text("Mine oppdrag")
    expect(page.locator(".handlingslinje")).to_have_count(0)
    page.context.clear_cookies()
    _logg_inn(page, OLA)
    expect(page.get_by_role("link", name=BAERE)).to_be_visible()


def test_to_faner_gir_feilmeldingen_i_fokus(page: Page) -> None:
    """§4.0: avbrutt i fane 1, så «Lagre endringer» i fane 2: feilmeldingen i fokus, og
    «Last siden på nytt» laster siden uten meldingen."""
    _logg_inn(page, KARI)
    _detaljer(page, MAKE)
    page.get_by_role("link", name="Rediger", exact=True).click()
    fane_1 = page.context.new_page()
    try:
        fane_1.goto(page.url.replace("/rediger", ""))
        fane_1.get_by_role("link", name="Avbryt oppdrag").click()
        fane_1.get_by_role("button", name="Ja, avbryt oppdraget").click()
        expect(fane_1.locator("#kvittering")).to_contain_text("Oppdraget er avbrutt.")
    finally:
        fane_1.close()
    page.get_by_label("Tittel").fill("Endret i fane 2")
    page.get_by_role("button", name="Lagre endringer").click()
    melding = page.locator("#feilmelding")
    expect(melding).to_contain_text("Oppdraget er endret. Last siden på nytt.")
    expect(melding).to_be_focused()
    expect(page.get_by_role("heading", level=1)).to_have_text(MAKE)
    page.get_by_role("link", name="Last siden på nytt").click()
    expect(page.get_by_role("heading", level=1)).to_have_text(MAKE)
    expect(page.locator("#feilmelding")).to_have_count(0)
    expect(page.locator(".statusmerke")).to_contain_text("Avbrutt")


# ---------- bilde (story 2.7, FR-27, AD-18) ----------

FIRE_MB = 4 * 1024 * 1024
FIL_ER_SKALERT = "() => { const f = document.querySelector('#bilde').files[0]; return f && f.type === 'image/jpeg'; }"
FILSTORRELSE = "() => document.querySelector('#bilde').files[0].size"


def _velg(page: Page, data: bytes, navn: str, type_: str) -> None:
    page.locator("#bilde").set_input_files(files=[{"name": navn, "mimeType": type_, "buffer": data}])


def _fyll_ut_steg_2(page: Page) -> None:
    page.get_by_label("Dato").fill("25.11.2026")
    page.get_by_label("Klokkeslett").fill("07:00")
    page.get_by_label("Beløp", exact=True).check()
    page.get_by_label("Beløp i kr").fill("200")


def _detaljbildet(page: Page) -> tuple[int, int]:
    bilde = page.locator("img.detaljbilde")
    expect(bilde).to_have_js_property("complete", True)
    bredde, hoyde = bilde.evaluate("b => [b.naturalWidth, b.naturalHeight]")
    return bredde, hoyde


def test_stort_bilde_skaleres_vises_i_forhandsvisningen_og_publiseres(page: Page) -> None:
    """Akseptansekriterium 1: Kari på mobil velger et PNG-bilde på cirka 6 MB. Fila byttes med
    en JPEG under 4 MB, forhåndsvisningen viser bildet, og detaljene har et bilde på høyst 1 600 px."""
    stort = bilder.stoy_png(2000, 1000)
    assert len(stort) > 5 * 1024 * 1024  # uten skalering ville kroppen vært over grensen
    page.set_viewport_size(MOBIL)
    _logg_inn(page, KARI)
    fyll_ut_steg_1(page)
    bildetekst = page.get_by_label("Hva viser bildet?")
    expect(bildetekst).to_be_hidden()
    _velg(page, stort, "kamera.png", "image/png")
    expect(bildetekst).to_be_visible()
    page.wait_for_function(FIL_ER_SKALERT)
    assert page.evaluate(FILSTORRELSE) < FIRE_MB
    bildetekst.fill("Snødekt innkjørsel")
    page.get_by_role("button", name="Neste").click()
    forhandsvisning = page.locator('[data-forhandsvisning] img[data-felt="bilde"]')
    expect(forhandsvisning).to_be_visible()
    expect(forhandsvisning).to_have_attribute("src", re.compile(r"^blob:"))
    expect(forhandsvisning).to_have_js_property("complete", True)
    assert forhandsvisning.evaluate("b => b.naturalWidth") == 1600
    _fyll_ut_steg_2(page)
    page.get_by_role("button", name="Publiser").click()
    expect(page.locator("#kvittering")).to_contain_text("Oppdraget er lagt ut.")
    bredde, hoyde = _detaljbildet(page)
    assert max(bredde, hoyde) <= 1600 and (bredde, hoyde) == (1600, 800)
    expect(page.get_by_role("img", name="Snødekt innkjørsel")).to_be_visible()


# Holder `createImageBitmap` til testen kaller `window.slippBilde()`, så skaleringen garantert
# pågår når «Publiser» trykkes.
HOLD_SKALERING = """
window.slippBilde = null;
const ekteCreateImageBitmap = window.createImageBitmap.bind(window);
window.createImageBitmap = (...argumenter) => new Promise((ok, feil) => {
  window.slippBilde = () => ekteCreateImageBitmap(...argumenter).then(ok, feil);
});
"""


def _poster_til(page: Page, sti: str) -> list[str]:
    poster: list[str] = []
    page.on("request", lambda r: poster.append(r.url) if r.method == "POST" and r.url.endswith(sti) else None)
    return poster


def test_innsending_mens_skaleringen_pagar_venter_pa_bildet(page: Page) -> None:
    """AD-18: «Publiser» mens skaleringen pågår, stoppes til skaleringen er ferdig, og sendes så
    med den skalerte fila (originalen ville gitt 413)."""
    page.add_init_script(HOLD_SKALERING)
    page.set_viewport_size({"width": 1280, "height": 800})
    _logg_inn(page, KARI)
    fyll_ut_nytt_oppdrag(page)
    poster = _poster_til(page, "/oppdrag/ny")
    # Bildeteksten fylles ut før fila velges (feltet er skjult til da).
    page.locator("#bildetekst").evaluate("felt => { felt.value = 'Snødekt innkjørsel'; }")
    _velg(page, bilder.stoy_png(2000, 1000), "kamera.png", "image/png")
    page.wait_for_function("() => window.slippBilde !== null")
    page.get_by_role("button", name="Publiser").click()
    page.wait_for_timeout(300)
    assert page.url.endswith("/oppdrag/ny") and poster == []
    page.evaluate("() => window.slippBilde()")
    # Skaleringen av et bilde på 6 MB kan ta noen sekunder i CI.
    expect(page.locator("#kvittering")).to_contain_text("Oppdraget er lagt ut.", timeout=20_000)
    assert len(poster) == 1
    assert _detaljbildet(page) == (1600, 800)


def test_to_trykk_under_skaleringen_gir_en_innsending(page: Page) -> None:
    """NFR-5: to trykk på «Lagre endringer» mens skaleringen pågår gir nøyaktig én POST, også i
    redigeringsskjemaet, som ikke har `skjema_id`."""
    page.add_init_script(HOLD_SKALERING)
    page.set_viewport_size({"width": 1280, "height": 800})
    _logg_inn(page, KARI)
    _detaljer(page, MAKE)
    page.get_by_role("link", name="Rediger", exact=True).click()
    poster = _poster_til(page, "/rediger")
    _velg(page, bilder.stoy_png(2000, 1000), "kamera.png", "image/png")
    page.wait_for_function("() => window.slippBilde !== null")
    knapp = page.get_by_role("button", name="Lagre endringer")
    knapp.click()
    knapp.click()
    page.wait_for_timeout(300)
    assert poster == []
    page.evaluate("() => window.slippBilde()")
    expect(page.locator("#kvittering")).to_contain_text("Endringene er lagret.", timeout=20_000)
    page.wait_for_timeout(500)
    assert len(poster) == 1
    assert _detaljbildet(page) == (1600, 800)


def test_fjern_bildet_tar_bildet_ut_av_forhandsvisningen(page: Page) -> None:
    """«Fjern bildet» fjerner det lagrede bildet fra forhåndsvisningen, og setter det inn igjen."""
    page.set_viewport_size({"width": 1280, "height": 800})
    _logg_inn(page, KARI)
    _detaljer(page, MAKE)
    page.get_by_role("link", name="Rediger", exact=True).click()
    # Vent til bilde.js (defer) har koblet til lytterne før avkrysningen.
    page.wait_for_load_state("load")
    forhandsvisning = page.locator('[data-forhandsvisning] img[data-felt="bilde"]')
    expect(forhandsvisning).to_be_visible()
    page.get_by_label("Fjern bildet").check()
    expect(forhandsvisning).to_be_hidden()
    page.get_by_label("Fjern bildet").uncheck()
    expect(forhandsvisning).to_be_visible()
    expect(page.get_by_role("img", name="Valgt bilde")).to_be_visible()


def test_ny_fil_slar_av_beholdt_bilde(page: Page) -> None:
    """Etter 422 med beholdt bilde: en ny fil slår av `bilde_beholdt`, og fjernes fila, slås det på igjen."""
    page.set_viewport_size({"width": 1280, "height": 800})
    _logg_inn(page, KARI)
    fyll_ut_nytt_oppdrag(page)
    _velg(page, bilder.jpeg(800, 600), "bilde.jpg", "image/jpeg")
    page.get_by_role("button", name="Publiser").click()
    expect(page.locator("#bildetekst-feil")).to_contain_text("Skriv hva bildet viser.")
    beholdt = page.locator('input[name="bilde_beholdt"]')
    expect(beholdt).to_be_enabled()
    _velg(page, bilder.png(400, 300), "nytt.png", "image/png")
    expect(beholdt).to_be_disabled()
    page.locator("#bilde").set_input_files(files=[])
    expect(beholdt).to_be_enabled()


def test_bildeteksten_vises_bare_med_fil(page: Page) -> None:
    """«Hva viser bildet?» er skjult til en fil er valgt, og skjules igjen når fila fjernes.
    Ved redigering av et oppdrag med bilde står feltet synlig fra start."""
    page.set_viewport_size({"width": 1280, "height": 800})
    _logg_inn(page, KARI)
    page.goto("/oppdrag/ny")
    bildetekst = page.get_by_label("Hva viser bildet?")
    forhandsvisning = page.locator('[data-forhandsvisning] img[data-felt="bilde"]')
    expect(bildetekst).to_be_hidden()
    expect(forhandsvisning).to_be_hidden()
    _velg(page, bilder.jpeg(800, 600), "bilde.jpg", "image/jpeg")
    expect(bildetekst).to_be_visible()
    expect(forhandsvisning).to_be_visible()
    page.locator("#bilde").set_input_files(files=[])
    expect(bildetekst).to_be_hidden()
    expect(forhandsvisning).to_be_hidden()
    _detaljer(page, MAKE)
    page.get_by_role("link", name="Rediger", exact=True).click()
    expect(page.get_by_label("Hva viser bildet?")).to_be_visible()
    expect(page.get_by_label("Bytt bilde")).to_be_visible()


def test_fil_som_ikke_kan_dekodes_sendes_som_den_er(page: Page) -> None:
    """JS avviser aldri en fil: en tekstfil sendes uendret, og serveren gir feilen."""
    page.set_viewport_size({"width": 1280, "height": 800})
    _logg_inn(page, KARI)
    fyll_ut_nytt_oppdrag(page)
    _velg(page, bilder.TEKST, "bilde.jpg", "image/jpeg")
    page.get_by_role("button", name="Publiser").click()
    expect(page.locator("#bilde-feil")).to_contain_text("Velg et bilde i JPEG, PNG eller WebP.")


def test_bilde_uten_js(browser, browser_context_args: dict) -> None:
    """AR-28: uten JS står «Hva viser bildet?» alltid synlig, og et JPEG-bilde på cirka 1 MB
    sendes som det er og vises i detaljene."""
    data = bilder.stoy_jpeg(900, 900)
    assert 700_000 < len(data) < 2 * 1024 * 1024
    kontekst = browser.new_context(**browser_context_args, java_script_enabled=False, viewport=MOBIL)
    try:
        side = kontekst.new_page()
        _logg_inn(side, KARI)
        fyll_ut_steg_1(side)
        expect(side.get_by_label("Hva viser bildet?")).to_be_visible()
        _velg(side, data, "bilde.jpg", "image/jpeg")
        side.get_by_label("Hva viser bildet?").fill("Snødekt innkjørsel")
        _fyll_ut_steg_2(side)
        side.get_by_role("button", name="Publiser").click()
        expect(side.locator("#kvittering")).to_contain_text("Oppdraget er lagt ut.")
        assert _detaljbildet(side) == (900, 900)
    finally:
        kontekst.close()


# ---------- utløpt innlogging (story 2.6, AD-7) ----------

TITTEL_UTLOPT = "Måke snø før helgen"


def _utlopt_og_logg_inn_igjen(side: Page) -> None:
    """Kari fyller ut «Nytt oppdrag», sesjonen forsvinner, hun trykker «Publiser» og logger inn
    på 401-siden. Hun havner i detaljene med kvitteringen og alt hun skrev."""
    _logg_inn(side, KARI)
    fyll_ut_nytt_oppdrag(side, tittel=TITTEL_UTLOPT)
    side.context.clear_cookies(name="sesjon")
    side.get_by_role("button", name="Publiser").click()
    expect(side.get_by_role("heading", level=1)).to_have_text("Du må logge inn igjen.")
    expect(side.get_by_label("E-post")).to_be_focused()
    expect(side.locator("nav")).to_have_count(0)
    side.get_by_label("E-post").fill(KARI.epost)
    side.locator("#innlogging-passord").fill(KARI.passord)
    side.get_by_role("button", name="Logg inn").click()
    expect(side.locator("#kvittering")).to_contain_text("Oppdraget er lagt ut.")
    expect(side.get_by_role("heading", level=1)).to_have_text(TITTEL_UTLOPT)
    expect(side.get_by_text("Trenger noen som kan måke snø i innkjørselen min i morgen.")).to_be_visible()
    expect(side.locator(".pris")).to_have_text("200 kr")
    expect(side.locator(".merkelinje")).to_contain_text("Snømåking")
    expect(side.locator(".fakta__sted")).to_have_text("0571 Oslo")
    expect(side.locator(".fakta__tid")).to_have_text("I morgen kl. 07:00")


def test_utlopt_innlogging_beholder_skjemaet(page: Page, antall_oppdrag) -> None:
    """AC 1, AD-7: på mobil (360 px) med JS gir innlogging på 401-siden det publiserte oppdraget."""
    page.set_viewport_size(MOBIL)
    _utlopt_og_logg_inn_igjen(page)
    assert antall_oppdrag(TITTEL_UTLOPT) == 1


def test_utlopt_innlogging_uten_js(browser, browser_context_args: dict, antall_oppdrag) -> None:
    """AC 2, AD-7: samme flyt uten JS gir samme resultat."""
    kontekst = browser.new_context(**browser_context_args, java_script_enabled=False, viewport=MOBIL)
    try:
        _utlopt_og_logg_inn_igjen(kontekst.new_page())
    finally:
        kontekst.close()
    assert antall_oppdrag(TITTEL_UTLOPT) == 1
