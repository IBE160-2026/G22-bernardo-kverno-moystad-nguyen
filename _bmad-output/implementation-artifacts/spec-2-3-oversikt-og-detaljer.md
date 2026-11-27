---
title: 'Story 2.3: Finne oppdrag i oversikten og se detaljene'
type: 'feature'
created: '2026-11-27'
status: 'done'
baseline_commit: '5c8a4e88cf0b5623b78c0ce588572a4a67f7b411'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-2-context.md'
  - '{project-root}/_bmad-output/planning-artifacts/ux-designs/ux-G22-bernardo-kverno-moystad-nguyen-2026-11-07/EXPERIENCE.md'
  - '{project-root}/_bmad-output/planning-artifacts/ux-designs/ux-G22-bernardo-kverno-moystad-nguyen-2026-11-07/mockups/key-oversikt.html'
  - '{project-root}/_bmad-output/planning-artifacts/ux-designs/ux-G22-bernardo-kverno-moystad-nguyen-2026-11-07/mockups/key-detaljer.html'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Oversikten viser bare overskriften og en tomtilstand, så en hjelper finner ingen oppdrag. Detaljene for andres oppdrag mangler oppdragsgiverblokken, og en ny bruker som registrerer seg fra en delt lenke, havner på `/` i stedet for på lenken (FR-9, FR-10, FR-11, retro R3).

**Approach:** Oversikten lister åpne oppdrag som ikke er passert, i brukerens postnummer og uten egne oppdrag, som kort med lenke. Filtrene er GET-parametre (`kategori`, `postnummer`), og én hjelper bygger lenkene. Detaljene får `brukerkort` med `erfaring()` for alle andre enn oppdragsgiveren. `Innlogget` får `postnummer` (R7), og `neste` bæres gjennom registreringen (T-2). Ingen migrering. Bilder kommer i 2.7.

**Beslutninger (anbefalt alternativ, delegert av Heidi 2026-11-26):**
- Ukjent eller tomt postnummer i filteret gir bare feilen ved feltet: feltet får fokus, og `<title>` har «Feil: » foran. Det blir ingen feiloppsummering etter `h1` (EXPERIENCE § Filtrene). Lista står rett under, og feltet med fokus leser opp feilen.
- Specen beholdes samlet (cirka 6 000 tokens), fordi storyen er ett mål.

## Boundaries & Constraints

**Always:** Tekstene er ordrett fra EXPERIENCE.md: `h1` «Ledige oppdrag i 0571 Oslo», antallslinja «4 ledige oppdrag i 0571 Oslo» / «1 ledig oppdrag i 0571 Oslo» / «2 ledige oppdrag i Hage i 0571 Oslo», `<title>` «Ledige oppdrag i 0571 Oslo – Nabolagshelten» og med kategori «Hage – Ledige oppdrag i 0571 Oslo – Nabolagshelten», etiketten «Kategori», «Alle», etiketten «Postnummer», knappen «Vis», feltfeilene «Skriv postnummeret.» og «Finner ikke postnummeret. Sjekk at det har fire siffer.», tomtilstandene «Ingen ledige oppdrag i 0571 Oslo akkurat nå.» med «Prøv en annen kategori eller et annet postnummer.» og «Vis alle kategorier», eller «Prøv et annet postnummer.» og «Velg et annet postnummer», og i detaljene «Lagt ut av …», «Ingen vurderinger ennå» og «Se profil». Postnummer vises alltid med poststed. «Utgått» (tidspunkt ≤ `klokke.na()`) har én funksjon i `oppdrag/service.py` (AD-3). Malene får bare `OppdragKort`, `OppdragVisning`, `OffentligBruker` og `Erfaring` (AD-16). Tid, beløp, kategori og vurdering formateres bare med filtrene. Høyst ett `autofocus` per side. Krav-ID-er står i commits og tester.

