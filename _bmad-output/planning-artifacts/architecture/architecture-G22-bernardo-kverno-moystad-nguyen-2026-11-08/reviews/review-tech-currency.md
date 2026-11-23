---
review: tech-currency
target: ../ARCHITECTURE-SPINE.md
companion: ../.memlog.md
date: 2026-11-23
lens: Er hver bindende beslutning i spinen undersøkt på nettet eller sjekket mot virkeligheten, i stedet for å være hentet fra treningsdata? Gjelder versjoner, at teknologiene finnes og passer, og hvordan plattformene faktisk oppfører seg.
---

# Review: teknologisk aktualitet – Arkitekturspine Nabolagshelten v1

## Konklusjon

**Stort sett godt undersøkt, men med to plattformfunn som må inn før spinen godkjennes.** Alle versjonene i Stack-tabellen stemmer med PyPI i dag, og memloggen viser at det faktisk ble gjort oppslag (PyPI JSON og websøk 2026-11-23). Vercel-entrypoint, `maxDuration`, StaticFiles, Supabase-pooleren, psycopg og bcrypt er bekreftet. Det som mangler er hvordan plattformene oppfører seg **over tid og i rekkefølge**:

1. **Supabase Free pauser prosjekter etter 1 uke uten aktivitet.** Dette står ikke i spinen. Hvis sensor åpner produksjonen etter en stille uke, svarer databasen ikke. (Høy)
2. **Rekkefølgen «migrering før publisering» i figuren håndheves ikke.** Vercels Git-integrasjon publiserer `main` uavhengig av GitHub Actions. (Høy)
3. `static/postnumre.json` «lages ved seeding», men seeding kjører aldri på Vercel. (Middels)
4. GitHub Actions når ikke Supabase sin direkte tilkobling (bare IPv6). Migreringer trenger session pooler-URL (port 5432). (Middels)
5. `httpx` har ingen samlet frist for hele kallet. «Total frist på 10 s» (AD-12) krever egen kode. (Middels)

Skala for alvorlighet: **Kritisk** = bygget virker ikke. **Høy** = sannsynlig feil i drift eller ved sensur. **Middels** = vil gi feil hvis det ikke blir håndtert i en story. **Lav** = presisering eller fallgruve.

---

## 1. Versjonene i Stack-tabellen (PyPI JSON, hentet 2026-11-23)

Kilde: `https://pypi.org/pypi/<pakke>/json`

| Pakke | Spine | Siste på PyPI (dato) | requires-python | Status |
|---|---|---|---|---|
| fastapi | 0.165.x | 0.165.0 (2026-11-18) | >=3.11 | **Bekreftet** |
| uvicorn | 0.54.x | 0.54.0 (2026-09-25) | >=3.10 | **Bekreftet** |
| jinja2 | 3.1.x | 3.1.6 (2025-03-05) | >=3.7 | **Bekreftet** |
| python-multipart | 0.0.34 | 0.0.34 (2026-11-16) | >=3.11 | **Bekreftet** |
| sqlalchemy | 2.1.x | 2.1.9 (2026-11-16) | >=3.11 | **Bekreftet** |
| alembic | 1.20.x | 1.20.1 (2026-10-22) | >=3.10 | **Bekreftet** |
| psycopg | 3.3.x | 3.3.9 (2026-11-12), også `psycopg-binary` 3.3.9 | >=3.10 | **Bekreftet** (se funn 2.6 om `[binary]`) |
| pydantic | 2.14.x | 2.14.4 (2026-11-19) | >=3.10 | **Bekreftet** |
| pydantic-settings | 2.16.x | 2.16.3 (2026-11-13) | >=3.11 | **Bekreftet** |
| bcrypt | 5.0.x | 5.0.0 (2025-09-25), ingen nyere | >=3.8 | **Bekreftet** |
| itsdangerous | 2.2.x | 2.2.0 (2024-04-16) | >=3.8 | **Bekreftet** |
| httpx | 0.28.x | 0.28.1 (2024-12-06). `1.0.dev6` finnes som forhåndsutgave (2026-08-31) | >=3.8 | **Bekreftet**. Lav: hold `<1.0`, siden 1.0 kan endre API-et. uv velger ikke forhåndsutgaver uten videre. |
| tzdata | 2026.6 | 2026.6 (2026-10-28) | – | **Bekreftet** |
| pytest | 9.2.x | 9.2.0 (2026-10-27) | >=3.10 | **Bekreftet** |
| playwright | 1.65.x | 1.65.2 (2026-11-14) | >=3.10 | **Bekreftet** |
| pytest-playwright | 0.10.x | 0.10.0 (2026-10-08) | >=3.10 | **Bekreftet** |
| axe-playwright-python | 0.1.x | 0.1.9 (2026-11-23) | >=3.8 | **Bekreftet**, se 2.11 |
| starlette (kommer med FastAPI) | – | 1.10.0 (2026-10-24). FastAPI krever `starlette>=1.6.0` | – | Ikke nevnt i spinen. Se 2.13. |

