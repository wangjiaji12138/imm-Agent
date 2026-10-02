# 模块依赖与接口边界

本文件是目标约束；目前平铺代码尚未完全满足，见 [迁移任务](../tasks/architecture.md#task-ARCH-02)。不通过新增一批空目录宣称已实现依赖隔离。

## 依赖规则

| 分区 | 可以依赖 | 不应依赖 |
| --- | --- | --- |
| core | 标准库、配置/校验库 | API、业务模块、外部服务客户端 |
| knowledge | 自己的 schema/repository、SQL 基础设施 | Agent、Qdrant SDK、生成模型 |
| retrieval | 自己的 ports/schema、knowledge 公开服务 | Agent、生成模型、直接写知识表 |
| answering | 自己的 ports/schema、已核验 Evidence DTO、core | 检索执行、SQL Session、网页抓取 |
| conversations | 自己的模型/repository/schema、core 与 SQL 基础设施 | Agent、模型供应商、其他模块内部表 |
| feedback | 自己的 repository、会话服务的归属校验接口 | 会话表直接查询、模型调用 |
| agent | retrieval/answering/conversations 公开服务与 DTO | FastAPI Request、SQLAlchemy Session、具体 SDK |
| evaluation | 业务服务公开接口、题集与报告工具 | 改写线上策略或成为线上依赖 |
| infrastructure | core、业务定义的 ports/schema、外部 SDK | 路由与工作流编排 |
| API / CLI | 业务入口、依赖装配、适配实现 | 将核心业务规则写进路由或 argparse |
| frontend features | shared/api、shared/ui、显式传入的回调与数据 | 数据库、模型 SDK、其他 feature 内部状态 |

业务 repository 可以使用 SQLAlchemy；服务到 repository 的关系优先采用具体清晰的方法，不强制给每个数据库表增加抽象接口。Embedding、VectorStore 和模型 Provider 是实际可替换边界，应定义最小 Protocol 并注入假实现测试。

后续 ARCH-02 为这些允许关系添加实际 import 依赖检查；当前架构检查只校验文件、任务覆盖和文档链接，不假装已检测所有依赖倒置。

## 对外调用契约（待实现部分为设计目标）

| 调用方 → 提供方 | 输入 | 输出与约束 | 任务 |
| --- | --- | --- | --- |
| 导入 CLI → knowledge | ImportRecord + UTF-8 正文位置 | success/skipped/failed；每行独立事务 | 11，现有实现 |
| 状态 CLI → knowledge | 文档 ID + publish/withdraw/expire | 状态与索引任务同事务提交 | 12，现有实现 |
| retrieval → knowledge | 候选 chunk ID | 仅当前 published 且版本匹配的 Evidence；文本取 SQL | 12 已有 eligible_chunks；21 封装 DTO |
| indexing → knowledge | 版本 ID + 带位置片段 | 批量持久化与幂等结果；不允许外部写其他知识表 | 20 |
| indexing → knowledge | 文档任务领取/完成/失败 | 任务尝试次数与错误，旧任务不得覆盖新状态 | 20 |
| Agent → retrieval | query、语言/文档/日期过滤、limit | 排序后的 Evidence 数组；无命中为空，依赖超时是错误 | 21 |
| Agent → answering | 问题、确认过的上下文、Evidence | 带引用的 AnswerResult；空证据不调用模型 | 22 |
| API → Agent | 已校验问题 + 已认证上下文 | 六类业务结果或明确的依赖错误 | 23/31 |
| API → knowledge | chunk ID | 已核验来源详情；过期或撤回视为不可作为证据 | 23 |
| API → conversations | 不可猜测凭据 | 当前会话的最小上下文；不匹配返回不存在 | 31 |
| feedback → conversations | 会话身份 + request_id | 是否属于该会话的回答；不得只校验 ID 存在 | 32 |
| evaluation → 业务服务 | 固定数据/模型/提示词版本、题集划分 | 逐题结果、指标和不可覆盖的运行报告 | 21/40 |

业务服务公开返回普通 DTO/Pydantic 对象；不要把 ORM 实例、HTTP Response 或 SDK 响应跨模块传递。现有函数仍返回 ORM 的地方由 ARCH-02 或对应功能卡调整，并补兼容测试。

## 数据归属与事务

- knowledge 统一拥有现有六张表。retrieval 负责计算片段与处理索引任务，通过知识服务公开方法写入；不能独立修改 documents.status。
- conversations 拥有会话和消息；feedback 拥有反馈。跨模块只传稳定 ID 或校验后的身份对象。
- infrastructure.orm 是唯一 Base；模型注册只在迁移入口/装配层统一完成。移动 Python 文件不改变表名、约束、UUID 或迁移版本。
- 导入每行一个事务；状态与索引任务在同一事务提交。模型和网络调用不放进持锁的数据库长事务。
- 在线检索通过新的短事务核验状态与版本，避免长期保留旧快照；向量 payload 的 published 字段不能替代 SQL 判断。
- 同一文档索引任务串行处理，执行前重新核对版本和状态；撤回后的过时 upsert 不得使内容重新可检索。
- 数据库 Session 在 API/CLI 边界建立并明确关闭；禁止在模块 import 时连接数据库或调用模型。

## 装配和错误

`main.py` 保留应用创建；`api/dependencies.py` 装配在线服务；每个 CLI 的 main 装配离线服务。模型名称、地址、超时和凭据由配置注入，不在业务代码写死。

`answer/clarify/insufficient/refuse/out_of_scope/emergency` 是业务结果。SQL/Qdrant/模型不可用是依赖错误，由 API 映射为统一错误响应；不得把网络故障伪装成“资料不足”。模型引用越界时视为无效生成，不把未经核验的文本返回为正式回答。

日志仅记录请求 ID、候选 ID、版本、耗时和用量等白名单字段，排除完整问题、会话凭据、数据库密码和反馈备注。
