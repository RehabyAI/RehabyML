"""
Angle Calculator - Compute shoulder angles from pose landmarks
"""

import numpy as np
from typing import Dict, Tuple


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
        
        for idx in required_landmarks:
            if landmarks[idx]["visibility"] < 0.5:
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