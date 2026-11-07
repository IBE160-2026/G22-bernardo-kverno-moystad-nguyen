# Kildeutdrag for UX – Nabolagshelten v1

Laget 2026-11-07. Kilder og forkortelser:
- **PRD** = `prds/prd-G22-…-2026-11-05/prd.md` v1.1 (ferdig). ID-er: UJ-N, FR-N, NFR-N, SM-N.
- **Brief** = `product-brief-nabolagshelten.md` v2.2. Regler R1–R13, suksesskriterier SK1–SK10.
- **Skisser** = `skisser-skjermbilder.md` (status «Forslag til gruppen»).
- **TB** = `tilbakemelding-product-brief.md` (faglærer 2026-10-06).
- **SV** = `docs/sensorveiledning-del1.md`.
Sitat i «» er ordrett. Ved konflikt gjelder PRD (PRD §0: «Briefen er fasit», men PRD presiserer/avviker i §9.2).

## 1. Personer

- **Kari, 72** (Brief «Hvem tjenesten er for»; PRD §2.1, UJ-1). Bor alene i rekkehus. Bruker nettbrett og mobil til nettbank og nyheter, «gir opp hvis noe er uoversiktlig». Trenger: legge ut oppdrag på under to minutter, se hvem som har meldt interesse, velge noen hun føler seg trygg på. *Designkonsekvens (Brief):* «stor og lesbar tekst, få felter per skjerm, tydelige knapper med tekst (ikke bare ikoner), enkelt språk, og fungerer godt på mobil og nettbrett.»
- **Amir, 21, student** (Brief; PRD §2.1, UJ-2). Vil tjene ekstra og ha noe på CV-en. Tid ettermiddager/helger. Trenger: raskt se ledige oppdrag i nærheten, forstå innhold og betaling, samle tilbakemeldinger. *Designkonsekvens (Brief):* «rask liste med filter, tydelig godtgjørelse og tidspunkt, profil som viser erfaringen hans.»
- **Andre navn i skisser:** Sara («2 fullførte · 5,0 av 5», «Bor rett over gata.»), Jonas («Ingen fullførte ennå») – interesserte i skisse 3b.
- **Andre grupper:** barnefamilier, travle, arbeidsledige – samme flyt (PRD §2.1, Brief).
- **Ikke målgruppe v1:** under 18 år; firmaer, håndverkere, store/komplekse oppdrag (PRD §2.2).
- **Ingen kontotyper:** samme bruker kan være oppdragsgiver og hjelper (PRD §2.1, §3 «Bruker»). «Hjelper» = «oppdragstaker» i briefen; PRD bruker bare «hjelper».

## 2. Brukerreiser

### UJ-1 Kari får måkt innkjørselen (PRD §2.3)
Utgangspunkt: har konto, innlogget på nettbrett, starter på oppdragsoversikten. Mandag morgen i januar.
1. Trykker «Legg ut oppdrag», skriver i beskrivelsesfeltet: «Trenger noen som kan måke snø i innkjørselen min i morgen.»
2. Trykker «Få forslag». KI foreslår tittel, kategori (Snømåking), bedre beskrivelse; hun trykker «Bruk».
3. Postnummer forhåndsutfylt og riktig; velger tidspunkt, 200 kr, trykker «Publiser». Status **Åpen**, synlig for alle som ser på hennes postnummer.
4. Senere: «Mine oppdrag» → ser at to har meldt interesse → åpner. Per interessert: navn, antall fullførte, snittvurdering, melding.
5. Velger den hun er tryggest på → **Hjelper valgt**; de ser hverandres telefonnummer.
- Vendepunkt: sammenligne interesserte på erfaring og vurderinger.
- Avslutning: hjelper måker; Kari betaler med Vipps utenfor appen; hjelper markerer **Utført**; Kari gir fem stjerner + kort kommentar, vises i hjelperens profil.
- Når noe går galt:
  - *Ingen melder interesse:* fortsatt **Åpen** under «Mine oppdrag»; kan redigere tidspunkt/godtgjørelse.
  - *Tidspunktet passerer uten hjelper:* forsvinner fra oversikten, ingen nye interesser; merket «Tidspunktet er passert»; kan endre tidspunkt eller avbryte.
  - *Hjelper glemmer å markere utført:* etter tidspunktet står «Er jobben gjort?»; Kari markerer **Utført** selv og gir tilbakemelding.
- Krav: FR-5, 6, 7, 8, 14, 15, 16, 18, 19, 20, 21, 23, 24, 25.

