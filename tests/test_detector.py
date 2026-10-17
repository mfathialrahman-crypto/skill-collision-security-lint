"""Tests for collision detector."""

from pathlib import Path

from skill_collision.detector import detect_collisions


FIXTURES = Path(__file__).parent / "fixtures"


def test_scans_valid_skills():
    result = detect_collisions(FIXTURES)
    assert result["scanned"] >= 5, f"expected ≥5 fixtures, got {result['scanned']}"
    assert isinstance(result["collisions"], list)


def test_planted_description_overlap_detected():
    result = detect_collisions(FIXTURES)
    pairs = {(c["a"], c["b"]) for c in result["collisions"] if c["type"] == "description-overlap"}
    # collision-a and collision-b were designed to share high token overlap
    assert ("collision-a", "collision-b") in pairs or ("collision-b", "collision-a") in pairs


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
