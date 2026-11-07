---
title: PRD – Nabolagshelten
status: final
created: 2026-11-05
updated: 2026-11-07
---

# PRD – Nabolagshelten

| | |
|---|---|
| **Gruppe** | G22 – Bernardo, Kverno, Møystad, Nguyen |
| **Versjon** | 1.0 (ferdig) |
| **Bygger på** | [Product brief v2.2](../../product-brief-nabolagshelten.md) (= «proposal» i sensorveiledningen), [skisser av skjermbilder](../../skisser-skjermbilder.md) |

## 0. Om dokumentet

PRD-en beskriver *hva* versjon 1 (v1) av Nabolagshelten skal gjøre, slik at gruppen kan lage arkitektur, epics og stories fra den. Den er skrevet for gruppen, faglærer og sensor.

- **Briefen er fasit.** PRD-en gjør briefens regler (R1–R13) og suksesskriterier (SK1–SK10) om til krav med faste ID-er (sporingstabell i §4). Der briefen ikke avgjør noe, har gruppen tatt et valg. Alle slike presiseringer og tillegg står med begrunnelse i §10.
- **Faste ID-er.** Brukerreiser heter UJ-N, funksjonelle krav FR-N, kvalitetskrav NFR-N og suksessmål SM-N. ID-ene endres ikke selv om rekkefølgen endres, og de skal brukes i stories, commits og PR-er.
- **Testbare krav.** Hvert krav har konsekvenser som kan bli akseptansekriterier og automatiske eller manuelle tester.
- **Ordlisten (§3) er bindende.** Begrepene brukes likt i hele dokumentet og i koden der det er naturlig.
- Teknologivalg hører hjemme i arkitekturdokumentet, ikke her.
- Endringer etter at PRD-en er ferdig, føres i endringsloggen nederst.

## 1. Visjon

Nabolagshelten er en webapp som kobler personer som trenger hjelp til små, praktiske hverdagsoppgaver – snømåking, gressklipping, bærehjelp, hundelufting, teknologihjelp – med naboer i samme postnummer som har tid til å hjelpe.

V1 har én kjerneflyt: legge ut et oppdrag → melde interesse → velge hjelper → markere som utført → gi tilbakemelding. Fullførte oppdrag og tilbakemeldinger samles i hjelperens profil, slik at småjobber blir dokumentert erfaring som kan brukes i en jobbsøknad. En avgrenset KI-funksjon hjelper oppdragsgiveren å formulere oppdraget, men appen fungerer fullt ut uten KI.

I dag løses slike behov tilfeldig via Facebook-grupper, Finn eller bekjente. Der er det uklart hvem som tar jobben, om oppdraget fortsatt er ledig og om personen er til å stole på. Nabolagshelten gir tydelig status, lokal oversikt og en historikk som bygger tillit.

## 2. Målgruppe

### 2.1 Behov (jobs to be done)

- **Oppdragsgiver (Kari):** Få hjelp til en liten oppgave i nærheten uten å ringe rundt, og kunne velge noen hun føler seg trygg på. Legge ut et oppdrag på under to minutter.
- **Hjelper (Amir):** Raskt finne ledige oppdrag i nærheten, forstå hva de innebærer og betaler, og samle dokumentert erfaring og tilbakemeldinger til CV-en.
- **Begge:** Se tydelig om et oppdrag er ledig, tatt eller utført. Samme person kan være oppdragsgiver én dag og hjelper neste – det finnes ikke egne kontotyper.

Andre grupper (barnefamilier, travle personer, arbeidsledige) har de samme behovene og dekkes av den samme flyten.

### 2.2 Ikke målgruppe i v1

- Personer under 18 år (krever godkjenning fra foresatte; utsatt).
- Firmaer, håndverkere og større eller komplekse oppdrag.

### 2.3 Brukerreiser

**UJ-1. Kari får måkt innkjørselen uten å ringe rundt.**

- **Person og situasjon:** Kari, 72 år, bor alene i rekkehus. En mandag morgen i januar har det snødd mye i løpet av natten, og hun orker ikke å måke selv. Hun bruker nettbrett, men gir opp hvis noe er uoversiktlig.
- **Utgangspunkt:** Hun har allerede konto og er innlogget på nettbrettet. Hun starter på oppdragsoversikten.
- **Veien:**
  1. Hun trykker «Legg ut oppdrag» og skriver med egne ord i beskrivelsesfeltet: «Trenger noen som kan måke snø i innkjørselen min i morgen.»
  2. Hun trykker «Få forslag». KI-en foreslår tittel, kategori (Snømåking) og en bedre beskrivelse, og hun trykker «Bruk» på forslagene.
  3. Hun ser at postnummeret er forhåndsutfylt og riktig, velger tidspunkt, legger inn 200 kr i godtgjørelse og trykker «Publiser». Oppdraget får status **Åpen** og blir synlig for brukere i samme postnummer.
  4. Senere samme dag går hun til «Mine oppdrag», ser at to har meldt interesse, og åpner oppdraget. For hver av de interesserte ser hun navn, antall fullførte oppdrag, gjennomsnittlig vurdering og meldingen deres.
  5. Hun velger den hun føler seg tryggest på. Status blir **Hjelper valgt**, og de ser hverandres telefonnummer, så de kan avtale detaljene direkte.
- **Vendepunktet:** Kari kan sammenligne de interesserte på erfaring og vurderinger før hun velger. Det er det som gjør at hun føler seg trygg.
- **Avslutningen:** Neste dag måker hjelperen innkjørselen, og Kari betaler 200 kr med Vipps utenfor appen. Hjelperen markerer oppdraget som **Utført**. Kari gir fem stjerner og en kort kommentar, som vises i hjelperens profil. Hun fikk hjelp uten å ringe rundt og uten innlegg på Facebook.
- **Når noe går galt:**
  - *Ingen melder interesse:* Kari ser fortsatt oppdraget under «Mine oppdrag» med status **Åpen**. Hun kan redigere tidspunktet eller godtgjørelsen for å gjøre det mer attraktivt.
  - *Tidspunktet passerer uten hjelper:* Oppdraget forsvinner fra oversikten og kan ikke få nye interesser. Under «Mine oppdrag» er det merket «Tidspunktet er passert», og Kari kan endre tidspunktet eller avbryte oppdraget.

