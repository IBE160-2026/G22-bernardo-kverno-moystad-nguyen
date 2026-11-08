---
title: DESIGN – Nabolagshelten
status: final
created: 2026-11-07
updated: 2026-11-08
name: Nabolagshelten
description: Responsiv webapp for småjobber i nabolaget. Ett lyst fargetema «Salvie og sand», ingen mørk modus. Bygget for Kari (72) og Amir (21).
sources:
  - ../../prds/prd-G22-bernardo-kverno-moystad-nguyen-2026-11-05/prd.md
  - ../../product-brief-nabolagshelten.md
  - ../../skisser-skjermbilder.md
  - ../../../../tilbakemelding-product-brief.md
  - ../../../../docs/sensorveiledning-del1.md
colors:
  # Flater og tekst
  surface-page: '#E3D3B3'        # sand
  surface-card: '#EEE5D3'        # beige
  surface-input: '#F4E8CF'       # champagne
  ink: '#2F302D'                 # antrasitt
  ink-muted: '#6E4E3A'           # mokka
  border: '#7B6C5D'              # taupe, mørkere (nyanse)
  focus: '#2F302D'               # antrasitt
  scrim: '#2F302D'               # antrasitt, brukes med 55 % opasitet bak dialog
  # Handling
  primary: '#47553F'             # salviegrønn, mørk (nyanse)
  on-primary: '#F4E8CF'          # champagne
  link: '#47553F'                # salviegrønn, mørk – sekundærknapp og lenke
  disabled-bg: '#D2CABD'         # greige
  disabled-fg: '#5E5347'         # taupe, mørk (nyanse)
  # Topplinje og meny
  topbar: '#47553F'              # salviegrønn, mørk
  topbar-text: '#F4E8CF'         # champagne
  topbar-focus: '#EBC7BC'        # blush
  brand-icon: '#EBC7BC'          # blush
  nav-indicator: '#EBC7BC'       # blush
  # Merke «Trenger handling» (antall i menyen og merker i lister)
  badge-bg: '#EBC7BC'            # blush
  badge-fg: '#4B3324'            # mørkebrun
  # Kategori
  chip-bg: '#EEE5D3'             # beige
  chip-fg: '#4B3324'             # mørkebrun
  chip-border: '#7B6C5D'         # taupe, mørkere (nyanse) – samme som border
  # Status (kant = tekstfarge)
  status-open-bg: '#CBDDC1'      # pastellgrønn
  status-open-fg: '#47553F'      # salviegrønn, mørk
  status-open-border: '#47553F'
  status-chosen-bg: '#EBC7BC'    # blush
  status-chosen-fg: '#81432C'    # terrakotta, mørk (nyanse)
  status-chosen-border: '#81432C'
  status-done-bg: '#F4E8CF'      # champagne
  status-done-fg: '#4D5829'      # oliven, mørk (nyanse)
  status-done-border: '#4D5829'
  status-cancelled-bg: '#D2CABD' # greige
  status-cancelled-fg: '#5E5347' # taupe, mørk (nyanse)
  status-cancelled-border: '#5E5347'
  # Meldinger
  error: '#81432C'               # terrakotta, mørk
  success: '#47553F'             # salviegrønn, mørk
typography:
  heading-1:
    fontFamily: 'ui-rounded, "SF Pro Rounded", "Nunito", "Segoe UI Variable Display", "Segoe UI", system-ui, sans-serif'
    fontSize: 28px
    fontWeight: '700'
    lineHeight: '1.25'
  heading-2:
    fontFamily: 'ui-rounded, "SF Pro Rounded", "Nunito", "Segoe UI Variable Display", "Segoe UI", system-ui, sans-serif'
    fontSize: 24px
    fontWeight: '700'
    lineHeight: '1.3'
  heading-3:
    fontFamily: 'ui-rounded, "SF Pro Rounded", "Nunito", "Segoe UI Variable Display", "Segoe UI", system-ui, sans-serif'
    fontSize: 20px
    fontWeight: '700'
    lineHeight: '1.3'
  brand:
    fontFamily: 'ui-rounded, "SF Pro Rounded", "Nunito", "Segoe UI Variable Display", "Segoe UI", system-ui, sans-serif'
    fontSize: 20px
    fontWeight: '800'
    lineHeight: '1.2'
    letterSpacing: -0.01em
  body:
    fontFamily: 'system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif'
    fontSize: 18px
    fontWeight: '400'
    lineHeight: '1.55'
  body-strong:
    fontFamily: 'system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif'
    fontSize: 18px
    fontWeight: '700'
    lineHeight: '1.55'
  label:
    fontFamily: 'system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif'
    fontSize: 18px
    fontWeight: '700'
    lineHeight: '1.4'
  option:
    fontFamily: 'system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif'
    fontSize: 18px
    fontWeight: '400'
    lineHeight: '1.4'
  price:
    fontFamily: 'system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif'
    fontSize: 22px
    fontWeight: '700'
    lineHeight: '1.3'
  meta:
    fontFamily: 'system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif'
    fontSize: 16px
    fontWeight: '700'
    lineHeight: '1.3'
rounded:
  sm: 10px
  md: 12px
  lg: 14px
  xl: 20px
  full: 9999px
