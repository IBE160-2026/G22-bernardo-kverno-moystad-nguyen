---
title: EXPERIENCE – Nabolagshelten
status: draft
created: 2026-11-07
updated: 2026-11-07
sources:
  - ../../prds/prd-G22-bernardo-kverno-moystad-nguyen-2026-11-05/prd.md
  - ../../product-brief-nabolagshelten.md
  - ../../skisser-skjermbilder.md
  - ../../../../tilbakemelding-product-brief.md
  - ../../../../docs/sensorveiledning-del1.md
---

# EXPERIENCE – Nabolagshelten

Hvordan appen virker: struktur, tekster, tilstander, samhandling, tilgjengelighet og brukerreiser. Utseendet står i [DESIGN.md](DESIGN.md); tokens refereres som `{colors.primary}` og `{components.card}`. Krav-ID-ene (UJ, FR, NFR, SM) er fra PRD v1.1 og gjentas ikke her – denne fila sier bare hvordan de oppleves. Beslutningene er logget i `.memlog.md`.

**Kildeprioritet:** PRD > denne fila og DESIGN.md > mockups og fargeprøver i `mockups/` > skisser. Ved konflikt mellom spinene og en mockup, skisse eller fargeprøve gjelder spinene.

## Foundation

- **Form:** én responsiv webapp for smarttelefon, nettbrett og PC (NFR-6). Ingen egen mobilapp. Kari bruker nettbrett (UJ-1), Amir mobil (UJ-2).
- **UI-system:** ikke valgt. [NOTE FOR ARCHITECTURE] Frontend-rammeverk og eventuelt komponentbibliotek velges i arkitekturen. Valget må støtte native `<dialog>` eller tilsvarende fokushåndtering, `aria-live`, og skjema som virker med tastatur. Spinene forutsetter ikke et bibliotek; komponentene i DESIGN.md kan bygges med vanlig HTML og CSS.
- **Visuell referanse:** DESIGN.md (ett lyst tema «Salvie og sand», ingen mørk modus).
- **Mockups** (illustrasjoner; spinene gjelder ved konflikt):
  - [key-oversikt.html](mockups/key-oversikt.html) – oppdragsoversikten på mobil og PC, med treff og tom (UJ-2 steg 3)
  - [key-nytt-oppdrag.html](mockups/key-nytt-oppdrag.html) og [key-nytt-oppdrag-steg2.html](mockups/key-nytt-oppdrag-steg2.html) – nytt oppdrag steg 1 med KI-forslag, steg 2 utfylt og med feil (UJ-1 steg 2–4)
  - [key-detaljer.html](mockups/key-detaljer.html) – detaljer for oppdragsgiver med interesserte og dialogen «Velge Amir?» (UJ-1 steg 7–8)
  - [key-mine-oppdrag.html](mockups/key-mine-oppdrag.html) – Mine oppdrag med grupper, merker og antall (UJ-1 steg 6, UJ-2 steg 6)
  - [key-profil.html](mockups/key-profil.html) – Amirs profil (UJ-2 steg 8–10)
  - [key-tilbakemelding.html](mockups/key-tilbakemelding.html) – tilbakemelding med stjerner og kvittering (UJ-1 steg 11)
  - [key-registrering.html](mockups/key-registrering.html) – registrering, tom og med feil (UJ-2 steg 2)
  - [key-slett-konto.html](mockups/key-slett-konto.html) – slett konto, og feil passord (Støtteflyter)
  - Bare fra spinene, uten mockup: innlogging, rediger oppdrag, rediger profil, slettet bruker, feilside og dialogene for å avbryte, fjerne hjelper, trekke seg og markere utført.
- **Språk:** norsk bokmål, `lang="nb"` (NFR-7, NFR-8).
- **Innlogging kreves** for alt unntatt registrering og innlogging (FR-3). Uten innlogging vises topplinjen med bare logo, uten meny.
- **Ingen varsler** i v1 (PRD §6.2). «Mine oppdrag» og antallet i menyen er stedet brukeren ser at noe har skjedd.

## Information Architecture

**Meny (NFR-11):** tre valg i fast rekkefølge – **Oppdrag · Mine oppdrag · Profil**. Under 768 px: `{components.bottom-nav}` fast nederst. Fra 768 px: i `{components.topbar}`. Menyen vises på alle sider etter innlogging, også i skjema og detaljer. Aktivt valg har `aria-current="page"`.

**Aktivt menyvalg på undersider.** En underside markerer menyvalget den hører til, med samme utseende som på menysiden (fet + strek), og `aria-current="true"` i stedet for `"page"` [ASSUMPTION] ARIA-verdien:

| Underside | Aktivt menyvalg |
|---|---|
| Nytt oppdrag, rediger oppdrag | «Mine oppdrag» |
| Oppdragsdetaljer for **eget** oppdrag (brukeren er oppdragsgiver) | «Mine oppdrag» |
| Oppdragsdetaljer for **andres** oppdrag (også når brukeren har meldt interesse eller er hjelper) | «Oppdrag» |
| Andres profil | Ingen |
| Rediger profil, slett konto [ASSUMPTION] | «Profil» |
| Feilside, slettet bruker [ASSUMPTION] | Ingen |

**Antall ved «Mine oppdrag»** (`{components.nav-badge}`): antall oppdrag som står under «Trenger handling» i de to fanene til sammen, altså oppdrag med et av merkene i FR-18. Ikke «nytt siden sist», og ingen lagring av hva brukeren har sett. Regnes ut på nytt ved hver sidevisning. Vises ikke når tallet er 0. Skjermleser: «Mine oppdrag, 2 trenger handling». [ASSUMPTION] Ordlyden for skjermleser. Svar på skisse-spørsmål 3; PRD trenger en presisering (se Åpne punkter).

| Flate | Nås fra | Innhold og handlinger | Krav |
|---|---|---|---|
| Innlogging | Alle sider uten innlogging; «Logg ut» | E-post, Passord, «Logg inn». Lenke til registrering. | FR-2, FR-3 |
| Registrering | Lenke fra innlogging | Navn, E-post, Passord, Telefonnummer, Postnummer (poststed vises når nummeret er gyldig), Fødselsdato. Personverntekst over knappen. Etterpå innlogget og sendt til oversikten. | FR-1, NFR-9 |
| Oppdragsoversikt («Oppdrag») | Startside etter innlogging; meny | «+ Legg ut oppdrag» (primær), overskrift «Ledige oppdrag i 0571 Oslo», synlig antall rett under («4 ledige oppdrag i 0571 Oslo»), kategoriknapper (filter), postnummerfelt med poststed og knappen «Vis» (sekundær), oppdragskort. | FR-10, FR-11, FR-5 |
| Nytt oppdrag | «Legg ut oppdrag» (oversikten, tom fane i Mine oppdrag) | Steg 1: Beskrivelse, «Få forslag», Tittel, Kategori. Steg 2: Postnummer, «Når?» (Dato + Klokkeslett som tekstfelt), «Hva tilbyr du?», forhåndsvisning, «Publiser». To steg under 768 px, én skjerm fra 768 px. Mockup: [steg 1](mockups/key-nytt-oppdrag.html), [steg 2](mockups/key-nytt-oppdrag-steg2.html). | FR-5, FR-23–FR-26, NFR-9 |
| Rediger oppdrag | «Rediger» / «Endre tidspunkt» i detaljer eller Mine oppdrag | Samme skjema uten KI, knapp «Lagre endringer». Bare mens Åpen. | FR-6, FR-8 |
| Oppdragsdetaljer | Kort i oversikten; rad i Mine oppdrag | Alle felt, status, oppdragsgiverblokken («Lagt ut av Kari», erfaring, «Se profil») – ikke for oppdragsgiveren selv. Nederst varierer innholdet etter rolle og status (tabell under). | FR-7, FR-9, FR-12–FR-17, FR-19 |
| Tilbakemelding | Del av detaljer ved Utført | «Hvordan gikk det med Amir?», stjerner, kommentar, «Send». | FR-20 |
| Bekreftelsesdialoger | Handlingene i NFR-8 | Fem dialoger (Interaction Primitives). | NFR-8, FR-7, FR-15, FR-17, FR-19 |
| Mine oppdrag | Meny | Linja «2 oppdrag trenger at du gjør noe.» under overskriften når antallet i menyen er over 0 (forklarer tallet). Fanene «Oppdrag jeg har lagt ut» og «Oppdrag jeg hjelper med», gruppert «Trenger handling» · «Pågår» · «Ferdige». | FR-18, FR-8 |
| Profil (egen) | Meny «Profil» | Som andres profil, med «Rediger profil» og «Logg ut» (sekundærknapper) **øverst**, rett under navn og postnummer, og «Slett konto» (lenke) **nederst**. | FR-21, FR-2 |
| Profil (andres) | «Se profil» i detaljer og interessertliste | Navn, postnummer og poststed, om meg, snitt med stjerner (`star-rating`, visning), fullførte per kategori, alle tilbakemeldinger nyeste først (`list-row`), tekst om at erfaringen ikke er verifisert. | FR-21 |
| Rediger profil | «Rediger profil» | Navn, e-post og fødselsdato som tekst (kan ikke endres); Om meg, Postnummer, Telefonnummer; «Lagre endringer». | FR-22 |
| Slett konto | «Slett konto» på egen profil | Forklaring av hva som skjer, Passord, «Slett kontoen min». Egen side; siden er bekreftelsen. | FR-4 |
| Slettet bruker | Direkte lenke til en slettet profil | Forståelig melding, lenke til oversikten. | FR-4 |
| Feilside | Ingen tilgang, finnes ikke, uventet feil | Forståelig melding og vei videre, aldri teknisk feil. | FR-9, NFR-10 |

Ingen andre sider. Ingen «glemt passord» (PRD §6.2). Ingen skjulte funksjoner: alle handlinger brukeren har lov til, står synlig på flaten der de gjelder; ingen sveip, lange trykk eller menyer med tre prikker.

### Oppdragsdetaljer etter rolle og status

