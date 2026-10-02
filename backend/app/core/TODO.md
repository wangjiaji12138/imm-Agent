# 配置与共用错误 TODO

任务入口：[02](../../../docs/tasks/phase-01-foundation.md#task-02)、[41](../../../docs/tasks/phase-05-release.md#task-41)、[42](../../../docs/tasks/phase-05-release.md#task-42)、[ARCH-02](../../../docs/tasks/architecture.md#task-ARCH-02)。任务卡是完成状态的唯一来源。

| 计划文件 | 职责 |
| --- | --- |
| [settings.py](settings.py) | 现有配置类迁入，保留环境变量名和缓存行为 |
| [errors.py](errors.py) | 业务/依赖错误类型，不依赖 HTTP 或厂商 SDK |
| [logging.py](logging.py) | 结构化白名单日志，排除问题全文、凭据和反馈备注 |

实现顺序与禁止依赖见 [模块边界](../../../docs/architecture/boundaries.md)。settings.py 已实现；errors.py 与 logging.py 仍为占位。
