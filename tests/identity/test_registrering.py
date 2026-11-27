"""Registrering over HTTP: radene i I/O-matrisen i spec 1.4 (FR-1, NFR-5, NFR-9, NFR-10).

Også felttyper, `autocomplete`, personvernteksten, at alle feilene vises
samtidig, at passordet er tomt etter feil, sidetittel, fokus, og at kontoen kan
logge inn og ut etter registrering (UX-DR12, UX-DR13, UX-DR22, UX-DR27).
"""

from __future__ import annotations

import logging
import re
from datetime import date, datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, inspect, select
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.identity.models import Bruker, Sesjon
from app.identity.service import hash_sesjonsnokkel

from ..core.test_render import les_side

# Tirsdag 24. november 2026 kl. 13 i Oslo.
T0 = datetime(2026, 11, 24, 12, 0, tzinfo=timezone.utc)

GYLDIG = {
    "navn": "Kari Nordmann",
    "epost": " Kari@X.no ",
    "passord": "hemmelig-1",
    "telefon": "+47 912 34 567",
    "postnummer": "0571",
    "fodselsdato": "03.05.1954",
}

FELTREKKEFOLGE = ["navn", "epost", "passord", "telefon", "postnummer", "fodselsdato"]

PERSONVERN = [
    "Vi lagrer det du skriver her. Passordet lagres slik at ingen kan lese det.",
    "Navnet, postnummeret og profilen din vises for alle som er logget inn.",
    "Telefonnummeret ditt vises bare for den andre i et oppdrag, når en hjelper er valgt. "
    "E-post og fødselsdato vises ikke for andre.",
    "Trykker du «Få forslag» når du legger ut et oppdrag, sendes beskrivelsen til en ekstern KI-tjeneste.",
    "Du kan slette kontoen din når du vil, under Profil.",
]


@pytest.fixture(autouse=True)
def _klokke(sett_na) -> None:
    sett_na(T0)


def csrf(klient: TestClient) -> str:
    """CSRF-nøkkelen fra registreringssiden, eller fra profilen når klienten er innlogget."""
    html = klient.get("/registrer").text
    if 'name="csrf_token"' not in html:
        html = klient.get("/profil").text
    return re.search(r'name="csrf_token" value="([^"]+)"', html).group(1)


def send(klient: TestClient, **endringer: str):
    data = {"csrf_token": csrf(klient), **GYLDIG, **endringer}
    return klient.post("/registrer", data=data, follow_redirects=False)


def antall_brukere(db: Session) -> int:
    return db.scalar(select(func.count()).select_from(Bruker))


def felt(html: str, navn: str) -> dict:
    """Attributtene til `<input name=navn>`."""
    return next(a for t, a in les_side(html).tagger if t == "input" and a.get("name") == navn)


def feltfeil(html: str, navn: str) -> str | None:
    treff = re.search(rf'<p class="feltfeil" id="{navn}-feil">.*?<span>([^<]*)</span>', html, re.S)
    return treff.group(1) if treff else None


def oppsummering(html: str) -> list[tuple[str, str]]:
    blokk = re.search(r'<div class="melding melding--feil".*?</div>', html, re.S)
    if blokk is None:
        return []
    return re.findall(r'<a href="#([a-z]+)">([^<]*)</a>', blokk.group(0))


# ---------- tomt skjema ----------


