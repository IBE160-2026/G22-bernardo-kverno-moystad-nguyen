// Teller og forhåndsvisning i skjema (UX-DR13, UX-DR15, AD-10, AR-28).
//
// Teller ved tekstområder (UX-DR13, AD-10). Progressiv forbedring: serveren
// skriver startverdien, «37 av 1000 tegn», og uten JS står den uendret til
// neste innsending. Feltet har `data-maks` (grensen), `data-teller` (id-en til
// telleren) og `data-varsel` (id-en til en skjult `aria-live`-node).
//
// Telleren teller kodepunkter etter NFC og trim, som serveren (AD-10), så
// «e» + kombinerende akutt teller som ett tegn. Telleren leses ikke opp for
// hvert tegn. Varselnoden får tekst bare når grensen nås, og tømmes når
// teksten blir kortere igjen. Ingen regler her; serveren sjekker lengden.
(function () {
  "use strict";

  function antallTegn(tekst) {
    var normalisert = tekst.normalize ? tekst.normalize("NFC") : tekst;
    return Array.from(normalisert.trim()).length;
  }

  function kobleTil(felt) {
    var teller = document.getElementById(felt.getAttribute("data-teller"));
    var varsel = document.getElementById(felt.getAttribute("data-varsel"));
    var maks = parseInt(felt.getAttribute("data-maks"), 10);
    if (!teller || isNaN(maks)) {
      return;
    }
    var varslet = false;

    // `skrivVarsel` er usann ved oppstart og `pageshow`: telleren rettes, men
    // ingenting leses opp før brukeren skriver.
    function oppdater(skrivVarsel) {
      var antall = antallTegn(felt.value);
      var tekst = antall + " av " + maks + " tegn";
      teller.textContent = tekst;
      if (!varsel) {
        return;
      }
      if (antall >= maks) {
        if (!varslet && skrivVarsel) {
          varsel.textContent = tekst;
        }
        varslet = true;
      } else if (varslet) {
        varsel.textContent = "";
        varslet = false;
      }
    }

    felt.addEventListener("input", function () {
      oppdater(true);
    });
    // Nettleseren kan fylle inn feltet igjen (tilbakeknappen, gjenopprettet skjema).
    window.addEventListener("pageshow", function () {
      oppdater(false);
    });
    oppdater(false);
  }

  document.querySelectorAll("[data-maks][data-teller]").forEach(kobleTil);

  // ---------- forhåndsvisningen (UX-DR15) ----------
  // «Slik vises oppdraget for andre.» i «Nytt oppdrag». Serveren skriver
  // startverdiene med de samme reglene (`forhandsvisning` i oppdrag/routes.py),
  // så siden ikke hopper. Kortet oppdateres ved `input` og `change` i skjemaet,
  // når poststed.js skriver poststedet, ved oppstart og ved `pageshow`. Det har
  // ingen `aria-live`, så ingenting leses opp, og fokus flyttes ikke.
  //
  // Reglene (spec 2.2, Design Notes): tomme felt vises som «–». Dato og
  // klokkeslett vises slik brukeren skrev dem, «{dato} kl. {klokkeslett}»; tid
  // tolkes og formateres bare på serveren (AD-9). Beløp med bare sifre vises som
  // «1 000 kr» med NBSP, som `kr` på serveren; annen tekst vises som den er, med « kr».

  var TOM = "–";
  var NBSP = "\u00a0";

  // Samme algoritme som `_kr_fra_sifre` i oppdrag/routes.py: nuller foran fjernes,
  // sifrene grupperes tre og tre fra høyre med NBSP. Ingen Intl (som kan mangle
  // norske data) og ingen tallkonvertering, så server og klient gir samme tekst.
  function kr(sifre) {
    sifre = sifre.replace(/^0+/, "") || "0";
    var forste = sifre.length % 3 || 3;
    var grupper = [sifre.slice(0, forste)];
    for (var i = forste; i < sifre.length; i += 3) {
      grupper.push(sifre.slice(i, i + 3));
    }
    return grupper.join(NBSP) + NBSP + "kr";
  }

  function pris(skjema) {
    var valgt = skjema.querySelector('input[name="tilbud"]:checked');
    var belop = skjema.elements.belop ? skjema.elements.belop.value.trim() : "";
    if (valgt && valgt.value === "uten") {
      return "Uten betaling";
    }
    if (!valgt || valgt.value !== "belop" || !belop) {
      return TOM;
    }
    var sifre = belop.replace(/\s/g, "");
    return /^[0-9]+$/.test(sifre) ? kr(sifre) : belop + NBSP + "kr";
  }

  function verdi(skjema, navn) {
    var felt = skjema.elements[navn];
    return felt && typeof felt.value === "string" ? felt.value.trim() : "";
  }

  function kobleTilForhandsvisning(kort) {
    var skjema = kort.closest("form");
    if (!skjema) {
      return;
    }
    function felt(navn) {
      return kort.querySelector('[data-felt="' + navn + '"]');
    }
    var postnummer = skjema.elements.postnummer;
    var poststed = postnummer && document.getElementById(postnummer.getAttribute("data-poststed"));

    function settTekst(element, tekst) {
      if (element && element.textContent !== tekst) {
        element.textContent = tekst;
      }
    }

    // Kategorimerket får ikonet klonet fra den valgte kategoriknappen.
    function settKategori() {
      var merke = felt("kategori");
      if (!merke) {
        return;
      }
      var valgt = skjema.querySelector('input[name="kategori"]:checked');
      var knapp = valgt && valgt.closest("label");
      var ikon = knapp && knapp.querySelector(".kategoriikon");
      var tekst = knapp && knapp.querySelector(".kategoriknapp__tekst");
      while (merke.firstChild) {
        merke.removeChild(merke.firstChild);
      }
      if (ikon) {
        var kopi = ikon.cloneNode(true);
        kopi.setAttribute("width", "18");
        kopi.setAttribute("height", "18");
        merke.appendChild(kopi);
      }
      var span = document.createElement("span");
      span.textContent = tekst ? tekst.textContent.trim() : TOM;
      merke.appendChild(span);
    }

    function oppdater() {
      settKategori();
      settTekst(felt("tittel"), verdi(skjema, "tittel") || TOM);
      var dato = verdi(skjema, "dato");
      var klokkeslett = verdi(skjema, "klokkeslett");
      settTekst(felt("tid"), dato && klokkeslett ? dato + " kl. " + klokkeslett : TOM);
      var nummer = verdi(skjema, "postnummer");
      var sted = poststed ? poststed.textContent.trim() : "";
      settTekst(felt("sted"), nummer ? (sted ? nummer + " " + sted : nummer) : TOM);
      settTekst(felt("pris"), pris(skjema));
    }

    skjema.addEventListener("input", oppdater);
    skjema.addEventListener("change", oppdater);
    if (poststed && window.MutationObserver) {
      new MutationObserver(oppdater).observe(poststed, { childList: true, characterData: true, subtree: true });
    }
    window.addEventListener("pageshow", oppdater);
    oppdater();
  }

  document.querySelectorAll("[data-forhandsvisning]").forEach(kobleTilForhandsvisning);
})();
