"""Arkitekturtest: importretning, forbudte mønstre og navn (AD-1, AD-11, AD-13, AR-21, AR-27).

Importretning (bare direkte piler): profil → oppdrag/identity, oppdrag → identity/ki,
alle → core. `core` importerer ingen slice. `app/__init__.py`, `app/seed.py` og
`app/admin.py` setter sammen appen og kan importere alt.
"""

from __future__ import annotations

import ast
import io
import re
import tokenize
from pathlib import Path

import pytest

from app import lag_app
from app.core.config import Settings
from app.core.sesjon import alle_ruter

ROT = Path(__file__).resolve().parents[2]
APP = ROT / "app"

LOVLIGE_IMPORTER = {
    "core": {"core"},
    "identity": {"identity", "core"},
    "ki": {"ki", "core"},
    "oppdrag": {"oppdrag", "identity", "ki", "core"},
    "profil": {"profil", "oppdrag", "identity", "core"},
}
SAMMENSETTING = {APP / "__init__.py", APP / "seed.py", APP / "admin.py"}

# AD-11: tillatt liste for |safe, Markup( og innerHTML. Skal være tom.
TILLATT_LISTE: set[str] = set()
FORBUDTE_MONSTRE = {
    "|safe": re.compile(r"\|\s*safe\b"),
    "Markup(": re.compile(r"\bMarkup\("),
    "innerHTML": re.compile(r"\binnerHTML\b"),
}


def python_filer(mappe: Path) -> list[Path]:
    return sorted(p for p in mappe.rglob("*.py") if "__pycache__" not in p.parts)


def importerte_moduler(fil: Path) -> set[str]:
    tre = ast.parse(fil.read_text(encoding="utf-8"), filename=str(fil))
    pakke = ".".join(fil.relative_to(ROT).with_suffix("").parts[:-1])
    moduler: set[str] = set()
    for node in ast.walk(tre):
        if isinstance(node, ast.Import):
            moduler.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                deler = pakke.split(".")
                base = ".".join(deler[: len(deler) - node.level + 1])
                moduler.add(f"{base}.{node.module}" if node.module else base)
            elif node.module:
                moduler.add(node.module)
    return moduler


def slice_for(fil: Path) -> str | None:
    deler = fil.relative_to(APP).parts
    return deler[0] if len(deler) > 1 else None


@pytest.mark.parametrize("fil", python_filer(APP), ids=lambda p: p.relative_to(ROT).as_posix())
def test_importretning(fil: Path) -> None:
    """AD-1: en slice importerer bare fra slicene pilene tillater."""
    if fil in SAMMENSETTING:
        return
    egen = slice_for(fil)
    assert egen in LOVLIGE_IMPORTER, f"Ukjent slice: {egen}"
    for modul in importerte_moduler(fil):
        deler = modul.split(".")
        if deler[0] != "app":
            continue
        assert len(deler) > 1, f"{fil.name} importerer `app` direkte"
        assert deler[1] in LOVLIGE_IMPORTER[egen], (
            f"{fil.relative_to(ROT).as_posix()} importerer {modul}, men {egen} kan bare importere "
            f"fra {sorted(LOVLIGE_IMPORTER[egen])} (AD-1)"
        )


def test_alle_slicene_finnes() -> None:
    for navn in LOVLIGE_IMPORTER:
        assert (APP / navn / "__init__.py").is_file(), navn


def test_ingen_forbudte_monstre_i_app() -> None:
    """AD-11: ingen |safe, Markup( eller innerHTML i app/."""
    funn = []
    for fil in sorted(APP.rglob("*")):
        if fil.suffix not in {".py", ".html", ".js", ".svg", ".css"}:
            continue
        tekst = fil.read_text(encoding="utf-8")
        for navn, monster in FORBUDTE_MONSTRE.items():
            if monster.search(tekst) and f"{fil.relative_to(ROT).as_posix()}:{navn}" not in TILLATT_LISTE:
                funn.append(f"{fil.relative_to(ROT).as_posix()}: {navn}")
    assert funn == []


def test_ingen_create_all() -> None:
    """AD-13: skjemaet endres bare med Alembic."""
    for fil in python_filer(APP) + python_filer(ROT / "migrations"):
        assert not re.search(r"\bcreate_all\(", fil.read_text(encoding="utf-8")), fil


def test_bare_config_leser_miljovariabler() -> None:
    """AD-14: all konfig går gjennom én Settings."""
    for fil in python_filer(APP):
        if fil == APP / "core" / "config.py":
            continue
        tekst = fil.read_text(encoding="utf-8")
        assert "os.environ" not in tekst and "getenv" not in tekst, fil


