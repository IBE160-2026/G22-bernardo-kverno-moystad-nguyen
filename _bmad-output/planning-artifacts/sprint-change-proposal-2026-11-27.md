---
title: 'Sprint Change Proposal – Bilde av oppdraget'
date: '2026-11-27'
status: 'godkjent'
trigger: 'Nytt krav fra Heidi (produkteier) under Epic 2'
scope: 'Moderat'
---

# Sprint Change Proposal – Bilde av oppdraget

## 1. Hva som utløste endringen

**Utløser:** Heidi kom på et krav som manglet i planen, mens story 2.2 ble implementert (27.11.2026): «bilder skal være en mulighet å legge inn sammen med oppdragsbeskrivelse. Et bilde som viser oppdraget. At oppdrag vises sammen med et bilde i oversikten om bilde er tatt med.»

**Type:** Nytt krav fra produkteieren.

**Problem:** Oppdragsgiveren kan bare beskrive oppdraget med tekst. Et bilde (snøen i innkjørselen, hekken som skal klippes, flyttelasset) gjør det lettere for hjelperen å anslå jobben. I dag finnes bilder ingen steder i PRD, arkitektur, UX eller epics. Søk etter «bilde», «foto», «image» og «opplast» i planleggingsdokumentene gir bare treff om skjermbilder og statiske filer.

**Bevis og begrensninger:**
- PRD §6.2 og §6.3 utelukker ikke bilder. Kravet er nytt, ikke i strid med ikke-målene.
- Vercel Functions godtar høyst 4,5 MB i forespørselskroppen. Bilder fra mobilkamera er ofte 3–8 MB.
- Vercel har ikke varig filsystem, så bildet må lagres i databasen eller i en ekstern lagringstjeneste.
- Bilder fra mobil har EXIF-data, ofte med GPS-posisjon. NFR-9 sier at appen aldri ber om eksakt adresse. En GPS-posisjon i et bilde er en adresse.
- Nettlesere kan ikke fylle ut et filfelt på nytt. Det påvirker gjenvisning ved feil (NFR-10, DoD «alt utfylt beholdes») og AD-7 (story 2.6).

## 2. Konsekvensanalyse

### Epics

| Epic | Påvirkning |
|---|---|
| Epic 1 | Ingen. |
| Epic 2 (pågår) | Ny story **2.7 Bilde av oppdraget (Bør)**. Den bygges etter 2.5 og før 2.6, fordi den trenger kortet fra 2.3 og redigeringen fra 2.5. 2.1–2.5 endres ikke, og 2.2 implementeres videre som planlagt. 2.6 får et akseptansekriterium om bildet. |
| Epic 3 | Ingen endring i stories. Detaljene viser bildet for alle som ser detaljene (FR-9). |
| Epic 4 | Story 4.5 (slette konto): bildet slettes også på oppdrag som beholdes. |
| Epic 5 | Ingen. KI ser ikke bildet. |
| Epic 6 | Story 6.1 og T2–T5: bildet og bildeteksten er med i de manuelle testene. Story 6.3: README nevner bildene i eksempeldataene. |

Ingen epic blir overflødig, og rekkefølgen av epics endres ikke.

### Dokumenter

