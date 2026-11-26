# Story 1.5: Automatisk test av universell utforming

## 2026-11-25 kl. 11:58 — Heidi

### Oppgave
Bygge story 1.5 (T1: automatisk test av universell utforming med Playwright og axe) med `bmad-build`. Som før skulle storyen først settes til `in-progress` og pushes.

### Plan
- Satte `1-5-automatisk-test-av-universell-utforming: in-progress` på `main`, pushet (`cdc1633`) og laget branchen `story/1-5-automatisk-test-uu`.
- Skrev specen [spec-1-5-automatisk-test-uu.md](../../_bmad-output/implementation-artifacts/spec-1-5-automatisk-test-uu.md) ut fra epics, AD-14, AR-29, UX-DR31 og versjonene i arkitekturen. Heidi godkjente den hel (cirka 2 800 tokens).
- En subagent implementerte specen. Tre reviewere gikk gjennom diffen, og funnene ble vurdert i triage-loggen i specen og rettet av den samme agenten.

### Resultat
- **Testoppsett:**
  - `playwright~=1.65.2`, `pytest-playwright~=0.10.0` og `axe-playwright-python~=0.1.9` i dev.
  - Markøren `e2e`. Vanlig `uv run pytest` hopper over E2E (`-m "not e2e"`), så den virker uten nettleser (NFR-1).
- **`POST /_test/tilstand`** (`app/core/testtilstand.py`):
  - Finnes bare i `test`. Den stiller klokka, setter KI-utgaven (`mock`/`feil`) og laster testbrukerne på nytt (`seed.last_eksempeldata`, koblet inn via `app.state`).
  - Ugyldige verdier gir 400. I `local` og `production` gir stien 404.
- **T1** (`tests/e2e/`):
  - Uvicorn i en tråd med egen SQLite-fil.
  - 11 sider og tilstander sjekkes med axe ved 360 og 1280 px og for vannrett rulling ved 320 px.
  - En kontrolltest med et bevisst brudd viser at filteret faktisk feiler.
  - Tester av «Vis passord», sendeknappen (`aria-disabled`, `pageshow`) og poststed.
- **Brudd:** axe og 320 px-sjekken fant ingen brudd på dagens sider, så malene og CSS-en er uendret.
- **CI:** ny jobb, «T1 (Playwright og axe)». README forklarer hvordan T1 kjøres lokalt.
- **Tester:** `uv run pytest` gir 498 bestått (37 E2E valgt bort). `uv run pytest -m e2e` gir 37 bestått. T1-jobben i CI har ikke kjørt ennå.
- **Review:** 26 funn.
  - 8 rettet: kontrolltest for axe og 320 px, røyktest mot testappen, `ki` nullstilles, CSRF-hjelperen virker når nettleseren er innlogget, klokke før seed er testet, poststed `0000`, sending etter `pageshow`, og navn i røyktest-testene.
  - 1 utsatt (vakt mot `APP_ENV=test` på Vercel, i `deferred-work.md`).
  - Resten avvist med begrunnelse.
- **Status:** specen er `done`, og storyen står som `review`.
- **Commits på branchen:** `1a840c4`, `322eb4f`, `09546ed`, `60ea301`, `e638b1b`, `615fa26`, `f7c3730`, `de8d861`, `71f5267`. Branchen er ikke pushet.
- **Lukket i `issues.md`:**
  - JS-oppførselen i T1 (fra 1.2).
  - Playwright-test av `poststed.js` (fra 1.4). Sjekken som ignorerer utdaterte svar, er fortsatt utestet og notert i `deferred-work.md`.

### Åpne punkter
- **Etter push og merge av story 1.5:** T1-jobben skal være grønn i CI (første kjøring på GitHub), og story 1.5 skal settes til `done`. Da er Epic 1 ferdig før sjekkpunktet 28. november.
- **Vakt i `Settings`:** nekt `APP_ENV=test` og `local` når `VERCEL` er satt (B5 i triage-loggen, `deferred-work.md`).

## 2026-11-26 kl. 21:28 — Heidi

### Oppgave
Heidi ba om push og PR for story 1.5.

### Plan
- Pushet branchen og åpnet PR mot `main`, med samme oppsett som PR #4.

### Resultat
- `story/1-5-automatisk-test-uu` er pushet til origin.
- PR #5: https://github.com/IBE160-2026/G22-bernardo-kverno-moystad-nguyen/pull/5 (sjekkliste for etter merge i PR-beskrivelsen).
- CI startet med fire jobber, blant dem den nye «T1 (Playwright og axe)». De var ikke ferdige da loggen ble skrevet.

### Åpne punkter
- Ingen nye. Punktene fra forrige seksjon gjelder fortsatt: T1 grønn i CI og story 1.5 til `done` etter merge, og vakten mot `APP_ENV=test` på Vercel.

## 2026-11-26 kl. 21:37 — Heidi

### Oppgave
Heidi ba om merge av PR #5 når alle CI-jobbene var grønne.

### Plan
- Ventet på CI for siste commit i PR-en, merget med merge-commit (som #4) og fulgte `Deploy`.
- Sjekket `/_test/tilstand` i produksjon.

### Resultat
- CI var grønn på `171d9ef`: gitleaks, pytest (SQLite) og alembic heads, pytest (Postgres), og T1 (Playwright og axe) på 58 s. Det var første kjøring av T1 på GitHub.
- PR #5 er merget som `8290941`.
- `Deploy` (kjøring 45892049950) er grønn: CI med T1, migrering, deploy og røyktest.
- I produksjon gir `GET /_test/tilstand` 404. `POST` uten token gir 403, fordi CSRF-sjekken avviser forespørselen før rutingen. Ruta finnes altså ikke.
- Etter at Heidi ba om det, ble story 1.5 og Epic 1 satt til `done` i `sprint-status.yaml`, og resultatet fra CI og produksjon ble ført i Implementation Notes i specen (`167cc5d`). Epic 1 ble altså ferdig før sjekkpunktet 28. november.
- Lukket i `issues.md`: punktet om T1 i CI og `done`, og sjekkpunktet 28. november.

### Åpne punkter
- Vakten mot `APP_ENV=test` på Vercel står fortsatt åpen (`deferred-work.md`).
