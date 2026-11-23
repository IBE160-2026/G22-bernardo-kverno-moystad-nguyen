---
type: review
lens: adversarial (par av enheter som følger spinen og likevel bygger uforenlig)
spine: ../ARCHITECTURE-SPINE.md (draft, oppdatert 2026-11-23)
context: ../../../prds/prd-G22-bernardo-kverno-moystad-nguyen-2026-11-05/prd.md
date: 2026-11-23
---

# Adversarial gjennomgang av arkitekturspinen

## Konklusjon

Spinen er god på *hva* som skal gjelde (én eier per tabell, atomiske statusoverganger, én render-funksjon), men nesten taus om *mekanikken under en forespørsel*: hvem som eier databasesesjonen og committer, hvordan `core` når `identity` uten å importere den, hvilken rekkefølge mellomvarene har, hvilke URL-er og rutenavn som finnes, og hvordan testdatabasen settes opp. Det er nøyaktig der to nybegynnere eller to agenter som bygger hver sin story, gjør hvert sitt fornuftige valg og ender med noe som ikke virker sammen.

Jeg fant **3 kritiske, 9 høye, 6 middels og 2 lave** hull. Ingen av dem gjentar funn fra `reconcile-prd.md` eller `reconcile-ux.md`. De kritiske må lukkes før første story i `core`, fordi de bestemmer signaturen til hver service-funksjon.

Alvorlighet: **kritisk** = to enheter som følger spinen, gir datatap, delvis lagret sletting eller en app som ikke virker i produksjon. **høy** = stor sannsynlighet for uforenlig bygging eller 500-feil. **middels** = reelt avvik som oppdages sent. **lav** = presisering.

| # | Hull | Par som kolliderer | Alvorlighet |
|---|---|---|---|
| A1 | Ingen eier av transaksjonen; services kan committe og rulle tilbake | FR-7 avbryt × FR-4 sletting | kritisk |
| A2 | Postnumre finnes ikke i produksjon eller preview | seed × FR-1/FR-5 på Vercel | kritisk |
| A3 | `core` må logge inn og slå opp sesjon, men kan ikke bruke `identity` | AD-4/AD-7-mellomvare × FR-2 | kritisk |
| A4 | URL-er, rutenavn og unntakslista i AD-4 er ikke fastsatt | AD-4 × FR-1; FR-9 × FR-21 | høy |
| A5 | Ingen felles måte å få innlogget bruker og CSRF-nøkkel i ruta | AD-7 × alle ruter | høy |
| A6 | Rekkefølge på mellomvarer, lesing av skjemakroppen og feltnavn i AD-7 | AD-5 × AD-7; AD-7 × FR-4 | høy |
| A7 | AD-2 sier ikke at sjekker skjer *etter* den betingede UPDATE-en | FR-15 × FR-13; SQLite × Postgres | høy |
| A8 | `tidligere_hjelper` har ingen form, og to stories skriver den | FR-17 × FR-4 × FR-12/FR-18 | høy |
| A9 | Fremmednøkler oppfører seg ulikt i SQLite og Postgres | FR-4 sletting × FR-12 interesse | høy |
| A10 | KI-kvoten holder en skrivetransaksjon åpen under et 10 s eksternt kall | AD-12 × A1 × alle skrivinger lokalt | høy |
| A11 | Testdatabase: SQLite i minnet og Alembic ser ikke samme database; fixtures kolliderer | testoppsett × hver slice | høy |
| A12 | Én avvisningstype for tre ulike svar (422, PRG, redirect til eksisterende) | FR-15 × FR-17 × FR-5 | høy |
| A13 | Navnerom for maler, eier av brukerkortet og formen på `erfaring()` | FR-9/FR-14 × FR-21 | middels |
| A14 | Kategori lagres som kode eller tekst? | FR-5 × FR-11 × FR-25 × FR-21 | middels |
| A15 | `/oppdrag/ny` mot `/oppdrag/{id}` gir 422 avhengig av rekkefølge | FR-5 × FR-9 | middels |
| A16 | E2E: én `TEST_NA` per prosess og delt seed-database | to e2e-tester | middels |
| A17 | Feilsider og menykroken krasjer når transaksjonen er ødelagt; fragmenter spiser kvitteringen | NFR-10 × render-krok × AD-15 | middels |
| A18 | Klokka kan importeres på to måter, og bare én kan byttes i tester | to slices × felles klokkefixture | middels |
| A19 | `OffentligBruker` mangler «om meg», og «egne opplysninger» har ingen type | FR-21/FR-22 × AD-16 | lav |
| A20 | Tilgang til `postnummer` og poststed er ikke ett funksjonskall | identity × oppdrag × profil | lav |

