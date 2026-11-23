# Kvalitetsreview av PRD – Nabolagshelten (v1.2, endrede deler)

Vurdert: `prd.md` versjon 1.2 (2026-11-23), mot rubrikken i `.claude/skills/bmad-prd/assets/prd-validation-checklist.md`. Bare delene som er endret i v1.2 er vurdert: topptabellen, FR-5, FR-18, NFR-7, NFR-11, SM-5, §8, nye og endrede rader i §9.2 og endringsloggen for 1.2. I tillegg er det sjekket om endringene bryter med resten av PRD-en (§3, §4.0, FR-4, FR-6, FR-8, FR-13–FR-15, FR-17, FR-19, FR-20, UJ-1, UJ-2, §9.1). Kildene for endringene er EXPERIENCE.md (Information Architecture, State Patterns § Mine oppdrag, Accessibility Floor med T1–T6, Åpne punkter) og ARCHITECTURE-SPINE.md (AD-1, AD-3, AD-5, AD-9, AD-10). PRD-en går foran UX; der de er uenige, er det UX som må rettes.

## Samlet vurdering

Endringene i v1.2 er godt forankret. Hver av dem kan spores til et åpent punkt i EXPERIENCE.md eller arkitekturspinen, alle kryssreferansene stemmer (AD-1, AD-5, AD-9, AD-10, T1–T6, `#accessibility-floor`, FR-numrene), og gruppene i FR-18 dekker alle oppdrag nøyaktig én gang, fordi de er definert som «med merke» og «uten merke». Svakheten er at fordelingen ikke blir bedre enn vilkårene for merkene, og merket «Oppdraget er endret etter at du meldte interesse» har verken statusvilkår eller sluttpunkt. Dermed havner oppdrag brukeren ikke kan gjøre noe med, under «Trenger handling» og teller i menyen for alltid. Det bør rettes sammen med to mindre presiseringer (begrepet «merke» og sommertid i FR-5) før det skrives stories for FR-18 og FR-5.

## Klar for beslutninger – tilstrekkelig

Endringene står som beslutninger, og overstyringen av v1.1 er sagt rett ut: «hjelper-fanen grupperes etter brukerens egen situasjon, ikke oppdragets status (endrer v1.1)» (endringsloggen 1.2). §9.2 begrunner tallet i menyen med tesen om at appen ikke har varsler («Uten varsler (§6.2) må brukeren se at noe venter»). FR-5 skiller godt mellom produktkravet (norsk tid) og teknologivalget (AD-9). Én avveining er ikke tatt med: tallet beregnes uten å lagre hva brukeren har sett («appen lagrer ikke hva brukeren har sett», FR-18), så et merke blir stående til tilstanden endrer seg. Det er ikke sikkert at tilstanden endrer seg.

### Funn

- **medium** Tallet i menyen kan bli stående uten at brukeren kan gjøre noe (FR-18, merket «Hjelperen trakk seg») – merket «forsvinner når en ny hjelper er valgt, eller oppdraget avbrytes». Har ingen andre meldt interesse, kan ikke Kari velge noen. Da er avbryting det eneste som fjerner merket, og «Mine oppdrag 1» står i menyen helt til noen melder interesse eller tidspunktet passerer. Det svekker tallet som signal, og det er Kari (72, «gir opp hvis noe er uoversiktlig») som rammes. *Fix:* Ta et valg og skriv det inn. Enten sier FR-18 rett ut at merket står til oppdraget har ny hjelper eller er avbrutt, også når ingen andre er interessert (avveining mot det å lagre hva brukeren har sett). Eller så teller «Hjelperen trakk seg» bare i menyen når oppdraget også har «Velg hjelper» eller «Tidspunktet er passert», og ellers står det som et merke under «Pågår». Da må definisjonen av «Trenger handling» endres tilsvarende.

## Innhold fremfor pynt – sterk

Det er ingen pynt i endringene. NFR-7 har fått en målbar grense med WCAG-henvisning («flyter om ved 320 CSS px bredde (400 % zoom på 1280 px) uten vannrett rulling (WCAG 1.4.10)»), og regnestykket stemmer. SM-5 er utvidet med konkrete tilstander, ikke med adjektiver. Merket «Velg hjelper» har et presist vilkår (status Åpen, ikke passert, minst én interessert) og et sluttpunkt.

## Strategisk sammenheng – sterk

Tallet i menyen, grupperingen og det nye merket støtter samme tese som resten av PRD-en: tydelig status uten varsler (§1, §6.2). At hjelper-fanen grupperes etter brukerens egen situasjon, følger av at «Trenger handling» skal bety at *brukeren* har noe å gjøre. Det er riktig ut fra tesen. Det er bare vilkårene for merkene som ikke helt følger opp (se neste del).

