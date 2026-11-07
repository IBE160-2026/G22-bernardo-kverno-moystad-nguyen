# Gjennomgang: universell utforming – Nabolagshelten

Reviewer Gate, linse universell utforming. Gjennomgått 2026-11-07: `DESIGN.md`, `EXPERIENCE.md`, `.working/key-oversikt.html`, `key-nytt-oppdrag.html`, `key-detaljer.html`, `key-mine-oppdrag.html` og `key-profil.html`, målt mot WCAG 2.1 AA, PRD NFR-6, NFR-7, NFR-8, NFR-11, SM-4 og SM-5, og sensorveiledningen, kriterium 4. Ingen filer er endret, bortsett fra at denne rapporten er skrevet.

**Metode:** Kontrastforholdene er regnet ut på nytt med et skript (relativ luminans etter WCAG 2.1) for alle fargepar i DESIGN.md og i mockupenes CSS. HTML-en i mockupene er analysert maskinelt for nestede interaktive elementer, dupliserte id-er, overskriftsnivåer, felt uten etikett, `autocomplete`, live-regioner og SVG-er uten `aria-hidden`. Mockupene er også målt i headless Chrome ved 360 og 320 px, med og uten tekstavstand etter 1.4.12 og med 200 % rot-skriftstørrelse.

## Samlet vurdering

Spinene er et sterkt utgangspunkt. Hvert eneste kontrasttall i DESIGN.md stemmer når det regnes ut på nytt. Farge bærer aldri mening alene, og mockupene har ingen nestede interaktive elementer, ingen dupliserte id-er og ingen hull i overskriftsnivåene. Det som gjenstår, er kontrakten for **dynamikk og mekanikk**. Det gjelder hvordan statusmeldinger og fokus oppfører seg etter en sidelasting, hvordan kategorifilteret virker, `autocomplete` i skjemaene, steg 2 i nytt oppdrag (dato og klokkeslett) og den faste bunnmenyen ved zoom og skjermtastatur. Testplanen dekker heller ikke 320 px. Ingen funn er kritiske, men de fire høye bør løses før spinene settes til ferdig.

## Kontrastberegning

Krav: tekst ≥ 4,5:1 (1.4.3); kanter, fokusring, tilstandsmerker og grafikk ≥ 3:1 (1.4.11). All tekst er under 24 px eller under 18,66 px fet, så kravet for stor tekst (3:1) brukes ikke. «Informativt» betyr at paret ikke er et krav, fordi en kant, tekst eller avstand bærer grensen.

