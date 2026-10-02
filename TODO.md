# Imm-Agent 开发任务导航

这是开发总入口。任务按阶段验收，代码按业务能力分区；二者用稳定任务编号关联。

**状态维护规则：** `docs/tasks/` 中每张任务卡的勾选及完成记录是唯一来源。本文件和模块 `TODO.md` 只负责导航，不能另行复制一套完成状态。完成任务时同时更新实际实现、相关文档和架构目录清单。

## 当前进度与下一步

第一阶段 01—04、第二阶段 10—13、架构准备及第三阶段任务 20 已完成；5 篇 NCI 资料的 180 个真实向量点已通过重复重建与原文追溯核验。下一步为任务 21（统一检索接口与基线）。其余任务尚未完成，目录占位不代表功能上线。

推荐顺序：ARCH-01 目录设计 → ARCH-02 迁移现有模块 → 20 索引 → 21 检索 → 22 生成与分流 → 23 API → 30 页面 → 31 会话 → 32 反馈 → 40/41/42 交付验收。42 中的跨设备备份恢复可先实施，完整索引重建演练需等 20 完成。

## 按阶段找任务（唯一验收卡）

| 阶段 | 任务 | 卡片入口 |
| --- | --- | --- |
| 架构准备 | ARCH-01 目录设计；ARCH-02 既有代码迁移 | [架构任务](docs/tasks/architecture.md) |
| 一：可启动应用 | 01 范围；02 后端；03 数据服务；04 前端 | [第一阶段](docs/tasks/phase-01-foundation.md) |
| 二：可追溯知识库 | 10 表结构；11 导入；12 状态；13 评测题 | [第二阶段](docs/tasks/phase-02-knowledge.md) |
| 三：最小 RAG | 20 索引；21 检索；22 生成；23 API | [第三阶段](docs/tasks/phase-03-rag.md) |
| 四：网页与多轮 | 30 问答页；31 会话；32 反馈 | [第四阶段](docs/tasks/phase-04-conversation.md) |
| 五：首版交付 | 40 独立评测；41 安全；42 部署恢复 | [第五阶段](docs/tasks/phase-05-release.md) |

## 按功能找代码与模块 TODO

| 功能分区 | 模块入口 | 对应任务 |
| --- | --- | --- |
| HTTP 路由与依赖装配 | [api](backend/app/api/TODO.md) | 02/03/23/32/42、ARCH-02 |
| 配置、错误与日志 | [core](backend/app/core/TODO.md) | 02/41/42、ARCH-02 |
| SQL、向量与模型适配 | [infrastructure](backend/app/infrastructure/TODO.md) | 10/20/22/42、ARCH-02 |
| 资料治理与证据状态 | [knowledge](backend/app/modules/knowledge/TODO.md) | 10/11/12、ARCH-02 |
| 切分、索引与检索 | [retrieval](backend/app/modules/retrieval/TODO.md) | 20/21 |
| 生成与引用校验 | [answering](backend/app/modules/answering/TODO.md) | 22 |
| 问题分类与工作流 | [agent](backend/app/modules/agent/TODO.md) | 22/23/31/41 |
| 会话与必要历史 | [conversations](backend/app/modules/conversations/TODO.md) | 31/41 |
| 回答反馈 | [feedback](backend/app/modules/feedback/TODO.md) | 32/41 |
| 评测运行与指标 | [evaluation](backend/app/modules/evaluation/TODO.md) | 13/21/40、ARCH-02 |
| 离线管理命令 | [CLI](backend/app/cli/TODO.md) | 11/12/13/20/21/22/40/42 |
| 前端功能与公共代码 | [frontend](frontend/TODO.md) | 04/30/31/32 |
| 测试与端到端验收 | [backend tests](backend/tests/TODO.md)、[frontend tests](frontend/tests/TODO.md)、[e2e](tests/e2e/TODO.md) | 各功能卡与 40/41/42 |
| 评测题资产 | [evals](evals/TODO.md) | 13/21/40 |
| 资料、版本与备份 | [data](data/TODO.md) | 11/12/42 |
| 部署与恢复 | [deploy](deploy/TODO.md) | 42 |
| 持续集成 | [CI](.github/TODO.md) | 41/42 |
| 仓库维护脚本 | [scripts](scripts/TODO.md) | ARCH-01/ARCH-02/42 |

## 开始一张任务卡

1. 先读 [README](README.md)、[架构导航](docs/architecture/README.md) 和所选卡片；新设备先完成 [开发环境](docs/development-workflow.md)。
2. 根据 [目录职责](docs/architecture/directory-map.md)、[模块边界](docs/architecture/boundaries.md) 和对应模块 TODO 确认文件位置与允许依赖。
3. 只实现卡片范围；跨模块工作在同一卡片中验收。原文仅放 `data/raw/`，凭据不进入 Git。
4. Python/Node 依赖和测试在容器中运行；不要用占位函数、占位测试或模拟页面冒充已完成的功能。
5. 完成卡片指定验收后，勾选该卡片，追加记录，并更新 [layout.json](docs/architecture/layout.json) 的文件状态。

完成记录格式：

```text
完成记录：文件=<主要文件>；验证=<命令与实际结果>；备注=<遗留问题或无>
```

范围、响应分类和拒答规则以 [mvp-scope](docs/mvp-scope.md) 为准；已有来源和第二阶段操作分别见 [来源说明](docs/knowledge-sources.md) 与 [知识库工作流](docs/stage-two-workflow.md)。

## 首版完成的判断标准

以下条件同时满足时，首版才算完成：

- 用户可以在网页中提问、追问、查看每条引用的原文并提交反馈。
- 只使用状态为 `published` 的当前资料版本；撤回后立即停止作为证据。
- 资料不足时明确说明不足，个体化治疗请求按范围文档处理。
- 所有引用都能映射到本次检索到的真实片段和原始来源。
- 独立评测、安全检查、部署和恢复演练都有可重复执行的记录。

## 首版之后再考虑

只有评测报告出现明确瓶颈时，才新增对应任务：召回不足时实验关键词与向量融合；排序不佳时实验 Reranker；关系类问题确实需要多跳查询时再评估知识图谱；证据充分但模型行为持续不合格时再评估微调；页面等待时间成为主要问题时再实现流式进度。每项实验必须保留旧基线、对比指标和回退方法。
