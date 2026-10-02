# 后端 TODO 导航

[根任务导航](../TODO.md) · [架构与边界](../docs/architecture/README.md)

第一、二阶段逻辑已按 [ARCH-02](../docs/tasks/architecture.md#task-ARCH-02) 迁入 api/core/infrastructure/modules。main.py 仅负责装配；旧平铺 Python 模块按用户要求删除。后续功能仍以 PLANNED 标识占位。

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
