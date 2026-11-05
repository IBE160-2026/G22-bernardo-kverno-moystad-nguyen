# Product Brief – Nabolagshelten

| | |
|---|---|
| **Gruppe** | G22 – Bernardo, Kverno, Møystad, Nguyen |
| **Versjon** | 2.1 (revidert etter tilbakemelding fra faglærer 2026-10-06, med KI-funksjon) |
| **Plassering** | `_bmad-output/planning-artifacts/product-brief-nabolagshelten.md` |
| **Neste steg** | PRD → arkitektur → epics og stories (BMAD) |

## Executive Summary

Nabolagshelten er en webapp som kobler personer som trenger hjelp til små, praktiske hverdagsoppgaver med naboer i samme område som har tid til å hjelpe. Eksempler er snømåking, gressklipping, bærehjelp, hundelufting og teknologihjelp.

Første versjon (v1) har **én kjerneflyt**: legge ut et oppdrag → melde interesse → velge hjelper → markere som utført → gi tilbakemelding. Fullførte oppdrag og tilbakemeldinger samles i hjelperens profil, slik at småoppdrag blir dokumentert erfaring som kan vises til i en jobbsøknad.

I tillegg har v1 én avgrenset KI-funksjon: når en oppdragsgiver skriver et oppdrag, kan hun få forslag til kategori, tittel og en tydeligere beskrivelse. Funksjonen er et hjelpemiddel. Brukeren bestemmer alltid selv, og appen fungerer fullt ut uten KI.

Kjerneideen: *det finnes ofte noen i nærheten som kan hjelpe* — Nabolagshelten gjør det lett å finne dem.

## Problemet

Mange hverdagsoppgaver er for små til at det føles naturlig å kontakte et firma, men det finnes ingen enkel vei til noen i nærheten som kan og vil hjelpe. I dag løses dette tilfeldig gjennom lokale Facebook-grupper, Finn eller bekjente. Det gjør det uklart:

- hvem som trenger hjelp, og hvem som kan hjelpe
- hvor nært oppdraget er
- om personen har gjort lignende oppdrag før og er pålitelig
- om et oppdrag fortsatt er ledig, eller allerede er løst

**Eksempler på situasjoner vi har sett:**

- En eldre nabo legger ut et innlegg i en lokal Facebook-gruppe om hjelp til snømåking. Innlegget får mange kommentarer, men det er uklart hvem som faktisk tar jobben, og innlegget forsvinner i strømmen etter en dag.
- En student som ønsker seg sommerjobb har ingen arbeidserfaring å vise til. Hun har hjulpet flere naboer med hage og flytting, men har ingenting dokumentert.

Det finnes altså et gap mellom små hverdagsbehov og menneskene som kan dekke dem — og ingen oversikt over hvem som har hjulpet hvem.

## Løsningen

### Kjerneflyten i v1

1. **Legge ut oppdrag.** Oppdragsgiveren fyller inn tittel, beskrivelse, kategori, postnummer, ønsket tidspunkt og hva hun tilbyr som godtgjørelse (et beløp i kroner, eller «uten betaling»). Eksempel: *«Trenger hjelp til å måke innkjørselen i morgen tidlig – 200 kr»*.
2. **Finne oppdrag.** Oppdragstakeren ser en liste over åpne oppdrag i sitt postnummer, og kan filtrere på kategori og postnummer.
3. **Melde interesse.** Oppdragstakeren åpner et oppdrag og melder interesse med en kort melding (*«Jeg kan komme kl. 07:30»*).
4. **Velge hjelper.** Oppdragsgiveren ser alle som har meldt interesse, med navn, antall fullførte oppdrag og gjennomsnittlig vurdering, og velger én. Først da blir telefonnummeret til begge synlig for den andre parten, slik at de kan avtale detaljer direkte.
5. **Markere som utført.** Når jobben er gjort, markerer den valgte hjelperen oppdraget som utført.
6. **Gi tilbakemelding.** Begge parter kan gi hverandre én vurdering (1–5 stjerner) og en kort kommentar. Tilbakemeldingene vises i profilen.

