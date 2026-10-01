# 审查日志

---

## 2026-10-01 15:39

### 变更
- `.env.example` — 增加 Compose 所需的本地 MySQL root 密码变量。
- `.env` — 创建被 Git 忽略的容器及后端本地开发配置。
- `compose.yaml` — 增加带持久化卷和健康检查的 MySQL 8.4、Qdrant 1.15.5 服务。
- `backend/pyproject.toml` — 增加运行时 HTTP 和 MySQL 客户端依赖。
- `backend/app/settings.py` — 增加经过校验的 MySQL、Qdrant 连接配置。
- `backend/app/readiness.py` — 增加短超时的 MySQL、Qdrant 就绪检查。
- `backend/app/main.py` — 增加 `GET /ready` 接口及 HTTP 503 行为。
- `backend/tests/test_readiness.py` — 增加依赖可用及不可用场景测试。
- `TODO.md` — 标记任务 02、03 完成并记录验证结果。

### 原因
- 为从零实现项目安装并配置完整的本地开发环境及所需容器。

### 验证
- `python --version` → `Python 3.10.11`。
- `node --version` → `v22.23.2`。
- `docker compose ps` → MySQL、Qdrant 均显示 `healthy`。
- `cd backend; .\.venv\Scripts\python.exe -m pytest` → `3 passed`。
- 启动 Uvicorn 并请求 `http://127.0.0.1:8000/ready` → HTTP 200，两项检查均为 `ok`。

### 未处理
- 任务 04 尚未开始，因此未初始化前端依赖。
- 任务 22 尚未开始，因此未配置模型服务依赖。

---

## 2026-10-01 15:40

### 变更
- 当前用户 PowerShell 执行策略 — 设为 `RemoteSigned`，使已安装的 `npm.ps1` 可以运行。

### 原因
- 使文档中的 `npm run ...` 命令可以直接在用户的 PowerShell 开发终端中运行。

### 验证
- `npm --version` → 返回 `10.9.8`，没有执行策略错误。

### 未处理
- 未修改计算机级和策略管理的 PowerShell 执行策略范围。

---

## 2026-10-01 15:47

### 变更
- `backend/Dockerfile` — 增加 Python 3.10 后端镜像，并在镜像中安装运行和测试依赖。
- `backend/.dockerignore` — 从镜像构建上下文中排除本地 Python 产物。
- `compose.yaml` — 增加后端服务、容器内依赖地址、启动顺序、端口和健康检查。
- `TODO.md` — 将 Docker 设为后端及后续前端命令的必需运行环境。
- `README.md` — 说明宿主机只需要 Git、WSL 2 和 Docker Desktop。
- 当前用户 PowerShell 执行策略 — 恢复为 `Undefined`；项目流程不再使用宿主机 npm。

### 原因
- 修正开发环境，使 Python、Node.js、项目包、MySQL 和 Qdrant 均由 Docker 提供，无需安装到 Windows。

### 验证
- `docker compose build backend` → 成功构建 `imm-agent-backend` 镜像。
- `docker compose run --rm backend python -m pytest` → `3 passed`。
- `docker compose up -d backend` 和 `docker compose ps` → 后端、MySQL、Qdrant 均显示 `healthy`。
- 请求 `http://127.0.0.1:8000/ready` → HTTP 200，MySQL、Qdrant 均为 `ok`。

### 未处理
- 宿主机 Python 3.10、Node.js 22 当时仍保留，因为用户尚未明确要求卸载软件。
- 自动命令审查拒绝递归删除 `backend/.venv`；该目录继续被 Git 和 Docker 构建排除。

---

## 2026-10-01 15:50

### 变更
- Windows 用户环境 — 卸载误装的 Python 3.10.11 运行时。
- Windows 用户环境 — 卸载误装的 Node.js 22.23.2 运行时。

### 原因
- 落实用户关于项目运行时和依赖全部由 Docker 容器提供的要求。

### 验证
- `winget list --id Python.Python.3.10 --exact` → 找不到已安装的软件包。
- `winget list --id OpenJS.NodeJS.22 --exact` → 找不到已安装的软件包。
- `docker compose run --rm backend python -m pytest` → 不使用宿主机 Python 时仍为 `3 passed`。
- `docker compose ps` → 后端、MySQL、Qdrant 均显示 `healthy`。

### 未处理
- 保留 WSL 2 和 Docker Desktop，因为容器运行需要它们。
- 保留 Windows Store 的 `python.exe` 应用执行别名；该别名不是 Python 运行时。
- 自动命令审查再次拒绝递归删除 `backend/.venv`；该目录继续被 Git 和 Docker 构建排除。

---

## 2026-10-01 15:51

### 变更
- `REVIEW.md` — 将标题、章节名称及全部历史记录翻译为中文。

### 原因
- 按用户要求统一使用中文维护审查日志。

### 验证
- 打开 `REVIEW.md` → 标题、章节和说明文字均为中文，命令、路径和技术标识保持原样。

### 未处理
- 未改变历史记录的时间、顺序、命令和事实内容。

---

## 2026-10-01 15:52

### 变更
- `docs/development-workflow.md` — 记录从新电脑安装 WSL 2、Docker Desktop 到构建、启动、测试、日常开发和故障处理的完整步骤。
- `README.md` — 增加 Windows 开发工作流入口。
- `TODO.md` — 要求首次开发先执行并验证环境工作流。

### 原因
- 让用户能够独立复刻本次已验证的正确环境配置和容器操作。

### 验证
- 按文档命令执行 `docker compose config --quiet`、`docker compose ps` 和容器内 pytest → 配置有效、三个服务健康、测试通过。
- 检查文档 → 宿主机只要求 Git、WSL 2、Docker Desktop，没有宿主机 Python 或 Node.js 安装步骤。

### 未处理
- 前端容器将在任务 04 实现后补充实际构建和启动结果。

---

## 2026-10-01 16:06

### 变更
- `figs/imm-agent-architecture.drawio` — 新增可编辑的应用架构与问答闭环流程图，展示在线问答、离线知识处理、容器运行环境和质量闭环，并区分已实现基础与首版规划。

### 原因
- 根据整体应用搭建逻辑提供可继续编辑、可用于开发沟通和汇报的架构图。

### 验证
- PowerShell 解析 `figs/imm-agent-architecture.drawio` → XML 解析成功，共 44 个图形、22 条连线，无重复 ID 或断开的连线引用。
- 在 draw.io（diagrams.net）中选择“文件 → 从设备打开”并选择该文件 → 可查看并编辑所有文字、图形和连线。

### 未处理
- 未额外生成 PPT；draw.io 源文件已满足可编辑要求。

---

## 2026-10-01 16:07

### 变更
- `figs/imm-agent-architecture.drawio` — 统一离线知识链和容器质量区的标题措辞，使模块名称与架构说明一致。

### 原因
- 让流程图标题直接表达模块职责，便于按图理解和实施。

### 验证
- 检查 draw.io XML 中的关键标签 → “离线知识处理链路”和“容器运行环境与质量保障”均存在。

### 未处理
- 未调整其余已经通过结构检查的图形和连线。
