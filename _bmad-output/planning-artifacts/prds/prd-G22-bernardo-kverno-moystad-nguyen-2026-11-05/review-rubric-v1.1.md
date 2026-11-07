# Kvalitetsreview av PRD – Nabolagshelten (v1.1)

Vurdert: `prd.md` versjon 1.1 (2026-11-07), mot rubrikken i `.claude/skills/bmad-prd/assets/prd-validation-checklist.md`. Product brief v2.2 er fasit, og bevisste avvik i §9.2 er ikke funn i seg selv. Funn fra `review-prd-v1.0-2026-11-07.md` som er rettet i v1.1, er ikke tatt med på nytt.

## Samlet vurdering

Omskrivingen til v1.1 har holdt sporbarheten intakt. «Krav:»-linjene i UJ-1 og UJ-2 stemmer begge veier med sporingslinjene i FR-ene, tabellene i §9.1 stemmer med hver sporingslinje, og statustabellen i §4.0 stemmer med FR-4, FR-7, FR-15, FR-17 og FR-19. Kravene er konkrete og testbare. Risikoen ligger i tre ting: kuttplanen i §6.1 kolliderer med definisjonen av «ferdig» (SM-2 og NFR-5 krever en test av R12, som bare Bør-krav dekker), den nye situasjonstabellen i FR-18 har hull og motsier FR-9 og FR-13, og §9.2 lover en fullstendighet den ikke har. Ingen av funnene blokkerer UX eller arkitektur, men de bør rettes før stories skrives.

## Klar for beslutninger – sterk

Beslutningene står som beslutninger, og avviket fra R7 er begrunnet med problemet det løser («Ellers kunne oppdrag bli stående i Hjelper valgt for alltid», §9.2). Kjente begrensninger er navngitt der de finnes: postnummergrensen (FR-10), uverifisert erfaring og tilbakemeldinger som ikke kan endres (§4.7). §6.1 sier hva som kuttes først og hva det koster. Én avveining mangler: hva som skjer med en ekte bruker som glemmer passordet.

### Funn

- **medium** Glemt passord gir varig utestengning uten utvei (§6.2, FR-1, FR-2, FR-4) – §6.2 sier at passord «ikke kan tilbakestilles» i v1, men ikke hva det betyr sammen med de andre kravene. Innloggingen varer i høyst 7 dager (FR-2), sletting krever passordet (FR-4), og e-postadressen kan ikke brukes til en ny konto så lenge den gamle finnes (FR-1). Kari, som er hovedpersonen og «gir opp hvis noe er uoversiktlig», kan dermed bli stengt ute for godt. Personopplysningene hennes blir liggende, hun kan ikke slette kontoen selv (R13), og hun kan ikke registrere seg på nytt. *Fix:* Skriv det som kjent begrensning i §6.2, med en manuell framgangsmåte slik §4.7 har for kommentarer: «Ber en bruker om det, kan gruppen slette kontoen eller sette nytt passord direkte i databasen.» Vurder også om 7 dager er riktig avveining for Kari.

## Innhold fremfor pynt – sterk

To personer, og begge styrer krav (Kari: 18 px og 48 px, få felter, «Er jobben gjort?»; Amir: oversikt og profil). Hver NFR har tall og en «Testes ved»-linje. Visjonen i §1 kunne ikke vært flyttet til et annet produkt. Motmålene er reelle, men det ene kan ikke måles.

### Funn

- **low** SM-C1 kan ikke måles (§7) – SM-C1 sier at «manuell utfylling skal være like enkel» og er «Motvekt til SM-4». SM-4 måler bare at oppdraget legges ut på under to minutter, ikke med og uten «Få forslag», så motmålet får ingen data. *Fix:* I SM-4: «Hver testperson gjør én runde med og én uten «Få forslag», og begge skal ta under to minutter.» Eller skriv at SM-C1 er en retningslinje som ikke måles.

## Strategisk sammenheng – tilstrekkelig

Tesen er tydelig: lokalt, tydelig status, og småjobber som blir dokumentert erfaring. Kjerneflyten følger tesen, og suksessmålene måler leveranse, noe som passer et sensurert prosjekt. Den andre halvdelen av tesen, at erfaringen «kan brukes i en jobbsøknad» (§1), har ingen mekanisme i v1, og PRD-en sier ikke fra om det.

### Funn