| Hvem | Status | Nederst på siden | Handlinger |
|---|---|---|---|
| Annen innlogget | Åpen, ikke passert | Felt «Melding til Kari (valgfritt)» | «Meld interesse» (primær) |
| Har meldt interesse | Åpen, ikke passert | «Du har meldt interesse. Under Mine oppdrag ser du om Kari har valgt deg.» Ved endring: `{components.action-tag}` «Oppdraget er endret etter at du meldte interesse» | «Trekk interessen» (lenke) |
| Har meldt interesse | Åpen, passert | «Tidspunktet er passert.» [ASSUMPTION] tekst | Ingen (FR-13) |
| Fjernet som valgt hjelper | Åpen | «Du er ikke lenger valgt til dette oppdraget» | Ingen (FR-12) |
| Oppdragsgiver | Åpen, ikke passert | Overskriften «2 har meldt interesse», merket «Velg hjelper» **rett under** den (samme rekkefølge i koden, så den som hopper mellom overskrifter, hører merket), så interessertlista (FR-14) som `list-row` uten lenke. Ingen interesserte: «Ingen har meldt interesse ennå. Oppdraget vises for alle som ser på 0571 Oslo.» | «Rediger», «Avbryt oppdrag», «Velg Amir» per interessert (alle sekundære) |
| Oppdragsgiver | Åpen, passert | Merke «Tidspunktet er passert». Lista vises, men i stedet for «Velg» står «Velg et nytt tidspunkt for å kunne velge hjelper.» [ASSUMPTION] tekst | «Endre tidspunkt» (primær), «Avbryt oppdrag» |
| Oppdragsgiver | Hjelper valgt | `{components.phone-box}` med hjelperen. Etter tidspunktet: merke «Er jobben gjort?» | «Marker som utført» (primær, bare når passert), «Fjern hjelper», «Avbryt oppdrag» |
| Valgt hjelper | Hjelper valgt | Telefonboks med oppdragsgiveren. Før datoen: «Du kan markere oppdraget som utført fra fredag 6. nov.» [ASSUMPTION] tekst | «Marker som utført» (primær, fra kl. 00:00 på datoen), «Trekk meg fra oppdraget» (lenke) |
| Oppdragsgiver / valgt hjelper | Utført | Telefonboks (FR-16). Tilbakemeldingsskjema, eller egen gitt tilbakemelding når den er sendt | «Send» (primær) |
| Oppdragsgiver / valgt hjelper | Avbrutt | Status Avbrutt, ingen telefonnumre | Ingen |

Andre brukere får ikke åpne oppdrag som ikke er Åpne (FR-9); de ser feilsiden. Fra «Mine oppdrag» er rader med «bare tittel og status» ikke lenker.

**Oppdragsgiverblokken** («Lagt ut av Kari» [ASSUMPTION], fullførte oppdrag og snitt, «Se profil») vises for alle andre enn oppdragsgiveren. På sitt eget oppdrag ser oppdragsgiveren den ikke – det er ikke noe nytt å lære om seg selv, og siden blir kortere for Kari. [ASSUMPTION] Besluttet i UX 2026-11-07.

## Voice and Tone

Merkevarens uttrykk står i DESIGN.md § Brand & Style. Her: mikrotekst.

| Gjør | Ikke gjør |
|---|---|
| Ordene i PRD §3 og skissene: oppdrag, oppdragsgiver, hjelper, «Meld interesse» | «Oppdragstaker», «Send forespørsel», engelske ord |
| Korte setninger, du-form, verb først på knapper («Legg ut oppdrag») | Passiv form, fagord, «Vennligst …» |
| Si hva som skjer og hva brukeren kan gjøre nå («Du kan fylle inn selv.») | Teknisk feil, feilkoder, «Error 500» (NFR-10) |
| Navnet på motparten der det hjelper («Velge Amir?») | «Brukeren», «den valgte personen» |
| Ærlig om tillit: erfaringen er registrert av brukere, ikke verifisert (FR-21) | «Verifisert», «godkjent hjelper» |
| Rolig og vennlig, uten utropstegn bortsett fra i takk | Mas om KI («Prøv vår smarte KI!»), utropstegn i feilmeldinger |

**Formater:** tidspunkt som «I morgen kl. 07:00» og ellers «Lørdag 14. nov. kl. 12:00» (år tas med når det ikke er inneværende år), alltid i norsk tid (FR-5). Godtgjørelse «200 kr», «1 000 kr» eller «Uten betaling». Postnummer alltid med poststed: «0571 Oslo» – overalt, også i overskrifter, tomtilstander, «Ingen treff» og hjelpetekster. Snitt «4,3 av 5, 7 vurderinger» overalt (FR-21, FR-9, FR-14); fullførte som «12 fullførte oppdrag»; uten vurderinger «Ingen vurderinger ennå». [ASSUMPTION] «I dag»/«I morgen» og ukedag skrevet fullt.

### Ordrette tekster fra PRD

| Hvor | Tekst | Krav |
|---|---|---|
| Hjelpetekst, beskrivelse | «Ikke skriv adresse eller telefonnummer – det avtaler dere når hjelperen er valgt.» | FR-5, NFR-9 |
| Passert tidspunkt ved redigering | «Velg et nytt tidspunkt fram i tid» | FR-6 |
| Interessert ser endring | «Oppdraget er endret etter at du meldte interesse» – beholdes ordrett, ikke forkortet; merket kan brytes over to linjer | FR-6, FR-18 |
| Interessertliste | «Meldt før endring» | FR-6, FR-14 |
| Etter meldt interesse | «Du har meldt interesse» (skisse 3a utvider: «… Under Mine oppdrag ser du om Kari har valgt deg.») | FR-12 |
| Fjernet hjelper i detaljer | «Du er ikke lenger valgt til dette oppdraget» | FR-12 |
| Velge-dialog | «Velge Amir? Dere får se hverandres telefonnummer.» | FR-15 |
| Utført-dialog | «Marker som utført? Det kan ikke angres.» | FR-19 |
| Stjerne for skjermleser | «4 av 5 stjerner» | FR-20 |
| Kvittering tilbakemelding | «Takk! Tilbakemeldingen er lagt til i Amirs profil.» | FR-20, NFR-8 |
| KI venter | «Lager forslag …» | FR-23 |
| KI-feil | «Vi fikk ikke laget forslag akkurat nå. Du kan fylle inn selv.» | FR-25 |
| Samtidighet | «Oppdraget er endret. Last siden på nytt.» | §4.0 |
| Ingen vurderinger | «Ingen vurderinger ennå» | FR-14, FR-21 |
| Slettet bruker | «Slettet bruker» (uten lenke) | FR-4 |
| Situasjoner og merker | Ordlyden i FR-18-tabellen og merkelista, uendret | FR-18 |

### Tekster fra skissene som beholdes

«Hva trenger du hjelp til?», «Skriv med egne ord.», «Når?», «Hva tilbyr du?», «Slik vises oppdraget for andre.», «Melding til Kari (valgfritt)», «Kommentar (valgfritt)», «Kommentaren vises i Amirs profil.», «Hvordan gikk det med Amir?», «Dårlig» / «Veldig bra», «Avtal detaljene direkte.», «Ja, velg Amir», «Trenger handling», «Pågår», «Ferdige», «Skriv en tittel» (mønster for feltfeil: «Skriv …» / «Velg …»).

### Skisse og PRD sier ulikt – PRD gjelder

| Skisse | PRD (brukes) | Krav |
|---|---|---|
| «Få forslag til tekst» | «Få forslag» | FR-23 |
| «Publiser oppdrag» | «Publiser» | FR-5, UJ-1 |
| «Send tilbakemelding» | «Send» | FR-20 |
| «Lagt ut (3)», «Hjelper med(2)» | «Oppdrag jeg har lagt ut (3)», «Oppdrag jeg hjelper med (2)» | FR-18 |
| «4,9 av 5 i snitt (11 vurderinger)», «12 fullførte · 4,9 av 5» | «12 fullførte oppdrag · 4,9 av 5, 11 vurderinger» | FR-21 |
| «Ingen fullførte ennå» | «Ingen fullførte oppdrag ennå» [ASSUMPTION] | FR-14 |
| «Teksten sendes til en ekstern tjeneste …» | Må si «ekstern KI-tjeneste» (se under) | FR-23 |
| «Trekk meg» (UJ-2) / «Trekk meg fra oppdraget» (skisse 3c) | «Trekk meg fra oppdraget» på knappen; dialogknapp «Ja, trekk meg» | FR-17 |
| <Logg ut> som lenke | «Logg ut» som knapp | FR-21 |
| «Avbryt» ved utgått oppdrag | «Avbryt oppdrag» | FR-7, FR-8 |

### Tekster som mangler i kildene – forslag

Alle er [ASSUMPTION] og må godkjennes av gruppen før de låses i stories.

