# Story 2.5: Redigere og avbryte oppdrag

## 2026-11-27 kl. 18:42 — Heidi

### Oppgave
Femte story i den autonome kjøringen av Epic 2. Oppdragsgiveren kan redigere et åpent oppdrag og avbryte det med bekreftelse. Snarveiene «Endre tidspunkt» og «Avbryt oppdrag» kommer i detaljene og i «Mine oppdrag», og `Konflikt` får en handler (FR-6, FR-7, FR-8, NFR-5, AD-2, AD-3, UX-DR18, UX-DR26).

### Plan
- Spec: [spec-2-5-redigere-og-avbryte.md](../../_bmad-output/implementation-artifacts/spec-2-5-redigere-og-avbryte.md). De to åpne spørsmålene ble løst med anbefalt alternativ:
  - etter avbrudd fra «Mine oppdrag» går brukeren tilbake dit (`fra=mine`);
  - redigeringen vises på én skjerm uten `steg.js`.
- Implementering i en subagent, så review i tre lag og retting av funnene med samme subagent.
- Branch `story/2-5-redigere-og-avbryte`, PR #12, grønn CI, merge og deploy.

### Resultat
- **Redigering:** `/oppdrag/{id}/rediger` bruker det felles skjemaet (`ny.html` er omdøpt til `skjema.html`). `valider_oppdrag` er delt ut, og `rediger_oppdrag` bruker én betinget `UPDATE` som setter `vesentlig_endret` bare når tidspunkt, beløp eller postnummer endres.
- **Avbrudd:** bekreftelsesside med GET, avbrudd med POST via `endre_status`, og `fra=mine`.
- **Dialog:** `dialog.js` og makroen `bekreft_dialog`, som Epic 3 og 4 gjenbruker.
- **Konflikt:** handler med feilmelding i signert cookie. «database is locked» blir `Konflikt` og logges.
- **Snarveier:** «Rediger», «Endre tidspunkt» og «Avbryt oppdrag» i detaljene og i radene med merket i «Mine oppdrag».
- **Commits:** 4565cbe, 2496458, 93d30dc, b8a87a9, fa9c2d4, 8c71c22 og 0b797b3. Merget som cff2192 (PR #12).
- **Tester:**
  - 1063 vanlige og 150 E2E-tester bestått lokalt. CI er grønn på alle fire jobber.
  - Samtidighetstesten bestod mot både SQLite og Postgres (2 tester i `test-postgres`), og den sjekker at transaksjonene overlapper.
- **Deploy:** run 46043464403 er grønn, med røyktesten OK. Ingen migrering.
- **Review:** 17 funn. 10 er rettet, og 7 avvist (blant dem dobbel avbrudd, der EXPERIENCE UJ-1 sier at den andre forespørselen skal få feilmeldingen). Ett funn som fantes fra før, er utsatt.
- Implementeringen ble avbrutt én gang av bruksgrensen og fortsatte etter nullstillingen.
- `2-5` er satt til `done` i sprint-status.

### Åpne punkter
- Tastatursjekk av redigering, dialogen og snarveiene, cirka fem minutter. Utsatt til 6.1 (retro T-5).
- Detaljsiden ruller vannrett ved 320 px med 200 % rotstørrelse (366 px), og det gjaldt før 2.5 også. Står i `deferred-work.md` og bør tas i 6.1 (T3).
