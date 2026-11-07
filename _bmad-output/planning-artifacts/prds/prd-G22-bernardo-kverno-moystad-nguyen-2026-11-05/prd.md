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
| **Versjon** | 1.1 (ferdig) |
| **Bygger på** | [Product brief v2.2](../../product-brief-nabolagshelten.md) (= «proposal» i sensorveiledningen), [skisser av skjermbilder](../../skisser-skjermbilder.md) |

## 0. Om dokumentet

PRD-en beskriver *hva* versjon 1 (v1) av Nabolagshelten skal gjøre, slik at gruppen kan lage arkitektur, epics og stories fra den. Den er skrevet for gruppen, faglærer og sensor. V1 er ferdig når suksessmålene SM-1–SM-3 er nådd (§7).

- **Briefen er fasit.** PRD-en gjør briefens regler (R1–R13) og suksesskriterier (SK1–SK10) om til krav med faste ID-er. Sporingen står samlet i §9.1. Der briefen ikke avgjør noe, har gruppen tatt et valg, og der PRD-en avviker fra briefen, er det sagt. Alle presiseringer, avvik og tillegg står med begrunnelse i §9.2.
- **Faste ID-er.** Brukerreiser heter UJ-N, funksjonelle krav FR-N, kvalitetskrav NFR-N og suksessmål SM-N. ID-ene skal brukes i stories, commits og PR-er. En ID endres ikke selv om rekkefølgen endres, og den brukes aldri om igjen. Et krav som fjernes, blir stående med merknaden «Utgått (dato, grunn)».
- **Testbare krav.** Hvert krav har konsekvenser som kan bli akseptansekriterier og automatiske eller manuelle tester. Hvert krav har også en sporingslinje (brukerreise, regel og suksesskriterium i briefen) og en prioritet (§6.1).
- **Ordlisten (§3) er bindende.** Begrepene brukes likt i hele dokumentet og i koden der det er naturlig.
- Teknologivalg hører hjemme i arkitekturdokumentet, ikke her.
- Endringer etter at PRD-en er ferdig, føres i endringsloggen nederst.

## 1. Visjon

Nabolagshelten er en webapp som kobler personer som trenger hjelp til små, praktiske hverdagsoppgaver – snømåking, gressklipping, bærehjelp, hundelufting, teknologihjelp – med naboer som bor i samme postnummer og har tid til å hjelpe.

V1 har én kjerneflyt: legge ut et oppdrag → melde interesse → velge hjelper → markere som utført → gi tilbakemelding. Fullførte oppdrag og tilbakemeldinger samles i hjelperens profil, slik at småjobber blir dokumentert erfaring som kan brukes i en jobbsøknad. En avgrenset KI-funksjon hjelper oppdragsgiveren å formulere oppdraget, men appen fungerer fullt ut uten KI.

I dag løses slike behov tilfeldig via Facebook-grupper, Finn eller bekjente. Da er det uklart hvem som tar jobben, om oppdraget fortsatt er ledig og om personen er til å stole på. Nabolagshelten gir tydelig status, lokal oversikt og en historikk som bygger tillit.

## 2. Målgruppe

### 2.1 Behov (jobs to be done)

- **Oppdragsgiver (Kari):** Få hjelp til en liten oppgave i nærheten uten å ringe rundt, og kunne velge noen hun føler seg trygg på. Legge ut et oppdrag på under to minutter.
- **Hjelper (Amir):** Raskt finne ledige oppdrag i nærheten, forstå hva de innebærer og betaler, og samle dokumentert erfaring og tilbakemeldinger til CV-en.
- **Begge:** Se tydelig om et oppdrag er ledig, tatt eller utført. Samme person kan være oppdragsgiver én dag og hjelper neste – det finnes ikke egne kontotyper.

Andre grupper (barnefamilier, travle personer, arbeidsledige) har de samme behovene og dekkes av den samme flyten.

### 2.2 Ikke målgruppe i v1

Personer under 18 år (§6.2), og firmaer, håndverkere og større eller komplekse oppdrag (§6.3).

### 2.3 Brukerreiser

**UJ-1. Kari får måkt innkjørselen uten å ringe rundt.**

- **Person og situasjon:** Kari, 72 år, bor alene i rekkehus. En mandag morgen i januar har det snødd mye i løpet av natten, og hun orker ikke å måke selv. Hun bruker nettbrett, men gir opp hvis noe er uoversiktlig.
- **Utgangspunkt:** Hun har allerede konto og er innlogget på nettbrettet. Hun starter på oppdragsoversikten.
- **Veien:**
  1. Hun trykker «Legg ut oppdrag» og skriver med egne ord i beskrivelsesfeltet: «Trenger noen som kan måke snø i innkjørselen min i morgen.»
  2. Hun trykker «Få forslag». KI-en foreslår tittel, kategori (Snømåking) og en bedre beskrivelse, og hun trykker «Bruk» på forslagene.
  3. Hun ser at postnummeret er forhåndsutfylt og riktig, velger tidspunkt, legger inn 200 kr i godtgjørelse og trykker «Publiser». Oppdraget får status **Åpen** og blir synlig i oppdragsoversikten for alle som ser på postnummeret hennes – som standard naboene i samme postnummer.
  4. Senere samme dag går hun til «Mine oppdrag», ser at to har meldt interesse, og åpner oppdraget. For hver av de interesserte ser hun navn, antall fullførte oppdrag, gjennomsnittlig vurdering og meldingen deres.
  5. Hun velger den hun føler seg tryggest på. Status blir **Hjelper valgt**, og de ser hverandres telefonnummer, så de kan avtale detaljene direkte.
- **Vendepunktet:** Kari kan sammenligne de interesserte på erfaring og vurderinger før hun velger. Det er det som gjør at hun føler seg trygg.
- **Avslutningen:** Neste dag måker hjelperen innkjørselen, og Kari betaler 200 kr med Vipps utenfor appen. Hjelperen markerer oppdraget som **Utført**. Kari gir fem stjerner og en kort kommentar, som vises i hjelperens profil. Hun fikk hjelp uten å ringe rundt og uten innlegg på Facebook.
- **Når noe går galt:**
  - *Ingen melder interesse:* Kari ser fortsatt oppdraget under «Mine oppdrag» med status **Åpen**. Hun kan redigere tidspunktet eller godtgjørelsen for å gjøre det mer attraktivt.
  - *Tidspunktet passerer uten hjelper:* Oppdraget forsvinner fra oversikten og kan ikke få nye interesser. Under «Mine oppdrag» er det merket «Tidspunktet er passert», og Kari kan endre tidspunktet eller avbryte oppdraget.
  - *Hjelperen glemmer å markere oppdraget som utført:* Etter tidspunktet står det «Er jobben gjort?» ved oppdraget under «Mine oppdrag». Kari markerer det som **Utført** selv og gir tilbakemelding.
- **Krav:** FR-5, FR-6, FR-7, FR-8, FR-14, FR-15, FR-16, FR-18, FR-19, FR-20, FR-21, FR-23, FR-24, FR-25

**UJ-2. Amir gjør småjobber og bygger en profil han kan vise til.**

- **Person og situasjon:** Amir, 21 år, student. Vil tjene litt ekstra ved siden av studiene og få erfaring å vise til når han søker sommerjobb. Har tid på ettermiddager og i helger.
- **Utgangspunkt:** En ettermiddag hører han om Nabolagshelten og åpner nettsiden på mobilen. Han har ingen konto.
- **Veien:**
  1. Han registrerer seg med navn, e-post, telefonnummer, postnummer, fødselsdato og passord. Han er over 18 år, så kontoen opprettes, og han er innlogget.
  2. Oppdragsoversikten viser åpne oppdrag i hans postnummer, sortert etter tidspunkt. Han ser et oppdrag i kategorien Bærehjelp/flytting på lørdag, med godtgjørelse 400 kr. Han har fri den dagen.
  3. Han åpner oppdraget, leser beskrivelsen, skriver en melding – «Hei! Jeg kan gjerne hjelpe deg på lørdag. Jeg har erfaring med å bære møbler fra tidligere flyttinger.» – og trykker «Meld interesse».
  4. Senere går han til «Mine oppdrag», fanen «Oppdrag jeg hjelper med», og ser at oppdraget er merket «Du er valgt». Han ser oppdragsgiverens telefonnummer, så de kan avtale detaljene direkte.
  5. På lørdag bærer han møblene. Etterpå markerer han oppdraget som **Utført**, og får 400 kr med Vipps utenfor appen.
- **Vendepunktet:** Oppdragsgiveren gir ham fem stjerner og en kommentar om at han møtte presis og gjorde en god jobb. Amir ser at det fullførte oppdraget og vurderingen nå står i profilen hans.
- **Avslutningen:** Amir gir også oppdragsgiveren en vurdering, siden begge parter kan gi tilbakemelding. Etter hvert som han tar flere oppdrag, viser profilen antall fullførte oppdrag per kategori, gjennomsnittlig vurdering og tilbakemeldinger. Når han søker sommerjobb, viser han profilen på mobilen som dokumentasjon på praktisk erfaring.
- **Når noe går galt:**
  - *Oppdragsgiveren velger en annen:* Under «Mine oppdrag» er oppdraget merket «Ikke valgt», og Amir ser bare tittel og status, ikke detaljene. Han fortsetter å se etter andre åpne oppdrag i nærheten.
  - *Han kan ikke likevel:* Mens status er **Hjelper valgt**, trykker han «Trekk meg» og bekrefter. Oppdraget får status **Åpen** igjen, telefonnumrene skjules, og oppdragsgiveren kan velge blant de andre interesserte. Under «Mine oppdrag» er oppdraget merket «Du trakk deg».
