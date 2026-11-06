"""Guards the google-adk version constraint in pyproject.toml."""

import tomllib
from pathlib import Path

PYPROJECT = Path(__file__).resolve().parent.parent / "pyproject.toml"


def _adk_dependencies() -> list[str]:
    data = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
    deps = data["project"]["dependencies"]
    return [d.replace(" ", "") for d in deps if d.replace(" ", "").startswith("google-adk")]


def test_google_adk_lower_bound_is_v2():
    assert "google-adk>=2.0.0" in _adk_dependencies()


def test_google_adk_no_upper_bound():
    for dep in _adk_dependencies():
        assert "<" not in dep, f"unexpected upper bound in {dep}"


def test_google_adk_no_compatible_release_operator():
    for dep in _adk_dependencies():
        assert "~=" not in dep, f"unexpected ~= operator in {dep}"
