---
status: draft
stepsCompleted: [1, 2]
inputDocuments:
  - _bmad-output/planning-artifacts/prds/prd-G22-bernardo-kverno-moystad-nguyen-2026-11-05/prd.md
  - _bmad-output/planning-artifacts/architecture/architecture-G22-bernardo-kverno-moystad-nguyen-2026-11-08/ARCHITECTURE-SPINE.md
  - _bmad-output/planning-artifacts/ux-designs/ux-G22-bernardo-kverno-moystad-nguyen-2026-11-07/DESIGN.md
  - _bmad-output/planning-artifacts/ux-designs/ux-G22-bernardo-kverno-moystad-nguyen-2026-11-07/EXPERIENCE.md
contextNotes:
  - .logs/heidi/issues.md (åpne punkter om første story, testhull i review-accessibility.md og README)
  - _bmad-output/planning-artifacts/ux-designs/ux-G22-bernardo-kverno-moystad-nguyen-2026-11-07/review-accessibility.md (testdekning, M10)
excluded:
  - _bmad-output/planning-artifacts/architecture/technology.md (beskriver Pytagoras Website V2; mock-fallback er dekket av AD-12 og AD-14)
  - _bmad-output/planning-artifacts/product-brief-nabolagshelten.md (PRD-en bygger på den)
  - _bmad-output/planning-artifacts/skisser-skjermbilder.md (erstattet av UX-spinene)
---

# Nabolagshelten (G22) – Epics og stories

## Overview

Dokumentet deler kravene i PRD v1.2, UX-spinene (DESIGN.md og EXPERIENCE.md) og arkitekturspinen opp i epics og stories som kan implementeres. Krav-ID-ene (FR-N, NFR-N, AD-N, UX-DR-N) brukes i stories, commits, tester og PR-er, slik PRD §0 og arkitekturkonvensjonen «Sporbarhet» krever.

**Kildeprioritet:** PRD > arkitekturspinen og UX-spinene > mockups. Kravteksten under er et sammendrag for sporing. Ved tvil gjelder ordlyden i PRD-en, og tekstene i EXPERIENCE.md gjelder ordrett.

## Requirements Inventory

### Functional Requirements

Prioritet etter PRD §6.1: **Må** = FR-1–FR-21, **Bør** = FR-22–FR-26.

**Konto og innlogging (§4.1)**

- **FR-1: Registrere konto** (Må). Navn 1–80 tegn, gyldig e-post, passord 8–64 tegn, telefon åtte siffer (mellomrom, +47 og 0047 godtas), postnummer fra lista, fødselsdato som ikke er fram i tid og høyst 120 år tilbake. Under 18 år i norsk tid avvises (fyller 18 i dag godtas, 29. februar fyller år 1. mars i år som ikke er skuddår). E-post i bruk avvises uten å skille store og små bokstaver. Personverntekst på siden. «Om meg» er ikke med. Etter registrering er brukeren innlogget.
- **FR-2: Logge inn og ut** (Må). Samme melding for feil e-post og feil passord. E-post sammenlignes uten store og små bokstaver. 5 mislykkede forsøk med samme e-post på 15 min gir sperre i 15 min. Innloggingen varer høyst 7 dager eller til utlogging. Etter utlogging er det ingen tilgang til innhold.
- **FR-3: Innlogging kreves** (Må). Alle sider og forespørsler unntatt registrering, innlogging og statiske filer krever innlogging, og avvisningen skjer på serveren. En automatisk test går gjennom alle ruter uten innlogging.
- **FR-4: Slette egen konto** (Må). Krever passord. Først forklares hva som skjer. Bare brukeren selv kan slette kontoen sin. Personfeltene slettes (testes ved at databasen ikke lenger inneholder den gamle e-posten eller telefonnummeret). Alle innlogginger avsluttes. E-posten kan brukes på nytt uten kobling til gamle data. «Slettet bruker» vises uten lenke, og en direkte lenke til profilen gir en forståelig melding. Dataene behandles etter tabellen i FR-4: egne åpne og avbrutte oppdrag slettes, Hjelper valgt blir Avbrutt, Utført beholdes, interesser slettes, valgt hjelper på Hjelper valgt blir som FR-17, gitte tilbakemeldinger beholdes som «Slettet bruker», og mottatte tilbakemeldinger slettes.

**Oppdrag (§4.2)**

- **FR-5: Legge ut oppdrag** (Må). Tittel 3–80 tegn, beskrivelse 10–1000 tegn, kategori fra lista, postnummer forhåndsutfylt fra profilen, tidspunkt som ikke er passert og høyst 12 måneder fram, godtgjørelse et heltall fra 1 til 10 000 kr eller «uten betaling». Alle felt er påkrevd. Ugyldige felt gir melding ved feltet, og ingenting lagres. Norsk tid med sommertidsregler: klokkeslett som ikke finnes, avvises, og klokkeslett som finnes to ganger, tolkes som det første. Hjelpetekst om adresse og telefon. Lagret oppdrag får status Åpen.
- **FR-6: Redigere oppdrag** (Må). Bare oppdragsgiveren, og bare når status er Åpen. Samme validering som FR-5, og et passert tidspunkt må endres («Velg et nytt tidspunkt fram i tid»). Interessene beholdes. Endres tidspunkt, godtgjørelse eller postnummer, merkes tidligere interesser «Meldt før endring», og den interesserte ser «Oppdraget er endret etter at du meldte interesse» når situasjonen er «Venter på svar». Ingen KI ved redigering.
- **FR-7: Avbryte oppdrag** (Må). Bare oppdragsgiveren, og bare fra Åpen eller Hjelper valgt. Krever bekreftelse. Telefonnumrene skjules. Avbrytes oppdraget fra Hjelper valgt, beholdes koblingen til hjelperen, som ser oppdraget som Avbrutt uten telefonnumre.
- **FR-8: Utgåtte oppdrag** (Må). Åpent oppdrag med passert tidspunkt vises ikke i oversikten, kan ikke få nye interesser, og hjelper kan ikke velges. Under «Mine oppdrag» står merket «Tidspunktet er passert», og oppdraget kan endres eller avbrytes. Får det nytt tidspunkt, vises det igjen.
- **FR-9: Innsyn i oppdragsdetaljer** (Må). Alle felt og status, oppdragsgiverens navn, erfaring og snitt med lenke til profilen. Åpen: alle innloggede ser detaljene, men bare oppdragsgiveren ser de interesserte. Andre statuser: bare oppdragsgiveren og valgt hjelper, og andre avvises.

**Finne oppdrag (§4.3)**

- **FR-10: Oppdragsoversikt** (Må). Viser Åpne oppdrag som ikke er passert, i eget postnummer, sortert etter tidspunkt og så etter når de ble lagt ut. Kortet viser tittel, kategori, tidspunkt og godtgjørelse. Egne oppdrag vises ikke. Tomtilstand med forslag.
- **FR-11: Filtrere oppdrag** (Må). Filter på kategori og et annet postnummer, som kan kombineres. Ukjent postnummer avvises med melding.

**Interesse og valg av hjelper (§4.4)**

- **FR-12: Melde interesse** (Må). Valgfri melding, høyst 500 tegn. Avvises for eget oppdrag, ved dobbel interesse, når status ikke er Åpen og når tidspunktet er passert. En fjernet hjelper kan ikke melde interesse på nytt og ser «Du er ikke lenger valgt til dette oppdraget». Den som trakk seg selv, kan melde interesse igjen. Etterpå vises «Du har meldt interesse».
- **FR-13: Trekke interesse** (Må). Bare når status er Åpen og tidspunktet ikke er passert. Etterpå kan brukeren melde interesse på nytt.
- **FR-14: Se interesserte** (Må). Bare oppdragsgiveren ser lista. For hver: navn, fullførte oppdrag, snitt eller «Ingen vurderinger ennå», melding, eventuelt «Meldt før endring» og lenke til profilen. Eldste først. Tomtilstand.
- **FR-15: Velge hjelper** (Må). Krever bekreftelse («Velge Amir? Dere får se hverandres telefonnummer.»). Status blir Hjelper valgt. Avvises hvis brukeren ikke er oppdragsgiver, status ikke er Åpen, tidspunktet er passert eller den valgte ikke er interessert. Ved dobbeltklikk blir det bare én valgt hjelper.
- **FR-16: Dele telefonnummer** (Må). Bare oppdragsgiveren og valgt hjelper ser numrene, og bare ved Hjelper valgt og Utført. Numrene skjules ved fjerning, tilbaketrekking og avbrytelse, og når motparten er slettet. Ingen andre steder viser telefon, e-post eller fødselsdato, heller ikke i svar fra serveren, unntatt brukerens egne opplysninger på «Rediger profil».
- **FR-17: Fjerne hjelper eller trekke seg** (Må). Krever bekreftelse, og status blir Åpen. Den tidligere hjelperens interesse slettes, mens de andre beholdes. Telefonnumrene skjules. Andre brukere og andre statuser enn Hjelper valgt avvises.

**Mine oppdrag (§4.5)**

- **FR-18: Mine oppdrag** (Må). To faner. Situasjonstabellen gir nøyaktig én situasjon per oppdrag i «Oppdrag jeg hjelper med», og det som skjedde sist, gjelder. Merkene: «Velg hjelper», «Tidspunktet er passert», «Er jobben gjort?», «Gi tilbakemelding», «Hjelperen trakk seg» og «Oppdraget er endret etter at du meldte interesse», og alle merker som gjelder, vises. Gruppene «Trenger handling», «Pågår» og «Ferdige» med fast rekkefølge, og grupper uten oppdrag vises ikke. Hjelper-fanen grupperes etter brukerens egen situasjon. Menyen viser antallet under «Trenger handling» (et oppdrag telles én gang, tallet regnes ut ved hver sidelasting, vises ikke ved 0 og leses som «Mine oppdrag, 2 trenger handling»). Tom fane har tomtilstand med lenke.

**Fullføre og gi tilbakemelding (§4.6)**

- **FR-19: Markere som utført** (Må). Krever bekreftelse («Marker som utført? Det kan ikke angres.»). Valgt hjelper kan markere fra kl. 00:00 norsk tid på datoen, og oppdragsgiveren når tidspunktet er passert. Bare fra Hjelper valgt, og etterpå kan oppdraget ikke endres.
- **FR-20: Gi tilbakemelding** (Må). 1–5 stjerner som store knapper som virker med tastatur og har tekst for skjermleser, og en valgfri kommentar på høyst 500 tegn. Lagres først ved «Send». Bare ved Utført, bare mellom partene og én gang per person. Tilbakemelding til en slettet bruker avvises. Kvittering, og profil og snitt oppdateres straks.

**Profil (§4.7)**

- **FR-21: Vise profil** (Må). Navn, postnummer med poststed, «om meg», fullførte oppdrag per kategori (bare som valgt hjelper), snitt («4,3 av 5, 7 vurderinger», med én desimal og desimalkomma) fra alle mottatte tilbakemeldinger, og alle tilbakemeldinger nyeste først med vurdering, kommentar, giver, dato og rolle. «Ingen vurderinger ennå». Teksten om at erfaringen ikke er verifisert. «Slettet bruker» uten lenke. Aldri telefon, e-post eller fødselsdato. Egen profil har «Rediger profil» og «Logg ut».
- **FR-22: Redigere egen profil** (Bør). «Om meg» (valgfri, høyst 500 tegn), postnummer og telefon, validert som i FR-1. Nytt postnummer brukes straks i oversikten og i nye oppdrag. Nytt telefonnummer vises straks for motparten. Navn, e-post og fødselsdato kan ikke endres. Bare brukeren selv.

**KI-forslag (§4.8, bygges etter at kjerneflyten er stabil)**

- **FR-23: Be om forslag** (Bør). Bare i «Nytt oppdrag», og aktiv fra 10 tegn i beskrivelsen. Teksten ved knappen sier om beskrivelsen sendes eksternt eller ikke (mock). Bare beskrivelsen sendes. «Lager forslag …» med opplesning. Høyst 20 forslag per bruker per time. Prompten ligger i en egen fil.
- **FR-24: Bruke eller forkaste forslag** (Bør). Forslagene vises under feltene de gjelder. Ingenting fylles inn før «Bruk». Tipset vises. Beskrivelsen omformuleres uten nye opplysninger, på bokmål, og det testes manuelt med fem faste eksempeltekster. Feltet kan redigeres etterpå. KI lagrer aldri noe.
- **FR-25: Kontroll av KI-svar** (Bør). Gyldig JSON med kategori fra lista, tittel og beskrivelse som følger reglene i FR-5, og tips på høyst 200 tegn. Ugyldige svar vises ikke. Tidsavbrudd etter 10 s. Vennlig melding, og skjemaet beholdes. Svaret vises som ren tekst. Testdobler for ugyldig JSON, ukjent kategori, for lang tekst, feil og for sent svar.
- **FR-26: Mock-modus** (Bør). Tom nøkkel eller plassholder betyr mock. Nøkkelordtabellen der nøkkelordet treffer starten av et ord, og den første kategorien som treffer, gjelder. Tittel fra første setning, og beskrivelse med stor forbokstav og eventuelt punktum. Ingen tips. Deterministisk. Testene kjører alltid i mock-modus.

### NonFunctional Requirements

Alle er **Må** og med i Definition of Done for hver story (PRD §5).

- **NFR-1: Kjørbar på en ren maskin.** README med forutsetninger og versjoner, eksakte kommandoer, seed og testkommando. Mock er standard. *Testes ved:* noen utenfor gruppen har appen i gang innen 15 min (SM-3).
- **NFR-2: Eksempeldata og testbrukere.** Minst 6 brukere i 2–3 postnumre og 10–15 oppdrag som dekker alle kategorier, flere interesserte, Hjelper valgt, Utført med og uten tilbakemelding, Avbrutt, utgått, Hjelper valgt etter tidspunktet og bruker med og uten vurderinger. Tidspunktene er relative til innlastingen. Én kommando laster dataene på nytt. Testbrukerne står i README. *Testes ved:* en automatisk test av situasjonene.
- **NFR-3: Ingen hemmeligheter i repoet.** `.env.example` uten ekte verdier, og `.gitignore` holder ute `.env`. *Testes ved:* gitleaks på hele historikken, dokumentert.
- **NFR-4: Sikker lagring av passord.** Hash med en algoritme laget for passord. *Testes ved:* en automatisk test av at passordet ikke ligger i databasen.
- **NFR-5: Regler håndheves på serveren.** *Testes ved:* hver regel R1–R13 har minst én automatisk test direkte mot serveren.
- **NFR-6: Responsiv.** Kjerneflyten fungerer fra 360 px til PC uten vannrett rulling. *Testes ved:* UJ-1 og UJ-2 ved 360, 768 og 1280 px med skjermbilder.
- **NFR-7: Universell utforming, WCAG 2.1 AA.** Kontrast, tastatur med synlig fokus (også dato og klokkeslett), etiketter og feil ved feltet, tekst på knapper, 18 px brødtekst, 48 px trykkflater, 200 % zoom og omflyt ved 320 px, status med ord, statusmeldinger som leses opp, fokus inn i og ut av dialoger, `lang="nb"` og tomtilstander. *Testes ved:* T1–T5 i EXPERIENCE.md.
- **NFR-8: Tydelig og enkelt språk.** Ordene fra ordlisten, kvittering for hver handling og bekreftelse for handlinger som ikke kan angres. *Testes ved:* manuell gjennomgang mot ordlisten.
- **NFR-9: Personvern.** Lagrer bare de listede opplysningene og aldri adresse. Eksempeldata er oppdiktet. *Testes ved:* gjennomgang av databaseskjemaet.
- **NFR-10: Robust mot ugyldig input.** Validering på serveren og forståelige meldinger, aldri en teknisk feil. *Testes ved:* automatiske tester med ugyldige verdier til hvert skjema og hver handling.
- **NFR-11: Navigasjon.** Fast meny med Oppdrag, Mine oppdrag og Profil, og antallet ved «Mine oppdrag». *Testes ved:* manuelt, med axe og med testene for tallet.
- **NFR-12: Sikkerhet mot vanlige angrep.** Tekst vises alltid som tekst, og handlinger kan ikke utløses fra andre nettsteder. *Testes ved:* en automatisk XSS-test på alle tekstfelt og en CSRF-test.

### Additional Requirements

