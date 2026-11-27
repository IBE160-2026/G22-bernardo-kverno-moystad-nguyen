---
title: 'Story 2.4: Se egne oppdrag under «Mine oppdrag»'
type: 'feature'
created: '2026-11-27'
status: 'in-progress'
baseline_commit: '8c538ebff15c405c8be6d13226a7d6ab6dc4e341'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-2-context.md'
  - '{project-root}/_bmad-output/planning-artifacts/ux-designs/ux-G22-bernardo-kverno-moystad-nguyen-2026-11-07/EXPERIENCE.md'
  - '{project-root}/_bmad-output/planning-artifacts/ux-designs/ux-G22-bernardo-kverno-moystad-nguyen-2026-11-07/DESIGN.md'
  - '{project-root}/_bmad-output/planning-artifacts/ux-designs/ux-G22-bernardo-kverno-moystad-nguyen-2026-11-07/mockups/key-mine-oppdrag.html'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** «Mine oppdrag» er fortsatt den enkle lista fra 2.1, med bare titler, nyeste først, og uten status, tidspunkt eller merke. Et utgått oppdrag forsvinner fra oversikten uten at oppdragsgiveren ser det noe sted, og menyen viser ikke at noe trenger handling (FR-8, FR-18, NFR-11).

**Approach:** «Oppdrag jeg har lagt ut» blir lenkerader (`list-row`) med tittel, statusmerke, merket «Tidspunktet er passert», tidspunkt og ›, sortert etter tidspunkt. Merkene og antallet beregnes ved lesing med én funksjon hver i `oppdrag/service.py` (AD-3), og `lag_app()` kobler inn menykroken `(db, bruker_id) -> int`, som `render` kaller når noen er innlogget. Ingen migrering. Fanene kommer i 3.1, snarveiene i 2.5, og gruppene og de andre merkene i 3.5.

**Beslutninger (anbefalt alternativ, delegert av Heidi 2026-11-26):**
- Linja «1 oppdrag trenger at du gjør noe.» (og «2 oppdrag …») står under `h1` i «Mine oppdrag» når tallet fra menykroken er over 0, og vises ikke ved 0 (EXPERIENCE.md l. 67 og 169). Tallet i menyen får dermed forklaringen på siden det peker til, og 3.5 utvider bare tellingen. Akseptansekriteriet flyttes fra story 3.5 til 2.4 i `epics.md`.
- Specen beholdes samlet (cirka 5 500 tokens), fordi storyen er ett mål.

## Boundaries & Constraints

**Always:** Tekstene er ordrett fra EXPERIENCE.md: `h1` «Mine oppdrag», `h2` «Oppdrag jeg har lagt ut», `<title>` «Mine oppdrag: Oppdrag jeg har lagt ut – Nabolagshelten», merket «Tidspunktet er passert» med skjult «Må gjøres: » foran og «.» etter, statusmerket med skjult «Status: », tomtilstanden «Du har ikke lagt ut noen oppdrag.» med lenken «Legg ut oppdrag», og menyvalget lest som «Mine oppdrag, 1 trenger handling». Merket gjelder status `apen` med `utgatt(tidspunkt)`, og `utgatt` er eneste definisjon av passert. Antallet teller rader med minst ett merke fra den samme merkefunksjonen (AD-3). Malen får bare `OppdragRad` (AD-16). Tid og status formateres bare med filtrene. I raden er tittelen eneste lenke, lenkens navn er bare tittelen, den har `aria-describedby` til merkelinja, og pila › er `aria-hidden`. Kroken kalles bare når noen er innlogget, og aldri fra `feilside` eller `render_fragment`. Høyst ett `autofocus` per side. Krav-ID-er står i commits og tester.

