# Valideringsrapport – Nabolagshelten

- **DESIGN.md:** `_bmad-output/planning-artifacts/ux-designs/ux-G22-bernardo-kverno-moystad-nguyen-2026-11-07/DESIGN.md`
- **EXPERIENCE.md:** `_bmad-output/planning-artifacts/ux-designs/ux-G22-bernardo-kverno-moystad-nguyen-2026-11-07/EXPERIENCE.md`
- **Kjørt:** 2026-11-07T21:05:23+01:00

## Samlet vurdering

**Bare én gjennomgang ble kjørt: universell utforming.** Rubrikkgjennomgangen (de åtte kategoriene nedenfor) ble ikke kjørt, og det finnes ingen `review-rubric.md`. Kategoriene står derfor som «ikke vurdert». Rapporten gir ingen dom over flytdekning, tokenfullstendighet, komponentdekning, tilstandsdekning, visuelle referanser, overspesifisering, arv eller form. Der UU-gjennomgangen berører en kategori, er funnene nevnt med ID, men det er ikke en kategoridom.

Ifølge UU-gjennomgangen er spinene et sterkt utgangspunkt. Alle kontrasttallene i DESIGN.md stemmer når de regnes ut på nytt (laveste tekst 4,61:1, laveste kant 3,43:1, altså liten margin). Farge bærer aldri mening alene, og mockupene har ingen nestede interaktive elementer, ingen dupliserte id-er og ingen hull i overskriftsnivåene. Det som gjenstår, er kontrakten for **dynamikk og mekanikk**: statusmeldinger og fokus etter sidelasting, kategorifilteret, `autocomplete`, steg 2 i nytt oppdrag (dato og klokkeslett), den faste bunnmenyen ved zoom og skjermtastatur, og at testplanen ikke dekker 320 px.

**Funn: 0 kritiske, 4 høye, 10 medium, 13 lave (27 i alt).** Ingen funn er kritiske, men gjennomgangen sier at de fire høye (H1–H4) bør løses før spinene settes til ferdig.

## Kategoridommer

- Flytdekning (Flow coverage) – ikke vurdert. UU berører: H4 (steg 2 i UJ-1 mangler), M10 (skjermlesertest bare for UJ-1).
- Tokenfullstendighet (Token completeness) – ikke vurdert. UU berører: alle kontrastmål for bærende par er oppgitt og stemmer. Det sier ikke at tokensettet er komplett.
- Komponentdekning (Component coverage) – ikke vurdert. UU berører: H2, H3, H4, M1, M2, M3, M5, M7, L4.
- Tilstandsdekning (State coverage) – ikke vurdert. UU berører: H1, L8, L13, M10.
- Visuelle referanser (Visual reference coverage) – ikke vurdert. UU berører: H4 (steg 2 ikke mocket), M9 (snarveien mangler i mockupene).
- Overspesifisering (Bloat & overspecification) – ikke vurdert. UU sier ingenting om dette.
- Arv (Inheritance discipline) – ikke vurdert. UU berører: M4 (320 px ikke i NFR-6), M10 (NFR-7-punkter ikke knyttet til test).
- Form (Shape fit) – ikke vurdert. UU sier ingenting om dette.

## Funn etter alvorlighet

### Kritisk (0)

Ingen.

### Høy (4)

**[Universell utforming]** – H1. Kvitteringer, feiloppsummering og fokus etter sidelasting er motstridende og ikke spesifisert (4.1.3, 2.4.3, 3.3.1; EXPERIENCE.md § Component Patterns `message-success` / `message-error`, § State Patterns «Valideringsfeil», § Interaction Primitives «Fokus»)
`role="status"` og `role="alert"` blir ikke lest opp når de allerede finnes i HTML-en ved sidelasting. Spinene legger opp til server-rendrede sider, og da blir «Oppdraget er lagt ut.» og «Skjemaet har 2 feil.» stille. «Kvittering øverst i innholdet» og «fokus til sidens overskrift, så kvitteringen leses først» kan ikke begge stemme. «Fokus til første ugyldige felt» og samtidig `role="alert"` gir to kunngjøringer som avbryter hverandre.
Fix: Velg mønster i spinen. (a) Kvitteringen rett etter `h1`, eller fokus på kvitteringen (`tabindex="-1"`). (b) Ved valideringsfeil etter sidelasting: feiloppsummering med `tabindex="-1"` får fokus, overskrift «Skjemaet har 2 feil», hver feil er en lenke til feltet, `<title>` får «Feil: ». (c) `aria-live` bare for endringer uten sidelasting (KI, filter). [NOTE FOR ARCHITECTURE] om at server- eller klientrendring avgjør mønsteret.