Fra arkitekturspinen. **Startmal:** Arkitekturen bruker ingen startmal. Det er et greenfield-prosjekt med uv, og **første story er et gjennomgående skjelett** (Structural Seed § Første story). Ingen andre stories starter før den er ferdig.

**Skjelett og infrastruktur**

- **AR-1 Første story (skjelett):** `lag_app()` med mellomvaren i riktig rekkefølge, lesing av skjemakroppen i ren ASGI-mellomvare (prøves ut her), `core.render` og `base.html`, innlogging gjennom `Autentisering`, én Alembic-migrering med postnumre, seed, grønn CI og produksjonspublisering på Vercel mot Supabase med migrering først.
- **AR-2 Stack:** Python 3.12 (`requires-python >=3.11`), uv med `uv.lock`, FastAPI ~=0.165, Jinja2 3.1, SQLAlchemy 2.1 (synkron), Alembic 1.20, psycopg[binary] 3.3, Pydantic 2.14, pydantic-settings 2.16, bcrypt 5.0, itsdangerous 2.2, httpx 0.28, tzdata 2026.6, pytest 9.2, Playwright 1.65 med axe-playwright-python og gitleaks. Ingen npm og intet byggsteg.
- **AR-3 Kildetre og slices (AD-1):** `app/core`, `identity`, `oppdrag`, `profil` og `ki`, hver med `routes.py`, `service.py`, `models.py` og `templates/<slice>/`. Importene går én vei (profil→oppdrag→identity/ki→core). Hver tabell har én eier. `core` når slices bare gjennom `Autentisering` og menykroken. `lag_app()` nekter å starte hvis en kobling mangler.
- **AR-4 Database og migreringer (AD-13):** Samme kode mot SQLite (lokalt og i test) og Postgres (Supabase og CI). Bare Alembic, med `render_as_batch=True`. Én migrering per story. CI feiler ved mer enn ett hode. Etter første produksjonspublisering legger migreringer bare til. Transaction pooler (6543, `NullPool`, `prepare_threshold=None`) for appen og session pooler (5432) for Alembic i Actions.
- **AR-5 Miljø (AD-14):** Én `Settings` med `APP_ENV` lik `local`, `test` eller `production`, og en ukjent verdi stopper oppstarten. Produksjon krever en ekte `SECRET_KEY` og har ingen seed, demokontoer eller testbrytere (`/_test/tilstand` gir 404).
- **AR-6 Postnumre (AD-1, AD-10):** `data/postnumre.tsv` fra Brings register, konvertert til UTF-8 og lastet med en datamigrering. Tilgang bare gjennom `core/postnummer.py`. `core/static/postnumre.json` genereres og sjekkes inn, og en test sammenligner de to. README krediterer «Postnummerdata fra Posten Bring, lisensiert under NLOD 2.0.»
- **AR-7 CI/CD:** `ci.yml` (pytest mot SQLite og Postgres, `alembic heads`, Playwright med axe, gitleaks), `deploy.yml` (på `main`: `alembic upgrade head` og så `vercel deploy --prod`) og `keepalive.yml` (besøk hver 3. dag). `main` er beskyttet og tar bare PR med grønn CI. `vercel.json` slår av automatisk publisering og preview og har `maxDuration = 30`. Workflows bruker aldri `pull_request_target`. Vercel må kobles til GitHub (Vercels GitHub-app på organisasjonen, bare dette repoet).
- **AR-8 Konfig og hemmeligheter:** Appen leser `APP_ENV`, `DATABASE_URL`, `SECRET_KEY`, `OPENROUTER_API_KEY` og `OPENROUTER_MODEL` (i `.env.example` uten verdier og i Vercel env). `MIGRATION_DATABASE_URL` og `VERCEL_*` ligger bare i GitHub Secrets. `.vercel/` er git-ignorert.
- **AR-9 Admin-verktøy (AD-6):** `uv run python -m app.admin nytt-passord|slett-konto <e-post>` for manuell hjelp (glemt passord er utsatt).
- **AR-10 README:** Kontoeiere og reserve (Vercel, Supabase, OpenRouter), kreditering av postnummerdata, testbrukere merket «bare for lokal testing», og at eieren sjekker Supabase før demo.
- **AR-11 Kuttliste for infrastruktur (i denne rekkefølgen):** (1) gjenvisning av skjemaet i AD-7, (2) Postgres-jobben i CI, (3) `steg.js`, (4) besøksjobben. Hvert kutt føres i memlog og i PRD §9.2.

**Regler for kjernen**

- **AR-12 Atomiske statusoverganger (AD-2):** All endring av status går gjennom én funksjon. Andre statusavhengige skrivinger starter med `UPDATE … SET versjon = versjon + 1` med alle radbetingelsene i `WHERE`, og andre sjekker kommer etterpå. 0 rader gir `FinnesIkke` eller `Konflikt`. SQLite bruker `BEGIN IMMEDIATE`, «database is locked» blir `Konflikt`, og `foreign_keys=ON`. Ingen `ON DELETE CASCADE`. Unik-constraint på `interesse(oppdrag_id, bruker_id)`, `tilbakemelding(oppdrag_id, giver_id)`, `oppdrag.skjema_id` og `bruker.epost`. `tidligere_hjelper` med `arsak` lik `fjernet`, `trakk_seg` eller `slettet` skrives bare av overgangen `hjelper_valgt → apen`.
- **AR-13 Avledede tilstander (AD-3):** Utgått, «Er jobben gjort?», merkene, antallet i menyen og synlig telefonnummer beregnes ved lesing med én funksjon hver i `oppdrag/service.py`. Ingen cron. «Meldt før endring» betyr `interesse.opprettet < oppdrag.vesentlig_endret`. `erfaring(db, bruker_ids)` gir `Erfaring` (fra `core/domene.py`). Klokka brukes alltid som `klokke.na()`.
- **AR-14 Innlogging og sesjon (AD-4):** Grensesnittet `Autentisering` ligger i `core/sesjon.py` og implementasjonen i `identity`. Alle ruter krever innlogging, unntatt dem som er merket offentlige. Uten innlogging gir GET 303 til `/logg-inn?neste=` (bare lokale stier), POST følger AD-7, og `X-Fragment` gir 401. Sesjonsnøkkelen ligger i en HttpOnly-cookie med SameSite=Lax (og Secure i produksjon), lagres i `sesjon` og varer i 7 dager. `innloggingsforsok` teller per normalisert e-post og ryddes ved bruk.
- **AR-15 Mellomvare, CSRF og headere (AD-5):** Rekkefølgen er feilhåndtering → headere → CSRF/Origin → sesjon → ruter. Ren ASGI som leser skjemaet én gang (`request.state.skjema`). Signert CSRF-cookie og skjult felt i alle skjema, også før innlogging. `Origin`/`Sec-Fetch-Site` sjekkes. Bare POST endrer data. Headerne CSP `frame-ancestors 'none'`, `X-Frame-Options: DENY`, `nosniff` og `Referrer-Policy: same-origin`.
- **AR-16 Passord og e-post (AD-6):** `hash_passord` og `sjekk_passord` (NFC, ingen trim, bcrypt over base64(SHA-256)) og `normaliser_epost` (trim, NFC, små bokstaver) ligger bare i `identity/service.py`.
- **AR-17 Utløpt innlogging (AD-7):** En POST uten sesjon endrer ingen data og gir en 401-side med de innsendte feltene skjult (unntatt passord og CSRF), en ny CSRF-nøkkel og innloggingsfelt. Etter innlogging går forespørselen videre. Ingen andre feltnavn begynner med `_`. Kan kuttes (AR-11).
- **AR-18 Gravstein ved sletting (AD-8):** `bruker`-raden beholdes med personfeltene satt til NULL og `slettet_tidspunkt` satt. «Slettet bruker» kommer fra én funksjon. `profil/service.py` styrer slettingen i én transaksjon. En test feiler slettingen til slutt med vilje og sjekker at ingenting er endret, både i SQLite og i Postgres.
- **AR-19 Tid (AD-9):** `UtcDateTime` i `core/db.py` (lagrer UTC og gir tilbake aware UTC), og fødselsdato er `Date`. «I dag» regnes i Europe/Oslo. `core/tid.py` eier tolkning og visning (filtrene `tidspunkt` og `dato_kort`), tosifret år og sommertid. En tabelltest dekker alle skrivemåtene og en rundtur over skiftene.
- **AR-20 Tekst og domeneverdier (AD-10):** Alt er UTF-8. Tekst trimmes og NFC-normaliseres før `len()`. `core/domene.py` har `KATEGORIER` (koder i ASCII), statusord og grensene for tittel og beskrivelse. Kategorien lagres som kode og vises bare med `kategori_tekst`. Grensen sendes som `data-maks`, og felt med teller har ikke `maxlength`.
- **AR-21 Escaping (AD-11):** Autoescape er alltid på. Ingen `|safe`, `Markup(` eller `innerHTML` på tekst fra brukere eller KI. `tests/core/test_arkitektur.py` sjekker dette og importretningen.
- **AR-22 KI-grensesnitt (AD-12):** Tre utgaver (OpenRouter med frist på 10 s, mock og testdobbel), og utgaven velges ett sted. `sender_eksternt()` styrer teksten i malen. Lik validering mot `core/domene.py`. Kvoten (20 i glidende 60 min, i `ki_bruk`) sjekkes i en egen transaksjon som committes før kallet. Kredittgrense i produksjon, ellers mock.
- **AR-23 KI-fragment (AD-15):** `POST /oppdrag/forslag` svarer med et HTML-fragment fra `core.render_fragment`. Feil, kvote og tidsavbrudd gir et feilfragment med 200, og utløpt sesjon gir 401. `ki.js` setter inn bare svar med 200 eller 401, i faste beholdere. Uten JS er «Få forslag» skjult. Ingen andre forespørsler skjer uten sidelasting.
- **AR-24 Personopplysninger i maler (AD-16):** Malene får bare `OffentligBruker`, `Profil` og `EgneOpplysninger`. Telefonnummeret gis bare av `telefon_for_motpart`. En test søker etter testbrukernes telefon, e-post og fødselsdato i HTML fra alle GET-ruter.
- **AR-25 Transaksjoner (AD-17):** `hent_db()` gir én `Session` per forespørsel, og en POST-rute kjører `with db.begin():`. Services kaller aldri commit eller rollback. `IntegrityError` fanges med `begin_nested()` (SAVEPOINT). KI-kvoten er det eneste unntaket.
- **AR-26 Feil og PRG:** `core/feil.py` har `RegelBrudd` (422, skjemaet vises på nytt med alle feilene og verdiene), `Konflikt` (redirect med melding), `Duplikat` (redirect til det som finnes), `IngenTilgang` og `FinnesIkke` (404, samme side) og uventede feil (vennlig side, ingen stack trace). Etter vellykket handling: POST → redirect → GET med kvittering i en signert, kortlivet cookie. Skjemamodellene har bare `str | None`, og `RequestValidationError` gir den vennlige siden.
- **AR-27 Rendring:** `core.render(request, mal, *, tittel, aktiv_meny, fokus=None, **ctx)` legger til innlogget bruker, CSRF, kvittering, «Feil: » i tittelen, `aria-current`, antallet i menyen og `tilbake_url`. `core.render_fragment`. Ett Jinja-miljø. Makroene `brukerkort`, `bekreft_dialog`, `feltfeil` og `kvittering`. Filtrene `status_tekst`, `kategori_tekst`, `vurdering`, `tidspunkt` og `kr`. URL-ene og rutenavnene `<slice>.<handling>` fra konvensjonstabellen, `url_for` i malene og en test av at rutenavnene er unike.
- **AR-28 Klientatferd:** Én JS-fil per oppgave i `core/static/js/`: `fokus.js`, `dialog.js` (uten JS: GET-bekreftelsesside med POST-knapp), `sending.js`, `steg.js`, `ki.js` og `skjema.js`. JS har aldri regler. Filtrene er GET-parametre som bygges av én hjelper.
- **AR-29 Tester:** `uv run pytest`. Midlertidig SQLite (Postgres i CI) med `alembic upgrade head` én gang, og hver test rulles tilbake. Fabrikkene `lag_bruker`, `lag_oppdrag`, `lag_interesse`, `lag_tilbakemelding` og `sett_na` ligger bare i `tests/conftest.py`. Hver regel testes mot serveren, også dobbel innsending. FR-3-testen forventer 303 for GET og 401 for POST. Tester av CSRF, headere og rekkefølgen på mellomvaren. E2E bruker `POST /_test/tilstand`. T1 kjøres med axe ved 360 og 1280 px og sjekk ved 320 px. T2–T6 er protokoller i `docs/tester/`.
- **AR-30 Logging og sporbarhet:** Passord, telefon, e-post, sesjonsnøkler og KI-tekst logges aldri. Commits, tester og docstrings for regler oppgir krav-ID-en.

### UX Design Requirements

Fra DESIGN.md og EXPERIENCE.md. Tekstene markert [ASSUMPTION] i EXPERIENCE.md og DESIGN.md ble godkjent av Heidi på vegne av gruppen 2026-11-23, og de gjelder som de står. Akseptansekriteriene viser til tekstene i EXPERIENCE.md i stedet for å skrive dem på nytt.

**Grunnlag**

- **UX-DR1 Designtokens:** Alle farger, typografi (i `rem`), radier og avstander fra frontmatter i DESIGN.md blir CSS-variabler. `color-scheme: light`, ingen mørk modus, systemskrifter (avrundet til overskrifter og `system-ui` til brødtekst), ingen hvit eller svart.
- **UX-DR2 Sideramme (`base.html`):** `lang="nb"`, landemerkene `header`, `nav` («Hovedmeny») og `main` (`tabindex="-1"`), én `h1`, «Hopp til innholdet» som første fokuserbare element, `<title>` etter mønsteret «Side – Nabolagshelten» med «Feil: » foran ved feil (tabellen i EXPERIENCE.md). Uten innlogging vises topplinjen med bare logoen.
- **UX-DR3 Meny:** `topbar` fra 768 px og `bottom-nav` under 768 px. Tre like brede valg med minstehøyde 56 px og tekst som brytes. Fast nederst, men `position: static` når skjermen er lav eller teksten stor. `padding-bottom` og `scroll-padding-bottom` reserverer plass. `nav-badge` med antall, og skjermleser leser «Mine oppdrag, 2 trenger handling». `aria-current` følger tabellen over undersider. Logoen er en lenke med navnet «Nabolagshelten, til oversikten».
- **UX-DR4 Fokus:** 3 px `outline` med 3 px avstand (blush i topplinje og meny). Ringen tegnes på `::after` for kort og lenkerader. `:focus` (ikke bare `:focus-visible`) for kvittering, feiloppsummering og `h1` med `tabindex="-1"`. Aldri `outline: none` uten erstatning. Fokus, merker og valgt tilstand synes med `forced-colors: active`.
- **UX-DR5 Responsiv layout:** 1, 2 og 3 kolonner i oversikten (360–767, 768–1279 og fra 1280 px). Maksbredder 1200, 760 og 640 px. Sidemarg 16 eller 24 px. Omflyt ved 320 px uten vannrett rulling. Tekst brytes, og flater vokser med `min-height`, aldri `nowrap`, `line-clamp` eller ellipse.
- **UX-DR6 Ikoner:** Strekikoner som alltid står sammen med tekst og har `aria-hidden`. Logoen er et hus med hjerte. Ingen illustrasjoner eller emoji.

**Komponenter**

