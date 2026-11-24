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
