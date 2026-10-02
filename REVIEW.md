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

---

## 2026-10-01 22:14

### Changed
- `docs/technical-summary.md` — 改为入门导读，22 个技术小节统一解释“是什么 / 为什么 / 在本项目里怎么用”，加入术语表、学习路径和启动练习，移除后续任务与历史验收段落。
- `README.md` — 同步技术文档入口名称与说明。
- `REVIEW.md` — 追加本次文档修改记录。

### Why
- 按用户要求将阶段快照改为适合新手阅读的技术栈说明，保留简短解释和可自行搜索的关键词。

### Verify
- `git diff --check` → 无空白错误。
- 打开 `docs/technical-summary.md`，逐节检查“是什么 / 为什么 / 在本项目里怎么用” → 22 个技术小节均包含三项；已用临时 PowerShell 检查确认。
- 从 README 打开“技术栈入门导读”，逐一打开文档的本地文件链接 → 路径存在；已用临时 PowerShell 检查确认两份文档共 25 处本地链接有效。
- 在导读中搜索“后续工作”“后续实施顺序”“本次验证与限制” → 无匹配；术语表和学习路径存在。

### Not touched
- 未修改应用代码、依赖、TODO 任务状态或开发工作流；保留全部既有 REVIEW 条目。
- 本次只做文档检查，未重新运行容器构建、应用测试或浏览器交互；正文中的运行命令供读者练习使用。

---

## 2026-10-02｜第二阶段：可追溯知识库与本机环境

### 变更
- 安装 Docker Desktop 4.93.0 到 `/Applications/Docker.app`，Docker CLI 29.8.1、Compose 5.5.1；在 `/opt/homebrew/bin` 添加 Docker 与凭据助手链接。Homebrew 安装步骤遇到系统链接需要管理员密码，最终使用已下载的官方 DMG 直接复制安装。
- 创建被 Git 忽略的 `.env`，随机生成本地 MySQL 密码，不记录密码值；后端和前端依赖在容器内安装。Docker 安装期间使用 `/private/tmp/imm-agent-stage2-venv` 做了隔离预检，正式验收以容器结果为准。
- `backend/app/models.py`、`database.py`、`migrations/`：六张知识表、状态/版本/哈希约束及 Alembic 迁移。
- `backend/app/knowledge.py`、`cli/`：逐行 JSONL 导入、清洗与去重、审核发布/撤回/过期、事务内索引任务、SQL 当前状态和最新版本核验。
- `data/sources.json`、`docs/knowledge-sources.md`：五篇 NCI 官方资料及复用规则，ACS/CRI 补充目录。原始网页、提取正文、哈希和抓取记录仅保留在 Git 忽略的 `data/raw/`。
- `evals/questions.jsonl`、`backend/app/evaluation.py`：20 道中文评测题、15/5 开发与独立测试划分、Pydantic 格式及真实数据库来源验证。
- `compose.yaml` 挂载 data 和只读 evals；Dockerfile 包含迁移文件；新增来源、评测与第二阶段运行文档，更新 TODO 和开发工作流。

### 验证
- macOS 15.4.1 / Apple Silicon；Docker 引擎 `linux/aarch64`；前后端、MySQL、Qdrant 使用 `linux/arm64` 镜像。
- `docker compose config --quiet`、`docker compose build backend frontend` 通过。
- MySQL 8.4 的 `alembic upgrade head`、重复 upgrade、确认空资料库后 `downgrade base`、检查六表移除、再次 upgrade 全部通过。
- `docker compose run --rm -e IMM_AGENT_TEST_MYSQL=1 backend python -m pytest` → **34 passed**，保留 1 条上游 TestClient 弃用警告。真实 MySQL 测试验证 CHECK 错误码 3819、内容哈希唯一约束及撤回后残留候选被过滤；测试写入均回滚。
- 虚构清单首次 `2 success / 1 failed`，再次 `2 skipped / 1 failed`，均按约定退出 1。两条虚构资料验收后精确清理，不进入正式证据池。
- NCI 清单首次 `5 success`，再次 `5 skipped`；原始正文哈希与来源快照元数据一致。正式容器 `fetch_sources --output data/raw/container-check` 也成功抓取全部五篇。
- 待审核时 `validate_evals` 返回 `ready=false` 并逐项报告未发布；五篇逐一核对并 publish 后返回 `ready=true, total=20, dev=15, test=5`。正式资料库保留五篇 published NCI 资料。
- `docker compose run --rm --no-deps frontend npm run build`、`npm run lint` 通过；lint 无警告或错误。
- 实际 `/health`、`/ready` 及前端 `/health` 代理均返回约定响应；四个服务为 healthy。
- `git diff --check` 通过；`.env` 与 `data/raw/` 均被 Git 忽略。