## Tydelig når det er ferdig – tilstrekkelig

De fleste nye konsekvensene kan testes slik de står. Tabellen med grupper i FR-18 er entydig per fane, og «en gruppe uten oppdrag vises ikke», «et oppdrag med flere merker telles én gang», «tallet vises ikke når det er 0» og skjermleserteksten kan alle bli akseptansekriterier. Alle situasjonene og merkene i begge faner havner i nøyaktig én gruppe. Jeg har sjekket kanttilfellene: utgått oppdrag med og uten interesserte, «Hjelperen trakk seg» sammen med «Velg hjelper» eller «Tidspunktet er passert», at merket forsvinner når status blir Avbrutt eller Hjelper valgt igjen, og slettet konto i alle radene i FR-4 (valgt hjelper sletter: Åpen og «Hjelperen trakk seg»; oppdragsgiver sletter: Avbrutt for hjelperen; motpart slettet på Utført: «Gi tilbakemelding» faller bort og oppdraget går til «Ferdige»). Avbrutte oppdrag kan aldri ha merke, så «Ferdige» i fanen for egne oppdrag er riktig. To ting gjør likevel at en utvikler som følger teksten bokstavelig, bygger feil eller ikke kan teste.

### Funn

- **high** «Oppdraget er endret etter at du meldte interesse» mangler statusvilkår og sluttpunkt (FR-18, merkelista; FR-6) – merket gjelder «hos den interesserte (FR-6)», uten flere vilkår. Interessen blir liggende når en annen blir valgt («Ikke valgt»), når oppdraget blir utgått eller avbrutt, og når brukeren selv blir valgt hjelper (interessen slettes først ved FR-17, og ordlisten sier at valgt hjelper fortsatt er «den interesserte»). Merket gjelder dermed også for «Ikke valgt», «Avbrutt», «Tidspunktet er passert», «Du er valgt» og «Utført». Hver slik rad havner under «Trenger handling» og teller i menyen for alltid. Det strider mot FR-18 selv: «Ikke valgt» skal stå under «Ferdige», «fordi brukeren ikke har noe mer å gjøre der». Den eneste handlingen merket peker på, er å trekke interessen (FR-13), og det er bare lov «mens status er Åpen og tidspunktet ikke er passert». *Fix:* «Oppdraget er endret etter at du meldte interesse» hos den interesserte når situasjonen er «Venter på svar» (FR-6, FR-13). I andre situasjoner vises det ikke. Rett også FR-6 («Den interesserte ser …») slik at den viser til vilkåret i FR-18.
- **medium** «Også ved overgang til og fra sommertid» er ikke en betingelse som kan sjekkes (FR-5) – setningen sier at noe skal virke ved sommertid, men ikke hva som skal skje. Hva brukeren opplever, er et produktvalg og hører hjemme i PRD-en, selv om lagringen hører hjemme i arkitekturen. AD-9 har tatt valget («Klokkeslett som ikke finnes … avvises», «tolkes som det første (`fold=0`)»), men en regel om hva som er gyldig verdi står nå bare i arkitekturen. Den står ikke i lista over gyldige verdier i FR-5. *Fix:* Legg til i FR-5: «Et klokkeslett som ikke finnes den dagen klokka stilles fram, avvises med melding ved feltet. Et klokkeslett som finnes to ganger når klokka stilles tilbake, tolkes som det første. Et oppdrag vises med samme dato og klokkeslett før og etter skiftet.» Den siste setningen er den som gjør «vises i norsk tid» testbart. FR-5 oppfyller ellers den opprinnelige hensikten: brukeren angir og ser norsk tid, og «Hvordan tid lagres, avgjøres i arkitekturen (AD-9)» lekker ikke teknologi.
- **low** Ingen regel for like tidspunkt i gruppene (FR-18, kolonnen «Rekkefølge») – FR-10 sorterer like tidspunkt etter når oppdraget ble lagt ut. FR-18 har ingen slik regel, så tester av rekkefølgen kan gi ulikt resultat fra gang til gang. *Fix:* «Like tidspunkt sorteres som i FR-10.»
- **low** «Testes ved» i NFR-11 dekker ikke tallet (NFR-11) – manuell gjennomgang og axe sjekker ikke regnestykket (0 skjules, flere merker telles én gang, begge fanene til sammen). Tallet dekkes av testene for FR-18, men NFR-11 viser ikke dit. *Fix:* Legg til «og de automatiske testene for tallet i FR-18» i «Testes ved».

## Ærlig om omfang – sterk