| Element | Forgrunn | Bakgrunn | Ratio | Krav | Bestått |
|---|---|---|---|---|---|
| Brødtekst | `ink` #2F302D | `surface-page` #E3D3B3 | 9,00:1 | 4,5:1 | ja |
| Brødtekst | `ink` #2F302D | `surface-card` #EEE5D3 | 10,61:1 | 4,5:1 | ja |
| Felttekst | `ink` #2F302D | `surface-input` #F4E8CF | 10,93:1 | 4,5:1 | ja |
| Dempet tekst / hjelpetekst | `ink-muted` #6E4E3A | `surface-page` #E3D3B3 | 5,06:1 | 4,5:1 | ja |
| Dempet tekst (metalinje i rad) | `ink-muted` #6E4E3A | `surface-card` #EEE5D3 | 5,96:1 | 4,5:1 | ja |
| Dempet tekst | `ink-muted` #6E4E3A | `surface-input` #F4E8CF | 6,14:1 | 4,5:1 | ja |
| Primærknapp, topplinjetekst, menyvalg | `on-primary`/`topbar-text` #F4E8CF | `primary`/`topbar` #47553F | 6,55:1 | 4,5:1 | ja |
| Logo (tekst i `brand-icon`) | `brand-icon` #EBC7BC | `topbar` #47553F | 5,09:1 | 4,5:1 | ja |
| Lenke / sekundærknapp | `link` #47553F | `surface-card` #EEE5D3 | 6,36:1 | 4,5:1 | ja |
| Lenke / sekundærknapp | `link` #47553F | `surface-page` #E3D3B3 | 5,39:1 | 4,5:1 | ja |
| Lenke | `link` #47553F | `surface-input` #F4E8CF | 6,55:1 | 4,5:1 | ja |
| `nav-badge`, `action-tag` | `badge-fg` #4B3324 | `badge-bg` #EBC7BC | 7,47:1 | 4,5:1 | ja |
| `category-chip` | `chip-fg` #4B3324 | `chip-bg` #EEE5D3 | 9,33:1 | 4,5:1 | ja |
| Status Åpen | `status-open-fg` #47553F | `status-open-bg` #CBDDC1 | 5,55:1 | 4,5:1 | ja |
| Status Hjelper valgt | `status-chosen-fg` #81432C | `status-chosen-bg` #EBC7BC | 4,84:1 | 4,5:1 | ja |
| Status Utført | `status-done-fg` #4D5829 | `status-done-bg` #F4E8CF | 6,30:1 | 4,5:1 | ja |
| Status Avbrutt | `status-cancelled-fg` #5E5347 | `status-cancelled-bg` #D2CABD | 4,61:1 | 4,5:1 | ja (lavest i appen) |
| Feiltekst | `error` #81432C | `surface-card` #EEE5D3 | 6,05:1 | 4,5:1 | ja |
| Feiltekst ved felt | `error` #81432C | `surface-page` #E3D3B3 | 5,13:1 | 4,5:1 | ja |
| Feiltekst | `error` #81432C | `surface-input` #F4E8CF | 6,24:1 | 4,5:1 | ja |
| Suksesstekst | `success` #47553F | `surface-card` / `surface-page` | 6,36 / 5,39:1 | 4,5:1 | ja |
| Telefonboks | `ink` #2F302D | `status-chosen-bg` #EBC7BC | 8,49:1 | 4,5:1 | ja |
| KI-forslagsboks | `ink` #2F302D | `surface-page` #E3D3B3 | 9,00:1 | 4,5:1 | ja |
| Deaktivert knappetekst | `disabled-fg` #5E5347 | `disabled-bg` #D2CABD | 4,61:1 | unntatt (deaktivert) | ja likevel |
| Feltkant | `border` #7B6C5D | `surface-input` #F4E8CF | 4,17:1 | 3:1 | ja |
| Feltkant, kategoriknapp, chip, KI-boks, inaktiv fane | `border` #7B6C5D | `surface-page` #E3D3B3 | 3,43:1 | 3:1 | ja (lavest av kantene) |
| Kort-, rad-, chip- og kategoriknappkant | `border` #7B6C5D | `surface-card` #EEE5D3 | 4,05:1 | 3:1 | ja |
| Feilkant (2 px) | `error` #81432C | `surface-input` / `surface-page` | 6,24 / 5,13:1 | 3:1 | ja |
| Valgt kategoriknapp (3 px) | `primary` #47553F | `surface-page` / `surface-card` | 5,39 / 6,36:1 | 3:1 | ja |
| Hover-/fokuskant på kort og rad | `primary` #47553F | `surface-page` #E3D3B3 | 5,39:1 | 3:1 | ja |
| Fokusring | `focus` #2F302D | `surface-page` / `surface-card` / `surface-input` | 9,00 / 10,61 / 10,93:1 | 3:1 | ja |
| Fokusring i topplinje og bunnmeny | `topbar-focus` #EBC7BC | `topbar` #47553F | 5,09:1 | 3:1 | ja |
| Aktiv-strek i meny | `nav-indicator` #EBC7BC | `topbar` #47553F | 5,09:1 | 3:1 | ja |
| Aktiv fane-strek (4 px) | `primary` #47553F | `surface-page` #E3D3B3 | 5,39:1 | 3:1 | ja |
| `nav-badge`-flate mot menyen | `badge-bg` #EBC7BC | `topbar` #47553F | 5,09:1 | 3:1 | ja |
| Stjerne fylt | `primary` #47553F | `surface-page` / `surface-card` | 5,39 / 6,36:1 | 3:1 | ja |
| Stjerne omriss | `border` #7B6C5D | `surface-page` / `surface-card` | 3,43 / 4,05:1 | 3:1 | ja |
| Pil › i lenkerad | `link` #47553F | `surface-card` #EEE5D3 | 6,36:1 | 3:1 | ja |
| Statuskant Åpen / valgt / utført / avbrutt | fg-fargene | `surface-card` #EEE5D3 | 6,36 / 6,05 / 6,12 / 5,99:1 | 3:1 | ja |
| Statuskant Åpen / valgt / utført / avbrutt | fg-fargene | `surface-page` #E3D3B3 | 5,39 / 5,13 / 5,19 / 5,08:1 | 3:1 | ja |
| Sekundærknappkant | `link` #47553F | `surface-page` / `surface-card` | 5,39 / 6,36:1 | 3:1 | ja |
| Primærknappflate | `primary` #47553F | `surface-page` / `surface-card` | 5,39 / 6,36:1 | 3:1 | ja |
| Telefonboks-kant | `status-chosen-border` #81432C | `surface-card` / `surface-page` | 6,05 / 5,13:1 | 3:1 | ja |
| Meldingsstripe feil / suksess | `error` / `success` | `surface-card` #EEE5D3 | 6,05 / 6,36:1 | 3:1 | ja |
| Deaktivert knappekant | `disabled-fg` #5E5347 | `surface-page` #E3D3B3 | 5,08:1 | unntatt | ja likevel |
| Deaktivert knappeflate | `disabled-bg` #D2CABD | `surface-page` #E3D3B3 | 1,10:1 | unntatt | – (kanten bærer) |
| `action-tag`-flate, uten kant | `badge-bg` #EBC7BC | `surface-card` / `surface-page` | 1,25 / 1,06:1 | informativt | – (teksten bærer) |
| Status Utført-flate | `status-done-bg` #F4E8CF | `surface-card` #EEE5D3 | 1,03:1 | informativt | – (kanten bærer) |
| Feltflate / kortflate mot side | `surface-input` / `surface-card` | `surface-page` #E3D3B3 | 1,21 / 1,18:1 | informativt | – (kanten bærer) |
| Fokusring rett mot primærknapp | `focus` #2F302D | `primary` #47553F | 1,67:1 | informativt | – (krever offset ≥ 2 px, se L1) |
| Fokusring mot aktiv-strek i bunnmenyen | `topbar-focus` #EBC7BC | `nav-indicator` #EBC7BC | 1,00:1 | informativt | – (ringen syns på de tre andre sidene) |
| Dialogkort mot slør (55 % antrasitt over sand = #807969) | `surface-card` #EEE5D3 | #807969 | 3,46:1 | informativt | – |

**Konklusjon:** Alle par med krav består, og alle tallene i DESIGN.md § Colors stemmer med to desimaler. Den laveste teksten er 4,61:1 og den laveste kanten 3,43:1, så det er lite margin. En ny bakgrunn, for eksempel champagne-kort på sand, må kontrolleres på nytt. Se T6 under Testdekning.

## Funn

### Kritisk

Ingen.

### Høy

**H1. [høy] Kvitteringer, feiloppsummering og fokus etter sidelasting er motstridende og ikke spesifisert** (4.1.3, 2.4.3, 3.3.1; EXPERIENCE.md § Component Patterns `message-success` / `message-error`, § State Patterns «Valideringsfeil», § Interaction Primitives «Fokus», Foundation/State Patterns «Sidelasting: vanlig sidelasting»)
- `role="status"` og `role="alert"` blir ikke lest opp når de allerede finnes i HTML-en ved sidelasting. Live-regioner leser bare opp endringer. Spinene legger opp til server-rendrede sider («vanlig sidelasting»), og da blir «Oppdraget er lagt ut.» og «Skjemaet har 2 feil.» stille.
- «Kvittering øverst i innholdet» og «fokus til sidens overskrift, så kvitteringen leses først» kan ikke begge stemme. Står kvitteringen over `h1`, hopper skjermleseren over den når fokus settes på `h1`.
- «Fokus til første ugyldige felt» og samtidig `role="alert"` gir to kunngjøringer som avbryter hverandre.

*Fix:* Velg mønster i spinen, uavhengig av rammeverk. (a) Kvitteringen står rett **etter** `h1`, eller fokus settes på selve kvitteringen (`tabindex="-1"`). (b) Ved valideringsfeil etter sidelasting: en feiloppsummering øverst i skjemaet med `tabindex="-1"` får fokus. Den har overskriften «Skjemaet har 2 feil», og hver feil er en lenke til feltet. `<title>` får forstavelsen «Feil: ». (c) `aria-live` brukes bare for endringer uten sidelasting (KI, filter). Legg inn [NOTE FOR ARCHITECTURE] om at valget mellom server- og klientrendring avgjør hvilket mønster som gjelder.

**H2. [høy] Kategorifilteret i oversikten: mekanismen er uklar og kan gi brudd på 3.2.2** (3.2.2, 4.1.3, 4.1.2, 2.4.3; EXPERIENCE.md § Component Patterns `category-button`, § Interaction Primitives «Ikke tillatt … (unntak: kategorifilteret)»)
- Spinen sier både «`aria-pressed`», «ett valg om gangen» og «unntak fra automatisk innsending ved valg i skjema». «Ett valg om gangen» er radiosemantikk, og med radioknapper og `onchange`-innsending gir hver piltast en ny sidelasting. Det er brudd på 3.2.2 (F36/F37), og tastaturbrukeren kommer ikke forbi «Alle».
- «Antall treff leses opp» går ikke sammen med en vanlig sidelasting (se H1), og fokus havner øverst på siden etter lasting.
- Spinen sier ikke hva som skjer når brukeren trykker på en knapp som allerede er valgt.

*Fix:* Lås mønsteret til `<button aria-pressed>` (aldri radio med automatisk innsending), og skriv «knapper, ikke radioknapper» i spinen. Uten sidelasting: fokus blir på knappen, og en **synlig** linje «3 ledige oppdrag» står i `aria-live="polite"`. Med sidelasting: lenker (`?kategori=hage`) med `aria-current="true"`, fokus tilbake til valgt knapp og antallet i `h1` eller i en synlig linje rett etter. Trykk på knappen som allerede er valgt, gjør ingenting. Etter «Vis alle kategorier» går fokus til «Alle».

**H3. [høy] Formålet med feltene (`autocomplete`) er ikke spesifisert** (1.3.5; EXPERIENCE.md § Information Architecture «Registrering», «Innlogging», «Rediger profil», § Component Patterns `input`)
Spinene nevner verken `autocomplete` eller felttyper. Bare postnummerfilteret i mockupen har `autocomplete="postal-code"`. Registrering, innlogging og rediger profil er med i SM-5, og axe melder ikke manglende `autocomplete`. Feilen blir derfor ikke oppdaget av testen.

*Fix:* Legg til en tabell i `input`. Navn → `name`. E-post → `type="email" autocomplete="email"`. Telefon → `type="tel" autocomplete="tel"`. Postnummer → `inputmode="numeric" autocomplete="postal-code"`. Fødselsdato → `autocomplete="bday"` med synlig format «dd.mm.åååå». Passord ved registrering → `new-password`, ved innlogging og sletting av konto → `current-password`. «Vis passord» får `aria-pressed` eller bytter tekst til «Skjul passord». Påkrevde felt får `required`. Valgfrie felt er allerede merket «(valgfritt)», og det er bra.

**H4. [høy] Steg 2 i nytt oppdrag («Når?», «Hva tilbyr du?», forhåndsvisning) er verken spesifisert eller vist** (2.1.1, 1.3.1, 3.3.2, NFR-7 «også dato og klokkeslett»; EXPERIENCE.md § Accessibility Floor, NOTE FOR ARCHITECTURE; Åpne punkter «Ikke vist i mockupene»)
NFR-7 nevner dato og klokkeslett særskilt, og dette er den risikable delen av kjerneflyten (UJ-1 steg 4). Likevel er valget mellom native felt og tekstfelt utsatt, og flere ting mangler. «Når?» er ikke en gruppe med `fieldset`/`legend` (bare radio og stjerner er nevnt). Radiogruppen «Beløp / Uten betaling» og beløpsfeltet som vises når «Beløp» velges, mangler regler for plassering, etikett («Beløp i kr»), `inputmode` og feiltekst. Native `type="date"` viser formatet etter nettleserens språk, ikke `lang="nb"` (mm/dd/åååå hos en engelsk Chrome), og det kan forvirre Kari.

*Fix:* Skriv komponentregler for «Når?» (`fieldset`, `legend` «Når?», etikettene «Dato» og «Klokkeslett», synlig format, feiltekster) og for «Hva tilbyr du?» (radiogruppe, beløpsfeltet rett etter «Beløp» i DOM, det nye feltet flytter ikke fokus). Ta en beslutning i arkitekturen før stories, og legg til en mockup av steg 2. Forhåndsvisningen er en region med etikett, uten lenke, og får ikke en overskrift som kan forveksles med sidens.

### Medium

**M1. [medium] Den faste bunnmenyen kan dekke fokus ved skjermtastatur, liggende skjerm og zoom** (2.4.7, 1.4.10, 1.4.4; DESIGN.md § Layout «padding-bottom», EXPERIENCE.md `bottom-nav` «Alltid synlig, også når skjermtastaturet er oppe [ASSUMPTION]»)
`padding-bottom` hindrer bare at innholdet er dekket nederst på siden. Den hindrer ikke at et felt med fokus havner bak menyen når brukeren ruller eller tabber. Ved 400 % zoom (320 × 256 CSS px) tar 56 px meny pluss safe-area over 20 % av høyden. Mobilnettlesere legger dessuten faste elementer bak tastaturet, så antakelsen er verken realistisk eller ønsket.

*Fix:* `scroll-padding-bottom` lik menyhøyden på `html`. Menyen blir `position: static` (nederst i flyten) ved `@media (max-height: 30em)` og når den vises i stor tekst. Fjern antakelsen om at menyen alltid er synlig over tastaturet. Test i liggende format og ved 400 %.

**M2. [medium] Bunnmenyen har fast høyde og `white-space: nowrap`, og det gir overflyt ved stor tekst** (1.4.4, 1.4.12, 1.4.10; DESIGN.md `bottom-nav` `itemHeight: 56px`; mockup-CSS `.bottomnav a{height:56px; white-space:nowrap}`)
Målt i headless Chrome: ved 200 % rot-skriftstørrelse er menylista 478 px bred på en skjerm som er 360 px. «Mine oppdrag» trenger 245 px, og teksten klippes eller gir vannrett rulling. Ikon, tekst og mellomrom trenger cirka 69 px høyde mot 56 px. Ved 320 px blir kolonnene ulike (98/124/98 px), og med tekstavstand (1.4.12) 90/153/76 px. Altså er de ikke «like brede».

*Fix:* `min-height: 56px` i stedet for `height`, tillat linjebryting (`white-space: normal`, `overflow-wrap: break-word`), og bruk `grid-template-columns: repeat(3, minmax(0, 1fr))`. Skriv i DESIGN.md at 56 px er en minstehøyde.

**M3. [medium] `action-tag` med `maxLines: 2` kan bli implementert som avkorting** (1.4.4, 1.4.10; DESIGN.md frontmatter `action-tag maxLines: 2`, § Components «høyst to linjer»)
Målt: ved 200 % tekst brytes «Oppdraget er endret etter at du meldte interesse» over 4–5 linjer (174–200 px høyt) og «Gi tilbakemelding» over 3 linjer. «Høyst to linjer» stemmer bare ved 100 %. En utvikler som leser `maxLines` som `line-clamp`, skjuler innhold.

*Fix:* Erstatt med «normalt to linjer på 360 px ved 100 %. Aldri `line-clamp`, ellipse eller `overflow: hidden`, og teksten brytes så mange linjer som trengs.»

**M4. [medium] Reflow ved 320 px står i DESIGN, men verken i NFR-6 eller testplanen** (1.4.10; DESIGN.md § Layout «flyte om ved 320 px», PRD NFR-6 «fra 360 px», EXPERIENCE.md «Testes ved» punkt 4)
1.4.10 krever innhold uten vannrett rulling ved 320 CSS px, som tilsvarer 400 % zoom på 1280 px. NFR-6 og test 4 sjekker bare 360, 768 og 1280 px og 200 % zoom. Mockupene flyter riktig om ved 320 px (målt, unntatt M2), men ingen test sikrer det i koden.

*Fix:* Legg til «320 px / 400 % zoom på 1280 px» i test 4. Foreslå for PRD-en (bmad-prd) at NFR-6 eller NFR-7 får «Innhold flyter om ved 320 CSS px (WCAG 1.4.10)», så kravet kan spores.

**M5. [medium] Dialogen mangler regler for liten høyde og stor tekst** (1.4.10, 2.1.1; DESIGN.md `dialog`, EXPERIENCE.md `dialog`)
Ved 400 % zoom eller i liggende format med stor tekst kan dialogen med knapper under hverandre bli høyere enn skjermen. Uten rulling inne i dialogen kan ikke knappene nås.

*Fix:* `max-height: calc(100dvh - 32px); overflow-y: auto` på dialogen, og bruk native `<dialog>` med `showModal()` (det gir `inert` bakgrunn og Esc gratis). Skriv det inn i DESIGN.md og i NOTE FOR ARCHITECTURE.

**M6. [medium] «Avbryt» som angre-valg og dialoger som ikke sier hvilket oppdrag det gjelder (kognitivt, Kari 72)** (3.2.4, 3.3.4 som god praksis, NFR-8; EXPERIENCE.md § Interaction Primitives, Bekreftelser)
Spinen har løst problemet med to «Avbryt» for «Avbryte oppdrag» ved å bruke «Behold oppdraget». Men «Fjerne Amir …», «Trekke deg …» og «Marker som utført …» bruker fortsatt «Avbryt» som angre-valg, i en app der «Avbryt oppdrag» er en ugjenkallelig handling. «Avbryt oppdrag» i en rad i Mine oppdrag åpner dessuten «Avbryte oppdraget?» uten tittel. Kari kan ikke se hvilket oppdrag hun avbryter.

*Fix:* Bruk angre-tekster med verb: «Nei, behold Amir», «Nei, jeg blir», «Ikke ennå». Ta med oppdragstittelen i dialogen: «Avbryte «Henge opp gardiner»? Det kan ikke angres.»

**M7. [medium] Status, situasjon og merke skilles bare visuelt, og radlenken mangler beskrivelse** (1.3.1, 2.4.4 god praksis; EXPERIENCE.md `list-row`, `situation-label`, `action-tag`; key-mine-oppdrag.html)
I mockupen leser skjermleseren «Åpen Venter på svar Oppdraget er endret etter at du meldte interesse» som tre løse tekstbiter. Forskjellen mellom oppdragets status, brukerens situasjon og et merke som krever handling vises bare med form og farge. Når brukeren tabber, hører hen bare tittelen på radlenken, uten merket «Gi tilbakemelding».

*Fix:* Skjult tekst foran: «Status: Åpen.», «Din situasjon: Venter på svar.», «Må gjøres: Gi tilbakemelding.» Gi radlenken `aria-describedby` som peker til merkelinja. Skriv begge deler inn i `list-row`.

**M8. [medium] Feilmeldingene er ikke komplette** (3.3.1, 3.3.3; EXPERIENCE.md § Voice and Tone «Tekster som mangler», mønster «Skriv …» / «Velg …»; sensorveiledningen kriterium 4 «feilmeldinger»)
Disse mangler: tittel tom eller over 80 tegn, beskrivelse under 10 eller over 1000 tegn, ingen kategori valgt, ugyldig datoformat, ugyldig klokkeslett, ugyldig beløp, ugyldig telefonnummer, passordregler, fødselsdato i ugyldig format og ugyldig e-postadresse. Påkrevde felt er ikke merket med `required`/`aria-required`.

*Fix:* En fullstendig tabell (felt → regel → feiltekst med forslag til retting, f.eks. «Skriv datoen som dd.mm.åååå, for eksempel 14.11.2026.») og regelen «påkrevde felt har `required`, valgfrie står med «(valgfritt)»».

**M9. [medium] Snarveien «Hopp til innholdet» og sidetitlene er bare antakelser, og mockupene mangler snarveien** (2.4.1, 2.4.2; EXPERIENCE.md § Accessibility Floor)
Fra 768 px kommer logoen og tre menyvalg før `main`. Landemerkene oppfyller 2.4.1 formelt, men NFR-7 og sensor ser etter tastaturnavigasjon. Ingen av de fem mockupene har snarveien. For `<title>` finnes bare ett eksempel.

*Fix:* Gjør snarveien bindende (første fokuserbare element, synlig ved fokus, mål `main` med `tabindex="-1"`). Legg til en tabell med `<title>` per side og tilstand, for eksempel «Nytt oppdrag, steg 1 av 2 – Nabolagshelten», «Feil: Registrering – Nabolagshelten» og «Amir – profil – Nabolagshelten».

**M10. [medium] Testplanen knytter ikke hvert NFR-7-punkt til en test, og flere tilstander mangler** (NFR-7, SM-5; EXPERIENCE.md «Testes ved»)
Se Testdekning. Kort sagt: testene er ikke knyttet til NFR-7-punktene. axe-lista mangler steg 2 og nettbrettskjemaet, KI-forslag og KI-feil, tilbakemelding med stjerner, tomtilstander, feilside, slettet bruker og detaljer for hjelperen. Skjermlesertesten dekker bare UJ-1, så kunngjøringen fra filteret (UJ-2) testes ikke.

*Fix:* Legg til en kolonne «Testes ved» i tabellen i § Accessibility Floor, og utvid lista over sider og tilstander (forslag under Testdekning).

### Lav

**L1. [lav] Fokusringen på kort og rader avhenger av `:has()` uten reserveløsning** (2.4.7; mockup-CSS `.card-link:focus-visible{outline:none}` + `.link-card:has(...)`)
Støtter ikke nettleseren `:has()`, får hele kortet ingen fokusindikator. Ringen er dessuten bare 1,67:1 mot `primary` hvis offset settes til 0.
*Fix:* Skriv i DESIGN.md: «fokusringen tegnes på lenkens `::after` (som dekker kortet), `outline-offset` ≥ 2 px, aldri `outline: none` uten erstatning i samme regel.»

**L2. [lav] Like knappenavn i samme visning** (2.4.6, 2.4.4; key-nytt-oppdrag.html «Bruk»/«Forkast» × 3, key-detaljer.html «Se profil» × 3, key-mine-oppdrag.html «Endre tidspunkt»/«Avbryt oppdrag» per rad)
Mockupen gir «Se profil» `aria-describedby` til navnet, og det er bra, men spinen krever det ikke.
*Fix:* Skriv i spinen at «Bruk», «Forkast», «Se profil» og snarveiene i rader får `aria-describedby` til tittelen på forslaget, navnet eller oppdraget. Behold den synlige teksten først (2.5.3).

**L3. [lav] Merket «Velg hjelper» står over overskriften «3 har meldt interesse»** (1.3.2; EXPERIENCE.md detaljer-tabellen, key-detaljer.html)
Den som navigerer med overskrifter, lander på `h2` og går glipp av merket.
*Fix:* Plasser merket rett etter overskriften i DOM-en (visuelt kan det stå over), eller ta det med i overskriften.

**L4. [lav] Stjernene ved tilbakemelding: synlige ytterpunkter, `legend` og tilstand** (2.5.3, 1.3.1, 2.4.7; EXPERIENCE.md `star-rating` input)
«Dårlig» og «Veldig bra» står synlig ved stjerne 1 og 5, men er ikke med i navnene («1 av 5 stjerner»). `legend` «Vurdering» er ikke synlig, og spørsmålet «Hvordan gikk det med Amir?» er den synlige etiketten. Det står ikke hvordan fokus og valgt tilstand tegnes når radioknappen er visuelt skjult, eller om stjerne 1 til n fylles.
*Fix:* Navn «1 av 5 stjerner, dårlig» og «5 av 5 stjerner, veldig bra». `legend` = det synlige spørsmålet. `label:has(:focus-visible)` tegner ringen og `:has(:checked)` fyller stjernene til og med valgt verdi. Det samme gjelder kategori-radioene i skjemaet, som i mockupen bare har CSS for `aria-pressed`/`.selected` og ikke for `:checked`.

**L5. [lav] Små lenker i tekst bryter med «også lenker har 48 px trykkflate»** (NFR-7; key-profil.html «Fra Kari», telefonlenken i `phone-box`)
Giver-navnet «Kari» er cirka 38 px bredt. NFR-7 sier bare høyde, og 2.5.5 er AAA, men spinen lover mer.
*Fix:* Presiser: «Lenker inne i løpende tekst er unntatt; frittstående lenker er minst 48 × 48 px.» Gi telefonlenken minst 48 px høyde.

**L6. [lav] Kategoriknappene i skjemaet bryter ord midt i ordet ved tekstavstand** (1.4.12; DESIGN.md `category-button` «aldri midt i et ord», mockup-CSS `overflow-wrap:anywhere`)
Målt: med tekstavstand etter 1.4.12 brytes «Teknologihjelp» over to linjer ved 360 og 320 px.
*Fix:* `hyphens: auto` (virker med `lang="nb"`) i stedet for `anywhere`, eller én kolonne under cirka 22em.

**L7. [lav] Tvungne farger, redusert bevegelse og skjermretning er ikke nevnt** (1.3.4, 1.4.11; EXPERIENCE.md § Accessibility Floor)
I Windows høykontrast forsvinner `box-shadow`-delen av fokus og hover og flata på `action-tag`. Teksten og omrisset består, så det er trolig i orden, men det er ikke testet.
*Fix:* Én linje hver: «Låser ikke skjermretning», «`prefers-reduced-motion`: ingen myk rulling ved fokusflytting» og «Sjekkes i `forced-colors: active`».

**L8. [lav] «Tilbake» betyr to ting i nytt oppdrag, og fokus ved tilbake til steg 1 er ikke spesifisert** (3.2.4, 2.4.3; EXPERIENCE.md § Interaction Primitives «To steg»)
*Fix:* På steg 2 heter knappen «Tilbake til steg 1». Fokus går til `h1` «Nytt oppdrag 1 av 2». `<title>` byttes per steg.

**L9. [lav] Antall treff og tallet i menyen er ikke forklart for den som ser** (kognitivt; key-oversikt.html, `nav-badge`)
Antallet «4 ledige oppdrag» finnes bare som skjult tekst. «2» ved «Mine oppdrag» står uten forklaring for Kari.
*Fix:* Vis antallet synlig under overskriften. Vurder en kort linje øverst i Mine oppdrag: «2 oppdrag trenger at du gjør noe.»

**L10. [lav] Ord og forkortelser som kan være uklare for Kari** (NFR-8, kognitivt)
«Forkast», forkortede måneder («14. nov.»; skjermlesere kan lese «nov punktum») og «Meldt før endring».
*Fix:* Vurder «Ikke bruk» for «Forkast» og måneder skrevet fullt på detaljer og profil. Ta det med i SM-4-testen.

**L11. [lav] Angre-kolonnen heter «(lenke)», og `aria-disabled` stopper ikke innsending med Enter** (4.1.2; EXPERIENCE.md Bekreftelser, `button-disabled`)
*Fix:* «Angre-valget er en `<button>` med utseende som tekstknapp, ikke `<a>`.» Skjemaet stopper innsending mens forespørselen pågår (ikke bare knappen).

**L12. [lav] To `aria-current="page"` på Mine oppdrag** (4.1.2; key-mine-oppdrag.html: menyvalget og fanen)
*Fix:* Fanen får `aria-current="page"`, og menyvalget `aria-current="true"` når en fane er aktiv. Alternativt: skriv i spinen at begge er tillatt.

**L13. [lav] Når innloggingen utløper, kan utfylt skjema gå tapt** (2.2.1 og 2.2.5 som god praksis; EXPERIENCE.md «Innlogging utløpt»)
7 dager er godt over unntaket på 20 timer i 2.2.1, og sperren på 15 minutter er en sikkerhetsgrense med tydelig melding. Begge er i orden. Men hvis innloggingen utløper ved «Publiser», sier spinen ikke at innholdet beholdes.
*Fix:* «Utfylt innhold beholdes ved ny innlogging, eller brukeren får beskjed før det går tapt.»

## Det som er bra

- **Kontrast:** Alle 50+ par med krav består, og alle tallene i DESIGN.md stemmer. Ingen hvit eller svart. Mørkere nyanser er dokumentert med begrunnelse.
- **Farge aldri alene (1.4.1):** Status har ord, ikon, kant og farge. Valgt kategori har kant, hake og fet skrift. Aktiv fane og meny har strek, fet skrift og `aria-current`. Lenker er understreket. Regelen om fet skrift som «valgt» kommer alltid sammen med et tegn som ikke er skrift.
- **Ingen nestede interaktive elementer:** Det står i spinen («Knapper står aldri inne i lenken») og er bekreftet maskinelt i alle fem mockupene. Det samme gjelder unike id-er og overskrifter uten hull i nivåene (`h1` → `h2` → `h3`).
- **Ikoner:** Alle 70+ SVG-er har `aria-hidden="true" focusable="false"` og står alltid sammen med tekst. Stjernene i snittet er dekorative, og teksten bærer verdien. Logoen har navnet «Nabolagshelten, til oversikten», som begynner med den synlige teksten (2.5.3).
- **Skjema:** Synlig etikett over hvert felt, ingen plassholdertekst som etikett, hjelpetekst og feil koblet med `aria-describedby`, `aria-invalid`, «(valgfritt)» på valgfrie felt, `fieldset`/`legend` for kategori. Alt utfylt beholdes ved feil.
- **Dialoger:** Fokus til spørsmålet, Tab holdes inne, Esc angrer, fokus tilbake til knappen som åpnet dialogen, og reserveplan når knappen forsvinner. Bekreftelse for alle ugjenkallelige handlinger (NFR-8). «Behold oppdraget» i stedet for et nytt «Avbryt». Forhåndsvisning før «Publiser» (3.3.4).
- **KI:** Fast rekkefølge (felt → knapp → personverntekst → forslag), `aria-live` for «Lager forslag …» og «Forslagene er klare.», `role="alert"` ved feil, fokus blir på knappen, «Bruk»/«Forkast» flytter fokus til feltet. Aldri automatisk.
- **`aria-disabled`** i stedet for `disabled`, så knappen beholder fokus og blir lest opp, med en synlig forklaring på hvorfor.
- **Fanene er lenker med egen adresse og `aria-current`**, ikke en falsk `tablist`. Tilbake-knappen i nettleseren virker.
- **Ingen skjulte funksjoner:** ingen sveip, ingen innhold bare ved hover (1.4.13 er ikke relevant), ingen meldinger som forsvinner av seg selv, ingen karuseller. Fast menyrekkefølge på alle sider (3.2.3).
- **Antallet i menyen** har et fullt navn for skjermleser («Mine oppdrag, 2 trenger handling»). Det synlige tallet er `aria-hidden`.
- **Tekst og trykkflater:** brødtekst 18 px i `rem`, trykkflater 48 px, `lang="nb"`, én `h1` og landemerker.
- **Reflow:** Mockupene har ingen vannrett overflyt ved 320 px, heller ikke med tekstavstand etter 1.4.12 (målt), bortsett fra bunnmenyen ved 200 % tekst (M2).
- **Tomtilstander:** forklaring og én vei videre. «Velg et annet postnummer» flytter fokus og markerer innholdet.

## Testdekning (NFR-7/SM-5)

EXPERIENCE.md § Accessibility Floor har fem testtyper (axe, tastatur, skjermleser, bredder og zoom, SM-4). Det samsvarer med «Testes ved» i NFR-7 og med SM-5, og slett konto-siden er lagt til. Det mangler en kobling fra hvert NFR-7-punkt til en test, og noen punkter dekkes bare av axe, som ikke finner dem.

| NFR-7-punkt | Dekkes av i spinen | Hull | Forslag |
|---|---|---|---|
| Kontrast ≥ 4,5:1 | axe (bare tekst som rendres) | Kanter, fokus og tilstander (1.4.11) sjekkes ikke av axe | T6: automatisk test som regner ut tokenparene fra DESIGN.md, eller manuell kontroll med fargevelger, dokumentert |
| Tastatur og synlig fokus, også dato og klokkeslett | Tastaturgjennomgang UJ-1 og UJ-2 | Registrering, innlogging, rediger profil og slett konto er ikke med. Steg 2 er ikke mocket (H4) | Ta med støtteflytene i tastaturtesten |
| Synlige etiketter og feil ved feltet | axe + «skjema med valideringsfeil» | Fokus og kunngjøring etter innsending (H1) testes ikke | Skjermlesertest av ett skjema med feil |
| Knapper med tekst og alt-tekst | axe | – | OK |
| 18 px / 48 px | Ingen eksplisitt test | Ikke målt | Sjekkliste i tastaturtesten eller måling i DevTools |
| 200 % zoom | Test 4 | 320 px / 400 % (1.4.10), tekstavstand (1.4.12) og stor tekst i OS-et mangler (M2–M4) | Legg til 320 px, tekstavstand (bokmerke) og 200 % tekststørrelse |
| Status med ord | Visuell gjennomgang (implisitt) | – | Ta med en kontroll i gråtoner eller tvungne farger (L7) |
| Statusmeldinger leses opp | Skjermleser UJ-1 | Filterkunngjøringen (UJ-2 steg 3) og kvitteringer etter sidelasting er ikke med | Skjermleser også for UJ-2 steg 3–6 |
| Dialoger flytter fokus | Tastatur + axe på fem dialoger | – | OK. Legg til «fokus tilbake» som eget kontrollpunkt |
| `lang="nb"` | axe | – | OK |
| Tomtilstander | Ikke i axe-lista | Tom oversikt (begge varianter), tom fane, ingen interesserte | Ta med i axe og den visuelle gjennomgangen |

**Sider og tilstander SM-5 bør dekke i tillegg** (axe kjøres på hver tilstand, ikke bare hver side): nytt oppdrag steg 2 og nettbrettvisningen på én skjerm. KI-forslag synlige, KI venter og KI-feil. Detaljer som hjelper (meld interesse og telefonboks). Tilbakemeldingsskjema med stjerner (FR-20). Mine oppdrag med begge faner. Tom oversikt. Feilside og slettet bruker. Dette er ikke krav i SM-5, men det er her mange av de nye komponentene ligger, og det gjør det lettere for sensor å se at kriterium 4 er testet.

**SM-4** (brukertest med en person over 60) er godt beskrevet. Ta med ordene i L10 og spørsmålet om én eller to steg på nettbrett (Åpne punkter) som observasjonspunkter.
