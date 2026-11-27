"""Oppsett for T1, ende-til-ende i ekte nettleser (AR-29, AD-14, SM-5).

- Appen kjører i en ekte uvicorn-server i en tråd, på en ledig port, med
  `APP_ENV=test` og en egen SQLite-fil i temp-mappen, migrert med Alembic.
  E2E bruker aldri den delte test-databasen som pytest ruller tilbake per test,
  fordi nettleseren trenger committede data.
- Serveren kjører i samme prosess, så `/_test/tilstand` stiller den samme
  klokka (`app.core.klokke`). Klokka nullstilles etter økta.
- `tilstand(page, **felt)` henter CSRF-nøkkelen fra `/logg-inn` og poster
  feltene til `/_test/tilstand`.
- Før hver test: `seed=1` og fast klokke. Etter hver test og etter økta: vanlig klokke.
- `logg_inn_som(page, testbruker)` logger inn en av testbrukerne gjennom
  skjemaet. `fyll_ut_nytt_oppdrag(page, ...)` fyller ut «Nytt oppdrag» med
  gyldige verdier for den faste klokka (story 2.1).

Kjøres med `uv run playwright install chromium` og `uv run pytest -m e2e`.
Vanlig `uv run pytest` velger E2E bort (`-m "not e2e"` i pyproject.toml).
"""

from __future__ import annotations

import re
import shutil
import socket
import tempfile
import threading
import time
from collections.abc import Callable, Iterator
from pathlib import Path

import pytest
import uvicorn
from alembic import command
from playwright.sync_api import Page, expect
from sqlalchemy import func, select

from app import lag_app
from app.core import klokke
from app.core.config import Settings
from app.core.db import lag_motor
from app.identity.models import Bruker
from app.oppdrag.models import Oppdrag
from app.seed import TESTBRUKERE, Testbruker

from ..conftest import alembic_config

FAST_KLOKKE = "2026-11-24T12:00:00+00:00"
CSRF_FELT = re.compile(r'name="csrf_token" value="([^"]+)"')
KARI = next(t for t in TESTBRUKERE if t.epost == "kari@eksempel.no")
OLA = next(t for t in TESTBRUKERE if t.epost == "ola@eksempel.no")


@pytest.fixture(scope="session")
def e2e_database_url() -> Iterator[str]:
    """Egen SQLite-fil for E2E, migrert til `head`."""
    mappe = tempfile.mkdtemp(prefix="nabolagshelten-e2e-")
    url = f"sqlite:///{Path(mappe, 'e2e.db').as_posix()}"
    motor = lag_motor(url)
    try:
        with motor.begin() as tilkobling:
            command.upgrade(alembic_config(tilkobling), "head")
    finally:
        motor.dispose()
    yield url
    shutil.rmtree(mappe, ignore_errors=True)


@pytest.fixture(scope="session")
def server_url(e2e_database_url: str) -> Iterator[str]:
    """Adressen til en ekte server med testappen (APP_ENV=test)."""
    settings = Settings(_env_file=None, app_env="test", database_url=e2e_database_url)
    app = lag_app(settings=settings)

    # Porten bindes her og gis til uvicorn, så ingen andre rekker å ta den.
    sokkel = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sokkel.bind(("127.0.0.1", 0))
    port = sokkel.getsockname()[1]
    server = uvicorn.Server(uvicorn.Config(app, log_level="warning", lifespan="off"))
    traad = threading.Thread(target=server.run, kwargs={"sockets": [sokkel]}, daemon=True)
    traad.start()
    frist = time.monotonic() + 15
    while not server.started:
        if not traad.is_alive() or time.monotonic() > frist:
            raise RuntimeError("E2E-serveren startet ikke.")
        time.sleep(0.05)
    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        server.should_exit = True
        traad.join(timeout=15)
        sokkel.close()
        app.state.motor.dispose()
        klokke.sett_na(None)


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict, server_url: str) -> dict:
    """Norsk språk og `base_url`, så testene kan bruke `page.goto("/logg-inn")`."""
    return {**browser_context_args, "base_url": server_url, "locale": "nb-NO"}