- **Krav:** FR-1, FR-9, FR-10, FR-12, FR-16, FR-17, FR-18, FR-19, FR-20, FR-21

## 3. Ordliste

- **Bruker** – En person med konto. Alle brukere kan både legge ut oppdrag og hjelpe; det finnes ikke egne kontotyper.
- **Innlogget bruker** – En bruker med gyldig innlogging (FR-2, FR-3).
- **Oppdrag** – En liten, praktisk oppgave som en oppdragsgiver trenger hjelp til. Har feltene tittel, beskrivelse, kategori, postnummer, tidspunkt og godtgjørelse, og har til enhver tid nøyaktig én status.
- **Oppdragsgiver** – Brukeren som har lagt ut et oppdrag. Ett oppdrag har én oppdragsgiver.
- **Hjelper** – En bruker som melder interesse for eller utfører oppdrag for andre. Samme rolle som «oppdragstaker» i briefen; PRD-en bruker bare «hjelper».
- **Interesse** – En brukers ønske om å ta et oppdrag, eventuelt med en kort melding til oppdragsgiveren (regler: FR-12, FR-13).
- **Interessert** – En bruker som har meldt interesse for et oppdrag og ikke trukket den.
- **Valgt hjelper** – Den interesserte som oppdragsgiveren har valgt. Et oppdrag har null eller én valgt hjelper. Koblingen beholdes når oppdraget blir Utført eller Avbrutt.
- **Tidligere valgt hjelper** – En bruker som var valgt hjelper og ble fjernet av oppdragsgiveren eller trakk seg selv (FR-17). Appen husker hvem det var og hvorfor (FR-12, FR-18).
- **Status** – Tilstanden til et oppdrag: **Åpen**, **Hjelper valgt**, **Utført** eller **Avbrutt**. Utført og Avbrutt er endelige. Overgangene står i §4.0.
- **Passert** – Et tidspunkt er passert når det ikke lenger er fram i tid, målt i norsk tid (Europe/Oslo).
- **Utgått oppdrag** – Et oppdrag med status Åpen der tidspunktet er passert. Ikke en egen status.
- **Kategori** – Én fra den faste lista: Snømåking, Hage, Bærehjelp/flytting, Dyrepass, Teknologihjelp, Annet.
- **Godtgjørelse** – Det oppdragsgiveren tilbyr: et beløp i kroner eller «uten betaling» (regler: FR-5). Betales utenfor appen.
- **Tidspunkt** – Ønsket dato og klokkeslett for oppdraget.
- **Postnummer** – Fire siffer som finnes i lista over norske postnumre som ligger i repoet. Vises sammen med poststedet.
- **Oppdragsoversikt** («oversikten») – Startsiden med åpne oppdrag, med filter på kategori og postnummer. Menyvalget heter «Oppdrag» (NFR-11).
- **Mine oppdrag** – Siden med fanene «Oppdrag jeg har lagt ut» og «Oppdrag jeg hjelper med».
- **Tilbakemelding** – En vurdering (1–5 stjerner) og en valgfri kommentar fra én part i et utført oppdrag til den andre.
- **Profil** – Det andre brukere ser om en bruker (innhold: FR-21).
- **Fullført oppdrag** – Et oppdrag med status Utført, telt for den som var valgt hjelper.
- **KI-tjenesten** – Språkmodellen appen bruker, eller mock-modus når ingen API-nøkkel er satt.
- **KI-forslag** – Forslag til kategori, tittel og beskrivelse som KI-tjenesten lager fra teksten i beskrivelsesfeltet.
- **Mock-modus** – Innebygd erstatning for språkmodellen, som lager svar etter faste regler (FR-26).
- **Avvises** – Handlingen utføres ikke, ingen data endres, og brukeren får en forståelig melding.
- **Slettet bruker** – Visningsnavnet for en bruker som har slettet kontoen sin, i oppdrag og tilbakemeldinger som beholdes.

## 4. Funksjoner

### 4.0 Statusmodell og felles regler

| Fra | Til | Hvem og når | Krav |
|---|---|---|---|
| (nytt) | Åpen | Oppdragsgiver legger ut | FR-5 |
| Åpen | Hjelper valgt | Oppdragsgiver velger hjelper, før tidspunktet er passert | FR-15 |
| Hjelper valgt | Åpen | Oppdragsgiver fjerner hjelper, eller valgt hjelper trekker seg | FR-17 |
| Hjelper valgt | Utført | Valgt hjelper fra dagen for tidspunktet, eller oppdragsgiver når tidspunktet er passert | FR-19 |
| Åpen / Hjelper valgt | Avbrutt | Oppdragsgiver | FR-7 |
| Hjelper valgt | Avbrutt | Systemet, når oppdragsgiveren sletter kontoen | FR-4 |
| Hjelper valgt | Åpen | Systemet, når valgt hjelper sletter kontoen | FR-4 |
| Åpen / Avbrutt | (slettet) | Systemet, når oppdragsgiveren sletter kontoen | FR-4 |

Disse reglene gjelder for alle FR-ene:

- Alle regler for hvem som kan gjøre hva, og når, håndheves på serveren (NFR-5).
- Hver statusovergang sjekker gjeldende status i samme operasjon som endrer den. Kommer to handlinger samtidig (dobbeltklikk, to nettleserfaner eller to brukere), utføres bare den første. Den andre avvises med meldingen «Oppdraget er endret. Last siden på nytt.»
- Knapper som sender noe, er deaktivert mens forespørselen pågår.
- Mellomrom i starten og slutten av tekstfelt fjernes før lengden sjekkes, og felt med bare mellomrom regnes som tomme.
- Telefonnummer godtas med mellomrom og med +47 eller 0047 foran, og lagres som åtte siffer.
- Hvert ugyldig felt gir en forståelig melding rett ved feltet, og alt brukeren har fylt ut, beholdes (unntatt passord).

### 4.1 Konto og innlogging

Alle må ha konto for å bruke appen. Registrering krever at brukeren er minst 18 år (egenerklært fødselsdato). Brukeren kan slette kontoen sin selv, og da fjernes personopplysningene uten at andres dokumenterte erfaring forsvinner.

#### FR-1: Registrere konto
En person uten konto kan registrere seg med navn, e-post, passord, telefonnummer, postnummer og fødselsdato.
**Sporing:** UJ-2 · R11 · SK1 · **Prioritet:** Må

**Konsekvenser (testbare):**
- Gyldige verdier: navn 1–80 tegn; e-post i gyldig format; passord 8–64 tegn; telefonnummer åtte siffer; postnummer som finnes i lista (§3); fødselsdato som ikke er etter dagens dato og høyst 120 år tilbake.
- Fødselsdato som gir alder under 18 år, avvises. Alderen regnes i norsk tid. Den som fyller 18 i dag, godtas, og den som er født 29. februar, fyller år 1. mars i år som ikke er skuddår.
- E-post som allerede er i bruk, avvises, uten å skille mellom store og små bokstaver (`Kari@x.no` = `kari@x.no`).
- Registreringssiden har en kort tekst om personvern: hva som lagres, at navn, postnummer og profil vises for alle innloggede, at telefonnummeret bare deles med motparten når en hjelper er valgt, at beskrivelsen av et oppdrag kan sendes til en ekstern KI-tjeneste, og at kontoen kan slettes.
- «Om meg» er ikke en del av registreringen; den skrives senere i profilen (FR-22).
- Etter vellykket registrering er brukeren innlogget.

#### FR-2: Logge inn og ut
En bruker kan logge inn med e-post og passord, og logge ut.
**Sporing:** — · — · SK1 · **Prioritet:** Må

**Konsekvenser (testbare):**
- Feil e-post eller passord gir samme melding, uten å avsløre hva som var feil.
- E-post sammenlignes uten å skille mellom store og små bokstaver.
- Etter 5 mislykkede forsøk med samme e-post innen 15 minutter avvises nye forsøk i 15 minutter, med en melding om å prøve igjen senere.
- Innloggingen varer i høyst 7 dager, eller til brukeren logger ut.
- Etter utlogging får brukeren ikke tilgang til sider med innhold før hen logger inn igjen.

#### FR-3: Innlogging kreves
Alle sider og forespørsler krever innlogging, unntatt registrering, innlogging og statiske filer (stilark, skript og bilder).
**Sporing:** — · R1 · — · **Prioritet:** Må

**Konsekvenser (testbare):**
- Forespørsler uten gyldig innlogging avvises på serveren, og nettleseren sendes til innloggingssiden. Det gjelder også KI-forslag, «Mine oppdrag», redigering av profil og sletting av konto.
- En automatisk test går gjennom alle ruter uten innlogging og sjekker at de avvises.

#### FR-4: Slette egen konto
En innlogget bruker kan slette sin egen konto etter å ha bekreftet det med passordet sitt.
**Sporing:** — · R13 · SK1 (briefen: «Sletting av konto») · **Prioritet:** Må

