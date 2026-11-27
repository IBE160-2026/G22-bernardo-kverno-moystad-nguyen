---
title: 'Story 2.5: Redigere og avbryte oppdrag'
type: 'feature'
created: '2026-11-27'
status: 'in-progress'
baseline_commit: '12cb5a0c1fc712702bf9d22f4174089b68367c07'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-2-context.md'
  - '{project-root}/_bmad-output/planning-artifacts/ux-designs/ux-G22-bernardo-kverno-moystad-nguyen-2026-11-07/EXPERIENCE.md'
  - '{project-root}/_bmad-output/planning-artifacts/ux-designs/ux-G22-bernardo-kverno-moystad-nguyen-2026-11-07/DESIGN.md'
  - '{project-root}/_bmad-output/planning-artifacts/ux-designs/ux-G22-bernardo-kverno-moystad-nguyen-2026-11-07/mockups/key-detaljer.html'
  - '{project-root}/_bmad-output/planning-artifacts/ux-designs/ux-G22-bernardo-kverno-moystad-nguyen-2026-11-07/mockups/key-mine-oppdrag.html'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Oppdragsgiveren kan ikke endre eller avbryte et oppdrag etter at det er lagt ut. Et utgått oppdrag har merket «Tidspunktet er passert» under «Mine oppdrag», men ingen vei videre. Dermed kan det verken komme tilbake i oversikten eller avsluttes (FR-6, FR-7, FR-8). `Konflikt` har ingen handler, og det finnes ingen bekreftelsesdialog.

**Approach:** `/oppdrag/{id}/rediger` gjenbruker skjemaet fra 2.1 uten KI, med «Lagre endringer». Én betinget `UPDATE` lagrer endringen, øker `versjon` og setter `vesentlig_endret` (AD-2, AD-3). `/oppdrag/{id}/avbryt` gir en bekreftelsesside med GET og avbryter med POST gjennom `endre_status`. Med JS åpner `dialog.js` den samme bekreftelsen som `<dialog>` fra makroen `bekreft_dialog`, som Epic 3 og 4 gjenbruker. Detaljene for oppdragsgiveren får «Rediger» og «Avbryt oppdrag», eller merket «Tidspunktet er passert» med «Endre tidspunkt» og «Avbryt oppdrag». Radene med merket under «Mine oppdrag» får de samme to snarveiene. `Konflikt` får en handler i `core` med feilmeldingen og «Last siden på nytt». Ingen migrering, fordi `versjon` og `vesentlig_endret` finnes fra 0003. Bilder kommer i 2.7.

**Beslutninger (anbefalt alternativ, delegert av Heidi 2026-11-26):**
- Etter avbrudd fra «Mine oppdrag» havner Kari tilbake i «Mine oppdrag». «Oppdraget er avbrutt.» har fokus, og raden viser «Avbrutt». Fra detaljene havner hun i detaljene. En hvitlistet parameter `fra=mine` følger med i snarveien, i skjemaet i dialogen og på bekreftelsessiden. `Konflikt` går til detaljene i begge tilfellene.
- Redigering vises på én skjerm på alle bredder, uten `steg.js`, med de to `h2`-ene. EXPERIENCE § Responsive nevner to steg bare for «Nytt oppdrag», og «Dato» (målet for «Endre tidspunkt») skal ikke ligge skjult i steg 2.
- Specen beholdes samlet (cirka 6 300 tokens), fordi storyen er ett mål.

## Boundaries & Constraints

