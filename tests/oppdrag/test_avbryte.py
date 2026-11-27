"""Avbryte oppdrag over HTTP: radene i I/O-matrisen i spec 2.5 om avbrudd, dialogen og snarveiene.

FR-7, FR-8, NFR-5, NFR-8, NFR-12, AD-2, AR-28, UX-DR18, UX-DR26, §4.0. Klokka står fast på
tirsdag 24.11.2026 kl. 13:00 norsk tid, og databasen har eksempeldataene fra seed.

- POST `/oppdrag/{id}/avbryt` med CSRF avbryter og gir «Oppdraget er avbrutt.» i fokus, i
  detaljene, eller i «Mine oppdrag» med `fra=mine` (den eneste verdien som godtas).
- GET `/oppdrag/{id}/avbryt` er bekreftelsessiden uten JS, med samme tekst som dialogen.
- Dialogen fra `bekreft_dialog` og snarveiene i raden med merket «Tidspunktet er passert».
"""

from __future__ import annotations

import re
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.oppdrag.models import Oppdrag

from ..core.test_render import les_side
from .test_legge_ut import attrs
from .test_redigere import (  # noqa: F401  (fiksturene brukes av testene her)
    BAERE,
    KONFLIKT,
    MAKE,
    baere,
    csrf,
    eksempeldata,
    les,
    make,
    oppdrag_med_tittel,
    som,
)

T0 = datetime(2026, 11, 24, 12, 0, tzinfo=timezone.utc)


def avbryt(klient: TestClient, oppdrag_id: int, *, med_csrf: bool = True, **data: str):
    if med_csrf:
        data["csrf_token"] = csrf(klient)
    return klient.post(f"/oppdrag/{oppdrag_id}/avbryt", data=data, follow_redirects=False)


# ---------- POST (FR-7) ----------


def test_avbryte_fra_detaljene(som, db: Session, make) -> None:
    """FR-7, UX-DR22: status `avbrutt`, `versjon` + 1, 303 til detaljene med kvitteringen i fokus.

    Detaljene viser «Avbrutt» uten knapper og uten dialog.
    """
    klient = som("kari")
    svar = avbryt(klient, make.id)
    assert svar.status_code == 303
    assert svar.headers["location"] == f"/oppdrag/{make.id}"
    lagret = les(db, make.id)
    assert (lagret.status, lagret.versjon) == ("avbrutt", 2)
    html = klient.get(svar.headers["location"]).text
    kvittering = attrs(html, "div", id="kvittering")
    assert "autofocus" in kvittering
    assert "<span>Oppdraget er avbrutt.</span>" in html
    assert html.count("autofocus") == 1
    assert '<span class="skjult-tekst">Status: </span>Avbrutt</span>' in html
    for fravaer in ("Rediger", "Avbryt oppdrag", "Endre tidspunkt", "<dialog"):
        assert fravaer not in html, fravaer


def test_avbryte_fra_mine_oppdrag(som, db: Session, baere) -> None:
    """Spec 2.5, beslutning 1: med `fra=mine` havner Kari i «Mine oppdrag» med kvitteringen i fokus,
    og raden viser «Avbrutt»."""
    klient = som("kari")
    svar = avbryt(klient, baere.id, fra="mine")
    assert svar.status_code == 303
    assert svar.headers["location"] == "/mine-oppdrag"
    html = klient.get("/mine-oppdrag").text
    assert "autofocus" in attrs(html, "div", id="kvittering")
    assert "<span>Oppdraget er avbrutt.</span>" in html
    rad = re.search(rf'<li class="listerad listerad--lenke">(?:(?!</li>).)*{BAERE}.*?</li>', html, re.S).group(0)
    assert "Status: </span>Avbrutt" in rad
    assert "listerad__handlinger" not in html and 'class="menytall"' not in html


@pytest.mark.parametrize("fra", ["", "detaljer", "https://angriper.example", "//angriper.example", "MINE"])
def test_andre_verdier_av_fra_gir_detaljene(som, make, fra: str) -> None:
    """Spec 2.5: `fra=mine` er den eneste verdien som godtas; adressen kan aldri sende brukeren ut."""
    svar = avbryt(som("kari"), make.id, fra=fra)
    assert svar.headers["location"] == f"/oppdrag/{make.id}"


def test_avbryte_uten_csrf_gir_403(som, db: Session, make) -> None:
    """AD-5, NFR-12: uten CSRF-nøkkel avvises POST, og ingenting endres."""
    svar = avbryt(som("kari"), make.id, med_csrf=False)
    assert svar.status_code == 403
    assert les(db, make.id).status == "apen"