**Konsekvenser (testbare):**
- Før sletting får brukeren beskjed om hva som skjer, inkludert at tilbakemeldinger hen har gitt, beholdes med navnet «Slettet bruker», og at kommentarene i noen tilfeller kan avsløre hvem som skrev dem.
- Brukeren må skrive passordet sitt for å bekrefte. Feil passord avviser slettingen.
- Bare brukeren selv kan slette sin konto; forsøk på å slette andres konto avvises.
- Navn, e-post, passord-hash, telefonnummer, postnummer, fødselsdato og «om meg» slettes. Testes ved at databasen etter sletting ikke inneholder den gamle e-postadressen eller telefonnummeret.
- Alle innlogginger for kontoen avsluttes, også på andre enheter, og kontoen kan ikke logge inn igjen.
- E-postadressen kan brukes til en ny registrering. Den nye kontoen har ingen kobling til data fra den slettede kontoen.
- «Slettet bruker» vises uten lenke til profil. En direkte lenke til profilen til en slettet bruker gir en forståelig melding.
- Data behandles slik:

| Situasjon | Resultat |
|---|---|
| Egne oppdrag med status Åpen | Slettes, sammen med interessene på dem |
| Egne oppdrag med status Hjelper valgt | Settes til Avbrutt, slik at hjelperen ser at oppdraget ikke blir noe av (FR-7). Brukeren vises som «Slettet bruker», og telefonnumrene skjules |
| Egne oppdrag som allerede hadde status Avbrutt | Slettes |
| Oppdrag med status Utført (som oppdragsgiver eller hjelper) | Beholdes; brukeren vises som «Slettet bruker», telefonnummeret vises ikke lenger, og oppdraget teller fortsatt i den andre partens profil |
| Interesser brukeren har meldt | Slettes |
| Brukeren er valgt hjelper på oppdrag med status Hjelper valgt | Oppdraget går tilbake til Åpen som i FR-17, og oppdragsgiveren ser merket «Hjelperen trakk seg» (FR-18) |
| Brukeren er valgt hjelper på oppdrag med status Avbrutt | Brukeren vises som «Slettet bruker» |
| Tilbakemeldinger brukeren har gitt | Beholdes som «Slettet bruker» og teller fortsatt i mottakerens gjennomsnitt |
| Tilbakemeldinger brukeren har fått | Slettes |
| Tilbakemelding som ennå ikke er gitt til brukeren | Kan ikke lenger gis (FR-20) |

### 4.2 Oppdrag

Oppdragsgiveren legger ut, redigerer og avbryter egne oppdrag.

#### FR-5: Legge ut oppdrag
En innlogget bruker kan legge ut et oppdrag.
**Sporing:** UJ-1 · — · SK2 · **Prioritet:** Må

**Konsekvenser (testbare):**
- Gyldige verdier: tittel 3–80 tegn; beskrivelse 10–1000 tegn; kategori fra lista (§3); postnummer som finnes i lista (§3), forhåndsutfylt fra profilen og mulig å endre; tidspunkt som ikke er passert og høyst 12 måneder fram i tid; godtgjørelse et heltall fra 1 til 10 000 kr, eller «uten betaling». Alle felt er obligatoriske.
- Ugyldige felt avvises med melding ved feltet, og ingenting lagres.
- Tidspunkt angis, lagres og vises i norsk tid (Europe/Oslo).
- Beskrivelsesfeltet har hjelpeteksten «Ikke skriv adresse eller telefonnummer – det avtaler dere når hjelperen er valgt.» (NFR-9).
- Et lagret oppdrag får status Åpen, og innlogget bruker er oppdragsgiver.

#### FR-6: Redigere oppdrag
Oppdragsgiveren kan redigere sitt eget oppdrag mens det har status Åpen.
**Sporing:** UJ-1 · R4 · SK2 · **Prioritet:** Må

**Konsekvenser (testbare):**
- Samme feltvalidering som FR-5. Er tidspunktet passert, må det endres før oppdraget kan lagres, og meldingen ved feltet er «Velg et nytt tidspunkt fram i tid».
- Redigering fra andre enn oppdragsgiveren avvises.
- Redigering av oppdrag med status Hjelper valgt, Utført eller Avbrutt avvises.
- Interessene beholdes ved redigering, slik at oppdragsgiveren fortsatt kan velge blant dem.
- Endres tidspunkt, godtgjørelse eller postnummer, merkes interesser som ble meldt før endringen, med «Meldt før endring» i lista over interesserte (FR-14). Den interesserte ser «Oppdraget er endret etter at du meldte interesse» under «Mine oppdrag» (FR-18), og kan trekke interessen (FR-13).
- KI-forslag finnes ikke ved redigering (FR-23).

#### FR-7: Avbryte oppdrag
Oppdragsgiveren kan avbryte sitt eget oppdrag mens det har status Åpen eller Hjelper valgt.
**Sporing:** UJ-1 · R4 · SK2 · **Prioritet:** Må

**Konsekvenser (testbare):**
- Avbrytelse krever bekreftelse, og status blir Avbrutt.
- Avbrytelse fra andre enn oppdragsgiveren avvises.
- Avbrytelse av oppdrag med status Utført eller Avbrutt avvises.
- Etter avbrytelse skjules telefonnumrene (FR-16), og oppdraget kan ikke endres.
- Avbrytes oppdraget fra Hjelper valgt, beholdes koblingen til valgt hjelper. Hen ser oppdraget med status Avbrutt under «Oppdrag jeg hjelper med» og kan åpne detaljene, uten telefonnumre.

#### FR-8: Utgåtte oppdrag
Et oppdrag med status Åpen der tidspunktet er passert, er utgått.
**Sporing:** UJ-1 · R3 · SK3 (briefen: «Utgåtte oppdrag») · **Prioritet:** Må

**Konsekvenser (testbare):**
- Utgåtte oppdrag vises ikke i oversikten.
- Nye interesser for et utgått oppdrag avvises, og oppdragsgiveren kan ikke velge hjelper (FR-15).
- Under «Mine oppdrag» er oppdraget merket «Tidspunktet er passert», og oppdragsgiveren kan endre tidspunktet (FR-6) eller avbryte (FR-7). Får oppdraget et nytt tidspunkt som ikke er passert, vises det igjen i oversikten.

#### FR-9: Innsyn i oppdragsdetaljer
Hvem som ser detaljene i et oppdrag, avhenger av status og rolle.
**Sporing:** UJ-2 · R9 · — · **Prioritet:** Må

**Konsekvenser (testbare):**
- Detaljene viser alle feltene i oppdraget og status. De viser også oppdragsgiverens navn, antall fullførte oppdrag og gjennomsnittlig vurdering (som i FR-21), med lenke til oppdragsgiverens profil.
- Status Åpen: alle innloggede ser detaljene, men bare oppdragsgiveren ser lista over interesserte.
- Andre statuser: bare oppdragsgiveren og valgt hjelper ser detaljene. Forespørsler fra andre brukere avvises.
- Interesserte som ikke ble valgt, ser bare tittel og status under «Mine oppdrag» (FR-18).

### 4.3 Finne oppdrag

Hjelperen ser åpne oppdrag i nærheten, sortert etter når de skal gjøres. «I nærheten» betyr samme postnummer i v1.

#### FR-10: Oppdragsoversikt
En innlogget bruker ser som standard åpne oppdrag i sitt eget postnummer.
**Sporing:** UJ-2 · — · SK3 · **Prioritet:** Må

**Konsekvenser (testbare):**
- Bare oppdrag med status Åpen der tidspunktet ikke er passert, vises.
- Sortering er etter tidspunkt, tidligste først. Oppdrag med samme tidspunkt sorteres etter når de ble lagt ut, eldste først.
- Hvert oppdrag i oversikten viser tittel, kategori, tidspunkt og godtgjørelse.
- Brukerens egne oppdrag vises ikke i oversikten. De finnes under «Mine oppdrag» (FR-18).
- Ingen treff gir en tomtilstand med forklaring og forslag (for eksempel å velge et annet postnummer).

**Kjent begrensning:** Naboer på hver sin side av en postnummergrense ser ikke hverandres oppdrag som standard. Det godtas i v1; kart og avstand er utsatt (§6.2).

#### FR-11: Filtrere oppdrag
Brukeren kan filtrere oversikten på kategori og velge et annet postnummer.
**Sporing:** — · — · SK3 · **Prioritet:** Må

**Konsekvenser (testbare):**
- Filter på kategori viser bare oppdrag i valgt kategori.
- Valgt postnummer erstatter eget postnummer i oversikten. Et postnummer som ikke finnes i lista (§3), avvises med melding.
- Filtrene kan kombineres.

### 4.4 Interesse og valg av hjelper

Hjelpere melder interesse, og oppdragsgiveren velger én av dem. Først da deles telefonnumrene.

#### FR-12: Melde interesse
En innlogget bruker kan melde interesse for et oppdrag, eventuelt med en kort melding til oppdragsgiveren.
**Sporing:** UJ-2 · R2, R3 · SK4 · **Prioritet:** Må

**Konsekvenser (testbare):**
- Interesse for eget oppdrag avvises.
- Ny interesse fra en bruker som allerede har interesse for oppdraget, avvises.
- Interesse avvises hvis status ikke er Åpen, eller tidspunktet er passert.
- En hjelper som oppdragsgiveren har fjernet (FR-17), kan ikke melde interesse for samme oppdrag igjen; forsøket avvises. Hen ser detaljene som andre innloggede (FR-9), men i stedet for knappen «Meld interesse» står det «Du er ikke lenger valgt til dette oppdraget». En hjelper som trakk seg selv, kan melde interesse på nytt.
- Meldingen er valgfri og maks 500 tegn.
- Etter at hjelperen har meldt interesse, ser hen «Du har meldt interesse» i stedet for knappen «Meld interesse», og oppdraget vises under «Oppdrag jeg hjelper med».

