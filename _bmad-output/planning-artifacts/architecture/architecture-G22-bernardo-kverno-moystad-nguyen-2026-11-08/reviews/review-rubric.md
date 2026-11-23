---
type: review-rubric
spine: ../ARCHITECTURE-SPINE.md (draft, oppdatert 2026-11-23)
input: ../../../prds/prd-G22-bernardo-kverno-moystad-nguyen-2026-11-05/prd.md (PRD v1.1)
date: 2026-11-23
forutsetter: reconcile-prd.md og reconcile-ux.md er tatt inn (funnene der gjentas ikke)
---

# Rubrikk-review: arkitekturspinen for Nabolagshelten v1

## Konklusjon

**Godkjent med endringer.** Spinen er sterk der det kodes: AD-1 til AD-16 setter de reelle avvikspunktene mellom stories (status og samtidighet, tid, tekst, sesjon, CSRF, KI, personopplysninger, rendring, fokus og klient-JS). Alle FR-1 til FR-26 og NFR-1 til NFR-12 er bundet og står i kartet. Versjonene ble sjekket mot PyPI 2026-11-23 (memlog) og er ferske.

Hullet er **drift og miljøer**. Spinen tegner lokalt, CI, Preview og Produksjon, men sier ikke hvordan data og skjema kommer dit, i hvilken rekkefølge, hvem som eier kontoene, eller hva som skjer ved feil. Ett funn gjør produksjon ubrukelig slik spinen står (K1). I tillegg er det lite tid igjen: fristen er tidlig i desember, og det er omtrent to uker til. For fire nybegynnere bør noe av infrastrukturen kuttes eller forenkles (H4), siden sensor kjører appen lokalt etter README (sensorveiledningen, kriterium 6).

Alvorlighet: **kritisk** = slik spinen står, virker ikke et Må-krav i et miljø spinen lover. **høy** = stories eller publisering vil sannsynligvis gå i stykker eller bygges ulikt. **middels** = reell risiko, bør avgjøres før stories skrives. **lav** = presisering.

| # | Tema | Alvorlighet |
|---|---|---|
| K1 | Postnummertabellen og `postnumre.json` fylles bare lokalt og i test | kritisk |
| H1 | Migrering før publisering kan ikke håndheves, og tilbakerulling mangler | høy |
| H2 | Preview-miljøet er udefinert (skjema, data, flere PR-er, tilgang) | høy |
| H3 | Parallelle stories gir flere Alembic-hoder, og SQLite tåler ikke `ALTER` | høy |
| H4 | Mye infrastruktur i forhold til tid og erfaring | høy |
| M1 | Hvem eier Vercel, Supabase og hemmelighetene, og Supabase pauser gratisprosjekter | middels |
| M2 | Ekte OpenRouter-nøkkel i en åpen app uten kostnadstak | middels |
| M3 | `APP_ENV` har ikke verdien `preview`, og `Secure` «utenfor lokalt» brekker testene | middels |
| M4 | AD-7 er tung og har en regel som ikke kan håndheves («samme bruker») | middels |
| M5 | Ingen gangbar første story som går helt ut til Vercel | middels |
| L1 | AD-1 og AD-11 håndheves bare ved gjennomlesing | lav |
| L2 | Vercel-detaljer: dev-avhengigheter, `maxDuration`, statiske filer | lav |
| L3 | AD-5: hva `Origin` sammenlignes med | lav |

---

## Kritisk

### K1 — Postnummertabellen og `postnumre.json` fylles bare lokalt og i test

