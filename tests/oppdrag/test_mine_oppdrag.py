"""«Mine oppdrag» og tallet i menyen over HTTP: radene i I/O-matrisen i spec 2.4.

FR-8, FR-9, FR-18, NFR-2, NFR-11, NFR-12, AD-1, AD-3, AD-16, UX-DR3, UX-DR9, UX-DR10,
UX-DR21, UX-DR26. Klokka står fast på tirsdag 24.11.2026 kl. 13:00 norsk tid, og
databasen har testbrukerne og eksempeloppdragene fra seed. Kari har seks oppdrag, og
ett av dem («Bære ved opp til tredje etasje») er utgått. Ola har ingen.

Tallet i menyen testes med en spion gitt til `lag_app(menykrok=…)`: den kalles bare når
noen er innlogget, med forespørselens sesjon, og aldri fra feilsiden.
"""

from __future__ import annotations

import html as html_lib
import re
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app import lag_app, seed
from app.identity.models import Bruker
from app.oppdrag.models import Oppdrag
from app.oppdrag.service import antall_trenger_handling

from ..core.test_render import les_side
from .test_grunnsider import menyvalg
from .test_legge_ut import send

T0 = datetime(2026, 11, 24, 12, 0, tzinfo=timezone.utc)

KARIS_SEKS = [
    # (tittel, status, merker, tidspunkt) i rekkefølgen etter tidspunkt
    ("Bytte lyspære i taket", "Utført", [], "Torsdag 19. nov. kl. 12:00"),
    ("Bære ved opp til tredje etasje", "Åpen", ["Tidspunktet er passert"], "Søndag 22. nov. kl. 10:00"),
    ("Måke snø i innkjørselen", "Åpen", [], "I morgen kl. 09:00"),
    ("Raking av løv i hagen", "Åpen", [], "Lørdag 28. nov. kl. 11:00"),
    ("Hjelp med nytt nettbrett", "Åpen", [], "Mandag 30. nov. kl. 14:00"),
    ("Lufte hunden mens jeg er bortreist", "Avbrutt", [], "Fredag 4. des. kl. 16:00"),
]
FORKLARING = "1 oppdrag trenger at du gjør noe."


@pytest.fixture(autouse=True)
def eksempeldata(db: Session, sett_na) -> None:
    sett_na(T0)
    seed.last_eksempeldata(db)
    db.commit()


def hent_testbruker(db: Session, navn: str) -> Bruker:
    return db.scalars(select(Bruker).where(Bruker.epost == f"{navn}@eksempel.no")).one()


def oppdrag_med_tittel(db: Session, tittel: str) -> Oppdrag:
    return db.scalars(select(Oppdrag).where(Oppdrag.tittel == tittel)).one()


@pytest.fixture
def som(klient: TestClient, db: Session, logg_inn_som):
    """`som("kari")` logger inn testbrukeren og gir klienten."""

    def _som(navn: str) -> TestClient:
        klient.cookies.clear()
        logg_inn_som(klient, hent_testbruker(db, navn))
        return klient

    return _som


class Spion:
    """Menykroken som spion: noterer hvert kall og teller som den ekte kroken."""

    def __init__(self) -> None:
        self.kall: list[tuple[Session, int]] = []

    def __call__(self, db: Session, bruker_id: int) -> int:
        self.kall.append((db, bruker_id))
        return antall_trenger_handling(db, bruker_id)


@pytest.fixture
def spion_app(sesjonsfabrikk: sessionmaker[Session], db: Session, logg_inn_som):
    """(klient, spion, sesjoner): appen med spionen som menykrok, innlogget som Kari.

    `sesjoner` er sesjonene appen har laget fra `sesjonsfabrikk`, i rekkefølge.
    """
    spion = Spion()
    sesjoner: list[Session] = []

    def fabrikk() -> Session:
        sesjon = sesjonsfabrikk()
        sesjoner.append(sesjon)
        return sesjon

    app = lag_app(menykrok=spion)
    app.state.sesjonsfabrikk = fabrikk
    with TestClient(app) as klient:
        logg_inn_som(klient, hent_testbruker(db, "kari"))
        yield klient, spion, sesjoner


# ---------- hjelpere for HTML ----------