#### FR-13: Trekke interesse
En interessert kan trekke interessen sin.
**Sporing:** — · R3 · SK4 · **Prioritet:** Må

**Konsekvenser (testbare):**
- Tillatt bare mens status er Åpen og tidspunktet ikke er passert; ellers avvises det.
- Etter tilbaketrekking er interessen borte fra lista over interesserte (FR-14), og brukeren kan melde interesse på nytt.

#### FR-14: Se interesserte
Oppdragsgiveren ser alle som har meldt interesse for sitt oppdrag.
**Sporing:** UJ-1 · R9 · SK4 · **Prioritet:** Må

**Konsekvenser (testbare):**
- For hver interessert vises navn, antall fullførte oppdrag, gjennomsnittlig vurdering (som i FR-21, eller «Ingen vurderinger ennå»), meldingen og eventuelt merket «Meldt før endring» (FR-6), med lenke til profilen.
- Lista er sortert etter når interessen ble meldt, eldste først.
- Lista vises ikke for andre enn oppdragsgiveren.
- Ingen interesserte gir en tomtilstand med forklaring.

#### FR-15: Velge hjelper
Oppdragsgiveren kan velge nøyaktig én av de interesserte.
**Sporing:** UJ-1 · R3, R5 · SK5 · **Prioritet:** Må

**Konsekvenser (testbare):**
- Valget krever bekreftelse («Velge Amir? Dere får se hverandres telefonnummer.»).
- Status blir Hjelper valgt, og oppdraget forsvinner fra oversikten.
- Valg avvises hvis brukeren ikke er oppdragsgiver, status ikke er Åpen, tidspunktet er passert, eller den valgte ikke har meldt interesse.
- Hvis statusen allerede er endret (for eksempel ved dobbeltklikk), avvises valget, og det finnes fortsatt bare én valgt hjelper (§4.0).

#### FR-16: Dele telefonnummer
Oppdragsgiveren og valgt hjelper ser hverandres telefonnummer.
**Sporing:** UJ-1, UJ-2 · R10 · SK5 · **Prioritet:** Må

**Konsekvenser (testbare):**
- Telefonnumrene vises bare for disse to, og bare mens status er Hjelper valgt eller Utført.
- Når hjelperen fjernes eller trekker seg, eller oppdraget avbrytes, skjules numrene igjen.
- Telefonnummeret til en slettet bruker vises ikke (FR-4).
- Ingen andre steder i appen viser telefonnummer, e-post eller fødselsdato, heller ikke i svar fra serveren. Unntaket er at brukeren ser sine egne opplysninger når hen redigerer profilen sin (FR-22).

#### FR-17: Fjerne hjelper eller trekke seg
Mens status er Hjelper valgt, kan oppdragsgiveren fjerne valgt hjelper, og valgt hjelper kan trekke seg.
**Sporing:** UJ-2 · R6 · SK6 · **Prioritet:** Må

**Konsekvenser (testbare):**
- Begge handlinger krever bekreftelse.
- Status blir Åpen, og oppdraget vises igjen i oversikten hvis tidspunktet ikke er passert.
- Den tidligere valgte hjelperens interesse slettes; de andre interessene beholdes.
- Telefonnumrene skjules (FR-16).
- Hva begge parter ser etterpå under «Mine oppdrag», står i FR-18.
- Forsøk fra andre, eller ved annen status enn Hjelper valgt, avvises.

### 4.5 Mine oppdrag

Én side der brukeren ser egne oppdrag og oppdrag hen hjelper med. Uten varsler (§6.2) er dette stedet brukeren ser endringer.

#### FR-18: Mine oppdrag
En innlogget bruker ser sine oppdrag i to faner.
**Sporing:** UJ-1, UJ-2 · R9 · — (briefen: «Viktigste skjermbilder» nr. 4) · **Prioritet:** Må

**Konsekvenser (testbare):**
- «Oppdrag jeg har lagt ut» viser alle egne oppdrag med status, antall interesserte og navnet på valgt hjelper hvis en er valgt.
- «Oppdrag jeg hjelper med» viser oppdrag der brukeren har interesse, er valgt hjelper eller er tidligere valgt hjelper, med brukerens egen situasjon. Hvert oppdrag passer i nøyaktig én rad:

| Brukerens situasjon | Vises som | Detaljer |
|---|---|---|
| Har interesse, status Åpen, tidspunktet ikke passert | «Venter på svar» | Kan åpnes (FR-9), og interessen kan trekkes (FR-13) |
| Har interesse, utgått oppdrag (FR-8) | «Tidspunktet er passert» | Kan åpnes; interessen kan ikke trekkes (FR-13) |
| Har interesse, og oppdraget har en annen valgt hjelper (status Hjelper valgt, Utført eller Avbrutt) | «Ikke valgt» | Bare tittel og status |
| Har interesse, status Avbrutt uten valgt hjelper | «Avbrutt» | Bare tittel og status |
| Valgt hjelper, status Hjelper valgt | «Du er valgt» | Kan åpnes, med telefonnumre (FR-16) |
| Valgt hjelper, status Utført | «Utført» | Kan åpnes |
| Valgt hjelper, status Avbrutt | «Avbrutt» | Kan åpnes, uten telefonnumre (FR-7) |
| Fjernet som valgt hjelper (FR-17) | «Du er ikke lenger valgt» | Som for andre innloggede (FR-9); kan ikke melde interesse igjen (FR-12) |
| Trakk seg som valgt hjelper (FR-17), uten ny interesse | «Du trakk deg» | Som for andre innloggede (FR-9); kan melde interesse på nytt (FR-12) |

- Merker som vises i tillegg:
  - «Tidspunktet er passert» på egne utgåtte oppdrag (FR-8).
  - «Er jobben gjort?» for begge parter på oppdrag med status Hjelper valgt der tidspunktet er passert (FR-19).
  - «Gi tilbakemelding» for oppdragsgiveren og valgt hjelper på oppdrag med status Utført, så lenge brukeren ikke har gitt tilbakemelding, men ikke når motparten er «Slettet bruker» (FR-20).
  - «Hjelperen trakk seg» hos oppdragsgiveren når valgt hjelper har trukket seg eller slettet kontoen (FR-17, FR-4). Merket forsvinner når en ny hjelper er valgt, eller oppdraget avbrytes.
  - «Oppdraget er endret etter at du meldte interesse» hos den interesserte (FR-6).
- Sortering i begge faner: først oppdrag med merke, deretter oppdrag med status Åpen eller Hjelper valgt etter tidspunkt, tidligste først, og til slutt oppdrag med status Utført eller Avbrutt, nyeste tidspunkt først.
- Tom fane gir en tomtilstand med forklaring og lenke videre: «Oppdrag jeg har lagt ut» lenker til «Legg ut oppdrag», og «Oppdrag jeg hjelper med» lenker til oversikten.

### 4.6 Fullføre og gi tilbakemelding

Oppdraget markeres som utført, og begge parter kan gi hverandre en tilbakemelding som vises i profilen.

#### FR-19: Markere som utført
Valgt hjelper kan markere oppdraget som Utført fra dagen for tidspunktet. Når tidspunktet er passert, kan også oppdragsgiveren gjøre det.
**Sporing:** UJ-1, UJ-2 · R7 (avvik, §9.2) · SK7 · **Prioritet:** Må

**Konsekvenser (testbare):**
- Markeringen krever bekreftelse («Marker som utført? Det kan ikke angres.»).
- Valgt hjelper kan markere fra kl. 00:00 norsk tid på datoen for tidspunktet. Tidligere forsøk avvises.
- Oppdragsgiveren kan markere når tidspunktet er passert. Tidligere forsøk avvises.
- Tillatt bare når status er Hjelper valgt. Forsøk fra andre, eller ved annen status, avvises.
- Når oppdraget er markert som Utført, kan det ikke endres, og begge parter kan gi tilbakemelding (FR-20).

#### FR-20: Gi tilbakemelding
Oppdragsgiveren og valgt hjelper kan gi hverandre én tilbakemelding per oppdrag.
**Sporing:** UJ-1, UJ-2 · R8 · SK8 · **Prioritet:** Må

**Konsekvenser (testbare):**
- Vurderingen er 1–5 stjerner. Hver stjerne er en stor knapp som kan brukes med tastatur og har tekst for skjermleser («4 av 5 stjerner»), jf. NFR-7. Et trykk på en stjerne velger bare vurderingen; tilbakemeldingen lagres først når brukeren trykker «Send». Kommentar er valgfri, maks 500 tegn.
- Tillatt bare når status er Utført, bare mellom oppdragsgiver og valgt hjelper, og bare én gang per person per oppdrag. Andre forsøk avvises.
- Tilbakemelding til en bruker som har slettet kontoen, avvises.
- Etter «Send» får brukeren en kvittering («Takk! Tilbakemeldingen er lagt til i Amirs profil.»), tilbakemeldingen vises straks i mottakerens profil, og gjennomsnittet oppdateres.

### 4.7 Profil og dokumentert erfaring

Profilen er «erfaringsbeviset» en hjelper kan vise til i en jobbsøknad.

