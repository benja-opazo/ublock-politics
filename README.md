# ublock-politics

Curated [uBlock Origin](https://github.com/gorhill/uBlock) filter lists that mute
political, current-events, war, and AI noise on social media.

You edit a clean, tiered **word list** (`words/*.yml`); a script wraps those words
in **site templates** (`sources/*.yml`) and produces the subscribable filter lists
in `dist/`. Words are decoupled from sites, so a site can be re-targeted without
touching the vocabulary, and the vocabulary grows without touching site selectors.

## Subscribe (in uBlock Origin)

Dashboard → *Filter lists* → *Import…* → paste a raw URL of a file in `dist/`.

Each region (`cl`, `us`, …) ships four lists by **tier** — pick your tolerance for
false positives:

| File            | Contains            | For                                  |
|-----------------|---------------------|--------------------------------------|
| `<region>-1.txt`| tier 1 only         | cautious — unambiguously political    |
| `<region>-2.txt`| tier 2 only         | charged terms (crime, geopolitics)    |
| `<region>-3.txt`| tier 3 only         | tangential / playwords / high-FP      |
| `<region>-4.txt`| tier 4 only         | extreme false positives — opt-in only |
| `<region>.txt`  | all tiers (master)  | block everything                      |

Tiers are **exclusive slices**. Subscribe to one master (`cl.txt`) to block all, or
stack individual tiers (`cl-1.txt` + `cl-2.txt`) for an in-between setting.

Tier meaning:

- **1** — unambiguously political / on-topic (e.g. `boric`, `Trump`).
- **2** — strongly associated; some false positives (e.g. `carabineros`, `MAGA`).
- **3** — tangential, playwords, or high false-positive (e.g. `Elmo`, `LGBT`).
- **4** — extreme false positives; opt-in only (e.g. `Historical`, and the
  case-sensitive `US` / `PC`).

Some tier-4 terms are matched **case-sensitively** (all-caps only) so `US` blocks
"US" but not the pronoun "us".

## Develop

Requires [uv](https://docs.astral.sh/uv/).

```sh
uv sync                                  # create .venv, install deps
uv run python scripts/validate.py        # lint the YAML data
uv run python scripts/generate.py        # rebuild dist/ from words + sources
uv run python scripts/generate.py --check  # CI: fail if dist/ is stale
```

**`dist/` is generated — never edit it by hand.** Edit the YAML and regenerate.

## Layout

```
words/<region>.yml      vocabulary: categories of terms, each with a tier  (edit this)
sources/<site>.yml      per-site filter template using the {TERMS} placeholder
site-rules/<site>.yml   raw site-specific filters (subreddits, memes), tier-tagged
scripts/generate.py     words × sources × tier  ->  dist/
scripts/validate.py     lints tiers, regex, duplicates, templates
dist/                   generated, subscribable lists
```

## Extending

- **Add/curate words** → `.claude/skills/curate-words`
- **Add a site or site-specific rule** → `.claude/skills/site-filters`
- **Fix a list a site broke** → `.claude/skills/update-methodology`