**UJ-2. Amir gjør småjobber og bygger en profil han kan vise til.**

- **Person og situasjon:** Amir, 21 år, student. Vil tjene litt ekstra ved siden av studiene og få erfaring å vise til når han søker sommerjobb. Har tid på ettermiddager og i helger.
- **Utgangspunkt:** En ettermiddag hører han om Nabolagshelten og åpner nettsiden på mobilen. Han har ingen konto.
- **Veien:**
  1. Han registrerer seg med navn, e-post, telefonnummer, postnummer, fødselsdato og passord. Han er over 18 år, så kontoen opprettes og han logger inn.
  2. Oppdragsoversikten viser åpne oppdrag i hans postnummer, sortert etter tidspunkt. Han ser et oppdrag i kategorien Bærehjelp/flytting på lørdag, med godtgjørelse 400 kr. Han har fri den dagen.
  3. Han åpner oppdraget, leser beskrivelsen, skriver en melding – «Hei! Jeg kan gjerne hjelpe deg på lørdag. Jeg har erfaring med å bære møbler fra tidligere flyttinger.» – og trykker «Meld interesse».
  4. Senere går han til «Mine oppdrag», fanen «Oppdrag jeg hjelper med», og ser at oppdragsgiveren har valgt ham. Status er **Hjelper valgt**, og han ser oppdragsgiverens telefonnummer, så de kan avtale detaljene direkte.
  5. På lørdag bærer han møblene. Etterpå markerer han oppdraget som **Utført**, og får 400 kr med Vipps utenfor appen.
- **Vendepunktet:** Oppdragsgiveren gir ham fem stjerner og en kommentar om at han møtte presis og gjorde en god jobb. Amir ser at det fullførte oppdraget og vurderingen nå står i profilen hans.
- **Avslutningen:** Amir gir også oppdragsgiveren en vurdering, siden begge parter kan gi tilbakemelding. Etter hvert som han tar flere oppdrag, viser profilen antall fullførte oppdrag per kategori, gjennomsnittlig vurdering og tilbakemeldinger. Når han søker sommerjobb, viser han til profilen som dokumentasjon på praktisk erfaring.
- **Når noe går galt:**
  - *Oppdragsgiveren velger en annen:* Under «Mine oppdrag» ser Amir bare tittel og status for oppdraget, ikke detaljene. Han fortsetter å se etter andre åpne oppdrag i nærheten.
  - *Han kan ikke likevel:* Mens status er **Hjelper valgt**, trykker han «Trekk meg» og bekrefter. Oppdraget får status **Åpen** igjen, telefonnumrene skjules, og oppdragsgiveren kan velge blant de andre interesserte.

## 3. Ordliste

- **Bruker** – En person med konto. Alle brukere kan både legge ut oppdrag og hjelpe; det finnes ikke egne kontotyper.
- **Innlogget bruker** – En bruker med aktiv innlogging. Alt innhold i appen krever innlogging (FR-3).
- **Oppdrag** – En liten, praktisk oppgave som en oppdragsgiver trenger hjelp til. Har feltene tittel, beskrivelse, kategori, postnummer, tidspunkt og godtgjørelse, og har til enhver tid nøyaktig én status.
- **Oppdragsgiver** – Brukeren som har lagt ut et oppdrag. Ett oppdrag har én oppdragsgiver.
- **Hjelper** – En bruker som melder interesse for eller utfører oppdrag for andre. Samme rolle som «oppdragstaker» i briefen; PRD-en bruker bare «hjelper».
- **Interesse** – En hjelpers melding om at hen vil ta et oppdrag, eventuelt med en kort melding til oppdragsgiveren. Maks én interesse per bruker per oppdrag.
- **Interessert** – En bruker som har en aktiv interesse på et oppdrag.
- **Valgt hjelper** – Den ene interesserte som oppdragsgiveren har valgt. Et oppdrag har null eller én valgt hjelper.
- **Status** – Tilstanden til et oppdrag: **Åpen**, **Hjelper valgt**, **Utført** eller **Avbrutt**. Utført og Avbrutt er endelige.
- **Utgått oppdrag** – Et oppdrag med status Åpen der tidspunktet er passert. Ikke en egen status.
- **Kategori** – Én fra den faste listen: Snømåking, Hage, Bærehjelp/flytting, Dyrepass, Teknologihjelp, Annet.
- **Godtgjørelse** – Det oppdragsgiveren tilbyr: et heltall fra 1 til 10 000 kr, eller «uten betaling». Betales utenfor appen.
- **Tidspunkt** – Ønsket dato og klokkeslett for oppdraget.
- **Oppdragsoversikt** – Startsiden med åpne oppdrag, med filter på kategori og postnummer.
- **Mine oppdrag** – Siden med fanene «Oppdrag jeg har lagt ut» og «Oppdrag jeg hjelper med».
- **Tilbakemelding** – En vurdering (1–5 stjerner) og en valgfri kommentar fra én part i et utført oppdrag til den andre.
- **Profil** – Det andre brukere ser om en bruker: navn, postnummer, «om meg» (hvis utfylt), antall fullførte oppdrag per kategori, gjennomsnittlig vurdering og mottatte tilbakemeldinger. Aldri telefonnummer, e-post eller fødselsdato.
- **Fullført oppdrag** – Et oppdrag med status Utført, telt for den som var valgt hjelper.
- **KI-forslag** – Forslag til kategori, tittel og beskrivelse som en språkmodell lager fra teksten i beskrivelsesfeltet.
- **Mock-modus** – Innebygd erstatning for språkmodellen som brukes når ingen API-nøkkel er satt. Gir alltid samme svar for samme tekst.
- **Slettet bruker** – Visningsnavnet for en bruker som har slettet kontoen sin, i oppdrag og tilbakemeldinger som beholdes.

