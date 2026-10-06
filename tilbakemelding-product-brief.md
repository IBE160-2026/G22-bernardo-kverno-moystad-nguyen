# Tilbakemelding på product brief

| | |
|---|---|
| **Gruppe** | G22 – G22-bernardo-kverno-moystad-nguyen |
| **Product brief** | `Product-brief-nabolagshelten.md` (commit `452dcef`) |
| **Tilbakemelding fra** | Faglærer i IBE160 (utarbeidet med KI-støtte) |
| **Dato** | 2026-10-06 |

## Samlet vurdering

- **Bør revideres før dere går videre.** Rett punktene markert «Endre» før dere lager PRD og arkitektur.

**Det som er bra:**

1. Ideen er lett å forstå, og problemet er godt beskrevet. Hverdagsoppgaver som er for små for et firma, blir i dag løst tilfeldig i Facebook-grupper og på Finn. Eksemplene («måke innkjørselen i morgen tidlig», «sette opp en ny iPad») gjør brukssituasjonen konkret.
2. Dere har en tydelig «Ikke inkludert»-liste (ikke jobbportal, ikke bemanningsplattform, ikke markedsplass for håndverkere osv.). Den hjelper med å holde produktet avgrenset.
3. To tydelige brukergrupper, oppdragsgivere og oppdragstakere, og en fin idé om at fullførte oppdrag kan gi dokumentert erfaring til CV-en.

**De viktigste endringene:**

1. **Fjern BankID/Vipps-verifisering og godkjenning fra foresatte fra v1.** Ekte BankID- eller Vipps-innlogging krever avtaler, testmiljø og godkjenning som en studentgruppe ikke får i løpet av semesteret. Sensor kan heller ikke kjøre det lokalt. Bruk vanlig innlogging med e-post og passord, og beskriv verifisering som en fremtidig utvidelse. Godkjenning fra foresatte gir en ekstra rolle og en egen flyt. Det enkleste er å sette 18-årsgrense i v1.
2. **Begrens v1 til én kjerneflyt.** Briefen har to produkter i v1: småoppdrag og utlån av utstyr. Legg utlån i «senere» og bli ferdig med flyten for oppdrag: legge ut → melde interesse → velge hjelper → markere som utført → gi tilbakemelding.
3. **Skriv suksesskriterier som kan testes.** Kriteriene er i dag ønsker («raskt kunne beskrive behovet», «sterkere kontakt mellom naboer»). Skriv dem som «en oppdragsgiver kan legge ut et oppdrag med kategori og sted, og det vises i oversikten for brukere i samme område».

## Vanskelighetsgrad og gjennomførbarhet

### Vurdert vanskelighetsgrad

- **Middels**

**Sammenlignbart med:** 2) AI CV- og søknadsassistent (middels) i omfang. Nabolagshelten har ikke KI som kjerne, men flere brukere med ulike roller, personopplysninger og en flyt der brukere påvirker hverandre. Med BankID/Vipps og foresattgodkjenning slik briefen beskriver, ville prosjektet nærme seg vanskelig, men av grunner som ikke gir mye læring i dette emnet.

**Begrunnelse:**

| Faktor | Nivå (lav / middels / høy) | Kommentar |
|---|---|---|
| Domenelogikk – hvor mange og hvor kompliserte regler og beregninger må stemme? | middels | Statusene for et oppdrag (åpent, interesse meldt, hjelper valgt, utført), hvem som kan gjøre hva, og eventuelt utlånsperioder. |
| Datamodell – antall entiteter og relasjoner mellom dem | middels | Bruker, profil, oppdrag, kategori, interesse, tilbakemelding og utstyr/utlån. Med utlån blir det mange relasjoner. |
| Brukere, roller og innlogging | høy | Oppdragsgiver, oppdragstaker, foresatt og BankID/Vipps. Med vanlig innlogging og 18-årsgrense blir dette middels. |
| KI-funksjonalitet i appen, f.eks. kall til språkmodell, prompts i koden og håndtering av usikre svar | lav | Ingen KI er beskrevet. Det er greit. Hvis dere vil ha KI, kan en avgrenset funksjon være forslag til kategori og pris ut fra oppdragsteksten. |
| Integrasjoner og eksterne tjenester, f.eks. API-er, betaling og e-post | høy | BankID/Vipps er en tung integrasjon. Kart og geografisk matching er utsatt, men «lokal tilhørighet» må likevel løses, for eksempel med postnummer. |
| Sanntid, samtidighet eller flere brukere som påvirker hverandre | middels | Flere brukere melder interesse på samme oppdrag, og oppdragsgiveren velger én. Ingen sanntidschat i v1, og det er bra. |
| Filhåndtering, f.eks. opplasting, PDF-lesing og eksport | lav | Ikke nevnt. Bilder av utstyr kan bli aktuelt ved utlån. |
| Sikkerhet og personvern | høy | Navn, adresse/område, alder og vurderinger av personer. Mindreårige brukere gjør dette ekstra sensitivt. |

