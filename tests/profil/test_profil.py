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


@pytest.mark.parametrize("bruker_id", ["0", "2147483648", "99999999999999999999"])
def test_id_utenfor_gyldig_omrade_gir_404(klient: TestClient, kari, logg_inn_som, bruker_id) -> None:
    """Store tall gir 404, ikke OverflowError og 500."""
    logg_inn_som(klient, kari)
    svar = klient.get(f"/profil/{bruker_id}")
    assert svar.status_code == 404
    assert "<h1>Fant ikke siden</h1>" in svar.text


def test_id_som_ikke_er_tall_gir_404(klient: TestClient, kari, logg_inn_som) -> None:
    logg_inn_som(klient, kari)
    assert klient.get("/profil/abc").status_code == 404


MANEDER = ("januar", "februar", "mars", "april", "mai", "juni", "juli", "august",
           "september", "oktober", "november", "desember")


def personopplysninger(*brukere) -> list[str]:
    """Telefon, e-post og fødselsdato i de skrivemåtene en mal kunne brukt."""
    funn = []
    for b in brukere:
        t, d = b.telefon, b.fodselsdato
        maned = MANEDER[d.month - 1]
        funn += [
            b.epost,
            b.epost.split("@")[0] + "&#64;",  # e-post med escapet @
            t,
            f"+47{t}",
            f"+47 {t}",
            f"{t[:3]} {t[3:5]} {t[5:]}",
            f"{t[:2]} {t[2:4]} {t[4:6]} {t[6:]}",
            d.isoformat(),
            d.strftime("%d.%m.%Y"),
            f"{d.day}.{d.month}.{d.year}",
            f"{d.day}. {maned} {d.year}",
            f"{d.day}. {maned[:3]}. {d.year}",
        ]
    return funn


def test_ar24_ingen_get_rute_viser_telefon_epost_eller_fodselsdato(
    app: FastAPI, klient: TestClient, kari, amir, logg_inn_som, lag_oppdrag, lag_bilde
) -> None:
    """AR-24, AD-16: alle GET-ruter rendret for innlogget bruker, også `/profil/{annen id}`
    og detaljene for et oppdrag Amir har lagt ut (story 2.1). Redigering og bekreftelsessiden
    for avbrudd (story 2.5) rendres for et oppdrag Kari eier, fordi andre får 404. Amirs
    oppdrag har bilde, så også bilderutene (story 2.7) gir 200."""
    amirs_oppdrag = lag_oppdrag(oppdragsgiver=amir)
    lag_bilde(amirs_oppdrag)
    karis_oppdrag = lag_oppdrag(oppdragsgiver=kari)
    id_for_rute = {
        "oppdrag.detaljer": amirs_oppdrag.id,
        "oppdrag.bilde": amirs_oppdrag.id,
        "oppdrag.bilde_liten": amirs_oppdrag.id,
        "oppdrag.rediger": karis_oppdrag.id,
        "oppdrag.avbryt": karis_oppdrag.id,
    }
    logg_inn_som(klient, kari)
    sider = 0
    for rute in alle_ruter(app.routes):
        if "GET" not in (getattr(rute, "methods", None) or set()):
            continue
        verdi_ = id_for_rute.get(rute.name, amir.id)
        sti = rute.path_format.format(**{navn: str(verdi_) for navn in rute.param_convertors})
        svar = klient.get(sti)
        assert svar.status_code == 200, (sti, svar.status_code)
        for verdi in personopplysninger(kari, amir):
            assert verdi not in svar.text, (sti, verdi)
        sider += 1
    assert sider >= 5
