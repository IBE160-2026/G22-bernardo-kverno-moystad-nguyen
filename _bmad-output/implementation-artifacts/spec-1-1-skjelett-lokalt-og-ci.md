---
title: 'Story 1.1: Skjelett – appen kjører lokalt og i CI'
type: 'feature'
created: '2026-11-24'
status: 'done'
route: 'dispatch'
baseline_commit: '4d2c1d1f7d920562a87aa11fd93eb1f6ae3d7460'
review_loop_iteration: 0
story_key: '1-1-skjelett-appen-kjører-lokalt-og-i-ci'
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-1-context.md'
  - '{project-root}/_bmad-output/planning-artifacts/architecture/architecture-G22-bernardo-kverno-moystad-nguyen-2026-11-08/ARCHITECTURE-SPINE.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Repoet har ingen kode. Alle senere stories trenger samme kjerne: app-fabrikk, mellomvare, rendring, database med migreringer, testoppsett og CI. Uten den bygger hver story sin egen variant.

**Approach:** Et greenfield FastAPI-skjelett etter arkitekturspinen (AD-1, AD-4, AD-5, AD-9–AD-11, AD-13, AD-14, AD-17). Det starter lokalt med `uv` mot SQLite uten `.env`, viser `/logg-inn` gjennom `core.render` og `base.html`, har én migrering (postnumre, `bruker`, `sesjon`) og kjører grønt i GitHub Actions mot SQLite og Postgres, med gitleaks.

## Boundaries & Constraints

**Always:** Kildetreet og navnene følger spinen § Kildetre og § Consistency Conventions: ASCII-identifikatorer og tabellnavn i entall. Mellomvaren er ren ASGI i rekkefølgen feilhåndtering → headere → CSRF/Origin → sesjon → ruter. All konfig går gjennom én `Settings`. Skjemaendringer gjøres bare med Alembic (`render_as_batch=True`). Autoescape er alltid på. Filer leses og skrives med `encoding="utf-8"`. Commits er små og oppgir krav-ID-er. Teksten i UI er ordrett fra EXPERIENCE.md.

**Never:** Ingen innlogging, utlogging, 303/401-håndheving eller FR-3-test. Det kommer i story 1.2, og `logg_inn` og `logg_ut` implementeres der. Ingen `deploy.yml`, `vercel.json` eller `keepalive.yml` (1.3). Ingen Playwright eller axe (1.5). Ingen eksempelbrukere i seed (1.2). Ingen meny for innloggede. Ingen `create_all`, npm, byggsteg, `|safe`, `Markup(` eller `innerHTML`. Ingen `pull_request_target`. Ingen testruter i `lag_app()`.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Ren start | ingen `.env`, `uv run python -m app.seed`, deretter oppstart | migrering kjørt, appen svarer på `/logg-inn` | N/A |
| Ugyldig miljø | `APP_ENV=foo`, eller `production` uten `SECRET_KEY` eller med standardverdien eller kortere enn 32 tegn | oppstarten stopper | tydelig melding i loggen |
| Gyldig POST | riktig `csrf_token` og cookie, samme `Origin`, urlencoded eller multipart | ruta får feltene selv om mellomvaren har lest kroppen | N/A |
| CSRF-feil | feil eller manglende nøkkel, eller fremmed `Origin`/`Sec-Fetch-Site: cross-site` | 403 med «Noe gikk galt. Prøv igjen om litt.» og lenke tilbake, ingen data endret | ingen teknisk tekst |
| Ukjent sti eller metode | GET `/finnes-ikke`, POST `/logg-inn` | 404 «Fant ikke siden» / 405 vennlig side, begge med vei videre | aldri JSON eller `detail` |
| Uventet feil | unntak i rute | 500 «Noe gikk galt. Prøv igjen om litt.» med sikkerhetsheaderne | logges uten personopplysninger |
| Postnummer | `"0571"`, `" 0571 "`, `"0000"`, `"0001"` (postboks) | `finnes` True/True/False/False, `poststed("0571") == "Oslo"`, `poststed("8622") == "Mo i Rana"` | N/A |

