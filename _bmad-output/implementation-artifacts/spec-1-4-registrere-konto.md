---
title: 'Story 1.4: Registrere konto'
type: 'feature'
created: '2026-11-24'
baseline_commit: 'ef1dd338874a013025672242e0d8f44c81a344c2'
status: 'in-review'
route: 'dispatch'
review_loop_iteration: 0
story_key: '1-4-registrere-konto'
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-1-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Det finnes ingen måte å lage en konto på. Bare seed-brukere lokalt kan logge inn, og i produksjon kan ingen bruke appen (FR-1).

**Approach:** Offentlig `/registrer` (GET og POST) i `identity` med de seks feltene, personverntekst og «Opprett konto», etter mockupen `key-registrering.html`. Servicen samler alle feltfeil i én `RegelBrudd`, lagrer normalisert e-post og telefon som åtte siffer, og logger inn med en ny sesjon. Fødselsdato tolkes i nye `core/tid.py` (AD-9). Poststed vises med JS fra `postnumre.json`, ellers etter innsending.

## Boundaries & Constraints

**Always:** Feltrekkefølge, etiketter, `type`/`autocomplete`, hjelpetekstene «8–64 tegn» og «dd.mm.åååå, for eksempel 03.05.1954», overskriften «Personvern» med de fem punktene, «Opprett konto» og «Har du konto fra før?» + «Logg inn» ordrett fra mockupen. Feiltekstene står ordrett i EXPERIENCE.md § Feiltekster ved felt. Tekst trimmes og NFC-normaliseres før lengdesjekk, og felt med bare mellomrom er tomme. Passord trimmes ikke (`passord_har_gyldig_lengde`). Alle feil vises samtidig i feltrekkefølge, verdiene beholdes, og passordet tømmes. Når et annet felt har feil, får passordet hjelpeteksten «Skriv passordet på nytt.». «I dag» er datoen i Europe/Oslo via `klokke.na()`. Krav-ID-er står i commits og tester.

**Beslutninger (godkjent av Heidi 2026-11-24):** Specen beholdes hel, selv om den er over grensen på 1 600 tokens. Fødselsdato godtar `.`, `/`, `-` eller mellomrom mellom tallene, dag og måned med ett eller to siffer, og år med to eller fire siffer, som datoene i oppdrag. Tosifret år blir den nyeste datoen som ikke er fram i tid (20xx, ellers 19xx). En dato som ikke finnes (31.02.1990), gir «Sjekk fødselsdatoen.». Grensen for 120 år er i dag minus 120 år. Telefon: mellomrom fjernes, så fjernes `+47` eller `0047` foran, og resten må være åtte siffer. E-post er gyldig med nøyaktig én `@`, tekst før, et domene med punktum og uten mellomrom, høyst 320 tegn. Ruta fanger `RegelBrudd` og viser skjemaet med 422, som innloggingen gjør. Den automatiske røyktesten registrerer ikke kontoer. Den sjekker bare at `/registrer` svarer, og testkontoen i produksjon lages manuelt.