def rader(html: str) -> list[dict]:
    """Hver lenkerad: lenken, merkelinja, status, merker, tidspunkt og hele blokken."""
    ut = []
    for blokk in re.findall(r'<li class="listerad listerad--lenke">(.*?)</li>', html, re.S):
        lenke = re.search(
            r'<a class="listerad__lenke" href="([^"]+)" aria-describedby="([^"]+)">([^<]*)</a>', blokk
        )
        assert lenke, blokk
        merkelinje = re.search(r'<div class="merkelinje" id="([^"]+)">(.*?)</div>', blokk, re.S)
        assert merkelinje, blokk
        ut.append(
            {
                "href": lenke.group(1),
                "beskrevet_av": lenke.group(2),
                "tittel": html_lib.unescape(lenke.group(3)),
                "merkelinje_id": merkelinje.group(1),
                "status": re.search(r'<span class="skjult-tekst">Status: </span>([^<]+)</span>',
                                    merkelinje.group(2)).group(1),
                "merker": re.findall(
                    r'<span class="skjult-tekst">Må gjøres: </span>([^<]+)<span class="skjult-tekst">\.</span>',
                    merkelinje.group(2),
                ),
                "tid_id": re.search(r'<span class="listerad__tid" id="([^"]+)">', blokk).group(1),
                "tid": re.search(r'<span class="listerad__tid" id="[^"]+">([^<]+)</span>', blokk).group(1),
                "blokk": blokk,
            }
        )
    return ut


def menytall(html: str, variant: str) -> tuple[str | None, str | None]:
    """(synlig tall, skjult tekst) ved «Mine oppdrag» i menyen «topp» eller «bunn»."""
    nav = re.search(rf'<nav class="meny meny--{variant}" aria-label="Hovedmeny">(.*?)</nav>', html, re.S)
    assert nav, f"Mangler menyen {variant}"
    lenke = re.search(r'<a class="meny__valg" href="/mine-oppdrag"[^>]*>(.*?)</a>', nav.group(1), re.S)
    assert lenke
    tall = re.search(r'<span class="menytall" aria-hidden="true">([^<]*)</span>', lenke.group(1))
    skjult = re.search(r'<span class="skjult-tekst">([^<]*)</span>', lenke.group(1))
    return (tall.group(1) if tall else None, skjult.group(1) if skjult else None)


def forklaring(html: str) -> str | None:
    treff = re.search(r'<p class="handlingslinje">.*?<span>([^<]*)</span>\s*</p>', html, re.S)
    return treff.group(1) if treff else None


# ---------- «Oppdrag jeg har lagt ut» (FR-18) ----------


def test_kari_ser_seks_lenkerader_etter_tidspunkt(som, db: Session) -> None:
    """FR-8, FR-18, UX-DR9: title, h1, h2 og én lenkerad per eget oppdrag, etter tidspunkt.

    Det avbrutte og det utførte står med, og andres oppdrag vises ikke.
    """
    svar = som("kari").get("/mine-oppdrag")
    assert svar.status_code == 200
    html = svar.text
    assert "<title>Mine oppdrag: Oppdrag jeg har lagt ut – Nabolagshelten</title>" in html
    assert "<h1>Mine oppdrag</h1>" in html
    assert "<h2>Oppdrag jeg har lagt ut</h2>" in html
    funnet = rader(html)
    assert [(r["tittel"], r["status"], r["merker"], r["tid"]) for r in funnet] == KARIS_SEKS
    for rad in funnet:
        assert rad["href"] == f"/oppdrag/{oppdrag_med_tittel(db, rad['tittel']).id}"
    for andres in ("Mate katten i helgen", "Klippe hekken", "Henge opp gardiner"):
        assert andres not in html
    assert "Du har ikke lagt ut noen oppdrag." not in html


