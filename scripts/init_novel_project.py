#!/usr/bin/env python3
"""Initialize a Markdown novel-planning project from this Skill's templates.

Uses only the Python standard library. It never overwrites a non-empty project
unless --force is explicitly supplied.
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from datetime import date
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = SKILL_ROOT / "templates"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a novel planning Markdown project")
    parser.add_argument("--name", required=True, help="Project/folder name")
    parser.add_argument("--platform", default="<待填写>", help="Target platform or publishing direction")
    parser.add_argument("--target-words", type=int, default=0, help="Target word count")
    parser.add_argument("--output", type=Path, default=Path.cwd(), help="Parent output directory")
    parser.add_argument("--force", action="store_true", help="Replace an existing project directory")
    return parser.parse_args()


def safe_name(name: str) -> str:
    cleaned = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", name).strip().rstrip(".")
    if not cleaned:
        raise ValueError("Project name becomes empty after filename sanitization")
    return cleaned


def read_template(filename: str) -> str:
    path = TEMPLATES / filename
    if not path.exists():
        raise FileNotFoundError(f"Template missing: {path}")
    return path.read_text(encoding="utf-8")


def strip_frontmatter(text: str) -> str:
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end != -1:
            return text[end + 5 :].lstrip("\n")
    return text


def demote_headings(text: str, levels: int = 1) -> str:
    result: list[str] = []
    in_fence = False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            result.append(line)
            continue
        if not in_fence:
            m = re.match(r"^(#{1,6})\s+(.*)$", line)
            if m:
                hashes = "#" * min(6, len(m.group(1)) + levels)
                line = f"{hashes} {m.group(2)}"
        result.append(line)
    return "\n".join(result).rstrip() + "\n"


def frontmatter(doc_id: str, title: str, updated: str, depends: list[str] | None = None) -> str:
    depends = depends or ["DOC-00"]
    deps = "[]" if not depends else "\n" + "\n".join(f"  - {item}" for item in depends)
    return (
        "---\n"
        f"doc_id: {doc_id}\n"
        f"title: {title}\n"
        "status: candidate\n"
        "version: 0.1.0\n"
        f"updated: {updated}\n"
        f"depends_on: {deps}\n"
        "canonical_scope: 尚未冻结\n"
        "---\n\n"
    )


def single_doc(doc_id: str, title: str, template: str, updated: str, depends: list[str] | None = None) -> str:
    body = strip_frontmatter(read_template(template))
    # Normalize the first H1 to the generated title.
    lines = body.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("# "):
            lines[i] = f"# {title}"
            break
    return frontmatter(doc_id, title, updated, depends) + "\n".join(lines).rstrip() + "\n"


def combined_doc(
    doc_id: str,
    title: str,
    templates: list[tuple[str, str]],
    updated: str,
    depends: list[str] | None = None,
) -> str:
    parts = [frontmatter(doc_id, title, updated, depends), f"# {title}\n"]
    for section_title, template in templates:
        body = demote_headings(strip_frontmatter(read_template(template)), 2)
        parts.append(f"\n## {section_title}\n\n{body}")
    return "".join(parts).rstrip() + "\n"


def project_readme(name: str, platform: str, target_words: int, updated: str) -> str:
    words = f"{target_words:,}" if target_words else "<待填写>"
    return f"""# {name}｜小说大纲与设定库

- 创建日期：{updated}
- 目标平台/方向：{platform}
- 目标字数：{words}
- 资料状态：candidate
- Skill 版本：1.0.0

## 使用顺序

1. 先完成并冻结 `00_项目宪法.md`。
2. 在 `01_总索引与状态看板.md` 维护进度、版本与审计状态。
3. 按 02—11 完成市场、原创、世界、角色、关系与冲突。
4. 按 12—20 完成总纲、细纲、开篇、回报、伏笔、主题、声纹和包装。
5. 使用 21—23 维护一致性、审计和决策。
6. 使用 24 完成最终交付验收；灵感、废案和待决策分别进入 90—92。
7. 交付前运行：

```bash
python /path/to/skill/scripts/validate_novel_package.py "{name}"
```

## 状态说明

- `canonical`：已审计并生效。
- `candidate`：候选，不得作为下游事实。
- `deprecated`：已废弃，保留追溯。
- `unknown`：缺证据或未决定。
- `frozen`：用户锁定。

## 当前入口

- [项目宪法](00_项目宪法.md)
- [总索引与状态看板](01_总索引与状态看板.md)
- [最终交付清单](24_最终交付清单.md)
"""


def core_promise_doc(updated: str) -> str:
    return frontmatter("DOC-05", "05｜核心卖点与读者承诺", updated, ["DOC-00", "DOC-02", "DOC-04"]) + """# 05｜核心卖点与读者承诺