**Never:** ny migrering (`bruker` og `uq_bruker_epost` finnes fra 0001), «om meg», adresse, logging av e-post, telefon eller passord, `|safe`, regler i JS, eller en egen vei rundt `Autentisering` for innlogging andre steder enn i `identity`.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Gyldig | `" Kari@X.no "`, `"+47 912 34 567"`, `0571`, `03.05.1954` | rad med `kari@x.no`, `91234567`, hash; sesjonscookie; 303 til `/` | – |
| Navn | 1 og 80 tegn / 0, bare mellomrom, 81 | godtas / «Skriv navnet ditt.», «Navnet kan ha høyst 80 tegn.» | 422 |
| Passord | 8 og 64 / tomt, 7, 65 | godtas / «Skriv et passord.», «Passordet må ha 8–64 tegn.» | 422 |
| Telefon | `91234567`, `912 34 567`, `+47 912 34 567`, `0047 91234567` / `9123456`, `+46 91234567`, `912-34-567` | godtas / formatfeilen fra EXPERIENCE.md | 422 |
| Postnummer | `0571` / `9999`, postboksnummer, `57` | godtas, poststed vises / «Finner ikke postnummeret. Sjekk at det har fire siffer.» | 422 |
| Alder (`sett_na`) | fyller 18 i dag / i morgen; født 29.02.2008, i dag 28.02 og 01.03.2026 | godtas / «Du må være minst 18 år …»; avvist 28.02, godtatt 01.03 | 422 |
| Dato | fram i tid, i dag minus 120 år minus én dag / `3.5.54`, `03-05-1954` / `1954.05.03`, `abc` | «Sjekk fødselsdatoen.» / godtas (1954) / formatfeilen | 422 |
| E-post i bruk | `KARI@x.no` finnes som `kari@x.no` | «Det finnes allerede en konto med denne e-posten.» | 422, ingen ny rad |
| Samtidig | forhåndssjekken passeres, to inserts | én rad, den andre får e-postfeilen | `IntegrityError` i `begin_nested()` blir `RegelBrudd` |
| Flere feil | tomt navn + e-post i bruk + under 18 | «Skjemaet har 3 feil», verdier beholdt, passord tomt | 422, «Feil: Registrering – Nabolagshelten» |
| Innlogget | GET `/registrer` med sesjon | 303 til `/` | – |

</frozen-after-approval>

## Code Map

- `app/identity/service.py` -- `normaliser_epost`, `hash_passord`, `passord_har_gyldig_lengde`, `MAKS_EPOST`, `_finn_aktiv_bruker`. Trekk ut sesjonsopprettingen i `logg_inn` (l. 184–198) til `opprett_sesjon(db, bruker_id, gammel_nokkel=None) -> str`, og bruk den fra både `logg_inn` og `registrer`. Sletting av forsøk gjelder bare `logg_inn`.
- `app/identity/routes.py` -- mønsteret `_vis_skjema` + 422, `trygg_neste`, `sett_sesjonscookie(..., secure=settings.produksjon)`, `with db.begin():`. `vis_logg_inn` sender innloggede til `/`.
- `app/identity/templates/identity/logg_inn.html` -- mal for felt, feltfeil, `aria-describedby` og «Vis passord» (`data-vis-passord`). Fjern kommentaren «Ingen lenke til registrering før story 1.4», og legg til en lenke nederst.
- `app/core/feil.py` -- `RegelBrudd` legges til her (docstringen l. 11 sier det).
- `app/core/postnummer.py` -- `normaliser_postnummer`, `finnes`, `poststed`. Skal ikke endres.
- `app/core/klokke.py` -- `na()`. `tests/conftest.py` -- `sett_na`, `lag_bruker`, `db`.
- `app/core/static/js/vis_passord.js` -- virker allerede for alle `[data-vis-passord]`. `base.html` l. 9–10 laster skriptene.
- `app/core/static/postnumre.json` -- `{nummer: poststed}`.
- `tests/core/test_tilgang.py:22` `OFFENTLIGE`, `tests/identity/test_innlogging.py:307` og `tests/oppdrag/test_grunnsider.py:80` -- forventer i dag at registrering ikke finnes. Oppdateres.
- `scripts/roykttest.py:_sjekk` + `tests/test_roykttest.py` -- legg til GET `/registrer`.
- `README.md` l. 24 (status) og l. 30 (produksjon: «registrering kommer i story 1.4»).
- `pyproject.toml`/`uv.lock` -- `tzdata` finnes bare for win32 (gjennom psycopg). Legg den til som direkte avhengighet, så `zoneinfo` virker på Vercel.

## Tasks & Acceptance

