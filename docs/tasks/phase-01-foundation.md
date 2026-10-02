# 第一阶段任务卡

[返回任务总入口](../../TODO.md) · [架构导航](../architecture/README.md)

这里是本阶段任务状态、验收条件和完成记录的唯一维护位置。原任务卡和历史完成记录保留；卡片中路径表示仓库根目录下的位置。未来实现位置以架构目录表为准，历史记录不改写。

## 第一阶段：先得到可以启动的空应用

<a id="task-01"></a>

### 01｜写死首版范围

- [x] 创建 `docs/mvp-scope.md`，明确首版做什么、输入输出是什么、什么情况必须拒答。

文档必须包含以下内容：

- 支持的问题：概念解释、术语解释、作用机制、不同疗法的资料内比较、研究进展、基于上一轮的追问。
- 回答结构：简短结论、通俗解释、适用条件或研究状态、来源列表。
- 证据不足时的固定行为：明确说“当前资料不足以回答”，同时列出已找到的相关来源，不补写结论。
- 个体化治疗请求的固定行为：解释只能提供一般科普信息，建议咨询专业医生，不判断用户适合哪种治疗。
- 首版不做：诊断、剂量建议、治疗方案选择、联网自由搜索、知识图谱、模型微调。
- 5 个正常问题示例和 5 个拒答或证据不足示例，每个示例写预期行为。

验收：开发者看到任意一个用户问题，都能依据文档判断它属于“回答”“澄清”还是“拒答/证据不足”。

交给编程助手：

> 创建 docs/mvp-scope.md。把 TODO 任务 01 中列出的支持范围、回答结构、证据不足行为、个体化请求行为、排除项和 10 个示例完整写入文档。使用可以测试的句子，避免“适当处理”“视情况而定”等模糊表达。

完成记录：文件=`docs/mvp-scope.md`；验证=10 个示例均包含输入、预期分类和通过条件；备注=无。

<a id="task-02"></a>

### 02｜创建后端骨架和健康检查

- [x] 创建一个能启动的 FastAPI 后端。

需要创建：

```text
backend/
  Dockerfile
  .dockerignore
  pyproject.toml
  app/__init__.py
  app/main.py
  app/settings.py
  tests/test_health.py
.env.example
.gitignore
```

具体行为：

- `GET /health` 返回 HTTP 200 和 `{"status":"ok","service":"imm-agent"}`。
- 配置从环境变量读取；缺少与健康检查无关的数据库或模型配置时，应用仍能启动。
- `.env.example` 只放变量名和无敏感性的示例值。
- `.gitignore` 排除 `.env`、虚拟环境、缓存、构建产物、`data/raw/` 和数据库导出文件。

验收命令（在项目根目录执行）：

```powershell
docker compose build backend
docker compose run --rm backend python -m pytest
docker compose up -d backend
```

启动后访问 `http://127.0.0.1:8000/health`，必须得到任务中指定的 JSON。

交给编程助手：

> 完成 TODO 任务 02。使用 Python 3.10 容器、FastAPI、Pydantic v2 和 pytest 创建后端骨架。创建 Dockerfile 和 .dockerignore，实现精确的 /health 响应，补齐 .env.example 和 .gitignore，并在容器内运行测试。不要要求宿主机安装 Python，不要实现数据库和聊天功能。完成后列出改动文件、启动命令和测试结果。

完成记录：文件=`backend/Dockerfile`、`backend/app/main.py`、`backend/app/settings.py`、`backend/tests/test_health.py`；验证=后端镜像构建成功，容器内 pytest 通过，实际访问 `/health` 返回 HTTP 200 和约定 JSON；备注=测试依赖产生一条上游弃用警告，不影响结果。

<a id="task-03"></a>

### 03｜创建本地 MySQL 和 Qdrant

- [x] 创建 `compose.yaml`，让 MySQL 与 Qdrant 可以在本地启动并保存数据。

具体行为：

- 服务名使用 `mysql` 和 `qdrant`。
- MySQL 的库名、用户名和密码从 `.env` 读取；`.env.example` 提供本地开发示例。
- 两个服务都有持久化卷和健康检查。
- 后端新增 `GET /ready`：能连接 MySQL 和 Qdrant 时返回 200；任一服务不可用时返回 503，并在 `checks` 字段分别标出状态。
- 不把密码、数据库文件或卷内容提交到 Git。

验收命令：

```powershell
docker compose config
docker compose up -d
docker compose ps
```

后端、MySQL 与 Qdrant 都必须显示 healthy；访问 `/ready` 必须返回 200。

交给编程助手：

> 完成 TODO 任务 03。增加 compose.yaml，统一管理后端、MySQL、Qdrant、持久化卷和健康检查。扩展后端配置并实现 /ready，逐项检查两个依赖。为 ready 接口写测试，测试中使用依赖替身。最后运行 docker compose config 和容器内后端测试。

完成记录：文件=`compose.yaml`、`backend/app/readiness.py`、`backend/tests/test_readiness.py`；验证=后端、MySQL 与 Qdrant 均为 healthy，容器内后端测试通过，实际访问 `/ready` 返回 HTTP 200；备注=无。

<a id="task-04"></a>

### 04｜创建前端骨架

- [x] 创建 `frontend/` React + TypeScript 页面和 Node.js 22 Dockerfile，并显示后端健康状态。

页面必须包含：标题“Imm-Agent”、一句科普定位、禁用状态的提问框、后端状态文字。页面加载时请求 `/health`；成功显示“服务正常”，失败显示“服务未连接”。

验收命令（在项目根目录执行）：

```powershell
docker compose build frontend
docker compose run --rm frontend npm run build
docker compose run --rm frontend npm run lint
```

浏览器打开开发地址后能看到页面，后端启停会导致状态文字发生对应变化。

交给编程助手：

> 完成 TODO 任务 04。用 Node.js 22 容器和 Vite 创建 React + TypeScript 前端，实现标题、定位说明、暂时禁用的提问框和后端健康状态。把前端服务加入 Compose，配置开发代理访问后端。不要要求宿主机安装 Node.js 或 npm。保持页面简单，按用户决定使用 Material UI，不加入聊天或登录。在容器内运行 lint 与 build。

完成记录：文件=`frontend/`、`compose.yaml`、`docs/development-workflow.md`；验证=前端镜像构建成功，容器内 build 和 lint 通过，四个 Compose 服务均为 healthy，浏览器验证后端正常和断开状态；备注=提问框按首版任务保持禁用。

