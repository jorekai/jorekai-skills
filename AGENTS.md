# Working in this collection

Skills live under `skills/<theme>/<skill>/`; `README.md` explains the layout and the SEO loop. Rules for editing:

- Everything is English: skill prose, references, templates, scripts, comments, this file. German appears only as matching data for German-language sites (stopwords, soft-404 phrases, names of legal documents).
- Every claim about how a platform, product, or Google feature behaves lives in `references/` and has a row in `skills/seo/seo/references/sources.md` with URL and check date, verified against the primary source before it is written. Unverified means labelled as a heuristic or left out.
- The router must not lie: adding, renaming, or changing a sub-skill updates `skills/seo/seo/SKILL.md` and the tables in `README.md` in the same commit.
- Test a script before editing the SKILL.md that calls it: `python3 skills/seo/seo-tech-audit/scripts/test_audit.py` (offline) and `python3 skills/seo/seo-tech-audit/scripts/audit.py https://example.com`, `python3 skills/seo/seo-gsc-review/scripts/gsc_opportunities.py --help`, `python3 skills/seo/seo-setup/scripts/scaffold.py --root /tmp/x example.com`, `bash -n skills/seo/seo-connect/templates/wizard.sh`. Scripts stay Python stdlib or bash.
- Every line in a SKILL.md must change behaviour; what the model does anyway goes. Steps end on a completion criterion; reference material sits behind a pointer, not inline.
- A new skill is user-invoked (`disable-model-invocation: true` plus `policy.allow_implicit_invocation: false` in `agents/openai.yaml`) unless the agent must reach it on its own; then it gets a model-facing `description` with one trigger per branch. Every skill has `agents/openai.yaml`.

## SEO

SEO workspace: `docs/seo/README.md` (layout, log format). Domains: example-bootsschule.de. Read `docs/seo/<domain>/config.md` before running any `seo-*` skill; every change to the site gets a row in `docs/seo/<domain>/log/`.
