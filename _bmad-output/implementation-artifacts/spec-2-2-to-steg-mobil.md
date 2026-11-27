---
title: 'Story 2.2: Nytt oppdrag i to steg på mobil, med forhåndsvisning'
type: 'feature'
created: '2026-11-27'
status: 'in-progress'
baseline_commit: 'acfb9692bf1132cb3d7136eb5d0e33d395b0c5fb'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-2-context.md'
  - '{project-root}/_bmad-output/planning-artifacts/ux-designs/ux-G22-bernardo-kverno-moystad-nguyen-2026-11-07/EXPERIENCE.md'
  - '{project-root}/_bmad-output/planning-artifacts/ux-designs/ux-G22-bernardo-kverno-moystad-nguyen-2026-11-07/mockups/key-nytt-oppdrag.html'
  - '{project-root}/_bmad-output/planning-artifacts/ux-designs/ux-G22-bernardo-kverno-moystad-nguyen-2026-11-07/mockups/key-nytt-oppdrag-steg2.html'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** «Nytt oppdrag» fra 2.1 er én lang skjerm, også på mobil. Det finnes ingen forhåndsvisning av kortet, og «Beløp i kr» vises selv når «Uten betaling» er valgt (FR-5, NFR-6, NFR-7, UX-DR13, UX-DR15, UX-DR16).

**Approach:** Serveren rendrer fortsatt ett skjema på én skjerm, nå med to `section` og hver sin `h2`, og en forhåndsvisning rett over «Publiser». Den nye `steg.js` deler skjemaet i to steg under 768 px. Forhåndsvisningen ligger i `skjema.js`, og «Beløp i kr» skjules med CSS `:has(:checked)` (AR-28). Ruta, reglene og databasen endres ikke.

**Beslutninger (anbefalt alternativ, delegert av Heidi 2026-11-26):**
- `h2` «Hva trenger du hjelp til?» står ordrett fra EXPERIENCE.md, selv om etiketten under har samme tekst på én skjerm. EXPERIENCE gjelder ordrett, og det bryter ikke WCAG.
- Forhåndsvisningen viser dato og klokkeslett slik brukeren skrev dem («25.11.2026 kl. 7»), ikke «I morgen kl. 07:00» som i mockupen. Arkitekturen forbyr formatering av tid i JS.
- Specen beholdes samlet (cirka 4 100 tokens), fordi storyen er ett mål.

## Boundaries & Constraints

**Always:** Tekstene er ordrett fra EXPERIENCE.md: «Nytt oppdrag 1 av 2» og «Nytt oppdrag 2 av 2», «Neste», «Tilbake til steg 1», `<title>` «Nytt oppdrag, steg 1 av 2 – Nabolagshelten» og «Nytt oppdrag, steg 2 av 2 – Nabolagshelten» (med «Feil: » foran ved feil), `h2` «Hva trenger du hjelp til?» og «Når og hvor?», og «Slik vises oppdraget for andre.». Steg 1 har beskrivelse, tittel og kategori. Steg 2 har postnummer, «Når?», «Hva tilbyr du?», forhåndsvisningen, «Publiser» og «Tilbake til steg 1». Feltrekkefølgen, feltnavnene og `skjema_id` i DOM-en er som i 2.1, og alt ligger i ett `<form>`. Ved stegbytte får `h1` fokus. «Neste» sjekker bare om beskrivelse, tittel eller kategori er tomme, med feiltekstene som serveren legger i malen. Alle andre regler sjekkes av serveren ved «Publiser». Forhåndsvisningen har stiplet kant, ingen lenke, ingen overskrift og ingen `aria-live`, og tomme felt vises som «–». JS setter tekst bare med `textContent`. Steget som ikke vises, har `hidden`. Krav-ID-er står i commits og tester.

**Never:** KI («Få forslag», Epic 5), `fokus.js` og oppdragslista med kortene som lenker (2.3), lagring av utkast (2.6), egne URL-er eller POST per steg, at serveren ser på skjermbredde eller user-agent, regler i JS utover tomme felt, formatering av tidspunkt i JS, `innerHTML`, `|safe`, `maxlength`, `role` på feiloppsummeringen, endring av `opprett_oppdrag` og feiltekstene, migrering, og flytting av `poststed.js` eller `vis_passord.js`.

