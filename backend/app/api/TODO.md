# HTTP 接口层 TODO

任务入口：[23](../../../docs/tasks/phase-03-rag.md#task-23)、[32](../../../docs/tasks/phase-04-conversation.md#task-32)、[42](../../../docs/tasks/phase-05-release.md#task-42)、[ARCH-02](../../../docs/tasks/architecture.md#task-ARCH-02)。任务卡是完成状态的唯一来源。

| 计划文件 | 职责 |
| --- | --- |
| [dependencies.py](dependencies.py) | 在请求边界装配服务、短事务与会话认证依赖 |
| [schemas.py](schemas.py) | HTTP 请求/响应与业务 DTO 的边界映射 |
| [errors.py](errors.py) | 统一 error code/message/request_id 与 404/422/503 |
| [middleware.py](middleware.py) | 请求 ID、限流与安全日志边界 |
| [routes/health.py](routes/health.py) | 将现有 /health 与 /ready 路由迁入，契约不变 |
| [routes/chat.py](routes/chat.py) | POST /api/chat，调用注入的工作流 |
| [routes/sources.py](routes/sources.py) | GET /api/sources/{chunk_id}，调用实时证据核验 |
| [routes/feedback.py](routes/feedback.py) | POST /api/feedback，校验会话和回答归属 |

实现顺序与禁止依赖见 [模块边界](../../../docs/architecture/boundaries.md)。聊天、来源、请求 ID 和统一错误已实现；会话认证与反馈待后续任务。
