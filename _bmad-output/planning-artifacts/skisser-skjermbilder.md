# Skisser av skjermbilder – Nabolagshelten v1

| | |
|---|---|
| **Status** | Forslag til gruppen |
| **Bygger på** | [Product brief](product-brief-nabolagshelten.md), delene «Viktigste skjermbilder», «Regler» og «Suksesskriterier» |
| **Neste steg** | Diskuter i gruppen og bruk som innspill til PRD og UX (`bmad-ux`) |

Skissene viser innhold og rekkefølge, ikke endelig utseende. De er tegnet for mobil (360 px bredde), fordi det er den smaleste skjermen appen må fungere på. På nettbrett og PC kan de samme elementene ligge bredere.

## Felles prinsipper

Hentet fra personene Kari (72) og Amir (21) i briefen:

- **Stor tekst og store trykkflater.** Brødtekst minst 18 px, knapper minst 48 px høye.
- **Knapper med tekst**, ikke bare ikoner. «Legg ut oppdrag», ikke bare «+».
- **Én hovedhandling per skjerm**, som en tydelig fylt knapp. Mindre viktige handlinger er vanlige lenker eller omrissede knapper.
- **Status vises alltid med ord**, for eksempel «Åpen» eller «Hjelper valgt», ikke bare med farge.
- **Fast meny nederst** med tre valg: Oppdrag · Mine oppdrag · Profil.
- **Enkelt språk.** «Meld interesse», ikke «Send forespørsel».

Tegnforklaring i skissene:

```
[ Knapp ]        hovedknapp (fylt)
( Knapp )        sekundær knapp (omriss)
[____________]   tekstfelt
[ Valg      v]   nedtrekksliste
<Lenke>          lenke
```

---

## 1. Oppdragsoversikt (startside)

Det første en innlogget bruker ser. Viser bare **åpne** oppdrag, som standard i eget postnummer.

```
+------------------------------------+
|  Nabolagshelten                    |
+------------------------------------+
|                                    |
|  [     + Legg ut oppdrag        ]  |
|                                    |
|  Ledige oppdrag i 0571             |
|                                    |
|  Kategori       Postnummer         |
|  [ Alle     v]  [ 0571      ]      |
|                                    |
|  +------------------------------+  |
|  | Måke innkjørselen            |  |
|  | Snømåking                    |  |
|  | I morgen kl. 07:00           |  |
|  | 200 kr                       |  |
|  +------------------------------+  |
|  +------------------------------+  |
|  | Bære sofa til 2. etasje      |  |
|  | Bærehjelp/flytting           |  |
|  | Lørdag 14. nov. kl. 12:00    |  |
|  | 300 kr                       |  |
|  +------------------------------+  |
|  +------------------------------+  |
|  | Sette opp ny iPad            |  |
|  | Teknologihjelp               |  |
|  | Fleksibelt denne uken        |  |
|  | Uten betaling                |  |
|  +------------------------------+  |
|                                    |
+------------------------------------+
| Oppdrag | Mine oppdrag | Profil    |
+------------------------------------+
```

**Merknader**

- Hele kortet kan trykkes og åpner *Oppdragsdetaljer*.
- Sortert etter tidspunkt, de som skal gjøres først øverst.
- Ingen treff: «Ingen ledige oppdrag i 0571 akkurat nå.» med lenken <Se alle postnumre>.
- Oppdrag med status Hjelper valgt, Utført eller Avbrutt vises ikke her.

**Krav:** suksesskriterium 3, regel 1.

---

## 2. Nytt oppdrag

Skjemaet er delt i to steg, så Kari ikke får alle feltene på én gang.

### Steg 1: Beskriv oppdraget