spacing:
  '1': 4px
  '2': 8px
  '3': 12px
  '4': 16px
  '5': 24px
  '6': 32px
  '7': 48px
  '8': 64px
  gutter-mobile: 16px
  gutter-wide: 24px
  card-padding: 24px
  touch-target: 48px
  content-max: 1200px
  reading-max: 760px
  form-max: 640px
components:
  button-primary: { backgroundColor: '{colors.primary}', textColor: '{colors.on-primary}', borderColor: '{colors.primary}', borderWidth: 2px, typography: '{typography.label}', rounded: '{rounded.md}', height: '{spacing.touch-target}', padding: 0 22px }
  button-secondary: { backgroundColor: transparent, textColor: '{colors.link}', borderColor: '{colors.link}', borderWidth: 1.5px, typography: '{typography.label}', rounded: '{rounded.md}', height: '{spacing.touch-target}', padding: 0 22px }
  button-text: { backgroundColor: transparent, textColor: '{colors.link}', textDecoration: underline (offset 3px), typography: '{typography.label}', height: '{spacing.touch-target}', padding: 0 14px }
  button-disabled: { backgroundColor: '{colors.disabled-bg}', textColor: '{colors.disabled-fg}', borderColor: '{colors.disabled-fg}', borderWidth: 1.5px }
  card: { backgroundColor: '{colors.surface-card}', borderColor: '{colors.border}', borderWidth: 1px, rounded: '{rounded.lg}', padding: '{spacing.card-padding}', shadow: '0 1px 2px rgba(47,48,45,.06), 0 4px 14px rgba(47,48,45,.07)' }
  status-badge: { typography: '{typography.meta}', rounded: '{rounded.full}', borderWidth: 1.5px, padding: 3px 12px, variants: 'open | chosen | done | cancelled → {colors.status-<variant>-bg/-fg/-border}' }
  action-tag: { backgroundColor: '{colors.badge-bg}', textColor: '{colors.badge-fg}', typography: '{typography.meta}', rounded: '{rounded.full}', padding: 4px 16px, wrap: 'brytes så mange linjer som trengs; aldri line-clamp, ellipse eller overflow hidden', maxWidth: 100% }
  situation-label: { textColor: '{colors.ink}', typography: '{typography.body-strong}' }
  category-chip: { backgroundColor: '{colors.chip-bg}', textColor: '{colors.chip-fg}', borderColor: '{colors.chip-border}', borderWidth: 1px, typography: '{typography.meta}', rounded: '{rounded.full}', padding: 3px 12px }
  category-button: { backgroundColor: '{colors.surface-card}', textColor: '{colors.ink}', borderColor: '{colors.border}', borderWidth: 1px, borderWidthSelected: 3px, borderColorSelected: '{colors.primary}', typography: '{typography.option}', typographySelected: '{typography.label}', rounded: '{rounded.md}', minHeight: '{spacing.touch-target}', hyphens: auto }
  list-row: { backgroundColor: '{colors.surface-card}', borderColor: '{colors.border}', borderWidth: 1px, rounded: '{rounded.lg}', padding: '{spacing.5}', gap: '{spacing.3}', shadow: '0 1px 2px rgba(47,48,45,.06), 0 4px 14px rgba(47,48,45,.07)', titleTypography: '{typography.body-strong}', chevron: '› strekikon 24 px, {colors.link}, på tittellinja, 16 px fra høyre kant', titlePaddingRight: 40px, actionsDivider: '1px {colors.border}', actionsPadding: '{spacing.4} {spacing.5}', hoverBorder: '2px {colors.primary}' }
  input: { backgroundColor: '{colors.surface-input}', textColor: '{colors.ink}', borderColor: '{colors.border}', borderWidth: 1.5px, borderColorError: '{colors.error}', borderWidthError: 2px, typography: '{typography.body}', rounded: '{rounded.sm}', height: '{spacing.touch-target}', padding: 0 14px }
  field-error: { textColor: '{colors.error}', typography: '{typography.body-strong}' }
  message-error: { backgroundColor: '{colors.surface-card}', textColor: '{colors.error}', borderColor: '{colors.border}', stripeColor: '{colors.error}', stripeWidth: 6px, rounded: '{rounded.sm}', padding: 12px 16px }
  message-success: { backgroundColor: '{colors.surface-card}', textColor: '{colors.success}', borderColor: '{colors.border}', stripeColor: '{colors.success}', stripeWidth: 6px, rounded: '{rounded.sm}', padding: 12px 16px }
  topbar: { backgroundColor: '{colors.topbar}', textColor: '{colors.topbar-text}', brandColor: '{colors.brand-icon}', typography: '{typography.option}', typographyActive: '{typography.label}', activeIndicator: '3px {colors.nav-indicator} (underkant)', focusRing: '3px {colors.topbar-focus}, offset 2px', padding: 8px 16px }
  bottom-nav: { backgroundColor: '{colors.topbar}', textColor: '{colors.topbar-text}', typography: '{typography.option}', typographyActive: '{typography.label}', activeIndicator: '3px {colors.nav-indicator} (overkant)', focusRing: '3px {colors.topbar-focus}, offset -3px', minItemHeight: 56px, columns: 'repeat(3, minmax(0, 1fr))', whiteSpace: normal }
  nav-badge: { backgroundColor: '{colors.badge-bg}', textColor: '{colors.badge-fg}', typography: '{typography.meta}', rounded: '{rounded.full}', padding: 1px 9px }
  tabs: { textColor: '{colors.ink}', activeIndicator: '4px {colors.primary} (underkant)', borderColor: '{colors.border}', typography: '{typography.option}', typographyActive: '{typography.label}', height: '{spacing.touch-target}' }
  star-rating: { starSize: 48px, starSelected: '{colors.primary}', starUnselected: '{colors.border} (omriss)', gap: '{spacing.2}', variants: 'input | display', displayStarSize: 20px, displayGap: '{spacing.1}', displayText: '{typography.body-strong}' }
  dialog: { backgroundColor: '{colors.surface-card}', rounded: '{rounded.xl}', padding: '{spacing.5}', maxWidth: 480px, maxHeight: 'calc(100dvh - 32px)', overflowY: auto, shadow: '0 8px 32px rgba(47,48,45,.25)', backdrop: '{colors.scrim} @ 55 %' }
  ki-suggestion-box: { backgroundColor: '{colors.surface-page}', textColor: '{colors.ink}', borderColor: '{colors.border}', borderStyle: dashed, borderWidth: 1.5px, rounded: '{rounded.md}', padding: '{spacing.4}' }
  phone-box: { backgroundColor: '{colors.status-chosen-bg}', textColor: '{colors.ink}', borderColor: '{colors.status-chosen-border}', borderWidth: 2px, rounded: '{rounded.lg}', padding: '{spacing.4}' }
  empty-state: { textColor: '{colors.ink}', typography: '{typography.body}', padding: '{spacing.6} {spacing.4}' }
