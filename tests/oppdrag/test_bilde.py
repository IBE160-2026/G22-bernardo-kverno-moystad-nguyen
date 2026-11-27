"""Bilde av oppdraget over HTTP: radene i I/O-matrisen i spec 2.7.

FR-27, FR-3, FR-6, FR-9, FR-10, NFR-5, NFR-10, NFR-12, AD-2, AD-5, AD-18, UX-DR33.
Klokka står fast på tirsdag 24.11.2026 kl. 13:00 norsk tid, og databasen har
testbrukerne og eksempeloppdragene fra seed: Kari eier «Måke snø i innkjørselen»
(med bilde), Nora eier «Mate katten i helgen» (med bilde, 0571), og Ola bor i 0571.
Hver test sender skjemaet med CSRF-nøkkel, og noen også uten.
"""

from __future__ import annotations

import base64
import html as htmlmodul
import re
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app import seed
from app.identity.models import Bruker
from app.oppdrag.bilde import (
    BILDETEKST_FOR_KORT,
    BILDETEKST_FOR_LANG,
    FEIL_FORMAT,
    FOR_MANGE_PIKSLER,
    FOR_STORT,
    SKRIV_BILDETEKST,
)
from app.core.csrf import MAKS_MULTIPART
from app.oppdrag.models import Oppdrag, Oppdragsbilde
from tests import bilder

from ..core.test_render import les_side
from .test_legge_ut import attrs, feltfeil

T0 = datetime(2026, 11, 24, 12, 0, tzinfo=timezone.utc)
# Bildene i seed og nye bilder er lagret med den faste klokka, så `?v=` er «{versjon}-{TS}».
TS = int(T0.timestamp())
MAKE = "Måke snø i innkjørselen"
KATTEN = "Mate katten i helgen"
LUFTE = "Lufte hunden mens jeg er bortreist"  # Karis avbrutte
CSRF = re.compile(r'name="csrf_token" value="([^"]+)"')
SKJEMA_ID = re.compile(r'name="skjema_id" value="([^"]+)"')
BEHOLDT = re.compile(r'name="bilde_beholdt" value="([^"]+)"')
TEKST = "Snø i innkjørselen"
BILDEBUFFER = "private, max-age=31536000, immutable"
KONFLIKT = "Oppdraget er endret. Last siden på nytt."

NYTT = {
    "beskrivelse": "Trenger noen som kan måke snø i innkjørselen min i morgen.",
    "tittel": "Måke snø foran garasjen",
    "kategori": "snomaking",
    "postnummer": "0571",
    "dato": "25.11.2026",
    "klokkeslett": "7",
    "tilbud": "belop",
    "belop": "300",
}
REDIGER = {
    "beskrivelse": "Trenger noen som kan måke snø i innkjørselen min i morgen tidlig.",
    "bildetekst": "Snødekt innkjørsel med en spade",
    "tittel": MAKE,
    "kategori": "snomaking",
    "postnummer": "0571",
    "dato": "25.11.2026",
    "klokkeslett": "09:00",
    "tilbud": "belop",
    "belop": "200",
}


@pytest.fixture(autouse=True)
def eksempeldata(db: Session, sett_na) -> None:
    sett_na(T0)
    seed.last_eksempeldata(db)
    db.commit()


@pytest.fixture
def som(klient: TestClient, db: Session, logg_inn_som):
    def _som(navn: str) -> TestClient:
        klient.cookies.clear()
        bruker = db.scalars(select(Bruker).where(Bruker.epost == f"{navn}@eksempel.no")).one()
        logg_inn_som(klient, bruker)
        return klient

    return _som


def oppdrag_med_tittel(db: Session, tittel: str) -> Oppdrag:
    db.expire_all()
    return db.scalars(select(Oppdrag).where(Oppdrag.tittel == tittel)).one()


def bilde_for(db: Session, oppdrag_id: int) -> Oppdragsbilde | None:
    db.expire_all()
    return db.get(Oppdragsbilde, oppdrag_id)


def antall(db: Session, modell) -> int:
    return db.scalar(select(func.count()).select_from(modell))


def fil(data: bytes, navn: str = "bilde.jpg", type_: str = "image/jpeg") -> dict:
    return {"bilde": (navn, data, type_)}


