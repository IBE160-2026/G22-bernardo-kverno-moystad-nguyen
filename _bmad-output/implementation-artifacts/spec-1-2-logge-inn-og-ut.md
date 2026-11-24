---
title: 'Story 1.2: Logge inn og ut'
type: 'feature'
created: '2026-11-24'
status: 'draft'
route: 'dispatch'
baseline_commit: 'ab54a16a8f3db09717dca37b9e1e5262158f23e3'
review_loop_iteration: 0
story_key: '1-2-logge-inn-og-ut'
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-1-context.md'
  - '{project-root}/_bmad-output/planning-artifacts/architecture/architecture-G22-bernardo-kverno-moystad-nguyen-2026-11-08/ARCHITECTURE-SPINE.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Skjelettet fra 1.1 viser innloggingssiden, men ingen kan logge inn, alle ruter er åpne, og det finnes ingen brukere å teste med. Alle senere stories trenger en innlogget bruker, menyen og grunnsidene.

**Approach:** Innlogging med e-post og passord (bcrypt, sperre etter 5 feil), sesjon i cookie med hashet nøkkel, utlogging, og håndheving i sesjonsmellomvaren (303 for GET, 401 for resten) etter merkingen `offentlig`. I tillegg menyen, grunnsidene for Oppdrag, Mine oppdrag og Profil, profilen til andre brukere, seks testbrukere i seed og README, og `app.admin nytt-passord` (FR-2, FR-3, FR-21, NFR-2, NFR-4, AR-9, AR-14, AR-16, AR-17, AR-24).

## Boundaries & Constraints

**Always:** Spinen § Consistency Conventions gjelder (navn, `render`, POST → redirect → GET, `with db.begin():` i POST-ruter, services committer aldri, autoescape). `hash_passord`, `sjekk_passord` og `normaliser_epost` finnes bare i `identity/service.py`. Tabellen `sesjon` lagrer bare `hash_sesjonsnokkel(nokkel)`. Klokka leses bare med `klokke.na()`. Maler får aldri ORM-objekter for `bruker`, bare `OffentligBruker`. Aldri logg passord, e-post, telefon eller sesjonsnøkler. Én ny migrering (`0002`). Tekst i UI er ordrett fra EXPERIENCE.md eller story-AC-en. Commits er små og oppgir krav-ID-er.

**Never:** Ingen registrering, `/registrer` eller lenke til registrering (1.4). Ingen «+ Legg ut oppdrag», lenken «Legg ut oppdrag», postnummerfilter eller «Velg et annet postnummer» (2.1, 2.3). Ingen `oppdrag`-tabell. Ingen gjenvisning av skjema ved utløpt innlogging (2.6). Ingen `slett-konto` (4.5). Ingen menykrok eller teller i menyen (2.4). Ingen `deploy.yml` (1.3), Playwright eller `/_test/tilstand` (1.5). Ingen `|safe`, `Markup(` eller `innerHTML`.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Riktig innlogging | `" Kari@Eksempel.no "` + riktig passord, `neste=/profil` | 303 til `/profil`, ny sesjon (hash i `sesjon`, `utloper` = nå + 7 dager), cookie `sesjon` HttpOnly, `SameSite=Lax`, `Secure` i produksjon, tellerne for e-posten slettet | N/A |
| Ugyldig `neste` | `//evil.no`, `/\evil.no`, `https://evil.no`, tom | 303 til `/` | N/A |
| Feil e-post eller passord | ukjent e-post, eller feil passord | 422 med «Feil e-post eller passord.», e-posten beholdt, passordfeltet tomt, `<title>` med «Feil: » | samme svar og omtrent samme tid i begge tilfeller |
| Tomme felt | tom e-post og/eller tomt passord | «Skriv e-postadressen din.» / «Skriv passordet ditt.» ved feltene og i oppsummeringen | teller ikke som mislykket forsøk |
| Sperre | 5 mislykkede innen 15 min, så riktig passord | «For mange mislykkede forsøk. Prøv igjen om 15 minutter.» | etter 15 min (`sett_na`) går innloggingen igjennom |
| Uten innlogging, GET | `/`, `/profil`, `/mine-oppdrag`, `/profil/3?x=1` | 303 til `/logg-inn?neste=<sti med spørrestreng, URL-kodet>` | N/A |
| Uten innlogging, POST | `/logg-ut` med gyldig CSRF, eller GET med `X-Fragment` | 401 «Du må logge inn igjen.» med lenken «Logg inn», ingen data endret | ingen databaseinnhold på siden |
| Utløpt sesjon | `utloper` passert | behandles som uten innlogging | N/A |
| Andres profil | `/profil/{id}` for annen bruker | navn og postnummer med poststed, `<title>` «<Navn> – profil – Nabolagshelten», ingen aktiv meny | ukjent eller slettet id → 404 «Fant ikke siden» |
| Utlogging | POST `/logg-ut` | sesjonsraden slettet, cookien fjernet, 303 til `/logg-inn` med kvitteringen «Du er logget ut.» | N/A |