`requires-python >=3.11` er riktig, fordi fastapi, sqlalchemy 2.1, python-multipart og pydantic-settings alle krever 3.11 eller nyere. SQLAlchemy 2.1 sluttet med 3.10 i august 2026 (migration_21).

**Lav (gjelder alle):** FastAPI gir ut en ny minorversjon med noen dagers mellomrom (0.162.7 → 0.165.0 på fem dager). For en 0.x-pakke kan en minorversjon være en brytende endring. `uv.lock` beskytter mot dette, men bruk `fastapi>=0.165,<0.166` (eller `~=0.165.0`) i `pyproject.toml`, og oppgrader bevisst.

---

## 2. Plattformer og teknologier, punkt for punkt

### 2.1 Vercel: `main.py` i roten med `app`
- **Status: Bekreftet.**
- Kilde: https://vercel.com/docs/frameworks/backend/fastapi og https://vercel.com/docs/functions/runtimes/python
- Vercel ser etter en `FastAPI`-instans med navnet `app` i `app.py`, `index.py`, `server.py`, `main.py`, `wsgi.py` eller `asgi.py`, og i de samme filnavnene under `src/` eller `app/`. Hele appen blir én Vercel Function. Avhengigheter leses fra `pyproject.toml` med eller uten `uv.lock`. Python 3.12 er standard, og 3.13 og 3.14 kan velges.
- **Lav:** Repoet har både `main.py` i roten og pakken `app/`, og Vercel søker også i `app/`. Det virker i dag fordi `app/` ikke har noen `main.py` eller `app.py` osv. Gjør valget eksplisitt med `[tool.vercel] entrypoint = "main:app"` i `pyproject.toml`, slik at en fil som legges til senere (for eksempel `app/server.py`) ikke flytter entrypointet.

### 2.2 Vercel: `maxDuration` 30 s og grensene i Hobby
- **Status: Bekreftet.**
- Kilde: https://vercel.com/docs/functions/configuring-functions/duration
- Med Fluid compute (på som standard) har Hobby **300 s som standard og som maksimum**, så 30 s er lov. For Python-rammeverk settes det i `vercel.json` med entrypoint-fila som nøkkel:
  ```json
  { "functions": { "main.py": { "maxDuration": 30 } } }
  ```
- **Lav:** Skriv nøkkelen (`"main.py"`) inn i Structural Seed. Legg merke til at 30 s *senker* grensen fra standardverdien 300 s. Det er greit og passer med fristen på 10 s, men det bør stå at det er med vilje.

### 2.3 Vercel: StaticFiles-mount
- **Status: Bekreftet** (memloggen hadde det, og dokumentasjonen bekrefter det).
- Kilde: https://vercel.com/docs/frameworks/backend/fastapi (avsnittet «Middleware»)
- `app.mount(... StaticFiles ...)` flyttes til CDN ved bygging, men **ikke når appen har mellomvare på toppnivå**. Nabolagshelten har det (AD-4, AD-5), så `/static` serveres fra funksjonen. Det betyr at sikkerhetsheaderne fra AD-5 også gjelder statiske filer, og det er bra.
- **Lav:** Sett **ikke** `[tool.vercel.fastapi.static] cdn = true`. Da hopper statiske filer over mellomvaren, og headerne fra AD-5 forsvinner for dem. Ikke bruk `public/` sammen med `app.mount()`.

