# Imm-Agent Windows 开发工作流

本文记录已经在 Windows 11 上实际验证过的环境安装、容器启动、测试和日常开发步骤。目标是在一台新电脑上仅安装 Git、WSL 2 和 Docker Desktop，即可复现当前开发环境。

项目运行时全部位于容器中：后端使用 Python 3.10 镜像，后续前端使用 Node.js 22 镜像，数据服务使用 MySQL 与 Qdrant 镜像。不要在 Windows 上为本项目安装 Python、Node.js、MySQL、Qdrant、pip 或 npm。

## 1. 当前已验证的版本

| 组件 | 版本或镜像 | 安装位置 |
| --- | --- | --- |
| Windows | Windows 11 64 位 | 宿主机 |
| WSL | WSL 2 | 宿主机 |
| Docker Desktop | 29.8.1 | 宿主机 |
| Docker Compose | 5.5.1 | 随 Docker Desktop 安装 |
| 后端 | `python:3.10.11-slim` | Docker 镜像 |
| MySQL | `mysql:8.4` | Docker 镜像 |
| Qdrant | `qdrant/qdrant:v1.15.5` | Docker 镜像 |
| 前端 | Node.js 22 | 任务 04 创建前端镜像时加入 |

版本表用于说明已验证组合。更新任一镜像版本后，必须重新构建、运行测试并在 `REVIEW.md` 记录结果。

## 2. 新电脑首次安装

以下命令使用 PowerShell。安装 WSL 2 和 Docker Desktop 时会出现 Windows 管理员权限确认。

### 2.1 检查 Git

```powershell
git --version
```

能输出版本号即可。如果电脑没有 Git，先从 Git for Windows 官方安装包安装，安装后重新打开 PowerShell。

### 2.2 安装 WSL 2

以管理员身份打开 PowerShell，执行：

```powershell
wsl --install --no-distribution
```

Windows 要求重启时先重启。重启后验证：

```powershell
wsl --status
```

通过条件：输出包含“默认版本: 2”或 `Default Version: 2`。

本项目通过 Docker Desktop 使用 WSL 2，不需要额外安装 Ubuntu 等 Linux 发行版。

### 2.3 安装 Docker Desktop

以管理员身份执行：

```powershell
winget install --id Docker.DockerDesktop --exact --source winget --scope machine --accept-package-agreements --accept-source-agreements
```

安装结束后从开始菜单启动 Docker Desktop，等待状态显示引擎已运行。关闭并重新打开 PowerShell，使新的 PATH 生效，然后验证：

```powershell
docker --version
docker compose version
docker info
```

三个命令都成功后，宿主机环境准备完成。不要继续安装 Python 或 Node.js。

## 3. 第一次启动项目

### 3.1 获取代码

```powershell
git clone https://github.com/wangjiaji12138/imm-Agent.git
Set-Location imm-Agent
```

如果代码已经存在，直接在 PowerShell 中进入仓库根目录。以下命令都必须从包含 `compose.yaml` 的项目根目录执行。

### 3.2 创建本地配置

```powershell
Copy-Item .env.example .env
```

打开 `.env`，至少修改以下两个本地数据库密码：

```text
IMM_AGENT_MYSQL_PASSWORD=<新的本地开发密码>
IMM_AGENT_MYSQL_ROOT_PASSWORD=<新的本地 root 密码>
```

`.env` 已被 `.gitignore` 排除，不能提交到 Git。`.env.example` 只维护变量名和无敏感性的示例值。

### 3.3 检查 Compose 配置

```powershell
docker compose config --quiet
```

通过条件：命令无输出并以退出码 0 结束。如果提示缺少变量，先检查 `.env` 是否位于项目根目录，以及变量名是否与 `.env.example` 一致。

### 3.4 拉取固定基础镜像

```powershell
docker pull python:3.10.11-slim
docker pull mysql:8.4
docker pull qdrant/qdrant:v1.15.5
```

显式拉取可以提前发现网络或 Docker Hub 访问问题，也能规避已经遇到过的 BuildKit 获取基础镜像元数据时 IPv6 超时问题。

### 3.5 构建后端镜像

```powershell
docker compose build backend
```

该命令在镜像内部安装 `backend/pyproject.toml` 中声明的 FastAPI、pytest、PyMySQL 等包，不读取宿主机 Python 环境。

通过条件：最后出现 `Image imm-agent-backend Built`，且命令退出码为 0。

### 3.6 启动全部服务

```powershell
docker compose up -d
docker compose ps
```

首次启动 MySQL 可能需要几十秒。重复执行 `docker compose ps`，直到以下三个服务的状态都包含 `healthy`：

- `backend`
- `mysql`
- `qdrant`

端口只绑定到本机：后端 `127.0.0.1:8000`、MySQL `127.0.0.1:3306`、Qdrant `127.0.0.1:6333` 和 `6334`。

