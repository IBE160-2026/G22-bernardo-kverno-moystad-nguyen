---
type: reconcile
input: ../../../prds/prd-G22-bernardo-kverno-moystad-nguyen-2026-11-05/prd.md (PRD v1.1)
spine: ../ARCHITECTURE-SPINE.md (draft, oppdatert 2026-11-23)
date: 2026-11-23
---

# Avstemming: PRD v1.1 mot arkitekturspinen

## Konklusjon

Spinen dekker det PRD-en eksplisitt gir til arkitekturen (§8: postnummerkilde, CSRF, sommertid, tegnsett; NFR-4: bcrypt; NFR-12: AD-5). Alle FR- og NFR-ID-er er bundet. Men det er **to motsigelser mot PRD-en som vil gi feilende tester** (F1 og F2), og flere tverrgående regler der to stories kan bygge uforenlig (F3–F9). De fleste rettelsene er én setning i en eksisterende AD eller en ny rad i konvensjonstabellen.

Alvorlighet: **kritisk** = bryter et testbart PRD-krav slik spinen står; **høy** = stories vil sannsynligvis bygge uforenlig eller låse seg; **middels** = reell risiko for avvik; **lav** = presisering.

| # | Tema | PRD | Alvorlighet |
|---|---|---|---|
| F1 | Slettet e-post blir liggende i `innloggingsforsok` | FR-4, NFR-9 | kritisk |
| F2 | Avhengighetsgrafen hindrer vurdering/fullførte i oppdragsdetaljer og interesserte | FR-9, FR-14, FR-21 | høy |
| F3 | Kategoriliste og feltgrenser trengs i både `oppdrag` og `ki` | FR-5, FR-25, FR-26 | høy |
| F4 | Normalisering av e-post og passord er ikke bestemt | FR-1, FR-2, §4.0, AD-10 | høy |
| F5 | Bare statusskriving er atomisk; interesse, redigering og engangsregler er det ikke | §4.0, FR-6, FR-12, FR-20 | høy |
| F6 | Tid med tidssone i SQLite vs Postgres | AD-9, AD-13, FR-5 | høy |
| F7 | 10 s er ikke total tid i `httpx`, og Vercel-grensen er ukjent | FR-25 | middels |
| F8 | Tester skal alltid bruke mock, spinen sier testdobbel | FR-26 | middels |
| F9 | «Virker uten JavaScript» mot krav som trenger JS | §4.0, FR-23, FR-24, NFR-7, NFR-8 | middels |
| F10 | Telefon, e-post og fødselsdato kan lekke via maler | FR-16, FR-21 | middels |
| F11 | Clickjacking er ikke dekket | NFR-12 | middels |
| F12 | AD-7 mot FR-3 (og AD-4) | FR-3 | middels |
| F13 | Manglende piler: `tilbakemelding → identity`, `mine_oppdrag → identity` | FR-18, FR-20, FR-21 | middels |
| F14 | Ingen felles regel for «ingen tilgang» / «finnes ikke» | FR-9, FR-4, FR-22 | middels |
| F15 | Lagringstid for `sesjon`, `innloggingsforsok`, `ki_bruk` uten cron | NFR-9, AD-3 | middels |
| F16 | Seed bryter AD-1 og tjenestereglene | NFR-2, AD-1 | middels |
| F17 | Hvordan skjemaet lages lokalt (Alembic) står ikke | NFR-1 | middels |
| F18 | Manuell tilbakestilling av passord må bruke AD-6 | §6.2, §4.7 | lav |
| F19 | KI-kvote: vindu og hva som telles | FR-23 | lav |
| F20 | «Meldt før endring» trenger et lagret tidspunkt | FR-6, FR-14, FR-18 | lav |
| F21 | Statusord og vurderingsformat ett sted | NFR-7, FR-21 | lav |
| F22 | FR-1 alder i norsk tid er ikke bundet til AD-9 | FR-1 | lav |
| F23 | `ki_bruk` er ikke med i slettingen | FR-4, AD-8 | lav |
| F24 | NFR-12-test og gitleaks står ikke i testkonvensjonen | NFR-12, NFR-3 | lav |