---

## Kritiske

### A1 — Ingen eier av transaksjonen; services kan committe og rulle tilbake (kritisk)

- **Enhet A:** Story for FR-7 (avbryte). Utvikleren skriver `oppdrag/service.avbryt(db, oppdrag_id, seer)`, som gjør den betingede UPDATE-en fra AD-2 og så `db.commit()`, fordi ruta trenger at endringen er lagret før redirect. Følger AD-2 til punkt og prikke.
- **Enhet B:** Story for FR-4 (slette konto). `profil/service.slett_konto` åpner «én databasetransaksjon» (AD-8) og kaller `oppdrag.service`-funksjoner (som igjen kaller overgangsfunksjonen) og så `identity`.
- **Kollisjon:** Første `commit()` inne i oppdrag lagrer halve slettingen. Feiler `identity`-delen etterpå (for eksempel feil passord oppdaget sent, eller en `IntegrityError`), er oppdragene allerede avbrutt, men brukeren finnes fortsatt. Samme feil oppstår når FR-12-storyen gjør om `IntegrityError` til `RegelBrudd` med `db.rollback()` (vanlig mønster): rollbacken ruller tilbake alt profil har gjort før, og SQLAlchemy starter en ny transaksjon automatisk, så resten av slettingen lagres alene. På Postgres er transaksjonen i tillegg ubrukelig etter en feilet setning («current transaction is aborted»), mens SQLite fortsetter. Testene mot SQLite kan altså bestå mens Postgres feiler.
- **I tillegg:** Commit i teardown av en `yield`-avhengighet kan, avhengig av FastAPI-versjon, skje etter at 303-svaret er sendt. Da kan neste GET komme før dataene er lagret, eller brukeren får kvittering selv om commit feilet.
- **Rettelse (ny AD-17 «Én transaksjon per forespørsel, eid av ruta»):**
  > - `core/db.py` har én avhengighet `hent_db()` som gir en `Session` per forespørsel. Alle service-funksjoner tar `db: Session` som første parameter. Ingen service oppretter egne sesjoner.
  > - Bare ruta avslutter transaksjonen: en POST-rute kjører service-kallene inne i `with db.begin():` og bygger svaret (redirect eller 422) etter blokken. Services kaller aldri `commit()` eller `rollback()`; de kan kalle `flush()`.
  > - En service som må fange `IntegrityError` (AD-2), gjør det rundt én setning med `with db.begin_nested():` (SAVEPOINT), slik at resten av transaksjonen kan fortsette. `core/db.py` setter opp SAVEPOINT for pysqlite etter SQLAlchemy-dokumentasjonen.
  > - En service som kaller en annen service, deler samme `db` og samme transaksjon (AD-8).
  > - En test kjører slettingen med en `identity`-feil injisert til slutt og sjekker at ingen oppdrag er endret, mot både SQLite og Postgres.

### A2 — Postnumre finnes ikke i produksjon eller preview (kritisk)

- **Enhet A:** Seed-storyen (NFR-2). AD-1 sier at `app/seed.py` bare kjører når `APP_ENV` er `local` eller `test`, og Klientatferd sier at `static/postnumre.json` «lages ved seeding». Utvikleren lar seed laste `postnummer`-tabellen og skrive JSON-fila, og legger JSON-fila i `.gitignore` fordi den er generert.
- **Enhet B:** Story for FR-1 (registrering) og publiseringsstoryen. Registrering krever at postnummeret finnes i `postnummer`. Vercel kjører ikke seed, og GitHub Actions kjører bare `alembic upgrade head`.
- **Kollisjon:** På Supabase (begge prosjekter) er `postnummer` tom. Ingen kan registrere seg eller legge ut oppdrag i produksjon, og `skjema.js` får 404 på `postnumre.json`. Lokalt og i CI virker alt, så feilen oppdages først ved publisering. AD-1 sier også at `core` eier `postnummer` «bare lesing etter seeding», men ingenting seeder produksjon.
- **Rettelse (i AD-1, AD-13 og Klientatferd):**
  > - Postnumre er referansedata, ikke eksempeldata. De lastes av en egen Alembic-migrasjon som leser `data/postnumre.tsv`, slik at `alembic upgrade head` gir dem i alle miljøer (lokalt, test, CI, preview, produksjon). Seed tømmer aldri `postnummer`.
  > - `core/static/postnumre.json` lages av `uv run python -m app.core.postnumre` fra samme TSV og **sjekkes inn** i repoet. En test sjekker at JSON-fila og TSV-fila har samme innhold, så de ikke glir fra hverandre.
  > - Nye versjoner av registeret legges inn som ny migrasjon.