## 4. Funksjoner

Statusmodellen som FR-ene bygger på:

| Fra | Til | Hvem | Krav |
|---|---|---|---|
| (nytt) | Åpen | Oppdragsgiver legger ut | FR-5 |
| Åpen | Hjelper valgt | Oppdragsgiver velger hjelper | FR-15 |
| Hjelper valgt | Åpen | Oppdragsgiver fjerner hjelper, eller valgt hjelper trekker seg | FR-17 |
| Hjelper valgt | Utført | Valgt hjelper | FR-19 |
| Åpen / Hjelper valgt | Avbrutt | Oppdragsgiver | FR-7 |

Alle regler for hvem som kan gjøre hva, håndheves på serveren (NFR-5). «Avvises» betyr i hele dokumentet: handlingen utføres ikke, ingen data endres, og brukeren får en forståelig melding.

Sporing fra briefen til kravene i PRD-en:

| Regel i briefen | Innhold (kort) | Krav |
|---|---|---|
| R1 | Innlogging kreves | FR-3 |
| R2 | Ikke interesse på eget oppdrag | FR-12 |
| R3 | Én interesse per oppdrag; melde og trekke bare når Åpen og ikke utgått | FR-12, FR-13 |
| R4 | Bare oppdragsgiver redigerer (Åpen) og avbryter (Åpen, Hjelper valgt) | FR-6, FR-7 |
| R5 | Bare oppdragsgiver velger nøyaktig én interessert, bare når Åpen | FR-15 |
| R6 | Fjerne hjelper eller trekke seg → Åpen | FR-17 |
| R7 | Bare valgt hjelper markerer Utført | FR-19 |
| R8 | Tilbakemelding: bare Utført, bare partene, én gang | FR-20 |
| R9 | Hvem ser detaljer, interesserte og profiler | FR-9, FR-14, FR-18, FR-21 |
| R10 | Når telefonnummer vises | FR-16 |
| R11 | 18-årsgrense | FR-1 |
| R12 | KI endrer aldri oppdrag; bare beskrivelsen sendes | FR-23, FR-24 |
| R13 | Bare brukeren selv sletter konto | FR-4 |

| Suksesskriterium i briefen | Krav |
|---|---|
| SK1 Registrering og innlogging | FR-1, FR-2, FR-4 |
| SK2 Legge ut og endre oppdrag | FR-5, FR-6, FR-7 |
| SK3 Finne oppdrag | FR-8, FR-10, FR-11 |
| SK4 Melde og trekke interesse | FR-12, FR-13, FR-14 |
| SK5 Velge hjelper | FR-15, FR-16 |
| SK6 Bytte hjelper | FR-17 |
| SK7 Fullføre oppdrag | FR-19 |
| SK8 Tilbakemelding | FR-20 |
| SK9 Dokumentert erfaring | FR-21 |
| SK10 KI-forslag | FR-23, FR-24, FR-25, FR-26 |

FR-18 (Mine oppdrag) og FR-22 (Redigere egen profil) kommer fra briefens skjermbilder og profilbeskrivelse, ikke fra en egen regel.

### 4.1 Konto og innlogging

Alle må ha konto for å bruke appen. Registrering krever at brukeren er minst 18 år (egenerklært fødselsdato). Brukeren kan slette kontoen sin selv, og da fjernes personopplysningene uten at andres dokumenterte erfaring forsvinner. Realiserer UJ-2.

#### FR-1: Registrere konto
En person uten konto kan registrere seg med navn, e-post, passord, telefonnummer, postnummer og fødselsdato. Realiserer UJ-2. Brief: R11, SK1.

**Konsekvenser (testbare):**
- Gyldige verdier: navn 1–80 tegn; e-post i gyldig format; passord minst 8 tegn; telefonnummer åtte siffer; postnummer fire siffer; fødselsdato ikke i fremtiden.
- Fødselsdato som gir alder under 18 år avvises. Den som fyller 18 i dag, godtas.
- E-post som allerede er i bruk avvises, uavhengig av store og små bokstaver (`Kari@x.no` = `kari@x.no`).
- Hvert ugyldig felt gir en forståelig melding rett ved feltet, og de andre utfylte feltene beholdes (unntatt passord).
- «Om meg» er ikke en del av registreringen; den skrives senere i profilen (FR-22).
- Etter vellykket registrering er brukeren innlogget.

#### FR-2: Logge inn og ut
En bruker kan logge inn med e-post og passord, og logge ut. Brief: SK1.

**Konsekvenser (testbare):**
- Feil e-post eller passord gir samme melding, uten å avsløre hvilken som var feil.
- E-post sammenlignes uten hensyn til store og små bokstaver.
- Etter utlogging gir ingen side med innhold tilgang før ny innlogging.

#### FR-3: Innlogging kreves
Bare innloggede brukere kan se oppdrag og profiler, legge ut oppdrag og melde interesse. Brief: R1.

**Konsekvenser (testbare):**
- Forespørsler uten gyldig innlogging mot oppdrag, profiler, interesser eller tilbakemeldinger avvises på serveren, og nettleseren sendes til innloggingssiden.

#### FR-4: Slette egen konto
En innlogget bruker kan slette sin egen konto etter å ha bekreftet det. Brief: R13, SK1, «Sletting av konto».

**Konsekvenser (testbare):**
- Før sletting får brukeren beskjed om hva som skjer, inkludert at kommentarer hen har gitt beholdes anonymt og i noen tilfeller kan avsløre hvem som skrev dem. Brukeren må bekrefte.
- Bare brukeren selv kan slette sin konto; forsøk på å slette andres konto avvises.
- Etter sletting kan brukeren ikke logge inn, og e-postadressen kan brukes til en ny registrering.
- Data behandles slik:

