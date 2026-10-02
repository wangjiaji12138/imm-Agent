# chat TODO

任务入口：[30](../../../../docs/tasks/phase-04-conversation.md#task-30)。完成状态只在任务卡维护。

| 计划文件 | 职责 |
| --- | --- |
| [ChatPanel.tsx](ChatPanel.tsx) | 问题与回答列表、加载/错误/证据不足状态 |
| [useChat.ts](useChat.ts) | 发送、取消、重复提交限制与失败后保留草稿 |

问答组件和 hook 已接入 App。feature 只通过 shared/api 访问后端；跨 feature 的编排由 App 完成。
