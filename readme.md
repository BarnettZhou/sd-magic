# sd-magic

sd-magic 是一个用于管理 AI 提示词的工具，它可以帮助用户创建、管理和组织提示词。

## 容器运行

在根目录下运行

```bash
docker-compose up -d
```

即可构建 `backend` 和 `db` 容器，`backend` 容器运行在 8000 端口，`db` 容器运行在 5432 端口，如果出现端口冲突，可以修改 `docker-compose.yml` 文件中的端口。

## 访问应用

打开浏览器，访问 `http://localhost:8000` 即可访问 sd-magic。

## 前端开发

前端开发请在 frontend 目录下进行，使用 `npm run dev` 即可启动开发服务器。

启动本地开发服务后，如果你已经启动了 `backend` 容器 和 `db` 容器，即可访问 `sd-magic`。

在`/frontend/src/config/api.ts`中指定了后端 API 的地址为`http://localhost:8000`，如果遇到端口占用，可自行修改。

## 前端构建

前端静态文件已经提前构建到了 `fastapi` 的 `static` 目录下（`backend/static`），如果你修改了前端代码，需要重新构建静态文件，可以按照以下步骤进行：

首先确保已经安装了 `npm`，然后执行以下命令

```bash
cd frontend
```

Windows 下执行

```bash
npm run build-and-copy-win
```

Linux 下执行

```bash
npm run build-and-copy-linux
```

完成后，将在 `backend/static` 目录下生成静态文件