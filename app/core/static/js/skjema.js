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
})();