**Kjent begrensning – erfaringen er ikke verifisert:** Brukerne er ikke identitetsverifisert i v1, og navn og fødselsdato er egenerklært. Én person kan også opprette flere kontoer og registrere oppdrag mellom dem. Profilen dokumenterer derfor hva andre brukere har gitt tilbakemelding på i appen; den er ikke en attest. Det står i profilen at erfaringen er registrert av brukere i Nabolagshelten. Identitetsverifisering er utsatt (§6.2).

**Kjent begrensning – profilen kan bare ses av innloggede:** Alt innhold krever innlogging (R1, FR-3), så en arbeidsgiver må ha konto for å se profilen. I v1 kan hjelperen vise profilen på sin egen skjerm eller som skjermbilde. Eksport til PDF er utsatt (§6.2).

**Kjent begrensning – tilbakemeldinger kan ikke endres:** Brukerne kan ikke endre eller fjerne en tilbakemelding, og rapportering er utsatt (§6.2). Ber noen om å få fjernet en krenkende kommentar eller en kommentar med personopplysninger, kan gruppen fjerne kommentaren direkte i databasen. Vurderingen beholdes.

#### FR-21: Vise profil
En innlogget bruker kan se sin egen profil og profilen til andre brukere.
**Sporing:** UJ-1, UJ-2 · R9 · SK9 · **Prioritet:** Må

**Konsekvenser (testbare):**
- Egen profil ser ut som for andre, med lenke til «Rediger profil» (FR-22) og knappen «Logg ut» (FR-2). Menyvalget «Profil» (NFR-11) går til egen profil.
- Profilen viser navn, postnummer med poststed, «om meg», antall fullførte oppdrag per kategori, gjennomsnittlig vurdering og alle mottatte tilbakemeldinger, nyeste først.
- For hver tilbakemelding vises vurdering, kommentar, hvem som ga den, dato, og om den gjaldt brukeren som hjelper eller som oppdragsgiver.
- Gjennomsnittet regnes ut fra alle tilbakemeldinger brukeren har fått, både som hjelper og som oppdragsgiver. Det vises med én desimal og desimalkomma, sammen med antall vurderinger («4,3 av 5, 7 vurderinger»). Samme visning brukes i FR-9 og FR-14.
- Bruker uten vurderinger vises med «Ingen vurderinger ennå».
- «Fullførte oppdrag» teller oppdrag med status Utført der brukeren var valgt hjelper. Oppdrag brukeren selv har lagt ut, teller ikke.
- Profilen har en kort tekst om at fullførte oppdrag og tilbakemeldinger er registrert av brukere i Nabolagshelten og ikke er verifisert.
- Tilbakemeldinger fra brukere som har slettet kontoen, vises med «Slettet bruker», uten lenke (FR-4).
- Profilen viser aldri telefonnummer, e-post eller fødselsdato.

#### FR-22: Redigere egen profil
En innlogget bruker kan skrive og endre en kort tekst om seg selv («om meg»), og endre postnummer og telefonnummer.
**Sporing:** — · — · — (briefen: «Profil og dokumentert erfaring», «Nærhet») · **Prioritet:** Bør

**Konsekvenser (testbare):**
- «Om meg» er valgfri, maks 500 tegn. Er den tom, vises ikke feltet i profilen.
- Postnummer og telefonnummer valideres som ved registrering (FR-1); ugyldig verdi avvises med melding ved feltet.
- Nytt postnummer brukes straks som standard i oversikten (FR-10) og forhåndsutfylles i nye oppdrag (FR-5). Oppdrag som allerede er lagt ut, beholder sitt postnummer.
- Nytt telefonnummer vises straks for motparten i oppdrag med status Hjelper valgt eller Utført (FR-16).
- På siden for å redigere profilen ser brukeren sine egne opplysninger, også e-post og telefonnummer.
- Navn, e-post og fødselsdato kan ikke endres i v1.
- Bare brukeren selv kan endre sin profil; andre forsøk avvises.

### 4.8 KI-forslag

I skjemaet for nytt oppdrag kan brukeren få forslag til kategori, tittel og beskrivelse. KI-en er et hjelpemiddel: brukeren bestemmer alltid selv, og alle felt kan fylles inn uten KI. FR-23–FR-26 har prioritet Bør og bygges etter at kjerneflyten er ferdig og stabil (§6.1).

#### FR-23: Be om forslag
I skjemaet for nytt oppdrag kan brukeren trykke «Få forslag» når beskrivelsesfeltet har minst 10 tegn.
**Sporing:** UJ-1 · R12 · SK10 · **Prioritet:** Bør

**Konsekvenser (testbare):**
- Funksjonen finnes bare når et oppdrag legges ut, ikke ved redigering.
- Knappen er deaktivert når beskrivelsen har færre enn 10 tegn.
- Ved knappen står det, før brukeren trykker, at teksten i beskrivelsesfeltet sendes til en ekstern KI-tjeneste. I mock-modus står det i stedet at teksten ikke sendes ut.
- Bare teksten i beskrivelsesfeltet sendes. Navn, e-post, telefonnummer og andre profilopplysninger legges aldri til.
- Mens forslaget hentes, er knappen deaktivert og viser «Lager forslag …», og skjermleseren leser opp at forslag lages (NFR-7).
- Serveren tillater høyst 20 forslag per bruker per time. Flere forespørsler avvises med en vennlig melding.
- Prompten ligger i en egen fil i koden, slik at den er lett å finne og forbedre.

#### FR-24: Bruke eller forkaste forslag
Forslagene vises ved feltene, og brukeren velger «Bruk» eller «Forkast» for hvert.
**Sporing:** UJ-1 · R12 · SK10 · **Prioritet:** Bør

**Konsekvenser (testbare):**
- På smal skjerm vises hvert forslag under feltet det gjelder (NFR-6).
- Et forslag fyller aldri inn et felt før brukeren trykker «Bruk».
- Et eventuelt tips fra KI-tjenesten (for eksempel «Skriv gjerne hvor stor innkjørselen er») vises sammen med forslagene.
- Forslaget til beskrivelse omformulerer bare det brukeren skrev, uten nye opplysninger; det som mangler, kommer som tips. Forslagene er på norsk bokmål. Testes manuelt med fem faste eksempeltekster mot språkmodellen, og resultatet dokumenteres.
- Etter «Bruk» kan feltet fortsatt redigeres.
- KI-tjenesten lagrer eller publiserer aldri noe; oppdraget lagres bare når brukeren trykker «Publiser» (FR-5).

#### FR-25: Kontroll av KI-svar
Svaret fra KI-tjenesten valideres før det vises, også i mock-modus.
**Sporing:** UJ-1 · R12 · SK10 (briefen: «Kontroll av svaret fra KI-en») · **Prioritet:** Bør

**Konsekvenser (testbare):**
- Svaret må være gyldig JSON med kategori (fra lista i §3), tittel og beskrivelse. Tittel og beskrivelse må oppfylle de samme reglene som i FR-5: tittel 3–80 tegn, beskrivelse 10–1000 tegn, ikke bare mellomrom. Svaret kan ha et tips på maks 200 tegn.
- Ugyldig JSON, ukjent kategori eller tekst som bryter reglene, regnes som ugyldig svar og vises ikke.
- Får appen ikke svar innen 10 sekunder, avbrytes forespørselen (tidsavbrudd), og et svar som kommer senere, vises ikke.
- Ved ugyldig svar, tidsavbrudd eller feil i tjenesten vises en vennlig melding («Vi fikk ikke laget forslag akkurat nå. Du kan fylle inn selv.»), skjemaet beholder det brukeren har skrevet, og oppdraget kan lagres manuelt.
- Forslag og tips vises som ren tekst, aldri som HTML (NFR-12).
- Feiltilfellene testes automatisk ved at testene bytter ut KI-tjenesten med en testdobbel som svarer med ugyldig JSON, ukjent kategori, for lang tekst, en feil, og et svar som kommer for sent.

#### FR-26: Mock-modus
Når ingen API-nøkkel er satt, brukes mock-modus, som lager svar etter faste regler.
**Sporing:** — · — · SK10 (briefen: «Mock-modus») · **Prioritet:** Bør

**Konsekvenser (testbare):**
- En tom API-nøkkel, eller plassholderen fra `.env.example`, regnes som ingen nøkkel.
- Kategorien er den første i tabellen, regnet ovenfra, som har minst ett nøkkelord i teksten. Et nøkkelord treffer når et ord i teksten begynner med det, uten å skille mellom store og små bokstaver. «Snømåking» treffer derfor «snø», og «hundelufting» treffer «hund».

| Kategori | Nøkkelord |
|---|---|
| Snømåking | snø, måke, brøyte, strø |
| Hage | hage, plen, gress, klippe, hekk, løv, luke |
| Bærehjelp/flytting | bære, flytte, flytting, sofa, møbel, eske |
| Dyrepass | hund, katt, lufte, dyr, mate |
| Teknologihjelp | pc, data, ipad, nettbrett, mobil, wifi, tv, skriver |
| Annet | Ingen nøkkelord treffer |

