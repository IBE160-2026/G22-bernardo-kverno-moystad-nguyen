# Story 1.2: elisitering av specen

## 2026-11-24 kl. 12:14 — Heidi

### Oppgave
Kjøre `bmad-advanced-elicitation` på den siste leveransen, specen for story 1.2 (logge inn og ut), før implementeringen starter. Målet var å finne svakheter mens de fortsatt er billige å rette, og så committe specen.

### Plan
- Målet for elisiteringen: `_bmad-output/implementation-artifacts/spec-1-2-logge-inn-og-ut.md` (status `draft`).
- Valgte metoder: 1 Security Audit Personas, 3 Problem Decomposition, 4 Pre-mortem Analysis. Funnene bygger på koden fra 1.1 (`sesjon.py`, `mellomvare.py`, `csrf.py`, `identity/service.py`, `render.py`, `seed.py`) og spinen AD-4 til AD-7 og AD-14.
- Hver metode endte med et forslag. Alle tre ble godkjent (Apply) og lagt inn utenfor den frosne Intent-delen.

### Resultat
Specen er committet som `4bbaab1` på `story/1-2-logge-inn-og-ut`. Endringer fra elisiteringen:
- **Sikkerhet:**
  - Cookien `sesjon` har `Path=/; Max-Age=604800` og slettes med samme attributter.
  - `Cache-Control: no-store` på alle svar unntatt `/static/`.
  - `trygg_neste()` i `core` avviser `\`, kontrolltegn og `/logg-inn`/`/logg-ut`.
  - Dummy-hashen lages med `hash_passord`, så kostnaden er den samme som for ekte hasher.
  - Alle rader i `innloggingsforsok` eldre enn 15 min ryddes, og `tidspunkt` er indeksert.
  - Ved POST `/logg-inn` med gyldig sesjon slettes den gamle raden.
  - `app.admin` viser hvilken database den bruker og krever `ja`.
  - Kvitteringscookien inneholder en nøkkel, ikke tekst.
  - Ny seksjon «Kjente begrensninger»: sperre per e-post, parallelle forsøk og CSRF-nøkkel som ikke byttes.
- **Oppdeling:** oppgavelista er byttet ut med seks trinn i avhengighetsrekkefølge: passord og sperre → håndheving → meny og grunnsider → innlogging og utlogging → testbrukere og admin → JS. Testene committes sammen med koden de tester.
- **Kuttlinje:** JS flyttes til 1.4, `app.admin` til 1.3 og `/profil/{id}` til 2.3, med faste tidspunkter for når kuttene utløses (se åpne punkter).
- **Pre-mortem:**
  - én review-runde
  - test av bcrypt-kostnaden (`$2b$04$` i test)
  - FR-3-testen fyller stiparametre og krever minst fem ruter
  - manuell sjekk ved 320 px og cirka fem minutters tastatursjekk
  - teksten i EXPERIENCE.md er fasit, ikke linjenumrene
- Ikke tatt med: å lagre e-posten i `innloggingsforsok` som SHA-256, fordi det avviker fra spinen. Metodene Boundary & Edge Case Sweep og Assumption Audit ble ikke kjørt.
- Ingen kode er skrevet. Story 1.2 er `in-progress`, og specen står fortsatt som `draft`.
- `_bmad-output/party-mode/` er privat og skal ikke committes. Den ignoreres bare lokalt, gjennom `.git/info/exclude`, med vilje ikke i `.gitignore`. Mappa finnes ikke i git-historikken.
- `epic-1-context.md` (beslutningene fra 1.1, endret før økta) er committet som `a8e71cc` etter en sjekk av at den ikke har personlige opplysninger eller hemmeligheter.

### Åpne punkter
- Implementer story 1.2 etter specen med `bmad-build`, fra trinn 1.
- Kuttene i story 1.2 utløses på faste tidspunkter: er trinn 4 ikke grønt onsdag 25. nov kl. 20, flyttes JS og `app.admin`. Er PR-en ikke åpnet torsdag 26. nov kl. 12, flyttes også `/profil/{id}`. Hvert kutt føres i Spec Change Log, epics og `sprint-status.yaml`.

## 2026-11-24 kl. 13:05 — Heidi

### Oppgave
Kjøre `bmad-build` på story 1.2 (logge inn og ut) etter den elisiterte specen: sjekke at specen er klar, godkjenne, implementere, reviewe og rette.

### Plan
- Specen ble sjekket mot READY-standarden før godkjenning: [spec-1-2-logge-inn-og-ut.md](../../_bmad-output/implementation-artifacts/spec-1-2-logge-inn-og-ut.md).
- En subagent implementerte de seks trinnene. Jeg sjekket diffen og matrisetestene selv.
- Tre reviewere (blind, kanttilfeller, testhull) gikk gjennom diffen. Funnene ble vurdert i specens triage-logg, og den samme subagenten rettet dem.

### Resultat
- **Beslutning av Heidi:** sjekkpunktdatoene i `epics.md` hadde ukedager fra 2025-kalenderen. Datoene er beholdt, og ukedagene er rettet (lørdag 28. nov., torsdag 3. des., tirsdag 8. des., lørdag 12. des.), også i `epic-1-context.md` og kuttlinja i specen (`1be921b`).
- Specen ble godkjent (`7d87a2d`) og står nå som `done`. Story 1.2 er `review` i `sprint-status.yaml` (`e33d665`).
- **Kode** (`14e08fb`–`18e7b95`):
  - bcrypt og tabellen `innloggingsforsok` (migrering `0002`), passord og e-post bare i `identity/service.py`, sperre etter 5 feil på 15 min, sesjon med hashet nøkkel i 7 dager.
  - Innlogging kreves i sesjonsmellomvaren (303 for GET, 401 ellers), med FR-3-test over alle ruter.
  - Meny, grunnsidene Oppdrag, Mine oppdrag og Profil, og andres profil med `OffentligBruker` og AR-24-test.
  - POST `/logg-inn` og `/logg-ut`, kvittering i signert cookie og feiloppsummering med fokus.
  - Seks testbrukere i seed og README, `app.admin nytt-passord`, og JS for «Vis passord» og sendeknappen.
- **Review:** 34 funn. 11 er rettet (`92f991a`–`9a9f960`), blant annet `no-store` også på feilsider, dummy-hash ved oppstart, vakt mot for lang e-post og for stor profil-id, og flere tester. 23 er avvist med begrunnelse, og ingen er utsatt.
- **Verifisert lokalt:** `uv run pytest` gir 280 bestått. `alembic heads` gir `0002`. Seed to ganger gir 6 og så 0 nye brukere. gitleaks 8.30.1 finner ingenting i 140 commits.
- Commitene for trinn 2–4 passerer ikke testene hver for seg, fordi trinnene ble bygget samlet (står i specens Implementation Notes). Sluttilstanden er grønn.
- Ingenting er pushet.
- Lukket i `issues.md`: hashet sesjonsnøkkel (story 1.2), implementering av 1.2, og kuttene for trinn 4.

### Åpne punkter
- Push branchen og åpne PR mot `main` før torsdag 26. nov kl. 12, ellers flyttes `/profil/{id}` til 2.3 (kuttlinja). Story 1.2 settes til `done` når CI er grønn og PR-en er merget.
- Manuelle sjekker gjenstår: ingen vannrett rulling ved 320 px, cirka fem minutters tastatursjekk av meny, innlogging og profil, og `app.admin nytt-passord` i en ekte terminal.
- JS-oppførselen («Vis passord», sendeknappen med `aria-disabled` og `pageshow`) har ingen automatiske tester. Ta den med i T1/Playwright i story 1.5.


## 2026-11-24 kl. 14:16 — Heidi

### Oppgave
Pushe branchen for story 1.2 og åpne PR mot `main`.

### Plan
- Push `story/1-2-logge-inn-og-ut` og åpne PR med samme oppsett som PR #1.
- Vente på CI før loggen oppdateres.

### Resultat
- Branchen er pushet (til `8afddcc`), og [PR #2](https://github.com/IBE160-2026/G22-bernardo-kverno-moystad-nguyen/pull/2) er åpnet mot `main`. Kuttfristen torsdag 26. nov kl. 12 er dermed nådd, og `/profil/{id}` blir i story 1.2.
- CI er grønn: pytest mot SQLite og `alembic heads` (16 s), pytest mot Postgres 17 (30 s), og gitleaks over hele historikken (7 s). Det er første gang testene for 1.2 har kjørt mot Postgres.
- Lukket i `issues.md`: push og PR før kuttfristen.

### Åpne punkter
- Merge PR #2, og sett deretter story 1.2 til `done` i `sprint-status.yaml`.
- De manuelle sjekkene og JS-testene i 1.5 fra forrige seksjon står fortsatt åpne.

## 2026-11-24 kl. 14:21 — Heidi

### Oppgave
Gjøre ferdig det som gjensto for story 1.2: pushe loggen først, merge PR #2 og sette storyen til `done`.

### Plan
- Pushe logg-commiten til PR-branchen og vente på grønn CI for den nye commiten.
- Merge PR #2 og sette status `done` direkte på `main`, slik det ble gjort for story 1.1 (`887def3`).

### Resultat
- Logg-commiten `7f04baa` ble pushet, og CI var grønn på den (kjøring 45402301157: SQLite, Postgres og gitleaks).
- PR #2 er merget i `9a8f7d2`, og branchen `story/1-2-logge-inn-og-ut` er slettet.
- Story 1.2 står som `done` i `sprint-status.yaml` (`b8b10c3`). Epic 1 er fortsatt `in-progress`.
- Lukket i `issues.md`: merge PR #2 og `done`-status.

### Åpne punkter
- De manuelle sjekkene for 1.2 (320 px, tastatur, `app.admin` i ekte terminal) og JS-testene i 1.5 står fortsatt åpne i `issues.md`.
- Sjekkpunkt lørdag 28. nov: Epic 1 ferdig. Story 1.3–1.5 gjenstår (står allerede i `issues.md`).
