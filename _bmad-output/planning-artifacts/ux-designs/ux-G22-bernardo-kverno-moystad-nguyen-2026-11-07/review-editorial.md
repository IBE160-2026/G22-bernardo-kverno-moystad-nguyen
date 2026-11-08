# Redaksjonell gjennomgang (structure og prose) – Nabolagshelten UX

- **Kjørt:** 2026-11-07, `bmad-review lenses=structure,prose` (doc_standards-steget i `bmad-ux` Finalize)
- **Innhold:** [DESIGN.md](DESIGN.md) (4 646 ord, 3 677 i brødtekst) og [EXPERIENCE.md](EXPERIENCE.md) (10 764 ord)
- **Stil:** Microsoft Writing Style Guide, tilpasset norsk bokmål. Lesere: utviklerne i gruppen og sensor.

Structure-linsen kjørte først. Prose-linsen kjørte etter den og hoppet over tekst som structure foreslår å kutte eller flytte. Ingen rangering; overlapp mellom linsene er markert.

## Selvmotsigelser (rettes uansett)

1. **Fokusregelen** (EXPERIENCE.md § State Patterns, raden «Fokus»): «flyttes bare ved …» utelater «Bruk»/«Ikke bruk», «Endre tidspunkt», lenker i feiloppsummeringen, «Vis alle kategorier» og «Hopp til innholdet».
2. **`role="alert"`** (EXPERIENCE.md § Accessibility Floor, raden «Statusmeldinger leses opp»): sier at feil uten sidelasting får `role="alert"`, men feiloppsummeringen skal ikke ha det (Component Patterns).

## DESIGN.md – structure (18)

| # | Hvor | Forslag |
|---|---|---|
| S1 | § Components, hele lista (1 737 ord, ca. 30 punkter) | Del i H3-grupper i frontmatter-rekkefølge: Knapper · Fokus · Flater · Merker · Skjema · Meldinger · Navigasjon · resten |
| S2 | Fokus (7. punkt) | Flytt først i Components – gjelder alle interaktive elementer |
| S3 | list-row (sist) | Flytt rett etter card |
| S4 | Sammensatte mønstre (Hopp til innholdet, Knapper nederst i skjema, Feiloppsummering, Antallslinje, Forhåndsvisning) | Plasser under sin token-komponent, eller samle i «Sammensatte mønstre» |
| S5 | star-rating visning, nav-badge, Hopp til innholdet | Kutt atferd som allerede står i EXPERIENCE.md |
| S6 | star-rating: avrunding av snitt | Flytt til EXPERIENCE.md (visningslogikk) |
| S7 | button-primary/-secondary/-text: lister med knappetekster | Kort ned til rolle + 2–3 eksempler (avveining: lista er en sjekkliste) |
| S8 | «Knapper under hverandre» i Knapper nederst i skjema og i dialog | Slå sammen til ett sted |
| S9 | Kontrasttabellen: like par (link/success, ink/focus, border/chip-border) | Én rad per fargepar med alle tokens i venstre celle |
| S10 | Typography «Fet skrift i valg» | Kort ned til kravet om et tegn som ikke er skrift + unntaket for etiketter |
| S11 | Typography «Regler:» | Flytt før tabellen; kutt FR-18-setningen (står i action-tag) |
| S12 | input: «Når?» og «Hva tilbyr du?» | Flytt til eget punkt «Skjema, steg 2» |
| S13 | Layout: setningen om kategoriknapper | Flytt til category-button |
| S14 | Layout: bunnmenyen fast/statisk | Vurder å flytte fast/statisk-regelen til bottom-nav |
| S15 | Elevation: rgba-verdier | Vis til tokens i frontmatter |
| S16 | Fokus: `:focus`-setningen | Kort ned; når fokus flyttes er atferd (EXPERIENCE.md) |
| S17 | Do's and Don'ts | Behold |
| S18 | Palett-tabellens kolonne «Roller (token)» | Behold |

Anslag: ca. −255 ord (7 % av brødteksten). Største gevinst er oppslag, ikke ordtall.

## DESIGN.md – prose (17)

