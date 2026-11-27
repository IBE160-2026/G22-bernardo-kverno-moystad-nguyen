---
title: 'Story 2.1: Legge ut oppdrag'
type: 'feature'
created: '2026-11-26'
status: 'done'
baseline_commit: '1bc8c844bd12776a88b27b6a81c3082d2ee5bd22'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-2-context.md'
  - '{project-root}/_bmad-output/planning-artifacts/ux-designs/ux-G22-bernardo-kverno-moystad-nguyen-2026-11-07/EXPERIENCE.md'
  - '{project-root}/_bmad-output/planning-artifacts/ux-designs/ux-G22-bernardo-kverno-moystad-nguyen-2026-11-07/mockups/key-nytt-oppdrag.html'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Ingen kan legge ut et oppdrag. Tabellen `oppdrag`, statusfunksjonen, tolkningen av oppdragstid og eksempeloppdragene mangler, og Epic 2–4 bygger på dem (FR-5, AR-12, AR-19, AR-20, NFR-2).

**Approach:** «Nytt oppdrag» på én skjerm (`/oppdrag/ny`) i `oppdrag`, med alle feltfeil samlet i én `RegelBrudd`, `skjema_id` mot dobbel innsending og PRG til detaljsiden med kvitteringen «Oppdraget er lagt ut.». Ny migrering 0003, `core/domene.py`, tidstolkning og visningsfiltre i `core/tid.py`, statusfunksjonen i `oppdrag/service.py`, eksempeloppdrag i seed og en generisk tømming i `last_eksempeldata` (retro T-3).

**Beslutninger (anbefalt alternativ, delegert av Heidi 2026-11-26):**
- «Mine oppdrag» før 2.4: tomtilstanden med lenken «Legg ut oppdrag» vises bare når brukeren ikke har oppdrag. Ellers vises en enkel `ul` med tittelen som lenke til detaljene, nyeste først. Oversikten beholder tomtilstanden til 2.3.
- Klokkeslett som ikke finnes ved overgang til sommertid gir «Klokkeslettet finnes ikke den natten, fordi klokka stilles fram. Velg et annet klokkeslett.» ved feltet Klokkeslett. Teksten føres inn i EXPERIENCE.md § Feiltekster ved felt.
- Specen beholdes samlet (cirka 5 500 tokens), fordi storyen er ett mål.

## Boundaries & Constraints

**Always:** Etiketter, hjelpetekster og feiltekster står ordrett i EXPERIENCE.md (§ Skjemafelt, § Feiltekster ved felt, § Formater). Beskrivelsesfeltet har etiketten «Hva trenger du hjelp til?» og hjelpetekstene «Skriv med egne ord.» og «Ikke skriv adresse eller telefonnummer – det avtaler dere når hjelperen er valgt.» (mockup og EXPERIENCE). Feltrekkefølgen er beskrivelse, tittel, kategori, postnummer, dato, klokkeslett, tilbud, beløp. Tekst trimmes og NFC-normaliseres før `len()`, og felt med bare mellomrom regnes som tomme. Ingen `maxlength` på tekstfelt. Kategorien lagres som kode og vises bare med `kategori_tekst`. Tid lagres med `UtcDateTime`, og «nå» er `klokke.na()`. POST kjører `with db.begin():`, og service committer aldri. Undersider har menyvalget med `aria-current="true"`: «Mine oppdrag» på skjemaet og på eget oppdrag, «Oppdrag» på andres. Krav-ID-er står i commits og tester.

**Never:** KI («Få forslag», Epic 5), to steg, forhåndsvisning eller skjuling av «Beløp i kr» med CSS (2.2), lista i oversikten (2.3), faner, merker og menytall (2.4), redigering, avbryting og `Konflikt`-handler (2.5), oppdragsgiverblokk og `erfaring` (2.3). Ingen adresse i modellen, `|safe`, regler i JS, `ON DELETE CASCADE` eller statusendring utenom `endre_status`.

## I/O & Edge-Case Matrix