### 3.7 验证接口

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod http://127.0.0.1:8000/ready
```

预期结果：

```json
{"status":"ok","service":"imm-agent"}
```

```json
{"status":"ready","checks":{"mysql":"ok","qdrant":"ok"}}
```

`/health` 只说明后端进程存活；`/ready` 同时验证后端能够连接 MySQL 与 Qdrant。

### 3.8 在容器内运行测试

```powershell
docker compose run --rm backend python -m pytest
```

通过条件：当前版本输出 `3 passed`。测试临时容器会在结束后由 `--rm` 删除。

## 4. 每天开始和结束开发

### 开始开发

1. 启动 Docker Desktop 并等待引擎可用。
2. 在仓库根目录执行：

```powershell
docker compose up -d
docker compose ps
```

3. 确认三个服务均为 `healthy`。

### 查看日志

```powershell
docker compose logs --tail 100 backend
docker compose logs --tail 100 mysql
docker compose logs --tail 100 qdrant
```

持续查看某个服务时使用：

```powershell
docker compose logs -f backend
```

按 `Ctrl+C` 退出日志跟踪，不会停止容器。

### 修改后端代码后

当前后端代码在构建时复制进镜像，没有使用宿主机目录挂载。代码或 `pyproject.toml` 发生变化后执行：

```powershell
docker compose build backend
docker compose run --rm backend python -m pytest
docker compose up -d backend
docker compose ps
```

随后重新请求 `/health` 和 `/ready`。只有构建、测试、容器健康和接口行为都符合任务卡验收条件，才能在 `TODO.md` 勾选任务。

### 结束开发

临时停止服务并保留容器：

```powershell
docker compose stop
```

停止并移除容器及项目网络，同时保留 MySQL、Qdrant 数据卷：

```powershell
docker compose down
```

日常开发不要执行 `docker compose down -v`。其中的 `-v` 会删除 MySQL 与 Qdrant 数据卷，只有明确需要清空全部本地数据并已确认备份时才能使用。

## 5. 每项开发任务的固定流程

1. 在 `TODO.md` 选择一张未完成任务卡，读清输入、输出、文件范围和验收条件。
2. 只修改该任务需要的文件，不顺带重构其他模块。
3. 重新构建受影响的镜像。
4. 在容器内运行相关测试。
5. 启动服务并按任务卡验证真实接口或页面行为。
6. 在 `REVIEW.md` 最下方追加中文记录。
7. 验收全部通过后，在 `TODO.md` 勾选任务并写完成记录。

`REVIEW.md` 使用以下格式：

```markdown
---

## YYYY-MM-DD HH:MM

### 变更
- `path/to/file` — 具体修改

### 原因
- 与当前需求直接相关的原因

### 验证
- `实际运行的命令` → 预期或实际结果

### 未处理
- 已发现但本次有意未修改的内容；没有则写“无”
```

旧记录只能追加，不能重排或删除。命令失败时记录真实结果，不得把未运行的测试写成已通过。

## 6. 常见问题

### `docker` 命令不存在

Docker Desktop 安装后关闭并重新打开 PowerShell。如果仍然失败，确认 Docker Desktop 已启动，并在“应用和功能”中修复安装。不要通过安装其他 Python 或 Node 工具解决 Docker PATH 问题。

### `docker-credential-desktop` 不存在

关闭当前 PowerShell，启动 Docker Desktop，再打开新的 PowerShell。该错误通常来自终端仍在使用 Docker 安装前的旧 PATH。

### 构建时访问 Docker Hub 的 IPv6 地址超时

先单独拉取 Dockerfile 使用的固定基础镜像，再重新构建：

```powershell
docker pull python:3.10.11-slim
docker compose build backend
```

如果普通 `docker pull` 也失败，先检查 Docker Desktop 的代理设置和网络连接，不要修改项目代码规避网络错误。

### 某个服务显示 `unhealthy`

```powershell
docker compose ps
docker compose logs --tail 200 <服务名>
```

根据日志修复配置后重建或重启对应服务。不要直接删除数据卷。

### 端口已被占用

```powershell
Get-NetTCPConnection -State Listen | Where-Object LocalPort -In 8000,3306,6333,6334
```

先识别占用进程。不要在不清楚进程用途时强制终止它；可以关闭已知的旧开发服务，或在 `compose.yaml` 中有记录地修改宿主机端口。

## 7. 从零复刻检查表

- [ ] Git 可用。
- [ ] `wsl --status` 显示默认版本 2。
- [ ] Docker Desktop 已启动，`docker info` 成功。
- [ ] 仓库根目录存在未提交的 `.env`，且本地密码已修改。
- [ ] `docker compose config --quiet` 通过。
- [ ] 固定基础镜像拉取成功。
- [ ] `docker compose build backend` 成功。
- [ ] 后端、MySQL、Qdrant 均为 `healthy`。
- [ ] `/health` 和 `/ready` 返回预期内容。
- [ ] 容器内 pytest 全部通过。
- [ ] Windows 上没有为本项目额外安装 Python、Node.js、MySQL 或 Qdrant。
