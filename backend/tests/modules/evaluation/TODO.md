# 数据校验与质量评测测试 TODO

对应任务：[13](../../../../docs/tasks/phase-02-knowledge.md#task-13)、[21](../../../../docs/tasks/phase-03-rag.md#task-21)、[40](../../../../docs/tasks/phase-05-release.md#task-40)、[ARCH-02](../../../../docs/tasks/architecture.md#task-ARCH-02)。

沿用 test_evaluation；新增指标与报告测试放 backend/tests/modules/evaluation/。

此目录当前只有测试计划，不计入测试通过数。原有 tests/test_*.py 保留，迁移代码时先运行现有回归；新增功能的行为测试不得只检查占位文件存在。
