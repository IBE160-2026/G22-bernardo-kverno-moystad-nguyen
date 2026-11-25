---
title: 'Story 1.5: Automatisk test av universell utforming'
type: 'feature'
created: '2026-11-25'
baseline_commit: 'cdc16337b2bf3095ffcab26fa65f488e811040b1'
status: 'done'
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
- [x] `pyproject.toml`, `uv.lock` -- dev-avhengighetene, markøren `e2e` og `-m "not e2e"` i `addopts` -- AR-29, NFR-1
- [x] `app/seed.py`, `tests/test_seed_og_admin.py` -- `last_eksempeldata(db)` med test -- AR-29
- [x] `app/core/testtilstand.py`, `app/__init__.py`, `tests/core/test_testtilstand.py` -- `POST /_test/tilstand` (`core.test_tilstand`, `@offentlig`) med 204 eller 400, bare i `test`, og tester for radene om tilstand i I/O-matrisen -- AD-14, AR-29
- [x] `tests/core/test_tilgang.py`, `tests/core/test_arkitektur.py`, `tests/test_roykttest.py` -- oppdatert etter Code Map -- FR-3, AD-14
- [x] `tests/e2e/conftest.py` -- server i tråd på ledig port med egen SQLite-fil i temp-mappen, migrert med Alembic. Fixturer `server_url`, `tilstand(page, **felt)` (henter CSRF fra `/logg-inn`) og `logg_inn_som_kari(page)`. Klokka nullstilles etter økta -- AR-29
- [x] `tests/e2e/test_t1.py` -- parametrisert over sidene × 360/1280 med axe, og × 320 for rulling. Kjører `seed=1` og fast klokke før hver test -- SM-5, NFR-6, NFR-7, UX-DR5, UX-DR31
- [x] `tests/e2e/test_klientatferd.py` -- Vis passord, sending og poststed etter matrisen -- UX-DR13, UX-DR28
- [x] maler og `app/core/static/css/app.css` -- rett det axe og 320 px-sjekken finner, og før hvert funn i Implementation Notes -- NFR-6, NFR-7
- [x] `.github/workflows/ci.yml` -- jobben «T1 (Playwright og axe)»: `uv sync --locked`, `uv run playwright install --with-deps chromium`, `uv run pytest -m e2e` -- AR-7, SM-5
- [x] `README.md` -- hvordan T1 kjøres lokalt, at vanlig `pytest` hopper over den, og at senere stories legger nye sider inn i T1 -- AR-10, SM-5

**Acceptance Criteria:**
- Gitt `uv run pytest` på en maskin uten Playwright-nettlesere, så er alt grønt, og E2E-testene er valgt bort (ikke feilet).
- Gitt `uv run pytest -m e2e` lokalt og i CI, så er T1 og JS-testene grønne, og CI viser jobben «T1 (Playwright og axe)».
- Gitt en side med et bevisst brudd (for eksempel et `<input>` uten etikett), så feiler T1 med regel-id og selektor. Prøves lokalt én gang, og resultatet føres i Implementation Notes.

## Implementation Notes

- **Funn fra axe og 320 px-sjekken:** ingen. Første kjøring av T1 var grønn på alle 11 sider og tilstander ved 360, 1280 og 320 px, så maler og `app.css` er ikke endret. For å se at axe faktisk kjører, ble T1 kjørt én gang med alle alvorlighetsgrader (også «moderate» og «minor»): heller ingen brudd. Kravet i testen er fortsatt bare «serious» og «critical».
- **Bevisst brudd (akseptansekriterium 3), prøvd lokalt 2026-11-25:** et `<input type="text">` uten etikett og en `<div style="width: 400px">` ble lagt midlertidig i `logg_inn.html`. T1 feilet på «logg-inn» med `label (critical): input[type="text"] – Form elements must have labels` ved 360 og 1280 px, og med `Vannrett rulling på «logg-inn» ved 320 px: scrollWidth 416 > clientWidth 320`. Malen ble satt tilbake etterpå.
- **Sider i T1:** lista i Code Map pluss «logg-inn-logget-ut» (innloggingssiden med kvitteringen «Du er logget ut.»), som også er en tilstand fra Epic 1.
- **`/_test/tilstand`:** ukjent feltnavn gir også 400, ikke bare ukjent verdi. Klokka settes før seed, så testbrukerne får `opprettet` fra den faste klokka. Alle verdier sjekkes før noe endres.
- **Klokka** nullstilles etter hver E2E-test og etter økta, så `uv run pytest -m "e2e or not e2e"` (alt i én kjøring) også er grønn.
- **Advarsel fra pytest-playwright 0.10** (`base_url`-fixturen er en metode i en klasse) er filtrert bort i `pyproject.toml`; den gjelder pluginen, ikke testene.
- **axe.min.js** lastes med `Axe.from_file(AXE_FILE_PATH)`, fordi biblioteket ellers leser fila med systemets tegnsett på Windows.
- **Sendeknappen:** andre innsending gjøres med Enter i e-postfeltet, fordi Playwright regner `aria-disabled="true"` som deaktivert og ikke vil klikke. Det er også slik en bruker kan sende på nytt.

## Spec Change Log

## Review Triage Log

Runde 1 (2026-11-25). B = blind, K = kanttilfeller, V = verifikasjonshull. Patch = rettes i denne runden.

