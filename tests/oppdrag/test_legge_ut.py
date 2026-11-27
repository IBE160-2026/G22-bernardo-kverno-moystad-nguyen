"""«Nytt oppdrag» og detaljene over HTTP: radene i I/O-matrisen i spec 2.1
(FR-5, FR-9, NFR-5, NFR-10, NFR-12, AD-16, UX-DR10–UX-DR14, UX-DR22, UX-DR27).

Også etiketter, `fieldset`/`legend`, felttyper, `aria-describedby`/`aria-invalid`,
forhåndsutfylt postnummer, menyvalget på undersider, kvitteringen og at detaljene
ikke inneholder telefon, e-post eller fødselsdato. Klokka står fast på tirsdag
24.11.2026 kl. 13:00 norsk tid.
"""

from __future__ import annotations

import re
from datetime import date, datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app.oppdrag.models import Oppdrag

from ..core.test_render import les_side
from .test_grunnsider import menyvalg

T0 = datetime(2026, 11, 24, 12, 0, tzinfo=timezone.utc)
NBSP = " "

GYLDIG = {
    "beskrivelse": "Trenger noen som kan måke snø i innkjørselen min i morgen.",
    "tittel": "Måke snø i innkjørselen",
    "kategori": "snomaking",
    "postnummer": "0571",
    "dato": "25.11.2026",
    "klokkeslett": "7",
    "tilbud": "belop",
    "belop": "1000",
}
GRUPPELENKER = {"nar": "dato", "kategori": "kategori-snomaking", "tilbud": "tilbud-belop"}


@pytest.fixture(autouse=True)
def _klokke(sett_na) -> None:
    sett_na(T0)


@pytest.fixture
def kari(lag_bruker):
    return lag_bruker(navn="Kari Nordmann", postnummer="0571", telefon="91234567",
                      epost="kari.n@eksempel.no", fodselsdato=date(1954, 5, 3))


@pytest.fixture
def kari_klient(klient: TestClient, kari, logg_inn_som) -> TestClient:
    logg_inn_som(klient, kari)
    return klient


def skjemanokler(klient: TestClient) -> tuple[str, str]:
    """(csrf_token, skjema_id) fra et nytt skjema."""
    html = klient.get("/oppdrag/ny").text
    csrf = re.search(r'name="csrf_token" value="([^"]+)"', html).group(1)
    skjema_id = re.search(r'name="skjema_id" value="([^"]+)"', html).group(1)
    return csrf, skjema_id


def send(klient: TestClient, *, skjema_id: str | None = None, **endringer: str):
    csrf, ny_id = skjemanokler(klient)
    data = {"csrf_token": csrf, "skjema_id": skjema_id if skjema_id is not None else ny_id, **GYLDIG, **endringer}
    return klient.post("/oppdrag/ny", data=data, follow_redirects=False)


def antall(db) -> int:
    return db.scalar(select(func.count()).select_from(Oppdrag))


def attrs(html: str, tag: str, **filter_: str) -> dict:
    return next(
        a for t, a in les_side(html).tagger
        if t == tag and all(a.get(k) == v for k, v in filter_.items())
    )


def feltfeil(html: str, felt: str) -> str | None:
    treff = re.search(rf'<p class="feltfeil" id="{felt}-feil">.*?<span>([^<]*)</span>', html, re.S)
    return treff.group(1) if treff else None


# ---------- skjemaet ----------


