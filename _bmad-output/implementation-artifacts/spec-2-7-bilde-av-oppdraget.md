---
title: 'Story 2.7: Bilde av oppdraget'
type: 'feature'
created: '2026-11-27'
status: 'done'
baseline_commit: '0b9d8a36738f654c003f0d3531398ebd2b0b8223'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-2-context.md'
  - '{project-root}/_bmad-output/planning-artifacts/ux-designs/ux-G22-bernardo-kverno-moystad-nguyen-2026-11-07/EXPERIENCE.md'
  - '{project-root}/_bmad-output/planning-artifacts/ux-designs/ux-G22-bernardo-kverno-moystad-nguyen-2026-11-07/DESIGN.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Oppdragsgiveren kan bare beskrive oppdraget med tekst, så hjelperen må gjette hvor stor jobben er (FR-27). Appen kan heller ikke ta imot filer i dag: CSRF-mellomvaren avviser kropper over 1 MB med 413, Starlette avviser tekstfelt over 1 MB i multipart, rutene får bare tekstfelt (`request.state.skjema`), og `HeaderMellomvare` overskriver all `Cache-Control` med `no-store`.

**Approach:** Ett valgfritt bilde per oppdrag i ny tabell `oppdragsbilde` (migrering 0004), behandlet bare av `oppdrag/bilde.py` med Pillow (AD-18). Mellomvaren legger filene i `request.state.filer` som bytes, og tekstfeltene står i `request.state.skjema` som før. Skjemaet fra 2.1/2.5 får «Bilde (valgfritt)» og «Hva viser bildet?» i steg 1 rett etter beskrivelsen. Et gyldig bilde beholdes ved 422 som `bilde_beholdt` (base64) med miniatyr og «Fjern bildet». Ved redigering vises gjeldende bilde med «Bytt bilde» og «Fjern bildet». Detaljene viser bildet med bildeteksten som `alt`, og kortet i oversikten viser miniatyren øverst med `alt=""`. `GET /oppdrag/{id}/bilde` og `/bilde/liten` følger tilgangsregelen i FR-9. `bilde.js` skalerer ned i nettleseren før innsending. Seed tegner 4 bilder.

**Beslutninger (anbefalt alternativ, delegert av Heidi 2026-11-26):**
- **Pillow 13.0.x (`pillow~=13.0.0`), ikke 12.x.** Siste 12.x (12.3.0) har over 50 kjente sårbarheter på PyPI, som alle er rettet i 13.0.0 (16.10.2026). Flere gjelder akkurat det appen gjør med filer fra brukere: JPEG-dekoderen, PNG-eXIf (DoS) og APNG-allokering før bombe-sjekken. 13.0.0 har wheels for cp311 og cp312 på manylinux x86_64 (Vercel og CI) og win_amd64. Stack-raden i spinen endres til 13.x, og endringen føres i `.memlog.md`.
- **Bildene i seed:** «Måke snø i innkjørselen» (Kari, snømåking), «Mate katten i helgen» (Nora, dyrepass), «Flytte sofa ned i kjelleren» (Nora, bærehjelp) og «Klippe hekken» (Sofie, hage). Ola i 0571 ser da to kort med bilde og to uten. Kari kan prøve «Bytt bilde» og «Fjern bildet» på sitt eget oppdrag.
- **Grensene:** 4 MB betyr 4 × 1024 × 1024 byte, og 40 megapiksler betyr bredde × høyde > 40 000 000. Kroppsgrensen for multipart blir 5 MiB, så en fil litt over 4 MB får vår egen melding. Grensen for urlencoded forblir 1 MB.
- **Når «Hva viser bildet?» vises:** feltet er skjult til en fil er valgt, og `bilde.js` viser det. Uten JS står feltet alltid synlig. Med et beholdt eller lagret bilde rendrer serveren det synlig. CSS `:has()` kan ikke se om et valgfritt filfelt har en fil, så EXPERIENCE.md rettes til denne mekanismen.
- **Specen beholdes samlet** (cirka 6 000 tokens), fordi storyen er ett mål.

## Boundaries & Constraints

