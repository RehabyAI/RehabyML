"""
Pose Analyzer - Extract pose landmarks from video frames using MediaPipe
"""

import mediapipe as mp
import cv2
import numpy as np
from typing import Tuple, Dict, Optional


class PoseAnalyzer:
    """
    Uses MediaPipe Pose to detect body landmarks and extract shoulder positions.
    
    MediaPipe landmarks of interest for shoulder raise:
    - 11: Left shoulder
    - 12: Right shoulder
    - 23: Left hip
    - 24: Right hip
    - 0: Nose (for head reference)
    """
    
    def __init__(self):
        """Initialize MediaPipe Pose model"""
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,  # 0=light, 1=full (we want accuracy)
            smooth_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
    def analyze_frame(self, frame: np.ndarray) -> Dict:
        """
        Analyze a single frame and extract pose landmarks.
        
        Args:
            frame: BGR image from OpenCV (numpy array)
            
        Returns:
            Dictionary with:
            - landmarks: list of 33 MediaPipe landmarks (x, y, z, visibility)
            - has_pose: bool (True if pose detected)
            - left_shoulder: (x, y, z) normalized coordinates
            - right_shoulder: (x, y, z) normalized coordinates
            - left_hip: (x, y, z) normalized coordinates
            - right_hip: (x, y, z) normalized coordinates
        """
        # Convert BGR to RGB
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image_rgb.flags.writeable = False
        
        # Run inference
        results = self.pose.process(image_rgb)
        image_rgb.flags.writeable = True
        
        output = {
            "has_pose": False,
            "landmarks": None,
            "left_shoulder": None,
            "right_shoulder": None,
            "left_hip": None,
            "right_hip": None,
            "raw_results": results
        }
        
        if results.pose_landmarks:
            # Extract landmarks as list of (x, y, z, visibility)
            landmarks = []
            for lm in results.pose_landmarks.landmark:
                landmarks.append({
                    "x": lm.x,
                    "y": lm.y,
                    "z": lm.z,
                    "visibility": lm.visibility
                })
            
            output["landmarks"] = landmarks
            output["has_pose"] = True
            
            # Extract key shoulder/hip landmarks
            # Index 11 = left shoulder, 12 = right shoulder
            # Index 23 = left hip, 24 = right hip
            output["left_shoulder"] = (
                landmarks[11]["x"], 
                landmarks[11]["y"], 
                landmarks[11]["z"]
            )
            output["right_shoulder"] = (
                landmarks[12]["x"], 
                landmarks[12]["y"], 
                landmarks[12]["z"]
            )
            output["left_hip"] = (
                landmarks[23]["x"], 
                landmarks[23]["y"], 
                landmarks[23]["z"]
            )
            output["right_hip"] = (
                landmarks[24]["x"], 
                landmarks[24]["y"], 
                landmarks[24]["z"]
            )
        
        return output
    
    def draw_landmarks(self, frame: np.ndarray, landmarks_dict: Dict) -> np.ndarray:
        """
        Draw pose landmarks and skeleton on frame for visualization.
        
        Args:
            frame: Input BGR image
            landmarks_dict: Output from analyze_frame()
            
        Returns:
            Frame with drawn landmarks
        """
        if landmarks_dict["raw_results"].pose_landmarks:
            # Draw all landmarks and skeleton
            self.mp_drawing.draw_landmarks(
                frame,
                landmarks_dict["raw_results"].pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS,
                self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                self.mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2)
            )
        
        return frame
    
    def close(self):
        """Clean up resources"""
        self.pose.close()