def test_skjemaet_har_feltene_i_rekkefolge(kari_klient: TestClient) -> None:
    """FR-5, UX-DR11, UX-DR15, UX-DR16: etikettene og hjelpetekstene ordrett, i feltrekkefølgen
    fra spec 2.1, med de to `h2` og forhåndsvisningen fra spec 2.2 (én skjerm, uten JS)."""
    svar = kari_klient.get("/oppdrag/ny")
    assert svar.status_code == 200
    html = svar.text
    assert "<title>Nytt oppdrag – Nabolagshelten</title>" in html
    assert "<h1>Nytt oppdrag</h1>" in html
    rekkefolge = [
        ">Hva trenger du hjelp til?</h2>",
        '<label for="beskrivelse">Hva trenger du hjelp til?</label>',
        "Skriv med egne ord.",
        "Ikke skriv adresse eller telefonnummer – det avtaler dere når hjelperen er valgt.",
        '<label for="tittel">Tittel</label>',
        '<legend class="gruppe__etikett">Kategori</legend>',
        ">Neste</button>",
        ">Når og hvor?</h2>",
        '<label for="postnummer">Postnummer</label>',
        '<legend class="gruppe__etikett">Når?</legend>',
        '<label for="dato">Dato</label>',
        "dd.mm.åååå, for eksempel 14.11.2026",
        '<label for="klokkeslett">Klokkeslett</label>',
        "tt:mm, for eksempel 07:00",
        '<legend class="gruppe__etikett">Hva tilbyr du?</legend>',
        '<label for="tilbud-belop">Beløp</label>',
        '<label for="belop">Beløp i kr</label>',
        '<label for="tilbud-uten">Uten betaling</label>',
        ">Slik vises oppdraget for andre.</p>",
        ">Publiser</button>",
        ">Tilbake til steg 1</button>",
    ]
    posisjoner = [html.index(tekst) for tekst in rekkefolge]
    assert posisjoner == sorted(posisjoner)
    assert re.search(r'<a class="tekstknapp" href="[^"]+" data-vis-i-steg="1">Tilbake</a>', html)
    kategorier = re.findall(r'name="kategori" value="([^"]+)"', html)
    assert kategorier == ["snomaking", "hage", "baerehjelp-flytting", "dyrepass", "teknologihjelp", "annet"]
    for tekst in ("Snømåking", "Hage", "Bærehjelp/<wbr>flytting", "Dyrepass", "Teknologihjelp", "Annet"):
        assert f"<span>{tekst}</span>" in html


def test_skjemaet_har_riktige_felttyper(kari_klient: TestClient) -> None:
    """EXPERIENCE.md § Felttyper: autocomplete=off, ingen inputmode på dato og klokkeslett, ingen maxlength."""
    html = kari_klient.get("/oppdrag/ny").text
    form = attrs(html, "form")
    assert form["method"] == "post" and form["action"] == "/oppdrag/ny" and "novalidate" in form
    beskrivelse = attrs(html, "textarea", name="beskrivelse")
    assert beskrivelse["autocomplete"] == "off" and beskrivelse["data-maks"] == "1000"
    for navn in ("tittel", "dato", "klokkeslett"):
        felt = attrs(html, "input", name=navn)
        assert (felt["type"], felt["autocomplete"]) == ("text", "off"), navn
        assert "inputmode" not in felt, navn
    belop = attrs(html, "input", name="belop")
    assert (belop["type"], belop["inputmode"], belop["autocomplete"]) == ("text", "numeric", "off")
    postnummer = attrs(html, "input", name="postnummer")
    assert (postnummer["inputmode"], postnummer["autocomplete"]) == ("numeric", "postal-code")
    assert "maxlength" not in html
    assert 'type="date"' not in html and 'type="time"' not in html
    assert html.count('type="radio"') == 8


def test_skjemaet_har_forhandsutfylt_postnummer_og_skjema_id(kari_klient: TestClient) -> None:
    """FR-5: postnummeret fra profilen med poststed. AD-2: ny `skjema_id` for hvert skjema."""
    html = kari_klient.get("/oppdrag/ny").text
    assert attrs(html, "input", name="postnummer")["value"] == "0571"
    assert '<span id="postnummer-sted" aria-live="polite">Oslo</span>' in html
    skjema_id = attrs(html, "input", name="skjema_id")
    assert skjema_id["type"] == "hidden"
    assert re.fullmatch(r"[A-Za-z0-9_-]{16,64}", skjema_id["value"])
    assert skjemanokler(kari_klient)[1] != skjema_id["value"]


def test_skjemaet_har_teller_og_aria_live(kari_klient: TestClient) -> None:
    """UX-DR13: serveren skriver «0 av 1000 tegn», og varselnoden er tom til grensen nås."""
    html = kari_klient.get("/oppdrag/ny").text
    beskrivelse = attrs(html, "textarea", name="beskrivelse")
    assert beskrivelse["aria-describedby"] == "beskrivelse-hjelp beskrivelse-personvern beskrivelse-teller"
    assert (beskrivelse["data-teller"], beskrivelse["data-varsel"]) == ("beskrivelse-teller", "beskrivelse-varsel")
    assert '<p class="teller" id="beskrivelse-teller">0 av 1000 tegn</p>' in html
    assert '<p class="skjult-tekst" id="beskrivelse-varsel" aria-live="polite"></p>' in html


