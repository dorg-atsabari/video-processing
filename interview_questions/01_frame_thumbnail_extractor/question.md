# Question 1: Frame Thumbnail Extractor

## Task

Using PyAV, implement the following function:

```python
def extract_thumbnails(
    input_path: str,
    interval_sec: float,
    output_dir: str,
    width: int = 320,
    height: int = 180,
    quality: int = 85,
) -> list[str]:
    ...
```

## Requirements

- Open the input video using `av.open()`
- Decode only the video stream (skip audio)
- Extract one frame every `interval_sec` seconds based on the frame's PTS (presentation timestamp)
- Resize each frame to `width x height` before saving — use `av.VideoReformat` or `libswscale` via PyAV
- Save each frame as a JPEG with the given `quality` (1–95 scale)
- Name output files as `thumb_{timestamp_ms}.jpg` where `timestamp_ms` is the frame's PTS in milliseconds
- Return the list of saved file paths

## Key Concepts to Cover

- **Container vs Stream**: `av.open()` gives you a container; you must select the correct stream
- **PTS vs DTS**: Use PTS (not DTS) for presentation timing; convert using `stream.time_base`
- **Frame resampling**: Resize using `av.VideoReformat` — specify `width`, `height`, and pixel format (`yuv420p` or `rgb24`)
- **JPEG quality**: Controlled via codec context options when encoding the frame

## Example

```python
paths = extract_thumbnails("input.mp4", interval_sec=5.0, output_dir="./thumbs")
# => ["./thumbs/thumb_0.jpg", "./thumbs/thumb_5000.jpg", "./thumbs/thumb_10000.jpg", ...]
```

## Constraints

- Do not use `subprocess` or `ffmpeg` CLI — use PyAV only
- Skip frames where PTS is `None`
- The function should work on H.264 and H.265 encoded inputs
