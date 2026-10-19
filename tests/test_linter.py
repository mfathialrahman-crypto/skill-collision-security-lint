"""Regression tests for skill-lint."""

from pathlib import Path

from skill_lint.linter import lint_path


FIXTURES = Path(__file__).parent / "fixtures"


def test_good_skill_all_pass():
    results = lint_path(FIXTURES / "good-skill")
    assert all(r["ok"] for r in results), [r for r in results if not r["ok"]]
    assert any(r["check"] == "name-format" and r["ok"] for r in results)


def test_bad_skill_fails_expected():
    results = lint_path(FIXTURES / "bad-skill")
    fails = {r["check"] for r in results if not r["ok"]}
    assert "name-present" in fails or "name-format" in fails
    assert any("eval" in r["check"] and not r["ok"] for r in results)
    assert any("rm -rf" in r["check"] and not r["ok"] for r in results)


def test_description_length_message_is_valid():
    # Ensure the previously broken f-string path still works
    results = lint_path(FIXTURES / "good-skill")
    length = next(r for r in results if r["check"] == "description-length")
    assert length["ok"] is True
    assert "len=" in length["message"]

def test_unsafe_patterns_detected():
    results = lint_path(FIXTURES / "unsafe-skill")
    fails = {r["check"] for r in results if not r["ok"]}
    assert any("pickle.loads" in r["check"] and not r["ok"] for r in results)
    assert any("base64" in r["check"] and not r["ok"] for r in results)
    # yaml.load without SafeLoader should be flagged
    assert any("yaml.load" in r["check"] and not r["ok"] for r in results)
