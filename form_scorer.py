"""
Form Scorer - Convert angle measurements into form score (0-100) and error feedback
"""

from typing import Dict, List
from angle_calculator import AngleCalculator
from config import FormScoringConfig


class FormScorer:
    """
    Score shoulder raise form (0-100).
    
    Score breakdown:
    - Start: 100
    - Penalty: Asymmetry (shoulders not level)
    - Penalty: Trunk lean (leaning forward/backward)
    - Penalty: Low elevation (not raising enough)
    - Minimum: 0, Maximum: 100
    """
    
    def __init__(self, config: FormScoringConfig = None):
        """
        Initialize form scorer.
        
        Args:
            config: FormScoringConfig object (uses defaults if None)
        """
        self.config = config or FormScoringConfig()
    
    def score_form(self, angles: Dict) -> Dict:
        """
        Score the current form and generate error messages.
        
        Args:
            angles: Dictionary from AngleCalculator.calculate_all_angles()
            
        Returns:
            Dictionary with:
            - score: 0-100 form score
            - errors: List of error messages (empty if form is good)
            - severity: "good" / "warning" / "critical"
            - details: Debug info on how score was calculated
        """
        
        result = {
            "score": 100,
            "errors": [],
            "severity": "good",
            "details": {}
        }
        
        # If pose not detected or joints not visible
        if not angles["is_valid"]:
            result["score"] = 0
            result["errors"] = ["Cannot detect pose - check camera angle and lighting"]
            result["severity"] = "critical"
            return result
        
        left_elev = angles["left_shoulder_elevation"]
        right_elev = angles["right_shoulder_elevation"]
        asymmetry = angles["asymmetry"]
        lean = angles["trunk_lean"]
        
        # ---- Asymmetry check ----
        if asymmetry > self.config.ASYMMETRY_THRESHOLD:
            penalty = (asymmetry - self.config.ASYMMETRY_THRESHOLD) * self.config.ASYMMETRY_PENALTY_MULTIPLIER
            result["score"] -= penalty
            
            # Determine which shoulder is higher
            if left_elev > right_elev:
                result["errors"].append("Right shoulder elevated - level both shoulders")
            else:
                result["errors"].append("Left shoulder elevated - level both shoulders")
            
            result["details"]["asymmetry_penalty"] = penalty
        
        # ---- Trunk lean check ----
        if lean > self.config.TRUNK_LEAN_THRESHOLD:
            penalty = (lean - self.config.TRUNK_LEAN_THRESHOLD) * self.config.TRUNK_LEAN_PENALTY_MULTIPLIER
            result["score"] -= penalty
            result["errors"].append("Trunk leaning - keep chest upright")
            result["details"]["lean_penalty"] = penalty
        
        # ---- Elevation check ----
        avg_elevation = (left_elev + right_elev) / 2
        
        if avg_elevation < self.config.MIN_ELEVATION:
            result["score"] -= self.config.LOW_ELEVATION_PENALTY
            result["errors"].append("Raise shoulders higher")
            result["details"]["elevation_penalty"] = self.config.LOW_ELEVATION_PENALTY
        
        # ---- Min elevation difference (one shoulder lags) ----
        elev_diff = abs(left_elev - right_elev)
        if avg_elevation > self.config.MIN_ELEVATION and elev_diff > self.config.MIN_ELEVATION_DIFF:
            # One shoulder is raising significantly less than the other
            if left_elev < right_elev:
                if "Left shoulder elevated" not in result["errors"]:
                    result["errors"].append("Left shoulder lagging - raise both equally")
            else:
                if "Right shoulder elevated" not in result["errors"]:
                    result["errors"].append("Right shoulder lagging - raise both equally")
        
        # ---- Clamp score ----
        result["score"] = max(0, min(100, result["score"]))
        
        # ---- Determine severity ----
        if result["score"] >= 75:
            result["severity"] = "good"
        elif result["score"] >= 50:
            result["severity"] = "warning"
        else:
            result["severity"] = "critical"
        
        # ---- If score is good, no errors ----
        if result["score"] >= 80:
            result["errors"] = []
        
        return result
    
    def score_frame(self, landmarks_dict: Dict) -> Dict:
        """
        Convenience method: Score directly from landmarks dict.
        
        Args:
            landmarks_dict: Output from PoseAnalyzer.analyze_frame()
            
        Returns:
            Scoring result (same format as score_form)
        """
        angles = AngleCalculator.calculate_all_angles(landmarks_dict)
        return self.score_form(angles)
