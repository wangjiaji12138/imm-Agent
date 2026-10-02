# 回答反馈 TODO

任务状态与验收见 [32](../../../../docs/tasks/phase-04-conversation.md#task-32)、[41](../../../../docs/tasks/phase-05-release.md#task-41)。本文件维护模块边界和落点，不另建重复的完成勾选。

## 数据归属

feedback 表；会话内 request_id 与反馈唯一性。

## 调用边界

通过 conversations 的身份校验结果验证归属；不直接读写其他模块的表，不触发模型调用。

## 计划文件（当前均为占位）

| 文件 | 职责 |
| --- | --- |
| [schemas.py](schemas.py) | helpful/not_helpful 与最多 500 字备注 |
| [models.py](models.py) | 反馈表与同会话同回答唯一约束 |
| [repository.py](repository.py) | 反馈幂等创建或更新 |
| [service.py](service.py) | 归属验证、输入限制和重复提交更新 |

## 实现顺序

1. 32：先验证 request_id 属于当前会话，再写反馈。
2. 32：未知请求 404，超长输入 422；备注不进入日志。

## 验证

新增测试放 backend/tests/modules/feedback/；覆盖归属、长度和幂等更新。
