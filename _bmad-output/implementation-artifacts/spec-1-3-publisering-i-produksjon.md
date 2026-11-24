---
title: 'Story 1.3: Skjelett – appen publiseres i produksjon'
type: 'feature'
created: '2026-11-24'
status: 'in-review'
baseline_commit: '449786eafd63365d69b0b467c4c6e956ebc7a59d'
route: 'dispatch'
review_loop_iteration: 0
story_key: '1-3-skjelett-appen-publiseres-i-produksjon'
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-1-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Appen kjører bare lokalt og i CI. Ingen versjon kjører i produksjon, og det er ikke prøvd om mellomvaren, postnummerfila og databasetilkoblingen virker på Vercel mot Supabase. De risikoene skal oppdages i uke én (AR-1).

**Approach:** Hver merge til `main` som endrer kode, kjører `deploy.yml`. Den kjører `alembic upgrade head` mot Supabase gjennom session pooler, deretter `vercel deploy --prod`, og til slutt en automatisk røyktest mot produksjonsversjonen. `keepalive.yml` besøker appen hver tredje dag slik at det blir et databasekall. Heidi legger inn hemmelighetene selv. De står aldri i repoet eller i chatten.

## Boundaries & Constraints

**Always:** Hemmelighetene ligger bare i Vercel env (`APP_ENV=production`, `DATABASE_URL` på port 6543, `SECRET_KEY`) og i GitHub Secrets (`MIGRATION_DATABASE_URL` på port 5432, `VERCEL_TOKEN`, `VERCEL_ORG_ID`, `VERCEL_PROJECT_ID`). Workflows bruker aldri `pull_request_target`, og versjoner pinnes (`vercel@66.6.0`). Deploy-jobben avbrytes aldri midt i (`concurrency`, `cancel-in-progress: false`). Krav-ID-er skrives i commits.

**Beslutninger (Heidi 2026-11-24):** Supabase-prosjektet ligger i `eu-west-1` (Irland), så `vercel.json` har `"regions": ["dub1"]`. Vercel-prosjektet lages nytt med navnet `nabolagshelten`. Den endelige adressen (`nabolagshelten.vercel.app`, eller med suffiks hvis navnet er tatt) leses etter `vercel link` og brukes i README, keepalive og røyktesten. Specen beholdes hel, selv om den er over grensen på 1 600 tokens.

**Never:** seed eller demokontoer i produksjon, preview-miljø, Vercels GitHub-app, `create_all`, migreringer som fjerner noe etter første publisering, og hemmeligheter i logger (`--token` bare fra secrets, ingen `echo`).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Merge med kode | push til `main` | migrering → deploy → røyktest grønn | migrering feiler → ingen deploy |
| Bare logger eller dokumenter | push som bare endrer `.logs/`, `_bmad-output/`, `docs/`, `*.md` | ingen publisering | – |
| Røyktest `/logg-inn` | GET | 200, CSP `frame-ancestors 'none'`, `X-Frame-Options: DENY`, `nosniff`, `Referrer-Policy: same-origin` | avvik → jobben feiler |
| Røyktest innlogging | POST med CSRF-token, `Origin: https://<vert>`, `kari@eksempel.no` / seed-passordet | 422 med «Feil e-post eller passord.» (eller sperremeldingen) → CSRF gjennom proxyen, kropp avspilt, Supabase nådd, ingen demokonto | 403 → Origin-sjekken må rettes (oppgave 7) |
| Røyktest testrute og statiske filer | GET `/_test/tilstand`, GET `/static/css/app.css` | 404, 200 | avvik → jobben feiler |
| Postnummerfila mangler i funksjonen | `data/postnumre.tsv` ikke med | kaldstart feiler → røyktesten feiler | – |
| Keepalive | GET `/` med cookien `sesjon=keepalive` | 303 etter sesjonsoppslag i databasen | annet svar → jobben feiler (e-post fra GitHub) |

</frozen-after-approval>

## Code Map