def test_raden_har_bare_tittelen_som_lenke(som) -> None:
    """UX-DR9, UX-DR10: tittelen er eneste lenke, med aria-describedby til merkelinja og tidspunktet.

    Merkelinja og tidspunktet har unik id, tidspunktet har klokkeikon, pila er aria-hidden, og lenkedelen
    har ingen knapper. Merket har skjult «Må gjøres: » foran og «.» etter. Fra story 2.5 har bare raden
    med merket snarveiene, i `listerad__handlinger` etter lenkedelen (test_avbryte.py sjekker dem).
    """
    html = som("kari").get("/mine-oppdrag").text
    funnet = rader(html)
    ider = [r["merkelinje_id"] for r in funnet]
    assert len(set(ider)) == len(ider) == 6
    for rad in funnet:
        blokk = rad["blokk"]
        oppdrag_id = rad["href"].rsplit("/", 1)[1]
        assert rad["merkelinje_id"] == f"rad-{oppdrag_id}-merker"
        assert rad["tid_id"] == f"rad-{oppdrag_id}-tid"
        assert rad["beskrevet_av"] == f'{rad["merkelinje_id"]} {rad["tid_id"]}'
        assert html.count(f'id="{rad["merkelinje_id"]}"') == html.count(f'id="{rad["tid_id"]}"') == 1
        assert f'<p class="listerad__tittel" id="rad-{oppdrag_id}-tittel">' in blokk
        hoved, _, handlinger = blokk.partition('<div class="listerad__handlinger">')
        assert hoved.count("<a ") == 1
        assert "<button" not in hoved and "<form" not in hoved
        assert bool(handlinger) is bool(rad["merker"])
        assert '<svg class="listerad__pil" aria-hidden="true" focusable="false"' in blokk
        fakta = re.search(r'<p class="listerad__fakta">(.*?)</p>', blokk, re.S).group(1)
        assert '<svg class="ikon" aria-hidden="true"' in fakta
    bare = next(r for r in funnet if r["merker"])
    assert '<span class="handlingsmerke">' in bare["blokk"]
    assert (
        '<span><span class="skjult-tekst">Må gjøres: </span>Tidspunktet er passert'
        '<span class="skjult-tekst">.</span></span>'
    ) in bare["blokk"]
    assert bare["blokk"].index("statusmerke") < bare["blokk"].index("handlingsmerke")
    assert html.count("handlingsmerke") == 1  # bare én rad har merket


def test_tom_viser_h2_og_tomtilstanden(som) -> None:
    """FR-18, UX-DR21: Ola har ingen oppdrag: h2, tomtilstanden og lenken, uten liste og uten linje."""
    html = som("ola").get("/mine-oppdrag").text
    assert "<h2>Oppdrag jeg har lagt ut</h2>" in html
    assert "Du har ikke lagt ut noen oppdrag." in html
    assert '<a class="tekstknapp tomtilstand__lenke" href="/oppdrag/ny">Legg ut oppdrag</a>' in html
    assert "listerad" not in html
    assert forklaring(html) is None
    assert html.index("<h2>Oppdrag jeg har lagt ut</h2>") < html.index("Du har ikke lagt ut noen oppdrag.")


def test_tittel_vises_som_tekst(som, db: Session, lag_oppdrag) -> None:
    """NFR-12, AD-11: HTML i tittelen vises escaped i raden."""
    skadelig = "<script>alert(1)</script>"
    lag_oppdrag(oppdragsgiver=hent_testbruker(db, "kari"), tittel=skadelig)
    html = som("kari").get("/mine-oppdrag").text
    assert skadelig not in html
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html
    assert skadelig in [r["tittel"] for r in rader(html)]


def test_ingen_personopplysninger(som, db: Session) -> None:
    """FR-16, AD-16: ingen telefonnummer, e-post eller fødselsdato i HTML fra «Mine oppdrag»."""
    html = som("kari").get("/mine-oppdrag").text
    for testbruker_ in seed.TESTBRUKERE:
        assert testbruker_.telefon not in html
        assert testbruker_.epost not in html
        assert testbruker_.fodselsdato.strftime("%d.%m.%Y") not in html
        assert testbruker_.fodselsdato.isoformat() not in html


# ---------- forklaringslinja og tallet i menyen (FR-18, NFR-11, AD-3) ----------