## I/O & Edge-Case Matrix

Klokka står fast på tirsdag 24.11.2026 kl. 13:00 norsk tid (`FAST_KLOKKE`). «Mobil» er 360 px med JS, og «én skjerm» er 768 eller 1280 px, eller uten JS.

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Mobil, steg 1 | GET `/oppdrag/ny` | `h1` «Nytt oppdrag 1 av 2», tittelen for steg 1, beskrivelse, tittel, kategori og «Neste» vises. Steg 2 og begge `h2` er skjult, og `autofocus` står på beskrivelsen | – |
| «Neste» med tomme felt | tittel med bare mellomrom, ingen kategori | Ingen forespørsel. «Skjemaet har 2 feil» med «Skriv en tittel.» og «Velg en kategori.» står rett etter `h1` og får fokus. Feltfeil og `aria-invalid` vises ved feltene, og tittelen får «Feil: » foran | blir i steg 1 |
| «Neste» gyldig | steg 1 utfylt | steg 2 vises, `h1` «Nytt oppdrag 2 av 2» får fokus, og `<title>` byttes. Ingen forespørsel | – |
| Tilbake og Enter | «Tilbake til steg 1» / Enter i Tittel i steg 1 | alt utfylt beholdes, og `h1` for steg 1 får fokus / virker som «Neste», uten POST. «Publiser» virker etterpå og får `aria-disabled` | – |
| Serverfeil i begge steg | tittel `ab` (slipper gjennom «Neste»), dato tom | 422. Oppsummeringen lister «Tittelen må ha minst 3 tegn.» og «Skriv datoen.», og steg 1 vises. Lenken til datoen bytter til steg 2 og gir fokus til `#dato` | – |
| Serverfeil i steg 2 | bare «Hva tilbyr du?» mangler | steg 2 vises med oppsummeringen i fokus | – |
| Én skjerm | 768/1280 px, eller uten JS | `h1` «Nytt oppdrag», `h2` «Hva trenger du hjelp til?» og «Når og hvor?», «Nytt oppdrag – Nabolagshelten». «Neste» og «Tilbake til steg 1» er skjult, og forhåndsvisningen vises | – |
| Bredden endres | mobil steg 2 → 900 px → 360 px | én skjerm, og så steg 1 igjen. Verdiene beholdes | – |
| Forhåndsvisning tom | GET | kategori «–», tittel «–», tid «–», «0571 Oslo», pris «–» | – |
| Forhåndsvisning utfylt | Snømåking, «Måke snø», `25.11.2026` og `7`, `5006`, Beløp `1000` / «Uten betaling» | kategorimerke med ikon, «Måke snø», «25.11.2026 kl. 7», «5006 Bergen», «1 000 kr» / «Uten betaling». Ingenting leses opp | – |
| «Beløp i kr» | ingen valgt / «Beløp» / `200`, så «Uten betaling» og tilbake | skjult / vises, og fokus blir på radioknappen / `200` står der fortsatt. Det samme gjelder uten JS | – |
| Invariant 2.1 (T-6) | samme `skjema_id` to ganger, også via dobbeltklikk | én rad, og den andre gir 303 til samme oppdrag | `Duplikat` |
| Invariant 2.1 (T-6) | tom POST rett mot serveren | «Skjemaet har 6 feil», verdiene og `skjema_id` beholdes, og ingen rad lagres | 422 |
| Invariant: serveren avgjør (T-6) | tittel `ab`, beløp `abc` gjennom stegene / POST uten stegene | samme feil og samme svar fra serveren | 422 |
| Invariant XSS (T-6) | `<script>alert(1)</script>` i tittel | vises som tekst i forhåndsvisningen, både fra serveren og fra JS | – |
| Invariant skjema 2.1 (T-6) | GET | ett `autofocus`, «Mine oppdrag» med `aria-current="true"`, ingen `"page"`, ingen `maxlength`, telleren virker, og ingen feltnavn begynner med `_` (AD-7) | – |
| Invariant 1.2/1.4 (T-6) | innlogging og registrering | knappen får `aria-disabled` ved innsending, og `5006` gir «Bergen» | – |
| Invariant T1 (T-6) | alle sider i `SIDER` | fortsatt uten «serious»/«critical» og uten vannrett rulling ved 320 px | – |

</frozen-after-approval>