---

## Funn

### F1 — Slettet e-post blir liggende i `innloggingsforsok` (kritisk)

- **PRD:** FR-4: «Testes ved at databasen etter sletting ikke inneholder den gamle e-postadressen eller telefonnummeret.» NFR-9: bare data appen trenger.
- **Motsigelse:** AD-4 teller mislykkede innlogginger per e-post i `innloggingsforsok`, og AD-8 nuller bare personfeltene i `bruker`. Har brukeren noen gang skrevet feil passord, ligger e-posten igjen i klartekst, og FR-4-testen feiler. Tabellen samler også e-poster fra folk som ikke har konto, uten noen sletting (se F15).
- **Rettelse:** Legg til i AD-8: «Identity-funksjonen som kalles ved sletting, sletter også brukerens rader i `sesjon` og alle rader i `innloggingsforsok` med brukerens e-post.» Legg til i AD-4: «Ved vellykket innlogging slettes radene for e-posten. Rader eldre enn 15 min slettes ved hvert innloggingsforsøk.» Vurder å lagre SHA-256 av e-post (små bokstaver) i stedet for e-posten selv; da er heller ikke klartekst lagret.

### F2 — Avhengighetsgrafen hindrer vurdering og fullførte i oppdragsdetaljer og interesserte (høy)

- **PRD:** FR-9 (detaljene viser oppdragsgiverens antall fullførte og gjennomsnittlige vurdering), FR-14 (hver interessert vises med fullførte og vurdering), FR-21 («Samme visning brukes i FR-9 og FR-14»).
- **Motsigelse:** FR-9 og FR-14 ligger i `oppdrag`. Gjennomsnittet kommer fra `tilbakemelding`, men grafen har `tilbakemelding → oppdrag`, ikke omvendt. `oppdrag` kan altså ikke hente vurderinger uten en sirkel. To stories (detaljer og profil) vil løse dette ulikt: egne spørringer mot `tilbakemelding`-tabellen fra `oppdrag`, eller duplisert snittberegning.
- **Rettelse:** Ny regel i AD-1: «Pilene gjelder `service.py`. En slices `routes.py` kan i tillegg kalle lesefunksjoner i slices som ligger over den i grafen, for å sette sammen en side.» Og: «`tilbakemelding/service.py` har én funksjon `erfaring(bruker_ids) -> {id: (fullforte, fullforte_per_kategori, snitt, antall)}` som brukes av FR-9, FR-14, FR-18 og FR-21. Den henter fullførte fra `oppdrag/service.py`. Formatet «4,3 av 5, 7 vurderinger» / «Ingen vurderinger ennå» er én Jinja-makro i `core`.» Alternativt: flytt sidene for detaljer og interesserte til en slice over `tilbakemelding`.

### F3 — Kategoriliste og feltgrenser trengs i både `oppdrag` og `ki` (høy)

- **PRD:** FR-25: KI-svaret må oppfylle «de samme reglene som i FR-5» (tittel 3–80, beskrivelse 10–1000, kategori fra §3). FR-26: mocken bruker kategorilista. FR-23: minst 10 tegn, samme som beskrivelsen i FR-5.
- **Hull:** AD-10 sier «Grensene står ett sted per slice». `ki` kan ikke importere `oppdrag` (`oppdrag → ki`), så grensene og kategorilista må skrives to ganger, og PRD-ens poeng (forslag som ellers avvises ved «Publiser», §9.2) går tapt hvis de glir fra hverandre.
- **Rettelse:** Ny rad i Consistency Conventions, «Delte domeneverdier»: «Kategorilista (§3, i rekkefølge), statusnavn og feltgrensene for tittel og beskrivelse ligger én gang i `core/domene.py`. `oppdrag` og `ki` leser derfra.» Endre AD-10 til «Grensene står ett sted: i `core/domene.py` når mer enn én slice trenger dem, ellers i eier-slicen.»