| Situasjon | Forslag | Krav |
|---|---|---|
| Feil e-post eller passord | «Feil e-post eller passord.» | FR-2 |
| For mange forsøk (5 på 15 min) | «For mange mislykkede forsøk. Prøv igjen om 15 minutter.» | FR-2 |
| Utløpt innlogging | «Du må logge inn igjen.» | FR-2, FR-3 |
| Etter utlogging | «Du er logget ut.» | FR-2 |
| KI ved knappen (ekte tjeneste) | «Teksten i beskrivelsen sendes til en ekstern KI-tjeneste for å lage forslag.» | FR-23 |
| KI ved knappen (mock-modus) | «Forslagene lages i appen. Teksten sendes ikke ut.» | FR-23, FR-26 |
| KI deaktivert (< 10 tegn) | «Skriv minst 10 tegn for å få forslag.» | FR-23 |
| KI-kvote (20 per time) | «Du har bedt om mange forslag den siste timen. Prøv igjen senere, eller fyll inn selv.» | FR-23 |
| Forslag klare (skjermleser) | «Forslagene er klare.» | FR-23, NFR-7 |
| Publisert | «Oppdraget er lagt ut.» | FR-5, NFR-8 |
| Lagret endring | «Endringene er lagret.» | FR-6 |
| Trukket interesse | «Interessen din er trukket.» | FR-13 |
| Valgt hjelper | «Du har valgt Amir. Avtal detaljene direkte.» | FR-15 |
| Fjernet hjelper | «Amir er fjernet. Oppdraget er åpent igjen.» | FR-17 |
| Trukket seg | «Du har trukket deg fra oppdraget.» | FR-17 |
| Avbrutt | «Oppdraget er avbrutt.» | FR-7 |
| Markert utført | «Oppdraget er markert som utført.» | FR-19 |
| Profil lagret | «Profilen er oppdatert.» | FR-22 |
| Konto slettet (på innloggingssiden) | «Kontoen din er slettet.» | FR-4 |
| Feil passord ved sletting | «Passordet er feil. Kontoen er ikke slettet.» | FR-4 |
| Slettet brukers profil | «Denne brukeren har slettet kontoen sin.» | FR-4 |
| Antall treff i oversikten (synlig, under overskriften) | «4 ledige oppdrag i 0571 Oslo» / med kategori: «2 ledige oppdrag i Hage i 0571 Oslo» / «1 ledig oppdrag …». Ved 0 treff vises ikke linja; tomtilstanden tar plassen, og den valgte kategorien får `aria-describedby` til tomtilstandens første setning. | FR-10, FR-11 |
| Forklaring øverst i Mine oppdrag | «2 oppdrag trenger at du gjør noe.» / «1 oppdrag trenger at du gjør noe.» Vises ikke når antallet er 0. | FR-18 |
| Feiloppsummering | Overskrift «Skjemaet har 2 feil» / «Skjemaet har 1 feil», så én lenke per feil med feiltekst | NFR-7, NFR-10 |
| Ingen tilgang | «Du har ikke tilgang til dette oppdraget.» | FR-9 |
| Uventet feil | «Noe gikk galt. Prøv igjen om litt.» | NFR-10 |
| Tom oversikt, kategori valgt | «Ingen ledige oppdrag i 0571 Oslo akkurat nå.» + «Prøv en annen kategori eller et annet postnummer.» + knapp «Vis alle kategorier» | FR-10, FR-11 |
| Tom oversikt, «Alle» valgt | «Ingen ledige oppdrag i 0571 Oslo akkurat nå.» + «Prøv et annet postnummer.» + knapp «Velg et annet postnummer» [ASSUMPTION] | FR-10 |
| Postnummerfilter | Knapp «Vis» ved feltet [ASSUMPTION] | FR-10 |
| Ingen interesserte (detaljer) | «Ingen har meldt interesse ennå. Oppdraget vises for alle som ser på 0571 Oslo.» | FR-14 |
| Ingen interesserte (rad i Mine oppdrag) | «Ingen har meldt interesse ennå» [ASSUMPTION] | FR-18 |
| Oppdragsgiver i detaljer | «Lagt ut av Kari» [ASSUMPTION] | FR-9 |
| Valgt hjelper (rad i Mine oppdrag) | «Hjelper: Amir» [ASSUMPTION] | FR-18 |
| Metalinje på tilbakemelding | «Fra Kari · 14. feb. · Amir var hjelper» (giver, dato, profileierens rolle); slettet giver: «Fra Slettet bruker · …» [ASSUMPTION] | FR-21, FR-4 |
| Snitt med stjerner (profil) | Stjernene + «4,9 av 5, 11 vurderinger» – teksten står alltid ved stjernene | FR-21 |
| Tom fane, lagt ut | «Du har ikke lagt ut noen oppdrag.» + lenke «Legg ut oppdrag» | FR-18 |
| Tom fane, hjelper med | «Du har ikke meldt interesse for noen oppdrag.» + lenke «Se ledige oppdrag» | FR-18 |
| Ikke verifisert (profil) | «Fullførte oppdrag og tilbakemeldinger er registrert av brukere i Nabolagshelten og er ikke verifisert.» | FR-21 |

### Feiltekster ved felt

Hver feil sier hva som er galt og hvordan det rettes, med et eksempel der formatet er poenget. Reglene er fra PRD-en; tekstene er [ASSUMPTION] og godkjennes av gruppen sammen med tabellen over. Påkrevde felt har `required`; skjemaet har `novalidate`, så appens egne tekster vises i stedet for nettleserens bobler. Valgfrie felt har «(valgfritt)» i etiketten; påkrevde felt merkes ikke ekstra, fordi nesten alle felt er påkrevde.

| Felt | Regel | Feiltekst | Krav |
|---|---|---|---|
| Navn | Påkrevd, 1–80 tegn | «Skriv navnet ditt.» / «Navnet kan ha høyst 80 tegn.» | FR-1 |
| E-post | Påkrevd, gyldig format, ikke i bruk | «Skriv e-postadressen din.» / «Skriv e-postadressen som navn@eksempel.no.» / «Det finnes allerede en konto med denne e-posten.» | FR-1, FR-2 |
| Passord (registrering) | 8–64 tegn | «Skriv et passord.» / «Passordet må ha 8–64 tegn.» Når skjemaet kommer tilbake med feil i andre felt, er passordet tømt (§4.0) og feltet har hjelpeteksten «Skriv passordet på nytt.» i stedet for en feil. | FR-1 |
| Passord (innlogging, sletting) | Påkrevd | «Skriv passordet ditt.» | FR-2, FR-4 |
| Telefonnummer | Åtte siffer; mellomrom og +47 godtas | «Skriv telefonnummeret ditt.» / «Skriv et telefonnummer med åtte siffer, for eksempel 912 34 567.» | FR-1, FR-22 |
| Postnummer | Finnes i lista | «Skriv postnummeret.» / «Finner ikke postnummeret. Sjekk at det har fire siffer.» | FR-1, FR-5, FR-10 |
| Fødselsdato | Format, ikke fram i tid, høyst 120 år tilbake, minst 18 år | «Skriv fødselsdatoen din.» / «Skriv fødselsdatoen som dd.mm.åååå, for eksempel 03.05.1954.» / «Sjekk fødselsdatoen.» / «Du må være minst 18 år for å bruke Nabolagshelten.» | FR-1 |
| Beskrivelse | 10–1000 tegn, ikke bare mellomrom | «Skriv hva du trenger hjelp til.» / «Skriv minst 10 tegn.» / «Beskrivelsen kan ha høyst 1000 tegn. Nå har den 1046.» | FR-5 |
| Tittel | 3–80 tegn | «Skriv en tittel.» / «Tittelen må ha minst 3 tegn.» / «Tittelen kan ha høyst 80 tegn.» | FR-5 |
| Kategori | Ett valg | «Velg en kategori.» | FR-5 |
| Dato | dd.mm.åååå, finnes | «Skriv datoen.» / «Skriv datoen som dd.mm.åååå, for eksempel 14.11.2026.» / «Den datoen finnes ikke. Sjekk dag og måned.» | FR-5 |
| Klokkeslett | tt:mm | «Skriv klokkeslettet.» / «Skriv klokkeslettet som tt:mm, for eksempel 07:00.» | FR-5 |
| Når? (dato + klokkeslett sammen) | Ikke passert, høyst 12 måneder fram | «Velg et nytt tidspunkt fram i tid» (ordrett FR-6, brukes også i nytt oppdrag) / «Velg et tidspunkt høyst 12 måneder fram i tid.» Vises under gruppen og knyttes til begge feltene. | FR-5, FR-6 |
| Hva tilbyr du? | Ett valg | «Velg beløp eller uten betaling.» | FR-5 |
| Beløp i kr | Heltall 1–10 000 | «Skriv et beløp fra 1 til 10 000 kr, i hele kroner.» | FR-5 |
| Melding, kommentar, om meg | Høyst 500 tegn | «Teksten kan ha høyst 500 tegn. Nå har den 512.» | FR-12, FR-20, FR-22 |
| Stjerner | Ett valg | «Velg antall stjerner.» | FR-20 |

## Component Patterns

Atferd. Utseendet står i DESIGN.md § Components; navnene er de samme.