| Situasjon | Resultat |
|---|---|
| Egne oppdrag med status Åpen | Slettes, sammen med interessene på dem |
| Egne oppdrag med status Hjelper valgt | Settes til Avbrutt; telefonnumrene skjules |
| Egne oppdrag med status Avbrutt | Slettes |
| Oppdrag med status Utført (som oppdragsgiver eller hjelper) | Beholdes; brukeren vises som «Slettet bruker»; oppdraget teller fortsatt i den andre partens profil |
| Interesser brukeren har meldt | Slettes |
| Brukeren er valgt hjelper på oppdrag med status Hjelper valgt | Oppdraget går tilbake til Åpen som i FR-17 |
| Tilbakemeldinger brukeren har gitt | Beholdes som «Slettet bruker» og teller fortsatt i mottakerens gjennomsnitt |
| Tilbakemeldinger brukeren har fått | Slettes |
| Tilbakemelding som ennå ikke er gitt til brukeren | Kan ikke lenger gis (FR-20) |

### 4.2 Oppdrag

Oppdragsgiveren legger ut, redigerer og avbryter egne oppdrag. Skjemaet er delt i to steg, så det ikke blir for mange felter på én skjerm (se skissene). Realiserer UJ-1.

#### FR-5: Legge ut oppdrag
En innlogget bruker kan legge ut et oppdrag. Realiserer UJ-1. Brief: SK2.

**Konsekvenser (testbare):**
- Gyldige verdier: tittel 3–80 tegn; beskrivelse 10–1000 tegn; kategori fra den faste listen; postnummer fire siffer (forhåndsutfylt fra profilen, kan endres); tidspunkt ikke tilbake i tid; godtgjørelse heltall 1–10 000 kr eller «uten betaling». Alle felt er obligatoriske.
- Ugyldige felt avvises med forståelig melding ved feltet, og ingenting lagres.
- Tidspunkt angis, lagres og vises i norsk tid (Europe/Oslo). «Tilbake i tid» og «passert» (FR-8) vurderes mot nåværende norsk tid.
- Et lagret oppdrag får status Åpen, og innlogget bruker er oppdragsgiver.

#### FR-6: Redigere oppdrag
Oppdragsgiveren kan redigere sitt eget oppdrag mens det har status Åpen. Realiserer UJ-1 (når ingen melder interesse). Brief: R4.

**Konsekvenser (testbare):**
- Samme feltvalidering som FR-5.
- Redigering fra andre enn oppdragsgiveren avvises.
- Redigering av oppdrag med status Hjelper valgt, Utført eller Avbrutt avvises.
- Interesser på oppdraget beholdes ved redigering, slik at oppdragsgiveren fortsatt kan velge blant dem. En interessert som ikke passer lenger med de nye opplysningene, kan trekke interessen (FR-13).

#### FR-7: Avbryte oppdrag
Oppdragsgiveren kan avbryte sitt eget oppdrag mens det har status Åpen eller Hjelper valgt. Brief: R4.

**Konsekvenser (testbare):**
- Avbrytelse krever bekreftelse, og status blir Avbrutt.
- Avbrytelse fra andre enn oppdragsgiveren avvises.
- Avbrytelse av oppdrag med status Utført eller Avbrutt avvises.
- Etter avbrytelse skjules telefonnumrene (FR-16), og oppdraget kan ikke endres.

#### FR-8: Utgåtte oppdrag
Et oppdrag med status Åpen der tidspunktet er passert, er utgått. Realiserer UJ-1 (feiltilfelle). Brief: «Utgåtte oppdrag».

**Konsekvenser (testbare):**
- Utgåtte oppdrag vises ikke i oppdragsoversikten.
- Nye interesser på et utgått oppdrag avvises.
- Under «Mine oppdrag» er oppdraget merket «Tidspunktet er passert», og oppdragsgiveren kan endre tidspunktet (FR-6) eller avbryte (FR-7). Med nytt tidspunkt fram i tid vises det igjen i oversikten.

#### FR-9: Innsyn i oppdragsdetaljer
Hvem som ser detaljene i et oppdrag, avhenger av status og rolle. Brief: R9.

**Konsekvenser (testbare):**
- Detaljene viser alle feltene i oppdraget, status, og oppdragsgiverens navn, antall fullførte oppdrag og gjennomsnittlig vurdering, med lenke til profilen.
- Status Åpen: alle innloggede ser detaljene; lista over interesserte ser bare oppdragsgiveren.
- Andre statuser: bare oppdragsgiveren og valgt hjelper ser detaljene. Andre får avvist forespørselen.
- Interesserte som ikke ble valgt, ser bare tittel og status under «Mine oppdrag».

### 4.3 Finne oppdrag

Hjelperen ser åpne oppdrag i nærheten, sortert etter når de skal gjøres. «I nærheten» betyr samme postnummer i v1. Realiserer UJ-2.

#### FR-10: Oppdragsoversikt
En innlogget bruker ser som standard åpne oppdrag i sitt eget postnummer. Realiserer UJ-2. Brief: SK3.

**Konsekvenser (testbare):**
- Bare oppdrag med status Åpen og tidspunkt fram i tid vises.
- Sortering er etter tidspunkt, tidligste først.
- Hvert oppdrag i lista viser tittel, kategori, tidspunkt og godtgjørelse.
- Brukerens egne oppdrag vises ikke i oversikten. De finnes under «Mine oppdrag» (FR-18).
- Ingen treff gir en tomtilstand med forklaring og forslag (for eksempel å velge et annet postnummer).

**Kjent begrensning:** Naboer på hver sin side av en postnummergrense ser ikke hverandres oppdrag som standard. Det godtas i v1; kart og avstand er utsatt (§7.2).

