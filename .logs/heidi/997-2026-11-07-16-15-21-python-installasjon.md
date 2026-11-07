# Python-installasjon

## 2026-11-07 kl. 16:15 — Heidi

### Oppgave
Heidi spurte om Python må installeres i prosjektmappa (svar: nei, Python installeres for hele maskinen, og bare det virtuelle miljøet `.venv` hører hjemme i prosjektet). Deretter ba Heidi om at Python ble installert.

### Plan
- Sjekket først maskinen: `python` var ikke installert, og kommandoen sendte til Microsoft Store.
- Sjekket repoet: BMAD-skriptene i `_bmad/scripts/` krever Python 3.11 eller nyere, og `.venv/` står allerede i `.gitignore`.
- Installerte nyeste stabile Python fra winget, bare for brukeren (trenger ikke administratorrettigheter), lagt til i PATH og med `py`-launcheren.

### Resultat
- Installert Python 3.14.10 med `winget install --id Python.Python.3.14 --scope user --custom "PrependPath=1 Include_launcher=1"`.
- Plassering: `C:\Users\heidi\AppData\Local\Programs\Python\Python314\`.
- Verifisert: `python --version` og `py --version` gir begge 3.14.10. Python-mappene ligger foran `WindowsApps` i bruker-PATH, så Store-snarveien tar ikke over.
- Ingen endringer i prosjektfilene. Ingen `.venv` er laget ennå.
- Nye terminaler og VS Code må startes på nytt før de finner `python`.

### Åpne punkter
- README bør beskrive Python-kravet (3.11 eller nyere for BMAD-skriptene) og hvordan man lager `.venv`, hvis appen også skal bruke Python. Avklares etter `bmad-architecture`.