def test_forklaringslinja_star_rett_under_h1(som) -> None:
    """FR-18, UX-DR26: «1 oppdrag trenger at du gjør noe.» rett under h1, med samme tall som menyen."""
    html = som("kari").get("/mine-oppdrag").text
    assert forklaring(html) == FORKLARING
    assert re.search(r'<h1>Mine oppdrag</h1>\s*<p class="handlingslinje">\s*<svg class="ikon" aria-hidden="true"',
                     html)
    assert menytall(html, "topp") == ("1", ", 1 trenger handling")
    assert html.count(FORKLARING) == 1


def test_forklaringslinja_folger_tallet(som, db: Session, lag_oppdrag) -> None:
    """To utgåtte gir «2 oppdrag trenger at du gjør noe.» og 2 i menyen."""
    lag_oppdrag(oppdragsgiver=hent_testbruker(db, "kari"), tidspunkt=T0 - timedelta(hours=1), tittel="Passert nå")
    html = som("kari").get("/mine-oppdrag").text
    assert forklaring(html) == "2 oppdrag trenger at du gjør noe."
    assert menytall(html, "bunn") == ("2", ", 2 trenger handling")


@pytest.mark.parametrize("side", ["/", "/mine-oppdrag", "/profil", "detaljer", "/oppdrag/ny", "422"])
def test_tallet_i_begge_menyene_pa_alle_sider(som, db: Session, side: str) -> None:
    """NFR-11, UX-DR3: «1» (aria-hidden) og «, 1 trenger handling» ved «Mine oppdrag» i begge menyene."""
    klient = som("kari")
    if side == "detaljer":
        svar = klient.get(f"/oppdrag/{oppdrag_med_tittel(db, 'Måke snø i innkjørselen').id}")
    elif side == "422":
        svar = send(klient, tittel="")
        assert svar.status_code == 422
    else:
        svar = klient.get(side)
    html = svar.text
    for variant in ("topp", "bunn"):
        assert menytall(html, variant) == ("1", ", 1 trenger handling"), variant
        assert [t for _, _, t in menyvalg(html, variant)] == ["Oppdrag", "Mine oppdrag", "Profil"]
    assert html.count('class="menytall"') == 2
    assert "aria-live" not in re.search(r'<nav class="meny meny--bunn".*?</nav>', html, re.S).group(0)


def test_tallet_0_uten_utgatte(som, sett_na) -> None:
    """NFR-11: Ola, og Kari før alle tidspunktene, får verken tall, skjult tekst eller linje."""
    html = som("ola").get("/").text
    assert menytall(html, "topp") == menytall(html, "bunn") == (None, None)
    sett_na(T0 - timedelta(days=10))
    html = som("kari").get("/mine-oppdrag").text
    assert menytall(html, "topp") == menytall(html, "bunn") == (None, None)
    assert "trenger handling" not in html and forklaring(html) is None
    assert all(r["merker"] == [] for r in rader(html))


def test_andres_utgatte_teller_ikke(som, db: Session, lag_oppdrag) -> None:
    """NFR-11: Noras utgåtte oppdrag teller hos Nora, ikke hos Kari."""
    lag_oppdrag(oppdragsgiver=hent_testbruker(db, "nora"), tidspunkt=T0 - timedelta(days=1), tittel="Noras utgåtte")
    assert menytall(som("kari").get("/").text, "topp") == ("1", ", 1 trenger handling")
    assert menytall(som("nora").get("/").text, "topp") == ("1", ", 1 trenger handling")


# ---------- menykroken (AD-1, AD-3, spinen § Rendring) ----------


def test_kroken_far_foresporselens_sesjon(spion_app, db: Session) -> None:
    """AD-3: kroken får sesjonen fra `hent_db` (`request.state.db`) og åpner ingen egen.

    Forespørselen lager to sesjoner: én i mellomvaren (innloggingen) og én i `hent_db`.
    """
    klient, spion, sesjoner = spion_app
    oppdrag = oppdrag_med_tittel(db, "Måke snø i innkjørselen")
    sesjoner.clear()
    html = klient.get(f"/oppdrag/{oppdrag.id}").text
    assert len(sesjoner) == 2
    assert spion.kall == [(sesjoner[1], hent_testbruker(db, "kari").id)]
    assert menytall(html, "topp") == ("1", ", 1 trenger handling")