**[Universell utforming]** – H2. Kategorifilteret i oversikten: mekanismen er uklar og kan gi brudd på 3.2.2 (3.2.2, 4.1.3, 4.1.2, 2.4.3; EXPERIENCE.md § Component Patterns `category-button`, § Interaction Primitives)
Spinen sier både `aria-pressed`, «ett valg om gangen» og «unntak fra automatisk innsending». Med radioknapper og `onchange`-innsending gir hver piltast en ny sidelasting (F36/F37), og tastaturbrukeren kommer ikke forbi «Alle». «Antall treff leses opp» går ikke sammen med vanlig sidelasting, og fokus havner øverst. Trykk på knapp som allerede er valgt, er ikke spesifisert.
Fix: Lås til `<button aria-pressed>`, skriv «knapper, ikke radioknapper». Uten sidelasting: fokus blir på knappen, synlig linje «3 ledige oppdrag» i `aria-live="polite"`. Med sidelasting: lenker (`?kategori=hage`) med `aria-current="true"`, fokus tilbake til valgt knapp, antallet i `h1` eller synlig linje rett etter. Trykk på valgt knapp gjør ingenting. Etter «Vis alle kategorier» går fokus til «Alle».

**[Universell utforming]** – H3. Formålet med feltene (`autocomplete`) er ikke spesifisert (1.3.5; EXPERIENCE.md § Information Architecture «Registrering», «Innlogging», «Rediger profil», § Component Patterns `input`)
Spinene nevner verken `autocomplete` eller felttyper. Bare postnummerfilteret i mockupen har `autocomplete="postal-code"`. axe melder ikke manglende `autocomplete`, så testen fanger det ikke.
Fix: Tabell i `input`: navn → `name`; e-post → `type="email" autocomplete="email"`; telefon → `type="tel" autocomplete="tel"`; postnummer → `inputmode="numeric" autocomplete="postal-code"`; fødselsdato → `autocomplete="bday"` med synlig format «dd.mm.åååå»; passord → `new-password` ved registrering, `current-password` ved innlogging og sletting. «Vis passord» får `aria-pressed` eller bytter tekst. Påkrevde felt får `required`.

**[Universell utforming]** – H4. Steg 2 i nytt oppdrag («Når?», «Hva tilbyr du?», forhåndsvisning) er verken spesifisert eller vist (2.1.1, 1.3.1, 3.3.2, NFR-7; EXPERIENCE.md § Accessibility Floor, NOTE FOR ARCHITECTURE, Åpne punkter)
NFR-7 nevner dato og klokkeslett særskilt, og dette er den risikable delen av kjerneflyten (UJ-1 steg 4). «Når?» er ikke en `fieldset`/`legend`-gruppe. «Beløp / Uten betaling» og beløpsfeltet mangler regler for plassering, etikett, `inputmode` og feiltekst. Native `type="date"` følger nettleserens språk, ikke `lang="nb"`, og kan forvirre Kari.
Fix: Komponentregler for «Når?» (`fieldset`, `legend`, etikettene «Dato» og «Klokkeslett», synlig format, feiltekster) og «Hva tilbyr du?» (radiogruppe, beløpsfeltet rett etter «Beløp» i DOM, flytter ikke fokus). Beslutning i arkitekturen før stories, og en mockup av steg 2. Forhåndsvisningen er en region med etikett, uten lenke og uten overskrift som kan forveksles med sidens.

### Medium (10)