Klokka står fast på tirsdag 24.11.2026 kl. 13:00 norsk tid (`sett_na`).

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Gyldig | alle felt, `25.11.2026` `7`, beløp `1000` | rad med `apen`, kode, UTC 06:00Z, `belop=1000`; 303 til `/oppdrag/{id}`; «I morgen kl. 07:00», «1 000 kr», «Åpen» | – |
| Uten betaling | tilbud `uten`, beløp `50` | `belop` NULL, «Uten betaling» | beløp ignoreres |
| Lengder | tittel 3/80, beskrivelse 10/1000 / tittel 2/81, beskrivelse 9/1001, bare mellomrom | godtas / tekstene fra EXPERIENCE (1001 gir «… Nå har den 1001.») | 422 |
| Beløp | `1`, `10 000` / `0`, `10001`, `1,5`, `abc`, tomt | godtas / «Skriv et beløp fra 1 til 10 000 kr, i hele kroner.» | 422 |
| Valg mangler | ingen kategori, ingen tilbud, ukjent kode | «Velg en kategori.» / «Velg beløp eller uten betaling.» | 422 |
| Skrivemåter | `14.11.2026`, `14/11/26`, `14-11-2026`, `14 11 2026`; `07:00`, `7`, `0700`, `7.00` | samme tidspunkt | – |
| Passert / for langt | tidspunkt = nå; nå + 12 mnd + 1 min | «Velg et nytt tidspunkt fram i tid» / «Velg et tidspunkt høyst 12 måneder fram i tid.» under «Når?» | 422 |
| Sommertid | 28.03.2027 02:30 / 31.10.2027 02:30 | «Klokkeslettet finnes ikke den natten, fordi klokka stilles fram. Velg et annet klokkeslett.» ved Klokkeslett / 00:30Z (første) | 422 / – |
| Mange feil | tom innsending (postnummeret er forhåndsutfylt) | «Skjemaet har 6 feil», `Feil: Nytt oppdrag – Nabolagshelten`, verdier og `skjema_id` beholdt, ingen rad | 422 |
| Dobbel innsending | samme `skjema_id` to ganger | én rad; andre svar 303 til samme oppdrag uten kvittering | `IntegrityError` i `begin_nested()` → `Duplikat` |
| Ugyldig `skjema_id` | mangler eller ikke `[A-Za-z0-9_-]{16,64}` | feilsiden med 400, ingen rad | – |
| XSS | `<script>alert(1)</script>` i tittel og beskrivelse | vises escaped på detaljene | – |
| Detaljer, tilgang | finnes ikke / annens `avbrutt` / annens `apen` | 404 / 404 (samme side) / 200 med menyvalget «Oppdrag» | `FinnesIkke`, `IngenTilgang` |
| Invariant 1.5 (T-6) | `POST /_test/tilstand seed=1` | testbrukerne og eksempeloppdragene, ingen sesjoner eller forsøk; `opprettet` følger den faste klokka; ruta finnes bare i `test` | – |
| Invariant 1.5 (T-6) | `uv run python -m app.seed` to ganger | samme seks brukere, ingen andre brukere røres; testbrukernes oppdrag byttes ut, 10–15 totalt | – |
| Invariant 1.2 (T-6) | `/`, `/mine-oppdrag`, `/profil` | menyen i fast rekkefølge med én `aria-current="page"`; én `h1`; «Hopp til innholdet» først; høyst ett `autofocus`; ingen lenke til `/registrer` eller postnummerfilter; oversikten har fortsatt tomtilstanden | – |
| Invariant T1 (T-6) | alle sider i `SIDER` fra Epic 1 | fortsatt uten «serious»/«critical» og uten vannrett rulling ved 320 px | – |

</frozen-after-approval>

## Code Map

