import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from api import categories, prompts, templates

app = FastAPI(title="SD Magic API")

# 确保静态文件目录存在
STATIC_DIR = "static"
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# API 路由
app.include_router(categories.router, prefix="/api/categories", tags=["categories"])
app.include_router(prompts.router, prefix="/api/prompts", tags=["prompts"])
app.include_router(templates.router, prefix="/api/templates", tags=["templates"])

# 处理静态资源
@app.get("/static/{path:path}")
async def static_files(path: str):
    static_path = os.path.join(STATIC_DIR, path)
    if os.path.exists(static_path):
        return FileResponse(static_path)
    return FileResponse(f"{STATIC_DIR}/index.html", media_type="text/html")

# 静态资源路由
@app.get("/assets/{path:path}")
async def assets_files(path: str):
    assets_path = os.path.join(STATIC_DIR, "assets", path)
    if os.path.exists(assets_path):
        return FileResponse(assets_path)
    return FileResponse(f"{STATIC_DIR}/index.html", media_type="text/html")

# 首页路由
@app.get("/")
async def read_root():
    return FileResponse(f"{STATIC_DIR}/index.html", media_type="text/html")

# 处理前端路由刷新
@app.get("/{path:path}")
async def catch_all(request: Request, path: str):
    # 其他路由返回 index.html，让前端路由处理
    return FileResponse(f"{STATIC_DIR}/index.html", media_type="text/html")
