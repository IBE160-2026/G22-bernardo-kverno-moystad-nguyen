---
title: 'Story 2.6: Utfylt skjema går ikke tapt når innloggingen utløper'
type: 'feature'
created: '2026-11-27'
status: 'done'
baseline_commit: 'e25abaca3f91b1692aa87ec6b17f24eb5ca5ab0d'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-2-context.md'
  - '{project-root}/_bmad-output/planning-artifacts/ux-designs/ux-G22-bernardo-kverno-moystad-nguyen-2026-11-07/EXPERIENCE.md'
  - '{project-root}/_bmad-output/planning-artifacts/architecture/architecture-G22-bernardo-kverno-moystad-nguyen-2026-11-08/ARCHITECTURE-SPINE.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** En POST uten gyldig sesjon gir i dag den enkle 401-siden fra story 1.2 med lenken «Logg inn». Alt Kari har skrevet i «Nytt oppdrag» eller i redigeringen, går tapt, og et valgt bilde også (FR-2, FR-3, AD-7).

**Approach:** `SesjonMellomvare` svarer 401 med én generisk side, «Du må logge inn igjen.», som har alle innsendte tekstfelt som skjulte felt (unntatt `passord`, `csrf_token` og `_innlogging_*`), CSRF-nøkkelen, feltene `_innlogging_epost` og `_innlogging_passord` og knappen «Logg inn», som sender til samme adresse. Når skjemaet kommer tilbake, logger mellomvaren inn gjennom `Autentisering` med samme regler, tekster og sperre som `/logg-inn`. Så fjerner den `_innlogging_*` fra `request.state.skjema` og fra kroppen, legger den nye sesjonen i forespørselen og svaret og slipper forespørselen videre til ruta. Ruta behandler den som den nye innloggede brukeren. Filer kan ikke bli skjulte felt: hadde innsendingen et nytt bilde, står «Velg bildet på nytt etter innlogging.» over knappen, og `bilde_beholdt` følger med som vanlig tekstfelt (AD-18). Ingen migrering.

**Beslutninger (anbefalt alternativ, delegert av Heidi 2026-11-26):**
- Er det nye bildet tapt etter innlogging, lagres ingenting. Skjemaet vises igjen med 422, med alle verdiene og feilen «Velg bildet på nytt.» ved bildefeltet. Et gyldig `bilde_beholdt` vises fortsatt med «Fjern bildet». Mellomvaren gjør merket `_innlogging_fil` om til `request.state.tapte_filer`, og `tolk_bildevalg` gir feilen når `bilde` er tapt og ingen ny fil er valgt. Teksten føres i EXPERIENCE.md § Feiltekster ved felt.
- `/logg-ut` merkes `offentlig`. Uten gyldig sesjon sletter ruta cookien og sender til innloggingssiden med «Du er logget ut.», uten passord. CSRF gjelder fortsatt. Lista over offentlige ruter i AD-4 og testene som brukte `/logg-ut` til å utløse 401, endres, og avviket føres i memlog.
- Specen beholdes samlet (cirka 5 400 tokens), fordi storyen er ett mål.

## Boundaries & Constraints

**Always:** Tekstene er ordrett fra EXPERIENCE.md: «Du må logge inn igjen.», «Velg bildet på nytt etter innlogging.», «Feil e-post eller passord.», «For mange mislykkede forsøk. Prøv igjen om 15 minutter.», «Skriv e-postadressen din.», «Skriv passordet ditt.», «Skriv passordet på nytt.», etikettene «E-post» og «Passord» og knappen «Logg inn». Feltene har `type="email" autocomplete="email"` og `type="password" autocomplete="current-password"`, og «Vis passord» virker som på innloggingssiden. 401-siden leser ikke innhold fra databasen og har ikke meny (innloggingsforsøket bruker databasen, men siden viser ingenting derfra). Mellomvaren kaller bare `Autentisering` og leser aldri `sesjon`, `bruker` eller `innloggingsforsok` selv (AD-1, AD-4). Innloggingen i mellomvaren og på `/logg-inn` går gjennom én felles funksjon, så tekstene, sperren og oppryddingen er like (FR-2, T-6). bcrypt og databasekall kjøres i `run_in_threadpool`. CSRF sjekkes fortsatt før sesjonen (AD-5). CSRF-nøkkelen byttes ikke, og skjemaet bruker `request.state.csrf`. Fokus: `autofocus` på «E-post» ved første visning, og feiloppsummeringen ved feil (UX-DR27). Høyst ett `autofocus`. Passord, e-post og feltverdier logges aldri. Bare `_innlogging_`-feltene på 401-siden begynner med `_` (AD-7). Krav-ID-er står i commits og tester.

