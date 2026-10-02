# 资料与知识治理 TODO

任务状态与验收见 [10](../../../../docs/tasks/phase-02-knowledge.md#task-10)、[11](../../../../docs/tasks/phase-02-knowledge.md#task-11)、[12](../../../../docs/tasks/phase-02-knowledge.md#task-12)、[ARCH-02](../../../../docs/tasks/architecture.md#task-ARCH-02)。本文件维护模块边界和落点，不另建重复的完成勾选。

## 数据归属

documents、document_versions、chunks、terms、term_aliases、index_jobs；正文哈希、文档状态、最新版本与片段追溯规则。

## 调用边界

向检索模块提供资料读取、片段写入与证据核验；不调用 Qdrant 或生成模型。抓取仅在离线白名单采集中进行。

## 计划文件（当前均为占位）

| 文件 | 职责 |
| --- | --- |
| [schemas.py](schemas.py) | ImportRecord 与资料摘要；从现有 knowledge.py 提取输入校验 |
| [text.py](text.py) | 清洗、SHA-256、URL 规范化和稳定文档 ID 纯函数 |
| [models.py](models.py) | 现有六张知识表 ORM；使用 infrastructure.orm.Base |
| [repository.py](repository.py) | 资料、版本、片段和索引任务的 SQL 访问；向外返回 schema，不暴露 ORM |
| [service.py](service.py) | 逐行导入与发布/撤回事务；对外统一资料服务 |
| [evidence.py](evidence.py) | 检索候选的当前 published 状态与最新版本核验，以及来源详情读取 |
| [acquisition.py](acquisition.py) | NCI 白名单抓取、robots 核验和正文提取，供 CLI 调用 |

## 实现顺序

1. 先迁移纯函数与输入模型，再迁移 ORM、仓储和服务；旧导入路径保留显式转发。
2. 索引任务与文档状态同事务提交；索引消费者只通过公开方法领取/完成任务。
3. 证据核验始终查询 SQL 当前状态；单次在线请求使用短事务。

## 验证

沿用 test_models、test_import_documents、test_publication、test_fetch_sources 和 MySQL 集成测试。
