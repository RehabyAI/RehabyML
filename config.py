"""
config.py - Centralized configuration for form scoring thresholds

Edit these values to tune form scoring during Day 1.
"""

class FormScoringConfig:
    """
    Shoulder Raise Form Scoring Configuration
    
    TUNING GUIDE:
    - If all videos score too low (0-40): Decrease penalties
    - If all videos score too high (80-100): Increase penalties  
    - If good/bad videos too similar: Adjust thresholds
    - If not detecting real errors: Lower thresholds
    - If flagging false positives: Raise thresholds
    """
    
    # ====== ASYMMETRY SETTINGS ======
    # Asymmetry = |left_shoulder_elevation - right_shoulder_elevation|
    # Measures how level the shoulders are (0 = perfectly level, 1 = very uneven)
    
    ASYMMETRY_THRESHOLD = 0.08
    # Start penalizing when asymmetry exceeds this value
    # Lower = more strict (penalize small differences)
    # Higher = more lenient (only penalize big differences)
    # Try: 0.04 (strict), 0.08 (medium), 0.12 (lenient)
    
    ASYMMETRY_PENALTY_MULTIPLIER = 200
    # How many points to deduct per unit of asymmetry beyond threshold
    # Formula: penalty = (asymmetry - threshold) * multiplier
    # Lower = less harsh penalty
    # Higher = harsher penalty
    # Try: 50 (gentle), 150 (medium), 250 (strict)
    # Example: asymmetry=0.12, threshold=0.08, multiplier=200 
    #         → penalty = (0.12 - 0.08) * 200 = -8 points
    
    # ====== TRUNK LEAN SETTINGS ======
    # Trunk lean = forward/backward movement of torso
    # Measures how upright the person is (0 = straight, 1 = very leaned)
    
    TRUNK_LEAN_THRESHOLD = 0.05
    # Start penalizing when trunk lean exceeds this value
    # Lower = more strict
    # Higher = more lenient
    # Try: 0.03 (strict), 0.05 (medium), 0.08 (lenient)
    
    TRUNK_LEAN_PENALTY_MULTIPLIER = 150
    # How many points to deduct per unit of lean beyond threshold
    # Try: 50 (gentle), 150 (medium), 200 (strict)
    
    # ====== ELEVATION SETTINGS ======
    # Elevation = how high the shoulders moved up
    # Measures if person is actually doing a shoulder raise (0 = no movement, 1 = high raise)
    
    MIN_ELEVATION = 0.10
    # Minimum elevation required to count as a real shoulder raise
    # Below this = "not raising enough"
    # Try: 0.08 (low), 0.10 (medium), 0.15 (high)
    
    LOW_ELEVATION_PENALTY = 20
    # Points deducted if elevation is below MIN_ELEVATION
    # Try: 10 (gentle), 20 (medium), 30 (strict)
    
    MIN_ELEVATION_DIFF = 0.05
    # Maximum allowed difference between left and right elevation
    # If one shoulder lags more than this, flag an error
    # Try: 0.03 (strict), 0.05 (medium), 0.08 (lenient)


# ===== EXAMPLE TUNING SCENARIOS =====
"""
SCENARIO 1: All videos scoring too low (0-40 range)
→ Penalties are too harsh
→ Decrease ASYMMETRY_PENALTY_MULTIPLIER to 80
→ Decrease TRUNK_LEAN_PENALTY_MULTIPLIER to 50
→ Increase ASYMMETRY_THRESHOLD to 0.10
→ Increase TRUNK_LEAN_THRESHOLD to 0.07

SCENARIO 2: All videos scoring too high (80-100 range)
→ Penalties are too lenient
→ Increase ASYMMETRY_PENALTY_MULTIPLIER to 300
→ Increase TRUNK_LEAN_PENALTY_MULTIPLIER to 200
→ Decrease ASYMMETRY_THRESHOLD to 0.05
→ Decrease TRUNK_LEAN_THRESHOLD to 0.03

SCENARIO 3: Good form has errors (flagging false positives)
→ Thresholds are too strict
→ Increase all thresholds: ASYMMETRY to 0.12, LEAN to 0.08
→ Decrease penalties
→ Increase MIN_ELEVATION (require bigger movement)

SCENARIO 4: Bad form has no errors (missing real problems)
→ Thresholds are too lenient
→ Decrease all thresholds: ASYMMETRY to 0.04, LEAN to 0.02
→ Increase penalties
→ Decrease MIN_ELEVATION_DIFF to catch smaller imbalances
"""


# ===== EXPERIMENT LOG =====
# Keep track of what you tried and the results
"""
ATTEMPT 1:
  ASYMMETRY_PENALTY_MULTIPLIER = 200 (default)
  TRUNK_LEAN_PENALTY_MULTIPLIER = 150 (default)
  Result: Good=65, Bad1=55, Bad2=58 (too close, not separating)
  
ATTEMPT 2:
  ASYMMETRY_PENALTY_MULTIPLIER = 80
  TRUNK_LEAN_PENALTY_MULTIPLIER = 60
  Result: Good=88, Bad1=62, Bad2=65 (better separation!)
  
ATTEMPT 3:
  ASYMMETRY_THRESHOLD = 0.06 (stricter)
  TRUNK_LEAN_THRESHOLD = 0.03 (stricter)
  Result: Good=82, Bad1=48, Bad2=52 (PERFECT - clear separation)
  Final choice: Use Attempt 3 settings
"""