### A3 — `core` må logge inn og slå opp sesjon, men kan ikke bruke `identity` (kritisk)

- **Enhet A:** Core-storyen for AD-4/AD-7. Den globale sjekken ligger i `core`, og `core` «importerer ingen slice». Utvikleren slår derfor opp `sesjon` og `bruker` med egen SQL i `core`, og for AD-7 skriver hen egen innlogging i mellomvaren: bcrypt-sjekk, teller i `innloggingsforsok`, ny rad i `sesjon`.
- **Enhet B:** Identity-storyen for FR-2. Den lager `identity/service.logg_inn` med `normaliser_epost`, `sjekk_passord`, telling og rydding etter AD-4 og AD-6.
- **Kollisjon:** To innlogginger. `core` skriver til `sesjon` og `innloggingsforsok`, som `identity` eier (AD-1), og kaller bcrypt selv (AD-6 sier at ingen annen kode gjør det). Normalisering, sperring etter 5 forsøk og rydding vil gli fra hverandre, og FR-4 («alle innlogginger avsluttes») kan bryte hvis `core` cacher eller tolker sesjoner annerledes. Hvis A i stedet importerer `identity`, brytes AD-1.
- **Rettelse (i AD-1 og AD-4):**
  > - `core/sesjon.py` definerer et grensesnitt `Autentisering` med `finn_innlogget(db, nokkel) -> Innlogget | None`, `logg_inn(db, epost, passord) -> str` (ny sesjonsnøkkel, eller `RegelBrudd`) og `logg_ut(db, nokkel)`. `Innlogget` er en liten dataklasse i `core` (`bruker_id`, `visningsnavn`).
  > - `lag_app()` registrerer `identity.service` som implementasjon, på samme måte som menykroken. Mellomvaren i AD-4/AD-7 og FR-2-ruta kaller begge **bare** dette grensesnittet. `core` leser og skriver aldri `sesjon`, `bruker` eller `innloggingsforsok` selv.
  > - Mangler registreringen når appen starter, nekter `lag_app()` å starte.

---

## Høye

### A4 — URL-er, rutenavn og unntakslista i AD-4 er ikke fastsatt (høy)

- **Par 1:** Core-storyen skriver unntakslista i AD-4 som `{"/registrering", "/logg-inn", "/static"}`. Identity-storyen kaller ruta `/registrer` (eller `/ny-bruker`). Begge følger spinen. Resultat: registreringssiden krever innlogging, og ingen kan lage konto.
- **Par 2:** Detaljsiden (FR-9, i `oppdrag`) skal lenke til profilen (FR-21, i `profil`). `oppdrag` kan ikke importere `profil`, så utvikleren bruker `request.url_for("vis", ...)` eller skriver `/bruker/{id}` rett i malen. Profil-storyen kaller ruta `/profil/{id}` med funksjonsnavnet `vis`. Funksjonsnavnet `vis` brukes også i `oppdrag`. Starlette slår opp rutenavn globalt, så `url_for("vis")` gir den første som ble registrert, og lenka går til feil side uten feilmelding.
- **Rettelse (ny rad «URL-er og rutenavn» i Consistency Conventions, med tabell):**
  > - Spinen har én tabell over alle sider: `/` (oversikt), `/logg-inn`, `/logg-ut` (POST), `/registrer`, `/oppdrag/ny`, `/oppdrag/{oppdrag_id:int}`, `/oppdrag/{oppdrag_id:int}/rediger`, `/oppdrag/{oppdrag_id:int}/<handling>` (GET = bekreftelsesside, POST = handling), `/oppdrag/forslag`, `/mine-oppdrag`, `/profil` (egen), `/profil/{bruker_id:int}`, `/profil/rediger`, `/profil/slett`.
  > - Rutenavn er `<slice>.<handling>` (`name="profil.vis"`), og maler lager lenker bare med `url_for(navn, ...)`. En test sjekker at alle rutenavn er unike.
  > - Offentlige ruter markeres på ruta (`dependencies=[Depends(core.offentlig)]` eller tilsvarende), ikke med en liste over stier i `core`. FR-3-testen leser markeringen og sjekker resten.

### A5 — Ingen felles måte å få innlogget bruker og CSRF-nøkkel i ruta (høy)

