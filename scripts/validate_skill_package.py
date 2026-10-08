#!/usr/bin/env python3
"""Validate this Skill package: manifest, links, headings and basic encoding."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

LOCAL_LINK = re.compile(r"\[[^\]]+\]\((?!https?://|mailto:|#)([^)#]+)(?:#[^)]+)?\)")


def without_fenced_code(text: str) -> str:
    """Remove fenced code before link checks; examples may contain project-relative links."""
    kept: list[str] = []
    in_fence = False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            kept.append(line)
    return "\n".join(kept)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("path", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    return p.parse_args()


def main() -> int:
    root = parse_args().path.resolve()
    manifest = root / "manifest.txt"
    errors: list[str] = []
    warnings: list[str] = []

    if not manifest.is_file():
        errors.append("manifest.txt missing")
        listed: set[str] = set()
    else:
        lines = manifest.read_text(encoding="utf-8").splitlines()
        listed = {line.strip() for line in lines if line.strip()}
        if len(listed) != len([line for line in lines if line.strip()]):
            errors.append("manifest.txt contains duplicate entries")

    actual = {
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file() and path.name != "manifest.txt" and "__pycache__" not in path.parts
    }
    missing = sorted(listed - actual)
    unlisted = sorted(actual - listed)
    for item in missing:
        errors.append(f"Manifest entry missing on disk: {item}")
    for item in unlisted:
        errors.append(f"File missing from manifest: {item}")

    for path in sorted(root.rglob("*.md")):
        rel = path.relative_to(root).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            errors.append(f"{rel}: invalid UTF-8")
            continue
        if len(text.strip()) < 40:
            errors.append(f"{rel}: effectively empty")
        if sum(1 for line in text.splitlines() if line.lstrip().startswith("```")) % 2:
            errors.append(f"{rel}: unclosed code fence")
        for target in LOCAL_LINK.findall(without_fenced_code(text)):
            candidate = (path.parent / target).resolve()
            if not candidate.exists():
                # Template fragments are copied into a generated project, where their
                # project-relative links become valid. The generated project validator
                # checks those links after initialization.
                if "templates" in path.relative_to(root).parts and not target.startswith(("../", "./")):
                    continue
                errors.append(f"{rel}: broken local link {target}")
        if path.name == "SKILL.md" and not text.startswith("---\n"):
            errors.append("SKILL.md: missing frontmatter")

    if not (root / "SKILL.md").is_file():
        errors.append("SKILL.md missing")
    if not (root / "AGENTS.md").is_file():
        errors.append("AGENTS.md missing")
    if not (root / "STATE_CONTRACT.md").is_file():
        errors.append("STATE_CONTRACT.md missing")

    print(f"Skill package: {root}")
    print(f"Manifest entries: {len(listed)} | Actual files: {len(actual)}")
    if errors:
        print("\nERRORS:")
        for item in errors:
            print(f"- {item}")
    if warnings:
        print("\nWARNINGS:")
        for item in warnings:
            print(f"- {item}")
    if not errors:
        print("\nPASS: Skill package manifest and Markdown integrity are valid.")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