</frozen-after-approval>

## Code Map

- `app/core/sesjon.py` -- `Autentisering` har bare `finn_innlogget`. Legg til `logg_inn` og `logg_ut` og avhengigheten `innlogget_bruker`. `offentlig`/`er_offentlig` finnes, gjenbrukes.
- `app/core/mellomvare.py` -- `SesjonMellomvare` setter bare `request.state.innlogget`; håndhevingen legges her. `/static/` hoppes over allerede.
- `app/identity/service.py` -- `hash_sesjonsnokkel`, `IdentityAutentisering.finn_innlogget` (filtrerer på `utloper` og `slettet_tidspunkt`). Gjenbrukes.
- `app/identity/models.py` -- `Bruker`, `Sesjon` (nøkkel `String(64)`, hex SHA-256). Ikke endre kolonnene.
- `app/identity/routes.py`, `templates/identity/logg_inn.html` -- GET `/logg-inn` med skjema og `csrf_token`. Skjemaet poster allerede til `identity.logg_inn`.
- `app/core/render.py` -- `render`, `sidetittel(feil=)`, `tilbake_url` (faller tilbake til `/` når innlogget). Kvitteringen leses her.
- `app/core/templates/core/{base,makroer}.html` -- logoen er allerede lenke når `innlogget`. `feltfeil`-makroen gjenbrukes.
- `app/core/feil.py` -- `FinnesIkke` → 404, `feilside`. 401-siden rendres uten databasekall, på samme måte.
- `app/core/csrf.py` -- skjemaet ligger i `request.state.skjema` (dict med tekst). POST-ruter leser derfra.
- `app/__init__.py` -- `include_router` for identity; legg til `oppdrag` og `profil`.
- `app/seed.py`, `tests/conftest.py` (fabrikkene kommer fra 1.2), `migrations/versions/0001_*.py` (mønster for 0002).
- `pyproject.toml` -- legg til `bcrypt~=5.0.0` (siste versjon på PyPI 2026-11-24).
- EXPERIENCE.md: feiltekster l. 142–145 og 187–189, tomtilstander l. 174–176, titler l. 448–460, meny l. 37–52, «Vis passord» l. 239–240, fokus l. 370–391 og 540. Linjenumrene er bare hjelp til å finne fram. Teksten i EXPERIENCE.md er fasit og sjekkes før den kopieres.

## Tasks & Acceptance

**Execution:** Seks trinn i avhengighetsrekkefølge. Hvert trinn ender med grønn `uv run pytest` og én eller noen få commits med krav-ID-er. Testene committes sammen med koden de tester.

*Trinn 1: Passord, e-post og sperre (ingen HTTP)*
- [ ] `pyproject.toml`, `uv.lock` -- `bcrypt~=5.0.0` -- AD-6
- [ ] `app/identity/models.py`, `migrations/versions/0002_innloggingsforsok.py` -- `innloggingsforsok(id, epost String(320) indeksert, tidspunkt UtcDateTime indeksert)` -- AR-14
- [ ] `app/identity/service.py` -- `normaliser_epost`, `hash_passord`/`sjekk_passord`, dummy-hash, sperren og oppryddingen, `logg_inn`/`logg_ut` -- AD-4, AD-6, AR-16
- [ ] `tests/conftest.py` -- `lag_bruker(**felt)`; bcrypt med kostnad 4 i test -- AR-29
- [ ] `tests/identity/` -- `passord_hash` inneholder ikke passordet, normalisering, sperre og opprydding med `sett_na`, og hashen begynner med `$2b$04$` i test (kostnaden leses fra `Settings`) -- NFR-4, NFR-5

