"""Meny og grunnsider for oppdrag (FR-21 grunnsider, NFR-11, UX-DR3, UX-DR27, NFR-5)."""

from __future__ import annotations

import re

import pytest
from fastapi.testclient import TestClient

from ..core.test_render import les_side


@pytest.fixture
def kari_klient(klient: TestClient, lag_bruker, logg_inn_som) -> TestClient:
    logg_inn_som(klient, lag_bruker(navn="Kari Nordmann", postnummer="0571"))
    return klient


def menyvalg(html: str, variant: str) -> list[tuple[str, str | None, str]]:
    """(href, aria-current, tekst) for hvert valg i menyen «topp» eller «bunn»."""
    nav = re.search(rf'<nav class="meny meny--{variant}" aria-label="Hovedmeny">(.*?)</nav>', html, re.S)
    assert nav, f"Mangler menyen {variant}"
    valg = []
    for treff in re.finditer(r"<a ([^>]*)>(.*?)</a>", nav.group(1), re.S):
        attrs, innhold = treff.groups()
        href = re.search(r'href="([^"]+)"', attrs).group(1)
        current = re.search(r'aria-current="([^"]+)"', attrs)
        tekst = re.sub(r"<[^>]+>", "", innhold).strip()
        valg.append((href, current.group(1) if current else None, tekst))
    return valg


@pytest.mark.parametrize(
    ("sti", "aktiv"),
    [("/", "/"), ("/mine-oppdrag", "/mine-oppdrag"), ("/profil", "/profil")],
)
def test_meny_med_aktivt_valg(kari_klient: TestClient, sti: str, aktiv: str) -> None:
    """NFR-11: Oppdrag · Mine oppdrag · Profil i fast rekkefølge, aktivt valg med aria-current."""
    html = kari_klient.get(sti).text
    for variant in ("topp", "bunn"):
        valg = menyvalg(html, variant)
        assert [(h, t) for h, _, t in valg] == [
            ("/", "Oppdrag"),
            ("/mine-oppdrag", "Mine oppdrag"),
            ("/profil", "Profil"),
        ]
        assert [h for h, c, _ in valg if c == "page"] == [aktiv]
        assert all(c in (None, "page") for _, c, _ in valg)


def test_logoen_er_lenke_til_oversikten(kari_klient: TestClient) -> None:
    html = kari_klient.get("/mine-oppdrag").text
    assert '<a class="logo" href="/" aria-label="Nabolagshelten, til oversikten">' in html


def test_oversikten_har_overskrift_og_tomtilstand(kari_klient: TestClient) -> None:
    svar = kari_klient.get("/")
    assert svar.status_code == 200
    assert "<title>Ledige oppdrag i 0571 Oslo – Nabolagshelten</title>" in svar.text
    assert "<h1>Ledige oppdrag i 0571 Oslo</h1>" in svar.text
    assert "Ingen ledige oppdrag i 0571 Oslo akkurat nå." in svar.text


def test_oversikten_bruker_brukerens_postnummer(klient, lag_bruker, logg_inn_som) -> None:
    logg_inn_som(klient, lag_bruker(postnummer="5006"))
    assert "<h1>Ledige oppdrag i 5006 Bergen</h1>" in klient.get("/").text


def test_mine_oppdrag_har_tomtilstand(kari_klient: TestClient) -> None:
    svar = kari_klient.get("/mine-oppdrag")
    assert "<title>Mine oppdrag – Nabolagshelten</title>" in svar.text
    assert "<h1>Mine oppdrag</h1>" in svar.text
    assert "Du har ikke lagt ut noen oppdrag." in svar.text


@pytest.mark.parametrize("sti", ["/", "/mine-oppdrag", "/profil"])
def test_ingen_lenker_til_funksjoner_som_ikke_finnes(kari_klient: TestClient, sti: str) -> None:
    """Story 1.2: ingen «Legg ut oppdrag» eller postnummerfilter ennå.

    Registreringen (story 1.4) lenkes bare fra innloggingssiden, aldri fra sider for innloggede.
    """
    html = kari_klient.get(sti).text
    for tekst in ("Legg ut oppdrag", "Velg et annet postnummer", "/registrer", "Postnummer</label>"):
        assert tekst not in html, tekst
    hrefs = set(re.findall(r'href="([^"#]+)"', html))
    assert hrefs <= {"/", "/mine-oppdrag", "/profil", "/static/css/app.css"}, hrefs


@pytest.mark.parametrize("sti", ["/", "/mine-oppdrag", "/profil"])
def test_sideramme_for_innlogget(kari_klient: TestClient, sti: str) -> None:
    """UX-DR2/UX-DR27: én h1, «Hopp til innholdet» først, høyst ett autofocus."""
    html = kari_klient.get(sti).text
    side = les_side(html)
    assert [t for t, _ in side.tagger].count("h1") == 1
    tag, attrs, tekst = side.forste_fokuserbare
    assert (tag, attrs.get("href"), tekst) == ("a", "#innhold", "Hopp til innholdet")
    assert html.count("autofocus") <= 1
    assert 'class="har-meny"' in html
