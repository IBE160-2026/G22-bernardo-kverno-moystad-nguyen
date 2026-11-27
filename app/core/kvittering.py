"""Kvittering og feilmelding etter POST → redirect → GET (AR-27, UX-DR22, AD-2).

Kvitteringen ligger i cookien `kvittering`, signert med `itsdangerous` (egen salt)
og gyldig i 60 sekunder. Cookien har bare en nøkkel, for eksempel `"logget_ut"`,
som slås opp i `TEKSTER`. Ukjente nøkler ignoreres, så cookien aldri kan få
appen til å vise annen tekst. `render` leser den og sletter cookien i samme svar.

Feilmeldingen etter en `Konflikt` (story 2.5, §4.0) går på samme måte gjennom
cookien `feilmelding`, med egen salt og nøklene i `FEILMELDINGER`. Den vises som
`melding--feil` med «Last siden på nytt», og slettes også i svaret som viser den.
"""

from __future__ import annotations

from itsdangerous import BadSignature, URLSafeTimedSerializer
from starlette.requests import Request
from starlette.responses import Response

KVITTERING_COOKIE = "kvittering"
FEILMELDING_COOKIE = "feilmelding"
MAKS_ALDER = 60  # sekunder

TEKSTER: dict[str, str] = {
    "logget_ut": "Du er logget ut.",
    "oppdrag_lagt_ut": "Oppdraget er lagt ut.",
    "endringer_lagret": "Endringene er lagret.",
    "oppdrag_avbrutt": "Oppdraget er avbrutt.",
}

# Ordrett fra EXPERIENCE.md § Ordrette tekster fra PRD (Samtidighet, §4.0).
FEILMELDINGER: dict[str, str] = {
    "konflikt": "Oppdraget er endret. Last siden på nytt.",
}


def _signerer(secret_key: str, salt: str) -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(secret_key, salt=salt)


def _secret_key(request: Request) -> str:
    return request.app.state.settings.secret_key


def _secure(request: Request) -> bool:
    return request.app.state.settings.produksjon


def _sett(request: Request, svar: Response, cookie: str, nokkel: str) -> None:
    svar.set_cookie(
        cookie,
        _signerer(_secret_key(request), cookie).dumps(nokkel),
        max_age=MAKS_ALDER,
        path="/",
        httponly=True,
        samesite="lax",
        secure=_secure(request),
    )


def _les(request: Request, cookie: str, tekster: dict[str, str]) -> str | None:
    signert = request.cookies.get(cookie)
    if not signert:
        return None
    try:
        nokkel = _signerer(_secret_key(request), cookie).loads(signert, max_age=MAKS_ALDER)
    except BadSignature:  # også utløpt (SignatureExpired)
        return None
    return tekster.get(nokkel) if isinstance(nokkel, str) else None


def _slett(request: Request, svar: Response, cookie: str) -> None:
    svar.delete_cookie(cookie, path="/", httponly=True, samesite="lax", secure=_secure(request))


def sett_kvittering(request: Request, svar: Response, nokkel: str) -> None:
    """Legger kvitteringen i cookien. Nøkkelen må finnes i `TEKSTER`."""
    if nokkel not in TEKSTER:
        raise ValueError(f"Ukjent kvittering: {nokkel!r}")
    _sett(request, svar, KVITTERING_COOKIE, nokkel)


def les_kvittering(request: Request) -> str | None:
    """Teksten for kvitteringen i forespørselen, eller `None`."""
    return _les(request, KVITTERING_COOKIE, TEKSTER)


def har_kvitteringscookie(request: Request) -> bool:
    return KVITTERING_COOKIE in request.cookies


def slett_kvittering(request: Request, svar: Response) -> None:
    _slett(request, svar, KVITTERING_COOKIE)


def nokkel_for_feilmelding(melding: str) -> str:
    """Nøkkelen til en fast feilmelding. En tekst som ikke står i `FEILMELDINGER`, gir `ValueError`."""
    for nokkel, tekst in FEILMELDINGER.items():
        if tekst == melding:
            return nokkel
    raise ValueError(f"Ukjent feilmelding: {melding!r}")


def sett_feilmelding(request: Request, svar: Response, nokkel: str) -> None:
    """Legger feilmeldingen i cookien. Nøkkelen må finnes i `FEILMELDINGER`."""
    if nokkel not in FEILMELDINGER:
        raise ValueError(f"Ukjent feilmelding: {nokkel!r}")
    _sett(request, svar, FEILMELDING_COOKIE, nokkel)


def les_feilmelding(request: Request) -> str | None:
    """Teksten for feilmeldingen i forespørselen, eller `None`."""
    return _les(request, FEILMELDING_COOKIE, FEILMELDINGER)


def har_feilmeldingscookie(request: Request) -> bool:
    return FEILMELDING_COOKIE in request.cookies


def slett_feilmelding(request: Request, svar: Response) -> None:
    _slett(request, svar, FEILMELDING_COOKIE)