## Code Map

- `app/oppdrag/templates/oppdrag/ny.html` -- skjemaet fra 2.1. «Tilbake» (l. 14), `<h1>Nytt oppdrag</h1>` uten attributter (testen i `test_legge_ut.py` l. 96 matcher strengen eksakt), `belopfelt` mellom de to radioknappene (l. 89–111, så `:has` virker), og «Publiser» (l. 114).
- `app/oppdrag/routes.py` -- `_vis_skjema` (l. 103) gir konteksten, og `GRUPPELENKER` (l. 55) og `SKJEMAFELT` (l. 42) brukes. `send_ny` og `ny` endres ikke, bortsett fra konteksten.
- `app/oppdrag/service.py` -- `SKRIV_BESKRIVELSE`, `SKRIV_TITTEL` og `VELG_KATEGORI` (l. 34–39) er tekstene «Neste» bruker. Ruta sender dem til malen. `opprett_oppdrag` endres ikke.
- `app/core/render.py` -- `sidetittel(tittel, feil=)` (l. 79) lager titlene for stegene, og `render(..., underside)` (l. 124).
- `app/core/domene.py` -- `kr` (l. 81) er formatet som JS etterligner for beløp (NBSP som tusenskille og før «kr»). `KATEGORIER` og `kategori_tekst` brukes også.
- `app/core/templates/core/makroer.html` -- markupen i `meldinger(lenker)` (l. 21) kopieres av klienten: `#feiloppsummering`, `tabindex="-1"`, `h2.melding__overskrift` og ingen `role`. Også `feltfeil` (l. 9), `kategoriikon` (l. 74) og `kategorimerke` (l. 87). Den nye makroen `oppdragskort` legges her.
- `app/core/templates/core/base.html` -- skriptene l. 10–13. `steg.js` legges til.
- `app/core/static/js/skjema.js` -- telleren. Forhåndsvisningen legges til her (AR-28).
- `app/core/static/js/poststed.js` -- flyttes ikke. Den skriver poststedet i `#postnummer-sted`, og forhåndsvisningen leser det derfra.
- `app/core/static/js/sending.js` -- l. 121–133 merker skjemaet også når en annen lytter har kalt `preventDefault()`. Enter i steg 1 ville da låse «Publiser».
- `app/core/static/css/app.css` -- har ingen regel for `[hidden]`, mens `.knapp`, `.skjema__knapper`, `.felt` og `.skjema` setter `display`. Også `.belopfelt` (l. 868), mønsteret `.kategoriknapp:has(:checked)` (l. 790) og `.kategorimerke`, `.fakta`, `.pris` (fra l. 885), som kan brukes i kortet.
- `app/core/static/postnumre.json` -- finnes og serveres på `/static/postnumre.json` (testet i `tests/identity/test_registrering.py` l. 148, og mot TSV i `tests/core/test_postnummer.py` l. 82).
- `tests/oppdrag/test_legge_ut.py` -- rekkefølgen (l. 90), menyen (l. 165), `autofocus` (l. 175) og `GRUPPELENKER` (l. 37).
- `tests/e2e/conftest.py` -- `fyll_ut_nytt_oppdrag` (l. 159) fyller alt på én skjerm og feiler ved 360 px.
- `tests/e2e/test_t1.py` -- ved 360 px feiler tre hjelpere: `nytt_oppdrag` (l. 103) forventer `h1` «Nytt oppdrag», `nytt_oppdrag_feil` (l. 109) klikker «Publiser», som er skjult, og `oppdrag_detaljer` (l. 117) bruker `fyll_ut_nytt_oppdrag`. Se også `SIDER` (l. 132) og `BREDDER_AXE` (l. 25, uten 768).
- `tests/e2e/test_klientatferd.py` -- `test_dobbeltklikk_pa_publiser_gir_ett_oppdrag` (l. 179) kjører på standardvisningen (1280 px).
- `tests/core/test_arkitektur.py` -- forbyr `innerHTML` også i `.js`. Skal ikke endres.

## Tasks & Acceptance

