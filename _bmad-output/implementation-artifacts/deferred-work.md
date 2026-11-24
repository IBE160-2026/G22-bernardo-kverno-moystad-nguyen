# Utsatt arbeid

- source_spec: `_bmad-output/implementation-artifacts/spec-1-1-skjelett-lokalt-og-ci.md`
  summary: Origin-sjekken i `app/core/csrf.py` sammenligner bare `netloc` i `Origin` med `Host`, uten hensyn til proxy, skjema (http/https) eller standardport.
  evidence: maybe-false, medium hvis sant. Avgjøres i story 1.3: send innloggingsskjemaet i produksjon på Vercel og se om POST godtas. Avvises den med 403, må sjekken bruke den offentlige verten (f.eks. `X-Forwarded-Host`) eller normalisere standardport.

- source_spec: `_bmad-output/implementation-artifacts/spec-1-1-skjelett-lokalt-og-ci.md`
  summary: `core/postnummer.finnes()` og `poststed()` leser `data/postnumre.tsv` ved kjøring, mens fremmednøkkelen sjekker tabellen `postnummer` som migreringen lastet.
  evidence: maybe-false, medium hvis sant. De er like så lenge TSV-fila og migrering 0001 er uendret. Avgjøres i story 1.3: sjekk at `data/` følger med i Vercel-funksjonen (ellers `FileNotFoundError`), og vurder å lese fra tabellen eller fra `postnumre.json` i stedet.