**Never:** bilder på kortet og i detaljene (2.7), «Meld interesse», interessertlista og telefonboksen (Epic 3), «Rediger» og «Avbryt oppdrag» (2.5), snitt fra tilbakemeldinger (Epic 4), sidenummerering, kart eller avstand, endring av tilgangsregelen i `hent_for_visning`, av `opprett_oppdrag`, `steg.js`, `skjema.js` eller grenen `forhandsvisning=True` i `oppdragskort`, endring av `trygg_neste` og `tilbake_url` (retro S3 er egen oppgave), regler i JS, `innerHTML`, `|safe`, `aria-live` på antallslinja, ny tabell og migrering.

## I/O & Edge-Case Matrix

Klokka står fast på tirsdag 24.11.2026 kl. 13:00 norsk tid (`FAST_KLOKKE`). «Ola» bor i 0571 og ser i seed fire oppdrag: Karis «Måke snø i innkjørselen», Noras «Mate katten i helgen», Karis «Raking av løv i hagen» og «Hjelp med nytt nettbrett».

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Eget postnummer | Ola, GET `/` | `h1`, antallslinja og `<title>` for 0571, fire kort i rekkefølgen over. Ikke vist: egne, Karis utgåtte og avbrutte, og 0572. «Alle» har `aria-current="true"` uten `autofocus`, og siden har ingen `autofocus` | – |
| Sortering | to oppdrag med samme tidspunkt | det som ble lagt ut først, står først (så `id`) | – |
| Grensen for passert | `sett_na` lik tidspunktet / 1 s før | ikke vist / vist | – |
| Kort | ett oppdrag | `<li>` med kategorimerke, `h2` med én lenke til `/oppdrag/{id}` der navnet er tittelen, «I morgen kl. 09:00», «0571 Oslo» og «200 kr» eller «Uten betaling». Ingen andre lenker eller knapper i kortet | – |
| Kategori | `?kategori=hage` | bare Hage, «1 ledig oppdrag i Hage i 0571 Oslo», tittelen med «Hage – » foran. Lenken «Hage» har `aria-current="true"`, `autofocus` og `aria-describedby` til antallslinja, og ingen annen lenke har `aria-current` | – |
| «Alle» | `?kategori=alle`, eller ukjent kode `?kategori=xyz` | alle kategorier, og «Alle» har `aria-current="true"` og `autofocus` | ukjent kode regnes som «Alle» |
| Annet postnummer | «Vis»/Enter med `5006` mens Hage er valgt | `?postnummer=5006&kategori=hage&vist_postnummer=0571`: `h1` «Ledige oppdrag i 5006 Bergen», Hage beholdes, og postnummerfeltet har `autofocus` og `aria-describedby` til antallslinja. Kategorilenkene beholder `postnummer=5006` | – |
| Ukjent postnummer | `9999`, `abc`, 3 000 tegn / tomt felt, med `vist_postnummer=5006` | 200. Lista, `h1` og antallslinja for 5006 står uendret. Feltet har den skrevne verdien, `aria-invalid`, «Finner ikke postnummeret. Sjekk at det har fire siffer.» / «Skriv postnummeret.» og `autofocus`. `<title>` har «Feil: » foran | uten gyldig `vist_postnummer` brukes eget postnummer |
| Tom, kategori valgt | Kari, `?kategori=hage` | ingen antallslinje. «Ingen ledige oppdrag i 0571 Oslo akkurat nå.», «Prøv en annen kategori eller et annet postnummer.» og «Vis alle kategorier» (`?kategori=alle`, beholder postnummeret). «Hage» har `aria-describedby` til den første setningen | – |
| Tom, «Alle» | `?postnummer=` med et gyldig postnummer uten oppdrag | «Prøv et annet postnummer.» og lenken «Velg et annet postnummer» til `#postnummer`. Med JS får feltet fokus med innholdet markert, og uten JS hopper siden til feltet | – |
| Detaljer, annen bruker | Ola åpner Noras åpne oppdrag | alle feltene, «Åpen», blokken «Lagt ut av Nora Berg» med «1 fullført oppdrag · Ingen vurderinger ennå» og «Se profil» til `/profil/{id}`. «Oppdrag» har `aria-current="true"`, og «har meldt interesse» står ikke på siden | – |
| Detaljer, eier | Kari åpner sitt eget | ingen oppdragsgiverblokk, og «Mine oppdrag» har `aria-current="true"` | – |
| Annen status | en annen åpner `hjelper_valgt`, `utfort` eller `avbrutt` | samme 404-side som `/oppdrag/999999`. Valgt hjelper og eier får 200 | `IngenTilgang` |
| XSS | `<script>alert(1)</script>` i tittel og i navnet til oppdragsgiveren | vises som tekst på kortet og i blokken | – |
| Personvern | HTML fra oversikten og fra detaljene for eier og andre | ingen telefonnummer, e-post eller fødselsdato til testbrukerne | – |
| `neste` gjennom registrering (T-2) | utlogget GET `/oppdrag/5` → «Registrer deg» → gyldig POST | «Registrer deg» har `?neste=%2Foppdrag%2F5`, `/registrer` har `neste` som skjult felt også etter 422, og vellykket registrering gir 303 til `trygg_neste(neste)` = `/oppdrag/5`. «Logg inn» på registreringen bærer `neste` tilbake | `//evil.no`, `https://evil.no` og `/logg-ut` gir `/` |
| `Innlogget` (R7) | innlogget forespørsel | `Innlogget.postnummer` er brukerens postnummer fra samme spørring, og oversikten kaller ikke `hent_offentlig_bruker` | – |
| Invariant 1.2/1.4 (T-6) | innlogging med `neste`, og registrering etter mislykkede forsøk | innloggingen sender fortsatt til `trygg_neste(neste)`, registreringen sletter `innloggingsforsok` for e-posten, og en innlogget GET eller POST til `/registrer` gir 303 til `/` | – |
| Invariant 2.1/2.2 (T-6) | «Publiser», og HTML fra «Nytt oppdrag» | 303 til detaljene med «Oppdraget er lagt ut.» i fokus. Forhåndsvisningen og stegene er uendret, og `test_to_steg.py` er grønn | – |
| Invariant FR-3 (T-6) | utlogget GET `/?kategori=hage` | 303 til `/logg-inn?neste=/%3Fkategori%3Dhage` eller tilsvarende, og etter innlogging tilbake til filteret | – |
| Invariant T1 (T-6) | alle sider i `SIDER` | fortsatt uten «serious»/«critical» og uten vannrett rulling ved 320 px | – |

