import sys
print("🔍 DEBUG MODE")
print(f"Arguments: {sys.argv}")

from pathlib import Path
from pose_analyzer import PoseAnalyzer
from angle_calculator import AngleCalculator
from form_scorer import FormScorer
import cv2

video_path = Path(sys.argv[1])
print(f"📹 Video path: {video_path}")
print(f"📹 Exists: {video_path.exists()}")

if not video_path.exists():
    print(f"❌ Video not found!")
    sys.exit(1)

print("Initializing PoseAnalyzer...")
analyzer = PoseAnalyzer()
print("✅ PoseAnalyzer initialized")

print("Opening video...")
cap = cv2.VideoCapture(str(video_path))
print(f"✅ Video opened")

total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
fps = cap.get(cv2.CAP_PROP_FPS)
print(f"📊 Frames: {total_frames}, FPS: {fps}")

print("Processing first 10 frames...")
for i in range(min(10, total_frames)):
    ret, frame = cap.read()
    if not ret:
        print(f"⚠️ Frame {i} failed to read")
        break
    
    print(f"  Frame {i}: analyzing...", end=" ", flush=True)
    landmarks = analyzer.analyze_frame(frame)
    has_pose = landmarks["has_pose"]
    print(f"{'✅ Pose detected' if has_pose else '❌ No pose'}")

cap.release()
analyzer.close()
print("✅ Debug complete!")