def test_skjemaet_er_underside_av_mine_oppdrag(kari_klient: TestClient) -> None:
    """EXPERIENCE.md § Information Architecture: «Mine oppdrag» med aria-current="true", ingen "page"."""
    html = kari_klient.get("/oppdrag/ny").text
    for variant in ("topp", "bunn"):
        assert [(h, c) for h, c, _ in menyvalg(html, variant)] == [
            ("/", None), ("/mine-oppdrag", "true"), ("/profil", None),
        ]
    assert 'aria-current="page"' not in html


def test_skjemaet_har_ett_autofocus_pa_beskrivelsen(kari_klient: TestClient) -> None:
    html = kari_klient.get("/oppdrag/ny").text
    assert html.count("autofocus") == 1
    assert "autofocus" in attrs(html, "textarea", name="beskrivelse")
    side = les_side(html)
    assert [t for t, _ in side.tagger].count("h1") == 1
    assert side.forste_fokuserbare[2] == "Hopp til innholdet"


def test_oversikten_lenker_til_skjemaet(kari_klient: TestClient) -> None:
    """Akseptansekriterium 1: «+ Legg ut oppdrag» på oversikten fører til «Nytt oppdrag»."""
    html = kari_klient.get("/").text
    assert 'href="/oppdrag/ny"' in html
    assert kari_klient.get("/oppdrag/ny").status_code == 200


# ---------- gyldig innsending ----------


def test_gyldig_innsending_gir_303_og_kvittering(kari_klient: TestClient, db, kari) -> None:
    """FR-5, UX-DR22: rad med `apen`, 303 til detaljene, kvitteringen i fokus og tittelen som `<title>`."""
    svar = send(kari_klient)
    assert svar.status_code == 303
    oppdrag = db.scalars(select(Oppdrag)).one()
    assert svar.headers["location"] == f"/oppdrag/{oppdrag.id}"
    assert (oppdrag.status, oppdrag.kategori, oppdrag.belop) == ("apen", "snomaking", 1000)
    assert oppdrag.tidspunkt == datetime(2026, 11, 25, 6, 0, tzinfo=timezone.utc)
    assert oppdrag.oppdragsgiver_id == kari.id

    side = kari_klient.get(svar.headers["location"])
    html = side.text
    assert side.status_code == 200
    assert "<title>Måke snø i innkjørselen – Nabolagshelten</title>" in html
    assert "<h1>Måke snø i innkjørselen</h1>" in html
    kvittering = attrs(html, "div", id="kvittering")
    assert "autofocus" in kvittering and kvittering["tabindex"] == "-1"
    assert "<span>Oppdraget er lagt ut.</span>" in html
    assert html.count("autofocus") == 1
    assert html.index("<h1>") < html.index('id="kvittering"')
    # Kvitteringen vises én gang.
    assert "Oppdraget er lagt ut." not in kari_klient.get(svar.headers["location"]).text


def test_detaljene_viser_feltene_formatert(kari_klient: TestClient) -> None:
    """FR-9, UX-DR14: statusmerke med skjult «Status: », kategori, tidspunkt, sted, beløp og beskrivelse."""
    html = kari_klient.get(send(kari_klient).headers["location"]).text
    assert '<span class="skjult-tekst">Status: </span>Åpen</span>' in html
    assert 'class="statusmerke statusmerke--apen"' in html
    assert '<span class="kategorimerke">' in html and "<span>Snømåking</span>" in html
    assert "<span>I morgen kl. 07:00</span>" in html
    assert "<span>0571 Oslo</span>" in html
    assert f'<li class="pris">1{NBSP}000{NBSP}kr</li>' in html
    assert '<p class="beskrivelse">Trenger noen som kan måke snø i innkjørselen min i morgen.</p>' in html


def test_uten_betaling(kari_klient: TestClient, db) -> None:
    """FR-5: «Uten betaling» lagres som NULL; et skrevet beløp ignoreres."""
    svar = send(kari_klient, tilbud="uten", belop="50")
    assert svar.status_code == 303
    assert db.scalars(select(Oppdrag.belop)).one() is None
    assert '<li class="pris">Uten betaling</li>' in kari_klient.get(svar.headers["location"]).text


