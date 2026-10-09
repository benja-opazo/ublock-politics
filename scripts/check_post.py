#!/usr/bin/env python3
"""Check whether a specific Reddit post would be hidden by our filters.

The Reddit filters test the post's title, selftext preview, flair, and
subreddit name — not just the title. This reproduces that check offline against the same
words/*.yml + site-rules/*.yml data generate.py uses, so "why did this get
hidden" (or "why didn't this get hidden") is answerable without digging through
uBlock's logger.

Usage:
  uv run python scripts/check_post.py --url "https://www.reddit.com/r/politics/comments/abc123/some_title/"
  uv run python scripts/check_post.py --title "..." --flair "Politics" --subreddit changemyview
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate import (  # noqa: E402
    WORDS_DIR, load_yaml, load_site_rules, normalize_terms, fragment,
)


def fetch_post(url: str) -> dict[str, str]:
    json_url = url.split("?")[0].rstrip("/") + ".json"
    req = urllib.request.Request(json_url, headers={"User-Agent": "ublock-politics-checker/1.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.load(resp)
    post = data[0]["data"]["children"][0]["data"]
    return {
        "title": post.get("title") or "",
        "selftext": post.get("selftext") or "",
        "flair": post.get("link_flair_text") or "",
        "subreddit": post.get("subreddit") or "",
        "domain": post.get("domain") or "",
    }


def word_matches(fields: dict[str, str]) -> list[str]:
    hits = []
    for region_path in sorted(WORDS_DIR.glob("*.yml")):
        data = load_yaml(region_path)
        region = data["meta"]["region"]
        for cat in data["categories"]:
            for term in normalize_terms(cat):
                flags = 0 if term["cs"] else re.IGNORECASE
                try:
                    pattern = re.compile(rf"\b(?:{fragment(term)})\b", flags)
                except re.error:
                    continue
                for field, text in fields.items():
                    if text and pattern.search(text):
                        hits.append(
                            f"{region}/{cat['id']} tier {term['tier']}: "
                            f"{term['value']!r} matched in [{field}] {text!r}")
    return hits


def site_rule_matches(fields: dict[str, str]) -> list[str]:
    hits = []
    for source_id, rules in load_site_rules().items():
        for rule in rules:
            filt = rule["filter"]
            sub_match = re.search(r'/r/([^/"]+)/', filt)
            if sub_match and fields.get("subreddit", "").lower() == sub_match.group(1).lower():
                hits.append(f"{source_id} tier {rule['tier']}: subreddit rule matches r/{fields['subreddit']}")
                continue
            text_match = re.search(r"has-text\(/(.+)/([a-z]*)\)", filt)
            if text_match:
                pattern = re.compile(text_match.group(1), re.IGNORECASE if "i" in text_match.group(2) else 0)
                for field, text in fields.items():
                    if text and pattern.search(text):
                        hits.append(f"{source_id} tier {rule['tier']}: site text rule matched in [{field}] {text!r}")
    return hits


def main() -> int:
    parser = argparse.ArgumentParser(description="Check if a Reddit post would be hidden.")
    parser.add_argument("--url", help="Reddit post URL (fetches title/selftext/flair/subreddit)")
    parser.add_argument("--title", default="")
    parser.add_argument("--selftext", default="")
    parser.add_argument("--flair", default="")
    parser.add_argument("--subreddit", default="")
    parser.add_argument("--domain", default="")
    args = parser.parse_args()

    if args.url:
        try:
            fields = fetch_post(args.url)
        except Exception as exc:
            print(f"Could not fetch {args.url!r}: {exc}")
            print("Pass fields manually instead: --title/--selftext/--flair/--subreddit/--domain")
            return 1
    else:
        fields = {"title": args.title, "selftext": args.selftext, "flair": args.flair,
                  "subreddit": args.subreddit, "domain": args.domain}

    if not any(fields.values()):
        parser.error("provide --url, or at least one of --title/--selftext/--flair/--subreddit/--domain")

    print("Fields checked:")
    for key, value in fields.items():
        if value:
            print(f"  {key}: {value!r}")
    print()

    hits = word_matches(fields) + site_rule_matches(fields)
    if not hits:
        print("No match — this post would NOT be hidden by any current filter.")
        return 0

    print(f"{len(hits)} match(es) — this post WOULD be hidden:")
    for hit in hits:
        print(f"  - {hit}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