**Always:** Tekstene er ordrett fra EXPERIENCE.md: «Rediger», «Lagre endringer», `<title>` «Rediger «{tittel}» – Nabolagshelten», «Endringene er lagret.», «Endre tidspunkt», «Avbryt oppdrag», «Velg et nytt tidspunkt fram i tid», dialogen «Avbryte «{tittel}»? Det kan ikke angres.» med «Ja, avbryt oppdraget» og «Behold oppdraget», «Oppdraget er avbrutt.», og «Oppdraget er endret. Last siden på nytt.» med knappen «Last siden på nytt». Bare oppdragsgiveren kan redigere, og bare når status er `apen`. Avbryte gjelder `apen` og `hjelper_valgt` (FR-7). Andre enn oppdragsgiveren får samme 404 som for et oppdrag som ikke finnes, og ser aldri knappene. Feltvalideringen er den samme funksjonen som i `opprett_oppdrag`, så tekstene og rekkefølgen er de samme. Den betingede `UPDATE`-en er første skriving i transaksjonen. Er 0 rader endret, gir det `FinnesIkke` eller `Konflikt`, og ingenting lagres. `vesentlig_endret` settes til `klokke.na()` bare når tidspunkt, beløp eller postnummer faktisk endres. «Utgått» kommer bare fra `utgatt`, og merket bare fra `merker_lagt_ut` (AD-3). Angre-valget heter aldri «Avbryt». Alt virker uten JS (AR-28). POST-ruter kjører `with db.begin():`, og services committer aldri (AD-17). Malene får bare dataklasser (AD-16). Høyst ett `autofocus` per side. Krav-ID-er står i commits og tester.

**Never:** KI på redigeringsskjemaet, bilde, «Bytt bilde» og «Fjern bildet» (2.7), «Meldt før endring», merket «Oppdraget er endret etter at du meldte interesse», interessertlista, «Velg et nytt tidspunkt for å kunne velge hjelper.» og knappene for status Hjelper valgt (Epic 3), `ikke_passert` i redigering eller avbrudd, `versjon` som skjult felt, `skjema_id` i redigeringsskjemaet, en fri `til`-URL i adressen, sletting av oppdrag, endring av `utgatt`, `merker_lagt_ut`, `antall_trenger_handling`, `hent_for_visning` eller `OVERGANGER`, regler i JS, `innerHTML`, `|safe`, ny tabell og migrering.

## I/O & Edge-Case Matrix

