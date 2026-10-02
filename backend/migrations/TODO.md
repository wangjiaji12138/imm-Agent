# 数据库迁移 TODO

任务：[10](../../docs/tasks/phase-02-knowledge.md#task-10)、[31](../../docs/tasks/phase-04-conversation.md#task-31)、[32](../../docs/tasks/phase-04-conversation.md#task-32)、[42](../../docs/tasks/phase-05-release.md#task-42)、[ARCH-02](../../docs/tasks/architecture.md#task-ARCH-02)。

1. 保留已执行的 0001_knowledge.py；代码归位不得修改其建表行为。
2. ARCH-02 把唯一 Base 与所有模型注册接到 env.py；metadata 对比必须没有额外差异。
3. 31 新增会话与消息迁移，32 新增反馈迁移；编号和真实字段等任务实现时确定，不预建空迁移。
4. 42 验证空库升级、隔离环境恢复与版本回滚；不能拿现有资料库做清空演练。

已执行迁移是历史，不能通过编辑旧文件修复新的 schema 变化。新变化必须新增迁移并记录数据兼容方案。
