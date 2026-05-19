"""
Rep Counter - Detect shoulder raise reps from shoulder elevation over time.
"""

from collections import deque
from dataclasses import dataclass
from typing import Deque, Dict, Optional


@dataclass
class RepCounterConfig:
    """Configuration for rep counting and smoothing."""
    SMOOTHING_WINDOW: int = 5
    MIN_RAISE_DELTA: float = 0.01
    UP_CONFIRM_FRAMES: int = 2
    DOWN_CONFIRM_FRAMES: int = 1
    LOWER_THRESHOLD_RATIO: float = 0.35
    MIN_REP_INTERVAL_FRAMES: int = 5


class RepCounter:
    """Track shoulder elevation and count raise/lower rep cycles."""

    def __init__(self, config: RepCounterConfig = None):
        self.config = config or RepCounterConfig()
        self.samples: Deque[float] = deque(maxlen=self.config.SMOOTHING_WINDOW)
        self.smoothed_elevation: Optional[float] = None
        self.state = "down"
        self.rep_count = 0
        self.baseline = None
        self.last_peak = 0.0
        self.up_hits = 0
        self.down_hits = 0
        self.frames_since_last_rep = 0

    @staticmethod
    def get_average_elevation(angles: Dict) -> float:
        """Return average shoulder elevation from angle output."""
        return (angles["left_shoulder_elevation"] + angles["right_shoulder_elevation"]) / 2.0

    def add_sample(self, elevation: float) -> Dict:
        """Add a new elevation sample, update state, and count reps."""
        self.samples.append(elevation)
        smoothed = sum(self.samples) / len(self.samples)
        self.smoothed_elevation = smoothed

        if self.baseline is None:
            self.baseline = smoothed

        self.frames_since_last_rep += 1

        # Use the lowest observed elevation while in the down state as a dynamic baseline.
        if self.state == "down":
            self.baseline = min(self.baseline, smoothed)

        raise_threshold = self.baseline + self.config.MIN_RAISE_DELTA
        if self.state == "down":
            if smoothed >= raise_threshold:
                self.up_hits += 1
            else:
                self.up_hits = 0

            if self.up_hits >= self.config.UP_CONFIRM_FRAMES:
                self.state = "up"
                self.last_peak = smoothed
                self.down_hits = 0
                self.up_hits = 0

        elif self.state == "up":
            self.last_peak = max(self.last_peak, smoothed)
            movement_range = self.last_peak - self.baseline
            end_threshold = self.baseline + max(
                self.config.MIN_RAISE_DELTA * 0.5,
                movement_range * 0.35
            )

            if smoothed <= end_threshold:
                self.down_hits += 1
            else:
                self.down_hits = 0

            if self.down_hits >= self.config.DOWN_CONFIRM_FRAMES:
                if self.last_peak - smoothed >= self.config.MIN_RAISE_DELTA and self.frames_since_last_rep >= self.config.MIN_REP_INTERVAL_FRAMES:
                    self.rep_count += 1
                self.state = "down"
                self.baseline = min(self.baseline, smoothed)
                self.down_hits = 0
                self.frames_since_last_rep = 0

        return {
            "rep_count": self.rep_count,
            "state": self.state,
            "smoothed_elevation": self.smoothed_elevation,
            "baseline": self.baseline,
            "raise_threshold": raise_threshold,
        }

    def reset(self) -> None:
        """Reset rep counter state."""
        self.__init__(config=self.config)