**Execution:**
- [x] `pyproject.toml`, `uv.lock` -- `tzdata` som avhengighet (`uv add tzdata`) -- AD-9
- [x] `app/core/feil.py` -- `RegelBrudd(feil: list[tuple[str, str]])` med `.feil` -- AR-26, NFR-10
- [x] `app/core/tid.py`, `tests/core/test_tid.py` -- `OSLO`, `i_dag()`, `tolk_fodselsdato(tekst, *, i_dag) -> date` (kaster `RegelBrudd` på `fodselsdato` med formatfeil eller «Sjekk fødselsdatoen.»), `fyller_ar(fodselsdato, ar) -> date` (29.02 → 01.03), `er_myndig(fodselsdato, i_dag) -> bool`. Tabelltest for skrivemåter, tosifret år, 29. februar og grensene ved 18 og 120 år -- FR-1, AD-9, AR-19
- [x] `app/identity/service.py`, `tests/identity/test_registrering_regler.py` -- `normaliser_telefon`, `sjekk_epostformat`, `opprett_sesjon`, `registrer(db, *, navn, epost, passord, telefon, postnummer, fodselsdato) -> str` (gir sesjonsnøkkelen). Samler feil i feltrekkefølge, slår opp e-posten bare når formatet er gyldig, og setter inn i `with db.begin_nested():`, der `IntegrityError` blir e-postfeilen -- FR-1, AD-2, AD-6, AD-17
- [x] `app/identity/routes.py` -- `@offentlig` GET `identity.registrer` og POST `identity.send_registrer` på `/registrer`. Innloggede sendes til `/`. Ved `RegelBrudd` vises skjemaet med 422, `poststed` for gyldig postnummer og fokus på feiloppsummeringen. Ved suksess følger cookien med, og svaret er 303 til `/` -- FR-1, FR-3, NFR-10
- [x] `app/identity/templates/identity/registrer.html`, `logg_inn.html`, `app/core/static/css/app.css` -- skjema etter mockupen. Poststedet er `<span id="postnummer-sted">`, knyttet til feltet med `aria-describedby`. Personvernseksjonen har `aria-labelledby`. Høyst ett `autofocus` (navn, eller feiloppsummeringen). Innloggingssiden lenker til registrering -- FR-1, NFR-9, UX-DR12, UX-DR13
- [x] `app/core/static/js/poststed.js`, `base.html` -- henter `postnumre.json` første gang et `[data-poststed]`-felt endres, og viser poststedet for gyldige fire sifre. Ellers tømmes teksten. Ingen validering -- UX-DR13
- [x] `tests/identity/test_registrering.py` -- HTTP-tester for radene i I/O-matrisen. Sjekker også felttyper, `autocomplete`, personvernteksten, at alle feilene vises samtidig, at passordet er tomt etter feil, sidetittel, fokus, at kontoen kan logge inn og ut etter registrering, og at `bruker` bare har de tillatte kolonnene (NFR-9) -- FR-1, NFR-5, NFR-9, NFR-10
- [x] `tests/core/test_tilgang.py`, `tests/identity/test_innlogging.py`, `tests/oppdrag/test_grunnsider.py` -- `/registrer` blir offentlig, og innloggingssiden lenker til den -- FR-3
- [x] `scripts/roykttest.py`, `tests/test_roykttest.py` -- GET `/registrer` gir 200 med headerne og «Opprett konto» -- AD-14
- [x] `README.md` -- statustabellen, produksjonsavsnittet, og at testkontoen i produksjon har oppdiktede opplysninger og slettes i story 4.5 -- AR-10

**Manuell oppgave for Heidi (etter merge og grønn deploy):** registrer en testkonto med oppdiktede opplysninger på https://nabolagshelten.vercel.app/registrer, logg ut og inn igjen, og noter resultatet. Ingen verdier skal stå i chatten eller i repoet.

**Acceptance Criteria:**
- Gitt `uv run pytest` mot SQLite og Postgres i CI, så er alt grønt, og FR-3-testen viser at `/registrer` er den eneste nye offentlige ruta.
- Gitt registreringssiden uten JS, så er «Vis passord» skjult, og poststedet vises etter en innsending med feil i et annet felt.
- Gitt produksjonsversjonen etter merge, så røyktestes registrering, innlogging og utlogging manuelt, og resultatet føres i Implementation Notes.