### Statuser for et oppdrag

| Status | Betyr | Hvem endrer |
|---|---|---|
| **Åpen** | Synlig i oversikten, andre kan melde interesse | Opprettes av oppdragsgiver |
| **Hjelper valgt** | Én hjelper er valgt, oppdraget vises ikke lenger i oversikten | Oppdragsgiver |
| **Utført** | Jobben er gjort, tilbakemelding kan gis | Valgt hjelper |
| **Avbrutt** | Oppdraget er trukket tilbake | Oppdragsgiver (fra Åpen eller Hjelper valgt) |

### KI-hjelp til å skrive oppdrag

Mange oppdragsgivere, særlig eldre, synes det er vanskelig å formulere et oppdrag slik at hjelperen forstår hva jobben innebærer. I skjemaet for nytt oppdrag finnes derfor knappen **«Få forslag»**.

1. Oppdragsgiveren skriver med egne ord, for eksempel *«trenger noen til å måke innkjørselen før jobb i morgen»*.
2. Hun trykker «Få forslag». Appen sender **bare oppdragsteksten** til en språkmodell.
3. Modellen svarer i fast JSON-format med **kategori** (fra den faste listen), **forslag til tittel** og **forslag til forbedret beskrivelse**. Den kan også gi et kort tips om hva som mangler, for eksempel tidspunkt eller omfang.
4. Forslagene vises i skjemaet. Hun kan **godta, endre eller forkaste** hvert forslag før hun publiserer.

**Kontroll av svaret fra KI-en:**

- Svaret valideres mot et fast skjema. Ugyldig JSON, en kategori som ikke finnes, eller for lang tekst blir avvist.
- Ved ugyldig svar, tidsavbrudd eller feil i tjenesten vises skjemaet uten forslag sammen med en vennlig melding. Oppdraget kan alltid lagres manuelt.
- KI-en lagrer aldri noe selv. Ingenting publiseres uten at brukeren trykker «Publiser».

**Mock-modus:** Når ingen API-nøkkel er satt i `.env`, bruker appen en innebygd mock-tjeneste med forhåndsdefinerte svar basert på nøkkelord (for eksempel «snø» → Snømåking). Sensor kan dermed bruke og teste funksjonen uten nøkkel og uten betalte tjenester. Automatiske tester kjører alltid mot mock-modus.

### Profil og dokumentert erfaring

Hver bruker har en profil med navn, postnummer, en kort tekst om seg selv, antall fullførte oppdrag per kategori, gjennomsnittlig vurdering og tilbakemeldinger fra oppdragsgivere. Dette er «erfaringsbeviset» en oppdragstaker kan vise til i en jobbsøknad.

### Nærhet

«I nærheten» løses med **postnummer** i v1. Brukeren oppgir postnummer ved registrering, og oversikten viser som standard åpne oppdrag i samme postnummer. Brukeren kan velge et annet postnummer i filteret. Eksakt adresse lagres ikke i appen; den deles direkte mellom partene etter at hjelper er valgt.

### Betaling

Det er **ingen betaling i appen**. Oppdragsgiveren oppgir hva hun tilbyr, og partene gjør opp seg imellom (for eksempel kontant eller Vipps privat). Appen viser bare den foreslåtte godtgjørelsen.

## Hva gjør dette annerledes

