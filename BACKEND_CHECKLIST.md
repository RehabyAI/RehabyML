# Backend Integration Checklist

## Before handing off to Frontend:

- [ ] /analyze-frame endpoint built
- [ ] Accepts base64 frame in JSON
- [ ] Calls all 5 ML modules in sequence
- [ ] Returns JSON with score, errors, rep_count
- [ ] Latency measured (<200ms target)
- [ ] Error handling (no pose, joints not visible, etc.)
- [ ] Tested on 3 sample frames
- [ ] Endpoint documented in README

## Testing command:
```bash
# Save a test frame as base64 and POST to endpoint
python -c "
import cv2
import base64
import requests

frame = cv2.imread('data/test_videos/frame.jpg')
_, buffer = cv2.imencode('.jpg', frame)
b64 = base64.b64encode(buffer).decode()

response = requests.post('http://localhost:8000/analyze-frame', 
    json={'frame': b64})
print(response.json())
"
```

## Expected response:
```json
{
  "score": 85.3,
  "errors": ["Right shoulder elevated"],
  "rep_count": 3,
  "phase": "raising",
  "success": true
}
```