### UJ-2 Amir bygger profil (PRD §2.3)
Utgangspunkt: ingen konto, åpner nettsiden på mobil en ettermiddag.
1. Registrerer seg: navn, e-post, telefon, postnummer, fødselsdato, passord. Over 18 → konto opprettes, innlogget.
2. Oversikten viser åpne oppdrag i hans postnummer, sortert etter tidspunkt. Ser Bærehjelp/flytting lørdag, 400 kr.
3. Åpner, leser, skriver melding («Hei! Jeg kan gjerne hjelpe deg på lørdag. Jeg har erfaring med å bære møbler fra tidligere flyttinger.») og trykker «Meld interesse».
4. «Mine oppdrag», fanen «Oppdrag jeg hjelper med»: merket «Du er valgt»; ser oppdragsgiverens telefonnummer.
5. Bærer møbler, markerer **Utført**, får 400 kr med Vipps utenfor appen.
- Vendepunkt: får fem stjerner og kommentar; ser fullført oppdrag og vurdering i profilen.
- Avslutning: gir oppdragsgiveren vurdering også; profilen viser antall fullførte per kategori, snitt, tilbakemeldinger; viser profilen på mobilen ved jobbsøknad.
- Når noe går galt:
  - *Oppdragsgiver velger en annen:* merket «Ikke valgt», ser bare tittel og status.
  - *Han kan ikke likevel:* mens **Hjelper valgt** trykker «Trekk meg» og bekrefter → **Åpen**, numre skjules, oppdragsgiver kan velge blant andre; merket «Du trakk deg».
- Krav: FR-1, 9, 10, 12, 16, 17, 18, 19, 20, 21.

### Kjerneflyt (Brief «Kjerneflyten i v1»; PRD §1)
Legge ut → finne → melde interesse → velge hjelper → markere utført → gi tilbakemelding. Briefens eksempel: «Trenger hjelp til å måke innkjørselen i morgen tidlig – 200 kr»; melding «Jeg kan komme kl. 07:30».

## 3. Skjermer og flater

Navigasjon: fast meny med tre valg **Oppdrag · Mine oppdrag · Profil** etter innlogging (NFR-11; Skisser «Fast meny nederst»). Menyvalget for oversikten heter «Oppdrag» (PRD §3). Brief «Viktigste skjermbilder» nr. 1–5 + ikke-skisserte.

| Skjerm | Kilde | FR/NFR |
|---|---|---|
| Registrering (med personverntekst) | PRD FR-1; Skisser «Ikke skissert ennå» | FR-1, FR-3 (åpen uten innlogging), NFR-7, NFR-8 |
| Innlogging | PRD FR-2; Skisser «Ikke skissert ennå» | FR-2, FR-3 |
| 1 Oppdragsoversikt (startside) | Brief #1; Skisse 1 | FR-8, FR-10, FR-11, (FR-5 «Legg ut oppdrag»-knapp) |
| 2 Nytt oppdrag (evt. 2 steg) | Brief #2; Skisse 2 | FR-5, FR-23, FR-24, FR-25, FR-26, NFR-9 |
| Rediger oppdrag (samme skjerm, «Lagre endringer», uten KI) | Skisse 2 merknad; PRD FR-6 | FR-6, FR-23 (ikke ved redigering) |
| 3 Oppdragsdetaljer, varianter 3a–3d | Brief #3; Skisse 3 | FR-7, FR-9, FR-12, FR-13, FR-14, FR-15, FR-16, FR-17, FR-19, FR-20 |
| Bekreftelsesdialoger (velge, fjerne, trekke seg, avbryte, utført, slette konto) | PRD NFR-8; FR-7, 15, 17, 19, 4 | NFR-7 (fokushåndtering), SM-5 |
| Tilbakemeldingsskjema (i detaljer, 3d) | Skisse 3d; PRD FR-20 | FR-20 |
| 4 Mine oppdrag (to faner) | Brief #4; Skisse 4 | FR-8, FR-18, FR-19, FR-20 |
| 5 Profil (egen og andres) | Brief #5; Skisse 5 | FR-21, FR-2 («Logg ut»), FR-4 (lenke) |
| Rediger profil | PRD FR-22; Skisser «Ikke skissert ennå» | FR-22 |
| Slett konto (bekreftelse med passord) | PRD FR-4; Skisser «Ikke skissert ennå» | FR-4 |
| Melding for slettet brukers profil (direkte lenke) | PRD FR-4 | FR-4 |
| Tomtilstander (oversikt, interesserte, faner i Mine oppdrag) | FR-10, FR-14, FR-18; NFR-7 | |
| Skjema med valideringsfeil | SM-5 | NFR-7, NFR-10 |

SM-5 sidene som skal testes med axe: de fem viktigste skjermbildene, registrering, innlogging, redigering av profil, et skjema med valideringsfeil og hver bekreftelsesdialog.