**Execution:**
- [ ] `app/core/templates/core/makroer.html` -- makroen `oppdragskort(kategori, tittel, tid, sted, pris, forhandsvisning=False)`: kategorimerke, tittel, fakta med klokke- og stedikon, og pris. Med `forhandsvisning=True` er tittelen en `p` med samme stil som `h2`, og hver verdi har `data-felt`. 2.3 bruker makroen med lenke og `h2` -- UX-DR15
- [ ] `app/oppdrag/templates/oppdrag/ny.html`, `app/oppdrag/routes.py` -- to `section` med `data-steg="1"` og `"2"`, og hver sin `h2`. Knappene «Neste» (`type="button"`, primær) og «Tilbake til steg 1» (`button-text`) rendres med `hidden`. Overskriftene og titlene for stegene, både med og uten «Feil: », legges i `data-`-attributter og lages med `sidetittel`. Tekstene for tomme felt ligger på feltene. Forhåndsvisningen er en `section` med `aria-labelledby` til teksten «Slik vises oppdraget for andre.» og `oppdragskort(..., forhandsvisning=True)`, rett over knappene. Ruta lager startverdiene til forhåndsvisningen fra `verdier` med de samme reglene som JS (se Design Notes) -- FR-5, UX-DR15, UX-DR16
- [ ] `app/core/static/js/steg.js` (ny), `base.html` -- `matchMedia("(max-width: 47.99em)")` med lytter på `change`. Skriptet bytter `hidden` på seksjonene, `h2` og knappene, og setter `h1`-tekst, `tabindex="-1"` og `document.title` fra `data-`-attributtene. Det har også sjekken av tomme felt ved «Neste». Enter i steg 1 kaller `preventDefault()` og virker som «Neste». Ved sidelasting med feil vises steget som har feltet i den første lenken i oppsummeringen. Et klikk på en lenke til et felt i det andre steget bytter steg og gir feltet fokus -- AR-28, UX-DR16, UX-DR22, UX-DR27
- [ ] `app/core/static/js/skjema.js` -- forhåndsvisningen oppdateres ved `input` og `change` i skjemaet, ved endring i `#postnummer-sted` (`MutationObserver`), ved oppstart og ved `pageshow`. Kategoriikonet klones fra den valgte kategoriknappen -- UX-DR15, AR-28
- [ ] `app/core/static/js/sending.js` -- returnerer straks når `hendelse.defaultPrevented` er sann -- UX-DR28
- [ ] `app/core/static/css/app.css` -- `[hidden] { display: none !important; }`. `.belopfelt` skjules når «Beløp» ikke er valgt (`fieldset:has(#tilbud-belop:not(:checked))`). Forhåndsvisningskortet får `card`-tokens med 1,5 px stiplet `--color-border`, uten skygge for hover. Seksjonene får samme avstand som `.skjema` -- UX-DR13, UX-DR15, DESIGN.md § Forhåndsvisning
- [ ] `tests/oppdrag/test_to_steg.py` (ny), `tests/oppdrag/test_legge_ut.py` -- HTTP-tester av HTML-en uten JS: `h1` og to `h2` i rekkefølge, hvilke felt som ligger i hvert `data-steg`, «Neste» og «Tilbake til steg 1» med `hidden`, at tekstene i `data-` er lik konstantene i `service.py` og titlene lik `sidetittel`, og forhåndsvisningen tom, etter 422 og med XSS escaped. Rekkefølgetesten oppdateres, og invariantradene fra 2.1 består -- FR-5, NFR-5, NFR-12, UX-DR15, UX-DR16
- [ ] `tests/e2e/conftest.py`, `tests/e2e/test_t1.py` -- `fyll_ut_nytt_oppdrag` og hjelperne i T1 trykker «Neste» når knappen er synlig. Nye sider i `SIDER`: `nytt-oppdrag-steg-2`, og `nytt-oppdrag-feil` med feil i begge steg. En egen T1-test kjører «Nytt oppdrag» på én skjerm ved 768 px -- NFR-6, NFR-7, SM-5
- [ ] `tests/e2e/test_klientatferd.py` -- klienttester for radene i matrisen som trenger nettleser: «Neste» med tomme felt (ingen POST, fokus på oppsummeringen), «Neste» og «Tilbake» (fokus på `h1`, `document.title`), Enter i steg 1, steget med første serverfeil og lenken som bytter steg, endring av bredde, forhåndsvisningen (også poststed, beløp og at den ikke har `aria-live`), «Beløp i kr» (fokus og verdi), én skjerm i en kontekst med `java_script_enabled=False`, og `aria-disabled` på innloggingsknappen -- NFR-7, UX-DR13, UX-DR15, UX-DR16, UX-DR27, UX-DR28
- [ ] `README.md` -- statuslinja (l. 24) nevner 2.2 -- NFR-2

