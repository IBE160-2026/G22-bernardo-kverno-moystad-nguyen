"""Regler for konto og innlogging, og implementasjonen av `Autentisering` (AD-4).

Story 1.1 har bare oppslaget av en innlogget bruker. Innlogging, utlogging og
passord (AD-6) kommer i story 1.2.
"""

from __future__ import annotations

import hashlib

from sqlalchemy import select
from starlette.requests import Request

from app.core import klokke
from app.core.sesjon import SESJON_COOKIE, Innlogget
from app.identity.models import Bruker, Sesjon


def hash_sesjonsnokkel(nokkel: str) -> str:
    """SHA-256 (hex) av sesjonsnøkkelen. Tabellen `sesjon` lagrer bare hashen."""
    return hashlib.sha256(nokkel.encode("utf-8")).hexdigest()


class IdentityAutentisering:
    """`Autentisering` for appen. Sesjonene ligger i tabellen `sesjon` (AD-4).

    Story 1.2 lagrer `hash_sesjonsnokkel(nokkel)`, aldri selve nøkkelen fra cookien.
    """

    def finn_innlogget(self, request: Request) -> Innlogget | None:
        nokkel = request.cookies.get(SESJON_COOKIE)
        if not nokkel:
            return None
        with request.app.state.sesjonsfabrikk() as db:
            rad = db.execute(
                select(Sesjon.bruker_id, Bruker.navn)
                .join(Bruker, Bruker.id == Sesjon.bruker_id)
                .where(
                    Sesjon.nokkel == hash_sesjonsnokkel(nokkel),
                    Sesjon.utloper > klokke.na(),
                    Bruker.slettet_tidspunkt.is_(None),
                )
            ).first()
        if rad is None:
            return None
        return Innlogget(bruker_id=rad.bruker_id, visningsnavn=rad.navn or "")
