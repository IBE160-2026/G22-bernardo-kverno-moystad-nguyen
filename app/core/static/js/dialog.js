// Bekreftelsesdialoger (AR-28, NFR-8, UX-DR18, EXPERIENCE.md § dialog).
//
// Progressiv forbedring: en handling som må bekreftes, er en lenke til
// bekreftelsessiden (GET), med `data-dialog="<id>"`. Siden har også en native
// `<dialog id="<id>">` fra makroen `bekreft_dialog`, med det samme innholdet.
// Uten JS, eller i en nettleser uten `showModal`, følges lenken. Med JS:
//
// - Et klikk på lenken åpner dialogen med `showModal()`, og spørsmålet
//   (overskriften med `tabindex="-1"`) får fokus, så det leses opp.
// - Tab og Shift+Tab går rundt i dialogen, så fokus aldri går til nettleserens
//   adresselinje (det varierer mellom nettlesere).
// - Esc (nettleserens egen `cancel`) og knapper med `data-lukk-dialog` lukker
//   dialogen, og fokus går tilbake til lenken som åpnet den.
// - Et klikk på sløret lukker ikke dialogen, så den ikke lukkes ved et uhell.
// - Bare én dialog er åpen om gangen.
// - Klikk med Ctrl, Cmd, Shift eller Alt og midtklikk følger lenken som vanlig.
//
// Ingen regler her: serveren avgjør om handlingen er lov. Tekst settes aldri med JS.
(function () {
  "use strict";

  var FOKUSERBARE =
    'a[href], button:not([disabled]), input:not([type="hidden"]):not([disabled]), ' +
    'select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])';

  function apenDialog() {
    return document.querySelector("dialog[open]");
  }

  function fokuserbare(dialog) {
    return Array.prototype.filter.call(dialog.querySelectorAll(FOKUSERBARE), function (element) {
      return element.getClientRects().length > 0;
    });
  }

  function apne(dialog, lenke) {
    dialog.showModal();
    dialog.addEventListener(
      "close",
      function () {
        if (document.contains(lenke)) {
          lenke.focus();
        }
      },
      { once: true }
    );
    var sporsmal = dialog.querySelector('[tabindex="-1"]');
    if (sporsmal) {
      sporsmal.focus();
    }
  }

  document.addEventListener("click", function (hendelse) {
    if (!hendelse.target.closest) {
      return;
    }
    var lenke = hendelse.target.closest("a[data-dialog]");
    if (lenke) {
      // Ny fane, nytt vindu og midtklikk får nettleserens vanlige oppførsel.
      if (
        hendelse.defaultPrevented ||
        hendelse.button !== 0 ||
        hendelse.ctrlKey ||
        hendelse.metaKey ||
        hendelse.shiftKey ||
        hendelse.altKey
      ) {
        return;
      }
      var dialog = document.getElementById(lenke.getAttribute("data-dialog"));
      if (!dialog || typeof dialog.showModal !== "function") {
        return; // lenken følges til bekreftelsessiden
      }
      hendelse.preventDefault();
      if (!apenDialog()) {
        apne(dialog, lenke);
      }
      return;
    }
    var lukk = hendelse.target.closest("[data-lukk-dialog]");
    if (lukk) {
      var egen = lukk.closest("dialog");
      if (egen && egen.open) {
        egen.close();
      }
    }
  });

  document.addEventListener("keydown", function (hendelse) {
    if (hendelse.key !== "Tab") {
      return;
    }
    var dialog = apenDialog();
    if (!dialog) {
      return;
    }
    var liste = fokuserbare(dialog);
    if (!liste.length) {
      return;
    }
    var forste = liste[0];
    var siste = liste[liste.length - 1];
    var aktiv = document.activeElement;
    var iLista = liste.indexOf(aktiv) !== -1;
    if (hendelse.shiftKey) {
      if (aktiv === forste || !iLista) {
        hendelse.preventDefault();
        siste.focus();
      }
    } else if (aktiv === siste || !dialog.contains(aktiv)) {
      hendelse.preventDefault();
      forste.focus();
    }
  });
})();
