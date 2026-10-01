# Imm-Agent 可执行开发清单

这份清单用于直接驱动开发。一次只做一个任务卡；完成卡片里的全部验收后，才把 `- [ ]` 改成 `- [x]`。

当前仓库只有 `README.md` 和本文件，还没有应用代码。本项目从空仓库开始实现，不寻找、不导入、不适配任何旧网页、旧爬虫、旧代码或旧数据库。下面定义的目录、接口和数据结构都是新系统的唯一实现目标。

## 使用方法

首次开发或更换电脑时，先完整执行 [Windows 开发工作流](docs/development-workflow.md)，确认容器构建、健康检查和测试全部通过。

每次 VibeCoding 时，把一个任务卡中“交给编程助手”下的文字完整复制给编程助手。编程助手需要先读 `README.md` 和本文件，只修改任务涉及的文件，完成后运行卡片指定的验收命令。

每个任务完成时，在该任务下面追加一行结果：

```text
完成记录：文件=<主要文件>；验证=<运行的命令与结果>；备注=<遗留问题，没有则写无>
```

项目默认技术选择如下：

- 后端镜像使用 Python 3.10、FastAPI、Pydantic v2、SQLAlchemy 2、Alembic、pytest。
- 前端镜像使用 Node.js 22、React、TypeScript、Vite。
- MySQL 保存业务数据，Qdrant 保存向量索引。
- 后端目录为 `backend/`，前端目录为 `frontend/`，项目文档为 `docs/`，原始资料只放在不提交 Git 的 `data/raw/`。
- 首版只做癌症免疫疗法科普问答、来源展示和多轮追问。不做诊断、个体化治疗建议、自动用药建议、模型微调和知识图谱。

宿主机只要求安装 Git、WSL 2 和 Docker Desktop。Python、Node.js、项目包、MySQL 与 Qdrant 全部安装在镜像或容器内。除 Docker 命令外，本文命令都通过 `docker compose run` 或 `docker compose exec` 执行，不依赖宿主机的 Python、Node.js、pip 或 npm。

## 第一阶段：先得到可以启动的空应用

### 01｜写死首版范围

- [x] 创建 `docs/mvp-scope.md`，明确首版做什么、输入输出是什么、什么情况必须拒答。

文档必须包含以下内容：

- 支持的问题：概念解释、术语解释、作用机制、不同疗法的资料内比较、研究进展、基于上一轮的追问。
- 回答结构：简短结论、通俗解释、适用条件或研究状态、来源列表。
- 证据不足时的固定行为：明确说“当前资料不足以回答”，同时列出已找到的相关来源，不补写结论。
- 个体化治疗请求的固定行为：解释只能提供一般科普信息，建议咨询专业医生，不判断用户适合哪种治疗。
- 首版不做：诊断、剂量建议、治疗方案选择、联网自由搜索、知识图谱、模型微调。
- 5 个正常问题示例和 5 个拒答或证据不足示例，每个示例写预期行为。

验收：开发者看到任意一个用户问题，都能依据文档判断它属于“回答”“澄清”还是“拒答/证据不足”。

交给编程助手：

> 创建 docs/mvp-scope.md。把 TODO 任务 01 中列出的支持范围、回答结构、证据不足行为、个体化请求行为、排除项和 10 个示例完整写入文档。使用可以测试的句子，避免“适当处理”“视情况而定”等模糊表达。

完成记录：文件=`docs/mvp-scope.md`；验证=10 个示例均包含输入、预期分类和通过条件；备注=无。

### 02｜创建后端骨架和健康检查

- [x] 创建一个能启动的 FastAPI 后端。

需要创建：

```text
backend/
  Dockerfile
  .dockerignore
  pyproject.toml
  app/__init__.py
  app/main.py
  app/settings.py
  tests/test_health.py
.env.example
.gitignore
```

具体行为：

- `GET /health` 返回 HTTP 200 和 `{"status":"ok","service":"imm-agent"}`。
- 配置从环境变量读取；缺少与健康检查无关的数据库或模型配置时，应用仍能启动。
- `.env.example` 只放变量名和无敏感性的示例值。
- `.gitignore` 排除 `.env`、虚拟环境、缓存、构建产物、`data/raw/` 和数据库导出文件。

验收命令（在项目根目录执行）：

```powershell
docker compose build backend
docker compose run --rm backend python -m pytest
docker compose up -d backend
```

启动后访问 `http://127.0.0.1:8000/health`，必须得到任务中指定的 JSON。

