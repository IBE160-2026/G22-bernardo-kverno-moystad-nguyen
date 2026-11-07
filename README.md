# G22 — ZipIT

Gruppeprosjekt i **IBE160 Programmering med KI** ved Høgskolen i Molde, høsten 2026 (15 studiepoeng).

Repoet inneholder gruppens applikasjon og dokumentasjon av utvikling, testing og kvalitetssikring med KI.

## Nabolagshelten

Nabolagshelten er en webapp som kobler personer som trenger hjelp til små, praktiske hverdagsoppgaver – snømåking, hagearbeid, bærehjelp, dyrepass, teknologihjelp – med naboer i samme postnummer som har tid til å hjelpe.

Appen har én kjerneflyt: legge ut et oppdrag → melde interesse → velge hjelper → markere som utført → gi tilbakemelding. Fullførte oppdrag og tilbakemeldinger samles i hjelperens profil, slik at småjobber blir dokumentert erfaring. En avgrenset KI-funksjon foreslår kategori, tittel og beskrivelse når et oppdrag legges ut, men appen fungerer fullt ut uten KI.

## Status

Prosjektet er i planleggingsfasen. Frist for innlevering er begynnelsen av desember 2026.

| Steg | Status |
|---|---|
| Product brief | Ferdig (v2.2), revidert etter tilbakemelding fra faglærer |
| PRD (kravdokument) | Ferdig (v1.1) |
| UX-skisser | Utkast; oppdateres i UX-steget |
| Arkitektur | Neste steg |
| Epics og stories | Etter arkitekturen |
| Implementasjon og testing | Etter epics og stories |

## Kom i gang

Appen er ikke laget ennå. Kjøreinstruksjonene kommer når teknologien er valgt i arkitekturen: forutsetninger med versjoner, kommandoer for oppstart og eksempeldata, testbrukere og kommandoen som kjører testene. De skal virke på en ren maskin uten betalte tjenester eller gruppens egne nøkler (krav NFR-1 og NFR-2 i PRD-en).

## Dokumentasjon

| Dokument | Innhold |
|---|---|
| [Product brief](_bmad-output/planning-artifacts/product-brief-nabolagshelten.md) | Problem, målgruppe, regler (R1–R13) og suksesskriterier (SK1–SK10). Brukes som «proposal» i sensorveiledningen. |
| [Tilbakemelding fra faglærer](tilbakemelding-product-brief.md) | Faglærers vurdering av product brief |
| [PRD](_bmad-output/planning-artifacts/prds/prd-G22-bernardo-kverno-moystad-nguyen-2026-11-05/prd.md) | Krav med faste ID-er (FR-1–FR-26, NFR-1–NFR-12), sporing fra briefen (§9.1) og avvik fra briefen (§9.2) |
| [Reviewer av PRD-en](_bmad-output/planning-artifacts/prds/prd-G22-bernardo-kverno-moystad-nguyen-2026-11-05/) | Review-rapporter, hva som ble gjort med hvert funn, og beslutningsloggen (`.memlog.md`) |
| [Skisser av skjermbilder](_bmad-output/planning-artifacts/skisser-skjermbilder.md) | Utkast til de viktigste skjermbildene |
| [Sensorveiledning del 1](docs/sensorveiledning-del1.md) | Kriteriene prosjektet vurderes etter |

## Slik jobber vi med KI

- Vi bruker [BMAD Method](https://github.com/bmad-code-org/BMAD-METHOD) (v6.12.4) med Claude Code. Arbeidet går i rekkefølgen brief → PRD → UX → arkitektur → epics og stories → kode, og hvert steg bygger på dokumentet fra steget før.
- Krav-ID-ene i PRD-en (FR-N, NFR-N) brukes i stories, commits og PR-er, slik at et krav kan spores fra briefen til koden.
- Hver KI-økt logges i `.logs/<navn>/`: hva vi ba om, hvordan det ble løst, resultatet og hva som gjenstår. Åpne punkter samles i `.logs/<navn>/issues.md`.
- [CLAUDE.md](CLAUDE.md) gir Claude Code prosjektets regler, blant annet at sensorveiledningen skal følges i alt arbeid.

## Mappestruktur

```text
.claude/skills/   BMAD-skills og sesjonslogg-skillen for Claude Code
_bmad/            BMAD-rammeverket: konfigurasjon og skript
_bmad-output/     Dokumenter laget med BMAD (brief, PRD, skisser)
docs/             Sensorveiledning
.logs/            KI-sesjonslogger per gruppemedlem
CLAUDE.md         Instruksjoner til Claude Code
```

## For gruppen: oppsett for BMAD

BMAD-skillene kjører skriptene i `_bmad/scripts/` med `uv run`. Det krever:

- Python 3.11 eller nyere. Python installeres for hele maskinen, ikke i prosjektmappa.
- [uv](https://docs.astral.sh/uv/getting-started/installation/)

Sjekk med `python --version` og `uv --version`. Personlige BMAD-innstillinger ligger i `_bmad/config.user.toml`, som ikke er i repoet.

## Medlemmer

- Reika Bernardo
- Heidi Kverno
- Anders Møystad
- Jenny T Nguyen