**Never:** snarveiene «Endre tidspunkt» og «Avbryt oppdrag», `dialog.js` og merket i detaljene (2.5), fanene og `?fane=` (3.1), «3 har meldt interesse», «Ingen har meldt interesse ennå» og «Hjelper: …» (3.2, 3.3), gruppene og de andre merkene (3.5), bilder i radene (2.7), lagring av merker eller av hva brukeren har sett, cron, endring av `utgatt`, `ikke_utgatt`, `ledige_oppdrag`, `hent_for_visning`, `endre_status` eller `statusmerke`, en egen `Session` for kroken når ruta allerede har en, `aria-live` på tallet, `|safe`, `innerHTML`, ny tabell og migrering.

## I/O & Edge-Case Matrix

Klokka står fast på tirsdag 24.11.2026 kl. 13:00 norsk tid (`FAST_KLOKKE`). Kari har seks oppdrag i seed, og ett av dem er utgått. Ola har ingen.

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Lagt ut | Kari, GET `/mine-oppdrag` | 200, `<title>`, `h1` og `h2` som over. Én `<li>` per oppdrag, i rekkefølgen «Bytte lyspære i taket» (Utført, «Torsdag 19. nov. kl. 12:00»), «Bære ved opp til tredje etasje» (Åpen og merket, «Søndag 22. nov. kl. 10:00»), «Måke snø i innkjørselen» («I morgen kl. 09:00»), «Raking av løv i hagen», «Hjelp med nytt nettbrett» og «Lufte hunden mens jeg er bortreist» (Avbrutt). Alle er lenkerader til `/oppdrag/{id}`, og andres oppdrag vises ikke | – |
| Rad | ett oppdrag | tittelen med lenke, merkelinja (statusmerke og eventuelt merke) med unik id, tidspunktet med klokkeikon og pila. Lenken har `aria-describedby` til merkelinja. Ingen andre lenker eller knapper i raden | – |
| Sortering | to egne oppdrag med samme tidspunkt | det som ble lagt ut først, står først, og så etter `id` | – |
| Grensen (AD-3) | eget åpent oppdrag, `sett_na` 1 s før tidspunktet / lik tidspunktet | ingen merke og antall 0 / merket og antall 1. Ingenting lagres | – |
| Andre statuser | `hjelper_valgt`, `utfort` og `avbrutt` med passert tidspunkt | ingen «Tidspunktet er passert», og antall 0 | – |
| Forklaringslinje | Kari på `/mine-oppdrag` med ett utgått oppdrag / Ola uten | «1 oppdrag trenger at du gjør noe.» rett under `h1`, med samme tall som menyen / ingen linje | – |
| Menytall | Kari på `/`, `/mine-oppdrag`, `/profil`, egne detaljer, «Nytt oppdrag» og skjemaet med 422 | ved «Mine oppdrag» i begge menyene står «1» (`aria-hidden`) og den skjulte teksten «, 1 trenger handling» | – |
| Tallet 0 | Ola, og Kari med `sett_na` før alle tidspunktene | verken tall eller skjult tekst | – |
| Andres utgåtte | Nora har et utgått oppdrag | teller ikke hos Kari | – |
| Feilside | Kari, GET `/finnes-ikke` og et annet oppdrag som gir 404 | 404 med menyen uten tall, og kroken kalles ikke | – |
| Ingen kobling | `lag_app(menykrok=None)`, eller noe som ikke kan kalles | `KonfigFeil` med en melding om menykroken (AD-1) | appen starter ikke |
| Tom | Ola, GET `/mine-oppdrag` | `h2` og tomtilstanden med lenken til `/oppdrag/ny`, uten liste | – |
| XSS | `<script>alert(1)</script>` i tittelen | vises som tekst i raden | – |
| Personvern | HTML fra «Mine oppdrag» | ingen telefonnummer, e-post eller fødselsdato | – |
| Invariant 2.3 (T-6) | Karis utgåtte oppdrag, og Kari åpner et eget oppdrag fra raden | oppdraget vises ikke i Olas oversikt. Detaljene har «Mine oppdrag» med `aria-current="true"`, ingen oppdragsgiverblokk, og «Tilbake» går til `/mine-oppdrag` | – |
| Invariant meny (T-6) | `/`, `/mine-oppdrag`, `/profil` | menyen i fast rekkefølge med én `aria-current="page"` (på `/mine-oppdrag` er det fortsatt menyvalget, fordi fanene ikke finnes ennå), én `h1`, og «Hopp til innholdet» først | – |
| Invariant 2.1/2.2 (T-6) | «Publiser» | 303 til detaljene med «Oppdraget er lagt ut.», og oppdraget står i lista med status Åpen. `test_to_steg.py` er grønn | – |
| Invariant T1 (T-6) | alle sider i `SIDER` | fortsatt uten «serious»/«critical» og uten vannrett rulling ved 320 px, også med tallet i bunnmenyen | – |