```
+------------------------------------+
|  <- Tilbake       Nytt oppdrag 1/2 |
+------------------------------------+
|                                    |
|  Hva trenger du hjelp til?         |
|  Skriv med egne ord.               |
|  +------------------------------+  |
|  | trenger noen til å måke      |  |
|  | innkjørselen før jobb i      |  |
|  | morgen                       |  |
|  +------------------------------+  |
|                                    |
|  ( Få forslag til tekst )          |
|  Teksten sendes til en ekstern     |
|  tjeneste for å lage forslag.      |
|                                    |
|  +------------------------------+  |
|  | Forslag                      |  |
|  |                              |  |
|  | Kategori: Snømåking          |  |
|  |            ( Bruk ) <Forkast>|  |
|  | Tittel: Måke innkjørselen    |  |
|  |   før kl. 07:30              |  |
|  |            ( Bruk ) <Forkast>|  |
|  | Beskrivelse: Innkjørselen er |  |
|  |   ca. 10 meter. Spade finnes.|  |
|  |            ( Bruk ) <Forkast>|  |
|  |                              |  |
|  | Tips: Skriv gjerne hvor stor |  |
|  | innkjørselen er.             |  |
|  +------------------------------+  |
|                                    |
|  Tittel                            |
|  [ Måke innkjørselen før 07:30 ]   |
|  Kategori                          |
|  [ Snømåking              v]       |
|                                    |
|  [           Neste           ]     |
+------------------------------------+
```

### Steg 2: Når, hvor og hva du tilbyr

```
+------------------------------------+
|  <- Tilbake       Nytt oppdrag 2/2 |
+------------------------------------+
|                                    |
|  Postnummer                        |
|  [ 0571                      ]     |
|                                    |
|  Når?                              |
|  [ 06.11.2026 ]  [ 07:00 ]         |
|                                    |
|  Hva tilbyr du?                    |
|  (o) Beløp  [ 200     ] kr         |
|  ( ) Uten betaling                 |
|                                    |
|  +------------------------------+  |
|  | Måke innkjørselen før 07:30  |  |
|  | Snømåking · 0571             |  |
|  | Fre 6. nov. kl. 07:00        |  |
|  | 200 kr                       |  |
|  +------------------------------+  |
|  Slik vises oppdraget for andre.   |
|                                    |
|  [        Publiser oppdrag    ]    |
+------------------------------------+
```

**Merknader**

- «Få forslag» er en sekundær knapp. Brukeren kan hoppe over den og fylle inn tittel og kategori selv.
- Forslagsboksen vises bare etter at brukeren har trykket «Få forslag». «Bruk» fyller inn feltet under, og brukeren kan fortsatt endre det.
- Hvis forslaget feiler: «Vi fikk ikke laget forslag akkurat nå. Du kan fylle inn selv.» Skjemaet virker som vanlig.
- Postnummer er forhåndsutfylt fra profilen.
- Feil i obligatoriske felter vises med tekst rett under feltet, for eksempel «Skriv en tittel».
- Forhåndsvisningen i steg 2 viser kortet slik det blir seende ut i oversikten.
- Den samme skjermen brukes til å *redigere* et oppdrag. Da står det «Lagre endringer» i stedet for «Publiser oppdrag».

**Krav:** suksesskriterium 2 og 9, regel 10.

---

## 3. Oppdragsdetaljer

Samme skjerm, men innholdet nederst avhenger av **hvem** som ser den og **hvilken status** oppdraget har.

### 3a. En annen bruker ser et åpent oppdrag

```
+------------------------------------+
|  <- Tilbake                        |
+------------------------------------+
|                                    |
|  Måke innkjørselen før 07:30       |
|  Status: Åpen                      |
|                                    |
|  Snømåking · 0571                  |
|  Fre 6. nov. kl. 07:00             |
|  200 kr                            |
|                                    |
|  Innkjørselen er ca. 10 meter.     |
|  Spade finnes i garasjen.          |
|                                    |
|  Lagt ut av Kari                   |
|  4 fullførte oppdrag · 4,8 av 5    |
|  <Se profil>                       |
|                                    |
|  Melding til Kari (valgfritt)      |
|  [ Jeg kan komme kl. 06:45   ]     |
|                                    |
|  [       Meld interesse       ]    |
|                                    |
+------------------------------------+
| Oppdrag | Mine oppdrag | Profil    |
+------------------------------------+
```

Etter at brukeren har meldt interesse, byttes knappen ut med teksten «Du har meldt interesse. Under Mine oppdrag ser du om Kari har valgt deg.» (Varsler er utsatt til senere, så appen sender ingen beskjed.)