**[Universell utforming]** – M1. Den faste bunnmenyen kan dekke fokus ved skjermtastatur, liggende skjerm og zoom (2.4.7, 1.4.10, 1.4.4; DESIGN.md § Layout, EXPERIENCE.md `bottom-nav`)
`padding-bottom` hindrer ikke at et felt med fokus havner bak menyen. Ved 400 % zoom tar menyen over 20 % av høyden. Mobilnettlesere legger faste elementer bak tastaturet, så antakelsen er verken realistisk eller ønsket.
Fix: `scroll-padding-bottom` lik menyhøyden; `position: static` ved `@media (max-height: 30em)` og stor tekst; fjern antakelsen; test liggende og ved 400 %.

**[Universell utforming]** – M2. Bunnmenyen har fast høyde og `white-space: nowrap`, og det gir overflyt ved stor tekst (1.4.4, 1.4.12, 1.4.10; DESIGN.md `bottom-nav` `itemHeight: 56px`; mockup-CSS `.bottomnav a`)
Målt: ved 200 % rot-skriftstørrelse er menylista 478 px på 360 px skjerm; «Mine oppdrag» trenger 245 px; høyden trengs cirka 69 px mot 56 px. Ved 320 px er kolonnene ikke «like brede» (98/124/98, med tekstavstand 90/153/76 px).
Fix: `min-height: 56px`, `white-space: normal`, `overflow-wrap: break-word`, `grid-template-columns: repeat(3, minmax(0, 1fr))`. Skriv at 56 px er minstehøyde.

**[Universell utforming]** – M3. `action-tag` med `maxLines: 2` kan bli implementert som avkorting (1.4.4, 1.4.10; DESIGN.md frontmatter `action-tag`, § Components)
Målt: ved 200 % brytes «Oppdraget er endret etter at du meldte interesse» over 4–5 linjer. En utvikler som leser `maxLines` som `line-clamp`, skjuler innhold.
Fix: «Normalt to linjer på 360 px ved 100 %. Aldri `line-clamp`, ellipse eller `overflow: hidden`.»

**[Universell utforming]** – M4. Reflow ved 320 px står i DESIGN, men verken i NFR-6 eller testplanen (1.4.10; DESIGN.md § Layout, PRD NFR-6, EXPERIENCE.md «Testes ved» punkt 4)
Test 4 sjekker bare 360, 768 og 1280 px og 200 % zoom. Mockupene flyter riktig om ved 320 px, men ingen test sikrer det i koden.
Fix: «320 px / 400 % zoom på 1280 px» i test 4. Foreslå for PRD-en (bmad-prd) at NFR-6 eller NFR-7 får «Innhold flyter om ved 320 CSS px (WCAG 1.4.10)».

**[Universell utforming]** – M5. Dialogen mangler regler for liten høyde og stor tekst (1.4.10, 2.1.1; DESIGN.md `dialog`, EXPERIENCE.md `dialog`)
Ved 400 % zoom eller liggende med stor tekst kan dialogen bli høyere enn skjermen, og knappene kan ikke nås.
Fix: `max-height: calc(100dvh - 32px); overflow-y: auto`, native `<dialog>` med `showModal()`. Inn i DESIGN.md og NOTE FOR ARCHITECTURE.

**[Universell utforming]** – M6. «Avbryt» som angre-valg og dialoger som ikke sier hvilket oppdrag det gjelder (3.2.4, 3.3.4, NFR-8; EXPERIENCE.md § Interaction Primitives, Bekreftelser)
«Fjerne Amir …», «Trekke deg …» og «Marker som utført …» bruker fortsatt «Avbryt» som angre-valg i en app der «Avbryt oppdrag» er ugjenkallelig. «Avbryte oppdraget?» fra en rad i Mine oppdrag viser ikke tittelen. Kari kan ikke se hvilket oppdrag hun avbryter.
Fix: Angre-tekster med verb («Nei, behold Amir», «Nei, jeg blir», «Ikke ennå»), og oppdragstittelen i dialogen.