- Kjente feiltreff godtas og står som testtilfeller: «hundre» gir Dyrepass, og «strømbrudd» gir Snømåking.
- Tittelforslaget er første setning i teksten, uten tegnet som avslutter den, med stor forbokstav og forkortet til maks 80 tegn. En setning slutter ved punktum, utropstegn eller spørsmålstegn fulgt av mellomrom og stor bokstav, eller ved linjeskift, slik at «kl. 07:30» ikke kutter setningen. Er første setning kortere enn 3 tegn, er tittelforslaget kategorinavnet.
- Beskrivelsesforslaget er teksten med stor forbokstav. Slutter teksten ikke på punktum, utropstegn eller spørsmålstegn, og er den kortere enn 1000 tegn, legges det til punktum.
- Mock-modus gir ikke tips.
- «måke snø i innkjørselen» gir kategorien Snømåking og tittelforslaget «Måke snø i innkjørselen». En tekst uten nøkkelord gir Annet.
- Samme tekst gir alltid samme svar. Automatiske tester kjører alltid i mock-modus, også når `.env` har en API-nøkkel; unntaket er testdoblene i FR-25.

## 5. Tverrgående kvalitetskrav

Kvalitetskravene gjelder for alle FR-ene og er med i Definition of Done for hver story.

### NFR-1: Kjørbar på en ren maskin
Appen kan startes lokalt ved å følge README, uten betalte tjenester, eksterne kontoer eller gruppens egne nøkler.
**Sporing:** briefen: «Kvalitetskrav» · **Prioritet:** Må

- Appen er en vanlig webapp med én database som kjøres lokalt.
- README har forutsetninger med versjoner, eksakte kommandoer, kommandoen som laster eksempeldataene (NFR-2), og kommandoen som kjører de automatiske testene.
- Uten API-nøkkel bruker KI-funksjonen mock-modus (FR-26), og README sier at det er standard.

*Testes ved:* Noen utenfor gruppen følger README fra start på en ren maskin eller i en container, og har appen i gang med eksempeldata innen 15 minutter. Operativsystem og tidsbruk skrives i testrapporten (SM-3).

### NFR-2: Eksempeldata og testbrukere
Repoet har oppdiktede eksempeldata, slik at hvert steg i kjerneflyten kan prøves uten å lage data først.
**Sporing:** briefen: «Kvalitetskrav» · **Prioritet:** Må

- Minst 6 testbrukere i 2–3 postnumre, og 10–15 oppdrag.
- Åpne oppdrag i alle kategorier, og minst ett oppdrag med flere interesserte.
- Minst ett oppdrag med status Hjelper valgt, ett Utført med tilbakemelding fra begge parter, ett Utført der tilbakemelding ennå ikke er gitt, og ett Avbrutt.
- Minst ett utgått oppdrag, og minst ett oppdrag med status Hjelper valgt der tidspunktet er passert («Er jobben gjort?»).
- Minst én bruker med vurderinger og én uten («Ingen vurderinger ennå»).
- Tidspunktene regnes ut fra når dataene lastes inn (for eksempel «i morgen kl. 10», «om 5 dager» og «i går» for det utgåtte oppdraget), slik at de åpne oppdragene fortsatt er åpne når sensor kjører appen. Dataene kan lastes inn på nytt med én kommando.
- README har innloggingsinformasjon for testbrukerne og en kort beskrivelse av hva hver testbruker kan brukes til å prøve. Testpassordene er oppdiktede og merket «bare for lokal testing»; de er ikke hemmeligheter slik NFR-3 bruker ordet.

*Testes ved:* En automatisk test laster eksempeldataene og sjekker at hver situasjon i lista over finnes.

### NFR-3: Ingen hemmeligheter i repoet
Hemmeligheter, som API-nøkler, ligger i `.env`, som ikke er i repoet.
**Sporing:** briefen: «Kvalitetskrav» · **Prioritet:** Må

- `.env.example` viser alle variabler uten ekte verdier.
- `.gitignore` holder ute `.env`, avhengigheter og byggmapper.

*Testes ved:* Git-historikken skannes etter nøkler og passord (for eksempel med gitleaks) før innlevering, og resultatet dokumenteres.

### NFR-4: Sikker lagring av passord
Passord lagres aldri i klartekst, bare som hash med en algoritme laget for passord (for eksempel bcrypt eller Argon2; valget tas i arkitekturen).
**Sporing:** briefen: «Kvalitetskrav» · **Prioritet:** Må

*Testes ved:* En automatisk test sjekker at passordfeltet i databasen ikke inneholder passordet.

### NFR-5: Regler håndheves på serveren
Alle regler i FR-ene for hvem som kan gjøre hva, og når, sjekkes på serveren, ikke bare ved å skjule knapper.
**Sporing:** briefen: R1–R13 · **Prioritet:** Må

*Testes ved:* Hver regel R1–R13 i briefen har minst én automatisk test mot kravene den er koblet til i sporingstabellen (§9.1), unntatt regler for krav som er kuttet etter §6.1. Testene sender forespørslene direkte til serveren.

### NFR-6: Responsiv
Hele kjerneflyten kan gjennomføres i vanlig nettleser fra 360 px bredde (mobil) til PC, uten vannrett rulling. Ingen egen mobilapp.
**Sporing:** briefen: «Kvalitetskrav» · **Prioritet:** Må

*Testes ved:* Manuell gjennomgang av UJ-1 og UJ-2 ved 360, 768 og 1280 px bredde, dokumentert med skjermbilder.

### NFR-7: Universell utforming
Appen følger WCAG 2.1 nivå AA.
**Sporing:** sensorveiledningen, kriterium 4 · **Prioritet:** Må

- Kontrast minst 4,5:1 for tekst.
- Alt kan brukes med tastatur, med synlig fokus. Det gjelder også valg av dato og klokkeslett.
- Alle skjemafelt har synlige etiketter; feilmeldinger står ved feltet og er knyttet til det.
- Knapper har tekst, ikke bare ikoner; bilder og ikoner med mening har alt-tekst.
- Brødtekst er minst 18 px, og knapper og andre trykkflater er minst 48 px høye (som i skissene).
- Siden kan forstørres til 200 % uten at innhold forsvinner.
- Status vises alltid med ord («Åpen», «Hjelper valgt»), ikke bare med farge.
- Statusmeldinger («Lager forslag …», kvitteringer og feil etter innsending) leses opp av skjermleser.
- Bekreftelsesdialoger flytter fokus inn i dialogen og tilbake etterpå.
- Sidens språk er angitt som norsk bokmål (`nb`).
- Lister og faner uten innhold har en tomtilstand med forklaring.

*Testes ved:* Automatisk verktøy (SM-5), manuell tastaturgjennomgang av kjerneflyten og manuell gjennomgang av UJ-1 med skjermleser (NVDA eller VoiceOver). Begge de manuelle gjennomgangene dokumenteres.

### NFR-8: Tydelig og enkelt språk
All tekst i appen er på norsk bokmål, med enkelt språk.
**Sporing:** briefen: «Målgruppe» (Kari) · **Prioritet:** Må

- Knapper og overskrifter bruker ordene i ordlisten (§3) og skissene, for eksempel «Meld interesse», ikke «Send forespørsel».
- Hver handling gir en tydelig kvittering (for eksempel «Takk! Tilbakemeldingen er lagt til i Amirs profil.»).
- Handlinger som ikke kan angres, krever bekreftelse: avbryte oppdrag, velge hjelper, fjerne hjelper, trekke seg, markere som utført og slette konto. For tilbakemelding regnes «Send» etter at stjernene er valgt, som bekreftelse (FR-20).

*Testes ved:* Manuell gjennomgang av kjerneflyten mot ordlisten, dokumentert.

### NFR-9: Personvern
Appen lagrer bare navn, e-post, hashet passord, telefonnummer, postnummer, fødselsdato og innhold brukeren selv legger inn, pluss data appen trenger for å virke (innlogginger, mislykkede innloggingsforsøk, antall KI-forslag og tidligere valgte hjelpere). Appen ber aldri om eksakt adresse.
**Sporing:** briefen: «Personvern og sikkerhet i v1» · **Prioritet:** Må

- Hjelpeteksten ved beskrivelsesfeltet ber brukeren ikke skrive adresse eller telefonnummer (FR-5).
- Eksempeldata inneholder ingen ekte personopplysninger.

*Testes ved:* Gjennomgang av databaseskjemaet mot lista over, dokumentert.

### NFR-10: Robust mot ugyldig input
All input valideres på serveren, også når nettleseren allerede har sjekket den. Ugyldig input eller uventede feil gir en forståelig melding til brukeren, aldri en teknisk feilmelding eller krasj.
**Sporing:** sensorveiledningen, kriterium 3 · **Prioritet:** Må

*Testes ved:* Automatiske tester som sender ugyldige verdier til hvert skjema og hver handling.

### NFR-11: Navigasjon
Etter innlogging har appen en fast meny med tre valg: Oppdrag, Mine oppdrag og Profil.
**Sporing:** briefen: «Viktigste skjermbilder»; sensorveiledningen, kriterium 4 · **Prioritet:** Må

*Testes ved:* Manuell gjennomgang av kjerneflyten, og den automatiske tilgjengelighetstesten (SM-5).

### NFR-12: Sikkerhet mot vanlige angrep
Tekst fra brukere og fra KI-tjenesten vises alltid som tekst, aldri som HTML, og handlinger som endrer data, kan ikke utløses fra andre nettsteder.
**Sporing:** sensorveiledningen, kriterium 3 · **Prioritet:** Må

*Testes ved:* En automatisk test sjekker at `<script>alert(1)</script>` i tittel, beskrivelse, melding, kommentar og «om meg» vises som tekst. Mekanismen mot forespørsler fra andre nettsteder velges i arkitekturen og testes der.

