---
name: update-methodology
description: Procedure for fixing this repo's filter lists when a site changes its layout and a list stops hiding content. Use when a generated filter for reddit/youtube/etc. no longer works, or to periodically re-verify selectors. Doc-only methodology, no automation.
---

# Updating site filters when a site breaks them

Word matching rarely breaks; the **selector** in a source template or a site-rule
does, when a site ships new markup. Symptom: blocked topics start showing again even
though the words are still in the list.

## Diagnose

1. Confirm it's the selector, not the words: open `dist/<region>.txt` and check the
   term is present. If it is, the wrapper/selector is stale.
2. On the live site, open uBlock Origin → **element picker** and click the unit that
   should have been hidden (a feed card, a comment). Note the element type and a
   stable attribute (a tag like `shreddit-post`, a `data-*` attribute, an `href`
   prefix). Avoid hashed/random class names.
3. Cross-check in the uBlock **logger** which existing filter (if any) is matching.

## Fix

- If the **wrapper** changed (the container element), edit the `template` in
  `sources/<site>.yml`. Keep the `{TERMS}` placeholder and the `\b…\b` / `/i`.
- If a **site-rule** selector changed, edit that entry in `site-rules/<site>.yml`.
- Test the new filter live first: paste it into uBlock → *My filters*, reload the
  page, confirm the unit is hidden and that ordinary content is not.

## Apply

```sh
uv run python scripts/validate.py
uv run python scripts/generate.py
```

Optionally bump `expires` in the affected `words/<region>.yml` `meta` down (e.g.
`1 day`) so subscribers refresh sooner, then restore it once stable. Commit the
template/rule change with the regenerated `dist/`.

## Periodic re-verification (semi-automatic)

No automated DOM checks (kept simple by design). Re-verify by hand on a cadence:

1. For each `sources/<site>.yml`, visit the site, scroll a known-noisy feed, and
   confirm matching content is hidden.
2. Spot-check one tier-1 term per source via the logger.
3. Fix any stale selector per above.

If automation is wanted later, the smallest useful step is a headless browser that
loads a fixture page per site and asserts each template's selector still matches at
least one node — out of scope for now.