def test_skjemaet_har_feltene_i_rekkefolge_med_type_og_autocomplete(klient: TestClient) -> None:
    """FR-1, UX-DR12: seks felt i rekkefølgen fra mockupen, med felttype og autocomplete."""
    svar = klient.get("/registrer")
    assert svar.status_code == 200
    html = svar.text
    inputs = [a for t, a in les_side(html).tagger if t == "input" and a.get("type") != "hidden"]
    assert [a["name"] for a in inputs] == FELTREKKEFOLGE
    forventet = {
        "navn": ("text", "name"),
        "epost": ("email", "email"),
        "passord": ("password", "new-password"),
        "telefon": ("tel", "tel"),
        "postnummer": ("text", "postal-code"),
        "fodselsdato": ("text", "bday"),
    }
    for a in inputs:
        assert (a["type"], a["autocomplete"]) == forventet[a["name"]], a["name"]
        assert a["id"] == a["name"]  # lenkene i feiloppsummeringen går til id-en
        assert "required" in a
    assert felt(html, "postnummer")["inputmode"] == "numeric"
    assert "novalidate" in re.search(r"<form[^>]*>", html).group(0)
    etiketter = re.findall(r'<label for="([a-z]+)">([^<]*)</label>', html)
    assert etiketter == [
        ("navn", "Navn"),
        ("epost", "E-post"),
        ("passord", "Passord"),
        ("telefon", "Telefonnummer"),
        ("postnummer", "Postnummer"),
        ("fodselsdato", "Fødselsdato"),
    ]


def test_hjelpetekster_og_vis_passord(klient: TestClient) -> None:
    """UX-DR13: hjelpetekstene er knyttet til feltene; «Vis passord» er skjult uten JS."""
    html = klient.get("/registrer").text
    assert '<p class="hjelpetekst" id="passord-hjelp">8–64 tegn</p>' in html
    assert (
        '<p class="hjelpetekst" id="fodselsdato-hjelp">dd.mm.åååå, for eksempel 03.05.1954</p>' in html
    )
    assert felt(html, "passord")["aria-describedby"] == "passord-hjelp"
    assert felt(html, "fodselsdato")["aria-describedby"] == "fodselsdato-hjelp"
    assert "Skriv passordet på nytt." not in html
    knapp = re.search(r"<button[^>]*data-vis-passord[^>]*>([^<]*)</button>", html)
    assert knapp and knapp.group(1) == "Vis passord"
    for attributt in ('type="button"', 'aria-pressed="false"', 'aria-controls="passord"', "hidden"):
        assert attributt in knapp.group(0), attributt


def test_poststed_er_knyttet_til_postnummerfeltet(klient: TestClient) -> None:
    """UX-DR13: `<span id="postnummer-sted">` er tomt før innsending og fylles av poststed.js."""
    html = klient.get("/registrer").text
    postnummer = felt(html, "postnummer")
    assert postnummer["aria-describedby"] == "postnummer-sted"
    assert postnummer["data-poststed"] == "postnummer-sted"
    assert postnummer["data-postnumre"] == "/static/postnumre.json"
    assert '<span id="postnummer-sted" aria-live="polite"></span>' in html
    assert "/static/js/poststed.js" in html
    assert klient.get("/static/postnumre.json").status_code == 200
    assert klient.get("/static/js/poststed.js").status_code == 200


def test_personvern_over_knappen(klient: TestClient) -> None:
    """FR-1: personverntekst med fem punkter rett over «Opprett konto»."""
    html = klient.get("/registrer").text
    seksjon = re.search(r'<section class="personvern" aria-labelledby="([^"]+)">(.*?)</section>', html, re.S)
    assert seksjon
    assert f'<h2 class="personvern__overskrift" id="{seksjon.group(1)}">Personvern</h2>' in seksjon.group(2)
    assert re.findall(r"<li>([^<]*)</li>", seksjon.group(2)) == PERSONVERN
    knapp = '<button class="knapp knapp--primar" type="submit">Opprett konto</button>'
    assert html.index("</section>") < html.index(knapp)


def test_lenke_til_innlogging_nederst(klient: TestClient) -> None:
    html = klient.get("/registrer").text
    blokk = re.search(r'<div class="annen-side">(.*?)</div>', html, re.S).group(1)
    assert "<p>Har du konto fra før?</p>" in blokk
    assert '<a class="tekstknapp" href="/logg-inn">Logg inn</a>' in blokk
    assert html.index("</form>") < html.index('<div class="annen-side">')


