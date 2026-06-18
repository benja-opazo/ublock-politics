---
name: curate-words
description: Add, edit, or re-tier blocked terms in this repo's word lists (words/*.yml). Use when curating the vocabulary — adding political figures, parties, topics, playwords, or adjusting a term's false-positive tier. Not for site selectors (see site-filters).
---

# Curate words

The vocabulary lives in `words/<region>.yml` (e.g. `cl`, `us`). It is the source of
truth; `dist/` is generated from it.

## Add or edit a term

1. Open `words/<region>.yml`. Find the matching `category` (or add one with a unique
   `id`, a `name`, an optional `description`, and a `default_tier`).
2. Add the term in the form that fits:
   - **Literal** (most terms): a bare string — `- boric`. The generator regex-escapes
     it, so write it plainly even if it has spaces or punctuation (`- frente amplio`).
   - **Literal with a tier** different from the category default:
     `- { term: rn, tier: 3 }`.
   - **Pattern** when you need a regex — plurals, accents, optional groups, custom
     boundaries: `- { pattern: 'diputado(?:s)?' }` or
     `- { pattern: 'contralor[íi]a', tier: 1 }`. Inserted verbatim into the
     alternation, so you own the regex.
   - **Case-sensitive**: add `cs: true` to match the exact case only —
     `- { term: US, tier: 4, cs: true }` blocks "US" but not "us". Use for all-caps
     acronyms that are common lowercase words (`US`, `PC`).
3. Assign a **tier** by false-positive tolerance (not importance):
   - **1** — unambiguously political / on-topic (`Trump`, `boric`).
   - **2** — strongly associated, some FP (`carabineros`, `MAGA`, `ICE`).
   - **3** — tangential / playword / high-FP (`Elmo`, `LGBT`).
   - **4** — extreme FP, opt-in only (`Historical`); pair with `cs: true` for
     all-caps-only terms.
   When unsure, prefer the higher number (safer for cautious subscribers).

## Rules

- **No duplicate term within a region** (case-insensitive). If a term fits two
  categories, pick one. The validator rejects duplicates.
- Don't add `\b` or `/i` to terms — the source template owns boundaries and flags.
- Quote patterns in single quotes so YAML keeps backslashes literal:
  `'d\.?d\.?h\.?h\.?'`.

## After editing

```sh
uv run python scripts/validate.py     # tiers valid, patterns compile, no dupes
uv run python scripts/generate.py     # rebuild dist/
```

Commit the changed `words/<region>.yml` **and** the regenerated `dist/` together.

## New region

Create `words/<new>.yml` with a `meta` block (`region`, `title`, `description`,
`expires`) mirroring `words/us.yml`, then generate. Output files
`dist/<new>{,-1,-2,-3}.txt` appear automatically.
