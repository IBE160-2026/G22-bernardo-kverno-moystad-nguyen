"""T1: universell utforming i ekte nettleser (SM-5, NFR-6, NFR-7, UX-DR5, UX-DR31).

Hver side og tilstand fra Epic 1 sjekkes
- med axe ved 360 og 1280 px: ingen brudd med `impact` «serious» eller «critical»,
- for vannrett rulling ved 320 px: `scrollWidth <= clientWidth` på `<html>`.

Ingen regler slås av, og ingen side utelates. Senere stories legger sine nye
sider og tilstander inn i `SIDER` (Definition of Done).
"""

from __future__ import annotations

from collections.abc import Callable

import pytest
from axe_playwright_python.base import AXE_FILE_PATH
from axe_playwright_python.sync_playwright import Axe
from playwright.sync_api import Page, expect

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
    h["logg_inn_som_kari"](page)  # ender på oversikten med tomtilstanden


def mine_oppdrag(page: Page, h: dict) -> None:
    h["logg_inn_som_kari"](page)
    page.goto("/mine-oppdrag")
    expect(page.get_by_role("heading", level=1)).to_have_text("Mine oppdrag")


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


SIDER: dict[str, Callable[[Page, dict], None]] = {
    "logg-inn": logg_inn_tom,
    "logg-inn-tom-innsending": logg_inn_tom_innsending,
    "logg-inn-logget-ut": logg_inn_logget_ut,
    "registrer": registrer_tom,
    "registrer-tom-innsending": registrer_tom_innsending,
    "oversikt-tom": oversikt,
    "mine-oppdrag": mine_oppdrag,
    "profil": min_profil,
    "profil-andre": andres_profil,
    "404": fant_ikke_siden,
    "401": logg_inn_igjen_401,
}


@pytest.fixture
def hjelpere(logg_inn_som_kari, bruker_id) -> dict:
    return {"logg_inn_som_kari": logg_inn_som_kari, "bruker_id": bruker_id}


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


@pytest.mark.parametrize("side", list(SIDER))
def test_ingen_vannrett_rulling_ved_320(page: Page, hjelpere: dict, side: str) -> None:
    """NFR-7, UX-DR31: ingen vannrett rulling ved 320 px."""
    page.set_viewport_size({"width": 320, "height": 640})
    SIDER[side](page, hjelpere)
    scroll, klient = page.evaluate(RULLING)
    assert scroll <= klient, (
        f"Vannrett rulling på «{side}» ved 320 px: scrollWidth {scroll} > clientWidth {klient}"
    )