</frozen-after-approval>

## Code Map

- `app/oppdrag/service.py` -- `utgatt` og `ikke_utgatt` (l. 72–84) gjenbrukes uendret. `OppdragRad` (l. 273–278) har bare id og tittel, og `lagt_ut_av` (l. 311–318) sorterer nyeste først. Begge byttes ut. Docstringen (l. 11–12) nevner allerede merket i 2.4.
- `app/oppdrag/routes.py` -- `mine_oppdrag` (l. 178–194) har tittelen «Mine oppdrag». `detaljer` (l. 358–390) og `_tilbake_fra_detaljer` (l. 350) gir allerede «Mine oppdrag» og ingen blokk for eier, og endres ikke. Docstringen l. 23.
- `app/oppdrag/templates/oppdrag/mine.html` -- `ul.oppdragsliste` (l. 9–14) erstattes. Tomtilstanden (l. 15–21) beholdes.
- `app/core/templates/core/makroer.html` -- `statusmerke` (l. 92–103) gjenbrukes uendret, fordi testene sjekker HTML-en ordrett. `meny` og `_menyvalg` (l. 49–71) får tallet. Det finnes ingen makro for handlingsmerket ennå.
- `app/core/render.py` -- `render` (l. 154–194) og `_kontekst` (l. 141). Docstringen (l. 6) sier at antallet kommer i 2.4. `render_fragment` (l. 197) endres ikke.
- `app/core/feil.py` -- `feilside` (l. 87–101) bruker `render`, og spinen krever at feilsider rendres uten databasekall.
- `app/core/db.py` -- `hent_db` (l. 99–110). I SQLite starter hver transaksjon, også lesing, med `BEGIN IMMEDIATE` (l. 81–83).
- `app/__init__.py` -- `lag_app` (l. 39–93) og `_STANDARD`-mønsteret for `Autentisering` (l. 30–56). Docstringen (l. 4) sier at kroken blir påkrevd fra 2.4.
- `app/core/static/css/app.css` -- `.oppdragsliste` (l. 1054–1063) brukes bare av `mine.html`. Mønstre: `.merkelinje` (l. 920), `.statusmerke` (l. 928–971), `.fakta` (l. 979), `.kort__lenke::after` med hover og fokus (l. 1163–1195), bunnmenyen (l. 338–375) og forced-colors (l. 208, l. 423). Tokens: `--color-badge-bg/-fg` (l. 32–33), `--color-link` (l. 22), `--shadow-card` (l. 108).
- `app/seed.py` -- `EKSEMPELOPPDRAG` (l. 90–127) har allerede seks oppdrag for Kari, med ett utgått, ett avbrutt og ett utført. Endres ikke.
- `README.md` -- l. 87 om oversikten og «Mine oppdrag».
- `tests/oppdrag/test_grunnsider.py` -- `menyvalg` (l. 27) leser lenketeksten. `test_mine_oppdrag_har_tomtilstand` (l. 88) og `test_mine_oppdrag_viser_egne_oppdrag_nyeste_forst` (l. 97) forutsetter 2.1.
- `tests/oppdrag/test_legge_ut.py` -- `test_nytt_oppdrag_vises_under_mine_oppdrag` (l. 256) sjekker `<li><a href=…>` ordrett. XSS-testen (l. 395).
- `tests/oppdrag/test_legge_ut_regler.py` -- `test_lagt_ut_av_gir_egne_nyeste_forst` (l. 335).
- `tests/core/test_config.py` -- `test_lag_app_uten_autentisering_stopper` (l. 138) er mønsteret for kroken.
- `tests/conftest.py` -- `app` (l. 116) bytter `sesjonsfabrikk` etter `lag_app()`, og alle sesjoner deler én tilkobling, så låsing i SQLite syns ikke i pytest. `sett_na` (l. 129) og `lag_oppdrag` (l. 193).
- `tests/e2e/test_t1.py` -- `mine_oppdrag` (l. 113, Kari) og `mine_oppdrag_tom` (l. 212, Ola), og `SIDER` (l. 219).
- `tests/e2e/test_klientatferd.py` -- `test_riktig_meny_ved_bredden` (l. 125) bruker `to_have_text(["Oppdrag", "Mine oppdrag", "Profil"])` med Kari, og det feiler når tallet og den skjulte teksten står i lenken. `test_klikk_pa_kortflaten_apner_detaljene` (l. 690) er mønsteret for radflaten.

