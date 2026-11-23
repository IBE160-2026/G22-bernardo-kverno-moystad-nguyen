---
title: Avstemming UX → arkitekturspine
date: 2026-11-23
spine: ../ARCHITECTURE-SPINE.md (status draft, updated 2026-11-23)
inputs:
  - ../../../ux-designs/ux-G22-bernardo-kverno-moystad-nguyen-2026-11-07/EXPERIENCE.md
  - ../../../ux-designs/ux-G22-bernardo-kverno-moystad-nguyen-2026-11-07/DESIGN.md
---

# Avstemming: UX-dokumentene mot arkitekturspinen

## Konklusjon

Spinen har tatt hovedvalget UX ba om (server-rendret, native `<dialog>`, vanlig CSS, ingen skjelett-lasting), og AD-7, AD-9, AD-10 og AD-11 svarer på flere av punktene i EXPERIENCE.md § Åpne punkter → Til arkitektur. Men spinen sier nesten ingenting om **klientsiden**. Den sier at «det finnes ikke noe eget frontend-lag» og at «alle skjema virker uten JavaScript», mens UX krever flere ting som bare går med JavaScript eller med forespørsler uten sidelasting: KI-forslag, to steg på mobil, poststed som vises mens man skriver, teller, forhåndsvisning, sending-tilstand og dialoger. Hvordan dette bygges, er nettopp der stories som bygges hver for seg, kommer til å gjøre det ulikt.

Største hull: KI-flyten (kritisk), at AD-7 ikke kan gjennomføres slik den står uten å bryte AD-1 (kritisk), og at det mangler én felles mekanisme for fokus og for hvordan sider rendres (base-kontekst, antallet i menyen, `<title>`, `aria-current`).

Antall funn: 2 kritiske, 8 høye, 6 middels, 5 lave.

Alvorlighet: **kritisk** = stories vil bygge dette ulikt, eller spinen sier noe som ikke kan gjennomføres. **høy** = UX-krav uten arkitektureier, med stor risiko for avvik eller omarbeid. **middels** = bør inn før stories skrives. **lav** = presisering.

---

## Kritiske

### K1 – KI-forespørselen («Få forslag») har ingen arkitektur

- **UX-referanse:** EXPERIENCE.md § Interaction Primitives → KI-forslag (punkt 1–6); § Fokus og opplesning, radene «Få forslag» og «Konflikt, KI-feil … uten sidelasting»; State Patterns, radene «KI henter» og «KI-feil / tidsavbrudd 10 s / kvote» («Resten av skjemaet kan fortsatt brukes», «Skjemaet beholder alt»); `{components.ki-suggestion-box}`; Voice and Tone («Lager forslag …», «Forslagene er klare.»).
- **Hva mangler:** UX beskriver en handling **uten sidelasting**. Knappen bytter tekst til «Lager forslag …» med `aria-live`, forslagsboksene settes inn under tre felt, feil vises med `role="alert"`, og «Bruk»/«Ikke bruk» flytter fokus til feltet. Spinen har bare AD-12 (KI-utgavene på serversiden) og regelen «Små vanilla-JS-filer for fokus og `<dialog>`». Ingenting sier:
  - om «Få forslag» er en `fetch` mot et eget endepunkt, eller en vanlig innsending som rendrer hele skjemaet på nytt
  - hvilken URL, hvilken metode og hvilket svarformat (HTML-bit eller JSON) som brukes
  - hvordan CSRF (AD-5: skjult felt + cookie) sendes med en `fetch`
  - hva endepunktet svarer når sesjonen er utløpt. AD-4 sender til innloggingssiden, og da får `fetch` en HTML-side med status 200 i stedet for en feil.
  - hvordan KI-tekst settes inn på klienten uten å bryte AD-11. AD-11 gjelder bare Jinja, så `innerHTML` på JSON-tekst er en XSS-vei.
  - hva som skjer uten JavaScript, når spinen sier at alle skjema virker uten
  - hvilken slice som eier ruta. `oppdrag` bruker `ki`, men hvem rendrer forslagsboksene?
