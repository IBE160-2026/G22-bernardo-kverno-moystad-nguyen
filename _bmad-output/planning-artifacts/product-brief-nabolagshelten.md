# Product Brief – Nabolagshelten

| | |
|---|---|
| **Gruppe** | G22 – Bernardo, Kverno, Møystad, Nguyen |
| **Versjon** | 2.2 (revidert etter tilbakemelding fra faglærer 2026-10-06 og etter review 2026-11-05) |
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

## Hvem tjenesten er for

Vi designer v1 rundt to konkrete personer.

**Primær oppdragsgiver – Kari, 72 år.** Bor alene i et rekkehus. Klarer seg fint selv, men snømåking og tunge bæreoppdrag er blitt vanskelige. Bruker nettbrett og mobil til nettbank og nyheter, men gir opp hvis noe er uoversiktlig.
*Trenger:* å legge ut et oppdrag på under to minutter, se tydelig hvem som har meldt interesse, og kunne velge noen hun føler seg trygg på.
*Konsekvens for design:* stor og lesbar tekst, få felter per skjerm, tydelige knapper med tekst (ikke bare ikoner), enkelt språk, og fungerer godt på mobil og nettbrett.

**Primær oppdragstaker – Amir, 21 år, student.** Ønsker litt ekstra inntekt og noe å skrive på CV-en før han søker sommerjobb. Har tid på ettermiddager og i helger.
*Trenger:* raskt se ledige oppdrag i nærheten, forstå hva de innebærer og hva de betaler, og samle tilbakemeldinger han kan vise til.
*Konsekvens for design:* rask liste med filter, tydelig godtgjørelse og tidspunkt, profil som viser erfaringen hans.

Andre grupper — barnefamilier, travle personer og arbeidsledige — har de samme behovene og dekkes av den samme flyten.

**Aldersgrense:** Alle brukere må være **18 år eller eldre** i v1. Grensen bygger på fødselsdatoen brukeren selv oppgir (egenerklæring). Ungdom under 18 er en viktig målgruppe på sikt, men krever godkjenning fra foresatte og kommer i et senere trinn.

## Løsningen

V1 består av én kjerneflyt i seks steg, fire statuser for et oppdrag, faste regler for feltene i et oppdrag og én KI-funksjon. «Oppdragstaker» og «hjelper» brukes om samme rolle; en oppdragstaker som er valgt til et oppdrag, kalles *valgt hjelper*.

### Kjerneflyten i v1

1. **Legge ut oppdrag.** Oppdragsgiveren fyller inn tittel, beskrivelse, kategori, postnummer, ønsket tidspunkt og hva hun tilbyr som godtgjørelse (et beløp i kroner, eller «uten betaling»). Eksempel: *«Trenger hjelp til å måke innkjørselen i morgen tidlig – 200 kr»*.
2. **Finne oppdrag.** Oppdragstakeren ser en liste over åpne oppdrag i sitt postnummer, og kan filtrere på kategori eller velge et annet postnummer.
3. **Melde interesse.** Oppdragstakeren åpner et oppdrag og melder interesse med en kort melding (*«Jeg kan komme kl. 07:30»*). Interessen kan trekkes tilbake så lenge oppdraget er åpent.
4. **Velge hjelper.** Oppdragsgiveren ser alle som har meldt interesse, med navn, antall fullførte oppdrag og gjennomsnittlig vurdering, og velger én. Først da ser oppdragsgiveren og hjelperen hverandres telefonnummer, slik at de kan avtale detaljer direkte.
5. **Markere som utført.** Når jobben er gjort, markerer den valgte hjelperen oppdraget som utført.
6. **Gi tilbakemelding.** Begge parter kan gi hverandre én vurdering (1–5 stjerner) og en kort kommentar. Tilbakemeldingene vises i mottakerens profil.

### Statuser for et oppdrag

| Status | Betyr | Hvordan oppdraget kommer hit |
|---|---|---|
| **Åpen** | Synlig i oversikten så lenge tidspunktet ikke er passert. Andre kan melde og trekke interesse | Oppdragsgiver legger ut oppdraget, eller valgt hjelper fjernes eller trekker seg (regel 6) |
| **Hjelper valgt** | Én hjelper er valgt. Oppdraget vises ikke i oversikten | Oppdragsgiver velger hjelper (regel 5) |
| **Utført** | Jobben er gjort, og tilbakemelding kan gis | Valgt hjelper markerer utført (regel 7) |
| **Avbrutt** | Oppdraget er trukket tilbake | Oppdragsgiver avbryter fra Åpen eller Hjelper valgt (regel 4) |