def test_sideramme_tittel_og_fokus(klient: TestClient) -> None:
    """UX-DR2, UX-DR27: «Registrering – Nabolagshelten», én h1, ingen meny, ett autofocus på Navn."""
    html = klient.get("/registrer").text
    assert "<title>Registrering – Nabolagshelten</title>" in html
    side = les_side(html)
    assert [t for t, _ in side.tagger].count("h1") == 1
    assert "<h1>Registrering</h1>" in html
    assert "<nav" not in html
    tag, attrs, tekst = side.forste_fokuserbare
    assert (tag, attrs.get("href"), tekst) == ("a", "#innhold", "Hopp til innholdet")
    assert html.count("autofocus") == 1
    assert "autofocus" in felt(html, "navn")


def test_ingen_om_meg_eller_adresse(klient: TestClient) -> None:
    """FR-1, NFR-9: registreringen spør ikke om «om meg» eller adresse."""
    html = klient.get("/registrer").text.lower()
    for ord_ in ("om meg", "adresse</label>", 'name="adresse"', "<textarea"):
        assert ord_ not in html, ord_


def test_innlogget_sendes_til_oversikten(klient: TestClient, lag_bruker, logg_inn_som) -> None:
    logg_inn_som(klient, lag_bruker())
    svar = klient.get("/registrer", follow_redirects=False)
    assert svar.status_code == 303
    assert svar.headers["location"] == "/"


# ---------- gyldig registrering ----------


def test_gyldig_registrering_logger_inn(klient: TestClient, db: Session) -> None:
    """FR-1: rad med normaliserte verdier og hash, sesjonscookie og 303 til oversikten."""
    svar = send(klient)
    assert svar.status_code == 303
    assert svar.headers["location"] == "/"
    cookie = next(c for c in svar.headers.get_list("set-cookie") if c.startswith("sesjon="))
    for attributt in ("HttpOnly", "SameSite=lax", "Path=/", "Max-Age=604800"):
        assert attributt.lower() in cookie.lower(), attributt
    nokkel = re.match(r"sesjon=([^;]+)", cookie).group(1)

    bruker = db.scalars(select(Bruker)).one()
    assert (bruker.navn, bruker.epost, bruker.telefon, bruker.postnummer, bruker.fodselsdato) == (
        "Kari Nordmann",
        "kari@x.no",
        "91234567",
        "0571",
        date(1954, 5, 3),
    )
    assert bruker.passord_hash and GYLDIG["passord"] not in bruker.passord_hash
    sesjon = db.scalars(select(Sesjon)).one()
    assert sesjon.nokkel == hash_sesjonsnokkel(nokkel)
    assert sesjon.utloper == T0 + timedelta(days=7)

    oversikt = klient.get("/")
    assert oversikt.status_code == 200
    assert "Ledige oppdrag i 0571 Oslo" in oversikt.text


def test_kontoen_kan_logge_ut_og_inn_igjen(klient: TestClient) -> None:
    """FR-1, FR-2: etter registrering virker utlogging og innlogging med samme e-post og passord."""
    assert send(klient).status_code == 303
    utlogging = klient.post("/logg-ut", data={"csrf_token": csrf(klient)}, follow_redirects=False)
    assert utlogging.status_code == 303
    assert klient.get("/", follow_redirects=False).status_code == 303

    html = klient.get("/logg-inn").text
    token = re.search(r'name="csrf_token" value="([^"]+)"', html).group(1)
    innlogging = klient.post(
        "/logg-inn",
        data={"csrf_token": token, "epost": "KARI@x.no", "passord": GYLDIG["passord"]},
        follow_redirects=False,
    )
    assert innlogging.status_code == 303
    assert klient.get("/profil").status_code == 200


def test_innlogget_post_sendes_til_oversikten(
    klient: TestClient, db: Session, lag_bruker, logg_inn_som
) -> None:
    """Innloggede sendes til `/`: ingen ny konto, og den gamle sesjonen er urørt."""
    gammel = logg_inn_som(klient, lag_bruker())
    svar = send(klient, epost="ny@x.no")
    assert svar.status_code == 303
    assert svar.headers["location"] == "/"
    assert not any(c.startswith("sesjon=") for c in svar.headers.get_list("set-cookie"))
    assert antall_brukere(db) == 1
    assert set(db.scalars(select(Sesjon.nokkel))) == {hash_sesjonsnokkel(gammel)}