| Komponent | Brukes | Atferdsregler |
|---|---|---|
| `{components.button-primary}` | Hovedhandlingen | Én per skjerm. Sender skjema eller åpner dialog. Mens forespørselen pågår, er knappen deaktivert, og skjemaet stopper ny innsending, også med Enter i et felt (§4.0). |
| `{components.button-secondary}` | Andre handlinger | Navigerer (som lenke) eller sender (som knapp). «Velg Amir» per interessert: visuell tekst inneholder navnet, så hver knapp har unikt navn. |
| `{components.button-text}` | Navigering og angre | Lenker («Tilbake», «Se profil») går til en side; «Trekk interessen» og «Ikke bruk» utfører handlingen direkte og er `<button>`. Angre-valget i en dialog er alltid `<button>`, aldri `<a>`. «Tilbake» går til forrige side i appen, ellers til oversikten. |
| Like knappenavn i samme visning | «Bruk» / «Ikke bruk» (KI), «Se profil» (interesserte), snarveiene i rader | Den synlige teksten står først i navnet (2.5.3), og knappen får `aria-describedby` til det den gjelder: forslagets overskrift, personens navn eller oppdragstittelen. |
| Lenken «Hopp til innholdet» | Alle sider | Første fokuserbare element. Usynlig til den får fokus, da synlig øverst til venstre. Går til `main`, som har `tabindex="-1"`. |
| `{components.button-disabled}` | Alle knapper når de ikke kan brukes | Bruk `aria-disabled="true"` slik at knappen beholder fokus og kan leses opp; klikk gjør ingenting. Brukes bare kortvarig (under forespørsel) eller når en synlig tekst forklarer hvorfor (KI under 10 tegn). Ellers vises en forklarende tekst i stedet for knappen. |
| `{components.card}` | Oppdragskort i oversikten | Hele kortet er én lenke til detaljer: tittelen er lenken, og trykkflaten dekker kortet. Ingen andre knapper på kortet. Viser tittel, kategori, tidspunkt, godtgjørelse (FR-10) og postnummer med poststed. |
| `{components.list-row}` | Mine oppdrag, interessertlista i detaljer, tilbakemeldinger på profilen | **Lenkerad** (rader i Mine oppdrag som kan åpnes): tittelen er lenken, trykkflaten dekker hele raden over eventuelle knapper, pil › til høyre; lenkens navn er bare tittelen. **Ikke-lenkerad** (rader med «bare tittel og status», interesserte, tilbakemeldinger): ingen pil; raden kan ha egne lenker og knapper. Knapper i en rad står alltid under lenkedelen, aldri inne i lenken (ingen nestede interaktive elementer). Rekkefølge: tittel → status-badge → situation-label / action-tag → faktalinjer → knapper. [ASSUMPTION] Lenken får `aria-describedby` til merkelinja, så den som tabber hører «Måke snø i innkjørselen, Status: Hjelper valgt. Må gjøres: Er jobben gjort?». |
| `{components.status-badge}` | Detaljer, Mine oppdrag | Viser oppdragets status med ord. Ikke trykkbar. Skjult tekst foran for skjermleser: «Status: Åpen.» |
| `{components.action-tag}` | Rader i Mine oppdrag, detaljer | Viser FR-18-merkene. Ikke trykkbar selv; raden den står i er lenken. Et oppdrag med merke står under «Trenger handling» og teller i `{components.nav-badge}`. Skjult tekst foran: «Må gjøres: Gi tilbakemelding.» Teksten forkortes aldri og brytes over så mange linjer som trengs (normalt høyst to på 360 px ved 100 %); aldri `line-clamp`, ellipse eller skjult overflyt. I detaljer for oppdragsgiver står «Velg hjelper» rett under overskriften «N har meldt interesse». |
| `{components.situation-label}` | «Oppdrag jeg hjelper med» | Viser «Vises som» fra FR-18. Når situasjonen er lik statusen («Utført», «Avbrutt»), vises bare statusmerket. Skjult tekst foran: «Din situasjon: Venter på svar.» |
| `{components.category-chip}` | Kort, detaljer, forhåndsvisning | Bare visning. Beige flate med tynn kant (DESIGN.md). |
| `{components.category-button}` (filter) | Oversikten | «Alle» + seks kategorier. **Lenker med egen adresse** (`?kategori=hage`), samme mønster som fanene, ikke radioknapper. Valgt lenke har `aria-current="true"`. Ett valg om gangen; virker med en gang, uten egen knapp. Etter valget står fokus på den valgte kategorien, og lista og antallslinja under overskriften («2 ledige oppdrag i Hage i 0571 Oslo») er oppdatert. Den valgte lenken har `aria-describedby` til antallslinja, så skjermleseren leser antallet når fokus lander der. Oppdateres lista uten ny sidelasting, er antallslinja i tillegg `aria-live="polite"`. Trykk på kategorien som allerede er valgt, endrer ingenting. «Vis alle kategorier» (tom tilstand) velger «Alle» og setter fokus der. Tastatur: Tab mellom kategoriene, Enter velger. [NOTE FOR ARCHITECTURE] Med server-rendring settes fokus på valgt lenke ved sidelasting (f.eks. med `autofocus` eller et lite skript). |
| `{components.category-button}` (skjema) | Nytt og rediger oppdrag | Radiogruppe (`fieldset`, `legend` «Kategori») med samme utseende. Piltaster flytter valget, Tab går videre; valg sender ikke skjemaet. Valgt knapp beholder kategoriikonet og får i tillegg hake og fet tekst (både for `:checked` og for `aria-current` i filteret). |
| Postnummerfilter (`{components.input}` + `{components.button-secondary}`) | Oversikten | Feltet «Postnummer» med poststed ved siden av og knappen «Vis» (sekundær) rett etter. Nytt postnummer brukes først ved «Vis» eller Enter i feltet – ikke for hvert tastetrykk. Ugyldig postnummer gir feltfeilen «Finner ikke postnummeret. Sjekk at det har fire siffer.», og lista står uendret. Etter «Vis» står fokus på feltet, og antallslinja er oppdatert og knyttet til feltet med `aria-describedby`, som for kategorifilteret. [ASSUMPTION] Enter og feilvisning. |
| `{components.input}` | Alle skjema | Synlig etikett, hjelpetekst og feil knyttet med `aria-describedby`; ugyldig felt får `aria-invalid="true"`. Tekstområder viser teller «37 av 500 tegn» (1000 for beskrivelse); telleren leses ikke opp for hvert tegn, bare når grensen nås. Postnummer viser poststed ved siden av når det er gyldig. Telefon godtar mellomrom og +47 (§4.0). Passord har knappen «Vis passord» med `aria-pressed`; teksten står fast. [ASSUMPTION] Teller og «Vis passord». Felttype og formål (1.3.5) i tabellen under. |
| «Når?» (`{components.input}` × 2) | Steg 2 i nytt oppdrag, rediger oppdrag | `fieldset` med `legend` «Når?». To tekstfelt, **ikke** nettleserens dato- og klokkevelger: «Dato» med hjelpeteksten «dd.mm.åååå, for eksempel 14.11.2026» og «Klokkeslett» med «tt:mm, for eksempel 07:00». Alltid norsk format, uansett nettleserens språk. Appen godtar også skråstrek, bindestrek og mellomrom mellom tallene, tosifret år og klokkeslett uten kolon («7», «0700», «7.00») [ASSUMPTION]. `autocomplete="off"`. Ikke `inputmode="numeric"`, fordi talltastaturet på enkelte telefoner mangler punktum [ASSUMPTION]. Feil for hvert felt ved feltet; feil for tidspunktet samlet («Velg et nytt tidspunkt fram i tid») under gruppen. «Endre tidspunkt» setter fokus på «Dato». |
| «Hva tilbyr du?» (radio + `{components.input}`) | Steg 2 i nytt oppdrag, rediger oppdrag | `fieldset` med `legend` «Hva tilbyr du?» og to radioknapper: «Beløp» og «Uten betaling». Ingen er valgt på forhånd [ASSUMPTION]. Feltet «Beløp i kr» (`inputmode="numeric"`, `autocomplete="off"`) står rett etter radioknappen «Beløp» i koden, innrykket under den, og vises bare når «Beløp» er valgt. Å vise feltet flytter ikke fokus. Skrevet beløp beholdes om brukeren bytter fram og tilbake. |
| Forhåndsvisning | Steg 2, rett over «Publiser» | Region (`section`) med navnet «Slik vises oppdraget for andre», som også står som synlig tekst over. Viser kortet slik det blir i oversikten, men uten lenke, og tittelen er ikke en overskrift (så den ikke forveksles med sidens). Oppdateres når feltene endres, uten å leses opp. Tomme felt vises som «–». [ASSUMPTION] Tomme felt. |
| `{components.field-error}` | Under ugyldig felt | Vises etter innsending (og når brukeren forlater et felt som allerede har vist feil). Forsvinner når verdien er gyldig. Alt utfylt beholdes, unntatt passord (§4.0). Tekstene står i Voice and Tone § Feiltekster ved felt. |
| Feiloppsummering (`{components.message-error}`) | Øverst i skjemaet, rett etter `h1`, når innsending gir feil | Overskrift «Skjemaet har 2 feil» og én lenke per feil («Skriv en tittel.»), som flytter fokus til feltet. Oppsummeringen har `tabindex="-1"` og får fokus når den vises, både etter sidelasting og når appen sjekker uten ny side. **Ikke** `role="alert"` (fokus gir opplesningen; to kunngjøringer ville avbryte hverandre). `<title>` får «Feil: » foran. I to steg: oppsummeringen lister feil fra begge steg, og appen viser steget med første feil; en lenke til et felt i det andre steget bytter steg og setter fokus på feltet. |
| `{components.message-success}` | Kvittering etter handling | Rett etter `h1` på siden brukeren havner på. Etter sidelasting får kvitteringen fokus (`tabindex="-1"`), så den leses først. Ved endring uten sidelasting: `role="status"`. Blir stående til neste sidebytte – forsvinner ikke av seg selv. |
| `{components.message-error}` | Konflikt, KI-feil, uventet feil uten sidelasting | `role="alert"` bare når meldingen kommer uten ny side. Kommer den med en ny side, får den fokus som kvitteringen. Blir stående til brukeren gjør noe nytt. Ved konflikt har meldingen knappen «Last siden på nytt». |
| `{components.topbar}` | Alle sider | Logo lenker til oversikten. Fra 768 px har den menyen. |
| `{components.bottom-nav}` | Under 768 px | Fast nederst ved vanlig bruk. Når skjermen er lav (liggende telefon, stor zoom, skjermtastatur) eller teksten er stor, ligger menyen nederst i sideflyten i stedet for fast (regel i DESIGN.md § Layout). Et felt med fokus havner aldri bak menyen. Ingen krav om at menyen skal synes over skjermtastaturet. |
| `{components.nav-badge}` | «Mine oppdrag» i menyen | Antall «Trenger handling». Er en del av lenkens navn for skjermleser. |
| `{components.tabs}` | Mine oppdrag | To lenker med egen adresse (f.eks. `?fane=hjelper`), aktiv har `aria-current="page"`; menyvalget «Mine oppdrag» har da `aria-current="true"`, så siden bare har én `"page"`. Tilbake-knappen i nettleseren virker. Ikke ARIA-`tablist`. [ASSUMPTION] Fanen som åpnes først: den med «Trenger handling»-oppdrag (først «lagt ut» hvis begge har); ellers «Oppdrag jeg har lagt ut». |
| `{components.star-rating}` (input) | Tilbakemelding | Fem radioknapper med utseende som stjerner, i en `fieldset` der `legend` er det synlige spørsmålet «Hvordan gikk det med Amir?». Navnene er «1 av 5 stjerner, dårlig», «2 av 5 stjerner», «3 av 5 stjerner», «4 av 5 stjerner», «5 av 5 stjerner, veldig bra» – ytterpunktene har med ordet som står synlig. Trykk eller piltast velger; ingenting lagres før «Send» (FR-20). Stjerne 1 til valgt verdi fylles. Valgt verdi står med ord under stjernene. |
| `{components.star-rating}` (visning) | Snittet på profilen | Bare visning, ikke trykkbar og ikke i Tab-rekkefølgen. Stjernene er dekorative (`aria-hidden="true"`); teksten «4,9 av 5, 11 vurderinger» står alltid ved siden av eller under og bærer meningen. Ingen vurderinger: ingen stjerner, bare «Ingen vurderinger ennå». Interessertlista og oppdragsgiverblokken viser snittet bare som tekst, så radene holdes korte [ASSUMPTION]. |
| `{components.dialog}` | Bekreftelser (NFR-8) | Native `<dialog>` åpnet med `showModal()`: bakgrunnen blir utilgjengelig, Tab holdes inne og Esc angrer. Fokus flyttes inn, og tilbake til knappen som åpnet den (NFR-7). Én dialog om gangen. Blir dialogen høyere enn skjermen (stor zoom, liggende skjerm), ruller innholdet inne i dialogen, så begge knappene alltid kan nås. Hver dialog nevner oppdragstittelen. |
| `{components.ki-suggestion-box}` | Under feltet forslaget gjelder | Ett per felt (beskrivelse, tittel, kategori). «Bruk» fyller feltet og fjerner boksen; «Ikke bruk» fjerner boksen. Feltet kan redigeres etterpå (FR-24). Nytt «Få forslag» erstatter alle bokser. Teksten vises som ren tekst (FR-25, NFR-12). |
| `{components.phone-box}` | Detaljer ved Hjelper valgt og Utført | Viser motpartens navn og nummer. Nummeret er en `tel:`-lenke med minst 48 px høy trykkflate. Vises bare for de to partene (FR-16), aldri for slettet bruker. |
| `{components.empty-state}` | Tomme lister og faner | Forklaring + én vei videre (NFR-7). Tekster i Voice and Tone. Tom oversikt med «Alle» valgt: knappen «Velg et annet postnummer» flytter fokus til postnummerfeltet og markerer innholdet, så brukeren kan skrive et nytt nummer med en gang (FR-10) [ASSUMPTION] markeringen. Tom oversikt med kategori valgt: «Vis alle kategorier» velger «Alle». |

**Felttyper og formål (WCAG 1.3.5).** Nettleseren kan da fylle inn kjente opplysninger, og hjelpemidler vet hva feltet er til:

