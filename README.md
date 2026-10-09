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

Site rules (whole-subreddit blocks, DOM/URL rules) are **not region-specific** —
they're a separate list, independent of tier and region. Stack it with any region's
word list for full coverage, or skip it to keep only word-based hiding.

### 🌐 Subreddits & site rules

- All sites, all regions: `https://raw.githubusercontent.com/benja-opazo/ublock-politics/main/dist/subreddits.txt`

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
uv run python scripts/check_post.py --url "<reddit post url>"   # why would/wouldn't this post be hidden?
```

**`dist/` is generated — never edit it by hand.** Edit the YAML and regenerate.

### Debugging a false positive / miss

Reddit filters match a post's title, selftext preview, flair, and subreddit name
(not just the title), so a post can get hidden by a word that never appears in
its title. `scripts/check_post.py` replays the same word/site-rule
matching offline against a post URL (or manually-typed fields) and reports exactly
which term/tier matched and in which field. For live debugging, uBlock's own
**Logger** panel (toolbar icon → the chart icon) shows which specific filter fired
on a given element in real time — the fastest way to confirm a hit or a miss.

If a whole subreddit isn't being hidden, the likely cause is Reddit's DOM: the
`site-rules/*.yml` filters were written against a specific layout and are marked
`VERIFY against current Reddit DOM` because they haven't all been checked live —
see `.claude/skills/update-methodology` to re-verify and fix a broken selector.

## Layout

```
words/<region>.yml      vocabulary: categories of terms, each with a tier  (edit this)
sources/<site>.yml      per-site filter template using the {TERMS} placeholder
site-rules/<site>.yml   raw site-specific filters (subreddits, memes), tier-tagged
scripts/generate.py     words × sources × tier -> dist/<region>*.txt
                        site-rules × sources     -> dist/subreddits.txt
scripts/validate.py     lints tiers, regex, duplicates, templates
dist/                   generated, subscribable lists
```

## Extending

- **Add/curate words** → `.claude/skills/curate-words`
- **Add a site or site-specific rule** → `.claude/skills/site-filters`
- **Fix a list a site broke** → `.claude/skills/update-methodology`