| # | Funn | Verdikt | Begrunnelse | Rute |
|---|------|---------|-------------|------|
| B1 | `ki_utgave` nullstilles ikke mellom E2E-testene | low | Stemmer: `nullstill` sender bare `seed` og `klokke`, og serveren deles i hele økta. Ingen test setter `feil` ennå, men story 5.1 kommer til å gjøre det. Rettingen er ett felt til | patch (med K4) |
| B2 | `SIDER` mangler feil passord, sperre, registrering med serverfeil, 403, 500, nødsiden og 401-fragmentet | low | Feil passord, sperre og serverfeil bruker samme mal og markup som tom innsending. 403 og 500 bruker `core/feil.html`, som 404 dekker. Nødsiden og fragmentet er ikke sider en bruker navigerer til | avvist |
| B3 | At klokka settes før seed, er ikke testet | low | Stemmer, og rettingen er én ekstra sjekk av `opprettet` i en test som finnes | patch |
| B4 | En feil i seed etter at klokka er satt gir 500 med endret klokke | low | Bare i `test`, og krever en databasefeil. Docstringen lover «ingenting endret» bare ved 400, og det holder | avvist (med K1) |
| B5 | Bare `APP_ENV` hindrer at `/_test/tilstand` og standardnøkkelen kommer i produksjon | medium | Stemmer. Feilkonfigureringen fantes fra før (`APP_ENV=local` på Vercel gir også standardnøkkelen), men skaden blir større nå. Røyktesten oppdager det etter publisering (V2). Rettingen er en ny vakt i `Settings` | defer |
| B6 | CI lagrer ikke spor eller skjermbilder når T1 feiler, og Chromium caches ikke | low | Gjelder bare feilsøking. Nye steg er mer enn en direkte retting | avvist |
| B7 | Poststed-testen prøver ikke et firesifret nummer som ikke finnes | low | Stemmer. `aria-live` er allerede testet i `test_registrering.py` | patch (med K8) |
| B8 | `pageshow` testes med en syntetisk hendelse og ikke med ekte tilbakeknapp | low | Sidene har `no-store`, så bfcache er lite forutsigbart i nettleseren. Den syntetiske hendelsen tester lytteren | avvist |
| B9 | axe sine `incomplete`-resultater ignoreres | low | Kontrast som axe ikke kan avgjøre, dekkes av T5 (manuell, UX-DR32). Varsler ville vært ny logikk | avvist (med K6) |
| B10 | Ingen test av tastatur, tvungne farger eller redusert bevegelse | false | T1 er axe og 320 px (UX-DR31). Tastatur og tvungne farger er T2 og T5, manuelle protokoller i story 6.1 (UX-DR32) | avvist |
| B11 | `test_roykttest.py` kaller den lokale appen «testappen» | low | Stemmer, og rettingen er tekst | patch |
| K1 | Seed feiler etter at klokka er satt | low | Samme som B4 | avvist (med B4) |
| K2 | `klokke` nær `datetime.min` eller `max` gir `OverflowError` og 500 | low | Bare testene sender verdier hit. Rettingen er en ny vakt | avvist (med K12) |
| K3 | Samme felt sendt to ganger: den siste verdien vinner | low | Bare testene sender skjemaet. Ingen kaller sender felt to ganger | avvist |
| K4 | `ki` lekker mellom testene | low | Samme som B1 | patch (med B1) |
| K5 | `tilstand()` feiler når nettleseren er innlogget, fordi `/logg-inn` gir 303 | low | Stemmer, og story 5.1 trenger det (KI-feil etter innlogging). Rettingen er en reserve på `/profil` | patch |
| K6 | `incomplete` fra axe ignoreres | low | Samme som B9 | avvist (med B9) |
| K7 | `overflow-x: hidden` kan skjule innhold, så 320 px-sjekken passerer | false | `app.css` har ingen `overflow`-regler, bare `overflow-wrap` | avvist |
| K8 | Firesifret nummer som ikke finnes | low | Samme som B7 | patch (med B7) |
| K9 | `pytest tests/e2e/test_t1.py` uten `-m e2e` velger bort alt og gir kode 5 | low | README sier `uv run pytest -m e2e`. En hook ville vært ny logikk | avvist |
| K10 | Motoren til appen i røyktest-testene lukkes ikke | low | SQLite-filen ryddes med `ignore_errors`, og det har ingen merkbar virkning | avvist (med K11) |
| K11 | Motorer fra parametriserte `lag_app()` lukkes ikke | low | Samme som K10 | avvist (med K10) |
| K12 | Påstand: «ukjent verdi gir 400» holder ikke for ekstreme `klokke` | low | Samme som K2 | avvist (med K2) |
| V1 | Ingen test viser at `alvorlige_brudd` og 320 px-uttrykket kan feile | gap | Arkivert evidens: kriterium 3 ble bare prøvd for hånd. Et filter som slipper alt, ville gitt grønn T1 for alltid | patch |
| V2 | Sjekken av 404 for `/_test/tilstand` i røyktesten er aldri kjørt mot en app som har ruta | gap | Arkivert evidens: alle røyktest-testene bruker nå appen med `local` | patch |
| V3 | Sendeknappen sendes ikke på nytt etter `pageshow` | low | Stemmer: en `pageshow` som glemte `data-sender` på skjemaet, ville passert testen. Rettingen er én innsending til i testen | patch |

## Design Notes

- **Egen server og database for E2E:** pytest sin test-database rulles tilbake per test. En nettleser trenger committede data og en ekte HTTP-server. Uvicorn i en tråd i samme prosess deler `klokke`, så `/_test/tilstand` kan stille klokka uten en ny prosess.
- **Seed via `app.state`:** `core` importerer aldri slices (AD-1). `lag_app()` kobler inn `seed.last_eksempeldata` på samme måte som `Autentisering`.

## Verification

**Commands:**
- `uv run pytest` -- expected: grønn, E2E valgt bort
- `uv run playwright install chromium` og `uv run pytest -m e2e` -- expected: grønn

**Manual checks (if no CLI):**
- Etter push: CI viser fire jobber, og alle er grønne.