- **Risiko:** Story for «nytt oppdrag» og story for «KI-forslag» velger hver sin modell. Den ene lager hel sidelasting, som mister fokus og bryter «resten av skjemaet kan brukes». Den andre lager JSON og innerHTML.
- **Alvorlighet:** kritisk
- **Forslag til spinen:** Ny AD-15 «KI-forslag er den eneste forespørselen uten sidelasting»:
  - `POST /oppdrag/forslag` ligger i `oppdrag/routes.py` og kaller `ki`-servicen. Ruta tar imot `FormData` fra selve skjemaet, så det skjulte CSRF-feltet blir med og AD-5 gjelder uendret. I tillegg settes `Origin`.
  - Svaret er et **HTML-fragment** rendret med samme Jinja-makro som forslagsboksene (autoescape, AD-11 dekker det), eller `message-error`-makroen ved feil, kvote eller tidsavbrudd. Statuskoder: 200 for forslag, 200 med feilfragment for KI-feil og kvote, 401 for utløpt sesjon, 403 for CSRF.
  - `static/js/ki.js` setter fragmentet inn i én fast beholder per felt, styrer «Lager forslag …» (`aria-disabled` + `aria-live="polite"`) og flytter fokus ved «Bruk»/«Ikke bruk». KI-tekst settes aldri inn med `innerHTML` fra JSON.
  - Den globale innloggingssjekken (AD-4) svarer 401 + fragmentet «Du må logge inn igjen.» på forespørsler med header `X-Fragment: 1` i stedet for å sende videre til innlogging. Utfylt innhold blir da stående i nettleseren.
  - **Uten JavaScript** vises ikke «Få forslag» (knappen har `hidden` til `ki.js` har lastet). KI er valgfritt (SM-C1), og manuell utfylling er like rask. Skriv dette som et uttrykkelig unntak fra «alle skjema virker uten JavaScript».
  - Alternativet er en vanlig innsending med `formaction` som rendrer skjemaet på nytt med forslag. Det gir dårligere fokus og opplesning og krever at «Bruk» er innsendingsknapper. Hvis gruppen velger det, må spinen si det i stedet.

### K2 – AD-7 kan ikke gjennomføres som skrevet uten å bryte AD-1, eller uten at hver rute gjør det på sin måte

- **UX-referanse:** EXPERIENCE.md State Patterns, raden «Innlogging utløpt» med [NOTE FOR ARCHITECTURE]; § Åpne punkter → «Utfylt skjema beholdes når innloggingen utløper».
- **Hva motsier eller mangler:** AD-7 sier at serveren «viser samme skjema igjen med verdiene … og innloggingsfelt på siden. Etter innlogging sendes skjemaet videre.» Men AD-4 legger sjekken i `core`, og `core` importerer ingen slice (AD-1). Den globale sjekken kjenner derfor ikke malen til skjemaet. Enten må hver rute gjøre dette selv, og det var akkurat det AD-7 skulle hindre, eller så trengs en generisk mekanisme som spinen ikke beskriver. Spinen sier heller ikke:
  - hvordan «sendes videre» skjer. En 303-redirect mister innholdet i POST-forespørselen.
  - hva som skjer med to steg, med KI-`fetch` (se K1) og med GET-sider som har `?neste=`
  - om `neste` bare kan være en intern sti (åpen redirect)
- **Alvorlighet:** kritisk
- **Forslag til spinen:** Skriv mekanismen inn i AD-7:
  1. Kommer en POST med utløpt sesjon, rendrer `core` én generisk side, «Du må logge inn igjen.». Siden har alle innsendte felt (unntatt passord og CSRF) som skjulte felt, i tillegg felt for e-post og passord, og en knapp som sender til **samme URL**.
  2. Mellomvaren i `core` ser at innsendingen har innloggingsfelt. Den logger inn (med AD-4-telling og AD-6), oppretter sesjon og slipper forespørselen videre til ruta. Ruta behandler skjemaet som vanlig, så valideringsfeil viser skjemaet med verdiene.
  3. GET uten sesjon gir 303 til `/logg-inn?neste=<sti>`. `neste` godtas bare hvis den begynner med `/` og ikke med `//`.
  4. Forespørsler med `X-Fragment` får 401 (K1).
  5. Testen for FR-3 dekker alle tre.

  Da beholder AD-7 «én mekanisme», og UX-kravet «beholdes og vises igjen, eller brukeren får beskjed før det går tapt» er oppfylt.

---

## Høye

### H1 – Spinen sier noe UX motsier: «ikke noe eget frontend-lag» og «alle skjema virker uten JavaScript»

