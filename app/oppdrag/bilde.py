"""Bilde av oppdraget: eneste sted opplastede filer åpnes (FR-27, NFR-9, NFR-12, AD-18).

- `behandle(data)`: bytes fra filfeltet (`request.state.filer`) blir en ny JPEG
  på høyst 1 600 px og en miniatyr på høyst 640 px. Størrelsen sjekkes før
  fila åpnes, og antallet piksler før den dekodes. Formatet bestemmes av
  innholdet (`Image.open(formats=...)`), aldri av filnavn eller `Content-Type`.
  Bildet snus etter EXIF-orienteringen, gjennomsiktige områder blir hvite, og
  et animert bilde gir første bilde. Resultatet har aldri EXIF, GPS, ICC eller
  andre metadata, og bildet forstørres aldri.
- `fra_beholdt(tekst)`: det skjulte feltet `bilde_beholdt` (base64) går gjennom
  `behandle` på nytt, så et forfalsket felt ikke gir mer enn en vanlig
  opplasting. `til_beholdt(bilde)` lager feltet.
- Feil gir `RegelBrudd([("bilde", tekst)])` med tekstene fra EXPERIENCE.md.

PIL importeres bare her og i `app/seed.py` (arkitekturtesten).
"""

from __future__ import annotations

import base64
import binascii
from dataclasses import dataclass
from io import BytesIO

from PIL import Image, ImageOps

from app.core.domene import BILDE_MAKS_BYTE
from app.core.feil import RegelBrudd

# Grensene (FR-27, spec 2.7): 4 MB er 4 × 1024 × 1024 byte, og 40 megapiksler betyr
# bredde × høyde > 40 000 000.
MAKS_BYTE = BILDE_MAKS_BYTE
MAKS_PIKSLER = 40_000_000
STOR = 1600
LITEN = 640
KVALITET = 85
FORMATER = ["JPEG", "PNG", "WEBP"]

# Feiltekstene står ordrett i EXPERIENCE.md § Feiltekster ved felt (FR-27).
FEIL_FORMAT = "Velg et bilde i JPEG, PNG eller WebP."
FOR_STORT = "Bildet er for stort. Velg et bilde på høyst 4 MB."
FOR_MANGE_PIKSLER = "Bildet har for mange piksler. Velg et mindre bilde."
SKRIV_BILDETEKST = "Skriv hva bildet viser."
BILDETEKST_FOR_KORT = "Teksten må ha minst 3 tegn."
BILDETEKST_FOR_LANG = "Teksten kan ha høyst 120 tegn."

_GRAATONER_16 = frozenset({"I", "I;16", "I;16B", "I;16L", "I;16N", "F"})


@dataclass(frozen=True)
class Bilde:
    """Et ferdig behandlet bilde: to JPEG-er uten metadata, og målene til den store."""

    bilde: bytes
    miniatyr: bytes
    bredde: int
    hoyde: int


def _feil(tekst: str) -> RegelBrudd:
    return RegelBrudd([("bilde", tekst)])


def _paa_hvitt(im: Image.Image) -> Image.Image:
    """RGB-kopi av bildet. Gjennomsiktige områder legges på hvit bakgrunn."""
    if im.mode in _GRAATONER_16:
        # 16-biters gråtoner (PNG) skaleres til 8 bit i stedet for å klippes. Det skjer før
        # gjennomsiktigheten, fordi `I;16` med `tRNS` ikke kan gjøres om til RGBA direkte.
        im = im.convert("I").point(lambda verdi: verdi * (1 / 256)).convert("L")
    if im.mode in {"RGBA", "LA", "PA", "RGBa", "La"} or "transparency" in im.info:
        rgba = im.convert("RGBA")
        bakgrunn = Image.new("RGB", rgba.size, (255, 255, 255))
        bakgrunn.paste(rgba, mask=rgba.getchannel("A"))
        return bakgrunn
    return im.convert("RGB")


def _jpeg(im: Image.Image) -> bytes:
    # Ingen exif= og icc_profile=, og `info` tømmes, så ingen metadata følger med.
    im.info = {}
    ut = BytesIO()
    im.save(ut, format="JPEG", quality=KVALITET, optimize=True)
    return ut.getvalue()


def behandle(data: bytes) -> Bilde:
    """Bytes fra en opplasting blir et `Bilde`, eller `RegelBrudd` ved `bilde`."""
    if len(data) > MAKS_BYTE:
        raise _feil(FOR_STORT)
    try:
        with Image.open(BytesIO(data), formats=FORMATER) as im:
            # Bare overskriften er lest. Pikslene sjekkes før noe dekodes.
            if im.width * im.height > MAKS_PIKSLER:
                raise _feil(FOR_MANGE_PIKSLER)
            # JPEG kan dekodes rett i mindre skala. Gjør ingenting for andre formater.
            im.draft("RGB", (STOR, STOR))
            snudd = ImageOps.exif_transpose(im)  # laster pikslene (første bilde)
            rgb = _paa_hvitt(snudd)
    except RegelBrudd:
        raise
    except Image.DecompressionBombError:
        raise _feil(FOR_MANGE_PIKSLER) from None
    except MemoryError:
        raise
    except Exception:
        # Ødelagt EXIF eller feil i dekoderen (`UnidentifiedImageError`, `OSError`,
        # `struct.error`, `KeyError` og andre): fila er ikke et bilde vi kan bruke.
        raise _feil(FEIL_FORMAT) from None
    rgb.thumbnail((STOR, STOR), Image.Resampling.LANCZOS)  # forstørrer aldri
    liten = rgb.copy()
    liten.thumbnail((LITEN, LITEN), Image.Resampling.LANCZOS)
    return Bilde(bilde=_jpeg(rgb), miniatyr=_jpeg(liten), bredde=rgb.width, hoyde=rgb.height)


def fra_beholdt(tekst: str) -> Bilde:
    """Det skjulte feltet `bilde_beholdt` behandlet på nytt (AD-18). Ugyldig base64 gir formatfeilen."""
    try:
        data = base64.b64decode(tekst.strip(), validate=True)
    except (binascii.Error, ValueError):
        raise _feil(FEIL_FORMAT) from None
    return behandle(data)


def til_beholdt(bilde: Bilde) -> str:
    """Verdien i det skjulte feltet `bilde_beholdt`: den store JPEG-en som base64."""
    return base64.b64encode(bilde.bilde).decode("ascii")


def miniatyr_data_url(bilde: Bilde) -> str:
    """Miniatyren som `data:`-URL, til et beholdt bilde som ikke er lagret ennå."""
    return "data:image/jpeg;base64," + base64.b64encode(bilde.miniatyr).decode("ascii")
