# Avstemming av PRD mot kildene – 2026-11-07

PRD v0.3 sjekket mot de fire kildene i `.memlog.md`. Funn markert ✅ er rettet i PRD-en samme dag.

## Product brief v2.2

- Regel R1–R13 er alle dekket: R1 FR-3, R2 FR-12, R3 FR-12/FR-13, R4 FR-6/FR-7, R5 FR-15, R6 FR-17, R7 FR-19, R8 FR-20, R9 FR-9/FR-14/FR-18/FR-21, R10 FR-16, R11 FR-1, R12 FR-23/FR-24, R13 FR-4.
- Suksesskriterium SK1–SK10 er alle dekket: SK1 FR-1/2/4, SK2 FR-5/6/7, SK3 FR-10/11, SK4 FR-12/13/14, SK5 FR-15, SK6 FR-17, SK7 FR-19, SK8 FR-20, SK9 FR-21, SK10 FR-23–26.
- Kvalitetskravene i briefen er dekket av NFR-1–NFR-6 og NFR-9.
- ✅ Kjent begrensning ved postnummergrenser («Nærhet») manglet – lagt til under FR-10.
- ✅ KI-tips («kort tips om hva som mangler») ble validert i FR-25, men ikke vist – lagt til i FR-24.
- Bevisst avvik: ingen. Vurdering med 1–5 stjerner følger briefen.

## Skisser av skjermbilder

- ✅ Brødtekst ≥ 18 px og knapper ≥ 48 px høye – erstatter antakelsen om 44 px i NFR-7.
- ✅ Status vises alltid med ord, ikke bare farge – lagt til i NFR-7.
- ✅ Fast meny (Oppdrag · Mine oppdrag · Profil) – lagt til i NFR-8.
- ✅ Oppdragsdetaljer viser oppdragsgiverens navn, fullførte oppdrag og snitt (skisse 3a) – lagt til i FR-9.
- ✅ «Gi tilbakemelding»-merke i Mine oppdrag (skisse 4) – lagt til i FR-18.
- Avvik i skissene (rettes i UX-steget, §9 punkt 1): tallknapper i stedet for stjerner; «Fleksibelt denne uken» som tidspunkt.
- Til UX, ikke PRD: gruppering i Mine oppdrag (Trenger handling / Pågår / Ferdige), avbrutte bak lenke, skjema i to steg, forhåndsvisning av kortet.

## Tilbakemelding fra faglærer (2026-10-06)

- Alle «Endre»-punkter er løst i briefen v2.2 og videreført: ingen BankID/Vipps eller foresatte (§2.2, §7.2), én kjerneflyt, testbare kriterier (FR-konsekvenser), ingen betaling i appen (§6), nærhet via postnummer (FR-10), README/testbrukere/eksempeldata (NFR-1, NFR-2), `.env.example` (NFR-3).

## Sensorveiledning del 1

- Faste krav-ID-er og testbare akseptansekriterier: ja (§0, alle FR).
- Endringslogg: ja.
- ✅ «Appen tåler feil input» – ny NFR-10.
- ✅ Testene kan kjøres etter README, og sensor bruker 15–20 minutter – lagt til i NFR-1.
- ✅ `.gitignore` – lagt til i NFR-3.
- Universell utforming (kontrast, tastatur, alt-tekst, skjemaetiketter, skjermstørrelser) og tomtilstander: NFR-6, NFR-7, FR-10/14/18.