**Utført** og **Avbrutt** er endelige: oppdraget kan ikke endres etterpå.

Hvis den valgte hjelperen ikke gjør jobben, kan oppdragsgiveren fjerne hjelperen og velge en annen, eller avbryte oppdraget. Bare hjelperen kan markere et oppdrag som utført.

**Utgåtte oppdrag:** Et åpent oppdrag der ønsket tidspunkt er passert, vises ikke lenger i oversikten og kan ikke få nye interesser. Oppdragsgiveren ser det under «Mine oppdrag» merket «Tidspunktet er passert», og kan endre tidspunktet eller avbryte oppdraget. Dette er ikke en egen status.

### Felter i et oppdrag

| Felt | Obligatorisk | Gyldig verdi |
|---|---|---|
| Tittel | Ja | 3–80 tegn |
| Beskrivelse | Ja | 10–1000 tegn |
| Kategori | Ja | Én fra den faste listen: *Snømåking, Hage, Bærehjelp/flytting, Dyrepass, Teknologihjelp, Annet* |
| Postnummer | Ja | Fire siffer. Forhåndsutfylt fra profilen, kan endres |
| Tidspunkt | Ja | Dato og klokkeslett, ikke tilbake i tid |
| Godtgjørelse | Ja | Heltall fra 1 til 10 000 kr, eller «uten betaling» |

Ved registrering gjelder:

| Felt | Gyldig verdi |
|---|---|
| Navn | 1–80 tegn |
| E-post | Gyldig format. Må være unik, uavhengig av store og små bokstaver |
| Passord | Minst 8 tegn |
| Telefonnummer | Åtte siffer (norsk nummer) |
| Postnummer | Fire siffer |
| Fødselsdato | Ikke i fremtiden, og gir minst 18 år. Den som fyller 18 i dag, godtas |

Ugyldige felter avvises med en forståelig melding rett ved feltet.

### KI-hjelp til å skrive oppdrag

Mange oppdragsgivere, særlig eldre, synes det er vanskelig å formulere et oppdrag slik at hjelperen forstår hva jobben innebærer. I skjemaet for nytt oppdrag finnes derfor knappen **«Få forslag»**.

1. Oppdragsgiveren skriver med egne ord i beskrivelsesfeltet, for eksempel *«trenger noen til å måke innkjørselen før jobb i morgen»*. Knappen er deaktivert så lenge feltet er tomt.
2. Hun trykker «Få forslag», og teksten sendes til en språkmodell (regel 12).
3. Modellen svarer i fast JSON-format med **kategori** (fra den faste listen), **forslag til tittel** og **forslag til forbedret beskrivelse**. Den kan også gi et kort tips om hva som mangler, for eksempel tidspunkt eller omfang.
4. Forslagene vises ved siden av feltene. Hun kan **bruke, endre eller forkaste** hvert forslag før hun publiserer. Et forslag overskriver aldri et felt før hun trykker «Bruk».

**Kontroll av svaret fra KI-en:**

- Svaret valideres mot et fast skjema. Ugyldig JSON, en kategori som ikke finnes, eller for lang tekst blir avvist.
- Ved ugyldig svar, tidsavbrudd eller feil i tjenesten vises en vennlig melding, og skjemaet vises uten forslag. Oppdraget kan alltid lagres manuelt.
- KI-en lagrer aldri noe selv. Ingenting publiseres uten at brukeren trykker «Publiser».

**Mock-modus:** Når ingen API-nøkkel er satt i `.env`, bruker appen en innebygd mock-tjeneste. Sensor kan dermed bruke og teste funksjonen uten nøkkel og uten betalte tjenester, og automatiske tester kjører alltid mot mock-modus. Mock-tjenesten svarer alltid likt for samme tekst:

| Kategori | Nøkkelord (første kategori med treff vinner) |
|---|---|
| Snømåking | snø, måke, brøyte, strø |
| Hage | hage, plen, gress, klippe, hekk, løv, luke |
| Bærehjelp/flytting | bære, flytte, flytting, sofa, møbel, eske |
| Dyrepass | hund, katt, lufte, dyr, mate |
| Teknologihjelp | pc, data, ipad, nettbrett, mobil, wifi, tv, skriver |
| Annet | Ingen nøkkelord treffer |