## Decisions

- **Beskyttelse av `main` (Heidi, 2026-11-24):** Ingen i gruppen har admin-rettighet på repoet i IBE160-2026, så teknisk beskyttelse kan ikke slås på. Den erstattes av en skrevet regel i README: all kode går via PR med grønn CI før merge, mens logger (`.logs/`) og `sprint-status.yaml` kan pushes direkte til `main`. Avviket føres i PRD §9.2 og i arkitekturens memlog. AR-7 i `epics.md` rettes samtidig, også motsigelsen om Vercels GitHub-app (story 1.3 gjelder: appen trengs ikke).
- **Størrelse (Heidi, 2026-11-24):** Spesifikasjonen beholdes hel, med CI som del av 1.1.
- **Postnumre (Heidi, 2026-11-24):** Bare postnumre for gateadresser godtas (Brings kategori G og B, 3 382 numre). Postboks (P) og service (S) utelates. Story-AC-en i `epics.md` («alle postnumrene») rettes, og presiseringen føres i PRD §9.2.

</frozen-after-approval>

## Code Map

- `README.md` -- har status, dokumentasjon og «Kom i gang» som plassholder. «Kom i gang» erstattes med kjøreinstruksjoner, og statustabellen oppdateres (står fortsatt på PRD v1.1 og frist i begynnelsen av desember).
- `.gitignore` -- har allerede `.env`, `.venv/`, `.vercel/` og byggmapper. Legg til `*.db` og `*.db-journal`. Behold resten.
- `_bmad-output/implementation-artifacts/epic-1-context.md` -- samlet kontekst for Epic 1, les først.
- Spinen § Consistency Conventions (Rendring, Feil, Validering, Tester) og § Stack. Versjonene er sjekket på PyPI: FastAPI 0.165.0, Starlette 1.10.0, SQLAlchemy 2.1.9, Alembic 1.20.1, Pydantic 2.14.4, pydantic-settings 2.16.3, uvicorn 0.54.0, pytest 9.2.0, psycopg 3.3.9, python-multipart 0.0.34.
- `DESIGN.md` frontmatter (ux-designs/…/DESIGN.md) -- tokens som blir CSS-variabler. `EXPERIENCE.md` § sidetitler (l. 462) og feiltekster (l. 167, 346) -- ordrette tekster.
- Brings register: `https://www.bring.no/postnummerregister-ansi.txt` (cp1252, tabulator, kolonnene postnummer, POSTSTED, kommunenr, KOMMUNE, kategori G/B/P/S, 5 112 rader per 2026-11-24).
- Ingen eksisterende kode å gjenbruke eller la være.

## Tasks & Acceptance