def test_kroken_kalles_ikke_fra_feilsiden(spion_app, db: Session, lag_oppdrag) -> None:
    """Spinen § Feil: 404 for en ukjent sti og for et oppdrag uten tilgang har menyen uten tall."""
    klient, spion, _ = spion_app
    avbrutt = lag_oppdrag(oppdragsgiver=hent_testbruker(db, "nora"), status="avbrutt", tittel="Noras avbrutte")
    for sti in ("/finnes-ikke", f"/oppdrag/{avbrutt.id}"):
        svar = klient.get(sti)
        assert svar.status_code == 404, sti
        assert "<h1>Fant ikke siden</h1>" in svar.text
        assert '<nav class="meny meny--topp" aria-label="Hovedmeny">' in svar.text
        assert menytall(svar.text, "topp") == menytall(svar.text, "bunn") == (None, None)
    assert spion.kall == []


def test_kroken_kalles_ikke_uten_innlogging(spion_app) -> None:
    klient, spion, _ = spion_app
    klient.cookies.clear()
    assert klient.get("/logg-inn").status_code == 200
    assert klient.get("/registrer").status_code == 200
    assert spion.kall == []


# ---------- invariantene fra 2.1, 2.2 og 2.3 (T-6) ----------


def test_eget_utgatt_oppdrag_fra_raden(som, db: Session) -> None:
    """FR-8, FR-9, UX-DR25: det utgåtte står ikke i Olas oversikt. Kari åpner det fra raden:
    «Mine oppdrag» har aria-current="true", ingen oppdragsgiverblokk, og «Tilbake» går til lista.
    """
    assert "Bære ved opp til tredje etasje" not in som("ola").get("/").text
    klient = som("kari")
    rad = next(r for r in rader(klient.get("/mine-oppdrag").text) if r["merker"])
    html = klient.get(rad["href"], headers={"referer": "http://testserver/mine-oppdrag"}).text
    assert "<h1>Bære ved opp til tredje etasje</h1>" in html
    assert [(h, c) for h, c, _ in menyvalg(html, "topp")] == [
        ("/", None), ("/mine-oppdrag", "true"), ("/profil", None),
    ]
    assert 'class="oppdragsgiver"' not in html
    assert '<a class="tekstknapp" href="/mine-oppdrag">Tilbake</a>' in html


@pytest.mark.parametrize(("sti", "aktiv"), [("/", "/"), ("/mine-oppdrag", "/mine-oppdrag"), ("/profil", "/profil")])
def test_menyen_og_siderammen_med_tallet(som, sti: str, aktiv: str) -> None:
    """NFR-11, UX-DR2: fast rekkefølge, én aria-current="page" (på «Mine oppdrag» fortsatt
    menyvalget, fordi fanene ikke finnes ennå), én h1, «Hopp til innholdet» først og høyst ett autofocus.
    """
    html = som("kari").get(sti).text
    for variant in ("topp", "bunn"):
        valg = menyvalg(html, variant)
        assert [(h, t) for h, _, t in valg] == [("/", "Oppdrag"), ("/mine-oppdrag", "Mine oppdrag"), ("/profil", "Profil")]
        assert [h for h, c, _ in valg if c == "page"] == [aktiv]
    side = les_side(html)
    assert [t for t, _ in side.tagger].count("h1") == 1
    tag, attrs, tekst = side.forste_fokuserbare
    assert (tag, attrs.get("href"), tekst) == ("a", "#innhold", "Hopp til innholdet")
    assert html.count("autofocus") <= 1


def test_publisert_oppdrag_star_i_lista(som, db: Session) -> None:
    """FR-5, FR-18: «Publiser» gir 303 til detaljene med kvitteringen, og oppdraget står i lista som Åpen."""
    klient = som("kari")
    svar = send(klient, tittel="Henge opp lamper")
    assert svar.status_code == 303
    assert "Oppdraget er lagt ut." in klient.get(svar.headers["location"]).text
    funnet = {r["tittel"]: r for r in rader(klient.get("/mine-oppdrag").text)}
    assert len(funnet) == 7
    assert funnet["Henge opp lamper"]["status"] == "Åpen"
    assert funnet["Henge opp lamper"]["merker"] == []
    assert funnet["Henge opp lamper"]["href"] == svar.headers["location"]
