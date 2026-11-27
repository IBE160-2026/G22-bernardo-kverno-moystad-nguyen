// «Nytt oppdrag» i to steg under 768 px (AR-28, UX-DR16, UX-DR22, UX-DR27).
//
// Progressiv forbedring: serveren rendrer alltid ett skjema på én skjerm, med
// to `section[data-steg]`. Serveren vet ikke skjermbredden. Under 768 px viser
// dette skriptet ett steg om gangen, og fra 768 px (og uten JS) står alt på én
// skjerm. Det finnes ingen egne URL-er eller POST per steg.
//
// Skriptet lastes uten `defer` rett etter skjemaet i oppdrag/skjema.html (bare når `to_steg`), så
// stegvisningen er satt før første opptegning (ingen blink og layoutskift).
//
// - `data-kun-en-skjerm` (de to `h2`) skjules i to steg, og `data-kun-steg`
//   («Neste», «Tilbake til steg 1») vises bare i to steg. `data-vis-i-steg="1"`
//   («Tilbake» øverst) vises på én skjerm og i steg 1.
// - `h1` og `<title>` hentes fra `data-overskrift[-n]` og `data-tittel[-n][-feil]`
//   på skjemaet, så tekstene bare står i malen. Ved stegbytte får `h1` fokus.
// - «Neste» (og Enter i steg 1) sjekker bare om felt med `data-tom` er tomme, og
//   viser da feiloppsummering og feltfeil med samme markup som serveren lager.
//   Alle andre regler sjekker serveren ved «Publiser».
// - Ved sidelasting med feil vises steget med feltet i den første lenken i
//   feiloppsummeringen. En lenke til et felt i det andre steget bytter steg.
// - Endres bredden, vises alt på én skjerm, eller steg 1 (steget med første
//   feil) under 768 px. Fokus flyttes ikke da, bortsett fra når feltet med
//   fokus havner i en skjult del. Da får `h1` fokus, så fokus ikke faller til
//   `<body>` (WCAG 2.4.3).
//
// Tekst settes bare med `textContent`.
(function () {
  "use strict";

  var skjema = document.querySelector("form[data-steg-skjema]");
  var h1 = document.querySelector("main h1");
  if (!skjema || !h1 || !window.matchMedia) {
    return;
  }
  var seksjoner = {
    1: skjema.querySelector('[data-steg="1"]'),
    2: skjema.querySelector('[data-steg="2"]'),
  };
  if (!seksjoner[1] || !seksjoner[2]) {
    return;
  }
  // Det motsatte av `min-width: 48em` i CSS, så ingen bredde (brøkdeler ved zoom) faller mellom.
  var smal = window.matchMedia("not all and (min-width: 48em)");
  var SVG = "http://www.w3.org/2000/svg";
  var steg = 1;

  function oppsummering() {
    return document.getElementById("feiloppsummering");
  }

  function stegFor(element) {
    var seksjon = element && element.closest("[data-steg]");
    return seksjon ? Number(seksjon.getAttribute("data-steg")) : null;
  }

  function malForLenke(lenke) {
    var href = lenke.getAttribute("href") || "";
    return href.charAt(0) === "#" ? document.getElementById(href.slice(1)) : null;
  }

  function stegMedForsteFeil() {
    var boks = oppsummering();
    var lenke = boks && boks.querySelector('a[href^="#"]');
    return (lenke && stegFor(malForLenke(lenke))) || 1;
  }

  function vis() {
    var toSteg = smal.matches;
    [1, 2].forEach(function (n) {
      seksjoner[n].hidden = toSteg && n !== steg;
    });
    document.querySelectorAll("[data-kun-steg]").forEach(function (element) {
      element.hidden = !toSteg;
    });
    document.querySelectorAll("[data-kun-en-skjerm]").forEach(function (element) {
      element.hidden = toSteg;
    });
    document.querySelectorAll("[data-vis-i-steg]").forEach(function (element) {
      element.hidden = toSteg && Number(element.getAttribute("data-vis-i-steg")) !== steg;
    });
    var nokkel = toSteg ? "-" + steg : "";
    h1.textContent = skjema.getAttribute("data-overskrift" + nokkel);
    document.title = skjema.getAttribute("data-tittel" + nokkel + (oppsummering() ? "-feil" : ""));
  }

  function byttTil(n) {
    steg = n;
    vis();
    h1.focus();
  }

  // ---------- tomme felt ved «Neste» ----------

  function feltene(felt) {
    return felt.tagName === "FIELDSET" ? Array.from(felt.querySelectorAll("input")) : [felt];
  }

  function erTomt(felt) {
    if (felt.tagName === "FIELDSET") {
      return !felt.querySelector("input:checked");
    }
    return felt.value.trim() === "";
  }

  function varselikon() {
    var svg = document.createElementNS(SVG, "svg");
    var egenskaper = {
      class: "ikon", "aria-hidden": "true", focusable: "false", width: "20", height: "20",
      viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", "stroke-width": "2",
      "stroke-linecap": "round", "stroke-linejoin": "round",
    };
    Object.keys(egenskaper).forEach(function (navn) {
      svg.setAttribute(navn, egenskaper[navn]);
    });
    ["M12 3 2 20h20L12 3z", "M12 10v4", "M12 17h.01"].forEach(function (d) {
      var sti = document.createElementNS(SVG, "path");
      sti.setAttribute("d", d);
      svg.appendChild(sti);
    });
    return svg;
  }

  function lag(tag, klasse, tekst) {
    var element = document.createElement(tag);
    if (klasse) {
      element.className = klasse;
    }
    if (tekst !== undefined) {
      element.textContent = tekst;
    }
    return element;
  }

  // Fjerner feilene «Neste» la til. Feil fra serveren står urørt.
  function fjernKlientfeil() {
    document.querySelectorAll("[data-klientfeil]").forEach(function (element) {
      element.remove();
    });
    document.querySelectorAll("[data-klientugyldig]").forEach(function (element) {
      var id = element.getAttribute("data-klientugyldig");
      var ider = (element.getAttribute("aria-describedby") || "").split(/\s+/).filter(function (verdi) {
        return verdi && verdi !== id;
      });
      if (ider.length) {
        element.setAttribute("aria-describedby", ider.join(" "));
      } else {
        element.removeAttribute("aria-describedby");
      }
      element.removeAttribute("aria-invalid");
      element.removeAttribute("data-klientugyldig");
    });
  }

  // Samme markup som makroen `feltfeil()`, og feltene får aria-invalid og aria-describedby.
  function settFeltfeil(felt) {
    var inndata = feltene(felt);
    var id = inndata[0].name + "-feil";
    var gammel = document.getElementById(id);
    if (gammel) {
      gammel.remove();
    }
    var feil = lag("p", "feltfeil");
    feil.id = id;
    feil.setAttribute("data-klientfeil", "");
    feil.appendChild(varselikon());
    feil.appendChild(lag("span", "", felt.getAttribute("data-tom")));
    (felt.tagName === "FIELDSET" ? felt : felt.closest(".felt") || felt.parentNode).appendChild(feil);
    // En feil fra serveren ved samme felt er nå erstattet, så `fjernKlientfeil`
    // rydder feltet helt når det ikke lenger er tomt.
    inndata.forEach(function (element) {
      var ider = (element.getAttribute("aria-describedby") || "").split(/\s+/).filter(Boolean);
      if (ider.indexOf(id) === -1) {
        ider.push(id);
        element.setAttribute("aria-describedby", ider.join(" "));
      }
      element.setAttribute("aria-invalid", "true");
      element.setAttribute("data-klientugyldig", id);
    });
  }

  // Samme markup som makroen `meldinger()`: tabindex="-1" og ingen role.
  function lagOppsummering(mangler) {
    var boks = lag("div", "melding melding--feil");
    boks.id = "feiloppsummering";
    boks.tabIndex = -1;
    boks.setAttribute("data-klientfeil", "");
    var overskrift = lag("h2", "melding__overskrift");
    overskrift.appendChild(varselikon());
    overskrift.appendChild(lag("span", "", "Skjemaet har " + mangler.length + " feil"));
    boks.appendChild(overskrift);
    var liste = lag("ul", "melding__liste");
    mangler.forEach(function (felt) {
      var lenke = lag("a", "", felt.getAttribute("data-tom"));
      lenke.href = "#" + feltene(felt)[0].id;
      var punkt = lag("li");
      punkt.appendChild(lenke);
      liste.appendChild(punkt);
    });
    boks.appendChild(liste);
    return boks;
  }

  function neste() {
    fjernKlientfeil();
    var mangler = Array.from(seksjoner[1].querySelectorAll("[data-tom]")).filter(erTomt);
    if (!mangler.length) {
      byttTil(2);
      return;
    }
    var gammel = oppsummering();
    if (gammel) {
      gammel.remove();
    }
    mangler.forEach(settFeltfeil);
    var boks = lagOppsummering(mangler);
    h1.insertAdjacentElement("afterend", boks);
    vis();
    boks.focus();
  }

  // ---------- lyttere ----------

  h1.setAttribute("tabindex", "-1");

  skjema.querySelectorAll("[data-neste]").forEach(function (knapp) {
    knapp.addEventListener("click", neste);
  });
  skjema.querySelectorAll("[data-tilbake-steg]").forEach(function (knapp) {
    knapp.addEventListener("click", function () {
      byttTil(1);
    });
  });

  // Enter i et felt i steg 1 sender skjemaet. I to steg virker det som «Neste».
  // Lytteren står på skjemaet, så sending.js (på document) ser at innsendingen er stoppet.
  skjema.addEventListener("submit", function (hendelse) {
    if (smal.matches && steg === 1) {
      hendelse.preventDefault();
      neste();
    }
  });

  // En lenke i feiloppsummeringen til et felt i det andre steget bytter steg først.
  document.addEventListener("click", function (hendelse) {
    var lenke = hendelse.target.closest && hendelse.target.closest("#feiloppsummering a[href^='#']");
    if (!lenke || !smal.matches) {
      return;
    }
    var mal = malForLenke(lenke);
    var malsteg = stegFor(mal);
    if (!mal || !malsteg || malsteg === steg) {
      return;
    }
    hendelse.preventDefault();
    steg = malsteg;
    vis();
    mal.focus();
  });

  function vedNyBredde() {
    // Husket før `vis()`, fordi nettleseren kan flytte fokus til `<body>` når feltet skjules.
    var aktiv = document.activeElement;
    if (smal.matches) {
      steg = stegMedForsteFeil();
    }
    vis();
    if (aktiv && aktiv !== document.body && aktiv.closest("[hidden]")) {
      h1.focus();
    }
  }
  if (smal.addEventListener) {
    smal.addEventListener("change", vedNyBredde);
  } else if (smal.addListener) {
    smal.addListener(vedNyBredde);
  }

  steg = stegMedForsteFeil();
  vis();
})();