- **UX-DR7 Knapper:** `button-primary` (én per skjerm), `button-secondary`, `button-text` og deaktivert tilstand med `aria-disabled="true"` (kan fortsatt få fokus). Under 768 px står knappene under hverandre med primærknappen øverst i full bredde. Fra 768 px står de på én linje. Like knappenavn får `aria-describedby`. Angre-valget heter aldri «Avbryt».
- **UX-DR8 Oppdragskort (`card`):** Hele kortet er én lenke (tittelen er lenken). Kategori, tittel (h2), tidspunkt, postnummer med poststed og beløp. Hover og fokus gir en kant på 2 px.
- **UX-DR9 Listerad (`list-row`):** Lenkerad (tittelen er lenken, pil ›, `aria-describedby` til merkelinja) og ikke-lenkerad. Rekkefølgen er tittel → statusmerke → situasjon og merke → faktalinjer → knapper under en skillelinje, aldri inne i lenken.
- **UX-DR10 Merker:** `status-badge` (ikon, kant, ord og skjult «Status: Åpen.»), `action-tag` (blush, brytes over så mange linjer som trengs, skjult «Må gjøres: …»), `situation-label` (fet tekst med ikon og skjult «Din situasjon: …») og `category-chip` (beige med kant).
- **UX-DR11 Kategoriknapper:** I filteret er de lenker med `aria-current="true"`. I skjemaet er de en radiogruppe med `fieldset` og `legend`, piltaster og `label:has(:checked)`. Valgt tilstand har kant på 3 px, hake, fet tekst og beholder ikonet. Lange navn brytes etter skråstreken, med `hyphens: auto` og aldri `overflow-wrap: anywhere`.
- **UX-DR12 Skjemafelt:** Synlig `label`, hjelpetekst i `ink-muted`, `aria-describedby` til hjelpetekst og feil, `aria-invalid`, `required` med `novalidate` og «(valgfritt)» på valgfrie felt. Felttype og `autocomplete` etter tabellen i EXPERIENCE.md (WCAG 1.3.5). Feltfeil vises etter innsending (og når brukeren forlater et felt som allerede har vist feil), og passordet tømmes med hjelpeteksten «Skriv passordet på nytt.»
- **UX-DR13 Teller, poststed, passord og beløp:** Teller («37 av 500 tegn») som teller kodepunkter etter NFC og trim og bare leses opp ved grensen. Poststed vises ved gyldig postnummer (fra `postnumre.json`). «Vis passord» med `aria-pressed`. «Beløp i kr» vises med CSS `:has(:checked)`, og beløpet beholdes ved bytte.
- **UX-DR14 «Når?»:** `fieldset` med to tekstfelt (dato `dd.mm.åååå` og klokkeslett `tt:mm`) med formatet som hjelpetekst, ingen kalender, `autocomplete="off"` og ikke `inputmode="numeric"`. Andre skrivemåter godtas. Feltene står under hverandre under 768 px. En feil for hele tidspunktet står samlet under gruppen.
- **UX-DR15 Forhåndsvisning:** `section` «Slik vises oppdraget for andre» med et kort med stiplet kant, uten lenke og uten overskrift. Den oppdateres uten opplesning, og tomme felt vises som «–».
- **UX-DR16 Nytt oppdrag i to steg:** Under 768 px heter stegene «Nytt oppdrag 1 av 2» og «2 av 2», med «Neste» og «Tilbake til steg 1» og `<title>` per steg. Fra 768 px er alt på én skjerm med to `h2`. Feiloppsummeringen lister feil fra begge steg og viser steget med første feil. Uten JS: én skjerm.
- **UX-DR17 Stjerner:** Input er fem radioknapper på 48 × 48 px i en `fieldset` med navnene «1 av 5 stjerner, dårlig» … «5 av 5 stjerner, veldig bra» og valgt verdi med ord. Visning er 20 px stjerner med `aria-hidden` og teksten «4,9 av 5, 11 vurderinger», avrundet til nærmeste hele stjerne.
- **UX-DR18 Bekreftelsesdialoger:** Native `<dialog>` med `showModal()`, fokus på spørsmålet, Tab holdt inne, Esc angrer og fokus tilbake til knappen (eller kvitteringen). Innholdet ruller inne i dialogen. Fem dialoger med tekstene i EXPERIENCE.md (velge, avbryte, fjerne, trekke seg, utført). Uten JS: en GET-bekreftelsesside. Slett konto er en egen side.
- **UX-DR19 KI-forslagsboks:** Rekkefølgen er beskrivelse → «Få forslag» → KI-teksten → forslag eller feil. Én stiplet boks per felt med «Bruk» og «Ikke bruk», og tipset står inne i beskrivelsesboksen. Et nytt trykk erstatter alle boksene. Fokus går til feltet etter «Bruk» eller «Ikke bruk». `aria-live` for «Lager forslag …» og «Forslagene er klare.», og feil med `role="alert"`.
- **UX-DR20 Telefonboks:** Motpartens navn og nummer som `tel:`-lenke med 48 px trykkflate og «Avtal detaljene direkte.»
- **UX-DR21 Tomtilstander:** Ikon, forklaring og én vei videre, med tekstene i EXPERIENCE.md for oversikten (med og uten kategori), ingen interesserte, tom fane (begge), ingen vurderinger og ingen fullførte oppdrag.
- **UX-DR22 Meldinger:** Feiloppsummering («Skjemaet har N feil», lenker til feltene, `tabindex="-1"`, aldri `role`). Kvittering rett etter `h1` som blir stående til neste side. Feilmelding med «Last siden på nytt» ved konflikt.
- **UX-DR23 Faner:** To lenker med egen adresse (`?fane=…`) og `aria-current="page"` på aktiv fane (menyvalget har da `"true"`). Den første fanen som åpnes, er den med «Trenger handling». Fanen har fullt navn med antall.

**Flater og atferd**

- **UX-DR24 Filtrene i oversikten:** Kategorilenker uten egen knapp. Antallslinja «4 ledige oppdrag i 0571 Oslo» med `aria-describedby` fra valgt lenke eller felt. Postnummerfelt med poststed og «Vis» (eller Enter), og ved ugyldig verdi står lista uendret. Fokus går til valgt kategori etter sidelasting.
- **UX-DR25 Oppdragsdetaljer etter rolle og status:** Tabellen i EXPERIENCE.md bestemmer hva som står nederst og hvilke handlinger som finnes for annen innlogget, interessert, fjernet hjelper, oppdragsgiver (Åpen, passert, Hjelper valgt), valgt hjelper og begge parter ved Utført og Avbrutt. Oppdragsgiverblokken («Lagt ut av Kari») vises ikke for oppdragsgiveren selv. «Velg hjelper» står rett under «N har meldt interesse».
- **UX-DR26 Mine oppdrag:** Linja «N oppdrag trenger at du gjør noe.» Radene i «Oppdrag jeg har lagt ut» viser «3 har meldt interesse», «Ingen har meldt interesse ennå» eller «Hjelper: Amir». Raden «Tidspunktet er passert» har snarveiene «Endre tidspunkt» og «Avbryt oppdrag». Rader med «bare tittel og status» er ikke lenker.
- **UX-DR27 Fokus og opplesning:** Tabellen i EXPERIENCE.md. Høyst ett `autofocus` per side, i rekkefølgen feiloppsummering > feilmelding > kvittering > sidens eget mål. `aria-live`, `role="status"` og `role="alert"` bare på fragmenter som JS setter inn. «Endre tidspunkt» gir fokus på «Dato».
- **UX-DR28 Sending:** Knappen som sendte, får `aria-disabled` til svaret kommer, Enter stoppes, og tilstanden nullstilles ved `pageshow`.
- **UX-DR29 Mikrotekst:** De ordrette tekstene fra PRD-en, tekstene fra skissene som beholdes, forslagstekstene og feiltekstene ved felt i EXPERIENCE.md. Formatene: «I morgen kl. 07:00» og «Lørdag 14. nov. kl. 12:00», «1 000 kr» og «Uten betaling», postnummer alltid med poststed, «4,3 av 5, 7 vurderinger» og «12 fullførte oppdrag».
- **UX-DR30 Ikke tillatt:** Skjulte funksjoner (hamburgermeny, menyer med tre prikker, ikonknapper), sveip og lange trykk, hover som eneste måte, uendelig rulling og karuseller, meldinger som forsvinner, automatisk innsending, interaktive elementer inne i lenker, myk rulling med `prefers-reduced-motion` og låst skjermretning.

**Testing av universell utforming (inkludert testhullene fra `review-accessibility.md`)**

- **UX-DR31 T1, automatisk med axe:** Ingen funn på nivåene «serious» eller «critical» på alle sidene og tilstandene i T1 (oversikt med treff og tom, nytt oppdrag steg 1, steg 2 og én skjerm, KI-forslag og KI-feil, detaljer for oppdragsgiver med og uten interesserte, for interessert og for valgt hjelper, tilbakemelding, Mine oppdrag i begge faner og tom, profil, registrering, innlogging, rediger profil, skjema med feil, feilside, slettet bruker og de fem dialogene pluss slett konto). Ingen vannrett rulling ved 320 px.
- **UX-DR32 T2–T6, manuelle protokoller i `docs/tester/`:** T2 tastatur gjennom UJ-1, UJ-2 **og støtteflytene** (registrering, innlogging, rediger profil, slett konto), med kontroll av felttyper og `autocomplete`. T3 skjermleser gjennom UJ-1, UJ-2 steg 3–6, et skjema med feil og en kvittering. T4 ved 360, 768 og 1280 px, **320 px, 200 % zoom, tekstavstand etter WCAG 1.4.12, 200 % tekst i operativsystemet** og liggende telefon. T5 **kontrast på kanter, fokusring og tilstander (1.4.11)**, som axe ikke sjekker, og én gjennomgang med gråtoner eller tvungne farger. T6 brukertest (SM-4).

### FR Coverage Map

| Krav | Epic | Kort |
|---|---|---|
| FR-1 | Epic 1 | Registrere konto |
| FR-2 | Epic 1 | Logge inn og ut (enkel profilside med «Logg ut»; full profil i Epic 4) |
| FR-3 | Epic 1 | Innlogging kreves |
| FR-4 | Epic 4 | Slette egen konto (berører alle tabellene) |
| FR-5 | Epic 2 | Legge ut oppdrag |
| FR-6 | Epic 2 | Redigere oppdrag («Meldt før endring» vises i Epic 3, når interesser finnes) |
| FR-7 | Epic 2 | Avbryte oppdrag (avbrudd fra Hjelper valgt testes i Epic 3) |
| FR-8 | Epic 2 | Utgåtte oppdrag, med merket i grunnversjonen av «Mine oppdrag» |
| FR-9 | Epic 2 | Innsyn i oppdragsdetaljer |
| FR-10 | Epic 2 | Oppdragsoversikt |
| FR-11 | Epic 2 | Filtrere oppdrag |
| FR-12 | Epic 3 | Melde interesse |
| FR-13 | Epic 3 | Trekke interesse |
| FR-14 | Epic 3 | Se interesserte |
| FR-15 | Epic 3 | Velge hjelper |
| FR-16 | Epic 3 | Dele telefonnummer |
| FR-17 | Epic 3 | Fjerne hjelper eller trekke seg |
| FR-18 | Epic 2 → 3 → 4 | Mine oppdrag. Epic 2 har en grunnversjon av «Oppdrag jeg har lagt ut» (liste med status og tidspunkt, og merket «Tidspunktet er passert»), slik at oppdragsgiveren finner egne oppdrag. Epic 3 har hjelper-fanen, de andre merkene, gruppene og antallet i menyen. Epic 4 legger til «Er jobben gjort?» og «Gi tilbakemelding» |
| FR-19 | Epic 4 | Markere som utført |
| FR-20 | Epic 4 | Gi tilbakemelding |
| FR-21 | Epic 4 | Vise profil |
| FR-22 | Epic 4 | Redigere egen profil (Bør) |
| FR-23 | Epic 5 | Be om forslag (Bør) |
| FR-24 | Epic 5 | Bruke eller forkaste forslag (Bør) |
| FR-25 | Epic 5 | Kontroll av KI-svar (Bør) |
| FR-26 | Epic 5 | Mock-modus (Bør) |

| Kvalitetskrav | Epic |
|---|---|
| NFR-1 | Epic 1 (README og lokal kjøring), Epic 6 (test på ren maskin, SM-3) |
| NFR-2 | Epic 1 (seed-grunnlag), utvides i hver epic; fullstendig sjekk i Epic 4 |
| NFR-3 | Epic 1 (`.env.example`, `.gitignore`, gitleaks i CI), Epic 6 (dokumentert skanning) |
| NFR-4 | Epic 1 |
| NFR-5, NFR-8, NFR-10, NFR-12 | Alle epics (Definition of Done); mekanismene (AD-5, AD-11, feilhandlere) i Epic 1 |
| NFR-6, NFR-7 | Alle epics (T1 med axe for nye sider); T2–T5 i Epic 6 |
| NFR-9 | Epic 1 (datamodell for bruker), Epic 4 (sletting), gjennomgang i Epic 6 |
| NFR-11 | Epic 1 (meny), Epic 3 (antallet ved «Mine oppdrag») |
| SM-4 (T6) | Epic 6 |

**Definition of Done for hver story:** akseptansekriteriene er oppfylt og testet automatisk der det er mulig; regler testes direkte mot serveren (NFR-5) inkludert dobbel innsending der det gjelder; ugyldig input gir forståelige meldinger (NFR-10); tekst vises som tekst (NFR-12); nye sider og tilstander er med i T1 (axe) og har ingen vannrett rulling ved 320 px; den nye flaten er sjekket med tastatur i cirka fem minutter (Tab gjennom alt, synlig fokus, dialoger og skjema virker; dette er ikke den fullstendige T2-protokollen); seed dekker det nye (NFR-2); ingen av mønstrene i UX-DR30 (skjulte funksjoner, hover som eneste måte, meldinger som forsvinner, interaktive elementer i lenker osv.) er brukt; README er oppdatert; én Alembic-migrering hvis skjemaet endres (AD-13); commits og tester oppgir krav-ID-ene.

## Epic List

**Tidsramme:** Frist 15. desember 2026; målet er å være ferdig noen dager før. **Arbeidsfordeling:** Den kritiske veien er lagt opp slik at én person kan fullføre den. Oppgaver som ikke blokkerer noe (testprotokoller, brukertest, README-test, gjennomlesing av PR-er), kan tas av hvem som helst i gruppen. Blir tiden knapp, kuttes Epic 5 (Bør) først, deretter FR-22, og infrastruktur etter kuttlista i AR-11. Hvert kutt føres i PRD §9.2.

**Avhengigheter:** Epic 1 → 2 → 3 → 4. Epic 5 kan starte etter Epic 2. Epic 6 kommer til slutt og er uavhengig av Epic 5. Innad i en epic kan flere jobbe parallelt når første story er ferdig.

### Epic 1: Konto og innlogging
En person kan registrere seg, logge inn og logge ut, og alt annet i appen krever innlogging. Appen kjører lokalt med eksempeldata og i produksjon på Vercel med Supabase. Første story er skjelettet som går helt gjennom kjeden (AR-1), med Vercel og Supabase. **Tidsramme:** Virker ikke produksjonspubliseringen etter cirka én dag med feilsøking, deles storyen. Skjelettet merges med lokal kjøring og CI, og publiseringen blir en egen story. Publiseringen går fra Actions med `VERCEL_TOKEN`, så Vercels GitHub-app trengs ikke (det bekreftes i et akseptansekriterium).
**FRs covered:** FR-1, FR-2, FR-3
**Også:** NFR-1, NFR-3, NFR-4, NFR-11 (meny); AR-1–AR-10, AR-14–AR-17, AR-21, AR-25–AR-30; UX-DR1–UX-DR7, UX-DR12, UX-DR13, UX-DR22, UX-DR27–UX-DR30; infrastruktur for T1.

### Epic 2: Legge ut og finne oppdrag
Kari kan legge ut, redigere og avbryte oppdrag. Amir finner åpne oppdrag i sitt postnummer, filtrerer på kategori og postnummer, og åpner detaljene.
**FRs covered:** FR-5, FR-6, FR-7, FR-8, FR-9, FR-10, FR-11, og en grunnversjon av FR-18 («Oppdrag jeg har lagt ut» med status, tidspunkt og merket «Tidspunktet er passert»), slik at Kari finner egne oppdrag igjen når FR-10 skjuler dem i oversikten
**Også:** AR-12, AR-13, AR-17 (fullstendig AD-7, story 2.6), AR-19, AR-20, AR-28 (`skjema.js`, `steg.js`, `fokus.js`, `dialog.js`, `sending.js`); UX-DR8–UX-DR11, UX-DR14–UX-DR16, UX-DR18 (dialogkomponenten, først brukt for «Avbryt oppdrag»), UX-DR21, UX-DR24–UX-DR26.