### Innhold per skjerm (krav)
- **Oversikt (FR-10, FR-11):** bare Åpen + tidspunkt ikke passert; sortert tidligste først, likt tidspunkt → eldste lagt ut først; hvert kort: tittel, kategori, tidspunkt, godtgjørelse; egne oppdrag vises ikke; tomtilstand «med forklaring og forslag (for eksempel å velge et annet postnummer)»; filter kategori + annet postnummer (erstatter eget; ukjent postnummer avvises med melding); filtre kombineres. Kjent begrensning: postnummergrenser.
- **Detaljer (FR-9):** alle felt + status + oppdragsgivers navn, antall fullførte, snitt (som FR-21), lenke til profil. Åpen: alle innloggede ser; bare oppdragsgiver ser interesserte. Andre statuser: bare oppdragsgiver + valgt hjelper.
- **Interesserte (FR-14):** navn, antall fullførte, snitt (eller «Ingen vurderinger ennå»), melding, evt. «Meldt før endring», lenke til profil; eldste først; tomtilstand med forklaring.
- **Profil (FR-21):** navn, postnummer med poststed, «om meg» (skjules hvis tom, FR-22), antall fullførte per kategori, snitt, alle mottatte tilbakemeldinger nyeste først. Per tilbakemelding: vurdering, kommentar, hvem, dato, rolle (som hjelper/oppdragsgiver). Snitt: én desimal, desimalkomma + antall: «4,3 av 5, 7 vurderinger» (samme visning i FR-9, FR-14). Uten vurderinger: «Ingen vurderinger ennå». Fullførte = Utført der brukeren var valgt hjelper. Kort tekst om at fullførte oppdrag og tilbakemeldinger er registrert av brukere i Nabolagshelten og ikke er verifisert. «Slettet bruker» uten lenke. Aldri telefon, e-post, fødselsdato. Egen profil = som for andre + lenke «Rediger profil» + knapp «Logg ut». Kan bare ses av innloggede; vises på egen skjerm/skjermbilde (PDF utsatt, §4.7).
- **Rediger profil (FR-22, prioritet Bør):** «om meg» (valgfri, maks 500), postnummer, telefonnummer (validert som FR-1). Viser egne opplysninger inkl. e-post og telefon. Navn, e-post, fødselsdato kan ikke endres. Nytt postnummer straks standard i oversikt og nye oppdrag; eksisterende oppdrag beholder sitt.

## 4. Statusmodell (PRD §4.0; Brief «Statuser»)

Statuser: **Åpen**, **Hjelper valgt**, **Utført**, **Avbrutt**. Utført og Avbrutt er endelige. «Utgått oppdrag» = Åpen med passert tidspunkt, ikke egen status (FR-8). «Passert» måles i Europe/Oslo.

| Fra | Til | Hvem/når | Krav |
|---|---|---|---|
| (nytt) | Åpen | Oppdragsgiver legger ut | FR-5 |
| Åpen | Hjelper valgt | Oppdragsgiver velger, før tidspunktet er passert | FR-15 |
| Hjelper valgt | Åpen | Oppdragsgiver fjerner, eller valgt hjelper trekker seg | FR-17 |
| Hjelper valgt | Utført | Valgt hjelper fra dagen for tidspunktet (fra kl. 00:00), eller oppdragsgiver når tidspunktet er passert | FR-19 (avvik fra R7) |
| Åpen / Hjelper valgt | Avbrutt | Oppdragsgiver | FR-7 |
| Hjelper valgt | Avbrutt | System, oppdragsgiver sletter konto | FR-4 |
| Hjelper valgt | Åpen | System, valgt hjelper sletter konto | FR-4 |
| Åpen / Avbrutt | (slettet) | System, oppdragsgiver sletter konto | FR-4 |

