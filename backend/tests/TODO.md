# 后端测试 TODO

[任务导航](../../TODO.md) · [模块迁移验收](../../docs/tasks/architecture.md#task-ARCH-02)

现有 tests/test_*.py 保持入口，涵盖健康、资料、迁移、来源采集、评测格式及可选真实 MySQL。新增模块测试分别放 [knowledge](modules/knowledge/TODO.md)、[retrieval](modules/retrieval/TODO.md)、[answering](modules/answering/TODO.md)、[agent](modules/agent/TODO.md)、[conversations](modules/conversations/TODO.md)、[feedback](modules/feedback/TODO.md)、[evaluation](modules/evaluation/TODO.md)。跨依赖验证放 [integration](integration/TODO.md)。

从项目根目录运行：

```text
docker compose run --rm backend python -m pytest
docker compose run --rm -e IMM_AGENT_TEST_MYSQL=1 backend python -m pytest
```

第二条要求已迁移的 MySQL。普通测试不调用外部模型和真实网站；使用确定性替身验证内容、异常和边界。测试计划文件不包含假测试函数，不增加 passed 数量。

ARCH-02 的实际依赖检查位于 test_architecture.py：扫描应用 import、相对导入与循环依赖，并验证违规示例会失败。modules/knowledge/test_service.py 验证 DTO 脱离 Session 后可读、不可变，以及状态与索引任务一起回滚。原有 34 项测试保留行为断言，统一使用新模块路径。