§8 lukker punktene ærlig. Hvert punkt er knyttet til der det ble løst, og lista blir stående «for sporingen». Jeg har sjekket at alle UX-punktene i §8 finnes i EXPERIENCE.md § Endringer fra skissene (nr. 1, 2, 3, 4, 6, 7 og 9) og at alle arkitekturpunktene stemmer med AD-ene som er oppgitt. Det er ikke lagt til nye antakelser, og «Ingen antakelser står åpne» i §9.2 holder for de endrede delene.

### Funn

- **low** Overskriften i §8 er utdatert (§8) – «Åpne punkter til neste fase» står over en liste der alt er løst. *Fix:* «8. Punkter til neste fase (løst i v1.2)», eller la overskriften stå og flytt setningen om at alt er løst opp som første linje. Den står der allerede, så den enkleste løsningen er å endre overskriften.

## Brukbar for neste steg – tilstrekkelig

Kryssreferansene stemmer: lenkene i topptabellen og i NFR-7 og SM-5 peker på riktige filer, ankeret `#accessibility-floor` stemmer med overskriften «## Accessibility Floor», T1–T6 er riktig koblet til innholdet (axe, tastatur, skjermleser, bredder og zoom, kontrast og farge, brukertesten i SM-4), og AD-1, AD-5, AD-9 og AD-10 er de riktige beslutningene. AD-3 i arkitekturen nevner allerede «Velg hjelper» og tallet i menyen, så arkitekturen og v1.2 stemmer overens. To ting gjør det vanskeligere å hente krav ut av PRD-en: et begrep som nå bærer mye, mangler i ordlisten, og EXPERIENCE.md må oppdateres på noen punkter.

### Funn

- **medium** «Merke» er ikke definert, men avgjør nå gruppen og tallet (§3, FR-18, UJ-1, UJ-2) – «Trenger handling» er definert som «Oppdrag med minst ett merke». Ordlisten har ikke «merke», og UJ-2 bruker ordet om situasjoner: «merket «Du er valgt»», «merket «Ikke valgt»», «merket «Du trakk deg»». Den som leser UJ-2 bokstavelig, legger «Ikke valgt» under «Trenger handling». I tillegg er «Tidspunktet er passert» både et merke (hos oppdragsgiveren) og en situasjon (hos hjelperen), med samme tekst, men i hver sin gruppe. *Fix:* Legg inn i §3: «**Merke** – en tekst ved et oppdrag under «Mine oppdrag» som betyr at brukeren bør gjøre noe. Merkene og vilkårene står i FR-18. Ikke det samme som brukerens situasjon i «Oppdrag jeg hjelper med».» Endre UJ-2 til «står som «Du er valgt»» og så videre. Si i FR-18 at situasjonen «Tidspunktet er passert» ikke er et merke.
- **low** EXPERIENCE.md må oppdateres etter v1.2 (EXPERIENCE.md, State Patterns § Mine oppdrag, Accessibility Floor, Åpne punkter, linje 16). PRD-en går foran, men UX-dokumentet er nå utdatert på disse punktene:
  - «Ferdige» i hjelper-fanen mangler situasjonen «Tidspunktet er passert», som PRD-en legger der.
  - Rekkefølgen i «Trenger handling» står som [ASSUMPTION], men er nå bestemt i PRD-en.
  - «Nytt merke … krever presisering av FR-18» og de fire punktene under «Til PRD» er løst.
  - T1 sier ingenting om 320 px, men SM-5 sier at «Den samme testen sjekker at det ikke er vannrett rulling ved 320 px». Arkitekturen sier det samme som PRD-en, så det er T1 i UX som må rettes.
  - Linje 16 viser til «PRD v1.1».
  - Merket «Oppdraget er endret …» må få samme vilkår som i rettingen av det høye funnet over.

  *Fix:* Oppdater EXPERIENCE.md i én runde med `bmad-ux` etter at FR-18 er rettet.

## Passer formen til produktet – sterk

PRD-en ligger øverst i kjeden (UX, så arkitektur, så stories), og v1.2 tar hensyn til det. Den nye raden i topptabellen («Avstemt mot») viser hvilke versjoner av UX og arkitektur den er avstemt mot. Endringene står i kravene der de hører hjemme (tallet i FR-18, med en henvisning fra NFR-11), i stedet for i et nytt krav-ID, slik at ID-ene ikke blir flere enn nødvendig. Det er ingen funn.

## Mekaniske notater