</frozen-after-approval>

## Code Map

- `app/oppdrag/routes.py` -- `oversikt` (l. 75–91) slår opp `hent_offentlig_bruker` bare for postnummeret (R7). `ny` (l. 219–230) gjør det samme. `detaljer` (l. 275–294) og `_tilbake_fra_detaljer` (l. 267) beholdes. Docstringen l. 18 sier at lista kommer i 2.3.
- `app/oppdrag/service.py` -- `hent_for_visning` (l. 260–286) har tilgangsregelen fra FR-9, som ikke endres. `OppdragVisning` (l. 231–249) mangler `oppdragsgiver_id`. `endre_status` (l. 102–103) definerer ikke passert som `tidspunkt > klokke.na()`. Den nye funksjonen for utgått må gi det samme.
- `app/oppdrag/models.py` -- `tidspunkt` har indeks (l. 49), `valgt_hjelper_id` (l. 52) og `opprettet` (l. 55). Alt som trengs, finnes. Ingen migrering.
- `app/oppdrag/templates/oppdrag/oversikt.html` -- har bare «+ Legg ut oppdrag» før `h1` (beholdes) og tomtilstanden.
- `app/oppdrag/templates/oppdrag/detaljer.html` -- felt, merker og beskrivelse (l. 26–41). Blokken legges etter beskrivelsen.
- `app/core/templates/core/makroer.html` -- `oppdragskort` (l. 111–133) har `h2` uten lenke (l. 118–120). `kategoriikon` (l. 74), `kategorimerke` (l. 87), `meldinger` (l. 21) og `feltfeil` (l. 9). `brukerkort` finnes ikke ennå.
- `app/core/render.py` -- globalene og filtrene (l. 71–76) har ingen filterhjelper og ingen `vurdering`. `_kontekst` (l. 113) setter «Feil: » bare når `feil` ikke er tom, og `meldinger()` lager da en oppsummering. `fokusmal` (l. 104) og `sidetittel` (l. 79).
- `app/core/sesjon.py` -- `Innlogget` (l. 33–36). `trygg_neste` (l. 130) endres ikke.
- `app/identity/service.py` -- `finn_innlogget` (l. 408–424) henter `Sesjon.bruker_id` og `Bruker.navn`. `OffentligBruker` og `hent_offentlig_bruker` (l. 433–473). `SKRIV_POSTNUMMER` og `POSTNUMMER_UKJENT` brukes allerede av `oppdrag/service.py` (l. 30).
- `app/identity/routes.py` -- `send_registrer` sender til `/` (l. 171). `REGISTRERINGSFELT` (l. 120) går som `**verdier` til `registrer`, så `neste` må holdes utenfor. `_vis_registrering` (l. 123).
- `app/identity/templates/identity/logg_inn.html` -- skjult `neste` (l. 11) og «Registrer deg» uten `neste` (l. 38). I `registrer.html` står skjemaet på l. 15 og «Logg inn» nederst.
- `app/core/postnummer.py` -- `normaliser_postnummer` (l. 83), `finnes` (l. 93) og `poststed` (l. 99).
- `app/core/domene.py` -- `KATEGORIER` og `KATEGORIKODER` (l. 16–24). `Erfaring` legges her (AD-3).
- `app/core/static/js/` -- `fokus.js` finnes ikke. `poststed.js` kobles på med `data-poststed` og `data-postnumre`. Skriptene står i `base.html` (l. 10–13).
- `app/core/static/css/app.css` -- `.kort` (l. 1011–1036), `.kategoriknapp` med `:has(:checked)` (l. 798–845), `.tomtilstand` (l. 711) og `--spacing-content-max` (l. 103).
- `app/seed.py` -- `EKSEMPELOPPDRAG` (l. 90–127) har ingen utførte oppdrag, så alle får «Ingen fullførte oppdrag ennå».
- `app/profil/routes.py` -- `profil.vis` (l. 39) er målet for «Se profil».
- `tests/oppdrag/test_grunnsider.py` -- `test_oversikten_har_overskrift_og_tomtilstand` (l. 61) og `test_ingen_lenker_til_funksjoner_som_ikke_finnes` (l. 112), som forbyr «Postnummer</label>», «Velg et annet postnummer» og andre lenker på `/`.
- `tests/oppdrag/test_legge_ut.py` -- 404-likheten (l. 418), menyen (l. 430) og `test_detaljene_har_ingen_personopplysninger` (l. 449), som krever at «Kari Nordmann» ikke står på siden (l. 463).
- `tests/conftest.py` -- `sett_na` (l. 129), `lag_bruker` (l. 143), `logg_inn_som` (l. 171) og `lag_oppdrag` (l. 193).
- `tests/e2e/test_t1.py` -- `oversikt` (l. 71) logger inn Kari og venter tomtilstanden, men Kari ser nå Noras «Mate katten i helgen». `SIDER` (l. 181).
- `tests/e2e/conftest.py` -- `_logg_inn` (l. 141) venter `h1` med «Ledige oppdrag i». Se også `OLA` (l. 52) og `FAST_KLOKKE` (l. 49).
- `tests/identity/test_innlogging.py` -- testene av `neste` (l. 100 og 106). `tests/identity/test_registrering.py` -- innlogget sendes til `/` (l. 192 og 248).
- `_bmad-output/planning-artifacts/architecture/architecture-G22-bernardo-kverno-moystad-nguyen-2026-11-08/ARCHITECTURE-SPINE.md` -- l. 102 sier `Innlogget` (`bruker_id`, `visningsnavn`).