## Tasks & Acceptance

**Execution:**
- [ ] `app/oppdrag/templates/oppdrag/mine.html`, `app/oppdrag/routes.py`, `_bmad-output/planning-artifacts/epics.md` -- linja «N oppdrag trenger at du gjør noe.» under `h1` når `antall_trenger_handling` er over 0 (samme tall som menyen, én telling per forespørsel). Akseptansekriteriet («øverst i «Mine oppdrag» står …») flyttes fra story 3.5 til 2.4 i `epics.md`, med en merknad i 3.5 om at linja finnes fra 2.4 -- FR-18, UX-DR26
- [ ] `app/oppdrag/service.py` -- `TIDSPUNKTET_ER_PASSERT`. `OppdragRad(id, tittel, status, tidspunkt, merker: tuple[str, ...])`. `merker_lagt_ut(status, tidspunkt, *, na) -> tuple[str, ...]`, som gir merket når status er `apen` og `utgatt(tidspunkt, na=na)`. `lagt_ut_av(db, bruker_id)` leser `klokke.na()` én gang og sorterer etter `tidspunkt`, `opprettet` og `id`. `antall_trenger_handling(db, bruker_id) -> int` teller radene fra `lagt_ut_av` som har merker -- FR-8, FR-18, AR-13, AD-3
- [ ] `app/__init__.py` -- `lag_app(*, autentisering=..., menykrok=_STANDARD, settings=None)`. Standard er `antall_trenger_handling`. Med `None`, eller noe som ikke kan kalles, stopper oppstarten med `KonfigFeil`. Kroken lagres i `app.state.menykrok` -- AD-1, AR-3
- [ ] `app/core/db.py`, `app/core/render.py`, `app/core/feil.py` -- `hent_db` legger sesjonen i `request.state.db`. `render` får `med_menytall=True` og gir `meny_antall` til malen: kroken kalles bare når noen er innlogget, med `request.state.db`, eller med en kort egen sesjon fra `sesjonsfabrikk` når ruta ikke har en. `feilside` sender `med_menytall=False`. Docstringene oppdateres -- NFR-11, AD-3, spinen § Feil
- [ ] `app/core/templates/core/makroer.html` -- `_menyvalg` viser tallet ved «Mine oppdrag» når det er over 0, i begge menyene. Ny makro `handlingsmerke(tekst)` med pilikon og den skjulte teksten (se Design Notes) -- UX-DR3, UX-DR10
- [ ] `app/oppdrag/routes.py`, `app/oppdrag/templates/oppdrag/mine.html` -- tittelen, `h2`, lenkeradene og tomtilstanden (se Design Notes). Docstringene oppdateres -- FR-18, UX-DR9, UX-DR21
- [ ] `app/core/static/css/app.css` -- `.listerad`, `.handlingsmerke` og `.menytall` etter DESIGN.md (§ list-row, § action-tag, § nav-badge). `::after` på lenken dekker bare lenkedelen. Kanten ved hover er 2 px `--color-primary`, og fokus gir kanten og ringen. Merket brytes uten `line-clamp` eller ellipse. I forced-colors får merket og tallet kant. `.oppdragsliste` fjernes. Ingen vannrett rulling ved 320 px -- UX-DR9, UX-DR10, NFR-6, NFR-7
- [ ] `README.md` -- l. 87 får en setning om at Kari ser seks oppdrag under «Mine oppdrag», ett med «Tidspunktet er passert» og tallet 1 i menyen -- NFR-2
- [ ] `ARCHITECTURE-SPINE.md` -- én setning i konvensjonen Rendring: kroken får forespørselens `Session` (`request.state.db`) og kalles ikke fra feilsider -- planleggingsdokumentene holdes oppdatert
- [ ] `tests/oppdrag/test_mine_oppdrag_regler.py` (ny), `tests/oppdrag/test_mine_oppdrag.py` (ny), `tests/oppdrag/test_grunnsider.py`, `tests/oppdrag/test_legge_ut.py`, `tests/oppdrag/test_legge_ut_regler.py`, `tests/core/test_config.py`, `tests/core/test_render.py` -- servicetester av sorteringen, grensen (`sett_na` på begge sider), de andre statusene, andres oppdrag og at antallet er lik antall rader med merker. HTTP-tester for hver rad i matrisen. Tallet testes med en kroken-spion gitt til `lag_app(menykrok=…)`, også at den ikke kalles på feilsiden. `lag_app(menykrok=None)` stopper. Testene som forutsatte 2.1, snus -- FR-8, FR-18, NFR-11, NFR-12, AD-1, AD-3, AD-16
- [ ] `tests/e2e/test_t1.py`, `tests/e2e/test_klientatferd.py` -- `mine-oppdrag` (Kari) venter seks rader og merket. Klienttester: et klikk på radflaten utenfor tittelen åpner detaljene, og tallet «1» syns i bunnmenyen ved 360 px og i topplinjen ved 1280 px, med navnet «Mine oppdrag, 1 trenger handling». `test_riktig_meny_ved_bredden` sjekker navnene med `to_contain_text` eller tilgjengelig navn -- NFR-6, NFR-7, NFR-11, SM-5

