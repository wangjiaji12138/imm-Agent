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

---

## 2026-10-01 16:19

### 变更
- `figs/imm-agent-architecture.drawio` — 将流程图重构为开发者视角，按客户端与接口契约、后端与 Agent 编排、知识 ETL 与索引、响应事件、开发测试与交付组织内容；移除实现状态标注，并增加多色卡片和可编辑图标。

### 原因
- 根据用户反馈，让流程图直接服务于系统开发和模块协作，同时增强不同职责区域的视觉区分。

### 验证
- PowerShell 解析 `figs/imm-agent-architecture.drawio` → XML 有效，44 个图形和 22 条连线均可解析，无重复 ID 或断开的连线引用。
- 检查流程图内容 → “已实现基础”和“首版规划”均不存在，虚线状态卡片为 0，20 个关键图标全部存在，共使用 31 种填充色。

### 未处理
- 保留现有画布尺寸和模块总体位置，避免无关的版式重排。

---

## 2026-10-01 16:26

### 变更
- `figs/imm-agent-architecture.drawio` — 放大核心组件图标，精简卡片文字，并将配色统一为客户端粉色、Agent 蓝色、知识管线橙色、响应绿色和工程保障紫色。

### 原因
- 根据用户反馈提高图标辨识度和信息扫描效率，同时避免颜色在不同职责之间杂乱分布。

### 验证
- PowerShell 解析 `figs/imm-agent-architecture.drawio` → XML 和 22 条连线有效，无重复 ID 或断开引用。
- 检查 25 张核心卡片 → 5 个区域的填充色和边框色分别一致；全部包含 24–26px 图标，职责说明均不超过一行。

### 未处理
- 保留现有模块位置和调用关系，仅调整视觉层级与文字密度。

---

## 2026-10-01 19:10

### 变更
- `docs/mvp-scope.md` — 将 boundary 拆为拒绝、超范围和紧急引导；补充判定顺序、混合请求、证据状态、响应字段及验收示例。
- `TODO.md` — 同步任务 22 的结果类型和证据状态约定，引用范围文档中的分支规则。
- `REVIEW.md` — 追加本次文档调整记录。

### 原因
- 回应请求分类缺少明确拒绝结果及其他必要分支的问题，使拒绝、无法回答和系统故障能够区分。

### 验证
- `git diff --check` → 无空白错误。
- `rg -n '^\| `|^### 示例|预期分类|预期结果' docs/mvp-scope.md` → 六种处理结果、16 个示例；旧 boundary 不再作为预期分类。
- 对照第 4、5 节检查任务 22 → result_type 六个取值和 evidence_status 四个取值一致。

### 未处理
- 保留用户已有的产品定位和输入输出描述修改。
- 未修改后端代码或架构图；本次仅完善文档约定，尚未实现分类器。
- TODO 任务 01 的历史完成记录仍保留当时的 10 个示例数。

---

## 2026-10-01 19:21

### 变更
- `docs/development-workflow.md` — 分开 Windows、macOS Apple Silicon 和 Linux 安装步骤，共用 Docker 就绪检查、构建、测试及日常流程；补充平台命令差异、ARM64 检查和实测状态。
- `README.md` — 更新工作流入口名称及分平台宿主机要求。
- `TODO.md` — 更新工作流入口名称及分平台宿主机要求。
- `REVIEW.md` — 追加本次文档调整记录。

### 原因
- 按用户要求将安装流程分平台记录，Mac 仅覆盖 ARM 芯片，容器内开发流程保持统一。

### 验证
- `git diff --check` → 无空白错误。
- 在 Docker CLI 所在目录已加入当前终端 PATH 后，执行 `docker compose config --quiet` → 退出码 0。
- 阅读工作流第 2、3、6、7 节 → 三个平台有各自安装入口，通用命令共用，文件复制、接口请求、端口排查按平台区分。
- 分别执行 `docker buildx imagetools inspect python:3.10.11-slim`、`docker buildx imagetools inspect mysql:8.4`、`docker buildx imagetools inspect qdrant/qdrant:v1.15.5` → Docker Hub 连接被拒绝，未能核实远端 ARM64 清单。

### 未处理
- 未修改应用代码、Dockerfile 或 Compose 配置；未重复运行应用测试。
- macOS 与 Linux 没有实际设备验证，文档保留待实测状态；未添加 Intel Mac 流程或强制 AMD64 模拟配置。

---

## 2026-10-01 19:51

