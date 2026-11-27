"""Oversikten og detaljene over HTTP: radene i I/O-matrisen i spec 2.3.

FR-9, FR-10, FR-11, FR-16, AD-16, NFR-12, UX-DR5, UX-DR21, UX-DR24, UX-DR25, retro R7.
Klokka står fast på tirsdag 24.11.2026 kl. 13:00 norsk tid, og databasen har
testbrukerne og eksempeloppdragene fra seed. Ola bor i 0571 og ser fire oppdrag.
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from urllib.parse import parse_qs, urlsplit

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import seed
from app.core.sesjon import SESJON_COOKIE
from app.identity.models import Bruker
from app.oppdrag.models import Oppdrag

from ..core.test_render import les_side

# Tirsdag 24. november 2026 kl. 13 i Oslo (FAST_KLOKKE i T1).
T0 = datetime(2026, 11, 24, 12, 0, tzinfo=timezone.utc)

OLAS_FIRE = [
    "Måke snø i innkjørselen",
    "Mate katten i helgen",
    "Raking av løv i hagen",
    "Hjelp med nytt nettbrett",
]
SOFIES_TRE = ["Handle og bære opp varer", "Sette opp skriver", "Klippe hekken"]
POSTNUMMER_UTEN_OPPDRAG = "0150"  # Oslo, ingen eksempeloppdrag


@pytest.fixture(autouse=True)
def eksempeldata(db: Session, sett_na) -> None:
    sett_na(T0)
    seed.last_eksempeldata(db)
    db.commit()


def hent_testbruker(db: Session, epost: str) -> Bruker:
    return db.scalars(select(Bruker).where(Bruker.epost == epost)).one()


def oppdrag_med_tittel(db: Session, tittel: str) -> Oppdrag:
    return db.scalars(select(Oppdrag).where(Oppdrag.tittel == tittel)).one()


@pytest.fixture
def som(klient: TestClient, db: Session, logg_inn_som):
    """`som("ola")` logger inn testbrukeren og gir klienten."""

    def _som(navn: str) -> TestClient:
        klient.cookies.clear()
        logg_inn_som(klient, hent_testbruker(db, f"{navn}@eksempel.no"))
        return klient

    return _som


# ---------- hjelpere for HTML ----------


def kort(html: str) -> list[str]:
    """Titlene på kortene i rekkefølge, fra lenken i `h2`."""
    return re.findall(r'<h2 class="kort__tittel"><a class="kort__lenke" href="/oppdrag/\d+">([^<]*)</a></h2>', html)


def kategorilenker(html: str) -> list[dict]:
    """Attributtene og teksten til hver lenke i kategorifilteret."""
    gruppe = re.search(r'<div class="kategorifilter__valg">(.*?)</div>', html, re.S)
    assert gruppe, "Mangler kategorifilteret"
    lenker = []
    for attrs, innhold in re.findall(r"<a ([^>]*)>(.*?)</a>", gruppe.group(1), re.S):
        a = dict(re.findall(r'([a-z-]+)="([^"]*)"', attrs))
        a["autofocus"] = " autofocus" in f" {attrs}"
        a["tekst"] = re.sub(r"<[^>]+>", "", innhold).strip()
        lenker.append(a)
    return lenker


def lenke(html: str, tekst: str) -> dict:
    return next(a for a in kategorilenker(html) if a["tekst"] == tekst)


def postnummerfelt(html: str) -> dict:
    return next(a for t, a in les_side(html).tagger if t == "input" and a.get("name") == "postnummer")


def sporring(href: str) -> dict[str, list[str]]:
    return parse_qs(urlsplit(href.replace("&amp;", "&")).query, keep_blank_values=True)


def antallslinje(html: str) -> str | None:
    treff = re.search(r'<p class="antallslinje" id="antallslinje">([^<]*)</p>', html)
    return treff.group(1) if treff else None


def tittel(html: str) -> str:
    return re.search(r"<title>([^<]*)</title>", html).group(1)


# ---------- eget postnummer (FR-10) ----------


def test_eget_postnummer_viser_fire_oppdrag_i_rekkefolge(som) -> None:
    """FR-8, FR-10: åpne, ikke passert, i eget postnummer, uten egne, sortert etter tidspunkt.

    Ikke vist: Karis utgåtte, avbrutte og utførte, og oppdragene i 0572 og 5006.
    «Alle» er valgt uten autofocus, og siden har ingen autofocus.
    """
    svar = som("ola").get("/")
    html = svar.text
    assert svar.status_code == 200
    assert "<h1>Ledige oppdrag i 0571 Oslo</h1>" in html
    assert tittel(html) == "Ledige oppdrag i 0571 Oslo – Nabolagshelten"
    assert antallslinje(html) == "4 ledige oppdrag i 0571 Oslo"
    assert kort(html) == OLAS_FIRE
    for skjult in ("Bære ved opp til tredje etasje", "Lufte hunden mens jeg er bortreist",
                   "Bytte lyspære i taket", "Flytte sofa ned i kjelleren", "Klippe hekken"):
        assert skjult not in html, skjult
    alle = lenke(html, "Alle")
    assert alle["aria-current"] == "true" and alle["aria-describedby"] == "antallslinje"
    assert not alle["autofocus"]
    assert "autofocus" not in html


def test_egne_oppdrag_vises_ikke(som) -> None:
    """FR-10: Kari ser bare Noras oppdrag i 0571, ikke sine egne."""
    html = som("kari").get("/").text
    assert kort(html) == ["Mate katten i helgen"]
    assert antallslinje(html) == "1 ledig oppdrag i 0571 Oslo"


def test_kortet(som, db: Session) -> None:
    """UX-DR5: `li` med kategorimerke, `h2` med én lenke (tittelen), tid, sted og pris, ingen knapper."""
    html = som("ola").get("/").text
    assert '<ul class="kortliste">' in html
    elementer = re.findall(r'<li>\s*(<div class="kort kort--lenke">.*?<p class="pris">[^<]*</p>\s*</div>)\s*</li>',
                           html, re.S)
    assert len(elementer) == 4
    maake = elementer[0]
    oppdrag = oppdrag_med_tittel(db, "Måke snø i innkjørselen")
    assert re.findall(r"<a [^>]*>", maake) == [f'<a class="kort__lenke" href="/oppdrag/{oppdrag.id}">']
    assert "<button" not in maake
    assert maake.index('class="kategorimerke"') < maake.index("<h2")
    assert "<span>Snømåking</span>" in maake
    assert "I morgen kl. 09:00" in maake
    assert "0571 Oslo" in maake
    assert "200 kr" in maake
    assert "Uten betaling" in elementer[3]  # «Hjelp med nytt nettbrett»


# ---------- kategori (FR-11, UX-DR24) ----------


def test_kategori_hage(som) -> None:
    """FR-11: bare Hage, antallslinja og tittelen med kategori, og fokus på «Hage»."""
    html = som("ola").get("/?kategori=hage").text
    assert kort(html) == ["Raking av løv i hagen"]
    assert antallslinje(html) == "1 ledig oppdrag i Hage i 0571 Oslo"
    assert tittel(html) == "Hage – Ledige oppdrag i 0571 Oslo – Nabolagshelten"
    hage = lenke(html, "Hage")
    assert hage["aria-current"] == "true"
    assert hage["autofocus"]
    assert hage["aria-describedby"] == "antallslinje"
    assert [a["tekst"] for a in kategorilenker(html) if "aria-current" in a] == ["Hage"]
    assert html.count("autofocus") == 1


@pytest.mark.parametrize("verdi", ["alle", "xyz", ""])
def test_alle_og_ukjent_kategori(som, verdi: str) -> None:
    """FR-11: `alle` og en ukjent kode gir alle kategorier, med fokus på «Alle»."""
    html = som("ola").get(f"/?kategori={verdi}").text
    assert kort(html) == OLAS_FIRE
    assert tittel(html) == "Ledige oppdrag i 0571 Oslo – Nabolagshelten"
    alle = lenke(html, "Alle")
    assert alle["aria-current"] == "true" and alle["autofocus"]
    assert html.count("autofocus") == 1


def test_kategorilenkene_har_adresse_og_hake(som) -> None:
    """UX-DR24: «Alle» + seks kategorier som lenker med egen adresse; valgt har hake og ikon."""
    html = som("ola").get("/?kategori=hage").text
    lenker = kategorilenker(html)
    assert [a["tekst"] for a in lenker] == [
        "Alle", "Snømåking", "Hage", "Bærehjelp/flytting", "Dyrepass", "Teknologihjelp", "Annet",
    ]
    assert [a["href"] for a in lenker] == [
        "/?kategori=alle", "/?kategori=snomaking", "/?kategori=hage",
        "/?kategori=baerehjelp-flytting", "/?kategori=dyrepass", "/?kategori=teknologihjelp",
        "/?kategori=annet",
    ]
    gruppe = re.search(r'<div class="kategorifilter" role="group" aria-labelledby="kategori-etikett">', html)
    assert gruppe
    assert '<p class="gruppe__etikett" id="kategori-etikett">Kategori</p>' in html
    hage = re.search(r'<a class="kategoriknapp kategoriknapp--filter" href="/\?kategori=hage"[^>]*>(.*?)</a>',
                     html, re.S).group(1)
    assert hage.count("<svg") == 2  # hake og kategoriikon


# ---------- postnummer (FR-11) ----------


def test_annet_postnummer_beholder_kategorien(som) -> None:
    """FR-11: «Vis»/Enter med 5006 mens Hage er valgt. Fokus og beskrivelse på feltet."""
    html = som("ola").get("/?postnummer=5006&kategori=hage&vist_postnummer=0571").text
    assert "<h1>Ledige oppdrag i 5006 Bergen</h1>" in html
    assert kort(html) == ["Klippe hekken"]
    assert antallslinje(html) == "1 ledig oppdrag i Hage i 5006 Bergen"
    felt = postnummerfelt(html)
    assert felt["value"] == "5006"
    assert "autofocus" in felt
    assert "antallslinje" in felt["aria-describedby"].split()
    assert html.count("autofocus") == 1
    hage = lenke(html, "Hage")
    assert hage["aria-current"] == "true" and not hage["autofocus"]
    assert hage["aria-describedby"] == "antallslinje"
    for a in kategorilenker(html):
        assert sporring(a["href"])["postnummer"] == ["5006"], a
    assert "vist_postnummer=" not in "".join(a["href"] for a in kategorilenker(html))
    assert '<span id="postnummer-sted" aria-live="polite">Bergen</span>' in html


def test_postnummerskjemaet(som) -> None:
    """FR-11: GET-skjema med «Postnummer», poststed, skjult kategori og vist_postnummer, og «Vis»."""
    html = som("ola").get("/?kategori=hage").text
    skjema = re.search(r'<form class="postnummerfilter" method="get" action="/" novalidate>(.*?)</form>', html, re.S)
    assert skjema
    innhold = skjema.group(1)
    assert '<label for="postnummer">Postnummer</label>' in innhold
    felt = postnummerfelt(html)
    assert (felt["type"], felt["inputmode"], felt["autocomplete"]) == ("text", "numeric", "postal-code")
    assert felt["value"] == "0571"
    assert '<input type="hidden" name="kategori" value="hage">' in innhold
    assert '<input type="hidden" name="vist_postnummer" value="0571">' in innhold
    assert '<button class="knapp knapp--sekundar" type="submit">Vis</button>' in innhold
    assert innhold.index('name="postnummer"') < innhold.index('name="kategori"') < innhold.index(
        'name="vist_postnummer"'
    )
    # Uten kategori sendes ingen skjult kategori.
    assert 'name="kategori"' not in som("ola").get("/").text


@pytest.mark.parametrize(
    ("skrevet", "melding"),
    [
        ("9999", "Finner ikke postnummeret. Sjekk at det har fire siffer."),
        ("abc", "Finner ikke postnummeret. Sjekk at det har fire siffer."),
        ("1" * 3000, "Finner ikke postnummeret. Sjekk at det har fire siffer."),
        ("", "Skriv postnummeret."),
        ("   ", "Skriv postnummeret."),
    ],
    ids=["9999", "abc", "3000-tegn", "tomt", "mellomrom"],
)
def test_ukjent_postnummer_gir_feil_ved_feltet_og_lista_star(som, skrevet: str, melding: str) -> None:
    """FR-11: 200, lista for 5006 står uendret, og feilen står ved feltet med fokus.

    Ingen feiloppsummering etter h1 (beslutning i spec 2.3), men «Feil: » i tittelen.
    """
    svar = som("ola").get("/", params={"postnummer": skrevet, "vist_postnummer": "5006"})
    html = svar.text
    assert svar.status_code == 200
    assert "<h1>Ledige oppdrag i 5006 Bergen</h1>" in html
    assert kort(html) == SOFIES_TRE
    assert antallslinje(html) == "3 ledige oppdrag i 5006 Bergen"
    assert tittel(html) == "Feil: Ledige oppdrag i 5006 Bergen – Nabolagshelten"
    felt = postnummerfelt(html)
    assert felt["value"] == skrevet
    assert felt["aria-invalid"] == "true"
    assert "autofocus" in felt
    assert felt["aria-describedby"].split() == ["postnummer-feil", "postnummer-sted"]
    assert re.search(rf'<p class="feltfeil" id="postnummer-feil">.*?<span>{re.escape(melding)}</span>', html, re.S)
    assert "feiloppsummering" not in html
    assert html.count("autofocus") == 1
    for a in kategorilenker(html):
        assert sporring(a["href"])["postnummer"] == ["5006"], a


@pytest.mark.parametrize("vist", [None, "9999", "abc"])
def test_ukjent_postnummer_uten_gyldig_vist_bruker_eget(som, vist: str | None) -> None:
    """FR-11: uten gyldig `vist_postnummer` viser lista eget postnummer."""
    params = {"postnummer": "9999"} if vist is None else {"postnummer": "9999", "vist_postnummer": vist}
    html = som("ola").get("/", params=params).text
    assert "<h1>Ledige oppdrag i 0571 Oslo</h1>" in html
    assert kort(html) == OLAS_FIRE
    assert postnummerfelt(html)["aria-invalid"] == "true"
    assert tittel(html).startswith("Feil: ")


def test_postnummer_med_mellomrom_godtas(som) -> None:
    html = som("ola").get("/", params={"postnummer": " 5006 "}).text
    assert "<h1>Ledige oppdrag i 5006 Bergen</h1>" in html
    assert postnummerfelt(html)["value"] == "5006"


# ---------- tomtilstander (FR-10, FR-11, UX-DR21) ----------


def test_tom_med_kategori(som) -> None:
    """FR-11: Kari med Hage: ingen antallslinje, forslag og «Vis alle kategorier»."""
    html = som("kari").get("/?kategori=hage").text
    assert antallslinje(html) is None
    assert kort(html) == []
    assert '<p id="tom-forste">Ingen ledige oppdrag i 0571 Oslo akkurat nå.</p>' in html
    assert "Prøv en annen kategori eller et annet postnummer." in html
    assert "Velg et annet postnummer" not in html
    vis_alle = re.search(r'<a class="knapp knapp--sekundar" href="([^"]+)">Vis alle kategorier</a>', html)
    assert vis_alle and vis_alle.group(1) == "/?kategori=alle"
    hage = lenke(html, "Hage")
    assert hage["aria-describedby"] == "tom-forste" and hage["autofocus"]


def test_tom_med_kategori_beholder_postnummeret(som) -> None:
    html = som("ola").get(f"/?postnummer={POSTNUMMER_UTEN_OPPDRAG}&kategori=hage").text
    vis_alle = re.search(r'href="([^"]+)">Vis alle kategorier</a>', html).group(1)
    assert sporring(vis_alle) == {"kategori": ["alle"], "postnummer": [POSTNUMMER_UTEN_OPPDRAG]}


def test_tom_med_alle(som) -> None:
    """FR-10: «Prøv et annet postnummer.» og lenken «Velg et annet postnummer» til feltet."""
    html = som("ola").get(f"/?postnummer={POSTNUMMER_UTEN_OPPDRAG}").text
    assert f"<h1>Ledige oppdrag i {POSTNUMMER_UTEN_OPPDRAG} Oslo</h1>" in html
    assert antallslinje(html) is None
    assert f"Ingen ledige oppdrag i {POSTNUMMER_UTEN_OPPDRAG} Oslo akkurat nå." in html
    assert "Prøv et annet postnummer." in html
    assert '<a class="knapp knapp--sekundar" href="#postnummer" data-velg-felt>Velg et annet postnummer</a>' in html
    assert "Vis alle kategorier" not in html
    assert lenke(html, "Alle")["aria-describedby"] == "tom-forste"
    assert 'id="postnummer"' in html


def test_ingen_aria_live_pa_antallslinja(som) -> None:
    """Spec 2.3: antallslinja leses opp gjennom fokus og aria-describedby, ikke aria-live."""
    html = som("ola").get("/?kategori=hage").text
    assert re.search(r'<p class="antallslinje" id="antallslinje">', html)
    assert "aria-live" not in re.search(r'<p class="antallslinje"[^>]*>', html).group(0)


# ---------- detaljer (FR-9, UX-DR25) ----------


def test_detaljer_for_annen_bruker_har_oppdragsgiverblokken(som, db: Session) -> None:
    """FR-9: alle feltene, «Åpen», «Lagt ut av Nora Berg» med erfaring og «Se profil»."""
    oppdrag = oppdrag_med_tittel(db, "Mate katten i helgen")
    nora = hent_testbruker(db, "nora@eksempel.no")
    html = som("ola").get(f"/oppdrag/{oppdrag.id}").text
    assert "<h1>Mate katten i helgen</h1>" in html
    assert '<span class="skjult-tekst">Status: </span>Åpen</span>' in html
    assert "<span>Dyrepass</span>" in html
    assert "Fredag 27. nov. kl. 12:00" in html
    assert "250 kr" in html
    blokk = re.search(r'<section class="oppdragsgiver" aria-labelledby="oppdragsgiver-overskrift">(.*?)</section>',
                      html, re.S)
    assert blokk
    assert '<h2 class="oppdragsgiver__overskrift" id="oppdragsgiver-overskrift">Lagt ut av Nora Berg</h2>' in blokk.group(1)
    assert "1 fullført oppdrag · Ingen vurderinger ennå" in blokk.group(1)
    assert f'<a class="tekstknapp" href="/profil/{nora.id}">Se profil</a>' in blokk.group(1)
    assert html.index("beskrivelse") < html.index("oppdragsgiver-overskrift")
    assert 'href="/" aria-current="true"' in html
    assert "har meldt interesse" not in html


def test_detaljer_uten_fullforte(som, db: Session) -> None:
    """FR-21: Kari har ikke vært hjelper: «Ingen fullførte oppdrag ennå»."""
    oppdrag = oppdrag_med_tittel(db, "Måke snø i innkjørselen")
    html = som("ola").get(f"/oppdrag/{oppdrag.id}").text
    assert "Lagt ut av Kari Nordmann" in html
    assert "Ingen fullførte oppdrag ennå · Ingen vurderinger ennå" in html


def test_detaljer_for_eier_har_ingen_oppdragsgiverblokk(som, db: Session) -> None:
    """FR-9: Kari ser ikke blokken på sitt eget oppdrag, og «Mine oppdrag» er markert."""
    oppdrag = oppdrag_med_tittel(db, "Måke snø i innkjørselen")
    html = som("kari").get(f"/oppdrag/{oppdrag.id}").text
    assert "Lagt ut av" not in html
    assert 'class="oppdragsgiver"' not in html
    assert 'href="/mine-oppdrag" aria-current="true"' in html


def test_slettet_oppdragsgiver_vises_uten_lenke(som, db: Session, lag_bruker, lag_oppdrag) -> None:
    """AD-8: «Slettet bruker», uten erfaring og uten «Se profil»."""
    slettet = lag_bruker(navn=None, epost=None, telefon=None, postnummer=None, fodselsdato=None,
                         passord=None, slettet_tidspunkt=T0)
    oppdrag = lag_oppdrag(oppdragsgiver=slettet)
    html = som("ola").get(f"/oppdrag/{oppdrag.id}").text
    assert "Lagt ut av Slettet bruker" in html
    assert "Se profil" not in html
    assert "Ingen vurderinger ennå" not in html


@pytest.mark.parametrize("status", ["hjelper_valgt", "utfort", "avbrutt"])
def test_annen_status_gir_samme_404_for_andre(som, db: Session, lag_oppdrag, status: str) -> None:
    """FR-9: andre får samme 404 som for et oppdrag som ikke finnes; eier og valgt hjelper får 200."""
    kari = hent_testbruker(db, "kari@eksempel.no")
    nora = hent_testbruker(db, "nora@eksempel.no")
    oppdrag = lag_oppdrag(oppdragsgiver=kari, status=status, valgt_hjelper_id=nora.id, tittel="Hemmelig")
    klient = som("ola")
    svar = klient.get(f"/oppdrag/{oppdrag.id}")
    finnes_ikke = klient.get("/oppdrag/999999")
    assert svar.status_code == finnes_ikke.status_code == 404
    fjern_csrf = re.compile(r'value="[^"]*"')
    assert fjern_csrf.sub("", svar.text) == fjern_csrf.sub("", finnes_ikke.text)
    assert som("nora").get(f"/oppdrag/{oppdrag.id}").status_code == 200
    assert som("kari").get(f"/oppdrag/{oppdrag.id}").status_code == 200


# ---------- XSS og personvern (NFR-12, FR-16, AD-16) ----------


def test_html_vises_som_tekst_pa_kortet_og_i_blokken(som, db: Session, lag_bruker, lag_oppdrag) -> None:
    """NFR-12: tittel og navn med `<script>` vises som tekst."""
    skadelig = "<script>alert(1)</script>"
    eier = lag_bruker(navn=skadelig, postnummer="0571")
    oppdrag = lag_oppdrag(oppdragsgiver=eier, tittel=skadelig)
    klient = som("ola")
    for html in (klient.get("/").text, klient.get(f"/oppdrag/{oppdrag.id}").text):
        assert skadelig not in html
        assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html
    assert "Lagt ut av &lt;script&gt;" in klient.get(f"/oppdrag/{oppdrag.id}").text


def _personopplysninger() -> list[str]:
    verdier = []
    for t in seed.TESTBRUKERE:
        verdier += [t.telefon, f"{t.telefon[:3]} {t.telefon[3:5]} {t.telefon[5:]}", t.epost,
                    t.epost.replace("@", "&#64;"), t.fodselsdato.isoformat(), t.fodselsdato.strftime("%d.%m.%Y")]
    return verdier


def test_ingen_personopplysninger_i_oversikten_og_detaljene(som, db: Session) -> None:
    """FR-16, AD-16: HTML fra oversikten og detaljene (eier og andre) har ingen telefon,
    e-post eller fødselsdato til testbrukerne."""
    oppdrag = oppdrag_med_tittel(db, "Mate katten i helgen")
    sider = [
        som("ola").get("/").text,
        som("ola").get("/?postnummer=5006&kategori=alle&vist_postnummer=0571").text,
        som("ola").get(f"/oppdrag/{oppdrag.id}").text,
        som("nora").get(f"/oppdrag/{oppdrag.id}").text,
    ]
    for html in sider:
        for verdi in _personopplysninger():
            assert verdi not in html, verdi


# ---------- Innlogget (R7) ----------


def test_innlogget_har_postnummeret(app, db: Session, logg_inn_som, klient: TestClient) -> None:
    """R7, AD-4: `finn_innlogget` gir postnummeret fra samme spørring."""
    ola = hent_testbruker(db, "ola@eksempel.no")
    nokkel = logg_inn_som(klient, ola)
    request = SimpleNamespace(cookies={SESJON_COOKIE: nokkel}, app=app)
    innlogget = app.state.autentisering.finn_innlogget(request)
    assert (innlogget.bruker_id, innlogget.visningsnavn, innlogget.postnummer) == (ola.id, "Ola Hansen", "0571")


def test_oversikten_og_nytt_oppdrag_slar_ikke_opp_brukeren(som, monkeypatch) -> None:
    """R7: oversikten og «Nytt oppdrag» bruker `Innlogget.postnummer`, ikke `hent_offentlig_bruker`."""

    def feil(*args, **kwargs):
        raise AssertionError("hent_offentlig_bruker skal ikke kalles")

    monkeypatch.setattr("app.oppdrag.routes.hent_offentlig_bruker", feil)
    klient = som("ola")
    assert klient.get("/").status_code == 200
    html = klient.get("/oppdrag/ny").text
    assert postnummerfelt(html)["value"] == "0571"


# ---------- invariant FR-3 (T-6) ----------


def test_utlogget_filter_sendes_til_innlogging_og_tilbake(klient: TestClient, db: Session) -> None:
    """FR-3: utlogget GET `/?kategori=hage` gir innloggingen med `neste`, og etterpå filteret."""
    svar = klient.get("/?kategori=hage", follow_redirects=False)
    assert svar.status_code == 303
    location = svar.headers["location"]
    assert urlsplit(location).path == "/logg-inn"
    assert parse_qs(urlsplit(location).query) == {"neste": ["/?kategori=hage"]}
    side = klient.get(location).text
    assert 'name="neste" value="/?kategori=hage"' in side
    token = re.search(r'name="csrf_token" value="([^"]+)"', side).group(1)
    innlogging = klient.post(
        "/logg-inn",
        data={"csrf_token": token, "epost": "ola@eksempel.no", "passord": "ola-lokal-1", "neste": "/?kategori=hage"},
        follow_redirects=False,
    )
    assert innlogging.status_code == 303
    assert innlogging.headers["location"] == "/?kategori=hage"
    assert kort(klient.get("/?kategori=hage").text) == ["Raking av løv i hagen"]


# ---------- grensen for passert (FR-8) ----------


def test_grensen_for_passert_over_http(som, db: Session, lag_oppdrag, sett_na) -> None:
    """FR-8, AD-3: vist 1 s før tidspunktet, ikke vist når klokka er lik tidspunktet."""
    tidspunkt = T0 + timedelta(hours=3)
    lag_oppdrag(tittel="Grensetilfellet", tidspunkt=tidspunkt, kategori="annet")
    klient = som("ola")
    sett_na(tidspunkt - timedelta(seconds=1))
    assert "Grensetilfellet" in kort(klient.get("/?kategori=annet").text)
    sett_na(tidspunkt)
    assert "Grensetilfellet" not in kort(klient.get("/?kategori=annet").text)