@pytest.mark.parametrize("metode", ["GET", "POST"])
def test_andres_oppdrag_gir_samme_404(som, db: Session, make, metode: str) -> None:
    """FR-7, FR-9: Ola får samme 404 som for et oppdrag som ikke finnes, og ingenting endres."""
    klient = som("ola")
    svar = klient.get(f"/oppdrag/{make.id}/avbryt") if metode == "GET" else avbryt(klient, make.id)
    assert svar.status_code == 404
    assert "<h1>Fant ikke siden</h1>" in svar.text and MAKE not in svar.text
    finnes_ikke = klient.get("/oppdrag/999999/avbryt")
    assert finnes_ikke.status_code == 404
    assert les(db, make.id).status == "apen"


@pytest.mark.parametrize("tittel", ["Bytte lyspære i taket", "Lufte hunden mens jeg er bortreist"],
                         ids=["utfort", "avbrutt"])
@pytest.mark.parametrize("metode", ["GET", "POST"])
def test_feil_status_gir_konflikt(som, db: Session, tittel: str, metode: str) -> None:
    """FR-7, §4.0: Utført og Avbrutt kan ikke avbrytes: 303 til detaljene med feilmeldingen."""
    oppdrag = oppdrag_med_tittel(db, tittel)
    for_ = (oppdrag.status, oppdrag.versjon)
    klient = som("kari")
    svar = (klient.get(f"/oppdrag/{oppdrag.id}/avbryt", follow_redirects=False) if metode == "GET"
            else avbryt(klient, oppdrag.id))
    assert svar.status_code == 303
    assert svar.headers["location"] == f"/oppdrag/{oppdrag.id}"
    lagret = les(db, oppdrag.id)
    assert (lagret.status, lagret.versjon) == for_
    html = klient.get(svar.headers["location"]).text
    assert f"<span>{KONFLIKT}</span>" in html and "Last siden på nytt</a>" in html


def test_to_faner(som, db: Session, make) -> None:
    """§4.0: avbrutt i fane 1, så «Lagre endringer» eller «Ja, avbryt oppdraget» i fane 2.

    Bare den første handlingen er utført. Fane 2 får detaljene med feilmeldingen i fokus.
    """
    klient = som("kari")
    nokkel = csrf(klient)
    skjema = klient.get(f"/oppdrag/{make.id}/rediger").text  # fane 2 åpner skjemaet før avbruddet
    assert avbryt(klient, make.id).status_code == 303  # fane 1
    data_lagring = {
        "csrf_token": nokkel, "beskrivelse": "Trenger noen som kan måke snø i innkjørselen min.",
        "tittel": "Endret i fane 2", "kategori": "snomaking", "postnummer": "0571",
        "dato": "25.11.2026", "klokkeslett": "09:00", "tilbud": "belop", "belop": "200",
    }
    assert "Lagre endringer" in skjema
    for sti, data in ((f"/oppdrag/{make.id}/avbryt", {"csrf_token": nokkel}),
                      (f"/oppdrag/{make.id}/rediger", data_lagring)):
        svar = klient.post(sti, data=data, follow_redirects=False)  # fane 2
        assert svar.status_code == 303, sti
        assert svar.headers["location"] == f"/oppdrag/{make.id}"
        html = klient.get(svar.headers["location"]).text
        assert "autofocus" in attrs(html, "div", id="feilmelding"), sti
        assert html.count("autofocus") == 1
        assert "Last siden på nytt</a>" in html
    lagret = les(db, make.id)
    assert (lagret.status, lagret.versjon, lagret.tittel) == ("avbrutt", 2, MAKE)


# ---------- bekreftelsessiden uten JS (AR-28, UX-DR18) ----------


def test_bekreftelsessiden(som, make) -> None:
    """FR-7, NFR-8: h1 «Avbryte «…»?», «Det kan ikke angres.», POST-knappen og lenken «Behold oppdraget»."""
    svar = som("kari").get(f"/oppdrag/{make.id}/avbryt")
    assert svar.status_code == 200
    html = svar.text
    assert "<title>Avbryte «Måke snø i innkjørselen»? – Nabolagshelten</title>" in html
    assert "<h1>Avbryte «Måke snø i innkjørselen»?</h1>" in html
    assert "<p>Det kan ikke angres.</p>" in html
    form = attrs(html, "form", method="post")
    assert form["action"] == f"/oppdrag/{make.id}/avbryt"
    assert 'name="csrf_token"' in html and 'name="fra"' not in html
    assert '<button class="knapp knapp--primar" type="submit">Ja, avbryt oppdraget</button>' in html
    assert f'<a class="tekstknapp" href="/oppdrag/{make.id}">Behold oppdraget</a>' in html
    assert ">Avbryt<" not in html  # angre-valget heter aldri «Avbryt»
    side = les_side(html)
    assert [t for t, _ in side.tagger].count("h1") == 1
    assert "autofocus" not in html