| Dokument | Endring |
|---|---|
| PRD | Ny **FR-27 Bilde av oppdraget (Bør)**. FR-4, FR-9, FR-10, NFR-9 og NFR-12 får en linje hver. §6.1 får FR-27 under Bør og en linje om følgene av et kutt. Ny rad i §9.2, versjon 1.3 i endringsloggen. |
| Arkitekturspine | Ny **AD-18 Bilder behandles ett sted og lagres i databasen**. Endringer i AD-1 (tabellen eies av `oppdrag`), AD-7 (filfelt), Stack (Pillow), datamodellen, kildetreet (`bilde.js`), konvensjonen Klientatferd, Capability-kartet og URL-ene. |
| EXPERIENCE.md | Skjemafelt («Bilde (valgfritt)» og «Hva viser bildet?»), feiltekster, kortet i oversikten, detaljene, redigering, Accessibility Floor (T1-sider), sporingen og en rad i «Endringer fra skissene». |
| DESIGN.md | Kortet med bilde, bildet i detaljene og filfeltet. |
| Epics | FR-27 i inventaret og i FR Coverage Map, ny AR og UX-DR, Epic 2 dekker FR-27, ny story 2.7, og ett akseptansekriterium hver i 2.6, 4.5 og 6.1. |
| sprint-status.yaml | `2-7-bilde-av-oppdraget: backlog`, plassert før 2-6, med en kommentar om rekkefølgen. |
| epic-2-context.md | Oppdateres med FR-27, AD-18 og story 2.7. |
| Mockupene | Oppdateres ikke. Teksten i EXPERIENCE.md og DESIGN.md gjelder for bildet (se §4.5). |

### Tekniske følger

- Ny avhengighet: **Pillow** (12.x). Den har ferdige wheels for Linux og Windows, og pakken er langt under Vercels grense.
- Ny migrering (0004 eller neste): tabellen `oppdragsbilde`.
- Ny klientfil: `core/static/js/bilde.js`.
- Ingen nye hemmeligheter, ingen ny ekstern tjeneste og ingen endring i CI eller deploy.

## 3. Anbefalt vei

**Valgt: direkte justering.** Ny story i Epic 2, nytt Bør-krav, og ingen tilbakerulling.

- **Tilbakerulling** gir ingenting, fordi 2.1 og 2.2 virker uten bilde, og 2.7 legger bildet oppå.
- **MVP-gjennomgang** trengs ikke, fordi kravet er Bør og kan kuttes uten å røre kjerneflyten.

**Beslutninger (anbefalt alternativ, delegert av Heidi 2026-11-26 for Epic 2):**

| # | Valg | Anbefalt (valgt) | Alternativ | Hvorfor |
|---|---|---|---|---|
| 1 | Prioritet | **Bør** (FR-27), bygges etter 2.5 og før 2.6. Kuttes etter 2.6, men før Epic 5 | Må | Kjerneflyten (R1–R13) virker uten bilde. Fristen 3.12 for Epic 2 står fast. |
| 2 | Lagring | **I databasen**, i egen tabell `oppdragsbilde`, servert av appen | Supabase Storage | Samme kode mot SQLite og Postgres (AD-13). Ingen ny hemmelighet eller tjeneste. Tilgangskontrollen i FR-9 gjelder automatisk. Plassen holder: 1 600 px JPEG er cirka 250 kB, og Supabase Free har 500 MB. |
| 3 | Antall | **Ett bilde** per oppdrag | Flere | Det var det Heidi ba om. Det holder skjema, kort og test enkle. |
| 4 | Personvern | Bildet **kodes alltid om på serveren**, så EXIF (også GPS) forsvinner. Hjelpetekst: «Ikke vis husnummer, bilskilt, navn eller ansikter.» | Lagre originalen | NFR-9: appen skal aldri få eksakt adresse. |
| 5 | Alt-tekst | **«Hva viser bildet?»** er påkrevd når bildet er valgt (3–120 tegn). Teksten er `alt` i detaljene. I kortet i oversikten har bildet `alt=""` | Tittelen som alt | WCAG 1.1.1. Kortet er én lenke som allerede har tittelen, så bildet i kortet er pynt for skjermlesere. |
| 6 | Størrelse | Filen er **høyst 4 MB**, og bare JPEG, PNG og WebP godtas (sjekkes ved å åpne filen, ikke filnavnet). `bilde.js` skalerer ned i nettleseren før innsending | Ingen nedskalering i klienten | Vercel stopper forespørsler over 4,5 MB. Uten JS vises vår egen melding opp til grensen. Over 4,5 MB uten JS kommer Vercels feilside (kjent begrensning, §9.2). |
| 7 | Gjenvisning ved feil | Serveren **beholder et gyldig bilde** som et skjult felt (`bilde_beholdt`, base64 av den omkodede JPEG-en) og viser det med «Fjern bildet». Ved innsending kodes det om på nytt | «Velg bildet på nytt» | DoD: alt utfylt beholdes. Ingen tilstand på serveren og ingen opprydding. Et forfalsket felt gir ikke mer enn en vanlig opplasting gir. |
| 8 | Hvor bildet vises | Skjemaet (steg 1, rett etter beskrivelsen), forhåndsvisningen, kortet i oversikten (øverst, 16:9) og detaljene (under tittelen). **Ikke** i radene under «Mine oppdrag» | Også i radene | Radene er kompakte lenkerader (UX-DR). |
| 9 | Eksempeldata | 4 av de 12 eksempeloppdragene får bilde. Bildene **tegnes av seed med Pillow** (enkle illustrasjoner uten personer og adresser) | Bildefiler i repoet | Ingen lisensspørsmål og ingen binærfiler i repoet. Oversikten viser kort både med og uten bilde. |
| 10 | Mockupene | **Oppdateres ikke.** EXPERIENCE.md og DESIGN.md gjelder for bildet | Oppdatere 3 mockups | Tiden går heller til koden. Avviket står i EXPERIENCE § Endringer fra skissene. |