| Felt | Type og attributter |
|---|---|
| Navn | `type="text" autocomplete="name"` |
| E-post | `type="email" autocomplete="email"` |
| Telefonnummer | `type="tel" autocomplete="tel"` |
| Postnummer (registrering, profil, nytt oppdrag, filter) | `type="text" inputmode="numeric" autocomplete="postal-code"` |
| Fødselsdato | `type="text" autocomplete="bday"`, hjelpetekst «dd.mm.åååå, for eksempel 03.05.1954» |
| Passord ved registrering | `type="password" autocomplete="new-password"` |
| Passord ved innlogging og sletting | `type="password" autocomplete="current-password"` |
| Dato og klokkeslett i oppdrag | `type="text" autocomplete="off"` (se «Når?») |
| Beløp i kr | `type="text" inputmode="numeric" autocomplete="off"` |
| Tittel, beskrivelse, melding, kommentar, om meg | `autocomplete="off"` |

## State Patterns

### Statusmodell (PRD §4.0)

| Status | Merke | Hvor brukeren ser det |
|---|---|---|
| Åpen | `{components.status-badge}` open – «Åpen» | Detaljer, Mine oppdrag. Ikke på kort i oversikten (alle der er åpne). |
| Hjelper valgt | chosen – «Hjelper valgt» | Detaljer, Mine oppdrag, med navn på hjelperen. |
| Utført | done – «Utført» | Detaljer, Mine oppdrag. |
| Avbrutt | cancelled – «Avbrutt» | Detaljer, Mine oppdrag. |

«Utgått oppdrag» er ikke en status (FR-8): status forblir «Åpen», med merket «Tidspunktet er passert».

### Mine oppdrag (FR-18)

**«Oppdrag jeg hjelper med»** – én rad per oppdrag, ordrett fra FR-18:

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

**«Oppdrag jeg har lagt ut»** – hver rad (`{components.list-row}`): tittel, `{components.status-badge}` og eventuelt merke, tidspunkt, og «3 har meldt interesse», «Ingen har meldt interesse ennå» eller «Hjelper: Amir» [ASSUMPTION] de to siste.

**Merker** (`{components.action-tag}`, ordrett FR-18): «Tidspunktet er passert» (egne utgåtte) · «Er jobben gjort?» (begge parter, Hjelper valgt + passert) · «Gi tilbakemelding» (Utført, ikke gitt, motpart ikke slettet) · «Hjelperen trakk seg» (hos oppdragsgiver) · «Oppdraget er endret etter at du meldte interesse» (hos den interesserte).

**Nytt merke «Velg hjelper»** (UX-beslutning 2026-11-07, krever presisering av FR-18): vises hos oppdragsgiver på eget oppdrag med status Åpen, tidspunktet ikke passert, og minst én interessert. Forsvinner når en hjelper er valgt eller oppdraget avbrytes. Er tidspunktet passert, vises «Tidspunktet er passert» i stedet.

**Grupper** – overskriftene følger sorteringen i FR-18, med to presiseringer (begge krever oppdatering av FR-18, se Åpne punkter):

| Gruppe | «Oppdrag jeg har lagt ut» | «Oppdrag jeg hjelper med» | Rekkefølge |
|---|---|---|---|
| «Trenger handling» | Oppdrag med et merke, inkludert «Velg hjelper» | Oppdrag med et merke | [ASSUMPTION] Etter tidspunkt, tidligste først |
| «Pågår» | Status Åpen eller Hjelper valgt, uten merke | «Venter på svar», «Du er valgt» (uten merke) | Tidspunkt, tidligste først |
| «Ferdige» | Status Utført eller Avbrutt, uten merke | «Utført», «Avbrutt», «Ikke valgt», «Du er ikke lenger valgt», «Du trakk deg» – gruppert etter brukerens egen situasjon, ikke oppdragets status | Nyeste tidspunkt først |

En gruppe uten oppdrag vises ikke. Avbrutte oppdrag vises i «Ferdige», ikke skjult bak en lenke. Raden «Tidspunktet er passert» hos oppdragsgiver har snarveiene «Endre tidspunkt» og «Avbryt oppdrag» (UJ-1) som sekundærknapper under lenkedelen av raden, under en skillelinje – utenfor lenken, så ingen interaktive elementer ligger inni hverandre. Raden er fortsatt en lenke til detaljene. [ASSUMPTION] Plasseringen.

### Tomme, laste-, feil- og konflikttilstander

| Tilstand | Flate | Behandling | Krav |
|---|---|---|---|
| Ingen treff | Oversikten | `{components.empty-state}` under filtrene: «Ingen ledige oppdrag i 0571 Oslo akkurat nå.» + forslag. Kategori valgt: «Vis alle kategorier». «Alle» valgt: «Velg et annet postnummer», som flytter fokus til postnummerfeltet. Ingen «Se alle postnumre». | FR-10, FR-11 |
| Ingen interesserte | Detaljer (oppdragsgiver) | Tomtilstand med forklaring: «Ingen har meldt interesse ennå. Oppdraget vises for alle som ser på 0571 Oslo.» | FR-14 |
| Tom fane | Mine oppdrag | Tomtilstand + lenke («Legg ut oppdrag» / oversikten). | FR-18 |
| Ingen vurderinger | Profil, detaljer, interessertliste | «Ingen vurderinger ennå». | FR-21 |
| Tom «om meg» | Profil | Feltet vises ikke. | FR-22 |
| Ingen fullførte | Profil | «Ingen fullførte oppdrag ennå» [ASSUMPTION]. | FR-21 |
| Sidelasting | Alle | Vanlig sidelasting; ingen skjelett-plassholdere. [NOTE FOR ARCHITECTURE] Hvis klienten henter data selv, vises «Laster …» med `role="status"`. | NFR-10 |
| Sender | Alle skjema og handlinger | Knappen deaktiveres (`aria-disabled`) til svaret kommer. | §4.0 |
| KI henter | Nytt oppdrag | Knappen viser «Lager forslag …», leses opp. Resten av skjemaet kan fortsatt brukes. | FR-23 |
| KI-feil / tidsavbrudd 10 s / kvote | Nytt oppdrag | `{components.message-error}` der forslagene ellers ville kommet: rett under «Få forslag» og KI-teksten. Den erstatter forslagsområdet – ingen forslagsbokser vises, heller ikke gamle. Skjemaet beholder alt. Nytt «Få forslag» fjerner meldingen. | FR-23, FR-25 |
| Valideringsfeil | Alle skjema | Feil ved hvert felt, og feiloppsummeringen «Skjemaet har 2 feil» rett etter `h1` får fokus (se Component Patterns). Lenkene i oppsummeringen fører til feltene. `<title>` får «Feil: » foran. På mobil i to steg: appen viser steget med første feil. | §4.0, NFR-7, NFR-10 |
| Samtidighetskonflikt | Detaljer, dialoger | «Oppdraget er endret. Last siden på nytt.» + knappen «Last siden på nytt». Dialogen lukkes. | §4.0, FR-15 |
| Ingen tilgang / finnes ikke | Detaljer, profil | Feilside med tekst og lenke til oversikten. | FR-9, FR-4 |
| Innlogging utløpt | Alle | Til innlogging med «Du må logge inn igjen.»; etter innlogging tilbake til siden brukeren ville til [ASSUMPTION]. Utløper innloggingen mens et skjema er utfylt (f.eks. ved «Publiser»), beholdes innholdet og vises igjen etter ny innlogging, eller brukeren får beskjed før det går tapt. [NOTE FOR ARCHITECTURE] | FR-2, FR-3 |
| Uventet feil / nettverk | Alle | «Noe gikk galt. Prøv igjen om litt.» Utfylt innhold beholdes. | NFR-10 |
| Fokus | Alle | Synlig fokusring (DESIGN.md). Fokus flyttes bare ved dialog, kvittering eller feiloppsummering etter innsending, steg-bytte, filtervalg og «Velg et annet postnummer». | NFR-7 |

## Interaction Primitives

**Bekreftelser (NFR-8).** Disse handlingene åpner `{components.dialog}`; ingen andre:

Eksemplene bruker oppdraget «Måke snø i innkjørselen». Der PRD-en gir spørsmålet ordrett, står tittelen i en egen linje under: «Gjelder «Måke snø i innkjørselen».»

| Handling | Spørsmål | Bekreft (primær) | Angre (`button-text`) | Krav |
|---|---|---|---|---|
| Velge hjelper | «Velge Amir? Dere får se hverandres telefonnummer.» + «Gjelder «…».» | «Ja, velg Amir» | «Ikke ennå» | FR-15 |
| Avbryte oppdrag | «Avbryte «Måke snø i innkjørselen»? Det kan ikke angres.» [ASSUMPTION] | «Ja, avbryt oppdraget» [ASSUMPTION] | «Behold oppdraget» | FR-7 |
| Fjerne hjelper | «Fjerne Amir som hjelper på «Måke snø i innkjørselen»? Oppdraget blir åpent igjen, og telefonnumrene skjules.» [ASSUMPTION] | «Ja, fjern Amir» [ASSUMPTION] | «Nei, behold Amir» | FR-17 |
| Trekke seg | «Trekke deg fra «Måke snø i innkjørselen»? Oppdraget blir åpent igjen, og telefonnumrene skjules.» [ASSUMPTION] | «Ja, trekk meg» [ASSUMPTION] | «Nei, jeg blir» | FR-17 |
| Markere som utført | «Marker som utført? Det kan ikke angres.» + «Gjelder «…».» | «Ja, marker som utført» [ASSUMPTION] | «Ikke ennå» | FR-19 |
| Slette konto | Egen side, ikke dialog: forklaringen fra FR-4 + passordfelt | «Slett kontoen min» [ASSUMPTION] | «Tilbake til profilen» [ASSUMPTION] | FR-4 |
| Tilbakemelding | Ingen dialog: «Send» etter stjernevalg er bekreftelsen | «Send» | – | FR-20, NFR-8 |

Angre-valget heter aldri «Avbryt», fordi «Avbryt oppdrag» er en handling som ikke kan angres. Teksten sier hva som skjer når brukeren angrer (besluttet 2026-11-07).

**Fokus.** Dialog: fokus til dialogens spørsmål (overskrift med `tabindex="-1"`), Tab sirkulerer i dialogen, Esc = angre, fokus tilbake til knappen som åpnet den. Forsvinner knappen (fordi statusen endret seg), går fokus til kvitteringen. Etter innsending som laster ny side: fokus til kvitteringen rett etter `h1` (eller til feiloppsummeringen ved feil), så den leses først. `aria-live` brukes bare for endringer uten ny side (KI-forslag, filter uten sidelasting).