- `app/core/feil.py` -- `RegelBrudd`, `FinnesIkke`, `IngenTilgang`, `feilside(request, 400)`, `registrer_feilhandlere` (l. 205). Legg til `Duplikat(til_url)` med handler (303) og klassen `Konflikt(melding, til_url)` uten handler (docstringen l. 13 sier at de kommer nå).
- `app/core/render.py` -- `render(..., aktiv_meny, fokus)` (l. 374), `MENYVALG`, `fokusmal`, `miljo` (l. 324). Filtrene registreres på `miljo.filters`. Ny parameter `underside: bool = False` legges i konteksten (StrictUndefined krever en standardverdi).
- `app/core/templates/core/makroer.html` -- `meldinger()` (l. 20) lenker til `#{{ felt }}`. Gi den `lenker={}` som kobler gruppefelt til første input (`nar`→`dato`, `kategori`→første radio, `tilbud`→`tilbud-belop`). `_menyvalg` (l. 57) skriver `aria-current="true"` når `underside` er sann. CSS-en bruker allerede `[aria-current]`.
- `app/core/templates/core/base.html` -- skriptene l. 9–11. Legg til `skjema.js` og favicon (R8).
- `app/core/kvittering.py` -- `TEKSTER` (l. 19). Legg til `"oppdrag_lagt_ut": "Oppdraget er lagt ut."`.
- `app/core/tid.py` -- `OSLO`, `i_dag()`, `fyller_ar()`, `_DATO` (samme skilletegn). Oppdragstiden legges til her. `tolk_fodselsdato` skal ikke endres.
- `app/core/postnummer.py` -- `normaliser_postnummer`, `finnes`, `poststed`. Skal ikke endres.
- `app/identity/service.py` -- `_tekst` (l. 233) er mønsteret for NFC og trim. `SKRIV_POSTNUMMER`/`POSTNUMMER_UKJENT` (l. 70–71) importeres. `hent_offentlig_bruker` (l. 461) gir postnummeret til forhåndsutfyllingen. `registrer` (l. 284) er mønsteret for feilsamling og `begin_nested`.
- `app/identity/routes.py` -- `_vis_registrering` + 422 er mønsteret for `_vis_skjema` med `verdier`, `feil` og `feltfeil`. `request.state.skjema` er `dict[str, str]`.
- `app/identity/templates/identity/registrer.html` -- makroene `beskrevet_av`/`ugyldig` og postnummerfeltet med `data-poststed`/`data-postnumre` (`poststed.js` virker uendret).
- `app/oppdrag/routes.py` -- `oversikt` (l. 23) og `mine_oppdrag` (l. 42). Nye ruter legges her.
- `app/seed.py` -- `TESTBRUKERE`, `legg_inn_testbrukere`, `last_eksempeldata` (l. 88, håndskrevet liste), `main` (l. 102).
- `migrations/env.py` l. 14 og `tests/core/test_migrering.py` l. 19 -- importerer bare `app.identity.models`. Uten `app.oppdrag.models` blir `compare_metadata` avhengig av testrekkefølgen.
- `tests/conftest.py` -- `lag_bruker`, `logg_inn_som`, `sett_na`, `db`. Docstringen (l. 11) lover `lag_oppdrag` i 2.1.
- `tests/oppdrag/test_grunnsider.py` -- l. 48 (`aria-current` bare `page`/ingen), l. 75–87 (ingen «Legg ut oppdrag», hrefs-mengden) og l. 67 (tomtilstand) må oppdateres.
- `tests/test_seed_og_admin.py` l. 54 og l. 149, `tests/core/test_testtilstand.py` l. 33 -- invariantene fra 1.5.
- `tests/e2e/conftest.py` -- `tilstand`, `FAST_KLOKKE` (24.11.2026 12:00Z), `logg_inn_som_kari`, `bruker_id`. `tests/e2e/test_t1.py` `SIDER` (l. 101).
- `tests/core/test_arkitektur.py` -- importretning, forbudte mønstre, ASCII-identifikatorer og rutenavn `<slice>.<handling>`. Skal ikke endres.

## Tasks & Acceptance

