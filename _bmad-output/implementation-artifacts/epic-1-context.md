# Epic 1 Context: Konto og innlogging

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->

## Goal

En person kan registrere seg, logge inn og logge ut, og alt annet i appen krever innlogging (FR-1, FR-2, FR-3). Epicen legger også skjelettet som alle senere stories bygger på (AR-1): en server-rendret FastAPI-app med mellomvare, rendring, sesjon, én Alembic-migrering med postnumre, seed, grønn CI og produksjonspublisering på Vercel mot Supabase. Appen skal starte på en ren maskin uten kontoer eller nøkler (NFR-1), og sikkerhet (CSRF, headere, passordhash), feilhåndtering og universell utforming skal være på plass fra første side. Sjekkpunkt: Epic 1 ferdig fredag 28. nov.; hvis ikke, kuttes story 2.6 og 2.2.

## Stories

- Story 1.1: Skjelett – appen kjører lokalt og i CI
- Story 1.2: Logge inn og ut
- Story 1.3: Skjelett – appen publiseres i produksjon
- Story 1.4: Registrere konto
- Story 1.5: Automatisk test av universell utforming

## Requirements & Constraints

- **Registrering (FR-1):** navn 1–80 tegn, gyldig e-post, passord 8–64 tegn, telefon åtte siffer (mellomrom, +47 og 0047 godtas, lagres som åtte siffer), postnummer som finnes i lista, fødselsdato ikke fram i tid og høyst 120 år tilbake. Under 18 år i norsk tid avvises (fyller 18 i dag godtas; 29. februar fyller år 1. mars i ikke-skuddår). E-post i bruk avvises uavhengig av store/små bokstaver. Personverntekst over knappen. Ingen «om meg». Innlogget etter registrering.
- **Postnumre:** bare postnumre for gateadresser godtas (Brings kategori G og B, 3 382 numre). Postboksnumre (P) og servicenumre (S) avvises som ukjente, fordi ingen bor der. Gjelder alle steder der postnummer valideres.
- **Innlogging (FR-2):** samme melding for feil e-post og feil passord, e-post sammenlignes uten store/små bokstaver. 5 mislykkede forsøk per e-post på 15 min gir 15 min sperre, også for riktig passord; vellykket innlogging rydder tellerne. Sesjonen varer høyst 7 dager eller til utlogging, og etter utlogging (også via tilbakeknappen) er det ingen tilgang til innhold.
- **Innlogging kreves (FR-3):** alt unntatt rutene som er merket offentlige på selve ruta (`/logg-inn`, `/registrer`, `/static`) avvises på serveren. En automatisk test går gjennom alle ruter uten innlogging (303 for GET, 401 for POST).
- **Felles regler:** tekst trimmes og NFC-normaliseres før lengdesjekk, og felt med bare mellomrom er tomme. Alle feil vises ved feltet og samtidig, og alt utfylt beholdes unntatt passord (NFR-10).
- **Kvalitet:** passord bare som hash, testet (NFR-4); ingen hemmeligheter i repoet, gitleaks på hele historikken (NFR-3); `bruker` har bare navn, e-post, passord-hash, telefon, postnummer, fødselsdato og tidspunkter, aldri adresse (NFR-9); minst 6 oppdiktede testbrukere i 2–3 postnumre i README, merket «bare for lokal testing» (NFR-2); fast meny (NFR-11); tekst vises alltid som tekst og CSRF-beskyttelse (NFR-12).
- **Definition of Done:** regler testet mot serveren (NFR-5), nye sider i T1 (axe), ingen vannrett rulling ved 320 px, cirka fem minutters tastatursjekk, README oppdatert, én migrering per story ved skjemaendring, krav-ID i commits og tester.

## Technical Decisions