## 一句话承诺

> <主角 + 异常处境/优势 + 核心行动 + 主要代价>

## 三层卖点

| 层 | 内容 | 兑现窗口 |
|---|---|---|
| 公共卖点（10 秒可懂） |  |  |
| 中层卖点（支撑第一卷） |  |  |
| 深层卖点（支撑终局） |  |  |

## 读者购买的体验

- 主体验：
- 次体验：
- 明确不提供：

## 核心矛盾

- 外部矛盾：
- 关系矛盾：
- 制度矛盾：
- 内心矛盾：

## 终局问题

- 必须回答：
- 初始错误答案：
- 最终可能答案：
- 不可逆代价：

## 独特场景承诺

1. <只有本项目机制才能产生的场景>
2. <只有本项目关系才能产生的选择>
3. <只有本项目世界规则才能产生的后果>

## 承诺一致性

| 载体 | 表达 | 是否一致 | 待修 |
|---|---|---|---|
| 书名 |  |  |  |
| 简介 |  |  |  |
| 第一章 |  |  |  |
| 第一卷 |  |  |  |
| 终局 |  |  |  |
"""


def split_inspiration_docs(updated: str) -> tuple[str, str, str]:
    spark = frontmatter("DOC-90", "90｜灵感火种库", updated) + """# 90｜灵感火种库

| SPARK-ID | 点子 | 魅力来源 | 当前不采用原因 | 可用场景 | 依赖条件 | 风险 |
|---|---|---|---|---|---|---|
| SPARK-001 |  |  |  |  |  |  |

> 本文件内容均为 candidate，除非重新决策，不得被下游当作事实。
"""
    dead = frontmatter("DOC-91", "91｜废案库", updated) + """# 91｜废案库

| DEAD-ID | 原方案 | 废弃原因 | 冲突约束/审计 | 可复用部分 | 替代方案 |
|---|---|---|---|---|---|
| DEAD-001 |  |  |  |  |  |

> 废案不得静默复活；复用时建立新决策和新实体 ID。
"""
    pending = frontmatter("DOC-92", "92｜待决策清单", updated) + """# 92｜待决策清单

| DEC-ID | 问题 | 为什么必须决定 | 候选 | 推荐 | 影响文件 | 截止阶段 | 状态 |
|---|---|---|---|---|---|---|---|
| DEC-001 |  |  | A/B/C |  |  |  | open |

## 决策原则