**Never:** Endring av data før innloggingen har lykkes. Filfelt eller `<input type="file">` på 401-siden. Å vise passordet igjen. Å dekode eller nevne `bilde_beholdt` i `core` (feltet er bare et tekstfelt der). Endring av 303 for GET, 401-fragmentet for `X-Fragment`, `trygg_neste`, sperregrensene eller CSRF-rekkefølgen. Rotasjon av CSRF-nøkkelen. Nye tabeller eller migreringer. Nye tekster utenom «Velg bildet på nytt.». Regler i JS, `innerHTML` og `|safe`. Profilskjemaene (Epic 4) og KI (Epic 5), men de skal virke med mekanismen uten endring.

## I/O & Edge-Case Matrix

Klokka står fast (`FAST_KLOKKE`). «Utløpt» betyr `sett_na` 7 dager fram, eller at sesjonsraden er slettet. Kari og Ola er fra seed.

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| 401-siden | Kari, utløpt, «Publiser» i «Nytt oppdrag» med gyldige felt | 401 med `h1` «Du må logge inn igjen.». Hvert tekstfelt (`skjema_id`, `tittel`, `beskrivelse`, `bildetekst`, `tilbud`, `belop` …) står som `<input type="hidden">` med samme navn og verdi. `csrf_token` står én gang, med nøkkelen fra cookien. «E-post» har `autofocus`, og «Passord» er tomt. `<form method="post" enctype="multipart/form-data">` har `action` lik stien og spørrestrengen. Ingen meny, ingen navn fra databasen, `no-store`. Antall oppdrag er uendret | – |
| Unntatte felt | innsendingen har `passord`, `csrf_token` og `_innlogging_epost` | ingen av dem står som skjult felt (e-posten står bare i det synlige feltet) | – |
| Riktig innlogging | 401-skjemaet med Karis e-post og passord | 303 til detaljene med «Oppdraget er lagt ut.». Oppdraget er lagret én gang med Kari som eier. Svaret har en ny cookie `sesjon` (HttpOnly, `SameSite=Lax`, 7 dager), den utløpte raden er slettet, og forsøkene for e-posten er slettet | – |
| Ruta ser ikke innloggingen | testrute som ikke er offentlig, med `Form()` og `await request.form()` | `request.state.skjema`, `request.form()` og `Form()` gir de opprinnelige feltene uten `_innlogging_*`. `request.cookies["sesjon"]` er den nye nøkkelen, og `request.state.innlogget` er Kari | – |
| Annen bruker | Ola logger inn på 401-siden til Karis `/oppdrag/{id}/rediger`, eller til «Nytt oppdrag» | redigeringen gir samme 404 som for Ola, og Karis oppdrag er uendret. «Nytt oppdrag» legges ut med Ola som eier. Ola er innlogget etterpå (AD-7) | `FinnesIkke` |
| Feil passord | riktig e-post og feil passord, eller ukjent e-post | 401 igjen med «Feil e-post eller passord.» i feiloppsummeringen og lenke til «E-post», og «Skriv passordet på nytt.» ved passordet. E-posten er beholdt og passordet tomt, de skjulte feltene står som før, og `<title>` får «Feil: » foran. Én ny rad i `innloggingsforsok` | `FEIL` |
| Tomme felt | e-post eller passord tomt eller bare mellomrom | 401 med «Skriv e-postadressen din.» / «Skriv passordet ditt.» ved feltene. Telles ikke | – |
| Sperre (FR-2) | 5 feil på 15 min for e-posten, på `/logg-inn` og 401-siden til sammen, og så riktig passord | 401 med «For mange mislykkede forsøk. Prøv igjen om 15 minutter.». De skjulte feltene er beholdt, og ingenting lagres | `SPERRET` |
| Nytt bilde | utløpt, multipart med gyldig fil `bilde` | 401 med «Velg bildet på nytt etter innlogging.» rett over «Logg inn», uten filfelt, og det skjulte merket `_innlogging_fil` = `bilde`. Teksten står også etter feil passord. Etter innlogging: 422 med «Velg bildet på nytt.» ved bildefeltet, og ingenting lagres | – |
| Beholdt bilde | utløpt, `bilde_beholdt` (base64 av en JPEG på cirka 1 MB) og bildetekst | `bilde_beholdt` står som skjult felt. Det nye skjemaet sendes som multipart og gir ikke 413. Etter innlogging lagres oppdraget med bildet | – |
| Gyldig sesjon og `_innlogging_*` | Kari har logget inn i en annen fane, så sendes 401-skjemaet | ingen innlogging og ingen passordsjekk. Feltene fjernes, og ruta kjører som brukeren i sesjonen | – |
| Offentlig rute | `_innlogging_epost` sendt til `/logg-inn` eller `/registrer` | feltene fjernes og ignoreres | – |
| XSS | `"><script>alert(1)</script>` i tittelen | står escapet i `value` på 401-siden (NFR-12) | – |
| Invariant 1.2 (T-6) | GET uten sesjon, POST med `X-Fragment`, POST `/logg-inn` | 303 til `/logg-inn?neste=…` med `trygg_neste`, 401-fragmentet og innloggingssiden er uendret, med samme tekster, sperre, opprydding og `neste`. Første 401-side rendres uten databasekall. FR-3-testen gir 401 for alle POST-ruter som ikke er offentlige | – |
| Invariant 2.1 (T-6) | 401-skjemaet sendt to ganger, eller originalen sendt på nytt etter innlogging | `skjema_id` følger med, så den andre gir `Duplikat` til oppdraget som finnes. Det finnes ett oppdrag | `Duplikat` |
| Invariant 2.5 (T-6) | oppdraget avbrytes i en annen fane mellom 401 og innlogging, og «Ja, avbryt oppdraget» med `fra=mine` via 401 | `Konflikt`: 303 til detaljene med «Oppdraget er endret. Last siden på nytt.», og den nye sesjonscookien er satt. Avbrudd via 401 gir «Oppdraget er avbrutt.» i «Mine oppdrag» | `Konflikt` |
| Invariant 2.7 (T-6) | multipart med fil uten CSRF, GET `/oppdrag/{id}/bilde` uten sesjon | fortsatt 403 (CSRF før sesjon) og 303 | 403 |
| Invariant T1 (T-6) | alle sider i `SIDER` | fortsatt uten «serious» eller «critical» og uten vannrett rulling ved 320 px | – |