def send_ny(klient: TestClient, *, data: bytes | None = None, navn: str = "bilde.jpg",
            med_csrf: bool = True, skjema_id: str | None = None, **endringer: str):
    html = klient.get("/oppdrag/ny").text
    felt = {**NYTT, **endringer, "skjema_id": skjema_id or SKJEMA_ID.search(html).group(1)}
    if med_csrf:
        felt["csrf_token"] = CSRF.search(html).group(1)
    # Uten fil sendes et tomt filfelt, slik nettleseren gjør med multipart.
    filer = fil(data, navn) if data is not None else fil(b"", "", "application/octet-stream")
    return klient.post("/oppdrag/ny", data=felt, files=filer, follow_redirects=False)


def send_rediger(klient: TestClient, oppdrag_id: int, *, data: bytes | None = None,
                 med_csrf: bool = True, **endringer: str):
    html = klient.get("/profil").text
    felt = {**REDIGER, **endringer}
    if med_csrf:
        felt["csrf_token"] = CSRF.search(html).group(1)
    filer = fil(data) if data is not None else fil(b"", "", "application/octet-stream")
    return klient.post(f"/oppdrag/{oppdrag_id}/rediger", data=felt, files=filer, follow_redirects=False)


def bilder_i(html: str) -> list[dict]:
    return [a for t, a in les_side(html).tagger if t == "img"]


def nytt_oppdrag(db: Session) -> Oppdrag:
    return oppdrag_med_tittel(db, NYTT["tittel"])


# ---------- skjemaet (FR-27, UX-DR33) ----------


def test_skjemaet_har_filfeltet_og_bildeteksten_etter_beskrivelsen(som) -> None:
    """FR-27: tekstene ordrett fra EXPERIENCE.md, i steg 1 rett etter beskrivelsen og før tittelen."""
    html = som("kari").get("/oppdrag/ny").text
    skjema = attrs(html, "form", method="post")
    assert skjema["enctype"] == "multipart/form-data"
    rekkefolge = [
        '<label for="beskrivelse">',
        '<label for="bilde">Bilde (valgfritt)</label>',
        "Ikke vis husnummer, bilskilt, navn eller ansikter.",
        "JPEG, PNG eller WebP, høyst 4 MB.",
        'id="bilde"',
        '<label for="bildetekst">Hva viser bildet?</label>',
        "0 av 120 tegn",
        '<label for="tittel">Tittel</label>',
    ]
    posisjoner = [html.index(tekst) for tekst in rekkefolge]
    assert posisjoner == sorted(posisjoner)
    felt = attrs(html, "input", name="bilde")
    assert felt["type"] == "file"
    assert felt["accept"] == "image/jpeg,image/png,image/webp"
    assert felt["aria-describedby"] == "bilde-personvern bilde-format"
    assert "data-tom" not in felt and "required" not in felt
    tekst = attrs(html, "input", name="bildetekst")
    assert (tekst["type"], tekst["autocomplete"], tekst["data-maks"]) == ("text", "off", "120")
    assert "maxlength" not in tekst and "data-tom" not in tekst
    # Uten bilde er feltet skjult av bilde.js til en fil er valgt, men rendres alltid synlig.
    boks = attrs(html, "div", id="bildetekst-felt")
    assert "data-uten-bilde" in boks and "hidden" not in boks
    # Ingen miniatyr, «Fjern bildet» eller beholdt bilde uten bilde.
    for fravaer in ("Fjern bildet", "bilde_beholdt", "Bytt bilde"):
        assert fravaer not in html
    assert 'src="/static/js/bilde.js" defer' in html


def test_forhandsvisningen_har_skjult_bilde_til_bilde_js(som) -> None:
    html = som("kari").get("/oppdrag/ny").text
    (img,) = [a for a in bilder_i(html) if a.get("data-felt") == "bilde"]
    assert "hidden" in img and "src" not in img and img["alt"] == ""


# ---------- nytt oppdrag med bilde (FR-27, AD-18) ----------


