# Question 3: Audio/Video Muxer with Encoding Options

## Task

AI video generation pipelines often produce a video-only file and an audio-only file separately.
Using PyAV, implement the following function:

```python
def mux(
    video_path: str,
    audio_path: str,
    output_path: str,
    reencode_video: bool = False,
    video_codec: str = "libx264",
    crf: int = 23,
    resolution: tuple[int, int] | None = None,  # (width, height) or None to keep original
    video_bitrate: str | None = None,            # e.g. "2M" — used instead of CRF if provided
    audio_bitrate: str = "128k",
) -> None:
    ...
```

## Requirements

### Stream copying (default, `reencode_video=False`)
- Demux video packets from `video_path` and audio packets from `audio_path`
- Copy both streams directly into the output container without decoding/re-encoding
- Use `av.open(output_path, "w")` and add streams using `output.add_stream(template=input_stream)`

### Re-encoding (`reencode_video=True`)
- Decode the video stream and re-encode using `video_codec`
- If `video_bitrate` is provided, use **CBR (Constant Bitrate)** mode — set `bit_rate` on the codec context
- Otherwise, use **CRF mode** — pass `{"crf": str(crf)}` as codec options
- If `resolution` is provided, resize frames to `(width, height)` before encoding
- Re-encode audio to AAC at `audio_bitrate`

## Key Concepts to Cover

- **Stream copy vs re-encode**: Stream copy is lossless and fast; re-encoding allows format changes and compression tuning
- **CRF vs CBR**:
  - CRF targets constant quality — bitrate varies per scene complexity
  - CBR targets a fixed bitrate — quality varies, predictable file size
- **Bitrate notation**: `"2M"` = 2 Mbps, `"500k"` = 500 Kbps — PyAV accepts these as strings
- **Muxing**: Writing packets from multiple streams into one container, ensuring correct interleaving

## Example

```python
# Fast path — no re-encoding
mux("generated_video.mp4", "generated_audio.wav", "output.mp4")

# Re-encode with quality control
mux(
    "generated_video.mp4",
    "generated_audio.wav",
    "output.mp4",
    reencode_video=True,
    video_codec="libx265",
    crf=28,
    resolution=(1280, 720),
    audio_bitrate="192k",
)
```

## Constraints

- Do not use `subprocess` or `ffmpeg` CLI — use PyAV only
- When stream copying, do not decode any frames
- `video_bitrate` takes precedence over `crf` when both are provided
- Output container must be a valid MP4 playable by standard players