## Tasks & Acceptance

**Execution:**
- [x] `app/core/sesjon.py`, `app/identity/service.py` -- `Innlogget` får `postnummer: str | None`, og `finn_innlogget` henter `Bruker.postnummer` i samme spørring -- R7, AD-4
- [x] `app/core/domene.py`, `app/oppdrag/service.py` -- `Erfaring(fullforte, per_kategori, snitt, antall_vurderinger)`. Én funksjon for utgått, som både spørringen og 2.4 bruker. `ledige_oppdrag(db, *, postnummer, kategori, bruker_id) -> list[OppdragKort]` (åpne, ikke passert, ikke egne, sortert etter `tidspunkt`, `opprettet` og `id`). `erfaring(db, bruker_ids) -> dict[int, Erfaring]`: utførte oppdrag der brukeren er valgt hjelper, per kategori, med `snitt=None` og `antall_vurderinger=0` til Epic 4. `OppdragVisning` får `oppdragsgiver_id` -- FR-8, FR-10, FR-11, FR-21, AR-13, AD-3
- [x] `app/core/render.py` -- Jinja-globalen `filterlenke(**endringer)` lager en relativ `/?…` fra den gjeldende spørringen. Den beholder de andre parametrene, utelater `None` og fjerner alltid `vist_postnummer`. Filteret `vurdering(erfaring)` gir «4,3 av 5, 7 vurderinger» eller «Ingen vurderinger ennå» -- AR-27, FR-11, FR-21
- [x] `app/oppdrag/routes.py` -- `oversikt` leser `kategori`, `postnummer` og `vist_postnummer` fra spørringen og validerer postnummeret med `core/postnummer.py` og tekstene fra identity. Den velger fokusmål og lager `h1`, `<title>` og antallslinja (se Design Notes). `detaljer` gir `OffentligBruker` og `Erfaring` for oppdragsgiveren når brukeren ikke er eier. `ny` bruker `innlogget.postnummer` -- FR-9, FR-10, FR-11, UX-DR24, UX-DR25
- [x] `app/core/templates/core/makroer.html`, `app/oppdrag/templates/oppdrag/oversikt.html`, `detaljer.html` -- `oppdragskort(..., href=None)`: med `href` står lenken i `h2`, og grenen med forhåndsvisning er uendret. `brukerkort(bruker, erfaring, lenke=True)`. Oversikten får kategorigruppen (`role="group"`, «Kategori», lenker med ikon og hake), postnummerskjemaet (GET, `#postnummer` med poststed, skjult `kategori` og `vist_postnummer`, og «Vis»), antallslinja, kortlista `<ul>` og tomtilstandene -- UX-DR5, UX-DR8, UX-DR21, UX-DR24, UX-DR25
- [x] `app/core/static/js/fokus.js` (ny), `base.html` -- et klikk på `[data-velg-felt]` gir feltet fokus og kaller `select()`. Står fokus på `<body>` etter lasting, får `[autofocus]` fokus. Ingen regler -- AR-28, UX-DR21
- [x] `app/core/static/css/app.css` -- kortlista i 1, 2 og 3 kolonner (fra 48em og 80em, maks `--spacing-content-max`), og lenken i kortet dekker kortet med `::after`. Hover gir en kant på 2 px i `--color-primary`, og fokus gir kanten og ringen på `::after`. `.kategoriknapp[aria-current="true"]` ser ut som `:checked`. Kategoriene brytes over flere linjer, og raden med postnummer og «Vis» brytes ved 320 px -- UX-DR5, UX-DR8, DESIGN.md § card og § category-button
- [x] `app/identity/routes.py`, `logg_inn.html`, `registrer.html` -- «Registrer deg» bærer `neste` når den ikke er `/`. `vis_registrer` leser `neste` med `trygg_neste`, og skjemaet har den som skjult felt, også ved 422. `send_registrer` sender til `trygg_neste(neste)`. «Logg inn» på registreringen bærer `neste` tilbake -- FR-1, FR-2, AD-4, retro T-2
- [x] `app/seed.py`, `README.md` -- et 13. eksempeloppdrag: Karis, med passert tidspunkt og status `utfort` og Nora som valgt hjelper (gjennom `endre_status` apen → hjelper_valgt → utfort). Da viser blokken på Noras oppdrag «1 fullført oppdrag». README får ny tabell, antallet, statuslinja (l. 24) og l. 86 -- NFR-2, FR-9
- [x] `_bmad-output/planning-artifacts/epics.md`, `ARCHITECTURE-SPINE.md` -- akseptansekriteriet fra T-2 legges inn i § Story 2.3, og AD-4 nevner `postnummer` i `Innlogget` -- planleggingsdokumentene holdes oppdatert
- [x] `tests/oppdrag/test_oversikt_regler.py` (ny), `tests/oppdrag/test_oversikt.py` (ny), `tests/oppdrag/test_grunnsider.py`, `tests/oppdrag/test_legge_ut.py`, `tests/core/test_render.py`, `tests/identity/test_registrering.py`, `tests/test_seed_og_admin.py` -- servicetester av utvalget, sorteringen og grensen (`sett_na` på begge sider), og av `erfaring`. HTTP-tester for hver rad i matrisen, med personverntesten for oversikten og detaljene. Testene av `filterlenke` og `vurdering`, og av `neste` gjennom registreringen. Testene som forutsatte at 2.3 ikke fantes, snus -- FR-9, FR-10, FR-11, FR-16, AD-16, NFR-5, NFR-12
- [x] `tests/e2e/test_t1.py`, `tests/e2e/test_klientatferd.py` -- `oversikt-tom` erstattes av `oversikt` (Ola), `oversikt-kategori`, `oversikt-tom-kategori` (Kari, Hage), `oversikt-tom` (postnummer uten oppdrag), `oversikt-postnummer-feil` og `oppdrag-detaljer-andre` (Ola på Noras). Klienttester: fokus og `aria-describedby` etter kategori og etter «Vis»/Enter, «Velg et annet postnummer» (fokus og `selectionStart`/`selectionEnd`), «Vis alle kategorier» gir fokus på «Alle», et klikk på kortflaten åpner detaljene, og antall kolonner ved 360, 768 og 1280 px -- NFR-6, NFR-7, SM-5, UX-DR5, UX-DR24