</frozen-after-approval>

## Code Map

- `app/core/mellomvare.py` -- `SesjonMellomvare.__call__` (l. 46–63) og `_avvis` (l. 81–102) rendrer 401 med `innlogging_url` og lenke. `lag_mellomvare` (l. 105–116) gir bare `autentisering`, ikke `secure`.
- `app/core/csrf.py` -- `scope["state"]["skjema"]` og `["filer"]` (l. 132–133). `skjema` er `dict[str, str]` med siste verdi per navn. Ingen skjema har flere verdier per navn. `_avspilling(kropp, receive)` (l. 222–235) gir sesjonsmellomvaren kroppen. `MAKS_KROPP` = 1 MB for urlencoded (l. 44) og `MAKS_MULTIPART` (l. 47).
- `app/core/sesjon.py` -- `Autentisering` (l. 62–83), `Innloggingsresultat` (l. 52–59) og `sett_sesjonscookie` (l. 157–167). `trygg_neste` brukes uendret.
- `app/identity/service.py` -- `FEIL_INNLOGGING` og `FOR_MANGE_FORSOK` (l. 54–55), `sjekk_innloggingsskjema` (l. 130–141), `logg_inn` (l. 192–232, sperre og opprydding) og `IdentityAutentisering` (l. 397–438). `finn_innlogget` åpner sin egen sesjon fra `app.state.sesjonsfabrikk`, som testene bytter.
- `app/identity/routes.py` -- `logg_inn` (l. 91–126) gjør sjekk, `with db.begin()` og meldingsvalg, som skal deles. `logg_ut` (l. 196–204) leser `request.cookies[SESJON_COOKIE]`.
- `app/core/templates/core/logg_inn_igjen.html` -- den enkle siden. `identity/templates/identity/logg_inn.html` (l. 9–35) er mønsteret for feltene, hjelpeteksten og «Vis passord». `core/makroer.html` -- `csrf_felt` (l. 4) og `meldinger(lenker)` (l. 24–55).
- `app/core/render.py` -- `render(..., med_menytall=False)` (l. 192–245) og `fokusmal` (l. 148–158).
- `app/oppdrag/routes.py` -- `_bildevalg` (l. 403–407), `send_ny` (l. 423–465), `send_rediger` (l. 628–656) og `send_avbryt` (l. 700–722). Alle leser `request.state.skjema` og `filer`, ikke kroppen. `app/oppdrag/service.py` -- `tolk_bildevalg` (l. 212). Det finnes ingen POST-ruter i `profil` ennå.
- `tests/core/test_tilgang.py` -- 401-testene (l. 108–170) sjekker `">Logg inn</a>"` og bruker `/logg-ut`. `tests/core/test_mellomvare.py` -- `testruter` (l. 49–98, alle `offentlig`) og `Form()` etter avspilling (l. 221). `tests/oppdrag/test_to_steg.py:135` -- den eneste `_`-testen, og den gjelder bare `/oppdrag/ny`. `tests/e2e/test_t1.py` -- `logg_inn_igjen_401` (l. 152) og `SIDER` (l. 382).

