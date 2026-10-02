# 问题分类与显式工作流 TODO

任务状态与验收见 [22](../../../../docs/tasks/phase-03-rag.md#task-22)、[23](../../../../docs/tasks/phase-03-rag.md#task-23)、[31](../../../../docs/tasks/phase-04-conversation.md#task-31)、[41](../../../../docs/tasks/phase-05-release.md#task-41)。本文件维护模块边界和落点，不另建重复的完成勾选。

## 数据归属

流程顺序、业务分支、有限检索重试与澄清状态；不保存用户数据。

## 调用边界

编排 retrieval、answering、conversations 的服务；下游模块不反向依赖 agent。首版使用 Python 显式流程。

## 计划文件（当前均为占位）

| 文件 | 职责 |
| --- | --- |
| [state.py](state.py) | 当前问题、已确认上下文、证据和阶段结果 |
| [policy.py](policy.py) | 按 mvp-scope 对 emergency/refuse/out_of_scope/clarify 分流 |
| [workflow.py](workflow.py) | 先分流，再检索，再生成，再校验；故障走接口错误 |

## 实现顺序

1. 22：先实现回答边界；紧急/拒绝/超范围/澄清分支先于检索和知识生成。
2. 23：绑定单轮工作流；31：添加必要会话历史，模糊指代必须澄清。
3. 41：验证提示注入、任意 SQL/URL 诱导和敏感日志。

## 验证

新增测试放 backend/tests/modules/agent/；使用假检索与假生成服务。
