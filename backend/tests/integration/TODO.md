# 集成测试 TODO

任务入口：[20](../../../docs/tasks/phase-03-rag.md#task-20), [21](../../../docs/tasks/phase-03-rag.md#task-21), [23](../../../docs/tasks/phase-03-rag.md#task-23), [31](../../../docs/tasks/phase-04-conversation.md#task-31), [41](../../../docs/tasks/phase-05-release.md#task-41), [42](../../../docs/tasks/phase-05-release.md#task-42)。

覆盖真实 MySQL 事务、Qdrant 更新/撤回一致性、HTTP 来源可解析性、会话隔离和空库恢复。现有 test_mysql_integration.py 保持原入口；新测试使用隔离库/集合与回滚清理，不删除现有数据。
