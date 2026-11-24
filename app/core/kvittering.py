"""Kvittering etter POST → redirect → GET (AR-27, UX-DR22).

Kvitteringen ligger i cookien `kvittering`, signert med `itsdangerous` (egen salt)
og gyldig i 60 sekunder. Cookien har bare en nøkkel, for eksempel `"logget_ut"`,
som slås opp i `TEKSTER`. Ukjente nøkler ignoreres, så cookien aldri kan få
appen til å vise annen tekst. `render` leser den og sletter cookien i samme svar.
"""

from __future__ import annotations

from itsdangerous import BadSignature, URLSafeTimedSerializer
from starlette.requests import Request
from starlette.responses import Response

KVITTERING_COOKIE = "kvittering"
MAKS_ALDER = 60  # sekunder
_SALT = "kvittering"

TEKSTER: dict[str, str] = {
    "logget_ut": "Du er logget ut.",
}


def _signerer(secret_key: str) -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(secret_key, salt=_SALT)


def _secret_key(request: Request) -> str:
    return request.app.state.settings.secret_key


def _secure(request: Request) -> bool:
    return request.app.state.settings.produksjon


def sett_kvittering(request: Request, svar: Response, nokkel: str) -> None:
    """Legger kvitteringen i cookien. Nøkkelen må finnes i `TEKSTER`."""
    if nokkel not in TEKSTER:
        raise ValueError(f"Ukjent kvittering: {nokkel!r}")
    svar.set_cookie(
        KVITTERING_COOKIE,
        _signerer(_secret_key(request)).dumps(nokkel),
        max_age=MAKS_ALDER,
        path="/",
        httponly=True,
        samesite="lax",
        secure=_secure(request),
    )


def les_kvittering(request: Request) -> str | None:
    """Teksten for kvitteringen i forespørselen, eller `None`."""
    signert = request.cookies.get(KVITTERING_COOKIE)
    if not signert:
        return None
    try:
        nokkel = _signerer(_secret_key(request)).loads(signert, max_age=MAKS_ALDER)
    except BadSignature:  # også utløpt (SignatureExpired)
        return None
    return TEKSTER.get(nokkel) if isinstance(nokkel, str) else None


def har_kvitteringscookie(request: Request) -> bool:
    return KVITTERING_COOKIE in request.cookies


def slett_kvittering(request: Request, svar: Response) -> None:
    svar.delete_cookie(
        KVITTERING_COOKIE, path="/", httponly=True, samesite="lax", secure=_secure(request)
    )