## 6. Omfang og avgrensning

### 6.1 Med i v1

Alle FR-er og NFR-er i dette dokumentet er med i v1, prioritert slik:

| Prioritet | Krav | Betyr |
|---|---|---|
| Må | FR-1–FR-21, NFR-1–NFR-12 | Kjerneflyten og kvalitetskravene. Bygges først; v1 er ikke ferdig uten dem. |
| Bør | FR-22, FR-23–FR-26 | Bygges når kjerneflyten er ferdig og stabil. |

Blir tiden for knapp, kuttes Bør-krav før noe Må-krav, og hvert kutt føres i endringsloggen med begrunnelse. Et kutt endrer andre krav slik:

- **Kuttes FR-22:** Ingen bruker får skrevet «om meg», og postnummer og telefonnummer kan ikke endres etter registrering. «Om meg» og redigering av profil tas da ut av FR-21, NFR-12 og SM-5.
- **Kuttes FR-23–FR-26:** Appen har ingen KI-funksjon. R12 og SK10 gjelder ikke, NFR-5 og SM-2 gjelder da R1–R11 og R13, og SM-4 måler UJ-1 steg 1 og 3. Avviket føres i §9.2.

### 6.2 Utsatt til senere trinn

- Deling og utlån av utstyr (trinn 2)
- Identitetsverifisering med BankID eller Vipps
- Brukere under 18 år med godkjenning fra foresatte
- Kart og avstandsbasert matching (erstatter postnummer)
- Meldinger/chat i appen
- Varsler på e-post eller push – uten varsler må brukeren selv åpne «Mine oppdrag» for å se endringer
- Glemt passord (tilbakestilling via e-post) – krever utsending av e-post, som er utsatt sammen med varsler. I v1 kan passord ikke tilbakestilles; passordene til testbrukerne står i README (NFR-2). En bruker som har glemt passordet, kan verken logge inn, slette kontoen (FR-4) eller registrere seg på nytt med samme e-post. Da må gruppen hjelpe manuelt ved å tilbakestille passordet eller slette kontoen direkte i databasen
- Rapportering og blokkering av brukere – i v1 bygges tillit gjennom vurderinger og tilbakemeldinger (FR-20, FR-21), og oppdragsgiveren velger selv hjelper og kan fjerne hen (FR-15, FR-17)
- Eksport av erfaringsoversikt til PDF
- Flere KI-funksjoner (forslag til godtgjørelse, sjekk av upassende innhold, KI-generert CV-tekst)

### 6.3 Ikke-mål

Nabolagshelten har ingen betaling i appen. Den skal heller ikke være en jobbportal, en bemanningsplattform, en markedsplass for kjøp og salg, håndverkere eller utleie, et sosialt medium, eller et sted for store eller komplekse oppdrag.

## 7. Suksessmål

**Primære**
- **SM-1:** Alle krav FR-1–FR-26 og NFR-1–NFR-12 er dekket av akseptansekriterier i stories, og testene for dem passerer. Bør-krav som er kuttet etter §6.1, er unntatt. Dermed er også suksesskriteriene i briefen (SK1–SK10) oppfylt, med avvikene i §9.2 og bortsett fra det som er kuttet.
- **SM-2:** Hver regel R1–R13 har minst én automatisk test som passerer, unntatt R12 hvis KI-forslag er kuttet (§6.1). Validerer NFR-5.
- **SM-3:** En person utenfor gruppen får appen i gang ved å følge README, uten hjelp. Validerer NFR-1, NFR-2.

**Sekundære**
- **SM-4:** I en brukertest med minst to testpersoner utenfor gruppen, der minst én er over 60 år eller lite vant med apper, klarer hver av dem å legge ut et oppdrag (UJ-1, steg 1–3) på under to minutter på mobil eller nettbrett. Tiden måles fra testpersonen trykker «Legg ut oppdrag» til oppdraget er publisert. Enhet, nettleser og tid dokumenteres som manuell test. Validerer FR-5, NFR-6, NFR-7.
- **SM-5:** Automatisk tilgjengelighetstest (for eksempel axe) finner ingen feil på nivåene «serious» eller «critical» på disse sidene: de fem viktigste skjermbildene i briefen (oppdragsoversikt, nytt oppdrag, oppdragsdetaljer, Mine oppdrag og profil), registrering, innlogging, redigering av profil, et skjema med valideringsfeil og hver bekreftelsesdialog. Validerer NFR-7, NFR-11.

**Motmål (skal ikke optimeres)**
- **SM-C1:** Andel oppdrag laget med KI-forslag. Skal ikke presses opp; KI-en er et valgfritt hjelpemiddel, og manuell utfylling skal være like enkel. Måles ikke, men brukes som retningslinje i UX-steget. Motvekt til SM-4.
- **SM-C2:** Antall funksjoner. Flere funksjoner enn i §6.1 skal ikke prioriteres før SM-1–SM-3 er nådd. Motvekt til SM-1.

## 8. Åpne punkter til neste fase

Ingen åpne spørsmål blokkerer UX, arkitektur eller stories. Disse punktene følges opp i neste fase:

- **UX-steget (`bmad-ux`) oppdaterer skissene:**
  - Tilbakemelding: 1–5 stjerner som store knapper og en egen «Send»-knapp, ikke tallknapper (FR-20, NFR-7).
  - Oversikten: tidspunkt som dato og klokkeslett, ikke «Fleksibelt denne uken» (FR-5).
  - Tomtilstanden i oversikten: lenken «Se alle postnumre» fjernes, fordi filteret alltid gjelder ett postnummer (FR-11).
  - Eksemplet på KI-forslag legger til opplysninger brukeren ikke skrev («Spade finnes»), og rettes (FR-24).
  - «Mine oppdrag» viser brukerens egen situasjon og merkene i FR-18. Spørsmål 3 i skissene (merke for ny interesse i menyen) avgjøres her.
  - Skjemaet for nytt oppdrag skal ikke vise for mange felter på én skjerm. Skissene foreslår to steg; endelig oppsett avgjøres her.
  - Skjermene som mangler: registrering, redigering av profil og sletting av konto (med passord).
- **Arkitekturen (`bmad-architecture`) avgjør:** kilden til lista over postnumre, mekanismen mot forespørsler fra andre nettsteder (NFR-12), og håndtering av sommertid og tegnsett.

## 9. Forhold til briefen

### 9.1 Sporing

| Regel i briefen | Innhold (kort) | Krav |
|---|---|---|
| R1 | Innlogging kreves | FR-3 |
| R2 | Ikke interesse for eget oppdrag | FR-12 |
| R3 | Én interesse per oppdrag; melde og trekke bare når Åpen og ikke utgått | FR-8, FR-12, FR-13, FR-15 |
| R4 | Bare oppdragsgiver redigerer (Åpen) og avbryter (Åpen, Hjelper valgt) | FR-6, FR-7 |
| R5 | Bare oppdragsgiver velger nøyaktig én interessert, bare når Åpen | FR-15 |
| R6 | Fjerne hjelper eller trekke seg → Åpen | FR-17 |
| R7 | Bare valgt hjelper markerer Utført (avvik, §9.2) | FR-19 |
| R8 | Tilbakemelding: bare Utført, bare partene, én gang | FR-20 |
| R9 | Hvem ser detaljer, interesserte og profiler | FR-9, FR-14, FR-18, FR-21 |
| R10 | Når telefonnummer vises | FR-16 |
| R11 | 18-årsgrense | FR-1 |
| R12 | KI endrer aldri oppdrag; bare beskrivelsen sendes | FR-23, FR-24, FR-25 |
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

| Kvalitetskrav og personvern i briefen | Krav |
|---|---|
| Kan startes lokalt etter README, uten betalte tjenester | NFR-1 |
| Eksempeldata og testbrukere | NFR-2 |
| Passord hashet; hemmeligheter i `.env` | NFR-3, NFR-4 |
| Kjerneflyten på mobilskjerm | NFR-6 |
| Mock-modus og prompt i egen fil | FR-23, FR-26 |
| Lagrer bare det som trengs; ingen eksakt adresse | NFR-9 |
| Beskjed om at teksten sendes til ekstern tjeneste | FR-23 |

FR-18 (Mine oppdrag) og FR-22 (Redigere egen profil) har ikke et eget suksesskriterium; de kommer fra briefens skjermbilder og profilbeskrivelse. NFR-7, NFR-10, NFR-11 og NFR-12 kommer fra sensorveiledningen.

### 9.2 Presiseringer, avvik og tillegg

Briefen v2.2 avgjør ikke alt. Tabellen viser hvor PRD-en presiserer, avviker eller legger til, og hvorfor. Ingen antakelser står åpne.