**[Universell utforming]** – M7. Status, situasjon og merke skilles bare visuelt, og radlenken mangler beskrivelse (1.3.1, 2.4.4; EXPERIENCE.md `list-row`, `situation-label`, `action-tag`; key-mine-oppdrag.html)
Skjermleseren leser «Åpen Venter på svar Oppdraget er endret …» som løse tekstbiter. Ved tabbing høres bare tittelen, uten «Gi tilbakemelding».
Fix: Skjult tekst «Status: …», «Din situasjon: …», «Må gjøres: …», og `aria-describedby` fra radlenken til merkelinja. Skriv det inn i `list-row`.

**[Universell utforming]** – M8. Feilmeldingene er ikke komplette (3.3.1, 3.3.3; EXPERIENCE.md § Voice and Tone; sensorveiledningen kriterium 4)
Mangler for tittel, beskrivelse, kategori, dato, klokkeslett, beløp, telefon, passord, fødselsdato og e-post. Påkrevde felt er ikke merket med `required`/`aria-required`.
Fix: Fullstendig tabell (felt → regel → feiltekst med forslag til retting) og regelen «påkrevde felt har `required`, valgfrie står med «(valgfritt)»».

**[Universell utforming]** – M9. Snarveien «Hopp til innholdet» og sidetitlene er bare antakelser, og mockupene mangler snarveien (2.4.1, 2.4.2; EXPERIENCE.md § Accessibility Floor)
Fra 768 px kommer logo og tre menyvalg før `main`. Ingen av de fem mockupene har snarveien, og det finnes bare ett `<title>`-eksempel.
Fix: Gjør snarveien bindende (første fokuserbare element, synlig ved fokus, mål `main` med `tabindex="-1"`), og en `<title>`-tabell per side og tilstand.

**[Universell utforming]** – M10. Testplanen knytter ikke hvert NFR-7-punkt til en test, og flere tilstander mangler (NFR-7, SM-5; EXPERIENCE.md «Testes ved»)
axe-lista mangler steg 2, nettbrettskjemaet, KI-forslag og KI-feil, stjerner, tomtilstander, feilside, slettet bruker og detaljer for hjelperen. Skjermlesertesten dekker bare UJ-1.
Fix: Kolonne «Testes ved» i § Accessibility Floor, og utvidet liste over sider og tilstander (se testdekningstabellen i `review-accessibility.md`).

### Lav (13)

**[Universell utforming]** – L1. Fokusringen på kort og rader avhenger av `:has()` uten reserveløsning (2.4.7; mockup-CSS)
Uten `:has()` får kortet ingen fokusindikator; ringen er 1,67:1 mot `primary` med offset 0.
Fix: Ringen på lenkens `::after`, `outline-offset` ≥ 2 px, aldri `outline: none` uten erstatning.

**[Universell utforming]** – L2. Like knappenavn i samme visning (2.4.6, 2.4.4; key-nytt-oppdrag.html, key-detaljer.html, key-mine-oppdrag.html)
«Bruk»/«Forkast» × 3, «Se profil» × 3, radsnarveier. Mockupen har `aria-describedby` på «Se profil», men spinen krever det ikke.
Fix: Krev `aria-describedby` til tittel eller navn i spinen; synlig tekst først (2.5.3).

**[Universell utforming]** – L3. Merket «Velg hjelper» står over overskriften «3 har meldt interesse» (1.3.2; EXPERIENCE.md detaljer-tabellen, key-detaljer.html)
Overskriftsnavigasjon lander på `h2` og går glipp av merket.
Fix: Merket etter overskriften i DOM, eller i overskriften.

**[Universell utforming]** – L4. Stjernene ved tilbakemelding: synlige ytterpunkter, `legend` og tilstand (2.5.3, 1.3.1, 2.4.7; EXPERIENCE.md `star-rating`)
«Dårlig»/«Veldig bra» er ikke med i navnene; `legend` er ikke den synlige etiketten; fokus og fylling er ikke spesifisert.
Fix: «1 av 5 stjerner, dårlig» osv.; `legend` = synlig spørsmål; `label:has(:focus-visible)` og `:has(:checked)`. Gjelder også kategori-radioene.