---

# DESIGN – Nabolagshelten

Visuell identitet. Atferd, tekster og tilstander står i [EXPERIENCE.md](EXPERIENCE.md). Fargetemaet ble valgt i [mockups/color-themes-4.html](mockups/color-themes-4.html) (variant P1), med strukturen fra variant D2 i [mockups/color-themes-3.html](mockups/color-themes-3.html). Eksempeltekstene i de filene er ikke produkttekst. Mockups av nøkkelskjermene i temaet ligger i [mockups/](mockups/) og er listet i EXPERIENCE.md § Foundation. Ved konflikt gjelder denne fila og EXPERIENCE.md foran mockups, fargeprøver og skisser.

## Brand & Style

Nabolagshelten skal føles som en hyggelig oppslagstavle i nabolaget, ikke som en offentlig etat eller en legeside. Uttrykket er varmt og jordnært: sand og beige som flater, mørk salviegrønn som bærer handlingene, blush og terrakotta som en liten varm aksent. Litt personlighet gjennom avrundede overskrifter, myke hjørner og enkle strekikoner, men aldri barnslig. Det skal se profesjonelt og troverdig ut, fordi tillit mellom fremmede er hele poenget (PRD §1, §4.7).

Designet er laget for Kari, 72, som «gir opp hvis noe er uoversiktlig», og for Amir, 21, som vil ha en rask liste (PRD §2.1). Det gir tre faste grep: stor tekst og store trykkflater, knapper med tekst, og ingenting skjult bak menyer eller ikoner (NFR-7, NFR-11).

**Ett tema.** Appen har ett lyst fargetema og ingen mørk modus. Mørk modus ble vurdert og tatt ut igjen (se `.memlog.md`): ett tema halverer antall fargepar som må kontrasttestes (NFR-7, SM-5), og gruppen prioriterer kjerneflyten før fristen. Appen setter `color-scheme: light` og følger ikke `prefers-color-scheme`.

## Colors

Alle farger kommer fra gruppens palett: antrasitt, mørkebrun, mokka, pastellgrønn, salviegrønn, oliven, terrakotta, blush, champagne, karamell, sand, latte, cappuccino, greige, taupe og beige. Ingen hvit og ingen svart. Der en palettfarge måtte gjøres mørkere for å nå kontrastkravet, heter den «Nyanse av …» i tabellen under og «(nyanse)» i frontmatter.

| Palettnavn | Hex | Nyanse? | Roller (token) |
|---|---|---|---|
| Sand | `#E3D3B3` | | `surface-page`, KI-forslagsboks |
| Beige | `#EEE5D3` | | `surface-card` – kort, rader, dialoger, meldinger; `chip-bg` |
| Champagne | `#F4E8CF` | | `surface-input`, `on-primary`, `topbar-text`, `status-done-bg` |
| Pastellgrønn | `#CBDDC1` | | `status-open-bg` |
| Blush | `#EBC7BC` | | `badge-bg`, `brand-icon`, `nav-indicator`, `topbar-focus`, `status-chosen-bg` |
| Greige | `#D2CABD` | | `status-cancelled-bg`, `disabled-bg` |
| Antrasitt | `#2F302D` | | `ink`, `focus`, `scrim` |
| Mokka | `#6E4E3A` | | `ink-muted` – dempet tekst |
| Mørkebrun | `#4B3324` | | `chip-fg`, `badge-fg` |
| Salviegrønn, mørk | `#47553F` | Nyanse av salviegrønn – lys tekst på grønt og grønn tekst på lyse flater | `primary`, `link`, `topbar`, `status-open-fg`, `success` |
| Terrakotta, mørk | `#81432C` | Nyanse av terrakotta – feiltekst og «Hjelper valgt»-tekst ≥ 4,5:1 | `error`, `status-chosen-fg` |
| Oliven, mørk | `#4D5829` | Nyanse av oliven – olivengrønn tekst ≥ 4,5:1 | `status-done-fg` |
| Taupe, mørk | `#5E5347` | Nyanse av taupe – Avbrutt-tekst ≥ 4,5:1 | `status-cancelled-fg`, `disabled-fg` |
| Taupe, mørkere | `#7B6C5D` | Nyanse av taupe – kantlinje ≥ 3:1 mot sand og beige | `border`, `chip-border` |