def test_bekreftelsessiden_fra_mine_oppdrag(som, make) -> None:
    html = som("kari").get(f"/oppdrag/{make.id}/avbryt?fra=mine").text
    assert attrs(html, "input", name="fra")["value"] == "mine"
    assert '<a class="tekstknapp" href="/mine-oppdrag">Behold oppdraget</a>' in html
    html = som("kari").get(f"/oppdrag/{make.id}/avbryt?fra=https://angriper.example").text
    assert 'name="fra"' not in html and "angriper" not in html


def test_post_fra_bekreftelsessiden_virker(som, db: Session, make) -> None:
    """AR-28: uten JS gir lenken bekreftelsessiden, og skjemaet der avbryter."""
    klient = som("kari")
    html = klient.get(f"/oppdrag/{make.id}/avbryt").text
    nokkel = re.search(r'name="csrf_token" value="([^"]+)"', html).group(1)
    svar = klient.post(f"/oppdrag/{make.id}/avbryt", data={"csrf_token": nokkel}, follow_redirects=False)
    assert svar.status_code == 303
    assert les(db, make.id).status == "avbrutt"


# ---------- dialogen og lenkene (NFR-8, UX-DR18) ----------


def dialog(html: str, dialog_id: str) -> str:
    return re.search(rf'<dialog class="dialog" id="{dialog_id}"[^>]*>.*?</dialog>', html, re.S).group(0)


def test_dialogen_i_detaljene(som, make) -> None:
    """UX-DR18: lenken «Avbryt oppdrag» går til bekreftelsessiden og har `data-dialog`. Dialogen har
    navn fra spørsmålet (h2, tabindex="-1"), beskrivelse, CSRF, primærknapp og angreknapp."""
    html = som("kari").get(f"/oppdrag/{make.id}").text
    assert (f'<a class="knapp knapp--sekundar" href="/oppdrag/{make.id}/avbryt" '
            'data-dialog="avbryt-dialog">Avbryt oppdrag</a>') in html
    blokk = dialog(html, "avbryt-dialog")
    assert 'aria-labelledby="avbryt-dialog-sporsmal" aria-describedby="avbryt-dialog-forklaring"' in blokk
    assert ('<h2 class="dialog__sporsmal" id="avbryt-dialog-sporsmal" tabindex="-1">'
            "Avbryte «Måke snø i innkjørselen»?</h2>") in blokk
    assert '<p class="dialog__forklaring" id="avbryt-dialog-forklaring">Det kan ikke angres.</p>' in blokk
    assert f'<form method="post" action="/oppdrag/{make.id}/avbryt">' in blokk
    assert 'name="csrf_token"' in blokk and 'name="fra"' not in blokk
    assert '<button class="knapp knapp--primar" type="submit">Ja, avbryt oppdraget</button>' in blokk
    assert '<button class="tekstknapp" type="button" data-lukk-dialog>Behold oppdraget</button>' in blokk
    assert " open" not in blokk.split(">", 1)[0]
    assert html.count("<dialog") == 1
    assert '<script src="/static/js/dialog.js" defer></script>' in html


def test_snarveiene_i_raden(som, db: Session, baere) -> None:
    """FR-8, UX-DR26: bare raden med merket har `listerad__handlinger`, etter lenkedelen, med
    «Endre tidspunkt» og «Avbryt oppdrag» (sekundære) og `aria-describedby` til tittelen."""
    html = som("kari").get("/mine-oppdrag").text
    assert html.count('<div class="listerad__handlinger">') == 1
    rader = re.findall(r'<li class="listerad listerad--lenke">(.*?)</li>', html, re.S)
    med = [r for r in rader if "listerad__handlinger" in r]
    assert len(med) == 1 and BAERE in med[0]
    rad = med[0]
    hoved, _, resten = rad.partition('<div class="listerad__handlinger">')
    assert "Endre tidspunkt" not in hoved and "Avbryt oppdrag" not in hoved
    assert hoved.count("<a ") == 1
    tittel = f"rad-{baere.id}-tittel"
    assert (f'<a class="knapp knapp--sekundar" href="/oppdrag/{baere.id}/rediger?fokus=tidspunkt" '
            f'aria-describedby="{tittel}">Endre tidspunkt</a>') in resten
    assert (f'<a class="knapp knapp--sekundar" href="/oppdrag/{baere.id}/avbryt?fra=mine" '
            f'data-dialog="avbryt-dialog-{baere.id}" aria-describedby="{tittel}">Avbryt oppdrag</a>') in resten
    blokk = dialog(html, f"avbryt-dialog-{baere.id}")
    assert "Avbryte «Bære ved opp til tredje etasje»?" in blokk
    assert '<input type="hidden" name="fra" value="mine">' in blokk
    assert html.count("<dialog") == 1