def test_nytt_med_bilde_lagres_snudd_uten_metadata_og_vises(som, db: Session) -> None:
    """Matrisen «Nytt med bilde»: 303, en JPEG på 1067×1600 uten EXIF, bildet i detaljene og på kortet."""
    klient = som("kari")
    svar = send_ny(klient, data=bilder.jpeg(3000, 2000, orientering=6, gps=True), bildetekst=TEKST)
    assert svar.status_code == 303
    oppdrag = nytt_oppdrag(db)
    assert svar.headers["location"] == f"/oppdrag/{oppdrag.id}"
    rad = bilde_for(db, oppdrag.id)
    assert (rad.bildetekst, rad.bredde, rad.hoyde) == (TEKST, 1067, 1600)
    stor, liten = bilder.apne(rad.bilde), bilder.apne(rad.miniatyr)
    assert stor.size == (1067, 1600) and max(liten.size) <= 640
    assert not stor.getexif() and not liten.getexif()

    detaljer = klient.get(svar.headers["location"]).text
    assert "Oppdraget er lagt ut." in detaljer
    (img,) = bilder_i(detaljer)
    assert img == {
        "class": "detaljbilde", "src": f"/oppdrag/{oppdrag.id}/bilde?v=1-{TS}", "alt": TEKST,
        "width": "1067", "height": "1600",
    }
    # Under tittelen og kvitteringen, uten lenke rundt.
    assert detaljer.index("<h1>") < detaljer.index('id="kvittering"') < detaljer.index('class="detaljbilde"')
    assert not re.search(r'<a [^>]*>\s*<img class="detaljbilde"', detaljer)

    oversikt = som("ola").get("/").text
    kort = [a for a in bilder_i(oversikt) if a.get("src", "").startswith(f"/oppdrag/{oppdrag.id}/")]
    assert kort == [{
        "class": "kort__bilde", "src": f"/oppdrag/{oppdrag.id}/bilde/liten?v=1-{TS}", "alt": "",
        "loading": "lazy", "width": "640", "height": "360",
    }]


@pytest.mark.parametrize(
    ("data", "navn"),
    [(bilder.png_gjennomsiktig(), "bilde.png"), (bilder.webp(), "bilde.webp"),
     (bilder.webp_animert(), "animert.webp"), (bilder.jpeg(modus="CMYK"), "cmyk.jpg")],
    ids=["png-alfa", "webp", "webp-animert", "cmyk"],
)
def test_andre_formater_lagres_som_rgb_jpeg(som, db: Session, data: bytes, navn: str) -> None:
    assert send_ny(som("kari"), data=data, navn=navn, bildetekst=TEKST).status_code == 303
    stor = bilder.apne(bilde_for(db, nytt_oppdrag(db).id).bilde)
    assert (stor.format, stor.mode) == ("JPEG", "RGB")


def test_lite_bilde_forstorres_ikke(som, db: Session) -> None:
    assert send_ny(som("kari"), data=bilder.jpeg(300, 200), bildetekst=TEKST).status_code == 303
    rad = bilde_for(db, nytt_oppdrag(db).id)
    assert (rad.bredde, rad.hoyde) == (300, 200)


@pytest.mark.parametrize("bildetekst", ["", "Ignoreres uten bilde"])
def test_uten_bilde_ingen_rad_og_ingen_img(som, db: Session, bildetekst: str) -> None:
    klient = som("kari")
    svar = send_ny(klient, bildetekst=bildetekst)
    assert svar.status_code == 303
    oppdrag = nytt_oppdrag(db)
    assert bilde_for(db, oppdrag.id) is None
    assert not [a for a in bilder_i(klient.get(svar.headers["location"]).text) if a.get("class") == "detaljbilde"]
    oversikt = som("ola").get("/").text
    assert f"/oppdrag/{oppdrag.id}/bilde" not in oversikt


def test_uten_bilde_urlencoded_som_for(som, db: Session) -> None:
    """Invariant 2.1 (T-6): et skjema uten filfelt og uten bildetekst virker som før."""
    klient = som("kari")
    html = klient.get("/oppdrag/ny").text
    data = {**NYTT, "csrf_token": CSRF.search(html).group(1), "skjema_id": SKJEMA_ID.search(html).group(1)}
    svar = klient.post("/oppdrag/ny", data=data, follow_redirects=False)
    assert svar.status_code == 303
    assert bilde_for(db, nytt_oppdrag(db).id) is None


# ---------- feil i bildet (FR-27, NFR-10) ----------


@pytest.mark.parametrize(
    ("data", "navn"),
    [(bilder.TEKST, "bilde.jpg"), (bilder.SVG, "bilde.jpg"), (bilder.gif(), "bilde.gif"),
     (bilder.avkuttet_jpeg(), "bilde.jpg")],
    ids=["tekst-som-jpg", "svg-som-jpg", "gif", "avkuttet-jpeg"],
)
def test_feil_format_gir_422_ved_bildet(som, db: Session, data: bytes, navn: str) -> None:
    """Matrisen «Feil format»: feilen ved #bilde, alt annet beholdes, ingen feil ved bildeteksten."""
    for_ = antall(db, Oppdrag)
    svar = send_ny(som("kari"), data=data, navn=navn, bildetekst=TEKST, tittel="Min tittel")
    assert svar.status_code == 422
    html = svar.text
    assert feltfeil(html, "bilde") == FEIL_FORMAT
    assert feltfeil(html, "bildetekst") is None
    assert f'<a href="#bilde">{FEIL_FORMAT}</a>' in html
    felt = attrs(html, "input", name="bilde")
    assert felt["aria-invalid"] == "true"
    assert felt["aria-describedby"] == "bilde-personvern bilde-format bilde-feil"
    assert attrs(html, "input", name="bildetekst")["value"] == TEKST
    assert attrs(html, "input", name="tittel")["value"] == "Min tittel"
    assert "bilde_beholdt" not in html and "Fjern bildet" not in html
    assert antall(db, Oppdrag) == for_ and antall(db, Oppdragsbilde) == 4


