# SmartPeopleCounter

Absolutely! Below is a **complete and professional GitHub README.md-style explanation** for your project **SmartPeopleCounter**.

---

# 👁️‍🗨️ SmartPeopleCounter

**SmartPeopleCounter** is a real-time, AI-powered people counting system using YOLOv8 for detection and a lightweight centroid tracker for tracking individuals across video frames. It detects **entries and exits**, tracks **current occupancy**, and issues alerts when:

* Too many people enter within a short period (**burst alert**)
* The number of people inside exceeds a configured limit (**occupancy alert**)

It’s designed for applications like **retail analytics**, **office occupancy monitoring**, **event crowd control**, and more.

---

## 📸 Features

✅ **YOLOv8-powered person detection**
✅ **Simple and efficient centroid tracking** (no heavy tracking libraries)
✅ **Entry/Exit line crossing detection**
✅ **Occupancy tracking**
✅ **Burst alert** (e.g., 5 entries within 10 seconds)
✅ **Occupancy alert** (e.g., more than 50 people inside)
✅ **CSV logging** of all events and alerts
✅ **Alert screenshots** saved for later review
✅ **Cross-platform alert sound**
✅ **Overlay with live metrics and alert messages**
✅ Works with **video files, RTSP streams**, or **webcams**

---

## 🛠️ Installation

```bash
git clone https://github.com/your-username/SmartPeopleCounter.git
cd SmartPeopleCounter
pip install -r requirements.txt
```

**Requirements**:

* Python 3.7+
* OpenCV
* Ultralytics YOLOv8

> If you haven’t installed YOLOv8 before:

```bash
pip install ultralytics
```

---

## 🚀 Quick Start

### Webcam (default webcam = 0):

```bash
python smart_people_counter.py --source 0 --show
```

### RTSP/IP camera:

```bash
python smart_people_counter.py --source rtsp://your-camera-url --show
```

### Video file:

```bash
python smart_people_counter.py --source videos/people.mp4 --show
```

---

## ⚙️ Command Line Arguments

| Argument             | Description                                       | Default        |
| -------------------- | ------------------------------------------------- | -------------- |
| `--source`           | Video source (index, file path, or RTSP/HTTP URL) | `0`            |
| `--weights`          | YOLOv8 model weights (e.g., yolov8n.pt)           | `yolov8n.pt`   |
| `--conf`             | Confidence threshold for detections               | `0.5`          |
| `--line_orientation` | Line direction: `horizontal` or `vertical`        | `horizontal`   |
| `--line_position`    | Pixel position of the line                        | `300`          |
| `--line_hyst`        | Hysteresis band to avoid bounce                   | `10`           |
| `--burst_threshold`  | Entries within time to trigger burst alert        | `5`            |
| `--burst_window`     | Time window for burst alert (seconds)             | `10.0`         |
| `--occupancy_limit`  | Max people allowed inside                         | `50`           |
| `--cooldown`         | Cooldown between repeated alerts (seconds)        | `15.0`         |
| `--show`             | Show UI overlay in a window                       | off by default |

---

## 📂 Output Files

| File                                 | Description                            |
| ------------------------------------ | -------------------------------------- |
| `alerts_log.csv`                     | Logs all entries, exits, and alerts    |
| `alert_snapshot_YYYYMMDD_HHMMSS.jpg` | Frame image when an alert is triggered |

---

## 📊 Example Use Cases

* 📈 **Retail analytics**: Count foot traffic and monitor shop capacity
* 🏢 **Office management**: Track number of people in a meeting room
* 🎟️ **Events**: Detect crowd surges and prevent over-occupancy
* 🏫 **Classrooms/labs**: Ensure no overuse of limited spaces

---

## 🧠 How It Works

1. **Detect**: Uses YOLOv8 to detect people in each frame.
2. **Track**: A simple centroid tracker assigns consistent IDs across frames.
3. **Line Crossing**: When tracked centroids cross a virtual line (horizontal/vertical), it counts as an entry or exit.
4. **Alerts**:

   * **Burst Alert**: If X people enter within Y seconds.
   * **Occupancy Alert**: If the number inside exceeds a configured limit.
5. **Overlay**: Shows counts, alerts, and IDs directly on the video feed.
6. **Logs**: All events and alerts are written to a `.csv` log.
7. **Snapshots**: When an alert triggers, a screenshot of the frame is saved.

---



## 📌 Roadmap / Ideas

* [ ] Optional Flask API or web dashboard
* [ ] Live graph of occupancy over time
* [ ] Multiple camera input support
* [ ] MQTT or webhook support for alerts





## 📁 Repository Structure

SmartPeopleCounter/
├── smart_people_counter.py       # Main script
├── alerts_log.csv                # Generated during run
├── requirements.txt              # Python dependencies
└── README.md                     # Project documentation

