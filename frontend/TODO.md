# 前端 TODO 导航

当前 App.tsx 包含已运行的页面、草稿和健康检查。按 [30](../docs/tasks/phase-04-conversation.md#task-30)、[31](../docs/tasks/phase-04-conversation.md#task-31)、[32](../docs/tasks/phase-04-conversation.md#task-32) 逐步提取，保持现有布局和交互；新目录当前不接入 App。

| 功能 | 文件规划 |
| --- | --- |
| 问答与请求状态 | [chat](src/features/chat/TODO.md) |
| 来源展开 | [sources](src/features/sources/TODO.md) |
| 会话与凭据 | [conversations](src/features/conversations/TODO.md) |
| 回答反馈 | [feedback](src/features/feedback/TODO.md) |
| 统一 HTTP 客户端与类型 | [shared/api](src/shared/api/TODO.md) |
| 通用请求状态 UI | [shared/ui](src/shared/ui/TODO.md) |
| 交互测试 | [tests](tests/TODO.md) |

App 负责跨 feature 组装；组件以 props/callbacks 交换数据。前端不判断医学结论或证据是否充足，只显示 API 业务结果；不保存模型密钥。OpenAPI 类型在 API 实现后生成并纳入验证，目前 generated.ts 是占位。

任务 30 再引入必要测试框架，不为占位引入状态库、路由库或测试依赖。已有 build/lint 命令仍可使用。