Klokka står fast på tirsdag 24.11.2026 kl. 13:00 norsk tid (`FAST_KLOKKE`). Kari eier «Måke snø i innkjørselen» (Åpen, «I morgen kl. 09:00», 200 kr) og det utgåtte «Bære ved opp til tredje etasje» i seed. Ola bor i 0571.

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Skjemaet | Kari, «Rediger» i detaljene til «Måke snø» | 200. `h1` og `<title>` «Rediger «Måke snø i innkjørselen»», feltene er utfylt (dato «25.11.2026», klokkeslett «09:00», «Beløp» valgt med 200), forhåndsvisningen, «Lagre endringer», ingen «Få forslag», ingen `skjema_id` og ingen `autofocus`. «Mine oppdrag» har `aria-current="true"` | – |
| Lagre | gyldige endringer | 303 til detaljene. Der står «Endringene er lagret.» i fokus og de nye verdiene. `versjon` har økt med 1 | – |
| Feil i felt | tom tittel og beløp «abc» | 422 med feiloppsummeringen, begge feilene og alle verdiene. `<title>` får «Feil: » foran, og den lagrede tittelen står i `<title>` og `h1`. Ingenting er lagret | `RegelBrudd` |
| Endre tidspunkt | Kari, «Endre tidspunkt» på «Bære ved» (rad eller detaljer) | `/oppdrag/{id}/rediger?fokus=tidspunkt` med `autofocus` på «Dato» og de gamle verdiene utfylt | – |
| Fortsatt passert | lagret uten å endre tidspunktet, eller med et passert tidspunkt | 422 med «Velg et nytt tidspunkt fram i tid» under «Når?», knyttet til begge feltene | `RegelBrudd` |
| Nytt tidspunkt | «Bære ved» får dato i morgen | 303 til detaljene. Merket og snarveiene er borte, menytallet og linja i «Mine oppdrag» er borte, og Ola ser oppdraget i oversikten | – |
| Vesentlig (AD-3) | endring av tidspunkt, beløp (også 200 → «Uten betaling») eller postnummer | `vesentlig_endret` = `klokke.na()` | – |
| Ikke vesentlig | bare tittel, beskrivelse eller kategori, eller samme verdier sendt på nytt (også « 0571 » og «9» for «09:00») | `vesentlig_endret` uendret | – |
| Dobbel innsending | samme gyldige skjema to ganger | begge gir 303 til detaljene, og `vesentlig_endret` er satt av den første | – |
| Andres oppdrag | Ola, GET eller POST `/oppdrag/{id}/rediger` eller `/avbryt` på Karis åpne oppdrag | samme 404 som `/oppdrag/999999`. Ingenting endres, og detaljene til Ola har ingen av knappene | `FinnesIkke` |
| Ikke Åpen | Kari, GET eller POST `/rediger` på `avbrutt`, `utfort` eller `hjelper_valgt` | 303 til detaljene med «Oppdraget er endret. Last siden på nytt.». Ingenting endres, også når feltene har feil | `Konflikt` |
| Avbryte | Kari, POST `/oppdrag/{id}/avbryt` med CSRF | status `avbrutt`, `versjon` + 1, 303 med «Oppdraget er avbrutt.» i fokus. Detaljene viser «Avbrutt» uten knapper | – |
| Bekreftelsesside | GET `/oppdrag/{id}/avbryt` | 200 med `h1` «Avbryte «…»?», «Det kan ikke angres.», POST-knappen «Ja, avbryt oppdraget» og lenken «Behold oppdraget» | – |
| Avbryte, feil status | Kari, POST `/avbryt` på `utfort` eller `avbrutt` | 303 til detaljene med «Oppdraget er endret. Last siden på nytt.», og ingen endring (FR-7) | `Konflikt` |
| Avbryte, Hjelper valgt | `avbryt_oppdrag` på `hjelper_valgt` (servicenivå) | status `avbrutt`, og `valgt_hjelper_id` beholdes (FR-7) | – |
| To faner (§4.0) | avbrutt i fane 1, så «Lagre endringer» eller «Ja, avbryt oppdraget» i fane 2 | bare den første handlingen er utført. Fane 2 får detaljene med feilmeldingen i fokus og knappen «Last siden på nytt» | `Konflikt` |
| Samtidig (AD-2) | to tråder, hver med sin tilkobling, avbryter og avbryter / avbryter og redigerer | nøyaktig én lykkes, og den andre gir `Konflikt`. Gjelder både SQLite og Postgres | `Konflikt` |
| Låst SQLite | `OperationalError` «database is locked» i den betingede `UPDATE`-en | `Konflikt` til detaljene, ikke 500 | `Konflikt` |
| Snarveier i raden | Kari, «Mine oppdrag» | bare raden «Bære ved» har `listerad__handlinger` under en skillelinje, utenfor lenken, med «Endre tidspunkt» og «Avbryt oppdrag» (`aria-describedby` til tittelen). Ingen andre rader har knapper | – |
| Detaljer, eier | Kari, «Måke snø» / «Bære ved» | etter beskrivelsen: «Rediger» og «Avbryt oppdrag» (sekundære) / merket «Tidspunktet er passert», så «Endre tidspunkt» (primær) og «Avbryt oppdrag» | – |
| XSS | `<script>alert(1)</script>` i tittelen | vises som tekst i `<title>`, `h1`, dialogen og bekreftelsessiden | – |
| Invariant 2.1/2.2 (T-6) | «Publiser» i «Nytt oppdrag» | 303 med «Oppdraget er lagt ut.». `skjema_id`, `Duplikat` og stegene er uendret, og `test_to_steg.py` er grønn | – |
| Invariant 2.3/2.4 (T-6) | «Tilbake» i detaljene etter lagring eller avbrudd, og detaljene for andre | «Tilbake» går aldri til `/rediger` eller `/avbryt`, men til «Mine oppdrag». Detaljene for andre er uendret | – |
| Invariant T1 (T-6) | alle sider i `SIDER` | fortsatt uten «serious»/«critical» og uten vannrett rulling ved 320 px | – |

