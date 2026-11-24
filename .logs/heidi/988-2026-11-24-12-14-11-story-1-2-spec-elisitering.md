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

### Åpne punkter
- Implementer story 1.2 etter specen med `bmad-build`, fra trinn 1.
- Kuttene i story 1.2 utløses på faste tidspunkter: er trinn 4 ikke grønt onsdag 25. nov kl. 20, flyttes JS og `app.admin`. Er PR-en ikke åpnet torsdag 26. nov kl. 12, flyttes også `/profil/{id}`. Hvert kutt føres i Spec Change Log, epics og `sprint-status.yaml`.