def test_identifikatorer_er_ascii() -> None:
    """Konvensjonen Navn: identifikatorer i ASCII (æ → ae, ø → o, å → a)."""
    feil = []
    for fil in python_filer(APP) + python_filer(ROT / "migrations") + python_filer(ROT / "tests"):
        kilde = fil.read_text(encoding="utf-8")
        for token in tokenize.generate_tokens(io.StringIO(kilde).readline):
            if token.type == tokenize.NAME and not token.string.isascii():
                feil.append(f"{fil.relative_to(ROT).as_posix()}:{token.start[0]} {token.string}")
    assert feil == []


def test_filer_leses_med_utf8() -> None:
    """AD-10: open()/read_text()/write_text() oppgir encoding."""
    for fil in python_filer(APP) + python_filer(ROT / "migrations"):
        for node in ast.walk(ast.parse(fil.read_text(encoding="utf-8"))):
            if not isinstance(node, ast.Call):
                continue
            navn = getattr(node.func, "attr", None) or getattr(node.func, "id", None)
            if navn not in {"open", "read_text", "write_text"}:
                continue
            modus = [a.value for a in node.args if isinstance(a, ast.Constant)]
            if any(isinstance(m, str) and "b" in m for m in modus):
                continue
            nokkelord = {k.arg for k in node.keywords}
            assert "encoding" in nokkelord, f"{fil.relative_to(ROT).as_posix()}:{node.lineno} {navn}()"


def test_rutenavn_er_unike_og_folger_monsteret() -> None:
    """AR-27: rutenavn er `<slice>.<handling>` og unike."""
    app = lag_app()
    navn = [r.name for r in alle_ruter(app.routes) if getattr(r, "name", None) and r.name != "static"]
    assert len(navn) >= 7  # inkluderte routere telles enkeltvis
    assert len(navn) == len(set(navn))
    for n in navn:
        slice_, _, handling = n.partition(".")
        assert slice_ in LOVLIGE_IMPORTER and handling, n


def _testruter(app_env: str) -> dict[str, str]:
    # Produksjon nekter SQLite i `Settings`, så miljøet byttes etter valideringen.
    # Om ruta finnes, avgjøres bare av APP_ENV.
    settings = Settings(
        _env_file=None, app_env="local", secret_key="x" * 32, database_url="sqlite:///:memory:"
    ).model_copy(update={"app_env": app_env})
    app = lag_app(settings=settings)
    return {
        getattr(r, "path", ""): getattr(r, "name", "")
        for r in alle_ruter(app.routes)
        if getattr(r, "path", "").startswith("/_test")
    }


@pytest.mark.parametrize("app_env", ["local", "production"])
def test_ingen_testruter_utenfor_test(app_env: str) -> None:
    """AD-14: `/_test`-ruter finnes aldri i `local` eller `production`."""
    assert _testruter(app_env) == {}


def test_test_har_bare_test_tilstand() -> None:
    """AD-14: i `test` finnes akkurat `/_test/tilstand`, med navnet `core.test_tilstand`."""
    assert _testruter("test") == {"/_test/tilstand": "core.test_tilstand"}


def test_workflows_bruker_aldri_pull_request_target() -> None:
    """Konvensjonen Konfig og hemmeligheter. Kommentarlinjer telles ikke."""
    workflows = list((ROT / ".github" / "workflows").glob("*.yml"))
    assert workflows
    for fil in workflows:
        tekst = fil.read_text(encoding="utf-8")
        assert not re.search(r"(?m)^[^#\n]*\bpull_request_target\b", tekst), fil


def test_deploy_jobben_kjorer_bare_fra_main() -> None:
    """AR-7, R4: `workflow_dispatch` fra en annen branch skal ikke publisere.

    Jobben `deploy` i `deploy.yml` har ref-vakten på main. Kommentarlinjer telles ikke.
    """
    tekst = (ROT / ".github" / "workflows" / "deploy.yml").read_text(encoding="utf-8")
    jobb = re.search(r"(?ms)^  deploy:\n(.*?)(?=^  \S|\Z)", tekst)
    assert jobb, "fant ikke jobben deploy"
    assert re.search(
        r"(?m)^    if: github\.ref == 'refs/heads/main'\s*$", jobb.group(1)
    ), "jobben deploy mangler if: github.ref == 'refs/heads/main'"