### 2.4 Vercel: Preview-publiseringer og miljøvariabler per miljø
- **Status: Bekreftet**, med ett nytt funn.
- Kilde: https://vercel.com/docs/environment-variables og https://vercel.com/docs/deployment-protection
- Variabler kan gjelde Production, Preview (alle grener eller én bestemt gren) eller Development. Endringer gjelder bare **nye** publiseringer, så etter en endring må det publiseres på nytt.
- **Lav (nytt):** Standard Protection, som er tilgjengelig på alle planer og ofte standard for nye prosjekter, krever Vercel-innlogging for Preview-URL-er. Hvis sensor eller medstudenter skal kunne åpne en Preview, må beskyttelsen slås av for Preview, eller så må README si at bare produksjons-URL-en er offentlig. Passordbeskyttelse finnes ikke på Hobby.

### 2.5 Rekkefølgen migrering → publisering (Structural Seed-figuren)
- **Status: Feil, slik det står nå.** **Alvorlighet: Høy.**
- Kilde: https://vercel.com/docs/deployment-checks og https://vercel.com/kb/guide/how-can-i-use-github-actions-with-vercel
- Figuren viser `main → GitHub Actions: alembic upgrade head → Vercel Production`. Med Vercels Git-integrasjon starter publiseringen ved push til `main`, **samtidig med** GitHub Actions og uten å vente på den. Ny kode kan da kjøre mot det gamle skjemaet i minutter, eller for alltid hvis migreringsjobben feiler.
- I tillegg kjøres ingen migrering mot **Preview-databasen** (Supabase-prosjekt 2). En PR med en ny migrering gir derfor en Preview som feiler.
- **Fiks (velg én og skriv den i spinen):**
  - (a) **Deployment Checks:** krev GitHub-sjekken «migrate» før publiseringen blir produksjon. Det krever at automatisk aliasing for produksjon er på. *At dette finnes i Hobby er ikke bekreftet, så sjekk det i prosjektinnstillingene.*
  - (b) Slå av Git-publisering for `main` (`git.deploymentEnabled`) og publiser med `vercel deploy --prod` fra Actions etter migreringsjobben. Det krever at `VERCEL_TOKEN` ligger som GitHub-secret.
  - (c) Den enkleste regelen: migreringer skal alltid være **bakoverkompatible** (expand/contract), slik at gammel og ny kode tåler begge skjemaene. Godta et kort vindu.
  - For Preview: en Actions-jobb på `pull_request` som kjører `alembic upgrade head` mot Supabase-prosjekt 2, eller skriv uttrykkelig at Preview kan være ute av takt med skjemaet.

### 2.6 Supabase Free: to prosjekter og pausing etter inaktivitet
- **Status: To prosjekter er bekreftet. Pausing er IKKE tatt hensyn til.** **Alvorlighet: Høy.**
- Kilde: https://supabase.com/pricing
- «Limit of 2 active projects», og pausede prosjekter teller ikke. 500 MB per prosjekt. **«Free projects are paused after 1 week of inactivity.»**
- Produksjonen kan altså være pauset akkurat når sensor åpner den, og da får brukeren en databasefeil (NFR-10 viser en vennlig side, men appen virker ikke). Preview-prosjektet vil pause enda oftere.
- **Fiks:**
  - Legg inn en planlagt GitHub Actions-jobb (`schedule`, for eksempel hver 3. dag) som kjører en enkel `SELECT 1` mot begge prosjektene via session pooleren. Alternativt kan den kalle en lett side i produksjonen som gjør et databasekall.
  - Skriv i spinen (Deferred eller Structural Seed) og i README hvordan man gjenoppretter et pauset prosjekt i dashbordet.
  - Hva Supabase regner som «aktivitet», er ikke bekreftet. Test at keepalive-jobben faktisk hindrer pausing før fristen.
  - Merk: GitHub slår av planlagte workflows i offentlige repoer etter 60 dager uten aktivitet i repoet. Det er ikke et problem før desember 2026.