## Tasks & Acceptance

**Execution:**
- [x] `app/core/sesjon.py` -- `FEIL_INNLOGGING` og `FOR_MANGE_FORSOK` flyttes hit, og `identity` importerer dem. `Autentisering` får `sjekk_innloggingsskjema(epost, passord) -> list[(felt, melding)]`. Ny `prov_innlogging(autentisering, db, epost, passord, *, gammel_nokkel) -> (nokkel | None, feil)` gjør sjekken, kaller `logg_inn` i `with db.begin():` og velger meldingen. `INNLOGGING_PREFIKS = "_innlogging_"` og en hjelper som gir `Set-Cookie` med attributtene fra `sett_sesjonscookie` -- FR-2, AD-4, T-6
- [x] `app/identity/service.py`, `app/identity/routes.py` -- `IdentityAutentisering.sjekk_innloggingsskjema` delegerer. `/logg-inn` bruker `prov_innlogging`, med samme svar som før. `logg_ut` merkes `@offentlig` -- FR-2, AD-4
- [x] `app/core/mellomvare.py` -- Se Design Notes. `lag_mellomvare` gir `secure_cookie=settings.produksjon`. Docstringen beskriver AD-7 -- FR-3, AD-4, AD-5, AD-7
- [x] `app/core/templates/core/logg_inn_igjen.html` -- Skjemaet etter matrisen: `skjemabredde`, `h1`, `meldinger(lenker={"epost": "innlogging-epost", "passord": "innlogging-passord"})`, `csrf_felt()`, skjulte felt i innsendt rekkefølge, merket `_innlogging_fil`, feltene med id `innlogging-epost` og `innlogging-passord`, «Velg bildet på nytt etter innlogging.» som `<p>` rett over knappen, og «Logg inn» -- AD-7, UX-DR12, UX-DR27
- [x] `app/oppdrag/service.py`, `app/oppdrag/routes.py`, `EXPERIENCE.md` -- `tolk_bildevalg(..., tapt=False)` og `_bildevalg` leser `request.state.tapte_filer`. Den nye teksten føres i § Feiltekster ved felt -- FR-27, NFR-10
- [x] `ARCHITECTURE-SPINE.md`, `.memlog.md` -- AD-17: innloggingen i mellomvaren er et unntak med egen transaksjon, committet før ruta. AD-7: skjemaet er multipart, og merket `_innlogging_fil` finnes. AD-4: `/logg-ut` er offentlig. Én memlog-linje per endring
- [x] `tests/core/test_utlopt_innlogging.py` (ny) -- én test per rad i matrisen, med testruter som ikke er offentlige (`innlogget_bruker`, `Form()`, `request.form()`, `request.cookies`). -- FR-2, FR-3, NFR-5, NFR-12, AD-7
- [x] `tests/core/test_tilgang.py`, `tests/core/test_mellomvare.py`, `tests/identity/` -- 401-testene forventer skjemaet i stedet for lenken. Innloggingstestene er grønne uendret -- FR-3, T-6
- [x] `tests/core/test_arkitektur.py` -- ingen `name="_` i maler, ingen `"_`-nøkler i `FormData`/`append` i `core/static/js/` og ingen `skjema.get("_` i `app/`, unntatt 401-malen og `core/mellomvare.py` (AC 4). `test_to_steg.py:135` beholdes -- AD-7
- [x] `tests/e2e/test_t1.py`, `tests/e2e/test_klientatferd.py` -- nye sider i `SIDER`: `401-nytt-oppdrag` («Publiser» etter at `sesjon`-cookien er fjernet), `401-feil-passord` og `401-nytt-bilde`. «401» får en ny utløser, fordi `/logg-ut` er offentlig. Klienttest: Kari fyller ut «Nytt oppdrag», cookien fjernes, «Publiser», hun logger inn på 401-siden, og detaljene viser oppdraget med kvitteringen -- SM-5, NFR-6, NFR-7

