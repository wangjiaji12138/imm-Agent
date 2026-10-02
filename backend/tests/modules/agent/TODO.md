# 问题分类与显式工作流测试 TODO

对应任务：[22](../../../../docs/tasks/phase-03-rag.md#task-22)、[23](../../../../docs/tasks/phase-03-rag.md#task-23)、[31](../../../../docs/tasks/phase-04-conversation.md#task-31)、[41](../../../../docs/tasks/phase-05-release.md#task-41)。

新增测试放 backend/tests/modules/agent/；使用假检索与假生成服务。

此目录当前只有测试计划，不计入测试通过数。原有 tests/test_*.py 保留，迁移代码时先运行现有回归；新增功能的行为测试不得只检查占位文件存在。