- **Lokalt først.** Facebook-grupper og Finn er åpne for alle og alt. Nabolagshelten viser bare småoppdrag i ditt eget område, sortert etter når de skal gjøres.
- **Tydelig status.** I motsetning til en tråd i en Facebook-gruppe ser alle om et oppdrag er ledig, tatt eller utført.
- **Lav terskel.** Anbudstjenester som Mittanbud er laget for håndverkere og større jobber. Hos oss er en jobb på 30 minutter velkommen, uten anbud, firma eller kontrakt.
- **Fra småjobb til erfaring.** Fullførte oppdrag og tilbakemeldinger samles i profilen og kan brukes som referanse — noe ingen av de uformelle kanalene gir i dag.
- **Gjensidig hjelp.** Samme bruker kan være oppdragsgiver én dag og hjelper neste. Det finnes ikke egne kontotyper.
- **Hjelp til å formulere seg.** KI-forslag gjør det enklere for brukere som ikke er vant til å skrive annonser, å lage tydelige oppdrag. Hjelperne får da bedre informasjon å gå ut fra.
- **Tillit i v1** bygges gjennom historikk og tilbakemeldinger i profilen, ikke gjennom formell identitetsverifisering. Verifisering med BankID eller Vipps er en planlagt utvidelse (se Omfang).

## Hvem tjenesten er for

Vi designer v1 rundt to konkrete personer.

**Primær oppdragsgiver – Kari, 72 år.** Bor alene i et rekkehus. Klarer seg fint selv, men snømåking og tunge bæreoppdrag er blitt vanskelige. Bruker nettbrett og mobil til nettbank og nyheter, men gir opp hvis noe er uoversiktlig.
*Trenger:* å legge ut et oppdrag på under to minutter, se tydelig hvem som har meldt interesse, og kunne velge noen hun føler seg trygg på.
*Konsekvens for design:* stor og lesbar tekst, få felter per skjerm, tydelige knapper med tekst (ikke bare ikoner), enkelt språk, og fungerer godt på mobil og nettbrett.

**Primær oppdragstaker – Amir, 21 år, student.** Ønsker litt ekstra inntekt og noe å skrive på CV-en før han søker sommerjobb. Har tid på ettermiddager og i helger.
*Trenger:* raskt se ledige oppdrag i nærheten, forstå hva de innebærer og hva de betaler, og samle tilbakemeldinger han kan vise til.
*Konsekvens for design:* rask liste med filter, tydelig godtgjørelse og tidspunkt, profil som viser erfaringen hans.

Andre grupper — barnefamilier, travle personer og arbeidsledige — har de samme behovene og dekkes av den samme flyten.

**Aldersgrense:** Alle brukere må være **18 år eller eldre** i v1. Ungdom under 18 er en viktig målgruppe på sikt, men krever godkjenning fra foresatte og kommer i et senere trinn.

## Viktigste skjermbilder

| # | Skjermbilde | Innhold |
|---|---|---|
| 1 | **Oppdragsoversikt** (startside) | Liste over åpne oppdrag i eget postnummer: tittel, kategori, tidspunkt, godtgjørelse. Filter for kategori og postnummer. Knapp «Legg ut oppdrag». |
| 2 | **Nytt oppdrag** | Skjema: tittel, beskrivelse, kategori (nedtrekk), postnummer (forhåndsutfylt), dato/tid, godtgjørelse. Knappen «Få forslag» viser KI-forslag med «Bruk» og «Forkast» for hvert felt. |
| 3 | **Oppdragsdetaljer** | Full beskrivelse og status. For hjelper: «Meld interesse». For oppdragsgiver: liste over interesserte med «Velg». For valgt hjelper: «Marker som utført». Etter utført: «Gi tilbakemelding». |
| 4 | **Mine oppdrag** | To faner: «Oppdrag jeg har lagt ut» og «Oppdrag jeg hjelper med», med status. |
| 5 | **Profil** | Navn, postnummer, om meg, antall fullførte oppdrag per kategori, gjennomsnittlig vurdering og tilbakemeldinger. |

Alle skjermbilder skal fungere på mobil (fra 360 px bredde) og bruke stor nok tekst og trykkflater for eldre brukere.

## Regler (hvem kan gjøre hva)

Disse reglene skal håndheves på serveren, ikke bare skjules i grensesnittet, og hver regel skal ha minst én automatisk test.

