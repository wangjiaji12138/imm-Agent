# 会话与多轮上下文 TODO

任务状态与验收见 [31](../../../../docs/tasks/phase-04-conversation.md#task-31)、[41](../../../../docs/tasks/phase-05-release.md#task-41)。本文件维护模块边界和落点，不另建重复的完成勾选。

## 数据归属

conversations、messages、不可猜测会话凭据、必要历史和摘要。

## 调用边界

凭据校验在读取历史之前；不负责选疗法，不反向调用 Agent 或保存无必要完整隐私材料。

## 计划文件（当前均为占位）

| 文件 | 职责 |
| --- | --- |
| [schemas.py](schemas.py) | 会话引用、凭据校验后上下文和消息 DTO |
| [models.py](models.py) | 会话/消息表，新增 Alembic 迁移注册 |
| [repository.py](repository.py) | 会话隔离条件和消息读写 |
| [service.py](service.py) | 新建会话、认证上下文、追加消息和历史裁剪 |

## 实现顺序

1. 31：明确会话凭据传输与保存方式，和前端/API 一起实现。
2. 31：跨会话访问返回 404，支持新会话、三轮追问和话题切换。
3. 42：在发布前确定保留期限与删除流程。

## 验证

新增测试放 backend/tests/modules/conversations/；覆盖凭据隔离与模糊指代上下文。