### F4 — Normalisering av e-post og passord er ikke bestemt (høy)

- **PRD:** FR-1 og FR-2: e-post uten å skille store og små bokstaver. §4.0: mellomrom i tekstfelt fjernes. FR-1: passord 8–64 tegn.
- **Hull:** AD-4 sier at e-post er med små bokstaver i `innloggingsforsok`, men ikke hvordan `bruker.epost` lagres og sammenlignes. AD-10 sier at *all* tekst fra brukere trimmes og NFC-normaliseres. Gjelder det passord? Hvis registrering (FR-1) og innlogging (FR-2) eller sletting (FR-4) gjør det ulikt, slipper ikke brukeren inn. Lagres e-post slik den er skrevet, blir unik-regelen avhengig av databasen (`lower()`-indekser er ulike i SQLite og Postgres).
- **Rettelse:** I AD-6: «`hash_passord` og `sjekk_passord` NFC-normaliserer passordet, men trimmer det ikke. Lengden 8–64 sjekkes på den normaliserte verdien.» I AD-10: «Unntak: passord trimmes ikke (AD-6).» Ny regel i `identity`: «E-post trimmes, NFC-normaliseres og gjøres om til små bokstaver i én funksjon `normaliser_epost` før lagring og før alle oppslag. Kolonnen har en vanlig unik-constraint (NULL for slettede, AD-8).»

### F5 — Bare statusskriving er atomisk; interesse, redigering og engangsregler er det ikke (høy)

- **PRD:** §4.0: «Hver statusovergang sjekker gjeldende status i samme operasjon … bare den første utføres.» FR-12: interesse avvises hvis status ikke er Åpen; ny interesse fra samme bruker avvises. FR-6: redigering bare mens Åpen. FR-20: én tilbakemelding per person per oppdrag. FR-4: Åpne oppdrag slettes.
- **Hull:** AD-2 gjelder bare `oppdrag.status`. Å melde interesse (INSERT) mens oppdragsgiveren velger, avbryter eller sletter kontoen, og å redigere mens en hjelper velges, er like utsatt for kappløp. Dobbeltklikk på «Meld interesse» eller «Send» gir enten to rader eller `IntegrityError` → krasj (bryter NFR-10). Constraints er utsatt til koden («Kolonner, indekser …»), men regelen om *at* engangsregler håndheves i databasen er tverrgående.
- **Rettelse:** Utvid AD-2: «Alle skrivinger som avhenger av oppdragets status (redigering, melde og trekke interesse, fjerne/trekke seg), gjøres i én transaksjon som starter med en betinget `UPDATE oppdrag SET versjon = versjon + 1 WHERE id = ? AND status = forventet [AND tidspunkt > nå]`; 0 rader gir samme avvisning.» Ny rad i konvensjonene: «Engangsregler (én interesse per bruker og oppdrag, én tilbakemelding per giver og oppdrag, én aktiv e-post) har unik-constraint i databasen. `IntegrityError` fra dem gjøres om til `RegelBrudd` i servicen, aldri 500.»

### F6 — Tid med tidssone i SQLite vs Postgres (høy)

- **PRD:** FR-5, FR-8, FR-10, FR-19: «passert» i norsk tid; NFR-1: samme app lokalt og i produksjon.
- **Hull:** AD-9 sier «lagres i UTC», AD-13 «samme kode mot SQLite og Postgres». SQLite lagrer ikke tidssone: `DateTime(timezone=True)` gir naive verdier tilbake fra SQLite og aware fra Postgres. Én story som sammenligner med en aware `nå` fra `core`, krasjer lokalt eller i produksjon. Uten regel velger stories ulikt.
- **Rettelse:** Legg til i AD-9: «Alle tidskolonner bruker én `UtcDateTime`-type (TypeDecorator) i `core/db.py`, som lagrer naiv UTC og alltid gir tilbake aware UTC. `core.klokke.na()` gir aware UTC. Datoer uten klokkeslett (fødselsdato) er `Date`.» PRD FR-5 sier «lagres i norsk tid»; legg til en setning om at UTC-lagring av et tidspunkt som tolkes og vises i Europe/Oslo oppfyller kravet.