交给编程助手：

> 完成 TODO 任务 02。使用 Python 3.10 容器、FastAPI、Pydantic v2 和 pytest 创建后端骨架。创建 Dockerfile 和 .dockerignore，实现精确的 /health 响应，补齐 .env.example 和 .gitignore，并在容器内运行测试。不要要求宿主机安装 Python，不要实现数据库和聊天功能。完成后列出改动文件、启动命令和测试结果。

完成记录：文件=`backend/Dockerfile`、`backend/app/main.py`、`backend/app/settings.py`、`backend/tests/test_health.py`；验证=后端镜像构建成功，容器内 pytest 通过，实际访问 `/health` 返回 HTTP 200 和约定 JSON；备注=测试依赖产生一条上游弃用警告，不影响结果。

### 03｜创建本地 MySQL 和 Qdrant

- [x] 创建 `compose.yaml`，让 MySQL 与 Qdrant 可以在本地启动并保存数据。

具体行为：

- 服务名使用 `mysql` 和 `qdrant`。
- MySQL 的库名、用户名和密码从 `.env` 读取；`.env.example` 提供本地开发示例。
- 两个服务都有持久化卷和健康检查。
- 后端新增 `GET /ready`：能连接 MySQL 和 Qdrant 时返回 200；任一服务不可用时返回 503，并在 `checks` 字段分别标出状态。
- 不把密码、数据库文件或卷内容提交到 Git。

验收命令：

```powershell
docker compose config
docker compose up -d
docker compose ps
```

后端、MySQL 与 Qdrant 都必须显示 healthy；访问 `/ready` 必须返回 200。

交给编程助手：

> 完成 TODO 任务 03。增加 compose.yaml，统一管理后端、MySQL、Qdrant、持久化卷和健康检查。扩展后端配置并实现 /ready，逐项检查两个依赖。为 ready 接口写测试，测试中使用依赖替身。最后运行 docker compose config 和容器内后端测试。

完成记录：文件=`compose.yaml`、`backend/app/readiness.py`、`backend/tests/test_readiness.py`；验证=后端、MySQL 与 Qdrant 均为 healthy，容器内后端测试通过，实际访问 `/ready` 返回 HTTP 200；备注=无。

### 04｜创建前端骨架

- [ ] 创建 `frontend/` React + TypeScript 页面和 Node.js 22 Dockerfile，并显示后端健康状态。

页面必须包含：标题“Imm-Agent”、一句科普定位、禁用状态的提问框、后端状态文字。页面加载时请求 `/health`；成功显示“服务正常”，失败显示“服务未连接”。

验收命令（在项目根目录执行）：

```powershell
docker compose build frontend
docker compose run --rm frontend npm run build
docker compose run --rm frontend npm run lint
```

浏览器打开开发地址后能看到页面，后端启停会导致状态文字发生对应变化。

交给编程助手：

> 完成 TODO 任务 04。用 Node.js 22 容器和 Vite 创建 React + TypeScript 前端，实现标题、定位说明、暂时禁用的提问框和后端健康状态。把前端服务加入 Compose，配置开发代理访问后端。不要要求宿主机安装 Node.js 或 npm。保持页面简单，不加入聊天、登录和 UI 组件库。在容器内运行 lint 与 build。

## 第二阶段：从公开来源建立可追溯知识库

### 10｜定义数据库表

- [ ] 用 SQLAlchemy 和 Alembic 创建首版数据表。

必须包含：

- `documents`：资料本身，包含稳定 ID、标题、机构、来源 URL、语言、发布日期、抓取日期、当前状态和创建时间。
- `document_versions`：某次正文版本，包含文档 ID、正文、内容哈希、版本号和创建时间。
- `chunks`：正文片段，包含版本 ID、片段序号、标题路径、文本和字符起止位置。
- `terms` 与 `term_aliases`：规范术语及中英文别名。
- `index_jobs`：索引任务状态、尝试次数和错误信息。

状态只允许 `pending`、`published`、`expired`、`withdrawn`。未知发布日期保存为 `NULL`，不能用抓取日期代替。稳定 ID 使用 UUID；同一文档的内容哈希加唯一约束。

验收：空数据库可以执行 `alembic upgrade head`；再次执行不报错；执行 `alembic downgrade base` 后相关表被移除。

交给编程助手：

> 完成 TODO 任务 10。按卡片中的字段和约束创建 SQLAlchemy 2 模型及首个 Alembic 迁移。补充模型级测试，验证状态约束、内容哈希唯一性和可空发布日期。不要创建聊天表或用户表。

