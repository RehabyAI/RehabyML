from form_scorer import FormScorer


def test_form_scorer_perfect():
    scorer = FormScorer()
    angles = {
        "is_valid": True,
        "left_shoulder_elevation": 0.30,
        "right_shoulder_elevation": 0.30,
        "asymmetry": 0.0,
        "trunk_lean": 0.0,
    }
    res = scorer.score_form(angles)
    assert res["score"] == 100
    assert res["errors"] == []
    assert res["severity"] == "good"


def test_form_scorer_asymmetry_penalty():
    scorer = FormScorer()
    angles = {
        "is_valid": True,
        "left_shoulder_elevation": 0.30,
        "right_shoulder_elevation": 0.18,
        "asymmetry": 0.12,
        "trunk_lean": 0.0,
    }
    res = scorer.score_form(angles)
    assert res["score"] < 100
    assert res["score"] >= 0
    assert res["severity"] in ("good", "warning", "critical")