### 变更
- `frontend/.gitignore` — 脚手架生成前端忽略规则。
- `frontend/.oxlintrc.json` — 脚手架生成 lint 配置。
- `frontend/README.md` — 脚手架生成模板说明。
- `frontend/index.html` — 脚手架生成 HTML 入口。
- `frontend/package.json` — 脚手架声明 React、TypeScript、Vite 依赖及开发命令。
- `frontend/public/favicon.svg` — 脚手架生成默认站点图标。
- `frontend/public/icons.svg` — 脚手架生成示例图标集合。
- `frontend/src/App.tsx` — 脚手架生成示例页面与计数器。
- `frontend/src/App.css` — 脚手架生成示例页面样式。
- `frontend/src/index.css` — 脚手架生成全局样式。
- `frontend/src/main.tsx` — 脚手架生成 React 挂载入口。
- `frontend/src/assets/hero.png` — 脚手架生成示例图片。
- `frontend/src/assets/react.svg` — 脚手架生成 React 标志。
- `frontend/src/assets/vite.svg` — 脚手架生成 Vite 标志。
- `frontend/tsconfig.json` — 脚手架生成 TypeScript 配置入口。
- `frontend/tsconfig.app.json` — 脚手架生成页面 TypeScript 配置。
- `frontend/tsconfig.node.json` — 脚手架生成工具 TypeScript 配置。
- `frontend/vite.config.ts` — 脚手架启用 React 插件。
- `REVIEW.md` — 记录用户在 Node.js 22 容器中完成的前端初始化。

### 原因
- 按做中学的节奏开始任务 04，先生成 React + TypeScript 前端骨架。

### 验证
- 用户第二次运行 create-vite 输出 Done；检查上述文件已存在。
- `Get-Content frontend/package.json` → 包含 dev、build、lint 命令。

### 未处理
- 尚未安装前端依赖、启动页面或运行 build/lint；任务 04 仍未完成。
- 保留模板页面和资源，后续逐步修改；尚未添加前端 Dockerfile、Compose 服务或后端请求。

---

## 2026-10-01 20:12

### 变更
- `frontend/.dockerignore` — 排除前端镜像不需要的本地产物。
- `frontend/.gitignore` — 保留脚手架生成的前端忽略规则。
- `frontend/.oxlintrc.json` — 保留 React 与 TypeScript lint 规则。
- `frontend/Dockerfile` — 使用 Node.js 22 安装锁定依赖并启动 Vite。
- `frontend/README.md` — 记录容器内构建、检查和启动命令。
- `frontend/index.html` — 设置中文页面语言、产品标题和说明。
- `frontend/package.json` — 增加 Material UI、图标和 Emotion 依赖。
- `frontend/package-lock.json` — 锁定前端依赖版本。
- `frontend/src/App.tsx` — 实现 Material UI 首页、禁用提问框及后端健康状态展示。
- `frontend/src/index.css` — 添加最小全局布局样式。
- `frontend/src/main.tsx` — 配置 Material UI 主题和基础样式。
- `frontend/tsconfig.app.json` — 保留页面 TypeScript 严格配置。
- `frontend/tsconfig.json` — 保留 TypeScript 项目引用入口。
- `frontend/tsconfig.node.json` — 保留 Vite 配置的 TypeScript 设置。
- `frontend/vite.config.ts` — 固定开发端口并将 `/health` 代理到后端容器。
- `compose.yaml` — 增加前端服务、代码挂载、端口、依赖关系和健康检查。
- `docs/development-workflow.md` — 将前端加入统一构建、日常开发和四服务健康检查流程。
- `TODO.md` — 按 Material UI 决定更新任务 04，并记录完成结果。
- `REVIEW.md` — 追加任务 04 完成记录。

### 原因
- 完成用户要求的主要前端工作，使首版页面通过 Docker 运行并展示后端连接状态。

### 验证
- `docker compose config --quiet` → 配置有效。
- `docker compose build frontend` → Node.js 22 前端镜像构建成功。
- `docker compose run --rm --no-deps frontend npm run build` → TypeScript 与 Vite 构建通过。
- `docker compose run --rm --no-deps frontend npm run lint` → 0 warnings、0 errors。
- `docker compose run --rm backend python -m pytest` → 3 passed，保留一条上游弃用警告。
- `docker compose ps` → frontend、backend、mysql、qdrant 均为 healthy。
- 访问前端 `/health` → 返回 `{"status":"ok","service":"imm-agent"}`。
- 浏览器检查后端运行和停止场景 → 分别显示“服务正常”和“服务未连接”，断开时出现提示。