**Always:** Tekstene står ordrett fra EXPERIENCE.md: «Bilde (valgfritt)», «Ikke vis husnummer, bilskilt, navn eller ansikter.», «JPEG, PNG eller WebP, høyst 4 MB.», «Hva viser bildet?», «Fjern bildet», «Bytt bilde», og feiltekstene «Velg et bilde i JPEG, PNG eller WebP.», «Bildet er for stort. Velg et bilde på høyst 4 MB.», «Bildet har for mange piksler. Velg et mindre bilde.», «Skriv hva bildet viser.», «Teksten må ha minst 3 tegn.» og «Teksten kan ha høyst 120 tegn.». Bare `oppdrag/bilde.py` åpner opplastede filer og `bilde_beholdt`, og PIL importeres bare der og i `app/seed.py`. Formatet bestemmes av innholdet med `Image.open(formats=["JPEG", "PNG", "WEBP"])`, aldri av filnavn eller `Content-Type`. Størrelsen sjekkes før åpning, og pikslene før dekoding. Resultatet er alltid en ny JPEG uten EXIF, GPS og andre metadata, snudd etter EXIF-orienteringen, aldri forstørret, høyst 1 600 px, med en miniatyr på høyst 640 px. Bildeteksten normaliseres som andre tekstfelt (AD-10) og har teller med `data-maks="120"` uten `maxlength`. Bildefeilene vises sammen med de andre feltfeilene i feltrekkefølgen beskrivelse, bilde, bildetekst, tittel, … (NFR-10). Bilderutene bruker `hent_for_visning`, så tilgangsregelen og 404 er de samme som for detaljene. Endring av bildet setter aldri `vesentlig_endret`. Skriving til `oppdragsbilde` kommer etter den betingede `UPDATE`-en (AD-2), og barn slettes eksplisitt, uten `ON DELETE CASCADE`. Lister og kort leser aldri binærkolonnene. POST-ruter kjører `with db.begin():`, services committer aldri (AD-17), og malene får bare dataklasser (AD-16). Alt virker uten JS (AR-28). Krav-ID-er står i commits og tester.

**Never:** Flere bilder per oppdrag, bilde i radene under «Mine oppdrag», lenke eller zoom på bildet i detaljene, plassholder for kort uten bilde, lagring av originalfila, filsystem eller Supabase Storage, regler i JS (JS avviser aldri en fil), `innerHTML` og `|safe`, felt som begynner med `_` (AD-7), 401-siden med «Velg bildet på nytt etter innlogging.» (story 2.6), sletting av konto og oppdrag (4.5), KI (Epic 5), endring av `vesentlig_endret`-reglene, `skjema_id`, stegene eller `OVERGANGER`, og høyere kroppsgrense for urlencoded.

## I/O & Edge-Case Matrix