def test_for_stor_fil(som, db: Session) -> None:
    svar = send_ny(som("kari"), data=bilder.for_stor(), bildetekst=TEKST)
    assert svar.status_code == 422
    assert feltfeil(svar.text, "bilde") == FOR_STORT
    assert antall(db, Oppdragsbilde) == 4


def test_for_mange_piksler(som, db: Session) -> None:
    svar = send_ny(som("kari"), data=bilder.png_mange_piksler(), navn="stor.png", bildetekst=TEKST)
    assert svar.status_code == 422
    assert feltfeil(svar.text, "bilde") == FOR_MANGE_PIKSLER


def test_alle_feilene_vises_samtidig_i_feltrekkefolge(som) -> None:
    """NFR-10: beskrivelse, bilde, … i oppsummeringen."""
    svar = send_ny(som("kari"), data=bilder.TEKST, beskrivelse="", tittel="")
    lenker = re.findall(r'<li><a href="#([^"]+)">', svar.text)
    assert lenker[:3] == ["beskrivelse", "bilde", "tittel"]


@pytest.mark.parametrize(
    ("bildetekst", "melding"),
    [("", SKRIV_BILDETEKST), ("ab", BILDETEKST_FOR_KORT), ("x" * 121, BILDETEKST_FOR_LANG)],
    ids=["tom", "ab", "121"],
)
def test_bildetekst_mangler_beholder_bildet(som, db: Session, bildetekst: str, melding: str) -> None:
    """Matrisen «Bildetekst mangler»: 422, miniatyren som data:-URL, «Fjern bildet» og `bilde_beholdt`."""
    svar = send_ny(som("kari"), data=bilder.jpeg(), bildetekst=bildetekst)
    assert svar.status_code == 422
    html = svar.text
    assert feltfeil(html, "bildetekst") == melding
    assert attrs(html, "input", name="bildetekst")["aria-invalid"] == "true"
    miniatyr = attrs(html, "img", **{"class": "beholdt-bilde__miniatyr"})
    assert miniatyr["src"].startswith("data:image/jpeg;base64,") and miniatyr["alt"] == "Valgt bilde"
    assert '<label for="fjern_bilde">Fjern bildet</label>' in html
    assert '<label for="bilde">Bytt bilde</label>' in html
    assert "data-uten-bilde" not in attrs(html, "div", id="bildetekst-felt")
    beholdt = BEHOLDT.search(html).group(1)
    assert bilder.apne(base64.b64decode(beholdt)).format == "JPEG"
    assert antall(db, Oppdragsbilde) == 4


def _beholdt_fra_422(klient: TestClient) -> tuple[str, str]:
    svar = send_ny(klient, data=bilder.jpeg(800, 600), bildetekst="")
    assert svar.status_code == 422
    return BEHOLDT.search(svar.text).group(1), SKJEMA_ID.search(svar.text).group(1)


def test_beholdt_bilde_sendt_pa_nytt_lagres(som, db: Session) -> None:
    klient = som("kari")
    beholdt, skjema_id = _beholdt_fra_422(klient)
    svar = send_ny(klient, skjema_id=skjema_id, bildetekst=TEKST, bilde_beholdt=beholdt)
    assert svar.status_code == 303
    rad = bilde_for(db, nytt_oppdrag(db).id)
    assert (rad.bildetekst, rad.bredde, rad.hoyde) == (TEKST, 800, 600)


def test_beholdt_bilde_fjernet_lagres_uten_bilde(som, db: Session) -> None:
    klient = som("kari")
    beholdt, skjema_id = _beholdt_fra_422(klient)
    svar = send_ny(klient, skjema_id=skjema_id, bildetekst="", bilde_beholdt=beholdt, fjern_bilde="1")
    assert svar.status_code == 303
    assert bilde_for(db, nytt_oppdrag(db).id) is None