**Execution:**
- [x] `pyproject.toml`, `uv.lock`, `.python-version`, `.gitattributes` -- uv-prosjekt (Python 3.12) med versjonene over. uvicorn i hovedavhengighetene, pytest i `[dependency-groups] dev`. `*.tsv`/`*.json eol=lf` -- AR-2
- [x] `data/postnumre.tsv` -- Brings fil konvertert til UTF-8, alle rader og kolonner uendret -- AD-1, AD-10
- [x] `app/core/config.py` -- `Settings` med `APP_ENV` (standard `local`), `DATABASE_URL` (standard `sqlite:///./nabolagshelten.db`), `SECRET_KEY` (standard `"lokal-utvikling-ikke-hemmelig"`) og `OPENROUTER_*`. Stopper ved ukjent miljø, og i produksjon når nøkkelen er standardverdien eller kortere enn 32 tegn -- AD-14
- [x] `app/core/db.py` -- `Base`, `UtcDateTime`, `lag_motor(url)` (NullPool og `prepare_threshold=None` for Postgres; for SQLite `foreign_keys=ON` og pysqlite-oppskriften som sender `BEGIN IMMEDIATE`), sesjonsfabrikk på `app.state.sesjonsfabrikk`, og `hent_db()` som bruker den -- AD-2, AD-9, AD-13, AD-17
- [x] `app/core/klokke.py` -- `na()` gir aware UTC og kan overstyres i test. `domene.py` utsettes til 2.1 -- AD-9
- [x] `app/core/postnummer.py` -- `normaliser_postnummer`, `finnes`, `poststed`, `les_tsv()` (filtrerer G/B og formaterer poststed), og `__main__` som skriver `app/core/static/postnumre.json` (`ensure_ascii=False`, sortert) -- AD-1
- [x] `app/identity/models.py` -- `bruker(id, navn, epost unik, passord_hash, telefon, postnummer FK, fodselsdato Date, opprettet, slettet_tidspunkt)` med personfeltene NULL-bare; `sesjon(nokkel PK, bruker_id FK, opprettet, utloper)` -- AD-4, AD-8, NFR-9
- [x] `app/core/sesjon.py`, `app/identity/service.py` -- `Autentisering`-protokoll og `Innlogget`. `finn_innlogget` leser cookien `sesjon` og slår opp gjennom `app.state.sesjonsfabrikk` -- AD-4
- [x] `app/core/render.py`, `app/core/templates/core/{base,makroer,feil}.html`, `app/core/static/css/app.css` -- `render`/`render_fragment`, ett Jinja-miljø, sideramme, tokens, `color-scheme: light`, systemskrifter og fokusring -- AR-27, UX-DR1/2/4/6
- [x] `app/core/{feil,headere,csrf,mellomvare}.py` -- se Design Notes: feilhåndtering som ren ASGI med headere også på feilsider, én handler for alle `StarletteHTTPException` og `RequestValidationError`, CSRF med avspilling av kroppen -- AD-5, AR-26, NFR-10
- [x] `app/identity/routes.py`, `app/identity/templates/identity/logg_inn.html` -- offentlig GET `/logg-inn` med skjema og `csrf_token` (POST kommer i 1.2) -- UX-DR2
- [x] `app/__init__.py` (`lag_app()`), `main.py`, tomme slice-pakker `oppdrag`, `profil`, `ki` -- kobler `Autentisering` og nekter å starte uten. Monterer `/static`. `docs_url`, `redoc_url` og `openapi_url` er `None` -- AD-1
- [x] `alembic.ini`, `migrations/env.py`, `migrations/versions/0001_*.py` -- `env.py` henter URL fra `Settings` (eller en tilkobling i `config.attributes` fra testene). Én migrering: `postnummer(nummer PK, poststed)` lastet med `les_tsv()`, `bruker`, `sesjon` -- AD-13
- [x] `app/seed.py` -- kjører `alembic upgrade head` og nekter i produksjon -- NFR-1
- [x] `tests/conftest.py` -- setter `APP_ENV=test` før import. Midlertidig SQLite-fil, eller `TEST_DATABASE_URL` (Postgres i CI). Migrering én gang per kjøring, ytre transaksjon med `join_transaction_mode="create_savepoint"` som rulles tilbake, sesjonsfabrikken byttes på `app.state`, `sett_na`, og `engine.dispose()` før fila slettes -- AR-29
- [x] `tests/core/test_{arkitektur,mellomvare,config,postnummer,feil,render,migrering}.py` -- matrisen og AC-ene. Mellomvaretestene registrerer en ekko-/skriverute på appen i en fixture. 500-testen bruker `raise_server_exceptions=False` -- AR-29
- [x] `.github/workflows/ci.yml` -- på PR og push til `main`: pytest mot SQLite og mot tjenestecontaineren `postgres:17`, `alembic heads` med nøyaktig én linje, og gitleaks (se Design Notes) -- AR-7, NFR-3
- [x] `.env.example`, `.gitignore`, `README.md` -- variablene uten verdier, ignorer `*.db`. Forutsetninger med versjoner (Python 3.12, uv), eksakte kommandoer, testkommando, NLOD-kildelinja og PR-regelen for `main` -- NFR-1, NFR-3, AR-10
- [x] `prd.md` §9.2, arkitekturens `.memlog.md`, `epics.md` (AR-7 og story 1.1) -- før avvikene (beskyttelse av `main`, postnumre for gateadresser), og rett AR-7 om Vercels GitHub-app -- sporbarhet

