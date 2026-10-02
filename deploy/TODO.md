# 部署与恢复 TODO

唯一验收卡：[42](../docs/tasks/phase-05-release.md#task-42)。配置占位：[compose.production.yaml.example](compose.production.yaml.example)，当前不能作为部署命令输入。

1. 优先实现 CLI backup/restore：暂停资料维护写入或建立一致快照，导出 MySQL 和原文，记录哈希、Git 提交/工作区状态、schema 版本、文档/版本数量和发布状态；密钥单独配置。
2. 恢复默认要求显式目标空库。备份中的文件路径必须校验，禁止路径穿越；不得默认覆盖已有业务库。
3. 新环境按清单重建依赖，核对数据；Qdrant 重建需等待任务 20，记录 embedding 模型、维度、版本和切分配置。
4. 补生产镜像、运行配置、健康检查、限流、超时与结构化日志；开发 compose.yaml 继续作为开发入口。
5. 明确应用回滚与数据库兼容规则，执行隔离环境的完整恢复与索引重建演练。
6. 在 [release-checklist](../docs/release-checklist.md) 填入实际命令、耗时与结果，不将模板当验收记录。

不预建不可运行的备份 shell/PowerShell 两套脚本；核心流程用容器内 Python CLI，跨平台命令由工作流文档说明。