#### FR-11: Filtrere oppdrag
Brukeren kan filtrere oversikten på kategori og velge et annet postnummer. Brief: SK3.

**Konsekvenser (testbare):**
- Filter på kategori viser bare oppdrag i valgt kategori.
- Valgt postnummer erstatter eget postnummer i lista; ugyldig postnummer (ikke fire siffer) avvises med melding.
- Filtrene kan kombineres.

### 4.4 Interesse og valg av hjelper

Hjelpere melder interesse, og oppdragsgiveren velger én av dem. Først da deles telefonnumrene. Realiserer UJ-1 og UJ-2.

#### FR-12: Melde interesse
En innlogget bruker kan melde interesse for et oppdrag, eventuelt med en kort melding til oppdragsgiveren. Realiserer UJ-2. Brief: R2, R3, SK4.

**Konsekvenser (testbare):**
- Interesse på eget oppdrag avvises.
- Ny interesse fra en bruker som allerede har interesse på oppdraget, avvises.
- Interesse avvises hvis status ikke er Åpen, eller tidspunktet er passert.
- Meldingen er valgfri og maks 500 tegn.
- Etter innmelding ser hjelperen «Du har meldt interesse» i stedet for knappen, og oppdraget vises under «Oppdrag jeg hjelper med».

#### FR-13: Trekke interesse
En interessert kan trekke interessen sin. Brief: R3, SK4.

**Konsekvenser (testbare):**
- Tillatt bare mens status er Åpen og tidspunktet ikke er passert; ellers avvises det.
- Etter tilbaketrekking er interessen borte fra oppdragsgiverens liste, og brukeren kan melde interesse på nytt.

#### FR-14: Se interesserte
Oppdragsgiveren ser alle som har meldt interesse på sitt oppdrag. Realiserer UJ-1. Brief: R9, SK4.

**Konsekvenser (testbare):**
- For hver interessert vises navn, antall fullførte oppdrag, gjennomsnittlig vurdering (eller «Ingen vurderinger ennå») og meldingen, med lenke til profilen.
- Lista vises ikke for andre enn oppdragsgiveren.
- Ingen interesserte gir en tomtilstand med forklaring.

#### FR-15: Velge hjelper
Oppdragsgiveren kan velge nøyaktig én av de interesserte. Realiserer UJ-1. Brief: R5, SK5.

**Konsekvenser (testbare):**
- Valget krever bekreftelse («Velge Amir? Dere får se hverandres telefonnummer.»).
- Status blir Hjelper valgt, og oppdraget forsvinner fra oversikten.
- Valg avvises hvis brukeren ikke er oppdragsgiver, status ikke er Åpen, eller den valgte ikke har meldt interesse.
- Hvis statusen allerede er endret (for eksempel ved dobbeltklikk eller to faner), avvises det andre valget, og det finnes fortsatt bare én valgt hjelper.

#### FR-16: Dele telefonnummer
Oppdragsgiveren og valgt hjelper ser hverandres telefonnummer. Realiserer UJ-1, UJ-2. Brief: R10.

**Konsekvenser (testbare):**
- Telefonnumrene vises bare for disse to, og bare mens status er Hjelper valgt eller Utført.
- Når hjelperen fjernes eller trekker seg, eller oppdraget avbrytes, skjules numrene igjen.
- Ingen andre steder i appen viser telefonnummer, e-post eller fødselsdato (heller ikke i svar fra serveren).

#### FR-17: Fjerne hjelper eller trekke seg
Mens status er Hjelper valgt kan oppdragsgiveren fjerne valgt hjelper, og valgt hjelper kan trekke seg. Realiserer UJ-2 (feiltilfelle). Brief: R6, SK6.

**Konsekvenser (testbare):**
- Begge handlinger krever bekreftelse.
- Status blir Åpen, og oppdraget vises igjen i oversikten (hvis tidspunktet ikke er passert).
- Den tidligere hjelperens interesse slettes; de andre interessene beholdes.
- Telefonnumrene skjules (FR-16).
- Forsøk fra andre, eller ved annen status enn Hjelper valgt, avvises.

### 4.5 Mine oppdrag

Én side der brukeren ser egne oppdrag og oppdrag hen hjelper med. Realiserer UJ-1, UJ-2.

#### FR-18: Mine oppdrag
En innlogget bruker ser sine oppdrag i to faner. Brief: «Viktigste skjermbilder» nr. 4, R9.

**Konsekvenser (testbare):**
- «Oppdrag jeg har lagt ut» viser alle egne oppdrag med status, antall interesserte og navnet på valgt hjelper når det finnes; utgåtte er merket «Tidspunktet er passert».
- «Oppdrag jeg hjelper med» viser oppdrag der brukeren har interesse eller er valgt hjelper, med status.
- For oppdrag der brukeren meldte interesse uten å bli valgt, vises bare tittel og status.
- Oppdrag med status Utført der brukeren ennå ikke har gitt tilbakemelding, er merket «Gi tilbakemelding».
- Tom fane gir en tomtilstand med forklaring og lenke videre (til «Legg ut oppdrag» eller oversikten).

### 4.6 Fullføre og gi tilbakemelding

Hjelperen markerer oppdraget som utført, og begge parter kan gi hverandre en tilbakemelding som vises i profilen. Realiserer UJ-1, UJ-2.

#### FR-19: Markere som utført
Valgt hjelper kan markere oppdraget som Utført. Realiserer UJ-2. Brief: R7, SK7.

**Konsekvenser (testbare):**
- Tillatt bare for valgt hjelper og bare når status er Hjelper valgt; ellers avvises det.
- Etter Utført kan oppdraget ikke endres, og begge parter kan gi tilbakemelding.

#### FR-20: Gi tilbakemelding
Oppdragsgiveren og valgt hjelper kan gi hverandre én tilbakemelding per oppdrag. Realiserer UJ-1, UJ-2. Brief: R8, SK8.