**To steg i nytt oppdrag (under 768 px).** Steg 1 har `h1` «Nytt oppdrag 1 av 2» og knappen «Neste» (primær). «Neste» sjekker feltene i steg 1 og viser feiloppsummeringen der hvis noe mangler [ASSUMPTION]; ellers vises steg 2, og fokus går til `h1` «Nytt oppdrag 2 av 2». Steg 2 har «Publiser» (primær) og «Tilbake til steg 1» (`button-text`), som beholder alt utfylt og setter fokus på `h1` «Nytt oppdrag 1 av 2». `<title>` byttes per steg (se Accessibility Floor). Fra 768 px er begge delene på én side med `h1` «Nytt oppdrag» og hver sin `h2` («Hva trenger du hjelp til?», «Når og hvor?» [ASSUMPTION]).

**Sending.** Alle knapper som sender noe er deaktivert mens forespørselen pågår, så dobbeltklikk ikke gir to handlinger (§4.0). Serveren avviser likevel den andre.

**KI-forslag (FR-23–FR-26).**
1. «Få forslag» er en sekundær knapp under beskrivelsesfeltet (og telleren). Teksten om ekstern KI-tjeneste (eller mock-modus) står **under knappen**, synlig før brukeren trykker. Rekkefølgen er alltid: beskrivelsesfelt → «Få forslag» → KI-teksten → forslag til beskrivelse, feilmelding eller ingenting.
2. Under 10 tegn: knappen er deaktivert, med teksten «Skriv minst 10 tegn for å få forslag.»
3. Trykk: knappen viser «Lager forslag …», `aria-live="polite"` leser det opp.
4. Svar: én `{components.ki-suggestion-box}` under hvert av feltene Beskrivelse (under KI-teksten), Tittel og Kategori. Et eventuelt tips står inne i beskrivelsesboksen, under forslagsteksten og over «Bruk»/«Ikke bruk»; «Bruk» fyller bare inn beskrivelsen, ikke tipset. «Forslagene er klare.» leses opp; fokus blir på knappen. Ved feil: se State Patterns – feilmeldingen står der beskrivelsesforslaget ellers ville stått, og ingen bokser vises.
5. «Bruk» fyller feltet, fjerner boksen og flytter fokus til feltet. «Ikke bruk» fjerner boksen og flytter fokus til feltet.
6. Ingenting lagres før «Publiser». KI er aldri forhåndsvalgt eller automatisk; manuell utfylling er like rask (SM-C1).

**Tilbakemelding (FR-20).** Stjernene velges med trykk eller piltaster; «Send» lagrer. Uten stjerner gir «Send» feltfeilen «Velg antall stjerner.» Etter «Send» erstattes skjemaet av kvitteringen og den gitte tilbakemeldingen.

**Ikke tillatt:** sveip, lange trykk, dra-og-slipp, hover som eneste måte å se noe på, uendelig rulling, karuseller, meldinger som forsvinner av seg selv, automatisk innsending ved valg i skjema (kategorifilteret er lenker, ikke et skjema; postnummerfilteret brukes med «Vis»), interaktive elementer inne i en lenke, myk rulling ved fokusflytting når brukeren har valgt redusert bevegelse (`prefers-reduced-motion`), låst skjermretning.

## Accessibility Floor

Krav: NFR-7, WCAG 2.1 nivå AA. Visuell kontrast står i DESIGN.md § Colors. Hvert punkt i NFR-7 og hvordan det løses:

| NFR-7 | Slik | Testes ved |
|---|---|---|
| Kontrast minst 4,5:1 for tekst | Alle tekstpar i DESIGN.md er 4,61:1 eller bedre; kanter og fokus ≥ 3:1. | T5 |
| Alt kan brukes med tastatur, med synlig fokus, også dato og klokkeslett | Logisk Tab-rekkefølge lik leserekkefølgen. Lenken «Hopp til innholdet» er første fokuserbare element på hver side (Component Patterns). Dato og klokkeslett er to tekstfelt med fast format i gruppen «Når?» (besluttet 2026-11-07); ingen kalender å navigere. Fødselsdato er også tekstfelt med format. | T2 |
| Synlige etiketter; feil ved feltet og knyttet til det | Etikett over hvert felt, `aria-describedby` til hjelpetekst og feil, `aria-invalid`, felttype og `autocomplete` etter tabellen i Component Patterns. «Når?», «Hva tilbyr du?», kategori og stjerner har `fieldset`/`legend`. Feiloppsummering med lenker til feltene. | T1, T3 |
| Knapper har tekst; meningsbærende bilder og ikoner har alt-tekst | Alle ikoner står sammen med tekst og er `aria-hidden`, også pila › i lenkerader og stjernene i snittvisningen (teksten «4,9 av 5, 11 vurderinger» bærer verdien). Logoen er en lenke med navnet «Nabolagshelten, til oversikten». Like knappenavn får `aria-describedby`. | T1 |
| Brødtekst ≥ 18 px, trykkflater ≥ 48 px | Tokens i DESIGN.md. Frittstående lenker, stjerner og telefonlenken har minst 48 px høy trykkflate; lenker inne i løpende tekst (f.eks. navnet i «Fra Kari») er unntatt. | T2 (måles i DevTools) |
| Forstørre til 200 % uten tap | `rem`-størrelser; layouten skifter til mobilvisning når den blir smal. Flyter om ved 320 px (400 % zoom på 1280 px) uten vannrett rulling. Bunnmenyen og merkene bryter tekst i stedet for å klippe. | T4 |
| Status med ord, ikke bare farge | Status, situasjon, merker og valgt kategori har alltid tekst og ikon, og skjult forklaring for skjermleser («Status: Åpen.»). | T3, T5 (gråtoner / tvungne farger) |
| Statusmeldinger leses opp | Etter sidelasting får kvitteringen eller feiloppsummeringen fokus. Uten sidelasting: kvitteringer `role="status"`, feil `role="alert"`, «Lager forslag …» og antallslinja i filteret `aria-live="polite"`. | T3 |
| Bekreftelsesdialoger flytter fokus inn og tilbake | Se Interaction Primitives. | T2 («fokus tilbake» er eget kontrollpunkt) |
| `lang="nb"` | På `<html>`. Hver side har egen `<title>` (tabell under). | T1 |
| Tomtilstander med forklaring | Se State Patterns. | T1, T3 |

Også: én `h1` per side, overskrifter i riktig rekkefølge; landemerker `header`, `nav` («Hovedmeny»), `main`; ingen bevegelse eller animasjon som bærer mening; tidsbegrensning bare på innlogging (7 dager, FR-2). Appen låser ikke skjermretningen, ruller ikke mykt når brukeren har valgt redusert bevegelse, og sjekkes i Windows høykontrast (`forced-colors: active`): fokus, merker og valgt tilstand må synes med kant eller tekst, ikke bare skygge eller flate.

**Sidetitler** (`<title>`, 2.4.2). Mønster: «Side – Nabolagshelten». Ved valideringsfeil kommer «Feil: » foran.

| Side / tilstand | `<title>` |
|---|---|
| Oversikt | «Ledige oppdrag i 0571 Oslo – Nabolagshelten» (med kategori: «Hage – Ledige oppdrag i 0571 Oslo – Nabolagshelten») |
| Nytt oppdrag, mobil | «Nytt oppdrag, steg 1 av 2 – Nabolagshelten» / «Nytt oppdrag, steg 2 av 2 – Nabolagshelten» |
| Nytt oppdrag, fra 768 px | «Nytt oppdrag – Nabolagshelten» |
| Rediger oppdrag | «Rediger «Måke snø i innkjørselen» – Nabolagshelten» |
| Oppdragsdetaljer | «Måke snø i innkjørselen – Nabolagshelten» |
| Mine oppdrag | «Mine oppdrag: Oppdrag jeg har lagt ut – Nabolagshelten» / «Mine oppdrag: Oppdrag jeg hjelper med – Nabolagshelten» |
| Profil | «Min profil – Nabolagshelten» / «Amir – profil – Nabolagshelten» |
| Rediger profil, slett konto | «Rediger profil – Nabolagshelten» / «Slett konto – Nabolagshelten» |
| Registrering, innlogging | «Registrering – Nabolagshelten» / «Logg inn – Nabolagshelten» |
| Feil i skjema | «Feil: Registrering – Nabolagshelten» osv. |
| Feilside, slettet bruker | «Fant ikke siden – Nabolagshelten» / «Slettet bruker – Nabolagshelten» [ASSUMPTION] |

**Testes ved** (NFR-7, SM-5), dokumentert som manuelle tester (sensorveiledningen, kriterium 3). Kolonnen «Testes ved» over viser hvilket NFR-7-punkt hver test dekker.

1. **T1 Automatisk, axe:** ingen «serious» eller «critical» på oppdragsoversikt (med treff og tom), nytt oppdrag steg 1 og steg 2 (mobil) og som én skjerm (nettbrett), KI-forslag vist og KI-feil, oppdragsdetaljer for oppdragsgiver, for interessert og for valgt hjelper, tilbakemelding med stjerner, Mine oppdrag (begge faner og tom fane), profil, registrering, innlogging, rediger profil, et skjema med valideringsfeil, feilside, slettet bruker og hver bekreftelsesdialog (fem dialoger + slett konto-siden). axe finner ikke manglende `autocomplete`, så felttypene sjekkes mot tabellen i T2.
2. **T2 Tastatur:** UJ-1 og UJ-2 uten mus, og støtteflytene (registrering, innlogging, rediger profil, slett konto). Kontrollpunkter: «Hopp til innholdet», synlig fokus på alt, dato og klokkeslett, kategorifilter og kategoriknapper, stjerner, alle dialoger, fokus tilbake etter dialog, felttyper og `autocomplete`. Tekststørrelse og trykkflater måles i DevTools.
3. **T3 Skjermleser** (NVDA på Windows eller VoiceOver på iPad/Mac): UJ-1, UJ-2 steg 3–6 (antallet etter filtervalg), ett skjema med feil (feiloppsummeringen leses, lenkene fører til feltene) og en kvittering etter sidelasting.
4. **T4 Bredder og zoom:** UJ-1 og UJ-2 ved 360, 768 og 1280 px med skjermbilder (NFR-6); 320 px (400 % zoom på 1280 px) uten vannrett rulling; 200 % zoom; tekstavstand etter WCAG 1.4.12 (bokmerke); 200 % tekststørrelse i operativsystemet; liggende telefon med bunnmenyen og et felt med fokus.
5. **T5 Kontrast og farge:** kontrasttabellen i DESIGN.md er regnet ut fra tokens; stikkprøver i appen med fargevelger, også kanter, fokusring og tilstander (1.4.11), som axe ikke sjekker. Én gjennomgang i gråtoner eller med tvungne farger.
6. **T6 Brukertest SM-4:** to personer utenfor gruppen, minst én over 60 eller lite app-vant, legger ut et oppdrag på under to minutter på mobil eller nettbrett. Notér ord de ikke forstår.