### Epic 3: Interesse, valg av hjelper og Mine oppdrag
Amir melder interesse. Kari ser de interesserte, sammenligner erfaring og velger hjelper, og de ser hverandres telefonnummer. Hjelperen kan fjernes eller trekke seg. Begge følger oppdragene sine under «Mine oppdrag» med situasjoner, merker, grupper og antallet i menyen.
**FRs covered:** FR-12, FR-13, FR-14, FR-15, FR-16, FR-17, FR-18 (bygger videre på grunnversjonen fra Epic 2: hjelper-fanen, merkene, gruppene og antallet i menyen)
**Også:** NFR-11 (antallet); AR-12 (`tidligere_hjelper`), AR-13, AR-24; UX-DR9, UX-DR18 (dialogene for å velge, fjerne og trekke seg), UX-DR20, UX-DR23, UX-DR26.

### Epic 4: Fullføre, gi tilbakemelding og vise erfaring
Oppdraget markeres som utført, og partene gir hverandre stjerner og kommentar. Amir har en profil med fullførte oppdrag og tilbakemeldinger han kan vise fram. Brukeren kan redigere profilen sin og slette kontoen.
**FRs covered:** FR-19, FR-20, FR-21, FR-22, FR-4 (og merkene «Er jobben gjort?» og «Gi tilbakemelding» i FR-18)
**Også:** NFR-2 (full sjekk av alle situasjoner), NFR-9; AR-18; UX-DR17.

### Epic 5: KI-forslag (Bør)
Kari kan få forslag til tittel, kategori og beskrivelse når hun legger ut et oppdrag. Mock er standard, og appen fungerer fullt ut uten KI.
**FRs covered:** FR-23, FR-24, FR-25, FR-26
**Også:** AR-22, AR-23, AR-28 (`ki.js`); UX-DR19.

### Epic 6: Klar for sensur
En person utenfor gruppen får appen i gang fra README på en ren maskin, og testene for universell utforming og brukertesten er gjennomført og dokumentert.
**FRs covered:** ingen nye
**Også:** NFR-1 (SM-3), NFR-3 (dokumentert gitleaks), NFR-6, NFR-7 (T2–T5), NFR-9 (gjennomgang av skjemaet), SM-4 (T6); UX-DR31, UX-DR32.

---

## Epic 1: Konto og innlogging

En person kan registrere seg, logge inn og logge ut, og alt annet i appen krever innlogging. Appen kjører lokalt med eksempeldata og i produksjon på Vercel med Supabase. Story 1.1 og 1.2 er skjelettet (AR-1), og ingen andre stories starter før begge er ferdige.

### Story 1.1: Skjelett – appen kjører lokalt og i CI

Som utvikler i gruppen
vil jeg ha en app som starter lokalt med én kommando og testes automatisk i CI,
slik at alle senere stories bygger på samme kjerne, de samme reglene og den samme strukturen.

**Krav:** AR-1, AR-2, AR-3, AR-4, AR-5, AR-6, AR-7 (ci.yml), AR-8, AR-15, AR-21, AR-25, AR-26, AR-27, AR-29, AR-30, NFR-1, NFR-3, NFR-10, NFR-12; UX-DR1, UX-DR2, UX-DR4, UX-DR6

**Acceptance Criteria:**

**Gitt** en ren maskin med Python 3.12 og uv
**Når** utvikleren følger README (`uv sync`, `uv run python -m app.seed` og kommandoen som starter appen)
**Så** starter appen mot en SQLite-fil uten `.env`, uten kontoer og uten nøkler (NFR-1, AD-14)
**Og** `uv run python -m app.seed` kjører `alembic upgrade head` først.

**Gitt** at `APP_ENV` har en ukjent verdi, eller er `production` uten en ekte `SECRET_KEY`
**Når** appen starter
**Så** stopper oppstarten med en tydelig melding i loggen (AD-14).

**Gitt** en tom database
**Når** `alembic upgrade head` kjøres
**Så** finnes tabellen `postnummer` med alle postnumrene fra `data/postnumre.tsv` (UTF-8, konvertert fra Brings register)
**Og** `core/postnummer.py` gir `finnes("0571") == True` og `poststed("0571") == "Oslo"`, og et ukjent nummer gir `finnes == False` (AD-1, AD-10)
**Og** `core/static/postnumre.json` er generert av `uv run python -m app.core.postnummer`, og en test sjekker at fila stemmer med TSV-fila
**Og** migreringen lager også tabellene `bruker` og `sesjon`, som mellomvaren trenger for å slå opp innlogging (AD-4).

**Gitt** at appen kjører
**Når** en nettleser åpner `/logg-inn`
**Så** vises innloggingssiden, rendret med `core.render` og `base.html`, med `lang="nb"`, `<title>` «Logg inn – Nabolagshelten», landemerkene `header` og `main`, lenken «Hopp til innholdet» som første fokuserbare element, og en topplinje med bare logoen (UX-DR2)
**Og** stilarket har designtokenene fra DESIGN.md som CSS-variabler, `color-scheme: light` og systemskrifter. Fokusringen følger UX-DR4 (UX-DR1, UX-DR4).

**Gitt** en hvilken som helst forespørsel
**Når** svaret sendes
**Så** har det headerne `Content-Security-Policy: frame-ancestors 'none'`, `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff` og `Referrer-Policy: same-origin` (AD-5).

**Gitt** et skjema på siden
**Når** det sendes med POST uten gyldig CSRF-nøkkel, eller med `Origin` fra et annet nettsted
**Så** avvises forespørselen med en vennlig feilside, og ingen data endres (NFR-12, AD-5)
**Og** når CSRF-nøkkelen stemmer, får ruta skjemafeltene, selv om CSRF-mellomvaren allerede har lest kroppen (ren ASGI-mellomvare som spiller av kroppen på nytt; prøves ut her)
**Og** en test sjekker rekkefølgen på mellomvaren: feilhåndtering → headere → CSRF/Origin → sesjon → ruter.

**Gitt** en sti som ikke finnes, eller en uventet feil i en rute
**Når** siden vises
**Så** ser brukeren «Fant ikke siden» eller «Noe gikk galt. Prøv igjen om litt.» med en vei videre, aldri en stack trace eller teknisk feilmelding (NFR-10, AR-26).

**Gitt** kildekoden
**Når** `uv run pytest` kjøres
**Så** passerer `tests/core/test_arkitektur.py`, som sjekker importretningen i AD-1 og at `|safe`, `Markup(` og `innerHTML` ikke finnes i `app/` (AD-11)
**Og** testene for headere, CSRF og rekkefølgen på mellomvaren passerer
**Og** `tests/conftest.py` har fabrikkene og `sett_na`, og hver test rulles tilbake (AR-29).

**Gitt** en PR mot `main`
**Når** CI kjører (`ci.yml`)
**Så** kjører pytest mot SQLite og mot en Postgres-container, `alembic heads` gir nøyaktig én linje, og gitleaks skanner hele historikken (AR-7, NFR-3)
**Og** `main` er beskyttet, slik at bare PR-er med grønn CI kan merges.

**Gitt** repoet
**Når** det sjekkes
**Så** har `.env.example` alle variablene i AR-8 uten ekte verdier, og `.gitignore` holder ute `.env`, `.venv`, `.vercel/` og byggmapper (NFR-3)
**Og** README har forutsetninger med versjoner, eksakte kommandoer for å starte appen og kjøre testene, og kildelinja «Postnummerdata fra Posten Bring, lisensiert under NLOD 2.0.» (NFR-1, AR-10).

### Story 1.2: Skjelett – appen publiseres i produksjon

Som gruppe
vil vi at hver merge til `main` publiseres automatisk til Vercel med database hos Supabase, med migrering først,
slik at appen alltid finnes i en kjørende versjon, og problemer med produksjonsmiljøet oppdages i uke én.

**Krav:** AR-1, AR-4, AR-7 (deploy.yml, keepalive.yml, vercel.json), AR-8, AR-10, AD-13, AD-14

**Acceptance Criteria:**

**Gitt** et Supabase-prosjekt (Free) og et Vercel-prosjekt som Heidi eier
**Når** hemmelighetene er lagt inn (`DATABASE_URL`, `SECRET_KEY` og eventuelt `OPENROUTER_*` i Vercel env, og `MIGRATION_DATABASE_URL` og `VERCEL_*` i GitHub Secrets)
**Så** ligger ingen av dem i repoet eller i chatten, og README § Kontoer for drift sier hvem som eier kontoene (NFR-3, AR-8).

**Gitt** en merge til `main`
**Når** `deploy.yml` kjører
**Så** kjøres `alembic upgrade head` mot Supabase gjennom session pooler (port 5432) først, og `vercel deploy --prod` kjøres bare hvis migreringen lykkes (AD-13)
**Og** publiseringen lykkes uten at Vercels GitHub-app er installert på organisasjonen.

**Gitt** `vercel.json`
**Når** det leses
**Så** er automatisk publisering fra Git og preview slått av, og `functions."main.py".maxDuration` er 30.

**Gitt** produksjonsversjonen
**Når** `/logg-inn` åpnes
**Så** vises innloggingssiden med sikkerhetsheaderne
**Og** et skjema sendt med feil e-post viser «Feil e-post eller passord.» (eller en tilsvarende side som går gjennom CSRF-mellomvaren, lesing av kroppen og et databaseoppslag via transaction pooler, port 6543, `NullPool`). Det bekrefter at ASGI-kroppen og databasen virker på Vercel
**Og** `/_test/tilstand` gir 404, og det finnes ingen demokontoer i produksjon (AD-14).

**Gitt** at appen har vært uten trafikk
**Når** `keepalive.yml` kjører hver tredje dag
**Så** besøker den produksjonsversjonen, slik at Supabase ikke pauses
**Og** README sier at eieren sjekker Supabase før demo og innlevering.

**Gitt** at produksjonspubliseringen ikke virker etter cirka én dag med feilsøking
**Når** gruppen vurderer det
**Så** føres problemet som åpent punkt, story 1.3 kan starte, og publiseringen fullføres som egen oppgave før Epic 6. Det føres i memlog og i PRD §9.2.

### Story 1.3: Logge inn og ut

Som bruker med konto
vil jeg logge inn med e-post og passord, se menyen og logge ut,
slik at bare jeg får tilgang til innholdet mitt.

**Krav:** FR-2, FR-3, NFR-4, NFR-5, NFR-11, AR-14, AR-16, AR-17 (enkel 401-side), AR-9, NFR-2 (testbrukere); UX-DR3, UX-DR7, UX-DR12, UX-DR13 (Vis passord), UX-DR22, UX-DR27, UX-DR28

**Acceptance Criteria:**

**Gitt** at eksempeldataene er lastet (`uv run python -m app.seed`)
**Når** README leses
**Så** finnes minst 6 testbrukere i 2–3 postnumre, med e-post og passord merket «bare for lokal testing» og en kort beskrivelse av hva hver bruker brukes til (NFR-2)
**Og** passordene ligger bare som bcrypt-hash i databasen (`hash_passord`: NFC, ingen trim, bcrypt over base64(SHA-256)), og en test sjekker at passordfeltet ikke inneholder passordet (NFR-4, AD-6).

**Gitt** innloggingssiden
**Når** en testbruker skriver riktig e-post (også med store bokstaver eller mellomrom rundt) og passord og trykker «Logg inn»
**Så** er brukeren innlogget og havner på oversikten («/») eller på den lokale siden i `neste`
**Og** sesjonen er en tilfeldig nøkkel i en HttpOnly-cookie med `SameSite=Lax` (`Secure` i produksjon), lagret i `sesjon` og gyldig i høyst 7 dager (FR-2, AD-4)
**Og** `neste` godtas bare når den begynner med `/` og ikke med `//`.

**Gitt** feil e-post eller feil passord
**Når** brukeren prøver å logge inn
**Så** vises samme melding, «Feil e-post eller passord.», og e-posten er beholdt mens passordfeltet er tømt (FR-2, UX-DR12).

**Gitt** 5 mislykkede forsøk med samme e-post innen 15 minutter
**Når** det sjette forsøket kommer, også med riktig passord
**Så** avvises det med «For mange mislykkede forsøk. Prøv igjen om 15 minutter.»
**Og** etter 15 minutter kan brukeren logge inn igjen, og en vellykket innlogging rydder tellerne (FR-2, AD-4). Testet med `sett_na`.

**Gitt** en innlogget bruker
**Når** en side vises
**Så** har siden menyen med Oppdrag, Mine oppdrag og Profil: i topplinjen fra 768 px og som bunnmeny under 768 px, med aktivt valg markert med fet skrift, strek og `aria-current` (NFR-11, UX-DR3)
**Og** «Oppdrag» viser oversikten med overskriften «Ledige oppdrag i <postnummer> <poststed>» og tomtilstanden fra EXPERIENCE.md. «Mine oppdrag» viser tomtilstanden for fanen «Oppdrag jeg har lagt ut». «Profil» viser navn, postnummer med poststed og knappen «Logg ut». Epic 2 og Epic 4 bygger videre på disse sidene.

**Gitt** en innlogget bruker på profilen
**Når** hen trykker «Logg ut»
**Så** slettes sesjonen, brukeren havner på innloggingssiden med kvitteringen «Du er logget ut.», og tilbakeknappen gir ikke tilgang til innhold (FR-2).

**Gitt** en forespørsel uten gyldig innlogging
**Når** den er en GET til en rute som ikke er merket offentlig
**Så** gir den 303 til `/logg-inn?neste=<sti>`
**Og** en POST gir 401-siden «Du må logge inn igjen.» med lenke til innlogging og uten innhold fra databasen (enkel versjon av AD-7; den fullstendige kommer i story 2.6)
**Og** en automatisk test går gjennom alle ruter i appen uten innlogging og forventer 303 for GET og 401 for POST, unntatt rutene som er merket offentlige på selve ruta (FR-3, AD-4).

**Gitt** innloggingsskjemaet
**Når** det brukes
**Så** har feltene synlige etiketter, `type` og `autocomplete` etter tabellen i EXPERIENCE.md (`email`, `current-password`), «Vis passord» med `aria-pressed`, og knappen er `aria-disabled` mens forespørselen pågår (UX-DR12, UX-DR13, UX-DR28)
**Og** ved feil får feiloppsummeringen fokus, og `<title>` får «Feil: » foran (UX-DR22, UX-DR27).

**Gitt** en bruker som har glemt passordet
**Når** gruppen hjelper manuelt
**Så** setter `uv run python -m app.admin nytt-passord <e-post>` et nytt passord med de samme funksjonene (AR-9). `slett-konto` kommer i story 4.5.

### Story 1.4: Registrere konto

Som person uten konto
vil jeg registrere meg med navn, e-post, passord, telefonnummer, postnummer og fødselsdato,
slik at jeg kan bruke Nabolagshelten.

**Krav:** FR-1, NFR-9, NFR-10, AR-16, AR-19 (fødselsdato og «i dag» i Europe/Oslo), AR-20; UX-DR12, UX-DR13, UX-DR29

**Acceptance Criteria:**

**Gitt** innloggingssiden
**Når** brukeren trykker lenken til registrering
**Så** vises «Registrering» med feltene Navn, E-post, Passord, Telefonnummer, Postnummer og Fødselsdato, med `type` og `autocomplete` etter tabellen i EXPERIENCE.md, og knappen «Opprett konto»
**Og** over knappen står personvernteksten fra FR-1: hva som lagres, at navn, postnummer og profil vises for alle innloggede, at telefonnummeret bare deles med motparten når en hjelper er valgt, at beskrivelsen av et oppdrag kan sendes til en ekstern KI-tjeneste, og at kontoen kan slettes (FR-1, NFR-9).

**Gitt** gyldige verdier
**Når** brukeren trykker «Opprett konto»
**Så** opprettes kontoen med normalisert e-post (trim, NFC, små bokstaver) og telefonnummer lagret som åtte siffer, brukeren er innlogget og havner på oversikten (FR-1, AD-6, §4.0).

**Gitt** grenseverdiene i FR-1
**Når** skjemaet sendes
**Så** godtas navn med 1 og 80 tegn og avvises med 0 og 81 (etter trim og NFC). Passord med 8 og 64 tegn godtas, og 7 og 65 avvises. Telefon godtas som «91234567», «912 34 567», «+47 912 34 567» og «0047 91234567», og andre formater avvises. Et postnummer som ikke finnes i lista, avvises (FR-1, §4.0)
**Og** hver feil vises ved feltet med teksten fra EXPERIENCE.md § Feiltekster ved felt, alle feilene vises samtidig i feiloppsummeringen, og alt utfylt er beholdt, unntatt passord, som har hjelpeteksten «Skriv passordet på nytt.» (NFR-10, UX-DR12).