### 范围与限制
- 本阶段的 published 表示通过来源与提取完整性基础审核，可以进入一般科普的证据池；不表示医学专家审核。资料日期较早，不将其当作 2026 年最新获批清单或中国临床适用结论。
- 首批只有 NCI 正文。ACS、CRI 已核查官方入口并列为补充目录，未在未确认全文复用条件时批量复制正文。
- Qdrant 切分/embedding/写入/检索及索引任务工作器属于第三阶段；第二阶段通过模拟残留索引候选验证 SQL 核验。前端仍为现有骨架，问答发送尚未启用。
- 20 题验证的是格式、引用存在和发布状态；不代表已完成模型回答评测或临床验证。

---

## 2026-10-02｜整体架构、功能分区和任务占位

### 变更
- `docs/architecture/`：增加总体目录、逐文件职责、依赖与接口边界、现有代码迁移表、跨设备数据生命周期；明确采用模块化单体。
- 根 `TODO.md` 改为阶段和模块导航；原 01—42 共 18 张任务卡连同完成状态、验收命令与记录完整移至 `docs/tasks/phase-*.md`。新增 ARCH-01 目录设计与 ARCH-02 代码迁移任务。
- 后端预留 api/core/infrastructure 和 knowledge/retrieval/answering/agent/conversations/feedback/evaluation 七个业务分区；前端预留 features 与 shared；每个功能分区都有 TODO，引用唯一阶段验收卡。
- 补齐 CLI、提示词、模块/集成/端到端测试计划、生产部署及 CI 示例、评测/安全/发布报告模板；占位明确为未实现，未来 CLI 主动非零退出，CI 的 `.example` 不触发执行。
- `scripts/check_layout.py`：只读检查架构文件、占位标记、任务覆盖、Python 语法及 Markdown 本地链接。
- 新增 `data/backups/` 忽略规则；现有 raw、SQL 备份及 Docker 数据卷不移动。备份/恢复 CLI 仍是任务 42 占位。
- 同步 README 的架构入口与五阶段路线，开发工作流改为在阶段任务卡维护完成状态。

### 验证
- `docker compose run --rm --no-deps -v ".:/workspace:ro" -w /workspace backend python scripts/check_layout.py` → ok=true，85 个架构条目、20 张任务卡、63 份 Markdown、392 个本地链接，无错误。
- 对照本轮起点 `3745f12` 的 TODO，去除新增导航和锚点后，五阶段全部原任务文本、勾选及完成记录逐字一致。
- 在容器内执行六个占位 CLI → 均非零退出并说明“尚未实现”；导入当前 app.main → 不加载规划模块、不新增占位 `/api/` 路由。
- `docker compose run --rm --no-deps -e IMM_AGENT_TEST_MYSQL=1 -v "./backend/app:/app/app:ro" -v "./backend/tests:/app/tests:ro" backend python -m pytest -p no:cacheprovider` → 34 passed，1 条既有 TestClient 弃用警告。首次挂载整个只读 /app 与现有 data/evals 子挂载冲突，改为分别挂载源码和测试后通过。
- 容器内 `npm run build` 通过；`npm run lint` 检查 12 个文件，无警告和错误。
- `docker compose build backend` 通过；新镜像内运行 `docker compose run --rm --no-deps -e IMM_AGENT_TEST_MYSQL=1 backend python -m pytest` → 34 passed，1 条既有警告。`docker compose up -d --no-deps --wait backend` 更新本地后端后健康检查通过。
- `git diff --check` 通过。