@pytest.mark.parametrize(
    ("beholdt", "melding"),
    [("abc", FEIL_FORMAT), (base64.b64encode(bilder.TEKST).decode(), FEIL_FORMAT),
     (base64.b64encode(bilder.SVG).decode(), FEIL_FORMAT)],
    ids=["abc", "tekst", "svg"],
)
def test_forfalsket_beholdt_bilde(som, db: Session, beholdt: str, melding: str) -> None:
    svar = send_ny(som("kari"), bildetekst=TEKST, bilde_beholdt=beholdt)
    assert svar.status_code == 422
    assert feltfeil(svar.text, "bilde") == melding
    assert antall(db, Oppdragsbilde) == 4


def test_forfalsket_beholdt_over_4_mib_gir_feltfeilen(som, db: Session) -> None:
    """Matrisen «Forfalsket beholdt»: base64 av over 4 MiB er under kroppsgrensen og gir
    «Bildet er for stort. Velg et bilde på høyst 4 MB.» ved bildet (422)."""
    svar = send_ny(som("kari"), bildetekst=TEKST, bilde_beholdt=base64.b64encode(bilder.for_stor()).decode())
    assert svar.status_code == 422
    assert feltfeil(svar.text, "bilde") == FOR_STORT
    assert antall(db, Oppdragsbilde) == 4


def test_ny_fil_og_beholdt_bilde_av_maks_storrelse_er_under_kroppsgrensen(som, db: Session) -> None:
    """Uten JS: en ny fil på nesten 4 MB og et beholdt bilde som base64 får plass i én kropp, så
    skjemaet ikke går tapt med 413."""
    svar = send_ny(som("kari"), data=bilder.for_stor()[:-2], bildetekst="",
                   bilde_beholdt=base64.b64encode(bilder.for_stor()[:-2]).decode())
    assert svar.status_code == 422
    assert antall(db, Oppdragsbilde) == 4


def test_ny_ugyldig_fil_og_gyldig_beholdt(som, db: Session) -> None:
    """Matrisen: feilen ved #bilde, og det beholdte bildet står fortsatt med «Fjern bildet»."""
    klient = som("kari")
    beholdt, skjema_id = _beholdt_fra_422(klient)
    svar = send_ny(klient, data=bilder.TEKST, skjema_id=skjema_id, bildetekst=TEKST, bilde_beholdt=beholdt)
    assert svar.status_code == 422
    assert feltfeil(svar.text, "bilde") == FEIL_FORMAT
    assert BEHOLDT.search(svar.text) is not None
    assert "Fjern bildet" in svar.text


def test_kroppsgrensen(som, db: Session) -> None:
    """Multipart over grensen gir 413 med «Bildet er for stort. …», urlencoded over 1 MB gir 413,
    og ruta kalles ikke."""
    klient = som("kari")
    svar = send_ny(klient, data=b"\xff\xd8" + b"x" * MAKS_MULTIPART, bildetekst=TEKST)
    assert svar.status_code == 413
    assert f"<h1>{FOR_STORT}</h1>" in svar.text
    html = klient.get("/oppdrag/ny").text
    data = {**NYTT, "csrf_token": CSRF.search(html).group(1), "skjema_id": SKJEMA_ID.search(html).group(1),
            "bildetekst": "x" * (1024 * 1024)}
    assert klient.post("/oppdrag/ny", data=data, follow_redirects=False).status_code == 413
    assert antall(db, Oppdrag) == len(seed.EKSEMPELOPPDRAG)


def test_uten_csrf_med_fil_gir_403(som, db: Session) -> None:
    svar = send_ny(som("kari"), data=bilder.jpeg(), bildetekst=TEKST, med_csrf=False)
    assert svar.status_code == 403
    assert antall(db, Oppdrag) == len(seed.EKSEMPELOPPDRAG)


def test_dobbel_innsending_gir_en_rad_i_hver_tabell(som, db: Session) -> None:
    """NFR-5: samme `skjema_id` og bilde to ganger gir `Duplikat` til det første."""
    klient = som("kari")
    html = klient.get("/oppdrag/ny").text
    felt = {**NYTT, "bildetekst": TEKST, "csrf_token": CSRF.search(html).group(1),
            "skjema_id": SKJEMA_ID.search(html).group(1)}
    data = bilder.jpeg()
    forste = klient.post("/oppdrag/ny", data=felt, files=fil(data), follow_redirects=False)
    andre = klient.post("/oppdrag/ny", data=felt, files=fil(data), follow_redirects=False)
    assert forste.status_code == andre.status_code == 303
    assert forste.headers["location"] == andre.headers["location"]
    assert antall(db, Oppdrag) == len(seed.EKSEMPELOPPDRAG) + 1
    assert antall(db, Oppdragsbilde) == 5