- **Hvor:** AD-1 (tabelleier `core | postnummer (bare lesing etter seeding)`, og seed bare når `APP_ENV` er `local` eller `test`), Structural Seed («Lokalt kjører `uv run python -m app.seed` … laster så postnumre»), konvensjonen Klientatferd (`static/postnumre.json` «lages ved seeding»).
- **Problem:** Seed kjører aldri mot Supabase, og den tømmer tabellene først, så den kan heller ikke kjøres der. Da er `postnummer` tom i Preview og Produksjon. FR-1 (postnummer må finnes i lista), FR-5 og FR-11 avviser derfor alt, og ingen kan registrere seg. `postnumre.json` finnes heller ikke på Vercel, siden fila bare lages av seed, så poststed vises ikke mens man skriver.
- **Rettelse:**
  - Skill referansedata fra eksempeldata. Ny regel i AD-1 (eller AD-13): «Postnumre lastes av en Alembic-datamigrering som leser `data/postnumre.tsv`. Dermed fylles tabellen i alle miljøer av `alembic upgrade head`. Seed laster bare eksempeldata og tømmer aldri `postnummer`.»
  - `app/core/static/postnumre.json` lages av et lite skript fra samme TSV og **sjekkes inn**. En test sjekker at JSON og TSV har samme innhold.
  - Endre tabellraden til `core | postnummer (skrives bare av migreringen)`.

---

## Høy

### H1 — Migrering før publisering kan ikke håndheves, og tilbakerulling mangler

- **Hvor:** Structural Seed, diagrammet `main → mig (GitHub Actions) → prod` og «Migrasjoner kjøres av GitHub Actions før publisering». Deferred nevner ikke tilbakerulling.
- **Problem:**
  - Vercels Git-integrasjon publiserer `main` med en gang, uavhengig av GitHub Actions. Ny kode kan derfor gå live før migreringen har kjørt, og feile på en kolonne som ikke finnes. Pila i diagrammet er ikke noe som faktisk skjer.
  - Migreringen trenger en annen tilkobling enn appen. Den direkte tilkoblingen til Supabase er bare IPv6, og GitHub-runnere har IPv4. Alembic bør heller ikke kjøre gjennom transaction pooler (6543), så migreringen må bruke session pooler (5432). Den adressen er en hemmelighet som må ligge i GitHub Secrets, men spinen nevner den ikke.
  - Ingenting hindrer en direkte push til `main` som hopper over CI.
  - Vercels Instant Rollback ruller tilbake koden, men ikke skjemaet. Har en migrering fjernet eller gitt nytt navn til en kolonne, virker den forrige utgaven ikke etter tilbakerulling.
- **Rettelse:** Ny underseksjon «Publisering» i Structural Seed:
  1. `main` er beskyttet: endringer kommer bare via PR, og CI må være grønn.
  2. Velg én måte å sikre rekkefølgen på og skriv den inn:
     - (a) **Anbefalt:** Slå av automatisk produksjonspublisering i `vercel.json` (`git.deploymentEnabled.main: false`). Jobben på `main` kjører `alembic upgrade head` og deretter `vercel deploy --prod` med `VERCEL_TOKEN`.
     - (b) La Vercel publisere som nå, men bruk Vercels deployment checks, slik at produksjon ikke tas i bruk før GitHub-jobben `migrate` er grønn. Sjekk først at Hobby-planen har dette.
  3. Hemmeligheter i GitHub Secrets: `MIGRATION_DATABASE_URL` (session pooler, port 5432) og eventuelt `VERCEL_TOKEN`. Appen bruker fortsatt `DATABASE_URL` med port 6543.
  4. Tilbakerulling: «Migreringer etter første produksjonspublisering legger bare til (nye tabeller og kolonner som kan være NULL). Ingen kolonner fjernes eller får nytt navn i v1. Da er Vercel Instant Rollback alltid trygt. Feil i data rettes med en ny migrering.»
  5. `SECRET_KEY` kan byttes uten at noen blir logget ut, fordi sesjonene ligger i databasen. Bare CSRF- og kvitteringscookies blir ugyldige. Skriv det i én linje.

### H2 — Preview-miljøet er udefinert

