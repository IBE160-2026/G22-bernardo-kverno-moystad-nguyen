---
title: 'T-1: Herding etter Epic 1, før story 2.1'
type: 'bugfix'
created: '2026-11-26'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '76ea67c1e404e7d9756bee56b1359af072e741be'
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-1-retro-2026-11-26.md'
  - '{project-root}/_bmad-output/implementation-artifacts/epic-1-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Retrospektivet for Epic 1 fant feil i grensene mellom storyene. Røyktesten (1.3) kan gjøres rød av hvem som helst etter at registreringen ble åpnet (1.4) (R1), og den grønne stien er aldri testet (V2). Registreringen rydder ikke `innloggingsforsok` (R2). Deploy kan startes fra en annen branch enn main (R4). `main.py` importeres ikke av noen test (V1). Ingen test sjekker hvilken meny som vises ved hvilken bredde (V3). `APP_ENV=test`/`local` på Vercel stoppes ikke (B5). README-statusen er utdatert (S5).

**Approach:** Én samlet herding, tiltak T-1 (a)–(g) i retroen, med én test per retting og krav-ID i tester og commits. Ingen ny funksjonalitet for brukerne.

**Beslutninger (Heidi, 2026-11-26):**
- R1: Røyktesten logger inn med en e-post som ikke kan registreres, `roykttest@nabolagshelten` (domenet mangler punktum, så `sjekk_epostformat` avviser den). Registreringen endres ikke. Demokontosjekken fjernes fra røyktesten. NFR-2 hviler på at seed nekter å kjøre i produksjon (`test_seed_nekter_i_produksjon`). En test binder røyktest-e-posten til `sjekk_epostformat`, så den aldri kan bli registrerbar.
- Omfang: hele T-1 (a–g) i én spec og én PR, selv om specen er over 1 600 tokens.

## Boundaries & Constraints

**Always:** Invariantene fra tidligere stories holdes (T-6): røyktesten registrerer aldri kontoer og skriver aldri ut cookies eller nøkler (1.3/1.4). Innlogging gir samme melding for ukjent e-post og feil passord, og sperren er 5 forsøk på 15 min (1.2). Seed nekter å kjøre i produksjon (AD-14). Tekstene i røyktesten hentes fra appen. Services committer aldri (AD-17).

**Never:** Ingen migrering, ingen ny side, ingen endring i feiltekstene i EXPERIENCE.md. T-2 til T-7 er utenfor omfanget. Ingen endring i Vercel- eller GitHub-innstillinger.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Røyktest grønn sti | App med `APP_ENV=production` over https, uten demokonto | `kjor()` gir `[]` | N/A |
| Røyktest etter åpen registrering | Kari med seed-passordet finnes i databasen | Røyktesten er fortsatt grønn (den bruker ikke Karis e-post lenger) | N/A |
| Røyktest-e-posten registreres | `registrer` med `roykttest@nabolagshelten` | Avvises med `EPOST_FORMAT` | 422 |
| Registrering etter mislykkede forsøk | 4 mislykkede innlogginger med e-posten, så registrering | Forsøkene er slettet. Ett nytt feil passord gir ikke sperre | N/A |
| Registrering med feil | Ugyldig skjema | `RegelBrudd` som før, forsøkene røres ikke | 422 som før |
| Deploy fra annen branch | `workflow_dispatch` på `story/x` | Jobben `deploy` hoppes over | N/A |
| Vercel med feil miljø | `VERCEL=1` og `APP_ENV` = `local` eller `test` | Oppstarten stopper med tydelig melding | `KonfigFeil` |
| Vercel i produksjon | `VERCEL=1`, `APP_ENV=production`, ekte nøkkel, Postgres | Godtas | N/A |
| Meny 360 px / 1280 px | Innlogget | Bare bunnmenyen synlig ved 360, bare topplinjemenyen ved 1280 | N/A |

</frozen-after-approval>

## Code Map

