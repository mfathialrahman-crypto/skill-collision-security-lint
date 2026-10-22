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


def test_trigger_overlap_detected():
    """Skills with low overall description Jaccard but high trigger-phrase overlap are reported."""
    from skill_collision.detector import detect_collisions
    report = detect_collisions(Path("tests/fixtures"))
    trigger_hits = [
        c for c in report["collisions"]
        if c["type"] == "trigger-overlap"
        and {c["a"], c["b"]} == {"trigger-overlap-a", "trigger-overlap-b"}
    ]
    assert trigger_hits, "Expected trigger-overlap between the planted pair"
    # Ensure the full-description check did not also fire for this pair
    desc_hits = [
        c for c in report["collisions"]
        if c["type"] == "description-overlap"
        and {c["a"], c["b"]} == {"trigger-overlap-a", "trigger-overlap-b"}
    ]
    assert not desc_hits, "Full description Jaccard should stay below threshold for this pair"