### 未处理
- 提问框按任务范围保持禁用；聊天请求、来源列表和多轮会话留给后续任务。
- 未增加登录、路由或其他 UI 组件库。

---

## 2026-10-01 21:17

### Changed
- `frontend/src/App.css` — 补齐工作台、侧栏、提问区、证据面板和移动端布局样式。
- `REVIEW.md` — 追加本次样式修复记录。

### Why
- 修复页面引用缺失的样式文件，并完善不同屏幕宽度下的布局。

### Verify
- `docker compose exec -T frontend npm run build` → TypeScript 与 Vite 构建通过。
- `docker compose exec -T frontend npm run lint` → 0 warnings、0 errors。
- 访问 `http://127.0.0.1:5173/` 与 `/src/App.css` → 均返回 HTTP 200。

### Not touched
- `frontend/src/App.tsx` 已有未提交修改，本次未改动；发送问答与历史会话仍未开放。
- Vite 提示 JS 包超过 500 kB，本次未调整拆包；桌面自动化不可用，未完成截图检查。

---

## 2026-10-01 21:21

### Changed
- `frontend/src/App.css` — 限制侧栏与会话摘要的 flex 最小宽度，使长草稿以省略号显示。
- `REVIEW.md` — 追加本次修复记录。

### Why
- 修复输入连续文字时左栏被草稿内容撑宽的问题。

### Verify
- `docker compose exec -T frontend npm run build` → 构建通过。
- `docker compose exec -T frontend npm run lint` → 0 warnings、0 errors。
- `git diff --check` → 无空白错误。

### Not touched
- `frontend/src/App.tsx` 及问答功能未改动；桌面自动化仍不可用，未完成截图复核。

---

## 2026-10-01 21:31

### Changed
- `frontend/src/App.tsx` — 将问题与回答结构预览放在同一对话区，输入框移到底部，右侧仅保留资料来源和证据状态；同步使用指南。
- `frontend/src/App.css` — 使用视口高度和独立滚动区域固定底部输入框，添加问答预览样式并适配窄屏，删除不再使用的来源标签页样式。
- `REVIEW.md` — 追加本次布局调整记录。

### Why
- 按用户选择，将布局调整为上方依次显示用户问题和助手回答，底部持续显示输入框。

### Verify
- `docker compose exec -T frontend npm run build` → TypeScript 与 Vite 构建通过。
- `docker compose exec -T frontend npm run lint` → 0 warnings、0 errors。
- `git diff --check` → 无空白错误。
- `(Invoke-WebRequest -UseBasicParsing http://127.0.0.1:5173/).StatusCode` → 200。
- `(Invoke-WebRequest -UseBasicParsing http://127.0.0.1:5173/health).Content` → 返回 status 为 ok、service 为 imm-agent。
- 待浏览器复核：分别以桌面与手机宽度打开页面，滚动对话与来源区域 → 输入框保持在底部；点击示例问题 → 填入底部输入框；新建会话 → 清空草稿。

### Not touched
- 后端问答接口、真实发送与历史会话仍未实现，页面明确标记为预览，发送按钮保持禁用。
- 保留已有侧栏长草稿宽度修复与历史 REVIEW 记录；未改动后端和任务清单。
- Vite 仍提示 JS 包超过 500 kB，未调整拆包；浏览器工具无可用连接，尚未完成截图和交互复核。

---

## 2026-10-01 21:40

### Changed
- `frontend/src/App.tsx` — 移除空会话的问题、回答占位气泡及回答大纲，将对话引导简化为标题与说明；欢迎标题自然换行，输入框默认一行、最多展开四行。
- `frontend/src/App.css` — 缩小欢迎横幅、装饰图、推荐卡片及区块间距，减少底部输入区留白，同步窄屏样式并删除本次移除元素的专用样式。
- `REVIEW.md` — 追加本次首屏布局调整与验证记录。

### Why
- 减少初始欢迎区和底部输入框占用，为首次打开页面时完整展示欢迎内容与推荐问题留出空间。

