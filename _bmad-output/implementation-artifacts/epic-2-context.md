# Epic 2 Context: Legge ut og finne oppdrag

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Epic 2 gjør Nabolagshelten til en markedsplass: oppdragsgiveren (Kari) kan legge ut, redigere og avbryte oppdrag og finne dem igjen under «Mine oppdrag», og hjelperen (Amir) finner åpne oppdrag i sitt postnummer, filtrerer på kategori og postnummer og åpner detaljene. Epicen bygger på skjelettet, innloggingen og menyen fra Epic 1. Den legger grunnlaget (oppdragsmodellen, statusfunksjonen, tidstolkning og dialogkomponenten) som Epic 3 og 4 bygger videre på. Epic 2 skal være ferdig torsdag 3. desember. Hvis ikke, kuttes Epic 5 (KI).

## Stories

- Story 2.1: Legge ut oppdrag
- Story 2.2: Nytt oppdrag i to steg på mobil, med forhåndsvisning
- Story 2.3: Finne oppdrag i oversikten og se detaljene
- Story 2.4: Se egne oppdrag under «Mine oppdrag»
- Story 2.5: Redigere og avbryte oppdrag
- Story 2.6: Utfylt skjema går ikke tapt når innloggingen utløper (kan kuttes)

## Requirements & Constraints

- **Legge ut (FR-5):** tittel 3–80 tegn, beskrivelse 10–1000 tegn (etter trim og NFC, og felt med bare mellomrom regnes som tomme), kategori fra den faste lista (Snømåking, Hage, Bærehjelp/flytting, Dyrepass, Teknologihjelp, Annet), postnummer forhåndsutfylt fra profilen, tidspunkt fram i tid og høyst 12 måneder fram, godtgjørelse som heltall 1–10 000 kr eller «Uten betaling» (lagres som NULL). Alle felt er påkrevd. Lagret oppdrag får status Åpen. Hjelpeteksten om å ikke skrive adresse eller telefon skal stå på skjemaet.
- **Redigere (FR-6):** bare oppdragsgiveren, bare ved Åpen, med samme validering. Et passert tidspunkt må endres. Ingen KI ved redigering. Endres tidspunkt, godtgjørelse eller postnummer, settes `vesentlig_endret`.
- **Avbryte (FR-7):** bare oppdragsgiveren, fra Åpen (og Hjelper valgt, som testes i Epic 3), og handlingen må bekreftes. Etterpå kan oppdraget ikke endres.
- **Utgått (FR-8):** et åpent oppdrag med passert tidspunkt vises ikke i oversikten, får merket «Tidspunktet er passert» under «Mine oppdrag» og kan endres eller avbrytes. Med nytt tidspunkt vises det igjen.
- **Detaljer (FR-9):** åpne oppdrag kan ses av alle innloggede. Andre statuser kan bare ses av oppdragsgiveren og valgt hjelper. Andre får samme 404 som for et oppdrag som ikke finnes.
- **Oversikt og filter (FR-10, FR-11):** viser åpne oppdrag som ikke er passert, i brukerens postnummer, uten brukerens egne. Sortering etter tidspunkt og deretter etter når oppdraget ble lagt ut, eldste først. Kategori og et annet postnummer kan kombineres. Et ukjent postnummer gir melding ved feltet, og lista står uendret.
- **Mine oppdrag, grunnversjon (FR-18):** bare «Oppdrag jeg har lagt ut» med status, tidspunkt og merket «Tidspunktet er passert». Menytallet teller foreløpig bare utgåtte oppdrag og vises ikke ved 0.
- **Definition of Done for hver story:** hver regel testes direkte mot serveren, også dobbel innsending (NFR-5). Ugyldig input gir forståelige meldinger ved feltet, alle feil vises samtidig, og alt utfylt beholdes (NFR-10). Tekst vises alltid som tekst (XSS-test, NFR-12). Nye sider er med i T1 (axe, ingen «serious» eller «critical», ingen vannrett rulling ved 320 px). Siden sjekkes med tastatur i cirka fem minutter. Seed dekker det nye (10–15 oppdrag, alle kategorier, minst ett utgått og ett avbrutt). Én Alembic-migrering hvis skjemaet endres. Krav-ID-er står i commits og tester.
- **Personvern:** ingen HTML fra oversikten eller detaljene inneholder telefon, e-post eller fødselsdato (FR-16, AD-16). Adresse lagres aldri.

