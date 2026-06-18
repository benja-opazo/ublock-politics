# ublock-politics

Curated [uBlock Origin](https://github.com/gorhill/uBlock) filter lists that mute
political, current-events, war, and AI noise on social media.

You edit a clean, tiered **word list** (`words/*.yml`); a script wraps those words
in **site templates** (`sources/*.yml`) and produces the subscribable filter lists
in `dist/`. Words are decoupled from sites, so a site can be re-targeted without
touching the vocabulary, and the vocabulary grows without touching site selectors.

## Subscribe (in uBlock Origin)

Dashboard → *Filter lists* → scroll to *Import…* → paste a raw link below →
*Apply changes*. You can stack several (e.g. `us` + `cl`). All files live in
[`dist/`](https://github.com/benja-opazo/ublock-politics/tree/main/dist).

Tiers are **exclusive slices**: each `<region>-N` list holds *only* that tier. The
master (`cl.txt` / `us.txt`) is all tiers combined — subscribe to it to block
everything, or stack individual tiers (e.g. `cl-1` + `cl-2`) for an in-between
strictness.

### 🇨🇱 Chile

- All tiers: `https://raw.githubusercontent.com/benja-opazo/ublock-politics/main/dist/cl.txt`
- Tier 1 only — safest: `https://raw.githubusercontent.com/benja-opazo/ublock-politics/main/dist/cl-1.txt`
- Tier 2 only: `https://raw.githubusercontent.com/benja-opazo/ublock-politics/main/dist/cl-2.txt`
- Tier 3 only: `https://raw.githubusercontent.com/benja-opazo/ublock-politics/main/dist/cl-3.txt`
- Tier 4 only — extreme FP: `https://raw.githubusercontent.com/benja-opazo/ublock-politics/main/dist/cl-4.txt`

### 🇺🇸 United States

- All tiers: `https://raw.githubusercontent.com/benja-opazo/ublock-politics/main/dist/us.txt`
- Tier 1 only — safest: `https://raw.githubusercontent.com/benja-opazo/ublock-politics/main/dist/us-1.txt`
- Tier 2 only: `https://raw.githubusercontent.com/benja-opazo/ublock-politics/main/dist/us-2.txt`
- Tier 3 only: `https://raw.githubusercontent.com/benja-opazo/ublock-politics/main/dist/us-3.txt`
- Tier 4 only — extreme FP: `https://raw.githubusercontent.com/benja-opazo/ublock-politics/main/dist/us-4.txt`

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