- **Enhet A:** Core-storyen for AD-7 logger inn i mellomvaren, legger brukeren i `request.state.bruker` og setter ny sesjonscookie på svaret. Den bytter også CSRF-cookien ved innlogging, som er vanlig god praksis.
- **Enhet B:** Oppdrag-storyen lager sin egen avhengighet `hent_bruker(request, db)` som leser sesjonscookien fra `request.cookies` og slår opp i databasen. `core.render` leser CSRF-nøkkelen fra `request.cookies`.
- **Kollisjon:** Etter AD-7-innloggingen har forespørselen fortsatt den gamle, utløpte cookien. `hent_bruker` sier «ikke innlogget», og ruta svarer 401 en gang til (evig løkke) eller krasjer. Viser ruta skjemaet på nytt med 422, får skjemaet den *gamle* CSRF-nøkkelen, mens nettleseren har fått en ny cookie, og neste innsending avvises av AD-5.
- **Rettelse (i AD-4 og AD-5):**
  > - Mellomvaren setter `request.state.innlogget` (`Innlogget` fra A3, eller `None`). Ruter får brukeren bare gjennom `core.innlogget_bruker` (FastAPI-avhengighet som leser `request.state`). Ingen rute eller service leser sesjonscookien.
  > - CSRF-nøkkelen leses bare fra `request.state.csrf`, som CSRF-mellomvaren setter (ny verdi hvis den byttes). CSRF-cookien er uavhengig av sesjonen og byttes ikke ved innlogging, bare når den mangler.

### A6 — Rekkefølge på mellomvarer, lesing av skjemakroppen og feltnavn i AD-7 (høy)

- **Par 1 (rekkefølge):** AD-5 og AD-4/AD-7 er to mellomvarer, gjerne i to stories. Starlette kjører den sist registrerte først. Registreres innloggingsmellomvaren etter CSRF-mellomvaren, kjører innloggingen *før* CSRF-sjekken, og et fremmed nettsted kan logge inn brukeren via 401-siden (login-CSRF). Begge stories følger spinen.
- **Par 2 (kroppen):** Både CSRF-mellomvaren og AD-7-mellomvaren må lese skjemaet. Leses `await request.form()` i en mellomvare, er det avhengig av Starlette-versjon og mellomvaretype om ruta får lese kroppen på nytt. Én utvikler skriver ren ASGI-mellomvare, en annen `BaseHTTPMiddleware`, og ruta får et tomt skjema.
- **Par 3 (feltnavn):** AD-7-siden legger til feltene for e-post og passord. Story for FR-4 har et felt `passord` (bekreftelse med passord). Når innloggingen utløper på slette-siden, ser mellomvaren `passord`, tolker skjemaet som innlogging og slipper det videre. Ruta leser innloggingsfeltet som bekreftelse.
- **Rettelse (i AD-5 og AD-7):**
  > - `lag_app()` registrerer alle mellomvarer på ett sted, i denne rekkefølgen fra ytterst: feilhåndtering → sikkerhetsheadere → CSRF/Origin → sesjon og innlogging (AD-4, AD-7) → ruter. En test sender en POST med gyldige innloggingsfelt og feil CSRF og forventer avvisning uten innlogging.
  > - Skjemaet leses én gang av CSRF-mellomvaren, som legger feltene i `request.state.skjema`. Andre mellomvarer leser derfra. Mellomvarene er ren ASGI og spiller av kroppen på nytt for ruta.
  > - Innloggingsfeltene på AD-7-siden heter `_innlogging_epost` og `_innlogging_passord`. Ingen skjema i appen bruker navn som begynner med `_`. Mellomvaren fjerner dem før ruta får skjemaet.

### A7 — AD-2 sier ikke at sjekker skjer *etter* den betingede UPDATE-en (høy)