**Gitt** en fødselsdato
**Når** alderen regnes ut i norsk tid
**Så** godtas den som fyller 18 i dag, mens den som fyller 18 i morgen, avvises med «Du må være minst 18 år for å bruke Nabolagshelten.»
**Og** den som er født 29. februar, fyller år 1. mars i år som ikke er skuddår
**Og** en dato fram i tid eller mer enn 120 år tilbake gir «Sjekk fødselsdatoen.», og et ugyldig format gir eksemplet «dd.mm.åååå, for eksempel 03.05.1954». Tosifret år tolkes som året som gir en alder mellom 0 og 120 (FR-1, AD-9). Testet med `sett_na`.

**Gitt** en e-post som allerede er i bruk, også med andre store og små bokstaver
**Når** skjemaet sendes
**Så** avvises det med «Det finnes allerede en konto med denne e-posten.» (FR-1)
**Og** to samtidige registreringer med samme e-post gir bare én konto (unik-constraint på `bruker.epost`, AD-2).

**Gitt** registreringsskjemaet med JavaScript
**Når** brukeren skriver et gyldig postnummer
**Så** vises poststedet ved feltet (fra `postnumre.json`), og «Vis passord» virker som på innloggingssiden (UX-DR13)
**Og** uten JavaScript vises poststedet etter innsending.

**Gitt** at registreringen er ferdig
**Når** databasen sjekkes
**Så** inneholder `bruker` bare navn, e-post, passord-hash, telefon, postnummer, fødselsdato og tidspunkter, ingen adresse (NFR-9).

### Story 1.5: Automatisk test av universell utforming

Som bruker som navigerer med tastatur eller skjermleser
vil jeg at hver side testes automatisk for vanlige tilgjengelighetsfeil,
slik at feil oppdages med en gang og ikke rett før innlevering.

**Krav:** NFR-6, NFR-7, SM-5, AR-29 (E2E og `/_test/tilstand`); UX-DR5, UX-DR31

**Acceptance Criteria:**

**Gitt** `APP_ENV=test`
**Når** E2E-testene starter
**Så** kan de kalle `POST /_test/tilstand` for å sette klokka, velge KI-utgave og laste eksempeldataene på nytt. I `local` og `production` finnes ikke ruta (AD-14).

**Gitt** sidene som finnes etter Epic 1 (innlogging, innlogging med feil, registrering, registrering med valideringsfeil, oversikt med tomtilstand, Mine oppdrag med tom fane, egen profil, feilside og 401-siden)
**Når** T1 kjøres med Playwright og axe ved 360 og 1280 px
**Så** finnes ingen brudd på nivåene «serious» eller «critical» (SM-5)
**Og** ved 320 px er det ingen vannrett rulling (`scrollWidth <= clientWidth`) (NFR-7, UX-DR5).

**Gitt** CI
**Når** en PR kjøres
**Så** kjører T1 som en del av CI, og README sier hvordan testen kjøres lokalt.

**Gitt** en senere story som lager en ny side eller tilstand
**Når** storyen er ferdig
**Så** er siden lagt til i T1. Det følger av Definition of Done, og lista i T1 i EXPERIENCE.md er målet når Epic 4 er ferdig.

---

## Epic 2: Legge ut og finne oppdrag

Kari kan legge ut, redigere og avbryte oppdrag og finne dem igjen under «Mine oppdrag». Amir finner åpne oppdrag i sitt postnummer, filtrerer på kategori og postnummer, og åpner detaljene.

### Story 2.1: Legge ut oppdrag

Som oppdragsgiver
vil jeg legge ut et oppdrag med tittel, beskrivelse, kategori, postnummer, tidspunkt og godtgjørelse,
slik at naboer i postnummeret mitt kan se at jeg trenger hjelp.

**Krav:** FR-5, FR-9 (detaljer for oppdragsgiveren), NFR-9, NFR-10, AR-12 (statusfunksjonen og `skjema_id`), AR-19, AR-20; UX-DR10 (statusmerke og kategorimerke), UX-DR11 (skjema), UX-DR12, UX-DR13 (teller), UX-DR14, UX-DR29

**Acceptance Criteria:**

**Gitt** en innlogget bruker på oversikten
**Når** hen trykker «+ Legg ut oppdrag»
**Så** vises «Nytt oppdrag» på én skjerm med Beskrivelse (med hjelpeteksten «Ikke skriv adresse eller telefonnummer – det avtaler dere når hjelperen er valgt.»), Tittel, Kategori (seks store radioknapper), Postnummer (forhåndsutfylt fra profilen og mulig å endre), «Når?» (Dato og Klokkeslett) og «Hva tilbyr du?» («Beløp» med «Beløp i kr», eller «Uten betaling»), og knappen «Publiser» (FR-5, UX-DR11, UX-DR14)
**Og** menyvalget «Mine oppdrag» er markert med `aria-current="true"`.

**Gitt** gyldige verdier
**Når** brukeren trykker «Publiser»
**Så** lagres oppdraget med status `apen`, brukeren som oppdragsgiver, kategorien som kode og tidspunktet i UTC (AD-2, AD-9, AD-10)
**Og** brukeren havner på detaljene for oppdraget med kvitteringen «Oppdraget er lagt ut.» i fokus. Detaljene viser alle feltene, statusmerket «Åpen» og tidspunktet som «I morgen kl. 07:00» eller «Lørdag 14. nov. kl. 12:00», og beløpet som «1 000 kr» eller «Uten betaling» (FR-9, UX-DR29).

**Gitt** grenseverdiene i FR-5
**Når** skjemaet sendes
**Så** godtas tittel med 3 og 80 tegn og avvises med 2 og 81, og beskrivelse med 10 og 1000 tegn godtas mens 9 og 1001 avvises (etter trim og NFC, og felt med bare mellomrom regnes som tomme). Beløp 1 og 10 000 godtas, mens 0, 10 001, desimaltall og tekst avvises. «Uten betaling» lagres som NULL. Manglende kategori eller valg under «Hva tilbyr du?» avvises (FR-5, AD-10)
**Og** hver feil vises ved feltet med teksten fra EXPERIENCE.md, alle feilene vises samtidig i feiloppsummeringen, alt utfylt beholdes, og ingenting lagres (NFR-10).

**Gitt** feltene «Dato» og «Klokkeslett»
**Når** brukeren skriver tidspunktet
**Så** godtas «14.11.2026», «14/11/26», «14-11-2026» og «14 11 2026» som dato, og «07:00», «7», «0700» og «7.00» som klokkeslett. Tosifret år betyr 20xx (AD-9)
**Og** et tidspunkt som er passert, gir «Velg et nytt tidspunkt fram i tid», og et tidspunkt mer enn 12 måneder fram gir «Velg et tidspunkt høyst 12 måneder fram i tid.», under gruppen «Når?» (FR-5)
**Og** 02:30 natt til siste søndag i mars avvises med melding ved feltet, 02:30 natt til siste søndag i oktober tolkes som det første klokkeslettet, og et lagret oppdrag vises med samme dato og klokkeslett før og etter skiftet. En tabelltest i `core/tid.py` dekker alle skrivemåtene og rundturen over skiftene (FR-5, AD-9).

**Gitt** at brukeren trykker «Publiser» to ganger, eller sender det samme skjemaet på nytt
**Når** serveren mottar den andre innsendingen med samme `skjema_id`
**Så** lagres bare ett oppdrag, og brukeren sendes til oppdraget som finnes (`Duplikat`, AD-2)
**Og** knappen er `aria-disabled` mens forespørselen pågår (UX-DR28).

**Gitt** tekstområdene Beskrivelse
**Når** brukeren skriver
**Så** vises telleren «37 av 1000 tegn», som teller kodepunkter etter NFC og trim, og leses opp bare når grensen nås. Feltet har ikke `maxlength` (AD-10, UX-DR13).

**Gitt** et oppdrag
**Når** tittelen eller beskrivelsen inneholder `<script>alert(1)</script>`
**Så** vises teksten som tekst på detaljene (NFR-12).

**Gitt** eksempeldataene
**Når** `uv run python -m app.seed` kjøres
**Så** finnes 10–15 oppdrag med tidspunkter regnet fra når dataene lastes, med åpne oppdrag i alle seks kategorier, minst ett utgått oppdrag og minst ett avbrutt (NFR-2). Situasjonene som krever interesser og tilbakemeldinger, legges til i Epic 3 og Epic 4.

### Story 2.2: Nytt oppdrag i to steg på mobil, med forhåndsvisning

Som oppdragsgiver på mobil
vil jeg fylle ut «Nytt oppdrag» i to korte steg og se hvordan oppdraget vil se ut,
slik at skjemaet ikke blir uoversiktlig på en liten skjerm.

**Krav:** FR-5, NFR-6, NFR-7, AR-28 (`steg.js`, `skjema.js`); UX-DR13 (poststed og «Beløp i kr»), UX-DR15, UX-DR16, UX-DR27

**Acceptance Criteria:**

**Gitt** en skjerm under 768 px med JavaScript
**Når** «Nytt oppdrag» åpnes
**Så** er skjemaet delt i «Nytt oppdrag 1 av 2» (Beskrivelse, Tittel, Kategori, «Neste») og «Nytt oppdrag 2 av 2» (Postnummer, «Når?», «Hva tilbyr du?», forhåndsvisning, «Publiser» og «Tilbake til steg 1»), med `<title>` per steg (UX-DR16)
**Og** «Neste» sjekker feltene i steg 1 og viser feiloppsummeringen der hvis noe mangler. Ellers vises steg 2 med fokus på `h1`. «Tilbake til steg 1» beholder alt utfylt og gir fokus på `h1`.

**Gitt** at serveren finner feil etter «Publiser»
**Når** skjemaet vises på nytt
**Så** lister feiloppsummeringen feil fra begge steg, appen viser steget med første feil, og en lenke til et felt i det andre steget bytter steg (UX-DR16, UX-DR22).

**Gitt** 768 px eller bredere, eller en nettleser uten JavaScript
**Når** «Nytt oppdrag» åpnes
**Så** vises hele skjemaet på én skjerm med `h1` «Nytt oppdrag» og to `h2` (UX-DR16, AR-28).

**Gitt** steg 2 (eller den nederste delen på én skjerm)
**Når** brukeren fyller ut feltene
**Så** viser forhåndsvisningen «Slik vises oppdraget for andre» kortet slik det blir i oversikten, med stiplet kant, uten lenke og uten overskrift, med «–» for tomme felt. Den oppdateres uten opplesning (UX-DR15)
**Og** poststedet vises ved postnummeret, og «Beløp i kr» vises bare når «Beløp» er valgt (med CSS `:has(:checked)`), uten å flytte fokus, og beløpet beholdes ved bytte (UX-DR13).

**Gitt** T1
**Når** testen kjøres
**Så** er steg 1, steg 2 og skjemaet på én skjerm (nettbrett) uten brudd på nivåene «serious» eller «critical» og uten vannrett rulling ved 320 px.

### Story 2.3: Finne oppdrag i oversikten og se detaljene

Som hjelper
vil jeg se åpne oppdrag i postnummeret mitt, filtrere på kategori og postnummer, og åpne detaljene,
slik at jeg raskt finner noe jeg kan hjelpe med.

**Krav:** FR-9, FR-10, FR-11, AR-13 (utgått og `erfaring`), AR-24, AR-27 (filterhjelperen), AR-28 (`fokus.js`); UX-DR5, UX-DR8, UX-DR10, UX-DR21, UX-DR24, UX-DR25 (annen innlogget)

**Acceptance Criteria:**

**Gitt** en innlogget bruker
**Når** oversikten åpnes
**Så** vises overskriften «Ledige oppdrag i 0571 Oslo», antallslinja «4 ledige oppdrag i 0571 Oslo» og oppdragskortene i brukerens postnummer (FR-10)
**Og** bare oppdrag med status Åpen der tidspunktet ikke er passert, vises. Brukerens egne oppdrag vises ikke (FR-8, FR-10)
**Og** sorteringen er etter tidspunkt, tidligste først, og ved likt tidspunkt etter når oppdraget ble lagt ut, eldste først (FR-10)
**Og** hvert kort er én lenke og viser kategori, tittel, tidspunkt, postnummer med poststed og godtgjørelse, i 1, 2 eller 3 kolonner etter skjermbredden (UX-DR5, UX-DR8).

**Gitt** kategoriknappene
**Når** brukeren velger «Hage»
**Så** viser lista bare oppdrag i Hage, adressen er `?kategori=hage`, den valgte lenken har `aria-current="true"`, hake og fet tekst, fokus står på den valgte kategorien, og antallslinja «2 ledige oppdrag i Hage i 0571 Oslo» er knyttet til den med `aria-describedby` (FR-11, UX-DR24)
**Og** «Alle» fjerner kategorifilteret.

**Gitt** postnummerfeltet med knappen «Vis»
**Når** brukeren skriver et annet gyldig postnummer og trykker «Vis» eller Enter
**Så** erstatter det eget postnummer i lista, og kategorifilteret beholdes (FR-11)
**Og** et postnummer som ikke finnes, gir «Finner ikke postnummeret. Sjekk at det har fire siffer.» ved feltet, og lista står uendret (FR-11).

**Gitt** at det ikke er noen treff
**Når** oversikten vises
**Så** vises tomtilstanden fra EXPERIENCE.md: med kategori valgt «Prøv en annen kategori eller et annet postnummer.» og «Vis alle kategorier», og med «Alle» valgt «Prøv et annet postnummer.» og «Velg et annet postnummer», som gir fokus i postnummerfeltet med innholdet markert (FR-10, UX-DR21).

**Gitt** et åpent oppdrag lagt ut av en annen
**Når** en innlogget bruker åpner detaljene
**Så** ser hen alle feltene, status og oppdragsgiverblokken «Lagt ut av Kari» med fullførte oppdrag, snitt («Ingen vurderinger ennå» til Epic 4) og «Se profil» (FR-9, UX-DR25)
**Og** menyvalget «Oppdrag» er markert
**Og** lista over interesserte vises ikke for andre enn oppdragsgiveren (FR-9).

**Gitt** et oppdrag med en annen status enn Åpen
**Når** en annen bruker enn oppdragsgiveren (og valgt hjelper, fra Epic 3) åpner `/oppdrag/{id}`
**Så** vises feilsiden med samme 404-svar som for et oppdrag som ikke finnes (FR-9, AR-26).

**Gitt** HTML-en fra oversikten og detaljene
**Når** testen søker etter testbrukernes telefonnummer, e-post og fødselsdato
**Så** finnes ingen av dem (FR-16, AD-16).

### Story 2.4: Se egne oppdrag under «Mine oppdrag»

Som oppdragsgiver
vil jeg se alle oppdragene jeg har lagt ut, med status og tidspunkt,
slik at jeg finner dem igjen når de ikke vises i oversikten.

**Krav:** FR-18 (grunnversjon av «Oppdrag jeg har lagt ut»), FR-8, AR-13; UX-DR9, UX-DR10, UX-DR21, UX-DR26

**Acceptance Criteria:**

**Gitt** en bruker som har lagt ut oppdrag
**Når** hen åpner «Mine oppdrag»
**Så** vises «Oppdrag jeg har lagt ut» med én lenkerad per oppdrag: tittel, statusmerke, tidspunkt og pil ›. Raden går til detaljene (FR-18, UX-DR9)
**Og** radene står etter tidspunkt, tidligste først.

**Gitt** et eget oppdrag med status Åpen der tidspunktet er passert
**Når** «Mine oppdrag» vises
**Så** har raden merket «Tidspunktet er passert» med skjult tekst «Må gjøres: …», og snarveiene «Endre tidspunkt» og «Avbryt oppdrag» står under raden, utenfor lenken (FR-8, UX-DR10, UX-DR26)
**Og** oppdraget vises ikke i oversikten (FR-8)
**Og** merket beregnes ved lesing fra status, tidspunkt og `klokke.na()`, uten at noe lagres (AD-3). Testet med `sett_na` på begge sider av tidspunktet.

**Gitt** en bruker uten egne oppdrag
**Når** «Mine oppdrag» åpnes
**Så** vises tomtilstanden «Du har ikke lagt ut noen oppdrag.» med lenken «Legg ut oppdrag» (FR-18, UX-DR21).