Karamell, latte og cappuccino brukes ikke i v1.

**Kontrast** (WCAG 2.1, relativ luminans; krav: tekst ≥ 4,5:1; kanter, fokusring og merkekanter ≥ 3:1 – NFR-7):

| Par | Forhold |
|---|---|
| `ink` på `surface-page` / `surface-card` / `surface-input`; `focus` mot de to første | 9,00 / 10,61 / 10,93 |
| `ink-muted` på `surface-page` / `surface-card` | 5,06 / 5,96 |
| `on-primary` på `primary` (primærknapp, topplinje-tekst) | 6,55 |
| `link` (også pil › i `list-row`), `success` på `surface-card` / `surface-page` | 6,36 / 5,39 |
| `brand-icon`, `nav-indicator`, `topbar-focus` mot `topbar` | 5,09 |
| `badge-fg` på `badge-bg` | 7,47 |
| `chip-fg` på `chip-bg` (mørkebrun på beige) | 9,33 |
| `primary` / `border` (stjernevisning, dekorativ) mot `surface-page` | 5,39 / 3,43 |
| `status-open-fg` på `status-open-bg` | 5,55 |
| `status-chosen-fg` på `status-chosen-bg` | 4,84 |
| `status-done-fg` på `status-done-bg` | 6,30 |
| `status-cancelled-fg` på `status-cancelled-bg` | 4,61 |
| Statuskant mot `surface-card` (åpen/valgt/utført/avbrutt) | 6,36 / 6,05 / 6,12 / 5,99 |
| `error` på `surface-card` / `surface-page` | 6,05 / 5,13 |
| `border`, `chip-border` mot `surface-card` (= `chip-bg`) / `surface-page` / `surface-input` | 4,05 / 3,43 / 4,17 |
| `ink` på `status-chosen-bg` (telefonboks) | 8,49 |
| `disabled-fg` på `disabled-bg` | 4,61 |

**Hva fargene ikke brukes til.** Blush er bare i topplinjen, på handlingsmerker (`action-tag`) og på «Hjelper valgt» – aldri som knappefarge. Terrakotta brukes bare til feil og «Hjelper valgt». Grønt er handling og «Åpen». Ingen blå toner (fjernet bevisst fra tidligere tema). Farge er aldri eneste bærer av mening; status har alltid ord og ikon (NFR-7).

## Typography

To skriftfamilier, begge systemskrifter, ingen nedlastede fonter (raskt og virker på en ren maskin, NFR-1):

- **Overskrifter og logo:** avrundet systemskrift (`ui-rounded` → SF Pro Rounded → Nunito om installert → Segoe UI). Gir vennlighet uten å bli leken.
- **Brødtekst, etiketter, knapper:** nøytral systemskrift (`system-ui`-stakken). Lesbarhet først.

**Regler.** Brødtekst og all tekst brukeren skal lese eller skrive er minst 18 px (NFR-7). Bare merker er 16 px, og da alltid fet. Merker har normalt ett–fire ord (unntaket står under `action-tag`). Størrelser angis i `rem` i koden (18 px = 1.125rem) så zoom og nettleserens tekststørrelse virker. Ingen versaler i løpende tekst, ingen kursiv for viktig informasjon. Linjelengde høyst ca. 70 tegn i løpende tekst.

| Rolle | Token | Størrelse / vekt | Brukes til |
|---|---|---|---|
| Sidetittel | `{typography.heading-1}` | 28 / 700 | «Ledige oppdrag i 0571 Oslo», «Mine oppdrag» |
| Seksjon / korttittel | `{typography.heading-2}` | 24 / 700 | Oppdragstittel på kort og i detaljer, dialogspørsmål |
| Gruppe | `{typography.heading-3}` | 20 / 700 | «Trenger handling», «Pågår», «Ferdige», «Forslag» |
| Logo | `{typography.brand}` | 20 / 800 | «Nabolagshelten» i topplinjen |
| Brødtekst | `{typography.body}` | 18 / 400 | All løpende tekst, felttekst |
| Utheving | `{typography.body-strong}` | 18 / 700 | Tidspunkt, feiltekst ved felt, situasjon, radtittel i `list-row`, snitt ved stjerner |
| Etikett / knapp | `{typography.label}` | 18 / 700 | Feltetiketter, knappetekst, **aktivt** menyvalg, **aktiv** fane, **valgt** kategoriknapp |
| Valg | `{typography.option}` | 18 / 400 | Menyvalg, faner og kategoriknapper som **ikke** er valgt eller aktive |
| Beløp | `{typography.price}` | 22 / 700 | «200 kr», «Uten betaling» på kort |
| Merke | `{typography.meta}` | 16 / 700 | Bare merker: status, kategori, handlingsmerker (`action-tag`), antall i menyen |

