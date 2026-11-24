// Poststed ved postnummerfeltet (UX-DR13). Progressiv forbedring: uten JS
// viser serveren poststedet etter innsending. Feltet har `data-poststed` med
// id-en til elementet som viser poststedet, og `data-postnumre` med adressen
// til postnumre.json. Lista hentes første gang feltet endres. Ingen validering
// her; reglene ligger på serveren (AD-2).
(function () {
  "use strict";

  var lister = {};

  function hentListe(adresse) {
    if (!lister[adresse]) {
      lister[adresse] = fetch(adresse, { credentials: "same-origin" })
        .then(function (svar) {
          if (!svar.ok) {
            throw new Error("postnumre.json: " + svar.status);
          }
          return svar.json();
        })
        .catch(function () {
          delete lister[adresse];
          return null;
        });
    }
    return lister[adresse];
  }

  function oppdater(felt) {
    var sted = document.getElementById(felt.getAttribute("data-poststed"));
    var adresse = felt.getAttribute("data-postnumre");
    if (!sted || !adresse) {
      return;
    }
    var nummer = felt.value.trim();
    if (!/^[0-9]{4}$/.test(nummer)) {
      sted.textContent = "";
      return;
    }
    hentListe(adresse).then(function (liste) {
      // Feltet kan ha endret seg mens lista ble hentet.
      if (felt.value.trim() !== nummer) {
        return;
      }
      sted.textContent = liste && Object.prototype.hasOwnProperty.call(liste, nummer) ? liste[nummer] : "";
    });
  }

  document.querySelectorAll("[data-poststed]").forEach(function (felt) {
    felt.addEventListener("input", function () {
      oppdater(felt);
    });
  });
})();