**Konsekvenser (testbare):**
- Vurderingen er 1–5 stjerner. Hver stjerne er en stor knapp som kan brukes med tastatur og har tekst for skjermleser («4 av 5 stjerner»), jf. NFR-7. Kommentar er valgfri, maks 500 tegn.
- Tillatt bare når status er Utført, bare mellom oppdragsgiver og valgt hjelper, og bare én gang per person per oppdrag. Andre forsøk avvises.
- Tilbakemelding til en bruker som har slettet kontoen, avvises.
- Tilbakemeldingen vises straks i mottakerens profil, og gjennomsnittet oppdateres.

### 4.7 Profil og dokumentert erfaring

Profilen er «erfaringsbeviset» en hjelper kan vise til i en jobbsøknad. Realiserer UJ-2.

#### FR-21: Vise profil
En innlogget bruker kan se profilen til en annen bruker. Realiserer UJ-1, UJ-2. Brief: R9, SK9.

**Konsekvenser (testbare):**
- Profilen viser navn, postnummer, om meg, antall fullførte oppdrag per kategori, gjennomsnittlig vurdering og alle mottatte tilbakemeldinger (vurdering, kommentar, hvem som ga den, dato).
- Bruker uten vurderinger vises med «Ingen vurderinger ennå».
- Tilbakemeldinger fra brukere som har slettet kontoen, vises med «Slettet bruker» (FR-4).
- Profilen viser aldri telefonnummer, e-post eller fødselsdato.
- «Fullførte oppdrag» teller oppdrag med status Utført der brukeren var valgt hjelper. Oppdrag brukeren selv har lagt ut, teller ikke.
- Gjennomsnittlig vurdering regnes av alle tilbakemeldinger brukeren har fått, både som hjelper og som oppdragsgiver.

#### FR-22: Redigere egen profil
En innlogget bruker kan skrive og endre en kort tekst om seg selv («om meg») og endre postnummer, for eksempel ved flytting. «Om meg» fylles ikke inn ved registrering. Brief: «Profil og dokumentert erfaring», «Nærhet».

**Konsekvenser (testbare):**
- «Om meg» er valgfri, maks 500 tegn. Er den tom, vises ikke feltet i profilen.
- Postnummer må være fire siffer; ugyldig verdi avvises med melding ved feltet.
- Nytt postnummer brukes straks som standard i oppdragsoversikten (FR-10) og forhåndsutfylles i nye oppdrag (FR-5). Oppdrag som allerede er lagt ut, beholder sitt postnummer.
- Navn, e-post, telefonnummer og fødselsdato kan ikke endres i v1.
- Bare brukeren selv kan endre sin profil; andre forsøk avvises.

### 4.8 KI-forslag

I skjemaet for nytt oppdrag kan oppdragsgiveren få forslag til kategori, tittel og beskrivelse. Funksjonen finnes bare når et oppdrag legges ut, ikke ved redigering (som i briefen). KI-en er et hjelpemiddel: brukeren bestemmer alltid selv, og appen fungerer fullt ut uten KI. Bygges etter at kjerneflyten er ferdig og stabil. Realiserer UJ-1.

#### FR-23: Be om forslag
Oppdragsgiveren kan trykke «Få forslag» når beskrivelsesfeltet har tekst. Realiserer UJ-1. Brief: R12, SK10.

**Konsekvenser (testbare):**
- Knappen er deaktivert når beskrivelsesfeltet er tomt.
- Brukeren får beskjed om at teksten sendes til en ekstern tjeneste.
- Bare teksten i beskrivelsesfeltet sendes. Navn, e-post, telefonnummer og andre profilopplysninger legges aldri til.
- Mens forslaget hentes, er knappen deaktivert og viser «Lager forslag …», slik at brukeren ikke kan sende flere forespørsler samtidig.

#### FR-24: Bruke eller forkaste forslag
Forslagene vises ved siden av feltene, og brukeren velger «Bruk» eller «Forkast» for hvert. Realiserer UJ-1. Brief: R12.

**Konsekvenser (testbare):**
- Et forslag fyller aldri inn et felt før brukeren trykker «Bruk».
- Et eventuelt tips fra KI-en (for eksempel «Skriv gjerne hvor stor innkjørselen er») vises sammen med forslagene.
- Etter «Bruk» kan feltet fortsatt redigeres.
- KI-en lagrer eller publiserer aldri noe; oppdraget lagres bare når brukeren trykker «Publiser» (FR-5).

#### FR-25: Kontroll av KI-svar
Svaret fra språkmodellen valideres før det vises. Brief: «Kontroll av svaret fra KI-en», SK10.

**Konsekvenser (testbare):**
- Svaret må være gyldig JSON med kategori (fra den faste listen), tittel (maks 80 tegn) og beskrivelse (maks 1000 tegn), og kan ha et kort tips.
- Ugyldig JSON, ukjent kategori eller for lang tekst avvises.
- Får appen ikke svar innen 10 sekunder, avbrytes forespørselen (tidsavbrudd).
- Ved ugyldig svar, tidsavbrudd eller feil i tjenesten vises en vennlig melding («Vi fikk ikke laget forslag akkurat nå. Du kan fylle inn selv.»), skjemaet beholder det brukeren har skrevet, og oppdraget kan lagres manuelt.

#### FR-26: Mock-modus
Når ingen API-nøkkel er satt, brukes en innebygd mock-tjeneste med faste svar. Brief: «Mock-modus», SK10.

**Konsekvenser (testbare):**
- Kategori velges etter første kategori med nøkkelordtreff i teksten (ikke skille på store og små bokstaver):