**[Universell utforming]** – L5. Små lenker i tekst bryter med «også lenker har 48 px trykkflate» (NFR-7; key-profil.html, `phone-box`)
«Kari» er cirka 38 px bred.
Fix: Unnta lenker i løpende tekst; frittstående lenker minst 48 × 48 px; telefonlenken minst 48 px høy.

**[Universell utforming]** – L6. Kategoriknappene i skjemaet bryter ord midt i ordet ved tekstavstand (1.4.12; DESIGN.md `category-button`, mockup-CSS `overflow-wrap:anywhere`)
«Teknologihjelp» brytes over to linjer ved 360 og 320 px.
Fix: `hyphens: auto` i stedet for `anywhere`, eller én kolonne under cirka 22em.

**[Universell utforming]** – L7. Tvungne farger, redusert bevegelse og skjermretning er ikke nevnt (1.3.4, 1.4.11; EXPERIENCE.md § Accessibility Floor)
I Windows høykontrast forsvinner `box-shadow`-delen av fokus og flata på `action-tag`; trolig i orden, men ikke testet.
Fix: Én linje hver om skjermretning, `prefers-reduced-motion` og `forced-colors: active`.

**[Universell utforming]** – L8. «Tilbake» betyr to ting i nytt oppdrag, og fokus ved tilbake til steg 1 er ikke spesifisert (3.2.4, 2.4.3; EXPERIENCE.md § Interaction Primitives «To steg»)
Fix: «Tilbake til steg 1», fokus til `h1`, `<title>` byttes per steg.

**[Universell utforming]** – L9. Antall treff og tallet i menyen er ikke forklart for den som ser (kognitivt; key-oversikt.html, `nav-badge`)
«4 ledige oppdrag» er bare skjult tekst; «2» ved Mine oppdrag står uten forklaring.
Fix: Vis antallet synlig; vurder «2 oppdrag trenger at du gjør noe.» øverst i Mine oppdrag.

**[Universell utforming]** – L10. Ord og forkortelser som kan være uklare for Kari (NFR-8, kognitivt)
«Forkast», «14. nov.» og «Meldt før endring».
Fix: «Ikke bruk», måneder skrevet fullt; ta det med i SM-4-testen.

**[Universell utforming]** – L11. Angre-kolonnen heter «(lenke)», og `aria-disabled` stopper ikke innsending med Enter (4.1.2; EXPERIENCE.md Bekreftelser, `button-disabled`)
Fix: Angre-valget er en `<button>`, ikke `<a>`; skjemaet stopper innsending mens forespørselen pågår.

**[Universell utforming]** – L12. To `aria-current="page"` på Mine oppdrag (4.1.2; key-mine-oppdrag.html)
Fix: Fanen `aria-current="page"`, menyvalget `aria-current="true"`, eller skriv i spinen at begge er tillatt.

**[Universell utforming]** – L13. Når innloggingen utløper, kan utfylt skjema gå tapt (2.2.1, 2.2.5; EXPERIENCE.md «Innlogging utløpt»)
Varighet og sperre er i orden, men spinen sier ikke at innholdet beholdes ved utløp under «Publiser».
Fix: «Utfylt innhold beholdes ved ny innlogging, eller brukeren får beskjed før det går tapt.»

## Mekaniske merknader

- Rubrikkgjennomgangen ble ikke kjørt, så navneavvik, kryssreferanser, frontmatter og Mermaid-syntaks er ikke kontrollert.
- Alle kontrasttallene i DESIGN.md § Colors stemmer med to desimaler. Margin er liten, så nye bakgrunner må kontrolleres på nytt.
- Mockupene har ingen nestede interaktive elementer, ingen dupliserte id-er og ingen hull i overskriftsnivåene. Alle SVG-er har `aria-hidden="true" focusable="false"`.
- Steg 2 i nytt oppdrag har ingen mockup (H4).

## Gjennomgangsfiler

- `review-accessibility.md`
- `review-rubric.md` – ikke kjørt
