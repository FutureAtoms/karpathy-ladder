#!/usr/bin/env bash
# Rebuild self-attention.mp4 and self-attention.srt from this folder.
#
# Steps: Kokoro voice (one clip for each sentence) -> timings.json ->
# Manim render timed from those clips -> ffmpeg mux of video, voice and a
# soft subtitle track.
#
# Settings (environment variables, all optional):
#   WORK_DIR       folder for clips, renders and caches (default: a new temp folder)
#   KOKORO_PY      a Python that has kokoro-onnx and soundfile
#   KOKORO_MODEL   kokoro-v1.0.onnx
#   KOKORO_VOICES  voices-v1.0.bin
#   MANIM          the manim command (Manim Community Edition)
#   QUALITY        manim quality letter: l (480p15), m, h (1080p60, default), k
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
OUT="$(dirname "$HERE")"
WORK="${WORK_DIR:-$(mktemp -d)}"
KOKORO_PY="${KOKORO_PY:-$HOME/.cache/hyperframes/kokoro-venv/bin/python}"
KOKORO_MODEL="${KOKORO_MODEL:-$HOME/.cache/hyperframes/tts/models/kokoro-v1.0.onnx}"
KOKORO_VOICES="${KOKORO_VOICES:-$HOME/.cache/hyperframes/tts/voices/voices-v1.0.bin}"
MANIM="${MANIM:-manim}"
QUALITY="${QUALITY:-h}"

mkdir -p "$WORK"
echo "work folder: $WORK"

# 1. Voice and timings
"$KOKORO_PY" "$HERE/narrate.py" "$WORK" --model "$KOKORO_MODEL" --voices "$KOKORO_VOICES"

# 2. Animation, timed from the voice clips
TIMINGS="$WORK/timings.json" "$MANIM" -q"$QUALITY" --disable_caching \
  --media_dir "$WORK/media" "$HERE/scene.py" SelfAttention

VIDEO="$(find "$WORK/media/videos" -name SelfAttention.mp4 -not -path '*partial*' | head -1)"
LEN="$(ffprobe -v error -select_streams v:0 -show_entries format=duration -of csv=p=0 "$VIDEO")"

# 3. Mux: the video track sets the length, so the closing hold stays.
ffmpeg -y -v error \
  -i "$VIDEO" -i "$WORK/narration.wav" -i "$WORK/subtitles.srt" \
  -map 0:v -map 1:a -map 2:s \
  -c:v copy \
  -af "loudnorm=I=-16:TP=-1.5:LRA=11,apad" -c:a aac -b:a 192k -ar 48000 \
  -c:s mov_text -metadata:s:a:0 language=eng -metadata:s:s:0 language=eng \
  -t "$LEN" -movflags +faststart \
  "$OUT/self-attention.mp4"
cp "$WORK/subtitles.srt" "$OUT/self-attention.srt"

ffprobe -v error -show_entries format=duration:stream=codec_type,codec_name,width,height \
  -of compact "$OUT/self-attention.mp4"
