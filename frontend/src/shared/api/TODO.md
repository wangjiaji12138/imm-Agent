# api TODO

任务入口：[23](../../../../docs/tasks/phase-03-rag.md#task-23)、[30](../../../../docs/tasks/phase-04-conversation.md#task-30)、[31](../../../../docs/tasks/phase-04-conversation.md#task-31)、[32](../../../../docs/tasks/phase-04-conversation.md#task-32)。完成状态只在任务卡维护。

| 计划文件 | 职责 |
| --- | --- |
| [client.ts](client.ts) | 统一 fetch、超时、request_id 和错误转换 |
| [generated.ts](generated.ts) | 从后端 OpenAPI 生成的类型落点，当前并非已生成契约 |

当前文件均占位；现有页面仍在 App.tsx。feature 只通过 shared/api 访问后端，不直接访问数据库或模型，不读写其他 feature 的内部状态；跨 feature 的编排由 App 完成。新增实际功能时再按任务补交互测试。