- **Enhet A:** Story for FR-15 (velge hjelper). `velg_hjelper` leser først om Amir har interesse (FR-15: «avvises hvis den valgte ikke har meldt interesse»), sjekker at `seer` er oppdragsgiver og at tidspunktet ikke er passert, og kjører så `UPDATE … SET status='hjelper_valgt' WHERE id=? AND status='apen'`.
- **Enhet B:** Story for FR-13 (trekke interesse). `trekk_interesse` kjører `UPDATE oppdrag SET versjon=versjon+1 WHERE id=? AND status='apen'` og sletter interessen.
- **Kollisjon:** Trekker Amir interessen mellom A sin lesing og A sin UPDATE, blir Amir valgt hjelper uten interesse, og FR-15 er brutt. Begge fulgte AD-2, fordi AD-2 ikke sier at alt som avgjør handlingen, må leses etter låsen. I tillegg: på SQLite tar en lesing først en leselås, og oppgradering til skrivelås kan gi «database is locked» (500) i stedet for 0 rader. På Postgres venter UPDATE-en på radlåsen og gir 0 rader. Samme kode gir ulik oppførsel lokalt og i produksjon.
- **Rettelse (i AD-2):**
  > - Den betingede UPDATE-en er første setning i transaksjonen. `WHERE` tar med alt som kan sjekkes på `oppdrag`-raden: `id`, `status`, eier (`oppdragsgiver_id = :seer` når handlingen krever det) og tidspunkt (`tidspunkt > :na` når PRD-en krever at det ikke er passert).
  > - Sjekker mot andre tabeller (interesse finnes, `tidligere_hjelper`, slettet bruker) gjøres **etter** UPDATE-en i samme transaksjon. Feiler de, kastes feilen og transaksjonen rulles tilbake av ruta (A1).
  > - Er 0 rader endret, leser servicen raden på nytt for å velge riktig melding (finnes ikke → 404, ikke eier → 404, ellers konflikt).
  > - På SQLite starter `core/db.py` skrivetransaksjoner med `BEGIN IMMEDIATE`, og «database is locked» gjøres om til konflikt-meldingen fra AD-2.

### A8 — `tidligere_hjelper` har ingen form, og to stories skriver den (høy)

- **Enhet A:** Story for FR-17. For å stoppe ny interesse fra en fjernet hjelper (FR-12) lagrer utvikleren bare *fjernede* hjelpere i `tidligere_hjelper(oppdrag_id, bruker_id)`, med unik-constraint fordi det «er en engangsregel» (AD-2 sier at engangsregler har unik-constraint).
- **Enhet B:** Story for FR-18 (Mine oppdrag) trenger både «Du er ikke lenger valgt» og «Du trakk deg», og merket «Hjelperen trakk seg», som skal forsvinne når en ny hjelper velges. Story for FR-4 skal sette oppdraget tilbake til Åpen «som i FR-17» og gi merket «Hjelperen trakk seg».
- **Kollisjon:** A lagrer ikke de som trakk seg, så B kan ikke vise «Du trakk deg» eller merket. Trekker samme hjelper seg to ganger (meld, bli valgt, trekk deg, meld, bli valgt, trekk deg), gir unik-constrainten `IntegrityError`, som AD-2 gjør om til `RegelBrudd`, og hjelperen kan ikke trekke seg. Merket «forsvinner når ny hjelper velges» kan ikke avledes (AD-3) uten et tidspunkt.
- **Rettelse (i AD-2 og AD-3):**
  > - `tidligere_hjelper(oppdrag_id, bruker_id, arsak, tidspunkt)` med `arsak` i `fjernet | trakk_seg | slettet`, uten unik-constraint. Den skrives bare av overgangen `hjelper_valgt → apen` i `oppdrag/service.py`, som FR-17 og FR-4 begge kaller. Overgangen sletter også den valgte hjelperens interesse.
  > - Avledning: «fjernet» (FR-12) = det finnes en rad med `arsak='fjernet'` for oppdraget og brukeren. «Hjelperen trakk seg» = status `apen` og den nyeste raden for oppdraget har `arsak` i `trakk_seg | slettet`. Situasjonen i FR-18 kommer fra nyeste rad for brukeren.

### A9 — Fremmednøkler oppfører seg ulikt i SQLite og Postgres (høy)

- **Enhet A:** Story for FR-4 sletter egne åpne oppdrag med `DELETE FROM oppdrag WHERE …` og regner med at interessene forsvinner, eller sletter interessene først uten lås på oppdraget.
- **Enhet B:** Story for FR-12 setter inn interesse (etter AD-2: versjon + 1 og så INSERT).
- **Kollisjon:** SQLite håndhever ikke fremmednøkler uten `PRAGMA foreign_keys=ON`. Lokalt og i SQLite-testene virker A selv om `interesse` og `tidligere_hjelper` peker til slettede oppdrag. På Postgres feiler den med brudd på fremmednøkkel, altså 500 i produksjon. Selv med riktig rekkefølge: Melder noen interesse mellom A sin `DELETE FROM interesse` og `DELETE FROM oppdrag`, feiler Postgres, fordi A ikke låste oppdraget først.
- **Rettelse (i AD-13 og AD-2):**
  > - `core/db.py` slår på `PRAGMA foreign_keys=ON` for hver SQLite-tilkobling.
  > - Migrasjonene bruker ikke `ON DELETE CASCADE`. Servicen sletter barn eksplisitt i fast rekkefølge.
  > - Sletting av et oppdrag er en statusavhengig skriving (AD-2): den starter med den betingede versjons-UPDATE-en på oppdraget, før barna slettes.