### Verify
- `docker compose exec -T frontend npm run build` → TypeScript 与 Vite 构建通过，无大包警告。
- `docker compose exec -T frontend npm run lint` → 0 warnings、0 errors。
- `git diff --check` → 无空白错误。
- `(Invoke-WebRequest -UseBasicParsing http://127.0.0.1:5173/).StatusCode` → 200。
- `(Invoke-WebRequest -UseBasicParsing http://127.0.0.1:5173/health).Content` → status 为 ok、service 为 imm-agent。
- 已静态复核桌面与窄屏断点、内容区最小高度和滚动边界；输入区保持底部布局与独立高度限制。
- 待浏览器验证：以 1366×768、1280×720 和手机尺寸打开页面，检查欢迎内容、全部推荐问题与输入区的可见范围；点击推荐问题应填入草稿，新建会话应清空草稿，长草稿应最多展开四行。

### Not touched
- 未改动后端、真实问答发送、历史会话和资料来源功能；发送按钮仍禁用。
- 浏览器工具未发现可用连接，自动化运行时初始化失败，尚未完成真实视口截图与交互复核；窄屏或低高度视口仍允许滚动查看内容。
- 保留所有既有 REVIEW 记录，未新增依赖或测试框架。

---

## 2026-10-01 21:44

### Changed
- `frontend/src/App.css` — 移除资料来源空状态的 253px 最小高度，改为图标与文字横向排列，压缩资料卡片、证据状态卡片的内边距与间距，保留全部文字和操作入口。
- `REVIEW.md` — 追加右侧面板首屏高度修复记录。

### Why
- 用户截图显示资料来源空状态留白过大，将“看懂证据状态”推到输入框上方滚动区域之外；减少右侧面板占用高度。

### Verify
- `docker compose exec -T frontend npm run build` → TypeScript 与 Vite 构建通过。
- `docker compose exec -T frontend npm run lint` → 0 warnings、0 errors。
- `git diff --check` → 无空白错误。
- 刷新 `http://127.0.0.1:5173/`，在截图对应的窗口尺寸检查右侧 → 空状态随内容收缩，三种证据状态应位于底部输入框上方；窄屏文字允许自然换行。

### Not touched
- 未改动欢迎区、推荐问题、输入框行为、后端与问答功能；保留前一轮未提交修改及既有日志。
- 当前浏览器自动化不可用，本次依据用户截图和布局代码修复，尚未完成实际窗口截图复核。

---

## 2026-10-01 21:47

### Changed
- `frontend/src/App.css` — 主内容双栏改为 stretch 对齐，让左右列等高，末尾卡片底边对齐。
- `REVIEW.md` — 追加双栏底边对齐记录。

### Why
- 修复用户截图中左侧功能规划与右侧证据状态卡片底边参差的问题。

### Verify
- `docker compose exec -T frontend npm run build` → 构建通过。
- `docker compose exec -T frontend npm run lint` → 0 warnings、0 errors。
- `git diff --check` → 无空白错误。
- 刷新 `http://127.0.0.1:5173/`，窗口宽度大于 1180px → 左右两列末尾卡片底边对齐；宽度不超过 1180px → 保持原有响应式排列。

### Not touched
- 未修改卡片文字、输入框、已有紧凑间距或业务逻辑；未设置固定列高。
- 浏览器自动化连接不可用，未完成实际截图复核。

---

## 2026-10-01 21:58

### Changed
- `docs/technical-summary.md` — 按 README 的 14 个技术方向总结当前实现，记录前端结构、服务边界、验证结果和后续任务。
- `README.md` — 增加技术总结入口。
- `REVIEW.md` — 追加本次文档整理记录。

### Why
- 前端页面阶段基本完成，按用户要求形成与 README 技术栈对应的 Markdown 总结。

### Verify
- `git diff --check` → 无空白错误；打开 README 的“技术栈与阶段实现总结”链接 → 能定位新文档并核对代码链接。
- `docker compose exec -T frontend npm run build` → 构建通过；`docker compose exec -T frontend npm run lint` → 0 warnings、0 errors。
- `docker compose exec -T backend python -m pytest` → 3 passed、1 条依赖弃用警告。
- `docker compose config --quiet` → 配置有效；`docker compose ps --format json` → 四个服务均 healthy。
- `(Invoke-WebRequest -UseBasicParsing http://127.0.0.1:5173/health).Content` → status 为 ok；`(Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8000/ready).Content` → status 为 ready。

### Not touched
- 未修改应用代码、依赖或任务勾选状态；真实问答、来源与历史会话仍待实现。
- TODO 开头“还没有应用代码”和任务 04 的禁用输入框记录与当前代码有差异，保留原文；本次总结按实际代码说明草稿可编辑、发送仍禁用。
- 未修复后端测试的依赖弃用警告；未进行浏览器截图或交互复验。