**Fet skrift i valg.** I menyen, fanene og kategoriknappene står fet skrift for valgt eller aktivt, alltid sammen med et tegn som ikke er skrift (strek, kant eller hake). Feltetiketter og knappetekst er alltid fete, fordi de ikke er valg. [ASSUMPTION] Regelen er satt etter mockupene.

## Layout & Spacing

Skala på 4 px-trinn: 4 / 8 / 12 / 16 / 24 / 32 / 48 / 64 (`{spacing.1}`–`{spacing.8}`). Tett relatert innhold (etikett og felt, tittel og kategori) får 4–8 px; elementer i et kort 12–16 px; seksjoner 24–32 px; større skiller 48 px. Mye luft er et bevisst valg for Kari.

| Bredde | Navn | Rammer |
|---|---|---|
| 360–767 px | Mobil | Én kolonne. Sidemarg `{spacing.gutter-mobile}`. Topplinje med bare logo; menyen `{components.bottom-nav}` fast nederst. |
| 768–1279 px | Nettbrett | Sidemarg `{spacing.gutter-wide}`. Menyen i topplinjen. Oversikten i 2 kolonner. Skjema i én kolonne, maks `{spacing.form-max}`. |
| ≥ 1280 px | PC | Innhold sentrert, maks `{spacing.content-max}`. Oversikten i 3 kolonner. Detaljer og «Mine oppdrag» maks `{spacing.reading-max}`. |

360, 768 og 1280 px er testbreddene i NFR-6. Layouten skal også flyte om ved 320 px (WCAG 1.4.10, tilsvarer 400 % zoom på 1280 px), uten vannrett rulling; det testes i T4 (EXPERIENCE.md). [ASSUMPTION] Antall kolonner og maksbredder er satt i UX-arbeidet; kildene sier bare «På nettbrett og PC kan de samme elementene ligge bredere» (skisser).

**Bunnmenyen og plass nederst.** Den faste bunnmenyen reserverer plass: `padding-bottom` på `body` lik menyhøyden + `env(safe-area-inset-bottom)`, og `scroll-padding-bottom` på `html` lik menyhøyden, så et felt eller en lenke med fokus rulles fram over menyen. Se `bottom-nav` for når menyen ikke er fast.

## Elevation & Depth

Dybde kommer først og fremst fra tone: sand side, beige kort, champagne felt. Skygge brukes lite:

- **Kort og rader:** én myk skygge, `{components.card.shadow}` (samme i `list-row`), antrasitt-tonet, aldri svart. Kortet har også 1 px kant, så det skilles fra siden selv uten skygge.
- **Dialog:** `{components.dialog.shadow}` over et slør av `{colors.scrim}` med 55 % opasitet.
- **Topplinje og bunnmeny:** ingen skygge; mørk salvie skiller dem fra innholdet.
- Ingen skygge ved hover som eneste tegn på at noe kan trykkes.

## Shapes

Myke, vennlige hjørner som skiller seg fra skarpe skjemaer på offentlige nettsider:

- `{rounded.sm}` 10 px – felt, meldinger, menyvalg.
- `{rounded.md}` 12 px – knapper, kategoriknapper, KI-forslagsboks.
- `{rounded.lg}` 14 px – kort, rader (`list-row`), telefonboks.
- `{rounded.xl}` 20 px – dialoger.
- `{rounded.full}` – bare merker: status, kategori, antall i menyen, handlingsmerker (`action-tag`).

Knapper er aldri pilleformet; pilleform betyr «merke», ikke «trykk her».

**Ikoner:** enkle strekikoner (ca. 2 px strek, avrundede ender), 20–24 px i tekst og 14–18 px i merker. Alltid sammen med tekst, aldri alene som knapp. Ikoner ved siden av tekst er dekorative (`aria-hidden`). Ingen illustrasjoner i v1. Logoen er et hus med hjerte i `{colors.brand-icon}`.

## Components

Visuelle spesifikasjoner, gruppert etter type. Atferd for de samme komponentene står i EXPERIENCE.md § Component Patterns.

### Fokus

- **Fokus** – Alle interaktive elementer: 3 px ring i `{colors.focus}` med 3 px avstand. I topplinje og bunnmeny: 3 px `{colors.topbar-focus}`. Fokus vises med `:focus-visible` og fjernes aldri. På kort og lenkerader, der lenken dekker hele flaten, tegnes ringen på lenkens `::after` med `outline-offset` minst 2 px, så ringen også virker i nettlesere uten `:has()`. Aldri `outline: none` uten erstatning i samme regel. Ringen er `outline`, ikke `box-shadow`, så den synes også med tvungne farger. Kvittering, feiloppsummering og `h1` som appen flytter fokus til (`tabindex="-1"`), viser ringen med `:focus`, ikke bare `:focus-visible`, så også den som trykket med finger eller mus, ser hvor hen er. Når fokus flyttes, står i EXPERIENCE.md.

### Knapper

Hvilken knappetype hver handling får, står i EXPERIENCE.md.