| # | Original | Forslag |
|---|---|---|
| P1 | «krav: tekst ≥ 4,5:1, kanter, fokusring og merkekanter ≥ 3:1» | Semikolon etter 4,5:1 |
| P2 | `label`/`option` brukt både som typografitoken og HTML-element | `{typography.label}` for token, `<label>` for elementet |
| P3 | «merker som krever handling», «Merke for noe brukeren må gjøre», «trenger handling» | Ett begrep, f.eks. «handlingsmerke (`action-tag`)» |
| P4 | «Feil for tidspunktet samlet står under begge feltene.» | «En feil som gjelder hele tidspunktet, står én gang under begge feltene.» |
| P5 | ki-suggestion-box «under «Bruk» … beskrivelsesboksen» | «og under den knappene …», «forslagsboksen for beskrivelsen» |
| P6 | list-row «16 px / 24 px polstring» | «16 px over og under og 24 px på sidene» |
| P7 | Fokus «(som dekker kortet) … så den virker uten `:has()`» | Kutt parentesen; «så ringen også virker i nettlesere uten `:has()`» |
| P8 | action-tag «ved 100 % … ved 200 % tekst» | «100 % tekststørrelse … 200 % tekststørrelse» |
| P9 | «`scroll-padding-bottom` lik menyhøyden på `html`» | «`scroll-padding-bottom` på `html` lik menyhøyden» |
| P10 | category-button: 48 px nevnt to ganger; «ikon over eller foran» | Én gang; vurder å si når ikonet står over og når foran |
| P11 | card/list-row «ved hover og fokus … i tillegg til fokusringen» | Hover: kant. Fokus: kant og ring. |
| P12 | «satt i dette steget» | «satt i UX-arbeidet» |
| P13 | «strukturen fra D2», «Key-screen-mockups» | «variant D2», «Mockups av nøkkelskjermene» |
| P14 | «i fargekartet» | «i tabellen under» |
| P15 | «Terrakotta er bare feil …» | «Terrakotta brukes bare til feil …» |
| P16 | «Dybde kommer først fra tone» | «først og fremst» |
| P17 | «`color-scheme: light` settes» | «Appen setter `color-scheme: light` og følger ikke `prefers-color-scheme`.» |

## EXPERIENCE.md – structure (21)

| # | Hvor | Forslag |
|---|---|---|
| E1 | Fokusregler på sju–ti steder | Slå sammen til én tabell «Fokus og opplesning» i Interaction Primitives (Utløser → Fokus går til → Opplesning); andre steder viser dit. Løser selvmotsigelse 1 |
| E2 | `role="alert"`/`aria-live` på fire steder | Inn i samme tabell. Løser selvmotsigelse 2 |
| E3 | Deaktivering under innsending fire steder | Ett sted (`button-disabled` eller «Sending.») |
| E4 | Feiloppsummeringen på seks steder, to steg tre ganger | Atferden bare i Component Patterns |
| E5 | Tom oversikt / «Velg et annet postnummer» fem steder | Tekst i Voice and Tone, atferd i `empty-state` |
| E6 | Antallslinja: atferd i Voice and Tone | Flytt atferden til `category-button` |
| E7 | Voice and Tone-raden «Postnummerfilter» | Kutt (UI-valg, står andre steder) |
| E8 | `required`/`novalidate`/«(valgfritt)» og passordatferd i «Feiltekster ved felt» | Flytt til `input`/`field-error` |
| E9 | Component Patterns-celler på 80–150 ord | Kort ned til 1–2 setninger; lange regler i H3-er «Filtrene i oversikten», «Skjemafelt», «Meldinger» |
| E10 | «Velg hjelper» under overskriften fire steder | Bare i `action-tag` |
| E11 | Knapper under lenkedelen i rader to steder | Bare i `list-row` |
| E12 | «Ikke tillatt»/skjulte funksjoner fem steder | Samle i Interaction Primitives «Ikke tillatt» |
| E13 | «Skisse og PRD sier ulikt» overlapper «Endringer fra skissene» | Én endringslogg |
| E14 | Endringer #4 gjengir hele KI-eksemplet | Kort ned, vis til UJ-1 steg 3 |
| E15 | «Sporing: krav → flate» under Key Flows | Egen H2, så sensor finner den |
| E16 | Mockup-dekning i Foundation og i Åpne punkter | Én liste i Foundation |
| E17 | Kildeprioritet sagt tre ganger | Bare i innledningen |
| E18 | To steg beskrevet fire steder | Responsive viser til Interaction Primitives |
| E19 | Nav-badge og «trenger handling» | IA er kilden, de andre viser dit |
| E20 | Accessibility Floor-tabellens «Se …»-mønster | Behold – modell for resten |
| E21 | T1–T6 og sidetittel-tabellen | Behold |

Anslag: ca. −1 100 til −1 250 ord (10–12 %).

## EXPERIENCE.md – prose (31 + 6 små)

