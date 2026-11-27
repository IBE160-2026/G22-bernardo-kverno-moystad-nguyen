"""Testbilder laget i minnet med Pillow (story 2.7, FR-27). Ingen binærfiler i repoet.

Bildene er laget så testene kan se hva `oppdrag/bilde.py` gjorde: venstre halvdel
er rød og høyre blå, så en snudd JPEG har rødt øverst (EXIF-orientering 6).
"""

from __future__ import annotations

import os
from io import BytesIO

from PIL import Image

from app.oppdrag.bilde import MAKS_BYTE

ROD = (220, 30, 30)
BLA = (30, 30, 220)
ORIENTERING = 0x0112
GPS_IFD = 0x8825


def todelt(bredde: int, hoyde: int, modus: str = "RGB") -> Image.Image:
    """Rød venstre halvdel og blå høyre halvdel."""
    im = Image.new("RGB", (bredde, hoyde), BLA)
    im.paste(ROD, (0, 0, bredde // 2, hoyde))
    return im if modus == "RGB" else im.convert(modus)


def lagre(im: Image.Image, format: str, **valg) -> bytes:
    ut = BytesIO()
    im.save(ut, format=format, **valg)
    return ut.getvalue()


def jpeg(bredde: int = 800, hoyde: int = 600, *, orientering: int | None = None, gps: bool = False,
         modus: str = "RGB", kvalitet: int = 85) -> bytes:
    """JPEG, eventuelt med EXIF-orientering og en GPS-posisjon (Oslo)."""
    exif = Image.Exif()
    if orientering is not None:
        exif[ORIENTERING] = orientering
    if gps:
        exif.get_ifd(GPS_IFD).update({1: "N", 2: (59.0, 55.0, 0.0), 3: "E", 4: (10.0, 45.0, 0.0)})
    valg = {"exif": exif.tobytes()} if (orientering is not None or gps) else {}
    return lagre(todelt(bredde, hoyde, modus), "JPEG", quality=kvalitet, **valg)


def png(bredde: int = 800, hoyde: int = 600, *, modus: str = "RGB") -> bytes:
    return lagre(todelt(bredde, hoyde, modus), "PNG")


def png_gjennomsiktig(bredde: int = 400, hoyde: int = 300) -> bytes:
    """Helt gjennomsiktig, unntatt et rødt kvadrat midt i."""
    im = Image.new("RGBA", (bredde, hoyde), (0, 0, 0, 0))
    im.paste((220, 30, 30, 255), (bredde // 3, hoyde // 3, 2 * bredde // 3, 2 * hoyde // 3))
    return lagre(im, "PNG")


def png_16_bit_gjennomsiktig(bredde: int = 100, hoyde: int = 80) -> bytes:
    """16-biters gråtoner (`I;16`) med `tRNS`: én gråverdi er gjennomsiktig."""
    return lagre(Image.new("I;16", (bredde, hoyde), 1000), "PNG", transparency=1000)


def png_mange_piksler(bredde: int = 7000, hoyde: int = 6000) -> bytes:
    """Modus «1» (1 bit per piksel): mange piksler, men bare noen kB som fil."""
    return lagre(Image.new("1", (bredde, hoyde), 1), "PNG", optimize=True)


def webp(bredde: int = 800, hoyde: int = 600) -> bytes:
    return lagre(todelt(bredde, hoyde), "WEBP", quality=80)


def webp_animert(bredde: int = 400, hoyde: int = 300) -> bytes:
    """To bilder: først rødt, så blått."""
    forste = Image.new("RGB", (bredde, hoyde), ROD)
    andre = Image.new("RGB", (bredde, hoyde), BLA)
    return lagre(forste, "WEBP", save_all=True, append_images=[andre], duration=200, loop=0)


def gif(bredde: int = 200, hoyde: int = 100) -> bytes:
    return lagre(todelt(bredde, hoyde), "GIF")


def avkuttet_jpeg() -> bytes:
    data = jpeg(800, 600)
    return data[: len(data) // 2]


SVG = (
    b'<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10">'
    b'<script>alert(1)</script></svg>'
)
TEKST = b"Dette er ikke et bilde.\n"


def for_stor() -> bytes:
    """4 MiB + 1 byte, som begynner som en JPEG."""
    data = jpeg(100, 100)
    return data + b"\0" * (MAKS_BYTE + 1 - len(data))


def stoy_png(bredde: int = 1450, hoyde: int = 1450) -> bytes:
    """Støy som PNG, cirka 6 MB: komprimeres nesten ikke (klienttesten i 2.7)."""
    return lagre(Image.frombytes("RGB", (bredde, hoyde), os.urandom(bredde * hoyde * 3)), "PNG")


def stoy_jpeg(bredde: int = 900, hoyde: int = 900, kvalitet: int = 95) -> bytes:
    """Støy som JPEG, cirka 1 MB (testen uten JS i 2.7)."""
    return lagre(Image.frombytes("RGB", (bredde, hoyde), os.urandom(bredde * hoyde * 3)), "JPEG",
                 quality=kvalitet)


def apne(data: bytes) -> Image.Image:
    im = Image.open(BytesIO(data))
    im.load()
    return im
