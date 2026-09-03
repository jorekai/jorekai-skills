#!/usr/bin/env bash
# Gate for a public collection: no private data, no em dashes, no filler words.
# Runs over every tracked file. Exit 1 with one line per hit.
#   scripts/check_public.sh
set -uo pipefail
cd "$(dirname "$0")/.."
fail=0
hit() { echo "$1"; fail=1; }

files=$(git ls-files | grep -v 'scripts/check_public.sh$')

# Private data: analytics ids, IndexNow key files, server paths, tracked workspaces. Customer names and
# domains come from .check_public.local (gitignored, one regex per line) so the public script never names them.
private='G-[A-Z0-9]{8,}|[a-f0-9]{32}\.txt|/opt/plesk|--allow-root|ssh_host: [^(]'
if [[ -f .check_public.local ]]; then
  while IFS= read -r pat; do [[ -n "$pat" ]] && private="$private|$pat"; done < .check_public.local
else
  echo "warning: no .check_public.local (customer patterns), only generic checks run" >&2
fi
while IFS= read -r line; do hit "private: $line"; done < <(echo "$files" | xargs grep -nE "$private" 2>/dev/null)
while IFS= read -r f; do hit "workspace tracked: $f"; done < <(echo "$files" | grep -E '^docs/seo/[^/]+/' )
while IFS= read -r f; do hit "link tracked: $f"; done < <(echo "$files" | grep -E '^\.(agents|claude)/skills/')

# Style: em dashes and filler words in prose and code.
while IFS= read -r line; do hit "em dash: $line"; done < <(echo "$files" | xargs grep -n "—" 2>/dev/null)
filler='\b(delve|leverage|seamless(ly)?|robust|crucial|game-changer|in today.s|it.s worth noting|unlock)\b'
while IFS= read -r line; do hit "filler: $line"; done < <(echo "$files" | xargs grep -niE "$filler" 2>/dev/null)

(( fail )) && exit 1
echo ok