## Technical Decisions

- **Slice:** all kode for oppdrag ligger i `app/oppdrag` (`routes.py`, `service.py`, `models.py`, `templates/oppdrag/`). Importene går bare mot `identity`, `ki` og `core`. `oppdrag` eier tabellene `oppdrag`, `interesse`, `tidligere_hjelper` og `tilbakemelding`.
- **Status (AD-2):** verdiene er `apen`, `hjelper_valgt`, `utfort` og `avbrutt`. All endring av status går gjennom én funksjon i `oppdrag/service.py`. Andre statusavhengige skrivinger (som redigering) starter med `UPDATE oppdrag SET versjon = versjon + 1 WHERE id, status, eier, (tidspunkt > :na)`. 0 rader gir `FinnesIkke` eller `Konflikt`. SQLite bruker `BEGIN IMMEDIATE`, og «database is locked» blir `Konflikt`. Testen med samtidige forespørsler kjøres mot både SQLite og Postgres.
- **Dobbel innsending:** et skjult `skjema_id` med unik-constraint. `IntegrityError` fanges med SAVEPOINT og gir `Duplikat`, som sender brukeren til oppdraget som finnes.
- **Avledet tilstand (AD-3):** utgått, merker og menytall beregnes ved lesing fra status, tidspunkt og `klokke.na()`, med én funksjon hver i `oppdrag/service.py`. Ingenting lagres, og det finnes ingen cron. Testes med `sett_na` på begge sider av tidspunktet. «Meldt før endring» betyr `interesse.opprettet < oppdrag.vesentlig_endret`.
- **Menykroken:** `oppdrag` kobler inn kroken `(db, bruker_id) -> int` i `lag_app()`.
- **Tid (AD-9):** `UtcDateTime` lagrer UTC. `core/tid.py` eier tolkning og visning: dato i formatene `14.11.2026`, `14/11/26`, `14-11-2026` og `14 11 2026`, klokkeslett i formatene `07:00`, `7`, `0700` og `7.00`, og tosifret år betyr 20xx. Et klokkeslett som ikke finnes ved sommertid, avvises, og et som finnes to ganger, tolkes som det første. En tabelltest dekker skrivemåtene og rundturen over skiftene. Visningen skjer med filtrene `tidspunkt` og `kr`.
- **Tekst og domene (AD-10):** `core/domene.py` har `KATEGORIER` (ASCII-koder), statusord og grensene. Kategorien lagres som kode og vises bare med `kategori_tekst`. Grensen sendes som `data-maks`, og felt med teller har ikke `maxlength`.
- **Postnummer:** bare gjennom `core/postnummer.py` (`normaliser_postnummer`, `finnes`, `poststed`). Klienten slår opp poststed i `postnumre.json`.
- **Feil og PRG:** `RegelBrudd` gir 422, og skjemaet vises på nytt. `Konflikt` gir redirect med «Oppdraget er endret. Last siden på nytt.». Etter en vellykket handling går POST via redirect til GET med kvittering i en signert cookie. Skjemamodellene har bare `str | None`. POST-ruter kjører `with db.begin():`, og services kaller aldri commit.
- **URL-er:** `/` (oversikt med `?kategori=&postnummer=`), `/oppdrag/ny`, `/oppdrag/{id:int}`, `/oppdrag/{id:int}/rediger`, `/oppdrag/{id:int}/<handling>` (GET viser bekreftelsessiden, POST utfører) og `/mine-oppdrag`. Rutenavnene er `oppdrag.<handling>`, og malene bruker `url_for`. Én hjelper bygger filterlenkene og beholder de andre parametrene.
- **Klient (AR-28):** én JS-fil per oppgave i `core/static/js/`: `skjema.js` (teller, poststed, forhåndsvisning), `steg.js` (to steg under 768 px), `fokus.js`, `dialog.js` og `sending.js`. JS har aldri regler, og alt virker uten JS.
- **Utløpt innlogging (AD-7, story 2.6):** en POST uten sesjon gir en 401-side med feltene som skjulte felt (unntatt passord og CSRF) og innloggingsfelt. Etter innlogging behandles den opprinnelige innsendingen. Ingen andre skjemafelt begynner med `_`.