**Acceptance Criteria:**
- Gitt `/logg-inn`, når siden hentes, så har den `lang="nb"`, `<title>` «Logg inn – Nabolagshelten», `header` og `main`, «Hopp til innholdet» som første fokuserbare element og en topplinje med bare logoen.
- Gitt stilarket, så har det tokenene fra DESIGN.md som CSS-variabler, `color-scheme: light`, systemskrifter og fokusring etter UX-DR4.
- Gitt et hvilket som helst svar, inkludert 403, 404, 405 og 500, så har det de fire sikkerhetsheaderne.
- Gitt `lag_app()` uten `Autentisering`, så kaster den en feil ved oppstart.
- Gitt en tom database, når `alembic upgrade head` kjøres, så har `postnummer` alle G/B-numrene fra TSV-fila, og `postnumre.json` stemmer med den filtrerte TSV-fila.
- Gitt `uv run pytest`, så passerer testene for arkitektur (importretning og forbudte mønstre), headere, CSRF, avspilling av kroppen og rekkefølgen på mellomvaren.
- Gitt en PR mot `main`, så er `ci.yml` grønn for begge databasene, `alembic heads` og gitleaks.
- Gitt README, så står regelen om at all kode går via PR med grønn CI, og avvikene står i PRD §9.2.

## Implementation Notes

- `lag_app()` uten argumenter kobler `IdentityAutentisering`; `lag_app(autentisering=None)` eller et objekt som ikke oppfyller protokollen gir `KonfigFeil`. `Autentisering` har bare `finn_innlogget` i 1.1 (ingen stubber for `logg_inn`/`logg_ut`).
- `url_for` i malene gir relative stier (egen global i `core/render.py`), så lenker virker bak Vercel sin proxy.
- Logoen er ikke lenke uten innlogging, og «Tilbake» faller tilbake til `/logg-inn` uten innlogging, fordi `/` ikke finnes før 1.2 (EXPERIENCE: ingen lenker til sider som ikke finnes).
- 403 brukes også når POST-kroppen ikke er et skjema (ingen nøkkel). For stor kropp gir 413. `Sec-Fetch-Site` godtas bare som `same-origin` eller `none`.
- `RequestValidationError` gir den vennlige siden med 400.
- Uventede feil logges med type, metode, sti og filnavn/linje, men uten unntaksmelding, kildelinjer eller spørrestreng.
- `.gitleaksignore` har ett falskt funn fra eksisterende historikk: SHA-256-hash i `_bmad/_config/files-manifest.csv` (commit 2d34266), regelen `generic-api-key`.
- Actions: `actions/checkout@v7`, `astral-sh/setup-uv@v10.3.3` (setup-uv har ikke lenger flytende major-tagger).
- Starlette 1.10 anbefaler `httpx2` for TestClient; arkitekturen har httpx 0.28, så advarselen er filtrert i `pyproject.toml`.
- Postgres-jobben er ikke kjørt lokalt (ingen Docker/Postgres på maskinen); den verifiseres først i CI.

## Spec Change Log

## Review Triage Log

Runde 1 (2026-11-24). VG = verification-gap, BH = blind-hunter, ECH = edge-case-hunter.