def test_lenkene_fungerer_uten_js(som, baere) -> None:
    """AR-28: lenkene i raden gir skjemaet med fokus på «Dato» og bekreftelsessiden."""
    klient = som("kari")
    html = klient.get(f"/oppdrag/{baere.id}/rediger?fokus=tidspunkt").text
    assert "autofocus" in attrs(html, "input", name="dato")
    html = klient.get(f"/oppdrag/{baere.id}/avbryt?fra=mine").text
    assert "<h1>Avbryte «Bære ved opp til tredje etasje»?</h1>" in html


# ---------- XSS (NFR-12) ----------


def test_tittel_vises_som_tekst_i_dialogen_og_bekreftelsessiden(som, db: Session, make, baere) -> None:
    skadelig = "<script>alert(1)</script>"
    for oppdrag in (make, baere):
        oppdrag.tittel = skadelig
    db.commit()
    klient = som("kari")
    escaped = "&lt;script&gt;alert(1)&lt;/script&gt;"
    for sti in (f"/oppdrag/{make.id}", f"/oppdrag/{make.id}/avbryt", "/mine-oppdrag"):
        html = klient.get(sti).text
        assert skadelig not in html, sti
        assert f"Avbryte «{escaped}»?" in html, sti
    assert f"<title>Avbryte «{escaped}»? – Nabolagshelten</title>" in klient.get(f"/oppdrag/{make.id}/avbryt").text


def test_seed_er_uendret(db: Session) -> None:
    """Spec 2.5: seed har allerede det utgåtte «Bære ved» og det avbrutte «Lufte hunden»."""
    assert oppdrag_med_tittel(db, BAERE).status == "apen"
    assert oppdrag_med_tittel(db, "Lufte hunden mens jeg er bortreist").status == "avbrutt"
    assert isinstance(oppdrag_med_tittel(db, MAKE), Oppdrag)


def test_ugyldig_id_gir_404(som) -> None:
    """GET og POST med id utenfor heltallskolonnen gir 404, ikke 500."""
    klient = som("kari")
    for oppdrag_id in (0, 2**31, 99999999999999999999):
        assert klient.get(f"/oppdrag/{oppdrag_id}/avbryt").status_code == 404, oppdrag_id
        assert avbryt(klient, oppdrag_id).status_code == 404, oppdrag_id


@pytest.mark.parametrize("fra", [None, "mine"])
def test_dobbel_innsending_gir_feilmeldingen_pa_den_andre(som, db: Session, make, fra: str | None) -> None:
    """NFR-5, EXPERIENCE.md UJ-1: bekreftelsessiden sendt to ganger. Bare første teller, og den andre
    får «Oppdraget er endret. Last siden på nytt.» i detaljene, også med `fra=mine`."""
    klient = som("kari")
    data = {"fra": fra} if fra else {}
    forste = avbryt(klient, make.id, **data)
    andre = avbryt(klient, make.id, **data)
    assert forste.status_code == andre.status_code == 303
    assert forste.headers["location"] == ("/mine-oppdrag" if fra else f"/oppdrag/{make.id}")
    assert andre.headers["location"] == f"/oppdrag/{make.id}"
    assert "feilmelding=" in andre.headers["set-cookie"]
    lagret = les(db, make.id)
    assert (lagret.status, lagret.versjon) == ("avbrutt", 2)


@pytest.mark.parametrize("hvor", ["skjema", "adresse"])
def test_konflikt_med_fra_mine_gaar_til_detaljene(som, db: Session, hvor: str) -> None:
    """Spec 2.5, beslutning 1: `Konflikt` går til detaljene også med `fra=mine`."""
    oppdrag = oppdrag_med_tittel(db, "Bytte lyspære i taket")  # utfort
    klient = som("kari")
    if hvor == "skjema":
        svar = avbryt(klient, oppdrag.id, fra="mine")
    else:
        svar = klient.post(f"/oppdrag/{oppdrag.id}/avbryt?fra=mine", data={"csrf_token": csrf(klient)},
                           follow_redirects=False)
    assert svar.status_code == 303
    assert svar.headers["location"] == f"/oppdrag/{oppdrag.id}"
    assert "feilmelding=" in svar.headers["set-cookie"]


def test_tilbake_etter_avbrudd_fra_dialogen_gaar_til_mine_oppdrag(som, make) -> None:
    """Invariant 2.3/2.4: Referer er detaljene selv etter avbrudd eller `Konflikt` fra dialogen.
    «Tilbake» på eget oppdrag går da til «Mine oppdrag», ikke til oversikten."""
    klient = som("kari")
    avbryt(klient, make.id)
    html = klient.get(f"/oppdrag/{make.id}", headers={"referer": f"http://testserver/oppdrag/{make.id}"}).text
    assert '<a class="tekstknapp" href="/mine-oppdrag">Tilbake</a>' in html