1. Bare innloggede brukere kan se oppdrag, legge ut oppdrag og melde interesse.
2. En bruker kan ikke melde interesse på sitt eget oppdrag.
3. En bruker kan melde interesse på samme oppdrag bare én gang, og bare mens oppdraget er **Åpen**.
4. Bare oppdragsgiveren kan redigere eller avbryte oppdraget, og bare før det er **Utført**.
5. Bare oppdragsgiveren kan velge hjelper, og bare blant brukere som har meldt interesse. Det kan velges nøyaktig én hjelper.
6. Bare den valgte hjelperen kan markere oppdraget som **Utført**, og bare når status er **Hjelper valgt**.
7. Tilbakemelding kan bare gis når oppdraget er **Utført**, bare mellom oppdragsgiver og valgt hjelper, og bare én gang per person per oppdrag.
8. Telefonnummer vises bare for oppdragsgiver og valgt hjelper, og først etter at hjelper er valgt.
9. Registrering krever at brukeren oppgir en fødselsdato som gir alder på minst 18 år.
10. KI-forslag endrer aldri et oppdrag direkte. Bare brukeren kan fylle inn og publisere. Bare oppdragsteksten sendes til KI-tjenesten, aldri navn, e-post, telefonnummer eller annen informasjon om brukeren.
11. Bare brukeren selv kan slette sin egen konto. Ved sletting behandles oppdrag, interesser og tilbakemeldinger som beskrevet i «Sletting av konto».

## Suksesskriterier

Kriteriene under er funksjonelle og skal kunne bli testtilfeller (akseptansekriterier i stories). V1 er ferdig når alle er oppfylt.

1. **Registrering og innlogging:** En person på 18 år eller eldre kan registrere seg med navn, e-post, passord, telefonnummer og postnummer, og logge inn og ut. Registrering med alder under 18 år eller en e-post som allerede er i bruk avvises med en forståelig feilmelding. En innlogget bruker kan slette sin egen konto etter å ha bekreftet det, og kan deretter ikke logge inn med den. Oppdrag, interesser og tilbakemeldinger behandles som beskrevet i «Sletting av konto», og utførte oppdrag og gitte tilbakemeldinger telles fortsatt i de andre brukernes profiler.
2. **Legge ut oppdrag:** En innlogget bruker kan legge ut et oppdrag med tittel, beskrivelse, kategori, postnummer, tidspunkt og godtgjørelse. Oppdraget får status **Åpen** og vises i oversikten for brukere med samme postnummer. Oppdrag med manglende obligatoriske felter avvises. Oppdragsgiveren kan redigere eller avbryte oppdraget så lenge det ikke er **Utført**. Et avbrutt oppdrag får status **Avbrutt**. Forsøk fra andre brukere på å redigere eller avbryte avvises.
3. **Finne oppdrag:** En bruker ser som standard bare åpne oppdrag i sitt eget postnummer, og kan filtrere på kategori og velge et annet postnummer. Oppdrag med status **Hjelper valgt**, **Utført** eller **Avbrutt** vises ikke i oversikten.
4. **Melde interesse:** En bruker kan melde interesse på et åpent oppdrag som ikke er hennes eget, med en kort melding. Oppdragsgiveren ser alle interesserte med navn, antall fullførte oppdrag og gjennomsnittlig vurdering.
5. **Velge hjelper:** Oppdragsgiveren kan velge én av de interesserte. Status endres til **Hjelper valgt**, og oppdragsgiver og valgt hjelper ser hverandres telefonnummer. Andre brukere kan ikke velge hjelper eller se telefonnumrene.
6. **Fullføre oppdrag:** Bare valgt hjelper kan markere oppdraget som **Utført**. Forsøk fra andre brukere avvises.
7. **Tilbakemelding:** Etter at oppdraget er utført, kan oppdragsgiver og hjelper gi hverandre én vurdering (1–5) med valgfri kommentar. Vurderingen vises i mottakerens profil, og gjennomsnittet oppdateres.
8. **Dokumentert erfaring:** En brukers profil viser antall fullførte oppdrag per kategori, gjennomsnittlig vurdering og alle mottatte tilbakemeldinger.
9. **KI-forslag:** En bruker som har skrevet en oppdragstekst, kan trykke «Få forslag» og få kategori, tittel og beskrivelse foreslått. Kategorien er alltid en av kategoriene i den faste listen. I mock-modus gir teksten «måke snø i innkjørselen» kategorien Snømåking. Hvis svaret fra KI-tjenesten er ugyldig eller tjenesten feiler, vises skjemaet uten forslag, og oppdraget kan likevel lagres.