Tittelforslaget er første setning i teksten, forkortet til maks 80 tegn og med stor forbokstav. Beskrivelsesforslaget er teksten med stor forbokstav og punktum til slutt.

### Profil og dokumentert erfaring

Hver bruker har en profil med navn, postnummer, en kort tekst om seg selv, antall fullførte oppdrag per kategori, gjennomsnittlig vurdering og tilbakemeldinger. En bruker uten vurderinger vises med «Ingen vurderinger ennå». Profilen er «erfaringsbeviset» en oppdragstaker kan vise til i en jobbsøknad.

### Nærhet

«I nærheten» løses med **postnummer** i v1. Brukeren oppgir postnummer ved registrering, og oversikten viser som standard åpne oppdrag i samme postnummer. Brukeren kan velge et annet postnummer i filteret. Naboer på hver sin side av en postnummergrense ser ikke hverandres oppdrag som standard; det er en kjent begrensning i v1. Eksakt adresse lagres ikke i appen; den deles direkte mellom partene etter at hjelper er valgt.

### Betaling

Det er **ingen betaling i appen**. Oppdragsgiveren oppgir hva hun tilbyr, og partene gjør opp seg imellom (for eksempel kontant eller Vipps privat). Appen viser bare den foreslåtte godtgjørelsen.

## Hva gjør dette annerledes

- **Lokalt først.** Facebook-grupper og Finn er åpne for alle og alt. Nabolagshelten viser bare småoppdrag i ditt eget område, sortert etter når de skal gjøres.
- **Tydelig status.** I motsetning til en tråd i en Facebook-gruppe ser alle om et oppdrag er ledig, tatt eller utført.
- **Lav terskel.** Anbudstjenester som Mittanbud er laget for håndverkere og større jobber. Hos oss er en jobb på 30 minutter velkommen, uten anbud, firma eller kontrakt.
- **Fra småjobb til erfaring.** Fullførte oppdrag og tilbakemeldinger samles i profilen og kan brukes som referanse — noe ingen av de uformelle kanalene gir i dag.
- **Gjensidig hjelp.** Samme bruker kan være oppdragsgiver én dag og hjelper neste. Det finnes ikke egne kontotyper.
- **Hjelp til å formulere seg.** KI-forslag gjør det enklere for brukere som ikke er vant til å skrive annonser, å lage tydelige oppdrag. Hjelperne får da bedre informasjon å gå ut fra.

## Viktigste skjermbilder

| # | Skjermbilde | Innhold |
|---|---|---|
| 1 | **Oppdragsoversikt** (startside) | Liste over åpne oppdrag i eget postnummer, sortert etter tidspunkt: tittel, kategori, tidspunkt, godtgjørelse. Filter for kategori og postnummer. Knapp «Legg ut oppdrag». |
| 2 | **Nytt oppdrag** | Skjema: tittel, beskrivelse, kategori (nedtrekk), postnummer (forhåndsutfylt), dato/tid, godtgjørelse. Knappen «Få forslag» viser KI-forslag med «Bruk» og «Forkast» for hvert felt. |
| 3 | **Oppdragsdetaljer** | Full beskrivelse og status. For hjelper: «Meld interesse» og «Trekk interessen». For oppdragsgiver: liste over interesserte med «Velg», og «Fjern hjelper» etter valg. For valgt hjelper: «Marker som utført» og «Trekk meg». Etter utført: «Gi tilbakemelding». |
| 4 | **Mine oppdrag** | To faner: «Oppdrag jeg har lagt ut» og «Oppdrag jeg hjelper med», med status. |
| 5 | **Profil** | Navn, postnummer, om meg, antall fullførte oppdrag per kategori, gjennomsnittlig vurdering og tilbakemeldinger. |

Alle skjermbilder skal fungere på mobil (fra 360 px bredde) og bruke stor nok tekst og trykkflater for eldre brukere.

Skisser av de fem skjermbildene ligger i [skisser-skjermbilder.md](skisser-skjermbilder.md).

## Regler (hvem kan gjøre hva)

Disse reglene skal håndheves på serveren, ikke bare skjules i grensesnittet, og hver regel skal ha minst én automatisk test. Reglene er den eneste kilden; suksesskriteriene viser til dem.

