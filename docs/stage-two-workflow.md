# 第二阶段运行与验收

在仓库根目录执行。先完成 `docs/development-workflow.md` 的 Docker 就绪检查并准备 `.env`。

## 构建与迁移

```text
docker compose config --quiet
docker compose build backend
docker compose up -d mysql qdrant
docker compose run --rm backend alembic upgrade head
docker compose run --rm backend alembic upgrade head
docker compose run --rm backend python -m pytest
docker compose run --rm -e IMM_AGENT_TEST_MYSQL=1 backend python -m pytest
```

`alembic downgrade base` 会删除第二阶段所有资料表，只在没有业务数据的验收库中测试；执行后重新 upgrade。正常更新使用 upgrade，不能对已有资料库执行 downgrade 验收。

后端健康检查不自动迁移数据库；由管理员显式迁移。健康检查仍可在缺少数据库设置时启动。

## 最小导入验收

仓库自带的样例都是虚构非医学文字，不能发布成正式证据：

```text
docker compose run --rm backend python -m app.cli.import_documents data/examples/manifest.jsonl
docker compose run --rm backend python -m app.cli.import_documents data/examples/manifest.jsonl
```

首次输出 success=2、skipped=0、failed=1；第二次 success=0、skipped=2、failed=1。两个命令都应退出 1，因为故意有一条缺失文件。逐行 JSON 包含行号、状态和文档 ID 或错误；最后一行汇总。失败行单独回滚，不影响其他行。

`text_path` 相对容器当前目录 `/app`，不是相对 manifest 所在目录。Compose 将仓库 `data/` 挂载到 `/app/data`；因此样例和原文均使用 `data/...` 路径。绝对路径必须指向容器可见文件。

## 首批权威资料

```text
docker compose run --rm backend python -m app.cli.fetch_sources
docker compose run --rm backend python -m app.cli.import_documents data/raw/nci/manifest.jsonl
docker compose run --rm backend python -m app.cli.documents list
```

抓取流程只访问 NCI 白名单，输出正文保存在 Git 忽略的 `data/raw/`。第一遍导入五篇 success，第二遍五篇 skipped。没有 Qdrant 写入、embedding 或模型调用。

先逐篇 show，并参照 `docs/knowledge-sources.md` 核对内容与来源；确认后分别 publish：

```text
docker compose run --rm backend python -m app.cli.documents show ea12a680-ac69-5485-91d4-7e842a9519c8
docker compose run --rm backend python -m app.cli.documents publish ea12a680-ac69-5485-91d4-7e842a9519c8
docker compose run --rm backend python -m app.cli.documents publish 052681c9-8a2f-5b0d-9719-84117a6516d0
docker compose run --rm backend python -m app.cli.documents publish 1b1ca196-5907-54e8-a953-11af8a5a2965
docker compose run --rm backend python -m app.cli.documents publish e6d89414-330a-5816-8aad-79a5e5940ec3
docker compose run --rm backend python -m app.cli.documents publish 7a87ff27-304f-5b53-ac42-f79be6e81b4f
docker compose run --rm backend python -m app.cli.validate_evals
```

五篇均已发布且正文哈希有效时，评测校验返回 ready=true。当前已发布的资料不要再次运行 publish，重复状态转换会明确失败。

撤回/过期示例（会影响知识库，按维护需要运行）：

```text
docker compose run --rm backend python -m app.cli.documents withdraw <document-id>
docker compose run --rm backend python -m app.cli.documents expire <document-id>
```

两者立即改变 MySQL 状态并增加删除任务，即使 Qdrant 尚未清理，SQL 核验层也过滤其片段。重新发布需重新检查来源。此次任务没有实现任务工作器及完整 search_knowledge，它们属于第三阶段。

## 数据结构

六张表：documents、document_versions、chunks、terms、term_aliases、index_jobs。文档状态有数据库 CHECK 约束；正文哈希在同一文档内唯一；版本号在同一文档内唯一且为正。URL 使用 SHA-256 唯一键以避开 MySQL utf8mb4 长 URL 的索引长度限制，完整 URL 另存 Text。

所有日期时间以 UTC 写入无时区 DATETIME，展示时附 Z；资料发布日期为可空 DATE。只有原文明确发布日期时填写；抓取时间不能代替发布日期。

更新原文创建新版本，并重新进入待审核。查询只接受 published 且版本最新的片段。索引任务和状态修改在同一个数据库事务提交。
