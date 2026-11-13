from pathlib import Path
from skill_lint.linter import lint_path

FIXTURES = Path(__file__).parent / "fixtures"


def _fails(name: str) -> set[str]:
    results = lint_path(FIXTURES / name)
    return {r["check"] for r in results if not r["ok"]}


def test_secret_and_exfil_detected():
    fails = _fails("secret-skill")
    assert any("github personal access token" in c for c in fails)
    assert any("prompt-injection" in c for c in fails)
    assert any("outbound http write" in c for c in fails)
    assert any("known exfil host" in c for c in fails)


def test_earlier_unsafe_yaml_not_hidden_by_later_safeloader():
    fails = _fails("yaml-mixed")
    assert any("yaml.load without SafeLoader" in c for c in fails)


def test_safe_yaml_stays_clean():
    fails = _fails("yaml-safe")
    assert not any("yaml.load" in c for c in fails)


def test_good_skill_still_clean_with_new_checks():
    fails = _fails("good-skill")
    assert fails == set()
