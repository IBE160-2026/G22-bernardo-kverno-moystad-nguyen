"""Røyktest mot en publisert versjon av Nabolagshelten (AR-1, AD-5, AD-13, AD-14).

Bruk:  uv run python scripts/roykttest.py [url]
Standard-url er produksjonsadressen. `deploy.yml` kjører testen etter hver publisering.

Sjekkene (radene i I/O-matrisen i spec-1-3):
- GET `/logg-inn` gir 200 og sikkerhetsheaderne. At siden svarer, viser også at
  appen startet, altså at `data/postnumre.tsv` fulgte med i funksjonen.
- CSRF-cookien har `Secure`. Den settes bare når `APP_ENV=production`; uten den
  kjører appen som `local` med den kjente standardnøkkelen.
- POST `/logg-inn` med CSRF-nøkkel, `Origin` og Karis seed-passord gir 422 med
  «Feil e-post eller passord.» (eller sperremeldingen). Det viser at CSRF- og
  Origin-sjekken slipper gjennom bak Vercels proxy, at kroppen spilles av for
  ruta, at Supabase svarer, og at det ikke finnes demokontoer i produksjon.
- GET `/registrer` gir 200, sikkerhetsheaderne og knappen «Opprett konto»
  (spec-1-4). Røyktesten registrerer aldri kontoer; testkontoen i produksjon
  lages for hånd.
- GET `/_test/tilstand` gir 404 (testruta finnes bare i `test`).
- GET `/static/css/app.css` gir 200.

Avslutter med kode 0 og «Røyktest OK», ellers kode 1 og én kort linje per avvik.
Skriver aldri ut cookies eller CSRF-nøkler. Tekstene og headerne hentes fra
appen selv, så de ikke kan skli fra hverandre. `tests/test_roykttest.py` kjører
`kjor()` mot testappen i CI.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

import httpx

# Så `uv run python scripts/roykttest.py` fra rotmappa finner pakken `app`.
ROT = Path(__file__).resolve().parents[1]
if str(ROT) not in sys.path:
    sys.path.insert(0, str(ROT))

from app.core.csrf import CSRF_COOKIE  # noqa: E402
from app.core.headere import SIKKERHETSHEADERE  # noqa: E402
from app.identity.service import FEIL_INNLOGGING, FOR_MANGE_FORSOK  # noqa: E402

STANDARD_URL = "https://nabolagshelten.vercel.app"

FORVENTEDE_HEADERE = {navn.decode(): verdi.decode() for navn, verdi in SIKKERHETSHEADERE}

# Seed-brukeren fra README (bare for lokal testing). Finnes aldri i produksjon.
SEED_EPOST = "kari@eksempel.no"
SEED_PASSORD = "kari-lokal-1"

OPPRETT_KONTO = "Opprett konto"

CSRF_FELT = re.compile(r'name="csrf_token" value="([^"]+)"')


def sjekk_headere(svar: httpx.Response, sti: str) -> list[str]:
    avvik = []
    for navn, forventet in FORVENTEDE_HEADERE.items():
        faktisk = svar.headers.get(navn)
        if faktisk != forventet:
            avvik.append(f"GET {sti}: headeren {navn} er {faktisk!r}, forventet {forventet!r}")
    return avvik


def sjekk_secure_cookie(svar: httpx.Response) -> list[str]:
    """CSRF-cookien skal ha `Secure`, som bare settes i produksjon."""
    for cookie in svar.headers.get_list("set-cookie"):
        if cookie.startswith(f"{CSRF_COOKIE}="):
            attributter = {a.strip().lower() for a in cookie.split(";")[1:]}
            if "secure" in attributter:
                return []
            return [
                f"GET /logg-inn: cookien {CSRF_COOKIE} mangler Secure. "
                "APP_ENV er trolig ikke production"
            ]
    return [f"GET /logg-inn: fikk ingen {CSRF_COOKIE}-cookie"]


def kjor(url: str, klient: httpx.Client | None = None) -> list[str]:
    """Kjører sjekkene og gir avvikene. `klient` kan være en `TestClient` i testene."""
    url = url.rstrip("/")
    if klient is None:
        with httpx.Client(base_url=url, timeout=30) as egen_klient:
            return _sjekk(url, egen_klient)
    return _sjekk(url, klient)


def _sjekk(url: str, klient: httpx.Client) -> list[str]:
    deler = urlsplit(url)
    opphav = f"{deler.scheme}://{deler.netloc}"
    avvik: list[str] = []

    # 1. Innloggingssiden, sikkerhetsheaderne og Secure på CSRF-cookien
    svar = klient.get("/logg-inn", follow_redirects=False)
    innloggingsside = svar
    if svar.status_code != 200:
        return [f"GET /logg-inn: status {svar.status_code}, forventet 200 (startet appen?)"]
    avvik += sjekk_headere(svar, "/logg-inn")
    avvik += sjekk_secure_cookie(svar)

    # 2. Registreringssiden svarer (FR-1). Ingen konto opprettes. Sjekkes før
    #    innloggingen, så en eventuell demokonto ikke gir 303 her.
    svar = klient.get("/registrer", follow_redirects=False)
    if svar.status_code != 200:
        avvik.append(f"GET /registrer: status {svar.status_code}, forventet 200")
    else:
        avvik += sjekk_headere(svar, "/registrer")
        if OPPRETT_KONTO not in svar.text:
            avvik.append(f"GET /registrer: fant ikke «{OPPRETT_KONTO}»")

    # 3. Innlogging med seed-passordet: skal avvises med 422
    treff = CSRF_FELT.search(innloggingsside.text)
    if treff is None:
        avvik.append("GET /logg-inn: fant ikke det skjulte feltet csrf_token")
    else:
        svar = klient.post(
            "/logg-inn",
            data={
                "csrf_token": treff.group(1),
                "neste": "/",
                "epost": SEED_EPOST,
                "passord": SEED_PASSORD,
            },
            headers={"Origin": opphav},
            follow_redirects=False,
        )
        if svar.status_code == 403:
            avvik.append(
                "POST /logg-inn: 403. CSRF- eller Origin-sjekken avviser skjemaet bak proxyen "
                "(se app/core/csrf.py:_samme_opphav)"
            )
        elif svar.status_code in (302, 303):
            avvik.append("POST /logg-inn: innloggingen lyktes. Det finnes en demokonto i produksjon")
        elif svar.status_code != 422:
            avvik.append(f"POST /logg-inn: status {svar.status_code}, forventet 422")
        elif FEIL_INNLOGGING not in svar.text and FOR_MANGE_FORSOK not in svar.text:
            avvik.append(f"POST /logg-inn: 422, men uten «{FEIL_INNLOGGING}» eller sperremeldingen")

    # 4. Testruta finnes ikke utenfor test
    svar = klient.get("/_test/tilstand", follow_redirects=False)
    if svar.status_code != 404:
        avvik.append(f"GET /_test/tilstand: status {svar.status_code}, forventet 404")

    # 5. Statiske filer
    svar = klient.get("/static/css/app.css", follow_redirects=False)
    if svar.status_code != 200:
        avvik.append(f"GET /static/css/app.css: status {svar.status_code}, forventet 200")

    return avvik


def main(argv: list[str]) -> int:
    url = argv[1] if len(argv) > 1 else STANDARD_URL
    try:
        avvik = kjor(url)
    except httpx.HTTPError as feil:
        avvik = [f"Fikk ikke kontakt med {url}: {type(feil).__name__}"]
    if avvik:
        for linje in avvik:
            print(f"AVVIK: {linje}")
        print(f"Røyktest feilet mot {url} ({len(avvik)} avvik)")
        return 1
    print(f"Røyktest OK mot {url}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
