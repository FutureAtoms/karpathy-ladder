"""Turn the body render into the finished film: title card with a spoken
intro, the body, a recap card with a spoken recap, a quiet piano bed, and
captions burned in. Run it after build.sh has rendered the body.

    python finish.py WORK_DIR --manim /path/to/manim --model kokoro-v1.0.onnx --voices voices-v1.0.bin

It writes self-attention.mp4 and self-attention.srt next to source/.
Burning captions needs an ffmpeg with libass. When the local ffmpeg has no
`subtitles` filter, the script runs ffmpeg in the linuxserver/ffmpeg container.
"""
import argparse
import json
import shutil
import subprocess
from pathlib import Path

import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

from music import piano_bed

HERE = Path(__file__).resolve().parent
OUT = HERE.parent
TITLE_HOLD, RECAP_TAIL, XFADE = 1.2, 3.0, 0.6
CAPTION = "FontName=DejaVu Sans,FontSize=14,PrimaryColour=&H00FFFFFF,OutlineColour=&H90000000,BorderStyle=1,Outline=1.5,Shadow=0"


def ts(t: float) -> str:
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def srt(cues) -> str:
    return "\n\n".join(f"{i}\n{ts(a)} --> {ts(b)}\n{t}" for i, (a, b, t) in enumerate(cues, 1)) + "\n"


def parse_srt(path: Path):
    cues = []
    for block in path.read_text().strip().split("\n\n"):
        lines = block.split("\n")
        a, b = lines[1].split(" --> ")
        sec = lambda x: sum(float(p) * m for p, m in zip(x.replace(",", ".").split(":"), (3600, 60, 1)))
        cues.append((sec(a), sec(b), " ".join(lines[2:])))
    return cues


def duration(path: Path) -> float:
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)]))


def speak(tts, lines, voice, speed, gap=0.8):
    parts, cues, t, sr = [], [], 0.0, 24000
    for i, line in enumerate(lines):
        a, sr = tts.create(line, voice=voice, speed=speed, lang="en-gb" if voice.startswith("b") else "en-us")
        cues.append((t, t + len(a) / sr, line))
        parts.append(a)
        t += len(a) / sr
        if i < len(lines) - 1:
            parts.append(np.zeros(int(sr * gap), dtype=np.float32))
            t += gap
    return np.concatenate(parts), sr, cues


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("work", type=Path)
    ap.add_argument("--manim", default="manim")
    ap.add_argument("--model", required=True)
    ap.add_argument("--voices", required=True)
    args = ap.parse_args()
    work = args.work
    script = json.loads((HERE / "script.json").read_text())
    body = next((work / "media" / "videos").rglob("SelfAttention.mp4"))
    body_mux = OUT / "self-attention.mp4"          # build.sh output: body with voice
    body_srt = OUT / "self-attention.srt"

    # Cards, rendered as still frames in the film's colours.
    for file, scene, name in (("title_card.py", "TitleCard", "title-card.png"), ("recap_card.py", "ClosingCard", "recap-card.png")):
        subprocess.run([args.manim, "-qh", "-s", "--disable_caching", "--media_dir", str(work / "cards"), str(HERE / file), scene],
                       check=True, capture_output=True)
        shutil.copy(next((work / "cards").rglob(f"{scene}*.png")), work / name)

    # Intro and recap narration, in the film's voice.
    tts = Kokoro(args.model, args.voices)
    intro, sr, intro_cues = speak(tts, [script["intro"]], script["voice"], script["speed"])
    recap, sr, recap_cues = speak(tts, script["recap"], script["voice"], script["speed"])
    sf.write(work / "intro.wav", intro, sr)
    sf.write(work / "recap.wav", recap, sr)

    # Timeline.
    body_len = duration(body_mux)
    title_len = 1.0 + len(intro) / sr + TITLE_HOLD
    body_at = title_len - XFADE
    recap_card_at = body_at + body_len - 2.0          # trim 2 s of the body's closing hold
    recap_voice_at = recap_card_at + 1.0
    recap_len = 1.0 + len(recap) / sr + RECAP_TAIL
    total = recap_card_at + recap_len

    sf.write(work / "piano.wav", piano_bed(total + 1), 48000)
    card_cues = [(a + 1.0, b + 1.0, t) for a, b, t in intro_cues] + [(a + recap_voice_at, b + recap_voice_at, t) for a, b, t in recap_cues]
    main_cues = [(a + body_at, b + body_at, t) for a, b, t in parse_srt(body_srt)]
    (work / "cards.srt").write_text(srt(card_cues))
    (work / "main.srt").write_text(srt(main_cues))
    shutil.copy(body_mux, work / "body.mp4")

    graph = (
        "[0:v]scale=1920:1080,fps=60,format=yuv420p,setsar=1[t];[1:v]fps=60,format=yuv420p,setsar=1[m];"
        "[2:v]scale=1920:1080,fps=60,format=yuv420p,setsar=1[c];"
        f"[t][m]xfade=transition=fade:duration={XFADE}:offset={body_at:.3f}[tm];"
        f"[tm][c]xfade=transition=fade:duration={XFADE}:offset={recap_card_at:.3f}[vc];"
        f"[vc]subtitles=main.srt:force_style='{CAPTION},MarginV=8'[v1];[v1]subtitles=cards.srt:force_style='{CAPTION},MarginV=49'[v];"
        f"[3:a]aresample=48000,adelay=1000|1000[i];[1:a]aresample=48000,adelay={int(body_at * 1000)}|{int(body_at * 1000)}[n];"
        f"[4:a]aresample=48000,adelay={int(recap_voice_at * 1000)}|{int(recap_voice_at * 1000)}[o];"
        "[i][n][o]amix=inputs=3:duration=longest:normalize=0,pan=stereo|c0=c0|c1=c0,asplit=2[nar][sc];"
        f"[5:a]atrim=0:{total:.3f},afade=t=out:st={total - 3:.3f}:d=3,volume=0.16[mus0];"
        "[mus0][sc]sidechaincompress=threshold=0.05:ratio=2.5:attack=250:release=1200[mus];"
        "[nar][mus]amix=inputs=2:duration=longest:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=11[a]"
    )
    cmd = ["-hide_banner", "-loglevel", "error", "-y",
           "-loop", "1", "-framerate", "60", "-t", f"{title_len:.3f}", "-i", "title-card.png",
           "-i", "body.mp4",
           "-loop", "1", "-framerate", "60", "-t", f"{recap_len:.3f}", "-i", "recap-card.png",
           "-i", "intro.wav", "-i", "recap.wav", "-i", "piano.wav",
           "-filter_complex", graph, "-map", "[v]", "-map", "[a]", "-t", f"{total:.3f}",
           "-c:v", "libx264", "-crf", "20", "-preset", "medium", "-c:a", "aac", "-b:a", "160k", "-ar", "48000",
           "-movflags", "+faststart", "final.mp4"]
    has_libass = b" subtitles " in subprocess.run(["ffmpeg", "-hide_banner", "-filters"], capture_output=True).stdout
    if has_libass:
        subprocess.run(["ffmpeg", *cmd], cwd=work, check=True)
    else:
        subprocess.run(["docker", "run", "--rm", "-v", f"{work}:/w", "-w", "/w", "linuxserver/ffmpeg:latest", *cmd], check=True)

    shutil.copy(work / "final.mp4", body_mux)
    body_srt.write_text(srt(sorted(card_cues + main_cues)))
    print(f"wrote {body_mux} ({total:.1f} s) and {body_srt}")


if __name__ == "__main__":
    main()
