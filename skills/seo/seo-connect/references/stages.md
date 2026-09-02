# Stages

Each journey below was checked against the vendor's documentation on the date in [../../seo/references/sources.md](../../seo/references/sources.md). UI labels drift; when the page in front of the user differs, the wizard's `step` text is what to update.

## 1. Search Console property

Records `GSC_PROPERTY`, `GSC_PROPERTY_TYPE`, `GSC_VERIFICATION`, `GSC_VERIFIED_AT`.

- Open `https://search.google.com/search-console/welcome`.
- **Domain property** (recommended: it "includes all subdomains (m, www, and so on) and multiple protocols", so one property covers every host variant). Verification is DNS only: a TXT record, host left blank or `@`; a CNAME variant exists for providers where a CNAME is present and the target is a parent domain. Google says manually added records can take "up to two or three days" to be served, so the wizard offers `skip` with a reminder rather than blocking.
- **URL-prefix property** when the user cannot touch DNS: HTML file upload, HTML tag in `<head>`, Google Analytics, or Google Tag Manager. The HTML tag goes into `head_template` from `config.md`; the agent adds it before the wizard runs, the human deploys.
- Several verification methods can coexist; adding a second one is insurance.
- `GSC_PROPERTY` is written as Search Console shows it: `sc-domain:example.com` or `https://example.com/`. Both can exist for one site; record the domain property as `GSC_PROPERTY` and mention the url-prefix one in the same value.
- A `google-site-verification` meta tag in the live HTML means a url-prefix property was verified by html-tag at some point; the wizard asks whether it still exists instead of creating a new one.

## 2. Sitemap

Records `SITEMAP_URL`, `SITEMAP_SUBMITTED_AT`.

- Wizard pre-check: `http_status "$SITEMAP_URL"` must be 200; otherwise `skip`.
- Open `https://search.google.com/search-console/sitemaps`, select the property, paste the URL into "Add a new sitemap", Submit.
- Status column: `Success` means fetched and read without errors; `Couldn't fetch`, `Has errors`, `Unknown` are the failures. Google retries a failed fetch "for a few days, and then stop[s]", so a red status is fixed now, not later.
- Resubmit only after significant changes; otherwise Google follows its regular schedule.

## 3. Bing Webmaster Tools

Records `BING_IMPORTED_AT`.

- Open `https://www.bing.com/webmasters`. Sign in.
- My Sites → Import → sign in with the Google account that owns the Search Console property → Allow → tick the site → Import. Imported sites arrive verified, with their sitemaps; traffic data can take up to 48 hours. Bing re-syncs ownership with Search Console periodically, so revoking that Google access later drops the verification.
- Why: Bing's index is what ChatGPT search and Copilot retrieve from (see `seo/references/tools.md`).

## 4. IndexNow

Records `INDEXNOW_KEY_FILE`, `INDEXNOW_TESTED_AT`.

- Precondition (agent, step 2 of the skill): key of 8 to 128 characters from `a-z`, `A-Z`, `0-9`, `-`; hosted as `https://<host>/<key>.txt` containing the key.
- Wizard: `http_status "https://<host>/<key>.txt"` must be 200 and the body must equal the key. Then a test submission: `http_status "https://api.indexnow.org/indexnow?url=<canonical_host>/&key=<key>"`. Expected 200 (submitted) or 202 (received, key validation pending). 403 means the key file was not found or does not contain the key; 422 means the URL does not belong to the host; 429 means too many requests. Submissions to `api.indexnow.org` are shared with every participating engine (Bing, Naver, Seznam, Yandex, Yep, Amazon; Google is not one).
- After that, `seo-content` and `seo-tech-audit` may push changed URLs through the same endpoint (`GET` per URL, or `POST` JSON with up to 10,000 URLs).

## 5. Analytics (optional)

Records `ANALYTICS`.

- Only the tool name and property or site id, so later skills know where on-site behaviour is visible. No setup steps: every tool differs, and Search Console stays the source of truth for search data.