- 用户冻结硬约束优先。
- 无法自动仲裁时给收益、代价和影响，不静默选择。
- 已决定项迁入 `23_变更日志与决策记录.md`。
"""
    return spark, dead, pending


def customize_constitution(text: str, name: str, platform: str, target_words: int, updated: str) -> str:
    text = text.replace("<YYYY-MM-DD>", updated)
    text = text.replace("| 项目名 | <待填写> |", f"| 项目名 | {name} |")
    text = text.replace("| 目标平台/出版方向 | <待填写> |", f"| 目标平台/出版方向 | {platform} |")
    if target_words:
        text = text.replace("| 目标字数 | <待填写> |", f"| 目标字数 | {target_words:,} |")
    return text


def write_file(root: Path, filename: str, content: str) -> None:
    path = root / filename
    path.write_text(content.rstrip() + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    args = parse_args()
    try:
        project_name = safe_name(args.name)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    root = args.output.expanduser().resolve() / project_name
    if root.exists():
        if not args.force:
            print(f"ERROR: {root} already exists. Use --force to replace it.", file=sys.stderr)
            return 2
        shutil.rmtree(root)
    root.mkdir(parents=True, exist_ok=False)

    updated = date.today().isoformat()
    files: dict[str, str] = {}
    files["00_README_使用指南.md"] = project_readme(project_name, args.platform, args.target_words, updated)
    files["00_项目宪法.md"] = customize_constitution(
        single_doc("DOC-00", "00｜项目宪法", "00_项目宪法模板.md", updated, []),
        project_name,
        args.platform,
        args.target_words,
        updated,
    )
    files["01_总索引与状态看板.md"] = single_doc("DOC-01", "01｜总索引与状态看板", "01_总索引与状态看板.md", updated)
    files["02_市场扫描.md"] = single_doc("DOC-02", "02｜市场扫描", "02_市场扫榜样本表.md", updated)
    files["03_竞品拆解.md"] = single_doc("DOC-03", "03｜竞品拆解", "03_单书拆解卡.md", updated, ["DOC-02"])
    files["04_创意差异化.md"] = single_doc("DOC-04", "04｜创意差异化", "04_创意差异化矩阵.md", updated, ["DOC-03"])
    files["05_核心卖点与读者承诺.md"] = core_promise_doc(updated)
    files["06_世界观与规则.md"] = single_doc("DOC-06", "06｜世界观与规则", "05_世界层级与规则卡.md", updated, ["DOC-04", "DOC-05"])
    files["07_资源经济与成长体系.md"] = combined_doc(
        "DOC-07",
        "07｜资源经济与成长体系",
        [
            ("资源经济与稀缺", "06_资源经济与稀缺表.md"),
            ("力量境界与极境", "07_力量境界与极境卡.md"),
            ("非对称优势与约束", "08_金手指能力与约束卡.md"),
        ],
        updated,
        ["DOC-06"],
    )
    files["08_角色总谱.md"] = single_doc("DOC-08", "08｜角色总谱", "09_角色小传模板.md", updated, ["DOC-05", "DOC-06", "DOC-07"])
    files["09_角色关系图谱.md"] = single_doc("DOC-09", "09｜角色关系图谱", "10_关系边与关系回路模板.md", updated, ["DOC-08"])
    files["10_欲望稀缺冲突矩阵.md"] = single_doc("DOC-10", "10｜欲望稀缺冲突矩阵", "11_欲望稀缺冲突矩阵.md", updated, ["DOC-06", "DOC-08", "DOC-09"])
    files["11_势力制度与社会运行.md"] = single_doc("DOC-11", "11｜势力制度与社会运行", "12_势力制度卡.md", updated, ["DOC-06", "DOC-10"])
    files["12_全书总纲.md"] = single_doc("DOC-12", "12｜全书总纲", "13_全书总纲模板.md", updated, ["DOC-05", "DOC-10", "DOC-11"])
    files["13_分卷大纲.md"] = single_doc("DOC-13", "13｜分卷大纲", "14_分卷大纲模板.md", updated, ["DOC-12"])
    files["14_章节细纲.md"] = combined_doc(
        "DOC-14",
        "14｜章节细纲",
        [("章节模板", "15_章节细纲模板.md"), ("场景卡", "16_场景卡模板.md")],
        updated,
        ["DOC-13"],
    )
    files["15_开篇与留存设计.md"] = single_doc("DOC-15", "15｜开篇与留存设计", "17_开篇三十章设计表.md", updated, ["DOC-05", "DOC-14"])
    files["16_爽点情绪与节奏.md"] = single_doc("DOC-16", "16｜爽点情绪与节奏", "18_爽点情绪回报台账.md", updated, ["DOC-13", "DOC-14"])
    files["17_伏笔谜题身份遗产.md"] = combined_doc(
        "DOC-17",
        "17｜伏笔谜题身份遗产",
        [("伏笔回收", "19_伏笔回收台账.md"), ("身份、秘密与遗产", "20_身份秘密与遗产台账.md")],
        updated,
        ["DOC-12", "DOC-13"],
    )
    files["18_主题母题与意象系统.md"] = single_doc("DOC-18", "18｜主题母题与意象系统", "28_主题母题与意象台账.md", updated, ["DOC-05", "DOC-08", "DOC-12"])
    files["19_文风声纹手册.md"] = single_doc("DOC-19", "19｜文风声纹手册", "21_文风声纹手册模板.md", updated, ["DOC-05", "DOC-08", "DOC-18"])
    files["20_书名简介与商业包装.md"] = single_doc("DOC-20", "20｜书名简介与商业包装", "22_标题简介候选评分表.md", updated, ["DOC-02", "DOC-05", "DOC-15"])
    files["21_事实一致性台账.md"] = single_doc("DOC-21", "21｜事实一致性台账", "24_一致性事实台账.md", updated, ["DOC-06", "DOC-08", "DOC-12"])
    files["22_审计报告.md"] = single_doc("DOC-22", "22｜审计报告", "23_审计报告模板.md", updated, ["DOC-00"])
    files["23_变更日志与决策记录.md"] = single_doc("DOC-23", "23｜变更日志与决策记录", "25_变更日志与决策记录.md", updated, ["DOC-00"])
    files["24_最终交付清单.md"] = single_doc("DOC-24", "24｜最终交付清单", "27_交付清单.md", updated, ["DOC-00", "DOC-22"])
    spark, dead, pending = split_inspiration_docs(updated)
    files["90_灵感火种库.md"] = spark
    files["91_废案库.md"] = dead
    files["92_待决策清单.md"] = pending

    for filename, content in files.items():
        write_file(root, filename, content)

    (root / ".novel-skill-version").write_text("1.0.0\n", encoding="utf-8")
    print(f"Created {len(files)} Markdown files in: {root}")
    print(f"Validate with: python {SKILL_ROOT / 'scripts' / 'validate_novel_package.py'} {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