**Acceptance Criteria:**
- Gitt en utlogget bruker som åpner en delt lenke til `/oppdrag/{id}`, når hen trykker «Registrer deg» og registrerer seg, så havner hen på `/oppdrag/{id}`. `neste` bæres som skjult felt gjennom «Registrer deg» og registreringen, også ved 422, og registreringen sender til `trygg_neste(neste)` (retro T-2).
- Gitt Ola ved 360, 768 og 1280 px, når oversikten vises, så står kortene i 1, 2 og 3 kolonner, og et klikk hvor som helst på et kort åpner detaljene.
- Gitt mobil med JS, når Amir velger «Hage», skriver `5006` og trykker Enter, så står fokus først på «Hage» og så i postnummerfeltet, antallslinja er knyttet til begge, og Hage er fortsatt valgt.
- Gitt T1, når `uv run pytest -m e2e` kjøres, så er alle sidene for oversikten og detaljene for andre uten «serious»/«critical» og uten vannrett rulling ved 320 px.

## Implementation Notes

- `utgatt(tidspunkt, na=None)` gir `bool` for en verdi og et SQL-uttrykk for kolonnen, så spørringen, `endre_status(ikke_passert=True)` (via `ikke_utgatt()`) og merket i 2.4 bruker samme grense.
- «Feil: » i tittelen uten feiloppsummering: ny parameter `render(..., feil_i_tittel=True)`. De andre sidene er uendret.
- Kategorilenkene og «Vis alle kategorier» kaller `filterlenke(kategori=..., postnummer=lenkepostnummer)`. `lenkepostnummer` er postnummeret lista viser når det er et annet enn eget, ellers `None`. Da bærer lenkene aldri et ugyldig postnummer videre fra en feil.
- Fullførte formateres med filteret `fullforte` (`domene.fullforte_tekst`) ved siden av `vurdering`.
- `Erfaring.per_kategori` er en tuple med `(kode, antall)` i rekkefølgen i `KATEGORIER`, uten kategorier med 0.
- Testen fra 2.1 som forbød `oppdragsgiver_id` i `OppdragVisning`, er snudd, fordi specen legger feltet til («Se profil» trenger id-en).

