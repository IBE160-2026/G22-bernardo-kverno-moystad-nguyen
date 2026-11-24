"""Røyktest mot en publisert versjon av Nabolagshelten (AR-1, AD-5, AD-13, AD-14).

Bruk:  uv run python scripts/roykttest.py [url]
Standard-url er produksjonsadressen. `deploy.yml` kjører testen etter hver publisering.

Sjekkene (radene i I/O-matrisen i spec-1-3):
- GET `/logg-inn` gir 200 og sikkerhetsheaderne. At siden svarer, viser også at
  appen startet, altså at `data/postnumre.tsv` fulgte med i funksjonen.
- POST `/logg-inn` med CSRF-nøkkel, `Origin` og Karis seed-passord gir 422 med
  «Feil e-post eller passord.» (eller sperremeldingen). Det viser at CSRF- og
  Origin-sjekken slipper gjennom bak Vercels proxy, at kroppen spilles av for
  ruta, at Supabase svarer, og at det ikke finnes demokontoer i produksjon.
- GET `/_test/tilstand` gir 404 (testruta finnes bare i `test`).
- GET `/static/css/app.css` gir 200.

Avslutter med kode 0 og «Røyktest OK», ellers kode 1 og én kort linje per avvik.
Skriver aldri ut cookies eller CSRF-nøkler.
"""

from __future__ import annotations

import re
import sys
from urllib.parse import urlsplit

import httpx

STANDARD_URL = "https://nabolagshelten.vercel.app"

FORVENTEDE_HEADERE = {
    "content-security-policy": "frame-ancestors 'none'",
    "x-frame-options": "DENY",
    "x-content-type-options": "nosniff",
    "referrer-policy": "same-origin",
}

# Seed-brukeren fra README (bare for lokal testing). Finnes aldri i produksjon.
SEED_EPOST = "kari@eksempel.no"
SEED_PASSORD = "kari-lokal-1"
FEIL_INNLOGGING = "Feil e-post eller passord."
FOR_MANGE_FORSOK = "For mange mislykkede forsøk. Prøv igjen om 15 minutter."

CSRF_FELT = re.compile(r'name="csrf_token" value="([^"]+)"')


def sjekk_headere(svar: httpx.Response, sti: str) -> list[str]:
    avvik = []
    for navn, forventet in FORVENTEDE_HEADERE.items():
        faktisk = svar.headers.get(navn)
        if faktisk != forventet:
            avvik.append(f"GET {sti}: headeren {navn} er {faktisk!r}, forventet {forventet!r}")
    return avvik


def kjor(url: str) -> list[str]:
    url = url.rstrip("/")
    deler = urlsplit(url)
    opphav = f"{deler.scheme}://{deler.netloc}"
    avvik: list[str] = []

    with httpx.Client(base_url=url, follow_redirects=False, timeout=30) as klient:
        # 1. Innloggingssiden og sikkerhetsheaderne
        svar = klient.get("/logg-inn")
        if svar.status_code != 200:
            return [f"GET /logg-inn: status {svar.status_code}, forventet 200 (startet appen?)"]
        avvik += sjekk_headere(svar, "/logg-inn")

        # 2. Innlogging med seed-passordet: skal avvises med 422
        treff = CSRF_FELT.search(svar.text)
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
                avvik.append("POST /logg-inn: 422, men uten «Feil e-post eller passord.» eller sperremeldingen")

        # 3. Testruta finnes ikke utenfor test
        svar = klient.get("/_test/tilstand")
        if svar.status_code != 404:
            avvik.append(f"GET /_test/tilstand: status {svar.status_code}, forventet 404")

        # 4. Statiske filer
        svar = klient.get("/static/css/app.css")
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