- **medium** Erfaringsbeviset kan ikke vises til en arbeidsgiver (§1, UJ-2 «Avslutningen», §4.7, FR-3, §6.2) – UJ-2 slutter med at Amir «viser til profilen som dokumentasjon på praktisk erfaring» når han søker sommerjobb. Men FR-3 krever innlogging på alle sider, en konto krever telefonnummer og fødselsdato, og eksport til PDF er utsatt (§6.2). En arbeidsgiver kan altså ikke se profilen uten å lage konto. Ingen FR dekker steget, og §4.7 nevner bare at erfaringen ikke er verifisert. *Fix:* Legg til en kjent begrensning i §4.7: «I v1 kan profilen bare ses av innloggede brukere. Amir kan vise den på sin egen skjerm eller som skjermbilde. Deling og PDF er utsatt (§6.2).» Juster UJ-2 tilsvarende. Alternativet er en offentlig profillenke som avvik fra R1, ført i §9.2.
- **low** SM-1 lover mer enn PRD-en gir (§7 SM-1, §9.2) – «Dermed er også suksesskriteriene i briefen (SK1–SK10) oppfylt, bortsett fra det som er kuttet.» SK7 i briefen sier «Forsøk fra andre avvises», mens FR-19 med vilje lar oppdragsgiveren markere Utført. SK10 sier at en bruker «som har skrevet i beskrivelsesfeltet» kan trykke «Få forslag», mens FR-23 krever minst 10 tegn. *Fix:* «… oppfylt, med avvikene i §9.2 og bortsett fra det som er kuttet.»

## Tydelig når det er ferdig – tilstrekkelig

De fleste FR-ene er svært presise: grenser, meldinger, sortering og testdobler er spesifisert. Svakheten er FR-18, som er skrevet om i v1.1. Situasjonstabellen er ikke uttømmende, én rad motsier FR-13, én rad stemmer ikke med FR-9, og sorteringen gir motsatt effekt av det fanen er til for. I tillegg mangler et krav om å se sin egen profil.

### Funn

