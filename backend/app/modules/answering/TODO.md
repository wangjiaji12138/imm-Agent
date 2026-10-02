# 有证据的回答生成 TODO

任务状态与验收见 [22](../../../../docs/tasks/phase-03-rag.md#task-22)。本文件维护模块边界和落点，不另建重复的完成勾选。

## 数据归属

结构化回答、引用验证、提示词版本；不负责检索和文档状态修改。

## 调用边界

只接收已核验 Evidence 和问题上下文，通过注入的模型接口生成；检索文本是数据，不能覆盖系统规则。

## 计划文件（当前均为占位）

| 文件 | 职责 |
| --- | --- |
| [schemas.py](schemas.py) | 六类 result_type 与 evidence_status 的响应约束 |
| [ports.py](ports.py) | 模型 Provider 输入输出及超时错误接口 |
| [service.py](service.py) | 空证据短路、最多一次超时重试、结构化生成 |
| [citations.py](citations.py) | 引用 ID 必须来自本次 Evidence，校验关键结论引用覆盖 |

## 实现顺序

1. 将提示词存入 prompts/ 并记录版本；未验收的占位提示词不得加载。
2. 以假 Provider 覆盖空证据、虚构引用、格式错误、冲突和超时。
3. 结构校验不能代替事实支持审查；评测时保留逐条复核。

## 验证

新增测试放 backend/tests/modules/answering/；不得调用真实模型 API。
