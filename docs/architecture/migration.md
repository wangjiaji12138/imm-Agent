# 现有实现与目标目录

本次完成设计和占位，不搬动已验证运行代码。[ARCH-02](../tasks/architecture.md#task-ARCH-02) 才执行下面的迁移。未来 RAG 模块尚无旧实现可迁，不应复制当前代码形成两套权威逻辑。

| 当前实际入口 | 目标位置 | 兼容要求 |
| --- | --- | --- |
| backend/app/settings.py | core/settings.py | 环境变量名、get_settings 缓存和健康检查启动条件不变 |
| backend/app/database.py | infrastructure/database.py | 保持惰性连接；逐步显式管理 Session/Engine 生命周期 |
| backend/app/models.py 的 Base | infrastructure/orm.py | 唯一 metadata，Alembic 注册所有模型 |
| backend/app/models.py 的六表 | modules/knowledge/models.py | 表名、外键、约束和既有 0001 迁移不改 |
| knowledge.py 的清洗/哈希/ID | modules/knowledge/text.py | 哈希、UUID、正文字符位置必须保持一致 |
| knowledge.py 的 ImportRecord | modules/knowledge/schemas.py | JSONL 格式和未知日期行为不变 |
| knowledge.py 的 SQL 查询 | modules/knowledge/repository.py | 明确事务归属，外部模块最终只看到 DTO |
| knowledge.py 的导入/状态 | modules/knowledge/service.py | 同事务写状态与任务；重复导入不创建版本 |
| knowledge.py 的 eligible_chunks | modules/knowledge/evidence.py | SQL 当前状态和版本核验保持拒绝失效证据 |
| cli/fetch_sources.py 的抓取函数 | modules/knowledge/acquisition.py | CLI 参数与白名单不变；CLI 仅组装与退出码 |
| evaluation.py 的 Pydantic 模型 | modules/evaluation/schemas.py | 20 题规则、dev/test 和行为分类不变 |
| evaluation.py 的校验执行 | modules/evaluation/dataset.py | validate_evals 的输出与退出码不变 |
| main.py 的健康路由 | api/routes/health.py | /health、/ready 契约和测试依赖覆盖点不变 |
| readiness.py | infrastructure/readiness.py | 超时和不可用行为不变 |
| frontend/src/App.tsx | features/* + shared/* | 随任务 30—32 提取；当前草稿、健康状态、布局不因占位改变 |

## 迁移步骤

1. 提取纯函数/schema，保留旧模块的显式 re-export。禁止 `import *` 和双向依赖。
2. 迁移 Base 与 ORM，再移动 repository/service；用 Alembic metadata 对比证明没有表结构漂移。不要通过 downgrade/up 删除现有数据库。
3. 迁移采集与评测实现，CLI 名称和 manifest 路径语义保持不变。
4. 迁移健康路由，保留当前 TestClient 的依赖覆盖能力；main 仅装配。
5. 更新内部 import；旧入口只转发，不包含第二份实现。明确兼容入口移除条件：文档、CLI、测试及外部调用均已迁完。
6. 在任务 30—32 中逐步提取前端功能，不提前更改页面交互。

## 验收边界

沿用当前容器回归，启用真实 MySQL 测试；已有资料 UUID、正文哈希、文档状态、版本数均保持。用只读对比验证数据，不对现有资料库执行迁移回滚。新增 import 约束检查，证明 Agent 不依赖 FastAPI/SQLAlchemy/厂商 SDK；只验证真实存在的实现，不针对空壳测试。
