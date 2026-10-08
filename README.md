# StoryForge

**A systematic framework for novel outlining and worldbuilding**

StoryForge transforms scattered ideas into executable, auditable, version-controlled novel outlines. Designed for web novels, genre fiction, and series writing, it addresses six common challenges:

1. **Settings without story** - Worldbuilding that doesn't generate natural plot progression
2. **Flat supporting cast** - Secondary characters lack relationships; the world feels like a stage backdrop
3. **Derivative plots** - Analysis becomes reskinning instead of original creation
4. **Rigid writing** - Overloading checks into the creative process kills spontaneity
5. **Revision chaos** - Multiple iterations without versioning or evidence trails
6. **Incomplete deliverables** - Seemingly thorough documentation with gaps, broken links, and contradictions

## What's Inside

- **[SKILL.md](SKILL.md)** - Main workflow and execution pipeline
- **[AGENTS.md](AGENTS.md)** - Multi-agent roles, permissions, and handoff protocols
- **[STATE_CONTRACT.md](STATE_CONTRACT.md)** - Canonical/candidate/deprecated state management
- **[docs/](docs/)** - Complete methodology from market research, competitive analysis, originality checks, to premium-grade audits
- **[templates/](templates/)** - 31 ready-to-use Markdown templates
- **[prompts/](prompts/)** - Coordinator, market research, character relationships, plot architecture, commercial editor, and reader feedback analysis prompts
- **[scripts/](scripts/)** - Project initialization, validation, and compression scripts (Python stdlib only)
- **[examples/](examples/)** - Abstract examples avoiding specific genre binding
- **[audits/](audits/)** - Four rounds of self-audit and revision records

## Core Philosophy

### Conflict Engines, Not Setting Dumps

StoryForge's central formula:

> Environment → Scarcity → Desire → Relationship/Institutional Leverage → Conflict → Choice → Cost → State Change → New Environment

Every setting element must answer: Who wants it? Why is it scarce? Who controls it? Who opposes? What's the cost? What changes?

### Character Relationships First, Then Plot

Instead of assembling hundreds of events and forcing characters into them, define long-term goals, debts, secrets, boundaries, power imbalances, and information asymmetries. Let events emerge as necessary consequences of these relationships under pressure.

### Multi-Resolution Planning

For million-word epics:
- **Whole book**: Plotted to arc level
- **Current volume**: Plotted to chapter level  
- **Next 30-50 chapters**: Plotted to scene level
- **Re-plan** as character growth makes distant details obsolete

### Separate Creation from Audit

**Front-stage**: Writers receive only essential constraints to preserve spontaneity and "spark"  
**Back-stage**: Strict audits fix logic, commercial viability, and consistency afterward

## Quick Start

### Method 1: As an Agent Skill

Place the entire directory in your environment's Skills folder, enabling agents to read [SKILL.md](SKILL.md).

### Method 2: As a Project Template

Place this directory in your project repository. In your root task, have the coordinator read:

1. [SKILL.md](SKILL.md)
2. [AGENTS.md](AGENTS.md)
3. [STATE_CONTRACT.md](STATE_CONTRACT.md)
4. Your project's `00_项目宪法.md` (Project Constitution)

Then invoke specialized agents by stage. All outputs go to a separate novel project directory, not modifying the Skill itself.

### Method 3: Generate a Blank Project

```bash
python scripts/init_novel_project.py \
  --name "ProjectName" \
  --platform "TargetPlatform" \
  --target-words 3000000 \
  --output /path/to/workspace
```

Validate and package:

```bash
python scripts/validate_novel_package.py /path/to/workspace/ProjectName
python scripts/package_novel_project.py /path/to/workspace/ProjectName
```

For final freeze, add `--final --strict` flags.

## File States

- **canonical** - Audited and currently valid
- **candidate** - Proposed solution, not yet fact
- **deprecated** - Obsolete but retained for tracing
- **unknown** - No evidence yet; do not fabricate

## Standard Workflow

