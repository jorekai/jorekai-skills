# 0007: The audit crawl obeys robots.txt, and a redirect stays on http

Date: 2026-09-04

## Context

`audit.py` fetches with a Googlebot user agent, which is the point: the report has to show what the index sees. With `--crawl` it then walks the internal links. The site check parsed `robots.txt` to answer "is this page blocked", but the crawl never saw the file and fetched every internal link it found, including paths the owner had disallowed. A tool that names itself Googlebot and ignores the file Googlebot obeys is a misrepresentation, and on a shop or a CMS it walks into search, filter, and account paths that exist for people, not for crawlers. Separately, the redirect chain was followed to whatever a `Location` header named, while `urllib.request.build_opener` installs handlers for `file://` and `ftp://`: a redirect could make the script read a local file into a report that is then committed to the site's repository.

## Decision

The crawl obeys `robots.txt`. A disallowed URL is reported under `crawl.robots-disallowed` and never fetched. The URL given on the command line is fetched even when it is disallowed, because a block on that URL is the finding the run was started for. A redirect is followed only when the target is `http://` or `https://`; anything else ends the fetch with an error in the report.

## Consequences

The crawled set can be smaller than the link graph, and the crawl says by how much, so a site that disallows large areas gets a list instead of silence. Internal links pointing into a disallowed area become visible as a finding of their own. The Googlebot user agent stays and now describes what the script does. It stays pointed at sites the user owns: `config.md` names the domain, and a fetch of somebody else's site for research uses a browser user agent.