**Acceptance Criteria:**
- Gitt Kari på mobil (360 px) med JS, når sesjonen utløper mens hun skriver og hun trykker «Publiser» og logger inn på 401-siden, så havner hun i detaljene med «Oppdraget er lagt ut.» og alt hun skrev.
- Gitt samme flyt uten JS, så er resultatet det samme.
- Gitt kodebasen, når `uv run pytest` kjøres, så feiler `test_arkitektur.py` hvis et annet skjema får et feltnavn som begynner med `_`.

## Implementation Notes

- `prov_innlogging` gir `Innloggingsprov(nokkel, feil)`, en `NamedTuple` som pakkes ut som `(nokkel, feil)`. Egenskapen `feltfeil` skiller feltfeil (tomme felt) fra «Feil e-post eller passord.» og sperren, som bare står i oppsummeringen. Slik får `/logg-inn` samme svar som før uten egen meldingslogikk.
- Mellomvaren gir aldri skjulte felt som begynner med `_` (ikke bare `_innlogging_*`), så «Bare `_innlogging_`-feltene på 401-siden begynner med `_`» gjelder også når noen sender et annet `_`-felt.
- Kroppen bygges på nytt hver gang `_innlogging_*`-felt finnes (også ved gyldig sesjon og på offentlige ruter), så passordet aldri kan leses av ruta. Den gamle kroppen leses fra avspillingen først. `request.state.filer` er uendret.
- Innlogging på 401-siden prøves ikke for `X-Fragment`-forespørsler, så 401-fragmentet er uendret.
- `action` på 401-siden har alltid én `/` foran, så den aldri kan peke til en annen vert.
- «401» i T1 utløses nå av «Ja, avbryt oppdraget» på bekreftelsessiden etter at sesjonscookien er fjernet.

## Spec Change Log

## Review Triage Log

Pass 1 (2026-11-28). Lag: Blind Hunter (BH), Edge Case Hunter (EC), Verification Gap (VG).