</frozen-after-approval>

## Code Map

- `app/oppdrag/service.py` -- `KONFLIKT` (l. 50), `TIDSPUNKTET_ER_PASSERT` (l. 52), `OVERGANGER` med `hjelper_valgt → avbrutt` (l. 57–65), `utgatt` (l. 77), `endre_status` (l. 100–141, med `FinnesIkke` ved feil eier og ellers `Konflikt`). Valideringen i `opprett_oppdrag` (l. 181–224) må skilles ut, så redigering bruker den samme. `OppdragVisning` (l. 256), `hent_for_visning` (l. 292) og `merker_lagt_ut` (l. 325) brukes uendret.
- `app/oppdrag/models.py` -- `versjon` (l. 53) og `vesentlig_endret` (l. 56) finnes, også i `migrations/versions/0003_oppdrag.py` (l. 43, 46). Ingen migrering.
- `app/oppdrag/routes.py` -- `SKJEMAFELT` (l. 67), `GRUPPELENKER` (l. 80), `stegdata` (l. 223), `forhandsvisning` (l. 260), `_vis_skjema` (l. 282–308, fast `tittel=NYTT_OPPDRAG` og `fokus="beskrivelse"`), `ny`/`send_ny` (l. 311–352), `_tilbake_fra_detaljer` (l. 358–363, unntar bare `/oppdrag/ny`) og `detaljer` (l. 366–398).
- `app/oppdrag/templates/oppdrag/ny.html` -- action og `data-steg-skjema` (l. 24–25), `skjema_id` (l. 27), «Publiser» (l. 136) og `steg.js` (l. 143) er faste for «Nytt oppdrag». Resten er felles.
- `app/oppdrag/templates/oppdrag/detaljer.html` -- beskrivelsen (l. 27). Handlingene legges etter den, og blokken «Lagt ut av» (l. 28–33) gjelder bare andre.
- `app/oppdrag/templates/oppdrag/mine.html` -- `listerad__hoved` (l. 28–41). Kommentaren l. 10–11 beskriver plassen til `listerad__handlinger`.
- `app/core/feil.py` -- `Konflikt(melding, til_url)` (l. 74–84) har ingen handler (docstringen l. 14–15 sier 2.5). `registrer_feilhandlere` (l. 125–130) og `_duplikat` (l. 120) er mønsteret.
- `app/core/kvittering.py` -- `TEKSTER` (l. 19–22) har bare kvitteringer. Det finnes ingen feilmelding i cookien.
- `app/core/render.py` -- `fokusmal` (l. 139–145) har ikke trinnet «feilmelding» (EXPERIENCE: feiloppsummering > feilmelding > kvittering > eget mål). `render` (l. 178–222).
- `app/core/templates/core/makroer.html` -- `meldinger` (l. 21–43) har ikke `melding--feil` for konflikt. `handlingsmerke` (l. 83–88) gjenbrukes i detaljene. `bekreft_dialog` finnes ikke.
- `app/core/db.py` -- `lag_motor` med `BEGIN IMMEDIATE` (l. 60–89). AD-2 sier at «database is locked» blir `Konflikt` her, men det er ikke laget.
- `app/core/tid.py` -- `TIDSPUNKT_PASSERT` (l. 47) og `tolk_tidspunkt` (l. 164–198). Det finnes ingen funksjon som gjør et lagret tidspunkt om til skjemaverdiene «25.11.2026» og «09:00».
- `app/core/static/js/` -- `skjema.js` kobles på med `data-`-attributter og virker uendret. `steg.js` kobles på `form[data-steg-skjema]` og lastes bare fra `ny.html`. `sending.js` virker på alle skjema, også i dialogen. `dialog.js` finnes ikke.
- `app/core/templates/core/base.html` -- skriptene (l. 10–14).
- `app/core/static/css/app.css` -- `.knapp--primar`/`--sekundar` (l. 597–608), `.tekstknapp` (l. 620), `.skjema__knapper` (l. 640–653), `.melding--feil` (l. 677), `.listerad` og `__hoved` (l. 1096–1160) og tokenet `--shadow-dialog` (l. 109). Det finnes ingen stil for `dialog`.
- `app/seed.py` -- `EKSEMPELOPPDRAG` (l. 90–127) har allerede det utgåtte «Bære ved» og det avbrutte «Lufte hunden». Endres ikke.
- `tests/conftest.py` -- alle sesjoner deler én tilkobling (l. 87–120), så samtidighet syns ikke der. `motor` (l. 74) gir egne tilkoblinger. `TEST_DATABASE_URL` (l. 32) er Postgres i CI.
- `.github/workflows/ci.yml` -- jobben `test-postgres` kjører `uv run pytest` mot `postgres:17` med `TEST_DATABASE_URL`. T1 kjører mot SQLite.
- `tests/oppdrag/test_status.py` (mønsteret for `Konflikt`), `test_legge_ut.py` (`send`, l. 65), `test_mine_oppdrag.py` og `tests/e2e/test_t1.py` (`SIDER`, l. 224), `test_klientatferd.py` (uten JS l. 572, radflaten l. 723).