| # | Kilde | Funn | Verdikt | Rute | Begrunnelse |
|---|---|---|---|---|---|
| 1 | VG, BH | `Secure` på CSRF-cookien i produksjon er ikke testet | medium | patch | Bare fravær utenfor produksjon testes (`test_mellomvare.py:146`); koblingen `secure_cookie=settings.produksjon` kan forsvinne uoppdaget |
| 2 | VG | Grensen på 1 MB uten `Content-Length` er ikke testet | low | patch | Eksisterende test treffer bare header-sjekken; byte-telleren i `_les_kropp` er udekket |
| 3 | VG | `BEGIN IMMEDIATE` i SQLite er ikke testet | medium | patch | Kan byttes til `BEGIN` uten at noen test feiler; AD-2 bygger på den |
| 4 | VG | `//`-vernet i `tilbake_url` er ikke testet | low | patch | Fjerning gir åpen omdirigering via «Tilbake» uten testfeil |
| 5 | VG | `NullPool` og `prepare_threshold=None` for Postgres er ikke testet | medium | patch | Vanlig Postgres i CI trenger dem ikke, så de kan forsvinne før Supabase (1.3); testen er to linjer uten database |
| 6 | VG | Stien «svaret har startet» i `FeilMellomvare` er ikke testet | low | reject | Ingen rute strømmer; nås ikke i dag |
| 7 | VG | Innlogget bruker får «Tilbake» til `/`, som ikke finnes før 1.2 | low | reject | Ingen kan logge inn i 1.1; `/` kommer i 1.2 |
| 8 | BH | README sier PRD v1.2, PRD er nå v1.2.1 | low | patch | Direkte retting |
| 9 | BH | Arkitekturspinen (l. 68, 334, 349) og AR-6 mangler avvikene | medium | patch | Planleggingsdokumenter skal holdes oppdatert (CLAUDE.md, sensorveiledning) |
| 10 | BH | `tilbake_url` kan peke til siden selv | low | patch | `reconcile-ux.md:256` sier «ikke siden selv»; 405 på `/logg-inn` med Referer `/logg-inn` lenker til seg selv |
| 11 | BH, ECH | Migrering 0001 bruker `les_tsv()` fra appen og er ikke frosset | medium | patch | Endret filter eller formatering gir ulike data i nye og gamle databaser; regelen skrives i migreringen og `postnummer.py` |
| 12 | BH | Ingen test av at modeller og migreringer stemmer | medium | patch | Med én migrering per story vil avvik gå uoppdaget; `compare_metadata` gir en kort test |
| 13 | BH | `downgrade()` testes ikke | low | reject | Migreringer legger bare til (AD-13); nedgradering brukes ikke |
| 14 | BH | Sesjonsoppslag på hver forespørsel, også `/static` | medium | patch | Med cookie gir hver CSS-fil et databasekall og ny tilkobling med `NullPool` |
| 15 | BH, ECH | Ingen reserve hvis 500-siden selv feiler; da mangler også headerne | medium | patch | Malfeil gir Starlettes rå 500 uten sikkerhetsheadere, mot matrisen |
| 16 | BH, ECH | Origin-sjekken tar ikke hensyn til proxy, skjema eller standardport | maybe-false | defer | Avhenger av hvilken `Host` Vercel sender; 1.3 prøver et ekte skjema i produksjon |
| 17 | BH | 405 og 413 får den generelle feilteksten | low | reject | Spesifikasjonen valgte teksten med vilje (matrisen) |
| 18 | BH | Skjemaet på `/logg-inn` gir alltid 405 i 1.1 | low | patch | README sier at innsendingen kommer i 1.2 |
| 19 | BH | Fokusringen på `main` vises ved hvert museklikk | low | patch | Klikk i `main` med `tabindex="-1"` gir fokus og ring rundt hele innholdet; direkte retting av selektoren |
| 20 | BH | Midlertidige testmapper blir liggende når databasen ikke brukes | low | patch | Opprettes ved import, slettes bare av `motor`-fixturen |
| 21 | BH | Ingen test holder `.env.example` i takt med `Settings` | low | reject | Lite sannsynlig, krever ny test |
| 22 | BH | Produksjon godtar SQLite-URL-en | medium | patch | Vercel feiler først ved første skriving; AD-14 sier Supabase i produksjon |
| 23 | BH, ECH | `.gitleaksignore` er låst til ett commit-fingeravtrykk | medium | patch | Neste endring av manifestet gir rød CI; allowlist på sti tåler det |
| 24 | BH | CI låser ikke uv-versjonen | low | patch | Én linje |
| 25 | BH | Sesjonsnøkkelen lagres i klartekst | medium | patch | En databaselekkasje gir virkende sesjoner; SHA-256 hex passer i `String(64)` og bestemmes før 1.2 skriver sesjoner |
| 26 | ECH | Frakobling midt i kroppen behandles som komplett skjema | low | patch | `_les_kropp` bryter ved `http.disconnect` og ruta kjøres med avkortede felt |
| 27 | ECH | To faner uten cookie samtidig får ulike nøkler | low | reject | Bare første besøk; krever mer logikk |
| 28 | ECH | `BEGIN IMMEDIATE` også for lesing serialiserer | low | reject | Arkitekturvalg (AD-2), bare lokalt |
| 29 | ECH | `finnes()` leser TSV-fila, mens fremmednøkkelen sjekker tabellen | maybe-false | defer | Like så lenge TSV og migrering er like; om `data/` følger med til Vercel avgjøres i 1.3 |
| 30 | ECH | `postgresql+psycopg2://` eller store bokstaver i URL | low | reject | Lite sannsynlig |
| 31 | ECH | `SECRET_KEY` med 32 mellomrom godtas | low | reject | Lite sannsynlig |
| 32 | ECH | Objekt med `finn_innlogget` som ikke er kallbar | low | reject | Lite sannsynlig |
| 33 | ECH | Arkitekturtesten feiler ved `open(..., mode="rb")` | low | reject | Ingen kode gjør det |
| 34 | ECH | `requires-python >=3.11` mot 3.12 | false | reject | Spinen § Stack sier `requires-python >=3.11` med `.python-version` 3.12 |