- **medium** Tabellen i FR-18 er verken uttømmende eller entydig (FR-18, FR-17, UJ-2 «Han kan ikke likevel») – Fanen «Oppdrag jeg hjelper med» viser oppdrag der brukeren «er eller var valgt hjelper», men tabellen har ingen rad for en valgt hjelper som har trukket seg selv. UJ-2 sier heller ikke hva Amir ser etter «Trekk meg». Når en annen er valgt og oppdraget deretter avbrytes, passer to rader: «Ikke valgt» («en annen er valgt») og «Avbrutt». *Fix:* Ny rad: «Trakk seg som valgt hjelper (FR-17) | «Du trakk deg» | Bare tittel og status, til hen eventuelt melder interesse på nytt (FR-12)». Presiser at «Avbrutt» bare gjelder når ingen ble valgt, og at «Ikke valgt» gjelder uansett hvilken status oppdraget får senere.
- **medium** «Venter på svar» lover tilbaketrekking som FR-13 avviser (FR-18 tabellrad 1, FR-13, FR-8) – Raden «Har interesse, status Åpen» sier at «interessen kan trekkes (FR-13)», men FR-13 avviser det når tidspunktet er passert. Den interesserte får heller ikke noe merke når oppdraget er utgått; «Tidspunktet er passert» gjelder bare «Oppdrag jeg har lagt ut». Amir ser derfor «Venter på svar» på et oppdrag som ikke kan bli noe av, og knappen for å trekke interessen gir en avvisning. *Fix:* Del raden i to: «Har interesse, status Åpen, tidspunktet ikke passert | «Venter på svar» | Kan åpnes, og interessen kan trekkes» og «Har interesse, utgått oppdrag | «Tidspunktet er passert» | Kan åpnes, interessen kan ikke trekkes».
- **medium** For en fjernet hjelper stemmer «bare tittel og status» ikke med FR-9 og FR-10 (FR-18 siste rad, FR-17, FR-9, FR-10, FR-12) – Etter fjerningen har oppdraget status Åpen. Da ser «alle innloggede» detaljene (FR-9), og oppdraget «vises igjen i oversikten» (FR-17), også for den fjernede hjelperen hvis hen har samme postnummer. Der får hen knappen «Meld interesse», som FR-12 alltid avviser. Den som skriver storyen, må gjette om hen skal stenges ute fra detaljene (mot FR-9) eller ikke, og i så fall betyr «bare tittel og status» ingenting. *Fix:* Avgjør det og skriv det i FR-12: «En fjernet hjelper ser detaljene som alle andre, men i stedet for «Meld interesse» står det «Du er ikke lenger valgt til dette oppdraget».» Juster kolonnen «Detaljer» i FR-18.
- **medium** Sorteringen i «Mine oppdrag» begraver aktive oppdrag (FR-18, §4.5) – «Resten er sortert etter tidspunkt, tidligste først.» «Resten» omfatter også utførte og avbrutte oppdrag, som har tidspunkt bakover i tid. Etter noen måneder står Amirs «Du er valgt» for neste lørdag under hele historikken. Uten varsler er dette «stedet brukeren ser endringer» (§4.5), så sorteringen motarbeider formålet. Merkene «Hjelperen trakk seg» (FR-17) og «Oppdraget er endret etter at du meldte interesse» (FR-6) løftes heller ikke øverst. *Fix:* «Først oppdrag med merke («Er jobben gjort?», «Gi tilbakemelding», «Tidspunktet er passert», «Hjelperen trakk seg», «Oppdraget er endret …»), deretter oppdrag med status Åpen eller Hjelper valgt etter tidspunkt, tidligste først, og til slutt Utført og Avbrutt, nyeste først.»
- **medium** Ingen FR dekker egen profil (FR-21, UJ-2 «Vendepunktet», NFR-11, FR-2) – FR-21 gjelder «profilen til en annen bruker». UJ-2 forutsetter at Amir ser sitt eget fullførte oppdrag og sin egen vurdering i profilen, og menyvalget «Profil» (NFR-11) må føre et sted. Skisse 5 viser egen profil med «Rediger profil» og «Logg ut», men det står ikke i PRD-en. Kuttes FR-22 (Bør), finnes det ikke noe krav bak menyvalget, og utlogging (FR-2) har ikke noe fast sted. *Fix:* FR-21: «En innlogget bruker kan se sin egen profil og andres. Egen profil ser ut som for andre, med lenke til «Rediger profil» (FR-22) og knappen «Logg ut» (FR-2).»
- **low** NFR-8 krever bekreftelse ved handlinger som ikke kan angres, men ikke ved tilbakemelding (NFR-8, FR-20, §4.7) – Lista har seks handlinger. En tilbakemelding kan verken endres eller fjernes (§4.7), men FR-20 har bare en egen «Send»-knapp. Regelen og lista sier dermed ulike ting. *Fix:* Legg «sende tilbakemelding» til i lista, eller skriv i NFR-8 at «Send» etter at stjernene er valgt, regnes som bekreftelse.
- **low** Merket «Hjelperen trakk seg» er bare halvveis definert (FR-17, FR-18, FR-4) – Merket står i FR-17, men ikke blant merkene i FR-18. Det står ikke om det vises når valgt hjelper sletter kontoen (FR-4: «går tilbake til Åpen som i FR-17»), eller om det blir stående når oppdraget avbrytes eller blir utgått («til en ny hjelper er valgt»). *Fix:* Flytt merket til FR-18, skriv når det forsvinner, og si i FR-4 om det vises ved sletting.
- **low** «Begge bekrefter» kan leses som tosidig bekreftelse (§9.2 første rad, FR-19) – FR-19 krever én bekreftelsesdialog for den som markerer. «Begge bekrefter» kan leses som at begge parter må bekrefte før oppdraget blir Utført, og det er et annet produkt. *Fix:* «Den som markerer, bekrefter i en dialog (FR-19).»
- **low** Testen i FR-3 vil feile på statiske filer (FR-3) – «Alle sider og forespørsler krever innlogging, unntatt registrering og innlogging», og testen går gjennom «alle ruter». Stilark, skript og bilder som innloggingssiden trenger, faller utenfor unntaket. *Fix:* «… unntatt registrering, innlogging og statiske filer (stilark, skript og bilder).»

## Ærlig om omfang – tilstrekkelig

Ikke-mål (§6.3), utsatte funksjoner med begrunnelse (§6.2) og prioritering (§6.1) er tydelige, og §9.2 er et godt grep for sensor. Men kuttplanen er ikke fulgt gjennom til suksessmålene, og §9.2 er ikke så fullstendig som §0 sier.

### Funn