## UX & Interaction Patterns

- **Skjema:** synlige etiketter, `aria-describedby` og `aria-invalid`, `novalidate`, en feiloppsummering med lenker til feltene (uten `role`), og telleren «37 av 1000 tegn», som bare leses opp ved grensen. Kategorien er en radiogruppe (`fieldset`/`legend`, `label:has(:checked)`). «Når?» er en `fieldset` med to tekstfelt, uten kalender og uten `inputmode="numeric"`. «Beløp i kr» vises med CSS `:has(:checked)`.
- **To steg under 768 px:** «Nytt oppdrag 1 av 2» og «2 av 2», med `<title>` per steg og fokus på `h1` ved bytte. Ved serverfeil vises steget med den første feilen. Fra 768 px, og uten JS, står alt på én skjerm med to `h2`. Forhåndsvisningen «Slik vises oppdraget for andre» har stiplet kant, ingen lenke og «–» for tomme felt, og leses ikke opp.
- **Oversikt:** hele kortet er én lenke, i 1, 2 eller 3 kolonner. Kategorilenkene har `aria-current="true"`, hake og fet tekst, og fokus står på valgt kategori etter sidelasting. Antallslinja er knyttet til lenken med `aria-describedby`. Tomtilstander har én vei videre.
- **Detaljer:** innholdet avhenger av rolle og status. Andre ser oppdragsgiverblokken «Lagt ut av …» med erfaring, men oppdragsgiveren ser den ikke. Menyvalget som markeres, avhenger av rollen («Oppdrag» eller «Mine oppdrag»).
- **Mine oppdrag:** lenkerader med tittel, statusmerke, tidspunkt og ›. Snarveiene «Endre tidspunkt» og «Avbryt oppdrag» står som knapper under en skillelinje, utenfor lenken.
- **Dialog:** native `<dialog>` med `showModal()`. Fokus går til spørsmålet, Tab holdes inne, og Esc gir fokus tilbake til knappen. Angre-valget heter aldri «Avbryt». Uten JS vises en GET-bekreftelsesside.
- **Fokus og sending:** høyst ett `autofocus` per side, i rekkefølgen feiloppsummering > feilmelding > kvittering > sidens eget mål. Knappen som sendte, får `aria-disabled` til svaret kommer.
- **Mikrotekst:** formatene «I morgen kl. 07:00», «Lørdag 14. nov. kl. 12:00», «1 000 kr» og «Uten betaling», og postnummer vises alltid med poststed. Tekstene i EXPERIENCE.md gjelder ordrett.

## Cross-Story Dependencies

- Epic 1 må være ferdig (skjelett, `Autentisering`, `core.render`, meny, CSRF og T1-oppsett).
- 2.1 legger grunnlaget for de andre (modell, migrering, statusfunksjon, `core/tid.py`, seed). 2.2 og 2.5 gjenbruker skjemaet fra 2.1. 2.5 legger til snarveiene i radene fra 2.4 og innfører `dialog.js`, som Epic 3 og 4 gjenbruker.
- 2.2 og 2.6 kuttes først hvis Epic 1 ikke er ferdig 28. november. Kuttes 2.6, står den enkle 401-siden fra story 1.2 igjen, og kuttet føres i PRD-en.
- Fram mot Epic 3 og 4: «Meldt før endring», avbrudd fra Hjelper valgt, hjelper-fanen, de andre merkene og snittet i oppdragsgiverblokken (foreløpig «Ingen vurderinger ennå») kommer senere. `erfaring()` og `vesentlig_endret` bør derfor finnes allerede nå.