**Hva vanskelighetsgraden betyr for dere:**

- _Middels:_ Et godt balansert valg. Pass på at kjerneflyten blir ferdig og stabil før dere legger til mer. For dere betyr det oppdragsflyten med vanlig innlogging før utlån og verifisering.

### Gjennomførbarhet med BMAD og Claude Code

Dere skal planlegge med BMAD (product brief → PRD → arkitektur → epics og stories) og implementere med Claude Code. Vurderingen under tar hensyn til at det må være tid til hele denne flyten, og til testing, retting og README til slutt.

| Spørsmål | Vurdering (OK / risiko / stor risiko) | Kommentar |
|---|---|---|
| **Tid og omfang** – kan v1 realistisk bli ferdig og stabil i løpet av semesteret, med tid til flere iterasjoner? | risiko | Oppdrag, profiler med historikk og tilbakemeldinger, utlån, BankID/Vipps og foresattgodkjenning er for mye. Uten verifisering og utlån er det realistisk for en gruppe på fire. |
| **BMAD-flyten** – er briefen konkret nok til at PRD, arkitektur og stories kan lages uten store hull, og blir det overkommelig mange stories? | risiko | Mange viktige valg er skjøvet til «senere BMAD-faser» (betaling, geografisk matching, sikkerhet, aldersgrense). Avklar i alle fall om det skal være betaling i appen (anbefaling: nei) og hvordan «i nærheten» skal fungere. |
| **Egnet for Claude Code** – bruker løsningen en vanlig, godt dokumentert teknologistakk som Claude Code håndterer godt, eller krever den nisjeteknologi, spesialmaskinvare eller mye manuell konfigurasjon? | OK | En vanlig webapp med database og innlogging passer godt for Claude Code. BankID/Vipps er unntaket. |
| **Kontroll på KI-ens arbeid** – kan gruppen selv avgjøre om koden gjør det riktige? Krever domenet kunnskap gruppen ikke har, f.eks. avanserte beregninger eller fagregler, så er det vanskelig å kvalitetssikre. | OK | Reglene er enkle å forstå, og dere kan selv sjekke om riktig person ser riktige oppdrag. |
| **Testbarhet** – finnes det tydelige regler og forventede resultater som tester kan skrives mot? | risiko | Det finnes gode testbare regler (bare oppdragsgiver kan velge hjelper, bare valgt hjelper kan markere utført osv.), men de står ikke i briefen. Skriv dem inn. |
| **Kjørbar for sensor** – kan appen kjøres lokalt etter README, uten gruppens nøkler, betalte kontoer eller egen infrastruktur? | stor risiko | Med BankID/Vipps kan sensor ikke logge inn. Med vanlig innlogging og testbrukere i README blir dette OK. |
| **Avhengigheter og kostnader** – krever løsningen betalte API-er, f.eks. språkmodeller, og finnes det en plan for kostnad, testmodus eller mock-data? | risiko | BankID/Vipps koster og krever avtale. Ellers trengs ingen betalte tjenester. Lag eksempeldata med noen naboer og oppdrag. |

**Konklusjon om gjennomførbarhet:**

- **Gjennomførbart med justert omfang.** Se forslagene under.

**Forslag til justering av omfang eller vanskelighetsgrad:**

1. **V1:** vanlig innlogging, profil, legge ut oppdrag med kategori og område (postnummer eller bydel), liste og filter over oppdrag i eget område, melde interesse, velge hjelper, markere utført og gi tilbakemelding som vises i profilen.
2. **Senere trinn:** utlån av utstyr, kart, BankID/Vipps-verifisering og foresattgodkjenning. Hvis dere vil ha en KI-funksjon, er automatisk forslag til kategori eller tydeligere oppdragstekst en avgrenset og testbar utvidelse.

## Hvorfor product brief er viktig for mappen

Product brief er utgangspunktet for PRD, arkitektur, stories og til slutt koden. Del 1 av mappen vurderes blant annet på om sensor kan følge en sporbar vei fra plan til ferdig app. Den vurderes også på om appen gjør det dere har beskrevet, om den er testet, om den er godt designet, og om den kan kjøres etter README. Et uklart, for stort eller for lite brief gjør alt dette vanskeligere senere. Det er mye enklere å rette nå enn sent i semesteret.

## 1. Gjennomgang av briefens deler

