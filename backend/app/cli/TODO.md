# 离线 CLI TODO

CLI 负责参数、依赖装配、逐行结果和退出码；业务规则放到所属模块。任务状态见根目录 [任务导航](../../../TODO.md)。

| 命令文件 | 状态 | 任务与依赖 |
| --- | --- | --- |
| fetch_sources.py / import_documents.py | 已实现 | [11](../../../docs/tasks/phase-02-knowledge.md#task-11)；采集/清洗/导入逻辑按 ARCH-02 下沉 knowledge |
| documents.py | 已实现 | [12](../../../docs/tasks/phase-02-knowledge.md#task-12)；发布、撤回、过期 |
| validate_evals.py | 已实现 | [13](../../../docs/tasks/phase-02-knowledge.md#task-13)；题集格式与来源就绪 |
| reindex.py | 占位，执行会失败 | [20](../../../docs/tasks/phase-03-rag.md#task-20)；全量/单文档重建及删除任务处理 |
| evaluate_retrieval.py | 占位，执行会失败 | [21](../../../docs/tasks/phase-03-rag.md#task-21)；开发集基线 |
| ask.py | 占位，执行会失败 | [22](../../../docs/tasks/phase-03-rag.md#task-22)；命令行科普回答 |
| evaluate_answers.py | 占位，执行会失败 | [40](../../../docs/tasks/phase-05-release.md#task-40)；独立评测 |
| backup.py / restore.py | 占位，执行会失败 | [42](../../../docs/tasks/phase-05-release.md#task-42)；数据版本、导出/恢复与完整性校验 |

未来命令不能输出模拟 success。backup/restore 当前尚不能使用；已导出的手工 SQL 保留在 data/raw/，不自动移动或覆盖。