### F7 — 10 s er ikke total tid i `httpx`, og Vercel-grensen er ukjent (middels)

- **PRD:** FR-25: «Får appen ikke svar innen 10 sekunder, avbrytes forespørselen, og et svar som kommer senere, vises ikke.» Skjemaet skal beholde det brukeren skrev.
- **Hull:** `httpx`-tidsavbrudd på 10 s gjelder hver fase for seg (tilkobling, lesing per bit osv.), ikke hele kallet, så et sakte svar kan ta mye lenger. Spinen sier heller ikke hva Vercel-funksjonens maksimale kjøretid er; hvis den er lik eller kortere enn KI-tiden, dreper Vercel kallet før den vennlige meldingen vises.
- **Rettelse:** I AD-12: «OpenRouter-utgaven har en total frist på 10 s (målt med `core`-klokka rundt hele kallet, og `httpx.Timeout(10)` som øvre grense per fase). Svar etter fristen forkastes. Vercel-funksjonens `maxDuration` settes til minst 20 s.» Testdobbelen for «for sent svar» bruker fristen, ikke ekte venting.

### F8 — Tester skal alltid bruke mock, spinen sier testdobbel (middels)

- **PRD:** FR-26: «Automatiske tester kjører alltid i mock-modus, også når `.env` har en API-nøkkel; unntaket er testdoblene i FR-25.»
- **Motsigelse:** Miljøtabellen sier KI = testdobbel i Test/CI, og AD-12 velger utgave ved oppstart ut fra nøkkelen. Det sier ikke at en nøkkel i `.env` ignoreres i tester, og mock-reglene i FR-26 (nøkkelord, tittel) må testes mot mocken.
- **Rettelse:** I AD-12 og miljøtabellen: «Med `APP_ENV=test` brukes alltid mock, uansett `OPENROUTER_API_KEY`. FR-25-testene bytter inn testdobbelen per test (FastAPI dependency override).»

### F9 — «Virker uten JavaScript» mot krav som trenger JS (middels)

- **PRD:** §4.0: knapper som sender noe, er deaktivert mens forespørselen pågår. FR-23: «Lager forslag …» leses opp mens forslaget hentes. FR-24: «Bruk»/«Forkast» per felt. NFR-8 og FR-7/15/17/19: bekreftelse før handling. NFR-7: dialoger flytter fokus.
- **Hull:** Konvensjonen sier at JS bare brukes til fokus og `<dialog>`, og at alle skjema virker uten JS. Den sier ikke (a) hvordan KI-forslag hentes (hel sidelasting med POST eller `fetch` som gir et HTML-utsnitt), (b) hva som skjer med bekreftelse uten JS, (c) hvem som eier skriptet som deaktiverer knapper. `oppdrag`- og `ki`-storyene kan bygge KI-flyten på hver sin måte, og hver handling-story kan lage sin egen bekreftelse.
- **Rettelse:** Ny rad i konvensjonene, «Progressiv forbedring»: «Uten JS: hver bekreftelse er en egen GET-side med samme tekst og en POST-knapp; KI-forslag er en POST som viser skjemaet på nytt med forslagsboksene, og «Bruk»/«Forkast» er submit-knapper. Med JS: `core/static/js/` har tre felles skript: `send.js` (deaktiverer knappen og stopper ny innsending, §4.0), `dialog.js` (åpner bekreftelsen som `<dialog>`, NFR-7) og `ki.js` (henter forslag med `fetch` fra samme rute, som gir et HTML-utsnitt; `aria-live`). Ingen slice skriver egne skript for dette.»

### F10 — Telefon, e-post og fødselsdato kan lekke via maler (middels)