def test_xss_i_bildeteksten_vises_som_tekst(som, db: Session) -> None:
    """NFR-12: bildeteksten står som tekst i `alt` og i feltverdien ved 422."""
    skadelig = "<script>alert(1)</script>"
    klient = som("kari")
    feil = send_ny(klient, data=bilder.jpeg(), bildetekst=skadelig, tittel="")
    assert feil.status_code == 422
    assert skadelig not in feil.text
    assert attrs(feil.text, "input", name="bildetekst")["value"] == skadelig
    svar = send_ny(klient, data=bilder.jpeg(), bildetekst=skadelig)
    assert svar.status_code == 303
    detaljer = klient.get(svar.headers["location"]).text
    assert skadelig not in detaljer
    assert f'alt="{htmlmodul.escape(skadelig)}"' in detaljer


# ---------- hente bildet (FR-9, FR-3, AD-18) ----------


@pytest.mark.parametrize("sti", ["bilde", "bilde/liten"])
def test_ola_henter_bildet_pa_karis_apne_oppdrag(som, db: Session, sti: str) -> None:
    make = oppdrag_med_tittel(db, MAKE)
    svar = som("ola").get(f"/oppdrag/{make.id}/{sti}?v=1-{TS}")
    assert svar.status_code == 200
    assert svar.headers["content-type"] == "image/jpeg"
    assert svar.headers.get_list("cache-control") == [BILDEBUFFER]
    assert svar.headers["x-content-type-options"] == "nosniff"
    im = bilder.apne(svar.content)
    assert im.format == "JPEG" and max(im.size) <= (640 if sti == "bilde/liten" else 1600)


@pytest.mark.parametrize("sti", ["bilde", "bilde/liten"])
def test_ingen_tilgang_gir_samme_404(som, db: Session, lag_bilde, sti: str) -> None:
    """FR-9: andres avbrutte, id som ikke finnes, id 0 og oppdrag uten bilde gir samme 404 som detaljene."""
    lufte = oppdrag_med_tittel(db, LUFTE)
    lag_bilde(lufte, bildetekst="Hundebånd ved døra")
    uten = oppdrag_med_tittel(db, "Raking av løv i hagen")
    klient = som("ola")
    finnes_ikke = klient.get("/oppdrag/999999")
    fjern_csrf = re.compile(r'value="[^"]*"')
    for oppdrag_id in (lufte.id, 999999, 0, 2**31, uten.id):
        svar = klient.get(f"/oppdrag/{oppdrag_id}/{sti}")
        assert svar.status_code == 404, oppdrag_id
        assert fjern_csrf.sub("", svar.text) == fjern_csrf.sub("", finnes_ikke.text), oppdrag_id
        assert svar.headers.get_list("cache-control") == ["no-store"]
    # Oppdragsgiveren ser bildet på sitt eget avbrutte oppdrag.
    assert som("kari").get(f"/oppdrag/{lufte.id}/{sti}").status_code == 200


def test_uten_innlogging_gir_303_til_innlogging(klient: TestClient, db: Session) -> None:
    make = oppdrag_med_tittel(db, MAKE)
    for sti in (f"/oppdrag/{make.id}/bilde", f"/oppdrag/{make.id}/bilde/liten"):
        svar = klient.get(sti, follow_redirects=False)
        assert svar.status_code == 303
        assert svar.headers["location"].startswith("/logg-inn?neste=/oppdrag/")


def test_andre_sider_har_fortsatt_no_store(som, db: Session) -> None:
    """FR-2: bare bilderutene har `Cache-Control` med `max-age`."""
    make = oppdrag_med_tittel(db, MAKE)
    klient = som("ola")
    for sti in ("/", f"/oppdrag/{make.id}", "/mine-oppdrag"):
        assert klient.get(sti).headers.get_list("cache-control") == ["no-store"], sti


# ---------- oversikt, detaljer og «Mine oppdrag» (FR-10, FR-18, UX-DR33) ----------