## Tasks & Acceptance

**Execution:**
- [ ] `app/core/tid.py` -- `skjemaverdier(tidspunkt) -> tuple[str, str]` gir «dd.mm.åååå» og «tt:mm» i norsk tid. En rundtur gjennom `tolk_tidspunkt` gir det samme tidspunktet, også over sommertidsskiftene -- AD-9
- [ ] `app/core/db.py` -- en kontekstbehandler som gjør `OperationalError` med «database is locked» om til `Konflikt(melding, til_url)`. Andre feil slipper gjennom -- AD-2
- [ ] `app/oppdrag/service.py` -- `valider_oppdrag(**felt)` skilles ut av `opprett_oppdrag`, som oppfører seg som før. `hent_eget_oppdrag(db, id, bruker_id, *, statuser) -> OppdragVisning` gir `FinnesIkke` når oppdraget ikke finnes eller har en annen eier, og `Konflikt` når status ikke er i `statuser`. `skjemaverdier_for(oppdrag) -> dict[str, str]`. `rediger_oppdrag(db, id, *, oppdragsgiver_id, **felt)`: valideringen først. Ved feil sjekkes tilgangen før `RegelBrudd`, så 404 og `Konflikt` går foran 422. Så én betinget `UPDATE` (se Design Notes) i kontekstbehandleren fra `db.py`. 0 rader gir `FinnesIkke` eller `Konflikt`. `avbryt_oppdrag(db, id, *, oppdragsgiver_id)` = `endre_status(fra=("apen", "hjelper_valgt"), til="avbrutt", …)`. Docstringen oppdateres -- FR-6, FR-7, FR-8, NFR-5, AD-2, AD-3
- [ ] `app/core/feil.py`, `app/core/kvittering.py`, `app/core/render.py`, `app/core/templates/core/makroer.html` -- handleren `_konflikt` gir 303 til `til_url` med feilmeldingen i den signerte cookien (bare faste nøkler). `render` gir den til malen, og `fokusmal` får trinnet `feilmelding`. `meldinger` viser `melding--feil` med teksten og lenken «Last siden på nytt» (`button-secondary`, `href` til siden selv). Nye kvitteringer: «Endringene er lagret.» og «Oppdraget er avbrutt.» -- §4.0, AD-2, UX-DR22, UX-DR27, spinen § Feil
- [ ] `app/core/templates/core/makroer.html` -- `bekreft_dialog(id, sporsmal, forklaring, handling, bekreft, angre, skjulte={})`: `<dialog>` med `aria-labelledby` til `h2` (`tabindex="-1"`), `aria-describedby` til forklaringen, og et POST-skjema med CSRF, skjulte felt, primærknappen og angreknappen (`<button type="button" class="tekstknapp" data-lukk-dialog>`) -- NFR-8, UX-DR18
- [ ] `app/core/static/js/dialog.js` (ny), `base.html` -- et klikk på `a[data-dialog]` åpner `<dialog id>` med `showModal()` og gir fokus til overskriften. Tab og Shift+Tab går rundt i dialogen. Esc og `[data-lukk-dialog]` lukker, og fokus går tilbake til lenken. Bare én dialog er åpen om gangen. Uten `showModal` følges lenken. Ingen regler, og tekst settes ikke med JS -- AR-28, UX-DR18
- [ ] `app/oppdrag/templates/oppdrag/skjema.html` (omdøpt fra `ny.html`), `app/oppdrag/routes.py` -- malen tar action, knappetekst, `skjema_id` og to steg som parametre. «Nytt oppdrag» er uendret. `GET /oppdrag/{id:int}/rediger` (`oppdrag.rediger`) og `POST` (`oppdrag.send_rediger`) bruker `hent_eget_oppdrag(statuser={"apen"})`, `tittel=f"Rediger «{tittel}»"`, `aktiv_meny="mine_oppdrag"`, `underside=True`, `fokus="dato"` bare når `fokus=tidspunkt` står i adressen, og «Tilbake» går til detaljene når `Referer` er skjemaet selv. `GET /oppdrag/{id:int}/avbryt` (`oppdrag.avbryt`) gir bekreftelsessiden `avbryt.html`, og `POST` (`oppdrag.send_avbryt`) avbryter. `_tilbake_fra_detaljer` unntar også `/rediger` og `/avbryt`. Docstringene oppdateres -- FR-6, FR-7, UX-DR7, UX-DR18, AR-28
- [ ] `app/oppdrag/templates/oppdrag/detaljer.html`, `mine.html`, `avbryt.html` (ny) -- handlingene etter beskrivelsen for eier og status `apen`: «Rediger» (lenke, sekundær) og «Avbryt oppdrag», eller `handlingsmerke` med «Endre tidspunkt» (lenke, primær) og «Avbryt oppdrag». «Avbryt oppdrag» er en lenke til bekreftelsessiden med `data-dialog`, og `bekreft_dialog` står i samme mal. Radene med merket får `listerad__handlinger` etter `listerad__hoved` med de to snarveiene (sekundære, `aria-describedby="rad-{id}-tittel"`) og en dialog per rad -- FR-7, FR-8, UX-DR18, UX-DR26
- [ ] `app/core/static/css/app.css` -- `.listerad__handlinger` (skillelinje 1 px `--color-border`, 16/24 px, `flex-wrap`), handlingene i detaljene, og `dialog` etter DESIGN.md § dialog (maks 480 px, full bredde minus 16 px marg på mobil, maks høyde `calc(100dvh - 32px)` med `overflow-y: auto`, `--shadow-dialog`, `::backdrop` i `scrim` med 55 % opasitet, knappene under hverandre under 768 px). I forced-colors får dialogen kant. Ingen vannrett rulling ved 320 px -- UX-DR18, NFR-6, NFR-7
- [ ] `README.md`, `EXPERIENCE.md` -- README forteller at Kari kan prøve «Endre tidspunkt» og «Avbryt oppdrag» på «Bære ved opp til tredje etasje». EXPERIENCE § Sidetitler får raden for bekreftelsessiden uten JS -- NFR-2, planleggingsdokumentene holdes oppdatert
- [ ] `tests/oppdrag/test_redigere_regler.py`, `test_redigere.py`, `test_avbryte.py` (nye), `tests/core/test_tid.py`, `tests/core/test_feil.py`, `tests/oppdrag/test_legge_ut.py`, `test_grunnsider.py` -- servicetester av `vesentlig_endret` (hver verdi som endres og ikke endres, `NULL` ↔ beløp), av `hent_eget_oppdrag`, av `avbryt_oppdrag` fra `hjelper_valgt`, og av «database is locked». HTTP-tester for hver rad i matrisen, med CSRF og uten. `opprett_oppdrag` og alle testene fra 2.1 er grønne -- FR-6, FR-7, FR-8, NFR-5, NFR-12, AD-2, AD-3
- [ ] `tests/oppdrag/test_samtidighet.py` (ny) -- to tråder med hver sin `Session` fra `motor` og `threading.Barrier`. Den første holder transaksjonen åpen et øyeblikk etter `UPDATE`-en, så den andre må vente (SQLite på låsen, Postgres på raden). Sjekker at nøyaktig én lykkes, og status og `versjon` etterpå. Radene er committet og slettes i `finally`. Kjøres mot SQLite lokalt og mot Postgres i `test-postgres` -- AD-2, §4.0
- [ ] `tests/e2e/test_t1.py`, `tests/e2e/test_klientatferd.py` -- nye sider i `SIDER`: `rediger-oppdrag`, `rediger-oppdrag-feil`, `endre-tidspunkt`, `oppdrag-detaljer-passert`, `avbryt-dialog` (detaljer og rad), `avbryt-bekreftelse`, `oppdrag-avbrutt` og `konflikt`. Klienttester: dialogen (fokus på spørsmålet, Tab og Shift+Tab går rundt, Esc og «Behold oppdraget» gir fokus tilbake til lenken), bekreftelse gir «Oppdraget er avbrutt.» i fokus, uten JS gir lenken bekreftelsessiden og POST virker, «Endre tidspunkt» gir fokus i «Dato» ved 360 og 1280 px, og to faner gir feilmeldingen i fokus, der «Last siden på nytt» laster siden uten meldingen -- NFR-6, NFR-7, SM-5, UX-DR18

