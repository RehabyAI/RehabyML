from angle_calculator import AngleCalculator


def make_landmarks(left_sh_y=0.4, right_sh_y=0.4, left_hip_y=0.6, right_hip_y=0.6, vis=1.0):
    landmarks = [{"x": 0.5, "y": 0.5, "z": 0.0, "visibility": vis} for _ in range(33)]
    landmarks[11] = {"x": 0.2, "y": left_sh_y, "z": 0.0, "visibility": vis}
    landmarks[12] = {"x": 0.8, "y": right_sh_y, "z": 0.0, "visibility": vis}
    landmarks[23] = {"x": 0.2, "y": left_hip_y, "z": 0.0, "visibility": vis}
    landmarks[24] = {"x": 0.8, "y": right_hip_y, "z": 0.0, "visibility": vis}
    return landmarks


def test_calculate_all_angles_valid():
    lm = make_landmarks()
    landmarks_dict = {
        "has_pose": True,
        "landmarks": lm,
        "left_shoulder": (lm[11]["x"], lm[11]["y"], lm[11]["z"]),
        "right_shoulder": (lm[12]["x"], lm[12]["y"], lm[12]["z"]),
        "left_hip": (lm[23]["x"], lm[23]["y"], lm[23]["z"]),
        "right_hip": (lm[24]["x"], lm[24]["y"], lm[24]["z"]),
    }

    res = AngleCalculator.calculate_all_angles(landmarks_dict)

    assert res["is_valid"] is True
    assert abs(res["left_shoulder_elevation"] - 0.2) < 1e-6
    assert abs(res["right_shoulder_elevation"] - 0.2) < 1e-6
    assert abs(res["asymmetry"]) < 1e-6
    assert abs(res["trunk_lean"]) < 1e-6


def test_calculate_all_angles_visibility_blocked():
    lm = make_landmarks(vis=0.2)
    landmarks_dict = {
        "has_pose": True,
        "landmarks": lm,
        "left_shoulder": (lm[11]["x"], lm[11]["y"], lm[11]["z"]),
        "right_shoulder": (lm[12]["x"], lm[12]["y"], lm[12]["z"]),
        "left_hip": (lm[23]["x"], lm[23]["y"], lm[23]["z"]),
        "right_hip": (lm[24]["x"], lm[24]["y"], lm[24]["z"]),
    }

    res = AngleCalculator.calculate_all_angles(landmarks_dict)

    assert res["is_valid"] is False
    assert res["left_shoulder_elevation"] == 0
    assert res["asymmetry"] == 0
