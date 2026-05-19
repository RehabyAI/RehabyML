"""
Latency profiler for MediaPipe pose detection and frame pipeline timing.
"""

import argparse
import cv2
import json
import time
from pathlib import Path
from typing import List

from pose_analyzer import PoseAnalyzer


def resize_frame(frame, target_height: int):
    height, width = frame.shape[:2]
    if height <= target_height:
        return frame
    scale = target_height / float(height)
    new_width = int(width * scale)
    return cv2.resize(frame, (new_width, target_height), interpolation=cv2.INTER_LINEAR)


def profile_video(video_path: Path, resolutions: List[int], max_frames: int = 120):
    results = []
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError(f"Failed to open video: {video_path}")

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    cap.release()

    for height in resolutions:
        analyzer = PoseAnalyzer()
        cap = cv2.VideoCapture(str(video_path))
        frame_count = 0
        warmup = min(10, max_frames)
        frame_times = []
        inference_times = []
        valid_frames = 0

        while frame_count < max_frames:
            ret, frame = cap.read()
            if not ret:
                break
            if height > 0:
                frame = resize_frame(frame, height)

            start_total = time.perf_counter()
            start_infer = time.perf_counter()
            analyzer.analyze_frame(frame)
            inference_times.append(time.perf_counter() - start_infer)
            frame_times.append(time.perf_counter() - start_total)
            frame_count += 1

        cap.release()
        analyzer.close()

        if frame_times:
            avg_frame_time_s = sum(frame_times) / len(frame_times)
            avg_frame_time_ms = round(1000.0 * avg_frame_time_s, 2)
            avg_pose_inference_ms = round(1000.0 * sum(inference_times) / len(inference_times), 2)
            results.append({
                "resolution_height": height,
                "frames_processed": len(frame_times),
                "average_frame_time_ms": avg_frame_time_ms,
                "average_pose_inference_ms": avg_pose_inference_ms,
                "fps_estimate": round(1.0 / avg_frame_time_s, 1),
            })

    return {
        "video_path": str(video_path),
        "original_frames": total_frames,
        "original_fps": fps,
        "results": results,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Profile pose detection latency across resolutions")
    parser.add_argument("video_path", help="Path to input video file")
    parser.add_argument("--resolutions", default="480,360,240",
                        help="Comma-separated target heights to profile")
    parser.add_argument("--frames", type=int, default=120,
                        help="Number of frames to profile per resolution")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")

    args = parser.parse_args()
    video_path = Path(args.video_path)
    resolutions = [int(r.strip()) for r in args.resolutions.split(",") if r.strip()]

    profile = profile_video(video_path, resolutions, max_frames=args.frames)
    if args.json:
        print(json.dumps(profile, indent=2))
    else:
        print(f"Latency profile for {video_path}")
        print(f"Original video frames: {profile['original_frames']}, fps: {profile['original_fps']:.1f}")
        for row in profile["results"]:
            print(f"  {row['resolution_height']}p -> {row['average_frame_time_ms']} ms/frame, "
                  f"pose={row['average_pose_inference_ms']} ms, {row['fps_estimate']} fps")