*Trinn 2: Innlogging kreves*
- [ ] `app/core/sesjon.py` -- protokollen utvidet med `logg_inn`/`logg_ut`, avhengigheten `innlogget_bruker`, `trygg_neste()` -- AD-4, AR-17
- [ ] `app/core/mellomvare.py`, `app/core/templates/core/logg_inn_igjen.html` -- håndheving med 303/401, 401-siden uten database, `Cache-Control: no-store` på alle svar unntatt `/static/` -- FR-3, AR-14
- [ ] `tests/core/` -- FR-3-testen over `app.routes` (fyller stiparametre med `1`, feiler på ruter den ikke klarer å bygge, og sjekker at minst fem ruter er testet), `trygg_neste`, 401 uten databaseinnhold, `no-store` -- FR-3, NFR-5

*Trinn 3: Meny og grunnsider*
- [ ] `app/core/templates/core/{base,makroer}.html`, `static/css/app.css` -- meny i topplinjen fra 768 px og som bunnmeny under, `aria-current` -- NFR-11, UX-DR3
- [ ] `app/oppdrag/routes.py` + maler -- `/` (`oppdrag.oversikt`) og `/mine-oppdrag` (`oppdrag.mine`) -- FR-21 grunnsider
- [ ] `app/identity/service.py`, `app/profil/routes.py` + maler -- `OffentligBruker`, `hent_offentlig_bruker`, `/profil` (`profil.min`) og `/profil/{bruker_id:int}` (`profil.vis`) -- FR-21, AR-24, AD-16
- [ ] `app/__init__.py` -- koble inn rutene for `oppdrag` og `profil`
- [ ] `tests/conftest.py` -- `logg_inn_som(klient, bruker)`, som setter sesjonsraden og cookien direkte -- AR-29
- [ ] `tests/oppdrag/`, `tests/profil/` -- meny og `aria-current`, titler og tomtilstander, AR-24-testen, 404 for ukjent eller slettet id, 303 fra `/profil/{egen id}` -- AR-24, NFR-5

*Trinn 4: Innlogging og utlogging*
- [ ] `app/core/kvittering.py`, `app/core/render.py`, `base.html` -- kvittering i signert cookie, lest og slettet ved neste side; feiloppsummering -- AR-27, UX-DR22
- [ ] `app/identity/routes.py`, `logg_inn.html` -- POST `/logg-inn` (`offentlig`), POST `/logg-ut`, skjult felt `neste` -- FR-2, UX-DR12, UX-DR27
- [ ] `tests/identity/` -- hver rad i I/O-matrisen, `Set-Cookie` ved innlogging og utlogging -- FR-2, NFR-5

*Trinn 5: Testbrukere og admin*
- [ ] `app/seed.py`, `README.md` -- seks testbrukere og tabell i README, merket «bare for lokal testing», og admin-kommandoen -- NFR-2
- [ ] `app/admin.py` -- `nytt-passord <e-post>` -- AR-9
- [ ] `tests/` -- seed to ganger, admin bytter passord og sletter sesjoner og tellere -- NFR-2, AR-9, NFR-5

*Trinn 6: Progressiv forbedring*
- [ ] `app/core/static/js/{vis_passord,sending}.js` -- «Vis passord» med `aria-pressed`, `aria-disabled` på sendeknappen og nullstilling ved `pageshow` -- UX-DR13, UX-DR28

