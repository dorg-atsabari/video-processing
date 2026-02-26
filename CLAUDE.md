# video-processing

Python scripts for trimming, cropping, and face-tracking video files using PyAV and OpenCV.

## Project Capabilities

- **Face-tracked crop** (`mux_fd_crop.py`): Trims a video segment, detects faces per frame, and outputs a horizontally-cropped video that smoothly follows the speaker's face. Includes an analysis mode to determine the optimal `min_size` filter.
- **Face detection overlay** (`mux.py`): Trims a video and draws face bounding boxes on each frame, outputs combined audio+video.
- **Audio extraction** (`extract_audio.py`): Extracts a time-range of audio to `.m4a`.
- **Video+audio extraction** (`extract_video_and_audio.py`): Extracts a time-range to separate video and audio files.

### `face_detector/` package

Pluggable face detection with two backends, selected via a factory:

```python
from face_detector import create_face_detector

detector = create_face_detector(backend="yunet")  # or "haar"
faces = detector.detect_faces(frame_bgr)          # -> [(x, y, w, h), ...]
face  = detector.get_first_face(frame_bgr)        # -> (x, y, w, h) | None
```

| Backend | Class | Notes |
|---------|-------|-------|
| `yunet` (default) | `YuNetFaceDetector` | Requires ONNX model file (see below) |
| `haar` | `HaarFaceDetector` | No model file needed, ships with OpenCV |

## Initialization

### 1. Install Python dependencies

```bash
pip install -e ".[dev]"
```

### 2. Download the YuNet ONNX model (required for the default backend)

```bash
mkdir -p face_detector/models
curl -L -o face_detector/models/face_detection_yunet_2023mar.onnx \
  https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx
```

The model file is gitignored (`face_detector/models/*.onnx`) and must be downloaded manually on each new clone.

### 3. Run tests

```bash
pytest
```

## Key Configuration (in `mux_fd_crop.py`)

| Variable | Default | Description |
|----------|---------|-------------|
| `trim_start_time` / `trim_end_time` | `30` / `50` | Time range to process (seconds) |
| `crop_width` | `600` | Output video width in pixels |
| `smoothing_factor` | `0.1` | Exponential smoothing (lower = smoother) |
| `dead_zone_threshold` | `30` | Ignore movements smaller than this (px) |
| `large_movement_threshold` | `80` | Snap immediately for movements larger than this (px) |
| `face_min_size` | `120` | Minimum face width to accept (px); use `analyze_mode=True` to auto-suggest |
| `analyze_mode` | `True` | Run analysis pass first to recommend `face_min_size` |
| `input_file_path` | URL | Source video (local path or HTTP URL) |