| Del av brief | Status | Kommentar |
|---|---|---|
| Executive Summary – er det klart hva appen er, og hvilket problem den løser? | OK | Det er tydelig at dette er en lokal plattform for småoppdrag og deling, med en klar kjerneidé. |
| The Problem – er problemet konkret, med reelle situasjoner og brukere? | OK | Gapet mellom små behov og folk som kan hjelpe er godt beskrevet. Det ville styrket briefen å ha med ett eller to eksempler fra virkeligheten, for eksempel fra egne nabolag. |
| The Solution – beskriver løsningen brukeropplevelsen, ikke bare teknologi? | Juster | Brukeropplevelsen er beskrevet, men det mangler hva som skjer etter at noen har meldt interesse: hvordan velges hjelper, hvordan avtales tid, og hvordan markeres oppdraget som utført? |
| What Makes This Different – er vurderingen ærlig og realistisk? | Juster | Punktene er gode, men «Tillit og trygghet» lover BankID/Vipps, som ikke er realistisk i v1. Vurder også hvordan dere skiller dere fra eksisterende tjenester for småjobber. |
| Who This Serves – er primærbrukerne tydelige, og vet vi hva de trenger? | Juster | To grupper er nevnt, men begge er brede («eldre, barnefamilier, travle personer»). Velg én typisk oppdragsgiver og én typisk oppdragstaker å designe for. Hvis eldre er en viktig målgruppe, må designet ta hensyn til det. |
| Success Criteria – kan kriteriene faktisk sjekkes eller testes? | Endre | Kriteriene er ønsker og samfunnsmål som ikke kan måles i emnet. Legg til funksjonelle kriterier som kan bli testtilfeller. |
| Scope – er det klart hva som er med i første versjon, og hva som ikke er det? | Endre | V1 inneholder både oppdrag og utlån, BankID/Vipps og foresattgodkjenning. Viktige valg som betaling og geografisk matching står som uavklart. |
| Vision – henger visjonen sammen med resten uten å blåse opp omfanget? | OK | Visjonen er tydelig og henger sammen med problemet. |

## 2. Utgangspunkt for del 1 av mappen

Punktene følger kriteriene i sensorveiledningen for del 1. Vektene i parentes viser hvor mye hvert kriterium teller i del 1.

| Kriterium i del 1 | Hva briefen bør legge til rette for | Status | Kommentar |
|---|---|---|---|
| **1. Prosess og KI-styring** (30 %) | Brief som er presis nok til at PRD og stories kan bygges direkte på den, slik at krav kan spores fra brief til kode. | Juster | Briefen er lastet opp i én commit uten BMAD-oppsett i repoet. Kjør BMAD-flyten i repoet videre, slik at PRD, arkitektur og stories bygger på briefen og historikken viser utviklingen. |
| **2. Funksjonalitet og omfang** (20 %) | Realistisk omfang for gruppen og semesteret: en tydelig kjerneflyt som kan bli ferdig og stabil, og nok innhold til å vise reell funksjonalitet. | Endre | Velg oppdragsflyten som kjerne og kutt verifisering og utlån fra v1. |
| **3. Kvalitetssikring og testing** (15 %) | Suksesskriterier og funksjoner som er konkrete nok til å bli testtilfeller. | Endre | Skriv inn regler og funksjonelle kriterier som kan testes, særlig hvem som får se og endre hva. |
| **4. Design og brukeropplevelse** (10 %) | Tydelige brukere og brukssituasjoner som designet kan bygges rundt, gjerne med de viktigste skjermbildene eller flytene skissert. | Juster | Skisser de 4–5 viktigste skjermbildene: oppdragsliste, nytt oppdrag, oppdragsdetaljer, profil. Tenk på eldre brukere og mobil. |
| **5. Kodekvalitet og arkitektur** (10 %) | Teknologivalg som er begrunnet og ikke mer komplekse enn appen trenger. | OK | Teknologivalg er bevisst utsatt. En vanlig webstakk med én database holder. |
| **6. README og kjørbarhet** (10 %) | Løsning som andre kan kjøre lokalt uten betalte kontoer, og uten tilgang til gruppens egne tjenester og nøkler. | Endre | BankID/Vipps hindrer lokal kjøring. Planlegg vanlig innlogging, testbrukere og eksempeldata som følger med repoet. |
| **7. Ryddighet i repoet** (5 %) | En plan for hvor hemmeligheter, testdata og dokumentasjon skal ligge. | Juster | Briefen ligger i rotmappen. Flytt planleggingsdokumentene til en egen mappe (for eksempel BMADs `_bmad-output/`), og planlegg `.env.example` uten ekte nøkler. |

## 3. Neste steg for gruppen

1. Oppdater Scope: flytt BankID/Vipps, foresattgodkjenning og utlån til «senere», og bestem at det ikke skal være betaling i v1 og at «nærhet» løses med for eksempel postnummer.
2. Skriv 6–8 funksjonelle suksesskriterier i formen «en bruker kan …», inkludert regler for hvem som kan velge hjelper og markere et oppdrag som utført.
3. Installer BMAD i repoet, flytt briefen inn i planleggingsmappen og lag PRD ut fra den reviderte briefen.

Oppdater product brief i repoet når dere har gjort endringene, slik at historikken viser hvordan planen utviklet seg. Det er en del av prosessen sensor ser etter.