def test_sesjonscookien_er_secure_i_produksjon(sesjonsfabrikk) -> None:
    """AD-4: registreringen setter `Secure` på sesjonscookien i produksjon, som innloggingen."""
    from app import lag_app

    settings = Settings(
        _env_file=None, app_env="production", secret_key="x" * 32,
        database_url="postgresql+psycopg://u@localhost/d",
    )
    app = lag_app(settings=settings)
    app.state.sesjonsfabrikk = sesjonsfabrikk
    with TestClient(app, base_url="https://testserver") as klient:
        token = re.search(r'name="csrf_token" value="([^"]+)"', klient.get("/registrer").text).group(1)
        svar = klient.post("/registrer", data={"csrf_token": token, **GYLDIG}, follow_redirects=False)
    assert svar.status_code == 303
    (cookie,) = [c for c in svar.headers.get_list("set-cookie") if c.startswith("sesjon=")]
    assert "secure" in cookie.lower()


def test_registrering_logger_ikke_personopplysninger(klient: TestClient, caplog) -> None:
    """AR-30: navn, e-post, telefon, fødselsdato og passord havner aldri i loggen."""
    caplog.set_level(logging.DEBUG)
    send(klient)
    send(klient, navn="", telefon="12")
    for post in caplog.records:
        tekst = post.getMessage()
        for verdi in (
            GYLDIG["navn"],
            "kari@x.no",
            "Kari@X.no",
            "912 34 567",
            "91234567",
            GYLDIG["fodselsdato"],
            "1954-05-03",
            GYLDIG["passord"],
        ):
            assert verdi not in tekst, post.name


def test_bruker_har_bare_tillatte_kolonner(db: Session) -> None:
    """NFR-9: `bruker` har bare navn, e-post, passord-hash, telefon, postnummer, fødselsdato og tidspunkter."""
    kolonner = {k["name"] for k in inspect(db.connection()).get_columns("bruker")}
    assert kolonner == {
        "id",
        "navn",
        "epost",
        "passord_hash",
        "telefon",
        "postnummer",
        "fodselsdato",
        "opprettet",
        "slettet_tidspunkt",
    }


# ---------- feil i ett felt (I/O-matrisen) ----------


@pytest.mark.parametrize(
    ("endringer", "felt_", "melding"),
    [
        ({"navn": ""}, "navn", "Skriv navnet ditt."),
        ({"navn": "   "}, "navn", "Skriv navnet ditt."),
        ({"navn": "K" * 81}, "navn", "Navnet kan ha høyst 80 tegn."),
        ({"epost": ""}, "epost", "Skriv e-postadressen din."),
        ({"epost": "kari@x"}, "epost", "Skriv e-postadressen som navn@eksempel.no."),
        ({"passord": ""}, "passord", "Skriv et passord."),
        ({"passord": "a" * 7}, "passord", "Passordet må ha 8–64 tegn."),
        ({"passord": "a" * 65}, "passord", "Passordet må ha 8–64 tegn."),
        ({"telefon": "9123456"}, "telefon", "Skriv et telefonnummer med åtte siffer, for eksempel 912 34 567."),
        ({"telefon": "+46 91234567"}, "telefon", "Skriv et telefonnummer med åtte siffer, for eksempel 912 34 567."),
        ({"telefon": "912-34-567"}, "telefon", "Skriv et telefonnummer med åtte siffer, for eksempel 912 34 567."),
        ({"postnummer": "9999"}, "postnummer", "Finner ikke postnummeret. Sjekk at det har fire siffer."),
        ({"postnummer": "0001"}, "postnummer", "Finner ikke postnummeret. Sjekk at det har fire siffer."),
        ({"postnummer": "57"}, "postnummer", "Finner ikke postnummeret. Sjekk at det har fire siffer."),
        ({"fodselsdato": "25.11.2008"}, "fodselsdato", "Du må være minst 18 år for å bruke Nabolagshelten."),
        ({"fodselsdato": "25.11.2026"}, "fodselsdato", "Sjekk fødselsdatoen."),
        ({"fodselsdato": "23.11.1906"}, "fodselsdato", "Sjekk fødselsdatoen."),
        ({"fodselsdato": "31.02.1990"}, "fodselsdato", "Sjekk fødselsdatoen."),
        (
            {"fodselsdato": "1954.05.03"},
            "fodselsdato",
            "Skriv fødselsdatoen som dd.mm.åååå, for eksempel 03.05.1954.",
        ),
        ({"fodselsdato": "abc"}, "fodselsdato", "Skriv fødselsdatoen som dd.mm.åååå, for eksempel 03.05.1954."),
    ],
)
def test_feil_i_ett_felt(klient: TestClient, db: Session, endringer: dict, felt_: str, melding: str) -> None:
    """NFR-10: 422, feilen ved feltet og i oppsummeringen, feltet er merket ugyldig, ingen rad."""
    svar = send(klient, **endringer)
    assert svar.status_code == 422
    html = svar.text
    assert oppsummering(html) == [(felt_, melding)]
    assert feltfeil(html, felt_) == melding
    attrs = felt(html, felt_)
    assert attrs.get("aria-invalid") == "true"
    assert f"{felt_}-feil" in attrs["aria-describedby"].split()
    assert antall_brukere(db) == 0
    assert not any(c.startswith("sesjon=") for c in svar.headers.get_list("set-cookie"))