- **PRD:** FR-16: «Ingen andre steder i appen viser telefonnummer, e-post eller fødselsdato, heller ikke i svar fra serveren.» FR-21: profilen viser dem aldri.
- **Hull:** AD-3 bestemmer *når* telefon er synlig, men ikke hvordan data når malen. Gir en rute et ORM-`bruker`-objekt til Jinja, kan feltene havne i HTML (skjulte felt, `data-`-attributter) uten at noen ser det.
- **Rettelse:** Ny regel (i AD-8 eller egen AD): «Maler får aldri ORM-objekter for `bruker`. `identity/service.py` gir `OffentligBruker` (id, visningsnavn, postnummer med poststed, slettet). Telefonnummer gis bare av `oppdrag/service.telefon_for_motpart(oppdrag, seer)`, og egne opplysninger bare til «Rediger profil». En test søker etter seed-brukernes telefon, e-post og fødselsdato i HTML fra alle GET-ruter.»

### F11 — Clickjacking er ikke dekket (middels)

- **PRD:** NFR-12: «handlinger som endrer data, kan ikke utløses fra andre nettsteder.»
- **Hull:** AD-5 stopper forfalskede forespørsler, men ikke at et annet nettsted viser appen i en `<iframe>` og lurer brukeren til å trykke (CSRF-nøkkelen er da gyldig).
- **Rettelse:** I AD-5: «Alle svar har `Content-Security-Policy: frame-ancestors 'none'` og `X-Frame-Options: DENY`, satt i én mellomvare i `core`.» Vurder også `X-Content-Type-Options: nosniff` og `Referrer-Policy: same-origin` på samme sted.

### F12 — AD-7 mot FR-3 (og AD-4) (middels)

- **PRD:** FR-3: forespørsler uten gyldig innlogging «avvises på serveren, og nettleseren sendes til innloggingssiden»; en test går gjennom alle ruter uten innlogging.
- **Motsigelse:** AD-4 sier at den globale sjekken sender *alle* forespørsler til innloggingssiden; AD-7 sier at POST viser skjemaet på nytt. `core` kan ikke vise en slices skjema (den importerer ingen slice), så den «globale» sjekken må i praksis ligge i hver rute for POST. Gjenvisning uten innlogging kan dessuten vise innhold fra databasen (for eksempel tittelen på oppdraget som redigeres) til noen som ikke er innlogget, og det bryter FR-3.
- **Rettelse:** Presiser i AD-4/AD-7: «Uten gyldig sesjon: GET → 303 til innlogging med `neste=`. POST → ingen data endres, HTTP 401, og `core` viser en felles side med innloggingsfelt og de innsendte verdiene som skjulte felt (unntatt passord), uten noe innhold fra databasen. Etter innlogging sendes POST-en videre med ny CSRF-nøkkel, og bare hvis samme bruker logget inn.» FR-3-testen godtar 303 (GET) og 401 (POST).

### F13 — Manglende piler: `tilbakemelding → identity`, `mine_oppdrag → identity` (middels)

- **PRD:** FR-20: tilbakemelding til slettet bruker avvises; FR-21: giverens navn eller «Slettet bruker»; FR-18: navnet på valgt hjelper.
- **Hull:** AD-8 sier at visningsnavnet kommer fra én funksjon i `identity`, men `tilbakemelding` og `mine_oppdrag` har ingen pil til `identity`. Det er uklart om AD-1 tillater å gå via en annen slice (transitivt).
- **Rettelse:** Legg til pilene `tilbakemelding --> identity` og `mine_oppdrag --> identity` i grafen, og skriv i AD-1: «Bare direkte piler gjelder.»

### F14 — Ingen felles regel for «ingen tilgang» / «finnes ikke» (middels)

