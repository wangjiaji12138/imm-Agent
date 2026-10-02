# 有证据的回答生成测试 TODO

对应任务：[22](../../../../docs/tasks/phase-03-rag.md#task-22)。

新增测试放 backend/tests/modules/answering/；不得调用真实模型 API。

此目录当前只有测试计划，不计入测试通过数。原有 tests/test_*.py 保留，迁移代码时先运行现有回归；新增功能的行为测试不得只检查占位文件存在。
