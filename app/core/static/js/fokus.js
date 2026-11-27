// Fokus etter sidelasting og «Velg et annet postnummer» (AR-28, UX-DR21, UX-DR24).
// Progressiv forbedring: uten JS gir `autofocus` fokus der nettleseren støtter
// det, og lenken til `#postnummer` hopper til feltet. Ingen regler her; serveren
// avgjør hvor fokus skal stå (AD-2).
//
// - Et klikk på en lenke med `data-velg-felt` gir feltet i `href` fokus og
//   markerer innholdet, så brukeren kan skrive et nytt nummer med en gang.
// - Står fokus fortsatt på `<body>` etter lasting, får elementet med
//   `autofocus` fokus. Det gjelder nettlesere som ikke støtter `autofocus` på
//   en lenke.
(function () {
  "use strict";

  document.addEventListener("click", function (hendelse) {
    var lenke = hendelse.target.closest ? hendelse.target.closest("[data-velg-felt]") : null;
    if (!lenke) {
      return;
    }
    var href = lenke.getAttribute("href") || "";
    var felt = href.charAt(0) === "#" ? document.getElementById(href.slice(1)) : null;
    if (!felt) {
      return;
    }
    hendelse.preventDefault();
    felt.focus();
    if (typeof felt.select === "function") {
      felt.select();
    }
  });

  function fokuserAutofocus() {
    var aktiv = document.activeElement;
    if (aktiv && aktiv !== document.body && aktiv !== document.documentElement) {
      return;
    }
    var mal = document.querySelector("[autofocus]");
    if (mal) {
      mal.focus();
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", fokuserAutofocus);
  } else {
    fokuserAutofocus();
  }
})();
