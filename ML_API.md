# ML Pipeline API Specification

## Overview
These 5 modules form the ML pipeline for shoulder raise form analysis:
- `pose_analyzer.py` - Detect pose landmarks from video frames
- `angle_calculator.py` - Calculate shoulder angles and metrics
- `form_scorer.py` - Score form (0-100) and detect errors
- `rep_counter.py` - Count shoulder raise repetitions
- `config.py` - Tuning parameters for all modules

## Backend Integration

### Input
```python
frame = cv2.imread("frame.jpg")  # BGR numpy array (H, W, 3)
# OR from base64
import base64
import numpy as np
frame = cv2.imdecode(np.frombuffer(base64.b64decode(frame_b64), np.uint8), cv2.IMREAD_COLOR)
```

### Pipeline
```python
from pose_analyzer import PoseAnalyzer
from angle_calculator import AngleCalculator
from form_scorer import FormScorer
from rep_counter import RepCounter

analyzer = PoseAnalyzer()
scorer = FormScorer()
counter = RepCounter()

# Step 1: Detect pose
landmarks = analyzer.analyze_frame(frame)
if not landmarks["has_pose"]:
    return {"error": "No pose detected"}

# Step 2: Calculate angles
angles = AngleCalculator.calculate_all_angles(landmarks)
if not angles["is_valid"]:
    return {"error": "Joints not clearly visible"}

# Step 3: Score form
score_result = scorer.score_form(angles)
score = score_result["score"]
errors = score_result["errors"]

# Step 4: Count reps
left_elev = angles["left_shoulder_elevation"]
right_elev = angles["right_shoulder_elevation"]
rep_state = counter.update(left_elev, right_elev)
rep_count = rep_state["rep_count"]
```

### Output (JSON)
```json
{
  "score": 85.3,
  "errors": ["Right shoulder elevated"],
  "rep_count": 3,
  "phase": "raising",
  "latency_ms": 47.2,
  "success": true
}
```

## Performance Targets
- Pose detection: <100ms per frame
- Full pipeline: <200ms per frame
- Pose detection rate: >90%
- Form scoring accuracy: >85% on test videos

## Tuning
Edit `config.py` to adjust:
- `ASYMMETRY_THRESHOLD` - How level shoulders must be
- `ASYMMETRY_PENALTY_MULTIPLIER` - Penalty for asymmetry
- `TRUNK_LEAN_THRESHOLD` - How upright trunk must be
- `TRUNK_LEAN_PENALTY_MULTIPLIER` - Penalty for leaning
- `MIN_ELEVATION` - Minimum shoulder raise height
- `VISIBILITY_THRESHOLD` - Minimum joint visibility confidence

## Testing
Test on video files:
```bash
python angle_calculator.py data/test_videos/good_form.mp4 -q
```

Expected scores:
- Good form: 80-100/100
- Bad form: 40-70/100