- **UX-referanse:** `{components.dialog}` (native `showModal()`); § Sending; § To steg i nytt oppdrag; § Skjemafelt (teller som leses opp ved grensen, poststed ved siden av gyldig postnummer, «Vis passord» med `aria-pressed`, «Beløp i kr» vises bare når «Beløp» er valgt, forhåndsvisning som oppdateres); § KI-forslag (deaktivert under 10 tegn); § Fokus og opplesning («Velg et annet postnummer» markerer innholdet).
- **Hva motsier:** Mange av disse går ikke uten JavaScript. Spinen nevner bare JavaScript for «fokus og `<dialog>`». Uten en liste over hva som er klientatferd, hvilken fil som eier det og hva som vises uten JavaScript, vil hver story legge til sitt eget skript, eller skrive regler på nytt i JavaScript.
- **Alvorlighet:** høy
- **Forslag til spinen:** Erstatt raden «Maler og frontend» med en liten tabell «Klientatferd (progressiv forbedring)». Hver rad har atferd, JS-fil og hva som skjer uten JavaScript:
  - `fokus.js`: fokus etter sidelasting (H3)
  - `dialog.js`: bekreftelser (H5). Uten JS: bekreftelsesside.
  - `sending.js`: H4. Uten JS: serveren avviser duplikater.
  - `steg.js`: H2. Uten JS: én skjerm.
  - `ki.js`: K1. Uten JS: skjult.
  - `skjema.js`: teller, poststed, «Vis passord», forhåndsvisning (M3, M4, M5). Uten JS: telleren mangler, men serverfeilen gir antallet; poststed vises etter innsending.
  - Beløp-feltet: ren CSS med `:has(:checked)`, ikke JavaScript.

  Regel: JavaScript skal aldri inneholde regler fra PRD-en, utover det som bare viser noe (lengde for telleren, 10 tegn for KI-knappen). Serveren avgjør alltid. Ingen bygg-steg og ingen npm.

### H2 – To steg på mobil er bestemt av skjermbredden, som serveren ikke kjenner

- **UX-referanse:** EXPERIENCE.md § To steg i nytt oppdrag; § Meldinger → Feiloppsummering («I to steg lister oppsummeringen feil fra begge steg, og appen viser steget med første feil»); § Åpne punkter → «To steg på mobil som ett skjema med to deler, så feil fra serveren kan vises i riktig steg»; Accessibility Floor → Sidetitler (ulik `<title>` per steg og ulik `h1`).
- **Hva mangler:** Spinen tar ikke stilling. To steg under 768 px og én skjerm fra 768 px kan ikke avgjøres på serveren. Da må `h1`, `<title>` og «Neste»/«Tilbake til steg 1» byttes på klienten. UX sier at «Neste» sjekker feltene i steg 1 og viser feiloppsummeringen, uten at det står om det skjer med en forespørsel til serveren eller på klienten. Skjer det på klienten, dupliseres reglene i JavaScript (i strid med NFR-5/10 og H1).
- **Alvorlighet:** høy
- **Forslag til spinen:** Legg til en regel for nytt oppdrag:
  - Ett `<form>` med to `<section>`. Serveren rendrer alltid begge, med `h1` «Nytt oppdrag» og `h2` per del.
  - `steg.js` gjør det om til to steg bare under 768 px (`matchMedia`). Skriptet bytter `h1`-tekst og `document.title` og flytter fokus til `h1`.
  - «Neste» sjekker bare at feltene i steg 1 ikke er tomme, med feiltekstene fra Voice and Tone, som serveren legger i `data-`-attributter. Alle andre regler sjekkes ved «Publiser».
  - Ved feil fra serveren merker hvert felt hvilket steg det hører til (`data-steg`), og `steg.js` viser steget med første feil.
  - Uten JavaScript: én skjerm på alle bredder.
  - T1 kjører begge visningene med fast viewport.

### H3 – Ingen felles mekanisme for fokus etter sidelasting

