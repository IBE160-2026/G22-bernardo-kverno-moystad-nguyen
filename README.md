# G22 — ZipIT

Gruppeprosjekt i **IBE160 Programmering med KI** ved Høgskolen i Molde, høsten 2026 (15 studiepoeng).

Repoet inneholder gruppens applikasjon og dokumentasjon av utvikling, testing og kvalitetssikring med KI.

## Nabolagshelten

Nabolagshelten er en webapp som kobler personer som trenger hjelp til små, praktiske hverdagsoppgaver – snømåking, hagearbeid, bærehjelp, dyrepass, teknologihjelp – med naboer i samme postnummer som har tid til å hjelpe.

Appen har én kjerneflyt: legge ut et oppdrag → melde interesse → velge hjelper → markere som utført → gi tilbakemelding. Fullførte oppdrag og tilbakemeldinger samles i hjelperens profil, slik at småjobber blir dokumentert erfaring. En avgrenset KI-funksjon foreslår kategori, tittel og beskrivelse når et oppdrag legges ut, men appen fungerer fullt ut uten KI.

## Status

Prosjektet er i implementasjonsfasen (Epic 1). Frist for innlevering er 15. desember 2026.

| Steg | Status |
|---|---|
| Product brief | Ferdig (v2.2), revidert etter tilbakemelding fra faglærer |
| PRD (kravdokument) | Ferdig (v1.2) |
| UX-design | Ferdig: designsystem, atferd, mockups og tilgjengelighetsgjennomgang |
| Arkitektur | Ferdig: FastAPI + Jinja, SQLite lokalt og Supabase Postgres på Vercel (AD-1–AD-17) |
| Epics og stories | Ferdig: [epics.md](_bmad-output/planning-artifacts/epics.md) og [sprint-status.yaml](_bmad-output/implementation-artifacts/sprint-status.yaml) |
| Implementasjon og testing | Pågår: story 1.1 (skjelett lokalt og i CI) |

## Kom i gang

Appen kjører lokalt mot en SQLite-fil, uten `.env`, kontoer eller nøkler (NFR-1).

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
- `uv run python -m app.seed` kjører `alembic upgrade head`. Det lager SQLite-fila `nabolagshelten.db` med tabellene og postnumrene. Eksempelbrukere og eksempeloppdrag kommer i story 1.2 og senere.
- Åpne <http://127.0.0.1:8000/logg-inn> i nettleseren. Stopp appen med Ctrl+C.

Vil du overstyre en innstilling, kopier `.env.example` til `.env` og fyll inn verdien. Tomme verdier gir standardverdien.

### Kjør testene

```bash
uv run pytest
```

Testene bruker en midlertidig SQLite-fil som slettes etterpå. Med miljøvariabelen `TEST_DATABASE_URL` kjører de mot Postgres i stedet, slik CI gjør.

### Arbeidsflyt og CI

- All kode går via pull request mot `main`, og en PR merges bare når CI er grønn. Logger (`.logs/`) og `sprint-status.yaml` kan pushes direkte til `main`.
- Regelen er skrevet her fordi ingen i gruppen har admin-rettighet på repoet, så GitHub sin beskyttelse av `main` kan ikke slås på (avvik ført i PRD §9.2).
- CI ([`.github/workflows/ci.yml`](.github/workflows/ci.yml)) kjører på hver PR og ved push til `main`: pytest mot SQLite og mot Postgres 17, sjekk av at Alembic har nøyaktig ett hode, og gitleaks over hele historikken (NFR-3).

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
data/postnumre.tsv  Brings postnummerregister i UTF-8
migrations/         Alembic-migreringer (skjema og postnumre)
tests/              pytest-tester; tests/core/ har arkitektur, mellomvare, feil og migrering
.github/workflows/  CI (ci.yml)
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

Appen publiseres på Vercel med database hos Supabase (se arkitekturspinen). Hemmeligheter ligger i Vercel og GitHub Secrets, aldri i repoet.

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
