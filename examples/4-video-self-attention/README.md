# Self-attention explainer video

A 47.9 s explainer of self-attention in transformers, in the style of 3Blue1Brown, with a narration voice that runs on this Mac.

## Files

- `self-attention.mp4`: the video, 1920 x 1080 at 60 fps, with an AAC voice track and a soft English subtitle track.
- `self-attention.srt`: the same subtitles as a separate file.
- `explainer-narration.md`: the narration, the facts behind it, and what the video leaves out.
- `explainer-scenes.md`: the scene plan, with times, the words for each scene, and the toy numbers.
- `source/script.json`: the narration sentences and the voice settings. Edit this file to change the words or the voice.
- `source/narrate.py`: makes one voice clip for each sentence with Kokoro, then the voice track, `timings.json` and the subtitles.
- `source/scene.py`: the Manim scene. It reads `timings.json` and starts each visual at the start of its sentence.
- `source/build.sh`: runs all the steps and writes the `.mp4` and the `.srt` into this folder.

## Rebuild

Run the build script. Point it to a Manim command and, if your Kokoro files are in a different place, to them:

```bash
MANIM=/path/to/venv/bin/manim WORK_DIR=/tmp/attention-build ./source/build.sh
```

The script uses these defaults for Kokoro:

```bash
KOKORO_PY=~/.cache/hyperframes/kokoro-venv/bin/python
KOKORO_MODEL=~/.cache/hyperframes/tts/models/kokoro-v1.0.onnx
KOKORO_VOICES=~/.cache/hyperframes/tts/voices/voices-v1.0.bin
```

Set `QUALITY=l` for a fast 480p draft. The 1080p build took less than 1 minute on this Mac.

## Requirements

Versions used for this build, as of 2026-10-03:

- Manim Community Edition 0.21.0 in a Python 3.12 venv (`uv venv --python 3.12`, then `uv pip install manim`).
- Cairo, Pango and ffmpeg from Homebrew.
- A LaTeX install with `standalone`, `preview`, `amsmath` and `xcolor` (TeX Live 2025 here) for the math.
- kokoro-onnx 0.6.1 with soundfile, in its own Python 3.12 venv, and the model files `kokoro-v1.0.onnx` and `voices-v1.0.bin` from the kokoro-onnx GitHub release.

The Kokoro model has an Apache 2.0 license, so you can use the voice in a published video.

## Voice

The voice is Kokoro `am_michael`, a calm American male voice, at speed 1.0. For a female narrator, set `"voice": "af_heart"` in `source/script.json`. If Kokoro stops with a "phontab" error, copy the espeak-ng data folder to a short path. Then set `ESPEAK_DATA_PATH` to that path.
