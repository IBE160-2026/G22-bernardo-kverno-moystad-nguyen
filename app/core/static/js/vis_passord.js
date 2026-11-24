// «Vis passord» (UX-DR13). Progressiv forbedring: uten JS er knappen skjult
// (`hidden`), og feltet virker som vanlig. Knappeteksten endres ikke;
// `aria-pressed` forteller om passordet vises.
(function () {
  "use strict";

  function kobleTil(knapp) {
    var felt = document.getElementById(knapp.getAttribute("aria-controls"));
    if (!felt) {
      return;
    }
    knapp.hidden = false;
    knapp.addEventListener("click", function () {
      var vises = knapp.getAttribute("aria-pressed") === "true";
      felt.type = vises ? "password" : "text";
      knapp.setAttribute("aria-pressed", vises ? "false" : "true");
    });
  }

  function skjulAlle() {
    // Passordet skal aldri sendes eller gjenopprettes som synlig tekst.
    document.querySelectorAll("[data-vis-passord]").forEach(function (knapp) {
      var felt = document.getElementById(knapp.getAttribute("aria-controls"));
      if (felt) {
        felt.type = "password";
      }
      knapp.setAttribute("aria-pressed", "false");
    });
  }

  document.querySelectorAll("[data-vis-passord]").forEach(kobleTil);
  document.addEventListener("submit", skjulAlle);
  window.addEventListener("pageshow", skjulAlle);
})();