**Acceptance Criteria:**
- Gitt innlogget bruker, så har hver side menyen Oppdrag · Mine oppdrag · Profil med aktivt valg markert med fet skrift, strek og `aria-current="page"`. Oversikten har overskriften «Ledige oppdrag i <postnummer> <poststed>» og «Ingen ledige oppdrag i <postnummer> <poststed> akkurat nå.». «Mine oppdrag» viser «Du har ikke lagt ut noen oppdrag.». «Min profil» har navnet som `h1`, postnummer med poststed og knappen «Logg ut».
- Gitt en automatisk test som går gjennom `app.routes`, så gir hver rute som ikke er merket `offentlig` 303 for GET og 401 for POST uten innlogging.
- Gitt alle GET-ruter rendret for en innlogget bruker (også `/profil/{annen id}`), så inneholder ingen av dem telefon, e-post eller fødselsdato for noen bruker (AR-24).
- Gitt seed, så finnes de seks testbrukerne, seed kan kjøres to ganger uten feil, og `passord_hash` inneholder ikke passordet (NFR-4).
- Gitt `uv run python -m app.admin nytt-passord kari@eksempel.no`, så kan Kari logge inn med det nye passordet, og hennes gamle sesjoner og tellere er slettet.
- Gitt utlogging, så viser tilbakeknappen ikke innhold, fordi alle svar unntatt `/static/` har `Cache-Control: no-store`, og cookien `sesjon` er slettet med samme `Path` som den ble satt med.

## Implementation Notes

## Spec Change Log

## Review Triage Log

## Design Notes