- **PRD:** FR-9: forespørsler fra andre avvises; FR-4: direkte lenke til slettet profil gir en forståelig melding; FR-6/7/17/22: forsøk fra andre avvises; NFR-10.
- **Hull:** Feil-konvensjonen dekker `RegelBrudd` i skjema (422), men ikke GET mot noe brukeren ikke har tilgang til, eller som ikke finnes. Slices vil svare 403, 404 eller 422 hver for seg.
- **Rettelse:** I raden «Feil»: «`IngenTilgang` og `FinnesIkke` fra service gir begge HTTP 404 og samme vennlige side, så det ikke avsløres om et oppdrag finnes. Slettet bruker gir 404 med teksten fra FR-4.»

### F15 — Lagringstid for `sesjon`, `innloggingsforsok`, `ki_bruk` uten cron (middels)

- **PRD:** NFR-9: bare data appen trenger. AD-3: ingen cron.
- **Hull:** Utløpte sesjoner, gamle innloggingsforsøk (med e-poster, se F1) og gamle KI-tellinger blir liggende for alltid.
- **Rettelse:** Ny rad «Lagringstid» i konvensjonene: «Uten cron rydder eier-slicen ved bruk: utløpte sesjoner slettes ved innlogging, `innloggingsforsok` eldre enn 15 min ved hvert forsøk, `ki_bruk` eldre enn 1 time ved hver telling.»

### F16 — Seed bryter AD-1 og tjenestereglene (middels)

- **PRD:** NFR-2: utgåtte oppdrag («i går»), Utført med tilbakemelding, Hjelper valgt etter tidspunktet; kan lastes på nytt med én kommando; en automatisk test laster dataene.
- **Hull:** AD-1 sier at bare eier-slicen skriver en tabell. Går seed gjennom servicene, avvises «i går»-oppdrag (FR-5). Går den rett mot modellene, brytes AD-1. Uten regel gjør seed-storyen enten det ene eller det andre uten at det er bestemt.
- **Rettelse:** I AD-1: «`app/seed.py` er det eneste unntaket: den skriver med modellene direkte, bare når `APP_ENV` er `local` eller `test` (AD-14), og tømmer tabellene før innlasting, slik at den kan kjøres på nytt.»

### F17 — Hvordan skjemaet lages lokalt (Alembic) står ikke (middels)

- **PRD:** NFR-1: eksakte kommandoer, i gang innen 15 minutter på en ren maskin.
- **Hull:** «Migrasjoner kjøres av GitHub Actions før publisering, aldri når appen starter.» Det står ikke hvordan SQLite-fila får tabellene lokalt, eller om testene bruker Alembic eller `create_all`.
- **Rettelse:** I Structural Seed: «Lokalt kjører `uv run python -m app.seed` først `alembic upgrade head` og laster så postnumre og eksempeldata. Testene bruker også `alembic upgrade head`, så migrasjonene testes.» Legg kommandoen i testkonvensjonen.

### F18 — Manuell tilbakestilling av passord må bruke AD-6 (lav)

- **PRD:** §6.2: gruppen tilbakestiller passord eller sletter kontoen manuelt i databasen; §4.7: gruppen fjerner krenkende kommentarer manuelt.
- **Hull:** En manuell bcrypt-hash uten SHA-256-forhåndshashing (AD-6) gir et passord som aldri virker. Manuell sletting utenom `profil/service.py` bryter AD-8 og F1.
- **Rettelse:** I Deferred eller Structural Seed: «`uv run python -m app.admin` har to kommandoer: `nytt-passord <e-post>` (kaller `hash_passord`) og `slett-konto <e-post>` (kaller slettingen i `profil/service.py`). Kommentarer fjernes ved at `tilbakemelding.kommentar` settes til NULL; vurderingen beholdes.»

### F19 — KI-kvote: vindu og hva som telles (lav)

- **PRD:** FR-23: høyst 20 forslag per bruker per time; flere *forespørsler* avvises.
- **Hull:** Glidende time eller klokketime? Telles mock, feil og tidsavbrudd?
- **Rettelse:** I AD-12: «Glidende 60 min fra `core`-klokka. Hver godtatt forespørsel registreres før kallet, også i mock og ved feil.»