- **UX-referanse:** § Fokus og opplesning: kvittering, feiloppsummering, feilmelding med sidelasting, valgt kategori ([NOTE FOR ARCHITECTURE]: «settes fokus på valgt lenke ved sidelasting (f.eks. med `autofocus` eller et lite skript)»), «Endre tidspunkt» → «Dato», «Velg et annet postnummer» → feltet med innholdet markert, «Vis alle kategorier» → «Alle»; § Ikke tillatt (ingen myk rulling ved `prefers-reduced-motion`); § Åpne punkter → «hvordan fokus settes på kvittering, feiloppsummering og valgt kategori etter sidelasting».
- **Hva mangler:** Spinen nevner bare «vanilla-JS for fokus». Hvis det ikke står hvilket element som får fokus, hvem som bestemmer det og hva som går foran, vil hver story løse det på sin måte (`autofocus` her, eget skript der, og to elementer som kjemper om fokus).
- **Alvorlighet:** høy
- **Forslag til spinen:** Ny konvensjon «Fokus etter sidelasting»:
  - Ruta (eller render-hjelperen, se H6) setter **høyst ett** fokusmål per side.
  - Rekkefølge: feiloppsummering > feilmelding (konflikt, uventet feil) > kvittering > sidens eget mål (valgt kategori, «Dato», postnummerfeltet med `select()`) > ingenting.
  - Makroen skriver `autofocus` på målet (virker uten JavaScript, også på `tabindex="-1"`-elementer). `fokus.js` gjør bare det `autofocus` ikke kan: `select()` og å vise riktig steg.
  - `scroll-behavior: smooth` brukes bare innenfor `prefers-reduced-motion: no-preference`.
  - En Playwright-test sjekker `document.activeElement` for hver rad i tabellen.

### H4 – Sending-tilstand og dobbel innsending utenfor statusendringer

- **UX-referanse:** § Sending («Alle knapper som sender noe, er deaktivert … også med Enter i et felt … Serveren avviser likevel den andre»); `{components.button-primary}`; `{components.button-disabled}` (`aria-disabled`, ikke `disabled`); UJ-1 «trykker «Ja, velg Amir» to ganger».
- **Hva mangler:** AD-2 stopper doble **statusendringer**. Men dobbel «Publiser» gir to oppdrag, dobbel «Meld interesse» to interesser, og dobbel «Send» to tilbakemeldinger. Ingenting i spinen hindrer det på serveren. Klientdelen (deaktivere knapper, stoppe Enter) har ingen eier. I tillegg blir knappene stående deaktivert når brukeren går tilbake i nettleseren (bfcache).
- **Alvorlighet:** høy
- **Forslag til spinen:**
  1. Unik nøkkel i databasen på `interesse(oppdrag_id, bruker_id)` og `tilbakemelding(oppdrag_id, giver_id)`. Brudd gir `RegelBrudd` med en vennlig tekst.
  2. Skjemaet for nytt oppdrag har et skjult engangsfelt `skjema_id` (UUID), lagret med unik nøkkel på `oppdrag`. Ved duplikat sendes brukeren til det oppdraget som allerede er opprettet.
  3. Én global `sending.js` setter `aria-disabled="true"` på knappen som sendte, og stopper nye `submit` til siden er byttet. Den nullstiller ved `pageshow`.
  4. Testene for NFR-5 dekker dobbel innsending for hver POST som oppretter noe.

### H5 – Native `<dialog>`: hva skjer uten JavaScript, én felles makro og hva skjer etterpå

- **UX-referanse:** `{components.dialog}` (`showModal()`, Tab holdes inne, Esc angrer, én om gangen, innholdet ruller); § Bekreftelser (fem dialoger); § Fokus og opplesning (fokus på spørsmålet når dialogen åpnes; tilbake til knappen når den lukkes, eller til kvitteringen hvis knappen er borte); State Patterns, raden «Samtidighetskonflikt» («Dialogen lukkes»); Foundation [NOTE FOR ARCHITECTURE].
- **Hva mangler:** `showModal()` krever JavaScript, men spinen sier at alle skjema virker uten. Det står ikke hva «Velg Amir» gjør uten JavaScript. Spinen nevner heller ikke at de fem dialogene skal komme fra **én** makro, og den sier ikke hvordan bekreftelsen sendes (POST med sidelasting, slik at AD-2-konflikten og kvitteringen følger de vanlige reglene).
- **Alvorlighet:** høy
- **Forslag til spinen:**
  - Utløseren er en lenke til en GET-bekreftelsesside (`/oppdrag/{id}/velg/{bruker_id}`). Siden har samme tekst og et POST-skjema, og fungerer som reserve uten JavaScript.
  - `dialog.js` fanger klikket og åpner `<dialog>`-markupen som allerede ligger på siden. Den kommer fra makroen `bekreft_dialog(id, spørsmål, gjelder, bekreft, angre, action)`.
  - Bekreft er en vanlig POST, som gir PRG og kvittering med fokus (H3), eller konfliktmelding med fokus. Angre lukker dialogen og gir fokus tilbake til utløseren.
  - Ingen andre handlinger enn de fem i § Bekreftelser bruker dialogen.

