#!/usr/bin/env python3
"""Validate and package a novel Markdown project into a reproducible ZIP."""

from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
import zipfile
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = SKILL_ROOT / "scripts" / "validate_novel_package.py"
EXCLUDED_DIRS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache"}
EXCLUDED_SUFFIXES = {".tmp", ".bak", ".swp", ".pyc"}
EXCLUDED_NAMES = {".DS_Store", "Thumbs.db"}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Validate and ZIP a novel project")
    p.add_argument("project", type=Path, help="Novel project directory")
    p.add_argument("--output", type=Path, help="ZIP path; default: sibling <project>_v<version>.zip")
    p.add_argument("--final", action="store_true", help="Reject unresolved placeholders")
    p.add_argument("--strict", action="store_true", help="Treat validator warnings as errors")
    return p.parse_args()


def allowed(path: Path, root: Path) -> bool:
    rel = path.relative_to(root)
    if any(part in EXCLUDED_DIRS for part in rel.parts):
        return False
    if path.name in EXCLUDED_NAMES or path.suffix in EXCLUDED_SUFFIXES:
        return False
    return path.is_file()


def skill_version(project: Path) -> str:
    marker = project / ".novel-skill-version"
    if marker.is_file():
        value = marker.read_text(encoding="utf-8").strip()
        if value:
            return value
    return "unversioned"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    args = parse_args()
    project = args.project.expanduser().resolve()
    if not project.is_dir():
        print(f"ERROR: project directory not found: {project}", file=sys.stderr)
        return 2

    cmd = [sys.executable, str(VALIDATOR), str(project)]
    if args.final:
        cmd.append("--final")
    if args.strict:
        cmd.append("--strict")
    result = subprocess.run(cmd, check=False)
    if result.returncode != 0:
        print("ERROR: validation failed; ZIP was not created.", file=sys.stderr)
        return result.returncode

    version = skill_version(project)
    output = args.output.expanduser().resolve() if args.output else project.parent / f"{project.name}_v{version}.zip"
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.unlink()

    files = sorted(path for path in project.rglob("*") if allowed(path, project))
    if not files:
        print("ERROR: no packageable files found", file=sys.stderr)
        return 2

    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path in files:
            arcname = Path(project.name) / path.relative_to(project)
            zf.write(path, arcname.as_posix())

    with zipfile.ZipFile(output, "r") as zf:
        bad = zf.testzip()
        if bad:
            output.unlink(missing_ok=True)
            print(f"ERROR: ZIP integrity test failed at {bad}", file=sys.stderr)
            return 2

    print(f"Created: {output}")
    print(f"Files: {len(files)}")
    print(f"SHA-256: {sha256(output)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