**Acceptance Criteria:**
- Gitt Kari med seed ved 360 og 1280 px, når «Mine oppdrag» vises, så kan hver rad åpnes med et klikk hvor som helst over skillelinjen, merket brytes over flere linjer uten å klippes, og siden ruller ikke vannrett ved 320 px.
- Gitt en skjermleser på lenken i raden «Bære ved opp til tredje etasje», når den får fokus, så leses tittelen og så «Status: Åpen» og «Må gjøres: Tidspunktet er passert.».
- Gitt `uv run python -m app.seed` og Kari innlogget lokalt med SQLite, når hun åpner detaljene for et eget oppdrag, så svarer siden uten forsinkelse og med tallet i menyen (kroken bruker forespørselens sesjon).

## Implementation Notes

## Spec Change Log

## Review Triage Log

## Design Notes

- **Kroken bruker forespørselens sesjon.** I SQLite starter hver transaksjon med `BEGIN IMMEDIATE`, også lesing. Når `detaljer` har lest oppdraget, holder rutas sesjon skrivelåsen til forespørselen er ferdig. En egen sesjon i `render` ville da vente i 5 s og få «database is locked». pytest merker det ikke, fordi alle sesjoner der deler én tilkobling. E2E og lokal kjøring ville merket det. Derfor legger `hent_db` sesjonen i `request.state.db` (som `request.state.innlogget`), og `render` bruker den. Ruter uten `hent_db` har ingen åpen sesjon, så der kan `render` åpne en kort en.
- **Én definisjon av merket.** Antallet regnes fra `lagt_ut_av`, ikke med en egen `COUNT` i SQL. Da kan lista og tallet aldri vise forskjellig, og 3.5 legger nye merker til på ett sted. Det koster én spørring på egne oppdrag per sidelasting, og det holder for v1.
- **Raden.** Strukturen følger mockupen, og 2.5 kan legge til snarveiene uten å endre resten:

  ```html
  <li class="listerad listerad--lenke">
    <div class="listerad__hoved">
      <p class="listerad__tittel" id="rad-7-tittel"><a class="listerad__lenke" href="/oppdrag/7" aria-describedby="rad-7-merker">Bære ved …</a></p>
      <div class="merkelinje" id="rad-7-merker">{statusmerke} {handlingsmerke}</div>
      <p class="listerad__fakta">{klokkeikon}<span class="listerad__tid">Søndag 22. nov. kl. 10:00</span></p>
      <svg class="listerad__pil" aria-hidden="true" focusable="false">…</svg>
    </div>
  </li>
  ```

  `listerad__hoved` har `position: relative`, så lenkens `::after` dekker bare den. I 2.5 kommer `<div class="listerad__handlinger">` etter `listerad__hoved`, med skillelinje og knapper som har `aria-describedby="rad-7-tittel"`. `listerad__hoved` er ikke en lenke selv, så knappene blir aldri nestet i lenken. Radmarkupen ligger i `mine.html`, og `handlingsmerke` ligger i `core`, fordi detaljene trenger merket i 2.5 og Epic 3.