def test_eget_oppdrag_markerer_mine_oppdrag_og_tilbake_gar_dit(kari_klient: TestClient) -> None:
    """Spec 2.1: «Tilbake» peker ikke på skjemaet, men på «Mine oppdrag»."""
    url = send(kari_klient).headers["location"]
    html = kari_klient.get(url, headers={"referer": "http://testserver/oppdrag/ny"}).text
    assert [(h, c) for h, c, _ in menyvalg(html, "topp")] == [
        ("/", None), ("/mine-oppdrag", "true"), ("/profil", None),
    ]
    assert '<a class="tekstknapp" href="/mine-oppdrag">Tilbake</a>' in html
    html = kari_klient.get(url, headers={"referer": "http://testserver/mine-oppdrag"}).text
    assert '<a class="tekstknapp" href="/mine-oppdrag">Tilbake</a>' in html


def test_nytt_oppdrag_vises_under_mine_oppdrag(kari_klient: TestClient, db) -> None:
    send(kari_klient)
    oppdrag = db.scalars(select(Oppdrag)).one()
    html = kari_klient.get("/mine-oppdrag").text
    assert f'<li><a href="/oppdrag/{oppdrag.id}">Måke snø i innkjørselen</a></li>' in html
    assert "Du har ikke lagt ut noen oppdrag." not in html


def test_linjeskift_beholdes_og_teller_som_ett_tegn(kari_klient: TestClient, db) -> None:
    """AD-10: CRLF fra nettleseren lagres som LF, så telleren og serveren teller likt."""
    send(kari_klient, beskrivelse="Linje en\r\nLinje to")
    assert db.scalars(select(Oppdrag.beskrivelse)).one() == "Linje en\nLinje to"


# ---------- feil (NFR-10) ----------


def test_tom_innsending_gir_seks_feil_og_beholder_verdiene(kari_klient: TestClient, db) -> None:
    """NFR-10: «Skjemaet har 6 feil», «Feil: »-tittel, verdier og `skjema_id` beholdt, ingen rad."""
    tom = {felt: "" for felt in GYLDIG} | {"postnummer": "0571"}
    svar = send(kari_klient, skjema_id="beholdt-skjema-id-01", **tom)
    assert svar.status_code == 422
    html = svar.text
    assert "<title>Feil: Nytt oppdrag – Nabolagshelten</title>" in html
    assert "<span>Skjemaet har 6 feil</span>" in html
    lenker = re.findall(r'<li><a href="#([^"]+)">', html)
    assert lenker == ["beskrivelse", "tittel", "kategori-snomaking", "dato", "klokkeslett", "tilbud-belop"]
    assert attrs(html, "input", name="skjema_id")["value"] == "beholdt-skjema-id-01"
    assert attrs(html, "input", name="postnummer")["value"] == "0571"
    assert "autofocus" in attrs(html, "div", id="feiloppsummering")
    assert html.count("autofocus") == 1
    assert 'role="alert"' not in html
    assert antall(db) == 0
    # Lenkemålene finnes.
    for mal in lenker:
        assert f'id="{mal}"' in html, mal


def test_feltfeil_knyttes_til_feltene(kari_klient: TestClient) -> None:
    """UX-DR12: feil ved feltet med `aria-describedby` og `aria-invalid`; gruppefeil under `fieldset`."""
    html = send(kari_klient, tittel="ab", kategori="", tilbud="", dato="24.11.2026", klokkeslett="12:00").text
    tittel = attrs(html, "input", name="tittel")
    assert tittel["aria-invalid"] == "true" and tittel["aria-describedby"] == "tittel-feil"
    assert feltfeil(html, "tittel") == "Tittelen må ha minst 3 tegn."
    assert feltfeil(html, "kategori") == "Velg en kategori."
    assert feltfeil(html, "tilbud") == "Velg beløp eller uten betaling."
    assert feltfeil(html, "nar") == "Velg et nytt tidspunkt fram i tid"
    for navn, hjelp in (("dato", "dato-hjelp"), ("klokkeslett", "klokkeslett-hjelp")):
        felt = attrs(html, "input", name=navn)
        assert felt["aria-invalid"] == "true"
        assert felt["aria-describedby"] == f"{hjelp} nar-feil"
    radioer = re.findall(r'<input class="skjult-tekst" type="radio"[^>]*>', html)
    assert len(radioer) == 6
    for radio in radioer:
        assert 'aria-describedby="kategori-feil"' in radio and 'aria-invalid="true"' in radio
    for verdi in ("belop", "uten"):
        radio = attrs(html, "input", id=f"tilbud-{verdi}")
        assert radio["aria-invalid"] == "true" and radio["aria-describedby"] == "tilbud-feil"
    assert '<li><a href="#dato">Velg et nytt tidspunkt fram i tid</a></li>' in html
    # Gyldige felt er ikke merket ugyldige.
    assert "aria-invalid" not in attrs(html, "textarea", name="beskrivelse")
    gyldig = send(kari_klient, tittel="ab").text
    assert "aria-invalid" not in attrs(gyldig, "input", id="kategori-snomaking")
    assert "aria-invalid" not in attrs(gyldig, "input", id="tilbud-belop")