### 2.7 Supabase transaction pooler (6543) + `NullPool` + `prepare_threshold=None`
- **Status: Bekreftet.**
- Kilder: https://supabase.com/docs/guides/database/connecting-to-postgres og https://www.psycopg.org/psycopg3/docs/advanced/prepare.html
- Den delte Supavisor-pooleren i transaction mode (port 6543) går over IPv4 og anbefales for serverless. Supabase skriver: «The shared pooler doesn't support prepared statements in transaction mode.» psycopg slår av prepared statements med `prepare_threshold=None`, som kan gis som parameter til `connect()` (fra 3.1). I SQLAlchemy gjøres det med `connect_args={"prepare_threshold": None}`.
- `NullPool` er ikke nevnt hos Supabase, men følger av at Vercel-funksjoner er kortlevde og at Supavisor allerede er en pool. Det er riktig praksis.
- **Lav, en presisering til memloggen:** «PgBouncer avviklet» gjelder den *delte* PgBouncer-tjenesten. Supabase har fortsatt en *dedikert* PgBouncer på Pro og høyere, men den er ikke aktuell her.

### 2.8 Migreringer fra GitHub Actions mot Supabase (IPv4)
- **Status: Ikke vurdert i spinen.** **Alvorlighet: Middels.**
- Kilde: https://supabase.com/docs/guides/troubleshooting/supabase--your-network-ipv4-and-ipv6-compatibility-cHe3BP og connecting-to-postgres (over)
- Den direkte tilkoblingen (`db.<ref>.supabase.co:5432`) går bare over IPv6 på Free, og Supabase nevner selv GitHub Actions blant tjenestene som bare har IPv4. Supabase anbefaler den direkte tilkoblingen til migreringer, og alternativet over IPv4 er **session pooler (port 5432)**. Transaction mode (6543) kan ødelegge DDL og migreringer som trenger tilstand i sesjonen.
- **Fiks:** Legg til en egen hemmelighet, for eksempel `MIGRATION_DATABASE_URL` (session pooler, port 5432), som brukes av `alembic` i Actions. `DATABASE_URL` (6543) brukes bare av appen. Skriv det inn i AD-13 og i konfig-konvensjonen. Den skal ikke stå i `.env.example` med en ekte verdi.

### 2.9 psycopg 3 på Vercel: `psycopg[binary]`
- **Status: Ikke bekreftet.** **Alvorlighet: Middels.**
- Kilde: https://www.psycopg.org/psycopg3/docs/basic/install.html (oppslaget på PyPI viser at `psycopg-binary` 3.3.9 finnes)
- Pakken `psycopg` alene er ren Python og trenger `libpq` på systemet. Det er ikke dokumentert at Vercels Python-runtime har `libpq`. Spinen skriver bare «psycopg 3.3.x».
- **Fiks:** Bruk `psycopg[binary]>=3.3,<3.4` i avhengighetene. Det er også det enkleste for nybegynnere på Windows (NFR-1).

### 2.10 SQLAlchemy 2.1 + psycopg 3-dialekten
- **Status: Bekreftet.**
- Kilde: https://docs.sqlalchemy.org/en/21/changelog/migration_21.html
- 2.1 har overskriften «Default PostgreSQL driver changed to psycopg (psycopg 3)», så `postgresql://` fra Supabase bruker psycopg 3 uten `+psycopg`. Det krever Python 3.11 eller nyere, og greenlet installeres ikke lenger som standard (påvirker bare async).
- **Lav:** Skriv likevel `postgresql+psycopg://` eksplisitt i `Settings`, eller gjør URL-en om der, så koden ikke avhenger av en standardverdi. I 2.1 kjører autoflush nå alltid, også for `text()`-SQL. Det har betydning for den betingede `UPDATE` i AD-2 og bør være med i testene.

