# CLAUDE.md

Guidance for working in this repo.

## What this is

A generator for uBlock Origin filter lists that hide political / news / war / AI
content. The design separates **what to block** (words) from **where/how to block
it** (site templates), so each evolves independently.

## Data flow

```
words/<region>.yml  ─┐
sources/<site>.yml  ─┼─►  scripts/generate.py  ─►  dist/<region>{,-1,-2,-3}.txt
site-rules/<site>.yml┘
```

- `words/<region>.yml` — vocabulary grouped into categories; **the source of truth**.
- `sources/<site>.yml` — a filter template with a `{TERMS}` placeholder. The generator
  builds a `|`-alternation of the selected terms and substitutes it in. One filter
  line is emitted per category, per source.
- `site-rules/<site>.yml` — raw, hand-written filters that target a site's DOM/URLs
  directly (e.g. whole subreddits). Appended per source, filtered by tier.
- `dist/` — **generated output, committed to the repo. Never hand-edit.**

## Term model

A term in a category is one of:

- `"boric"` — literal; the generator regex-escapes it.
- `{ term: "rn", tier: 3 }` — literal with an explicit tier.
- `{ pattern: 'senado(?:r(?:es)?)?', tier: 1 }` — raw regex fragment, inserted
  verbatim. Use a pattern for plurals, accents, optional groups, or custom boundaries.

Add `cs: true` to any term/pattern to match it **case-sensitively** (e.g.
`{ term: US, tier: 4, cs: true }` blocks "US" but not "us"). Case-sensitive terms
are emitted on their own filter line without the `/i` flag.

`default_tier` on a category sets the tier for bare-string terms; inline `tier:`
overrides it.

## Tiers (false-positive tolerance, not topical importance)

- **1** — unambiguously political / on-topic.
- **2** — strongly associated; some false positives.
- **3** — tangential, playwords, or high false-positive.
- **4** — extreme false positives; opt-in only. Often paired with `cs: true`.

`dist/<region>-N.txt` holds tier N **only** (exclusive, N = 1–4). `dist/<region>.txt`
is the master (all tiers, self-contained — it does not use `!#include`).

## Invariants

- Edit YAML, then run `uv run python scripts/generate.py`. CI fails if `dist/` is
  stale (`generate.py --check`).
- A term must not be duplicated within a region (case-insensitive); the validator
  enforces this. Patterns must compile. Tiers must be 1–3.
- The outer `\b(?:…)\b` lives in the **source template**; the regex flag is the
  template's `{FLAGS}` placeholder, set per group by the generator (`i` for
  case-insensitive terms, empty for `cs: true` terms).

## Commands

```sh
uv sync
uv run python scripts/validate.py            # lint
uv run python scripts/generate.py            # build dist/
uv run python scripts/generate.py --check    # verify dist/ is current
```

## Tasks → skills

- Curating the vocabulary: `.claude/skills/curate-words`
- Adding a source/site or site-specific rule: `.claude/skills/site-filters`
- Repairing a list after a site layout change: `.claude/skills/update-methodology`
- Refreshing the vocabulary with current/trending terms: `.claude/skills/refresh-vocabulary`

Vocabulary goes stale and the model's training cutoff misses recent names — run
`refresh-vocabulary` periodically. Each `words/<region>.yml` records `last_refreshed`.

## Conventions

- Concise, factual comments. YAML over other formats (chosen for human editing).
- Python ≥3.10, single dependency (PyYAML), managed with uv.
- Never run write git commands (commit, push, switch), only read non destructive commands.