- **Hvor:** Diagrammet `pr → prev → sb2`, miljøtabellen (raden Preview).
- **Problem:**
  - Ingen jobb migrerer Supabase-prosjekt 2. Diagrammet viser migrering bare fra `main`.
  - Det kommer ingen data dit. Seed er forbudt utenfor `local` og `test` (AD-1), så Preview har ingen brukere og ingen oppdrag, og (med K1) heller ingen postnumre.
  - Alle åpne PR-er deler én database. To PR-er med hver sin nye migrering gir to ulike Alembic-revisjoner. Den som publiseres sist, får en database den andre ikke kjenner, og `alembic upgrade` feiler med «Can't locate revision».
  - `APP_ENV` for Preview står ikke (se M3).
  - På Hobby har preview-adresser som standard Vercel Authentication. Da kan bare eieren av Vercel-kontoen åpne dem, og ikke de tre andre i gruppen. Dette bør sjekkes.
- **Rettelse:** Velg én av disse og skriv den inn:
  - (a) **Anbefalt med tanke på tiden (H4):** Ingen Preview-publisering i v1 (`git.deploymentEnabled` bare for `main`), og ingen Supabase-prosjekt 2. PR-er sjekkes av CI og ved at man kjører appen lokalt. Flytt Preview til Deferred med begrunnelse: «Sensor kjører lokalt. Preview gir lite i forhold til hva drift av en delt database koster.»
  - (b) Preview-databasen kan kastes: Ved hver preview-publisering kjører en GitHub-jobb `DROP SCHEMA public CASCADE; CREATE SCHEMA public`, så `alembic upgrade head`, og så seed med `APP_ENV=preview`. Utvid unntaket i AD-1 til `local`, `test` og `preview`. Regel: «Siste publisering vinner. Bare én PR kan prøves i Preview om gangen.» Slå av Vercel Authentication for previews, eller godta at bare eieren ser dem.

### H3 — Parallelle stories gir flere Alembic-hoder, og SQLite tåler ikke `ALTER`

- **Hvor:** AD-13 («Skjemaet endres bare med Alembic»), konvensjonen Tester.
- **Problem:**
  - To stories på hver sin gren lager hver sin migrering fra samme `down_revision`. Etter sammenslåing har `main` to hoder, `alembic upgrade head` feiler, og produksjonspubliseringen stopper. Med fire utviklere som jobber samtidig skjer dette nesten helt sikkert.
  - SQLite kan nesten ikke endre kolonner (`ALTER COLUMN`, nye constraints). Uten batch-modus kan en migrering som virker mot Postgres, feile lokalt, eller omvendt. Det er akkurat avviket AD-13 skal hindre.
  - Autogenerering skriver `UtcDateTime` (AD-9) som `app.core.db.UtcDateTime` uten import, og migreringsfila feiler.
- **Rettelse:** Legg til i AD-13:
  - «`migrations/env.py` bruker `render_as_batch=True`. Malen `script.py.mako` importerer `app.core.db`.»
  - «CI feiler hvis `alembic heads` gir mer enn én linje. Før sammenslåing tar den som er sist, `git pull` og setter `down_revision` på nytt (eller kjører `alembic merge`).»
  - «Én migrering per story. Den gjennomgås i PR-en som kode, også når den er autogenerert.»

### H4 — Mye infrastruktur i forhold til tid og erfaring

