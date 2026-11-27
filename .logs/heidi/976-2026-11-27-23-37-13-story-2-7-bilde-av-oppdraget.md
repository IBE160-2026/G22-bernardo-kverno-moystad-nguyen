# Story 2.7: Bilde av oppdraget

## 2026-11-27 kl. 23:37 — Heidi

### Oppgave
Sjette story i den autonome kjøringen av Epic 2, og kravet Heidi la til samme dag (FR-27, Bør). Oppdragsgiveren kan legge ved ett bilde av oppdraget, og bildet vises i oversikten og i detaljene (FR-27, FR-9, FR-10, NFR-9, NFR-12, AD-18, AR-31, UX-DR33).

### Plan
- Spec: [spec-2-7-bilde-av-oppdraget.md](../../_bmad-output/implementation-artifacts/spec-2-7-bilde-av-oppdraget.md). Endringsforslag: [sprint-change-proposal-2026-11-27.md](../../_bmad-output/planning-artifacts/sprint-change-proposal-2026-11-27.md).
- Det åpne spørsmålet ble løst med anbefalt alternativ: «Hva viser bildet?» er skjult til en fil er valgt (`bilde.js`) og står synlig uten JS. CSS `:has()` kan ikke se om et valgfritt filfelt har en fil.
- Implementering i en subagent, så review i tre lag og retting av funnene med samme subagent.
- Branch `story/2-7-bilde-av-oppdraget`, PR #13, og rettingen av en ustabil test i PR #14.

### Resultat
- **Pillow 13.0** i stedet for 12.x, fordi 12.x har kjente sårbarheter i JPEG- og PNG-dekodingen. Spinen, memlog, epics og epic-konteksten er oppdatert.
- **`oppdrag/bilde.py`** er eneste sted som åpner opplastede filer. Det sjekker størrelse, piksler og format etter innholdet, og lager en ny JPEG på høyst 1 600 px pluss en miniatyr på 640 px uten EXIF og GPS. Uventede feil fra dekoderen gir en feilmelding ved feltet.
- **Tabellen `oppdragsbilde`** og migrering 0004.
- **CSRF-mellomvaren:** filene legges i `request.state.filer`. Grensen for multipart rommer én fil pluss ett beholdt bilde. 413 for for store bilder har bildeteksten, og `Cache-Control` beholdes bare for `image/jpeg`.
- **Skjemaet:** et gyldig bilde beholdes ved 422 med «Valgt bilde» og «Fjern bildet». Ved redigering kan bildet byttes eller fjernes uten å sette `vesentlig_endret`.
- **Visning:** bilderutene har samme tilgangsregel som detaljene, kortet har miniatyren øverst, og detaljene viser bildet med bildeteksten som `alt`.
- **`bilde.js`:** skalerer ned i nettleseren, holder igjen innsendingen til bildet er klart, og sender bare én gang.
- **Seed:** tegner fire bilder selv.
- **Commits:** f163f5a, 76ee753, 830a3ed, 8da4775, faa6cec, 541452b, ff8a515 og bc585a3. Merget som f7f6206 (PR #13). Rettingen 7a31701 ligger i PR #14, merget som 55048ea.
- **Deploy:** den første kjøringen (46076598755) feilet i CI-steget, fordi en E2E-test krysset av «Fjern bildet» før `bilde.js` (`defer`) hadde koblet til lytteren. Produksjon ble ikke endret. Rettet i PR #14: `bilde.js` synkroniserer ved oppstart, og testen venter på `load`. Deploy 46077332663 er grønn med `Running upgrade 0003 -> 0004` og røyktesten OK.
- **Tester:** 1201 vanlige og 174 E2E-tester bestått lokalt. CI er grønn, også Postgres.
- **Review:** 20 funn. 15 er rettet og 5 avvist.
- `2-7` er satt til `done` i sprint-status.

### Åpne punkter
- Opplasting av et bilde i produksjon (Pillow på Vercel, binærdata i Supabase) er ikke prøvd manuelt. Det må gjøres med en ekte konto før demo.
- Tastatursjekk av bildefeltet, «Fjern bildet» og bildet i kort og detaljer, cirka fem minutter. Utsatt til 6.1.