| Tema | Briefen | PRD-en | Begrunnelse |
|---|---|---|---|
| Markere som utført | Bare valgt hjelper (R7) | **Avvik:** Valgt hjelper fra dagen for tidspunktet, og oppdragsgiveren når tidspunktet er passert. Den som markerer, bekrefter i en dialog (FR-19) | Ellers kunne oppdrag bli stående i Hjelper valgt for alltid, og utført arbeid kom aldri inn i profilen |
| Valg etter tidspunktet | R3: melde og trekke interesse bare før tidspunktet | Valg av hjelper avvises også når tidspunktet er passert (FR-15) | Ellers kunne en interessert som ikke lenger kan trekke interessen, bli valgt |
| Feltgrenser og normalisering | Tabellene «Felter i et oppdrag» og «Ved registrering gjelder» | Passord 8–64 tegn, fødselsdato høyst 120 år tilbake og egen regel for 29. februar (FR-1); mellomrom fjernes før lengden sjekkes, og telefonnummer godtas med mellomrom og +47 (§4.0) | Gjør grensetilfellene testbare, og hindrer at gyldige norske telefonnumre avvises |
| «Få forslag» | Knappen kan brukes når feltet har tekst (SK10) | Aktiv fra 10 tegn, og høyst 20 forslag per bruker per time (FR-23) | Samme minstelengde som beskrivelsen i FR-5, slik at forslaget kan brukes; grensen hindrer misbruk av KI-kvoten |
| Kontroll av KI-svar | «et kort tips» | Tittel og beskrivelse sjekkes mot reglene i FR-5, og tipset er høyst 200 tegn (FR-25) | Hindrer forslag som avvises når brukeren trykker «Publiser» |
| Mock-regler og testdobler | Nøkkelordtabell; automatiske tester kjører alltid mot mock-modus | Nøkkelord treffer i starten av ord, setningsslutt og reservetittel er definert, punktum legges ikke til etter «!» eller «?», og mock-modus gir ikke tips (FR-26). Feiltilfellene testes med en testdobbel (FR-25) | Gjør mock-svarene entydige og feilhåndteringen testbar |
| Profil og innlogging | Profilen er «erfaringsbeviset» | Egen profil har «Rediger profil» og «Logg ut» (FR-21); profilen kan bare ses av innloggede (§4.7) | R1 krever innlogging; deling og PDF er utsatt |
| Tid for oppstart | Ikke sagt | Innen 15 minutter etter README (NFR-1) | Sensor har 15–20 minutter til å få appen i gang |
| Endring etter interesse | Ikke sagt | Interessene beholdes, men merkes «Meldt før endring» (FR-6) | Ingen varsler i v1, så de interesserte må kunne se endringen |
| Ny interesse etter fjerning | Ikke sagt | En fjernet hjelper kan ikke melde interesse igjen; den som trakk seg selv, kan (FR-12) | Oppdragsgiveren skal ikke få tilbake en hjelper hen har fjernet |
| Vurdering | 1–5 stjerner | 1–5 stjerner som store knapper med tekst for skjermleser, og egen «Send»-knapp (FR-20) | Briefen følges; skissens tallknapper var for å gjøre det lett å treffe, og det løses med store knapper |
| Melding ved interesse | «kort melding» | Valgfri, maks 500 tegn (FR-12) | Skissen viser feltet som valgfritt; grense avklart med gruppen |
| Kommentar og «om meg» | Ingen lengdegrense | Maks 500 tegn (FR-20, FR-22) | Avklart med gruppen |
| Redigere profil | «Om meg» nevnes, ikke hvordan | «Om meg», postnummer og telefonnummer kan endres etter registrering; andre felt ikke (FR-22) | Brukere må kunne skrive om seg selv, endre postnummer ved flytting og rette feil telefonnummer |
| Postnummer | Fire siffer | Må finnes i lista over norske postnumre; poststedet vises (§3) | Ellers kan et oppdrag havne i et postnummer ingen ser |
| Egne oppdrag i oversikten | Ikke sagt | Vises ikke; finnes under «Mine oppdrag» (FR-10) | Oversikten er for å finne oppdrag man kan hjelpe med (jf. R2) |
| Fullførte oppdrag | Ikke presisert | Teller bare oppdrag som valgt hjelper (FR-21) | Profilen skal vise erfaring som hjelper |
| Tilbakemeldinger i profilen | Vurdering og kommentar | Viser rolle; snittet vises med én desimal og antall (FR-21) | Gjør erfaringsbeviset tydelig og testbart |
| Interesser ved redigering | Ikke sagt | Beholdes (FR-6) | Samme prinsipp som R6; interesserte kan trekke interessen (FR-13) |
| Sletting av konto | Brukeren bekrefter | Krever passord; opplysningene som slettes, er listet (FR-4) | Beskytter mot feiltrykk og andre på et delt nettbrett |
| Tidssone | Ikke sagt | Norsk tid, Europe/Oslo (FR-5) | Appen er for norske nabolag |
| Tidspunkt fram i tid | Ikke sagt | Høyst 12 måneder (FR-5) | Hindrer oppdrag som ligger åpne i årevis |
| Tidsavbrudd for KI | «tidsavbrudd» | 10 sekunder (FR-25) | Gjør kravet testbart |
| Personvern ved registrering | Ikke nevnt | Kort tekst om hva som lagres og hvem som ser det (FR-1) | Brukeren skal vite hva hen gir fra seg |
| Sikkerhet | Ikke nevnt | Grense for innloggingsforsøk og innlogging i høyst 7 dager (FR-2), grense for KI-forslag (FR-23), tekst aldri som HTML (NFR-12) | Sensorveiledningen ser etter validering, feilhåndtering og sikkerhet |
| Tekst og trykkflater | «stor nok» | Brødtekst ≥ 18 px, trykkflater ≥ 48 px (NFR-7) | Fra skissene |
| Glemt passord | Ikke nevnt | Utsatt; gruppen hjelper manuelt (§6.2) | Krever e-postutsending, som er utsatt sammen med varsler |
| Rapportering og blokkering | Ikke nevnt | Utsatt (§6.2); krenkende kommentarer fjernes manuelt (§4.7) | Tillit bygges gjennom vurderinger; oppdragsgiver velger og kan fjerne hjelper |
| Verifisert erfaring | «Erfaringsbevis» | Kjent begrensning: ikke verifisert, og det står i profilen (§4.7, FR-21) | Ærlig om hva profilen dokumenterer uten identitetsverifisering |
| Eksempeldata | 6 brukere, 10–15 oppdrag i ulike statuser | Dekker hvert steg i kjerneflyten, med datoer regnet fra innlasting (NFR-2) | Sensor skal kunne prøve alt uten å lage data selv |
| Prioritering | Ikke sagt | Må / Bør (§6.1) | Fristen; KI er valgfritt ifølge faglæreren |
| Universell utforming, robusthet og repo | Delvis | WCAG 2.1 AA (NFR-7), robust mot ugyldig input (NFR-10), navigasjon (NFR-11), `.gitignore` og testkommando i README (NFR-1, NFR-3) | Fra sensorveiledningen |

## Endringslogg

| Dato | Versjon | Endring |
|---|---|---|
| 2026-11-05 | 0.1 | Arbeidet startet. Form: webapp, coaching, brukerreiser først. |
| 2026-11-07 | 0.2 | UJ-1 (Kari) og UJ-2 (Amir) skrevet med gruppen. Utkast til ordliste, FR-1–FR-26, NFR-1–NFR-9, omfang og suksessmål laget fra briefen v2.2. |
| 2026-11-07 | 0.3 | Avklaringer: vurdering med 1–5 stjerner som i briefen (store knapper, jf. NFR-7); «om meg» skrives og postnummer kan endres i profilen etter registrering (FR-22); egne oppdrag vises bare under «Mine oppdrag» (FR-10); bare oppdrag som hjelper teller som fullført (FR-21); maks 500 tegn for melding, kommentar og «om meg». |
| 2026-11-07 | 1.0 | Ferdigstilt. Avstemt mot brief, skisser, faglærers tilbakemelding og sensorveiledning (rettet FR-9, FR-10, FR-18, FR-24, NFR-1, NFR-3, NFR-7, NFR-8; ny NFR-10). Review-funn rettet: sporingstabell R1–R13 og SK1–SK10 → FR i §4, KI-tidsavbrudd 10 s, testbar ventetilstand, NFR-4, NFR-5, NFR-8, SM-1, SM-4. Tidssone og interesser ved redigering avgjort. Ny §10 (nå §9.2) med alle presiseringer i forhold til briefen. Utsatte funn fra reviewen av briefen tatt inn: glemt passord og rapportering/blokkering utsatt (§7.2, nå §6.2), uverifisert erfaring som kjent begrensning (§4.7, FR-21), eksempeldata som dekker hele kjerneflyten (NFR-2). Språkvask. |
| 2026-11-07 | 1.1 | Rettet etter review med fire linser (`review-prd-v1.0-2026-11-07.md`) og rubrikk-review av utkastet (`review-rubric-v1.1.md`). **Produktvalg:** oppdragsgiveren kan markere Utført når tidspunktet er passert (FR-19, avvik fra R7); interesser meldt før en endring merkes (FR-6); prioritet Må/Bør med følger av kutt (§6.1); telefonnummer kan endres (FR-22); postnummerliste med poststed; rolle på tilbakemeldinger (FR-21); passord ved sletting (FR-4). **Hull tettet:** statusmodellen og «Mine oppdrag» (FR-15, FR-7, FR-12, FR-17, FR-18); sletting (FR-4); felles regler (§4.0); sikkerhet (FR-2, FR-3, FR-23, ny NFR-12); KI-svar og mock-regler (FR-25, FR-26); egen profil (FR-21); eksempeldata med relative datoer (NFR-2); kjente begrensninger for profil og glemt passord. **Struktur:** sporing og prioritet per krav, «Testes ved» i alle NFR-er, ny NFR-11 Navigasjon, sporingen samlet i §9.1, §6 og §7 slått sammen (§8–§10 er nå §7–§9). |