**Gitt** detaljene for et eget oppdrag
**Når** oppdragsgiveren åpner dem
**Så** er menyvalget «Mine oppdrag» markert, og oppdragsgiverblokken vises ikke (UX-DR25).

### Story 2.5: Redigere og avbryte oppdrag

Som oppdragsgiver
vil jeg endre et åpent oppdrag eller avbryte det,
slik at oppdraget alltid stemmer med det jeg trenger.

**Krav:** FR-6, FR-7, FR-8, NFR-5, NFR-8, AR-12, AR-28 (`dialog.js`, `sending.js`); UX-DR7, UX-DR18 (avbryte), UX-DR27

**Acceptance Criteria:**

**Gitt** et eget oppdrag med status Åpen
**Når** oppdragsgiveren trykker «Rediger»
**Så** vises det samme skjemaet uten KI, med knappen «Lagre endringer» og `<title>` «Rediger «…» – Nabolagshelten». Feltene valideres som i FR-5
**Og** etter lagring vises detaljene med kvitteringen «Endringene er lagret.» (FR-6).

**Gitt** et utgått oppdrag
**Når** oppdragsgiveren trykker «Endre tidspunkt»
**Så** åpnes skjemaet med fokus i feltet «Dato», og oppdraget kan ikke lagres før tidspunktet er fram i tid («Velg et nytt tidspunkt fram i tid»)
**Og** med nytt tidspunkt vises oppdraget igjen i oversikten (FR-6, FR-8, UX-DR27).

**Gitt** en redigering som endrer tidspunkt, godtgjørelse eller postnummer
**Når** den lagres
**Så** settes `oppdrag.vesentlig_endret`. Endring av bare tittel, beskrivelse eller kategori setter den ikke (AD-3). «Meldt før endring» vises i Epic 3.

**Gitt** en annen bruker enn oppdragsgiveren, eller et oppdrag som ikke har status Åpen
**Når** en redigering sendes direkte til serveren
**Så** avvises den, og ingen data endres (FR-6, NFR-5).

**Gitt** et eget oppdrag med status Åpen
**Når** oppdragsgiveren trykker «Avbryt oppdrag»
**Så** åpnes dialogen «Avbryte «…»? Det kan ikke angres.» med «Ja, avbryt oppdraget» og «Behold oppdraget». Fokus går til spørsmålet, Tab holdes i dialogen, og Esc angrer og gir fokus tilbake til knappen (UX-DR18)
**Og** uten JavaScript vises en egen bekreftelsesside med en POST-knapp (AR-28)
**Og** etter bekreftelse er status Avbrutt, kvitteringen «Oppdraget er avbrutt.» vises, og oppdraget kan ikke lenger endres (FR-7).

**Gitt** en annen bruker enn oppdragsgiveren, eller et oppdrag med status Utført eller Avbrutt
**Når** en avbrytelse sendes direkte til serveren
**Så** avvises den (FR-7, NFR-5).

**Gitt** to faner med det samme oppdraget
**Når** oppdragsgiveren avbryter i den ene og redigerer eller avbryter i den andre
**Så** utføres bare den første handlingen, og den andre gir «Oppdraget er endret. Last siden på nytt.» med knappen «Last siden på nytt» (§4.0, AD-2)
**Og** en test sender to samtidige forespørsler og sjekker at bare én lykkes, mot både SQLite og Postgres.

**Gitt** T1
**Når** testen kjøres
**Så** er redigeringsskjemaet og dialogen for å avbryte uten brudd på nivåene «serious» eller «critical».

### Story 2.6: Utfylt skjema går ikke tapt når innloggingen utløper

Som oppdragsgiver som har brukt lang tid på et skjema
vil jeg kunne logge inn igjen uten å miste det jeg har skrevet,
slik at jeg ikke må begynne på nytt.

**Krav:** AD-7 (fullstendig versjon), FR-2, FR-3, AR-17. **Kan kuttes** (AR-11, punkt 1). Da står den enkle 401-siden fra story 1.3 igjen, og kuttet føres i memlog og i PRD §9.2.

**Acceptance Criteria:**

**Gitt** en bruker som fyller ut «Nytt oppdrag» mens sesjonen utløper
**Når** hen trykker «Publiser»
**Så** endres ingen data, og svaret er 401-siden «Du må logge inn igjen.» med alle innsendte felt som skjulte felt (unntatt passord og CSRF), en ny CSRF-nøkkel, feltene E-post og Passord og en knapp som sender til samme adresse
**Og** siden viser ikke noe innhold fra databasen (AD-7).

**Gitt** 401-siden
**Når** brukeren logger inn med riktig e-post og passord
**Så** logger mellomvaren inn gjennom `Autentisering`, fjerner `_innlogging_*`-feltene, og ruta behandler den opprinnelige innsendingen som den nye innloggede brukeren
**Og** tilgangsreglene i servicen gjelder som vanlig. Logger en annen bruker inn, gjelder reglene for den brukeren.

**Gitt** feil passord på 401-siden
**Når** skjemaet sendes
**Så** vises 401-siden igjen med «Feil e-post eller passord.», og de skjulte feltene beholdes. Grensen for innloggingsforsøk gjelder (FR-2).

**Gitt** kodebasen
**Når** testen kjøres
**Så** bruker ingen andre skjema feltnavn som begynner med `_` (AD-7).

---

## Epic 3: Interesse, valg av hjelper og Mine oppdrag

Amir melder interesse. Kari ser de interesserte, sammenligner erfaring og velger hjelper, og de ser hverandres telefonnummer. Hjelperen kan fjernes eller trekke seg. Begge følger oppdragene sine under «Mine oppdrag» med situasjoner, merker, grupper og antallet i menyen.

### Story 3.1: Melde og trekke interesse

Som hjelper
vil jeg melde interesse for et oppdrag med en kort melding, og kunne trekke interessen,
slik at oppdragsgiveren vet at jeg kan hjelpe.

**Krav:** FR-12, FR-13, FR-18 (fanen «Oppdrag jeg hjelper med», første situasjoner), NFR-5, AR-12, AR-13; UX-DR10 (situasjon), UX-DR23, UX-DR25 (interessert)

**Acceptance Criteria:**

**Gitt** et åpent oppdrag som ikke er passert, lagt ut av en annen
**Når** en innlogget bruker skriver en valgfri melding (høyst 500 tegn, med teller) og trykker «Meld interesse»
**Så** lagres interessen, og detaljene viser «Du har meldt interesse. Under Mine oppdrag ser du om Kari har valgt deg.» og lenken «Trekk interessen» i stedet for knappen (FR-12, UX-DR25)
**Og** en melding på 501 tegn avvises med «Teksten kan ha høyst 500 tegn. Nå har den 501.», og meldingen beholdes (FR-12).

**Gitt** et eget oppdrag, en interesse som allerede finnes, et oppdrag som ikke har status Åpen, eller et utgått oppdrag
**Når** en interesse sendes direkte til serveren
**Så** avvises den, og ingen data endres (FR-12, FR-8, NFR-5)
**Og** to samtidige forespørsler fra samme bruker gir bare én interesse (unik-constraint `interesse(oppdrag_id, bruker_id)`, AD-2).

**Gitt** en interesse på et åpent oppdrag som ikke er passert
**Når** hjelperen trykker «Trekk interessen»
**Så** slettes interessen, kvitteringen «Interessen din er trukket.» vises, og hjelperen kan melde interesse på nytt (FR-13)
**Og** når oppdraget er utgått eller ikke lenger Åpent, avvises tilbaketrekkingen (FR-13).

**Gitt** en bruker med interesser
**Når** hen åpner «Mine oppdrag»
**Så** finnes fanene «Oppdrag jeg har lagt ut» og «Oppdrag jeg hjelper med» som lenker med egen adresse (`?fane=…`), med fullt navn og antall, og `aria-current="page"` på aktiv fane (UX-DR23)
**Og** i «Oppdrag jeg hjelper med» har hvert oppdrag nøyaktig én situasjon: «Venter på svar» (lenkerad), «Tidspunktet er passert» (lenkerad) eller «Avbrutt» (avbrutt uten valgt hjelper, bare tittel og status, ikke lenke), med skjult tekst «Din situasjon: …» (FR-18, UX-DR10)
**Og** en tom hjelper-fane viser «Du har ikke meldt interesse for noen oppdrag.» med lenken «Se ledige oppdrag».

**Gitt** detaljene for et oppdrag hjelperen har meldt interesse for, som er utgått
**Når** hen åpner dem
**Så** står «Tidspunktet er passert.», og det finnes ingen handlinger (FR-13, UX-DR25).

### Story 3.2: Se de interesserte

Som oppdragsgiver
vil jeg se hvem som har meldt interesse, med erfaring, vurderinger og melding,
slik at jeg kan velge noen jeg føler meg trygg på.

**Krav:** FR-14, FR-6 («Meldt før endring»), FR-18 (antall interesserte, merket «Oppdraget er endret …»), AR-13 (`erfaring`), NFR-2; UX-DR9 (ikke-lenkerad), UX-DR21

**Acceptance Criteria:**

**Gitt** et eget åpent oppdrag med interesserte
**Når** oppdragsgiveren åpner detaljene
**Så** står overskriften «2 har meldt interesse», og under den én rad per interessert med navn, «12 fullførte oppdrag · 4,9 av 5, 11 vurderinger» (eller «Ingen vurderinger ennå»), meldingen og «Se profil», sortert eldste interesse først (FR-14)
**Og** like knappenavn som «Se profil» har `aria-describedby` til personens navn (UX-DR7).

**Gitt** et eget åpent oppdrag uten interesserte
**Når** detaljene vises
**Så** står «Ingen har meldt interesse ennå. Oppdraget vises for alle som ser på 0571 Oslo.» (FR-14, UX-DR21).

**Gitt** en annen bruker enn oppdragsgiveren
**Når** hen åpner detaljene eller ber om lista direkte
**Så** vises ikke lista over interesserte (FR-14, FR-9).

**Gitt** en interesse meldt før oppdragsgiveren endret tidspunkt, godtgjørelse eller postnummer
**Når** lista vises
**Så** har raden merket «Meldt før endring» (`interesse.opprettet < oppdrag.vesentlig_endret`) (FR-6, AD-3)
**Og** den interesserte ser merket «Oppdraget er endret etter at du meldte interesse» under «Mine oppdrag» og i detaljene, men bare når situasjonen er «Venter på svar». Teksten forkortes aldri (FR-6, FR-18, UX-DR10).

**Gitt** «Oppdrag jeg har lagt ut»
**Når** et åpent oppdrag vises
**Så** viser raden «3 har meldt interesse» eller «Ingen har meldt interesse ennå» (FR-18).

**Gitt** eksempeldataene
**Når** de lastes
**Så** har minst ett oppdrag flere interesserte, og minst én interesse er meldt før en endring (NFR-2).

### Story 3.3: Velge hjelper og dele telefonnummer

Som oppdragsgiver
vil jeg velge én av de interesserte og få telefonnummeret hens,
slik at vi kan avtale detaljene direkte.

**Krav:** FR-15, FR-16, FR-9 (valgt hjelper), FR-7 (avbryte fra Hjelper valgt), FR-18 («Du er valgt», «Ikke valgt», «Avbrutt» for valgt hjelper, «Hjelper: Amir»), NFR-2, NFR-8, AR-12, AR-24; UX-DR18 (velge), UX-DR20, UX-DR25

**Acceptance Criteria:**

**Gitt** et eget åpent oppdrag som ikke er passert, med interesserte
**Når** oppdragsgiveren trykker «Velg Amir»
**Så** åpnes dialogen «Velge Amir? Dere får se hverandres telefonnummer.» med «Gjelder «…».», «Ja, velg Amir» og «Ikke ennå» (FR-15, UX-DR18)
**Og** etter bekreftelse er status Hjelper valgt, kvitteringen «Du har valgt Amir. Avtal detaljene direkte.» vises, og oppdraget er borte fra oversikten (FR-15).

**Gitt** at valget sendes direkte til serveren
**Når** brukeren ikke er oppdragsgiver, status ikke er Åpen, tidspunktet er passert, eller den valgte ikke har meldt interesse
**Så** avvises valget, og ingen data endres (FR-15, NFR-5)
**Og** ved dobbeltklikk eller to faner får den andre forespørselen «Oppdraget er endret. Last siden på nytt.», og det finnes fortsatt bare én valgt hjelper. Testet med samtidige forespørsler (§4.0, AD-2).

**Gitt** et oppdrag med status Hjelper valgt eller Utført
**Når** oppdragsgiveren eller valgt hjelper åpner detaljene
**Så** viser telefonboksen motpartens navn og nummer som `tel:`-lenke med minst 48 px trykkflate, og «Avtal detaljene direkte.» (FR-16, UX-DR20)
**Og** telefonnummeret kommer bare fra `telefon_for_motpart`. Alle andre brukere får feilsiden for oppdraget, og testen for personopplysninger i HTML sjekker også disse sidene (FR-9, FR-16, AD-16).

**Gitt** valgt hjelper
**Når** hen åpner «Mine oppdrag»
**Så** står oppdraget som «Du er valgt» (lenkerad), og andre interesserte ser «Ikke valgt» med bare tittel og status, uten lenke (FR-18)
**Og** oppdragsgiverens rad viser «Hjelper: Amir».

**Gitt** et oppdrag med status Hjelper valgt
**Når** oppdragsgiveren avbryter det med dialogen fra story 2.5
**Så** er status Avbrutt, telefonnumrene skjules, koblingen til valgt hjelper beholdes, og hjelperen ser oppdraget som «Avbrutt» under «Oppdrag jeg hjelper med» og kan åpne detaljene uten telefonnumre (FR-7, FR-16, FR-18).

**Gitt** eksempeldataene
**Når** de lastes
**Så** har minst ett oppdrag status Hjelper valgt (NFR-2).

### Story 3.4: Fjerne hjelper eller trekke seg

Som oppdragsgiver vil jeg kunne fjerne en valgt hjelper, og som hjelper vil jeg kunne trekke meg,
slik at oppdraget kan bli åpent igjen når planene endrer seg.

**Krav:** FR-17, FR-12 (fjernet hjelper), FR-16, FR-18 («Du er ikke lenger valgt», «Du trakk deg»), NFR-5, NFR-8, AR-12 (`tidligere_hjelper`); UX-DR18 (fjerne, trekke seg), UX-DR25

**Acceptance Criteria:**

**Gitt** et oppdrag med status Hjelper valgt
**Når** oppdragsgiveren trykker «Fjern hjelper» og bekrefter i dialogen («Fjerne Amir som hjelper på «…»? …», «Ja, fjern Amir», «Nei, behold Amir»)
**Så** blir status Åpen, den valgte hjelperens interesse slettes, de andre interessene beholdes, en rad med `arsak='fjernet'` skrives i `tidligere_hjelper`, og telefonnumrene skjules (FR-17, AD-2)
**Og** kvitteringen «Amir er fjernet. Oppdraget er åpent igjen.» vises, og oppdraget er tilbake i oversikten hvis tidspunktet ikke er passert.

**Gitt** valgt hjelper på et oppdrag med status Hjelper valgt
**Når** hen trykker «Trekk meg fra oppdraget» og bekrefter («Ja, trekk meg» / «Nei, jeg blir»)
**Så** skjer det samme med `arsak='trakk_seg'`, og kvitteringen «Du har trukket deg fra oppdraget.» vises (FR-17).

**Gitt** en fjernet hjelper
**Når** hen åpner detaljene for oppdraget
**Så** står «Du er ikke lenger valgt til dette oppdraget» i stedet for «Meld interesse», og en ny interesse sendt direkte til serveren avvises (FR-12)
**Og** under «Mine oppdrag» står oppdraget som «Du er ikke lenger valgt» (FR-18).

**Gitt** en hjelper som trakk seg selv
**Når** hen åpner detaljene
**Så** kan hen melde interesse på nytt, og under «Mine oppdrag» står «Du trakk deg» til en ny interesse er meldt (FR-12, FR-18)
**Og** har brukeren både trukket seg og blitt fjernet fra samme oppdrag, gjelder det som skjedde sist (FR-18).

**Gitt** en annen bruker, eller en annen status enn Hjelper valgt
**Når** en fjerning eller tilbaketrekking sendes direkte til serveren
**Så** avvises den (FR-17, NFR-5).