- **Hvor:** Hele Structural Seed og Stack: to Supabase-prosjekter, Preview, migrering i Actions, CI mot to databaser, Playwright med axe, gitleaks, AD-7 og AD-15.
- **Problem:** Fristen er tidlig i desember, omtrent to uker fra i dag (2026-11-23). Gruppen er nybegynnere (memlog, valg 1). Sensor vurderer appen **lokalt** etter README (kriterium 6). Vercel er et krav fra faglærer, men vurderes ikke. Hver ekstra driftsdel er noe som kan stoppe gruppen i siste uke uten at det hindrer avvik mellom stories. Spinen sier ikke hva som kan kuttes.
- **Rettelse:** Ny tabell «Prioritet for infrastruktur» (samme logikk som PRD §6.1):

  | Må (bygges først) | Kan kuttes, i denne rekkefølgen |
  |---|---|
  | Lokal kjøring med SQLite, seed og mock (NFR-1, NFR-2) | 1. Preview og Supabase-prosjekt 2 (H2a) |
  | pytest mot SQLite, CSRF og headere, FR-3-testen | 2. Gjenvisning av skjema med innlogging i AD-7 (M4): erstatt med en 401-side som har teksten og en lenke til innlogging |
  | Én produksjonspublisering på Vercel med Supabase | 3. Postgres-jobben i CI. Erstatt med én manuell kjøring før innlevering, og dokumenter den |
  | gitleaks (NFR-3), axe i Playwright (SM-5) | 4. `steg.js` (uten JS: én skjerm, som spinen allerede sier) |

  Hvert kutt føres i memlog og i PRD §9.2, slik PRD §6.1 sier.

---

## Middels

### M1 — Hvem eier Vercel, Supabase og hemmelighetene, og Supabase pauser gratisprosjekter

- **Hvor:** Stack (`Vercel … Hobby`, `Supabase Postgres | Free, to prosjekter`), miljøtabellen (kolonnen Hemmeligheter), Deferred («Vercel-loggene holder»).
- **Problem:**
  - Vercel Hobby er en personlig konto uten team (memlog: «ingen delte team»). Bare eieren ser miljøvariabler, logger og previews, og bare eieren kan rulle tilbake.
  - Supabase Free gir høyst to aktive gratisprosjekter per eier. Har eieren allerede ett, passer ikke to nye.
  - Gratisprosjekter pauses etter omtrent en uke uten trafikk. Produksjon kan være pauset når faglærer eller sensor åpner lenken.
  - Repoet er offentlig, og spinen sier ikke hvor hver hemmelighet ligger, eller hvem som kan endre den.
- **Rettelse:** Ny tabell «Kontoer og hemmeligheter» i Structural Seed:
  - Én navngitt eier (rolle, ikke nødvendigvis navn i spinen) for Vercel, Supabase og OpenRouter. Én reserveperson har innlogging til Supabase (Supabase-organisasjoner kan ha flere medlemmer gratis).
  - Hvor hver hemmelighet ligger: `SECRET_KEY`, `DATABASE_URL` og `OPENROUTER_API_KEY` i Vercel env (Production), og `MIGRATION_DATABASE_URL` og `VERCEL_TOKEN` i GitHub Secrets (H1). Ingenting i repoet (NFR-3).
  - GitHub Actions bruker aldri `pull_request_target`, så PR-er fra forks aldri får hemmelighetene.
  - Pause: «Eieren åpner Supabase og appen dagen før demo og innlevering.» (Alternativt en ukentlig planlagt GitHub-jobb som besøker appen. Det er ikke cron i appen, så det strider ikke mot AD-3.)

### M2 — Ekte OpenRouter-nøkkel i en åpen app uten kostnadstak

- **Hvor:** AD-12 (kvote 20 per bruker per time), miljøtabellen (Produksjon: «OpenRouter eller mock»).
- **Problem:** Registreringen er åpen, og alle kan lage så mange kontoer de vil. Kvoten per bruker begrenser derfor ikke den totale bruken. En nøkkel med kredittkort bak kan tømmes.
- **Rettelse:** Legg til i AD-12: «I produksjon brukes en OpenRouter-nøkkel med kredittgrense satt i OpenRouter (eller en gratismodell). Uten grense kjører produksjon i mock.» Én linje i Deferred: «Ingen grense for antall registreringer i v1.»

### M3 — `APP_ENV` har ikke verdien `preview`, og `Secure` «utenfor lokalt» brekker testene