**Execution:**
- [x] `app/core/domene.py` (ny) -- `KATEGORIER` som ordnet tuppel av `(kode, tekst)`: `snomaking` Snømåking, `hage` Hage, `baerehjelp-flytting` Bærehjelp/flytting, `dyrepass` Dyrepass, `teknologihjelp` Teknologihjelp, `annet` Annet. `STATUSER` med `apen` Åpen, `hjelper_valgt` Hjelper valgt, `utfort` Utført, `avbrutt` Avbrutt. `TITTEL_MIN=3`, `TITTEL_MAKS=80`, `BESKRIVELSE_MIN=10`, `BESKRIVELSE_MAKS=1000`. Funksjonene `kategori_tekst` og `status_tekst` -- AD-10, AR-20
- [x] `app/core/tid.py`, `tests/core/test_tid.py` -- `tolk_tidspunkt(dato, klokkeslett, *, na) -> datetime` (aware UTC) kaster én `RegelBrudd` med feil på `dato`, `klokkeslett` eller `nar`. `vis_tidspunkt(dt)` gir «I dag kl. 07:00», «I morgen kl. 07:00» eller «Lørdag 14. nov. kl. 12:00», med år når det ikke er inneværende år. Tabelltest for skrivemåtene, tosifret år (20xx), grensene, sommertid og rundturen (tolkes før skiftet, vises før og etter med samme dato og klokkeslett) -- FR-5, AD-9, AR-19
- [x] `app/core/feil.py`, `app/core/kvittering.py`, `app/core/render.py`, `app/core/templates/core/makroer.html` -- `Duplikat` med handler og `Konflikt`, kvitteringen, filtrene `tidspunkt`, `kr`, `kategori_tekst` og `status_tekst`, parameteren `underside` og `meldinger(lenker)`. Test av filtrene i `tests/core/test_render.py` -- AD-2, AD-10, UX-DR22, UX-DR29
- [x] `app/oppdrag/models.py` (ny), `migrations/versions/0003_oppdrag.py`, `migrations/env.py`, `tests/core/test_migrering.py` -- `Oppdrag`: `id`, `oppdragsgiver_id` (FK `bruker`, indeks), `tittel` String(80), `beskrivelse` String(1000), `kategori` String(30), `postnummer` (FK), `tidspunkt` (`UtcDateTime`, indeks), `belop` Integer NULL, `status` String(20), `valgt_hjelper_id` (FK `bruker`, NULL), `versjon` (1), `skjema_id` String(64) unik, `opprettet`, `vesentlig_endret` NULL. CHECK `ck_oppdrag_status`, `ck_oppdrag_kategori` og `ck_oppdrag_belop` (NULL eller 1–10 000). Ingen CASCADE. Testen sjekker kolonnene (ingen adresse), at `skjema_id` er unik og at CHECK avviser i begge databasene -- AD-2, AD-13, AR-12, NFR-9
- [x] `app/oppdrag/service.py` (ny), `tests/oppdrag/test_status.py` -- `endre_status(db, oppdrag_id, *, fra, til, oppdragsgiver_id=None, ikke_passert=False)`: én betinget `UPDATE … SET status, versjon = versjon + 1 WHERE id, status IN fra [, eier] [, tidspunkt > na]`. En overgang som ikke står i `OVERGANGER`, gir `ValueError`. Ved 0 rader leses raden på nytt: finnes ikke eller feil eier gir `FinnesIkke`, ellers `Konflikt("Oppdraget er endret. Last siden på nytt.", til_url)`. Test av alle tre utfallene -- AD-2, AR-12
- [x] `app/oppdrag/service.py`, `tests/oppdrag/test_legge_ut_regler.py` -- `opprett_oppdrag(db, *, oppdragsgiver_id, beskrivelse, tittel, kategori, postnummer, dato, klokkeslett, tilbud, belop, skjema_id) -> int` samler feilene i feltrekkefølge og setter inn i `begin_nested()`. Ved `IntegrityError` slås `skjema_id` opp, og funnet rad gir `Duplikat(detaljer_url(id))`. `hent_for_visning(db, oppdrag_id, bruker_id) -> OppdragVisning` (uten personfelt) gir `FinnesIkke` eller `IngenTilgang` etter FR-9. Enhetstester for I/O-radene -- FR-5, FR-9, NFR-5, NFR-10, AD-16
- [x] `app/oppdrag/routes.py`, `app/oppdrag/templates/oppdrag/ny.html`, `detaljer.html`, `oversikt.html`, `mine.html` -- GET `oppdrag.ny` og POST `oppdrag.send_ny` på `/oppdrag/ny`, og GET `oppdrag.detaljer` på `/oppdrag/{id:int}`. Skjemaet har `novalidate`, ny `skjema_id` (`secrets.token_urlsafe(16)`) ved GET, «Tilbake» og «Publiser». Ved suksess: 303 til detaljene med kvitteringen. Detaljene har `h1` med tittelen, statusmerke med skjult «Status: », kategorimerke, tidspunkt, «0571 Oslo», beløp og beskrivelse. På oversikten står «+ Legg ut oppdrag» (primær, før `h1`, «+» med `aria-hidden`). «Mine oppdrag» viser tomtilstanden bare uten oppdrag, ellers `ul` med titler som lenker, nyeste først (se Beslutninger) -- FR-5, FR-9, UX-DR10, UX-DR11, UX-DR12, UX-DR14
- [x] `app/core/static/js/skjema.js` (ny), `app/core/static/css/app.css`, `app/core/static/favicon.svg` (ny), `base.html` -- telleren «37 av 1000 tegn» (kodepunkter etter NFC og trim, `data-maks`). Serveren skriver startverdien, og en skjult `aria-live`-node får tekst bare når grensen nås. CSS for kategoriknappene (`label:has(:checked)` med 3 px kant, hake og fet tekst), «Når?», statusmerke, kategorimerke, `.skjult-tekst` og `white-space: pre-line` på beskrivelsen. `<link rel="icon">` til en SVG laget av logoen -- AD-10, AR-28, UX-DR11, UX-DR13, R8
- [x] `app/seed.py`, `tests/test_seed_og_admin.py` -- `last_eksempeldata` tømmer alle tabeller i `reversed(Base.metadata.sorted_tables)` unntatt `postnummer` (T-3), og legger så inn testbrukerne og `EKSEMPELOPPDRAG`. `main` bytter bare ut testbrukernes oppdrag. 12 oppdrag med tidspunkter relativt til `klokke.na()` og hele klokkeslett mellom kl. 09 og 18 i norsk tid. Bare Kari, Nora og Sofie eier oppdrag, og minst ett av Noras ligger i 0571. Alle seks kategorier finnes blant de åpne. Minst ett er utgått, og minst ett er avbrutt gjennom `endre_status`. Tester: kravene i NFR-2, at fremmede rader i hver tabell forsvinner, og at hver tabell i databasen (unntatt `alembic_version`) finnes i `Base.metadata` når `app.seed` er importert -- NFR-2, AR-29, T-3
- [x] `tests/conftest.py` -- fabrikken `lag_oppdrag(**felt)` med gyldige standardverdier (i morgen, 0571, `apen`), committer sin egen SAVEPOINT som `lag_bruker` -- AR-29
- [x] `tests/oppdrag/test_legge_ut.py`, `tests/oppdrag/test_grunnsider.py` -- HTTP-tester for I/O-matrisen og skjemaet: etiketter, `fieldset`/`legend`, `autocomplete="off"`, ingen `inputmode` på dato og klokkeslett, ingen `maxlength`, `aria-describedby`/`aria-invalid`, forhåndsutfylt postnummer, menyen med `"true"` og ingen `"page"`, kvitteringen med `autofocus`, ingen telefon, e-post eller fødselsdato i HTML-en fra detaljene. Oppdater invariantene fra 1.2 -- FR-5, FR-9, NFR-5, NFR-10, NFR-12, AD-16
- [x] `tests/e2e/test_t1.py`, `tests/e2e/conftest.py`, `tests/e2e/test_klientatferd.py` -- en generell `logg_inn_som(page, testbruker)`. Nye sider i `SIDER`: `nytt-oppdrag`, `nytt-oppdrag-feil`, `oppdrag-detaljer` (publisert gjennom skjemaet, med kvittering) og `mine-oppdrag-tom` (Ola). Klienttester for telleren (`é` som e+◌́ teller 1) og for dobbeltklikk på «Publiser» (én rad i E2E-databasen, knappen har `aria-disabled`) -- NFR-6, NFR-7, UX-DR13, UX-DR28, SM-5
- [x] `_bmad-output/planning-artifacts/ux-designs/ux-G22-bernardo-kverno-moystad-nguyen-2026-11-07/EXPERIENCE.md` -- sommertidsteksten føres inn i § Feiltekster ved felt -- FR-5, AD-9
- [x] `README.md` -- seed-avsnittet (l. 49) beskriver eksempeloppdragene, og statusen oppdateres -- NFR-2

