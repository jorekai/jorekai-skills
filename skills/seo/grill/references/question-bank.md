# Question bank: the design tree

Roots first. Indented items depend on the item above them. Per node: what the agent looks up before asking, then the questions, then the default to recommend. Answers land in the named `strategy.md` section.

## Offer (root), writes "Offer"

Look up: home page, pricing or product pages, footer, `git log` for what shipped recently.

- What does the site sell or do, in one sentence a customer would say?
- Which pages are the money pages (purchase, sign-up, contact, booking)?
- What happens after a visitor converts (so the content can point there)?
Default: the home page's own claim, quoted back for correction.

## Audience (root), writes "Audience"

Look up: language and market from `config.md`; device split and countries from the export if present.

- Who is searching: role, situation, what they tried before landing here?
- B2B or B2C; mobile or desktop; language(s) and market(s)?
- What do they call the problem, in their words? (First glossary entries.)
Default: derive from the offer and the export's country and device tables.

## Constraints (root), writes "Constraints"

- Is any topic YMYL or regulated (health, money, legal, safety)? Then evidence and bylines are non-negotiable.
- Brand voice in two lines; words the brand never uses.
- Topics the site will not write about, competitors it will not name.
- Capacity: pages per week, who writes, who approves, who can supply screenshots and numbers.
Default: one page a week, the user writes with the agent, the user approves.

## Competitors (needs Offer, Audience), writes "Competitors"

Look up first: WebSearch the three most obvious queries for the offer; note the top 10 domains per query; fetch the top 3 pages. Present the list before asking.

- Which of these do you consider competitors, which are noise (marketplaces, Wikipedia, news)?
- Anyone missing that you meet in sales or on social?
- Per competitor: what do they do better, what worse (pricing clarity, depth, tooling, trust)?
Default: the domains that appear in two of three SERPs.

## Keywords (needs Offer, Audience, Competitors), writes "Keyword clusters"

Look up first: expand the seed queries via the SERPs (titles, People-also-ask, related searches), the export's queries table, and competitor titles; cluster by intent (informational, commercial, transactional, navigational); propose one primary query per cluster and a page. Present the table before asking.

- Which clusters matter for money, which for reach?
- Priority order (top three first); anything to drop?
- For each top cluster: existing URL, or a slug to plan?
Default: commercial clusters where the site already has impressions first, then informational clusters that feed them by internal links.

## Evidence (needs Keywords), writes "Evidence inventory"

- What first-hand material exists: own data, tests run, screenshots, customer results, benchmarks, before/after numbers, failures?
- Where does it live (folder, dashboard, spreadsheet, person)?
- Which clusters can each item support?
- What could be produced within a week if a page needs it?
Default: list what the site already shows publicly, then ask what is unpublished.

## Vocabulary (every round), writes "`glossary.md`"

- For each term the user used this round that the audience would not search for: what does the audience say instead?
- Two words for one thing: which one wins on the page?
Default: the term with more search impressions or SERP occurrences wins; the other goes under `_Avoid_`.

## Open questions (close), writes "Open questions"

Anything the user deferred, with the recommended answer, so the next session starts there.