### H6 – Ingen felles render-funksjon: antallet i menyen, `aria-current`, `<title>`, kvittering og CSRF på hver side

- **UX-referanse:** Information Architecture: antall ved «Mine oppdrag» regnes ut ved hver sidelasting, vises ikke ved 0, og skjermleseren leser «Mine oppdrag, 2 trenger handling». Tabellen «Aktivt menyvalg på undersider» (`"page"` eller `"true"`); `{components.tabs}` (bare én `"page"`); Accessibility Floor → Sidetitler («Side – Nabolagshelten», «Feil: » foran); Foundation (topplinje uten meny når brukeren ikke er innlogget).
- **Hva mangler:**
  - `base.html` ligger i `core`. Antallet krever regelen for merker i `mine_oppdrag` og `oppdrag` (AD-3), og `core` kan ikke importere dem (AD-1). Spinen sier ikke hvordan antallet kommer inn på hver side.
  - Det står ikke hvem som bestemmer aktivt menyvalg, `aria-current`-verdien og «Feil: » i tittelen.
  - Hver rute kan dermed sende inn ulik kontekst, og noen sider vil mangle antallet eller ha to `aria-current="page"`.
- **Alvorlighet:** høy
- **Forslag til spinen:** Ny konvensjon «Rendring»:
  - Alle sider rendres med `core.render(request, mal, *, tittel, aktiv_meny, aktiv_meny_er_side, fokus=None, **ctx)`.
  - Funksjonen legger på innlogget bruker, CSRF-token, kvittering fra cookien, «Feil: » når det finnes feil, og `nav_antall`.
  - `nav_antall` hentes gjennom en krok som `lag_app()` registrerer ved oppstart (`core.registrer_nav_antall(mine_oppdrag.service.antall_trenger_handling)`). Slik importerer `core` fortsatt ingen slice.
  - Legg også i spinen at «Velg hjelper» (UX-beslutning 2026-11-07) er et av merkene i AD-3 og teller i antallet. Det er sendt til PRD, men koden trenger én definisjon.

### H7 – Tolkning av dato og klokkeslett fra tekstfelt har ingen eier og ingen format-regel

- **UX-referanse:** § Skjemafelt → «Når?»: alltid norsk format; godtar skråstrek, bindestrek, mellomrom og tosifret år; klokkeslett uten kolon («7», «0700», «7.00»). Voice and Tone § Feiltekster ved felt: ulik tekst for «feil format», «finnes ikke», «passert» og «over 12 mnd», og for fødselsdato («Sjekk fødselsdatoen.», minst 18 år). Voice and Tone § Formater: visning som «I morgen kl. 07:00» eller «Lørdag 14. nov. kl. 12:00», år bare når det ikke er i år. Åpne punkter → «Tolkning av dato og klokkeslett fra tekstfelt … i norsk tid» [NOTE].
- **Hva mangler:** AD-9 dekker tidssone og sommertid, men ikke **tolkning** og **visning**. Fødselsdato (`identity`) og oppdragstid (`oppdrag`) vil få hver sin tolker. Det står heller ikke hvordan tosifret år tolkes: «26» betyr 2026 for et oppdrag, men «54» må bety 1954 for fødselsdato. Formatet for visning brukes i oversikten, detaljer, Mine oppdrag og profil, altså i flere slices.
- **Alvorlighet:** høy
- **Forslag til spinen:** Utvid AD-9:
  - `core/tid.py` eier `tolk_dato(tekst, *, århundre="fram"|"bak")`, `tolk_klokkeslett(tekst)`, `til_utc(dato, kl)` og Jinja-filtrene `tidspunkt` («I morgen kl. 07:00») og `dato_kort`. Alle tar «nå» fra klokka i `core`.
  - Funksjonene kaster `RegelBrudd` med tekstene fra EXPERIENCE.md.
  - Regel for tosifret år: oppdrag → 20xx; fødselsdato → det året som gir alder mellom 0 og 120.
  - Én tabelltest med alle skrivemåtene fra UX.

### H8 – FastAPI/Pydantic gir engelske JSON-feil på skjema, i strid med UX-feilmønsteret

