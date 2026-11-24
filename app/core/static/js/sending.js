// Sending (UX-DR28). Knappen som sendte skjemaet, får `aria-disabled="true"`
// til svaret kommer, og en ny innsending (dobbeltklikk eller Enter) stoppes.
// Tilstanden nullstilles ved `pageshow`, så knappen virker igjen etter
// tilbakeknappen. Uten JS avviser serveren duplikater (AD-2).
(function () {
  "use strict";

  var MERKE = "data-sender";

  document.addEventListener("submit", function (hendelse) {
    var skjema = hendelse.target;
    if (skjema.hasAttribute(MERKE)) {
      hendelse.preventDefault();
      return;
    }
    var knapp = hendelse.submitter || skjema.querySelector('[type="submit"]');
    skjema.setAttribute(MERKE, "");
    if (knapp) {
      knapp.setAttribute("aria-disabled", "true");
      knapp.setAttribute(MERKE, "");
    }
  });

  window.addEventListener("pageshow", function () {
    document.querySelectorAll("[" + MERKE + "]").forEach(function (element) {
      element.removeAttribute(MERKE);
      if (element.getAttribute("aria-disabled") === "true") {
        element.removeAttribute("aria-disabled");
      }
    });
  });
})();