**Acceptance Criteria:**
- Gitt mobil med JS, når Kari fyller ut steg 1, trykker «Neste», fyller ut steg 2 og trykker «Publiser», så havner hun på detaljene med «Oppdraget er lagt ut.» i fokus, og databasen har én rad.
- Gitt steg 2 eller den nederste delen på én skjerm, når feltene endres, så viser forhåndsvisningen de nye verdiene uten at fokus flyttes og uten opplesning.
- Gitt T1, når `uv run pytest -m e2e` kjøres, så er steg 1, steg 2 og én skjerm (768 px) uten «serious»/«critical» og uten vannrett rulling ved 320 px.

## Implementation Notes

## Spec Change Log

## Review Triage Log

## Design Notes

- **Ett skjema, to visninger (reconcile-ux H2):** serveren vet ikke skjermbredden, så HTML-en er alltid én skjerm, og `steg.js` gjør om på den. Uten JS står «Neste» og «Tilbake til steg 1» med `hidden`, så de aldri vises. I steg-visningen er begge `h2` skjult, fordi mockupen for steg 1 går rett fra `h1` til etiketten. «Tilbake» øverst vises bare i steg 1 (mockupen for steg 2 har den ikke). Teksten for `h1` og `<title>` kommer fra `data-`-attributter som serveren skriver, så tekstene bare står i malen.
- **«Neste»:** «hvis noe mangler» i akseptansekriteriet betyr tomme felt (etter `trim()`) og ingen kategori, ikke lengder. Klienten setter inn den samme markupen som `meldinger()` og `feltfeil()` lager, og erstatter en eventuell oppsummering. Finnes det ingen tomme felt, står en oppsummering fra serveren urørt til neste innsending.
- **Bredden endres:** går skjermen til én skjerm, vises alt. Går den tilbake under 768 px, vises steg 1, eller steget med første feil hvis siden har feil. Fokus flyttes ikke ved et slikt bytte.
- **Forhåndsvisningen (spinen § Klientatferd):** dato og klokkeslett vises slik brukeren skrev dem, som «{dato} kl. {klokkeslett}», og «–» hvis ett av dem er tomt. Mockupen viser «I morgen kl. 07:00», men spinen gjelder, fordi formatering av tid i JS ville vært en ny kopi av `core/tid.py`. Beløp: tomt eller ingen «Hva tilbyr du?» gir «–», «Uten betaling» gir «Uten betaling», og bare sifre (mellomrom fjernet) formateres som `kr` med `Intl.NumberFormat("nb-NO")` og NBSP. Annen tekst vises som den er, med « kr» etter. Sted: «{postnummer} {poststed}», bare nummeret når poststedet mangler, og «–» når feltet er tomt. Kategori og tittel vises med «–» når de er tomme.
- **Startverdiene fra serveren** følger de samme reglene, så siden ikke hopper når JS starter. `skjema.js` regner ut alt på nytt ved oppstart.
- **Duplisert tekst:** `h2` «Hva trenger du hjelp til?» står rett over etiketten med samme tekst på én skjerm. Det er ordrett fra EXPERIENCE.md, og det er ikke et brudd på WCAG.

## Verification

**Commands:**
- `uv run pytest` -- forventet: alle tester er grønne, også `test_arkitektur.py`, de nye testene i `test_to_steg.py` og invariantene fra 2.1 i `test_legge_ut.py`.
- `uv run pytest -m e2e` -- forventet: T1 er grønn for alle sider i `SIDER`, både de gamle og de nye, ved 360 og 1280 px og 768 px for én skjerm, uten vannrett rulling ved 320 px. Klienttestene er grønne, også dobbeltklikk, telleren og poststed.

**Manual checks (if no CLI):**
- [ ] Tastatursjekk av «Nytt oppdrag» i to steg og på én skjerm i cirka fem minutter (DoD). **Utsatt til story 6.1** (retro T-5): den autonome kjøringen har ingen manuell tester, og T1 og klienttestene dekker de automatiske kravene. Storyen kan settes `done` med denne utsettelsen.
