---
name: refresh-vocabulary
description: Discover and propose current/trending political terms (new officeholders, candidates, parties, scandals, hot topics) for words/*.yml. Use periodically, before elections, or after big events — counters vocabulary staleness and the model's training-cutoff gaps. Run agent-assisted with web tools; it PROPOSES candidates for human review and adds only what the human approves.
---

# Refresh the vocabulary with current terms

The vocabulary goes stale: ministers change, new candidates emerge, scandals and
slogans appear, AI products launch. A model curating this list is also limited by
its **training cutoff** — it will not know the newest names. This skill pulls fresh
terms from authoritative, low-noise live sources and folds them into `words/*.yml`.

## Sources (best signal first)

Prefer structured lists of *current* entities over free-form news — they are
low-noise and easy to harvest.

**1. Current officeholders & candidates** (highest signal):
- US: Wikipedia "Cabinet of the United States", "List of current United States
  senators", "List of current members of the United States House of
  Representatives", "List of current state governors", and the current cycle's
  "20XX United States elections".
- CL: Wikipedia "Gabinete de <presidente actual>", "Cámara de Diputadas y Diputados
  de Chile" (current period), "Senado de Chile" (current), and the active election
  page e.g. "Elecciones presidenciales de Chile de 20XX". Party pages for new parties.

**2. Current-events portals** (dated, name-rich):
- `en.wikipedia.org/wiki/Portal:Current_events` (+ monthly archives)
- `es.wikipedia.org/wiki/Portal:Actualidad`

**3. The platform you actually block** (reflects the real noise):
- Top post titles from the subreddits you read: fetch `reddit.com/r/<sub>/top/?t=month`
  for r/politics, r/worldnews, r/chile, etc. These surface the slang, nicknames, and
  scandals trending *now* (often missing from encyclopedic sources).

**4. Headlines** (last resort, noisier): WebSearch `top political news this week
<country>` and skim recurring proper nouns.

## Procedure (human-in-the-loop)

**The human selects which words go in.** The agent gathers, dedupes, and proposes;
the human vets; only then does the agent edit the lists. **Never add a term without
explicit approval.**

1. **Pick** a region and 2–3 sources above.
2. **Fetch** them (WebFetch / WebSearch) and extract candidate terms:
   - proper nouns: people, parties, organizations, places
   - recurring topic/scandal keywords and slogans
3. **Dedupe** against the existing lists. Lowercase-compare each candidate to every
   term in `words/<region>.yml`; drop ones already covered (patterns like
   `Democrats?` already cover "democrat"/"democrats").
4. **Build a proposal — do not edit any file yet.** Present the surviving candidates
   as a table, one row per term, with the proposed:
   - region + category (figures, geopolitics, ai, economy, instituciones, …)
   - literal vs `pattern:` (patterns for plurals, accents `[íi]`, optional groups)
   - tier by false-positive risk (see `curate-words`):
     1 = current official/candidate/distinctive name · 2 = charged topic/scandal ·
     3 = generic word, common surname, party acronym · 4 = extreme FP, often `cs: true`
   - case sensitivity (`cs: true` for all-caps acronyms that are common words)
5. **Human review gate (required).** The human vets the proposal — approves, edits
   tiers/categories, or rejects rows. Add nothing until this happens.
6. **Apply only the approved rows** to `words/<region>.yml`, then
   `uv run python scripts/validate.py` and `uv run python scripts/generate.py`.
7. **Stamp** the refresh: bump `meta.last_refreshed: YYYY-MM-DD` (and lower `expires`
   briefly if a big event is unfolding).
8. **Commit** the approved word changes with the regenerated `dist/`.

## Triage heuristics

- A name with no other common meaning (Boric, Mamdani, Newsom) → literal, tier 1.
- A common surname used for a politician (Sanders, Johnson) → phrase form
  ("Bernie Sanders") at tier 1, plus the bare surname at tier 2 if wanted.
- Party acronyms (PS, DC, PPD, RN) → tier 3; if they collide with a common
  uppercase word, tier 4 + `cs: true`.
- Country/region names (China, France) → tier 2–3 (broad).
- AI products (Gemini, Grok) → `ai` category, tier 2 (some, like Gemini/Copilot,
  carry FP).

## Cadence

Triggered manually for now — a human starts each pass. Automatable later (see below),
but the human review gate in step 5 stays.

- **Monthly** light pass from sources 1–2.
- **Weekly** in the ~2 months before a major election in a covered region.
- **Ad hoc** after a major event (war escalation, large scandal, cabinet change).

## Caution

Fetching sends queries to external services; fine for public encyclopedic/news
data. Do not fetch authenticated or private pages.

## Future automation (out of scope, KISS for now)

A script could fetch the fixed officeholder-list URLs, extract names, and diff
against `words/*.yml` to print only the new candidates for human triage. Keep the
*judgement* (tier, category, FP) human/agent-assisted; only the *gathering* should
be automated.