- **high** Kutt av KI-kravene gjør at v1 aldri kan bli ferdig (§6.1, §0, SM-2, NFR-5, SM-4, UJ-1) – §6.1 sier at FR-23–FR-26 kuttes først ved tidsnød, og at da er bare «suksesskriterium SK10 i briefen ikke oppfylt». Men R12 spores bare til FR-23, FR-24 og FR-25 (§9.1). NFR-5 (Må) krever minst én automatisk test for hver regel R1–R13, og SM-2 (primært) krever at testene passerer, uten unntak for kuttede krav. Ifølge §0 er v1 ferdig først når SM-1–SM-3 er nådd. Et kutt som er planlagt, og sannsynlig siden «KI er valgfritt ifølge faglæreren» (§9.2), gjør dermed v1 uferdig per definisjon. SM-4 måler dessuten «UJ-1, steg 1–3», og steg 2 er KI-forslaget. *Fix:* Skriv i §6.1 hva som skjer med R12 ved kutt, for eksempel: «Da finnes ingen KI-funksjon, og R12 testes ikke. SM-2 og NFR-5 gjelder da R1–R11 og R13.» Ta samme unntak inn i SM-2 og NFR-5, og skriv at SM-4 da måler UJ-1 steg 1 og 3 uten KI.
- **medium** §9.2 er ikke fullstendig, slik §0 lover (§0, §9.2) – §0 sier: «Alle presiseringer, avvik og tillegg står med begrunnelse i §9.2.» Disse mangler:
  - FR-23 krever minst 10 tegn før «Få forslag» kan brukes. Ifølge briefen er knappen deaktivert bare «så lenge feltet er tomt», og SK10 gjelder en bruker «som har skrevet i beskrivelsesfeltet».
  - FR-26 endrer mock-reglene i briefen: nøkkelord treffer i starten av ord, punktum legges ikke til etter «!» eller «?» eller når teksten har 1000 tegn, kategorinavnet er reservetittel, og mock-modus gir ikke tips.
  - FR-25 og FR-26 gjør unntak for testdoblene fra briefens «automatiske tester kjører alltid mot mock-modus».
  - FR-1 setter passordet til høyst 64 tegn (briefen: «Minst 8 tegn») og fødselsdatoen til høyst 120 år tilbake, og har en egen regel for 29. februar.
  - FR-25 setter tipset til høyst 200 tegn (briefen: «et kort tips»).
  - §4.0 fjerner mellomrom før lengdesjekk og normaliserer telefonnummer.

  Sensor ser etter at «avvik fra planen er forklart» (kriterium 1). *Fix:* Legg til radene. De fleste kan samles i to rader, «Feltgrenser og normalisering» og «Mock-regler og testdobler». Ellers må påstanden i §0 mykes opp.
- **low** Kutt av FR-22 gir et «om meg»-felt som aldri kan fylles ut (§6.1, FR-1, FR-21, SM-5, NFR-12) – §6.1 sier: «Kuttes FR-22, kan «om meg», postnummer og telefonnummer ikke endres etter registrering.» Men ifølge FR-1 er «om meg» ikke en del av registreringen. Uten FR-22 blir feltet aldri fylt ut, selv om FR-21 (Må) viser det. SM-5 tester «redigering av profil», og NFR-12 tester «om meg». Begge forutsetter FR-22. *Fix:* «Kuttes FR-22, får ingen bruker skrevet «om meg», og postnummer og telefonnummer kan ikke endres. Feltet tas da ut av FR-21, SM-5 og NFR-12.»

## Brukbar for neste steg – sterk

Dette er den sterkeste siden ved v1.1. ID-ene er sammenhengende (UJ-1–2, FR-1–26, NFR-1–12, SM-1–5, SM-C1–C2). «Krav:»-linjene i UJ-1 (14 FR-er) og UJ-2 (10 FR-er) stemmer nøyaktig med brukerreisene i sporingslinjene. Tabellene for R1–R13 og SK1–SK10 i §9.1 stemmer med hver sporingslinje, og statustabellen i §4.0 stemmer med tabellen i FR-4. Ordlisten dekker nesten alle domenebegreper. To ting vil arkitekturen savne:

### Funn