| # | Original | Forslag |
|---|---|---|
| Q1 | «spinene» uforklart | Forklar første gang: «spinene (denne fila og DESIGN.md)» |
| Q2 | «Krav-ID-ene … gjentas ikke her» | «Kravene … gjentas ikke her. Denne fila viser til ID-ene …» |
| Q3 | «sidelasting», «ny side», «sidebytte», «sidevisning» | Ett begrep: «sidelasting»; tilstanden heter «Laster» |
| Q4 | «merke» om både statusmerke og handlingsmerke | «Statusmerke» for `status-badge`, «merke» bare for `action-tag` |
| Q5 | «(tom tilstand)» | «(tomtilstanden)» |
| Q6 | «(2.5.3)», «(1.3.5)», «2.4.2», «(1.4.11)» | «WCAG …» foran |
| Q7 | «Ett per felt», «Nytt «Få forslag»» | «Én per felt», «Et nytt trykk på «Få forslag»» |
| Q8 | «beholder fokus og kan leses opp» | «fortsatt kan få fokus og leses opp» |
| Q9 | «dekker hele raden over eventuelle knapper» | «dekker hele raden unntatt knappene under» |
| Q10 | «teksten står fast» (Vis passord) | «knappeteksten endres ikke» |
| Q11 | category-button skjema: parentes om filteret | Skill skjema (`:checked`) og filter (`aria-current`) tydelig |
| Q12 | «Når?»: dato- og klokkeslettregler blandet | Del i to setninger |
| Q13 | «(først «lagt ut» hvis begge har)» | Fullt fanenavn |
| Q14 | `aria-current="page"` i IA mot `"true"` på Mine oppdrag | Kryssreferanse til `tabs` |
| Q15 | «Tilbake» … «ellers til oversikten» | «… hvis brukeren ikke kom fra en side i appen» |
| Q16 | «visuell tekst» | «den synlige teksten» |
| Q17 | «Nettleseren kan da fylle inn» | «Med riktig felttype og `autocomplete` kan …» |
| Q18 | «åpner `{components.dialog}`; ingen andre:» | Punktum, ikke kolon |
| Q19 | «leses opp.», «`aria-live` leser det opp» | Subjekt: «teksten leses opp», «skjermleseren leser det opp» |
| Q20 | «når den blir smal» | «når vinduet blir smalt» |
| Q21 | «Knappen byttes med» | «byttes ut med» |
| Q22 | «hun kan «Rediger» tidspunkt» | «hun kan endre tidspunkt … med «Rediger»» |
| Q23 | «Raden har merket» (UJ-2 steg 9) | «Raden i Mine oppdrag har merket» |
| Q24 | «flater SM-5 tester» | «flater som testes i SM-5» |
| Q25 | «Punktene i PRD §8 og avstemming …» | «Lista dekker punktene i PRD §8 og …» |
| Q26 | «(se under)» | Navngi seksjonen |
| Q27 | Tidsformat «og ellers» | Si når hvert format gjelder |
| Q28 | «Personverntekst over knappen» | Navngi knappen («Opprett konto», fra mockupen) |
| Q29 | Kolonnen «Detaljer» i FR-18-tabellen | Vurder «Hva brukeren kan gjøre» (la stå hvis ordrett fra PRD) |
| Q30 | «manuelle tester» mot «T1 Automatisk» | Presiser |
| Q31 | «med linsen universell utforming» | «av universell utforming» |
| Q32–37 | Små: «ved 100 %» → «100 % zoom»; feltnavn i Responsive; subjekt i UJ-1; «fokus blir på knappen» → «på kategorien» (UJ-2); «siden Slett konto»; kolon etter [ASSUMPTION] i IA | |

## JSON

```json
[
  {"lens":"structure","location":"EXPERIENCE.md § State Patterns «Fokus» / § Interaction Primitives «Fokus.»","trigger_condition":"Fokusregler på 7–10 steder; «bare ved …» utelater flere tilfeller","guard_snippet":"Én tabell «Fokus og opplesning» i Interaction Primitives; andre steder viser dit","potential_consequence":"Utviklere og T2 tester mot ulike regler"},
  {"lens":"structure","location":"EXPERIENCE.md § Accessibility Floor «Statusmeldinger leses opp»","trigger_condition":"Sier role=alert for feil uten sidelasting; feiloppsummering skal ikke ha det","guard_snippet":"Én rad per tilfelle i fokustabellen","potential_consequence":"Dobbel opplesning eller feil implementasjon"},
  {"lens":"structure","location":"DESIGN.md § Components","trigger_condition":"30 punkter i én flat liste, annen rekkefølge enn frontmatter","guard_snippet":"H3-grupper i frontmatter-rekkefølge; Fokus først; list-row etter card","potential_consequence":"Vanskelig oppslag"},
  {"lens":"structure","location":"EXPERIENCE.md § Component Patterns","trigger_condition":"Tabellceller på 80–150 ord","guard_snippet":"1–2 setninger per celle; lange regler i H3-er","potential_consequence":"Vanskelig å skanne og diffe"},
  {"lens":"prose","location":"DESIGN.md § Colors, kontrastkrav","trigger_condition":"Komma gjør det uklart hvilke elementer som krever 4,5:1 og 3:1","guard_snippet":"Semikolon etter 4,5:1","potential_consequence":"Feil kontrastkrav brukes"},
  {"lens":"prose","location":"EXPERIENCE.md, hele dokumentet","trigger_condition":"Fem uttrykk for sidelasting; «merke» om to komponenter","guard_snippet":"«sidelasting» og «statusmerke»/«merke» konsekvent","potential_consequence":"Regler leses som ulike"}
]
```

JSON-lista har bare de bærende funnene. Alle funnene står i tabellene over.