Klokka står fast (`FAST_KLOKKE`) og seed er lastet. Testbildene lages i minnet med Pillow (`tests/bilder.py`).

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Nytt med bilde | Kari, JPEG 3000×2000 med EXIF-orientering 6 og GPS, «Snø i innkjørselen» | 303 og «Oppdraget er lagt ut.». Raden har en JPEG på 1067×1600 (snudd) og en miniatyr på høyst 640 px, og `getexif()` er tom for begge. Detaljene har `<img alt="Snø i innkjørselen" width height>` under tittelen. Olas kort har miniatyren øverst med `alt=""`, `loading="lazy"` og `?v=` | – |
| Andre formater | PNG med gjennomsiktighet, WebP, animert WebP, CMYK-JPEG | lagres som RGB-JPEG. Gjennomsiktige områder blir hvite, og animasjoner gir første bilde | – |
| Lite bilde | 300×200 | lagres som 300×200 og forstørres ikke | – |
| Uten bilde | som i 2.1, med eller uten bildetekst | ingen rad i `oppdragsbilde` og ingen `<img>` i kort eller detaljer. Bildeteksten ignoreres | – |
| Feil format | tekstfil og SVG som heter `bilde.jpg`, GIF, avkuttet JPEG | 422 med «Velg et bilde i JPEG, PNG eller WebP.» ved `#bilde` (`aria-invalid`, lenke i oppsummeringen). De andre feltene og bildeteksten beholdes, ingen feil vises ved bildeteksten, og ingenting lagres | `RegelBrudd` |
| For stor fil | 4 MiB + 1 byte | «Bildet er for stort. Velg et bilde på høyst 4 MB.», sjekket før åpning | `RegelBrudd` |
| For mange piksler | PNG på 7000×6000 i modus «1» (liten fil) | «Bildet har for mange piksler. Velg et mindre bilde.». Dekodes ikke. 40 000 000 piksler godtas | `RegelBrudd` |
| Bildetekst mangler | gyldig bilde, og bildeteksten er tom, «ab» eller 121 tegn | 422 med feilen ved «Hva viser bildet?». Bildet vises som miniatyr (`data:`) med «Fjern bildet», og `bilde_beholdt` følger med | `RegelBrudd` |
| Beholdt sendt på nytt | `bilde_beholdt` og gyldige felt | 303, og oppdraget lagres med bildet | – |
| Beholdt fjernet | `bilde_beholdt` og `fjern_bilde` | 303, og oppdraget lagres uten bilde | – |
| Forfalsket beholdt | `abc`, base64 av tekst eller SVG, base64 av over 4 MiB | «Velg et bilde i JPEG, PNG eller WebP.» eller «Bildet er for stort …» | `RegelBrudd` |
| Ny ugyldig fil og gyldig beholdt | begge sendt | feilen ved `#bilde`. Det beholdte bildet står fortsatt med «Fjern bildet» | `RegelBrudd` |
| Kroppsgrense | multipart over 5 MiB, eller urlencoded over 1 MB | 413-feilsiden. Ruta kalles ikke | 413 |
| Hente bildet | Ola, GET `/oppdrag/{id}/bilde` og `/bilde/liten` på Karis åpne oppdrag | 200 `image/jpeg` med `Cache-Control: private, max-age=31536000, immutable` og `nosniff` | – |
| Ingen tilgang | Ola på Karis avbrutte oppdrag, id 999999, id 0, oppdrag uten bilde | samme 404 som `/oppdrag/999999`. Oppdragsgiveren får 200 på sitt avbrutte | `FinnesIkke` |
| Uten innlogging | GET `/oppdrag/{id}/bilde` | 303 til `/logg-inn?neste=…` (FR-3) | – |
| Bytte bilde | Kari, «Rediger» på «Måke snø», ny fil | 303 og «Endringene er lagret.». Nytt bilde, `versjon` + 1, ny `?v=`, og `vesentlig_endret` er uendret | – |
| Fjerne bilde | Kari, `fjern_bilde` | raden er slettet, detaljene og kortet har ingen `<img>`, og `vesentlig_endret` er uendret | – |
| Bare bildetekst | Kari endrer «Hva viser bildet?» | teksten er oppdatert, og bildet og `vesentlig_endret` er uendret | – |
| Urørt bilde | Kari endrer bare tittelen | bildet beholdes. En tom bildetekst gir «Skriv hva bildet viser.» | `RegelBrudd` |
| Fjern og ny fil | `fjern_bilde` og en gyldig fil | den nye fila erstatter bildet | – |
| Andres eller ikke Åpen | Ola, eller status `avbrutt`, POST `/rediger` med fil | 404 eller `Konflikt` som i 2.5. Bildet er uendret | `FinnesIkke`, `Konflikt` |
| Dobbel innsending | samme `skjema_id` og bilde to ganger | `Duplikat`, og bare én rad i `oppdrag` og én i `oppdragsbilde` | `Duplikat` |
| XSS | `<script>alert(1)</script>` som bildetekst | står som tekst i `alt` i detaljene og i feltverdien ved 422 (NFR-12) | – |
| Seed | `python -m app.seed` to ganger, og `last_eksempeldata` | 4 oppdrag har bilde, i fire kategorier. Andre kjøring feiler ikke på fremmednøkkelen | – |
| Invariant 2.1/2.2 (T-6) | «Nytt oppdrag» uten bilde, også urlencoded som i de gamle testene | uendret: `skjema_id`, `Duplikat`, «Neste» krever ikke bilde, og steg.js viser steget med første feil. `test_to_steg.py` er grønn | – |
| Invariant 2.3/2.4/2.5 (T-6) | kort og detaljer uten bilde, «Mine oppdrag», redigering uten bilde | uendret. Radene har aldri bilde, og reglene for `vesentlig_endret`, `Konflikt` og 404 fra 2.5 holder | – |
| Invariant 1.x (T-6) | multipart uten CSRF, andre GET-svar, FR-3 | 403 uten CSRF også med fil. Alle svar unntatt bilderutene og `/static/` har `no-store`. Bilderutene følger FR-3 | – |
| Invariant T1 (T-6) | alle sider i `SIDER` | fortsatt uten «serious» eller «critical» og uten vannrett rulling ved 320 px | – |

</frozen-after-approval>

## Code Map