- **Stack:** Python 3.12, uv, FastAPI ~=0.165, Jinja2, SQLAlchemy 2.1 (synkron), Alembic, psycopg 3, pydantic-settings, bcrypt 5, itsdangerous, pytest, Playwright + axe. Ingen npm og intet byggsteg.
- **Slices:** `app/core`, `identity`, `oppdrag`, `profil`, `ki`, hver med `routes.py` / `service.py` / `models.py` / `templates/<slice>/`. Importer går profil→oppdrag→identity/ki→core. `identity` eier `bruker`, `sesjon`, `innloggingsforsok`; `core` eier `postnummer` (bare via migrering). `core` når slices bare gjennom `Autentisering`, koblet i `lag_app()`, som nekter å starte uten. Menykroken blir påkrevd først fra story 2.4; ingen stubb før det.
- **Sesjon:** `Autentisering` (`finn_innlogget`, `logg_inn`, `logg_ut`) og `Innlogget` i `core/sesjon.py`, implementert i `identity/service.py`. Tilfeldig nøkkel i HttpOnly-cookie, `SameSite=Lax`, `Secure` bare i produksjon, lagret i `sesjon`. Ruter får brukeren via `core.innlogget_bruker`. Uten sesjon: GET → 303 til `/logg-inn?neste=` (bare stier som begynner med `/` og ikke `//`); POST → 401-side «Du må logge inn igjen.» med lenke til innlogging og uten databaseinnhold (enkel versjon; full gjenvisning av skjema kommer i story 2.6).
- **Mellomvare:** fast rekkefølge feilhåndtering → headere → CSRF/Origin → sesjon → ruter, testet. Ren ASGI som leser skjemaet én gang (`request.state.skjema`) og spiller av kroppen for ruta. Signert CSRF-cookie (uavhengig av sesjon) + skjult felt i alle skjema, også før innlogging; `Origin`/`Sec-Fetch-Site` sjekkes mot `Host`. Headere på alle svar: CSP `frame-ancestors 'none'`, `X-Frame-Options: DENY`, `nosniff`, `Referrer-Policy: same-origin`. Bare POST endrer data.
- **Passord og e-post:** `hash_passord`/`sjekk_passord` (NFC, ingen trim, bcrypt over base64(SHA-256)) og `normaliser_epost` (trim, NFC, små bokstaver) finnes bare i `identity/service.py`. Unik-constraint på `bruker.epost`. `uv run python -m app.admin nytt-passord <e-post>` bruker de samme funksjonene; `slett-konto` kommer i story 4.5.
- **Tid og tekst:** `UtcDateTime` i `core/db.py`, fødselsdato som `Date`, «i dag» i Europe/Oslo, klokka alltid via `klokke.na()`. `core/tid.py` eier datotolkning (tosifret år for fødselsdato = året som gir alder 0–120). Postnumre bare via `core/postnummer.py` (`normaliser_postnummer`, `finnes`, `poststed`), lagret som fire sifre. `data/postnumre.tsv` er hele Brings register i UTF-8, men bare kategori G og B lastes; `core/static/postnumre.json` genereres og testes mot TSV-fila. README krediterer «Postnummerdata fra Posten Bring, lisensiert under NLOD 2.0.»
- **Database:** samme kode mot SQLite og Postgres, bare Alembic (`render_as_batch=True`), ett hode. `hent_db()` gir én `Session` per forespørsel; POST-ruter kjører `with db.begin():`, services committer aldri, `IntegrityError` fanges med `begin_nested()`. Etter første produksjonspublisering legger migreringer bare til.
- **Miljø:** én `Settings` med `APP_ENV` = `local` | `test` | `production`; ukjent verdi eller produksjon uten ekte `SECRET_KEY` stopper oppstarten. `/_test/tilstand` finnes bare i `test`. Ingen seed eller demokontoer i produksjon.
- **Personopplysninger:** maler får aldri ORM-objekter for `bruker`, bare `OffentligBruker` / `Profil` / `EgneOpplysninger`. Profilsider viser aldri telefon, e-post eller fødselsdato.
- **Feil og rendring:** `core/feil.py` (`RegelBrudd` → 422 med alle feil og verdier, `FinnesIkke`/`IngenTilgang` → 404, uventet → vennlig side uten stack trace). Skjemamodeller har bare `str | None`. POST → redirect → GET med kvittering i signert, kortlivet cookie. Alle sider via `core.render(request, mal, *, tittel, aktiv_meny, fokus=None, **ctx)`; autoescape alltid, ingen `|safe`/`Markup(`/`innerHTML` (arkitekturtest). Rutenavn `<slice>.<handling>`, `url_for` i maler. Aldri logg passord, e-post, telefon eller sesjonsnøkler.
- **Tester:** `tests/conftest.py` eier test-databasen, `sett_na` og fabrikkene (`lag_bruker` fra 1.2); hver test rulles tilbake.
- **CI/CD og arbeidsflyt:** `ci.yml` (pytest mot SQLite og Postgres, `alembic heads` = én linje, Playwright/axe, gitleaks), aldri `pull_request_target`. `main` er **ikke** teknisk beskyttet (ingen i gruppen har admin-rettighet); i stedet gjelder en skrevet regel i README: all kode går via PR med grønn CI før merge, mens logger (`.logs/`) og `sprint-status.yaml` kan pushes direkte til `main`. `deploy.yml` på `main`: `alembic upgrade head` via session pooler (5432), så `vercel deploy --prod` med `VERCEL_TOKEN` (Vercels GitHub-app trengs ikke). Appen bruker transaction pooler (6543, `NullPool`, `prepare_threshold=None`). `vercel.json`: Git-publisering og preview av, `maxDuration` 30. `keepalive.yml` hver 3. dag. Hemmeligheter bare i Vercel env (`DATABASE_URL`, `SECRET_KEY`, `OPENROUTER_*`) og GitHub Secrets (`MIGRATION_DATABASE_URL`, `VERCEL_*`); `.env.example` uten verdier.