def test_ola_ser_to_av_fire_kort_med_bilde(som, db: Session) -> None:
    """Seed: Karis «Måke snø» og Noras «Mate katten» har bilde, de to andre ikke. Ingen plassholder."""
    html = som("ola").get("/").text
    assert html.count('<div class="kort kort--lenke">') == 4
    kort = [a for a in bilder_i(html) if a.get("class") == "kort__bilde"]
    make, katten = oppdrag_med_tittel(db, MAKE), oppdrag_med_tittel(db, KATTEN)
    assert sorted(a["src"] for a in kort) == sorted(
        f"/oppdrag/{o.id}/bilde/liten?v={o.versjon}-{TS}" for o in (make, katten)
    )
    assert all(a["alt"] == "" and a["loading"] == "lazy" for a in kort)
    # Bildet står først i kortet, før kategorien og tittellenken.
    start = html.index(f'/oppdrag/{make.id}/bilde/liten')
    assert start < html.index(f'href="/oppdrag/{make.id}"') and html.rfind('<div class="kort', 0, start) > 0


def test_mine_oppdrag_viser_aldri_bilde(som) -> None:
    html = som("kari").get("/mine-oppdrag").text
    assert "<img" not in html


def test_detaljer_uten_bilde_har_ingen_img(som, db: Session) -> None:
    uten = oppdrag_med_tittel(db, "Raking av løv i hagen")
    assert "<img" not in som("ola").get(f"/oppdrag/{uten.id}").text


# ---------- redigering (FR-6, FR-27) ----------


def test_redigering_viser_lagret_bilde_med_bytt_og_fjern(som, db: Session) -> None:
    make = oppdrag_med_tittel(db, MAKE)
    html = som("kari").get(f"/oppdrag/{make.id}/rediger").text
    assert '<label for="bilde">Bytt bilde</label>' in html
    assert '<label for="fjern_bilde">Fjern bildet</label>' in html
    assert "checked" not in attrs(html, "input", name="fjern_bilde")
    miniatyr = attrs(html, "img", **{"class": "beholdt-bilde__miniatyr"})
    assert miniatyr["src"] == f"/oppdrag/{make.id}/bilde/liten?v={make.versjon}-{TS}"
    assert miniatyr["alt"] == "Valgt bilde"
    assert "bilde_beholdt" not in html
    assert attrs(html, "input", name="bildetekst")["value"] == "Snødekt innkjørsel med en spade"
    assert "data-uten-bilde" not in attrs(html, "div", id="bildetekst-felt")
    (forhandsvisning,) = [a for a in bilder_i(html) if a.get("data-felt") == "bilde"]
    assert forhandsvisning["src"] == miniatyr["src"] and "hidden" not in forhandsvisning


def test_bytte_bilde(som, db: Session) -> None:
    """Matrisen «Bytte bilde»: nytt bilde, `versjon` + 1, ny `?v=` og `vesentlig_endret` uendret."""
    make = oppdrag_med_tittel(db, MAKE)
    versjon = make.versjon
    gammelt = bytes(bilde_for(db, make.id).bilde)
    klient = som("kari")
    assert f"/oppdrag/{make.id}/bilde?v={versjon}-{TS}" in klient.get(f"/oppdrag/{make.id}").text
    svar = send_rediger(klient, make.id, data=bilder.png(400, 300))
    assert svar.status_code == 303
    assert "Endringene er lagret." in klient.get(svar.headers["location"]).text
    rad = bilde_for(db, make.id)
    assert (rad.bredde, rad.hoyde) == (400, 300) and bytes(rad.bilde) != gammelt
    lagret = oppdrag_med_tittel(db, MAKE)
    assert (lagret.versjon, lagret.vesentlig_endret) == (versjon + 1, None)
    detaljer = klient.get(f"/oppdrag/{make.id}").text
    assert f"/oppdrag/{make.id}/bilde?v={versjon + 1}-{TS}" in detaljer


def test_fjerne_bilde(som, db: Session) -> None:
    make = oppdrag_med_tittel(db, MAKE)
    klient = som("kari")
    assert send_rediger(klient, make.id, fjern_bilde="1", bildetekst="").status_code == 303
    assert bilde_for(db, make.id) is None
    assert oppdrag_med_tittel(db, MAKE).vesentlig_endret is None
    assert "<img" not in klient.get(f"/oppdrag/{make.id}").text
    assert f"/oppdrag/{make.id}/bilde" not in som("ola").get("/").text


def test_bare_bildetekst(som, db: Session) -> None:
    make = oppdrag_med_tittel(db, MAKE)
    gammelt = bytes(bilde_for(db, make.id).bilde)
    assert send_rediger(som("kari"), make.id, bildetekst="Innkjørsel full av snø").status_code == 303
    rad = bilde_for(db, make.id)
    assert rad.bildetekst == "Innkjørsel full av snø" and bytes(rad.bilde) == gammelt
    assert oppdrag_med_tittel(db, MAKE).vesentlig_endret is None