- `app/core/csrf.py` -- `MAKS_KROPP` = 1 MB (l. 30) gjelder alle kropper. `_les_kropp` (l. 131–148). `_tolk_skjema` (l. 151–164) kaller `form()` med Starlettes standard `max_part_size=1 MB` per tekstfelt, så en stor `bilde_beholdt` gir 403. Den forkaster `UploadFile` (l. 162), og ingen får fila. `scope["state"]["skjema"]` (l. 110).
- `app/core/headere.py` -- `med_sikkerhetsheadere` (l. 27–32) fjerner rutas egen `cache-control` og setter `no-store` på alt utenom `/static/`.
- `.venv/.../starlette/formparsers.py` -- et tomt filfelt gir `UploadFile` med `filename=""` og størrelse 0 (l. 212–223). Filer over 1 MB spooles til disk (l. 135), og `/tmp` er skrivbar på Vercel.
- `app/oppdrag/service.py` -- `valider_oppdrag` (l. 178–249, feltrekkefølgen), `opprett_oppdrag` (l. 252–308, `begin_nested` og `Duplikat`), `OppdragVisning` (l. 315), `hent_for_visning` (l. 350–377, FR-9), `skjemaverdier_for` (l. 406), `rediger_oppdrag` (l. 425–504, betinget `UPDATE` og så `return` l. 499), `OppdragKort` (l. 578) og `ledige_oppdrag` (l. 595–636, eksplisitt `select` av kolonner).
- `app/oppdrag/models.py` -- `Oppdrag` (l. 35–56). `migrations/versions/0003_oppdrag.py` er mønsteret for navngitte constraints.
- `app/oppdrag/routes.py` -- `SKJEMAFELT` (l. 94), `GRUPPELENKER` (l. 107), `_vis_skjema` (l. 312), `_skjemakontekst` (l. 337), `send_ny` (l. 368–396), `_sjekk_id` (l. 418), `detaljer` (l. 423–463), `_vis_redigering` (l. 479), `rediger` og `send_rediger` (l. 511–551).
- `app/oppdrag/templates/oppdrag/skjema.html` -- `<form>` (l. 28), beskrivelsen (l. 38–48), tittel (l. 50), forhåndsvisningen (l. 139–142) og `steg.js` (l. 155).
- `app/core/templates/core/makroer.html` -- `oppdragskort` (l. 142–164) brukes av oversikten (`oversikt.html` l. 61) og forhåndsvisningen.
- `app/oppdrag/templates/oppdrag/detaljer.html` -- `h1` (l. 15) og `meldinger` (l. 16).
- `app/core/static/js/skjema.js` -- telleren kobles på `[data-maks][data-teller]` (l. 59). Forhåndsvisningen (l. 107–169) leser feltene etter navn. `steg.js` sjekker bare felt med `data-tom` (l. 16). `sending.js` stopper innsendinger som andre lyttere allerede har stoppet.
- `app/core/static/css/app.css` -- `.felt` (l. 472), «Beløp i kr» med `:has()` (l. 899–905) og `.kort` (l. 1012–1040, `padding` og `--rounded-lg`).
- `app/seed.py` -- `EKSEMPELOPPDRAG` (l. 92–132), `legg_inn_eksempeloppdrag` (l. 168), `bytt_ut_eksempeloppdrag` (l. 209–216, vanlig `DELETE` på `oppdrag`) og `last_eksempeldata` (l. 219–233, tømmer `Base.metadata`).
- `tests/core/test_mellomvare.py` -- multipart (l. 189) og 413 (l. 318, l. 365). `tests/core/test_arkitektur.py` -- rutenavn og stier (l. 147–160). `tests/core/test_migrering.py` -- `compare_metadata`. `tests/test_seed_og_admin.py` -- README og seed. `tests/conftest.py` -- `lag_oppdrag` (l. 193). `tests/e2e/test_t1.py` -- `oversikt` (l. 75, Ola med fire kort) og `SIDER` (l. 313). `tests/e2e/test_klientatferd.py` -- uten JS (l. 574).
- `README.md` -- eksempeloppdragene (l. 67–69) og oversikten (l. 87).

## Tasks & Acceptance