I tillegg gjelder disse kvalitetskravene:

- Appen kan startes lokalt ved å følge README, uten betalte tjenester, eksterne kontoer eller gruppens egne nøkler.
- Repoet inneholder eksempeldata (minst 6 testbrukere i 2–3 postnumre og 10–15 oppdrag i ulike statuser) og innloggingsinformasjon for testbrukere i README.
- Passord lagres hashet, og hemmeligheter ligger i `.env` (ikke i repoet) med en `.env.example` som mal.
- Kjerneflyten kan gjennomføres på mobilskjerm.
- KI-funksjonen fungerer i mock-modus uten API-nøkkel. En ekte språkmodell aktiveres bare ved å legge inn en nøkkel i `.env`. Prompten ligger i en egen fil i koden, slik at den er lett å finne og forbedre.

## Personvern og sikkerhet i v1

- Vi lagrer bare det som trengs: navn, e-post, hashet passord, telefonnummer, postnummer, fødselsdato (for aldersgrensen) og innholdet brukeren selv legger inn.
- Eksakt adresse lagres ikke.
- Telefonnummer deles bare mellom partene i et oppdrag der hjelper er valgt (regel 8).
- En bruker kan slette sin egen konto (regel 11, suksesskriterium 1). Se «Sletting av konto» under.
- Til KI-tjenesten sendes bare oppdragsteksten (regel 10). Brukeren får beskjed om at teksten sendes til en ekstern tjeneste når hun bruker «Få forslag».
- Eksempeldata i repoet er oppdiktet og inneholder ingen ekte personopplysninger.

### Sletting av konto

Når en bruker sletter kontoen sin, fjernes personopplysningene. Andre brukeres dokumenterte erfaring skal likevel ikke forsvinne. Det som er igjen, vises som **«Slettet bruker»**.

| Situasjon | Hva skjer |
|---|---|
| Egne oppdrag med status **Åpen** | Slettes, sammen med interessene på dem |
| Egne oppdrag med status **Hjelper valgt** | Settes til **Avbrutt**, slik at hjelperen ser at oppdraget ikke blir noe av |
| Oppdrag med status **Utført** (som oppdragsgiver eller hjelper) | Beholdes, men den slettede brukeren vises som «Slettet bruker». Oppdraget teller fortsatt i den andre partens profil |
| Interesser brukeren har meldt | Slettes |
| Brukeren er valgt hjelper på et oppdrag som ikke er **Utført** | Oppdraget går tilbake til **Åpen**, slik at oppdragsgiveren kan velge en ny hjelper |
| Tilbakemeldinger brukeren har **gitt** | Beholdes anonymt («Slettet bruker») og teller fortsatt i mottakerens gjennomsnitt |
| Tilbakemeldinger brukeren har **fått** | Slettes sammen med profilen |

Kommentaren i en anonymisert tilbakemelding kan i noen tilfeller avsløre hvem som skrev den (for eksempel et gatenavn). Det godtar vi i v1. Brukeren får beskjed om dette før kontoen slettes.

## Omfang

### Inkludert i v1

