# Rehaby

AI posture coach for shoulder raise analysis.

## New Features

- `rep_counter.py` - counts shoulder raise repetitions by tracking smoothed shoulder elevation over time.
- `latency_profiler.py` - profiles MediaPipe latency across resolutions (480p, 360p, 240p).
- `test_on_videos.py` now supports `--count-reps` / `-r` and JSON summary output includes `rep_count`.

## Usage

Analyze a video and count reps:

```bash
venv/bin/python test_on_videos.py data/test_videos/good_form.mp4 -r
```

Profile latency:

```bash
venv/bin/python latency_profiler.py data/test_videos/good_form.mp4 --resolutions 480,360,240 --frames 120
```

Generate JSON output:

```bash
venv/bin/python test_on_videos.py data/test_videos/good_form.mp4 -j
```

## Validation

- `venv/bin/python -m pytest -q`
- `venv/bin/python test_on_videos.py data/test_videos/good_form.mp4 -r`
- `venv/bin/python latency_profiler.py data/test_videos/good_form.mp4 --resolutions 480,360,240 --frames 120`