### 11｜导入一份可追溯资料

- [ ] 实现命令 `docker compose run --rm backend python -m app.cli.import_documents <manifest.jsonl>`。

每行输入格式：

```json
{"title":"资料标题","organization":"发布机构","source_url":"https://example.org/a","language":"zh-CN","published_at":"2025-01-01","text_path":"data/raw/a.txt"}
```

具体行为：读取 UTF-8 正文、清除多余空白、计算 SHA-256、写入文档与版本。相同来源和相同哈希再次导入时输出 `skipped`，不能新增重复记录。输入错误只影响当前行，最终输出成功、跳过、失败数量，并以非零退出码表示存在失败。

验收：准备 2 条有效数据和 1 条错误数据；首次导入得到 2 成功、1 失败；再次导入得到 2 跳过、1 失败；数据库中文档没有重复。

交给编程助手：

> 完成 TODO 任务 11。实现 JSONL 清单导入命令、输入校验、正文清洗、SHA-256 去重和逐条错误记录。增加最小样例与 pytest 测试，测试重复导入、缺失文件、非法 URL 和未知日期。原始医学资料不要提交到仓库。

### 12｜审核、发布和撤回资料

- [ ] 实现资料状态命令，并确保只有 `published` 内容可进入检索。

命令：

```powershell
docker compose run --rm backend python -m app.cli.documents publish <document-id>
docker compose run --rm backend python -m app.cli.documents withdraw <document-id>
docker compose run --rm backend python -m app.cli.documents expire <document-id>
```

发布前必须具备标题、机构、来源 URL、正文和内容哈希。撤回或过期时创建索引删除任务。非法状态转换必须失败并解释原因。

验收：待审核资料无法被检索；发布后可检索；撤回后即使 Qdrant 清理尚未完成，查询层也不能把它作为证据。

交给编程助手：

> 完成 TODO 任务 12。实现 publish、withdraw、expire 命令及状态转换规则。发布时校验必填来源信息；撤回和过期时创建索引清理任务。用测试证明查询层始终以 MySQL 当前状态为准。

### 13｜建立首批评测题

- [ ] 创建 `evals/questions.jsonl` 和 `docs/evaluation-format.md`。

先写 20 题：8 题概念或术语、4 题比较、3 题多轮追问、3 题资料无答案、2 题个体化治疗请求。每题必须有 `id`、`question`、`expected_source_ids`、`required_points`、`forbidden_points`、`expected_behavior`。多轮题额外包含 `history`。

验收：创建校验脚本 `docker compose run --rm backend python -m app.cli.validate_evals`；20 题全部能读取且 ID 唯一，引用的资料 ID 都存在。开发阶段可使用其中 15 题，剩余 5 题标记为独立测试题。

交给编程助手：

> 完成 TODO 任务 13。定义评测 JSONL 格式、Pydantic 校验模型和 validate_evals 命令。先根据已发布资料创建 20 道有明确判断条件的题；如果资料不足，创建结构和示例，并在题目位置写 TODO_MISSING_SOURCE，校验命令要把它报告为未就绪。

## 第三阶段：跑通带引用的最小 RAG

### 20｜切分并建立 Qdrant 索引

- [ ] 将已发布文档切分、向量化并写入 Qdrant。

首版切分规则要固定在配置中：按标题和段落切分，过长段落再按句子切分；片段保留 `chunk_id`、`document_id`、`version_id`、标题路径、字符位置和文档状态。Embedding 通过接口封装，测试使用确定性的假模型。

提供命令：

```powershell
docker compose run --rm backend python -m app.cli.reindex --all
docker compose run --rm backend python -m app.cli.reindex --document <document-id>
```

验收：同一版本重复建索引不会产生重复点；更新文档后旧版本不再返回；撤回文档不再返回；能够从任一检索结果追溯到原始正文位置。

交给编程助手：

> 完成 TODO 任务 20。实现可测试的切分器、Embedding 接口、Qdrant 写入和全量/单文档重建命令。点 ID 必须稳定，payload 包含任务要求的追溯字段。生产模型通过环境变量配置，测试不得调用外部 API。

### 21｜实现统一检索接口

- [ ] 实现 `search_knowledge(query, filters, limit)`。

输入要求：`query` 长度 2～500，`limit` 范围 1～20，首版过滤器只支持语言、文档 ID 和发布日期范围。输出每项包含 `chunk_id`、`text`、`title`、`organization`、`source_url`、`published_at`、`score`。