1. **Project Constitution** - Lock constraints before creating
2. **Market Research** - Real-time ranking analysis and positioning
3. **Competitive Analysis** - Extract transferable mechanisms, not surface elements
4. **Originality Check** - Establish independent differentiation axes
5. **World Rules** - Build settings that affect choices and conflicts
6. **Character Network** - Define goals, relationships, and conflict engines
7. **Structure & Outline** - Five-layer planning from book to scene
8. **Opening & Retention** - Align title, synopsis, and first chapters
9. **Foreshadowing & Mystery** - Ledger all long-term assets
10. **Style & Theme** - Define parameters, not single-author imitation
11. **Independent Audit** - Minimum three rounds with different perspectives

## Quality Gates

### Every Major Character

- One-sentence core conflict
- Independent life plan not dependent on protagonist
- At least one choice that hurts self-interest but aligns with values
- Relationship changes, not just identity labels

### Every Volume

- Opening and ending states differ measurably
- At least one value choice, not just power-level resolution
- Reversals caused by existing information and character choices

### Every Chapter

Must change at least two of: Resources, Information, Relationships, Power/Position, Identity, Internal Beliefs

## Compatibility

- All outputs default to UTF-8 Markdown
- Standard relative links work with Git, Obsidian, VS Code, and plain folders
- Optional Mermaid diagrams; edge tables remain readable without Mermaid support
- Scripts require only Python standard library

## Boundaries

This Skill significantly improves systematic preparation and executability, but cannot guarantee publishing contracts, bestseller status, or specific commercial outcomes. Market judgments must note time and sample size. Creative evaluations must retain uncertainty.

---

## Project Structure

```text
ProjectName/
├── 00_README_使用指南.md
├── 00_项目宪法.md (Project Constitution)
├── 01_总索引与状态看板.md (Master Index & Status Board)
├── 02_市场扫描.md (Market Research)
├── 03_竞品拆解.md (Competitive Analysis)
├── 04_创意差异化.md (Creative Differentiation)
├── 05_核心卖点与读者承诺.md (Core Hook & Reader Promise)
├── 06_世界观与规则.md (Worldview & Rules)
├── 07_资源经济与成长体系.md (Resource Economy & Progression)
├── 08_角色总谱.md (Character Roster)
├── 09_角色关系图谱.md (Relationship Network)
├── 10_欲望稀缺冲突矩阵.md (Desire-Scarcity-Conflict Matrix)
├── 11_势力制度与社会运行.md (Factions & Social Systems)
├── 12_全书总纲.md (Master Outline)
├── 13_分卷大纲.md (Volume Outlines)
├── 14_章节细纲.md (Chapter Outlines)
├── 15_开篇与留存设计.md (Opening & Retention)
├── 16_爽点情绪与节奏.md (Emotional Beats & Pacing)
├── 17_伏笔谜题身份遗产.md (Foreshadowing & Mysteries)
├── 18_主题母题与意象系统.md (Theme & Motifs)
├── 19_文风声纹手册.md (Style Guide)
├── 20_书名简介与商业包装.md (Title & Synopsis)
├── 21_事实一致性台账.md (Consistency Ledger)
├── 22_审计报告.md (Audit Reports)
├── 23_变更日志与决策记录.md (Changelog & Decisions)
├── 24_最终交付清单.md (Final Deliverables)
├── 90_灵感火种库.md (Idea Sparks Archive)
├── 91_废案库.md (Rejected Concepts)
└── 92_待决策清单.md (Pending Decisions)
```

## Minimum Invocation Format

```text
Use novel-outline-worldbuilding Skill.
Project: <working title>
Target Platform: <platform/publishing direction>
Target Length: <word count>
Genre & Core Concept: <content>
Must Preserve: <hard constraints>
Absolutely Forbidden: <exclusions>
Reference Works: <titles and dimensions for reference only>
This Round: <market research/setting/relationships/master outline/volume outline/chapter outline/audit>
Allow Drafting: No
Deliverable: Complete Markdown package + audit report + compressed archive.
```

## Version

**v1.0.0** - Initial release

## License

See individual files for license information.

---

**StoryForge** - Transform scattered ideas into systematic, executable novel outlines.
