---
name: site-filters
description: Add a new target site (sources/*.yml) or a site-specific raw filter (site-rules/*.yml) to this repo. Use when supporting a new platform (YouTube, X, Instagram) or blocking something site-specific like a whole subreddit/channel. Not for adding words (see curate-words).
---

# Site filters

Two mechanisms turn words into per-site filters.

## A. Add a source (a new site)

A source wraps every word into that site's filter syntax. Create
`sources/<site>.yml`:

```yaml
id: youtube
name: YouTube
template: 'youtube.com##ytd-rich-item-renderer:has-text(/\b(?:{TERMS})\b/i)'
```

- `id` — unique; also the key `site-rules/<site>.yml` matches on.
- `template` — **must** contain `{TERMS}`. The generator substitutes a
  `|`-alternation of the selected terms there.
- The template owns the wrapper, the word boundaries (`\b…\b`), and the `/i` flag.
  Choose the cosmetic selector for the unit you want to hide (a feed card, a
  comment, a search result) — find it with uBlock's element picker (see
  `update-methodology`).
- If a term needs different boundaries than the template's `\b…\b`, express it as a
  `pattern:` in the word list instead of changing the template.

Generating picks up every `sources/*.yml` automatically and appends its block to
each region's output.

## B. Add a site-specific rule

For things that aren't word-matching — a whole subreddit, a channel, a feed module —
add a raw filter to `site-rules/<site>.yml`:

```yaml
id: reddit
rules:
  - filter: 'reddit.com##article:has(a[href^="/r/politics/"])'
    tier: 1
    note: Hide feed posts from r/politics.
```

- `filter` — a complete, valid uBlock filter line (you write the whole thing).
- `tier` — 1–3, same meaning as words; controls which `dist` files include it.
- `note` — optional; emitted as a comment above the rule.

These are site-fragile: verify them against the live site and re-check when the
layout changes (`update-methodology`).

## After editing

```sh
uv run python scripts/validate.py     # checks {TERMS}, rule filters and tiers
uv run python scripts/generate.py
```

Commit the source/site-rule change **and** the regenerated `dist/`.
