# Benchmark

As of 2026-10-03. Six evals, each run with the skill and with plain Claude Code (same model, no skill). Prompts are in [`skills/legible-explainer/evals/evals.json`](../skills/legible-explainer/evals/evals.json).

## Graded checks

Scripted checks (the STE linter, the page checker, file and fact checks) plus judgement checks scored by a grader agent with screenshots and rendered frames.

| Eval | With the skill | Plain Claude |
|---|---|---|
| STE prose: TCP congestion control | 11 of 12 | 9 of 12 |
| Diagram: OAuth 2.0 + PKCE | 11 of 12 | 8 of 12 |
| Spec sheet: ASD-STE100 overview | 13 of 14 | 9 of 14 |
| Spec sheet: review of an agent-written plan | 12 of 13 | 10 of 13 |
| Video: self-attention, 45 s, local voice | 13 of 13 | 12 of 13 |
| Short answer: mutex vs semaphore | 9 of 9 | 7 of 9 |
| **Pass rate** | **95%** | **76%** |

## Blind reader test

Four reviewers (two Anthropic models, one OpenAI model, one Moonshot model) got each pair of outputs labelled A and B at random, with every mention of the skill removed. For each task they said which output a reader would understand faster and act on.

| Eval | Reviewers who preferred the skill's output |
|---|---|
| STE prose: TCP | 4 of 4 |
| Diagram: OAuth | 4 of 4 |
| Spec sheet: ASD-STE100 | 2 of 4 |
| Spec sheet: plan review | 4 of 4 |
| Video: self-attention | 2 of 4 |
| Short answer: mutex | 4 of 4 |
| **Total** | **20 of 24** |

The first version of the skill won only 7 of 24: it put answers in files behind notes about its own process, shipped no PDF for a sheet meant to be printed, and made a video that did not look like 3Blue1Brown. The current version answers in the chat first, ships A4 and A3 PDFs, and uses Manim for the 3Blue1Brown look.

## Open issues

- A dense six-panel sheet prints at about 5.7 pt on A4. The A3 PDF (about 8.7 pt) is the one to pin up; for a readable A4 sheet, hold it to about four panels.
- Answers can still run a little long (a TCP answer at 1,318 words against a 1,200-word target).
- The checks were designed with the skill, so they reward what the skill aims for. The blind reader test is the fairer comparison.
- One run for each configuration, so small differences are noise.