| Kategori | Nøkkelord |
|---|---|
| Snømåking | snø, måke, brøyte, strø |
| Hage | hage, plen, gress, klippe, hekk, løv, luke |
| Bærehjelp/flytting | bære, flytte, flytting, sofa, møbel, eske |
| Dyrepass | hund, katt, lufte, dyr, mate |
| Teknologihjelp | pc, data, ipad, nettbrett, mobil, wifi, tv, skriver |
| Annet | Ingen nøkkelord treffer |

- Tittelforslaget er første setning i teksten, forkortet til maks 80 tegn og med stor forbokstav. Beskrivelsesforslaget er teksten med stor forbokstav og punktum til slutt.
- «måke snø i innkjørselen» gir Snømåking; en tekst uten nøkkelord gir Annet.
- Samme tekst gir alltid samme svar. Automatiske tester kjører alltid i mock-modus.

## 5. Tverrgående kvalitetskrav

#### NFR-1: Kjørbar på en ren maskin
Appen kan startes lokalt ved å følge README, uten betalte tjenester, eksterne kontoer eller gruppens egne nøkler. README har forutsetninger med versjoner, eksakte kommandoer, og kommandoen som kjører de automatiske testene. Testes ved at noen utenfor gruppen (eller en ren maskin/container) følger README fra start, innenfor 15–20 minutter.

#### NFR-2: Eksempeldata og testbrukere
Repoet har oppdiktede eksempeldata: minst 6 testbrukere i 2–3 postnumre og 10–15 oppdrag fordelt på alle fire statuser, inkludert minst ett utgått oppdrag og tilbakemeldinger. Innloggingsinformasjon for testbrukerne står i README.

#### NFR-3: Ingen hemmeligheter i repoet
Hemmeligheter ligger i `.env`, som ikke er i repoet. `.env.example` viser alle variabler uten ekte verdier. `.gitignore` holder ute `.env`, avhengigheter og byggmapper. Prompten til KI-tjenesten ligger i en egen fil i koden.

#### NFR-4: Sikker lagring
Passord lagres aldri i klartekst, bare som hash med en algoritme laget for passord (for eksempel bcrypt eller Argon2; valget tas i arkitekturen). Testes ved at passordfeltet i databasen ikke inneholder passordet. Data lagres i én database.

#### NFR-5: Regler håndheves på serveren
Alle regler i FR-ene for hvem som kan gjøre hva, og når, sjekkes på serveren, ikke bare ved å skjule knapper. Hver regel R1–R13 i briefen har minst én automatisk test mot kravene den er koblet til i sporingstabellen i §4.

#### NFR-6: Responsiv
Hele kjerneflyten kan gjennomføres i vanlig nettleser fra 360 px bredde (mobil) til PC, uten vannrett rulling. Ingen egen mobilapp.

#### NFR-7: Universell utforming
Appen følger WCAG 2.1 nivå AA for de delene som gjelder. Konkret:
- Kontrast minst 4,5:1 for tekst.
- Alt kan brukes med tastatur, med synlig fokus.
- Alle skjemafelt har synlige etiketter; feilmeldinger står ved feltet og er knyttet til det.
- Knapper har tekst, ikke bare ikoner; bilder og ikoner med mening har alt-tekst.
- Brødtekst er minst 18 px, og knapper og andre trykkflater er minst 48 px høye (som i skissene).
- Status vises alltid med ord («Åpen», «Hjelper valgt»), ikke bare med farge.
- Lister og faner uten innhold har en tomtilstand med forklaring.

Testes med automatisk verktøy (for eksempel axe/Lighthouse) og en manuell tastaturgjennomgang av kjerneflyten.

#### NFR-8: Tydelig og enkelt språk
All tekst i appen er på norsk bokmål, med enkelt språk: knapper og overskrifter bruker ordene i ordlisten (§3) og skissene, for eksempel «Meld interesse», ikke «Send forespørsel». Testes ved en manuell gjennomgang av kjerneflyten mot ordlisten. Hver handling gir tydelig tilbakemelding (for eksempel «Takk! Tilbakemeldingen er lagt til i Amirs profil.»), og farlige handlinger (avbryte, fjerne hjelper, trekke seg, slette konto) krever bekreftelse. Etter innlogging har appen en fast meny med tre valg: Oppdrag, Mine oppdrag og Profil.

#### NFR-9: Personvern
Appen lagrer bare navn, e-post, hashet passord, telefonnummer, postnummer, fødselsdato og innhold brukeren selv legger inn. Eksakt adresse lagres ikke. Eksempeldata inneholder ingen ekte personopplysninger.

#### NFR-10: Robust mot feil input
All input valideres på serveren, også når nettleseren allerede har sjekket den. Ugyldig input eller uventede feil gir en forståelig melding til brukeren, aldri en teknisk feilmelding eller krasj. Testes med automatiske tester som sender ugyldige verdier til hvert skjema og hver handling.

## 6. Ikke-mål

Nabolagshelten har ingen betaling i appen. Den skal heller ikke være en jobbportal, en bemanningsplattform, en markedsplass for kjøp og salg, håndverkere eller utleie, et sosialt medium, eller et sted for store eller komplekse oppdrag.

## 7. Omfang

### 7.1 Med i v1

Alle FR-er og NFR-er i dette dokumentet. KI-forslag (FR-23–FR-26) bygges etter at kjerneflyten er ferdig og stabil.

### 7.2 Utsatt til senere trinn

- Deling og utlån av utstyr (trinn 2)
- Identitetsverifisering med BankID eller Vipps
- Brukere under 18 år med godkjenning fra foresatte
- Kart og avstandsbasert matching (erstatter postnummer)
- Meldinger/chat i appen
- Varsler på e-post eller push – uten varsler må brukeren selv åpne «Mine oppdrag» for å se endringer
- Eksport av erfaringsoversikt til PDF
- Flere KI-funksjoner (forslag til godtgjørelse, sjekk av upassende innhold, KI-generert CV-tekst)

## 8. Suksessmål