- `main.py` -- Vercel-entrypoint (`app = lag_app()`), Vercel finner det i roten. Ikke endre.
- `app/__init__.py` -- `lag_app()`. Last postnummerregisteret her (`postnummer._register()`), så en manglende TSV-fil feiler ved oppstart og ikke senere.
- `app/core/postnummer.py` -- `TSV_STI`, `_register()` (`lru_cache`). TSV-fila er fortsatt kilden (deferred-punkt 2: de er like så lenge 0001 og fila er uendret).
- `app/core/csrf.py:_samme_opphav` -- `urlsplit(origin).netloc` mot `Host`. Endres bare hvis røyktesten gir 403 (deferred-punkt 1).
- `app/core/config.py` -- produksjon krever ekte `SECRET_KEY` på minst 32 tegn og en database som ikke er SQLite. Alembic (`migrations/env.py`) leser `DATABASE_URL` gjennom `hent_settings()` med `APP_ENV` standard `local`.
- `app/core/db.py:lag_motor` -- `NullPool` og `prepare_threshold=None` for Postgres finnes allerede (AD-13).
- `app/identity/service.py:finn_innlogget` -- spør databasen bare når cookien `sesjon` finnes. Keepalive bruker det.
- `.github/workflows/ci.yml` -- mønster for `actions/checkout@v7`, `astral-sh/setup-uv@v10.3.3` med uv `0.12.13` og `uv sync --locked`.
- `README.md` § Kom i gang (l. 26), § Kontoer for drift (l. 149), statustabellen (l. 13). Seed-passordet til Kari står på l. 56.
- `.gitignore` -- `.vercel/` og `.env*` er allerede ignorert.

## Tasks & Acceptance

**Execution:**
- [x] `app/__init__.py`, `tests/core/test_postnummer.py` -- last registeret i `lag_app()`. Testen sjekker at en manglende TSV-fil stopper oppstarten -- AR-1, AD-10
- [x] `vercel.json` -- `git.deploymentEnabled: false`, `regions: ["dub1"]`, `functions."main.py".maxDuration: 30` -- AR-7
- [x] `.vercelignore` -- utelat `_bmad/`, `_bmad-output/`, `.claude/`, `.logs/`, `docs/`, `tests/`, `*.db`, `.env*`. Behold `data/`, `migrations/` og `app/` -- AR-7
- [x] `scripts/roykttest.py` -- `uv run python scripts/roykttest.py <url>`, med httpx og radene i I/O-matrisen. Avslutter med kode 1 og en kort melding per avvik -- AD-5, AD-13, AD-14
- [x] `.github/workflows/deploy.yml` -- `push` til `main` med `paths-ignore` og `workflow_dispatch`. `permissions: contents: read`. Migrering med `DATABASE_URL: ${{ secrets.MIGRATION_DATABASE_URL }}`, så `npx --yes vercel@66.6.0 deploy --prod --yes --token`, så røyktesten -- AR-7, AD-13
- [x] `.github/workflows/keepalive.yml` -- `cron: '17 5 */3 * *'` og `workflow_dispatch`. `curl` med `sesjon=keepalive` og forventet 303 -- AR-7
- [x] `README.md` -- produksjonsadressen, hvordan publiseringen virker (navn på hemmelighetene, aldri verdier), at eieren sjekker Supabase før demo og innlevering, og oppdatert statustabell -- AR-10, NFR-3
- [ ] (bare ved 403) `app/core/csrf.py` + test -- godta den offentlige verten bak proxyen, og før funnet i `deferred-work.md` -- AD-5

**Manuelle oppgaver for Heidi** (i egen terminal eller nettleser, aldri i chatten): (M1) Hent tilkoblingsstrengene for transaction pooler (6543) og session pooler (5432) i Supabase. (M2) Kjør `npx vercel@66.6.0 login` og `npx vercel@66.6.0 link`, og les id-ene i `.vercel/project.json`. (M3) Legg inn Vercel env (Production): `APP_ENV`, `DATABASE_URL` og `SECRET_KEY`. Lag nøkkelen lokalt med `uv run python -c "import secrets; print(secrets.token_urlsafe(48))"`. (M4) Lag et Vercel-token. (M5) Kjør `gh secret set <NAVN>` for de fire GitHub-hemmelighetene. Verdien limes inn skjult.