- **low** «Fjernet hjelper» er en tilstand uten begrep (§3, FR-12, FR-17, FR-18) – FR-12 krever at appen husker hvem oppdragsgiveren har fjernet, og FR-18 viser oppdrag der brukeren «var valgt hjelper». Ordlisten sier bare at et oppdrag har «null eller én valgt hjelper», og FR-17 sletter interessen. Datamodellen må altså lagre tidligere valgte hjelpere og om de ble fjernet eller trakk seg, men det står ingen steder. *Fix:* Nytt ord i ordlisten: «Tidligere valgt hjelper – en bruker som var valgt hjelper og ble fjernet (FR-17) eller trakk seg. Appen husker hvem det var og hvorfor (FR-12, FR-18).»
- **low** NFR-9 sier «bare», men flere FR-er lagrer mer (NFR-9, FR-2, FR-23, FR-12) – «Appen lagrer bare navn, e-post, hashet passord, telefonnummer, postnummer, fødselsdato og innhold brukeren selv legger inn.» FR-2 må lagre mislykkede innloggingsforsøk per e-post, FR-23 antall forslag per bruker og FR-12 fjernede hjelpere, og innloggingene må lagres. Testen «Gjennomgang av databaseskjemaet mot lista over» feiler dermed hvis den leses bokstavelig. *Fix:* Legg til «… og data appen trenger for å virke (innlogginger, innloggingsforsøk og antall KI-forslag), som slettes sammen med kontoen.»

## Passer formen til produktet – sterk

Nabolagshelten er et forbrukerprodukt med to roller og eldre brukere. Derfor bærer brukerreisene med navngitte personer kravene, og «Når noe går galt» i hver reise peker på FR-ene som håndterer feilen. Formen passer.

### Funn

- **low** Lengden har vokst langt over målet (hele dokumentet) – PRD-en har gått fra omtrent 6 300 ord (v1.0) til omtrent 9 000 ord. Stakes-avklaringen i memloggen satte målet til 5–8 sider, slik at PRD-en skulle holdes kort med tanke på fristen. Det meste av veksten bærer vekt (tabellen i FR-4, tabellen i FR-18 og reglene i FR-26), men noe gjentas. Samtidighetsregelen står både i §4.0 og i FR-15, og endringsloggen for 1.1 er ett avsnitt på nesten 180 ord. *Fix:* Ikke kutt FR-detaljer. La arkitektur og stories vise til ID-ene i stedet for å kopiere tekst, og la neste endring erstatte tekst i stedet for å legge til.

## Mekaniske notater

- **Henvisninger:** Alle §-henvisninger i brødteksten peker riktig (§0–§9, §4.0, §4.7, §6.1–§6.3, §9.1–§9.2). Endringsloggens rad for 1.0 bruker gammel nummerering («Ny §10», «§7.2»). Raden for 1.1 forklarer omnummereringen, men «(nå §9.2 og §6.2)» ville spare leseren for å regne.
- **§9.1:** Merknaden under tabellene sier at FR-18 kommer fra briefens skjermbilder, «ikke fra en egen regel». FR-18 har likevel R9 i sporingslinjen, og R9-raden lister FR-18. Skriv heller at FR-18 og FR-22 ikke har et eget suksesskriterium.
- **Ordbruk:** §9.2-raden «Valg etter tidspunktet» sier «en interessert som ikke lenger kan trekke seg». Ellers brukes «trekke seg» bare om valgt hjelper (FR-17), så her skal det stå «trekke interessen».
- **Ordbruk:** NFR-11 kaller menyvalget «Oppdrag», mens ordlisten har «Oppdragsoversikt» («oversikten»), og NFR-8 krever ordene fra ordlisten på knapper og overskrifter. Legg «Oppdrag» inn som menynavn i ordlisten, eller kall menyvalget «Oversikt».
- **Antakelser:** PRD-en har ingen [ANTAKELSE]-merker, og §9.2 sier at «Ingen antakelser står åpne». Memloggen viser likevel at noen valg ble tatt som standardvalg som Heidi «protesterte ikke» mot: at en fjernet hjelper ikke kan melde interesse igjen, grensen på 12 måneder, innlogging i 7 dager, grensen på 15 minutter i NFR-1 og at FR-15 avviser valg etter tidspunktet. Valgene står med begrunnelse i §9.2 (unntatt 15 minutter), så rundturen er i orden. Gruppen bør likevel vite at de ikke er aktivt bekreftet.
- **Seksjoner:** Alt som trengs for et sensurert skoleprosjekt, er med: visjon, målgruppe, brukerreiser, ordliste, FR, NFR, omfang, suksessmål med motmål, åpne punkter, sporing og endringslogg.