查询 Qdrant 后必须回查 MySQL，只返回当前为 `published` 且版本匹配的片段。没有结果时返回空列表，不抛出业务异常。

验收：用固定问题运行评测，生成 `artifacts/retrieval-baseline.json`，至少记录每题 Top 5 结果、Recall@5 和耗时；测试覆盖空查询、非法 limit、已撤回文档和 Qdrant 超时。

交给编程助手：

> 完成 TODO 任务 21。按卡片定义 search_knowledge 的输入、输出和过滤器；检索后回查 MySQL 的发布状态与版本。增加超时处理和测试，并提供运行 evals/questions.jsonl 的检索评测命令，输出指定基线文件。

### 22｜接入大模型并生成结构化答案

- [ ] 建立可替换的模型适配层，并让回答只依据本次检索片段。

内部响应格式：

```json
{
  "answer": "回答正文",
  "citations": [{"chunk_id": "...", "claim": "该片段支持的结论"}],
  "evidence_status": "sufficient|insufficient|conflicting",
  "follow_up_question": null
}
```

超时只重试 1 次；记录模型名、提示词版本、耗时和 token 用量，日志不能记录完整用户隐私文本。模型引用的 `chunk_id` 必须属于本次检索结果，否则整次响应判为无效。检索为空时不调用模型，直接返回 `insufficient`。

验收：测试覆盖正常回答、空检索、虚构引用、格式错误、模型超时和来源冲突。命令行输入问题后能看到回答以及可解析的来源。

交给编程助手：

> 完成 TODO 任务 22。创建模型 Provider 接口、一个由环境变量配置的实现、版本化提示词和 Pydantic 响应模型。回答仅能使用传入片段，严格校验引用 ID。测试用假 Provider 覆盖卡片列出的 6 种情况，不在测试中调用真实模型。

### 23｜提供聊天 API

- [ ] 实现 `POST /api/chat` 和 `GET /api/sources/{chunk_id}`。

`POST /api/chat` 输入 `message` 和可空 `conversation_id`，输出 `request_id`、`conversation_id`、任务 22 的字段及来源摘要。`GET /api/sources/{chunk_id}` 返回资料标题、机构、日期、来源 URL、原文片段和片段位置。

统一错误格式为 `{"error":{"code":"...","message":"...","request_id":"..."}}`。非法输入返回 422，依赖暂不可用返回 503，找不到来源返回 404。每次请求生成 request ID。

验收：OpenAPI 文档能看到两个接口；接口测试覆盖 200、404、422、503；一次提问返回的每个引用都能通过来源接口展开。

交给编程助手：

> 完成 TODO 任务 23。实现两个 API、请求/响应模型、统一错误结构和 request ID。连接现有检索与回答服务。写接口测试，证明回答引用能通过 sources 接口解析。暂不实现登录、流式输出和反馈。

## 第四阶段：完成网页和多轮对话

### 30｜实现单轮问答页面

- [ ] 前端接入聊天 API。

页面包含提问框、发送按钮、加载状态、回答正文和来源卡片。发送期间禁用重复提交；失败后保留原问题并显示重试按钮。来源卡片显示标题、机构、日期和支持结论，点击后展开原文片段并提供来源链接。

验收：手工完成“输入问题 → 查看回答 → 展开每个引用 → 打开原始链接”；用前端测试覆盖成功、证据不足、服务不可用和重试。

交给编程助手：

> 完成 TODO 任务 30。根据后端 OpenAPI 类型实现单轮问答页面及来源卡片。明确展示加载、证据不足、错误和重试状态。不要加入流式输出、Markdown 任意 HTML、登录或管理后台。运行 lint、测试和 build。

### 31｜保存会话并支持追问

- [ ] 增加 `conversations` 和 `messages` 表，并实现同一会话内的追问。

只保存生成后续回答必需的消息和摘要。后端必须校验会话凭据，不能仅凭可枚举 ID 读取会话。追问中的“它”“前一种疗法”等指代不明确时，返回 `follow_up_question` 要求用户澄清，不能自行猜测。

验收：同一会话可完成至少 3 轮追问；新会话不会继承旧话题；使用另一会话的凭据访问记录得到 404；测试覆盖话题切换和含糊指代。

交给编程助手：

> 完成 TODO 任务 31。增加会话与消息模型、迁移和不可猜测的会话凭据，把必要历史传给回答服务。实现明确的追问与澄清行为，补充隔离、话题切换和含糊指代测试。前端展示当前会话并支持新建会话。