**Acceptance Criteria:**
- Gitt merge av PR-en til `main`, så er `deploy.yml` grønn med migrering, deploy og røyktest, uten at Vercels GitHub-app er installert.
- Gitt `gh secret list` og `git grep` etter verdiene, så finnes de fire hemmelighetene i GitHub, og ingen verdier ligger i repoet. gitleaks i CI er grønn (NFR-3).
- Gitt produksjonsadressen i en nettleser, så kan Heidi sende innloggingsskjemaet og får «Feil e-post eller passord.», ikke 403.
- Gitt `keepalive.yml` kjørt manuelt med `workflow_dispatch`, så er den grønn.

## Implementation Notes

- Adressen er ikke kjent før Heidi har kjørt `vercel link` (M2). Bruk `https://nabolagshelten.vercel.app` i README og keepalive, og som standard i røyktesten. Adressen rettes hvis Vercel ga et suffiks. De manuelle oppgavene M1–M5 er Heidis, og de er ikke en del av implementeringen.

## Spec Change Log

## Review Triage Log

Runde 1 (2026-11-24). B = blind, K = kanttilfeller, V = verifikasjonshull. Patch = rettes i denne runden.

| # | Funn | Verdikt | Begrunnelse | Rute |
|---|------|---------|-------------|------|
| B1 | `deploy.yml` venter ikke på CI for samme commit | medium | Stemmer: egen workflow på push, uten `needs`. En merge-commit eller direkte push kan migrere og publisere før CI går rød. Retting: `ci.yml` får `workflow_call`, og deploy-jobben får `needs: ci`. Concurrency-gruppen i `ci.yml` må ta med `github.workflow`, så kallet ikke avbryter push-kjøringen | patch (med K2, V2) |
| B2 | Ingen tilbakerulling når røyktesten feiler | low | Stemmer, versjonen blir liggende. Automatisk `vercel rollback` er mer logikk, og ved første publisering finnes det ingenting å rulle tilbake til. Direkte retting: README sier at eieren bruker Instant Rollback i Vercel | patch (README, med K3) |
| B3 | Røyktesten blir grønn selv om `APP_ENV` mangler i Vercel | medium | Stemmer: appen kjører da som `local` mot Supabase med den kjente standardnøkkelen, og alle sjekkene passerer. `csrf`-cookien har `Secure` bare når `settings.produksjon` (`mellomvare.py:113`). Retting: røyktesten sjekker `Secure` på cookien | patch |
| B4 | Røyktesten har ingen tester | medium | Stemmer (grep etter `roykttest` i `tests/` gir ingen treff). Endrer noen malen eller en tekst, går deploy rød etter at versjonen er publisert. Retting: `kjor()` tar en valgfri klient, og en test kjører den mot `lag_app()` | patch (med V3, B5) |
| B5 | Røyktesten kopierer konstanter fra appen, og CSP sammenlignes eksakt | low | Stemmer. Direkte retting: importer `SIKKERHETSHEADERE` og `FEIL_INNLOGGING`/`FOR_MANGE_FORSOK` | patch (med B4) |
| B6 | Produksjonsadressen er hardkodet fire steder | low | Stemmer, men rettes én gang etter `vercel link`. En repo-variabel krever et ekstra manuelt steg | avvist |
| B7 | Hemmelighetene er på repo-nivå, og actions er ikke pinnet til SHA | low | `environment` krever admin-rettighet (PRD §9.2). Alle med push-rettighet er i gruppen. SHA-pinning avviker fra `ci.yml` | avvist |
| B8 | Manglende TSV gir rå `FileNotFoundError`, og `_register` er privat | low | Tracebacken viser stien tydelig i Vercel-loggen. Å gjøre funksjonen offentlig og pakke inn feilen er mer enn en direkte retting | avvist |
| B9 | README sier ikke at produksjon foreløpig bare viser innloggingen, eller hvem som sjekker Supabase under sensur | low | Stemmer. Direkte tekstretting | patch (README) |
| B10 | Keepalive: cookienavnet er ikke testet, GitHub slår av planlagte workflows etter 60 dager, og e-posten går til den som sist endret cron | low | Testdelen er V1. 60-dagersgrensen nevnes i README (direkte retting). E-posten går til Heidi | patch (med V1, README) |
| B11 | Navnet på storyen er forskjellig i `sprint-status.yaml`, branch og spec | low | `story_key` i specen kobler dem. Specen er committet (`e40ea39`) | avvist |
| B12 | `.vercelignore` tar med `migrations/` og `*.md` i roten uten begrunnelse | low | Ufarlig: litt større bunt, ingen feil | avvist |
| K1 | Manglende `MIGRATION_DATABASE_URL` gir tom streng, og migreringen kjører mot SQLite på runneren | medium | Stemmer: `env_ignore_empty=True` faller tilbake til `sqlite:///` (`config.py`). Steget blir grønt, og deploy fortsetter uten migrert Supabase. Retting: vakt i steget som krever en Postgres-URL | patch (med V4) |
| K2 | Deploy kjører samtidig med CI | medium | Samme som B1 | patch (med B1) |
| K3 | Ingen tilbakerulling etter at røyktesten feiler | low | Samme som B2 | patch (med B2) |
| K4 | Migreringen lykkes, men deploy feiler, så nytt skjema kjører med gammel kode | false | AD-13: etter første publisering legger migreringer bare til, så gammel kode virker med det nye skjemaet | avvist |
| K5 | Røyktesten treffer aliaset og ikke deploy-URL-en | maybe-false | `vercel deploy --prod` venter til aliaset er satt. Avgjøres ved å se loggen fra første publisering. Ville bare vært low | avvist |
| K6 | Sperren (5 forsøk) gjør at demokonto-sjekken hoppes over | low | Stemmer, men krever 5 publiseringer på 15 min, og seed nekter å kjøre i produksjon. Retting krever ny logikk | avvist |
| K7 | `httpx.InvalidURL` fanges ikke og gir traceback | low | Stemmer, men skriptet avslutter likevel med kode ≠ 0. Gjelder bare utviklere | avvist (med K8) |
| K8 | Påstanden om «én kort melding per avvik» holder ikke for uventede unntak | low | Samme som K7 | avvist |
| V1 | Ingen test sier at keepalive får noe annet enn 303 når databasen feiler | gap | Arkivert evidens: ingen test gjør sesjonsoppslaget med en database som feiler. En «myk» `except` i `finn_innlogget` ville skjult en pauset Supabase | patch |
| V2 | Deploy venter ikke på CI | gap | Samme som B1 | patch (med B1) |
| V3 | `roykttest.py` kjøres aldri før deploy | gap | Samme som B4 | patch (med B4) |
| V4 | Hemmeligheten for migreringen mangler, og SQLite migreres | medium | Samme som K1 | patch (med K1) |
| V5 | Sjekken av `/_test/tilstand` kan aldri feile, fordi ruta ikke finnes | low | Stemmer i dag. Sjekken er et akseptansekriterium i epics (AD-14) og får mening når T1-infrastrukturen kommer i 1.5 | avvist |
| V6 | Røyktesten feiler mot en lokal server med seed, men README sier den kan kjøres lokalt | low | Stemmer. Direkte retting: «mot en lokal server uten seed» | patch (README) |

## Design Notes

- **Røyktest i stedet for enhetstest av publiseringen:** røyktesten sjekker akseptansekriteriene mot den ekte versjonen ved hver publisering. Det er bevis det er verdt å vise sensor. Innloggingen som Kari bruker seed-passordet fra README. At den feiler, viser at det ikke finnes demokontoer. Forsøket havner i `innloggingsforsok` og ryddes etter 15 minutter.
- **Keepalive uten ny rute:** en offentlig `/helse` ville være en ny unntaksrute fra FR-3. En falsk sesjonscookie gir et ekte databaseoppslag og deretter 303.
- **Første publisering skjer ved merge.** `workflow_dispatch` virker først når fila ligger på `main`. Feiler det, rettes det i en ny PR. Etter cirka én dag gjelder kuttregelen i storyen.

## Verification

**Commands:**
- `uv run pytest` -- expected: grønn
- `uv run python scripts/roykttest.py https://<navn>.vercel.app` -- expected: «Røyktest OK» etter første publisering
- `gh run list --workflow deploy.yml --limit 1` -- expected: success
