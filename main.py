Great! Based on your initial script and the enhancements we've discussed, here's the **full upgraded code** for the project.

---

## 🏷️ **Project Name**: `SmartPeopleCounter`

A smart people counting system with real-time entry/exit detection, burst and occupancy alerts, event logging, and optional alert snapshots.

---

## 📜 Full Script: `smart_people_counter.py`

```python
"""
SmartPeopleCounter
-------------------
A smart real-time people counter with:
- Entry/Exit tracking
- Burst and occupancy alerts
- Optional alert snapshots
- Alert sound
- Logging to CSV
- YOLOv8 + centroid tracking (no extra dependencies)

Run:
    python smart_people_counter.py --source 0 --show

Requirements:
    pip install ultralytics opencv-python
"""

import argparse
import time
import threading
from collections import deque, defaultdict
from dataclasses import dataclass
from typing import Dict, Tuple, List
import os
import csv

import cv2
import numpy as np

try:
    from ultralytics import YOLO
except ImportError:
    YOLO = None


@dataclass
class LineConfig:
    orientation: str = "horizontal"
    position: int = 300
    hysteresis: int = 10


@dataclass
class AlertConfig:
    burst_threshold: int = 5
    burst_window_sec: float = 10.0
    occupancy_limit: int = 50
    cooldown_sec: float = 15.0


@dataclass
class DrawConfig:
    show_tracks: bool = True
    show_ids: bool = True
    show_boxes: bool = True
    font_scale: float = 0.7
    thickness: int = 2


class CentroidTracker:
    def __init__(self, max_distance=80, max_missed=10):
        self.next_id = 1
        self.objects: Dict[int, Dict] = {}
        self.max_distance = max_distance
        self.max_missed = max_missed

    def _centroid(self, box):
        x1, y1, x2, y2 = box
        return ((x1 + x2) // 2, (y1 + y2) // 2)

    def update(self, detections: List[Tuple[int, int, int, int]]):
        cents = [self._centroid(b) for b in detections]
        for tid in list(self.objects.keys()):
            self.objects[tid]["missed"] += 1

        used_tracks = set()
        used_dets = set()
        for di, det in enumerate(detections):
            c = cents[di]
            best_tid, best_dist = None, 1e9
            for tid, obj in self.objects.items():
                if tid in used_tracks:
                    continue
                oc = obj["centroid"]
                dist = np.hypot(c[0] - oc[0], c[1] - oc[1])
                if dist < best_dist:
                    best_dist = dist
                    best_tid = tid
            if best_tid is not None and best_dist <= self.max_distance:
                self.objects[best_tid].update({
                    "box": det,
                    "centroid": c,
                    "missed": 0,
                })
                used_tracks.add(best_tid)
                used_dets.add(di)

        for di, det in enumerate(detections):
            if di in used_dets:
                continue
            c = cents[di]
            tid = self.next_id
            self.next_id += 1
            self.objects[tid] = {
                "box": det,
                "centroid": c,
                "missed": 0,
                "state": "unknown",
                "last_side": None,
                "history": deque(maxlen=8),
            }

        for tid in list(self.objects.keys()):
            if self.objects[tid]["missed"] > self.max_missed:
                del self.objects[tid]

        return self.objects


class AlertManager:
    def __init__(self, cfg: AlertConfig):
        self.cfg = cfg
        self.entry_events = deque()
        self.exit_events = deque()
        self.last_alert_time = defaultdict(lambda: 0.0)
        self._lock = threading.Lock()
        self.log_file = "alerts_log.csv"
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Timestamp", "Type", "Message"])

    def _rate_limited(self, key: str) -> bool:
        now = time.time()
        if now - self.last_alert_time[key] >= self.cfg.cooldown_sec:
            self.last_alert_time[key] = now
            return False
        return True

    def record_entry(self):
        with self._lock:
            self.entry_events.append(time.time())
        self._log("ENTRY", "Entry detected")

    def record_exit(self):
        with self._lock:
            self.exit_events.append(time.time())
        self._log("EXIT", "Exit detected")

    def _prune(self, deq: deque, window: float):
        cutoff = time.time() - window
        while deq and deq[0] < cutoff:
            deq.popleft()

    def check_burst_alert(self, frame=None) -> Tuple[bool, int]:
        self._prune(self.entry_events, self.cfg.burst_window_sec)
        count = len(self.entry_events)
        if count >= self.cfg.burst_threshold:
            if not self._rate_limited("burst"):
                msg = f"BURST ALERT: {count} entries in last {int(self.cfg.burst_window_sec)}s"
                self._trigger(msg, frame)
                return True, count
        return False, count

    def check_occupancy_alert(self, occupancy: int, frame=None) -> bool:
        if occupancy > self.cfg.occupancy_limit:
            if not self._rate_limited("occupancy"):
                msg = f"OCCUPANCY ALERT: occupancy {occupancy} > limit {self.cfg.occupancy_limit}"
                self._trigger(msg, frame)
                return True
        return False

    def _trigger(self, message: str, frame=None):
        print("[ALERT]", message)
        self._log("ALERT", message)

        try:
            import winsound
            winsound.Beep(1000, 500)
        except:
            print('\a', end='')

        if frame is not None:
            ts = time.strftime("%Y%m%d_%H%M%S")
            filename = f"alert_snapshot_{ts}.jpg"
            cv2.imwrite(filename, frame)

    def _log(self, alert_type: str, message: str):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, alert_type, message])


def side_of_line(line: LineConfig, centroid: Tuple[int, int]) -> str:
    x, y = centroid
    if line.orientation == "horizontal":
        if y < line.position - line.hysteresis:
            return "above"
        elif y > line.position + line.hysteresis:
            return "below"
        else:
            return "near"
    else:
        if x < line.position - line.hysteresis:
            return "left"
        elif x > line.position + line.hysteresis:
            return "right"
        else:
            return "near"


def draw_overlay(frame, line_cfg: LineConfig, counts, occupancy, alerts_text: List[str], draw_cfg: DrawConfig):
    h, w = frame.shape[:2]
    color = (0, 255, 255)
    if line_cfg.orientation == "horizontal":
        cv2.line(frame, (0, line_cfg.position), (w, line_cfg.position), color, 2)
    else:
        cv2.line(frame, (line_cfg.position, 0), (line_cfg.position, h), color, 2)

    x0, y0 = 15, 30
    cv2.putText(frame, f"Entered: {counts['in']}", (x0, y0), cv2.FONT_HERSHEY_SIMPLEX, draw_cfg.font_scale, (0, 255, 0), draw_cfg.thickness)
    cv2.putText(frame, f"Exited : {counts['out']}", (x0, y0 + 30), cv2.FONT_HERSHEY_SIMPLEX, draw_cfg.font_scale, (0, 0, 255), draw_cfg.thickness)
    cv2.putText(frame, f"Inside : {occupancy}", (x0, y0 + 60), cv2.FONT_HERSHEY_SIMPLEX, draw_cfg.font_scale, (255, 255, 255), draw_cfg.thickness)

    y = y0 + 100
    for t in alerts_text[-3:]:
        timestamp = time.strftime("%H:%M:%S")
        msg = f"[{timestamp}] {t}"
        cv2.putText(frame, msg, (x0, y), cv2.FONT_HERSHEY_SIMPLEX, draw_cfg.font_scale, (0, 140, 255), draw_cfg.thickness)
        y += 28


def run(
    source,
    weights="yolov8n.pt",
    conf_thres=0.5,
    line_orientation="horizontal",
    line_position=300,
    line_hyst=10,
    burst_threshold=5,
    burst_window_sec=10.0,
    occupancy_limit=50,
    cooldown_sec
```