### 2.11 bcrypt 5.0 og passord over 72 byte
- **Status: Bekreftet.**
- Kilde: https://github.com/pyca/bcrypt/blob/main/CHANGELOG.rst
- «Passing `hashpw` a password longer than 72 bytes now raises a `ValueError`.» Det har ikke kommet noen nyere versjon. Løsningen i AD-6, base64(SHA-256), gir alltid 44 ASCII-byte, uten NUL-byte. Det er riktig.

### 2.12 axe-playwright-python: vedlikehold
- **Status: Bekreftet at den vedlikeholdes.**
- Kilde: https://github.com/pamelafox/axe-playwright-python og PyPI
- Repoet er ikke arkivert. Det kom utgivelser i 2025 og i juli og november 2026 (0.1.9 den 2026-11-23). Det er et enmannsprosjekt (Pamela Fox) med bare sync-API: `Axe().run(page)`. Det passer med pytest-playwright (sync).
- **Lav:** README-en på GitHub sier Python 3.10+, mens PyPI sier >=3.8. Det spiller ingen rolle med 3.12. Hvis prosjektet stopper opp, er reserven å laste `axe.min.js` fra npm-pakken `axe-core` inn i siden med `page.add_script_tag` og kjøre `axe.run()`. Det gir ingen ny avhengighet.

### 2.13 FastAPI: `RequestValidationError` og skjemamodeller (konvensjonen Validering)
- **Status: Bekreftet**, med to fallgruver.
- Kilder: https://fastapi.tiangolo.com/tutorial/request-form-models/ og https://fastapi.tiangolo.com/tutorial/handling-errors/
- Skjemamodeller (`Annotated[Modell, Form()]`) finnes fra 0.113 og krever `python-multipart`. En egen handler registreres med `@app.exception_handler(RequestValidationError)` (import fra `fastapi.exceptions`). Ugyldige data i forespørselen gir `RequestValidationError`.
- **Lav:** Dokumentasjonen sier at «Using `| None` without a default still makes the parameter required». Felt av typen `str | None` må altså ha `= None`, ellers gir et felt som mangler (for eksempel en checkbox uten hake) en valideringsfeil i stedet for at reglene i service-laget får sjekke det. Skriv «`str | None = None`» i konvensjonen.
- **Lav:** Ikke sett `extra="forbid"` på skjemamodellene. AD-7 sender skjemaet på nytt med ekstra innloggingsfelt.
- **Lav (Starlette 1.x):** I 1.0 ble `TemplateResponse(name, context)` fjernet. Det må være `TemplateResponse(request, name, context)`. Det samme gjelder `on_startup` og `on_shutdown` (bruk `lifespan`) og `@app.middleware()` på Starlette-nivå. Mange veiledninger og mye treningsdata bruker de gamle formene. `core.render` må bruke den nye signaturen.
- **Ikke bekreftet (Middels):** Både CSRF-mellomvaren (AD-5) og innloggingen på nytt (AD-7) må lese **skjemakroppen** i mellomvaren, før ruta leser den igjen. Starlette-dokumentasjonen sier bare at ren ASGI-mellomvare kan pakke inn `receive` for å lese kroppen. Den sier ikke at kroppen er tilgjengelig videre etter `request.form()` i `BaseHTTPMiddleware`. **Fiks:** Lag en tidlig spike-test i første story: POST med skjema → mellomvaren leser `csrf` → ruta får alle feltene. Hvis det feiler, skriv mellomvaren som ren ASGI som lagrer kroppen og spiller den av på nytt, eller legg CSRF-sjekken i en avhengighet (`Depends`) i stedet for i en mellomvare.

