# 外部系统适配 TODO

任务入口：[10](../../../docs/tasks/phase-02-knowledge.md#task-10)、[20](../../../docs/tasks/phase-03-rag.md#task-20)、[22](../../../docs/tasks/phase-03-rag.md#task-22)、[42](../../../docs/tasks/phase-05-release.md#task-42)、[ARCH-02](../../../docs/tasks/architecture.md#task-ARCH-02)。任务卡是完成状态的唯一来源。

| 计划文件 | 职责 |
| --- | --- |
| [database.py](database.py) | 现有连接配置/Session 工厂迁入，保持惰性连接 |
| [orm.py](orm.py) | 全项目唯一 DeclarativeBase 与模型注册入口 |
| [readiness.py](readiness.py) | 现有 MySQL/Qdrant 连通性检查迁入 |
| [embedding.py](embedding.py) | 实现 retrieval.ports 的 embedding 接口 |
| [vector_store.py](vector_store.py) | 实现 retrieval.ports 的 Qdrant 接口 |
| [llm.py](llm.py) | 实现 answering.ports 的模型接口，封装供应商 SDK |

实现顺序与禁止依赖见 [模块边界](../../../docs/architecture/boundaries.md)。所有文件当前只是占位，不能因目录存在就宣称接口或适配器已完成。