### F20 — «Meldt før endring» trenger et lagret tidspunkt (lav)

- **PRD:** FR-6, FR-14, FR-18: interesser meldt før en endring av tidspunkt, godtgjørelse eller postnummer merkes.
- **Hull:** AD-3 regner ut merker ved lesing, men merket krever at endringstidspunktet lagres, og at interessen har et tidspunkt. Det sier ikke spinen, og redigering (FR-6) og merkene (FR-14, FR-18) er ulike stories.
- **Rettelse:** I AD-3: «`oppdrag.vesentlig_endret` settes av redigering når tidspunkt, godtgjørelse eller postnummer endres. «Meldt før endring» = `interesse.opprettet < oppdrag.vesentlig_endret`.»

### F21 — Statusord og vurderingsformat ett sted (lav)

- **PRD:** NFR-7: status alltid med ord; FR-21: «4,3 av 5, 7 vurderinger», samme visning i FR-9 og FR-14.
- **Hull:** Statusverdiene er ASCII (`hjelper_valgt`), visningen er «Hjelper valgt». Det står ikke hvor oversettelsen ligger.
- **Rettelse:** I «Maler og frontend»: «Jinja-filtre i `core`: `status_tekst` (AD-2-verdi → ord fra §3), `vurdering` (F2) og `norsk_tid` (AD-9). Maler formaterer aldri selv.»

### F22 — FR-1 alder i norsk tid er ikke bundet til AD-9 (lav)

- **PRD:** FR-1: alder regnes i norsk tid; 29. februar fyller år 1. mars.
- **Hull:** AD-9 binder ikke FR-1, og AD-3 nevner klokka bare for `oppdrag`.
- **Rettelse:** Legg FR-1 til i AD-9 Binds og skriv: «"I dag" er datoen i Europe/Oslo fra `core.klokke`, også for alder (FR-1).»

### F23 — `ki_bruk` er ikke med i slettingen (lav)

- **PRD:** FR-4, NFR-9.
- **Hull:** AD-8 kaller oppdrag, tilbakemelding og identity, ikke `ki`, og `profil` har ingen pil til `ki`. Radene peker til gravsteinen. Det er lite data, men slettingen er ikke fullstendig.
- **Rettelse:** Enten legg til `profil --> ki` og en `ki.slett_for_bruker`, eller skriv i AD-8 at `ki_bruk` beholdes til den ryddes etter en time (F15).

### F24 — NFR-12-test og gitleaks står ikke i testkonvensjonen (lav)

- **PRD:** NFR-12: «Mekanismen … velges i arkitekturen og testes der.» NFR-3: historikken skannes med gitleaks før innlevering.
- **Rettelse:** I «Tester»: «`tests/core/` har tester for CSRF (mangler eller feil nøkkel, fremmed `Origin`, POST før innlogging) og for `frame-ancestors`. CI kjører gitleaks på hele historikken.»

---

## Sjekket og i orden

- §8 til arkitekturen: postnummerkilde (Bring, `data/postnumre.tsv`; vilkårene er i Deferred), CSRF (AD-5), sommertid (AD-9), tegnsett (AD-10).
- NFR-4: bcrypt med forhåndshashing (AD-6). NFR-3/NFR-1: AD-14, `.env.example`.
- FR-2: grense for innlogging og 7 dager (AD-4), sesjoner i DB (Vercel uten minne).
- §4.0 statusovergang og samtidighetsmelding (AD-2), utgått og merker uten cron (AD-3).
- FR-4 gravstein og ett sted for slettingen (AD-8), utenom F1, F13 og F23.
- FR-23/25/26: ett KI-grensesnitt, bare beskrivelsen sendes, prompt i egen fil, svar valideres likt (AD-12), utenom F3, F7, F8 og F19.
- NFR-12 XSS (AD-11), NFR-10 vennlig feilside, NFR-11 meny i `base.html`, logging uten personopplysninger (NFR-9).
- Deferred samsvarer med PRD §6.2 (glemt passord, e-post, rapportering).
