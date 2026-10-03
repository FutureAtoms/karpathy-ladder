# Contributing

Thanks for helping. This skill gets better through examples, sharper checks and honest test results, so a small pull request is as welcome as a big one.

## Good places to start

- **Show an output.** Post a sheet, diagram or video the skill made for you in [Show and tell](https://github.com/FutureAtoms/karpathy-ladder/discussions/categories/show-and-tell). The best ones become examples in `examples/`.
- **Fix a false positive.** If `ste_lint.py` or `check_page.py` flags something correct, open a [checker false positive](https://github.com/FutureAtoms/karpathy-ladder/issues/new?template=checker_false_positive.yml) issue with the smallest input that shows it, or send the fix with a self-test case.
- **Grow the STE word table.** `ste_lint.py` knows a curated list of common unapproved words and their approved alternatives. Add the ones you see LLMs use. Paraphrase the alternatives; do not copy entries from the ASD-STE100 dictionary.
- **Add a rung or a style.** A new video style, a new sheet panel, a diagram type the skill does not draw well yet. Open an [idea](https://github.com/FutureAtoms/karpathy-ladder/issues/new?template=idea.yml) issue first so we can agree on the shape.
- Issues labelled [good first issue](https://github.com/FutureAtoms/karpathy-ladder/labels/good%20first%20issue) are small and well scoped.

## Set up

```bash
git clone https://github.com/FutureAtoms/karpathy-ladder
cd karpathy-ladder
python3 -m pip install playwright
python3 -m playwright install chromium
./tests/check.sh
```

To try your changed skill in Claude Code, link it in place of an installed copy:

```bash
ln -sfn "$PWD/skills/legible-explainer" ~/.claude/skills/legible-explainer
```

Start a new Claude Code session after the link so it loads the new `SKILL.md`. Remove the plugin version first if you installed it, so only one copy is active.

## How the skill is laid out

| Path | What it holds |
|---|---|
| `skills/legible-explainer/SKILL.md` | How to pick a rung, the STE dial, delivery rules. Keep it short; detail goes in `references/`. |
| `references/*.md` | One file for each rung, plus the STE writing guide. Claude reads these only when it needs them. |
| `assets/spec-sheet-template.html` | The working sheet that rung 3 starts from. |
| `scripts/ste_lint.py` | STE linter. Has a `--self-test`. |
| `scripts/check_page.py` | Page checker: 5 widths, print, overlap, accent bars, type size. Has a `--self-test`. |
| `evals/evals.json` | The test prompts behind [docs/benchmark.md](docs/benchmark.md). |

## Rules for changes

- **Every check passes.** Run `./tests/check.sh` before you push. CI runs the same script.
- **A script change needs a self-test case.** Add the input that used to fail to `self_test()` in the script you changed.
- **A change to how the skill writes or draws needs a real run.** Run at least one prompt from `evals/evals.json` with your changed skill, look at the output, and put a screenshot or excerpt in the pull request.
- **STE stays paraphrased.** ASD-STE100 is free to download but copyrighted. Explain rules in your own words and keep quotes from the specification short.
- **Pages stay self-contained.** Inline CSS and JavaScript, images as data URIs, Google Fonts as the only network request. A page must open from `file://`.
- **House style.** The skill's pages use justified body text, no em dashes, no one-sided accent bars and no narrow text columns. `check_page.py` enforces most of this. If you want a different style for yourself, edit your copy; changes to the defaults need a reason in the pull request.

## Adding an example

1. Make a folder in `examples/` named for the rung and the subject, for example `examples/2-diagram-raft-election/`.
2. Put the output in it, plus a short `README.md` with the prompt you used, the model, and the date.
3. Run `./tests/check.sh`. It lints every example and checks every example page.
4. For a video, keep the MP4 under 10 MB and include the narration script and scene plan.

## Benchmark results

If you re-run the evals, report the date, the model, how many runs for each side, and both numbers (with and without the skill). Results where the skill loses are just as useful. Use the [skill-creator](https://github.com/anthropics/skills) eval loop so the numbers compare with [docs/benchmark.md](docs/benchmark.md).

## Pull requests

Keep each pull request to one change. Fill in the template, and expect a review within a few days. By contributing you agree that your work is released under the [MIT license](LICENSE) of this repository.

Everyone here follows the [code of conduct](CODE_OF_CONDUCT.md).