@pytest.mark.parametrize(
    "endringer",
    [
        {"navn": "K"},
        {"navn": "K" * 80},
        {"passord": "a" * 8},
        {"passord": "a" * 64},
        {"telefon": "91234567"},
        {"telefon": "912 34 567"},
        {"telefon": "0047 91234567"},
        {"fodselsdato": "24.11.2008"},  # fyller 18 i dag
        {"fodselsdato": "24.11.1906"},  # i dag minus 120 år
        {"fodselsdato": "3.5.54"},
        {"fodselsdato": "03-05-1954"},
    ],
)
def test_grenseverdier_som_godtas(klient: TestClient, db: Session, endringer: dict) -> None:
    assert send(klient, **endringer).status_code == 303
    assert antall_brukere(db) == 1


@pytest.mark.parametrize(
    ("i_dag", "status"),
    [
        (datetime(2026, 2, 28, 12, 0, tzinfo=timezone.utc), 422),
        (datetime(2026, 3, 1, 12, 0, tzinfo=timezone.utc), 303),
    ],
)
def test_fodt_29_februar(klient: TestClient, sett_na, i_dag: datetime, status: int) -> None:
    """Født 29.02.2008: avvist 28.02.2026, godtatt 01.03.2026."""
    sett_na(i_dag)
    assert send(klient, fodselsdato="29.02.2008").status_code == status


def test_epost_i_bruk(klient: TestClient, db: Session, lag_bruker) -> None:
    """FR-1: `KARI@x.no` finnes som `kari@x.no`; 422 og ingen ny rad."""
    lag_bruker(epost="kari@x.no")
    svar = send(klient, epost="KARI@x.no")
    assert svar.status_code == 422
    assert feltfeil(svar.text, "epost") == "Det finnes allerede en konto med denne e-posten."
    assert antall_brukere(db) == 1


# ---------- flere feil ----------


