---
title: 'Story 1.5: Automatisk test av universell utforming'
type: 'feature'
created: '2026-11-25'
baseline_commit: 'cdc16337b2bf3095ffcab26fa65f488e811040b1'
status: 'in-progress'
route: 'dispatch'
review_loop_iteration: 0
story_key: '1-5-automatisk-test-av-universell-utforming'
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-1-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Ingen test åpner sidene i en ekte nettleser. Tilgjengelighetsfeil, vannrett rulling ved 320 px og feil i JS-oppførselen («Vis passord», sendeknappen, poststed) oppdages først i manuelle sjekker rett før innlevering (SM-5, NFR-6, NFR-7).

**Approach:** T1 kjøres som E2E-tester med Playwright og axe mot en ekte server (uvicorn i en tråd, `APP_ENV=test`, egen SQLite-fil). Testene setter tilstanden gjennom `POST /_test/tilstand`, som finnes bare i `test` (AD-14). Hver side og tilstand fra Epic 1 sjekkes med axe ved 360 og 1280 px og for vannrett rulling ved 320 px. T1 får en egen jobb i CI, og README forklarer hvordan testen kjøres lokalt.

## Boundaries & Constraints

**Always:** Versjonene fra arkitekturen: `playwright~=1.65.2`, `pytest-playwright~=0.10.0` og `axe-playwright-python~=0.1.9`, i dependency-gruppen `dev`. Alt installeres med uv, uten npm. axe feiler testen ved brudd med `impact` «serious» eller «critical». Feilmeldingen viser regel-id, impact og selektor. `/_test/tilstand` registreres bare når `settings.test`, og i `local` og `production` gir stien 404. Brudd som axe eller 320 px-sjekken finner, rettes i denne storyen i malene eller i CSS. Krav-ID-er står i commits og tester.

**Beslutninger (godkjent av Heidi 2026-11-25; specen beholdes hel, selv om den er over grensen på 1 600 tokens):**
- E2E-testene har markøren `e2e`, og vanlig `uv run pytest` hopper over dem (`-m "not e2e"` i `addopts`). Da virker README-kommandoen på en ren maskin uten nettleser (NFR-1). T1 kjøres med `uv run pytest -m e2e` etter `uv run playwright install chromium`.
- CI får en egen jobb, «T1 (Playwright og axe)», mot SQLite.
- `/_test/tilstand` er offentlig (`@offentlig`), siden E2E nullstiller før innlogging. CSRF gjelder som vanlig, så hjelperen henter nøkkelen fra `/logg-inn` først.
- Feltene er:
  - `klokke`: ISO 8601 med tidssone, eller tom for vanlig klokke.
  - `ki`: `mock` eller `feil`. Lagres i `app.state.ki_utgave` til story 5.1.
  - `seed=1`: tømmer `sesjon`, `innloggingsforsok` og `bruker`, og legger inn testbrukerne på nytt.
  - Ukjent verdi gir 400.
- JS-testene som er utsatt hit, tas med: «Vis passord» (fra 1.2), `aria-disabled` og `pageshow` på sendeknappen (fra 1.2) og `poststed.js` (fra 1.4, `deferred-work.md`).
- Andres profil (`/profil/{id}`) er med i T1, i tillegg til lista i storyen.

**Never:** npm, `package.json` eller et byggsteg. Ruta `/_test/tilstand` utenfor `test`. Ekte KI. E2E mot den delte test-databasen som pytest ruller tilbake. Å senke kravet fra axe med `disable_rules`, eller utelate en side for å få testen grønn.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Tilstand i `test` | POST `klokke=2026-11-24T12:00:00+00:00&ki=feil&seed=1` + CSRF | 204, `klokke.na()` er satt, `ki_utgave == "feil"`, akkurat de seks testbrukerne finnes, ingen sesjoner | – |
| Ugyldig verdi | `klokke=i går`, `klokke` uten tidssone, `ki=ekte`, `seed=2` | 400, ingenting endret | – |
| Uten CSRF | POST uten nøkkel | 403 (som for alle POST) | – |
| Andre miljøer | `APP_ENV=local` eller `production`, POST/GET `/_test/tilstand` | 404 | – |
| T1 axe | hver side × 360 og 1280 px | ingen brudd «serious» eller «critical» | test feiler med regel, impact og selektor |
| T1 320 px | hver side ved 320 px | `scrollWidth <= clientWidth` på `documentElement` | test feiler med siden og bredden |
| Vis passord | klikk på knappen, og så på nytt / send skjemaet | `type=text` og `aria-pressed=true`, så `password`/`false` / `password` ved innsending | – |
| Sending | submit med `preventDefault` i en egen lytter, så submit igjen, så `pageshow` | `aria-disabled=true`, andre submit stoppes, `aria-disabled` fjernes ved `pageshow` | – |
| Poststed | skriv `5006`, så `57` | «Bergen» i `#postnummer-sted`, så tomt | – |

</frozen-after-approval>

## Code Map