Handlinger per rolle/status (Brief #3, Skisse 3, PRD):
- Annen bruker, Åpen: «Meld interesse» (melding valgfri) → etterpå «Du har meldt interesse» (FR-12) + lenke «Trekk interessen» (FR-13, mens Åpen og ikke passert).
- Fjernet hjelper ser i stedet for knappen: «Du er ikke lenger valgt til dette oppdraget» (FR-12). Den som trakk seg selv kan melde på nytt.
- Oppdragsgiver, Åpen: «Rediger», «Avbryt oppdrag», liste med «Velg».
- Hjelper valgt: telefonboks for begge; valgt hjelper: «Marker som utført» + «Trekk meg fra oppdraget» (UJ-2 kaller knappen «Trekk meg»); oppdragsgiver: «Fjern hjelper», «Avbryt oppdrag».
- Utført: «Gi tilbakemelding».
- Fjerning/tilbaketrekking: den tidligere hjelperens interesse slettes, andre beholdes; numre skjules; vises igjen i oversikten hvis ikke passert (FR-17).
- Avbrutt fra Hjelper valgt: hjelperen ser det som Avbrutt under «Oppdrag jeg hjelper med», kan åpne detaljer uten telefonnumre (FR-7).
- Redigering mens Åpen: interesser beholdes; endres tidspunkt/godtgjørelse/postnummer → «Meldt før endring» i interessertlista og «Oppdraget er endret etter at du meldte interesse» hos den interesserte (FR-6).
- Telefon vises bare for de to partene, bare ved Hjelper valgt eller Utført; ikke for slettet bruker (FR-16).

### «Mine oppdrag» – fanen «Oppdrag jeg hjelper med» (FR-18, ordrett)

| Brukerens situasjon | Vises som | Detaljer |
|---|---|---|
| Har interesse, Åpen, ikke passert | «Venter på svar» | Kan åpnes, interessen kan trekkes |
| Har interesse, utgått oppdrag | «Tidspunktet er passert» | Kan åpnes; kan ikke trekke |
| Har interesse, annen valgt hjelper (Hjelper valgt/Utført/Avbrutt) | «Ikke valgt» | Bare tittel og status |
| Har interesse, Avbrutt uten valgt hjelper | «Avbrutt» | Bare tittel og status |
| Valgt hjelper, Hjelper valgt | «Du er valgt» | Kan åpnes, med telefonnumre |
| Valgt hjelper, Utført | «Utført» | Kan åpnes |
| Valgt hjelper, Avbrutt | «Avbrutt» | Kan åpnes, uten telefonnumre |
| Fjernet som valgt hjelper | «Du er ikke lenger valgt» | Som andre innloggede; kan ikke melde igjen |
| Trakk seg, uten ny interesse | «Du trakk deg» | Som andre innloggede; kan melde på nytt |

- Fanen «Oppdrag jeg har lagt ut»: alle egne oppdrag med status, antall interesserte, navn på valgt hjelper.
- Tilleggsmerker (FR-18): «Tidspunktet er passert» (egne utgåtte); «Er jobben gjort?» (begge parter, Hjelper valgt + passert); «Gi tilbakemelding» (Utført, ikke gitt, ikke når motpart er «Slettet bruker»); «Hjelperen trakk seg» (hos oppdragsgiver når valgt hjelper trakk seg eller slettet konto; forsvinner når ny hjelper velges eller oppdraget avbrytes); «Oppdraget er endret etter at du meldte interesse».
- Sortering begge faner: først med merke; så Åpen/Hjelper valgt etter tidspunkt tidligste først; til slutt Utført/Avbrutt nyeste tidspunkt først.
- Tom fane: forklaring + lenke – «Oppdrag jeg har lagt ut» → «Legg ut oppdrag»; «Oppdrag jeg hjelper med» → oversikten.
- Uten varsler er «Mine oppdrag» stedet brukeren ser endringer (PRD §4.5, §6.2).

## 5. Ordrette UI-tekster

Knapper/etiketter: «Legg ut oppdrag», «Få forslag» (skisse: «Få forslag til tekst»), «Bruk», «Forkast», «Publiser» (skisse: «Publiser oppdrag»), «Lagre endringer», «Neste», «Meld interesse», «Trekk interessen», «Velg», «Ja, velg Amir», «Avbryt», «Rediger», «Avbryt oppdrag», «Fjern hjelper», «Trekk meg» / «Trekk meg fra oppdraget», «Marker som utført», «Gi tilbakemelding», «Send» (PRD FR-20; skisse: «Send tilbakemelding»), «Rediger profil», «Logg ut», «Slett konto», «Se profil», «Endre tidspunkt», «Vis avbrutte oppdrag», «Vis alle tilbakemeldinger». Faner: «Oppdrag jeg har lagt ut», «Oppdrag jeg hjelper med» (skisse kortform: «Lagt ut (3)», «Hjelper med(2)»).

Meldinger:
- Samtidighetskonflikt: «Oppdraget er endret. Last siden på nytt.» (§4.0)
- Hjelpetekst beskrivelse: «Ikke skriv adresse eller telefonnummer – det avtaler dere når hjelperen er valgt.» (FR-5, NFR-9)
- Passert tidspunkt ved redigering: «Velg et nytt tidspunkt fram i tid» (FR-6)
- Velge-bekreftelse: «Velge Amir? Dere får se hverandres telefonnummer.» (FR-15)
- Utført-bekreftelse: «Marker som utført? Det kan ikke angres.» (FR-19)
- Kvittering tilbakemelding: «Takk! Tilbakemeldingen er lagt til i Amirs profil.» (FR-20, NFR-8)
- Stjerne for skjermleser: «4 av 5 stjerner» (FR-20)
- KI venter: «Lager forslag …» (FR-23)
- KI-feil: «Vi fikk ikke laget forslag akkurat nå. Du kan fylle inn selv.» (FR-25; Skisse 2)
- KI-tips eksempel: «Skriv gjerne hvor stor innkjørselen er» (FR-24)
- Ingen vurderinger: «Ingen vurderinger ennå» (FR-14, FR-21)
- Snitt: «4,3 av 5, 7 vurderinger» (FR-21); skisse: «4,9 av 5 i snitt (11 vurderinger)», «12 fullførte · 4,9 av 5»
- Etter meldt interesse (Skisse 3a): «Du har meldt interesse. Under Mine oppdrag ser du om Kari har valgt deg.»
- Tomtilstand oversikt (Skisse 1): «Ingen ledige oppdrag i 0571 akkurat nå.» (lenken <Se alle postnumre> skal fjernes, PRD §8)
- Skisse feltfeil-eksempel: «Skriv en tittel»
- Skisse 2: «Hva trenger du hjelp til?» «Skriv med egne ord.»; «Teksten sendes til en ekstern tjeneste for å lage forslag.»; «Når?»; «Hva tilbyr du?»; «Slik vises oppdraget for andre.»; overskrift oversikt «Ledige oppdrag i 0571»
- Skisse 3c: «Avtal detaljene direkte.»; 3d: «Hvordan gikk det med Amir?», «Kommentaren vises i Amirs profil.»; skala-ender «Dårlig» / «Veldig bra»
- Skisse 4 grupper: «Trenger handling», «Pågår», «Ferdige»
- Navn i stedet for slettet bruker: «Slettet bruker» (PRD §3, FR-4)
- Innlogging feil: samme melding for feil e-post/passord; etter 5 mislykkede på 15 min: melding om å prøve igjen senere (FR-2, tekst ikke gitt)
- KI-grense: «vennlig melding» over 20/time (FR-23, tekst ikke gitt)

## 6. Felt, grenser og validering

Felles (§4.0): mellomrom i start/slutt fjernes før lengdesjekk; bare mellomrom = tomt; telefon godtas med mellomrom og +47/0047, lagres som 8 siffer; hver ugyldig verdi gir forståelig melding rett ved feltet; alt utfylt beholdes (unntatt passord); sendeknapper deaktivert mens forespørsel pågår. Validering også på server (NFR-10); aldri teknisk feilmelding.

Registrering (FR-1): navn 1–80; e-post gyldig format, unik uten skille store/små; passord 8–64; telefon 8 siffer; postnummer i lista (vises med poststed); fødselsdato ikke etter i dag, høyst 120 år tilbake, alder ≥ 18 (norsk tid; fyller 18 i dag = OK; 29. feb → 1. mars i ikke-skuddår). Personverntekst på siden: hva som lagres; navn, postnummer og profil vises for alle innloggede; telefon deles bare med motparten når hjelper er valgt; beskrivelse kan sendes til ekstern KI; kontoen kan slettes. «Om meg» ikke i registrering. Innlogget etterpå.

Innlogging (FR-2): e-post + passord; innlogging varer høyst 7 dager. Glemt passord utsatt (§6.2) – ingen «glemt passord»-flyt i v1.

Oppdrag (FR-5): alle obligatoriske. Tittel 3–80; beskrivelse 10–1000; kategori fra lista: Snømåking, Hage, Bærehjelp/flytting, Dyrepass, Teknologihjelp, Annet (skisse: nedtrekk); postnummer i lista, forhåndsutfylt fra profil, kan endres; tidspunkt = dato og klokkeslett, ikke passert, høyst 12 måneder fram, i Europe/Oslo; godtgjørelse heltall 1–10 000 kr eller «uten betaling» (skisse: radioknapper «Beløp [ ] kr» / «Uten betaling»).

Interessemelding: valgfri, maks 500 (FR-12). Kommentar i tilbakemelding: valgfri, maks 500 (FR-20). «Om meg»: valgfri, maks 500 (FR-22).

Slett konto (FR-4): krever passord; feil passord avviser. Forklaring før sletting, inkl. at gitte tilbakemeldinger beholdes som «Slettet bruker» og at kommentarer i noen tilfeller kan avsløre hvem som skrev dem. Alle innlogginger avsluttes. Datatabell i FR-4 (Åpne egne slettes; Hjelper valgt → Avbrutt; Utført beholdes med «Slettet bruker» osv.).

## 7. KI-forslag – UX-regler (FR-23–FR-26, prioritet Bør; Brief «KI-hjelp», R12)

- Bare i skjema for **nytt** oppdrag, ikke ved redigering.
- «Få forslag» aktiv fra 10 tegn i beskrivelsen; deaktivert under.
- Før trykk står det ved knappen at teksten sendes til en ekstern KI-tjeneste; i mock-modus står det at teksten ikke sendes ut.
- Bare beskrivelsesteksten sendes; aldri profilopplysninger.
- Under henting: knappen deaktivert med «Lager forslag …», skjermleser leser opp.
- Forslag (kategori, tittel, beskrivelse) vises ved feltene; på smal skjerm under feltet det gjelder (FR-24, NFR-6). «Bruk»/«Forkast» per forslag. Fyller aldri inn før «Bruk»; feltet kan redigeres etterpå. Tips vises sammen med forslag (mock gir ikke tips; tips maks 200 tegn).
- Beskrivelsesforslag omformulerer bare det brukeren skrev, ingen nye opplysninger; manglende info kommer som tips. Bokmål.
- Ugyldig svar / tidsavbrudd 10 s / feil: vennlig melding, skjemaet beholder tekst, kan lagres manuelt. Ren tekst, aldri HTML.
- KI lagrer/publiserer aldri; bare «Publiser» lagrer.
- Maks 20 forslag per bruker per time.
- Appen virker fullt uten KI (PRD §1; Brief). Mock-modus standard uten API-nøkkel (NFR-1). Mock: «måke snø i innkjørselen» → Snømåking, tittel «Måke snø i innkjørselen».
- **SM-C1 (motmål):** andel oppdrag laget med KI skal ikke presses opp; «manuell utfylling skal være like enkel». «brukes som retningslinje i UX-steget».
- Skisse 2: «Få forslag» er sekundær knapp; kan hoppes over; forslagsboks vises bare etter trykk.

## 8. Ikke-funksjonelle krav relevante for UX

- **NFR-6 Responsiv:** hele kjerneflyten fra 360 px til PC, ingen vannrett rulling, ingen egen mobilapp. Testes manuelt UJ-1 og UJ-2 ved **360, 768 og 1280 px**, med skjermbilder. (Brief: «fra 360 px bredde»; skisser tegnet for 360 px, «På nettbrett og PC kan de samme elementene ligge bredere.»)
- **NFR-7 Universell utforming – WCAG 2.1 AA:** kontrast ≥ 4,5:1 for tekst; alt med tastatur, synlig fokus, også dato- og klokkeslettvalg; synlige etiketter på alle felt; feilmeldinger ved feltet og knyttet til det; knapper med tekst, ikke bare ikoner; meningsbærende bilder/ikoner har alt-tekst; brødtekst ≥ 18 px; knapper/trykkflater ≥ 48 px høye; zoom 200 % uten tap; status alltid med ord, ikke bare farge; statusmeldinger («Lager forslag …», kvitteringer, feil etter innsending) leses opp av skjermleser; bekreftelsesdialoger flytter fokus inn og tilbake etterpå; `lang="nb"`; tomtilstander med forklaring. *Testes ved:* axe (SM-5: ingen «serious»/«critical»), manuell tastaturgjennomgang av kjerneflyten, manuell UJ-1 med skjermleser (NVDA eller VoiceOver), dokumentert.
- **NFR-8 Språk:** norsk bokmål, enkelt språk; ord fra ordlisten (§3) og skissene («Meld interesse», ikke «Send forespørsel»); hver handling gir tydelig kvittering; irreversible handlinger krever bekreftelse: avbryte oppdrag, velge hjelper, fjerne hjelper, trekke seg, markere utført, slette konto. For tilbakemelding regnes «Send» etter stjernevalg som bekreftelse. Testes manuelt mot ordlisten.
- **NFR-9 Personvern:** ber aldri om eksakt adresse; hjelpetekst ved beskrivelse.
- **NFR-10 Robust:** forståelige meldinger, aldri teknisk feil/krasj.
- **NFR-11 Navigasjon:** fast meny Oppdrag, Mine oppdrag, Profil.
- **NFR-12:** bruker- og KI-tekst alltid som tekst.
- **Ytelse:** ingen eksplisitt responstidskrav utover KI-tidsavbrudd 10 s (FR-25). SM-4: legge ut oppdrag (UJ-1 steg 1–3) på **under to minutter** på mobil/nettbrett, brukertest med ≥ 2 personer utenfor gruppen, minst én over 60 eller lite app-vant; tid fra «Legg ut oppdrag» til publisert; enhet, nettleser og tid dokumenteres.
- **Samtidighet:** dobbeltklikk/to faner → bare første utføres (§4.0, FR-15).
- **NFR-2 Eksempeldata:** dekker alle UX-tilstander (alle kategorier, flere interesserte, Hjelper valgt, Utført med/uten tilbakemelding, Avbrutt, utgått, «Er jobben gjort?», bruker med/uten vurderinger) – nyttig for skjermbilder og tester.

## 9. PRD §8 – punkter til UX-steget (ordrett)

- **UX-steget (`bmad-ux`) oppdaterer skissene:**
  - Tilbakemelding: 1–5 stjerner som store knapper og en egen «Send»-knapp, ikke tallknapper (FR-20, NFR-7).
  - Oversikten: tidspunkt som dato og klokkeslett, ikke «Fleksibelt denne uken» (FR-5).
  - Tomtilstanden i oversikten: lenken «Se alle postnumre» fjernes, fordi filteret alltid gjelder ett postnummer (FR-11).
  - Eksemplet på KI-forslag legger til opplysninger brukeren ikke skrev («Spade finnes»), og rettes (FR-24).
  - «Mine oppdrag» viser brukerens egen situasjon og merkene i FR-18. Spørsmål 3 i skissene (merke for ny interesse i menyen) avgjøres her.
  - Skjemaet for nytt oppdrag skal ikke vise for mange felter på én skjerm. Skissene foreslår to steg; endelig oppsett avgjøres her.
  - Skjermene som mangler: registrering, redigering av profil og sletting av konto (med passord).
- (Arkitektur avgjør: kilde til postnummerliste, CSRF-mekanisme (NFR-12), sommertid og tegnsett.)

## 10. Eksisterende skissebeslutninger (Skisser)

Felles prinsipper (ordrett):
- «**Stor tekst og store trykkflater.** Brødtekst minst 18 px, knapper minst 48 px høye.»
- «**Knapper med tekst**, ikke bare ikoner. «Legg ut oppdrag», ikke bare «+».» (NB: skisse 1 viser «+ Legg ut oppdrag»)
- «**Én hovedhandling per skjerm**, som en tydelig fylt knapp. Mindre viktige handlinger er vanlige lenker eller omrissede knapper.»
- «**Status vises alltid med ord**, for eksempel «Åpen» eller «Hjelper valgt», ikke bare med farge.»
- «**Fast meny nederst** med tre valg: Oppdrag · Mine oppdrag · Profil.»
- «**Enkelt språk.** «Meld interesse», ikke «Send forespørsel».»

Per skjerm:
1. Oversikt: header «Nabolagshelten»; hovedknapp øverst; «Ledige oppdrag i 0571»; filter Kategori (nedtrekk «Alle») + Postnummer (tekstfelt); kort med tittel/kategori/tidspunkt/beløp; **hele kortet trykkbart** → detaljer. Tidsformat i skisse: «I morgen kl. 07:00», «Lørdag 14. nov. kl. 12:00».
2. Nytt oppdrag i **to steg** («Nytt oppdrag 1/2», «2/2», «<- Tilbake»). Steg 1: beskrivelse først («Hva trenger du hjelp til?»), «Få forslag» sekundær, forslagsboks, så Tittel og Kategori, «Neste». Steg 2: Postnummer, Når? (dato + klokkeslett, f.eks. «06.11.2026» «07:00»), Hva tilbyr du? (radio), **forhåndsvisning av kortet** («Slik vises oppdraget for andre.»), «Publiser oppdrag». Feil under feltet. Samme skjerm for redigering («Lagre endringer»), bare Åpen.
3. Detaljer: én skjerm, innhold nederst avhenger av rolle og status (3a–3d). Telefonboks: «Hjelper: Amir / Telefon: 912 34 567 / Avtal detaljene direkte.» «Trekk meg fra oppdraget» som lenke, «Fjern hjelper»/«Avbryt oppdrag» som sekundære. Velg-bekreftelse: [ Ja, velg Amir ] og <Avbryt>. 3d hadde tallknapper 1–5 (begrunnet «lettere å treffe og forstå») – **erstattes av 1–5 stjerner** (PRD FR-20, §8, §9.2).
4. Mine oppdrag: faner med antall; gruppert etter hva brukeren må gjøre («Trenger handling», «Pågår», «Ferdige»), handling øverst; avbrutte skjult bak <Vis avbrutte oppdrag>; utgåtte under «Trenger handling» med «Endre tidspunkt» og «Avbryt». (Må avstemmes med FR-18-sorteringen og -merkene.)
5. Profil: samme skjerm for andre («Se profil») uten redigering; <Vis alle tilbakemeldinger>; bare egen: ( Rediger profil ), <Logg ut>, <Slett konto> («lite fremtredende lenke nederst», åpner bekreftelse). NB: PRD FR-21 sier «knappen «Logg ut»».

Kjente nødvendige endringer: stjerner 1–5 i stedet for tallknapper; dato+klokkeslett i stedet for «Fleksibelt denne uken» (skisse 1, «Sette opp ny iPad»); fjerne «Se alle postnumre»; rette KI-eksempelet («Innkjørselen er ca. 10 meter. Spade finnes.» legger til opplysninger – også i 3a «Spade finnes i garasjen»); mangler skjermer for registrering (+ innlogging), rediger profil, slett konto (med passord).

**Spørsmål til gruppen (Skisser, ordrett):**
1. «Er det greit å dele «Nytt oppdrag» i to steg, eller vil dere ha alt på én skjerm?»
2. «Skal oversikten ha en egen kategori-rad med knapper (lettere å trykke) i stedet for nedtrekksliste?»
3. «Holder det at brukeren ser status ved å åpne appen, eller trengs et tydelig «ny interesse»-merke på «Mine oppdrag» i menyen? (Varsler på e-post/push er utsatt.)»

## 11. Faglærers tilbakemelding (TB) – UX-relevant

- «Who This Serves» (Juster): «Velg én typisk oppdragsgiver og én typisk oppdragstaker å designe for. Hvis eldre er en viktig målgruppe, må designet ta hensyn til det.»
- «The Solution» (Juster): manglet hva som skjer etter interesse – valg av hjelper, avtale tid, markere utført (nå løst i statusmodell).
- Kriterium 4 Design og brukeropplevelse (10 %), Juster: «Skisser de 4–5 viktigste skjermbildene: oppdragsliste, nytt oppdrag, oppdragsdetaljer, profil. Tenk på eldre brukere og mobil.»
- Positivt: konkrete eksempler («måke innkjørselen i morgen tidlig», «sette opp en ny iPad»).
- Ingen sanntidschat i v1 – «det er bra». KI-forslag til kategori/tydeligere tekst foreslått som avgrenset, testbar utvidelse.
- «Lokal tilhørighet» løses med postnummer.

## 12. Sensorveiledning (SV) – kriterier som påvirker UX-dokumentene

- **Kriterium 4 Design og UX (10 %):** «Konsistent uttrykk og tydelig navigasjon. Tydelige tilbakemeldinger, feilmeldinger og tomtilstander. Universell utforming: kontrast, tastaturnavigasjon, alt-tekst, skjemaetiketter, tilpasning til skjermstørrelser. Spor av designarbeid (skisser, wireframes, UX-beskrivelser).»
- **Kriterium 1 Prosess (30 %):** BMAD-dokumenter «faktisk brukt og oppdatert, ikke bare generert én gang»; funksjoner sporbare til krav og stories; avvik forklart; prompts og beslutninger koblet til konkrete endringer. → UX-dokumentene bør referere FR/NFR/UJ-ID-er og logge beslutninger.
- **Kriterium 2:** appen tåler feil input; utelatt/endret er beskrevet og begrunnet.
- **Kriterium 3:** dokumenterte manuelle tester der automatiske ikke passer (jf. NFR-6, NFR-7, SM-4).
- **Kriterium 6 README:** kort beskrivelse og **skjermbilde**.
- **Varseltegn:** «Planleggingsdokumentene beskriver en annen app enn den som er levert, eller er tydelig generert i etterkant.»
- CLAUDE.md: krav-ID-er sporbare PRD → stories → commits → kode; universell utforming; planleggingsdokumenter holdes oppdatert.

## 13. Visuell stil, farger, tone, merkevare

- **Ingen farger, typografi, logo eller merkevareprofil er definert** i noen av kildene. Skissene «viser innhold og rekkefølge, ikke endelig utseende».
- Gitt: produktnavn «Nabolagshelten» (header i skisse 1); hovedknapp fylt, sekundær omriss eller lenke; kort/bokser for oppdrag, interesserte, telefon, tilbakemeldinger; kontrast ≥ 4,5:1; farge aldri eneste statusbærer; ≥ 18 px brødtekst; ≥ 48 px trykkflater.
- Tone: enkelt, vennlig bokmål («vennlig melding» ved KI-feil og kvote); kjerneidé: «det finnes ofte noen i nærheten som kan hjelpe» (Brief); visjon: «Finnes det noen i nærheten som kan hjelpe?» Tillit gjennom historikk og tilbakemeldinger, ikke verifisering; ærlig om at erfaringen ikke er verifisert.
- Differensiering (Brief): lokalt først, tydelig status, lav terskel, fra småjobb til erfaring, gjensidig hjelp, hjelp til å formulere seg.

## 14. Utenfor v1 (skal ikke designes inn)

Chat/meldinger i appen; varsler e-post/push; glemt passord; rapportering/blokkering; kart/avstand; PDF-eksport av profil; BankID/Vipps; under 18; utlån av utstyr; betaling i appen; flere KI-funksjoner; endre/fjerne tilbakemelding (PRD §6.2, §6.3, §4.7).
