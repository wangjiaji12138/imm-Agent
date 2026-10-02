# 数据资产 TODO

任务：[11](../docs/tasks/phase-02-knowledge.md#task-11)、[12](../docs/tasks/phase-02-knowledge.md#task-12)、[42](../docs/tasks/phase-05-release.md#task-42)。规则见 [数据生命周期](../docs/architecture/data-lifecycle.md)。

| 路径 | 用途 | Git |
| --- | --- | --- |
| sources.json | 权威来源 URL、机构和页面日期 | 提交 |
| examples/ | 最小非医学导入样例 | 提交 |
| raw/ | 原始 HTML、正文、抓取清单、来源哈希 | 忽略 |
| backups/ | 后续 backup 命令生成的 SQL、原文与版本清单 | 忽略，运行时创建 |

下一步在 42 中实现：可重现数据版本清单、MySQL 一致导出、原文打包、哈希校验、空库恢复与资料状态核对。现有 data/raw/ 下的手工 SQL 备份继续保留；新约定不自动迁走已有文件。

不把原始医学正文、真实病例、模型密钥或数据库密码提交 Git。公开来源目录不等于完整备份，重新抓取网页不能保证还原同一版本。