def test_feilene_beholder_det_brukeren_skrev(kari_klient: TestClient) -> None:
    html = send(kari_klient, tittel="ab", beskrivelse="For kort", kategori="hage", tilbud="uten",
                belop="77", dato="1.12.26", klokkeslett="0930").text
    assert ">For kort</textarea>" in html
    assert '<p class="teller" id="beskrivelse-teller">8 av 1000 tegn</p>' in html
    assert attrs(html, "input", name="tittel")["value"] == "ab"
    assert "checked" in attrs(html, "input", id="kategori-hage")
    assert "checked" in attrs(html, "input", id="tilbud-uten")
    assert attrs(html, "input", name="belop")["value"] == "77"
    assert attrs(html, "input", name="dato")["value"] == "1.12.26"
    assert attrs(html, "input", name="klokkeslett")["value"] == "0930"


def test_for_lang_beskrivelse(kari_klient: TestClient) -> None:
    html = send(kari_klient, beskrivelse="b" * 1001).text
    assert feltfeil(html, "beskrivelse") == "Beskrivelsen kan ha høyst 1000 tegn. Nå har den 1001."
    assert '<p class="teller" id="beskrivelse-teller">1001 av 1000 tegn</p>' in html


def test_sommertid_feil_ved_klokkeslett(kari_klient: TestClient) -> None:
    html = send(kari_klient, dato="28.03.2027", klokkeslett="02:30").text
    assert feltfeil(html, "klokkeslett") == (
        "Klokkeslettet finnes ikke den natten, fordi klokka stilles fram. Velg et annet klokkeslett."
    )


@pytest.mark.parametrize("belop", ["0", "10001", "1,5", "abc", ""])
def test_ugyldig_belop(kari_klient: TestClient, db, belop: str) -> None:
    svar = send(kari_klient, belop=belop)
    assert svar.status_code == 422
    assert feltfeil(svar.text, "belop") == "Skriv et beløp fra 1 til 10 000 kr, i hele kroner."
    assert attrs(svar.text, "input", name="belop")["aria-invalid"] == "true"
    assert antall(db) == 0


# ---------- dobbel innsending og skjema_id (AD-2, NFR-5) ----------


def test_dobbel_innsending_gir_en_rad(kari_klient: TestClient, db) -> None:
    """NFR-5: samme `skjema_id` to ganger gir én rad; andre svar er 303 til samme oppdrag uten kvittering."""
    csrf, skjema_id = skjemanokler(kari_klient)
    data = {"csrf_token": csrf, "skjema_id": skjema_id, **GYLDIG}
    forste = kari_klient.post("/oppdrag/ny", data=data, follow_redirects=False)
    andre = kari_klient.post("/oppdrag/ny", data=data, follow_redirects=False)
    assert forste.status_code == andre.status_code == 303
    assert forste.headers["location"] == andre.headers["location"]
    assert "kvittering=" in forste.headers.get("set-cookie", "")
    assert "kvittering=" not in andre.headers.get("set-cookie", "")
    assert antall(db) == 1


@pytest.mark.parametrize(
    "skjema_id",
    ["", "kort", "a" * 15, "a" * 65, "ugyldig skjema id!", "<script>alert(1)</script>abcdefgh", "æøå" * 6],
    ids=["tom", "kort", "15-tegn", "65-tegn", "mellomrom", "html", "ikke-ascii"],
)
def test_ugyldig_skjema_id_gir_400(kari_klient: TestClient, db, skjema_id: str) -> None:
    svar = send(kari_klient, skjema_id=skjema_id)
    assert svar.status_code == 400
    assert "<h1>Noe gikk galt. Prøv igjen om litt.</h1>" in svar.text
    assert antall(db) == 0


