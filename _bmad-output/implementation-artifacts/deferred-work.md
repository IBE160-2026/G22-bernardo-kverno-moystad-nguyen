# Utsatt arbeid

- source_spec: `_bmad-output/implementation-artifacts/spec-1-1-skjelett-lokalt-og-ci.md`
  summary: Origin-sjekken i `app/core/csrf.py` sammenligner bare `netloc` i `Origin` med `Host`, uten hensyn til proxy, skjema (http/https) eller standardport.
  evidence: maybe-false, medium hvis sant. Avgjøres i story 1.3: send innloggingsskjemaet i produksjon på Vercel og se om POST godtas. Avvises den med 403, må sjekken bruke den offentlige verten (f.eks. `X-Forwarded-Host`) eller normalisere standardport.
  resolution: Løst 2026-11-24 (story 1.3). Funnet var falskt. Røyktesten i produksjon sendte innloggingsskjemaet med `Origin` og fikk 422 («Feil e-post eller passord.»), ikke 403. Vercel sender den offentlige verten i `Host`, så sjekken trenger ingen endring.

- source_spec: `_bmad-output/implementation-artifacts/spec-1-1-skjelett-lokalt-og-ci.md`
  summary: `core/postnummer.finnes()` og `poststed()` leser `data/postnumre.tsv` ved kjøring, mens fremmednøkkelen sjekker tabellen `postnummer` som migreringen lastet.
  evidence: maybe-false, medium hvis sant. De er like så lenge TSV-fila og migrering 0001 er uendret. Avgjøres i story 1.3: sjekk at `data/` følger med i Vercel-funksjonen (ellers `FileNotFoundError`), og vurder å lese fra tabellen eller fra `postnumre.json` i stedet.
  resolution: Løst 2026-11-24 (story 1.3). `lag_app()` laster nå registeret ved oppstart, så en manglende fil stopper appen i stedet for å gi feil senere (testet i `tests/core/test_postnummer.py`). `data/` følger med i Vercel-funksjonen: publiseringen startet og røyktesten var grønn.

- source_spec: `_bmad-output/implementation-artifacts/spec-1-4-registrere-konto.md`
  summary: `app/core/static/js/poststed.js` (poststed ved postnummerfeltet) kjøres ikke av noen automatisk test. Uten test merkes det ikke om skriptet slutter å fylle inn eller tømme poststedet, eller om sjekken av utdaterte svar forsvinner.
  evidence: Funnet i reviewen av story 1.4 (V3 og B8). Repoet har ingen JS- eller nettlesertester ennå, og pytest sjekker bare HTML-en og at filene svarer 200. Tas i story 1.5 (Playwright): skriv `5006`, forvent «Bergen», skriv `57`, forvent tomt.
  resolution: Delvis løst 2026-11-25 (story 1.5). `tests/e2e/test_klientatferd.py::test_poststed_vises_ved_gyldig_postnummer` skriver `5006` og forventer «Bergen», og så `57` og forventer tomt. Sjekken av utdaterte svar (feltet endres mens `postnumre.json` hentes) har fortsatt ingen test.

- source_spec: `_bmad-output/implementation-artifacts/spec-1-5-automatisk-test-uu.md`
  summary: Bare `APP_ENV` hindrer at den offentlige ruta `POST /_test/tilstand` (som tømmer `bruker` med `seed=1`) og standardnøkkelen kommer i produksjon. Settes `APP_ENV=test` ved en feil i Vercel, starter appen med ruta mot Supabase.
  evidence: Funnet i reviewen av story 1.5 (B5). Feilkonfigureringen fantes fra før: med `APP_ENV=local` starter appen også med standardnøkkelen. Story 1.5 gjør skaden større. Røyktesten oppdager det etter publisering (GET gir 405, ikke 404, og nå testet), men ruta er åpen til noen ruller tilbake. Mulig retting: `Settings` nekter `test` og `local` når `VERCEL` er satt, med en test. Severity medium.
  resolution: Løst 2026-11-26 (T-1-herdingen etter retro Epic 1, `spec-t-1-herding-epic-1.md`). `Settings` har feltet `vercel` (miljøvariabelen `VERCEL`, som Vercel setter ved bygging og kjøring). Er det satt og `APP_ENV` ikke er `production`, stopper oppstarten med `KonfigFeil` og en melding som nevner `APP_ENV` og `VERCEL`. Testet i `tests/core/test_config.py::test_vercel_uten_produksjon_stopper` (local og test) og `test_vercel_i_produksjon_godtas`.

- source_spec: `_bmad-output/implementation-artifacts/spec-t-1-herding-epic-1.md`
  summary: Ref-vakten på jobben `deploy` (`if: github.ref == 'refs/heads/main'`) hindrer bare publisering fra en annen branch ved et uhell. Den som kan pushe, kan endre `deploy.yml` på sin branch og starte den med `workflow_dispatch`, og jobben får da `MIGRATION_DATABASE_URL` og `VERCEL_TOKEN`.
  evidence: Funnet i reviewen av T-1 (Blind Hunter). `workflow_dispatch` kjører workflow-fila fra den valgte branchen, og repo-hemmeligheter er tilgjengelige for alle brancher. Fantes før T-1. Ekte vern er et GitHub Environment `production` som bare tillater `main`, med hemmelighetene flyttet dit. Det krever en innstilling i GitHub (admin), som ingen i gruppen har (AR-7). Severity medium, lav sannsynlighet (bare gruppemedlemmer kan pushe).

- source_spec: `_bmad-output/implementation-artifacts/spec-2-1-legge-ut-oppdrag.md`
  summary: `endre_status(..., ikke_passert=True)` gir `Konflikt` («Oppdraget er endret. Last siden på nytt.») også når tidspunktet bare er passert. Brukeren får da en melding som ikke hjelper.
  evidence: Funnet i reviewen av 2.1 (BH). Ingen rute bruker `ikke_passert` ennå. Tas når Epic 3 (3.1 melde interesse, 3.3 velge hjelper) første gang kaller den: skill passert fra endret (egen melding etter FR-8/EXPERIENCE). Severity medium når den tas i bruk.

- source_spec: `_bmad-output/implementation-artifacts/spec-2-1-legge-ut-oppdrag.md`
  summary: `bytt_ut_eksempeloppdrag` i `app/seed.py` sletter testbrukernes oppdrag med en vanlig `DELETE`. Når `interesse` (Epic 3) får fremmednøkkel til `oppdrag`, feiler `python -m app.seed` nummer to med FK-feil.
  evidence: Funnet i reviewen av 2.1 (BH), og nevnt av spec-forfatteren. Ingen barnetabell finnes nå. Tas i story 3.1: slett barneradene til testbrukernes oppdrag først. README bør også si tydelig at oppdrag som er laget for hånd på testkontoene, forsvinner.