### 范围
- 本次完成可导航、可检查的架构设计与文件占位；现有第一、二阶段实现保持原入口，未执行 ARCH-02 的实际搬迁。
- 模块边界是下一轮实现约束，当前检查工具不宣称已验证真实 import 依赖倒置；相应自动检查属于 ARCH-02。
- 未实现第三阶段 RAG、会话、反馈或自动备份；没有更改数据库结构和既有业务数据。

---

## 2026-10-02 15:23

### 变更
- 完成 ARCH-02：配置归入 core；惰性 SQL 连接、唯一 Base 和就绪检查归入 infrastructure；资料清洗、校验、六表 ORM、仓储、事务、SQL 证据核验与 NCI 采集归入 modules/knowledge；题集模型和来源校验归入 modules/evaluation。
- main.py 只装配 FastAPI；健康路由、响应结构与依赖覆盖点归入 api。CLI 与评测通过知识服务读取资料；公开结果使用只读 DTO，Session/事务仍由调用边界持有。
- 按用户“不需要兼容旧接口”的要求删除六个旧平铺 Python 模块，统一更新应用、CLI、Alembic 装配与测试导入。保留原工作区中文注释并随实现迁移；历史迁移文件未改动。
- 新增真实应用 import 边界、相对导入、循环依赖及违规示例检查，新增 DTO 脱离 Session 与状态/索引任务原子回滚测试。同步架构目录清单、模块导航、开发文档和任务卡；下一步指向任务 20。

### 原因
- 根 TODO 推荐在切分与索引之前完成 ARCH-02，使新业务在明确的模块边界内扩展。

### 验证
- 迁移前容器回归 34 passed；纯函数/schema 提取后与 ORM/仓储/服务迁移后分别 34 passed。各阶段均启用真实 MySQL；没有对既有库执行 downgrade、清空或重新导入。
- `docker compose build backend` → 最终镜像构建成功。
- `docker compose run --rm -e IMM_AGENT_TEST_MYSQL=1 backend python -m pytest` → 最终镜像 48 passed；含原有 34 项行为测试、12 项 import 检查和违规检测、2 项 DTO/回滚测试。真实 MySQL metadata 比较为空，无表结构漂移。
- 只读脚本按主键排序后计算六表全量行 JSON 的 SHA-256：迁移前后完全一致；documents=5、document_versions=5、index_jobs=5，chunks/terms/term_aliases=0。五篇资料的 ID、内容哈希、状态及版本均保持。
- 10 组 CLI 快照（四个 --help；documents list、不存在资料 show、缺少参数 publish；validate_evals 正常/缺失文件；import_documents 缺失文件）的 stdout、stderr、退出码完全一致。最终镜像再次核对通过。只读快照脚本及前后结果存于 Git 忽略的 `artifacts/arch02/`。
- 中途直接执行 /tmp 快照脚本时导入了旧镜像 site-packages 中的占位模块，出现 ImportError；改为明确 `PYTHONPATH=/app` 验证挂载代码，最终镜像验证无需该覆盖，全部通过。
- `docker compose up -d --no-deps backend` 和 `docker compose ps` → 后端更新成功，四服务 healthy；容器内 urllib 请求实际 /health 返回 ok，/ready 返回 ready，mysql/qdrant 均 ok。
- `docker compose run --rm --no-deps -v ".:/workspace:ro" -w /workspace backend python scripts/check_layout.py` → 81 个架构条目、20 张任务卡、本地文档链接无错误。
- 配置、就绪检查、ORM 类及采集函数的迁移前后 AST 对比一致；历史迁移无 diff；`git diff --check` 通过。

### 未处理
- 1 条既有 Starlette/TestClient 对 httpx 的弃用警告，不影响本次通过结果。
- 任务 20—23 及后续页面/会话/反馈继续保持未实现；本次未调整前端代码或新增 RAG 功能。