- **Handlingsmerket:** `<span class="handlingsmerke">{pil}<span><span class="skjult-tekst">Må gjøres: </span>Tidspunktet er passert<span class="skjult-tekst">.</span></span></span>`. `statusmerke` får ikke punktum, fordi testene fra 2.1 og 2.3 sjekker HTML-en ordrett, og «Må gjøres: » skiller de to i opplesningen.
- **Menytallet:** `<span class="menytall" aria-hidden="true">1</span>` og `<span class="skjult-tekst">, 1 trenger handling</span>` etter menynavnet. I bunnmenyen står tallet øverst til høyre på ikonet, som i mockupen, og i topplinjen etter teksten.
- **Ingen faner ennå.** Fanene med `?fane=` kommer i 3.1. Til da står «Oppdrag jeg har lagt ut» som `h2` over lista eller tomtilstanden, og menyvalget beholder `aria-current="page"`. `<title>` har fanenavnet allerede nå (EXPERIENCE § Sidetitler).
- **Alle egne rader er lenker.** Oppdragsgiveren kan se alle statusene sine (FR-9), og i mockupen har også avbrutte og utførte rader pil.
- **Merket i detaljene** kommer i 2.5, sammen med «Endre tidspunkt» (EXPERIENCE § Oppdragsdetaljer: oppdragsgiver, Åpen, passert). 2.4 endrer ikke detaljene.
- **«Hjelper: Nora Berg»** på det utførte oppdraget i seed vises ikke ennå, selv om `valgt_hjelper_id` finnes. Linja hører til 3.3.

## Verification

**Commands:**
- `uv run pytest` -- forventet: alle tester er grønne, også `test_arkitektur.py`, de nye testene for «Mine oppdrag», kroken og `lag_app`, og invariantene fra 2.1, 2.2 og 2.3.
- `uv run pytest -m e2e` -- forventet: T1 er grønn for alle sider i `SIDER` ved 360 og 1280 px og uten vannrett rulling ved 320 px, også `mine-oppdrag` med seks rader og tallet i menyen. Klienttestene er grønne, også de fra 1.5, 2.2 og 2.3.

**Manual checks (if no CLI):**
- [ ] Tastatursjekk av «Mine oppdrag» (radene, fokusringen på hele lenkedelen, tomtilstanden) og av menyen med tallet, i cirka fem minutter (DoD). **Utsatt til story 6.1** (retro T-5): den autonome kjøringen har ingen manuell tester, og T1 og klienttestene dekker de automatiske kravene. Storyen kan settes `done` med denne utsettelsen.