| # | Lag | Funn | Verdict | Begrunnelse | Rute |
|---|---|---|---|---|---|
| 1 | VG, BH | `Secure` på sesjonscookien etter innlogging på 401-siden er ikke testet i produksjon | medium | Forhåndsverifisert av VG. Å fjerne `secure_cookie=settings.produksjon` ville ikke blitt fanget | patch |
| 2 | EC | En feil i `_prov_innlogging` (databasefeil eller lås) gir 500, og det utfylte innholdet går tapt | medium | Nettopp det AD-7 skal hindre | patch |
| 3 | BH, EC | `prov.nokkel` satt, men `finn_innlogget` gir `None`: 401-siden kommer igjen uten feilmelding | low | Kappløp eller slettet bruker. Retten er logg og feiltekst | patch |
| 4 | BH, EC | `action` bygges fra den dekodede stien uten ny koding (`/\host`) | low | Trygt i dag fordi alle beskyttede ruter har `:int`. Direkte retting med `quote` | patch |
| 5 | BH | Ingen test sikrer at passord og e-post aldri logges | low | Sikkerhetsregel i Always uten test. Liten `caplog`-test | patch |
| 6 | BH | Redigering av eget oppdrag via 401-siden og tapt bilde ved redigering er ikke testet | medium | Problem-teksten nevner redigering, men bare 404 for Ola er testet | patch |
| 7 | BH | E2E-testen av AC 1 sjekker ikke kategori, postnummer og tidspunkt | low | Det er feltene som mest sannsynlig forsvinner hvis skjulte felt mistes | patch |
| 8 | BH | AD-7 «Svaret» sier fortsatt «unntatt passord, CSRF og filfelt» | low | Koden utelater alle felt med `_`. Planleggingsdokumentene skal stemme | patch |
| 9 | BH | EXPERIENCE «Innlogging utløpt» har gamle merker og gammel oppførsel | low | Planleggingsdokumentene skal stemme | patch |
| 10 | BH | En ekstra tom linje på slutten av `mellomvare.py` | low | Direkte retting | patch |
| 11 | BH, EC | Den gjenoppbygde kroppen og 401-siden beholder bare siste verdi per navn og ingen filer | medium | Gjelder ingen skjema i dag (ingen gjentatte navn, 401-siden har aldri filer). Gjelder Epic 4 og 5 | defer |
| 12 | BH | `/logg-inn` sletter ikke en utløpt sesjonsrad, mens mellomvaren gjør det | low | Fantes før 2.6. Utløpte rader er ufarlige | reject |
| 13 | BH | `Innloggingsprov.feltfeil` sorterer etter meldingstekst | low | Tekstene er konstanter i samme modul. Retten er omstrukturering | reject |
| 14 | BH | Rekkefølgen på `Set-Cookie` (ruta vinner) er ikke testet | low | Ingen rute setter sesjonscookien etter 401 i dag. Testes når FR-4 kommer | reject |
| 15 | BH, EC | Arkitekturtesten for `_`-navn fanger ikke alle skrivemåter | low | Testen er en vakt for de vanlige mønstrene. Retten er en parser | reject |
| 16 | BH | Re-eksporten av tekstene i `identity/service.py` for røyktesten | low | Kosmetisk | reject |
| 17 | EC | En kvittering i køen brukes opp på 401-siden og flytter fokus | low | Krever at sesjonen utløper mellom en handling og neste side. Sjeldent | reject |
| 18 | EC | GET `/logg-ut` uten sesjon gir 405 i stedet for 303 | low | Ingen lenke bruker GET mot `/logg-ut`. Bare en skrevet URL | reject |

## Design Notes

- **Flyten i `SesjonMellomvare`** (bare for `http` og ikke `/static/`):

  ```python
  skjema = scope["state"].get("skjema") or {}
  innlogging = {k: skjema.pop(k) for k in list(skjema) if k.startswith(INNLOGGING_PREFIKS)}
  innlogget = finn_innlogget(...)
  if innlogget is None and krever_innlogging and "_innlogging_epost" in innlogging:
      nokkel, feil = await run_in_threadpool(_prov, scope, innlogging)   # egen sesjon + db.begin()
      if nokkel:
          scope = _med_ny_sesjon(scope, nokkel, skjema)  # cookie-header, ny kropp, content-type/-length
          innlogget = finn_innlogget(Request(scope)); send = _med_set_cookie_forst(send, nokkel)
  if innlogget is None and krever_innlogging: return 401  # med `feil` og `innlogging["_innlogging_epost"]`
  ```
