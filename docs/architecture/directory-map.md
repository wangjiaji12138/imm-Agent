# 目录与文件职责

本表对应 [layout.json](layout.json)，记录当前实现与后续占位。ARCH-02 已将运行代码归位；按用户要求删除旧 Python 入口，不保留转发层。历史路径对照见 [迁移表](migration.md)。

| 文件 | 当前状态 | 任务 | 职责 |
| --- | --- | --- | --- |
| [backend/app/main.py](../../backend/app/main.py) | 现有实现 | 02 / 03 / 23 | FastAPI 应用装配；注册健康路由 |
| [backend/app/cli/fetch_sources.py](../../backend/app/cli/fetch_sources.py) | 现有实现 | 11 | NCI 采集 CLI 参数与退出码；采集实现在 knowledge.acquisition |
| [backend/app/cli/import_documents.py](../../backend/app/cli/import_documents.py) | 现有实现 | 11 | 现有逐行导入 CLI |
| [backend/app/cli/documents.py](../../backend/app/cli/documents.py) | 现有实现 | 12 | 现有资料状态 CLI |
| [backend/app/cli/validate_evals.py](../../backend/app/cli/validate_evals.py) | 现有实现 | 13 | 现有评测格式校验 CLI |
| [frontend/src/App.tsx](../../frontend/src/App.tsx) | 现有实现 | 04 / 30 / 31 / 32 | 现有页面与草稿交互；按任务逐步提取 feature 组件 |
| [backend/migrations/versions/0001_knowledge.py](../../backend/migrations/versions/0001_knowledge.py) | 现有实现 | 10 | 已执行的迁移不可因目录调整修改 |
| [evals/questions.jsonl](../../evals/questions.jsonl) | 现有实现 | 13 / 40 | 现有 20 题及 dev/test 划分 |
| [data/sources.json](../../data/sources.json) | 现有实现 | 11 | 现有公开来源元数据目录 |
| [backend/app/modules/knowledge/schemas.py](../../backend/app/modules/knowledge/schemas.py) | 现有实现 | 10 / 11 / 12 / ARCH-02 | ImportRecord 校验与只读 DocumentSummary、VersionSnapshot、ChunkSnapshot |
| [backend/app/modules/knowledge/text.py](../../backend/app/modules/knowledge/text.py) | 现有实现 | 10 / 11 / 12 / ARCH-02 | 清洗、SHA-256、URL 规范化和稳定文档 ID 纯函数 |
| [backend/app/modules/knowledge/models.py](../../backend/app/modules/knowledge/models.py) | 现有实现 | 10 / 11 / 12 / ARCH-02 | 现有六张知识表 ORM；使用 infrastructure.orm.Base |
| [backend/app/modules/knowledge/repository.py](../../backend/app/modules/knowledge/repository.py) | 现有实现 | 10 / 11 / 12 / ARCH-02 | 知识模块内部 SQL 查询与索引任务写入；ORM 不跨业务模块 |
| [backend/app/modules/knowledge/service.py](../../backend/app/modules/knowledge/service.py) | 现有实现 | 10 / 11 / 12 / ARCH-02 | 逐行导入与发布/撤回事务；对外统一资料服务 |
| [backend/app/modules/knowledge/evidence.py](../../backend/app/modules/knowledge/evidence.py) | 现有实现 | 10 / 11 / 12 / ARCH-02 | 候选当前 published 状态与最新版本核验，返回只读片段；来源 HTTP 详情待任务 23 |
| [backend/app/modules/knowledge/acquisition.py](../../backend/app/modules/knowledge/acquisition.py) | 现有实现 | 10 / 11 / 12 / ARCH-02 | NCI 白名单抓取、robots 核验和正文提取，供 CLI 调用 |
| [backend/app/modules/retrieval/schemas.py](../../backend/app/modules/retrieval/schemas.py) | 待实现占位 | 20 / 21 | 检索输入、过滤器、候选和已核验 Evidence DTO |
| [backend/app/modules/retrieval/ports.py](../../backend/app/modules/retrieval/ports.py) | 待实现占位 | 20 / 21 | Embedding 与 VectorStore 的最小接口，按任务 20 定义 |
| [backend/app/modules/retrieval/chunking.py](../../backend/app/modules/retrieval/chunking.py) | 待实现占位 | 20 / 21 | 按标题/段落/句子切分并保留 Unicode 字符区间 |
| [backend/app/modules/retrieval/indexing.py](../../backend/app/modules/retrieval/indexing.py) | 待实现占位 | 20 / 21 | 全量/单文档索引与删除任务处理、幂等和过时任务丢弃 |
| [backend/app/modules/retrieval/service.py](../../backend/app/modules/retrieval/service.py) | 待实现占位 | 20 / 21 | search_knowledge；候选召回后必须通过 knowledge 证据核验 |
| [backend/app/modules/answering/schemas.py](../../backend/app/modules/answering/schemas.py) | 待实现占位 | 22 | 六类 result_type 与 evidence_status 的响应约束 |
| [backend/app/modules/answering/ports.py](../../backend/app/modules/answering/ports.py) | 待实现占位 | 22 | 模型 Provider 输入输出及超时错误接口 |
| [backend/app/modules/answering/service.py](../../backend/app/modules/answering/service.py) | 待实现占位 | 22 | 空证据短路、最多一次超时重试、结构化生成 |
| [backend/app/modules/answering/citations.py](../../backend/app/modules/answering/citations.py) | 待实现占位 | 22 | 引用 ID 必须来自本次 Evidence，校验关键结论引用覆盖 |
| [backend/app/modules/agent/state.py](../../backend/app/modules/agent/state.py) | 待实现占位 | 22 / 23 / 31 / 41 | 当前问题、已确认上下文、证据和阶段结果 |
| [backend/app/modules/agent/policy.py](../../backend/app/modules/agent/policy.py) | 待实现占位 | 22 / 23 / 31 / 41 | 按 mvp-scope 对 emergency/refuse/out_of_scope/clarify 分流 |
| [backend/app/modules/agent/workflow.py](../../backend/app/modules/agent/workflow.py) | 待实现占位 | 22 / 23 / 31 / 41 | 先分流，再检索，再生成，再校验；故障走接口错误 |
| [backend/app/modules/conversations/schemas.py](../../backend/app/modules/conversations/schemas.py) | 待实现占位 | 31 / 41 | 会话引用、凭据校验后上下文和消息 DTO |
| [backend/app/modules/conversations/models.py](../../backend/app/modules/conversations/models.py) | 待实现占位 | 31 / 41 | 会话/消息表，新增 Alembic 迁移注册 |
| [backend/app/modules/conversations/repository.py](../../backend/app/modules/conversations/repository.py) | 待实现占位 | 31 / 41 | 会话隔离条件和消息读写 |
| [backend/app/modules/conversations/service.py](../../backend/app/modules/conversations/service.py) | 待实现占位 | 31 / 41 | 新建会话、认证上下文、追加消息和历史裁剪 |
| [backend/app/modules/feedback/schemas.py](../../backend/app/modules/feedback/schemas.py) | 待实现占位 | 32 / 41 | helpful/not_helpful 与最多 500 字备注 |
| [backend/app/modules/feedback/models.py](../../backend/app/modules/feedback/models.py) | 待实现占位 | 32 / 41 | 反馈表与同会话同回答唯一约束 |
| [backend/app/modules/feedback/repository.py](../../backend/app/modules/feedback/repository.py) | 待实现占位 | 32 / 41 | 反馈幂等创建或更新 |
| [backend/app/modules/feedback/service.py](../../backend/app/modules/feedback/service.py) | 待实现占位 | 32 / 41 | 归属验证、输入限制和重复提交更新 |
| [backend/app/modules/evaluation/schemas.py](../../backend/app/modules/evaluation/schemas.py) | 现有实现 | 13 / 21 / 40 / ARCH-02 | EvaluationQuestion 与 Turn 格式、分类及分组约束 |
| [backend/app/modules/evaluation/dataset.py](../../backend/app/modules/evaluation/dataset.py) | 现有实现 | 13 / 21 / 40 / ARCH-02 | 读取 JSONL、验证 ID/分组/已发布来源 |
| [backend/app/modules/evaluation/retrieval.py](../../backend/app/modules/evaluation/retrieval.py) | 待实现占位 | 13 / 21 / 40 / ARCH-02 | 开发集检索基线、Top 5、Recall@5 和耗时 |
| [backend/app/modules/evaluation/answers.py](../../backend/app/modules/evaluation/answers.py) | 待实现占位 | 13 / 21 / 40 / ARCH-02 | 独立集端到端运行及逐条审查材料 |
| [backend/app/modules/evaluation/metrics.py](../../backend/app/modules/evaluation/metrics.py) | 待实现占位 | 13 / 21 / 40 / ARCH-02 | 引用、证据不足行为、成功率、P95 和成本计算 |
| [backend/app/modules/evaluation/reports.py](../../backend/app/modules/evaluation/reports.py) | 待实现占位 | 13 / 21 / 40 / ARCH-02 | 按运行 ID 写不可覆盖的版本报告与汇总 |
| [backend/app/api/dependencies.py](../../backend/app/api/dependencies.py) | 现有实现 | 23 / 32 / 42 / ARCH-02 | 健康检查依赖装配；问答与会话装配待后续任务 |
| [backend/app/api/schemas.py](../../backend/app/api/schemas.py) | 现有实现 | 23 / 32 / 42 / ARCH-02 | HealthResponse 与 ReadinessResponse；问答契约待任务 23 |
| [backend/app/api/errors.py](../../backend/app/api/errors.py) | 待实现占位 | 23 / 32 / 42 / ARCH-02 | 统一 error code/message/request_id 与 404/422/503 |
| [backend/app/api/middleware.py](../../backend/app/api/middleware.py) | 待实现占位 | 23 / 32 / 42 / ARCH-02 | 请求 ID、限流与安全日志边界 |
| [backend/app/api/routes/health.py](../../backend/app/api/routes/health.py) | 现有实现 | 23 / 32 / 42 / ARCH-02 | /health 与 /ready 路由，保持响应及依赖覆盖能力 |
| [backend/app/api/routes/chat.py](../../backend/app/api/routes/chat.py) | 待实现占位 | 23 / 32 / 42 / ARCH-02 | POST /api/chat，调用注入的工作流 |
| [backend/app/api/routes/sources.py](../../backend/app/api/routes/sources.py) | 待实现占位 | 23 / 32 / 42 / ARCH-02 | GET /api/sources/{chunk_id}，调用实时证据核验 |
| [backend/app/api/routes/feedback.py](../../backend/app/api/routes/feedback.py) | 待实现占位 | 23 / 32 / 42 / ARCH-02 | POST /api/feedback，校验会话和回答归属 |
| [backend/app/core/settings.py](../../backend/app/core/settings.py) | 现有实现 | 02 / 41 / 42 / ARCH-02 | 环境变量配置与 get_settings 缓存 |
| [backend/app/core/errors.py](../../backend/app/core/errors.py) | 待实现占位 | 02 / 41 / 42 / ARCH-02 | 业务/依赖错误类型，不依赖 HTTP 或厂商 SDK |
| [backend/app/core/logging.py](../../backend/app/core/logging.py) | 待实现占位 | 02 / 41 / 42 / ARCH-02 | 结构化白名单日志，排除问题全文、凭据和反馈备注 |
| [backend/app/infrastructure/database.py](../../backend/app/infrastructure/database.py) | 现有实现 | 10 / 20 / 22 / 42 / ARCH-02 | 惰性 SQL 引擎与 Session 工厂 |
| [backend/app/infrastructure/orm.py](../../backend/app/infrastructure/orm.py) | 现有实现 | 10 / 20 / 22 / 42 / ARCH-02 | 唯一 DeclarativeBase；模型在 Alembic 装配入口显式注册 |
| [backend/app/infrastructure/readiness.py](../../backend/app/infrastructure/readiness.py) | 现有实现 | 10 / 20 / 22 / 42 / ARCH-02 | MySQL 与 Qdrant 连通性检查 |
| [backend/app/infrastructure/embedding.py](../../backend/app/infrastructure/embedding.py) | 待实现占位 | 10 / 20 / 22 / 42 / ARCH-02 | 实现 retrieval.ports 的 embedding 接口 |
| [backend/app/infrastructure/vector_store.py](../../backend/app/infrastructure/vector_store.py) | 待实现占位 | 10 / 20 / 22 / 42 / ARCH-02 | 实现 retrieval.ports 的 Qdrant 接口 |
| [backend/app/infrastructure/llm.py](../../backend/app/infrastructure/llm.py) | 待实现占位 | 10 / 20 / 22 / 42 / ARCH-02 | 实现 answering.ports 的模型接口，封装供应商 SDK |
| [backend/app/cli/reindex.py](../../backend/app/cli/reindex.py) | 待实现占位 | 20 | 全量/单文档重建与索引任务处理 |
| [backend/app/cli/ask.py](../../backend/app/cli/ask.py) | 待实现占位 | 22 | 命令行运行科普问答 |
| [backend/app/cli/evaluate_retrieval.py](../../backend/app/cli/evaluate_retrieval.py) | 待实现占位 | 21 | 生成开发集检索基线 |
| [backend/app/cli/evaluate_answers.py](../../backend/app/cli/evaluate_answers.py) | 待实现占位 | 40 | 运行固定配置下的独立评测 |
| [backend/app/cli/backup.py](../../backend/app/cli/backup.py) | 待实现占位 | 42 | 导出 MySQL 与原始资料、版本清单、SHA-256；不打包密钥 |
| [backend/app/cli/restore.py](../../backend/app/cli/restore.py) | 待实现占位 | 42 | 校验备份并恢复到显式指定的空测试库，拒绝默认覆盖现有库 |
| [frontend/src/features/chat/ChatPanel.tsx](../../frontend/src/features/chat/ChatPanel.tsx) | 待实现占位 | 30 | 问题与回答列表、加载/错误/证据不足状态 |
| [frontend/src/features/chat/useChat.ts](../../frontend/src/features/chat/useChat.ts) | 待实现占位 | 30 | 发送、取消、重复提交限制与失败后保留草稿 |
| [frontend/src/features/sources/SourceCard.tsx](../../frontend/src/features/sources/SourceCard.tsx) | 待实现占位 | 30 | 机构、标题、日期、支持结论及原文展开 |
| [frontend/src/features/conversations/ConversationList.tsx](../../frontend/src/features/conversations/ConversationList.tsx) | 待实现占位 | 31 | 当前会话与新建会话入口 |
| [frontend/src/features/conversations/useConversation.ts](../../frontend/src/features/conversations/useConversation.ts) | 待实现占位 | 31 | 会话凭据生命周期与历史请求隔离 |
| [frontend/src/features/feedback/FeedbackForm.tsx](../../frontend/src/features/feedback/FeedbackForm.tsx) | 待实现占位 | 32 | 反馈提交、更新、备注长度和错误提示 |
| [frontend/src/shared/api/client.ts](../../frontend/src/shared/api/client.ts) | 待实现占位 | 23 / 30 / 31 / 32 | 统一 fetch、超时、request_id 和错误转换 |
| [frontend/src/shared/api/generated.ts](../../frontend/src/shared/api/generated.ts) | 待实现占位 | 23 / 30 / 31 / 32 | 从后端 OpenAPI 生成的类型落点，当前并非已生成契约 |
| [frontend/src/shared/ui/RequestState.tsx](../../frontend/src/shared/ui/RequestState.tsx) | 待实现占位 | 30 | 被多个 feature 使用的加载与请求错误提示，不放医疗业务判断 |
| [backend/app/modules/answering/prompts/v1.md](../../backend/app/modules/answering/prompts/v1.md) | 待实现占位 | 22 | 版本化提示词占位，不能用于生成 |
| [deploy/compose.production.yaml.example](../../deploy/compose.production.yaml.example) | 待实现占位 | 42 | 生产部署配置示例占位，当前不可运行 |
| [.github/workflows/ci.yml.example](../../.github/workflows/ci.yml.example) | 待实现占位 | 41 / 42 | CI 设计占位，不自动执行 |
| [docs/mvp-scope.md](../../docs/mvp-scope.md) | 现有实现 | 01 | 现有首版范围与业务分类的唯一规则 |
| [scripts/check_layout.py](../../scripts/check_layout.py) | 现有实现 | ARCH-01 / ARCH-02 | 架构入口、占位、任务覆盖与本地文档链接检查；不代替 import 依赖检查 |
| [backend/tests/test_architecture.py](../../backend/tests/test_architecture.py) | 现有实现 | ARCH-02 | 静态 import 边界、相对导入、循环依赖及违规示例检查 |
| [backend/tests/modules/knowledge/test_service.py](../../backend/tests/modules/knowledge/test_service.py) | 现有实现 | ARCH-02 | 只读 DTO 脱离 Session 与状态/索引任务原子回滚验证 |