### A10 — KI-kvoten holder en skrivetransaksjon åpen under et 10 s eksternt kall (høy)

- **Enhet A:** KI-storyen følger AD-12 («hver godtatt forespørsel registreres før kallet») og A1 (én transaksjon per forespørsel): INSERT i `ki_bruk`, så OpenRouter-kallet, så commit.
- **Enhet B:** Alle andre POST-stories lokalt.
- **Kollisjon:** På SQLite har A skrivelåsen i opptil 10 s. Alle andre skrivinger venter (standard `timeout` i pysqlite er 5 s) og feiler med «database is locked». På Supabase holder A en tilkobling i transaction pooler åpen under kallet. Kvote-tellingen er også lese-så-skriv, så to samtidige forespørsler ved 19 kan begge slippe gjennom.
- **Rettelse (i AD-12):**
  > - KI-ruta gjør kvotesjekk og INSERT i `ki_bruk` i en egen, kort transaksjon som committes før kallet. Det er det eneste stedet der én forespørsel har to transaksjoner, og ingen transaksjon er åpen under det eksterne kallet.
  > - Overskridelse med én eller to ved samtidige forespørsler godtas (kvoten er vern mot kostnad, ikke en regel om rettferdighet).

### A11 — Testdatabase: SQLite i minnet og Alembic ser ikke samme database; fixtures kolliderer (høy)

- **Enhet A:** Teststoryen følger AD-13 («tester kjører `alembic upgrade head`») og miljøtabellen («SQLite i minnet»). Alembic åpner sin egen motor mot `sqlite://`, lager tabellene i en database i minnet som forsvinner når tilkoblingen lukkes, og appens motor ser en tom database («no such table»). Den neste utvikleren bruker `Base.metadata.create_all()` for å få det til å virke, og da testes ikke migrasjonene.
- **Enhet B:** Hver slice lager sin egen `tests/<slice>/conftest.py` med fixturen `bruker` og `oppdrag`, med ulike standardverdier (postnummer som ikke finnes, fødselsdato som gir 17 år). Noen lager oppdrag gjennom servicen (som avviser passert tidspunkt), andre rett med modellen.
- **Kollisjon:** Testene feiler eller blir trege og avhengige av rekkefølge. Fixturene til `oppdrag` og `profil` gir ulike brukere, og AD-16-testen (søk etter testbrukernes telefon) vet ikke hvilke brukere den skal søke etter.
- **Rettelse (i Tester og AD-13):**
  > - Testene bruker en midlertidig SQLite-*fil* (eller Postgres-containeren i CI), og kjører `alembic upgrade head` én gang per testkjøring. `migrations/env.py` tar imot en tilkobling utenfra. `create_all` brukes aldri.
  > - Hver test kjører i en ytre transaksjon som rulles tilbake (SQLAlchemy-oppskriften «join_transaction_mode="create_savepoint"»). Det virker fordi services aldri committer (A1).
  > - Én `tests/conftest.py` eier fabrikkene `lag_bruker(**felt)`, `lag_oppdrag(status=…, **felt)`, `lag_interesse(…)` og `lag_tilbakemelding(…)`. De skriver med modellene, som seed (AD-1-unntaket gjelder også tester), med gyldige standardverdier og postnumre fra migrasjonen (A2). Slicenes egne `conftest.py` lager ikke nye fixturer med de samme navnene.
  > - Klienten i testene lages med `lag_app()` og `dependency_overrides[hent_db]`.

### A12 — Én avvisningstype for tre ulike svar (høy)

- **Enhet A:** Story for FR-15 kaster `RegelBrudd("Oppdraget er endret. Last siden på nytt.")` når UPDATE-en endrer 0 rader. Feil-konvensjonen sier at ruta da viser skjemaet på nytt med 422. Men «Velg Amir» har ikke noe skjema, så utvikleren viser bekreftelsessiden med 422.
- **Enhet B:** Story for FR-17 lager en egen `Konflikt`-feil og gjør PRG til detaljsiden med feil-cookie, slik Feil-konvensjonen sier for konflikt.
- **Enhet C:** Story for FR-5: dobbel «Publiser» skal sende brukeren til oppdraget som finnes. AD-2 sier samtidig at `IntegrityError` fra `skjema_id` «gjøres om til `RegelBrudd`».
- **Kollisjon:** Samme situasjon gir ulike statuskoder, sider og fokus i ulike handlinger, og FR-5 kan ikke både gi `RegelBrudd` og redirect. `core` har ingen felles håndtering, så hver rute fanger feilene selv.
- **Rettelse (i Feil-konvensjonen, med typene i `core/feil.py`):**
  > - `RegelBrudd(feil: list[(felt, melding)])`: bare for skjema med felt brukeren skriver i. Ruta viser skjemaet på nytt med 422.
  > - `Konflikt(melding, til_url)`: AD-2 med 0 rader, og alle avvisninger av handlinger uten felt (velg, avbryt, utført, fjern, trekk seg, trekk interesse, «tidligere forsøk avvises» i FR-19). Gir PRG til `til_url` (detaljsiden) med feilmeldingen i cookien.
  > - `Duplikat(til_url)`: unik-constraint som betyr «allerede gjort» (`skjema_id`). Gir PRG til det som finnes, med vanlig kvittering.
  > - `IngenTilgang` og `FinnesIkke`: 404 som før.
  > - `core` har én exception-handler for hver type, så rutene fanger dem ikke selv.