- `app/__init__.py:lag_app` -- tar `settings`. Når `settings.test` er sann: ta med ruteren fra `app/core/testtilstand.py`, og sett `app.state.last_eksempeldata = seed.last_eksempeldata` og `app.state.ki_utgave = "mock"`. Core når seed bare gjennom `app.state`, som `Autentisering` (AD-1).
- `app/seed.py` -- `legg_inn_testbrukere(db)` og `TESTBRUKERE` (Kari: `kari@eksempel.no` / `kari-lokal-1`, 0571). Ny `last_eksempeldata(db)`: sletter `Sesjon`, `Innloggingsforsok` og `Bruker` i den rekkefølgen, og legger inn testbrukerne. Committer ikke. Senere stories legger til egne tabeller her.
- `app/core/klokke.py:sett_na` -- krever aware datetime.
- `app/core/csrf.py` -- POST krever skjema med `csrf_token` som stemmer med cookien. `Origin`, hvis den finnes, må være samme vert.
- `app/core/sesjon.py:offentlig`.
- `tests/core/test_tilgang.py:22` `OFFENTLIGE` -- legg til `("POST", "/_test/tilstand")`, fordi testappen kjører i `test`.
- `tests/core/test_arkitektur.py:157` `test_ingen_testruter_i_lag_app` -- skal nå sjekke at `local` og `production` ikke har `/_test`-ruter, og at `test` har akkurat `/_test/tilstand`. Rutenavnet blir `core.test_tilstand`.
- `tests/test_roykttest.py` -- `klient` er testappen, der `/_test/tilstand` nå finnes, så GET gir 405 og ikke 404. Kjør røyktesten mot en app med `Settings(app_env="local", database_url=<test-databasen>)` og samme `sesjonsfabrikk`.
- `tests/conftest.py` -- `alembic_config(tilkobling)` og `lag_motor` gjenbrukes for E2E-databasen.
- `.github/workflows/ci.yml` -- mønster for `checkout@v7`, `setup-uv@v10.3.3` (uv 0.12.13) og `uv sync --locked`.
- Sidene i T1: `/logg-inn` (tom og etter tom innsending), `/registrer` (tom og etter tom innsending), og som Kari `/` (tomtilstand), `/mine-oppdrag`, `/profil`, `/profil/{id}` (Ola), `/finnes-ikke` (404) og 401-siden. 401-siden: slett bare cookien `sesjon` (`context.clear_cookies(name="sesjon")`) på `/profil`, og trykk «Logg ut».
- `README.md` § Kjør testene -- legg til T1.

## Tasks & Acceptance

**Execution:**
- [ ] `pyproject.toml`, `uv.lock` -- dev-avhengighetene, markøren `e2e` og `-m "not e2e"` i `addopts` -- AR-29, NFR-1
- [ ] `app/seed.py`, `tests/test_seed_og_admin.py` -- `last_eksempeldata(db)` med test -- AR-29
- [ ] `app/core/testtilstand.py`, `app/__init__.py`, `tests/core/test_testtilstand.py` -- `POST /_test/tilstand` (`core.test_tilstand`, `@offentlig`) med 204 eller 400, bare i `test`, og tester for radene om tilstand i I/O-matrisen -- AD-14, AR-29
- [ ] `tests/core/test_tilgang.py`, `tests/core/test_arkitektur.py`, `tests/test_roykttest.py` -- oppdatert etter Code Map -- FR-3, AD-14
- [ ] `tests/e2e/conftest.py` -- server i tråd på ledig port med egen SQLite-fil i temp-mappen, migrert med Alembic. Fixturer `server_url`, `tilstand(page, **felt)` (henter CSRF fra `/logg-inn`) og `logg_inn_som_kari(page)`. Klokka nullstilles etter økta -- AR-29
- [ ] `tests/e2e/test_t1.py` -- parametrisert over sidene × 360/1280 med axe, og × 320 for rulling. Kjører `seed=1` og fast klokke før hver test -- SM-5, NFR-6, NFR-7, UX-DR5, UX-DR31
- [ ] `tests/e2e/test_klientatferd.py` -- Vis passord, sending og poststed etter matrisen -- UX-DR13, UX-DR28
- [ ] maler og `app/core/static/css/app.css` -- rett det axe og 320 px-sjekken finner, og før hvert funn i Implementation Notes -- NFR-6, NFR-7
- [ ] `.github/workflows/ci.yml` -- jobben «T1 (Playwright og axe)»: `uv sync --locked`, `uv run playwright install --with-deps chromium`, `uv run pytest -m e2e` -- AR-7, SM-5
- [ ] `README.md` -- hvordan T1 kjøres lokalt, at vanlig `pytest` hopper over den, og at senere stories legger nye sider inn i T1 -- AR-10, SM-5

**Acceptance Criteria:**
- Gitt `uv run pytest` på en maskin uten Playwright-nettlesere, så er alt grønt, og E2E-testene er valgt bort (ikke feilet).
- Gitt `uv run pytest -m e2e` lokalt og i CI, så er T1 og JS-testene grønne, og CI viser jobben «T1 (Playwright og axe)».
- Gitt en side med et bevisst brudd (for eksempel et `<input>` uten etikett), så feiler T1 med regel-id og selektor. Prøves lokalt én gang, og resultatet føres i Implementation Notes.

## Implementation Notes

## Spec Change Log

## Review Triage Log

## Design Notes

- **Egen server og database for E2E:** pytest sin test-database rulles tilbake per test. En nettleser trenger committede data og en ekte HTTP-server. Uvicorn i en tråd i samme prosess deler `klokke`, så `/_test/tilstand` kan stille klokka uten en ny prosess.
- **Seed via `app.state`:** `core` importerer aldri slices (AD-1). `lag_app()` kobler inn `seed.last_eksempeldata` på samme måte som `Autentisering`.

## Verification

**Commands:**
- `uv run pytest` -- expected: grønn, E2E valgt bort
- `uv run playwright install chromium` og `uv run pytest -m e2e` -- expected: grønn

**Manual checks (if no CLI):**
- Etter push: CI viser fire jobber, og alle er grønne.
