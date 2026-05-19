"""
Angle Calculator - Compute shoulder angles from pose landmarks
"""

import argparse
import json
import numpy as np
from typing import Dict, Tuple
import sys
import cv2
from pathlib import Path
from config import VISIBILITY_THRESHOLD, VERBOSE_VISIBILITY
from rep_counter import RepCounter



class AngleCalculator:
    """
    Calculate relevant angles for shoulder raise form analysis.
    
    Key metrics:
    1. Shoulder elevation angle: How high shoulder moved (relative to hip)
    2. Asymmetry: Difference between left and right shoulder height
    3. Trunk lean: Forward/backward deviation
    """
    
    @staticmethod
    def calculate_shoulder_elevation(
        shoulder_pos: Tuple[float, float, float],
        hip_pos: Tuple[float, float, float]
    ) -> float:
        """
        Calculate vertical distance between shoulder and hip (elevation angle).
        
        In a shoulder raise, the shoulder moves UP.
        We measure this as the vertical displacement.
        
        Args:
            shoulder_pos: (x, y, z) normalized coordinates (0-1)
            hip_pos: (x, y, z) normalized coordinates (0-1)
            
        Returns:
            Elevation in normalized coordinates (0-1 range, where higher = more elevation)
        """
        # In video coordinates, Y increases downward
        # So lower Y value = higher in image
        elevation = hip_pos[1] - shoulder_pos[1]
        return max(0, elevation)  # Clamp to 0 minimum
    
    @staticmethod
    def calculate_asymmetry(
        left_shoulder: Tuple[float, float, float],
        right_shoulder: Tuple[float, float, float],
        left_hip: Tuple[float, float, float],
        right_hip: Tuple[float, float, float]
    ) -> float:
        """
        Calculate asymmetry between left and right shoulder elevation.
        
        Asymmetry = |left_elevation - right_elevation|
        
        Args:
            left_shoulder: (x, y, z)
            right_shoulder: (x, y, z)
            left_hip: (x, y, z)
            right_hip: (x, y, z)
            
        Returns:
            Asymmetry score (0-1, where 0 = perfectly level)
        """
        left_elevation = AngleCalculator.calculate_shoulder_elevation(left_shoulder, left_hip)
        right_elevation = AngleCalculator.calculate_shoulder_elevation(right_shoulder, right_hip)
        
        asymmetry = abs(left_elevation - right_elevation)
        return min(asymmetry, 1.0)  # Clamp to 1.0 max
    
    @staticmethod
    def calculate_trunk_lean(
        left_shoulder: Tuple[float, float, float],
        right_shoulder: Tuple[float, float, float],
        left_hip: Tuple[float, float, float],
        right_hip: Tuple[float, float, float]
    ) -> float:
        """
        Calculate forward/backward trunk tilt.
        
        Ideal: Shoulders and hips should maintain similar horizontal alignment.
        Bad: If shoulders move significantly forward/backward relative to hips.
        
        Args:
            left_shoulder: (x, y, z)
            right_shoulder: (x, y, z)
            left_hip: (x, y, z)
            right_hip: (x, y, z)
            
        Returns:
            Trunk lean (0-1, where 0 = no lean)
        """
        # Calculate center of shoulders and hips
        shoulder_center_x = (left_shoulder[0] + right_shoulder[0]) / 2
        shoulder_center_y = (left_shoulder[1] + right_shoulder[1]) / 2
        
        hip_center_x = (left_hip[0] + right_hip[0]) / 2
        hip_center_y = (left_hip[1] + right_hip[1]) / 2
        
        # Lean = horizontal distance between shoulder and hip centers
        # (Forward/backward movement in camera view)
        lean = abs(shoulder_center_x - hip_center_x)
        return min(lean, 1.0)
    
    @staticmethod
    def calculate_all_angles(landmarks_dict: Dict) -> Dict:
        """
        Calculate all relevant angles from landmarks.
        
        Args:
            landmarks_dict: Output from PoseAnalyzer.analyze_frame()
            
        Returns:
            Dictionary with:
            - left_shoulder_elevation: float (0-1)
            - right_shoulder_elevation: float (0-1)
            - asymmetry: float (0-1)
            - trunk_lean: float (0-1)
            - is_valid: bool (all joints visible?)
        """
        result = {
            "left_shoulder_elevation": 0,
            "right_shoulder_elevation": 0,
            "asymmetry": 0,
            "trunk_lean": 0,
            "is_valid": False
        }
        
        if not landmarks_dict["has_pose"]:
            return result
        
        # Check visibility of key joints
        landmarks = landmarks_dict["landmarks"]
        required_landmarks = [11, 12, 23, 24]  # shoulders and hips
        
        # Use central visibility threshold from config
        for idx in required_landmarks:
            if landmarks[idx]["visibility"] < VISIBILITY_THRESHOLD:
                # Joint not clearly visible
                return result
        
        left_shoulder = landmarks_dict["left_shoulder"]
        right_shoulder = landmarks_dict["right_shoulder"]
        left_hip = landmarks_dict["left_hip"]
        right_hip = landmarks_dict["right_hip"]
        
        result["left_shoulder_elevation"] = AngleCalculator.calculate_shoulder_elevation(
            left_shoulder, left_hip
        )
        result["right_shoulder_elevation"] = AngleCalculator.calculate_shoulder_elevation(
            right_shoulder, right_hip
        )
        result["asymmetry"] = AngleCalculator.calculate_asymmetry(
            left_shoulder, right_shoulder, left_hip, right_hip
        )
        result["trunk_lean"] = AngleCalculator.calculate_trunk_lean(
            left_shoulder, right_shoulder, left_hip, right_hip
        )
        result["is_valid"] = True
        
        return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze shoulder raise form in a video")
    parser.add_argument("video_path", help="Path to input video file")
    parser.add_argument("--visibility", type=float, default=None,
                        help="Override visibility threshold for required landmarks (0-1)")
    parser.add_argument("--verbose", action="store_true", help="Enable per-frame visibility logging")
    parser.add_argument("-r", "--count-reps", action="store_true", help="Count shoulder raise repetitions")
    parser.add_argument("-q", "--quiet", action="store_true", help="Print only numeric overall score")
    parser.add_argument("-j", "--json", action="store_true", help="Print machine-readable JSON summary")



    args = parser.parse_args()
    

    if args.quiet and args.json:
        print("Error: --quiet and --json are mutually exclusive.")
        sys.exit(1)
    
    from pose_analyzer import PoseAnalyzer
    from form_scorer import FormScorer
    
    video_path = Path(args.video_path)
    quiet = args.quiet
    json_output = args.json
    
    if not video_path.exists():
        print(f"❌ Video not found: {video_path}")
        sys.exit(1)
    
    if not quiet and not json_output:
        print(f"📹 Processing: {video_path}")
    
    # Initialize components
    analyzer = PoseAnalyzer()
    scorer = FormScorer()
    rep_counter = RepCounter() if args.count_reps else None

    # Determine visibility threshold (CLI override wins)
    visibility_threshold = args.visibility if args.visibility is not None else VISIBILITY_THRESHOLD
    verbose = args.verbose or VERBOSE_VISIBILITY
    
    # Open video
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        print(f"❌ Failed to open video")
        sys.exit(1)
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    if not quiet and not json_output:
        print(f"📊 Frames: {total_frames}, FPS: {fps:.1f}")
    
    # Process video frames
    frame_count = 0
    valid_frames = 0
    scores = []
    
    if not quiet and not json_output:
        print("🔄 Analyzing frames...")
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Analyze pose
        landmarks = analyzer.analyze_frame(frame)

        # Optional per-frame visibility logging
        if verbose and not quiet and not json_output and landmarks.get("landmarks"):
            vis_list = [landmarks["landmarks"][i]["visibility"] for i in [11,12,23,24]]
            avg_vis = sum(vis_list) / len(vis_list)
            print(f"  Frame {frame_count}: vis={['{:.2f}'.format(v) for v in vis_list]} avg={avg_vis:.2f}")

        if landmarks["has_pose"]:
            valid_frames += 1
            
            # Calculate angles (this will check visibility against threshold)
            angles = AngleCalculator.calculate_all_angles(landmarks)
            
            if angles["is_valid"]:
                # Score the form
                result = scorer.score_form(angles)
                score = result["score"]
                scores.append(score)

                if rep_counter is not None:
                    elevation = RepCounter.get_average_elevation(angles)
                    rep_counter.add_sample(elevation)
                
                if frame_count % max(1, total_frames // 10) == 0 and not quiet and not json_output:
                    print(f"  Frame {frame_count}: ✅ Score: {score:.1f}/100")
        
        frame_count += 1
    
    cap.release()
    analyzer.close()
    
    rep_count = rep_counter.rep_count if rep_counter is not None else 0
    if args.quiet:
        if scores:
            avg_score = np.mean(scores)
            print(f"{avg_score:.1f}")
        else:
            print("0.0")
        sys.exit(0)
    if json_output:
        summary = {
            "total_frames": frame_count,
            "pose_frames": valid_frames,
            "scored_frames": len(scores),
            "average_score": round(float(np.mean(scores)), 1) if scores else 0.0,
            "min_score": round(float(np.min(scores)), 1) if scores else 0.0,
            "max_score": round(float(np.max(scores)), 1) if scores else 0.0,
            "rep_count": rep_count,
        }
        print(json.dumps(summary))
        sys.exit(0)
    # Print summary
    print("\n📊 Analysis Complete!")
    print(f"  Total frames: {frame_count}")
    print(f"  Frames with pose: {valid_frames}")
    if scores:
        avg_score = np.mean(scores)
        min_score = np.min(scores)
        max_score = np.max(scores)
        print(f"  Average score: {avg_score:.1f}/100")
        print(f"  Min/Max score: {min_score:.1f}/{max_score:.1f}")
        if rep_counter is not None:
            print(f"  Rep count: {rep_count}")
        print(f"\nOverall score: {avg_score:.1f}/100 (based on {len(scores)} scored frames)")
    else:
        print("  No valid scored frames (visibility thresholds may be too strict).")
        print(f"  Try lowering the visibility threshold in {Path('config.py').name} or review video quality.")
        print("\nOverall score: 0.0/100 (no scored frames)")