- **button-primary** – Fylt `{colors.primary}`, tekst `{colors.on-primary}`, høyde minst 48 px, `{rounded.md}`. Hovedhandlingen, én per skjerm, f.eks. «Legg ut oppdrag», «Publiser» og bekreftende knapp i dialog. Kan ha et strekikon foran teksten («+ Legg ut oppdrag»).
- **button-secondary** – Omriss 1,5 px `{colors.link}`, tekst `{colors.link}`, gjennomsiktig flate. Andre handlinger, f.eks. «Få forslag», «Rediger» og «Vis alle kategorier».
- **button-text** – Understreket tekst i `{colors.link}` med 48 px trykkflate. Navigering og angre, f.eks. «Tilbake», «Se profil» og angre-valget i dialoger («Ikke ennå»).
- **button-disabled** – Gjelder alle knappetyper når de er deaktivert: `{colors.disabled-bg}`, tekst `{colors.disabled-fg}` (4,61:1), kant i samme farge. Teksten forteller hvorfor der det trengs («Lager forslag …»). [ASSUMPTION] Utseendet er ikke gitt i kildene.
- **Knapper nederst i skjema og i dialog** – Under 768 px står knappene under hverandre, både i skjema og i dialog: primærknappen (den bekreftende) øverst i full bredde og en eventuell tekstknapp under, f.eks. «Publiser» / «Tilbake til steg 1» og «Slett kontoen min» / «Tilbake til profilen» (besluttet 2026-11-07). Fra 768 px står knappene nederst i skjema på samme linje, primærknappen først.

### Kort og rader

- **card** – `{colors.surface-card}`, 1 px `{colors.border}`, `{rounded.lg}`, innvendig `{spacing.card-padding}`, kortskygge. Oppdragskort i oversikten: kategori øverst (`category-chip`), tittel (`heading-2`), tidspunkt (`body-strong` med klokkeikon), postnummer og poststed (`ink-muted` med stedikon), beløp (`price`). Hele kortet er trykkflate. Hover: 2 px `{colors.primary}`-kant. Fokus: samme kant og fokusringen.
- **list-row** – Rad i en liste: «Mine oppdrag», interessertlista i detaljer og tilbakemeldinger på profilen. Flate `{colors.surface-card}`, 1 px `{colors.border}`, `{rounded.lg}`, kortskygge, innvendig 24 px, 12 px mellom radene. Oppbygning ovenfra: (1) **tittel** i `body-strong` (18/700) – oppdragstittel, navnet på en interessert eller vurderingen («5 av 5 stjerner»); (2) **merkelinje**: `status-badge` først, så `situation-label` og/eller handlingsmerke (`action-tag`), brytes til neste linje ved behov; (3) **faktalinjer** med ikon: tidspunkt (`body-strong`), «3 har meldt interesse» / «Hjelper: Amir», melding eller kommentar, metalinje i `ink-muted`; (4) eventuelt **knapper** nederst under en 1 px skillelinje i `{colors.border}`, med 16 px over og under og 24 px på sidene.
  - *Lenkerad:* hele raden over skillelinjen er én lenke (trykkflaten dekker den), med pil › (24 px strekikon i `{colors.link}`) til høyre på tittellinja; tittelen holder 40 px fri plass til pila, resten av raden bruker hele bredden. Hover: 2 px `{colors.primary}`-kant. Fokus: kant og fokusring, som `card`.
  - *Ikke-lenkerad:* ingen pil, ingen hover. Kan inneholde egne lenker og knapper (f.eks. «Se profil», «Velg Amir», navnet på den som ga tilbakemeldingen).
  - Knapper står aldri inne i lenken. [ASSUMPTION] Mål og oppbygning er satt etter mockupene.
- **Forhåndsvisning** – Den synlige teksten «Slik vises oppdraget for andre.» i `{typography.label}`, så et `card` uten hover og uten pil, med 1,5 px stiplet `{colors.border}` i stedet for heltrukken kant, så det ikke ser ut som et kort man kan trykke på. [ASSUMPTION] Stiplet kant.

### Merker

- **status-badge** – Pille med flate, tekst og 1,5 px kant i statusfargen, ikon foran: Åpen (åpen ring), Hjelper valgt (person), Utført (hake), Avbrutt (kryss). Farger: `{colors.status-open-bg}` / `-fg` / `-border` osv.
- **action-tag** – Handlingsmerke: noe brukeren må gjøre (FR-18-merkene, f.eks. «Er jobben gjort?»). Pille i `{colors.badge-bg}` med `{colors.badge-fg}`, uten kant, med et lite pilikon. Samme farge som antallet i menyen, så de to henger sammen. Teksten forkortes aldri og brytes over så mange linjer som trengs: normalt høyst to («Oppdraget er endret etter at du meldte interesse» på 360 px ved 100 % tekststørrelse), men fire–fem ved 200 % tekststørrelse. Aldri `line-clamp`, ellipse eller `overflow: hidden`. Ikonet står ved første linje, og 16 px sidepolstring holder teksten innenfor pilleformen. Merket er aldri bredere enn raden det står i. [ASSUMPTION] Polstring og ikonplassering ved to linjer.
- **situation-label** – Brukerens egen situasjon i «Oppdrag jeg hjelper med» («Venter på svar», «Du er valgt» …). Fet `ink`-tekst med strekikon, ingen flate – skal ikke forveksles med status.
- **category-chip** – Kategori på kort, i detaljer og i forhåndsvisningen: pille med beige flate `{colors.chip-bg}`, tekst `{colors.chip-fg}` og tynn kant (1 px `{colors.chip-border}`), med kategoriikon. Kanten gjør merket synlig både på beige kort og rett på sandfargen (4,05:1 / 3,43:1). Nøytral; kategorier har ikke egne farger. Pilleformen skiller merket fra kategoriknappene, som har `{rounded.md}`.

