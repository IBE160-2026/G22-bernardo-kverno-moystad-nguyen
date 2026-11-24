---
title: 'Story 1.4: Registrere konto'
type: 'feature'
created: '2026-11-24'
baseline_commit: 'ef1dd338874a013025672242e0d8f44c81a344c2'
status: 'in-progress'
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
- [ ] `pyproject.toml`, `uv.lock` -- `tzdata` som avhengighet (`uv add tzdata`) -- AD-9
- [ ] `app/core/feil.py` -- `RegelBrudd(feil: list[tuple[str, str]])` med `.feil` -- AR-26, NFR-10
- [ ] `app/core/tid.py`, `tests/core/test_tid.py` -- `OSLO`, `i_dag()`, `tolk_fodselsdato(tekst, *, i_dag) -> date` (kaster `RegelBrudd` på `fodselsdato` med formatfeil eller «Sjekk fødselsdatoen.»), `fyller_ar(fodselsdato, ar) -> date` (29.02 → 01.03), `er_myndig(fodselsdato, i_dag) -> bool`. Tabelltest for skrivemåter, tosifret år, 29. februar og grensene ved 18 og 120 år -- FR-1, AD-9, AR-19
- [ ] `app/identity/service.py`, `tests/identity/test_registrering_regler.py` -- `normaliser_telefon`, `sjekk_epostformat`, `opprett_sesjon`, `registrer(db, *, navn, epost, passord, telefon, postnummer, fodselsdato) -> str` (gir sesjonsnøkkelen). Samler feil i feltrekkefølge, slår opp e-posten bare når formatet er gyldig, og setter inn i `with db.begin_nested():`, der `IntegrityError` blir e-postfeilen -- FR-1, AD-2, AD-6, AD-17
- [ ] `app/identity/routes.py` -- `@offentlig` GET `identity.registrer` og POST `identity.send_registrer` på `/registrer`. Innloggede sendes til `/`. Ved `RegelBrudd` vises skjemaet med 422, `poststed` for gyldig postnummer og fokus på feiloppsummeringen. Ved suksess følger cookien med, og svaret er 303 til `/` -- FR-1, FR-3, NFR-10
- [ ] `app/identity/templates/identity/registrer.html`, `logg_inn.html`, `app/core/static/css/app.css` -- skjema etter mockupen. Poststedet er `<span id="postnummer-sted">`, knyttet til feltet med `aria-describedby`. Personvernseksjonen har `aria-labelledby`. Høyst ett `autofocus` (navn, eller feiloppsummeringen). Innloggingssiden lenker til registrering -- FR-1, NFR-9, UX-DR12, UX-DR13
- [ ] `app/core/static/js/poststed.js`, `base.html` -- henter `postnumre.json` første gang et `[data-poststed]`-felt endres, og viser poststedet for gyldige fire sifre. Ellers tømmes teksten. Ingen validering -- UX-DR13
- [ ] `tests/identity/test_registrering.py` -- HTTP-tester for radene i I/O-matrisen. Sjekker også felttyper, `autocomplete`, personvernteksten, at alle feilene vises samtidig, at passordet er tomt etter feil, sidetittel, fokus, at kontoen kan logge inn og ut etter registrering, og at `bruker` bare har de tillatte kolonnene (NFR-9) -- FR-1, NFR-5, NFR-9, NFR-10
- [ ] `tests/core/test_tilgang.py`, `tests/identity/test_innlogging.py`, `tests/oppdrag/test_grunnsider.py` -- `/registrer` blir offentlig, og innloggingssiden lenker til den -- FR-3
- [ ] `scripts/roykttest.py`, `tests/test_roykttest.py` -- GET `/registrer` gir 200 med headerne og «Opprett konto» -- AD-14
- [ ] `README.md` -- statustabellen, produksjonsavsnittet, og at testkontoen i produksjon har oppdiktede opplysninger og slettes i story 4.5 -- AR-10

**Manuell oppgave for Heidi (etter merge og grønn deploy):** registrer en testkonto med oppdiktede opplysninger på https://nabolagshelten.vercel.app/registrer, logg ut og inn igjen, og noter resultatet. Ingen verdier skal stå i chatten eller i repoet.

**Acceptance Criteria:**
- Gitt `uv run pytest` mot SQLite og Postgres i CI, så er alt grønt, og FR-3-testen viser at `/registrer` er den eneste nye offentlige ruta.
- Gitt registreringssiden uten JS, så er «Vis passord» skjult, og poststedet vises etter en innsending med feil i et annet felt.
- Gitt produksjonsversjonen etter merge, så røyktestes registrering, innlogging og utlogging manuelt, og resultatet føres i Implementation Notes.

## Implementation Notes

## Spec Change Log

## Review Triage Log

## Design Notes

- **`registrer` i service, ikke gjennom `Autentisering`:** registrering og innlogging ligger begge i `identity`, så ruta kaller servicen direkte. `opprett_sesjon` er felles, så sesjonene blir like (7 dager, bare hashen lagres). `Autentisering` endres ikke.
- **Forhåndssjekk + constraint:** oppslaget gir feilen sammen med de andre feltfeilene. `begin_nested()` rundt insert gjør at to samtidige registreringer gir én rad også på Postgres, uten at transaksjonen blir ubrukelig (AD-17).
- **Tosifret år:** `03.05.54` gir 1954. `03.05.08` gir 2008, og personen avvises som under 18. Det er bedre enn å gjette 1908 (118 år).

## Verification

**Commands:**
- `uv run pytest` -- expected: grønn
- `uv run python scripts/roykttest.py http://127.0.0.1:8000` mot lokal server uten seed -- expected: «Røyktest OK»

**Manual checks (if no CLI):**
- 320 px uten vannrett rulling, cirka fem minutters tastatursjekk av registreringen, og poststed og «Vis passord» med og uten JS.
