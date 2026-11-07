# Kvalitetsreview av PRD – Nabolagshelten (v0.3, etter avstemming)

## Samlet vurdering
PRD-en er klar for UX og arkitektur. Kravene er konkrete, testbare og kan spores til briefens regler og suksesskriterier, og omfanget er ærlig avgrenset. Risikoen ligger i noen få krav uten tallfestet grense (KI-tidsavbrudd, ventetilstand) og i at sporingen fra regel til FR bare står spredt i teksten.

## Klar for beslutninger – sterk
Beslutninger står som beslutninger (ingen betaling, postnummer, 18 år, stjerner, egne oppdrag bare under Mine oppdrag). Avveiinger er navngitt der de finnes: kjent begrensning ved postnummergrense (FR-10), anonymiserte kommentarer kan avsløre forfatter (FR-4), ingen varsler (§7.2). Åpne spørsmål (§9) er reelle og ingen blokkerer neste fase.

## Innhold fremfor pynt – sterk
To personer, begge driver konkrete krav (Kari → store trykkflater, KI-forslag; Amir → oversikt, profil). NFR-ene har konkrete terskler (4,5:1, 18 px, 48 px, 360 px, 15–20 min).

### Funn
- **low** Uklart målbart språk (NFR-8) – «enkelt språk» kan ikke testes direkte. *Fix:* knytt til manuell gjennomgang av kjerneflyten med ordvalgene i skissene.
- **low** Vag sikkerhetsformulering (NFR-4) – «anerkjent algoritme for passord». *Fix:* nevn eksempler (bcrypt, Argon2) og at valget tas i arkitekturen.

## Strategisk sammenheng – tilstrekkelig
Tesen er tydelig (lokalt, tydelig status, erfaring som dokumentasjon), og kjerneflyten følger den. Suksessmålene måler mest leveranse (tester, README), som passer et sensurert skoleprosjekt. Motmål er navngitt.

### Funn
- **low** Brukertesten i SM-4 er ikke definert – *Fix:* minst to testpersoner; tid måles fra «Legg ut oppdrag» til publisert oppdrag.

## Tydelig når det er ferdig – sterk
Alle FR har testbare konsekvenser, og «avvises» er definert én gang i §4.

### Funn
- **medium** KI-tidsavbrudd uten grense (FR-25) – «tidsavbrudd» sier ikke etter hvor lenge, så det er ikke testbart. *Fix:* sett for eksempel 10 sekunder som `[ANTAKELSE]`.
- **low** «Tydelig ventetilstand» (FR-23) er et adjektiv. *Fix:* «Knappen er deaktivert og viser «Lager forslag …» mens forespørselen pågår.»

## Ærlig om omfang – sterk
Ikke-mål (§6), utsatt (§7.2) og antakelser (§10) er eksplisitte. Én antakelse og to åpne spørsmål er lavt for dette nivået.

## Brukbar for neste steg – tilstrekkelig
Ordlisten dekker alle domenebegreper, og ID-ene FR-1–26, NFR-1–10 og UJ-1–2 er sammenhengende.

### Funn
- **medium** Ingen samlet sporing fra regel til FR – NFR-5 krever en test per regel R1–R13, men koblingen står bare spredt i FR-ene. Det gjør testplanlegging og sensors sporing tyngre. *Fix:* liten tabell R1–R13 → FR i §4 (innledningen).
- **low** Ufullstendig FR-liste i NFR-5 – FR-18, FR-21 og FR-22 mangler selv om de har regler som må sjekkes på serveren. *Fix:* skriv «alle regler i FR-ene» og vis til tabellen.
- **low** Ordlisteavvik – «blir Åpent igjen» (UJ-2) mot status «Åpen». *Fix:* «får status Åpen igjen».

## Passer formen til produktet – sterk
Forbrukerprodukt med to roller og mye UX: brukerreiser med navngitte personer er riktig. Lengden er over 5–8 sider, men detaljene i FR-ene trengs for stories.

## Mekaniske notater
- Antakelser: én inline (FR-6) og den står i §10. OK.
- Lenker til brief og skisser (`../../`) peker riktig.
- Versjon i hodet er 0.3; settes til 1.0 når PRD-en er ferdig.

## Utfall (2026-11-07)
Heidi valgte å rette alle funn. Alle åtte er rettet i PRD v1.0:
- KI-tidsavbrudd 10 s (FR-25) · sporingstabell R1–R13 og SK1–SK10 → FR (§4) · NFR-5 viser til tabellen · «Åpent» → «får status Åpen» (UJ-2) · testbar ventetilstand (FR-23) · NFR-4 med eksempler og test · NFR-8 testbar mot ordlisten · SM-4 definert.

Funnet ved gjennomlesing etterpå, også rettet: UJ-1 steg 4 og UJ-2 steg 3 i riktig rekkefølge i forhold til skjermbildene; melding ved interesse valgfri også i ordliste og FR-12; «Slettet bruker» og grunnlag for snitt i FR-21; navn på valgt hjelper i FR-18; KI bare ved nytt oppdrag; NFR-10 flyttet etter NFR-9; SM-1 dekker alle FR; ny §10 med alle presiseringer i forhold til briefen.