def test_urort_bilde_beholdes_og_tom_bildetekst_gir_feil(som, db: Session) -> None:
    make = oppdrag_med_tittel(db, MAKE)
    klient = som("kari")
    assert send_rediger(klient, make.id, tittel="Måke snø i morgen").status_code == 303
    assert bilde_for(db, make.id) is not None
    svar = send_rediger(klient, make.id, bildetekst="")
    assert svar.status_code == 422
    assert feltfeil(svar.text, "bildetekst") == SKRIV_BILDETEKST
    # Det lagrede bildet vises fortsatt, uten `bilde_beholdt`.
    assert "beholdt-bilde__miniatyr" in svar.text and "bilde_beholdt" not in svar.text


def test_fjern_valgt_beholdes_ved_422(som, db: Session) -> None:
    """«Fjern bildet» står krysset av, og forhåndsvisningen viser ikke bildet som skal fjernes."""
    make = oppdrag_med_tittel(db, MAKE)
    svar = send_rediger(som("kari"), make.id, fjern_bilde="1", bildetekst="", tittel="")
    assert svar.status_code == 422
    assert "checked" in attrs(svar.text, "input", name="fjern_bilde")
    (forhandsvisning,) = [a for a in bilder_i(svar.text) if a.get("data-felt") == "bilde"]
    assert "hidden" in forhandsvisning and "src" not in forhandsvisning
    assert bilde_for(db, make.id) is not None


def test_nytt_bilde_ved_422_i_redigering_beholdes(som, db: Session) -> None:
    make = oppdrag_med_tittel(db, MAKE)
    svar = send_rediger(som("kari"), make.id, data=bilder.png(400, 300), tittel="")
    assert svar.status_code == 422
    assert BEHOLDT.search(svar.text) is not None
    assert attrs(svar.text, "img", **{"class": "beholdt-bilde__miniatyr"})["src"].startswith("data:")
    assert bilde_for(db, make.id).bredde != 400


def test_fjern_og_ny_fil(som, db: Session) -> None:
    make = oppdrag_med_tittel(db, MAKE)
    assert send_rediger(som("kari"), make.id, data=bilder.png(400, 300), fjern_bilde="1").status_code == 303
    assert bilde_for(db, make.id).bredde == 400


def test_andres_oppdrag_med_fil_gir_404_og_bildet_er_uendret(som, db: Session) -> None:
    make = oppdrag_med_tittel(db, MAKE)
    gammelt = bytes(bilde_for(db, make.id).bilde)
    svar = send_rediger(som("ola"), make.id, data=bilder.png(400, 300))
    assert svar.status_code == 404
    assert bytes(bilde_for(db, make.id).bilde) == gammelt


def test_ikke_apen_med_fil_gir_konflikt_og_bildet_er_uendret(som, db: Session) -> None:
    make = oppdrag_med_tittel(db, MAKE)
    gammelt = bytes(bilde_for(db, make.id).bilde)
    make.status = "avbrutt"
    db.commit()
    klient = som("kari")
    svar = send_rediger(klient, make.id, data=bilder.png(400, 300))
    assert svar.status_code == 303
    assert svar.headers["location"] == f"/oppdrag/{make.id}"
    assert KONFLIKT in klient.get(svar.headers["location"]).text
    assert bytes(bilde_for(db, make.id).bilde) == gammelt


def test_rediger_uten_csrf_med_fil_gir_403(som, db: Session) -> None:
    make = oppdrag_med_tittel(db, MAKE)
    assert send_rediger(som("kari"), make.id, data=bilder.png(400, 300), med_csrf=False).status_code == 403
    assert bilde_for(db, make.id).bredde != 400


def test_redigering_uten_bilde_som_for(som, db: Session) -> None:
    """Invariant 2.5 (T-6): et oppdrag uten bilde redigeres som før, og bildeteksten ignoreres."""
    baere = oppdrag_med_tittel(db, "Bære ved opp til tredje etasje")
    klient = som("kari")
    html = klient.get(f"/oppdrag/{baere.id}/rediger").text
    assert '<label for="bilde">Bilde (valgfritt)</label>' in html and "Fjern bildet" not in html
    svar = send_rediger(klient, baere.id, tittel=baere.tittel, beskrivelse=baere.beskrivelse,
                        kategori=baere.kategori, belop="400", dato="28.11.2026", klokkeslett="10:00",
                        bildetekst="")
    assert svar.status_code == 303
    assert bilde_for(db, baere.id) is None