- **UX-referanse:** § Skjemafelt (`novalidate`, appens egne tekster); § Meldinger → Feiloppsummering; Voice and Tone § Feiltekster ved felt; State Patterns, raden «Valideringsfeil».
- **Hva motsier:** Konvensjonen «Validering» sier at skjema leses i routes til Pydantic-modeller. Er feltene typet (`date`, `int`, `EmailStr`, `constr`), svarer FastAPI med `RequestValidationError`, altså **JSON 422 på engelsk**, før ruta kjører. Da får brukeren hverken feiloppsummering, beholdte verdier eller norske tekster. Ulike stories vil type feltene ulikt.
- **Alvorlighet:** høy
- **Forslag til spinen:** Presiser konvensjonen «Validering»:
  - Alle felt i skjemamodellene er `str | None` (avkrysning og radio som `str | None`). Ingen Pydantic-begrensninger brukes på felt brukeren skriver.
  - All tolkning og alle regler ligger i service og `core/tid.py`, med tekstene fra EXPERIENCE.md.
  - En global handler for `RequestValidationError` viser den vennlige feilsiden og logger hendelsen, siden det i så fall er en programmeringsfeil.
  - Samle `RegelBrudd` per felt: servicen samler alle feltfeil (`RegelBrudd` med en liste), så oppsummeringen «Skjemaet har 2 feil» kan vise alle samtidig, ikke bare den første. Dagens `RegelBrudd(melding, felt=None)` gir bare én feil om gangen.

---

## Middels

### M1 – Regler for `aria-live` og `role` er ikke en konvensjon

- **UX-referanse:** § Fokus og opplesning, innledningen: «Etter sidelasting gir fokus opplesningen; `aria-live`, `role="status"` og `role="alert"` brukes bare for endringer uten sidelasting. Feiloppsummeringen har aldri `role="alert"`.» Se også radene for KI og konflikt.
- **Hva mangler:** Spinen har ingenting om dette. Det er lett å legge `role="alert"` på feilmakroen «for sikkerhets skyld», og da avbryter to kunngjøringer hverandre.
- **Alvorlighet:** middels
- **Forslag til spinen:** Én linje i konvensjonen «Rendring»: makroene `kvittering` og `feilmelding` rendres **uten** `role` når de kommer fra serveren ved sidelasting. `role="status"` eller `role="alert"` brukes bare på fragmenter som settes inn av JavaScript (K1). Feiloppsummeringen har aldri `role`.

### M2 – Testgulvet T1–T6: spinen sier noe annet enn UX, og det mangler oppsett for e2e

- **UX-referanse:** Accessibility Floor → «T1 kjøres automatisk med axe, T2–T6 manuelt; alle seks dokumenteres som tester». Listen over sider og tilstander i T1 (KI-forslag vist, KI-feil, alle fem dialoger, slettet bruker, tom fane, mobil og nettbrett). T4 (320 px uten vannrett rulling, 200 % zoom). DESIGN.md § Layout & Spacing (320 px reflow, testbredder 360, 768 og 1280).
- **Hva motsier eller mangler:**
  - Spinen sier «Playwright med axe for T1–T6». Det kan leses som at alt automatiseres, men T6 er en brukertest, og T2, T3 og T5 er manuelle.
  - For T1 må e2e-testene kunne nå bestemte tilstander: KI-feil på bestilling, «passert» tidspunkt og en slettet bruker. Det krever en klokke som kan styres og en testdobbel for KI som kan feile, også når appen kjører i en egen prosess under Playwright. Spinen sier ikke hvordan.
  - CI-diagrammet viser bare pytest. Det står ikke om Playwright kjører i CI.
- **Alvorlighet:** middels
- **Forslag til spinen:** Endre «Tester»-raden:
  - «T1 automatisert: axe i Playwright for sidene og tilstandene i lista, ved 360 og 1280 px. I tillegg en automatisk sjekk av vannrett rulling (`scrollWidth <= innerWidth`) ved 320 px på de samme sidene (støtte for T4). T2–T6 er manuelle protokoller i `docs/tester/` med resultat per dato.»
  - Med `APP_ENV=test` kan e2e-oppsettet sette klokka (`TEST_NA`) og KI-utgaven (`KI_TESTMODUS=ok|feil|tidsavbrudd|kvote`) fra miljøvariabler eller seed. Dette skal aldri virke i produksjon (AD-14).
  - Legg Playwright-jobben inn i CI-diagrammet.

### M3 – Poststed mens man skriver krever oppslag, og AD-4 blokkerer det på registreringssiden