---

## Middels

### A13 — Navnerom for maler, eier av brukerkortet og formen på `erfaring()` (middels)

- **Par:** FR-21 sier at visningen av navn, fullførte og snitt er den samme i FR-9, FR-14 og FR-21. Oppdrag-storyen lager makroen `brukerkort` i `oppdrag/templates/_brukerkort.html`. Profil-storyen lager sin egen `_brukerkort.html` i `profil/templates/`. Hvis Jinja-miljøet er en `ChoiceLoader` over alle `templates/`-mapper (det naturlige valget), vinner den første mappa, og den ene slicen får den andres mal uten feilmelding. `erfaring(bruker_ids)` har ingen fastsatt returtype: oppdrag lager `dict[int, tuple]`, profil forventer et objekt med `per_kategori`.
- **Rettelse:**
  > - Maler ligger i `app/<slice>/templates/<slice>/…` og brukes som `"oppdrag/detaljer.html"`. `core` har ett Jinja-miljø, og maler i `core` ligger under `core/`.
  > - Brukerkortet er makroen `core/makroer.html: brukerkort(bruker: OffentligBruker, erfaring: Erfaring, lenke=True)`. Slettet bruker vises uten lenke.
  > - `erfaring(db, bruker_ids) -> dict[int, Erfaring]`, der `Erfaring` er en dataklasse i `core/domene.py`: `fullforte: int`, `per_kategori: dict[str, int]`, `snitt: float | None`, `antall_vurderinger: int`. Alle id-er i lista finnes i svaret (nuller for dem uten data).

### A14 — Kategori lagres som kode eller tekst? (middels)

- **Par:** Oppdrag-storyen (FR-5) lagrer visningsteksten fra `core/domene.py` (for eksempel «Hage og utearbeid»). Filter-storyen (FR-11) bruker `?kategori=hage` (eksempelet i reconcile-ux L3). KI-storyen ber modellen svare med teksten og validerer mot lista. Profil-storyen grupperer «fullførte per kategori» på det som er lagret. En endring i teksten bryter da gamle rader.
- **Rettelse (i AD-10):**
  > `core/domene.KATEGORIER` er en ordnet liste av `(kode, tekst)`, der koden er ASCII. Databasen, URL-ene og skjemaverdiene bruker koden. Bare Jinja-filteret `kategori_tekst` viser teksten. KI-prompten lister kodene med tekst, og valideringen (FR-25) godtar bare kode.

### A15 — `/oppdrag/ny` mot `/oppdrag/{id}` gir 422 avhengig av rekkefølge (middels)

- **Par:** FR-9-storyen legger til `@router.get("/oppdrag/{id}")` med `id: int`. FR-5-storyen legger til `@router.get("/oppdrag/ny")` senere i samme fil. FastAPI matcher `{id}` først, validerer `"ny"` som heltall og kaster `RequestValidationError`, som Validering-konvensjonen gjør om til den vennlige feilsiden. «Legg ut oppdrag» virker ikke, og det kommer an på rekkefølgen i fila.
- **Rettelse:** Del av A4: alle stiparametre bruker Starlette-konvertering (`{oppdrag_id:int}`), slik at faste stier aldri kolliderer med parametre.

### A16 — E2E: én `TEST_NA` per prosess og delt seed-database (middels)