- Registrering og innlogging med e-post og passord, med 18-årsgrense
- Slette egen konto
- Brukerprofil med historikk og tilbakemeldinger
- Legge ut, redigere og avbryte oppdrag med fast liste over kategorier: *Snømåking, Hage, Bærehjelp/flytting, Dyrepass, Teknologihjelp, Annet*
- Oversikt over åpne oppdrag med filter på kategori og postnummer
- Melde interesse, velge hjelper, markere utført, gi tilbakemelding
- «Mine oppdrag» med status
- KI-forslag til kategori, tittel og beskrivelse, med validering, feilhåndtering og mock-modus (bygges etter at kjerneflyten er ferdig og stabil)
- Eksempeldata og testbrukere

### Utsatt til senere trinn

- **Deling og utlån av utstyr** (stiger, verktøy, hageredskap) — trinn 2, når kjerneflyten er ferdig og stabil
- **Identitetsverifisering med BankID eller Vipps**
- **Brukere under 18 år** med godkjenning fra foresatte
- Kart og avstandsbasert matching (erstatter postnummer)
- Meldinger/chat i appen
- Varsler på e-post eller push
- Eksport av erfaringsoversikt til PDF for CV
- Flere KI-funksjoner, for eksempel forslag til godtgjørelse, sjekk av upassende innhold eller en KI-generert erfaringstekst til CV

### Ikke inkludert

Betaling i appen, fullverdig jobbportal, bemanningsplattform, kjøp og salg, håndverkermarkedsplass, utleieplattform, sosialt medium, og store eller komplekse oppdrag.

### Avklarte forutsetninger for PRD og arkitektur

- Ingen betaling i appen.
- Nærhet løses med postnummer.
- Aldersgrense 18 år.
- KI brukes bare til forslag ved oppretting av oppdrag, alltid med mock-modus som standard.
- Vanlig webapp med én database, som kan kjøres lokalt. Konkret teknologistakk velges i arkitekturfasen, men skal være utbredt og godt dokumentert, og skal ikke kreve betalte tjenester.

## Visjon

På sikt skal *«Finnes det noen i nærheten som kan hjelpe?»* bli et naturlig spørsmål, fremfor å kjøpe noe nytt eller kontakte et firma. Etter v1 kan Nabolagshelten utvides med utlån av utstyr, verifisert identitet og trygg deltakelse for ungdom med godkjenning fra foresatte. Da kan en ungdom få sitt første oppdrag, en arbeidsledig bygge erfaring og referanser, en eldre person få praktisk hjelp, og en nabo låne bort et verktøy som ellers står ubrukt — og bidra til et mer ressursbevisst og inkluderende lokalmiljø.

## Endringer fra versjon 1

| Tilbakemelding | Endring |
|---|---|
| Fjern BankID/Vipps og foresattgodkjenning fra v1 | Vanlig innlogging med e-post og passord, 18-årsgrense. Begge flyttet til «Utsatt». |
| Begrens v1 til én kjerneflyt | Utlån av utstyr flyttet til trinn 2. V1 er oppdragsflyten fra start til tilbakemelding. |
| Testbare suksesskriterier | 9 funksjonelle kriterier i formen «en bruker kan …» og 11 regler for hvem som kan gjøre hva. |
| Hva skjer etter interesse? | Beskrevet valg av hjelper, deling av telefonnummer, utført og tilbakemelding, med statusmodell. |
| Uavklart betaling og nærhet | Ingen betaling i appen; nærhet via postnummer. |
| Skille fra eksisterende tjenester | Sammenligning med Facebook-grupper, Finn og anbudstjenester. |
| For brede målgrupper | To primærpersoner (Kari og Amir) med konkrete designkonsekvenser for eldre og mobil. |
| Skisser skjermbilder | Fem viktigste skjermbilder beskrevet. |
| Kjørbar for sensor | Krav om README, testbrukere, eksempeldata og `.env.example`. |
| Ryddighet i repoet | Briefen flyttes til `_bmad-output/planning-artifacts/`. |
| Forslag om avgrenset KI-funksjon | KI-forslag til kategori, tittel og beskrivelse lagt inn i v1, med validering, mock-modus, regel 10 og suksesskriterium 9. |
