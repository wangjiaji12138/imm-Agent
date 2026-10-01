# Imm-Agent 前端

React、TypeScript、Vite 与 Material UI 构成的首版页面。开发和验收统一通过项目根目录的 Docker Compose 执行，不依赖宿主机 Node.js。

```text
docker compose build frontend
docker compose run --rm frontend npm run build
docker compose run --rm frontend npm run lint
docker compose up -d frontend
```

浏览器访问 `http://127.0.0.1:5173`。Vite 将页面发往 `/health` 的请求代理到 Compose 网络中的后端服务。
