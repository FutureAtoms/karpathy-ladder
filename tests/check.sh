#!/usr/bin/env bash
# Runs every check that CI runs. Use it before you open a pull request:
#   ./tests/check.sh
# Needs Python 3.10+ and Playwright (pip install playwright && playwright install chromium).
set -euo pipefail
cd "$(dirname "$0")/.."

S=skills/legible-explainer/scripts
# Screenshots and reports go to a temporary folder, or to $CHECK_OUT when it is set (CI keeps them).
if [ -n "${CHECK_OUT:-}" ]; then
  OUT=$CHECK_OUT; mkdir -p "$OUT"
else
  OUT=$(mktemp -d); trap 'rm -rf "$OUT"' EXIT
fi
fail=0

step() { printf '\n== %s\n' "$1"; }

step "manifests and evals are valid JSON"
python3 - <<'PY'
import json
for p in [".claude-plugin/plugin.json", ".claude-plugin/marketplace.json", "skills/legible-explainer/evals/evals.json"]:
    json.load(open(p, encoding="utf-8"))
    print("ok  ", p)
PY

step "STE linter self-test"
python3 "$S/ste_lint.py" --self-test || fail=1

step "page checker self-test"
python3 "$S/check_page.py" --self-test || fail=1

step "STE prose in the examples"
while IFS= read -r f; do
  if out=$(python3 "$S/ste_lint.py" "$f"); then echo "${out##*$'\n'}"; else echo "$out"; fail=1; fi
done < <(find examples -name '*.md' \( -path '*1-ste-prose*' -o -name 'chat-reply.md' -o -name '*-narration.md' \) | sort)

step "HTML pages: the template and the examples"
while IFS= read -r f; do
  if out=$(python3 "$S/check_page.py" "$f" --out "$OUT/$(basename "$f" .html)"); then echo "${out%%$'\n'*}"; else echo "$out"; fail=1; fi
done < <({ echo skills/legible-explainer/assets/spec-sheet-template.html; find examples -name '*.html'; } | sort)

if [ "$fail" -ne 0 ]; then
  printf '\nSome checks failed. See the output above.\n'
  exit 1
fi
printf '\nAll checks passed.\n'
