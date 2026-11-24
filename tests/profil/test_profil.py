"""Profilsidene og personopplysninger i HTML (FR-21, AD-16, AR-24, NFR-5)."""

from __future__ import annotations

import re
from datetime import date, datetime, timezone

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.sesjon import alle_ruter


@pytest.fixture
def kari(lag_bruker):
    return lag_bruker(
        navn="Kari Nordmann",
        epost="kari@eksempel.no",
        telefon="41234567",
        postnummer="0571",
        fodselsdato=date(1954, 5, 3),
    )


@pytest.fixture
def amir(lag_bruker):
    return lag_bruker(
        navn="Amir Haddad",
        epost="amir@eksempel.no",
        telefon="98765432",
        postnummer="0572",
        fodselsdato=date(2005, 2, 14),
    )


def test_min_profil(klient: TestClient, kari, logg_inn_som) -> None:
    """FR-21: navn som h1, postnummer med poststed og knappen «Logg ut»."""
    logg_inn_som(klient, kari)
    svar = klient.get("/profil")
    assert svar.status_code == 200
    assert "<title>Min profil – Nabolagshelten</title>" in svar.text
    assert "<h1>Kari Nordmann</h1>" in svar.text
    assert "<span>0571 Oslo</span>" in svar.text
    skjema = re.search(r'<form[^>]*action="/logg-ut"[^>]*>(.*?)</form>', svar.text, re.S)
    assert skjema and 'method="post"' in skjema.group(0)
    assert 'name="csrf_token"' in skjema.group(1)
    assert '<button class="knapp knapp--sekundar" type="submit">Logg ut</button>' in skjema.group(1)


def test_andres_profil(klient: TestClient, kari, amir, logg_inn_som) -> None:
    """FR-21: navn og postnummer med poststed, ingen aktiv meny."""
    logg_inn_som(klient, kari)
    svar = klient.get(f"/profil/{amir.id}")
    assert svar.status_code == 200
    assert "<title>Amir Haddad – profil – Nabolagshelten</title>" in svar.text
    assert "<h1>Amir Haddad</h1>" in svar.text
    assert "<span>0572 Oslo</span>" in svar.text
    assert "aria-current" not in svar.text
    assert "Logg ut" not in svar.text


def test_egen_id_sendes_til_min_profil(klient: TestClient, kari, logg_inn_som) -> None:
    logg_inn_som(klient, kari)
    svar = klient.get(f"/profil/{kari.id}", follow_redirects=False)
    assert svar.status_code == 303
    assert svar.headers["location"] == "/profil"


def test_ukjent_id_gir_404(klient: TestClient, kari, logg_inn_som) -> None:
    logg_inn_som(klient, kari)
    svar = klient.get("/profil/999999")
    assert svar.status_code == 404
    assert "<h1>Fant ikke siden</h1>" in svar.text


def test_slettet_bruker_gir_404(klient: TestClient, kari, lag_bruker, logg_inn_som) -> None:
    slettet = lag_bruker(navn="Borte", slettet_tidspunkt=datetime(2026, 11, 1, tzinfo=timezone.utc))
    logg_inn_som(klient, kari)
    svar = klient.get(f"/profil/{slettet.id}")
    assert svar.status_code == 404
    assert "Borte" not in svar.text


def test_id_som_ikke_er_tall_gir_404(klient: TestClient, kari, logg_inn_som) -> None:
    logg_inn_som(klient, kari)
    assert klient.get("/profil/abc").status_code == 404


def personopplysninger(*brukere) -> list[str]:
    funn = []
    for b in brukere:
        funn += [
            b.epost,
            b.telefon,
            f"{b.telefon[:3]} {b.telefon[3:5]} {b.telefon[5:]}",
            b.fodselsdato.isoformat(),
            b.fodselsdato.strftime("%d.%m.%Y"),
        ]
    return funn


def test_ar24_ingen_get_rute_viser_telefon_epost_eller_fodselsdato(
    app: FastAPI, klient: TestClient, kari, amir, logg_inn_som
) -> None:
    """AR-24: alle GET-ruter rendret for innlogget bruker, også `/profil/{annen id}`."""
    logg_inn_som(klient, kari)
    sider = 0
    for rute in alle_ruter(app.routes):
        if "GET" not in (getattr(rute, "methods", None) or set()):
            continue
        sti = rute.path_format.format(**{navn: str(amir.id) for navn in rute.param_convertors})
        svar = klient.get(sti)
        assert svar.status_code == 200, (sti, svar.status_code)
        for verdi in personopplysninger(kari, amir):
            assert verdi not in svar.text, (sti, verdi)
        sider += 1
    assert sider >= 5