- **Par:** E2E-testen for «Er jobben gjort?» (FR-19) trenger en klokke etter tidspunktet. Testen for «Meld interesse» trenger en klokke før. Playwright kjører appen i én egen prosess, og `TEST_NA` leses fra miljøet ved oppstart. Testen for FR-15 velger hjelper på seed-oppdraget som testen for FR-12 forventer er åpent, så resultatet avhenger av rekkefølgen.
- **Rettelse (i Tester og AD-14):**
  > - Med `APP_ENV=test` registreres en rute `POST /_test/tilstand` som setter klokka og KI-utgaven og kjører seed på nytt. Ruta finnes ikke i andre miljøer, og en test sjekker at den gir 404 med `APP_ENV=production`.
  > - Hver e2e-test kaller den først. Seed har relative tidspunkt (NFR-2), så de fleste tester trenger bare standardklokka.

### A17 — Feilsider og menykroken krasjer når transaksjonen er ødelagt; fragmenter spiser kvitteringen (middels)

- **Par 1:** Den vennlige 500-siden (NFR-10) rendres med `core.render`, som kaller menykroken, som spør databasen. Var feilen en databasefeil på Postgres, er transaksjonen avbrutt, kroken feiler, og brukeren får rå 500.
- **Par 2:** KI-fragmentet (AD-15) rendres med `core.render`. Den leser og sletter kvitteringscookien og regner ut antallet i menyen. En kvittering som skulle vises på neste side, blir borte, og hvert KI-kall gjør en unødvendig spørring.
- **Par 3:** Kroken har ingen signatur. Én story gir den `(bruker_id)`, en annen kaller den med `(request)`.
- **Rettelse (i Rendring):**
  > - Kroken har signaturen `(db, bruker_id) -> int` og kalles bare når noen er innlogget.
  > - Feilhandlerne ruller tilbake, og rendrer feilsiden uten kroken og uten databasekall.
  > - Fragmenter rendres med `core.render_fragment(request, mal, **ctx)`, som ikke leser kvitteringen og ikke kaller kroken. For forespørsler med `X-Fragment: 1` svarer også CSRF-avvisning, 404 og 500 med det generelle feilfragmentet. `ki.js` setter bare inn svar med status 200 eller 401.

### A18 — Klokka kan importeres på to måter, og bare én kan byttes i tester (middels)

- **Par:** Én slice skriver `from app.core.klokke import na`, en annen `from app.core import klokke; klokke.na()`. Testfixturen bytter `app.core.klokke.na` med `monkeypatch`, og det virker bare for den andre. Tester for FR-8 og FR-19 blir ustabile.
- **Rettelse (i AD-3):** «Klokka brukes alltid som `klokke.na()` etter `from app.core import klokke`. Testene bytter den bare gjennom fixturen `sett_na(tidspunkt)` i `tests/conftest.py`.»

---

## Lave

### A19 — `OffentligBruker` mangler «om meg», og «egne opplysninger» har ingen type (lav)

- **Par:** Profil-storyen (FR-21) trenger «om meg», men `OffentligBruker` har bare id, visningsnavn, postnummer med poststed og slettet. Utvikleren utvider `OffentligBruker` (og alle andre steder får feltet), eller henter ORM-objektet (i strid med AD-16). «Rediger profil» (FR-22) trenger telefon, men AD-16 sier ikke hvilken type som gir det.
- **Rettelse (i AD-16):** «`identity/service.py` gir også `Profil` (OffentligBruker + `om_meg`) til FR-21 og `EgneOpplysninger` (i tillegg telefon) bare til «Rediger profil». Ingen andre typer med personfelt finnes.»

### A20 — Tilgang til `postnummer` og poststed er ikke ett funksjonskall (lav)

- **Par:** Identity (FR-1, OffentligBruker), oppdrag (FR-5, FR-11) og profil (FR-22) sjekker alle om et postnummer finnes og slår opp poststed. Hver lager sin egen spørring eller join, med ulik håndtering av mellomrom og ledende null («0150» mot 150).
- **Rettelse (i AD-1):** «`core/postnummer.py` har `normaliser_postnummer(tekst)`, `finnes(db, nr)` og `poststed(db, nr)`. Ingen slice spør `postnummer`-tabellen direkte. Postnummer lagres som tekst med fire sifre.»

---

## Sjekket uten funn

- AD-8 med gravstein og `NULL` i `bruker.epost`: Både SQLite og Postgres godtar flere `NULL` i en unik kolonne, så FR-4 («e-posten kan brukes på nytt») virker likt.
- AD-10 grenser i `core/domene.py` mot `data-maks`: Én kilde, ingen kollisjon funnet.
- AD-11 og AD-15 fragment med autoescape: Ingen vei til `innerHTML` på rå tekst, forutsatt A17 for feilsvar.
- AD-14 oppstartsvakt: Kolliderer ikke med A16 så lenge testruta bare registreres med `APP_ENV=test`.