@pytest.fixture
def tilstand(server_url: str) -> Callable[..., None]:
    """`tilstand(page, seed="1", klokke=..., ki=...)` poster til `/_test/tilstand` (AD-14).

    Bruker nettleserens egne cookies, så CSRF-cookien og skjemanøkkelen hører sammen.
    Som innlogget sender `/logg-inn` videre, og da hentes nøkkelen fra `/profil`.
    """

    def _sett(page: Page, **felt: str) -> None:
        side = page.request.get(f"{server_url}/logg-inn", max_redirects=0)
        treff = CSRF_FELT.search(side.text())
        if treff is None:
            side = page.request.get(f"{server_url}/profil", max_redirects=0)
            treff = CSRF_FELT.search(side.text())
        assert treff, f"Fant ingen csrf_token på /logg-inn eller /profil (status {side.status})"
        svar = page.request.post(
            f"{server_url}/_test/tilstand",
            form={"csrf_token": treff.group(1), **felt},
            max_redirects=0,
        )
        assert svar.status == 204, f"/_test/tilstand ga {svar.status}: {svar.text()}"

    return _sett


@pytest.fixture(autouse=True)
def nullstill(page: Page, tilstand: Callable[..., None]) -> Iterator[None]:
    """Før hver test: testbrukerne på nytt, ingen sesjoner og fast klokke (AR-29).

    Etter testen får klokka vanlig tid igjen, så andre tester i samme kjøring
    (`uv run pytest -m "e2e or not e2e"`) ikke arver den faste klokka.
    """
    tilstand(page, seed="1", klokke=FAST_KLOKKE, ki="mock")
    yield
    klokke.sett_na(None)


def _logg_inn(page: Page, testbruker: Testbruker) -> None:
    page.goto("/logg-inn")
    page.get_by_label("E-post").fill(testbruker.epost)
    page.locator("#passord").fill(testbruker.passord)
    page.get_by_role("button", name="Logg inn").click()
    expect(page.get_by_role("heading", level=1)).to_contain_text("Ledige oppdrag i")


@pytest.fixture
def logg_inn_som() -> Callable[[Page, Testbruker], None]:
    """Logger inn en testbruker gjennom skjemaet, slik en bruker gjør (FR-2)."""
    return _logg_inn


@pytest.fixture
def logg_inn_som_kari() -> Callable[[Page], None]:
    """Logger inn Kari gjennom skjemaet (FR-2)."""
    return lambda page: _logg_inn(page, KARI)


def fyll_ut_nytt_oppdrag(page: Page, *, tittel: str = "Måke snø i innkjørselen") -> None:
    """Fyller ut «Nytt oppdrag» med gyldige verdier: i morgen kl. 07:00 med den faste klokka, 200 kr."""
    page.goto("/oppdrag/ny")
    page.get_by_label("Hva trenger du hjelp til?").fill(
        "Trenger noen som kan måke snø i innkjørselen min i morgen."
    )
    page.get_by_label("Tittel").fill(tittel)
    page.locator('label[for="kategori-snomaking"]').click()
    page.get_by_label("Dato").fill("25.11.2026")
    page.get_by_label("Klokkeslett").fill("07:00")
    page.get_by_label("Beløp", exact=True).check()
    page.get_by_label("Beløp i kr").fill("200")


@pytest.fixture
def antall_oppdrag(e2e_database_url: str) -> Callable[[str], int]:
    """Antall oppdrag med tittelen i E2E-databasen."""

    def _tell(tittel: str) -> int:
        motor = lag_motor(e2e_database_url)
        try:
            with motor.connect() as tilkobling:
                return tilkobling.scalar(
                    select(func.count()).select_from(Oppdrag).where(Oppdrag.tittel == tittel)
                )
        finally:
            motor.dispose()

    return _tell


@pytest.fixture
def bruker_id(e2e_database_url: str) -> Callable[[str], int]:
    """Id-en til en testbruker etter seed, slått opp i E2E-databasen."""

    def _finn(epost: str) -> int:
        motor = lag_motor(e2e_database_url)
        try:
            with motor.connect() as tilkobling:
                verdi = tilkobling.scalar(select(Bruker.id).where(Bruker.epost == epost))
        finally:
            motor.dispose()
        assert verdi is not None, f"Fant ikke {epost} i E2E-databasen"
        return verdi

    return _finn