### Skjema og filter

- **category-button** – Store valgknapper for kategori i filteret og i skjemaet: `{colors.surface-card}`, 1 px kant, ikon foran teksten i filteret og over teksten i skjemaet, tekst `{typography.option}`, minst 48 px høy og vokser med teksten. Valgt: 3 px `{colors.primary}`-kant, hakeikon foran teksten og fet tekst (`{typography.label}`) – aldri bare farge. Kategoriikonet **beholdes** når knappen er valgt; haken kommer i tillegg («Alle» har bare hake). Valgt utseende gjelder både for `aria-current="true"` (filteret, som er lenker) og for `:checked` (radioknappene i skjemaet, via `label:has(:checked)`); fokusringen tegnes med `label:has(:focus-visible)`. Kategoriknappene brytes over flere linjer i stedet for å rulle sidelengs. Lange navn brytes etter skråstreken («Bærehjelp/» + «flytting»); ellers `hyphens: auto` (virker med `lang="nb"`), aldri `overflow-wrap: anywhere`. [ASSUMPTION] Utseendet på valgt tilstand.
- **input** – Tekstfelt, tekstområde, dato, klokkeslett og radioknapper: flate `{colors.surface-input}`, 1,5 px `{colors.border}`, `{rounded.sm}`, høyde minst 48 px, tekst 18 px. Etikett (`<label>`) alltid synlig over feltet; hjelpetekst i `ink-muted` mellom etikett og felt. Ingen plassholdertekst som erstatning for etikett. Feil: 2 px `{colors.error}`-kant + **field-error** under feltet (fet tekst i `{colors.error}` med varselikon). Radioknapper og avkrysning: minst 24 px merke inne i en 48 px høy trykkflate med etiketten.
- **Skjema, steg 2** – To feltgrupper med egen oppstilling:
  - *Når?*: gruppeetiketten «Når?» i `{typography.label}`, så «Dato» og «Klokkeslett» **under hverandre under 768 px**, så feiltekstene får full bredde (besluttet 2026-11-07); side om side fra 768 px (dato ca. 10,5em, klokkeslett ca. 7em, 12 px mellomrom). Formatet står som hjelpetekst over hvert felt («dd.mm.åååå, for eksempel 14.11.2026»), ikke som plassholdertekst. Ingen kalenderikon. En feil som gjelder hele tidspunktet, står én gang under begge feltene.
  - *Hva tilbyr du?*: to radioknapper under hverandre, «Beløp» og «Uten betaling». Feltet «Beløp i kr» står innrykket 36 px under «Beløp» (på linje med etiketteksten), ca. 8em bredt, med «kr» etter feltet.

### Meldinger

- **message-error / message-success** – Kvitteringer og feil etter innsending: `{colors.surface-card}`, 1 px kant og 6 px stripe til venstre i `{colors.error}` / `{colors.success}`, ikon (varseltrekant / hake) og tekst i samme farge.
- **Feiloppsummering** – `message-error` med overskrift «Skjemaet har 2 feil» i `heading-3` og en punktliste med lenker i `{colors.link}`, understreket, én per feil. Står rett etter `h1`.

### Navigasjon

- **Hopp til innholdet** – Når lenken har fokus, står den øverst til venstre over topplinjen som en `button-primary` med fokusring i `{colors.topbar-focus}` (blush), siden den står mot den grønne topplinjen.
- **topbar** – `{colors.topbar}` med logo i `{colors.brand-icon}` til venstre. Fra 768 px ligger menyvalgene til høyre: tekst `{colors.topbar-text}` (`{typography.option}`), 48 px høye, aktivt valg fet (`{typography.label}`) med 3 px strek i `{colors.nav-indicator}` under. Undersider markerer menyvalget de hører til på samme måte (regel i EXPERIENCE.md § Information Architecture).
- **bottom-nav** – Brukes under 768 px. `{colors.topbar}`, tre like brede valg (`grid-template-columns: repeat(3, minmax(0, 1fr))`) med ikon over tekst. 56 px er **minstehøyde**: teksten får bryte linje (`white-space: normal`, `overflow-wrap: break-word`), og menyen blir høyere ved stor tekst i stedet for å klippe eller rulle sidelengs. Aktivt valg fet med 3 px strek i `{colors.nav-indicator}` øverst; undersider som i topplinjen. [ASSUMPTION] Farge og oppbygning følger topplinjen; fargeprøven viste bare topplinjen.
  - *Fast eller i sideflyten:* menyen er fast nederst. Når skjermen er lav (`@media (max-height: 30em)`: liggende telefon, stor zoom, skjermtastatur) eller teksten er så stor at menyen blir høyere enn 56 px, er menyen `position: static` nederst i sideflyten i stedet for fast. Plassen den faste menyen reserverer, står i § Layout & Spacing. [ASSUMPTION] Hvordan «stor tekst» oppdages (f.eks. `min-height` målt i `em`) avgjøres i koden.
