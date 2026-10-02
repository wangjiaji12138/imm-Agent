# Imm-Agent 跨平台开发工作流

本文将 Windows、macOS（仅 Apple Silicon / ARM64）和 Linux 的首次安装分开说明，Docker 就绪后共用项目构建、启动、测试和日常开发流程。Windows 11 流程已验证；2026-10-02 在 macOS 15.4.1 / Apple Silicon 完成 Docker 安装、ARM64 镜像构建、四服务健康检查、前端 build/lint 和第二阶段后端测试。Linux 仍待实测。

项目运行时全部位于容器中：后端使用 Python 3.10 镜像，后续前端使用 Node.js 22 镜像，数据服务使用 MySQL 与 Qdrant 镜像。三个平台都不需要在宿主机为本项目安装 Python、Node.js、MySQL、Qdrant、pip 或 npm。代码仍在宿主机 IDE 中编辑，依赖安装、运行和测试由容器完成。

| 平台 | 宿主机准备 | 本文使用的终端 | 验证状态 |
| --- | --- | --- | --- |
| Windows 11 | Git、WSL 2、Docker Desktop（Linux 容器） | PowerShell | 已实测 |
| macOS Apple Silicon | Git、Apple Silicon 版 Docker Desktop | Terminal（zsh） | 已实测（2026-10-02） |
| Linux | Git、Docker Engine、Buildx 与 Compose 插件；接口检查使用 curl | Bash | 待实测 |

## 1. 当前已验证的版本

| 组件 | 版本或镜像 | 安装位置 |
| --- | --- | --- |
| Windows | Windows 11 64 位 | 宿主机 |
| WSL | WSL 2 | 宿主机 |
| Docker CLI | 29.8.1（由 Docker Desktop 提供） | 宿主机 |
| Docker Compose | 5.5.1 | 随 Docker Desktop 安装 |
| 后端 | `python:3.10.11-slim` | Docker 镜像 |
| MySQL | `mysql:8.4` | Docker 镜像 |
| Qdrant | `qdrant/qdrant:v1.15.5` | Docker 镜像 |
| 前端 | `node:22` | Docker 镜像 |

版本表中的 Docker CLI/Compose 与镜像组合已在 Windows 和 macOS Apple Silicon 验证；本次 Mac 使用 Docker Desktop 4.93.0。Linux 仍待验证。Docker CLI 版本不等于 Docker Desktop 应用版本。更新任一镜像版本后，必须重新构建、运行测试并在 `REVIEW.md` 记录结果。

## 2. 新电脑首次安装：按平台选择

只执行自己平台对应的安装步骤，然后进入 2.4 的统一就绪检查。

### 2.1 Windows 11

以下命令使用 PowerShell。安装 WSL 2 和 Docker Desktop 时会出现 Windows 管理员权限确认。

#### 检查 Git

```powershell
git --version
```

能输出版本号即可。如果电脑没有 Git，先从 Git for Windows 官方安装包安装，安装后重新打开 PowerShell。

#### 安装 WSL 2

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

#### 安装 Docker Desktop

以管理员身份执行：

```powershell
winget install --id Docker.DockerDesktop --exact --source winget --scope machine --accept-package-agreements --accept-source-agreements
```

