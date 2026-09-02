#!/usr/bin/env bash
# Link skills of this collection into a project, for Claude Code and Codex.
#   scripts/link.sh /path/to/repo               link every skill
#   scripts/link.sh /path/to/repo seo            link one bucket (skills/seo/*)
#   scripts/link.sh /path/to/repo seo-setup ...  link named skills (globs ok)
# Claude Code reads <repo>/.claude/skills/<name>/SKILL.md; Codex reads <repo>/.agents/skills/<name>/SKILL.md.
set -euo pipefail
here="$(cd "$(dirname "$0")/.." && pwd)"
repo="${1:?usage: link.sh REPO [BUCKET|SKILL ...]}"
shift || true
[[ -d "$repo" ]] || { echo "no such directory: $repo" >&2; exit 1; }

srcs=()
while IFS= read -r -d '' f; do srcs+=("$(dirname "$f")"); done < <(find "$here/skills" -name SKILL.md -print0 | sort -z)
if (( $# )); then
  sel=()
  for want in "$@"; do
    for s in "${srcs[@]}"; do
      bucket="$(basename "$(dirname "$s")")"; name="$(basename "$s")"
      # shellcheck disable=SC2053
      if [[ "$bucket" == "$want" || "$name" == $want ]]; then sel+=("$s"); fi
    done
  done
  srcs=("${sel[@]}")
fi
(( ${#srcs[@]} )) || { echo "nothing matched" >&2; exit 1; }

for dest in "$repo/.claude/skills" "$repo/.agents/skills"; do
  mkdir -p "$dest"
  for s in "${srcs[@]}"; do
    ln -sfn "$s" "$dest/$(basename "$s")"
    echo "linked $(basename "$s") -> $dest/$(basename "$s")"
  done
done