- **Topptabellen:** «arkitekturspinen (v1.2)». Arkitekturspinen har ikke noe versjonsnummer (frontmatter har bare `updated: '2026-11-23'`). Skriv «(oppdatert 2026-11-23)», eller fjern parentesen.
- **Begrunnelsen i FR-18 stemmer ikke helt:** «… står under «Ferdige» selv om oppdraget fortsatt har status Åpen eller Hjelper valgt, fordi brukeren ikke har noe mer å gjøre der.» «Ikke valgt» kan aldri ha status Åpen (situasjonstabellen: Hjelper valgt, Utført eller Avbrutt), og ved «Du trakk deg» *kan* brukeren melde interesse på nytt (FR-12). Skriv for eksempel «fordi brukeren ikke venter på svar fra oppdragsgiveren».
- **Ordlisten:** «Velg hjelper» krever at «minst én har meldt interesse». Ordlisten har begrepet «interessert», som også tar hensyn til tilbaketrukket interesse. Skriv «minst én interessert».
- **§9.2, raden «Tall i menyen»:** Raden samler tre endringer (tallet, merket «Velg hjelper» og gruppene), men begrunnelsen dekker bare tallet. Raden står også mellom «Tidssone» og «Tidspunkt fram i tid», som begge gjelder FR-5. Flytt den ned, og legg til en begrunnelse for gruppene («Brukeren ser først det som venter på hen»).
- **SM-5 og T1:** SM-5 krever «tomme tilstander». T1 har oversikten uten treff og tom fane, men ikke tomtilstanden «Ingen har meldt interesse ennå» i detaljene (NFR-7: «Lister og faner uten innhold»). Enten skrives tomtilstandene SM-5 krever, ut, eller så legges tomtilstanden for oppdragsgiveren til i T1.
- **NFR-6 og NFR-7:** NFR-6 krever kjerneflyten «fra 360 px», mens NFR-7 krever at innholdet flyter om ved 320 px. Kravene motsier ikke hverandre, men WCAG 1.4.10 betyr i praksis at funksjonene også må virke ved 320 px. Ifølge memlog skal NFR-6 bevisst beholde 360 px, så en setning i NFR-6 kan forklare forskjellen: «320 px sjekkes som omflyt i NFR-7».
- **«Testes ved» i NFR-7:** Testomfanget er nå bare en henvisning til EXPERIENCE.md. Før stod det i PRD-en at testene gjaldt «kjerneflyten» med tastatur og «UJ-1» med skjermleser. SM-5 har fortsatt et minimum («Lista dekker minst …»), men T2–T5 kan nå bli mindre i UX uten at PRD-en endres. Vurder å beholde minimumet i én bisetning: «T2 og T3 dekker minst UJ-1».
- **Situasjonstabellen i FR-18 (fra v1.1, ikke endret):** En hjelper som har trukket seg, meldt interesse på nytt, blitt valgt igjen og så fjernet, passer både i raden «Fjernet» og i raden «Trakk seg …, uten ny interesse», selv om tabellen sier «nøyaktig én rad». Begge radene ligger under «Ferdige», så grupperingen påvirkes ikke. Skriv for eksempel «Den nyeste grunnen gjelder».
- **Endringsloggen 1.2:** Den dekker endringene, men nevner ikke at SM-5-lista er utvidet (tomme tilstander, KI-feil og så videre) eller at testen ved 320 px er lagt til. Det er en liten sak, men det er nyttig for sporingen.
- **Sporing og ID-er:** Ingen nye ID-er og ingen ID-er brukt om igjen. Sporingslinjen for FR-18 og tabellene i §9.1 trenger ikke endres, siden endringene ikke kommer fra noen regel eller suksesskriterier i briefen. Merknaden etter tabellene i §9.1 («FR-18 … har ikke et eget suksesskriterium») gjelder fortsatt.

## Behandling (2026-11-23)

- **high** «Oppdraget er endret …» – tatt med: merket vises bare ved «Venter på svar» (FR-18), og FR-6 viser til vilkåret.
- **medium** Sommertid i FR-5 – tatt med: tre testbare regler, i samsvar med AD-9.
- **medium** «Merke» udefinert – tatt med: «Merke» og «Situasjon» i §3, UJ-2 bruker «står som», og FR-18 sier at situasjonene ikke er merker.
- **medium** «Hjelperen trakk seg» – tatt med: oppførselen beholdes, og avveiningen står i FR-18.
- **low** Like tidspunkt, «Testes ved» i NFR-11, overskriften på §8 – tatt med.
- **low** EXPERIENCE.md utdatert – utsatt til en kort `bmad-ux`-oppdatering (issues.md). Det gjelder også T1 (detaljer uten interesserte, sjekk ved 320 px).
- **Mekaniske notater** – alle som gjelder PRD-en, er tatt med: topptabellen, begrunnelsen i FR-18, «minst én interessert», raden i §9.2 flyttet og begrunnet, tomme tilstander i SM-5, en setning i NFR-6, minimum for T2 og T3 i NFR-7, «det som skjedde sist» i situasjonstabellen, og endringsloggen.