### Story 3.5: «Trenger handling», grupper og tall i menyen

Som bruker uten varsler
vil jeg se med en gang hvilke oppdrag som venter på meg, og hvor mange de er,
slik at jeg ikke går glipp av noe jeg må gjøre.

**Krav:** FR-18 (merkene «Velg hjelper», «Tidspunktet er passert», «Hjelperen trakk seg» og «Oppdraget er endret …», grupper, sortering og antall), NFR-11, AR-13, AR-27 (menykroken); UX-DR3 (nav-badge), UX-DR9, UX-DR23, UX-DR26

**Acceptance Criteria:**

**Gitt** et eget åpent oppdrag som ikke er passert, med minst én interessert
**Når** «Mine oppdrag» eller detaljene vises
**Så** har oppdraget merket «Velg hjelper». I detaljene står merket rett under «N har meldt interesse». Merket forsvinner når en hjelper er valgt eller oppdraget avbrytes, og er tidspunktet passert, vises «Tidspunktet er passert» i stedet (FR-18).

**Gitt** at valgt hjelper har trukket seg eller (fra Epic 4) slettet kontoen
**Når** oppdragsgiveren åpner «Mine oppdrag»
**Så** har oppdraget merket «Hjelperen trakk seg» til en ny hjelper er valgt eller oppdraget avbrytes, også når ingen andre er interessert. Når det er andre interesserte, vises også «Velg hjelper» (FR-18, AD-3).

**Gitt** begge fanene
**Når** de vises
**Så** er oppdragene delt i «Trenger handling» (minst ett merke), «Pågår» og «Ferdige» etter tabellen i FR-18, og grupper uten oppdrag vises ikke
**Og** i «Oppdrag jeg hjelper med» avgjør brukerens egen situasjon gruppen: «Ikke valgt», «Du er ikke lenger valgt», «Du trakk deg» og «Tidspunktet er passert» står under «Ferdige» uten merke
**Og** «Trenger handling» og «Pågår» sorteres etter tidspunkt, tidligste først, «Ferdige» nyeste først, og like tidspunkt som i FR-10 (FR-18)
**Og** lenkeradene har `aria-describedby` til merkelinja, slik at skjermleseren leser «Tittel, Status: …. Må gjøres: …» (UX-DR9).

**Gitt** en innlogget bruker
**Når** en hvilken som helst side lastes
**Så** viser «Mine oppdrag» i menyen antall oppdrag under «Trenger handling» i de to fanene til sammen. Et oppdrag med flere merker telles én gang, tallet vises ikke ved 0, og skjermleseren leser «Mine oppdrag, 2 trenger handling» (FR-18, NFR-11, UX-DR3)
**Og** tallet regnes ut på nytt ved hver sidelasting gjennom menykroken, uten at noe lagres om hva brukeren har sett (AD-3)
**Og** øverst i «Mine oppdrag» står «2 oppdrag trenger at du gjør noe.» når tallet er over 0.

**Gitt** at «Mine oppdrag» åpnes uten valgt fane
**Når** siden vises
**Så** åpnes fanen med «Trenger handling»-oppdrag («Oppdrag jeg har lagt ut» hvis begge har det), ellers «Oppdrag jeg har lagt ut» (UX-DR23).

**Gitt** de automatiske testene
**Når** de kjøres
**Så** finnes det en test for hver rad i situasjonstabellen og for hvert merke i FR-18 så langt, og for tallet i menyen med flere merker på samme oppdrag (FR-18, NFR-11)
**Og** T1 dekker begge fanene og tom fane.

---

## Epic 4: Fullføre, gi tilbakemelding og vise erfaring

Oppdraget markeres som utført, og partene gir hverandre stjerner og kommentar. Amir har en profil med fullførte oppdrag og tilbakemeldinger han kan vise fram. Brukeren kan redigere profilen sin og slette kontoen.

### Story 4.1: Markere oppdraget som utført

Som valgt hjelper eller oppdragsgiver
vil jeg markere oppdraget som utført når jobben er gjort,
slik at oppdraget blir avsluttet og kan telle som erfaring.

**Krav:** FR-19, FR-18 (merket «Er jobben gjort?» og situasjonen «Utført»), NFR-5, NFR-8, AR-12, AR-13, NFR-2; UX-DR18 (utført), UX-DR25

**Acceptance Criteria:**

**Gitt** et oppdrag med status Hjelper valgt
**Når** valgt hjelper åpner detaljene før datoen for tidspunktet
**Så** finnes ikke knappen «Marker som utført». I stedet står det når hen kan gjøre det («Du kan markere oppdraget som utført fra fredag 6. nov.») (FR-19, UX-DR25)
**Og** fra kl. 00:00 norsk tid på datoen vises «Marker som utført» som primærknapp. Testet med `sett_na` 23:59 dagen før og 00:00 samme dag, også over et skifte til eller fra sommertid (FR-19, AD-9).

**Gitt** et oppdrag med status Hjelper valgt
**Når** oppdragsgiveren åpner detaljene
**Så** vises «Marker som utført» først når tidspunktet er passert, sammen med merket «Er jobben gjort?» (FR-19).

**Gitt** knappen «Marker som utført»
**Når** brukeren trykker den
**Så** åpnes dialogen «Marker som utført? Det kan ikke angres.» med «Gjelder «…».», «Ja, marker som utført» og «Ikke ennå» (FR-19, UX-DR18)
**Og** etter bekreftelse er status Utført, kvitteringen «Oppdraget er markert som utført.» vises, oppdraget kan ikke lenger endres, og telefonboksen vises fortsatt for de to partene (FR-16, FR-19).

**Gitt** at markeringen sendes direkte til serveren
**Når** valgt hjelper gjør det før datoen, oppdragsgiveren gjør det før tidspunktet er passert, en annen bruker gjør det, eller status ikke er Hjelper valgt
**Så** avvises den, og ingen data endres (FR-19, NFR-5)
**Og** to samtidige markeringer gir én overgang, og den andre får «Oppdraget er endret. Last siden på nytt.» (AD-2).

**Gitt** et oppdrag med status Hjelper valgt der tidspunktet er passert
**Når** «Mine oppdrag» vises for begge parter
**Så** har oppdraget merket «Er jobben gjort?», står under «Trenger handling» og telles i menyen (FR-18)
**Og** etter markeringen står oppdraget som «Utført» for hjelperen og med status Utført for oppdragsgiveren.

**Gitt** eksempeldataene
**Når** de lastes
**Så** har minst ett oppdrag status Hjelper valgt der tidspunktet er passert (NFR-2).

### Story 4.2: Gi tilbakemelding

Som oppdragsgiver eller valgt hjelper på et utført oppdrag
vil jeg gi den andre parten stjerner og en kort kommentar,
slik at erfaringen blir dokumentert i profilen.

**Krav:** FR-20, FR-18 (merket «Gi tilbakemelding»), NFR-5, NFR-8, NFR-12, AR-12, NFR-2; UX-DR17 (input), UX-DR22

**Acceptance Criteria:**

**Gitt** et utført oppdrag der brukeren er oppdragsgiver eller valgt hjelper og ikke har gitt tilbakemelding
**Når** hen åpner detaljene
**Så** vises «Hvordan gikk det med Amir?» som `legend` over fem stjerner (radioknapper på 48 × 48 px med navnene «1 av 5 stjerner, dårlig» til «5 av 5 stjerner, veldig bra», som kan velges med trykk eller piltaster), «Kommentar (valgfritt)» med teller og hjelpeteksten «Kommentaren vises i Amirs profil.», og knappen «Send» (FR-20, UX-DR17)
**Og** et trykk på en stjerne lagrer ingenting. Valgt verdi står med ord under stjernene.

**Gitt** stjerner valgt og eventuelt en kommentar på høyst 500 tegn
**Når** brukeren trykker «Send»
**Så** lagres tilbakemeldingen, og skjemaet erstattes av kvitteringen «Takk! Tilbakemeldingen er lagt til i Amirs profil.» og den gitte tilbakemeldingen (FR-20)
**Og** «Send» uten stjerner gir «Velg antall stjerner.», og en kommentar på 501 tegn avvises med teksten fra EXPERIENCE.md.

**Gitt** at tilbakemeldingen sendes direkte til serveren
**Når** status ikke er Utført, avsenderen ikke er en av partene, mottakeren ikke er den andre parten, eller avsenderen allerede har gitt tilbakemelding
**Så** avvises den (FR-20, NFR-5)
**Og** to samtidige innsendinger gir én tilbakemelding (unik-constraint `tilbakemelding(oppdrag_id, giver_id)`, AD-2).

**Gitt** et utført oppdrag der brukeren ikke har gitt tilbakemelding
**Når** «Mine oppdrag» vises
**Så** har oppdraget merket «Gi tilbakemelding» og står under «Trenger handling» til tilbakemeldingen er gitt (FR-18).

**Gitt** en kommentar med `<script>alert(1)</script>`
**Når** den vises
**Så** vises den som tekst (NFR-12).

**Gitt** eksempeldataene
**Når** de lastes
**Så** finnes minst ett utført oppdrag med tilbakemelding fra begge parter og ett utført oppdrag der tilbakemelding ennå ikke er gitt (NFR-2).

### Story 4.3: Vise profil med dokumentert erfaring

Som hjelper
vil jeg ha en profil som viser fullførte oppdrag, snittvurdering og tilbakemeldinger,
slik at jeg kan vise til erfaringen min, for eksempel når jeg søker sommerjobb.

**Krav:** FR-21, FR-9 og FR-14 (snitt og erfaring), NFR-2 (fullstendig test), AR-13 (`erfaring`), AR-24; UX-DR9, UX-DR17 (visning), UX-DR21, UX-DR29

**Acceptance Criteria:**

**Gitt** en innlogget bruker
**Når** hen åpner profilen til en annen bruker (fra «Se profil») eller sin egen (fra menyvalget «Profil»)
**Så** vises navn, postnummer med poststed, «om meg» (bare når feltet har tekst), fullførte oppdrag per kategori, snittet med stjerner og teksten «4,9 av 5, 11 vurderinger», og alle mottatte tilbakemeldinger, nyeste først (FR-21, UX-DR17)
**Og** `<title>` er «Min profil – Nabolagshelten» eller «Amir – profil – Nabolagshelten».

**Gitt** tilbakemeldingene i profilen
**Når** de vises
**Så** viser hver rad vurderingen («5 av 5 stjerner»), kommentaren og metalinja «Fra Kari · 14. feb. · Amir var hjelper», med giverens navn som lenke til profilen (FR-21, UX-DR9).

**Gitt** utregningen av erfaring
**Når** `erfaring(db, bruker_ids)` kalles
**Så** teller «fullførte oppdrag» bare oppdrag med status Utført der brukeren var valgt hjelper, og snittet regnes ut fra alle tilbakemeldinger brukeren har fått, både som hjelper og som oppdragsgiver (FR-21, AD-3)
**Og** snittet vises med én desimal og desimalkomma («4,3 av 5, 7 vurderinger»), og de samme tallene vises i oppdragsgiverblokken (FR-9) og i lista over interesserte (FR-14)
**Og** stjernene i visningen avrundes til nærmeste hele stjerne (4,4 → 4 og 4,9 → 5), har `aria-hidden`, og teksten bærer verdien (UX-DR17).

**Gitt** en bruker uten vurderinger eller uten fullførte oppdrag
**Når** profilen vises
**Så** står «Ingen vurderinger ennå» og «Ingen fullførte oppdrag ennå» (FR-21, UX-DR21).

**Gitt** en hvilken som helst profil
**Når** den vises
**Så** står teksten «Fullførte oppdrag og tilbakemeldinger er registrert av brukere i Nabolagshelten og er ikke verifisert.»
**Og** profilen viser aldri telefonnummer, e-post eller fødselsdato, og malen får bare `Profil` (FR-21, AD-16).

**Gitt** egen profil
**Når** den vises
**Så** står «Rediger profil» og «Logg ut» som sekundærknapper øverst, rett under navn og postnummer (FR-21). «Slett konto» kommer i story 4.5.

**Gitt** eksempeldataene
**Når** den automatiske testen for NFR-2 kjøres
**Så** finnes hver situasjon i lista i NFR-2: minst 6 brukere i 2–3 postnumre, 10–15 oppdrag, åpne oppdrag i alle kategorier, ett oppdrag med flere interesserte, Hjelper valgt, Utført med og uten tilbakemelding, Avbrutt, utgått, Hjelper valgt etter tidspunktet, og én bruker med og én uten vurderinger (NFR-2).

### Story 4.4: Redigere egen profil (Bør)

Som bruker
vil jeg skrive litt om meg selv og endre postnummer og telefonnummer,
slik at profilen er riktig når jeg flytter eller bytter nummer.

**Krav:** FR-22, NFR-5, NFR-12, AR-24 (`EgneOpplysninger`); UX-DR12, UX-DR13. **Kan kuttes** etter PRD §6.1. Da tas «om meg» og «Rediger profil» ut av FR-21, NFR-12 og SM-5.

**Acceptance Criteria:**

**Gitt** egen profil
**Når** brukeren trykker «Rediger profil»
**Så** vises «Rediger profil» med navn, e-post og fødselsdato som tekst (kan ikke endres), og feltene Om meg (valgfritt, høyst 500 tegn, med teller), Postnummer (med poststed) og Telefonnummer, og knappen «Lagre endringer» (FR-22)
**Og** malen får `EgneOpplysninger`. Dette er den eneste siden som viser brukerens egen e-post og telefon (FR-16, AD-16).

**Gitt** gyldige verdier
**Når** brukeren trykker «Lagre endringer»
**Så** havner hen på profilen med kvitteringen «Profilen er oppdatert.» (FR-22)
**Og** nytt postnummer brukes straks i oversikten og forhåndsutfylles i nye oppdrag, mens oppdrag som allerede er lagt ut, beholder sitt postnummer
**Og** nytt telefonnummer vises straks for motparten i oppdrag med status Hjelper valgt eller Utført.

**Gitt** ugyldig postnummer, ugyldig telefonnummer eller «om meg» over 500 tegn
**Når** skjemaet sendes
**Så** vises feilen ved feltet, og ingenting lagres (FR-22, NFR-10).

**Gitt** at en endring sendes direkte til serveren for en annen bruker, eller med navn, e-post eller fødselsdato
**Når** serveren behandler den
**Så** endres bare innlogget brukers «om meg», postnummer og telefon (FR-22, NFR-5).

**Gitt** «om meg» med `<script>alert(1)</script>`
**Når** profilen vises
**Så** vises teksten som tekst (NFR-12).

### Story 4.5: Slette egen konto

Som bruker
vil jeg kunne slette kontoen min selv,
slik at personopplysningene mine fjernes uten at andres dokumenterte erfaring forsvinner.

**Krav:** FR-4, FR-17, FR-18 («Hjelperen trakk seg»), FR-20, FR-21, NFR-9, AR-9 (`slett-konto`), AR-18, AR-25; UX-DR21, UX-DR29

**Acceptance Criteria:**

**Gitt** egen profil
**Når** brukeren trykker lenken «Slett konto» nederst
**Så** vises siden «Slett konto» med forklaringen fra FR-4: hva som slettes, at tilbakemeldinger brukeren har gitt, beholdes med navnet «Slettet bruker», og at kommentarene i noen tilfeller kan avsløre hvem som skrev dem. Siden har feltet Passord (`current-password`), «Slett kontoen min» og «Tilbake til profilen» (FR-4).

**Gitt** feil passord
**Når** brukeren trykker «Slett kontoen min»
**Så** vises «Passordet er feil. Kontoen er ikke slettet.», og ingenting endres (FR-4).

**Gitt** riktig passord
**Når** kontoen slettes
**Så** beholdes `bruker`-raden med samme id, navn, e-post, passord-hash, telefon, postnummer, fødselsdato og «om meg» settes til NULL, og `slettet_tidspunkt` settes (AD-8)
**Og** alle sesjoner for kontoen slettes, også på andre enheter, og radene i `innloggingsforsok` for e-posten slettes
**Og** brukeren havner på innloggingssiden med «Kontoen din er slettet.»
**Og** en test sjekker at databasen ikke lenger inneholder den gamle e-postadressen eller telefonnummeret (FR-4).

