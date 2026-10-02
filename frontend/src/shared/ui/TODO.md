# ui TODO

任务入口：[30](../../../../docs/tasks/phase-04-conversation.md#task-30)。完成状态只在任务卡维护。

| 计划文件 | 职责 |
| --- | --- |
| [RequestState.tsx](RequestState.tsx) | 被多个 feature 使用的加载与请求错误提示，不放医疗业务判断 |

当前文件均占位；现有页面仍在 App.tsx。feature 只通过 shared/api 访问后端，不直接访问数据库或模型，不读写其他 feature 的内部状态；跨 feature 的编排由 App 完成。新增实际功能时再按任务补交互测试。
