# Arkitektur-validering og README

## 2026-11-23 kl. 18:40 — Heidi

### Oppgave
Validere arkitekturspinen og få oversikt over neste steg (`bmad-help`). Heidi lurte også på om UX-arbeidet mangler noe, fordi faglærer nevnte skillen Impeccable og at han liker SVG-baserte design. Til slutt: rette det som ble anbefalt rettet.

### Plan
- `bmad-architecture` (validate): kjørte `lint_spine.py` og leste spinen mot `.memlog.md`. De parallelle reviewerne ble ikke kjørt, fordi spinen fortsatt er en uutfylt mal.
- `bmad-help`: kartla status (brief, PRD og UX ferdig, arkitektur pågår, epics og stories gjenstår).
- Sjekket sensorveiledningen (kriterium 4) mot UX-dokumentene og PRD-en.
- Rettet README.

### Resultat
- **Arkitekturspinen** (`_bmad-output/planning-artifacts/architecture/architecture-…-2026-11-08/ARCHITECTURE-SPINE.md`) er ikke klar. Den er bare malteksten (13 plassholdere fra lint). Beslutningene i memlog er ikke destillert til `AD-n`. Flask, SQLAlchemy 2.0 og SQLite/Postgres står bare som antakelse. CSRF, passordhash, KI-adapter, avhengighetsretning, deployment og kapabilitetskartet mangler. `technology.md` i arkitekturmappen beskriver et annet prosjekt (Pytagoras Website V2) og bør ikke brukes som kilde.
- **UX:** ingen skill (Impeccable) eller SVG er krav i sensorveiledningen. Eksisterende arbeid (DESIGN.md, EXPERIENCE.md, 11 HTML-mockups og tilgjengelighetsgjennomgangen) dekker «spor av designarbeid». NFR-7 og SM-5 i PRD-en samsvarer med Accessibility Floor i EXPERIENCE.md.
- **README.md:** statusraden «UX-skisser: Utkast» er erstattet med «UX-design: Ferdig», og arkitekturen står som «Pågår». Dokumentasjonstabellen har fått lenker til DESIGN.md, EXPERIENCE.md, mockups og tilgjengelighetsgjennomgangen. Mappestrukturen nevner UX og arkitektur. README-endringen er ikke committet.

### Åpne punkter
- Fullfør arkitekturspinen med `bmad-architecture` (update): bekreft Flask, SQLAlchemy og SQLite/Postgres, avgjør CSRF, passordhash, KI-adapter og avhengighetsretning, pin versjonene, ta med deployment (Vercel + lokalt) og kapabilitetskartet mot FR/NFR, og kjør reviewer-gate.
- Avklar hva `technology.md` i arkitekturmappen skal være. Den beskriver et annet prosjekt og kan forvirre sensor.
- Stories: ta testhullene fra `review-accessibility.md` inn som akseptansekriterier: kontrast på kanter og fokus, støtteflytene i tastaturtesten, flere sider og tilstander i axe-testen, 320 px og tekstavstand.
- Valgfritt: noen få SVG-skisser (for eksempel navigasjonsflyt), siden faglærer liker det. Lav prioritet.