- `scripts/roykttest.py` -- `SEED_EPOST`/`SEED_PASSORD` (l. 51–52) erstattes av `ROYKTTEST_EPOST` og et fast passord. Steg 3 i `_sjekk` (l. 118–145): 303 betyr nå «røyktest-e-posten logget inn» (umulig, men meldes som avvik). Docstringen oppdateres. Grønn sti krever https, fordi CSRF-cookien får `Secure` i produksjon.
- `tests/test_roykttest.py` -- fixture `klient` (APP_ENV=local) og `MANGLER_SECURE`. `test_roykttesten_finner_demokonto` erstattes av en test der Kari med seed-passordet finnes og røyktesten likevel bare gir `[MANGLER_SECURE]`. Ny test: `sjekk_epostformat(normaliser_epost(ROYKTTEST_EPOST))` er `False`. Ny fixture for produksjon: `Settings(_env_file=None, app_env="production", secret_key="x"*32, database_url="postgresql+psycopg://u@h:5432/d")` (motoren kobler aldri til). Bytt `app.state.sesjonsfabrikk` som i `klient`, og bruk `TestClient(app, base_url="https://testserver")` med `kjor("https://testserver", ...)`.
- `app/identity/service.py` -- `registrer` (l. 284–367): slett `Innloggingsforsok` for `epost_` før `opprett_sesjon`, slik innloggingen gjør (l. 227). Ingen endring i `logg_inn`.
- `tests/identity/test_sperre.py` / `test_registrering.py` -- mønsteret for sperre og registrering over HTTP. Den nye testen legges der den passer best.
- `.github/workflows/deploy.yml` -- jobben `deploy` (l. 37): `if: github.ref == 'refs/heads/main'`. Jobben `ci` kan kjøre uansett.
- `main.py` -- importeres i en ny test. `tests/conftest.py` setter `APP_ENV=test` og `DATABASE_URL` før import. Kast motoren etterpå.
- `app/core/config.py` -- `Settings`: nytt felt `vercel: str = ""` (miljøvariabelen `VERCEL`, som Vercel setter). I `_sjekk_miljo`: er `vercel` satt og `app_env != "production"`, gis `ValueError`.
- `tests/core/test_config.py` -- hjelperen `lag()`, `EKTE_NOKKEL`, `POSTGRES_URL`. `monkeypatch.delenv("VERCEL")` i standardtesten.
- `tests/e2e/test_klientatferd.py` -- ny test. Bruker `logg_inn_som_kari` (`tests/e2e/conftest.py`), `page.set_viewport_size`, klassene `.meny--topp` og `.meny--bunn` (`app/core/static/css/app.css` l. 278–410, brytning ved 48em).
- `README.md` -- l. 15 og 24 (status) og l. 118 (røyktesten: ikke lenger Karis passord eller demokontosjekk, og kan nå kjøres mot en lokal server med seed).
- `_bmad-output/implementation-artifacts/deferred-work.md` -- B5-punktet får `resolution`.
- `_bmad-output/implementation-artifacts/sprint-status.yaml` -- `epic-1-retro-T1-herding` settes til `done` etter merge.

## Tasks & Acceptance

**Execution:**
- [x] `scripts/roykttest.py` -- logg inn med `ROYKTTEST_EPOST` i stedet for Kari, og oppdater docstring -- R1
- [x] `tests/test_roykttest.py` -- grønn sti mot en produksjonsapp (`== []`), Kari-finnes-test, test av at e-posten ikke kan registreres -- R1, V2, AD-14
- [x] `app/identity/service.py` + test -- `registrer` sletter forsøkene for e-posten. Test: 4 mislykkede forsøk, registrering, utlogging, 1 feil passord gir `FEIL`, ikke `SPERRET` -- R2, FR-2
- [x] `.github/workflows/deploy.yml` -- ref-vakt på `deploy`, og en kommentar -- R4, AR-7
- [x] `tests/test_main.py` -- importer `main` og sjekk at `main.app` er en `FastAPI` med ruta `identity.logg_inn` -- V1, AD-1
- [x] `app/core/config.py` + `tests/core/test_config.py` -- Vercel-vakt med test for local, test og production -- B5, AD-14
- [x] `tests/e2e/test_klientatferd.py` -- menysynlighet ved 360 og 1280 px -- V3, NFR-11, UX-DR3
- [x] `README.md` -- Epic 1 ferdig, Epic 2 neste. Røyktekst oppdatert -- S5
- [x] `deferred-work.md` -- resolution på B5

**Acceptance Criteria:**
- Given en kode-PR, when CI kjører, then `uv run pytest` og `uv run pytest -m e2e` er grønne, og ingen test kobler til en ekte Postgres utenfor Postgres-jobben.
- Given at workflowen leses, when `deploy.yml` inspiseres, then jobben `deploy` har `if: github.ref == 'refs/heads/main'`.

## Spec Change Log