## Responsive & Platform

| Bredde | Meny | Oversikt | Nytt oppdrag | Andre flater |
|---|---|---|---|---|
| 360–767 px | Bunnmeny | 1 kolonne; kategoriknapper over flere linjer | **To steg**: 1 «Hva trenger du hjelp til?» (beskrivelse, Få forslag, tittel, kategori, «Neste»); 2 postnummer, når, hva tilbyr du, forhåndsvisning, «Publiser» | 1 kolonne; dialogknapper under hverandre |
| 768–1279 px | Topplinje | 2 kolonner | **Én skjerm** med de samme to delene under hverandre, hver med egen overskrift [ASSUMPTION] | 1 kolonne, maks 760 px |
| ≥ 1280 px | Topplinje | 3 kolonner | Én skjerm, maks 640 px bred | 1 kolonne, maks 760 px |

- KI-forslag står under feltet de gjelder på alle bredder (FR-24 krever det på smal skjerm; samme mønster overalt er enklere å lære).
- Forhåndsvisningen («Slik vises oppdraget for andre.») står rett over «Publiser» på alle bredder.
- Ingen vannrett rulling på noen bredde (NFR-6). Lange ord (f.eks. «Bærehjelp/flytting») brytes.
- Berøring og mus behandles likt: trykk for å handle. Ingen funksjoner bare ved hover.
- Nettlesere: siste versjon av Chrome, Edge, Firefox og Safari (iOS/iPadOS) [ASSUMPTION].

## Key Flows

### UJ-1. Kari får måkt innkjørselen uten å ringe rundt

Kari, 72, på nettbrett (768 px eller mer), innlogget, mandag morgen i januar. Krav: FR-5–FR-8, FR-14–FR-16, FR-18–FR-21, FR-23–FR-25.

1. Oversikten «Ledige oppdrag i 0571 Oslo». Hun trykker «+ Legg ut oppdrag» (primær, øverst).
2. Nytt oppdrag, én skjerm. Fokus på «Hva trenger du hjelp til?». Hun skriver «Trenger noen som kan måke snø i innkjørselen min i morgen.» og ser hjelpeteksten om adresse og telefon.
3. Hun trykker «Få forslag». Knappen viser «Lager forslag …». Forslag kommer under beskrivelse («Trenger noen som kan måke snø i innkjørselen min i morgen.», med tipset «Skriv gjerne hvor stor innkjørselen er.» i samme boks), tittel («Måke snø i innkjørselen») og kategori (Snømåking); hun trykker «Bruk» på hvert. (FR-23, FR-24)
4. Postnummer «0571 Oslo» er forhåndsutfylt. Under «Når?» skriver hun morgendagens dato i «Dato» etter eksemplet i hjelpeteksten og «07:00» i «Klokkeslett». Hun velger «Beløp», feltet «Beløp i kr» kommer rett under, og hun skriver 200. Hun ser forhåndsvisningen og trykker «Publiser».
5. Hun havner i detaljene for oppdraget med kvitteringen «Oppdraget er lagt ut.» og status «Åpen».
6. Senere: menyen viser «Mine oppdrag 1». Øverst i Mine oppdrag står «1 oppdrag trenger at du gjør noe.», og oppdraget står under «Trenger handling» med merket «Velg hjelper» og «2 har meldt interesse». Hun åpner det; menyvalget «Mine oppdrag» er fortsatt markert, og merket «Velg hjelper» står rett under overskriften «2 har meldt interesse».
7. Interessertlista viser per person navn, «12 fullførte oppdrag · 4,9 av 5, 11 vurderinger», meldingen og «Se profil». (FR-14)
8. **Vendepunkt:** hun sammenligner erfaring og vurderinger, åpner én profil, går tilbake og trykker «Velg Amir». Dialogen: «Velge Amir? Dere får se hverandres telefonnummer.» – «Ja, velg Amir».
9. Status «Hjelper valgt»; telefonboksen viser Amirs nummer og «Avtal detaljene direkte.» (FR-15, FR-16)
10. Neste dag har Amir markert oppdraget som utført. Under «Mine oppdrag» står det under «Trenger handling» med merket «Gi tilbakemelding», og menyen viser antallet.
11. Hun velger fem stjerner («5 av 5 stjerner»), skriver en kort kommentar og trykker «Send». Kvittering: «Takk! Tilbakemeldingen er lagt til i Amirs profil.» (FR-20, FR-21)

Når noe går galt:
- *KI feiler eller tar mer enn 10 s:* «Vi fikk ikke laget forslag akkurat nå. Du kan fylle inn selv.» Tittel og kategori fylles manuelt; ingenting er tapt. (FR-25)
- *Felt mangler eller datoen er skrevet feil ved «Publiser»:* feiloppsummeringen «Skjemaet har 1 feil» får fokus, lenken fører til feltet, og feilen står også ved feltet («Skriv datoen som dd.mm.åååå, for eksempel 14.11.2026.»). Alt annet er beholdt.
- *Ingen melder interesse:* «Pågår», status Åpen; tomtilstand i detaljene; hun kan «Rediger» tidspunkt eller godtgjørelse. Interessene som kommer før en endring merkes «Meldt før endring». (FR-6)
- *Tidspunktet passerer uten hjelper:* under «Trenger handling» med «Tidspunktet er passert»; «Endre tidspunkt» åpner skjemaet med fokus på tidspunktet («Velg et nytt tidspunkt fram i tid»), eller «Avbryt oppdrag» med dialog. (FR-8)
- *Hjelperen glemmer å markere utført:* etter tidspunktet merket «Er jobben gjort?»; hun trykker «Marker som utført», bekrefter, og gir tilbakemelding. (FR-19)
- *Hjelperen trekker seg:* merket «Hjelperen trakk seg»; oppdraget er Åpent igjen, og hun velger blant de andre. (FR-17)
- *Hun trykker «Ja, velg Amir» to ganger, eller har to faner:* bare første teller; den andre får «Oppdraget er endret. Last siden på nytt.» (§4.0)

### UJ-2. Amir gjør småjobber og bygger en profil han kan vise til

Amir, 21, på mobil (360 px), ingen konto, en ettermiddag. Krav: FR-1, FR-9, FR-10, FR-12, FR-16–FR-21.

1. Innloggingssiden; han trykker lenken til registrering.
2. Registrering: navn, e-post, telefon, postnummer (poststed vises), fødselsdato, passord. Han leser personvernteksten og trykker knappen. Kontoen opprettes; han er innlogget og står på oversikten. (FR-1)
3. Oversikten viser åpne oppdrag i hans postnummer, tidligste først. Han trykker kategoriknappen «Bærehjelp/flytting»; fokus blir på knappen, og linja under overskriften viser «2 ledige oppdrag i Bærehjelp/flytting i …», som også leses opp. Han ser et oppdrag lørdag, 400 kr. (FR-10, FR-11)
4. Han trykker kortet. Detaljene viser beskrivelsen og oppdragsgiveren med erfaring. Han skriver i «Melding til …» og trykker «Meld interesse». (FR-9, FR-12)
5. Knappen byttes med «Du har meldt interesse. Under Mine oppdrag ser du om … har valgt deg.» og lenken «Trekk interessen».
6. Senere: «Mine oppdrag» → fanen «Oppdrag jeg hjelper med». Oppdraget står under «Pågår» med «Du er valgt». Han åpner det og ser oppdragsgiverens nummer i telefonboksen. (FR-16, FR-18)
7. Lørdag bærer han møblene, trykker «Marker som utført» og bekrefter. Kvittering «Oppdraget er markert som utført.» (FR-19)
8. **Vendepunkt:** oppdragsgiveren gir ham fem stjerner. På «Profil» ser han det fullførte oppdraget under Bærehjelp/flytting, snittet og kommentaren. (FR-21)
9. Raden har merket «Gi tilbakemelding»; han gir oppdragsgiveren stjerner og trykker «Send». (FR-20)
10. Når han søker sommerjobb, viser han profilen på mobilen. Teksten om at erfaringen er registrert av brukere og ikke verifisert står der. (§4.7)

Når noe går galt:
- *Under 18 eller e-post i bruk:* feil ved feltet; alt annet beholdt, unntatt passord. (FR-1)
- *Oppdragsgiveren velger en annen:* «Ikke valgt» under «Ferdige», bare tittel og status, raden kan ikke åpnes. (FR-18)
- *Han kan ikke likevel:* «Trekk meg fra oppdraget» → dialog → «Ja, trekk meg». Oppdraget blir Åpent, numrene skjules, raden viser «Du trakk deg», og han kan melde interesse på nytt. (FR-17)
- *Han prøver å markere utført for tidlig:* knappen finnes ikke før datoen; i stedet står når han kan gjøre det. (FR-19)
- *Han er fjernet av oppdragsgiveren:* «Du er ikke lenger valgt», og detaljene viser «Du er ikke lenger valgt til dette oppdraget» i stedet for «Meld interesse». (FR-12, FR-17)

### Støtteflyter

Ikke egne brukerreiser i PRD-en, men flater SM-5 tester. [ASSUMPTION] Personene er lånt fra UJ-1 og UJ-2.

**Innlogging og utlogging (Kari, FR-2):** 1. Innloggingssiden, fokus på «E-post». 2. Feil passord → «Feil e-post eller passord.», e-post beholdt. 3. Riktig → oversikten. 4. Profil → «Logg ut» (øverst, under navnet) → innloggingssiden med «Du er logget ut.» Etter fem feil på 15 minutter: «For mange mislykkede forsøk. Prøv igjen om 15 minutter.»

**Rediger profil (Amir, FR-22):** 1. Profil → «Rediger profil» (øverst, under navnet). 2. Ser navn, e-post og fødselsdato som tekst, og feltene Om meg, Postnummer, Telefonnummer. 3. Skriver «om meg», trykker «Lagre endringer». 4. Tilbake på profilen med «Profilen er oppdatert.» Ugyldig postnummer → feil ved feltet.

**Slett konto (Amir, FR-4):** 1. Profil → «Slett konto» (lenke nederst). 2. Siden forklarer hva som slettes, at gitte tilbakemeldinger beholdes som «Slettet bruker», og at kommentarer kan avsløre hvem som skrev dem. 3. Han skriver passordet og trykker «Slett kontoen min». 4. Feil passord → «Passordet er feil. Kontoen er ikke slettet.» 5. Riktig → innloggingssiden med «Kontoen din er slettet.»

### Sporing: krav → flate