**Execution:**
- [x] `pyproject.toml`, `uv.lock`, `ARCHITECTURE-SPINE.md`, `.memlog.md` -- `uv add "pillow~=13.0.0"`. Stack-raden blir «Pillow | 13.0.x», og memlog får en linje med begrunnelsen (Beslutninger) -- AD-18, NFR-12
- [x] `app/core/csrf.py` -- grensen er 5 MiB for `multipart/form-data` og 1 MB ellers, sjekket mot `Content-Length` og under lesing. `form(max_part_size=…)` tåler `bilde_beholdt`. Ikke-tomme filer leses og lukkes og legges i `scope["state"]["filer"]: dict[str, bytes]`, med første ikke-tomme fil per navn. `skjema` har bare tekst som før. Docstringen oppdateres -- AD-5, AD-18
- [x] `app/core/headere.py` -- en `Cache-Control` som ruta har satt selv, beholdes, og ellers settes `no-store` som før. Bare bilderutene setter den -- AD-18, FR-2
- [x] `app/oppdrag/bilde.py` (ny) -- konstantene og feiltekstene, `Bilde(bilde, miniatyr, bredde, hoyde)`, `behandle(data) -> Bilde`, `fra_beholdt(tekst) -> Bilde` (`b64decode(validate=True)`, ugyldig gir formatfeilen) og `til_beholdt(Bilde) -> str`. Feil kastes som `RegelBrudd([("bilde", tekst)])`. Se Design Notes -- FR-27, NFR-9, NFR-12, AD-18
- [x] `app/oppdrag/models.py`, `migrations/versions/0004_oppdragsbilde.py` (ny) -- `Oppdragsbilde`: `oppdrag_id` (PK og FK `fk_oppdragsbilde_oppdrag_id_oppdrag`), `bilde` og `miniatyr` som `LargeBinary` med `deferred=True`, `bildetekst` `String(120)`, `bredde`, `hoyde` og `opprettet` (`UtcDateTime`). Bare tillegg, og `downgrade` dropper tabellen -- AD-1, AD-13, AD-18
- [x] `app/oppdrag/service.py` -- `Bildevalg(ny: Bilde | None, fjern: bool, feil: str | None)` og `tolk_bildevalg(fil, beholdt, fjern)`, som aldri kaster. Ny fil går foran beholdt. En ugyldig ny fil gir `feil` og beholder et gyldig beholdt bilde i `ny`. `valider_oppdrag` får `bildevalg` og `bildetekst` og setter feilene inn etter beskrivelsen. Bildeteksten sjekkes bare når det finnes et gyldig bilde (nytt, beholdt eller lagret uten `fjern`). `opprett_oppdrag` legger inn raden i samme `begin_nested`. `rediger_oppdrag` lagrer, bytter, oppdaterer teksten eller sletter etter `UPDATE`-en, uten å røre `vesentlig_endret`. `slett_bilde(db, oppdrag_id)` (brukes av fjerning nå og av 4.5 senere). `hent_bilde(db, id, bruker_id, *, liten) -> bytes` med `hent_for_visning` først. `OppdragVisning.bilde: BildeInfo | None` (bildetekst, bredde, høyde, versjon) og `OppdragKort.bildeversjon: int | None` med `outerjoin` uten binærkolonner. `skjemaverdier_for` gir `bildetekst`. Docstringen oppdateres -- FR-4, FR-6, FR-9, FR-10, FR-27, AD-2, AD-16
- [x] `app/oppdrag/routes.py` -- `bildetekst` i `SKJEMAFELT` og `GRUPPELENKER["bilde"]`. `send_ny` og `send_rediger` kaller `tolk_bildevalg` før `with db.begin():` og sender inn valget. Ved 422 får malen `bilde_beholdt = til_beholdt(valg.ny)` og miniatyren som `data:`-URL. Redigering får gjeldende bilde fra `OppdragVisning.bilde`. `GET /oppdrag/{id:int}/bilde` (`oppdrag.bilde`) og `/bilde/liten` (`oppdrag.bilde_liten`) bruker `_sjekk_id` og `hent_bilde` og gir `Response(media_type="image/jpeg")` med `Cache-Control` fra AD-18. `detaljer` og `oversikt` sender bildedataene videre. Docstringen oppdateres -- FR-9, FR-10, FR-27, AD-18
- [x] `app/oppdrag/templates/oppdrag/skjema.html` -- `enctype="multipart/form-data"`. Etter beskrivelsen: filfeltet `bilde` (`accept="image/jpeg,image/png,image/webp"`, etiketten «Bilde (valgfritt)», eller «Bytt bilde» når det finnes et bilde), de to hjelpetekstene, feilen, et beholdt eller lagret bilde som miniatyr (`alt=""`) med avkrysningen «Fjern bildet» (`fjern_bilde`) og skjult `bilde_beholdt`, og «Hva viser bildet?» (`bildetekst`, `autocomplete="off"`, teller «N av 120 tegn», synlighet etter spørsmålet over). Ingen `data-tom`. Forhåndsvisningen får bildet når det finnes, ellers en skjult `<img data-felt="bilde">` til `bilde.js` -- FR-27, UX-DR33, NFR-10
- [x] `app/core/templates/core/makroer.html`, `oversikt.html`, `detaljer.html` -- `oppdragskort(…, bilde_url=None)` med `<img class="kort__bilde" alt="" loading="lazy" width="640" height="360">` først i kortet. Detaljene får `<img class="detaljbilde" alt="{bildetekst}" width height>` rett etter `meldinger()`, uten lenke -- FR-9, FR-10, UX-DR33
- [x] `app/core/static/js/bilde.js` (ny), lastet med `defer` fra `skjema.html` -- ved `change`: `createImageBitmap(fil, {imageOrientation: "from-image"})`, så en canvas med hvit bakgrunn og høyst 1 600 px, `toBlob("image/jpeg", 0.85)`, og fila byttes med `DataTransfer`. Forhåndsvisningen får `URL.createObjectURL`. En innsending mens skaleringen pågår, stoppes på skjemaet og sendes med `requestSubmit(submitter)` etterpå. Hvis noe feiler, sendes originalfila. Ingen regler og ingen `innerHTML` -- AR-28, AD-18
- [x] `app/core/static/css/app.css` -- `.kort__bilde` (full kortbredde med negativ marg lik kortets padding, øvre hjørner `--rounded-lg`, `aspect-ratio: 16 / 9`, `object-fit: cover`), `.detaljbilde` (full bredde, `max-height: 480px`, `object-fit: contain`, `--rounded-md`), filfeltet (trykkflate ≥ 48 px og samme fokusring) og miniatyren av beholdt bilde (≤ 160 px). Ingen vannrett rulling ved 320 px -- UX-DR33, NFR-6
- [x] `app/seed.py`, `README.md` -- `tegn_bilde(motiv)` tegner med `ImageDraw` (snø og spade, matskål, sofa og trapp, hekk og saks, uten personer og tekst) og sender PNG-en gjennom `bilde.behandle`. Bildetekstene er for eksempel «Snødekt innkjørsel med en spade». `bytt_ut_eksempeloppdrag` sletter `oppdragsbilde` for testbrukernes oppdrag før `oppdrag`. README forteller hvilke fire som har bilde, og at Kari kan bytte og fjerne bildet på «Måke snø» -- FR-27, NFR-2, AD-1
- [x] `EXPERIENCE.md` -- linja om `:has()` i § Skjemafelt rettes etter svaret på spørsmålet. Ingen andre tekster endres
- [x] `tests/bilder.py` (ny), `tests/oppdrag/test_bilde_regler.py`, `tests/oppdrag/test_bilde.py` (nye), `tests/core/test_mellomvare.py`, `test_arkitektur.py`, `test_migrering.py`, `tests/test_seed_og_admin.py` -- enhetstester av `bilde.py` for hver rad i matrisen (orientering, EXIF/GPS borte, alfa, animasjon, ikke forstørret, grensene på hver side, forfalsket base64), og av `tolk_bildevalg` og `vesentlig_endret`. HTTP-tester for hver rad, med CSRF og uten. Mellomvaren: `state.filer`, tomt filfelt gir ingen fil, grensene, og `Cache-Control` bare på bilderutene. Arkitekturen: PIL bare i `bilde.py` og `seed.py`, og stiene og navnene til bilderutene. Tabellen finnes etter migreringen. Seed: 4 bilder i 4 kategorier, seed to ganger og README -- FR-27, FR-9, NFR-5, NFR-10, NFR-12, AD-5, AD-18
- [x] `tests/e2e/test_t1.py`, `tests/e2e/test_klientatferd.py` -- nye sider i `SIDER`: `oversikt-med-bilde` (Ola, og docstringen i `oversikt` sier at to av fire kort har bilde), `oppdrag-detaljer-med-bilde`, `nytt-oppdrag-bildefeil` (tekstfil som `.jpg`), `nytt-oppdrag-beholdt-bilde` og `rediger-oppdrag-med-bilde`. Klienttester: et PNG-bilde på cirka 6 MB blir skalert og vises i forhåndsvisningen, og etter «Publiser» har detaljene et bilde på høyst 1 600 px. Uten JS gir et JPEG-bilde på cirka 1 MB detaljer med bilde. «Hva viser bildet?» følger svaret på spørsmålet -- SM-5, NFR-6, NFR-7, UX-DR33

