# 切分、索引与检索测试 TODO

对应任务：[20](../../../../docs/tasks/phase-03-rag.md#task-20)、[21](../../../../docs/tasks/phase-03-rag.md#task-21)。

新增测试放 backend/tests/modules/retrieval/，覆盖重复索引、旧版本、撤回候选、位置与超时。

此目录当前只有测试计划，不计入测试通过数。原有 tests/test_*.py 保留，迁移代码时先运行现有回归；新增功能的行为测试不得只检查占位文件存在。