1. Bare innloggede brukere kan se oppdrag og profiler, legge ut oppdrag og melde interesse.
2. En bruker kan ikke melde interesse på sitt eget oppdrag.
3. En bruker kan ha bare én interesse per oppdrag, og kan melde og trekke interesse bare mens oppdraget har status **Åpen** og tidspunktet ikke er passert.
4. Bare oppdragsgiveren kan redigere og avbryte oppdraget. Oppdraget kan redigeres bare mens det har status **Åpen**, og avbrytes bare mens det har status **Åpen** eller **Hjelper valgt**.
5. Bare oppdragsgiveren kan velge hjelper, bare mens oppdraget har status **Åpen**, og bare blant brukere som har meldt interesse. Det kan velges nøyaktig én hjelper. Hvis statusen allerede er endret (for eksempel ved dobbeltklikk), avvises valget.
6. Mens oppdraget har status **Hjelper valgt**, kan oppdragsgiveren fjerne den valgte hjelperen, og den valgte hjelperen kan trekke seg. Oppdraget går da tilbake til **Åpen**. Den tidligere hjelperens interesse slettes, og de andre interessene beholdes.
7. Bare den valgte hjelperen kan markere oppdraget som **Utført**, og bare når status er **Hjelper valgt**.
8. Tilbakemelding kan bare gis når oppdraget er **Utført**, bare mellom oppdragsgiver og valgt hjelper, bare én gang per person per oppdrag, og ikke til en bruker som har slettet kontoen sin.
9. Detaljene i et oppdrag med status **Åpen** kan ses av alle innloggede, men lista over interesserte ses bare av oppdragsgiveren. Detaljene i oppdrag med andre statuser ses bare av oppdragsgiveren og den valgte hjelperen. Brukere som meldte interesse uten å bli valgt, ser bare tittel og status under «Mine oppdrag». Profiler viser aldri telefonnummer, e-post eller fødselsdato.
10. Telefonnummer vises bare for oppdragsgiveren og den valgte hjelperen, og bare mens oppdraget har status **Hjelper valgt** eller **Utført**. Når hjelperen fjernes eller trekker seg, eller oppdraget avbrytes, skjules nummeret igjen.
11. Registrering krever en fødselsdato som gir alder på minst 18 år.
12. KI-forslag endrer aldri et oppdrag direkte. Bare brukeren kan fylle inn forslagene i skjemaet og publisere oppdraget. Bare teksten i beskrivelsesfeltet sendes til KI-tjenesten. Appen legger aldri til navn, e-post, telefonnummer eller andre opplysninger fra profilen.
13. Bare brukeren selv kan slette sin egen konto. Data behandles som beskrevet i «Sletting av konto».

## Suksesskriterier

Kriteriene under er funksjonelle og skal kunne bli testtilfeller (akseptansekriterier i stories). V1 er ferdig når alle er oppfylt.

1. **Registrering og innlogging:** En person kan registrere seg med feltene i «Ved registrering gjelder» og logge inn og ut. Ugyldige felter, alder under 18 år (regel 11) og en e-post som allerede er i bruk avvises med en forståelig melding. En innlogget bruker kan slette sin egen konto etter å ha bekreftet det, og kan deretter ikke logge inn med den (regel 13).
2. **Legge ut og endre oppdrag:** En innlogget bruker kan legge ut et oppdrag med feltene i «Felter i et oppdrag». Oppdraget får status **Åpen**. Ugyldige felter avvises. Oppdragsgiveren kan redigere og avbryte etter regel 4, og forsøk fra andre avvises.
3. **Finne oppdrag:** En bruker ser som standard åpne oppdrag i sitt eget postnummer, sortert etter tidspunkt med det tidligste først, og kan filtrere på kategori og velge et annet postnummer. Bare oppdrag med status **Åpen** og tidspunkt fram i tid vises.
4. **Melde og trekke interesse:** En bruker kan melde interesse med en kort melding, og trekke den tilbake, etter regel 2 og 3. Oppdragsgiveren ser alle interesserte med navn, antall fullførte oppdrag og gjennomsnittlig vurdering.
5. **Velge hjelper:** Oppdragsgiveren kan velge én av de interesserte (regel 5). Status endres til **Hjelper valgt**, og telefonnumrene vises etter regel 10.
6. **Bytte hjelper:** Oppdragsgiveren kan fjerne den valgte hjelperen, og hjelperen kan trekke seg (regel 6). Oppdraget blir **Åpen** igjen, vises i oversikten, og telefonnumrene skjules.
7. **Fullføre oppdrag:** Valgt hjelper kan markere oppdraget som **Utført** (regel 7). Forsøk fra andre avvises.
8. **Tilbakemelding:** Oppdragsgiver og hjelper kan gi hverandre én vurdering (1–5 stjerner) med valgfri kommentar (regel 8). Vurderingen vises i mottakerens profil, og gjennomsnittet oppdateres.
9. **Dokumentert erfaring:** En brukers profil viser antall fullførte oppdrag per kategori, gjennomsnittlig vurdering og alle mottatte tilbakemeldinger, uten kontaktopplysninger (regel 9).
10. **KI-forslag:** En bruker som har skrevet i beskrivelsesfeltet, kan trykke «Få forslag» og få kategori, tittel og beskrivelse foreslått (regel 12). Kategorien er alltid fra den faste listen. I mock-modus gir «måke snø i innkjørselen» kategorien Snømåking, og en tekst uten nøkkelord gir Annet. Hvis svaret er ugyldig eller tjenesten feiler, vises skjemaet uten forslag, og oppdraget kan likevel lagres.

