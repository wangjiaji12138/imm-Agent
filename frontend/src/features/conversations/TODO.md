# conversations TODO

任务入口：[31](../../../../docs/tasks/phase-04-conversation.md#task-31)。完成状态只在任务卡维护。

| 计划文件 | 职责 |
| --- | --- |
| [ConversationList.tsx](ConversationList.tsx) | 当前会话与新建会话入口 |
| [useConversation.ts](useConversation.ts) | 会话凭据生命周期与历史请求隔离 |

当前文件均占位；现有页面仍在 App.tsx。feature 只通过 shared/api 访问后端，不直接访问数据库或模型，不读写其他 feature 的内部状态；跨 feature 的编排由 App 完成。新增实际功能时再按任务补交互测试。
