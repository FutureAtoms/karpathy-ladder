# Tier 4: explainer video

A narrated video is the richest tier and the slowest to make. Use it when the
user asks for a video, or when the subject unfolds in time (a protocol
exchange, an algorithm step by step, an idea that builds up) and the user
wants something to watch.

## Pick the engine

| The user asks for | Engine | Why |
|---|---|---|
| "3b1b style", "3Blue1Brown", math or mechanism shown as geometry | **Manim Community Edition** with LaTeX | It is the tool that look comes from: LaTeX type, vectors as arrows on a plane, objects that transform into the next state |
| Any other explainer look (typographic, diagram-led, data-viz, a brand style) | The **`hyperframes`** skill, `faceless-explainer` workflow | HTML compositions, captions, music and a full review loop |

## Workflow

1. **Get the content right first.** Collect and verify the facts as for a sheet. For a subject with several parts, plan the sheet panels (`references/spec-sheet.md`) even if you do not build the sheet: each scene comes from a panel. Recompute every number you show.
2. **Write the message**: one sentence that the viewer must remember.
3. **Choose the voice** (below).
4. **Write the narration** and **the scene plan** (below) in a brief folder: `<delivery folder>/<slug>-video/explainer-narration.md` and `explainer-scenes.md`. Keep these names: hyperframes owns `STORYBOARD.md`, and on a case-insensitive disk `storyboard.md` is the same file.
5. **Build** with the engine (below).
6. **Verify the render** (below).
7. **Deliver** only what the user needs: the `.mp4`, an `.srt`, the narration, the scene plan, and the source in `<slug>-video/source/` (scene code and a build script). Keep framework working files (presets, packets, captures, caches) out of the delivery folder.

## Voice

- `ELEVENLABS_API_KEY` is set: ElevenLabs.
- The user asks for free and local, or there is no key: Kokoro on-device. With Manim, use `kokoro-onnx` in a Python venv and its model files (`kokoro-v1.0.onnx`, `voices-v1.0.bin` from the kokoro-onnx release). With hyperframes, use `media-use` with `--local-only`. espeak-ng stores its data path in a short buffer: if Kokoro fails with a "phontab" error, copy the espeak-ng data folder to a short path and point to it.
- Pick the voice that suits the named style (a calm narrator for a 3Blue1Brown-style video) and name the other option in one line.
- Nothing works: macOS `say -v Samantha -o narration.aiff`, and tell the user it is a placeholder.

Generate the voice one sentence at a time and record each clip's length; time the animation from those lengths, so each visual lands on the sentence that names it.

## Narration

Spoken English is the one place where STE yields. Keep its discipline (short
sentences, one idea in each, one word for one thing, active voice, no
progressive or perfect forms) but write the way a good teacher talks:
"Here is the trick.", "Now watch what happens to bank." Do not label the
narration as STE unless the user asked for STE.

- Speech runs at about 140 words a minute. Target words = seconds x 2.3: 45 s is about 100 words, 60 s about 140.
- At most 15 to 18 words in a sentence.
- Say what is on the screen: "This arrow is the query. It points at each key in turn."
- Define each term the first time you say it, then never change the word.
- Lint it with `ste_lint.py explainer-narration.md --mode 80` and fix the grammar findings.

## Scene plan

A table with one row for each scene. Each scene shows one idea.

| # | Seconds | Narration (exact words) | On screen | Motion |
|---|---|---|---|---|
| 1 | 0 to 6 | "Attention lets each word look at the other words." | A sentence of 5 tokens in a row | Tokens fade in from left to right |

## Look (3Blue1Brown style)

- Dark background, light ink, one accent colour for the thing being explained, a second accent only for contrast.
- Show mechanisms as geometry: vectors as arrows on a plane, a dot product as alignment between two arrows, weights as bar lengths.
- Build up, do not cut: objects move, split, combine and transform into the next state. Fade out a text label before you transform its object, so no garbled glyphs show mid-morph.
- One new object or change at a time, timed to the word that names it. Start each visual on the first word of its sentence, so no second of the video is empty.
- Show where each new quantity comes from when it first appears (for attention: q = W_Q x, k = W_K x, v = W_V x).
- Use one symbol for one thing in narration and on screen (for example √d_k everywhere, with "d_k is the key size" on screen once).
- Math in LaTeX (`MathTex`), set in pieces as the narration reaches them.
- Labels at 28 px or more at 1080p; keep everything inside a 5% title-safe margin.
- No burned-in captions. Ship subtitles as an `.srt` and as a soft track in the `.mp4` (`ffmpeg ... -c:s mov_text`), so the frame stays clean.
- Hold the final state for 2 to 3 seconds with the message on screen.

## Build with Manim

- Create a venv (`uv venv` or `python3 -m venv`) in scratch and install `manim`; it needs ffmpeg, cairo and pango, and a LaTeX install for `MathTex`.
- One `Scene` class with a section for each row of the scene plan; read the clip lengths from the timings file and use them as `run_time` and `wait` values.
- Render at 1080p (`manim -qh`), then mux the voice track and the subtitle track with ffmpeg; take the length from the video track so the closing hold is kept.
- Put `scene.py`, `narrate.py` and a `build.sh` that rebuilds everything in `source/`.

## Build with hyperframes

1. Create the film project in a new, empty folder, for example `<slug>-video/film/`: `npx hyperframes init <that folder> --skill=faceless-explainer`. `init` refuses a folder that has files in it.
2. Write `BRIEF.md` at the root of the film project, in the hyperframes brief format:

```markdown
---
workflow: faceless-explainer
flow: automation
storyboard: no            # yes when the user wants to review the plan before the build
message: "<the one sentence>"
destination: youtube
aspect: 1920x1080
language: en
length: 45s
angle: concept
audience: "<who watches>"
voice: <the voice you chose>
---

## Intent

<One short paragraph: what the video teaches, for whom, the tone.>

## Assets

- ../explainer-narration.md: final narration. VO_MODE: verbatim.
- ../explainer-scenes.md: scene plan with timings; build one frame for each row.

## Notes

- The narration is final. Do not rewrite it.
- Captions: soft subtitle track only, no burned-in captions.
- <When the user is not present:> The user is not available for questions. Proceed with these answers.
```

3. Load the `hyperframes` skill and ask it to build and render the project. A `BRIEF.md` on disk lets it run without its interview.

## Verify the render

```bash
ffprobe -v error -show_entries format=duration:stream=codec_type -of json <video.mp4>
```

- The duration is within 15% of the requested length; there is an audio stream and a subtitle stream.
- Extract frames (`ffmpeg -vf fps=0.5`) and look at them at full size: text is readable, nothing is cut off at the edges, no glyph is garbled mid-transform, each scene matches its row.
- Transcribe the audio locally (whisper.cpp when installed) and compare with the narration.

## Hand over

Lead the chat reply with the file path, the length and the voice, then two or
three lines on what the video shows. When the user asked for a free or local
tool, name it, its licence, and the one command that installs it on their
machine, even when it was already installed on yours. Put install and rebuild notes in a
`README.md` next to `source/`, not in the chat.