- **Hvor:** AD-14, AD-4 («`Secure` utenfor lokalt»), AD-1 (unntak for seed), miljøtabellen.
- **Problem:**
  - Verdiene står spredt (`local`, `test`, `production`), og Preview mangler. Setter noen `APP_ENV=local` i Preview, kan seed og demokontoer kjøre mot Supabase. Med `production` gjelder vakta mot standardnøkkel, men da bryter seed i H2b AD-1.
  - «`Secure` utenfor lokalt» omfatter `test`. FastAPIs `TestClient` går mot `http://testserver`, og httpx sender ikke `Secure`-cookies over http. Da blir alle innloggede tester røde.
- **Rettelse:** Én tabell i AD-14 med de fire verdiene og hva hver av dem slår på:

  | `APP_ENV` | Database | Seed og demokontoer | `Secure`-cookie | Krever ekte `SECRET_KEY` | Testbrytere |
  |---|---|---|---|---|---|
  | `local` | SQLite-fil | ja | nei | nei | nei |
  | `test` | SQLite i minnet / Postgres | ja | nei | nei | ja |
  | `preview` (bare hvis H2b) | Supabase 2 | ja, med tilbakestilling | ja | ja | nei |
  | `production` | Supabase 1 | nei | ja | ja | nei |

  Ukjent verdi gjør at appen ikke starter.

### M4 — AD-7 er tung og har en regel som ikke kan håndheves

- **Hvor:** AD-7.
- **Problem:**
  - «Slipper forespørselen videre … men bare hvis det er samme bruker»: Når sesjonen er utløpt eller slettet, vet ikke `core` hvem den gamle brukeren var. Utløpte sesjoner slettes ved neste innlogging (AD-4), så regelen kan ikke gjennomføres likt av alle. Den er dessuten unødvendig, fordi servicen uansett sjekker eierskap (NFR-5). Logger en annen bruker inn, avvises for eksempel redigering av andres oppdrag.
  - Rekkefølgen på mellomvarene står ikke. Gjenvisningssiden må ha en ny CSRF-nøkkel, og CSRF-sjekken må kjøre før innloggingen i mellomvaren. Ellers bygger to personer dette ulikt.
  - For en nybegynnergruppe er dette den mest kompliserte enkeltdelen i spinen. Det skjer sjelden, siden sesjonen varer i 7 dager.
- **Rettelse:**
  - Erstatt «bare hvis det er samme bruker» med «Ruta behandler forespørselen som den nye innloggede brukeren. Tilgangsreglene i servicen gjelder som vanlig.»
  - Legg til: «Rekkefølgen på mellomvarene er: sikkerhetsheadere → CSRF → innlogging (AD-4 og AD-7). Gjenvisningssiden har ny CSRF-nøkkel.»
  - Merk AD-7 som kuttbar (H4, punkt 2), med reserveløsning: 401-side med «Du må logge inn igjen.» og en lenke til innlogging. UX godtar «eller brukeren får beskjed før det går tapt».

### M5 — Ingen gangbar første story som går helt ut til Vercel

- **Hvor:** Deferred, raden «CSS-struktur …» («Den første storyen lager `core.render`, `base.html` og makroene»).
- **Problem:** Spinen sier hva den første storyen bygger i koden, men ikke at publiseringen skal virke tidlig. Problemer med Vercel og Supabase (IPv4, pooler, `prepare_threshold`, K1, H1) oppdages da først når mye er bygd, altså i siste uke.
- **Rettelse:** I Structural Seed: «Første story er et skjelett som går helt gjennom: `lag_app()`, `core.render`, innlogging som virker, én migrering med postnumre (K1), CI som er grønn, og produksjonspublisering på Vercel mot Supabase med migrering først (H1). Andre stories starter først når denne er ferdig.»

---

## Lav

### L1 — AD-1 og AD-11 håndheves bare ved gjennomlesing

