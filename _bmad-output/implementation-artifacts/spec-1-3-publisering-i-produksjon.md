---
title: 'Story 1.3: Skjelett – appen publiseres i produksjon'
type: 'feature'
created: '2026-11-24'
status: 'in-progress'
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

## Design Notes

- **Røyktest i stedet for enhetstest av publiseringen:** røyktesten sjekker akseptansekriteriene mot den ekte versjonen ved hver publisering. Det er bevis det er verdt å vise sensor. Innloggingen som Kari bruker seed-passordet fra README. At den feiler, viser at det ikke finnes demokontoer. Forsøket havner i `innloggingsforsok` og ryddes etter 15 minutter.
- **Keepalive uten ny rute:** en offentlig `/helse` ville være en ny unntaksrute fra FR-3. En falsk sesjonscookie gir et ekte databaseoppslag og deretter 303.
- **Første publisering skjer ved merge.** `workflow_dispatch` virker først når fila ligger på `main`. Feiler det, rettes det i en ny PR. Etter cirka én dag gjelder kuttregelen i storyen.

## Verification

**Commands:**
- `uv run pytest` -- expected: grønn
- `uv run python scripts/roykttest.py https://<navn>.vercel.app` -- expected: «Røyktest OK» etter første publisering
- `gh run list --workflow deploy.yml --limit 1` -- expected: success
