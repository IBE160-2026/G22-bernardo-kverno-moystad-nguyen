# Bilde av oppdraget (correct course)

## 2026-11-27 kl. 09:04 — Heidi

### Oppgave
Heidi oppdaget et krav som manglet: oppdragsgiveren skal kunne legge ved et bilde som viser oppdraget sammen med beskrivelsen, og bildet skal vises i oversikten når det er tatt med. Hun ba om at kravet fikk en plass i planen, og at alle steder som berøres, ble oppdatert.

### Plan
- Arbeidsflyten `bmad-correct-course` i batch-modus. Valgene ble tatt etter anbefalt alternativ, som Heidi har delegert for Epic 2.
- Endringsforslaget: [sprint-change-proposal-2026-11-27.md](../../_bmad-output/planning-artifacts/sprint-change-proposal-2026-11-27.md).
- Dokumentene ble oppdatert i et eget worktree på branchen `endring/bilde-av-oppdrag`, så arbeidet med story 2.2 ikke ble forstyrret.

### Resultat
- **PRD v1.3:** ny FR-27 «Bilde av oppdraget» (Bør). Linjer i FR-4, FR-9, FR-10, NFR-9, NFR-12, SM-1, SM-5, §6.1, §9.1 og §9.2.
- **Arkitektur:** ny AD-18.
  - Bildet lagres i databasen, i tabellen `oppdragsbilde`.
  - Pillow koder bildet om, så EXIF og GPS forsvinner.
  - Bildet vises bak tilgangsregelen i FR-9.
  - Endringer i AD-1, AD-7, Stack, datamodell, kildetre og Klientatferd.
- **UX:** bildefelt og «Hva viser bildet?» i EXPERIENCE.md og DESIGN.md, kort med bilde, bildet i detaljene og T1-tilstander.
- **Epics:** FR-27, AR-31 og UX-DR33. Ny story 2.7 (bygges etter 2.5 og før 2.6), og kriterier i 2.6, 4.5, 6.1 og 6.3.
- **sprint-status og epic-2-context.md:** `2-7-bilde-av-oppdraget: backlog` står før 2-6.
- **Commits:** 6359298, 33942b0, 5121a46 og a9a39b4. Merget som dd23651 (PR #8, grønn CI).
- **Hovedvalg:**
  - ett valgfritt bilde per oppdrag, i JPEG, PNG eller WebP og høyst 4 MB;
  - påkrevd alt-tekst;
  - nedskalering i nettleseren med `bilde.js`;
  - et gyldig bilde beholdes ved 422 (`bilde_beholdt`);
  - fire eksempelbilder som seed tegner selv;
  - mockupene oppdateres ikke.

### Åpne punkter
- Story 2.7 bygges etter 2.5. Hvis tiden blir knapp, kuttes 2.6 først og deretter 2.7. Kuttet føres i PRD §6.1 og endringsloggen.
- Kjent begrensning: uten JavaScript stopper Vercel bilder over cirka 4,5 MB med sin egen feilside (FR-27).