### 3b. Oppdragsgiveren ser interesserte

```
+------------------------------------+
|  <- Tilbake                        |
+------------------------------------+
|  Måke innkjørselen før 07:30       |
|  Status: Åpen                      |
|  Fre 6. nov. kl. 07:00 · 200 kr    |
|                                    |
|  ( Rediger )   ( Avbryt oppdrag )  |
|                                    |
|  3 har meldt interesse             |
|                                    |
|  +------------------------------+  |
|  | Amir                         |  |
|  | 12 fullførte · 4,9 av 5      |  |
|  | «Jeg kan komme kl. 06:45»    |  |
|  | <Se profil>     [ Velg ]     |  |
|  +------------------------------+  |
|  +------------------------------+  |
|  | Sara                         |  |
|  | 2 fullførte · 5,0 av 5       |  |
|  | «Bor rett over gata.»        |  |
|  | <Se profil>     [ Velg ]     |  |
|  +------------------------------+  |
|  +------------------------------+  |
|  | Jonas                        |  |
|  | Ingen fullførte ennå         |  |
|  | <Se profil>     [ Velg ]     |  |
|  +------------------------------+  |
+------------------------------------+
| Oppdrag | Mine oppdrag | Profil    |
+------------------------------------+
```

Trykk på «Velg» åpner en bekreftelse: «Velge Amir? Dere får se hverandres telefonnummer.» med [ Ja, velg Amir ] og <Avbryt>.

### 3c. Hjelper er valgt (det oppdragsgiver og valgt hjelper ser)

```
+------------------------------------+
|  <- Tilbake                        |
+------------------------------------+
|  Måke innkjørselen før 07:30       |
|  Status: Hjelper valgt             |
|  Fre 6. nov. kl. 07:00 · 200 kr    |
|                                    |
|  +------------------------------+  |
|  | Hjelper: Amir                |  |
|  | Telefon: 912 34 567          |  |
|  | Avtal detaljene direkte.     |  |
|  +------------------------------+  |
|                                    |
|  (bare for Amir:)                  |
|  [   Marker som utført        ]    |
|                                    |
|  (bare for Kari:)                  |
|  ( Avbryt oppdrag )                |
+------------------------------------+
```

Kari ser Amirs telefonnummer og Amir ser Karis. Ingen andre ser noen av numrene. Oppdraget er borte fra oversikten.

### 3d. Utført – gi tilbakemelding

```
+------------------------------------+
|  <- Tilbake                        |
+------------------------------------+
|  Måke innkjørselen før 07:30       |
|  Status: Utført                    |
|                                    |
|  Hvordan gikk det med Amir?        |
|                                    |
|  ( 1 ) ( 2 ) ( 3 ) ( 4 ) ( 5 )     |
|  Dårlig                   Veldig   |
|                            bra     |
|                                    |
|  Kommentar (valgfritt)             |
|  +------------------------------+  |
|  | Kom tidlig og gjorde en      |  |
|  | grundig jobb!                |  |
|  +------------------------------+  |
|  Kommentaren vises i Amirs profil. |
|                                    |
|  [     Send tilbakemelding    ]    |
+------------------------------------+
```

Vurderingen er tall-knapper (1–5) med tekst på endene, ikke små stjerner. Det er lettere å treffe og forstå. Etter at tilbakemeldingen er sendt: «Takk! Tilbakemeldingen er lagt til i Amirs profil.»

**Krav:** suksesskriterium 4–7, regel 2–8.

---

## 4. Mine oppdrag

To faner. Kari bruker mest den første og Amir den andre, men alle kan bruke begge.