## Spec Change Log

## Review Triage Log

Pass 1 (2026-11-27). Lag: Blind Hunter (BH), Edge Case Hunter (EC), Verification Gap (VG). VG fant ingen hull.

| # | Lag | Funn | Verdict | Begrunnelse | Rute |
|---|---|---|---|---|---|
| 1 | BH, EC | `_filterlenke` kopierer alle parametre fra adressen, også ukjente og søppelverdier, inn i alle filterlenkene | low | Bekreftet. Retten er direkte: behold bare `kategori` og `postnummer` | patch |
| 2 | BH, EC | `vurdering_tekst` runder midtpunkter ulikt (4,25 gir «4,2», 4,45 gir «4,5»), og testen låser feilen | low | Bekreftet: binær flyttallsavrunding. Brukes i Epic 4. Retten er direkte (`Decimal`, `ROUND_HALF_UP`) | patch |
| 3 | BH | README lover «fire oppdrag» for Ola, men antallet avhenger av når seed ble kjørt | low | Sensor kan lese README en annen dag enn seed ble kjørt. Retten er én setning | patch |
| 4 | BH, EC | En innlogget bruker uten postnummer gir «Ledige oppdrag i » | false | Registreringen krever et gyldig postnummer, og sletting av konto (4.5) avslutter alle sesjoner (AD-8). Ingen innlogget bruker kan ha NULL | reject |
| 5 | BH | «Postnummer med poststed» står tre steder (`_sted`, `OppdragKort.sted`, `OffentligBruker.sted`) | low | Samme `" ".join` i alle tre, og ingen avviker. Retten er refaktorering | reject |
| 6 | BH | Seed setter `valgt_hjelper_id` utenom `endre_status`, så `versjon` øker ikke | low | Bare eksempeldata. Valg av hjelper kommer i Epic 3 (`velg_hjelper`), og da byttes seed over | reject |
| 7 | BH | Code Map sier «definerer ikke passert som `tidspunkt > klokke.na()`» | low | Retten ville endre denne buildens spec | reject |
| 8 | BH | Status og sporing er ikke oppdatert ved fullføring | false | Gjøres i steg 5. Tastatursjekken føres i `issues.md` | reject |
| 9 | BH | To rader i I/O-matrisen er upresise (FR-3 «eller tilsvarende», «Tom, «Alle»») | low | Retten ville endre den frosne specen. Testene bruker eksakte verdier | reject |
| 10 | BH | Reservegrenen i `fokus.js` (`[autofocus]` når `<body>` har fokus) testes ikke i Chromium | low | Gjelder bare nettlesere uten `autofocus` på lenker. Retten krever en egen testrigg | reject |
| 11 | BH | Ingen HTTP-test for «Vis» mot et postnummer uten treff (`aria-describedby` til `tom-forste` på feltet) | low | Samme variabel `beskrevet_av` styrer feltet og lenken, og den er testet for lenken | reject |
| 12 | BH | Hover på kortet syns ikke i forced-colors | low | Hover er et tillegg. Fokus er dekket med `Highlight` | reject |
| 13 | BH | `feil_i_tittel`, `utgatt` og `filterlenke` står ikke i spine eller EXPERIENCE | false | EXPERIENCE § Filtrene sier at bare feltfeilen vises. AD-3 krever én funksjon per avledet tilstand, og AR-27 én hjelper for filterlenkene | reject |
| 14 | EC | Et eksempeloppdrag med både `avbrutt=True` og `utfort_av` gir `Konflikt` i seed | low | Ingen slik rad finnes. Feilen er høylytt og bare for utviklere | reject |

