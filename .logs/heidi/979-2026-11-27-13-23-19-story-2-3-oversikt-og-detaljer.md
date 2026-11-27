# Story 2.3: Finne oppdrag i oversikten og se detaljene

## 2026-11-27 kl. 13:23 — Heidi

### Oppgave
Tredje story i den autonome kjøringen av Epic 2. Hjelperen finner åpne oppdrag i sitt postnummer, filtrerer på kategori og postnummer og åpner detaljene, med oppdragsgiverblokken (FR-9, FR-10, FR-11, AR-13, AR-27, UX-DR24, UX-DR25). Retro T-2 og R7 er tatt med.

### Plan
- Spec: [spec-2-3-oversikt-og-detaljer.md](../../_bmad-output/implementation-artifacts/spec-2-3-oversikt-og-detaljer.md). Det ene åpne spørsmålet (feiloppsummering ved ukjent postnummer i filteret) ble løst med anbefalt alternativ: bare feilen ved feltet, slik EXPERIENCE § Filtrene sier.
- Implementering i en subagent, så review i tre lag og retting av funnene med samme subagent.
- Branch `story/2-3-oversikt-og-detaljer`, PR #10, grønn CI, merge og deploy.

### Resultat
- **Oversikten:** kort som én lenke i 1, 2 eller 3 kolonner, filter på kategori og postnummer (`filterlenke` tar bare med `kategori` og `postnummer`), begge tomtilstandene og fokus etter adressen. Et ukjent postnummer gir feilen ved feltet, og lista står uendret.
- **Detaljene:** blokken «Lagt ut av …» med erfaring og «Se profil» for alle andre enn oppdragsgiveren.
- **Service og klient:**
  - `utgatt` er eneste definisjon av passert tidspunkt (AD-3), og `endre_status` bruker den også.
  - Nye `ledige_oppdrag` og `erfaring`, og `Erfaring` i `domene`.
  - Ny `fokus.js`.
- **Retro R7:** `Innlogget` har `postnummer` fra samme spørring, så oversikten slår ikke opp brukeren på nytt.
- **Retro T-2:** `neste` bæres gjennom «Registrer deg» og registreringen, og sendes videre til `trygg_neste(neste)`.
- **Seed:** et 13. oppdrag, utført med Nora som hjelper.
- **Dokumenter:** README, AD-4 i spinen og T-2-kriteriet i `epics.md` er oppdatert.
- **Commits:** 70e1df8, b56e810, c2691fa, a1d93bc, ed96f97, c2c348c, d60786a, c4ad7de, 6a42a57, 299cf6b og 0f4728a. Merget som 9be4d5d (PR #10).
- **Tester:** 885 vanlige og 108 E2E-tester bestått lokalt. CI er grønn på alle fire jobber.
- **Deploy:** run 45997843712 er grønn, med røyktesten OK. Ingen migrering.
- **Review:** Verification Gap fant ingen hull. 14 funn: 3 er rettet (ukjente parametre i filterlenkene, avrunding av snittet og README-teksten om antallet) og 11 avvist. Ingenting er utsatt.
- Reviewen ble avbrutt én gang av bruksgrensen, og reviewerne fortsatte der de stoppet etter nullstillingen.
- `2-3` er satt til `done` i sprint-status.

### Åpne punkter
- Tastatursjekk av oversikten, filtrene og detaljene, cirka fem minutter. Utsatt til 6.1 (retro T-5).
