# Benchmark

As of 2026-10-03. Six tasks, each run once with the skill and once with plain Claude Code (same model, no skill), both on the same day. Prompts are in [`skills/legible-explainer/evals/evals.json`](../skills/legible-explainer/evals/evals.json).

## Graded checks

Scripted checks (the STE linter, the page checker, file and fact checks) plus judgement checks scored by a grader agent that rendered every page and watched every video frame.

| Task | With the skill | Plain Claude |
|---|---|---|
| STE prose: TCP congestion control | 12 of 12 | 9 of 12 |
| Diagram: OAuth 2.0 + PKCE | 11 of 12 | 7 of 12 |
| Spec sheet: ASD-STE100 overview | 11 of 14 | 12 of 14 |
| Spec sheet: review of an agent-written plan | 13 of 13 | 6 of 11 |
| Video: self-attention, 45 s, local voice | 12 of 13 | 12 of 13 |
| Short answer: mutex vs semaphore | 9 of 9 | 7 of 9 |
| **Pass rate** | **93%** (68 of 73) | **75%** (53 of 71) |

Plain Claude has fewer checks on two tasks because it delivered no page there, so the page checks did not apply.

## Blind reader test

Four AI reviewers from three model families (two Anthropic models, one OpenAI model, one Moonshot model) got each pair of outputs labelled A and B at random, with every mention of the skill removed. For each task they said which output a reader would understand faster and act on.

| Task | Skill preferred | Tie | Plain Claude preferred |
|---|---|---|---|
| STE prose: TCP | 4 | | |
| Diagram: OAuth | 2 | | 2 |
| Spec sheet: ASD-STE100 | 1 | | 3 |
| Spec sheet: plan review | 4 | | |
| Video: self-attention | 4 | | |
| Short answer: mutex | 2 | 2 | |
| **Total (24 judgements)** | **17** | **2** | **5** |

## How it got here

| Version | Blind preference for the skill | What changed |
|---|---|---|
| First draft | 7 of 24 | Answers sat in files behind notes on process; no PDF for a sheet meant to be printed; the video did not look like 3Blue1Brown |
| Second | 20 of 24 | Answer first in the chat, A4 and A3 PDFs, Manim for the 3Blue1Brown look (compared against the first round's plain-Claude outputs) |
| Third (this table) | 17 of 24, 2 ties | Shorter answers that count their words; both sides re-run fresh the same day |

## Where it still loses, and what changed after

- **The STE sheet.** In this run the skill dropped the reference's History panel and drew a near-square sheet, so the A4 print left a quarter of the page blank. The skill now keeps every panel the reference asks for and lays the sheet out in the paper's landscape shape.
- **The OAuth diagram.** Plain Claude built an interactive page with a compact mode that fits one screen. The skill now asks for a working diagram that fits a 1080p screen, with a marker for which steps show in the browser's DevTools.
- **Cost.** About 390 s more per task than plain Claude, mostly spent on checking the page and verifying facts.

## Limits of this test

- One run for each configuration, so a difference of one check or one reviewer is noise.
- The checks were designed with the skill, so they reward what the skill aims for. The blind reader test is the fairer comparison.
- The fixes listed above came after this run and are not yet measured.
