# G22 — ZipIT

Gruppeprosjekt i **IBE160 Programmering med KI** ved Høgskolen i Molde, høsten 2026 (15 studiepoeng).

Repoet inneholder gruppens applikasjon og dokumentasjon av utvikling, testing og kvalitetssikring med KI.

## Nabolagshelten

Nabolagshelten er en webapp som kobler personer som trenger hjelp til små, praktiske hverdagsoppgaver – snømåking, hagearbeid, bærehjelp, dyrepass, teknologihjelp – med naboer i samme postnummer som har tid til å hjelpe.

Appen har én kjerneflyt: legge ut et oppdrag → melde interesse → velge hjelper → markere som utført → gi tilbakemelding. Fullførte oppdrag og tilbakemeldinger samles i hjelperens profil, slik at småjobber blir dokumentert erfaring. En avgrenset KI-funksjon foreslår kategori, tittel og beskrivelse når et oppdrag legges ut, men appen fungerer fullt ut uten KI.

## Status

Prosjektet er i implementasjonsfasen: Epic 1 (konto og innlogging) er ferdig, Epic 2 (legge ut og finne oppdrag) er neste. Frist for innlevering er 15. desember 2026.

| Steg | Status |
|---|---|
| Product brief | Ferdig (v2.2), revidert etter tilbakemelding fra faglærer |
| PRD (kravdokument) | Ferdig (v1.2.1) |
| UX-design | Ferdig: designsystem, atferd, mockups og tilgjengelighetsgjennomgang |
| Arkitektur | Ferdig: FastAPI + Jinja, SQLite lokalt og Supabase Postgres på Vercel (AD-1–AD-17) |
| Epics og stories | Ferdig: [epics.md](_bmad-output/planning-artifacts/epics.md) og [sprint-status.yaml](_bmad-output/implementation-artifacts/sprint-status.yaml) |
| Implementasjon og testing | Pågår: Epic 1 ferdig (story 1.1–1.5: skjelett, innlogging, publisering i produksjon, registrering og automatisk test av universell utforming), med retrospektiv og herding. Epic 2 er neste |

## Kom i gang

Appen kjører lokalt mot en SQLite-fil, uten `.env`, kontoer eller nøkler (NFR-1).

Produksjonsversjonen ligger på <https://nabolagshelten.vercel.app/>. Der finnes ingen testbrukere fra seed. Lag en egen konto på <https://nabolagshelten.vercel.app/registrer> (FR-1). Bruk bare oppdiktede opplysninger, fordi kontoer ikke kan slettes før story 4.5 er ferdig. Se [Publisering i produksjon](#publisering-i-produksjon).

### Forutsetninger

