# 仓库维护脚本 TODO

任务：[ARCH-01](../docs/tasks/architecture.md#task-ARCH-01)、[ARCH-02](../docs/tasks/architecture.md#task-ARCH-02)、[42](../docs/tasks/phase-05-release.md#task-42)。

- check_layout.py：检查架构入口/占位、任务 ID 与本地 Markdown 链接；在容器中运行，只读仓库。
- 实际 import 边界检查位于 backend/tests/test_architecture.py，随 pytest 运行；覆盖真实应用及违规示例。
- 业务运维命令统一放 app/cli/backup.py、restore.py，不在本目录复制第二份业务实现。

从仓库根目录执行（PowerShell/zsh/Bash）：

```text
docker compose run --rm --no-deps -v ".:/workspace:ro" -w /workspace backend python scripts/check_layout.py
```