### Kvalitetskrav (ikke-funksjonelle)

- Appen kan startes lokalt ved å følge README, uten betalte tjenester, eksterne kontoer eller gruppens egne nøkler.
- Repoet inneholder eksempeldata (minst 6 testbrukere i 2–3 postnumre og 10–15 oppdrag i ulike statuser) og innloggingsinformasjon for testbrukere i README.
- Passord lagres hashet, og hemmeligheter ligger i `.env` (ikke i repoet) med en `.env.example` som mal.
- Kjerneflyten kan gjennomføres på mobilskjerm.
- KI-funksjonen fungerer i mock-modus uten API-nøkkel (se «Mock-modus»). Prompten ligger i en egen fil i koden, slik at den er lett å finne og forbedre.

## Personvern og sikkerhet i v1

- Vi lagrer bare det som trengs: navn, e-post, hashet passord, telefonnummer, postnummer, fødselsdato og innholdet brukeren selv legger inn.
- Eksakt adresse lagres ikke.
- Hvem som ser oppdrag, profiler og telefonnummer, styres av regel 9 og 10.
- Til KI-tjenesten sendes bare beskrivelsesteksten (regel 12). Når brukeren trykker «Få forslag», får hun beskjed om at teksten sendes til en ekstern tjeneste.
- **Tillit** bygges i v1 gjennom historikk og tilbakemeldinger i profilen, ikke gjennom formell identitetsverifisering. Verifisering med BankID eller Vipps er en planlagt utvidelse (se «Utsatt til senere trinn»).
- Eksempeldata i repoet er oppdiktet og inneholder ingen ekte personopplysninger.

### Sletting av konto

Når en bruker sletter kontoen sin, fjernes personopplysningene. Andre brukeres dokumenterte erfaring skal likevel ikke forsvinne. I oppdrag og tilbakemeldinger som beholdes, vises brukeren som **«Slettet bruker»**.

| Situasjon | Hva skjer |
|---|---|
| Egne oppdrag med status **Åpen** | Slettes, sammen med interessene på dem |
| Egne oppdrag med status **Hjelper valgt** | Settes til **Avbrutt**, slik at hjelperen ser at oppdraget ikke blir noe av. Telefonnumrene skjules |
| Egne oppdrag med status **Avbrutt** | Slettes |
| Oppdrag med status **Utført** (som oppdragsgiver eller hjelper) | Beholdes, men den slettede brukeren vises som «Slettet bruker». Oppdraget teller fortsatt i den andre partens profil |
| Interesser brukeren har meldt | Slettes |
| Brukeren er valgt hjelper på et oppdrag med status **Hjelper valgt** | Oppdraget går tilbake til **Åpen** som i regel 6, slik at oppdragsgiveren kan velge en ny hjelper |
| Tilbakemeldinger brukeren har **gitt** | Beholdes anonymt («Slettet bruker») og teller fortsatt i mottakerens gjennomsnitt |
| Tilbakemeldinger brukeren har **fått** | Slettes sammen med profilen |
| Tilbakemelding som ennå ikke er gitt **til** brukeren | Kan ikke lenger gis (regel 8) |
| E-postadressen | Frigjøres og kan brukes til en ny registrering |

Kommentaren i en anonymisert tilbakemelding kan i noen tilfeller avsløre hvem som skrev den (for eksempel et gatenavn). Det godtar vi i v1. Brukeren får beskjed om dette før kontoen slettes.

## Omfang

Omfanget er delt i tre: det som bygges i v1, det som er bevisst utsatt, og det som ikke skal være en del av produktet.

