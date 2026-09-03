#!/usr/bin/env bash
# Submit changed URLs to IndexNow (api.indexnow.org shares them with every participating engine).
#
# Usage: indexnow.sh [--root docs/seo] <domain> URL [URL ...]
#
# Reads INDEXNOW_KEY_FILE from docs/seo/<domain>/connections.md (written by the jorekai-seo:connect
# wizard), checks that the key file answers 200 with the key as body, then POSTs the URLs as
# one JSON document. Prints the status code with its meaning from the IndexNow documentation
# (seo/references/sources.md, IndexNow row). Exit 0 on 200 or 202, 1 otherwise.
# Google does not take part in IndexNow; "Request indexing" in Search Console is the owner's click.
set -euo pipefail

root="docs/seo"
if [[ "${1:-}" == "--root" ]]; then root="$2"; shift 2; fi
domain="${1:-}"; shift || true
if [[ -z "$domain" || $# -eq 0 ]]; then
  echo "usage: indexnow.sh [--root docs/seo] <domain> URL [URL ...]" >&2; exit 1
fi

connections="$root/$domain/connections.md"
[[ -f "$connections" ]] || { echo "no $connections: run jorekai-seo:connect first" >&2; exit 1; }
key_file=$(sed -n 's/^- *INDEXNOW_KEY_FILE: *\([^ ]*\).*/\1/p' "$connections" | head -1)
[[ -n "$key_file" ]] || { echo "INDEXNOW_KEY_FILE is empty in $connections: run the jorekai-seo:connect wizard, IndexNow stage" >&2; exit 1; }
key=$(basename "$key_file" .txt)
host=$(printf '%s' "$key_file" | sed -E 's#^https?://([^/]+)/.*#\1#')

# 1. The key file must be live, or every submission answers 403.
body=$(curl -s --max-time 15 -A "jorekai-seo:connect indexnow.sh" -w '\n%{http_code}' "$key_file" || printf '\n000')
status=${body##*$'\n'}; body=${body%$'\n'*}
if [[ "$status" != "200" ]]; then echo "key file $key_file answers $status, expected 200" >&2; exit 1; fi
if [[ "$(printf '%s' "$body" | tr -d '[:space:]')" != "$key" ]]; then echo "key file body does not equal the key $key" >&2; exit 1; fi

# 2. Every URL must sit on the key file's host (422 otherwise).
for u in "$@"; do
  case "$u" in
    "https://$host/"*|"http://$host/"*) ;;
    *) echo "$u is not on $host; IndexNow answers 422 for it" >&2; exit 1 ;;
  esac
done

# 3. One POST for all URLs (the endpoint takes up to 10,000).
list=$(printf '"%s",' "$@"); list="[${list%,}]"
payload=$(printf '{"host":"%s","key":"%s","keyLocation":"%s","urlList":%s}' "$host" "$key" "$key_file" "$list")
code=$(curl -s -o /dev/null --max-time 30 -w '%{http_code}' -X POST \
  -H 'Content-Type: application/json; charset=utf-8' -A "jorekai-seo:connect indexnow.sh" \
  --data "$payload" "https://api.indexnow.org/indexnow" || printf '000')

case "$code" in
  200) meaning="submitted: URLs accepted (no indexing guarantee)"; ok=0 ;;
  202) meaning="received: key validation pending"; ok=0 ;;
  400) meaning="bad request: invalid JSON or missing field"; ok=1 ;;
  403) meaning="forbidden: key not valid (key file not found or does not contain the key)"; ok=1 ;;
  422) meaning="unprocessable: a URL does not belong to the host or the key does not match the schema"; ok=1 ;;
  429) meaning="too many requests: wait, then retry with fewer URLs"; ok=1 ;;
  000) meaning="no response from api.indexnow.org"; ok=1 ;;
  *)   meaning="undocumented status"; ok=1 ;;
esac
echo "IndexNow $code $meaning ($# URL(s), host $host, $(date -u +%Y-%m-%dT%H:%MZ))"
exit $ok
