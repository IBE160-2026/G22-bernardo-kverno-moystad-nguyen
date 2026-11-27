# Story 2.6: Utfylt skjema går ikke tapt når innloggingen utløper

## 2026-11-28 kl. 00:28 — Heidi

### Oppgave
Siste story i den autonome kjøringen av Epic 2. Fullstendig AD-7: en innsending uten gyldig sesjon gir en 401-side som tar vare på det som er fylt ut. Brukeren logger inn på samme side, og den opprinnelige innsendingen blir behandlet (AD-7, FR-2, FR-3, FR-27, AR-17).

### Plan
- Spec: [spec-2-6-utlopt-innlogging.md](../../_bmad-output/implementation-artifacts/spec-2-6-utlopt-innlogging.md). De to åpne spørsmålene ble løst med anbefalt alternativ:
  - er det nye bildet tapt etter innlogging, lagres ingenting, og brukeren får «Velg bildet på nytt.» ved bildefeltet;
  - `/logg-ut` er offentlig, så utlogging virker uten passord når sesjonen er utløpt.
- Implementering i en subagent, så review i tre lag og retting av funnene med samme subagent.
- Branch `story/2-6-utlopt-innlogging`, PR #15, grønn CI, merge og deploy.

### Resultat
- **401-siden:** skjulte felt for alt som ble sendt (unntatt passord, CSRF og felt med `_`), innloggingsfelt og «Logg inn» til samme adresse, som multipart.
- **Innloggingen:** mellomvaren logger inn med `prov_innlogging`, felles med `/logg-inn`, i en egen transaksjon (unntak i AD-17). Den fjerner `_innlogging_*` og sender innsendingen videre til ruta som den nye brukeren.
- **Feil:** feil passord gir 401-siden igjen med de skjulte feltene. En databasefeil gir en generell feil, ikke 500. Ingen personopplysninger logges.
- **Bilde:** «Velg bildet på nytt etter innlogging.» står på 401-siden, og «Velg bildet på nytt.» kommer etter innlogging.
- **Dokumenter:** AD-4, AD-7 og AD-17 i spinen, memlog og «Innlogging utløpt» i EXPERIENCE er oppdatert.
- **Commits:** 3ae1975, c6c669b, d297dbe, e8461aa, bee706a, d4221af og c6e8a30. Merget som 50f5279 (PR #15).
- **Tester:** 1246 vanlige og 185 E2E-tester bestått lokalt. CI er grønn på alle fire jobber.
- **Deploy:** run 46082279166 er grønn, med røyktesten OK. Ingen migrering.
- **Review:** 18 funn. 10 er rettet, 1 er utsatt og 7 avvist.
- `2-6` og `epic-2` er satt til `done` i sprint-status. Epic 2 er ferdig 28.11, før fristen 3.12.

### Åpne punkter
- Tastatursjekk av 401-siden og flyten, cirka fem minutter. Utsatt til 6.1.
- Skjemaene i Epic 4 og 5 må unngå gjentatte feltnavn, eller så må mellomvaren bruke `form.multi_items()` (`deferred-work.md`).
- CSRF-cookien har ingen `Max-Age`, så etter at nettleseren har vært lukket, gir en innsending 403 før AD-7 slår inn (`deferred-work.md`).
- Retrospektiv for Epic 2 (valgfri) før Epic 3 starter.
