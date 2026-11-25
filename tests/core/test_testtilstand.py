"""`POST /_test/tilstand` (AD-14, AR-29): radene om tilstand i I/O-matrisen i spec-1-5."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app import lag_app
from app.core import klokke
from app.core.config import Settings
from app.identity.models import Bruker, Sesjon
from app.seed import TESTBRUKERE

from .test_mellomvare import hent_csrf

STI = "/_test/tilstand"


@pytest.fixture(autouse=True)
def vanlig_klokke():
    yield
    klokke.sett_na(None)


def antall(db, modell) -> int:
    return db.scalar(select(func.count()).select_from(modell))


def test_tilstand_setter_klokke_ki_og_seed(
    app: FastAPI, klient: TestClient, db, lag_bruker, logg_inn_som
) -> None:
    """AD-14: 204, klokka er satt, `ki_utgave` er «feil», bare de seks testbrukerne og ingen sesjoner."""
    nokkel = hent_csrf(klient)
    logg_inn_som(klient, lag_bruker(epost="annen@eksempel.no"))
    assert app.state.ki_utgave == "mock"

    svar = klient.post(
        STI,
        data={
            "csrf_token": nokkel,
            "klokke": "2026-11-24T12:00:00+00:00",
            "ki": "feil",
            "seed": "1",
        },
    )

    assert svar.status_code == 204
    assert klokke.na() == datetime(2026, 11, 24, 12, 0, tzinfo=timezone.utc)
    assert app.state.ki_utgave == "feil"
    db.expire_all()
    assert set(db.scalars(select(Bruker.epost)).all()) == {t.epost for t in TESTBRUKERE}
    # Klokka settes før seed, så testbrukerne får `opprettet` fra den faste klokka.
    assert set(db.scalars(select(Bruker.opprettet)).all()) == {
        datetime(2026, 11, 24, 12, 0, tzinfo=timezone.utc)
    }
    assert antall(db, Sesjon) == 0


def test_tom_klokke_gir_vanlig_klokke(klient: TestClient) -> None:
    klokke.sett_na(datetime(2020, 1, 1, tzinfo=timezone.utc))
    svar = klient.post(STI, data={"csrf_token": hent_csrf(klient), "klokke": ""})
    assert svar.status_code == 204
    assert klokke.na().year >= 2026


def test_klokke_med_annen_tidssone_lagres_som_utc(klient: TestClient) -> None:
    svar = klient.post(
        STI, data={"csrf_token": hent_csrf(klient), "klokke": "2026-11-24T13:00:00+01:00"}
    )
    assert svar.status_code == 204
    assert klokke.na() == datetime(2026, 11, 24, 12, 0, tzinfo=timezone.utc)


@pytest.mark.parametrize(
    "felt",
    [
        {"klokke": "i går"},
        {"klokke": "2026-11-24T12:00:00"},
        {"ki": "ekte"},
        {"seed": "2"},
        {"ukjent": "1"},
        # Én ugyldig verdi stopper også de gyldige.
        {"klokke": "2026-11-24T12:00:00+00:00", "seed": "1", "ki": "ekte"},
    ],
    ids=["klokke-tekst", "klokke-uten-tidssone", "ki-ekte", "seed-2", "ukjent-felt", "blandet"],
)
def test_ugyldig_verdi_gir_400_uten_endring(
    app: FastAPI, klient: TestClient, db, lag_bruker, felt: dict[str, str]
) -> None:
    """AD-14: ukjent verdi gir 400, og ingenting er endret."""
    lag_bruker(epost="annen@eksempel.no")
    for_ = antall(db, Bruker)
    fast = datetime(2026, 1, 2, 3, 4, tzinfo=timezone.utc)
    klokke.sett_na(fast)

    svar = klient.post(STI, data={"csrf_token": hent_csrf(klient), **felt})

    assert svar.status_code == 400
    assert klokke.na() == fast
    assert app.state.ki_utgave == "mock"
    db.expire_all()
    assert antall(db, Bruker) == for_


def test_uten_csrf_gir_403(app: FastAPI, klient: TestClient) -> None:
    """NFR-12: som for alle POST."""
    hent_csrf(klient)
    svar = klient.post(STI, data={"ki": "feil"})
    assert svar.status_code == 403
    assert app.state.ki_utgave == "mock"


@pytest.mark.parametrize("app_env", ["local", "production"])
@pytest.mark.parametrize("metode", ["GET", "POST"])
def test_stien_finnes_ikke_utenfor_test(app_env: str, metode: str) -> None:
    """AD-14: i `local` og `production` gir `/_test/tilstand` 404, også med gyldig CSRF."""
    settings = Settings(
        _env_file=None, app_env="local", secret_key="x" * 32, database_url="sqlite:///:memory:"
    ).model_copy(update={"app_env": app_env})
    app = lag_app(settings=settings)
    # I produksjon er CSRF-cookien `Secure`, så klienten må bruke https.
    with TestClient(app, base_url="https://testserver") as klient:
        nokkel = hent_csrf(klient)
        data = {"csrf_token": nokkel, "seed": "1"} if metode == "POST" else None
        svar = klient.request(metode, STI, data=data)
    assert svar.status_code == 404
    assert not hasattr(app.state, "last_eksempeldata")
