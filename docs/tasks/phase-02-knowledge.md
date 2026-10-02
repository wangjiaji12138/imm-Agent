# 第二阶段任务卡

[返回任务总入口](../../TODO.md) · [架构导航](../architecture/README.md)

这里是本阶段任务状态、验收条件和完成记录的唯一维护位置。原任务卡和历史完成记录保留；卡片中路径表示仓库根目录下的位置。未来实现位置以架构目录表为准，历史记录不改写。

## 第二阶段：从公开来源建立可追溯知识库

<a id="task-10"></a>

### 10｜定义数据库表

- [x] 用 SQLAlchemy 和 Alembic 创建首版数据表。

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

完成记录：文件=`backend/app/models.py`、`backend/app/database.py`、`backend/migrations/`；验证=MySQL 8.4 上 upgrade head、再次 upgrade、空库 downgrade base、确认六表移除、重新 upgrade 全部通过；容器内测试含真实 MySQL 状态约束和哈希唯一性验证通过；备注=无。

<a id="task-11"></a>

### 11｜导入一份可追溯资料

- [x] 实现命令 `docker compose run --rm backend python -m app.cli.import_documents <manifest.jsonl>`。

每行输入格式：

```json
{"title":"资料标题","organization":"发布机构","source_url":"https://example.org/a","language":"zh-CN","published_at":"2025-01-01","text_path":"data/raw/a.txt"}
```

具体行为：读取 UTF-8 正文、清除多余空白、计算 SHA-256、写入文档与版本。相同来源和相同哈希再次导入时输出 `skipped`，不能新增重复记录。输入错误只影响当前行，最终输出成功、跳过、失败数量，并以非零退出码表示存在失败。

验收：准备 2 条有效数据和 1 条错误数据；首次导入得到 2 成功、1 失败；再次导入得到 2 跳过、1 失败；数据库中文档没有重复。

交给编程助手：

> 完成 TODO 任务 11。实现 JSONL 清单导入命令、输入校验、正文清洗、SHA-256 去重和逐条错误记录。增加最小样例与 pytest 测试，测试重复导入、缺失文件、非法 URL 和未知日期。原始医学资料不要提交到仓库。

完成记录：文件=`backend/app/knowledge.py`、`backend/app/cli/import_documents.py`、`backend/app/cli/fetch_sources.py`、`data/examples/`、`data/sources.json`；验证=样例首次 2 success/1 failed、再次 2 skipped/1 failed，均退出 1；NCI 五篇首次 5 success、再次 5 skipped；UTF-8 错误行、非法 URL、缺失文件、未知日期均有测试；备注=原始正文仅存 Git 忽略的 data/raw/，虚构验收记录已清理。

<a id="task-12"></a>

### 12｜审核、发布和撤回资料

- [x] 实现资料状态命令，并确保只有 `published` 内容可进入检索。

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

完成记录：文件=`backend/app/cli/documents.py`、`backend/app/knowledge.py`、`backend/tests/test_publication.py`、`backend/tests/test_mysql_integration.py`；验证=五篇 NCI 资料已发布；测试证明 pending、撤回、过期和旧版本不进入 SQL 证据结果，删除任务未处理时仍过滤；备注=第二阶段完成检索前 SQL 核验层，Qdrant 切分/写入/检索与工作器按第三阶段实现。

<a id="task-13"></a>

### 13｜建立首批评测题

- [x] 创建 `evals/questions.jsonl` 和 `docs/evaluation-format.md`。

先写 20 题：8 题概念或术语、4 题比较、3 题多轮追问、3 题资料无答案、2 题个体化治疗请求。每题必须有 `id`、`question`、`expected_source_ids`、`required_points`、`forbidden_points`、`expected_behavior`。多轮题额外包含 `history`。

验收：创建校验脚本 `docker compose run --rm backend python -m app.cli.validate_evals`；20 题全部能读取且 ID 唯一，引用的资料 ID 都存在。开发阶段可使用其中 15 题，剩余 5 题标记为独立测试题。

交给编程助手：

> 完成 TODO 任务 13。定义评测 JSONL 格式、Pydantic 校验模型和 validate_evals 命令。先根据已发布资料创建 20 道有明确判断条件的题；如果资料不足，创建结构和示例，并在题目位置写 TODO_MISSING_SOURCE，校验命令要把它报告为未就绪。

完成记录：文件=`evals/questions.jsonl`、`backend/app/evaluation.py`、`backend/app/cli/validate_evals.py`、`docs/evaluation-format.md`；验证=20 题、15 dev/5 test，资料 pending 时 ready=false，五篇发布后 ready=true；容器内全套测试 34 passed（启用真实 MySQL 集成测试）；备注=保留 1 条上游 TestClient 弃用警告；评测格式与来源验证不等于医学专家审核。

