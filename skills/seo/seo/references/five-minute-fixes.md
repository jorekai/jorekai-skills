# Five-minute fixes

Pick one when there is no time for the weekly loop. Each is complete on its own.

- GSC > URL Inspection > Request indexing for the page you just changed.
- Move the target keyword into the first 60 characters of the title.
- Add the main GSC query to the H1 if it is missing there.
- Add 2 internal links from older posts to the page you want to push, with the query as anchor text.
- Add alt text to the first image on the page.
- Add a 3-question FAQ at the bottom, questions taken from GSC queries for that page.
- Resubmit `sitemap.xml` in GSC after a batch of new pages, and submit the RSS or Atom feed URL as a second sitemap once (Google accepts feeds for recent URLs).
- Put `fetchpriority="high"` on the hero image and remove `loading="lazy"` from it (web.dev: never lazy-load the LCP image).
- Add `max-image-preview:large` to the robots meta of article templates so Discover can show the large image.
- `site:yourdomain.com` in Google: spot missing pages and ugly titles. Indicative only; GSC URL Inspection is the authority.
- Google your brand plus product keyword: any page that mentions you without a link gets a one-line email asking for the link.
- Ask an AI assistant "best tool for [keyword]"; open the cited pages; email those authors the same day.
- Post the URL on X, LinkedIn, or Reddit with the keyword in the first line.
- Run `jorekai-seo:tech-audit` on the page and apply the first WARN.
