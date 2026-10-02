# 第二阶段资料来源与审核规则

## 来源选择

首批正文使用美国国家癌症研究所 NCI（NIH 下属机构）的患者教育页面。已核查 [NCI 复用政策](https://www.cancer.gov/policies/copyright-reuse)：未另行标注的文字可以复用，须署名并链接原始标题；图像可能另有版权。因此采集仅提取正文、标题和列表，去掉图片、图注、视频、导航、推荐卡片和页脚。

[NCI robots.txt](https://www.cancer.gov/robots.txt) 在首次核查时没有禁止这些路径；采集命令每次重新读取并检查，串行抓取，间隔至少一秒，不进行全站爬取，不跟随重定向。页面结构不符或请求失败即停止，不自动发布。

同时核查了下列权威网站，保留为扩充目录，未复制其完整正文：

| 机构 | 官方入口 | 使用方式 |
| --- | --- | --- |
| Cancer Research Institute (CRI) | [Immunotherapy Basics](https://www.cancerresearch.org/what-is-immunotherapy) | 专注癌症免疫治疗研究；新增正文前单独核查复用条款与资料时效 |
| American Cancer Society (ACS) | [What Is Immunotherapy?](https://www.cancer.org/cancer/treatment-types/immunotherapy.html) | 癌症患者教育补充来源；新增正文前单独核查复用条款 |

不因机构权威就认定网页包含最新获批清单，也不把美国监管状态直接适用于中国。首批仅用于基础概念、机制及资料内比较，不能据此声称已覆盖最新临床进展。

## 首批来源和稳定 ID

机器可读目录见 `data/sources.json`。文档 UUID v5 基于规范化来源 URL，跨数据库重建后保持一致；不使用随机导入 ID 作为评测引用。URL 只规范化协议/域名及移除 fragment，保留路径与 query，避免误合并不同资料。

| 简称 | 文档 ID | 原标题及入口 | 页面标注日期 |
| --- | --- | --- | --- |
| 总览 | `ea12a680-ac69-5485-91d4-7e842a9519c8` | [Immunotherapy to Treat Cancer](https://www.cancer.gov/about-cancer/treatment/types/immunotherapy) | Updated 2019-09-24 |
| 检查点 | `052681c9-8a2f-5b0d-9719-84117a6516d0` | [Immune Checkpoint Inhibitors](https://www.cancer.gov/about-cancer/treatment/types/immunotherapy/checkpoint-inhibitors) | Reviewed 2022-04-07 |
| T 细胞 | `1b1ca196-5907-54e8-a953-11af8a5a2965` | [T-cell Transfer Therapy](https://www.cancer.gov/about-cancer/treatment/types/immunotherapy/t-cell-transfer-therapy) | Updated 2024-08-05 |
| 单抗 | `e6d89414-330a-5816-8aad-79a5e5940ec3` | [Monoclonal Antibodies](https://www.cancer.gov/about-cancer/treatment/types/immunotherapy/monoclonal-antibodies) | Posted 2019-09-24 |
| 疫苗 | `7a87ff27-304f-5b53-ac42-f79be6e81b4f` | [Cancer Treatment Vaccines](https://www.cancer.gov/about-cancer/treatment/types/immunotherapy/cancer-treatment-vaccines) | Posted 2019-09-24 |

仅 `Posted` 进入 `published_at`。仅有 `Updated` 或 `Reviewed` 时发布日期为 NULL；这些页面日期保留在原始快照的 JSON 元数据和来源目录中。`fetched_at` 独立记录实际抓取时间（UTC），不充当发布日期。

## 采集与溯源

运行 `python -m app.cli.fetch_sources` 只下载代码白名单内的五个页面。输出放在被 Git 忽略的 `data/raw/nci/`：

- 以 HTML 哈希命名的原始 `.html`、提取 `.txt`、来源 `.json`。
- JSON 保存来源 URL、机构署名、抓取时间、页面日期、HTML 和清洗正文 SHA-256、提取方式、复用政策入口。
- `manifest.jsonl` 是本次完整抓取的导入清单，只有五篇全部成功才原子替换。抓取失败不会覆盖上次完整清单。
- 正文快照不提交 Git。`data/sources.json` 仅存元数据；`data/examples/` 只有虚构的非医学测试文字。

未翻译英文原文，中文评测题是开发者编写的检验条件，不是 NCI 官方译文，也不是经临床验证的标准答案。

## 发布审核

导入后为 pending。使用 `documents show <id>` 查看来源、正文、日期和哈希，核对原始网页，确认正文提取完整且判断条件有支持，再显式 publish。

本次基础审核覆盖五篇正文的标题、主体章节、否定和限定表述、页脚剔除、日期类型、内容哈希及 20 题证据映射。发布只表示允许作为本项目一般科普的检索材料，不表示医学专家背书。若将评测用于上线决策，需医学领域人员另行审核判断条件。

重复导入同一来源和同一正文哈希输出 skipped，不修改元数据或状态；历史正文再次出现也 skipped，不自动回滚版本。若正文变化，增加版本并回到 pending；若旧状态为 published，同时排入删除任务。元数据单独修订不通过重复正文导入覆盖，需另行审核维护流程。

## 生命周期和检索一致性

| 命令 | 允许的原状态 | 目标 | 同事务索引任务 |
| --- | --- | --- | --- |
| publish | pending / expired / withdrawn | published | upsert 最新版本 |
| withdraw | pending / published / expired | withdrawn | delete 最新版本 |
| expire | published | expired | delete 最新版本 |

重复执行同一状态转换会失败并说明原因。重新 publish 是一次明确重新审核。发布校验标题、机构、HTTP(S) URL、正文及 SHA-256；事务失败时状态与任务一起回滚。

索引任务自身状态为 pending/running/succeeded/failed，与文档四种状态不同。第二阶段仅创建任务；第三阶段实现工作器和真实向量检索。工作器应按文档串行处理，执行前核对 MySQL 当前状态和版本，过时任务不能重新激活旧内容。

`eligible_chunks(session, candidate_ids)` 是后续检索必须调用的 SQL 核验层：只返回当前 published 文档的最新版本，正文读取 SQL，不信任向量 payload 的状态或正文。每次检索使用新的短事务，避免 MySQL REPEATABLE READ 长事务持有旧快照。第二阶段通过模拟残留候选 ID 验证这条规则，不声称已完成第三阶段的向量检索。

字符位置使用清洗正文的 Unicode 字符下标，左闭右开 `[char_start, char_end)`；不是 HTML 字节位置。版本正文不可直接覆盖，未来片段必须满足 `text == version.text[start:end]`。