### 2.14 Python 3.12 `zoneinfo` og `tzdata` på Windows (AD-9)
- **Status: Bekreftet**, med én presisering.
- Kilde: https://docs.python.org/3.12/library/zoneinfo.html
- Windows har ingen IANA-database, så `tzdata` må være en avhengighet. Ellers gir det `ZoneInfoNotFoundError`. `fold=0` betyr forskyvningen *før* overgangen. Det stemmer med AD-9 («det første»).
- **Lav:** `zoneinfo` gir **ingen feil** for klokkeslett som ikke finnes, som 02:30 natt til sommertid. Den gir bare et datetime-objekt. Avvisningen i AD-9 må derfor sjekke rundturen: lokal → UTC → lokal, og avvise hvis veggklokketiden har endret seg. Skriv det i AD-9, så ingen tror at `ZoneInfo` sier fra av seg selv.

### 2.15 Brings postnummerregister: URL og lisens
- **Status: Bedre bekreftet enn spinen sier.** Lisensen står ikke på bring.no selv. **Alvorlighet: Lav.**
- Kilder:
  - https://data.norge.no/en/datasets/f7508db5-2167-3356-ab5e-aacffce2a9b6/postnummer-i-norge (Felles datakatalog, utgiver «Posten bring as», **lisens NLOD 2.0**, distribusjon «TABseparert ANSI»)
  - https://bring.no/en/services/address-verification-services/postcodes (filene `Postal-codes-Norway-ansi.txt` og xlsx, «valid from 2026/10/01», ingen lisenstekst på siden)
  - Brings manual (PDF) oppgir den stabile URL-en `https://www.bring.no/postnummerregister-ansi.txt`
- Spinen kaller NLOD 2.0 en «sekundærkilde». Oppføringen i data.norge.no er Brings egen publisering i den offisielle norske datakatalogen, så den er en sterkere kilde enn datahub.io, som memloggen brukte.
- **Fiks:** Bytt kilden i Deferred til data.norge.no-lenken og skriv «NLOD 2.0 (Felles datakatalog, utgiver Posten Bring AS)». Kreditering etter NLOD («Inneholder data under norsk lisens for offentlige data (NLOD) gjort tilgjengelig av Posten Bring AS») skal stå i README. Fila er **ANSI**, altså Windows-1252 og ikke strengt Latin-1. Konverter med `cp1252`. For de norske bokstavene gir det samme resultat, men det er det riktige navnet på kodingen. Vurder å skrive gyldighetsdatoen (2026-10-01) inn i fila eller i README.

### 2.16 OpenRouter via `httpx`
- **Status: Bekreftet at den finnes.** Fristen er **ikke** dekket av `httpx`. **Alvorlighet: Middels.**
- Kilder: https://openrouter.ai/docs/api-reference/chat-completion, https://openrouter.ai/docs/quickstart og https://www.python-httpx.org/advanced/timeouts/
- `POST https://openrouter.ai/api/v1/chat/completions` er OpenAI-kompatibel, med `Authorization: Bearer <nøkkel>` og `response_format` (json_schema) for strukturert svar. Quickstart viser nå `POST /api/v1/responses` som hovedvei, men chat/completions finnes fortsatt. Tittelheaderen heter nå `X-OpenRouter-Title`, ikke `X-Title`.
- **Middels:** `httpx`-timeouts gjelder **hver operasjon** (connect, read per bit, write, pool). Det finnes ingen samlet frist. `httpx.Client(timeout=10)` kan derfor bruke langt mer enn 10 s hvis svaret kommer sakte, bit for bit. AD-12 sier «total frist på 10 s for hele kallet».
- **Fiks:** Skriv i AD-12 *hvordan* fristen håndheves. For eksempel: kjør kallet i en `ThreadPoolExecutor` og bruk `future.result(timeout=10)`, slik at svaret forkastes hvis det kommer for sent (det passer med «Svar etter fristen forkastes»). Eller strøm svaret og sjekk `time.monotonic()` mot en frist mellom bitene. Velg også endepunkt (`/chat/completions`) eksplisitt i `openrouter.py`, og ta med `X-OpenRouter-Title` hvis dere vil ha attribusjon.