- **UX-referanse:** Information Architecture, Registrering («poststed vises når nummeret er gyldig»); § Skjemafelt («Postnummer viser poststed ved siden av når det er gyldig»); postnummerfilteret («feltet «Postnummer» med poststed ved siden av»).
- **Hva mangler:** Skal poststedet vises før innsending, trengs enten et endepunkt (`GET /postnummer/{nr}`) eller hele lista som statisk fil (ca. 5100 rader). Registrering skjer uten innlogging, og unntakslista i AD-4 har bare registrering, innlogging og `/static`. Spinen har heller ikke valgt hva som gjelder uten JavaScript.
- **Alvorlighet:** middels
- **Forslag til spinen:** Velg én løsning:
  - (a) `core` genererer `static/postnumre.json` ved bygging eller seeding fra `data/postnumre.tsv`, og `skjema.js` slår opp lokalt. Ingen ny rute og ingen endring i AD-4. Anbefalt.
  - (b) Et `GET`-endepunkt i `core` som legges inn i unntakslista i AD-4.

  Uten JavaScript vises poststedet etter innsending, og serveren er alltid fasit.

### M4 – Telleren på klienten og lengdesjekken på serveren teller ulikt

- **UX-referanse:** § Skjemafelt («37 av 500 tegn», leses opp ved grensen); Voice and Tone («Beskrivelsen kan ha høyst 1000 tegn. Nå har den 1046.»); AD-10 (trim + NFC før lengdesjekk).
- **Hva mangler:** JavaScript `value.length` teller UTF-16-enheter (en emoji teller 2, og en å skrevet som to tegn teller 2), og `maxlength` gjør det samme. Python `len()` etter NFC teller kodepunkter. Telleren kan da vise 1000, mens serveren sier 1001.
- **Alvorlighet:** middels
- **Forslag til spinen:** Utvid AD-10 med én linje:
  - Klienten teller `[...verdi.normalize('NFC').trim()].length`, og serveren `len(nfc(trim(v)))`.
  - `maxlength` brukes ikke på felt med teller, fordi feilen med antall tegn skal komme fra serveren.
  - Grensene sendes til malen fra konstanten i slicen (`data-maks`), så de ikke skrives to steder.

### M5 – Forhåndsvisningen på klienten gir to steder som formaterer tid og beløp

- **UX-referanse:** § Skjemafelt → Forhåndsvisning (oppdateres når feltene endres, tomme felt vises som «–», kortet slik det blir i oversikten); Voice and Tone § Formater («I morgen kl. 07:00», «1 000 kr», «Uten betaling»).
- **Hva mangler:** En forhåndsvisning som oppdateres mens man skriver, krever at JavaScript formaterer tid og beløp likt med Jinja-filtrene (H7). Ellers får brukeren to ulike formater. Spinen sier ingenting.
- **Alvorlighet:** middels
- **Forslag til spinen:** Velg én løsning:
  - (a) `skjema.js` har en liten formaterer for tid og beløp, med en delt testfil med eksempler (samme input og forventet tekst) som både pytest og en JS-test kjører.
  - (b) Enklere: forhåndsvisningen viser datoen og klokkeslettet slik brukeren skrev dem. Kortet er rendret av Jinja-makroen `oppdragskort(…, forhandsvisning=True)` med `data-felt`-plasser, og bare beløpet formateres på klienten.

  Uten JavaScript viser forhåndsvisningen verdiene fra siste innsending, eller «–».

### M6 – Malen trenger å vite om KI kjører som mock eller ekte tjeneste

- **UX-referanse:** Voice and Tone: «KI ved knappen (ekte tjeneste)» og «KI ved knappen (mock-modus)» har ulik tekst (FR-23, FR-26).
- **Hva mangler:** AD-12 velger utgave ved oppstart, men grensesnittet sier ikke at utgaven kan spørres om den sender tekst ut. Stories vil da sjekke `OPENROUTER_API_KEY` direkte i malen eller ruta.
- **Alvorlighet:** middels
- **Forslag til spinen:** Legg til i AD-12: grensesnittet har `sender_eksternt() -> bool`, og `oppdrag` sender verdien til malen. Ingen annen kode leser KI-konfigurasjonen.

---

## Lave

### L1 – Lukk [NOTE FOR ARCHITECTURE] om «Laster …»