## Design Notes

- **Adressen bestemmer fokus.** Serveren ser bare URL-en, så den bærer markøren. Kategorilenkene har alltid `kategori`, og «Alle» har `?kategori=alle` (som i mockupen). Det fjerner filteret, men gir fokus på «Alle», også fra «Vis alle kategorier». Postnummerskjemaet sender `vist_postnummer`, som både sier at innsendingen kom fra skjemaet (fokus i feltet) og hvilket postnummer lista viste (lista står uendret ved feil). Rekkefølgen er: `vist_postnummer` gir feltet, ellers gir `kategori` den valgte lenken, ellers er det ingen `autofocus` (EXPERIENCE: «fokus flyttes bare i tilfellene under»). `filterlenke` fjerner `vist_postnummer`, så den aldri følger med i delte lenker fra appen.
- **Ugyldig filter** gir 200, ikke 422. Lista vises som den skal, og det er bare filterverdien som avvises. Hvordan `render` får «Feil: » i tittelen uten `feil`, avgjøres i koden uten å endre de andre sidene.
- **`aria-describedby`:** den valgte kategorien og postnummerfeltet viser til antallslinja, eller til den første setningen i tomtilstanden ved 0 treff. Ved feil viser feltet til feilen og poststedet.
- **«Velg et annet postnummer»** er en lenke til `#postnummer` med stil som sekundærknapp og `data-velg-felt`. Uten JS hopper siden til feltet, og med JS gir `fokus.js` fokus og kaller `select()`. `autofocus` på `<a>` virker i Chromium, og `fokus.js` tar over der nettleseren ikke støtter det.
- **Kortet** følger mockupen: kategorimerket står før `h2` i koden, og lenken er bare tittelen. Trykkflaten er `::after` på lenken (DESIGN.md § Fokus), så kortet ikke har nestede interaktive elementer.
- **Oppdragsgiverblokken** er en `section` med `h2` «Lagt ut av {visningsnavn}» etter beskrivelsen, og under den erfaringen og «Se profil» (`button-text`). Navnet er det fulle visningsnavnet, som på profilen («Nora Berg»). Fullførte vises som «Ingen fullførte oppdrag ennå», «1 fullført oppdrag» eller «12 fullførte oppdrag», og så « · » og `vurdering`, som i mockupen for interessertlista. Er oppdragsgiveren slettet, står «Slettet bruker» uten lenke og uten erfaring (AD-8). Det kan først skje etter 4.5.
- **Utgått:** spørringen bruker samme funksjon som 2.4 skal bruke for merket. Grensen er den samme som i `endre_status(ikke_passert=True)`: passert betyr `tidspunkt <= na`.
- **Seed:** uten et utført oppdrag ville blokken alltid vise null. Nora som hjelper på Karis oppdrag gir et tall som syns når Ola åpner «Mate katten i helgen».
- **Ingen sidenummerering:** seed og v1 har få oppdrag per postnummer.

## Verification

**Commands:**
- `uv run pytest` -- forventet: alle tester er grønne, også `test_arkitektur.py`, de nye testene for oversikten, registreringen og seed, `test_to_steg.py` og invariantene fra 1.2, 1.4, 2.1 og 2.2.
- `uv run pytest -m e2e` -- forventet: T1 er grønn for alle sider i `SIDER`, både de gamle og de nye, ved 360 og 1280 px og uten vannrett rulling ved 320 px. Klienttestene er grønne, også de fra 1.5 og 2.2.

**Manual checks (if no CLI):**
- [ ] Tastatursjekk av oversikten (kategorier, postnummer og «Vis», tomtilstandene og kortene) og detaljene for andre i cirka fem minutter (DoD). **Utsatt til story 6.1** (retro T-5): den autonome kjøringen har ingen manuell tester, og T1 og klienttestene dekker de automatiske kravene. Storyen kan settes `done` med denne utsettelsen.