**Acceptance Criteria:**
- Gitt en innlogget bruker på oversikten, når hen trykker «+ Legg ut oppdrag», så vises «Nytt oppdrag» med alle feltene i rekkefølge, postnummeret fra profilen med poststed, og «Mine oppdrag» med `aria-current="true"`.
- Gitt gyldige verdier, når brukeren trykker «Publiser», så havner hen på detaljene med «Oppdraget er lagt ut.» i fokus, og tittelen er `<title>`.
- Gitt Beskrivelse, når brukeren skriver, så oppdateres telleren uten at hvert tegn leses opp, og ved 1000 tegn leses «1000 av 1000 tegn» opp.
- Gitt eksempeldataene, når `uv run python -m app.seed` kjøres, så finnes 10–15 oppdrag som oppfyller NFR-2 for denne storyen, og README beskriver dem.

## Implementation Notes

## Spec Change Log

## Review Triage Log

Pass 1 (2026-11-27). Lag: Blind Hunter (BH), Edge Case Hunter (EC), Verification Gap (VG).

| # | Lag | Funn | Verdict | Begrunnelse | Rute |
|---|---|---|---|---|---|
| 1 | EC | Datoen `01.01.0001` kl. `00:00` gir `OverflowError` i `finnes_i_oslo` og 500 | medium | Bekreftet av reviewer lokalt: `astimezone` ved `datetime.min` | patch |
| 2 | EC | Beløp med over 4 300 sifre gir `ValueError` i `int()` og 500 | low | Bare ved en konstruert POST. Retten er én lengdesjekk | patch |
| 3 | VG | Fjerningen av NUL i `normaliser_tekst` er ikke testet | medium | Forhåndsverifisert gap. Uten test kan en regresjon gi 500 på Postgres | patch |
| 4 | BH | CHECK-lista i 0003 er hardkodet, og `compare_metadata` sammenligner ikke CHECK, så en ny kategori i `domene.py` uten migrering gir `IntegrityError` i produksjon | medium | Alembic autogenerate ser ikke CHECK-constraints. Ingen test fanger glippen | patch (test) |
| 5 | BH | Radioknappene for kategori og tilbud får aldri `aria-invalid` | low | Riktig. Gjelder alle som får feil i gruppen med skjermleser. Retten er direkte | patch |
| 6 | BH | Telleren oppdateres bare ved `input`, så verdien er feil etter gjenoppretting fra bfcache | low | Riktig. Retten er direkte (kjør ved start og `pageshow`) | patch |
| 7 | BH | `ikke_passert=True` gir `Konflikt` med «Oppdraget er endret» når tidspunktet bare er passert | medium | Ingen rute kaller `endre_status` med `ikke_passert` ennå. Rammer Epic 3 (melde interesse, velge hjelper) | defer |
| 8 | BH | `bytt_ut_eksempeloppdrag` sletter uten å tømme barnetabeller og får FK-feil når Epic 3 legger til `interesse` | medium | Riktig for framtiden. Ingen barnetabell finnes nå | defer |
| 9 | BH | `Konflikt` har ingen handler | false | Specen utsetter handleren til 2.5 (Never), og ingen rute kaster `Konflikt` | avvist |
| 10 | BH, EC | Valgt kategori vises bare med `:has()` | low | `:has()` støttes i alle nettlesere som er i bruk i 2026 (Firefox fra 121, Safari fra 15.4) | avvist |
| 11 | BH, EC | Grensen på 12 måneder blir én time feil når den havner i hullet ved sommertid | low | Skjer bare noen minutter i året, og avviket er én time | avvist |
| 12 | EC | «Tilbake» går til `/` etter 422 | low | `/` er en rimelig reserve, og det vanligste utgangspunktet er oversikten | avvist |
| 13 | BH, EC | `trim()` i JS og `strip()` i Python er ulike for sjeldne tegn | low | Bare med konstruert tekst. Serveren avgjør uansett | avvist |
| 14 | BH | Usynlige tegn (U+200B) teller med i lengdereglene | low | Bare med konstruert tekst. Retten ville lagt til en ny normaliseringsregel | avvist |
| 15 | BH | Beløp uten valgt «Beløp» gir feil | false | Valgt design (EXPERIENCE, og CSS-skjulingen kommer i 2.2). Feilteksten sier hva som må gjøres | avvist |
| 16 | BH | Duplikat gir ingen kvittering | false | Matrisen i den låste intent-blokken sier «uten kvittering» | avvist |
| 17 | BH | Utgåtte og avbrutte oppdrag skilles ikke fra åpne i de midlertidige visningene | false | Merkene er utenfor storyen i Never (2.4), og avbrutt viser statusmerket på detaljene | avvist |
| 18 | BH | I går vises som ukedag | low | Utgått-merket i 2.4 gjør det tydelig. Kosmetisk nå | avvist |