**Acceptance Criteria:**
- Gitt Kari på mobil med JS, når hun velger et bilde på 6 MB, skriver hva det viser og publiserer, så viser forhåndsvisningen bildet før innsending, og detaljene viser det etterpå. Den innsendte fila er under 4 MB.
- Gitt Ola med seed, når han åpner oversikten, så har to av de fire kortene et bilde øverst, og skjermleseren leser bare tittellenken i kortet.
- Gitt jobben `test-postgres` i CI, når testene for bilder kjøres, så lagres og hentes `LargeBinary` likt i Postgres og SQLite.

## Implementation Notes

- `tests/core/test_arkitektur.py::test_filer_leses_med_utf8` hopper over `Image.open(...)`: den leser bytes fra minnet, ikke en tekstfil.
- Seed gir «Måke snø i innkjørselen» et bilde, så testene fra 2.5 som redigerer det, sender nå `bildetekst` (GYLDIG i `test_redigere.py`), og fraværet av `type="file"` og «Bytt bilde» i redigeringsskjemaet er byttet med at de finnes.
- `test_to_steg.py`: `img` er lagt til de tomme elementene i `Skjemaleser`, og steg 1 har nå `bilde` og `bildetekst`.
- Grenser i `domene.py`: `BILDETEKST_MIN = 3` og `BILDETEKST_MAKS = 120` (AD-10).
- «Fjern bildet» krysset av ved 422 i redigering beholdes krysset av (`fjern_valgt`). Med «Fjern bildet» og en ugyldig ny fil brukes ikke et beholdt bilde.
- `bilde.js` sender originalfila når et lite bilde ikke blir mindre som JPEG (ingen nedskalering og større blob).

## Spec Change Log

## Review Triage Log

Pass 1 (2026-11-27). Lag: Blind Hunter (BH), Edge Case Hunter (EC), Verification Gap (VG).

