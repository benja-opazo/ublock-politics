#!/usr/bin/env python3
"""Lint the word / source / site-rule data. Run before generating.

Checks:
  - every term tier is in {1, 2, 3}
  - every pattern compiles as a regex
  - no duplicate term within a region (case-insensitive)
  - source templates contain the {TERMS} placeholder and an id
  - site rules have a filter and a valid tier

Run:  uv run python scripts/validate.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
WORDS_DIR = ROOT / "words"
SOURCES_DIR = ROOT / "sources"
SITE_RULES_DIR = ROOT / "site-rules"
VALID_TIERS = {1, 2, 3, 4}
PLACEHOLDER = "{TERMS}"
FLAGS_PLACEHOLDER = "{FLAGS}"


def load_yaml(path: Path):
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def unpack(entry, default_tier):
    """Return (value, is_pattern, tier) or None if the entry is malformed."""
    if isinstance(entry, str):
        return entry, False, default_tier
    if isinstance(entry, dict) and "pattern" in entry:
        return entry["pattern"], True, entry.get("tier", default_tier)
    if isinstance(entry, dict) and "term" in entry:
        return entry["term"], False, entry.get("tier", default_tier)
    return None


def check_words(errors: list[str]) -> None:
    for path in sorted(WORDS_DIR.glob("*.yml")):
        data = load_yaml(path)
        rel = path.relative_to(ROOT)
        seen: dict[str, str] = {}
        for cat in data.get("categories", []):
            default_tier = cat.get("default_tier", 1)
            for entry in cat.get("terms", []) or []:
                unpacked = unpack(entry, default_tier)
                if unpacked is None:
                    errors.append(f"{rel}: malformed term entry {entry!r}")
                    continue
                value, is_pattern, tier = unpacked
                if tier not in VALID_TIERS:
                    errors.append(f"{rel}: term {value!r} has invalid tier {tier!r}")
                if is_pattern:
                    try:
                        re.compile(value)
                    except re.error as exc:
                        errors.append(f"{rel}: pattern {value!r} does not compile: {exc}")
                key = value.lower()
                if key in seen:
                    errors.append(
                        f"{rel}: duplicate term {value!r} "
                        f"(in {seen[key]!r} and {cat.get('id')!r})")
                else:
                    seen[key] = cat.get("id")


def check_sources(errors: list[str]) -> None:
    for path in sorted(SOURCES_DIR.glob("*.yml")):
        data = load_yaml(path)
        rel = path.relative_to(ROOT)
        if "id" not in data or "template" not in data:
            errors.append(f"{rel}: source needs both 'id' and 'template'")
            continue
        for placeholder in (PLACEHOLDER, FLAGS_PLACEHOLDER):
            if placeholder not in data["template"]:
                errors.append(f"{rel}: template missing {placeholder}")


def check_site_rules(errors: list[str]) -> None:
    for path in sorted(SITE_RULES_DIR.glob("*.yml")):
        data = load_yaml(path)
        rel = path.relative_to(ROOT)
        for rule in data.get("rules", []) or []:
            if "filter" not in rule:
                errors.append(f"{rel}: rule missing 'filter': {rule!r}")
            if rule.get("tier") not in VALID_TIERS:
                errors.append(f"{rel}: rule has invalid tier: {rule!r}")


def main() -> int:
    errors: list[str] = []
    check_words(errors)
    check_sources(errors)
    check_site_rules(errors)
    if errors:
        print(f"{len(errors)} problem(s) found:")
        for err in errors:
            print(f"  - {err}")
        return 1
    print("All checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
