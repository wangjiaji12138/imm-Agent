# 第三阶段任务卡

[返回任务总入口](../../TODO.md) · [架构导航](../architecture/README.md)

这里是本阶段任务状态、验收条件和完成记录的唯一维护位置。原任务卡和历史完成记录保留；卡片中路径表示仓库根目录下的位置。未来实现位置以架构目录表为准，历史记录不改写。

## 第三阶段：跑通带引用的最小 RAG

<a id="task-20"></a>

### 20｜切分并建立 Qdrant 索引

- [x] 将已发布文档切分、向量化并写入 Qdrant。

首版切分规则要固定在配置中：按标题和段落切分，过长段落再按句子切分；片段保留 `chunk_id`、`document_id`、`version_id`、标题路径、字符位置和文档状态。Embedding 通过接口封装，测试使用确定性的假模型。

提供命令：

```powershell
docker compose run --rm backend python -m app.cli.reindex --all
docker compose run --rm backend python -m app.cli.reindex --document <document-id>
```

验收：同一版本重复建索引不会产生重复点；更新文档后旧版本不再返回；撤回文档不再返回；能够从任一检索结果追溯到原始正文位置。

交给编程助手：

> 完成 TODO 任务 20。实现可测试的切分器、Embedding 接口、Qdrant 写入和全量/单文档重建命令。点 ID 必须稳定，payload 包含任务要求的追溯字段。生产模型通过环境变量配置，测试不得调用外部 API。

进度记录：文件=`backend/app/modules/retrieval/`、`backend/app/infrastructure/embedding.py`、`backend/app/infrastructure/vector_store.py`、`backend/app/cli/reindex.py`、`backend/app/modules/knowledge/service.py`；验证=确定性假模型覆盖 Unicode 位置、重复索引、版本替换和撤回；容器内后端测试含真实 MySQL 检查通过，独立临时集合上的真实 Qdrant 写入、重复写入和删除测试通过；待验收=配置真实 Embedding 服务，对已发布 NCI 资料执行全量重建并核对点数、重复重建和原文位置。在此之前任务保持未完成。任务 21 的在线检索尚未实现。

最终验收（2026-10-02，北京时间 20:49）：已配置百炼北京地域 `text-embedding-v4`，1024 维、每批 10 条。真实执行 `python -m app.cli.reindex --all` 两次，5 篇已发布 NCI 文档均成功，共 180 个向量点。两次点 ID 与 payload 摘要完全一致，未产生重复点；所有片段的原文字符区间、最新版本和 SQL 发布状态核验通过，无多余旧点。容器内全套测试启用 MySQL/Qdrant 集成检查，结果为 58 passed，保留 1 条上游 TestClient 弃用警告。核验记录保存在本地 `artifacts/task20/first.json`、`artifacts/task20/repeated.json`；不包含密钥或正文。版本替换、撤回过滤及失败重试由自动测试覆盖，未撤回现有 NCI 业务资料。任务 21 的统一检索与质量基线仍待开发。

<a id="task-21"></a>

### 21｜实现统一检索接口

- [x] 实现 `search_knowledge(query, filters, limit)`。

输入要求：`query` 长度 2～500，`limit` 范围 1～20，首版过滤器只支持语言、文档 ID 和发布日期范围。输出每项包含 `chunk_id`、`text`、`title`、`organization`、`source_url`、`published_at`、`score`。

查询 Qdrant 后必须回查 MySQL，只返回当前为 `published` 且版本匹配的片段。没有结果时返回空列表，不抛出业务异常。

验收：用固定问题运行评测，生成 `artifacts/retrieval-baseline.json`，至少记录每题 Top 5 结果、Recall@5 和耗时；测试覆盖空查询、非法 limit、已撤回文档和 Qdrant 超时。

交给编程助手：

> 完成 TODO 任务 21。按卡片定义 search_knowledge 的输入、输出和过滤器；检索后回查 MySQL 的发布状态与版本。增加超时处理和测试，并提供运行 evals/questions.jsonl 的检索评测命令，输出指定基线文件。

验收记录（2026-10-02）：实现查询校验、Qdrant 候选分页、MySQL 当前发布状态/最新版本与过滤条件核验；Embedding/Qdrant 超时返回依赖错误。运行 `python -m app.cli.evaluate_retrieval --questions ../evals/questions.jsonl --output ../artifacts/retrieval-baseline.json` 生成 20 题基线，17 道有预期来源的题平均 Recall@5 为 1.0；3 道无预期来源题的 Recall@5 为 null。每题记录 Top 5 和耗时。后端本地测试 62 passed、2 skipped，跳过的是真实 MySQL/Qdrant 集成检查；基线命令实际连接了已运行的 MySQL、Qdrant 与 Embedding 服务。

<a id="task-22"></a>

### 22｜接入大模型并生成结构化答案

- [ ] 建立可替换的模型适配层，并让回答只依据本次检索片段。

内部响应格式：

业务分类和字段约束以 `docs/mvp-scope.md` 第 4、5 节为准；拒绝、紧急引导、超范围和澄清分支在检索及知识结论生成之前处理，系统故障走接口错误响应。

```json
{
  "result_type": "answer|clarify|insufficient|refuse|out_of_scope|emergency",
  "answer": "回答正文",
  "citations": [{"chunk_id": "...", "claim": "该片段支持的结论"}],
  "evidence_status": "sufficient|insufficient|conflicting|not_applicable",
  "follow_up_question": null
}
```

超时只重试 1 次；记录模型名、提示词版本、耗时和 token 用量，日志不能记录完整用户隐私文本。模型引用的 `chunk_id` 必须属于本次检索结果，否则整次响应判为无效。检索为空时不调用模型，直接返回 `insufficient`。

验收：测试覆盖正常回答、空检索、虚构引用、格式错误、模型超时和来源冲突。命令行输入问题后能看到回答以及可解析的来源。

交给编程助手：

> 完成 TODO 任务 22。创建模型 Provider 接口、一个由环境变量配置的实现、版本化提示词和 Pydantic 响应模型。回答仅能使用传入片段，严格校验引用 ID。测试用假 Provider 覆盖卡片列出的 6 种情况，不在测试中调用真实模型。

<a id="task-23"></a>

### 23｜提供聊天 API

- [ ] 实现 `POST /api/chat` 和 `GET /api/sources/{chunk_id}`。

`POST /api/chat` 输入 `message` 和可空 `conversation_id`，输出 `request_id`、`conversation_id`、任务 22 的字段及来源摘要。`GET /api/sources/{chunk_id}` 返回资料标题、机构、日期、来源 URL、原文片段和片段位置。

统一错误格式为 `{"error":{"code":"...","message":"...","request_id":"..."}}`。非法输入返回 422，依赖暂不可用返回 503，找不到来源返回 404。每次请求生成 request ID。

验收：OpenAPI 文档能看到两个接口；接口测试覆盖 200、404、422、503；一次提问返回的每个引用都能通过来源接口展开。

交给编程助手：

> 完成 TODO 任务 23。实现两个 API、请求/响应模型、统一错误结构和 request ID。连接现有检索与回答服务。写接口测试，证明回答引用能通过 sources 接口解析。暂不实现登录、流式输出和反馈。
