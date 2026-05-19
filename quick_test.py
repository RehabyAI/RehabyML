import sys
print("Starting test...")
print(f"Arguments: {sys.argv}")

try:
    from pose_analyzer import PoseAnalyzer
    print("✅ pose_analyzer imported")
except Exception as e:
    print(f"❌ Error importing pose_analyzer: {e}")

try:
    import cv2
    print("✅ cv2 imported")
except Exception as e:
    print(f"❌ Error importing cv2: {e}")

try:
    import mediapipe as mp
    print("✅ mediapipe imported")
except Exception as e:
    print(f"❌ Error importing mediapipe: {e}")

print("Test script complete")
