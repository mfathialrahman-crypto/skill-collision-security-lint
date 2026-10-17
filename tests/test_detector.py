"""Tests for collision detector."""

from pathlib import Path

from skill_collision.detector import detect_collisions


FIXTURES = Path(__file__).parent / "fixtures"


def test_scans_valid_skills():
    result = detect_collisions(FIXTURES)
    assert result["scanned"] >= 1
    assert isinstance(result["collisions"], list)


def test_exact_name_collision(tmp_path: Path):
    a = tmp_path / "skill-a"
    b = tmp_path / "skill-b"
    a.mkdir()
    b.mkdir()
    skill = "---\nname: same-name\ndescription: unique description for this skill only\n---\n"
    (a / "SKILL.md").write_text(skill)
    (b / "SKILL.md").write_text(skill)
    result = detect_collisions(tmp_path)
    assert result["scanned"] == 2
    assert any(c["type"] == "exact-name" for c in result["collisions"])
