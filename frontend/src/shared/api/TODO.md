# api TODO

任务入口：[23](../../../../docs/tasks/phase-03-rag.md#task-23)、[30](../../../../docs/tasks/phase-04-conversation.md#task-30)、[31](../../../../docs/tasks/phase-04-conversation.md#task-31)、[32](../../../../docs/tasks/phase-04-conversation.md#task-32)。完成状态只在任务卡维护。

| 计划文件 | 职责 |
| --- | --- |
| [client.ts](client.ts) | 统一 fetch、超时、request_id 和错误转换 |
| [generated.ts](generated.ts) | 从后端 OpenAPI 生成的类型落点，当前并非已生成契约 |

客户端与任务 23 OpenAPI 契约对应的类型已接入页面。会话和反馈契约待后续任务扩展。