安装结束后从开始菜单启动 Docker Desktop，使用 WSL 2 后端和 Linux 容器，等待引擎运行。关闭并重新打开 PowerShell，使新的 PATH 生效。安装要求以 [Docker Windows 官方文档](https://docs.docker.com/desktop/setup/install/windows-install/) 为准。

### 2.2 macOS：仅 Apple Silicon（ARM64）

以下命令使用 Terminal 中的 zsh。先检查终端架构和 Git：

```sh
uname -m
git --version
```

`uname -m` 应输出 `arm64`。如果 Apple Silicon 设备输出 `x86_64`，先关闭终端的 Rosetta 运行模式，再重新打开终端；本文不覆盖 Intel Mac。

如果 Git 不可用，按 [Apple 命令行工具安装说明](https://developer.apple.com/documentation/xcode/installing-the-command-line-tools/) 执行以下命令，完成弹窗安装后再检查 `git --version`，无需安装完整 Xcode：

```sh
xcode-select --install
```

从 [Docker macOS 官方安装页](https://docs.docker.com/desktop/setup/install/mac-install/) 下载 **Docker Desktop for Mac with Apple silicon**，打开 `Docker.dmg`，将 Docker 拖入 Applications，然后启动 Docker，完成首次设置并等待引擎运行。重新打开终端，使 Docker CLI 的 PATH 设置生效。

本项目在 Mac 上以 `linux/arm64` 镜像为目标，不需要 WSL，也不默认添加 `platform: linux/amd64`。首次拉取后按 3.4 检查镜像架构；是否能完成构建和运行仍需在该设备上验证。

### 2.3 Linux

以下流程采用 Docker Engine 与 Compose 插件，无需安装 Docker Desktop。先用发行版的软件包管理器安装 Git 和 curl，再确认 `git --version`、`curl --version` 可用。

1. 在 [Docker Engine 官方安装页](https://docs.docker.com/engine/install/) 选择实际发行版，例如 Ubuntu、Debian 或 Fedora，按对应页面设置软件源并安装。不要混用不同发行版的安装命令。
2. 安装组件应包含 Docker Engine、CLI、containerd、Buildx 和 Compose 插件。若缺少 Compose，按 [Compose 插件安装说明](https://docs.docker.com/compose/install/linux/) 补装。
3. 对使用 systemd 的发行版，启动服务并设为开机启动：

```sh
sudo systemctl enable --now docker
```

非 systemd 发行版使用其服务管理方式启动 Docker。后续通用命令假设当前用户可以直接运行 `docker`。本地开发机可按 [Docker Linux 安装后配置](https://docs.docker.com/engine/install/linux-postinstall/) 将当前用户加入安装时创建的 `docker` 组：

```sh
sudo usermod -aG docker "$USER"
```

退出登录并重新登录后生效。`docker` 组具有相当于 root 的权限；若设备管理规则不允许加入该组，则在后续 Docker 命令前使用 `sudo`。

### 2.4 统一 Docker 就绪检查

三个平台都执行以下命令：

```text
docker --version
docker compose version
docker info
```

通过条件：CLI 和 Compose 能输出版本；`docker info` 能连接 Server，且 `OSType` 为 `linux`。Apple Silicon 设备的 Server 架构应为 `aarch64` 或 `arm64`。通过后进入通用流程，不继续安装宿主机 Python 或 Node.js。

## 3. 第一次启动项目：通用流程

以下 `text` 代码块中的 Docker/Git 命令可以直接在 PowerShell、zsh 或 Bash 中执行；宿主机命令有差异的步骤会单独列出。

### 3.1 获取代码

```text
git clone https://github.com/wangjiaji12138/imm-Agent.git
cd imm-Agent
```

如果代码已经存在，直接在所用终端中进入仓库根目录。以下命令都必须从包含 `compose.yaml` 的项目根目录执行。

### 3.2 创建本地配置

仅在 `.env` 不存在时执行，已有配置应保留。Windows PowerShell：

```powershell
Copy-Item .env.example .env
```

macOS / Linux：

```sh
cp .env.example .env
```

打开 `.env`，至少修改以下两个本地数据库密码：

```text
IMM_AGENT_MYSQL_PASSWORD=<新的本地开发密码>
IMM_AGENT_MYSQL_ROOT_PASSWORD=<新的本地 root 密码>
```

`.env` 已被 `.gitignore` 排除，不能提交到 Git。`.env.example` 只维护变量名和无敏感性的示例值。

### 3.3 检查 Compose 配置

```text
docker compose config --quiet
```

通过条件：命令无输出并以退出码 0 结束。如果提示缺少变量，先检查 `.env` 是否位于项目根目录，以及变量名是否与 `.env.example` 一致。

### 3.4 拉取固定基础镜像

```text
docker pull python:3.10.11-slim
docker pull mysql:8.4
docker pull qdrant/qdrant:v1.15.5
```

显式拉取可以提前发现网络或 Docker Hub 访问问题，也能规避已经遇到过的 BuildKit 获取基础镜像元数据时 IPv6 超时问题。

macOS Apple Silicon 首次拉取后，额外检查三个镜像的本地架构：

```sh
docker image inspect python:3.10.11-slim mysql:8.4 qdrant/qdrant:v1.15.5 --format '{{.RepoTags}} {{.Os}}/{{.Architecture}}'
```

三项都应显示 `linux/arm64`。若拉取报告 `no matching manifest` 或架构不是 ARM64，先按第 6 节排查，不能直接视为该平台验证通过。

### 3.5 构建应用镜像

```text
docker compose build backend frontend
```

该命令在镜像内部安装 `backend/pyproject.toml` 中声明的 Python 包和 `frontend/package-lock.json` 锁定的 Node.js 包，不读取宿主机 Python 或 Node.js 环境。

通过条件：前后端镜像均构建成功，且命令退出码为 0；输出中的镜像名前缀可能随项目目录名变化。

### 3.6 启动全部服务

```text
docker compose up -d
docker compose ps
```

首次启动 MySQL 可能需要几十秒。重复执行 `docker compose ps`，直到以下四个服务的状态都包含 `healthy`：

- `frontend`
- `backend`
- `mysql`
- `qdrant`

端口只绑定到本机：前端 `127.0.0.1:5173`、后端 `127.0.0.1:8000`、MySQL `127.0.0.1:3306`、Qdrant `127.0.0.1:6333` 和 `6334`。

### 3.7 验证接口

Windows PowerShell：

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod http://127.0.0.1:8000/ready
```

macOS / Linux：

```sh
curl --fail --silent --show-error http://127.0.0.1:8000/health
curl --fail --silent --show-error http://127.0.0.1:8000/ready
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

```text
docker compose run --rm backend python -m pytest
```

通过条件：ARCH-02 后默认测试输出 `47 passed, 1 skipped`；增加 `-e IMM_AGENT_TEST_MYSQL=1` 运行全部测试应为 `48 passed`。默认跳过的是真实 MySQL 集成测试。测试临时容器会在结束后由 `--rm` 删除。

第二阶段迁移、导入、资料发布和评测题验收见 [知识库工作流](stage-two-workflow.md)。

## 4. 每天开始和结束开发：通用流程

### 开始开发

1. Windows/macOS 启动 Docker Desktop；Linux 确认 Docker 服务运行。用 `docker info` 确认引擎可用。
2. 在仓库根目录执行：

```text
docker compose up -d
docker compose ps
```

3. 确认四个服务均为 `healthy`。

### 查看日志

```text
docker compose logs --tail 100 backend
docker compose logs --tail 100 frontend
docker compose logs --tail 100 mysql
docker compose logs --tail 100 qdrant
```

持续查看某个服务时使用：

```text
docker compose logs -f backend
```

按 `Ctrl+C` 退出日志跟踪，不会停止容器。

### 修改后端代码后

当前后端代码在构建时复制进镜像，没有使用宿主机目录挂载。代码或 `pyproject.toml` 发生变化后执行：

```text
docker compose build backend
docker compose run --rm backend python -m pytest
docker compose up -d backend
docker compose ps
```

随后重新请求 `/health` 和 `/ready`。只有构建、测试、容器健康和接口行为都符合任务卡验收条件，才能在 `TODO.md` 链接的阶段任务卡中勾选任务。

### 修改前端代码后

开发中的 `frontend/` 目录挂载到前端容器，保存代码后 Vite 会自动刷新页面。`package.json` 或 `package-lock.json` 变化后需要重建镜像；提交任务前始终执行：

```text
docker compose build frontend
docker compose run --rm --no-deps frontend npm run build
docker compose run --rm --no-deps frontend npm run lint
docker compose up -d frontend
```

### 结束开发

临时停止服务并保留容器：

```text
docker compose stop
```

停止并移除容器及项目网络，同时保留 MySQL、Qdrant 数据卷：

```text
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
7. 验收全部通过后，在 `TODO.md` 链接的阶段任务卡中勾选任务并写完成记录。

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

## 6. 常见问题与平台差异

### `docker` 命令不存在

- Windows：安装后重新打开 PowerShell；确认 Docker Desktop 已安装并启动，必要时在“应用和功能”中修复安装。
- macOS：重新打开 Terminal，检查 Docker Desktop 的 CLI 安装设置及终端 PATH。
- Linux：确认已安装 Docker CLI，并且其安装目录位于 PATH。

不要通过安装其他 Python 或 Node 工具解决 Docker PATH 问题。

### `docker-credential-desktop` 不存在

Windows/macOS 先启动 Docker Desktop，再重新打开终端，检查 Docker CLI 与凭据助手是否在 PATH 中。Linux Engine 环境若出现该错误，检查是否从另一台 Desktop 机器复制了 Docker 客户端配置；不要跨平台复制凭据配置。

### Linux 无权访问 Docker socket 或无法连接引擎

出现 `permission denied` 时，检查当前用户是否已加入 `docker` 组并重新登录，或使用 `sudo docker info` 验证。使用 systemd 时可执行 `sudo systemctl status docker` 查看服务状态；服务未启动时执行 `sudo systemctl start docker`。不要通过把 Docker socket 改为所有用户可写来解决。

### Apple Silicon 镜像架构不匹配

确认使用原生 ARM64 终端，并检查是否曾设置 `DOCKER_DEFAULT_PLATFORM=linux/amd64`；若有，应移除该覆盖后重新拉取。可用 `docker buildx imagetools inspect <镜像:标签>` 查看远端清单是否包含 `linux/arm64`。若目标标签确实不支持 ARM64，应先确认兼容标签并验证后再调整项目镜像版本，不默认给整个项目强制添加 AMD64 模拟配置。

### 构建时访问 Docker Hub 的 IPv6 地址超时

先单独拉取 Dockerfile 使用的固定基础镜像，再重新构建：

```text
docker pull python:3.10.11-slim
docker compose build backend
```

如果普通 `docker pull` 也失败，先检查网络连接和代理。Windows/macOS 检查 Docker Desktop 的代理设置；Linux 检查 Docker daemon 的代理配置。不要修改项目代码规避网络错误。

### 某个服务显示 `unhealthy`

```text
docker compose ps
docker compose logs --tail 200 <服务名>
```

根据日志修复配置后重建或重启对应服务。不要直接删除数据卷。

### 端口已被占用

Windows PowerShell：

```powershell
Get-NetTCPConnection -State Listen | Where-Object LocalPort -In 8000,3306,6333,6334
```

macOS：

```sh
lsof -nP -iTCP:8000 -iTCP:3306 -iTCP:6333 -iTCP:6334 -sTCP:LISTEN
```

Linux（查看监听列表中的上述端口）：

```sh
sudo ss -ltnp
```

先识别占用进程。不要在不清楚进程用途时强制终止它；可以关闭已知的旧开发服务，或在 `compose.yaml` 中有记录地修改宿主机端口。

## 7. 从零复刻检查表

- [ ] Git 可用。
- [ ] 完成对应平台安装：Windows 的 WSL 2 与 Docker Desktop、macOS 的 Apple Silicon 版 Docker Desktop，或 Linux 的 Engine 与插件。
- [ ] `docker --version`、`docker compose version`、`docker info` 均成功，使用 Linux 容器。
- [ ] macOS Apple Silicon 的三个基础镜像均确认为 `linux/arm64`（其他平台不适用）。
- [ ] 仓库根目录存在未提交的 `.env`，且本地密码已修改。
- [ ] `docker compose config --quiet` 通过。
- [ ] 固定基础镜像拉取成功。
- [ ] `docker compose build backend` 成功。
- [ ] 前端、后端、MySQL、Qdrant 均为 `healthy`。
- [ ] `/health` 和 `/ready` 返回预期内容。
- [ ] 容器内 pytest 全部通过。
- [ ] 宿主机没有为本项目额外安装 Python、Node.js、MySQL 或 Qdrant。
- [ ] 将实际操作系统、CPU 架构、Docker/Compose 版本和验证结果追加到 `REVIEW.md`，未实测的平台保持“待实测”。