| Krav | Flate / avsnitt |
|---|---|
| FR-1, FR-2, FR-3 | Registrering, Innlogging, Støtteflyter, UJ-2 steg 1–2 |
| FR-4 | Slett konto, Slettet bruker, «Slettet bruker» i Voice and Tone |
| FR-5, FR-6, FR-8 | Nytt / Rediger oppdrag, UJ-1 steg 1–5, Responsive |
| FR-7, FR-15, FR-17, FR-19 | Detaljer-tabellen, Bekreftelser |
| FR-9, FR-12, FR-13, FR-14, FR-16 | Detaljer-tabellen, UJ-2 steg 4–6, UJ-1 steg 7–9 |
| FR-10, FR-11 | Oversikten, `category-button`, postnummerfilter med «Vis», tomtilstand med «Velg et annet postnummer» |
| FR-18 | Mine oppdrag, `list-row`, nav-badge |
| FR-20, FR-21, FR-22 | Tilbakemelding, Profil (`star-rating` visning, `list-row`), Rediger profil |
| FR-23–FR-26 | KI-forslag i Interaction Primitives, `ki-suggestion-box` |
| NFR-6, NFR-7, NFR-8, NFR-9, NFR-10, NFR-11, NFR-12 | Responsive, Accessibility Floor, Voice and Tone, hjelpetekst, State Patterns, Information Architecture, ren tekst i `ki-suggestion-box` |

## Inspiration & Anti-patterns

Ingen referanseprodukter er valgt. Avvist i Discovery (`.memlog.md`):

- **Avvist – klinisk eller offentlig uttrykk** (legeside, etatsskjema): kaldt og skremmende for Kari; uttrykket skal være hyggelig og nabolagsaktig.
- **Avvist – barnslig eller overdrevent lekent:** undergraver tilliten mellom fremmede; derfor ingen illustrasjoner, maskoter eller emoji.
- **Avvist – skjulte funksjoner:** hamburgermeny, menyer med tre prikker, sveip, ikon-knapper uten tekst. Alt brukeren kan gjøre, står synlig.
- **Avvist – nedtrekksliste for kategori:** erstattet av store kategoriknapper (svar på skisse-spørsmål 2).
- **Avvist – å presse KI:** «Få forslag» er sekundær og valgfri (SM-C1).

## Endringer fra skissene

Punktene i PRD §8 og avstemming mot PRD v1.1. Skissene i `skisser-skjermbilder.md` er ikke oppdatert; denne lista og spinene gjelder.

| # | Endring | Krav |
|---|---|---|
| 1 | Tilbakemelding: 1–5 stjerner som store knapper og egen «Send»-knapp, ikke tallknapper. «Dårlig»/«Veldig bra» beholdes som ytterpunkter. | FR-20, NFR-7, PRD §8 |
| 2 | Oversikten: tidspunkt alltid som dato og klokkeslett; «Fleksibelt denne uken» («Sette opp ny iPad») får et ekte tidspunkt. | FR-5, PRD §8 |
| 3 | Tom oversikt: lenken «Se alle postnumre» fjernes. Med en kategori valgt: forslag om annen kategori + «Vis alle kategorier». Med «Alle» valgt: «Prøv et annet postnummer.» + knappen «Velg et annet postnummer», som flytter fokus til postnummerfeltet. Poststed står med i teksten («0571 Oslo»). | FR-10, FR-11, PRD §8 |
| 4 | KI-eksemplet rettes. Skissen la til «Innkjørselen er ca. 10 meter. Spade finnes.» (og i 3a «Spade finnes i garasjen.»), og tittelen «… før kl. 07:30» la til et klokkeslett. Eksemplet bruker nå Karis tekst fra PRD UJ-1, som i Key Flows: «Trenger noen som kan måke snø i innkjørselen min i morgen.» Rettet forslag: beskrivelse «Trenger noen som kan måke snø i innkjørselen min i morgen.» (uten nye opplysninger), tittel «Måke snø i innkjørselen» (som eksemplet i FR-26), kategori Snømåking, tips «Skriv gjerne hvor stor innkjørselen er.» (eksemplet i FR-24) inne i beskrivelsesboksen. | FR-24, FR-26, PRD §8 |
| 5 | KI-forslag står under feltet de gjelder, ikke i én samleboks. Knappen heter «Få forslag». | FR-23, FR-24 |
| 6 | Mine oppdrag: situasjonene og merkene fra FR-18; gruppene «Trenger handling» / «Pågår» / «Ferdige» følger FR-18-sorteringen; fullt fanenavn; avbrutte vises i «Ferdige» (ingen «Vis avbrutte oppdrag»); antall ved «Mine oppdrag» i menyen. | FR-18, PRD §8 |
| 7 | Nytt oppdrag: to steg under 768 px, én skjerm fra 768 px; kategori som store knapper; knappen heter «Publiser». | FR-5, PRD §8 |
| 8 | Oversikten: kategorifilter som knapper, ikke nedtrekksliste; overskriften har poststed. | FR-11, PRD §3 |
| 9 | Nye flater: registrering, innlogging, rediger profil, slett konto (egen side med passord), slettet bruker, feilside. | FR-1, FR-2, FR-4, FR-22, PRD §8 |
| 10 | «Logg ut» er en sekundær knapp, ikke lenke. «Rediger profil» er sekundær knapp-lenke. Begge står øverst på egen profil, under navnet; skissen hadde dem nederst. «Slett konto» blir stående som lenke nederst. | FR-21 |
| 11 | Menyen ligger nederst bare på mobil; i topplinjen fra 768 px. | NFR-11 |
| 12 | «Velg» på interesserte er sekundære knapper med navn («Velg Amir»), ikke fylte – én primærknapp per skjerm. | Skisser «Felles prinsipper», FR-15 |
| 13 | Snitt og antall som «4,9 av 5, 11 vurderinger». | FR-21 |
| 14 | Profilen viser alle tilbakemeldinger; ingen «Vis alle tilbakemeldinger». | FR-21 |
| 15 | «Avbryt» ved utgått oppdrag heter «Avbryt oppdrag». | FR-7, FR-8 |
| 16 | Oversikten: postnummerfilteret får knappen «Vis»; skissen hadde bare feltet. | FR-10 |
| 17 | Profil: snittet vises med stjerner (bare visning) i tillegg til teksten «4,9 av 5, 11 vurderinger». | FR-21 |
| 18 | Mine oppdrag, interesserte og tilbakemeldinger vises som rader (`list-row`); rader som kan åpnes har pil ›, de andre ikke. | FR-14, FR-18, FR-21 |
| 19 | KI-forslag: «Ikke bruk» i stedet for «Forkast». | FR-24, NFR-8 |
| 20 | Oversikten viser antall treff synlig under overskriften; Mine oppdrag forklarer tallet i menyen med en linje øverst. | FR-10, FR-18 |
| 21 | Bekreftelsesdialoger: angre-valget sier hva som skjer («Ikke ennå», «Nei, behold Amir», «Nei, jeg blir», «Behold oppdraget»), og dialogen nevner oppdragstittelen. | NFR-8 |
| 22 | Dato og klokkeslett er tekstfelt med fast format («dd.mm.åååå», «tt:mm»), ikke kalender. | FR-5, NFR-7 |

## Åpne punkter

**Til PRD (`bmad-prd`, oppdatering):**
- Antallet ved «Mine oppdrag» i menyen er ikke beskrevet i PRD-en. Trenger presisering i FR-18 eller NFR-11 (eller et nytt krav-ID) og en linje i endringsloggen, så sporingen holder.
- **Besluttet i UX 2026-11-07, må inn i FR-18:** nytt merke «Velg hjelper» på eget oppdrag med status Åpen, tidspunktet ikke passert og minst én interessert, så det står under «Trenger handling» og teller i menyen (UJ-1 steg 6).
- **Besluttet i UX 2026-11-07, må inn i FR-18:** «Oppdrag jeg hjelper med» sorteres etter brukerens egen situasjon: «Ikke valgt», «Du er ikke lenger valgt» og «Du trakk deg» står under «Ferdige» selv om oppdraget fortsatt er Åpent eller har Hjelper valgt.
- NFR-6 eller NFR-7 bør få «Innhold flyter om ved 320 CSS px (WCAG 1.4.10)», så kravet kan spores. SM-5 bør vise til den utvidede testlista T1–T6 i § Accessibility Floor.

**Til arkitektur (`bmad-architecture`):**
- Frontend-rammeverk og komponentbibliotek (Foundation). Native `<dialog>` med `showModal()`, `aria-live` og `aria-disabled` må virke.
- Fra PRD §8: kilde til postnummerlista (må gi poststed), mekanisme mot forespørsler fra andre nettsteder (NFR-12), sommertid og tegnsett.
- Tolkning av dato og klokkeslett fra tekstfelt (formatene i «Når?»), i norsk tid.
- Server-rendret eller klientrendret – avgjør om «Laster …»-tilstander trengs, og hvordan fokus settes på kvittering, feiloppsummering og valgt kategori etter sidelasting.
- Utfylt skjema beholdes når innloggingen utløper.
- To steg på mobil som ett skjema med to deler, så feil fra serveren kan vises i riktig steg.
- Faner med egen adresse; antall «Trenger handling» regnes ut per sidevisning.

**Til gruppen:**
- Alle [ASSUMPTION]-tekster i Voice and Tone og Interaction Primitives, særlig melding ved for mange innloggingsforsøk og ved KI-kvoten.
- Nettbrett (768–1279 px) får nytt oppdrag på én skjerm. Kari bruker nettbrett; sjekk i SM-4-testen om hun heller vil ha to steg.
- Ingen «glemt passord» i v1 (PRD §6.2). Skal innloggingssiden si hva man gjør da?

**I dette UX-steget:**
- Ni key-screen-mockups og de to fargeprøvene som valgte tema og struktur, ligger i `mockups/` (lista i § Foundation). De tidlige fargeprøvene og kildeutdraget ligger i `.working/`.
- Gjennomgangen med linsen universell utforming ([review-accessibility.md](review-accessibility.md)) er gjort. H1–H4, M1–M10 og de lave funnene er rettet i spinene 2026-11-07, unntatt L10 om måneder skrevet fullt (brukeren valgte kort form).
- Visuelle [ASSUMPTION]-er i DESIGN.md (bunnmeny, valgt kategoriknapp, deaktivert knapp, KI-boks, `list-row`, stjernevisning, `action-tag` over to linjer) er vist i mockupene, men ikke godkjent av gruppen.
- Ikke vist i mockupene: deaktivert «Få forslag» under 10 tegn, valgt kategori i skjemaet, oppdragsgiverblokken («Lagt ut av Kari») i andres oppdrag, PC-bredde for andre skjermer enn oversikten.