**Acceptance Criteria:**
- Gitt Kari med seed, når hun velger «Endre tidspunkt» på «Bære ved opp til tredje etasje», skriver datoen i morgen og velger «Lagre endringer», så står «Endringene er lagret.» i detaljene, merket og tallet i menyen er borte, og Ola ser oppdraget i oversikten.
- Gitt en skjermleser på «Avbryt oppdrag» i raden, når den får fokus, så leses «Avbryt oppdrag» og så tittelen. Når dialogen åpnes, leses spørsmålet.
- Gitt `uv run pytest` lokalt og jobben `test-postgres` i CI, når testen med samtidige forespørsler kjøres, så lykkes nøyaktig én av de to handlingene i begge databasene.

## Implementation Notes

## Spec Change Log

## Review Triage Log

## Design Notes

- **Én `UPDATE` for redigering.** Endringen, `versjon` og `vesentlig_endret` skrives i samme setning, så det ikke blir et kappløp mellom lesing og skriving. `is_distinct_from` behandler `NULL` riktig i begge databasene:

  ```python
  endret = or_(Oppdrag.tidspunkt != ny.tidspunkt,
               Oppdrag.belop.is_distinct_from(ny.belop),
               Oppdrag.postnummer != ny.postnummer)
  update(Oppdrag).where(Oppdrag.id == id, Oppdrag.status == "apen",
                        Oppdrag.oppdragsgiver_id == eier)
      .values(tittel=…, …, versjon=Oppdrag.versjon + 1,
              vesentlig_endret=case((endret, na), else_=Oppdrag.vesentlig_endret))
  ```

  `WHERE` har ikke `tidspunkt > :na`, fordi et utgått oppdrag skal kunne endres (FR-8). Det nye tidspunktet sjekkes av `tolk_tidspunkt`.