- **Hvor:** AD-1 (importretning), AD-11 (`|safe`, `Markup`, `innerHTML`).
- **Problem:** Reglene er tydelige, men ingen test eller sjekk fanger brudd. KI-generert kode bryter slike regler lett, og sensorveiledningen ber om spor av at feil i KI-kode blir funnet (kriterium 3).
- **Rettelse:** I konvensjonen Tester: «`tests/core/test_arkitektur.py` sjekker importretningen fra figuren i AD-1 (med `ast` eller import-linter), og at `|safe`, `Markup(` og `innerHTML` ikke finnes i `app/` utenom en tillatt liste.»

### L2 — Vercel-detaljer: dev-avhengigheter, `maxDuration`, statiske filer

- **Hvor:** Stack, Structural Seed.
- **Problem:**
  - Vercel installerer fra `pyproject.toml`. Ligger Playwright, pytest eller axe blant vanlige avhengigheter, blir funksjonen stor og kan gå over størrelsesgrensen.
  - Spinen sier ikke hvor `maxDuration` 30 s settes når FastAPI kjører uten konfigurasjon.
  - Memlog fant at med mellomvare på toppnivå blir statiske filer i funksjonen, med mindre `[tool.vercel.fastapi.static] cdn = true` er satt. Det står ikke i spinen.
  - `axe-playwright-python` 0.1.x er en liten pakke med få vedlikeholdere.
- **Rettelse:**
  - «Testverktøy ligger i `[dependency-groups] dev`.»
  - «`vercel.json` har `functions."main.py".maxDuration = 30`. Sjekkes i første publisering (M5).»
  - Ta med CDN-innstillingen for statiske filer eller avvis den uttrykkelig.
  - Reserve for axe: legg inn `axe-core` med `page.add_script_tag` hvis pakken slutter å virke.

### L3 — AD-5: hva `Origin` sammenlignes med

- **Hvor:** AD-5 («POST der `Origin` eller `Sec-Fetch-Site` viser et annet nettsted, avvises»).
- **Problem:** Det står ikke hva «annet nettsted» betyr. En fast URL i konfigurasjonen brekker preview-adresser og `localhost`. `TestClient` sender ingen `Origin`.
- **Rettelse:** «`Origin` sammenlignes med forespørselens egen `Host`. Mangler `Origin`, avgjør `Sec-Fetch-Site`. Mangler begge, avgjør CSRF-nøkkelen alene.»

---

## Sjekket og i orden

- **Avvikspunkter for stories:** statusoverganger og samtidighet (AD-2), avledede tilstander uten cron (AD-3), tid (AD-9), tekst og grenser (AD-10), personopplysninger i maler (AD-16), KI-flyten (AD-12, AD-15), rendring, fokus og klient-JS (konvensjonene). De er avgjort med regler som kan testes.
- **Reglene hindrer det de sier:** AD-2 (betinget `UPDATE` og unik-constraints), AD-4 (global sjekk med unntaksliste og FR-3-test), AD-6 (én funksjon for bcrypt), AD-16 (test som søker i HTML). Unntakene er AD-1 og AD-11 (L1) og AD-7 (M4).
- **Deferred:** Ingen rad kan få to stories til å bygge ulikt. Kolonner og indekser eies av den som eier tabellen (AD-1), og unik-constraints er bestemt (AD-2). Det som mangler, er at drift ikke står i Deferred i det hele tatt (H1, H2, M1).
- **Teknologi:** Versjonene er sjekket mot PyPI 2026-11-23. Oppsettet for Supabase (port 6543, `NullPool`, `prepare_threshold=None`) og bcrypt 5 med 72 byte er riktig håndtert.
- **Dekning av PRD:** FR-1 til FR-26 og NFR-1 til NFR-12 er bundet og står i kartet. Ingen nye hull utover reconcile-funnene, bortsett fra K1, der FR-1, FR-5 og FR-11 ikke virker i produksjon.
- **Passer for målgruppen:** Server-rendret monolitt, synkron SQLAlchemy, ingen npm og ingen byggsteg, og mock uten nøkler er godt valgt for nybegynnere. Det som er for tungt, er drift (H2, H4) og AD-7 (M4), ikke koden.
