#!/usr/bin/env python3
"""Validate the structure and basic integrity of a novel Markdown package."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Iterable

REQUIRED_FILES = [
    "00_README_使用指南.md",
    "00_项目宪法.md",
    "01_总索引与状态看板.md",
    "02_市场扫描.md",
    "03_竞品拆解.md",
    "04_创意差异化.md",
    "05_核心卖点与读者承诺.md",
    "06_世界观与规则.md",
    "07_资源经济与成长体系.md",
    "08_角色总谱.md",
    "09_角色关系图谱.md",
    "10_欲望稀缺冲突矩阵.md",
    "11_势力制度与社会运行.md",
    "12_全书总纲.md",
    "13_分卷大纲.md",
    "14_章节细纲.md",
    "15_开篇与留存设计.md",
    "16_爽点情绪与节奏.md",
    "17_伏笔谜题身份遗产.md",
    "18_主题母题与意象系统.md",
    "19_文风声纹手册.md",
    "20_书名简介与商业包装.md",
    "21_事实一致性台账.md",
    "22_审计报告.md",
    "23_变更日志与决策记录.md",
    "24_最终交付清单.md",
    "90_灵感火种库.md",
    "91_废案库.md",
    "92_待决策清单.md",
]

FM_REQUIRED = {"doc_id", "title", "status", "version", "updated"}
LOCAL_MD_LINK = re.compile(r"\[[^\]]+\]\((?!https?://|mailto:|#)([^)]+\.md)(?:#[^)]+)?\)")
DOC_ID_LINE = re.compile(r"^doc_id:\s*(\S+)\s*$", re.MULTILINE)
TODO_PATTERNS = ("<待填写>", "TODO[", "TBD", "<YYYY-MM-DD>")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a novel planning package")
    parser.add_argument("path", type=Path, help="Project directory")
    parser.add_argument("--final", action="store_true", help="Treat placeholders as errors")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    parser.add_argument("--json", action="store_true", dest="as_json", help="Emit JSON report")
    return parser.parse_args()


def extract_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    block = text[4:end]
    meta: dict[str, str] = {}
    for line in block.splitlines():
        if not line or line.startswith(" ") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip()
    return meta, text[end + 5 :]


def fence_balanced(text: str) -> bool:
    count = sum(1 for line in text.splitlines() if line.lstrip().startswith("```"))
    return count % 2 == 0


def iter_md(root: Path) -> Iterable[Path]:
    return sorted(p for p in root.rglob("*.md") if p.is_file())


def main() -> int:
    args = parse_args()
    root = args.path.expanduser().resolve()
    errors: list[str] = []
    warnings: list[str] = []
    stats = {"markdown_files": 0, "bytes": 0, "placeholders": 0}

    if not root.is_dir():
        errors.append(f"Not a directory: {root}")
    else:
        for name in REQUIRED_FILES:
            if not (root / name).is_file():
                errors.append(f"Missing required file: {name}")

    doc_ids: dict[str, str] = {}
    for path in iter_md(root) if root.is_dir() else []:
        stats["markdown_files"] += 1
        rel = path.relative_to(root).as_posix()
        try:
            raw = path.read_bytes()
            text = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            errors.append(f"{rel}: not valid UTF-8 ({exc})")
            continue
        stats["bytes"] += len(raw)
        if len(text.strip()) < 40:
            errors.append(f"{rel}: file is effectively empty")
        if "\r\n" in text:
            warnings.append(f"{rel}: CRLF line endings; LF is recommended")
        if not fence_balanced(text):
            errors.append(f"{rel}: unclosed Markdown code fence")

        meta, body = extract_frontmatter(text)
        if rel != "00_README_使用指南.md":
            if not meta:
                errors.append(f"{rel}: missing YAML frontmatter")
            else:
                missing = sorted(FM_REQUIRED - set(meta))
                if missing:
                    errors.append(f"{rel}: frontmatter missing {', '.join(missing)}")
                doc_id = meta.get("doc_id")
                if doc_id:
                    if doc_id in doc_ids:
                        errors.append(f"{rel}: duplicate doc_id {doc_id}; first in {doc_ids[doc_id]}")
                    else:
                        doc_ids[doc_id] = rel

        h1 = [line for line in body.splitlines() if re.match(r"^#\s+\S", line)]
        if len(h1) != 1:
            errors.append(f"{rel}: expected exactly one H1, found {len(h1)}")

        for target in LOCAL_MD_LINK.findall(text):
            target_path = (path.parent / target).resolve()
            try:
                target_path.relative_to(root)
            except ValueError:
                warnings.append(f"{rel}: link escapes project root: {target}")
                continue
            if not target_path.is_file():
                errors.append(f"{rel}: broken local Markdown link: {target}")

        placeholders = sum(text.count(pattern) for pattern in TODO_PATTERNS)
        stats["placeholders"] += placeholders
        if placeholders:
            msg = f"{rel}: contains {placeholders} placeholder marker(s)"
            if args.final:
                errors.append(msg)
            else:
                warnings.append(msg)

    # Basic package-level checks.
    if stats["markdown_files"] and stats["markdown_files"] < len(REQUIRED_FILES):
        errors.append(
            f"Only {stats['markdown_files']} Markdown files found; expected at least {len(REQUIRED_FILES)}"
        )

    constitution = root / "00_项目宪法.md"
    if constitution.is_file():
        text = constitution.read_text(encoding="utf-8")
        for token in ("HC-", "SP-", "是否允许写正文", "完成定义"):
            if token not in text:
                warnings.append(f"00_项目宪法.md: expected token missing: {token}")

    report = {
        "path": str(root),
        "ok": not errors and not (args.strict and warnings),
        "errors": errors,
        "warnings": warnings,
        "stats": stats,
    }
    if args.as_json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"Novel package: {root}")
        print(f"Markdown files: {stats['markdown_files']} | Bytes: {stats['bytes']} | Placeholders: {stats['placeholders']}")
        if errors:
            print("\nERRORS:")
            for item in errors:
                print(f"- {item}")
        if warnings:
            print("\nWARNINGS:")
            for item in warnings:
                print(f"- {item}")
        if not errors and not (args.strict and warnings):
            print("\nPASS: package structure and basic Markdown integrity are valid.")

    if errors or (args.strict and warnings):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