| # | Lag | Funn | Verdict | Begrunnelse | Rute |
|---|---|---|---|---|---|
| 1 | BH, EC | Grensen på 5 MiB for multipart har ikke plass til `bilde_beholdt` pluss en ny fil på nesten 4 MB uten JS. Et forfalsket `bilde_beholdt` over 4 MiB gir 413, ikke feilteksten som matriseraden krever | medium | Base64 av en beholdt JPEG er opptil cirka 2 MB. 413 sletter hele skjemaet | patch |
| 2 | BH, EC | 413 for et for stort bilde sier «Noe gikk galt. Prøv igjen om litt.» | medium | Gjelder uten JS eller når nettleseren ikke kan dekode bildet (HEIC). Feil råd | patch |
| 3 | BH | `headere.py` beholder all `Cache-Control` som en rute setter, ikke bare for bilderutene | medium | En senere rute som setter headeren, mister `no-store` uten varsel (FR-2) | patch |
| 4 | BH, EC | `behandle` fanger for få unntak. Ødelagt EXIF eller feil i dekoderen gir 500 | medium | Bekreftet i koden. Bryter løftet om at `tolk_bildevalg` aldri kaster, og gir 500 på brukerinput (NFR-10, NFR-12) | patch |
| 5 | BH, EC | En `I;16`-PNG med `tRNS` går inn i RGBA-grenen før konverteringen fra 16 bit | low | En gyldig PNG får feil melding. Retten er å bytte rekkefølge | patch |
| 6 | VG | Ugyldig ny fil sammen med gyldig beholdt bilde og «Fjern bildet» har ingen test | medium | Forhåndsverifisert av VG | patch |
| 7 | VG, BH | E2E-testen for innsending under skaleringen sikrer ikke at skaleringen fortsatt pågår ved klikket | medium | Forhåndsverifisert av VG. Testen kan bestå uten at lytteren finnes | patch |
| 8 | BH, EC | Flere klikk under skaleringen legger flere `requestSubmit` i kø | medium | Redigeringsskjemaet har ingen `skjema_id`, så det kan sendes to ganger | patch |
| 9 | EC | bfcache eller autofyll kan legge tilbake en stor original uten `change` | low | Originalen sendes uskalert. Retten er én `pageshow`-sjekk | patch |
| 10 | BH, EC | Forhåndsvisningen viser fortsatt bildet når «Fjern bildet» er krysset av | low | Viser noe annet enn det som blir lagret | patch |
| 11 | BH | Miniatyren av et beholdt eller lagret bilde har `alt=""`, så skjermleserbrukere vet ikke at et bilde er med | medium | NFR-7. Retten er en kort alt-tekst | patch |
| 12 | EC | `?v={versjon}` kan gi samme URL for et nytt oppdrag med gjenbrukt id i SQLite, så nettleseren viser et `immutable`-bilde fra et slettet oppdrag | low | Skjer lokalt etter ny seed. Retten er tidsstempelet til bildet i URL-en | patch |
| 13 | BH | README nevner ikke nedskaleringen eller grensen hos Vercel uten JS | low | En sensor som tester uten JS, møter en feil uten forklaring | patch |
| 14 | BH | `epics.md` AR-31 sier fortsatt Pillow 12.x | low | Sporingen. Rettet av koordinatoren. Endringsforslaget beholdes som historisk dokument | patch |
| 15 | BH | Importene i `seed.py` bryter grupperingen | low | Direkte retting | patch |
| 16 | EC | Multipart-grensen gjelder alle POST-ruter, også innlogging | low | 5 MiB mot 1 MB gir ingen reell skade. Retten krever hvitliste per sti | reject |
| 17 | EC | Reserven `skjema.submit()` uten `requestSubmit` mister knappen og `sending.js` | low | `requestSubmit` finnes i alle nettlesere appen støtter | reject |
| 18 | EC | Redigering med lagret A, beholdt B og «Fjern bildet» sletter A | low | Sjeldent, og hensikten er tvetydig. «Fjern bildet» betyr at oppdraget ikke skal ha bilde | reject |
| 19 | BH | Matriseraden for forfalsket beholdt over 4 MiB stemmer ikke med koden | low | Løses av rad 1: med den nye grensen gir raden feilteksten ved feltet, som matrisen sier | reject |
| 20 | BH | `opprettet` overskrives når bildet byttes | low | Kolonnen betyr når dette bildet ble laget. Ingen leser den som opprinnelig tid | reject |

## Design Notes

- **Flyten.** Mellomvaren → `request.state.filer["bilde"]` og `skjema["bilde_beholdt"]`, `skjema["fjern_bilde"]` og `skjema["bildetekst"]` → `tolk_bildevalg` i ruta (dekodingen skjer utenfor transaksjonen, så SQLite-låsen fra `BEGIN IMMEDIATE` ikke holdes mens et bilde på 40 MP dekodes) → service validerer og lagrer. Ruta leser aldri fila selv.
- **Behandlingen** i `bilde.py`:

  ```python
  if len(data) > MAKS_BYTE: raise RegelBrudd([("bilde", FOR_STORT)])
  try:
      with Image.open(BytesIO(data), formats=["JPEG", "PNG", "WEBP"]) as im:
          if im.width * im.height > MAKS_PIKSLER: raise RegelBrudd([("bilde", FOR_MANGE_PIKSLER)])
          im = ImageOps.exif_transpose(im)  # laster pikslene
          rgb = _paa_hvitt(im)              # RGBA/LA/P med alfa → hvit bakgrunn, ellers convert("RGB")
  except (UnidentifiedImageError, OSError, SyntaxError, Image.DecompressionBombError):
      raise RegelBrudd([("bilde", FEIL_FORMAT)]) from None
  stor = rgb.copy(); stor.thumbnail((1600, 1600)); liten = rgb.copy(); liten.thumbnail((640, 640))
  # save(format="JPEG", quality=85, optimize=True) uten exif= og icc_profile= → ingen metadata
  ```