def test_flere_feil_vises_samtidig(klient: TestClient, db: Session, lag_bruker) -> None:
    """NFR-10: tomt navn + e-post i bruk + under 18 gir «Skjemaet har 3 feil», verdiene beholdes
    og passordet er tomt."""
    lag_bruker(epost="kari@x.no")
    svar = send(klient, navn="", epost="kari@x.no", fodselsdato="01.01.2015")
    assert svar.status_code == 422
    html = svar.text
    assert "<title>Feil: Registrering – Nabolagshelten</title>" in html
    assert "<span>Skjemaet har 3 feil</span>" in html
    assert oppsummering(html) == [
        ("navn", "Skriv navnet ditt."),
        ("epost", "Det finnes allerede en konto med denne e-posten."),
        ("fodselsdato", "Du må være minst 18 år for å bruke Nabolagshelten."),
    ]
    # Verdiene beholdes, unntatt passordet.
    assert felt(html, "epost")["value"] == "kari@x.no"
    assert felt(html, "telefon")["value"] == GYLDIG["telefon"]
    assert felt(html, "postnummer")["value"] == "0571"
    assert felt(html, "fodselsdato")["value"] == "01.01.2015"
    assert "value" not in felt(html, "passord")
    assert GYLDIG["passord"] not in html
    # Passordet hadde ingen feil, men må skrives på nytt.
    assert '<p class="hjelpetekst" id="passord-pa-nytt">Skriv passordet på nytt.</p>' in html
    assert felt(html, "passord")["aria-describedby"] == "passord-hjelp passord-pa-nytt"
    assert "aria-invalid" not in felt(html, "passord")
    # Fødselsdatoen har både hjelpetekst og feil.
    assert felt(html, "fodselsdato")["aria-describedby"] == "fodselsdato-hjelp fodselsdato-feil"
    assert antall_brukere(db) == 1


def test_feil_gir_fokus_pa_feiloppsummeringen(klient: TestClient) -> None:
    """UX-DR27: oppsummeringen rett etter h1 får fokus, uten role, og er eneste autofocus."""
    html = send(klient, navn="").text
    assert html.count("autofocus") == 1
    oppsummeringen = re.search(r'<div class="melding melding--feil"[^>]*>', html).group(0)
    assert 'id="feiloppsummering"' in oppsummeringen
    assert 'tabindex="-1"' in oppsummeringen and "autofocus" in oppsummeringen
    assert "role=" not in oppsummeringen
    assert re.search(r"<h1>Registrering</h1>\s*<div class=\"melding melding--feil\"", html)


def test_passordfeil_gir_ikke_skriv_pa_nytt(klient: TestClient) -> None:
    html = send(klient, passord="kort").text
    assert "Skriv passordet på nytt." not in html
    assert felt(html, "passord")["aria-describedby"] == "passord-hjelp passord-feil"


def test_poststed_vises_etter_innsending_uten_js(klient: TestClient) -> None:
    """UX-DR13: med feil i et annet felt vises poststedet for et gyldig postnummer."""
    html = send(klient, navn="", postnummer="5006").text
    assert '<span id="postnummer-sted" aria-live="polite">Bergen</span>' in html
    assert felt(html, "postnummer")["aria-describedby"] == "postnummer-sted"


def test_ukjent_postnummer_gir_ikke_poststed(klient: TestClient) -> None:
    html = send(klient, postnummer="9999").text
    assert '<span id="postnummer-sted" aria-live="polite"></span>' in html
    assert felt(html, "postnummer")["aria-describedby"] == "postnummer-sted postnummer-feil"


def test_verdier_med_html_vises_som_tekst(klient: TestClient) -> None:
    """NFR-12: det brukeren skrev, escapes når skjemaet vises igjen."""
    html = send(klient, navn='<script>alert("x")</script>', epost="<b>x").text
    assert "<script>alert" not in html
    assert "&lt;script&gt;" in html


def test_post_uten_csrf_avvises(klient: TestClient, db: Session) -> None:
    """AD-5: også registreringen krever CSRF-nøkkelen."""
    klient.get("/registrer")
    svar = klient.post("/registrer", data=GYLDIG, follow_redirects=False)
    assert svar.status_code == 403
    assert antall_brukere(db) == 0


# ---------- `neste` gjennom registreringen (retro T-2, FR-1, FR-2, AD-4) ----------


def lenke_href(html: str, tekst: str) -> str:
    return re.search(rf'<a class="tekstknapp" href="([^"]+)">{tekst}</a>', html).group(1)


def skjult_neste(html: str) -> str:
    return felt(html, "neste")["value"]