```
+------------------------------------+
|  Mine oppdrag                      |
+------------------------------------+
|  +--------------+---------------+  |
|  | Lagt ut (3)  | Hjelper med(2)|  |
|  +==============+---------------+  |
|                                    |
|  Trenger handling                  |
|  +------------------------------+  |
|  | Måke innkjørselen            |  |
|  | Åpen · 3 har meldt interesse |  |
|  | Fre 6. nov. kl. 07:00        |  |
|  +------------------------------+  |
|                                    |
|  Pågår                             |
|  +------------------------------+  |
|  | Klippe plenen                |  |
|  | Hjelper valgt · Amir         |  |
|  | Søn 8. nov. kl. 13:00        |  |
|  +------------------------------+  |
|                                    |
|  Ferdige                           |
|  +------------------------------+  |
|  | Bære ved inn i boden         |  |
|  | Utført · Gi tilbakemelding   |  |
|  +------------------------------+  |
|                                    |
|  <Vis avbrutte oppdrag>            |
|                                    |
+------------------------------------+
| Oppdrag | Mine oppdrag | Profil    |
+------------------------------------+
```

**Merknader**

- Oppdragene er gruppert etter hva brukeren må gjøre, ikke bare listet etter status. Det som krever handling, kommer øverst.
- Fanen «Hjelper med» viser oppdrag brukeren har meldt interesse på, med status som «Venter på svar», «Du er valgt» eller «Utført».
- Avbrutte oppdrag er skjult bak en lenke, så lista ikke blir lang.

**Krav:** omfanget «Mine oppdrag med status».

---

## 5. Profil

Profilen er «erfaringsbeviset». Den samme skjermen vises når andre trykker «Se profil», men da uten redigering og innstillinger.

```
+------------------------------------+
|  Profil                            |
+------------------------------------+
|                                    |
|  Amir                              |
|  0571 Oslo                         |
|                                    |
|  Student på OsloMet. Har god tid   |
|  ettermiddager og i helger.        |
|                                    |
|  4,9 av 5 i snitt (11 vurderinger) |
|                                    |
|  Fullførte oppdrag: 12             |
|  +------------------------------+  |
|  | Snømåking               5    |  |
|  | Hage                    4    |  |
|  | Bærehjelp/flytting      2    |  |
|  | Teknologihjelp          1    |  |
|  +------------------------------+  |
|                                    |
|  Tilbakemeldinger                  |
|  +------------------------------+  |
|  | 5 av 5 · Snømåking · nov.    |  |
|  | «Kom tidlig og gjorde en     |  |
|  | grundig jobb!» – Kari        |  |
|  +------------------------------+  |
|  +------------------------------+  |
|  | 5 av 5 · Hage · okt.         |  |
|  | «Veldig hyggelig.»           |  |
|  | – Slettet bruker             |  |
|  +------------------------------+  |
|  <Vis alle tilbakemeldinger>       |
|                                    |
|  (bare på egen profil:)            |
|  ( Rediger profil )                |
|  <Logg ut>                         |
|  <Slett konto>                     |
+------------------------------------+
| Oppdrag | Mine oppdrag | Profil    |
+------------------------------------+
```

**Merknader**

- Telefonnummer og e-post vises **aldri** i profilen. Telefonnummeret vises bare inne i et oppdrag der hjelper er valgt (regel 8).
- «Slett konto» er en lite fremtredende lenke nederst. Den åpner en bekreftelse som forklarer hva som skjer (se «Sletting av konto» i briefen), blant annet at kommentarer i noen tilfeller kan avsløre hvem som skrev dem.
- Tilbakemeldinger fra slettede brukere vises med «Slettet bruker».

**Krav:** suksesskriterium 1 og 8, regel 8 og 11.

---

## Ikke skissert ennå

Disse skjermene trengs også, men er enkle skjemaer og kan tas i UX- eller PRD-fasen:

- Registrering (navn, e-post, passord, telefon, postnummer, fødselsdato) og innlogging
- Rediger profil
- Bekreftelse ved sletting av konto

## Spørsmål til gruppen

1. Er det greit å dele «Nytt oppdrag» i to steg, eller vil dere ha alt på én skjerm?
2. Skal oversikten ha en egen kategori-rad med knapper (lettere å trykke) i stedet for nedtrekksliste?
3. Holder det at brukeren ser status ved å åpne appen, eller trengs et tydelig «ny interesse»-merke på «Mine oppdrag» i menyen? (Varsler på e-post/push er utsatt.)