**Innsats:** middels, cirka én dag for story 2.7.
**Risiko:** middels.
- Pillow på Vercel: lav risiko, ferdige wheels.
- Grensen på 4,5 MB uten JS: dokumentert.
- Fristen 3.12 for Epic 2: 2.7 er Bør. Blir tiden knapp, kuttes 2.6 først og så 2.7, før Epic 5 berøres.

## 4. Detaljerte endringer

### 4.1 PRD (`prds/prd-G22-…-2026-11-05/prd.md`)

**Ny FR-27, etter FR-9 i §4.2:**

```markdown
#### FR-27: Bilde av oppdraget
Oppdragsgiveren kan legge ved ett bilde som viser oppdraget.
**Sporing:** UJ-1, UJ-2 · — · — (tillegg fra Heidi 2026-11-27, §9.2) · **Prioritet:** Bør

**Konsekvenser (testbare):**
- Bildet er valgfritt, både når oppdraget legges ut (FR-5) og når det redigeres (FR-6). Ved redigering kan bildet byttes eller fjernes. Endring av bildet setter ikke «Meldt før endring».
- Gyldig bilde: JPEG, PNG eller WebP, høyst 4 MB og høyst 40 megapiksler. Formatet avgjøres av innholdet i fila, ikke av navnet. Ugyldig fil avvises med melding ved feltet, og ingenting lagres.
- Når et bilde er valgt, er «Hva viser bildet?» påkrevd (3–120 tegn, samme normalisering som andre tekstfelt). Teksten er bildets alternative tekst.
- Bildet lagres uten metadata (EXIF, også GPS-posisjon) og skaleres ned til høyst 1 600 px på den lengste siden.
- Hjelpeteksten ved bildet er «Ikke vis husnummer, bilskilt, navn eller ansikter.» (NFR-9).
- Bildet vises i detaljene (FR-9) og øverst på kortet i oversikten (FR-10). Oppdrag uten bilde vises som før.
- Bildet kan bare hentes av den som kan se detaljene (FR-9). Andre får samme svar som for et oppdrag som ikke finnes.
- Finner serveren feil i andre felt, beholdes et gyldig bilde, og brukeren kan fjerne det.

**Kjent begrensning:** Uten JavaScript kan et bilde over cirka 4,5 MB stoppes av Vercel før appen ser det. Da vises Vercels feilside. Med JavaScript skaleres bildet ned før innsending.
```