def test_registrer_deg_baerer_neste(klient: TestClient) -> None:
    """T-2: «Registrer deg» har `?neste=` når innloggingen har en annen `neste` enn `/`."""
    assert lenke_href(klient.get("/logg-inn?neste=/oppdrag/5").text, "Registrer deg") == (
        "/registrer?neste=%2Foppdrag%2F5"
    )
    assert lenke_href(klient.get("/logg-inn").text, "Registrer deg") == "/registrer"


def test_registreringen_har_neste_som_skjult_felt_og_logg_inn_baerer_den(klient: TestClient) -> None:
    html = klient.get("/registrer?neste=/oppdrag/5").text
    assert skjult_neste(html) == "/oppdrag/5"
    assert lenke_href(html, "Logg inn") == "/logg-inn?neste=%2Foppdrag%2F5"
    html = klient.get("/registrer").text
    assert skjult_neste(html) == "/"
    assert lenke_href(html, "Logg inn") == "/logg-inn"


def test_neste_beholdes_ved_422(klient: TestClient) -> None:
    svar = send(klient, navn="", neste="/oppdrag/5")
    assert svar.status_code == 422
    assert skjult_neste(svar.text) == "/oppdrag/5"
    assert lenke_href(svar.text, "Logg inn") == "/logg-inn?neste=%2Foppdrag%2F5"


def test_vellykket_registrering_sender_til_neste(klient: TestClient, db: Session) -> None:
    """T-2: 303 til `trygg_neste(neste)`, og `neste` blir ikke et registreringsfelt."""
    svar = send(klient, neste="/oppdrag/5")
    assert svar.status_code == 303
    assert svar.headers["location"] == "/oppdrag/5"
    assert antall_brukere(db) == 1


@pytest.mark.parametrize("neste", ["//evil.no", "https://evil.no", "/logg-ut", "/\\evil.no", ""])
def test_ugyldig_neste_gir_oversikten(klient: TestClient, neste: str) -> None:
    assert skjult_neste(klient.get("/registrer", params={"neste": neste}).text) == "/"
    svar = send(klient, neste=neste)
    assert svar.status_code == 303
    assert svar.headers["location"] == "/"


def test_delt_lenke_gjennom_registrer_deg(klient: TestClient, lag_bruker, lag_oppdrag) -> None:
    """Akseptansekriteriet fra T-2: delt lenke → innlogging → «Registrer deg» → registrering → lenken."""
    oppdrag = lag_oppdrag(oppdragsgiver=lag_bruker(epost="eier@x.no"))
    sti = f"/oppdrag/{oppdrag.id}"
    innlogging = klient.get(sti, follow_redirects=False).headers["location"]
    registrering = lenke_href(klient.get(innlogging).text, "Registrer deg")
    html = klient.get(registrering).text
    assert skjult_neste(html) == sti
    token = re.search(r'name="csrf_token" value="([^"]+)"', html).group(1)
    svar = klient.post("/registrer", data={"csrf_token": token, **GYLDIG, "neste": sti}, follow_redirects=False)
    assert svar.status_code == 303
    assert svar.headers["location"] == sti
    assert klient.get(sti).status_code == 200


def test_registrering_med_neste_sletter_mislykkede_forsok(klient: TestClient, db: Session) -> None:
    """Invariant 1.4 (T-6): registreringen sletter `innloggingsforsok` for e-posten, også med `neste`."""
    from app.identity.models import Innloggingsforsok

    db.add(Innloggingsforsok(epost="kari@x.no", tidspunkt=T0))
    db.commit()
    assert send(klient, neste="/oppdrag/5").status_code == 303
    assert db.scalar(select(func.count()).select_from(Innloggingsforsok)) == 0


def test_innlogget_med_neste_sendes_fortsatt_til_oversikten(klient: TestClient, lag_bruker, logg_inn_som) -> None:
    """Invariant 1.4 (T-6): innlogget GET og POST til `/registrer` gir 303 til `/`, uansett `neste`."""
    logg_inn_som(klient, lag_bruker())
    assert klient.get("/registrer?neste=/oppdrag/5", follow_redirects=False).headers["location"] == "/"
    assert send(klient, epost="ny@x.no", neste="/oppdrag/5").headers["location"] == "/"
