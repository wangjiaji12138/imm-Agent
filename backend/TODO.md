# 后端 TODO 导航

[根任务导航](../TODO.md) · [架构与边界](../docs/architecture/README.md)

当前 app/main.py、knowledge.py、evaluation.py 等为已运行实现。新 api/core/infrastructure/modules 目录只有占位；先按 [ARCH-02](../docs/tasks/architecture.md#task-ARCH-02) 逐步迁入，不能直接删除旧入口。

| 分区 | 模块 TODO |
| --- | --- |
| HTTP | [api](app/api/TODO.md) |
| 共用配置与日志 | [core](app/core/TODO.md) |
| 外部适配 | [infrastructure](app/infrastructure/TODO.md) |
| 知识资料 | [knowledge](app/modules/knowledge/TODO.md) |
| 检索与索引 | [retrieval](app/modules/retrieval/TODO.md) |
| 回答生成 | [answering](app/modules/answering/TODO.md) |
| Agent 编排 | [agent](app/modules/agent/TODO.md) |
| 会话 | [conversations](app/modules/conversations/TODO.md) |
| 反馈 | [feedback](app/modules/feedback/TODO.md) |
| 评测 | [evaluation](app/modules/evaluation/TODO.md) |
| 管理命令 | [CLI](app/cli/TODO.md) |
| 迁移 | [migrations](migrations/TODO.md) |
| 测试 | [tests](tests/TODO.md) |

运行与依赖安装统一使用项目根目录的 docker compose。不要在占位 __init__.py 中自动导入未来模块或注册路由。