**Endringer i eksisterende tekst:**
- **FR-4, tabellen:** ny rad «Bilder på egne oppdrag som beholdes (Utført, eller Avbrutt fra Hjelper valgt) | Slettes». Oppdrag som slettes, tar bildet med seg.
- **FR-9, første punkt:** «Detaljene viser alle feltene i oppdraget, **bildet med bildeteksten hvis det finnes (FR-27)**, og status. …»
- **FR-10, punktet «Hvert oppdrag i oversikten viser …»:** «… tittel, kategori, tidspunkt og godtgjørelse, **og bildet øverst hvis oppdraget har et (FR-27)**.»
- **NFR-9:** «… og innhold brukeren selv legger inn (**også bilde av oppdraget, lagret uten metadata**), …». Nytt punkt: «Bilder lagres uten EXIF og GPS-posisjon, og hjelpeteksten ved bildet ber brukeren ikke vise husnummer, bilskilt, navn eller ansikter (FR-27).»
- **NFR-12, «Testes ved»:** legg til «bildetekst» i lista over felt som testes med `<script>alert(1)</script>`. Nytt punkt: «Opplastede filer åpnes og kodes om på serveren, og bare JPEG, PNG og WebP godtas (FR-27, AD-18).»
- **§6.1, tabellen:** Bør = «FR-22, FR-23–FR-26, **FR-27**». Nytt punkt: «**Kuttes FR-27:** Oppdrag har ikke bilde. FR-4, FR-9, FR-10, NFR-9 og NFR-12 mister linjene om bildet, og «Hva viser bildet?» og bildet tas ut av SM-5.»
- **§9.1, sporing:** FR-27 får raden «tillegg fra produkteier, ingen regel i briefen».
- **§9.2, ny rad:** «Bilde av oppdraget | Ikke nevnt | **Tillegg (2026-11-27):** ett valgfritt bilde per oppdrag med påkrevd bildetekst, vist i oversikten og detaljene. Lagret uten metadata. Kjent begrensning for store bilder uten JavaScript (FR-27) | Gjør det lettere for hjelperen å anslå jobben. Ønsket av Heidi under Epic 2. Bør, så kjerneflyten avhenger ikke av det.»
- **Frontmatter og topptabell:** `updated: 2026-11-27`, versjon 1.3.
- **Endringslogg:** «2026-11-27 | 1.3 | Ny FR-27 Bilde av oppdraget (Bør), fra Heidi under Epic 2. Linjer i FR-4, FR-9, FR-10, NFR-9, NFR-12, §6.1, §9.1 og §9.2. Se sprint-change-proposal-2026-11-27.md.»
- **SM-5:** legg til «oversikt og detaljer med bilde» blant tilstandene.

### 4.2 Arkitekturspine (`ARCHITECTURE-SPINE.md`)

**Ny AD-18, etter AD-17:**

```markdown
### AD-18 — Bilder behandles ett sted og lagres i databasen [ADOPTED]

- **Binds:** FR-27, FR-4, FR-9, NFR-9, NFR-12
- **Prevents:** at originalfiler med GPS-posisjon blir lagret, at en fil som later som den er et bilde, blir servert, at bilder kan hentes forbi tilgangsreglene i FR-9, og at bilder bare virker lokalt fordi Vercel ikke har varig filsystem.
- **Rule:**
  - **Lagring:** tabellen `oppdragsbilde` (én rad per oppdrag, `oppdrag_id` er primærnøkkel og fremmednøkkel) har `bilde` og `miniatyr` som binærdata (`LargeBinary`), `bildetekst`, `bredde`, `hoyde` og `opprettet`. Den eies av `oppdrag` (AD-1). Samme kode mot SQLite og Postgres (AD-13).
  - **Behandling:** bare `oppdrag/bilde.py` åpner opplastede filer. Den bruker Pillow og:
    - godtar formatet JPEG, PNG eller WebP slik Pillow leser det, og avviser alt annet
    - avviser filer over 4 MB og over 40 megapiksler (sjekket før dekoding)
    - snur bildet etter EXIF-orienteringen
    - lagrer en JPEG på høyst 1 600 px og en miniatyr på høyst 640 px, uten metadata
  - **Servering:** `GET /oppdrag/{id:int}/bilde` og `/oppdrag/{id:int}/bilde/liten` krever innlogging (AD-4). De bruker samme tilgangsregel som detaljene (FR-9) og gir samme 404 ellers. Svaret er `image/jpeg` med `Cache-Control: private, max-age=31536000, immutable`. URL-en i malene har `?v={versjon}`, så et nytt bilde får ny URL.
  - **Gjenvisning:** ved 422 legger ruta den omkodede JPEG-en i det skjulte feltet `bilde_beholdt` (base64). Ved neste innsending går feltet gjennom `oppdrag/bilde.py` på nytt, akkurat som en opplasting.
  - **Skjemaet:** `enctype="multipart/form-data"`. CSRF-mellomvaren (AD-5) leser filfelt uten å legge dem i `request.state.skjema` som tekst.
  - **Sletting:** bildet slettes med oppdraget, og `profil/service.py` sletter bildet på oppdrag som beholdes når en konto slettes (AD-8).
  - **Klienten:** `bilde.js` skalerer et valgt bilde ned i nettleseren (canvas, JPEG, høyst 1 600 px) før innsending, og viser det i forhåndsvisningen. Uten JS sendes fila som den er. JS har ingen regler. Serveren sjekker alltid.
```