## UX & Interaction Patterns

- **Sideramme:** `lang="nb"`, landemerker `header`/`nav` («Hovedmeny»)/`main` (`tabindex="-1"`), én `h1`, «Hopp til innholdet» først. `<title>` «Side – Nabolagshelten», med «Feil: » foran ved valideringsfeil («Logg inn», «Registrering», «Min profil», «<Navn> – profil», «Fant ikke siden»). Uten innlogging: topplinje med bare logo.
- **Meny:** Oppdrag · Mine oppdrag · Profil; i topplinjen fra 768 px, bunnmeny under 768 px (tre like brede valg, minst 56 px, tekst brytes, `position: static` på lav skjerm). Aktivt valg: fet + strek + `aria-current`. Logo er lenke «Nabolagshelten, til oversikten». Ingen lenker til funksjoner som ikke finnes ennå.
- **Design:** tokens fra DESIGN.md som CSS-variabler, ett lyst tema (`color-scheme: light`), systemskrifter, ingen hvit/svart, brødtekst 18 px, trykkflater 48 px, `rem`. Fokusring 3 px `outline` med 3 px avstand, `:focus` på elementer appen flytter fokus til, synlig i `forced-colors`.
- **Skjema:** synlige etiketter, `required` + `novalidate`, `aria-describedby`/`aria-invalid`. Felttyper: navn `name`, e-post `email`, telefon `tel`, postnummer `text` + `inputmode="numeric"` + `postal-code`, fødselsdato `text` + `bday` (hjelpetekst «dd.mm.åååå, for eksempel 03.05.1954»), passord `new-password` / `current-password`. «Vis passord» med `aria-pressed`; poststed vises ved gyldig postnummer (JS fra `postnumre.json`, ellers etter innsending). Passord tømmes ved feil med hjelpeteksten «Skriv passordet på nytt.».
- **Meldinger og fokus:** feiloppsummering «Skjemaet har N feil» rett etter `h1` med lenker til feltene og fokus, aldri `role`. Kvittering rett etter `h1`, får fokus og blir stående. Høyst ett `autofocus` per side. Sendeknapp får `aria-disabled` til svaret kommer, nullstilles ved `pageshow`.
- **Faste tekster:** «Feil e-post eller passord.», «For mange mislykkede forsøk. Prøv igjen om 15 minutter.», «Du må logge inn igjen.», «Du er logget ut.», «Det finnes allerede en konto med denne e-posten.», «Du må være minst 18 år for å bruke Nabolagshelten.», «Sjekk fødselsdatoen.», «Noe gikk galt. Prøv igjen om litt.». Øvrige feltfeil står ordrett i EXPERIENCE.md § Feiltekster ved felt.
- **Grunnsider:** oversikten har «Ledige oppdrag i <postnummer> <poststed>» med tomtilstand; «Mine oppdrag» viser «Du har ikke lagt ut noen oppdrag.»; egen profil viser navn, postnummer med poststed og «Logg ut»; andres profil viser navn og postnummer med poststed.
- **Ikke tillatt:** hamburgermeny, ikonknapper uten tekst, meldinger som forsvinner, hover som eneste måte, interaktive elementer inne i lenker.

## Cross-Story Dependencies

- 1.1 er ferdig. 1.2 kommer før 1.3 fordi produksjonssjekken bruker innloggingsskjemaet; 1.4 og 1.5 starter etter 1.1–1.3.
- Virker ikke produksjonspubliseringen (1.3) etter cirka én dag, føres det som åpent punkt, 1.4 starter, og publiseringen fullføres før Epic 6.
- 1.3 må også avklare to utsatte punkter fra 1.1: om Origin-sjekken godtar POST bak Vercels proxy, og om `data/postnumre.tsv` følger med i Vercel-funksjonen (ellers lese fra tabellen eller `postnumre.json`).
- 1.4 røyktester registrering i produksjon; testkontoen slettes med `app.admin slett-konto` når story 4.5 finnes.
- Grunnsidene fra 1.2 bygges videre i Epic 2 (oversikt, «+ Legg ut oppdrag» i 2.1, postnummerfilter og «Se profil»-lenker i 2.3, Mine oppdrag i 2.4) og Epic 4 (full profil i 4.3). Full gjenvisning av skjema ved utløpt innlogging kommer i 2.6. Fabrikkene `lag_oppdrag`, `lag_interesse`, `lag_tilbakemelding` kommer i 2.1, 3.1 og 4.2.
- T1 (1.5) utvides av hver senere story som lager en ny side eller tilstand.
