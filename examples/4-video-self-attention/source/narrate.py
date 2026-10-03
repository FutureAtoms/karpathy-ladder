"""Make the narration with Kokoro (kokoro-onnx), one clip for each sentence.

Reads script.json, writes into WORK_DIR:
  clips/<id>.wav     one clip for each sentence
  narration.wav      all clips on one track, each at its start time
  timings.json       start and end of each sentence (scene.py reads this)
  subtitles.srt      one cue for each sentence

Usage:
  python narrate.py WORK_DIR --model kokoro-v1.0.onnx --voices voices-v1.0.bin
Env:
  ESPEAK_DATA_PATH   optional: a short copy of the espeak-ng data folder,
                     for the "phontab" error on long paths.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

HERE = Path(__file__).resolve().parent


def make_kokoro(model: str, voices: str) -> Kokoro:
    data_path = os.environ.get("ESPEAK_DATA_PATH")
    if data_path:
        from kokoro_onnx.config import EspeakConfig

        return Kokoro(model, voices, espeak_config=EspeakConfig(data_path=data_path))
    return Kokoro(model, voices)


def srt_time(t: float) -> str:
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def trim_silence(samples: np.ndarray, rate: int, floor: float = 0.004, pad: float = 0.04) -> np.ndarray:
    """Cut the quiet ends of a clip so the timings match the speech."""
    loud = np.flatnonzero(np.abs(samples) > floor)
    if loud.size == 0:
        return samples
    start = max(0, loud[0] - int(pad * rate))
    end = min(len(samples), loud[-1] + int(pad * rate))
    return samples[start:end]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("work_dir")
    ap.add_argument("--model", required=True)
    ap.add_argument("--voices", required=True)
    ap.add_argument("--script", default=str(HERE / "script.json"))
    args = ap.parse_args()

    script = json.loads(Path(args.script).read_text())
    work = Path(args.work_dir)
    (work / "clips").mkdir(parents=True, exist_ok=True)

    kokoro = make_kokoro(args.model, args.voices)
    rate = None
    clips = []
    for s in script["sentences"]:
        samples, sr = kokoro.create(s["text"], voice=script["voice"], speed=script["speed"], lang="en-us")
        samples = trim_silence(np.asarray(samples, dtype=np.float32), sr)
        rate = rate or sr
        sf.write(work / "clips" / f"{s['id']}.wav", samples, sr)
        clips.append((s, samples))

    # Place the clips on one timeline. A wider gap separates scenes.
    t = script["lead_in"]
    timings = []
    prev_scene = None
    for s, samples in clips:
        if prev_scene is not None:
            t += script["scene_gap"] if s["scene"] != prev_scene else script["gap"]
        dur = len(samples) / rate
        timings.append({"id": s["id"], "scene": s["scene"], "text": s["text"],
                        "start": round(t, 3), "end": round(t + dur, 3), "dur": round(dur, 3)})
        t += dur
        prev_scene = s["scene"]

    speech_end = timings[-1]["end"]
    total = speech_end + script["final_hold"]
    track = np.zeros(int(np.ceil(total * rate)), dtype=np.float32)
    for (s, samples), tm in zip(clips, timings):
        i = int(round(tm["start"] * rate))
        track[i:i + len(samples)] += samples
    sf.write(work / "narration.wav", track, rate)

    (work / "timings.json").write_text(json.dumps(
        {"sentences": timings, "speech_end": round(speech_end, 3), "total": round(total, 3)}, indent=2))

    cues = []
    for n, tm in enumerate(timings, 1):
        cues.append(f"{n}\n{srt_time(tm['start'])} --> {srt_time(tm['end'] + 0.2)}\n{tm['text']}\n")
    (work / "subtitles.srt").write_text("\n".join(cues))

    words = sum(len(tm["text"].split()) for tm in timings)
    print(json.dumps({"sentences": len(timings), "words": words, "speech_end": round(speech_end, 2),
                      "total": round(total, 2)}))
    for tm in timings:
        print(f"{tm['id']}  {tm['start']:6.2f} {tm['end']:6.2f}  ({tm['dur']:.2f} s)  {tm['text']}")


if __name__ == "__main__":
    main()