- **`?v=`** er `oppdrag.versjon`. Redigering øker den alltid, også når bare bildet endres, fordi skjemaet sender alle feltene og `UPDATE`-en kjører. Et nytt eller fjernet bilde gir derfor ny URL uten egen kolonne. URL-en endres også ved andre endringer, og det koster bare én ny henting.
- **`Cache-Control` på bildene** (AD-18) betyr at bildet kan ligge i nettleserens buffer etter utlogging, i motsetning til sidene (FR-2, `no-store`). Det er et bevisst valg i AD-18: bildet er bare synlig for den som allerede kunne se det. Unntaket gjelder bare svar der ruta har satt `Cache-Control` selv.
- **Binærdata leses aldri ved et uhell.** `deferred=True` på `bilde` og `miniatyr`. `ledige_oppdrag` og `hent_for_visning` henter bare `oppdrag_id`, `bildetekst`, `bredde` og `hoyde`. Bare `hent_bilde` leser én binærkolonne.
- **Beholdt bilde.** Det skjulte feltet har den omkodede JPEG-en, og miniatyren vises som `data:image/jpeg;base64,…` (cirka 40 kB i stedet for den store fila to ganger). Ved neste innsending går feltet gjennom `behandle` på nytt (AD-18), så et forfalsket felt gir ikke mer enn en vanlig opplasting. JPEG-en kodes om én gang til, og kvalitetstapet syns ikke.
- **Ugyldig fil gir ingen feil ved bildeteksten.** Filfeltet er tomt etter 422 og ingen bilde er beholdt, så «Hva viser bildet?» er ikke nødvendig. Feltet kan da være skjult (spørsmålet over), og en feil der ville gitt en lenke i oppsummeringen til et skjult felt.
- **Bildet i detaljene** står etter `meldinger()`, så kvitteringen fortsatt står rett under `h1` og får fokus. Det er fortsatt «under tittelen».
- **`bilde.js` og `sending.js`.** `bilde.js` lytter på `submit` på skjemaet, altså før `sending.js` på `document`. Pågår skaleringen, kaller den `preventDefault()`, og `sending.js` lar innsendingen være (`defaultPrevented`). Etterpå sendes skjemaet med `requestSubmit(submitter)`. iPhone gjør HEIC om til JPEG når `accept` bare har JPEG, PNG og WebP. Kan nettleseren ikke dekode fila, sendes den som den er, og serveren avgjør.
- **Grensene.** Vercel stopper kropper over 4,5 MB før appen ser dem (kjent begrensning, FR-27). Lokalt og i CI gir 5 MiB vår egen melding for filer litt over 4 MB og 413 over det. Urlencoded forblir 1 MB, så de andre skjemaene ikke kan sende 5 MB.
- **Testbildene** lages i minnet: JPEG med `Image.Exif()` (orientering 6 og GPS-IFD 0x8825), en PNG på 7000×6000 i modus «1» (cirka 42 MP, men bare noen kB, og den dekodes aldri), og et PNG-bilde med støy på cirka 6 MB til klienttesten. Ingen binærfiler i repoet.
- **Fram mot Epic 4 og 5.** 4.5 og slettingen av oppdrag kaller `slett_bilde` før `oppdrag`-raden slettes (AD-2, FR-4). `ki.js` (Epic 5) sender skjemaets `FormData` og må fjerne `bilde` og `bilde_beholdt` før `fetch`, ellers lastes bildet opp ved hvert forslag. Story 2.6 bruker `request.state.filer` til å vise «Velg bildet på nytt etter innlogging.».

## Verification

**Commands:**
- `uv sync` -- forventet: Pillow 13.0.x installeres fra wheel på Windows og i CI (Linux), uten kompilering.
- `uv run pytest` -- forventet: alle tester er grønne, også `test_arkitektur.py` (PIL-importene og bilderutene `oppdrag.bilde` og `oppdrag.bilde_liten`), `test_migrering.py` (ett hode, 0004, og `compare_metadata` uten avvik), de nye bildetestene og invariantene fra 1.x og 2.1–2.5. Postgres-varianten kjøres av jobben `test-postgres` i CI.
- `uv run pytest -m e2e` -- forventet: T1 er grønn for alle sider i `SIDER` ved 360 og 1280 px, også de nye bildesidene, og uten vannrett rulling ved 320 px. Klienttestene er grønne, også de fra 1.5 og 2.2–2.5.

**Manual checks (if no CLI):**
- [ ] Tastatursjekk av filfeltet, «Hva viser bildet?», «Fjern bildet», «Bytt bilde» og kortene med bilde i cirka fem minutter (DoD, T2). **Utsatt til story 6.1** (retro T-5): den autonome kjøringen har ingen manuell tester, og T1 og klienttestene dekker de automatiske kravene. Storyen kan settes `done` med denne utsettelsen.
- [ ] Etter publisering: last opp et mobilbilde i produksjon og åpne detaljene som en annen bruker (Pillow på Vercel og `bytea` i Supabase).
