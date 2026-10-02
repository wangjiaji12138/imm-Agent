# 评测资产 TODO

任务：[13](../docs/tasks/phase-02-knowledge.md#task-13)、[21](../docs/tasks/phase-03-rag.md#task-21)、[40](../docs/tasks/phase-05-release.md#task-40)。运行代码在 [evaluation 模块](../backend/app/modules/evaluation/TODO.md)，本目录只保存题目与审查标注。

- 现有 questions.jsonl 保留 20 题及 15 dev / 5 test；格式见 [evaluation-format](../docs/evaluation-format.md)。
- 21 仅用 dev 做检索基线与调参；40 固定配置后运行 test，不能针对保留题改提示词。
- 为报告关联固定资料版本/正文哈希、模型、提示词与代码版本；来源更新后需要重新核对判断条件。
- 敏感病例不加入公开题集。新增题目应经过资料支持核对，并记录人工审查，不把模型生成内容直接当标准答案。
- 大型运行结果放被 Git 忽略的 artifacts/；可提交不含隐私的评测结论至 docs。