**Gitt** dataene til brukeren som slettes
**Når** slettingen kjøres
**Så** behandles de etter tabellen i FR-4: egne åpne og avbrutte oppdrag slettes sammen med interessene, egne oppdrag med Hjelper valgt blir Avbrutt med telefonnumrene skjult, utførte oppdrag beholdes og teller fortsatt i den andre partens profil, interesser brukeren har meldt slettes, oppdrag der brukeren er valgt hjelper med status Hjelper valgt går tilbake til Åpen gjennom overgangen i AD-2 (`arsak='slettet'`) slik at oppdragsgiveren ser «Hjelperen trakk seg», tilbakemeldinger brukeren har gitt beholdes, og tilbakemeldinger brukeren har fått slettes (FR-4, FR-17, FR-18)
**Og** hele slettingen skjer i én transaksjon styrt av `profil/service.py`. En test feiler slettingen til slutt med vilje og sjekker at ingenting er endret, både mot SQLite og mot Postgres (AD-8, AD-17).

**Gitt** en slettet bruker
**Når** hen vises i oppdrag og tilbakemeldinger
**Så** står «Slettet bruker» uten lenke og uten telefonnummer, fra én funksjon i `identity/service.py` (FR-4, AD-8)
**Og** en direkte lenke til profilen viser «Denne brukeren har slettet kontoen sin.» med lenke til oversikten og `<title>` «Slettet bruker – Nabolagshelten»
**Og** «Gi tilbakemelding» vises ikke når motparten er slettet, og en tilbakemelding til en slettet bruker avvises (FR-18, FR-20).

**Gitt** e-postadressen til den slettede kontoen
**Når** noen registrerer seg med den
**Så** opprettes en ny konto uten kobling til de gamle dataene, og den slettede kontoen kan ikke logge inn (FR-4).

**Gitt** at slettingen sendes direkte til serveren for en annen bruker
**Når** serveren behandler den
**Så** avvises den (FR-4, NFR-5).

**Gitt** en bruker som har glemt passordet og vil slette kontoen
**Når** gruppen hjelper manuelt
**Så** sletter `uv run python -m app.admin slett-konto <e-post>` kontoen med den samme service-funksjonen (AR-9).

**Gitt** T1
**Når** testen kjøres
**Så** er «Slett konto», «Slett konto» med feil passord og «Slettet bruker» uten brudd på nivåene «serious» eller «critical».

---

## Epic 5: KI-forslag (Bør)

Kari kan få forslag til tittel, kategori og beskrivelse når hun legger ut et oppdrag. Mock er standard, og appen fungerer fullt ut uten KI. Hele epicen kan kuttes etter PRD §6.1. Da gjelder ikke R12 og SK10, og avviket føres i PRD §9.2.

### Story 5.1: Få forslag i mock-modus

Som oppdragsgiver
vil jeg trykke «Få forslag» og få forslag til tittel, kategori og beskrivelse som jeg selv velger om jeg vil bruke,
slik at det blir lettere å skrive et tydelig oppdrag.

**Krav:** FR-23, FR-24, FR-25 (validering og testdobler), FR-26, NFR-1, NFR-7, NFR-12, AR-22 (grensesnitt, mock, testdobbel og kvote), AR-23, AR-28 (`ki.js`); UX-DR19, UX-DR27

**Acceptance Criteria:**

**Gitt** «Nytt oppdrag» uten API-nøkkel (tom, eller plassholderen fra `.env.example`)
**Når** skjemaet vises
**Så** står «Få forslag» som sekundærknapp under beskrivelsesfeltet og telleren, med teksten «Forslagene lages i appen. Teksten sendes ikke ut.» under knappen (FR-23, FR-26, UX-DR19)
**Og** under 10 tegn er knappen `aria-disabled` med teksten «Skriv minst 10 tegn for å få forslag.»
**Og** knappen finnes ikke ved redigering, og den er skjult uten JavaScript (FR-23, AD-15).

**Gitt** en beskrivelse på minst 10 tegn
**Når** brukeren trykker «Få forslag»
**Så** sender `ki.js` skjemaets `FormData` til `POST /oppdrag/forslag` med `X-Fragment: 1` og CSRF-feltet, knappen viser «Lager forslag …» med `aria-live`, og fokus blir på knappen (FR-23, AD-15)
**Og** serveren sender bare beskrivelsesteksten til KI-grensesnittet, aldri navn, e-post, telefon eller andre profilopplysninger (FR-23).

**Gitt** et gyldig svar
**Når** fragmentet kommer tilbake
**Så** vises én forslagsboks under hvert av feltene Beskrivelse, Tittel og Kategori, skjermleseren leser «Forslagene er klare.», og ingen felt fylles inn før brukeren trykker «Bruk» (FR-24, UX-DR19)
**Og** «Bruk» fyller feltet, fjerner boksen og gir fokus til feltet, som fortsatt kan redigeres. «Ikke bruk» fjerner boksen og gir fokus til feltet. Et nytt trykk på «Få forslag» erstatter alle boksene (FR-24)
**Og** ingenting lagres før «Publiser» (FR-24).

**Gitt** mock-modus
**Når** den lager et svar
**Så** følger kategorien nøkkelordtabellen i FR-26 (første kategori ovenfra med et ord som begynner med et nøkkelord, uten å skille store og små bokstaver), tittelen er første setning med stor forbokstav og høyst 80 tegn, og beskrivelsen er teksten med stor forbokstav og punktum når det mangler. Mock gir ikke tips (FR-26)
**Og** testene dekker «måke snø i innkjørselen» → Snømåking og «Måke snø i innkjørselen», en tekst uten nøkkelord → Annet, «hundre» → Dyrepass, «strømbrudd» → Snømåking, «kl. 07:30» kutter ikke setningen, første setning under 3 tegn gir kategorinavnet som tittel, og samme tekst gir alltid samme svar (FR-26)
**Og** automatiske tester kjører alltid i mock-modus, også når `.env` har en nøkkel (AD-12).

**Gitt** svaret fra en hvilken som helst utgave
**Når** det valideres
**Så** godtas det bare som JSON med kategori fra `core/domene.py` (som kode), tittel på 3–80 tegn, beskrivelse på 10–1000 tegn og eventuelt tips på høyst 200 tegn, etter trim og NFC (FR-25, AD-10)
**Og** testdobler som svarer med ugyldig JSON, ukjent kategori, for lang tekst, en feil og et svar etter fristen, gir alle feilfragmentet «Vi fikk ikke laget forslag akkurat nå. Du kan fylle inn selv.» med status 200 der forslagene ellers ville stått, `role="alert"`, ingen forslagsbokser, og skjemaet beholder alt (FR-25, AD-15).

**Gitt** en bruker som har bedt om 20 forslag den siste timen
**Når** hen ber om ett til
**Så** vises «Du har bedt om mange forslag den siste timen. Prøv igjen senere, eller fyll inn selv.» (FR-23)
**Og** kvoten sjekkes og registreres i `ki_bruk` i en egen transaksjon som committes før kallet, og rader eldre enn 60 minutter slettes ved telling (AD-12).

**Gitt** forslag eller tips med `<script>alert(1)</script>`
**Når** de vises
**Så** vises de som ren tekst, og `ki.js` setter bare inn ferdige fragmenter fra serveren (FR-25, NFR-12, AD-11).

**Gitt** en utløpt sesjon
**Når** brukeren trykker «Få forslag»
**Så** gir serveren 401 med fragmentet «Du må logge inn igjen.», som `ki.js` setter inn (AD-4, AD-15).

**Gitt** T1
**Når** testen kjøres
**Så** er «KI-forslag vist» og «KI-feil» uten brudd på nivåene «serious» eller «critical».

### Story 5.2: Ekte KI-tjeneste via OpenRouter

Som oppdragsgiver i produksjon
vil jeg få forslag fra en språkmodell som omformulerer det jeg skrev, på bokmål og uten nye opplysninger,
slik at forslagene blir bedre enn det faste reglene i mock-modus gir.

**Krav:** FR-23, FR-24, FR-25, NFR-3, NFR-9, AR-8, AR-22 (OpenRouter og kostnad)

**Acceptance Criteria:**

**Gitt** `OPENROUTER_API_KEY` og `OPENROUTER_MODEL` satt i Vercel env (aldri i repoet)
**Når** appen starter i produksjon
**Så** velges OpenRouter-utgaven ett sted, og `sender_eksternt()` gjør at teksten ved knappen blir «Teksten i beskrivelsen sendes til en ekstern KI-tjeneste for å lage forslag.» (FR-23, AD-12)
**Og** nøkkelen har en kredittgrense satt i OpenRouter, eller modellen er gratis. Uten grense kjører produksjon i mock (AD-12).

**Gitt** et kall til OpenRouter
**Når** det samlede kallet tar mer enn 10 sekunder
**Så** avbrytes det, et svar som kommer senere, vises ikke, og brukeren får KI-feilen (FR-25)
**Og** ingen databasetransaksjon er åpen under kallet (AD-12, AD-17).

**Gitt** prompten
**Når** koden leses
**Så** ligger den i `app/ki/prompt.txt`, og den ber om JSON med kategori (kode), tittel, beskrivelse og eventuelt tips, på norsk bokmål, med en beskrivelse som bare omformulerer det brukeren skrev og legger det som mangler i tipset (FR-23, FR-24).

**Gitt** fem faste eksempeltekster (blant annet Karis tekst fra UJ-1)
**Når** de sendes til den valgte modellen
**Så** er resultatet dokumentert i `docs/tester/`: om kategorien er riktig, om beskrivelsen legger til opplysninger, om språket er bokmål, og om svaret består valideringen i FR-25 (FR-24)
**Og** modellen som velges, står i README og i `.env.example` som eksempelverdi uten nøkkel.

**Gitt** loggene
**Når** et KI-kall gjøres
**Så** logges verken beskrivelsesteksten, svaret eller nøkkelen (AR-30).

---

## Epic 6: Klar for sensur

En person utenfor gruppen får appen i gang fra README på en ren maskin, og testene for universell utforming og brukertesten er gjennomført og dokumentert. Epicen avhenger ikke av Epic 5. Story 6.1 og 6.2 kan tas av hvem som helst i gruppen og blokkerer ikke noe annet.

### Story 6.1: Manuelle tester av universell utforming (T2–T5)

Som bruker med tastatur, skjermleser, stor tekst eller nedsatt syn
vil jeg at appen er testet manuelt på det automatiske tester ikke finner,
slik at jeg faktisk kan gjennomføre kjerneflyten.

**Krav:** NFR-6, NFR-7, NFR-8, NFR-11; UX-DR32

**Acceptance Criteria:**

**Gitt** protokollmalene i `docs/tester/` (én fil per test, med dato, nettleser, operativsystem, kontrollpunkter, funn og retting)
**Når** T2 (tastatur) gjennomføres
**Så** er UJ-1, UJ-2 og støtteflytene (registrering, innlogging, rediger profil, slett konto) gått gjennom uten mus, med kontrollpunktene «Hopp til innholdet», synlig fokus, dato og klokkeslett, kategorifilter og kategoriknapper, stjerner, alle dialoger, fokus tilbake etter dialog, og felttyper og `autocomplete` mot tabellen i EXPERIENCE.md. Tekststørrelse og trykkflater er målt i DevTools.

**Gitt** NVDA eller VoiceOver
**Når** T3 (skjermleser) gjennomføres
**Så** er UJ-1, UJ-2 steg 3–6 (antallet etter filtervalg), ett skjema med feil (feiloppsummeringen leses, og lenkene fører til feltene) og en kvittering etter sidelasting gått gjennom og dokumentert.

**Gitt** T4 (bredder og zoom)
**Når** den gjennomføres
**Så** er UJ-1 og UJ-2 dokumentert med skjermbilder ved 360, 768 og 1280 px (NFR-6), og sjekket ved 320 px, ved 200 % zoom, med tekstavstand etter WCAG 1.4.12 (bokmerke), med 200 % tekststørrelse i operativsystemet og på liggende telefon med bunnmenyen og et felt med fokus.

**Gitt** T5 (kontrast og farge)
**Når** den gjennomføres
**Så** er kontrasttabellen i DESIGN.md kontrollert med stikkprøver i appen, også kanter, fokusring og tilstander (WCAG 1.4.11), og appen er gått gjennom én gang i gråtoner eller med tvungne farger (`forced-colors: active`).

**Gitt** en gjennomgang av kjerneflyten mot ordlisten i PRD §3
**Når** den gjøres
**Så** er avvik i knappetekster og overskrifter dokumentert og rettet (NFR-8).

**Gitt** funn fra T2–T5
**Når** de er alvorlige (en flyt kan ikke gjennomføres, eller WCAG 2.1 AA brytes)
**Så** er de rettet, eller ført som kjent begrensning i README med begrunnelse.

### Story 6.2: Brukertest med personer utenfor gruppen (T6)

Som gruppe
vil vi se at personer som Kari faktisk klarer å legge ut et oppdrag,
slik at vi vet at appen er enkel nok for målgruppen.

**Krav:** SM-4, NFR-6, NFR-7, FR-5; UX-DR32 (T6)

**Acceptance Criteria:**

**Gitt** minst to testpersoner utenfor gruppen, der minst én er over 60 år eller lite vant med apper
**Når** hver av dem legger ut et oppdrag (UJ-1 steg 1–3) på mobil eller nettbrett
**Så** er tiden målt fra personen trykker «Legg ut oppdrag» til oppdraget er publisert, og målet er under to minutter (SM-4)
**Og** enhet, nettleser, tid og ord personen ikke forsto, er dokumentert i `docs/tester/T6-brukertest.md`.

**Gitt** at en testperson brukte nettbrett
**Når** resultatet vurderes
**Så** er det notert om personen ville foretrukket to steg også på nettbrett (åpent punkt i EXPERIENCE.md).

**Gitt** funn fra brukertesten
**Når** de er enkle å rette (ord, tekster, rekkefølge)
**Så** er de rettet, og ellers ført som forslag til neste versjon.

### Story 6.3: README og repo klare for sensor

Som sensor
vil jeg få appen i gang på en ren maskin bare ved å følge README, og finne planleggingsdokumentene og testene,
slik at jeg kan vurdere både produktet og prosessen innen 15–20 minutter.

**Krav:** NFR-1, NFR-2, NFR-3, NFR-9, SM-1, SM-2, SM-3, AR-10

**Acceptance Criteria:**

**Gitt** en ren maskin eller en container
**Når** en person utenfor gruppen følger README fra start, uten hjelp
**Så** har hen appen i gang med eksempeldata innen 15 minutter, og operativsystem, tidsbruk og eventuelle problemer er dokumentert i `docs/tester/` (NFR-1, SM-3)
**Og** problemene er rettet i README.

**Gitt** README
**Når** sensor leser den
**Så** har den en kort beskrivelse og et skjermbilde, forutsetninger med versjoner, eksakte kommandoer for å starte appen, laste eksempeldata og kjøre testene, testbrukere med hva de brukes til, at mock er standard for KI, mappestrukturen, lenker til brief, PRD, UX, arkitektur, epics, testprotokoller og `.logs/`, kildelinja for postnummerdata, kontoer for drift og lenke til produksjonsversjonen (NFR-1, NFR-2, AR-10)
**Og** statustabellen viser hva som er ferdig, og hva som er kuttet med begrunnelse.

**Gitt** git-historikken
**Når** gitleaks kjøres på hele historikken
**Så** er resultatet uten funn og dokumentert (NFR-3).

**Gitt** databaseskjemaet
**Når** det gjennomgås mot lista i NFR-9
**Så** lagres bare navn, e-post, passord-hash, telefon, postnummer, fødselsdato, innhold brukeren selv legger inn og data appen trenger for å virke, og gjennomgangen er dokumentert (NFR-9).

**Gitt** planleggingsdokumentene
**Når** de sammenlignes med appen som er levert
**Så** er alle kutt og avvik ført i PRD §9.2 og endringsloggen, `epics.md` stemmer med det som er bygget, og hver regel R1–R13 har minst én automatisk test som passerer, unntatt R12 hvis KI er kuttet (SM-1, SM-2)
**Og** `uv run pytest` passerer på `main`, og produksjonsversjonen og Supabase er sjekket rett før innlevering.

**Gitt** rotmappen
**Når** den sjekkes
**Så** finnes ingen løse filer, sikkerhetskopier, `.env`, `.venv`, `node_modules` eller byggmapper i repoet (sensorveiledningen, kriterium 7).
