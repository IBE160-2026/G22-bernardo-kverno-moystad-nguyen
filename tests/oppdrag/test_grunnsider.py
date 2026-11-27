"""Meny og grunnsider for oppdrag (FR-21 grunnsider, NFR-11, UX-DR3, UX-DR27, NFR-5).

Invariantene fra story 1.2, oppdatert i story 2.1: «+ Legg ut oppdrag» på
oversikten og lenken «Legg ut oppdrag» i tomtilstanden i «Mine oppdrag» (FR-5).
Oppdatert i story 2.3: oversikten har lista, filtrene og tomtilstandene (FR-10, FR-11).
"""

from __future__ import annotations

import re
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from app.core.domene import KATEGORIER

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
    """FR-10: uten oppdrag i postnummeret vises tomtilstanden med «Alle» valgt."""
    svar = kari_klient.get("/")
    assert svar.status_code == 200
    assert "<title>Ledige oppdrag i 0571 Oslo – Nabolagshelten</title>" in svar.text
    assert "<h1>Ledige oppdrag i 0571 Oslo</h1>" in svar.text
    assert "Ingen ledige oppdrag i 0571 Oslo akkurat nå." in svar.text
    assert "Prøv et annet postnummer." in svar.text


def test_oversikten_har_legg_ut_oppdrag_for_h1(kari_klient: TestClient) -> None:
    """FR-5, UX-DR10: «+ Legg ut oppdrag» er primærknappen, før h1, og «+» er skjult for skjermleser."""
    html = kari_klient.get("/").text
    knapp = re.search(r'<a class="knapp knapp--primar" href="/oppdrag/ny">(.*?)</a>', html, re.S)
    assert knapp, "Mangler «+ Legg ut oppdrag»"
    assert knapp.group(1) == '<span aria-hidden="true">+</span>&nbsp;Legg ut oppdrag'
    assert html.index('href="/oppdrag/ny"') < html.index("<h1>")


def test_oversikten_bruker_brukerens_postnummer(klient, lag_bruker, logg_inn_som) -> None:
    logg_inn_som(klient, lag_bruker(postnummer="5006"))
    assert "<h1>Ledige oppdrag i 5006 Bergen</h1>" in klient.get("/").text


def test_mine_oppdrag_har_tomtilstand(kari_klient: TestClient) -> None:
    """FR-18 (grunnversjon): uten oppdrag vises tomtilstanden med lenken «Legg ut oppdrag»."""
    svar = kari_klient.get("/mine-oppdrag")
    assert "<title>Mine oppdrag – Nabolagshelten</title>" in svar.text
    assert "<h1>Mine oppdrag</h1>" in svar.text
    assert "Du har ikke lagt ut noen oppdrag." in svar.text
    assert re.search(r'<a class="[^"]*" href="/oppdrag/ny">Legg ut oppdrag</a>', svar.text)


def test_mine_oppdrag_viser_egne_oppdrag_nyeste_forst(
    klient: TestClient, lag_bruker, logg_inn_som, lag_oppdrag
) -> None:
    """Beslutning i spec 2.1: med oppdrag vises titlene som lenker, nyeste først, og ingen tomtilstand."""
    kari = lag_bruker()
    eldst = lag_oppdrag(oppdragsgiver=kari, tittel="Eldste", opprettet=datetime(2026, 11, 1, tzinfo=timezone.utc))
    nyest = lag_oppdrag(oppdragsgiver=kari, tittel="Nyeste", opprettet=datetime(2026, 11, 20, tzinfo=timezone.utc))
    lag_oppdrag(tittel="Andres oppdrag")
    logg_inn_som(klient, kari)
    html = klient.get("/mine-oppdrag").text
    assert "Du har ikke lagt ut noen oppdrag." not in html
    lenker = re.findall(r'<li><a href="(/oppdrag/\d+)">([^<]+)</a></li>', html)
    assert lenker == [(f"/oppdrag/{nyest.id}", "Nyeste"), (f"/oppdrag/{eldst.id}", "Eldste")]


@pytest.mark.parametrize(
    ("sti", "legg_ut", "har_filter"),
    [("/", True, True), ("/mine-oppdrag", True, False), ("/profil", False, False)],
)
def test_ingen_lenker_til_funksjoner_som_ikke_finnes(
    kari_klient: TestClient, sti: str, legg_ut: bool, har_filter: bool
) -> None:
    """«Legg ut oppdrag» finnes fra 2.1 på oversikten og i tomtilstanden. Fra 2.3 har bare
    oversikten filtrene (kategorilenker og postnummerfeltet) og «Velg et annet postnummer».

    Registreringen (story 1.4) lenkes bare fra innloggingssiden, aldri fra sider for innloggede.
    """
    html = kari_klient.get(sti).text
    assert "/registrer" not in html
    for tekst in ("Velg et annet postnummer", "Postnummer</label>"):
        assert (tekst in html) is har_filter, tekst
    assert ("Legg ut oppdrag" in html) is legg_ut
    hrefs = set(re.findall(r'href="([^"#]+)"', html))
    tillatt = {"/", "/mine-oppdrag", "/profil", "/static/css/app.css", "/static/favicon.svg"}
    if legg_ut:
        tillatt.add("/oppdrag/ny")
    if har_filter:
        tillatt |= {"/?kategori=alle"} | {f"/?kategori={kode}" for kode, _ in KATEGORIER}
    assert hrefs <= tillatt, hrefs


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
