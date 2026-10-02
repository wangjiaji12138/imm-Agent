# 持续集成 TODO

任务：[41](../docs/tasks/phase-05-release.md#task-41)、[42](../docs/tasks/phase-05-release.md#task-42)。[ci.yml.example](workflows/ci.yml.example) 只是文件落点，不会被 GitHub Actions 执行。

实现后检查：架构/文档、后端离线测试、前端 lint/build/test；集成任务启动隔离 MySQL/Qdrant。恢复演练使用虚构数据和临时目录；日志/构建产物不包含凭据与原始医学资料。前端 test 脚本尚未实现，不能先添加始终失败或跳过却报绿的工作流。