**Primære**
- **SM-1:** Alle krav FR-1–FR-26 er dekket av akseptansekriterier i stories, og testene for dem passerer. Dermed er også alle ti suksesskriterier i briefen (SK1–SK10) oppfylt.
- **SM-2:** Hver regel R1–R13 har minst én automatisk test som passerer. Validerer NFR-5.
- **SM-3:** En person utenfor gruppen får appen i gang ved å følge README, uten hjelp. Validerer NFR-1, NFR-2.

**Sekundære**
- **SM-4:** I en brukertest med minst to testpersoner utenfor gruppen klarer hver av dem å legge ut et oppdrag (UJ-1, steg 1–3) på under to minutter på mobil eller nettbrett. Tiden måles fra «Legg ut oppdrag» trykkes til oppdraget er publisert. Resultatet dokumenteres som manuell test. Validerer FR-5, NFR-6, NFR-7.
- **SM-5:** Automatisk tilgjengelighetstest av de fem hovedskjermbildene gir ingen alvorlige feil. Validerer NFR-7.

**Motmål (skal ikke optimeres)**
- **SM-C1:** Andel oppdrag laget med KI-forslag. Skal ikke presses opp; KI-en er et valgfritt hjelpemiddel, og manuell utfylling skal være like enkel. Motvekt til SM-4.
- **SM-C2:** Antall funksjoner. Flere funksjoner enn i §7.1 skal ikke prioriteres før SM-1–SM-3 er nådd. Motvekt til SM-1.

## 9. Åpne punkter til neste fase

Ingen åpne spørsmål blokkerer UX, arkitektur eller stories. Disse punktene følges opp i neste fase:

1. **Skissene oppdateres i UX-steget** (`bmad-ux`): Skissen for tilbakemelding viser tallknapper, men PRD-en sier 1–5 stjerner som store knapper (FR-20, NFR-7). Skissen for oversikten viser «Fleksibelt denne uken» som tidspunkt, men tidspunkt skal være dato og klokkeslett (FR-5).

## 10. Presiseringer og tillegg i forhold til briefen

Briefen v2.2 avgjør ikke alt. Tabellen viser hvor PRD-en presiserer eller legger til, og hvorfor. Ingen antakelser står åpne.

| Tema | Briefen | PRD-en | Begrunnelse |
|---|---|---|---|
| Vurdering | 1–5 stjerner | 1–5 stjerner som store knapper med tekst for skjermleser (FR-20) | Briefen følges; skissens tallknapper var for å gjøre det lett å treffe, og det løses med store knapper |
| Melding ved interesse | «kort melding» | Valgfri, maks 500 tegn (FR-12) | Skissen viser feltet som valgfritt; grense avklart med gruppen |
| Kommentar og «om meg» | Ingen lengde | Maks 500 tegn (FR-20, FR-22) | Avklart med gruppen |
| Redigere profil | «Om meg» nevnes, ikke hvordan | «Om meg» og postnummer kan endres etter registrering; andre felt ikke (FR-22) | Gruppen: brukere må kunne skrive om seg selv senere og endre postnummer ved flytting |
| Egne oppdrag i oversikten | Ikke sagt | Vises ikke; finnes under «Mine oppdrag» (FR-10) | Gruppen: oversikten er for å finne oppdrag man kan hjelpe med (jf. R2) |
| Fullførte oppdrag | Ikke presisert | Teller bare oppdrag som valgt hjelper (FR-21) | Gruppen: profilen skal vise erfaring som hjelper |
| Interesser ved redigering | Ikke sagt | Beholdes (FR-6) | Samme prinsipp som R6; interesserte kan trekke seg (FR-13) |
| KI ved redigering | «I skjemaet for nytt oppdrag» | Bare ved nytt oppdrag (§4.8) | Som i briefen |
| Tidssone | Ikke sagt | Norsk tid, Europe/Oslo (FR-5) | Appen er for norske nabolag |
| Tidsavbrudd for KI | «tidsavbrudd» | 10 sekunder (FR-25) | Gjør kravet testbart |
| Tekst og trykkflater | «stor nok» | Brødtekst ≥ 18 px, trykkflater ≥ 48 px (NFR-7) | Fra skissene |
| Universell utforming, robusthet og repo | Delvis | WCAG 2.1 AA (NFR-7), robust mot feil input (NFR-10), `.gitignore` og testkommando i README (NFR-1, NFR-3) | Fra sensorveiledningen |

## Endringslogg

| Dato | Versjon | Endring |
|---|---|---|
| 2026-11-05 | 0.1 | Arbeidet startet. Form: webapp, coaching, brukerreiser først. |
| 2026-11-07 | 0.2 | UJ-1 (Kari) og UJ-2 (Amir) skrevet med gruppen. Utkast til ordliste, FR-1–FR-26, NFR-1–NFR-9, omfang og suksessmål laget fra briefen v2.2. |
| 2026-11-07 | 0.3 | Avklaringer: vurdering med 1–5 stjerner som i briefen (store knapper, jf. NFR-7); «om meg» skrives og postnummer kan endres i profilen etter registrering (FR-22); egne oppdrag vises bare under «Mine oppdrag» (FR-10); bare oppdrag som hjelper teller som fullført (FR-21); maks 500 tegn for melding, kommentar og «om meg». |
| 2026-11-07 | 1.0 | Ferdigstilt. Avstemt mot brief, skisser, faglærers tilbakemelding og sensorveiledning (rettet FR-9, FR-10, FR-18, FR-24, NFR-1, NFR-3, NFR-7, NFR-8; ny NFR-10). Review-funn rettet: sporingstabell R1–R13 og SK1–SK10 → FR i §4, KI-tidsavbrudd 10 s, testbar ventetilstand, NFR-4, NFR-5, NFR-8, SM-1, SM-4. Tidssone og interesser ved redigering avgjort. Ny §10 med alle presiseringer i forhold til briefen. Språkvask. |
