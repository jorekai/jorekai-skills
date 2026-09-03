#!/usr/bin/env bash
# The gate before every commit: STYLE.md rules a script can check, private data, then every offline test.
# Exit 1 with one line per hit; prints ok when everything passes.
#   scripts/check.sh            style and private data, then tests
#   scripts/check.sh --no-tests style and private data only
set -uo pipefail
cd "$(dirname "$0")/.."
fail=0
hit() { echo "$1"; fail=1; }

files=$(git ls-files | grep -v 'scripts/check.sh$')

# Private data: analytics ids, IndexNow key files, server paths, tracked workspaces and links. Customer names
# and domains come from .check_public.local (gitignored, one regex per line) so this script never names them.
private='G-[A-Z0-9]{8,}|[a-f0-9]{32}\.txt|/opt/plesk|--allow-root|ssh_host: [^(]'
if [[ -f .check_public.local ]]; then
  while IFS= read -r pat; do [[ -n "$pat" ]] && private="$private|$pat"; done < .check_public.local
else
  echo "warning: no .check_public.local (customer patterns), only generic private-data checks run" >&2
fi
while IFS= read -r line; do hit "private: $line"; done < <(echo "$files" | xargs grep -nE "$private" 2>/dev/null)
while IFS= read -r f; do hit "workspace tracked: $f"; done < <(echo "$files" | grep -E '^docs/')
while IFS= read -r f; do hit "link tracked: $f"; done < <(echo "$files" | grep -E '^\.(agents|claude)/skills/')

# Style (STYLE.md, "Forbidden"): em dashes, arrows, filler words, emoji. STYLE.md names them and is exempt.
style=$(echo "$files" | grep -v "^STYLE.md$")
while IFS= read -r line; do hit "dash: $line"; done < <(echo "$style" | xargs grep -n "—" 2>/dev/null)
while IFS= read -r line; do hit "arrow: $line"; done < <(echo "$style" | grep -vE '\.(py|sh|json|yaml|yml)$' | xargs grep -nE "→|[[:space:]]->[[:space:]]|[[:space:]]=>[[:space:]]" 2>/dev/null | grep -vE '^[^:]+:[0-9]+:\s*[A-Za-z0-9_"\[\]]+ *(-->|-\.|==)' )
filler='\b(delve|leverage|seamless(ly)?|robust|crucial|game-changer|unlock|in today.s|it.s worth noting|here.s the thing|let that sink in)\b'
while IFS= read -r line; do hit "filler: $line"; done < <(echo "$style" | xargs grep -niE "$filler" 2>/dev/null)
while IFS= read -r line; do hit "emoji: $line"; done < <(echo "$style" | xargs perl -ne 'print "$ARGV:$.:$_" if /[\x{1F300}-\x{1FAFF}\x{2600}-\x{27BF}]/; close ARGV if eof' 2>/dev/null)

# Plugin version equals the top changelog entry; a version bump without a changelog line is a hit.
pv=$(python3 -c 'import json;print(json.load(open(".claude-plugin/plugin.json"))["version"])')
cv=$(grep -m1 -oE '^## [0-9]+\.[0-9]+\.[0-9]+' CHANGELOG.md | cut -c4-)
[[ "$pv" == "$cv" ]] || hit "version: plugin.json says $pv, CHANGELOG.md top entry says $cv"

# Sources older than 180 days are a warning, not a hit: refresh them when touching the skill.
python3 scripts/sources_age.py --days 180 | sed 's/^/warning: stale source: /' | grep -v ': 0 row' >&2

# Secret scan over the whole history when gitleaks is installed (CI always runs it).
if command -v gitleaks >/dev/null; then
  gitleaks git . --no-banner --redact --exit-code 1 >/dev/null 2>&1 && echo "pass: gitleaks" || hit "gitleaks found a secret: run gitleaks git . --redact"
else
  echo "warning: gitleaks not installed, secret scan skipped (brew install gitleaks)" >&2
fi

(( fail )) && exit 1
[[ "${1:-}" == "--no-tests" ]] && { echo ok; exit 0; }

# Offline tests and syntax checks, one per script that a SKILL.md calls.
t() { "$@" >/dev/null 2>&1 && echo "pass: $*" || { echo "FAIL: $*"; fail=1; }; }
t python3 skills/seo/tech-audit/scripts/test_audit.py
t python3 skills/seo/gsc-review/scripts/test_gsc.py
t python3 skills/seo/and-now/scripts/test_status.py
t python3 skills/seo/gsc-review/scripts/gsc_opportunities.py --help
t python3 skills/seo/gsc-review/scripts/snippets.py --help
t python3 skills/seo/setup/scripts/scaffold.py --root "$(mktemp -d)/docs/seo" example.com
t python3 skills/seo/tech-audit/scripts/audit.py --help
t python3 skills/seo/and-now/scripts/status.py --help
t bash -n skills/seo/connect/templates/wizard.sh
t bash -n skills/seo/connect/scripts/indexnow.sh
t bash -n scripts/link.sh
t python3 scripts/sources_age.py --help
for f in $(git ls-files 'skills/*/*/agents/openai.yaml'); do t test -s "$f"; done
for d in $(git ls-files 'skills/*/*/SKILL.md' | xargs -n1 dirname); do t test -f "$d/agents/openai.yaml"; done

(( fail )) && exit 1
echo ok