- **UX-referanse:** State Patterns, raden «Laster»; § Fokus og opplesning, raden «Klienten henter data selv».
- **Mangler:** Spinen sier ikke uttrykkelig at klienten ikke henter data selv.
- **Forslag:** Én linje: «Klienten henter ikke data selv, bortsett fra KI-forslag (AD-15). Derfor finnes ingen «Laster …»-tilstander; KI har sin egen tekst, «Lager forslag …».»

### L2 – Hvordan konflikten vises etter POST fra en dialog

- **UX-referanse:** State Patterns, raden «Samtidighetskonflikt» (melding + knappen «Last siden på nytt», dialogen lukkes); § Meldinger.
- **Mangler:** AD-2 gir teksten, men sier ikke om svaret er en redirect med feil-cookie eller den samme siden med 409/422. Det står heller ikke at knappen «Last siden på nytt» skal være en GET-lenke til samme side.
- **Forslag:** Konvensjonen «Feil»: konflikt fra AD-2 gir PRG til detaljsiden med en feilmelding i samme kortlivede cookie som kvitteringer (type `feil`). Meldingen får fokus (H3), og knappen er en lenke til den samme URL-en.

### L3 – Tilstanden i filtrene ligger i URL-en

- **UX-referanse:** § Filtrene i oversikten (kategori som lenker `?kategori=hage`; postnummer med «Vis»; ugyldig postnummer → feil, og «lista står uendret»); `{components.tabs}` (`?fane=hjelper`).
- **Mangler:** Kategorilenkene må beholde postnummeret, og «Vis» må beholde kategorien. For at «lista står uendret» skal virke, må serveren vite hvilket postnummer som sist var gyldig. Det står ikke hvor det kommer fra.
- **Forslag:** Konvensjon: filtrene er GET-parametre (`postnummer`, `kategori`, `fane`), og lenkene bygges med én hjelper som beholder de andre parametrene. Postnummerskjemaet har det sist gyldige nummeret som skjult felt.

### L4 – «Tilbake» går til forrige side i appen eller til oversikten

- **UX-referanse:** `{components.button-text}` («Tilbake» går til forrige side i appen, eller til oversikten hvis brukeren ikke kom fra en side i appen).
- **Mangler:** Hvis ingen mekanisme er valgt, blir det `history.back()` i én story og `Referer` i en annen.
- **Forslag:** `render` regner ut `tilbake_url`: `Referer` hvis den er på samme nettsted og ikke er siden selv, ellers `/`. `Referrer-Policy: same-origin`.

### L5 – Tidsavbrudd for KI på 10 s og maks kjøretid på Vercel

- **UX-referanse:** State Patterns, raden «KI-feil / tidsavbrudd 10 s», med egen tekst.
- **Mangler:** Hvis funksjonen på Vercel har en grense på omtrent 10 s, stopper Vercel forespørselen før `httpx` får tidsavbruddet. Da får brukeren den generelle feilsiden i stedet for KI-teksten.
- **Forslag:** Sjekk standard maks kjøretid for prosjektet på Vercel, og sett `maxDuration` (for eksempel 30 s) i `vercel.json`. Det kan gjøres i Structural Seed.

---

## Det som har landet (til orientering)

- Server-rendret eller klientrendret (Åpne punkter): valgt server-rendret (paradigmet, memlog valg 2).
- Native `<dialog>`, vanlig HTML og CSS, ingen bibliotek (Foundation [NOTE]): konvensjonen «Maler og frontend». Mangler detaljene i H5.
- Utfylt skjema når innloggingen utløper (NOTE): AD-7. Mekanismen mangler, se K2.
- Sommertid, tegnsett, CSRF og postnummerkilde (fra PRD §8): AD-9, AD-10, AD-5 og memlog valg 10.
- Faner med egen adresse og antallet regnet ut per sidelasting: følger av AD-3 og server-rendring. Hvordan antallet kommer inn på siden, se H6.
- Fritekst som ren tekst (FR-25, NFR-12): AD-11. Mangler for KI-tekst satt inn med JavaScript, se K1.
- Komponentene som Jinja-makroer: konvensjonen finnes, og navnene er utsatt til «én story for felles maler». Det er greit, men H3, H5, H6 og M1 bør stå i spinen som krav makroene må oppfylle, så den første story-en ikke må finne dem opp selv.

Ikke tatt med: rene visuelle detaljer (farger, mål, ikoner, bunnmenyen som fast eller i sideflyten, `forced-colors`). Det eier CSS og koden, etter DESIGN.md.
