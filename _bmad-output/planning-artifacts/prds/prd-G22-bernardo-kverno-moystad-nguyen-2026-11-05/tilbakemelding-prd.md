# Tilbakemelding på PRD

| | |
|---|---|
| **Gruppe** | G22 – G22-bernardo-kverno-moystad-nguyen |
| **PRD vurdert** | `_bmad-output/planning-artifacts/prds/prd-G22-bernardo-kverno-moystad-nguyen-2026-11-05/prd.md` (status: final, sist endret 2026-11-07, commit 810be54) |
| **Dato** | 2026-11-12 |
| **Type** | Formativ tilbakemelding, ikke karakter |

## 1. Samlet inntrykk

Dette er en sterk PRD som er lett å bruke videre. Kjerneflyten er tydelig, kravene har faste ID-er med testbare konsekvenser, og avviket fra briefen er begrunnet. Hovedrisikoen er ikke kvalitet, men størrelse: 26 FR-er og 12 NFR-er (ca. 9 600 ord), der nesten alt er «Må». Det kan bli tungt å få ferdig og lett å miste oversikten i.

## 2. Dette fungerer godt

- **Testbare konsekvenser med grenseverdier.** FR-1 har «Den som fyller 18 i dag, godtas», og FR-5 har tittel 3–80 tegn og godtgjørelse 1–10 000 kr. Hvert krav kan bli akseptansekriterier nesten uendret.
- **Statusmodell og «Mine oppdrag» er gjort eksplisitte.** Tabellen i §4.0 og raden-for-rad-tabellen i FR-18 («Hvert oppdrag passer i nøyaktig én rad») fjerner gjetting for UX, arkitektur og tester.
- **KI-funksjonen er kontrollert.** FR-25 validerer svaret (gyldig JSON, kjent kategori, lengdegrenser), har tidsavbrudd på 10 sekunder og testes med en testdobbel. FR-26 gir deterministisk mock-modus, og NFR-1 sier at appen virker uten nøkkel. Det er nettopp det emnet ber om.
- **Ærlighet om begrensninger.** «Kjent begrensning – erfaringen er ikke verifisert» (§4.7) og «Glemt passord» (§6.2) sier rett ut hva v1 ikke løser.

## 3. Oversikt per dimensjon

| Dimensjon | Vurdering | Kort begrunnelse |
|---|---|---|
| Beslutningsklarhet | sterk | Valg og avvik står i §9.2 med begrunnelse (for eksempel at oppdragsgiver kan markere Utført, avvik fra R7). |
| Substans | sterk | Personaene Kari og Amir styrer faktiske krav, og NFR-ene har tall og «Testes ved». Ingen pynt. |
| Strategisk sammenheng | god | Tesen («småjobber blir dokumentert erfaring som bygger tillit») er klar, men suksessmålene måler fullføring, ikke tesen. |
| Testbarhet | sterk | Så godt som alle FR-er har målbare konsekvenser. Svakest er den manuelle KI-testen i FR-24. |
| Scope og avgrensning | god | §6.2–6.3 og kuttreglene i §6.1 er ryddige, men «Må» er veldig stort for fire personer. |
| Brukbarhet for neste fase | sterk | ID-er er sammenhengende (FR-1–26, NFR-1–12, SM-1–5, UJ-1–2), og sporingen til brief står i §9.1. |
| Formtilpasning | god | Passer et produkt med flere roller. Noen steder er PRD-en mer algoritmebeskrivelse enn krav (FR-26). |

## 4. Viktigste forbedringer

### 4.1 «Må» er for stort til å være en prioritering
- **Alvorlighet:** medium
- **Hvor:** §6.1: «Må | FR-1–FR-21, NFR-1–NFR-12»
- **Problem og hvorfor det betyr noe:** 21 FR-er og 12 NFR-er er «Må». Blant dem er innloggingssperre (FR-2), kontosletting med ti-radstabell (FR-4), tilgjengelighetstest med skjermleser (NFR-7) og skanning av git-historikk (NFR-3). Blir tiden knapp, finnes det ingen rekkefølge innenfor «Må», og epics/stories får ingen naturlig første leveranse.
- **Forslag:** Del «Må» i to. Eksempel: **Må-A (første skive):** FR-1, FR-2, FR-3, FR-5, FR-10, FR-12, FR-14, FR-15, FR-16, FR-19, FR-20, FR-21, NFR-1, NFR-2, NFR-4, NFR-5. **Må-B (herding):** FR-4, FR-6, FR-7, FR-13, FR-17, FR-18, resten av NFR-ene. Da kan første epic være «UJ-2 uten feilgrener», og dere ser tidlig om fremdriften holder.