**Endringer i eksisterende tekst:**
- **AD-1:** `oppdrag` eier også `oppdragsbilde`.
- **AD-7, Svaret:** «alle innsendte felt som skjulte felt, unntatt passord, CSRF **og filfelt**». Nytt punkt: «**Filfelt:** en fil kan ikke bli et skjult felt. Hadde innsendingen et nytt bilde, sier 401-siden «Velg bildet på nytt etter innlogging.». `bilde_beholdt` følger med som et vanlig skjult felt.»
- **Konvensjonen Klientatferd:** nytt punkt: «`bilde.js` skalerer et valgt bilde ned før innsending og viser det i forhåndsvisningen. Uten JS: fila sendes som den er, og serveren avviser over 4 MB.»
- **Konvensjonen URL-er (der URL-ene er listet):** `/oppdrag/{id:int}/bilde` og `/bilde/liten` er GET-ruter som gir bildet. De er unntak fra mønsteret `<handling>` med bekreftelsesside.
- **Stack:** ny rad «Pillow | 12.x».
- **Datamodell:** `OPPDRAG ||--o| OPPDRAGSBILDE : har`.
- **Kildetre:** `static/js/` får `bilde`, og `oppdrag/` får `bilde.py`.
- **Capability-kartet:** ny rad «FR-27 bilde av oppdraget | oppdrag (`bilde.py`) | AD-18, AD-1, AD-4, AD-13».
- **Frontmatter:** `binds` får FR-27, `updated: '2026-11-27'`. Endringen føres i `.memlog.md`.

### 4.3 EXPERIENCE.md

- **§ Skjemafelt:**
  - Ny rad for «Bilde (valgfritt)»: filfelt `accept="image/jpeg,image/png,image/webp"`, hjelpetekst «Ikke vis husnummer, bilskilt, navn eller ansikter.» og «JPEG, PNG eller WebP, høyst 4 MB.».
  - Ny rad for «Hva viser bildet?»: tekstfelt med teller (120). Det vises med CSS `:has()` når en fil er valgt, eller når et bilde er beholdt.
  - Et beholdt bilde vises som miniatyr med avkrysningen «Fjern bildet».
  - Plassering: steg 1, rett etter beskrivelsen.
- **§ Feiltekster ved felt:**
  - «Velg et bilde i JPEG, PNG eller WebP.»
  - «Bildet er for stort. Velg et bilde på høyst 4 MB.»
  - «Bildet har for mange piksler. Velg et mindre bilde.»
  - «Skriv hva bildet viser.»
  - «Teksten må ha minst 3 tegn.»
  - «Teksten kan ha høyst 120 tegn.»