### 2.17 GitHub Actions: Postgres som service container
- **Status: Bekreftet.**
- Kilde: https://docs.github.com/en/actions/tutorials/use-containerized-services/create-postgresql-service-containers
- `services: postgres: image: postgres`, `POSTGRES_PASSWORD`, helsesjekk med `pg_isready`, `ports: 5432:5432`, tilkobling til `localhost:5432` fra en jobb på `ubuntu-latest`. Det krever en Linux-runner.
- **Lav:** Lås imaget til en hovedversjon (for eksempel `postgres:17`) i stedet for `latest`, slik at CI ikke endrer seg av seg selv. Velg versjonen som Supabase-prosjektene kjører (vises i dashbordet), slik at CI tester mot samme hovedversjon.

### 2.18 `static/postnumre.json` «lages ved seeding»
- **Status: Feil i møte med plattformen.** **Alvorlighet: Middels.**
- Kilder: AD-1 og Structural Seed («seed … bare når `APP_ENV` er `local` eller `test`»), samt https://vercel.com/docs/frameworks/backend/fastapi (Build command)
- På Vercel kjører seeding aldri, og filsystemet i funksjonen er ikke varig. Fila finnes derfor ikke i produksjon eller Preview, og poststed-oppslaget i `skjema.js` blir borte der. Det svekker også progressiv forbedring. Det samme gjelder at `postnummer`-tabellen i Supabase må fylles et sted. Seeding er sperret utenfor local/test.
- **Fiks:**
  - (a) Generer `postnumre.json` fra `data/postnumre.tsv` i et byggsteg: `[tool.vercel.scripts] build = "python -m app.lag_postnumre_json"`. Alternativt kan fila committes som en generert fil sammen med TSV-en.
  - (b) Legg innlasting av postnumre til i migreringen (en Alembic-datamigrering) eller i en egen kommando som Actions kjører, atskilt fra eksempeldataene.

---

## 3. Ting som ikke ble sjekket (utenfor tidsrammen)

- Om Deployment Checks (fiks 2.5a) finnes i Hobby.
- Hva Supabase regner som «aktivitet» som hindrer pausing.
- Om Vercel installerer `[dependency-groups] dev` (Playwright, pytest) i funksjonspakken. Det har lite å si så lenge pakken er under 500 MB, men legg testverktøy i dev-gruppa og bruk `excludeFiles` for `tests/**` i `vercel.json`.
- Hvilken rekkefølge Vercel bruker hvis `.python-version` (3.12) og `requires-python` (>=3.11) peker forskjellig. Det er trolig ufarlig.

## 4. Samlet tiltaksliste

| # | Alvorlighet | Hvor i spinen | Tiltak |
|---|---|---|---|
| 2.6 | Høy | Stack / Structural Seed / Deferred | Supabase pauser etter 7 dager: planlagt keepalive-workflow og README-instruks for å gjenopprette |
| 2.5 | Høy | Structural Seed (figur) | Håndhev migrering før publisering (Deployment Checks, CLI-publisering eller bakoverkompatible migreringer), og bestem hvordan Preview-databasen migreres |
| 2.18 | Middels | Klientatferd / AD-1 / Structural Seed | `postnumre.json` og postnummer-tabellen må lages i bygg eller migrering, ikke bare ved seeding |
| 2.8 | Middels | AD-13 / Konfig | Egen `MIGRATION_DATABASE_URL` (session pooler, port 5432) for Alembic i Actions |
| 2.16 | Middels | AD-12 | Samlet 10 s-frist må lages selv; `httpx` gir bare frist per operasjon |
| 2.9 | Middels | Stack | `psycopg[binary]` |
| 2.13 | Middels (ikke bekreftet) | AD-5 / AD-7 | Spike-test av at kroppen kan leses i mellomvaren, ellers ren ASGI eller `Depends` |
| 2.1–2.4, 2.10–2.17 | Lav | diverse | Eksplisitt entrypoint, `functions`-nøkkel `main.py`, ikke `cdn=true`, Preview-beskyttelse, `postgresql+psycopg://`, `str \| None = None`, `TemplateResponse(request, …)`, rundtur for sommertid, NLOD-kilde og kreditering, `cp1252`, låst `postgres:`-image, `fastapi~=0.165.0`, `httpx<1.0` |