Valg tatt i planleggingen (dokumentene sier ikke noe om dem, eller story-AC-en går foran):
- **Sperre:** følger spinen. Mislykkede forsøk lagres per normalisert e-post, også ukjente. Ved hvert forsøk slettes *alle* rader eldre enn 15 min, ikke bare radene for e-posten, så feilskrevne e-poster ikke blir liggende (personvern). `innloggingsforsok.tidspunkt` er indeksert. Er det 5 eller flere rader igjen for e-posten, avvises forsøket uten å lagres og uten passordsjekk. Tomme felt teller ikke. Vellykket innlogging sletter radene for e-posten og alle utløpte sesjoner.
- **Ukjent e-post:** kjør `sjekk_passord` mot en dummy-hash, så svartiden ikke avslører om kontoen finnes. Dummy-hashen lages én gang ved første bruk med `hash_passord`, så den alltid har samme kostnad som ekte hasher (12, eller 4 i test).
- **Sesjon:** `secrets.token_urlsafe(32)`, ny nøkkel ved hver innlogging, absolutt 7 dager. Cookien settes med `Path=/; Max-Age=604800`, så den varer like lenge som raden. Utlogging sletter den med samme `Path` og attributter. En test sjekker `Set-Cookie` både ved innlogging og utlogging.
- **Buffer:** `SesjonMellomvare` setter `Cache-Control: no-store` på alle svar unntatt `/static/`. Det gjelder også innloggingssiden, som viser e-posten igjen ved feil, og 303-svarene.
- **Håndheving:** mellomvaren finner ruta med `route.matches(scope)` (`Match.FULL`). Offentlig: ruter merket `offentlig` (GET og POST `/logg-inn`) og `/static`. Treffer ingen rute, går forespørselen videre til 404. GET eller HEAD uten innlogging gir 303. Andre metoder, og GET med `X-Fragment`, gir 401 rendret uten database. `/logg-inn` for en innlogget bruker gir 303 til `/`. Kommer POST `/logg-inn` med en gyldig sesjon, slettes den gamle raden før den nye lages.
- **`neste`:** bare `trygg_neste()` i `core` bestemmer. Den returnerer verdien når den begynner med én `/` (ikke `//`) og ikke har `\`, kontrolltegn eller mellomrom, er høyst 2048 tegn og ikke peker til `/logg-inn` eller `/logg-ut`. Ellers returnerer den `/`. Den brukes både når 303-svaret lages og etter innlogging, og `neste` bæres som skjult felt i skjemaet. Vi stoler ikke på at Starlette koder `Location`. Testene bruker `/\t/evil.no`, `/%0d%0aSet-Cookie:x` og `/logg-ut`.
- **Kvittering:** cookien `kvittering`, signert med `itsdangerous` (egen salt), `max_age` 60 s, HttpOnly, `SameSite=Lax`. Den inneholder en nøkkel (`"logget_ut"`), som slås opp i en fast liste med tekster i `core/kvittering.py`, ikke selve teksten. Ukjent nøkkel ignoreres. `render` leser den, viser den rett etter `h1` med `tabindex="-1"` og sletter cookien i samme svar.
- **`aktiv_meny`:** `"oppdrag"`, `"mine_oppdrag"`, `"profil"` eller `None`. `aria-current="page"`. Undersider med `"true"` kommer når de finnes.
- **Titler:** «Ledige oppdrag i 0571 Oslo», «Mine oppdrag» (fanene og den lange tittelen kommer i 2.4), «Min profil», «<Navn> – profil», «Logg inn». `/profil/{egen id}` gir 303 til `/profil`.
- **Fokus:** høyst ett `autofocus`. Ved feil får feiloppsummeringen det, ved kvittering kvitteringen, ellers feltet «E-post» på innloggingen.
- **bcrypt:** kostnad 12, og 4 når `APP_ENV=test`. `hash_passord` er `bcrypt.hashpw(base64(sha256(NFC(passord))))`.
- **`app.admin`:** passordet leses to ganger med `getpass`, aldri som argument, så det ikke havner i skallhistorikken. Lengden er 8–64 tegn (FR-1). Kommandoen virker mot den `DATABASE_URL` som er satt, også produksjon, fordi det er der glemte passord skal hjelpes. Før den endrer noe, viser den hvilken database den er koblet til, uten passord (samme funksjon som seed bruker), og krever at du skriver `ja`.
- **Testbrukere:** Kari Nordmann og Ola Hansen (0571 Oslo), Amir Haddad og Nora Berg (0572 Oslo), Sofie Lie og Jonas Dahl (5006 Bergen). E-post `<fornavn>@eksempel.no`, passord på formen `kari-lokal-1`, så gitleaks ikke tar dem for nøkler. Rollene i README beskriver hva hver bruker skal brukes til i senere stories (oppdragsgiver, hjelper, andre postnummer).

**Kuttlinje:** Hvis tiden ikke strekker til, kuttes dette i denne rekkefølgen:
1. Trinn 6 (JS) flyttes til 1.4, der registreringen trenger det samme feltet «Vis passord». Uten JS virker skjemaene fortsatt.
2. `app.admin nytt-passord` flyttes til 1.3, fordi den først trengs når produksjonen har brukere.
3. `/profil/{id}` flyttes til 2.3, der den første lenken dit kommer.

Et kutt endrer Intent. Det føres derfor i Spec Change Log, i epics og i `sprint-status.yaml` før det gjennomføres. Kuttene utløses på faste tidspunkter, så torsdag og fredag er satt av til 1.3–1.5 før sjekkpunktet for Epic 1 fredag 28. nov:
- *Onsdag 25. nov kl. 20:* er trinn 4 ikke grønt, utløses kutt 1 og 2.
- *Torsdag 26. nov kl. 12:* er PR-en ikke åpnet, utløses kutt 3, og PR-en åpnes med det som er ferdig.

**Review:** Én runde med `bmad-code-review`. Bare feil som denne storyen har innført, rettes. Resten går til `deferred-work.md`.

**Kjente begrensninger** (valgt bevisst, i tråd med spinen):
- Sperren gjelder per e-post. Den som kjenner en e-post, kan derfor stenge brukeren ute ved å sende 5 feil hvert 15. minutt. Sperre per IP-adresse er droppet, fordi Vercel ikke har minne mellom kall og fordi delte nett ville stenge ute uskyldige.
- Parallelle forespørsler kan komme litt over 5 forsøk før telleren rekker å oppdatere seg. Det er akseptert, fordi bcrypt med kostnad 12 uansett gjør gjetting sakte.
- CSRF-nøkkelen byttes ikke ved innlogging (AD-5). Det er trygt nok, fordi cookien er HttpOnly, har `SameSite=Lax` og Origin sjekkes.

## Verification

**Commands:**
- `uv run pytest` -- expected: alle tester passerer mot SQLite
- `uv run alembic heads` -- expected: én linje (`0002`)
- `uv run python -m app.seed` to ganger -- expected: ingen feil, seks brukere
- gitleaks-binæren over historikken -- expected: ingen funn

**Manual checks:**
- `uv run uvicorn main:app`, logg inn som Kari, gå gjennom menyen, logg ut, trykk tilbake: ingen innhold.
- Ingen vannrett rulling ved 320 px (bunnmenyen og innloggingen), og cirka fem minutters tastatursjekk av menyen, innloggingen og profilen (DoD). Disse sidene kommer inn i T1 (axe) i 1.5.
