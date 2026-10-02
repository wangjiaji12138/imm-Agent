# 切分、索引与检索 TODO

任务状态与验收见 [20](../../../../docs/tasks/phase-03-rag.md#task-20)、[21](../../../../docs/tasks/phase-03-rag.md#task-21)。本文件维护模块边界和落点，不另建重复的完成勾选。

## 数据归属

确定性切分规则、向量点 ID、检索排序与输入过滤；不拥有文档发布状态。

## 调用边界

依赖 knowledge 的公开证据服务及本模块定义的 Embedding/VectorStore 接口；不直接调用供应商 SDK，不生成答案。

## 文件职责

| 文件 | 职责 |
| --- | --- |
| [schemas.py](schemas.py) | 检索输入、过滤器、候选和已核验 Evidence DTO |
| [ports.py](ports.py) | 已实现 Embedding 与 VectorStore 的最小接口 |
| [chunking.py](chunking.py) | 已实现按标题/段落/句子切分并保留 Unicode 字符区间 |
| [indexing.py](indexing.py) | 已实现全量/单文档重建、幂等和按当前 SQL 状态清理旧向量 |
| [service.py](service.py) | search_knowledge；候选召回后必须通过 knowledge 证据核验 |

## 实现顺序

1. 20：固定切分配置、片段位置和点 ID；测试使用确定性 embedding。
2. 20：删除任务按文档串行处理，执行前检查当前状态和版本。
3. 21：限制 query/limit/filters，保留候选排序，处理空结果及 Qdrant 超时。

## 验证

新增测试放 backend/tests/modules/retrieval/，覆盖重复索引、旧版本、撤回候选、位置与超时。
