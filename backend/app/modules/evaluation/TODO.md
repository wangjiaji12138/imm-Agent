# 数据校验与质量评测 TODO

任务状态与验收见 [13](../../../../docs/tasks/phase-02-knowledge.md#task-13)、[21](../../../../docs/tasks/phase-03-rag.md#task-21)、[40](../../../../docs/tasks/phase-05-release.md#task-40)、[ARCH-02](../../../../docs/tasks/architecture.md#task-ARCH-02)。本文件维护模块边界和落点，不另建重复的完成勾选。

## 数据归属

评测集格式、指标、基线报告和运行元数据；不拥有线上回答策略。

## 调用边界

离线调用应用服务；在线服务不得依赖评测模块。以知识服务查询来源状态。

## 文件职责

schemas.py 与 dataset.py 已实现；检索基线、回答评测、指标和报告仍为占位。

| 文件 | 职责 |
| --- | --- |
| [schemas.py](schemas.py) | EvaluationQuestion 与 Turn 格式校验 |
| [dataset.py](dataset.py) | 读取 JSONL、验证 ID/分组/已发布来源 |
| [retrieval.py](retrieval.py) | 开发集检索基线、Top 5、Recall@5 和耗时 |
| [answers.py](answers.py) | 独立集端到端运行及逐条审查材料 |
| [metrics.py](metrics.py) | 引用、证据不足行为、成功率、P95 和成本计算 |
| [reports.py](reports.py) | 按运行 ID 写不可覆盖的版本报告与汇总 |

## 实现顺序

1. ARCH-02：保持 validate_evals 输出和现有 20 题约束不变。
2. 21：只用 dev 做基线调参；40：固定配置后使用 test。
3. 40：记录数据版本、模型、提示词、时间和错误；不把格式校验当成质量评估。

## 验证

沿用 test_evaluation；新增指标与报告测试放 backend/tests/modules/evaluation/。
