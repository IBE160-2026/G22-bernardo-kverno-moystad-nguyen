# Sensorveiledning IBE160 – Del 1 (sammendrag)

| | |
|---|---|
| **Kilde** | [sensorveiledning-ibe160-del1.pdf](sensorveiledning-ibe160-del1.pdf) (høst 2026, 7 sider). Ved tvil gjelder PDF-en. |
| **Frist** | Begynnelsen av desember 2026. Sensor vurderer siste commit før fristen; senere endringer telles ikke. |
| **Formål** | Sjekkliste for gruppen og for KI-agenter (BMAD, Claude Code) gjennom hele prosjektet. |

Del 1 (applikasjon og prosess) teller **70 %** av karakteren. Refleksjonsrapporten (del 2) teller 30 %. Sensor vurderer «ikke bare sluttproduktet, men i like stor grad sporene av prosessen» (s. 1), og starter med å lese product brief (tidligere kalt proposal) for å se hva gruppen har lovet å lage (s. 2).

Karakter: hvert kriterium gis A=5 … F=0, og vektet sum gir karakteren. A ≥ 4,5, B ≥ 3,5, C ≥ 2,5, D ≥ 1,5, E ≥ 0,5 (s. 7).

## Kriteriene

| # | Kriterium | Vekt | Hva sensor ser etter |
|---|---|---|---|
| 1 | Prosess og KI-styring | 30 % | BMAD-dokumentene (brief, PRD, arkitektur, epics, stories) er «faktisk brukt og oppdatert, ikke bare generert én gang». Funksjoner kan spores tilbake til krav og stories, og avvik fra planen er forklart. Jevne, små commits med beskrivende meldinger, branches, PR-er og issues. Lagrede prompts og KI-økter som viser at gruppen har presisert krav og avvist, rettet eller forbedret KI-forslag. Teknologi- og arkitekturvalg er begrunnet. A–B: «Prompts og beslutninger er dokumentert og koblet til konkrete endringer.» |
| 2 | Funksjonalitet og omfang | 20 % | Kjerneflytene fra brief og README virker fra start til slutt. Omfang og kompleksitet teller (datalagring, flere roller, ikke-trivielle regler). Appen tåler feil input. Det som er utelatt eller endret, er beskrevet og begrunnet. |
| 3 | Kvalitetssikring og testing | 15 % | Automatiske tester som kan kjøres etter README og tester meningsfull logikk. Dokumenterte manuelle tester og testplaner der automatiske ikke passer. Spor av kodegjennomgang: feil funnet i KI-generert kode og hvordan de ble rettet. Validering, feilhåndtering og sikkerhet. |
| 4 | Design og UX | 10 % | Konsistent uttrykk og tydelig navigasjon. Tydelige tilbakemeldinger, feilmeldinger og tomtilstander. Universell utforming: kontrast, tastaturnavigasjon, alt-tekst, skjemaetiketter, tilpasning til skjermstørrelser. Spor av designarbeid (skisser, wireframes, UX-beskrivelser). |
| 5 | Kodekvalitet og arkitektur | 10 % | Mappestrukturen samsvarer med beskrevet arkitektur. Lite død kode og ingen utkommenterte rester fra KI-forsøk. Gjerne linter/formatterer. |
| 6 | README og kjørbarhet | 10 % | Kort beskrivelse og skjermbilde. Forutsetninger med versjoner. Eksakte kommandoer. `.env.example` uten ekte hemmeligheter. Testdata, testbrukere og hvordan testene kjøres. Mappestruktur og lenker til planleggings- og prosessdokumentasjon. Sensor kjører appen på en ren maskin kun etter README, i inntil 15–20 minutter (s. 2). |
| 7 | Ryddighet i repoet | 5 % | `.gitignore` holder ute node_modules, venv o.l. Ingen hemmeligheter i repoet eller historikken. Ingen løse filer eller sikkerhetskopier i rotmappen. |

Kjører ikke appen, vurderes den ut fra kode, tester, skjermbilder og video. Det trekker tydelig ned på kriterium 6 og begrenser kriterium 2 (s. 2).

## Varseltegn (gir trekk)

- All kode i én eller noen få commits rett før fristen.
- Planleggingsdokumentene beskriver en annen app enn den som er levert, eller er tydelig generert i etterkant.
- README er en uendret mal, eller kommandoene virker ikke.
- API-nøkler, passord eller `.env` er committet.
- node_modules, venv, build-mapper eller store binærfiler i repoet.
- Testene feiler eller tester bare trivielle ting.
- Mye død kode eller rester fra forkastede KI-forsøk.
- KI-dokumentasjonen er generell og kan ikke knyttes til konkrete endringer i repoet.

Ujevn commit-statistikk alene gir ikke trekk (s. 2).

## F-nivå

- Ingen planlegging eller prompts, eller koden er lastet opp ferdig.
- Ingen spor av testing.
- Appen fungerer ikke.
- README mangler, eller appen kan ikke kjøres.
- Ekte hemmeligheter i repoet som ikke er håndtert.

## Hva det betyr for arbeidet vårt

- Krav i PRD-en har faste ID-er som brukes i stories, commits og PR-er.
- Hvert krav har testbare akseptansekriterier.
- PRD og andre BMAD-dokumenter oppdateres når planen endres, med endringslogg.
- KI-økter logges i `.logs/` og knyttes til konkrete commits.
- Små commits gjennom hele perioden, ikke i en klump mot slutten.