## Review Triage Log

Pass 1 (2026-11-26). Lag: Blind Hunter (BH), Edge Case Hunter (EC), Verification Gap (VG: ingen hull funnet).

| # | Lag | Funn | Verdict | Begrunnelse | Rute |
|---|---|---|---|---|---|
| 1 | BH, EC | `concurrency` på workflownivå: en dispatch fra en annen branch (nå bare CI) går inn i gruppen `deploy-production` og kan avbryte en ventende publisering fra main | medium | Bekreftet i `deploy.yml` l. 24–27: gruppen er felles for alle refs, og GitHub beholder bare én ventende kjøring per gruppe | patch: `concurrency` flyttes til jobben `deploy` |
| 2 | BH | Ref-vakten kan omgås ved å endre workflowen på egen branch før dispatch, og kommentaren lover for mye | medium | Riktig: `workflow_dispatch` kjører branchens egen `deploy.yml`, og hemmelighetene er tilgjengelige. Risikoen fantes før T-1. Ekte vern krever et GitHub Environment, og det er en innstilling utenfor specen | patch (kommentaren) + defer (Environment `production`) |
| 3 | BH, EC | Grensen på 768 px står i docstringen, men bare 360 og 1280 testes | low | Riktig. Retten er bare to ekstra parametre | patch |
| 4 | BH | README-setningen om NFR-2 leses som en garanti for at ingen konto som kari@eksempel.no kan finnes | low | Riktig etter R1-beslutningen: kontoen kan registreres som en vanlig konto | patch (formulering) |
| 5 | BH | Importene i `tests/test_roykttest.py` står ikke i rekkefølge | low | Kosmetisk, en direkte retting | patch |
| 6 | BH | Vakten virker ikke hvis Vercel ikke gir funksjonen `VERCEL` | maybe-false | Avhenger av innstillingen «Automatically expose System Environment Variables» (standard på). Er den av, er tilstanden som før T-1. Kan bare avgjøres i Vercel. Ville i så fall vært low | avvist |
| 7 | BH | `VERCEL=0`/`false` tolkes som Vercel | low | Ingen i prosjektet setter dette. Retten ville lagt til en tolkningsregel | avvist |
| 8 | EC | `vercel env pull .env` eller `vercel dev` med `VERCEL=1` stopper den lokale appen | low | `vercel env pull` skriver til `.env.local` som standard, og `Settings` leser bare `.env`. `vercel dev` brukes ikke i prosjektet. Feilmeldingen sier hva som er galt | avvist |
| 9 | BH | `test_main` kjører med `APP_ENV=test`, kan få en bufret modul, og `finally` kan skjule feilen | low | Ingen annen test importerer `main` (grep), så modulen er ikke bufret. Produksjonsstien til `Settings` dekkes i `test_config.py`. En manglende `main.app` feiler testen uansett | avvist |
| 10 | BH | Arkitekturtesten vokter én jobb ved navn, ikke alle jobber med hemmeligheter | low | Gjelder en tenkt framtidig deling av jobben. Retten ville gjort testen mer kompleks | avvist |
| 11 | BH | R2-testene binder ikke normaliseringen av e-post, og det finnes ingen HTTP-test | false | `logg_inn` lagrer forsøk med `normaliser_epost`, og `registrer` sletter med `epost_ = normaliser_epost(epost)`, samme funksjon. Specen lot plasseringen av testen være åpen | avvist |
| 12 | BH | README sier «med retrospektiv og herding» mens herdingen er `in-review`, og T1 står `open` i sprint-status | low | README-teksten blir riktig ved merge. Tiltaket settes til `in-progress` nå og `done` etter merge, slik specen sier | avvist (ingen kodeendring) |

## Design Notes

Vercel setter `VERCEL=1` både ved bygging og ved kjøring. Produksjonsmiljøet i Vercel har `APP_ENV=production` (README § Hemmeligheter), så vakten slår ikke inn ved en vanlig publisering. Har noen fjernet `APP_ENV` der, feiler publiseringen synlig i stedet for å kjøre med standardnøkkelen.

## Verification

**Commands:**
- `uv run pytest` -- forventet: alle bestått (i dag 498 + nye)
- `uv run pytest -m e2e` -- forventet: alle bestått (i dag 37 + ny)

**Manual checks:**
- Etter merge: Deploy-workflowen på `main` er grønn, inkludert røyktesten mot produksjon.