- **nav-badge** – Antall ved «Mine oppdrag» i menyen: pille i `{colors.badge-bg}` / `{colors.badge-fg}`, 16 px fet, viser bare tallet («2»).
- **tabs** – De to fanene i «Mine oppdrag»: like brede, minst 48 px, tekst kan brytes over to linjer på 360 px. Aktiv fane: fet (`{typography.label}`), 4 px `{colors.primary}`-strek under. Inaktiv: `ink` i `{typography.option}`, 1 px `{colors.border}` under.

### Andre komponenter

- **star-rating** – To varianter:
  - *Input* (tilbakemelding): fem stjerner, hver en 48 × 48 px trykkflate. Stjerne 1 til og med valgt verdi er fylt i `{colors.primary}`; resten er omriss i `{colors.border}`. Fokusringen tegnes rundt stjernen med fokus (`label:has(:focus-visible)`). Under stjernene står valgt verdi med ord («4 av 5 stjerner»), og ytterpunktene «Dårlig» og «Veldig bra» står under første og siste stjerne.
  - *Visning* (snitt på profilen): fem små stjerner, 20 px med 4 px mellomrom, fylt i `{colors.primary}` og omriss i `{colors.border}`. Teksten «4,9 av 5, 11 vurderinger» står i `body-strong`, med stjernene foran teksten eller over den når linja blir for smal. [ASSUMPTION] Størrelsen.
- **dialog** – Native `<dialog>`. Sentrert kort i `{colors.surface-card}`, `{rounded.xl}`, maks 480 px bred (full bredde minus 16 px marg på mobil), maks høyde `calc(100dvh - 32px)` med `overflow-y: auto`, så innholdet ruller inne i dialogen ved stor zoom. Sløret er `::backdrop`. Spørsmålet i `heading-2`, linja «Gjelder «…».» og forklaring i `body`, knapper under: bekreftende som `button-primary`, angre som `button-text`, stilt opp som beskrevet i gruppen Knapper.
- **ki-suggestion-box** – Ett forslag per felt: flate `{colors.surface-page}`, 1,5 px stiplet `{colors.border}`. Stiplet kant betyr «ikke brukt ennå». Overskrift «Forslag til tittel» osv. i `heading-3`, forslagsteksten i `body`, og under den knappene «Bruk» (`button-secondary`) og «Ikke bruk» (`button-text`). Et eventuelt tips står **inne i** forslagsboksen for beskrivelsen, under forslagsteksten og over knappene, med lyspære-ikon. [ASSUMPTION] Utseendet.
- **phone-box** – Boks i `{colors.status-chosen-bg}` med 2 px `{colors.status-chosen-border}`: navn på motparten, telefonnummeret stort (`price`) som understreket `tel:`-lenke i `{colors.ink}` med minst 48 px høy trykkflate, og «Avtal detaljene direkte.». Fargen knytter boksen til status «Hjelper valgt».
- **empty-state** – Sentrert tekst i `body` med et enkelt strekikon over, forklaring og én videre handling (`button-secondary` eller `button-text`).
- **Antallslinje** – «4 ledige oppdrag i 0571 Oslo» i `body` og `{colors.ink-muted}` rett under `h1` i oversikten. I Mine oppdrag: «2 oppdrag trenger at du gjør noe.» i `body-strong`, med samme pilikon som handlingsmerket (`action-tag`) foran.

## Do's and Don'ts

| Gjør | Ikke gjør |
|---|---|
| Bruk bare palettfargene; mørkne en palettfarge og kall den «Nyanse av …» når kontrasten krever det | Hvit (`#FFFFFF`) eller svart (`#000000`) bakgrunn eller tekst |
| Vis status med ord + ikon + kant + farge | Status eller valgt tilstand vist bare med farge |
| Én fylt primærknapp per skjerm; resten omriss eller lenke | Flere fylte knapper som konkurrerer (heller ikke «Velg» på hver interessert) |
| Tekst på alle knapper og menyvalg, ikon som tillegg | Knapper med bare ikon, f.eks. bare «+» |
| Brødtekst ≥ 18 px, trykkflater ≥ 48 px (frittstående lenker også; lenker i løpende tekst er unntatt) | Små lenker tett i tett, tekst under 16 px |
| La tekst bryte linje og flater vokse (`min-height`) | Fast høyde, `nowrap`, `line-clamp` eller ellipse på tekst brukeren trenger |
| Grønt for handling og «Åpen», blush for «trenger handling» og «Hjelper valgt», terrakotta for feil | Blå toner; egne farger per kategori; rødt som flate bak tekst |
| Kategori som store knapper med ikon og tekst | Nedtrekksliste for kategori |
| Pil › bare på rader som er lenker; knapper under raden, utenfor lenken | Pil på rader som ikke kan åpnes; knapper inne i en lenke |
| Fet skrift i meny, faner og kategoriknapper bare for valgt/aktivt | Fet skrift på alle valg, eller fet som eneste tegn på valgt |
| Synlig fokusring på alt | `outline: none` uten erstatning |
| Systemskrifter, strekikoner | Nedlastede fonter, illustrasjoner, emoji som ikon |
| Ett lyst tema | Mørk modus eller fargebryter i v1 |