def test_manglende_skjema_id_gir_400(kari_klient: TestClient, db) -> None:
    csrf, _ = skjemanokler(kari_klient)
    svar = kari_klient.post("/oppdrag/ny", data={"csrf_token": csrf, **GYLDIG}, follow_redirects=False)
    assert svar.status_code == 400
    assert antall(db) == 0


# ---------- XSS (NFR-12) ----------


def test_tekst_vises_som_tekst(kari_klient: TestClient) -> None:
    """NFR-12, AD-11: HTML i tittel og beskrivelse vises escaped."""
    skadelig = "<script>alert(1)</script>"
    url = send(kari_klient, tittel=skadelig, beskrivelse=skadelig + " og mer tekst").headers["location"]
    html = kari_klient.get(url).text
    assert skadelig not in html
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html
    html = kari_klient.get("/mine-oppdrag").text
    assert skadelig not in html
    html = send(kari_klient, tittel=skadelig, beskrivelse="").text  # gjenvist med feil
    assert skadelig not in html


# ---------- detaljer og tilgang (FR-9, AD-16) ----------


def test_detaljer_som_ikke_finnes_gir_404(kari_klient: TestClient) -> None:
    for sti in ("/oppdrag/999999", "/oppdrag/0", f"/oppdrag/{2**31}", "/oppdrag/99999999999999999999"):
        svar = kari_klient.get(sti)
        assert svar.status_code == 404, sti
        assert "<h1>Fant ikke siden</h1>" in svar.text


def test_andres_avbrutte_gir_samme_404(kari_klient: TestClient, lag_oppdrag) -> None:
    """FR-9: et oppdrag brukeren ikke har tilgang til, ser ut som et som ikke finnes."""
    avbrutt = lag_oppdrag(status="avbrutt", tittel="Hemmelig avbrutt")
    svar = kari_klient.get(f"/oppdrag/{avbrutt.id}")
    finnes_ikke = kari_klient.get("/oppdrag/999999")
    assert svar.status_code == finnes_ikke.status_code == 404
    assert "Hemmelig avbrutt" not in svar.text
    fjern_csrf = re.compile(r'value="[^"]*"')
    assert fjern_csrf.sub("", svar.text) == fjern_csrf.sub("", finnes_ikke.text)


def test_andres_apne_oppdrag_markerer_oppdrag(kari_klient: TestClient, lag_oppdrag) -> None:
    """FR-9: andre innloggede ser åpne oppdrag; menyvalget er «Oppdrag» med aria-current="true"."""
    oppdrag = lag_oppdrag(tittel="Ola sitt oppdrag")
    svar = kari_klient.get(f"/oppdrag/{oppdrag.id}")
    assert svar.status_code == 200
    assert "<h1>Ola sitt oppdrag</h1>" in svar.text
    for variant in ("topp", "bunn"):
        assert [(h, c) for h, c, _ in menyvalg(svar.text, variant)] == [
            ("/", "true"), ("/mine-oppdrag", None), ("/profil", None),
        ]
    assert 'aria-current="page"' not in svar.text


def test_eget_avbrutt_oppdrag_kan_ses(kari_klient: TestClient, kari, lag_oppdrag) -> None:
    oppdrag = lag_oppdrag(oppdragsgiver=kari, status="avbrutt")
    svar = kari_klient.get(f"/oppdrag/{oppdrag.id}")
    assert svar.status_code == 200
    assert '<span class="skjult-tekst">Status: </span>Avbrutt</span>' in svar.text


def test_detaljene_har_ingen_personopplysninger(klient: TestClient, kari, lag_bruker, logg_inn_som) -> None:
    """AD-16, NFR-9: verken eier eller andre ser telefon, e-post eller fødselsdato i detaljene."""
    logg_inn_som(klient, kari)
    url = send(klient).headers["location"]
    sjekk = ["91234567", "912 34 567", "kari.n@eksempel.no", "kari.n&#64;", "1954-05-03", "03.05.1954",
             "3. mai 1954"]
    html = klient.get(url).text
    for verdi in sjekk:
        assert verdi not in html, verdi
    klient.cookies.clear()
    logg_inn_som(klient, lag_bruker())
    html = klient.get(url).text
    for verdi in sjekk:
        assert verdi not in html, verdi
    assert "Kari Nordmann" not in html  # oppdragsgiverblokken kommer i 2.3