## Design Notes

- **Valg som ikke merkes av brukeren:** «Fram i tid» betyr `> na`. «12 måneder» er samme dato og klokkeslett i norsk tid om ett år (`fyller_ar` for 29.02), og selve grensen godtas. Klokkeslett er `H`, `HH`, `H:MM`, `HH:MM`, `H.MM` eller `HHMM`, med timer 0–23 og minutter 0–59. Dato bruker `_DATO`. Beløp: mellomrom (også NBSP) fjernes, og resten må være ASCII-sifre. `kr` bruker NBSP som tusenskille og før «kr». Månedene forkortes jan., feb., mars, apr., mai, juni, juli, aug., sep., okt., nov., des. Ukedagen skrives med stor forbokstav.
- **Gruppefeil:** `nar`, `kategori` og `tilbud` har egne nøkler i `feltfeil`, slik at feilen står under `fieldset`. Lenken i oppsummeringen går til første input i gruppen (`meldinger(lenker=…)`), og gruppefeilen knyttes til begge tidsfeltene med `aria-describedby`.
- **Duplikat:** `detaljer_url(id)` i `service.py` gir `/oppdrag/{id}`, og en test sjekker at den er lik `app.url_path_for("oppdrag.detaljer", id=…)`. Valideringen kjører før innsettingen, så en ny innsending med feil viser feilene. Ved en `skjema_id` som tilhører en annen bruker, sender `Duplikat` brukeren dit, og tilgangsregelen avgjør hva hen får se.
- **Detaljene for andre:** FR-9 gjelder allerede: andre innloggede ser åpne oppdrag med de samme feltene. 2.3 legger til oppdragsgiverblokken. «Tilbake» bruker `tilbake_url`, men peker den på `/oppdrag/ny`, brukes «Mine oppdrag».
- **Seed `main` mot `last_eksempeldata`:** `main` beholder invarianten fra 1.5 om at ingen andre brukere røres, men sletter og legger inn testbrukernes oppdrag på nytt, så tidspunktene alltid er relative til innlastingen. `last_eksempeldata` (bare for test) tømmer alt.
- **`skjema.js`** inneholder bare telleren nå. `poststed.js` og `vis_passord.js` flyttes ikke i denne storyen.

## Verification

**Commands:**
- `uv run pytest` -- forventet: alle tester grønne, også `test_arkitektur.py`, `test_modellene_og_migreringene_stemmer` og de oppdaterte testene for 1.2 og 1.5. CI kjører de samme testene mot Postgres.
- `uv run pytest -m e2e` -- forventet: T1 er grønn for alle sidene i `SIDER`, både de gamle og de fire nye (axe ved 360 og 1280 px, ingen vannrett rulling ved 320 px), og klienttestene er grønne.

**Manual checks (if no CLI):**
- [ ] Tastatursjekk av «Nytt oppdrag» og detaljene i cirka fem minutter (DoD). **Utsatt til story 6.1** (T-5): den autonome kjøringen har ingen manuell tester, og T1 med axe dekker de automatiske kravene. Storyen kan settes `done` med denne utsettelsen.