### Inkludert i v1

- Registrering og innlogging med e-post og passord (se «Aldersgrense»)
- Slette egen konto
- Brukerprofil med historikk og tilbakemeldinger
- Legge ut, redigere og avbryte oppdrag med fast liste over kategorier
- Oversikt over åpne oppdrag med filter på kategori og postnummer
- Melde og trekke interesse, velge og fjerne hjelper, trekke seg som hjelper, markere utført, gi tilbakemelding
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

- Ingen betaling i appen (se «Betaling»).
- Nærhet løses med postnummer (se «Nærhet»).
- Aldersgrense 18 år (se «Aldersgrense»).
- KI brukes bare til forslag ved oppretting av oppdrag, med mock-modus som standard (se «KI-hjelp»).
- Vanlig webapp med én database, som kan kjøres lokalt. Konkret teknologistakk velges i arkitekturfasen, men skal være utbredt og godt dokumentert, og skal ikke kreve betalte tjenester.

## Visjon

På sikt skal *«Finnes det noen i nærheten som kan hjelpe?»* bli et naturlig spørsmål, fremfor å kjøpe noe nytt eller kontakte et firma. Etter v1 kan Nabolagshelten utvides med utlån av utstyr, verifisert identitet og trygg deltakelse for ungdom med godkjenning fra foresatte. Da kan en ungdom få sitt første oppdrag, en arbeidsledig bygge erfaring og referanser, en eldre person få praktisk hjelp, og en nabo låne bort et verktøy som ellers står ubrukt — og bidra til et mer ressursbevisst og inkluderende lokalmiljø.

## Endringer fra versjon 1

| Tilbakemelding | Endring |
|---|---|
| Fjern BankID/Vipps og foresattgodkjenning fra v1 | Vanlig innlogging med e-post og passord, 18-årsgrense. Begge flyttet til «Utsatt». |
| Begrens v1 til én kjerneflyt | Utlån av utstyr flyttet til trinn 2. V1 er oppdragsflyten fra start til tilbakemelding. |
| Testbare suksesskriterier | Funksjonelle kriterier i formen «en bruker kan …» og regler for hvem som kan gjøre hva. |
| Hva skjer etter interesse? | Beskrevet valg av hjelper, deling av telefonnummer, utført og tilbakemelding, med statusmodell. |
| Uavklart betaling og nærhet | Ingen betaling i appen; nærhet via postnummer. |
| Skille fra eksisterende tjenester | Sammenligning med Facebook-grupper, Finn og anbudstjenester. |
| For brede målgrupper | To primærpersoner (Kari og Amir) med konkrete designkonsekvenser for eldre og mobil. |
| Skisser skjermbilder | De fem viktigste skjermbildene er beskrevet og skissert. |
| Kjørbar for sensor | Krav om README, testbrukere, eksempeldata og `.env.example`. |
| Ryddighet i repoet | Briefen er flyttet til `_bmad-output/planning-artifacts/`. |
| Forslag om avgrenset KI-funksjon | KI-forslag til kategori, tittel og beskrivelse lagt inn i v1, med validering, mock-modus, regel 12 og suksesskriterium 10. |

## Endringer i versjon 2.2 (etter review)

| Funn i review | Endring |
|---|---|
| Oppdrag kunne bli stående fast i «Hjelper valgt» | Oppdragsgiver kan fjerne valgt hjelper, og hjelperen kan trekke seg (regel 6, kriterium 6). Interesse kan trekkes tilbake (regel 3). |
| Regel 4 var for vid | Redigering bare mens oppdraget er Åpen. Utført og Avbrutt er endelige. |
| Uklart hvem som ser hva | Ny regel 9 for innsyn i oppdrag og profiler. Regel 10 sier når telefonnummer skjules igjen. |
| Manglende feltvalidering og utgåtte oppdrag | Tabeller for felter i oppdrag og ved registrering. Utgåtte oppdrag vises ikke i oversikten. Sortering etter tidspunkt i kriterium 3. |
| Hull i sletting av konto og mock-modus | Nye rader for avbrutte oppdrag, tilbakemelding til slettet bruker og e-post. Nøkkelordtabell for mock-modus med «Annet» som standard. |
| Gjentakelser og rekkefølge | Målgruppen står foran løsningen. Reglene er eneste kilde, og kriteriene viser til dem. Kvalitetskravene har egen overskrift. |

Med dette har briefen 13 regler og 10 suksesskriterier.
