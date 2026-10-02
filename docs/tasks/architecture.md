# 架构与模块迁移任务

[返回任务总入口](../../TODO.md) · [架构导航](../architecture/README.md)

<a id="task-ARCH-01"></a>

## ARCH-01｜整体目录设计和占位

- [x] 完成功能分区、模块边界、文件占位、阶段任务卡及架构检查。

范围：backend 的业务模块/API/基础设施、frontend 的 features/shared、评测、测试、资料、运维和 CI 落点。保留原 01—42 的任务内容、状态及完成记录，任务卡是状态唯一来源；模块 TODO 只链接卡片并解释文件职责。

验收：所有计划路径存在并标注未实现；所有原任务均可从根入口与模块导航到达；未实现 CLI 非零退出；文档链接有效；既有容器回归通过；没有新增可用但虚假的 HTTP 接口或页面功能。

完成记录：文件=`docs/architecture/`、`docs/tasks/`、各模块 `TODO.md` 与占位、`scripts/check_layout.py`；验证=85 个架构条目、20 张任务卡、392 个本地链接检查通过；原 18 张验收卡及完成记录逐字核对保留；6 个占位 CLI 均非零退出且说明未实现；原应用未导入规划模块或注册占位 API；容器内后端 34 passed（含真实 MySQL）、前端 build/lint 通过；备注=保留 1 条上游 TestClient 弃用警告，真实模块迁移另见 ARCH-02。

<a id="task-ARCH-02"></a>

## ARCH-02｜按模块迁移已实现代码

- [x] 按迁移表归位第一、二阶段逻辑，并建立真实依赖检查。

前置：ARCH-01。建议在任务 20 前完成，按“纯函数/schema → ORM/仓储/事务 → 采集/评测 → 路由”的顺序逐步迁移，每步通过回归再继续。

执行规范见 [迁移表](../architecture/migration.md) 与 [依赖边界](../architecture/boundaries.md)。按用户本次要求，不兼容旧 Python 接口：更新全部内部导入后删除旧模块，不保留显式转发；原始数据、配置、表结构和历史迁移不变。

验收：既有 CLI 参数、输出与退出码保持；health/ready 契约保持；34 项既有测试及新增必要的依赖/DTO 检查通过；MySQL metadata 无漂移；已有五篇资料 ID/哈希/状态不变；后端新业务代码不再扩展旧平铺文件。

交给编程助手：

> 执行 ARCH-02。先读架构导航、迁移表和现有实现，按上述顺序逐步提取代码，不新增第三阶段功能。删除旧导入入口，统一更新调用方并补充实际 import 边界检查，使用现有测试验证行为不变。不要重建或清空资料库，不修改已执行迁移。验收后更新目录清单中的 implemented/planned 状态及完成记录。

完成记录：文件=`backend/app/core/`、`infrastructure/`、`modules/knowledge/`、`modules/evaluation/`、`api/`、`main.py`、CLI、`backend/migrations/env.py`、测试及架构文档；验证=迁移前和纯函数/ORM 提取后各 34 passed，最终镜像 `docker compose run --rm -e IMM_AGENT_TEST_MYSQL=1 backend python -m pytest` 为 48 passed，含 MySQL metadata 无漂移、静态 import 边界/循环依赖、只读 DTO 与事务回滚检查；六张表全量行摘要与迁移前一致（5 documents、5 versions、5 index_jobs，其余三表为空），10 组 CLI 输出及退出码一致；后端重新构建启动后四服务 healthy，实际 /health 与 /ready 契约通过；81 个架构条目、20 张任务卡及本地链接检查通过，git diff --check 通过；备注=按用户要求删除六个旧 Python 模块，不保留兼容入口；保留用户中文注释；历史迁移和原始资料未改动；1 条既有上游 TestClient 弃用警告；下一步为任务 20。