### 32｜收集最小反馈

- [ ] 实现 `POST /api/feedback` 和回答下方的反馈控件。

输入只允许 `request_id`、`rating`（`helpful` 或 `not_helpful`）和最多 500 字的可选备注。同一会话对同一回答重复提交时更新原记录。备注展示前要转义，日志不记录备注正文。

验收：前端能提交和修改反馈；无效 request ID 返回 404；超过长度返回 422；数据库不重复创建同一回答的反馈。

交给编程助手：

> 完成 TODO 任务 32。增加 feedback 数据表、迁移、API 和前端控件，严格限制字段和长度，实现幂等更新。写后端接口测试和前端交互测试。

## 第五阶段：验收并交付首版

### 40｜运行独立评测并修复阻塞问题

- [ ] 固定配置后运行保留的独立测试题，生成 `docs/evaluation-report.md`。

报告必须给出：测试日期、数据版本、Embedding 模型、生成模型、提示词版本、Recall@5、引用可解析率、证据不足题正确行为率、请求成功率、P95 延迟和估算单次成本。逐条列出错误案例、原因和处理决定。

首版最低门槛：引用可解析率 100%；撤回资料命中率 0%；无来源的关键结论为 0；关键权限测试全部通过。其余指标先记录真实基线，再写是否接受及理由。

验收：报告可以由一条命令重新生成；修复问题后再次运行不会覆盖旧报告，而是带时间或版本保存。

交给编程助手：

> 完成 TODO 任务 40。实现独立评测命令并生成版本化报告，计算卡片列出的指标。不要针对独立测试题修改提示词或配置。修复违反最低门槛的问题，并运行相关回归测试；无法达标的项写清原因和下一步。

### 41｜验证安全边界

- [ ] 为以下场景建立自动测试并写入 `docs/security-checks.md`：提示注入要求忽略证据、诱导执行 SQL、诱导抓取任意 URL、个体化治疗选择、输入敏感个人信息、跨会话访问、超长输入、模型和 Qdrant 超时。

固定要求：模型没有数据库管理权限；所有数据库查询参数化；检索工具不能访问任意 URL；日志不出现完整问题、会话凭据、数据库密码或反馈备注。

验收：文档中的每项都对应可运行测试或明确的人工验证步骤，测试结果和日期有记录。

交给编程助手：

> 完成 TODO 任务 41。审查当前实现并为卡片列出的场景补齐有效测试；创建 security-checks.md，把每项风险、预期行为、测试位置和本次结果写清楚。发现问题时直接修复并运行回归。

### 42｜部署、备份和恢复演练

- [ ] 完成可复现部署，并实际验证备份恢复。

需要完成：生产用容器构建、健康检查、环境变量说明、数据库迁移步骤、请求限流、模型超时、结构化日志、MySQL 备份命令、原始资料备份方式、Qdrant 从 MySQL 重建步骤、应用回滚步骤。

在一个干净目录或干净环境中按文档启动，导入样例资料，完成一次问答，再删除测试环境中的派生索引并重建。把执行命令、耗时和结果写入 `docs/release-checklist.md`。

验收：新环境能按文档启动；备份可恢复；索引可重建；已知可用版本可以回滚；密钥不进入镜像和 Git。

交给编程助手：

> 完成 TODO 任务 42。补齐容器部署、配置说明、迁移、限流、日志、备份、恢复、索引重建和回滚。创建 release-checklist.md，并在干净测试环境中实际执行所有步骤，记录结果。只操作测试数据，不删除现有业务数据。

## 首版完成的判断标准

以下条件同时满足时，首版才算完成：

- 用户可以在网页中提问、追问、查看每条引用的原文并提交反馈。
- 只使用状态为 `published` 的当前资料版本；撤回后立即停止作为证据。
- 资料不足时明确说明不足，个体化治疗请求按范围文档处理。
- 所有引用都能映射到本次检索到的真实片段和原始来源。
- 独立评测、安全检查、部署和恢复演练都有可重复执行的记录。

## 首版之后再考虑

只有评测报告出现明确瓶颈时，才新增对应任务：召回不足时实验关键词与向量融合；排序不佳时实验 Reranker；关系类问题确实需要多跳查询时再评估知识图谱；证据充分但模型行为持续不合格时再评估微调；页面等待时间成为主要问题时再实现流式进度。每项实验必须保留旧基线、对比指标和回退方法。