- [uv](https://docs.astral.sh/uv/getting-started/installation/), testet med 0.12.13. Sjekk med `uv --version`, og oppdater med `uv self update` hvis den er eldre.
- Python 3.12. Har du ikke Python 3.12, laster `uv sync` det ned automatisk (versjonen står i `.python-version`).
- Git. Ingen database, Node eller Docker trengs.

### Start appen

Kjør fra rotmappa i repoet:

```bash
uv sync
uv run python -m app.seed
uv run uvicorn main:app --reload
```

- `uv sync` installerer avhengighetene i `.venv/` med de låste versjonene i `uv.lock`.
- `uv run python -m app.seed` kjører `alembic upgrade head`. Det lager SQLite-fila `nabolagshelten.db` med tabellene og postnumrene, og legger inn de seks testbrukerne under. Seed kan kjøres flere ganger; brukere som finnes, røres ikke. Eksempeloppdrag kommer i story 2.1 og senere.
- Åpne <http://127.0.0.1:8000/> i nettleseren og logg inn med en av testbrukerne, eller lag en ny konto under «Registrer deg» (<http://127.0.0.1:8000/registrer>). Stopp appen med Ctrl+C.

### Testbrukere (bare for lokal testing)

Seed legger inn seks oppdiktede brukere i tre postnumre (NFR-2). E-post og passord er **bare for lokal testing**. De finnes aldri i produksjon, fordi seed nekter å kjøre der. Passordene lagres bare som hash (NFR-4).

| Navn | E-post | Passord | Postnummer | Brukes til |
|---|---|---|---|---|
| Kari Nordmann | kari@eksempel.no | kari-lokal-1 | 0571 Oslo | Oppdragsgiver (UJ-1): legger ut oppdrag og velger hjelper. |
| Ola Hansen | ola@eksempel.no | ola-lokal-1 | 0571 Oslo | Hjelper i samme postnummer som Kari: melder interesse og konkurrerer med Amir. |
| Amir Haddad | amir@eksempel.no | amir-lokal-1 | 0572 Oslo | Hjelper (UJ-2): melder interesse, blir valgt og bygger profil. |
| Nora Berg | nora@eksempel.no | nora-lokal-1 | 0572 Oslo | Oppdragsgiver i 0572: oppdrag i et annet postnummer enn Kari. |
| Sofie Lie | sofie@eksempel.no | sofie-lokal-1 | 5006 Bergen | Oppdragsgiver i Bergen: viser at oversikten bare viser eget postnummer. |
| Jonas Dahl | jonas@eksempel.no | jonas-lokal-1 | 5006 Bergen | Hjelper i Bergen: tester postnummerfilteret og andre postnumre. |

Etter fem feil passord på samme e-post innen 15 minutter er innloggingen sperret i 15 minutter (FR-2).

### Nytt passord for en bruker

Appen har ikke «glemt passord» i v1 (PRD §6.2). Gruppen setter et nytt passord for hånd:

```bash
uv run python -m app.admin nytt-passord kari@eksempel.no
```

Kommandoen viser hvilken database den er koblet til (uten passord), spør etter det nye passordet to ganger (8–64 tegn, vises ikke på skjermen) og krever at du skriver `ja`. Brukerens gamle innlogginger og mislykkede forsøk slettes. Den virker mot den `DATABASE_URL` som er satt, også produksjon, så sjekk databasenavnet før du skriver `ja`.

Vil du overstyre en innstilling, kopier `.env.example` til `.env` og fyll inn verdien. Tomme verdier gir standardverdien.

### Kjør testene

```bash
uv run pytest
```

Testene bruker en midlertidig SQLite-fil som slettes etterpå. Med miljøvariabelen `TEST_DATABASE_URL` kjører de mot Postgres i stedet, slik CI gjør.

Vanlig `uv run pytest` hopper over T1 (testene er valgt bort, ikke feilet), så kommandoen virker uten nettleser.

#### T1: universell utforming i nettleser

T1 åpner sidene i en ekte nettleser (Chromium) med Playwright og sjekker dem med axe (SM-5, NFR-6, NFR-7). Alt installeres med uv, uten npm:

```bash
uv run playwright install chromium   # én gang, laster ned nettleseren
uv run pytest -m e2e
```

- Hver side og tilstand sjekkes med axe ved 360 og 1280 px. Brudd med alvorlighet «serious» eller «critical» stopper testen, og feilmeldingen viser regel, alvorlighet og selektor.
- Hver side sjekkes for vannrett rulling ved 320 px.
- I tillegg testes JavaScript-oppførselen: «Vis passord», sendeknappen (`aria-disabled`) og poststed ved postnummerfeltet.
- Testene starter en egen server på en ledig port med en egen SQLite-fil i temp-mappen, og setter tilstanden (testbrukere og klokke) gjennom `POST /_test/tilstand`. Den ruta finnes bare når `APP_ENV=test`.
- Lista over sider står i `SIDER` i [`tests/e2e/test_t1.py`](tests/e2e/test_t1.py). Hver story som lager en ny side eller tilstand, legger den inn der (Definition of Done).
- På Linux trenger nettleseren systembiblioteker: `uv run playwright install --with-deps chromium`.

### Arbeidsflyt og CI

- All kode går via pull request mot `main`, og en PR merges bare når CI er grønn. Logger (`.logs/`) og `sprint-status.yaml` kan pushes direkte til `main`.
- Regelen er skrevet her fordi ingen i gruppen har admin-rettighet på repoet, så GitHub sin beskyttelse av `main` kan ikke slås på (avvik ført i PRD §9.2).
- CI ([`.github/workflows/ci.yml`](.github/workflows/ci.yml)) kjører på hver PR og ved push til `main`: pytest mot SQLite og mot Postgres 17, sjekk av at Alembic har nøyaktig ett hode, T1 med Playwright og axe (SM-5), og gitleaks over hele historikken (NFR-3).
- Etter merge til `main` publiseres appen automatisk, se under.

### Publisering i produksjon

Appen kjører på Vercel (region `dub1`, Irland) med database hos Supabase (`eu-west-1`): <https://nabolagshelten.vercel.app/> (AR-1, AR-7).

- **Når:** hver push til `main` som endrer kode, kjører [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml). Endringer som bare gjelder `.logs/`, `_bmad-output/`, `docs/` eller `.md`-filer, publiseres ikke. Workflowen kan også startes for hånd (Actions → Deploy → Run workflow), men publiseringen kjører bare fra `main`. Startes den fra en annen branch, kjører bare CI.
- **Hva:** først kjører hele CI ([`ci.yml`](.github/workflows/ci.yml)) på samme commit (`needs: ci`), så bare testet kode publiseres. Deretter `alembic upgrade head` mot Supabase gjennom session pooler (port 5432). Feiler migreringen, publiseres ingenting. Så `vercel deploy --prod` med Vercel CLI (`vercel@66.6.0`), og til slutt en røyktest mot produksjonsadressen. Vercels GitHub-app og preview-miljøer brukes ikke (`vercel.json`). En publisering avbrytes aldri midt i; neste venter i kø.
- **Røyktest:** `uv run python scripts/roykttest.py [url]` sjekker at innloggingssiden og registreringssiden svarer med sikkerhetsheaderne, at et innloggingsforsøk med e-posten `roykttest@nabolagshelten` avvises med «Feil e-post eller passord.» (det viser at CSRF-sjekken virker bak Vercels proxy og at databasen svarer), at testruta `/_test/tilstand` gir 404, og at CSS-fila lastes. E-posten kan ikke registreres (domenet mangler punktum), så ingen kan lage kontoen og gjøre publiseringen rød. At det ikke finnes testbrukere fra seed i produksjon, sikres av at seed nekter å kjøre der. Hvem som helst kan likevel registrere en adresse som `kari@eksempel.no` som en vanlig konto (den er da ikke en seed-konto), og derfor ser røyktesten ikke lenger etter den. Røyktesten registrerer aldri kontoer. Den kan også kjøres mot en lokal server, også med seed; da er eneste avvik at CSRF-cookien mangler `Secure`, fordi den bare settes i produksjon. `tests/test_roykttest.py` kjører den i CI mot en app med `APP_ENV=production` (ingen avvik), mot en lokal app og mot testappen.
- **Feiler røyktesten etter publisering:** eieren ruller tilbake i Vercel (Deployments → forrige versjon → Instant Rollback) og retter feilen i en ny PR.
- **Keepalive:** [`.github/workflows/keepalive.yml`](.github/workflows/keepalive.yml) besøker forsiden hver tredje dag med en falsk sesjonscookie. Appen slår opp sesjonen i databasen og svarer 303, så Supabase-prosjektet ikke settes på pause. Feiler jobben, sender GitHub e-post.
- **Ingen seed i produksjon:** seed nekter å kjøre der, og migreringer legger bare til etter første publisering.
- **Testkonto i produksjon:** gruppen registrerer én testkonto for hånd på `/registrer` for å sjekke registrering, innlogging og utlogging etter publisering. Den har bare oppdiktede opplysninger, verdiene står aldri i repoet, i logger eller i chat, og kontoen slettes med `app.admin slett-konto` når story 4.5 er ferdig (AR-10).

Hemmelighetene ligger bare hos Vercel og GitHub, aldri i repoet, i logger eller i chat (NFR-3). Her står bare navnene:

| Hvor | Navn | Innhold |
|---|---|---|
| Vercel env (Production) | `APP_ENV` | `production` (appen nekter å starte på Vercel med `local` eller `test`) |
| Vercel env (Production) | `DATABASE_URL` | Supabase transaction pooler (port 6543), brukt av appen |
| Vercel env (Production) | `SECRET_KEY` | tilfeldig nøkkel på minst 32 tegn |
| GitHub Secrets | `MIGRATION_DATABASE_URL` | Supabase session pooler (port 5432), brukt av migreringen |
| GitHub Secrets | `VERCEL_TOKEN` | token for Vercel CLI |
| GitHub Secrets | `VERCEL_ORG_ID`, `VERCEL_PROJECT_ID` | id-ene fra `.vercel/project.json` etter `vercel link` |

Verdiene legges inn i Vercels nettside og med `gh secret set <NAVN>` (verdien limes inn skjult). `gh secret list` viser navnene uten verdier.

### Data og lisens

Postnummerdata fra Posten Bring, lisensiert under NLOD 2.0.

`data/postnumre.tsv` er Brings postnummerregister (<https://www.bring.no/postnummerregister-ansi.txt>) konvertert til UTF-8 med alle rader og kolonner uendret. Appen godtar bare postnumre for gateadresser (Brings kategori G og B). `app/core/static/postnumre.json` lages fra TSV-fila med `uv run python -m app.core.postnummer`.

## Dokumentasjon

| Dokument | Innhold |
|---|---|
| [Product brief](_bmad-output/planning-artifacts/product-brief-nabolagshelten.md) | Problem, målgruppe, regler (R1–R13) og suksesskriterier (SK1–SK10). Brukes som «proposal» i sensorveiledningen. |
| [Tilbakemelding fra faglærer](tilbakemelding-product-brief.md) | Faglærers vurdering av product brief |
| [PRD](_bmad-output/planning-artifacts/prds/prd-G22-bernardo-kverno-moystad-nguyen-2026-11-05/prd.md) | Krav med faste ID-er (FR-1–FR-26, NFR-1–NFR-12), sporing fra briefen (§9.1) og avvik fra briefen (§9.2) |
| [Reviewer av PRD-en](_bmad-output/planning-artifacts/prds/prd-G22-bernardo-kverno-moystad-nguyen-2026-11-05/) | Review-rapporter, hva som ble gjort med hvert funn, og beslutningsloggen (`.memlog.md`) |
| [Skisser av skjermbilder](_bmad-output/planning-artifacts/skisser-skjermbilder.md) | Første utkast til de viktigste skjermbildene; videreført i UX-designet under |
| [DESIGN.md](_bmad-output/planning-artifacts/ux-designs/ux-G22-bernardo-kverno-moystad-nguyen-2026-11-07/DESIGN.md) | Hvordan appen ser ut: farger med kontrastverdier, typografi, layout og komponenter |
| [EXPERIENCE.md](_bmad-output/planning-artifacts/ux-designs/ux-G22-bernardo-kverno-moystad-nguyen-2026-11-07/EXPERIENCE.md) | Hvordan appen oppfører seg: navigasjon, tekster, feilmeldinger, tomtilstander, fokus og universell utforming (NFR-7) med testplan |
| [Mockups](_bmad-output/planning-artifacts/ux-designs/ux-G22-bernardo-kverno-moystad-nguyen-2026-11-07/mockups/) | Klikkbare HTML-mockups av nøkkelskjermbildene og fargetemaer |
| [Tilgjengelighetsgjennomgang](_bmad-output/planning-artifacts/ux-designs/ux-G22-bernardo-kverno-moystad-nguyen-2026-11-07/review-accessibility.md) | Gjennomgang av UX-designet mot WCAG 2.1 AA, med funn og testdekning |
| [Arkitekturspine](_bmad-output/planning-artifacts/architecture/architecture-G22-bernardo-kverno-moystad-nguyen-2026-11-08/ARCHITECTURE-SPINE.md) | Arkitekturbeslutningene (AD-1–AD-17) som alle stories skal følge, med stack, miljøer, datamodell og kobling til FR/NFR. Beslutningsloggen (`.memlog.md`) og reviewene ligger i samme mappe. |
| [Sensorveiledning del 1](docs/sensorveiledning-del1.md) | Kriteriene prosjektet vurderes etter |

## Slik jobber vi med KI

- Vi bruker [BMAD Method](https://github.com/bmad-code-org/BMAD-METHOD) (v6.12.4) med Claude Code. Arbeidet går i rekkefølgen brief → PRD → UX → arkitektur → epics og stories → kode, og hvert steg bygger på dokumentet fra steget før.
- Krav-ID-ene i PRD-en (FR-N, NFR-N) brukes i stories, commits og PR-er, slik at et krav kan spores fra briefen til koden.
- Hver KI-økt logges i `.logs/<navn>/`: hva vi ba om, hvordan det ble løst, resultatet og hva som gjenstår. Åpne punkter samles i `.logs/<navn>/issues.md`.
- [CLAUDE.md](CLAUDE.md) gir Claude Code prosjektets regler, blant annet at sensorveiledningen skal følges i alt arbeid.

## Mappestruktur

```text
main.py             Inngangspunkt for uvicorn og Vercel: app = lag_app()
app/                Appen: core/ (felles kjerne) og slicene identity/, oppdrag/, profil/, ki/
app/seed.py         Gjør databasen klar lokalt (uv run python -m app.seed)
app/admin.py        Manuell hjelp: nytt passord (uv run python -m app.admin nytt-passord <e-post>)
data/postnumre.tsv  Brings postnummerregister i UTF-8
migrations/         Alembic-migreringer (skjema og postnumre)
tests/              pytest-tester per slice; tests/core/ har arkitektur, mellomvare, tilgang, feil og migrering
tests/e2e/          T1: Playwright og axe i ekte nettleser (uv run pytest -m e2e)
scripts/roykttest.py  Røyktest mot en publisert versjon (brukes av deploy.yml)
.github/workflows/  CI (ci.yml), publisering (deploy.yml) og keepalive (keepalive.yml)
vercel.json         Vercel-oppsett: region, maks kjøretid, Git-publisering av; .vercelignore utelater dokumenter og tester
pyproject.toml      Avhengigheter; uv.lock låser versjonene
.claude/skills/     BMAD-skills og sesjonslogg-skillen for Claude Code
_bmad/              BMAD-rammeverket: konfigurasjon og skript
_bmad-output/       Dokumenter laget med BMAD (brief, PRD, UX, arkitektur, epics, stories)
docs/               Sensorveiledning
.logs/              KI-sesjonslogger per gruppemedlem
CLAUDE.md           Instruksjoner til Claude Code
```

## For gruppen: oppsett for BMAD

BMAD-skillene kjører skriptene i `_bmad/scripts/` med `uv run`. Det krever:

- Python 3.11 eller nyere. Python installeres for hele maskinen, ikke i prosjektmappa.
- [uv](https://docs.astral.sh/uv/getting-started/installation/)

Sjekk med `python --version` og `uv --version`. Personlige BMAD-innstillinger ligger i `_bmad/config.user.toml`, som ikke er i repoet.

## Kontoer for drift

Appen publiseres på Vercel med database hos Supabase (se [Publisering i produksjon](#publisering-i-produksjon) og arkitekturspinen). Hemmeligheter ligger i Vercel og GitHub Secrets, aldri i repoet.

Eieren sjekker i Supabase at prosjektet er aktivt (ikke satt på pause) og at siste keepalive-kjøring er grønn, før hver demo og jevnlig til sensuren er ferdig, ikke bare før innlevering. GitHub slår av planlagte workflows etter 60 dager uten aktivitet i repoet, og da stopper keepalive.

| Tjeneste | Eier | Reserve |
|---|---|---|
| Vercel | Heidi Kverno | ingen ennå |
| Supabase | Heidi Kverno | ingen ennå |
| OpenRouter (valgfri, KI) | Heidi Kverno | ingen ennå |

## Medlemmer

- Reika Bernardo
- Heidi Kverno
- Anders Møystad
- Jenny T Nguyen
