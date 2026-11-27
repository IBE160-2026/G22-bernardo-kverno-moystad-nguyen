// Bilde av oppdraget i skjemaet (story 2.7, FR-27, AR-28, AD-18).
//
// Progressiv forbedring. Uten JS sendes fila som den er, «Hva viser bildet?»
// står alltid synlig, og serveren sjekker alt. Dette skriptet har ingen regler
// og avviser aldri en fil:
//
// - Ved `change` på filfeltet (`input[data-bilde]`) tegnes bildet på en canvas
//   med hvit bakgrunn, høyst 1 600 px, snudd etter EXIF-orienteringen, og fila
//   byttes med en JPEG (`toBlob("image/jpeg", 0.85)`) gjennom `DataTransfer`.
//   Da er fila under grensen på 4 MB, også fra mobilkameraet. Hvis noe feiler
//   (nettleseren kan ikke dekode fila, eller mangler `DataTransfer`), sendes
//   originalfila, og serveren avgjør.
// - Forhåndsvisningen («Slik vises oppdraget for andre.») viser bildet med
//   `URL.createObjectURL`.
// - «Hva viser bildet?» har `data-uten-bilde` når det ikke finnes et beholdt
//   eller lagret bilde. Da skjules feltet til en fil er valgt. CSS `:has()` kan
//   ikke se om et filfelt har en fil, derfor gjøres det her.
// - En innsending mens skaleringen pågår, stoppes på skjemaet (før sending.js
//   på `document`, som lar en stoppet innsending være) og sendes med
//   `requestSubmit(submitter)` når skaleringen er ferdig. Høyst én innsending
//   venter; flere trykk på knappen imens stoppes bare, så redigeringsskjemaet
//   (uten `skjema_id`) aldri sendes to ganger.
// - Når en ny fil velges, slås det skjulte `bilde_beholdt` av, så det ikke sendes
//   sammen med den nye fila. Fjernes fila, slås det på igjen.
// - «Fjern bildet» tar det beholdte eller lagrede bildet ut av forhåndsvisningen,
//   og setter det inn igjen når avkrysningen fjernes.
// - Ved `pageshow` (tilbakeknappen eller autoutfylling kan fylle filfeltet uten
//   `change`) behandles en fil i feltet på samme måte som ved `change`.
//
// Tekst og attributter settes bare med DOM-metoder.
(function () {
  "use strict";

  var MAKS = 1600;
  var KVALITET = 0.85;

  var felt = document.querySelector("input[data-bilde]");
  var skjema = felt && felt.form;
  if (!skjema) {
    return;
  }
  var bildetekst = document.getElementById(felt.getAttribute("data-bildetekst"));
  var forhandsvisning = skjema.querySelector('[data-forhandsvisning] [data-felt="bilde"]');
  // Det beholdte eller lagrede bildet serveren viste som miniatyr, eller null.
  var miniatyr = skjema.querySelector(".beholdt-bilde__miniatyr");
  var serverbilde = miniatyr ? miniatyr.getAttribute("src") : null;
  var fjern = skjema.querySelector('input[name="fjern_bilde"]');
  var beholdt = skjema.querySelector('input[name="bilde_beholdt"]');
  var objektUrl = null;
  var arbeid = null; // Promise mens et bilde skaleres
  var venter = false; // en innsending venter på skaleringen
  var teller = 0; // bare siste valg teller, hvis brukeren velger på nytt under skaleringen

  function harFil() {
    return Boolean(felt.files && felt.files.length);
  }

  function visBildetekst() {
    if (bildetekst && bildetekst.hasAttribute("data-uten-bilde")) {
      bildetekst.hidden = !harFil();
    }
  }

  function settForhandsvisning(kilde) {
    if (!forhandsvisning) {
      return;
    }
    if (objektUrl) {
      URL.revokeObjectURL(objektUrl);
      objektUrl = null;
    }
    if (kilde) {
      objektUrl = URL.createObjectURL(kilde);
      forhandsvisning.setAttribute("src", objektUrl);
      forhandsvisning.hidden = false;
    } else if (serverbilde && !(fjern && fjern.checked)) {
      forhandsvisning.setAttribute("src", serverbilde);
      forhandsvisning.hidden = false;
    } else {
      forhandsvisning.removeAttribute("src");
      forhandsvisning.hidden = true;
    }
  }

  function tilBlob(lerret) {
    return new Promise(function (ok, feil) {
      lerret.toBlob(function (blob) {
        if (blob) {
          ok(blob);
        } else {
          feil(new Error("toBlob"));
        }
      }, "image/jpeg", KVALITET);
    });
  }

  // Gir en mindre JPEG, eller kaster. Kalleren beholder da originalfila.
  function skaler(fil) {
    if (!window.createImageBitmap || !window.DataTransfer) {
      return Promise.reject(new Error("mangler støtte"));
    }
    return createImageBitmap(fil, { imageOrientation: "from-image" }).then(function (bilde) {
      var faktor = Math.min(1, MAKS / Math.max(bilde.width, bilde.height));
      var lerret = document.createElement("canvas");
      lerret.width = Math.max(1, Math.round(bilde.width * faktor));
      lerret.height = Math.max(1, Math.round(bilde.height * faktor));
      var tegning = lerret.getContext("2d");
      tegning.fillStyle = "#ffffff";
      tegning.fillRect(0, 0, lerret.width, lerret.height);
      tegning.drawImage(bilde, 0, 0, lerret.width, lerret.height);
      if (bilde.close) {
        bilde.close();
      }
      return tilBlob(lerret).then(function (blob) {
        // Et lite bilde som allerede er godt komprimert, sendes som det er.
        if (faktor === 1 && blob.size >= fil.size) {
          throw new Error("ikke mindre");
        }
        return blob;
      });
    });
  }

  function byttFil(blob, original) {
    var navn = (original.name || "bilde").replace(/\.[^.]*$/, "") + ".jpg";
    var ny = new File([blob], navn, { type: "image/jpeg", lastModified: Date.now() });
    var overforing = new DataTransfer();
    overforing.items.add(ny);
    felt.files = overforing.files;
  }

  function behandleValg() {
    visBildetekst();
    var nummer = ++teller;
    if (beholdt) {
      beholdt.disabled = harFil();
    }
    if (!harFil()) {
      arbeid = null;
      settForhandsvisning(null);
      return;
    }
    var original = felt.files[0];
    settForhandsvisning(original);
    var denne = skaler(original)
      .then(function (blob) {
        if (nummer === teller) {
          byttFil(blob, original);
          settForhandsvisning(blob);
        }
      })
      .catch(function () {
        // Originalfila sendes, og serveren avgjør (AD-18).
      })
      .then(function () {
        if (arbeid === denne) {
          arbeid = null;
        }
      });
    arbeid = denne;
  }

  felt.addEventListener("change", behandleValg);

  if (fjern) {
    fjern.addEventListener("change", function () {
      if (!harFil()) {
        settForhandsvisning(null);
      }
    });
    // Avkrysningen kan være satt før skriptet (defer) koblet til lytteren.
    if (fjern.checked && !harFil()) {
      settForhandsvisning(null);
    }
  }

  function send(knapp) {
    if (!skjema.requestSubmit) {
      skjema.submit();
    } else if (knapp && knapp.form === skjema) {
      skjema.requestSubmit(knapp);
    } else {
      skjema.requestSubmit();
    }
  }

  skjema.addEventListener("submit", function (hendelse) {
    if (hendelse.defaultPrevented || !arbeid) {
      return;
    }
    hendelse.preventDefault();
    if (venter) {
      return;
    }
    venter = true;
    var knapp = hendelse.submitter || null;
    arbeid.then(function () {
      venter = false;
      send(knapp);
    });
  });

  // Nettleseren kan fylle filfeltet igjen etter tilbakeknappen, uten `change`.
  window.addEventListener("pageshow", function () {
    if (harFil()) {
      behandleValg();
    } else {
      visBildetekst();
    }
  });
  visBildetekst();
})();
