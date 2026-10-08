# Templates 使用说明

`templates/` 中的文件是可组合的 Markdown 片段。推荐使用：

```bash
python ../scripts/init_novel_project.py --name "项目名" --output /path/to/workspace
```

初始化脚本会：

- 为项目核心文件添加统一前置元数据。
- 合并资源、境界、金手指等相关模板。
- 创建索引、事实台账、审计、灵感、废案和待决策文件。

手动复制模板时，必须自行添加 `STATE_CONTRACT.md` 规定的前置元数据和唯一 `doc_id`。模板中的 `<待填写>` 是候选阶段占位符，最终交付前必须填写、删除或明确标为 `N/A`/`DEFERRED`。

模板是能力上限，不要求每个项目机械填满。参见 `docs/23_题材适配与规模裁剪.md`。