## Design Notes

- **Mellomvare:** Feilhåndteringen er egen ren ASGI ytterst. Den fanger unntak og rendrer feilsiden uten databasekall. Headerne settes med samme funksjon fra `headere.py`, så også feilsider får dem (Starlettes `ServerErrorMiddleware` ligger utenfor brukermellomvaren). CSRF-mellomvaren tolker `application/x-www-form-urlencoded` og `multipart/form-data` og avviser kropper over 1 MB. Den legger feltene i `request.state.skjema` og spiller av kroppen.
- **Navn:** feltet `csrf_token` (AD-7: ingen andre feltnavn begynner med `_`), cookien `csrf` (signert med `itsdangerous`, `SameSite=Lax`, `HttpOnly`, `Secure` i produksjon) og sesjonscookien `sesjon`.
- **Postnumre:** TSV-fila er lik kilden, så den kan spores. `les_tsv()` filtrerer til G/B og formaterer poststed fra Brings store bokstaver: stor forbokstav i hvert ord og i hvert bindestrek-ledd, og småordene `i`, `på`, `og` og `ved` med små bokstaver når de ikke står først. Den brukes både av migreringen og av JSON-generatoren.
- **Rute-merking:** En rute merkes offentlig på selve ruta (en hjelper i `core`). Sesjonsmellomvaren slår opp ruta med `route.matches(scope)` i 1.2. I 1.1 setter den bare `request.state.innlogget`.
- **gitleaks:** `gitleaks/gitleaks-action` krever lisens for organisasjoner. CI kjører `docker run --rm -v "$PWD:/repo" ghcr.io/gitleaks/gitleaks:v8.30.1 git /repo` (siste release, 2026-03-21) med `fetch-depth: 0` og `git config --global --add safe.directory`. Skanningen kjøres lokalt før PR, med Docker eller med gitleaks-binæren for Windows i scratchpad (Docker Desktop kjører ikke på maskinen nå).

## Verification

**Commands:**
- `uv sync && uv run python -m app.seed` -- expected: migrering uten feil, SQLite-fil opprettet
- `uv run uvicorn main:app` + `curl -i http://127.0.0.1:8000/logg-inn` -- expected: 200, headere og riktig `<title>`
- `uv run pytest` -- expected: alle grønne
- `uv run alembic heads` -- expected: nøyaktig én linje
- `gitleaks git .` (v8.30.1, binær eller Docker-image) -- expected: ingen funn
- `gh pr checks` -- expected: CI grønn