- **Ingen `versjon` i skjemaet.** AD-2 og epic-konteksten har `id`, status og eier i `WHERE`, ikke versjonen. To redigeringer som begge er gyldige, lagres etter hverandre, og den siste gjelder. En redigering etter avbrudd gir `Konflikt`, som storyen krever.
- **Utsatt punkt fra 2.1** (`ikke_passert` gir en misvisende `Konflikt`): 2.5 berører det ikke, fordi verken redigering eller avbrudd bruker `ikke_passert`. Punktet blir stående til Epic 3.
- **Fokus.** «Endre tidspunkt» gir `autofocus` på «Dato» med `?fokus=tidspunkt`, fordi et fragment (`#dato`) ikke gir fokus til feltet. «Rediger» gir ingen `autofocus`, fordi EXPERIENCE § Fokus og opplesning bare flytter fokus i tilfellene som står der. Etter en feil får feiloppsummeringen fokus som før.
- **Passert tidspunkt.** Skjemaet viser de lagrede verdiene, også et passert tidspunkt. «Velg et nytt tidspunkt fram i tid» kommer ved lagring, som feilen under «Når?» (FR-6: «meldingen ved feltet», EXPERIENCE § Skjemafelt: feil vises etter innsending).
- **`h1` og `<title>`** har den lagrede tittelen, også ved 422 når tittelfeltet er endret, så siden ikke skifter navn før endringen er lagret. Det følger mønsteret der `h1` er `tittel` fra ruta.
- **Dialogen og bekreftelsessiden** har samme innhold: overskriften «Avbryte «{tittel}»?» og så «Det kan ikke angres.» som egen linje, som «Velge Amir?» i mockupen. Ordene er de samme som i EXPERIENCE. Uten JS er «Avbryt oppdrag» en lenke til `GET /avbryt`, der overskriften er `h1`, `<title>` er «Avbryte «{tittel}»? – Nabolagshelten» og «Behold oppdraget» er en lenke tilbake. Med JS stopper `dialog.js` lenken og åpner `<dialog>`, der «Behold oppdraget» er `<button>`. Lenken ser ut som en sekundærknapp (EXPERIENCE § button-secondary: «navigerer (som lenke)»). Et klikk på sløret lukker ikke dialogen, så den ikke lukkes ved et uhell.
- **Tab i dialogen.** `showModal()` gjør resten av siden inert, men om Tab går til nettleserens adresselinje, varierer mellom nettlesere. `dialog.js` lar derfor Tab gå rundt selv, så testen ikke er avhengig av nettleseren.
- **`Konflikt` og meldingen.** Cookien har en fast nøkkel, som kvitteringen, så den aldri kan vise annen tekst. «Last siden på nytt» er en lenke til den samme adressen. Siden lastes da uten melding, fordi cookien er slettet. Ved `GET /rediger` på et oppdrag som ikke er Åpen, gir den samme handleren 303 til detaljene, som viser gjeldende status.
- **Avbryte fra Hjelper valgt** er lov i servicen nå (FR-7, `OVERGANGER`) og testes der. Knappene for den statusen kommer i Epic 3.
- **`fra=mine`** (hvis spørsmål 1 blir (a)) er den eneste verdien som godtas. Alt annet gir detaljene, så adressen aldri kan sende brukeren til en annen side.

## Verification

**Commands:**
- `uv run pytest` -- forventet: alle tester er grønne, også `test_arkitektur.py` (rutenavnene `oppdrag.rediger`, `send_rediger`, `avbryt`, `send_avbryt`), de nye testene for redigering, avbrudd og samtidighet (SQLite), og invariantene fra 2.1–2.4. Postgres-varianten kjøres av jobben `test-postgres` i CI, fordi det ikke finnes Docker lokalt.
- `uv run pytest -m e2e` -- forventet: T1 er grønn for alle sider i `SIDER` ved 360 og 1280 px og uten vannrett rulling ved 320 px, også med dialogen åpen. Klienttestene er grønne, også de fra 1.5 og 2.2–2.4.

**Manual checks (if no CLI):**
- [ ] Tastatursjekk av redigeringsskjemaet, «Endre tidspunkt», dialogen (fokus inn, Tab, Esc og fokus tilbake) og bekreftelsessiden uten JS, i cirka fem minutter (DoD, T2). **Utsatt til story 6.1** (retro T-5): den autonome kjøringen har ingen manuell tester, og T1 og klienttestene dekker de automatiske kravene. Storyen kan settes `done` med denne utsettelsen.