- **Ny kropp, ikke bare ny `state`.** Ingen rute i appen leser kroppen, men AD-5 lover at kroppen spilles av, og `test_fastapi_form_parameter_virker_etter_avspilling` sikrer det. Kroppen bygges derfor på nytt som `application/x-www-form-urlencoded` fra det rensede `skjema` (`urlencode`). `content-type` og `content-length` byttes i en kopi av `scope["headers"]`, og `receive` blir `_avspilling(ny_kropp, receive)`. Da finnes passordet ikke i noe ruta kan lese.
- **Cookien i forespørselen og svaret.** `cookie`-headeren i scopet får den nye nøkkelen, så `finn_innlogget` og `request.cookies` (for eksempel i `logg_ut`) ser den samme sesjonen. `Set-Cookie: sesjon=…` legges *foran* rutas egne headere i `http.response.start`. Da vinner en rute som selv setter eller sletter `sesjon`, fordi den siste headeren gjelder.
- **To transaksjoner.** Innloggingen committes i mellomvarens egen sesjon (`with app.state.sesjonsfabrikk() as db, db.begin():`) og lukkes før ruta åpner sin (SQLite-låsen fra `BEGIN IMMEDIATE`). Feiler ruta etterpå med 422, `Konflikt` eller 404, er Kari fortsatt innlogget, og det er riktig. Ved en uventet 500 før svaret starter mistes cookien, men raden står. Kari må da logge inn på nytt (godtatt). Unntaket føres i AD-17.
- **Multipart på 401-siden.** `bilde_beholdt` kan være over 1 MB som base64, og urlencoded avvises over 1 MB (413), med prosentkoding i tillegg. Skjemaet sendes derfor alltid som `multipart/form-data`. Den opprinnelige innsendingen gikk gjennom grensen, og den nye har de samme tekstfeltene uten fila.
- **Merket `_innlogging_fil`.** Den andre 401-siden (etter feil passord) har ingen fil i `request.state.filer`. Uten merket ville «Velg bildet på nytt etter innlogging.» forsvinne. Merket er et `_innlogging_`-felt og fjernes som de andre.
- **CSRF-nøkkelen** er `request.state.csrf`. CSRF-laget har allerede godtatt nøkkelen, og AD-5 sier at den bare byttes når den mangler. «Ny» betyr at siden skriver nøkkelen selv, ikke den innsendte verdien.
- **Kjent begrensning.** CSRF-cookien har ingen `Max-Age`. Har nettleseren vært lukket, gir innsendingen 403 fra CSRF-laget før AD-7 slår inn. Det er utenfor storyen (AD-5).

## Verification

**Commands:**
- `uv run pytest` -- forventet: alle tester er grønne, også `test_utlopt_innlogging.py`, de endrede 401-testene, `test_arkitektur.py` (`_`-feltnavn) og innloggingstestene fra 1.2 og T-1 uten endring. Postgres-varianten kjøres av `test-postgres` i CI.
- `uv run pytest -m e2e` -- forventet: T1 er grønn for alle sider i `SIDER` ved 360 og 1280 px, også de tre nye 401-sidene, og uten vannrett rulling ved 320 px. Klienttesten for hele flyten er grønn, og klienttestene fra 1.5 og 2.2–2.7 er det også.

**Manual checks (if no CLI):**
- [ ] Tastatursjekk av 401-siden (fokus på «E-post», «Vis passord», feiloppsummeringen og «Logg inn») i cirka fem minutter (DoD, T2). **Utsatt til story 6.1** (retro T-5): den autonome kjøringen har ingen manuell tester, og T1 og klienttesten dekker de automatiske kravene. Storyen kan settes `done` med denne utsettelsen.
- [ ] Etter publisering: slett `sesjon`-cookien i DevTools mens «Nytt oppdrag» er utfylt, trykk «Publiser» og logg inn på 401-siden i produksjon.