### 4.2 Suksessmålene måler ferdigstilling, ikke tesen
- **Alvorlighet:** medium
- **Hvor:** §7: «SM-1: Alle krav FR-1–FR-26 … er dekket av akseptansekriterier i stories»; «SM-C1 … Måles ikke»
- **Problem og hvorfor det betyr noe:** SM-1–SM-3 sier om dere er ferdige, ikke om ideen virker. Tesen er tillit og dokumentert erfaring, men ingen SM prøver om profilen faktisk gir det. Motmålet SM-C1 «måles ikke», så det styrer ingenting.
- **Forslag:** Legg til et sekundært mål, for eksempel: «**SM-6:** I brukertesten (SM-4) får testpersonene se Amirs profil fra eksempeldataene. Minst to av tre forklarer riktig hva profilen viser og at den ikke er verifisert. Validerer FR-21.» Gjør SM-C1 målbart ved å telle andelen eksempeloppdrag/testoppdrag laget med forslag, og noter tallet i testrapporten uten mål.

### 4.3 PRD-en er lang og blander krav med algoritmer
- **Alvorlighet:** medium
- **Hvor:** FR-26 (mock-regler, tittel- og punktumsalgoritme), §9.2 (31 rader), §4.0 («Definition of Done» står i §5-innledningen uten å være forklart)
- **Problem og hvorfor det betyr noe:** Ved ca. 9 600 ord er det vanskelig å se helheten, og de som skal skrive stories må lete. Detaljnivået i FR-26 hører mer hjemme i en spesifikasjon eller testtabell enn i et krav.
- **Forslag:** Flytt nøkkelordtabellen og tittelregelen til `addendum.md`, og la FR-26 si: «Samme tekst gir alltid samme svar; kategori velges med nøkkelordtabellen i addendumet; tabellen testes med eksemplene der.» Legg inn en oversikt øverst i §4 (feature → FR-er → prioritet). Forklar «Definition of Done» i ordlisten eller bytt til «ferdig-kriterier».

### 4.4 Manuell KI-test og KI-kostnad er ikke helt avgrenset
- **Alvorlighet:** lav
- **Hvor:** FR-24: «Testes manuelt med fem faste eksempeltekster mot språkmodellen, og resultatet dokumenteres»; FR-23: «høyst 20 forslag per bruker per time»
- **Problem og hvorfor det betyr noe:** Det står ikke når testen er bestått, så den kan ikke bli en story med klart ferdig-kriterium. Grensen per bruker begrenser ikke samlet kostnad hvis mange tester samtidig.
- **Forslag:** «Bestått når ingen av de fem forslagene inneholder tall, navn eller opplysninger som ikke står i teksten, kategorien er riktig i minst fire av fem, og alt er på bokmål. Resultatet føres i en tabell i testrapporten.» Legg til: «Totalt høyst 200 KI-kall per døgn; ved overskridelse vises meldingen i FR-25.»

## 5. Mekaniske funn

- ID-ene er sammenhengende og unike. Krysshenvisningene jeg sjekket, løser seg (FR/NFR/SM/R/SK).
- Ordlisten brukes konsekvent. «Oppdragstaker» fra briefen er bevisst byttet til «hjelper».
- Ingen `[ASSUMPTION]`-merker og ingen antakelsesliste. §9.2 sier at ingen antakelser står åpne, og det stemmer med innholdet.
- Flere FR-er har «—» i brukerreise (FR-2, FR-3, FR-4, FR-11, FR-13, FR-22, FR-26). Det er greit, men UJ-1 og UJ-2 viser at sletting, redigering av profil og trekking av interesse ikke er prøvd i noen reise.
- UJ-1 viser ikke hva Kari ser når KI-forslaget feiler. Én setning under «Når noe går galt» ville koblet UJ-1 til FR-25.

## 6. Før dere går videre

**Må avklares før UX/arkitektur/epics:**
- Hvilke krav som er første skive (4.1), slik at epics får en rekkefølge.
- Hva som skal gjøre at dere kutter KI-delen (FR-23–26), og når dere avgjør det. Beslutningsdato i planen er nok.

**Kan vente:**
- Målbare SM-er (4.2), flytting av detaljer til addendum (4.3) og ferdig-kriterium for KI-testen (4.4).
- Punktene i §8 («UX-steget oppdaterer skissene», postnummerkilde, sommertid) er riktig plassert til neste fase.

**Oppfølging av briefen:** ja. BankID/Vipps, foresattgodkjenning og utlån er flyttet til «utsatt» (§6.2). V1 har én kjerneflyt, 18-årsgrense, postnummer som nærhet og ingen betaling. Reglene R1–R13 og SK1–SK10 er blitt testbare krav. KI er en avgrenset funksjon med mock-modus, og NFR-1/NFR-2 sikrer kjøring og eksempeldata for sensor.

## 7. Refleksjonsspørsmål

1. Mange regler i FR-ene (som «29. februar» i FR-1 og tittelalgoritmen i FR-26) er svært detaljerte. Hvilke av dem kom fra dere, og hvilke fikk dere fra KI-en? Hvordan sjekket dere at de er riktige og ikke bare plausible?
2. Når dere nå ser hele PRD-en: hvis dere bare fikk bygge halvparten, hvilke krav ville dere ha beholdt, og hva sier det om hva som egentlig er kjernen i Nabolagshelten?

_Vurdert mot kvalitetsrubrikken i bmad-prd. Dette er veiledning, ikke sensur._