## Implementation Notes

- 2026-11-24 (implementasjon): alle oppgavene under Execution er gjort. `uv run pytest` gir 477 grønne mot SQLite. Postgres er ikke kjørt lokalt (Docker kjørte ikke) og sjekkes av CI.
- Lokal røyktest mot `uvicorn` uten seed: eneste avvik er «cookien csrf mangler Secure», som før story 1.4, fordi `Secure` bare settes når `APP_ENV=production`. `tests/test_roykttest.py` forventer det samme avviket. Registrering, utlogging og innlogging mot den lokale serveren gikk gjennom (303 hver gang).
- Valg som specen ikke låser: kontrolltegn i navn blir mellomrom (NUL gir ellers `DataError` i Postgres). Fødselsdato krever samme skilletegn begge steder. Lenketeksten på innloggingssiden er «Har du ikke konto?» + «Registrer deg». Ved feil i et annet felt står «Skriv passordet på nytt.» i tillegg til «8–64 tegn».
- Manuell røyktest i produksjon (registrering, innlogging, utlogging) står igjen til etter merge og deploy.

## Spec Change Log

## Review Triage Log

Runde 1 (2026-11-24). B = blind, K = kanttilfeller, V = verifikasjonshull. Patch = rettes i denne runden.

| # | Funn | Verdikt | Begrunnelse | Rute |
|---|------|---------|-------------|------|
| B1 | Innlogget bruker kan lage en konto til med POST `/registrer` | low | Stemmer: bare GET sendte til `/`, og en test låste oppførselen. Specen sier «Innloggede sendes til `/`» for ruta. Retting: POST sender også til `/` uten å lage konto | patch (med K3, K6) |
| B2 | Ingen grense for registreringer, og «e-post i bruk» avslører kontoer | false | Arkitekturen sier «Grense for antall registreringer: Ikke i v1». Feilteksten for e-post i bruk er et krav i FR-1 og EXPERIENCE.md | avvist |
| B3 | Usynlige tegn (Cf, for eksempel U+200B og U+202E) slipper gjennom i navn | low | Stemmer, men ingen møter det i vanlig bruk. Å fjerne alle Cf-tegn ødelegger ZWJ/ZWNJ i ekte navn, så rettingen krever en ny regel | avvist (med K2) |
| B4 | Personvernteksten lover sletting av konto og «Få forslag», som ikke finnes ennå | low | Stemmer til story 4.5 og 5.1. Teksten er låst ordrett i intensjonen (FR-1). README advarer nå mot ekte opplysninger i produksjon (B6) | avvist (rettingen ville endret specen) |
| B5 | Personvernteksten mangler behandlingsansvarlig, formål, lagringssted og lagringstid | low | Teksten er ordrett fra den godkjente mockupen og FR-1. En endring hører hjemme i planleggingsdokumentene | avvist (rettingen ville endret specen) |
| B6 | README ber folk registrere seg i produksjon uten å si at de skal bruke oppdiktede opplysninger | low | Stemmer, og rettingen er én setning | patch |
| B7 | Skjermlesere får ikke vite at poststedet vises | medium | Stemmer: `#postnummer-sted` endres uten sidelasting, og EXPERIENCE.md § Fokus og opplesning bruker `aria-live` for slike endringer. Universell utforming sensureres | patch |
| B8 | `poststed.js` har ingen automatiske tester og lastes på alle sider | medium | Testdelen: samme som V3. At skriptet lastes overalt, koster bare én liten fil og et `querySelectorAll` uten treff (negligible) | defer (med V3) |
| B9 | Røyktesten sender aldri POST `/registrer` | low | CSRF bak proxyen er vist med innloggingen, og `core/tid.py` importeres ved oppstart, så GET `/registrer` viser at tzdata virker. Ny sjekk er mer enn en direkte retting | avvist |
| B10 | E-postsjekken godtar `kari@x..no` og `kari@-x.no` | low | Stemmer, men følger regelen som er besluttet i specen (én `@`, tekst før, domene med punktum). Brukeren logger inn med samme skrivemåte | avvist |
| B11 | `tzdata>=2026.6` uten øvre grense, og diffen manglet `uv.lock` | false | tzdata har kalenderversjoner, og nyere tidssonedata er alltid ønsket. `uv.lock` er committet på branchen og ble bare holdt utenfor reviewdiffen | avvist |
| B12 | Testen for logging tar ikke med navn og fødselsdato | low | Stemmer, og rettingen er to ekstra sjekker og en docstring | patch |
| B13 | Slettede kontoer teller som «e-post i bruk» | false | AD-8: en slettet bruker blir en gravstein der alle personfelt er NULL, også `epost`. Unik-constrainten ville uansett stoppet en ny rad med samme e-post | avvist |
| K1 | Alle `IntegrityError` vises som «e-post i bruk» | false | Den eneste andre constrainten som kan slå til, er fremmednøkkelen på `postnummer`, og den er sjekket før med `finnes()` mot de samme dataene som migrering 0001 lastet | avvist |
| K2 | Navn med bare Cf-tegn | low | Samme som B3 | avvist (med B3) |
| K3 | Innlogget POST med feil viser skjemaet med menyen | low | Samme rot som B1 | patch (med B1) |
| K4 | Doble mellomrom eller NBSP i fødselsdato gir formatfeil | low | Stemmer, men sjelden, og brukeren får eksemplet og skriver på nytt. Rettingen er ny normalisering | avvist |
| K5 | `poststed.js` oppdaterer ikke etter autofyll eller gjenoppretting uten `input`-hendelse | low | Nettlesere sender `input` ved autofyll. Sidene har `no-store`, så gjenoppretting fra bfcache er lite sannsynlig. Etter innsending viser serveren poststedet | avvist |
| K6 | Påstand: «Innloggede sendes til `/`» gjelder bare GET | low | Samme som B1 | patch (med B1) |
| V1 | Ingen test for `Secure` på sesjonscookien fra registreringen i produksjon | gap | Arkivert evidens: bare innloggingen testes i produksjon (`test_innlogging.py:84`) | patch |
| V2 | Ingen test viser at Europe/Oslo finnes uten tidssonedata fra systemet | gap | Arkivert evidens: CI på Ubuntu har tidssonedata, så en fjernet tzdata ville først blitt oppdaget på Vercel | patch |
| V3 | `poststed.js` kjøres aldri i en test | gap | Arkivert evidens: repoet har ingen JS- eller nettlesertester ennå. Playwright kommer i story 1.5 | defer (med B8) |

## Design Notes

- **`registrer` i service, ikke gjennom `Autentisering`:** registrering og innlogging ligger begge i `identity`, så ruta kaller servicen direkte. `opprett_sesjon` er felles, så sesjonene blir like (7 dager, bare hashen lagres). `Autentisering` endres ikke.
- **Forhåndssjekk + constraint:** oppslaget gir feilen sammen med de andre feltfeilene. `begin_nested()` rundt insert gjør at to samtidige registreringer gir én rad også på Postgres, uten at transaksjonen blir ubrukelig (AD-17).
- **Tosifret år:** `03.05.54` gir 1954. `03.05.08` gir 2008, og personen avvises som under 18. Det er bedre enn å gjette 1908 (118 år).

## Verification

**Commands:**
- `uv run pytest` -- expected: grønn
- `uv run python scripts/roykttest.py http://127.0.0.1:8000` mot lokal server uten seed -- expected: bare avviket «cookien csrf mangler Secure» (Secure settes bare i produksjon, som siden story 1.3)

**Manual checks (if no CLI):**
- 320 px uten vannrett rulling, cirka fem minutters tastatursjekk av registreringen, og poststed og «Vis passord» med og uten JS.