- **§ Ordrette tekster / forslag:** «Fjern bildet», «Bytt bilde» og «Velg bildet på nytt etter innlogging.».
- **§ Oppdragsdetaljer etter rolle og status:** bildet står under tittelen for alle som ser detaljene, med `alt` = bildeteksten, `width` og `height` og ingen lenke.
- **Kortet i oversikten (§ Component Patterns, Rader i lister og kort):** miniatyren står øverst (16:9, `object-fit: cover`, `alt=""`, `loading="lazy"`, `width` og `height`). Kort uten bilde har ingen plassholder.
- **§ To steg i nytt oppdrag:** bildet og «Hva viser bildet?» står i steg 1. Forhåndsvisningen viser bildet når det er valgt.
- **Redigering (2.5-delen):** gjeldende bilde vises med «Bytt bilde» (filfelt) og «Fjern bildet».
- **§ Accessibility Floor, T1:** nye tilstander er «oversikt med bilde», «detaljer med bilde» og «nytt oppdrag med bildefeil».
- **§ Sporing:** FR-27 → skjema, kort, detaljer.
- **§ Endringer fra skissene:** ny rad «Bilde av oppdraget (2026-11-27): ikke i skissene eller mockupene. Teksten her gjelder.»

### 4.4 DESIGN.md

- **§ Kort og rader:** kort med bilde har bildet øverst, i full kortbredde, med radius som kortets øvre hjørner og forholdet 16:9 (`aspect-ratio`, `object-fit: cover`). Kort uten bilde er uendret.
- **§ Skjema og filter:** filfeltet har samme høyde for trykkflaten (≥ 48 px) og samme fokusring som andre felt. Miniatyren av et beholdt bilde er høyst 160 px bred.
- **§ Andre komponenter:** bildet i detaljene har full innholdsbredde, høyst 480 px høyt, med `object-fit: contain` og `--radius-md`.

### 4.5 Epics (`epics.md`)

- **Requirements Inventory:** ny linje **FR-27: Bilde av oppdraget (Bør)** med sammendrag av konsekvensene over.
- **Additional Requirements:** ny **AR-31** (AR-30 var tatt): AD-18 med `oppdrag/bilde.py`, tabellen `oppdragsbilde`, servering bak FR-9 og `bilde.js`.
- **UX Design Requirements:** ny **UX-DR33**: filfeltet med hjelpetekst og «Hva viser bildet?», kortet med bilde og bildet i detaljene.
- **FR Coverage Map:** «FR-27 → Epic 2 (story 2.7), med linjer i 4.5 (sletting) og 6.1».
- **Epic List og Epic 2 «FRs covered»:** legg til FR-27 (Bør).
- **Ny story 2.7, etter 2.6 i dokumentet**, med merknaden «Bygges etter 2.5 og før 2.6»:

```markdown
### Story 2.7: Bilde av oppdraget (Bør)

Som oppdragsgiver
vil jeg legge ved et bilde som viser oppdraget,
slik at hjelperen lettere ser hva jobben er.

**Krav:** FR-27, FR-4 (bildet ved sletting forberedes i service), FR-9, FR-10, NFR-9, NFR-10, NFR-12, AD-18, AR-31, UX-DR33. **Kan kuttes** (Bør). Bygges etter 2.5 og før 2.6.

**Acceptance Criteria:**

**Gitt** «Nytt oppdrag»
**Når** Kari velger et bilde og skriver hva det viser
**Så** lagres oppdraget med bildet, kodet om til JPEG på høyst 1 600 px uten EXIF og GPS, og med en miniatyr på høyst 640 px
**Og** detaljene viser bildet under tittelen med bildeteksten som `alt`, og kortet i oversikten viser miniatyren øverst med `alt=""`.

**Gitt** en fil som ikke er JPEG, PNG eller WebP (også en tekstfil eller SVG som heter `.jpg`), en fil over 4 MB eller et bilde over 40 megapiksler
**Når** skjemaet sendes
**Så** vises feilteksten ved bildefeltet, ingenting lagres, og de andre feltene beholdes (NFR-10).

**Gitt** et bilde uten «Hva viser bildet?», eller en tekst under 3 eller over 120 tegn
**Når** skjemaet sendes
**Så** vises feilen ved feltet, og bildet beholdes som miniatyr med «Fjern bildet» (`bilde_beholdt`).

**Gitt** et beholdt bilde etter 422
**Når** skjemaet sendes på nytt med gyldige felt
**Så** lagres oppdraget med bildet. Et forfalsket `bilde_beholdt` avvises som en ugyldig fil.

**Gitt** et oppdrag med status Avbrutt, eller et som ikke finnes
**Når** en annen bruker enn oppdragsgiveren og valgt hjelper henter `/oppdrag/{id}/bilde`
**Så** er svaret samme 404 som for detaljene (FR-9). Uten innlogging gjelder FR-3.

**Gitt** «Rediger oppdrag» (2.5)
**Når** Kari bytter eller fjerner bildet
**Så** lagres endringen, `vesentlig_endret` settes ikke, og URL-en til bildet endres (`?v=`).

**Gitt** mobil med JS
**Når** Kari velger et bilde på 6 MB
**Så** skalerer `bilde.js` det ned før innsending, og forhåndsvisningen viser bildet. Uten JS virker skjemaet med bilder opp til 4 MB.

**Gitt** `<script>alert(1)</script>` i «Hva viser bildet?»
**Når** detaljene vises
**Så** står teksten som tekst i `alt` (NFR-12).

**Gitt** seed
**Når** eksempeldataene lastes
**Så** har 4 av oppdragene bilder tegnet av seed (uten personer og adresser), i ulike kategorier.

**Gitt** T1
**Når** testen kjøres
**Så** er oversikten med bilder, detaljene med bilde og skjemaet med bildefeil uten brudd på nivåene «serious» eller «critical» og uten vannrett rulling ved 320 px.
```

- **Story 2.6, nytt akseptansekriterium:** «**Gitt** en innsending med et nytt bilde når sesjonen er utløpt **Når** 401-siden vises **Så** står «Velg bildet på nytt etter innlogging.» over knappen, og `bilde_beholdt` følger med som skjult felt hvis det fantes (AD-7, AD-18).»
- **Story 4.5, tabellen/kriteriene:** bilder på oppdrag som beholdes, slettes. Testen sjekker at `oppdragsbilde` ikke har rader for brukerens beholdte oppdrag etter slettingen.
- **Story 6.1:** bildet med alt-tekst og filfeltet med tastatur og skjermleser er med i T2–T5.

### 4.6 Sprint-status og epic-kontekst

- `sprint-status.yaml`: `2-7-bilde-av-oppdraget: backlog` settes inn før `2-6-…`, med kommentaren `# 2.7 bygges før 2.6 (sprint-change-proposal-2026-11-27)`.
- `epic-2-context.md`: FR-27, AD-18, story 2.7 og at 2.6 må håndtere filfelt.

## 5. Overlevering

**Omfang: moderat.** Planen får et nytt krav og en ny story, men ingen omplanlegging.

| Hvem | Ansvar |
|---|---|
| Utvikler (Claude, bmad-build) | Legger endringene over inn i dokumentene på branchen `endring/bilde-av-oppdrag`, med PR og merge etter grønn CI. Story 2.7 bygges som vanlig story etter 2.5, med egen spec, review og PR. |
| Heidi (produkteier) | Har bestilt endringen og delegert valgene. Kan endre beslutningene i §3 når som helst før 2.7 starter. |

**Suksesskriterier:**
- FR-27 kan spores fra PRD til epics, story 2.7, commits og tester.
- Alle dokumentene i §2 er oppdatert og peker til hverandre.
- Story 2.7 er `done` med grønn CI og deploy, eller kuttet med begrunnelse i PRD §6.1 og endringsloggen.
