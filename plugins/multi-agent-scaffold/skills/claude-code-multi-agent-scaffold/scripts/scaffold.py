#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Claude Code 多 Agent 项目脚手架生成器（混合式 · 可配置技术栈）。

设计：CLI 生成正确命名的骨架（dotnet new / create-vite / degit / 规范骨架），模板补充自定义基础设施。
技术栈不再写死：后端 dotnet|python，前端 vue|uniapp。命令行优先，缺省则交互式询问。

用法：
    python scaffold.py <目标目录> [--name 项目名] [--desc 描述] [--code-name 代码名] \
        [--backend dotnet|python] [--frontend vue|uniapp] [--standards 规范源目录]

示例：
    python scaffold.py D:/projects/ecommerce --name "电商系统" --code-name "Ecommerce" --backend python --frontend uniapp
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(SCRIPT_DIR, "..", "templates")
SPLIT_SCRIPT = os.path.join(SCRIPT_DIR, "split-standards.py")

# ============ 技术栈 Profile ============
# 每个 profile 提供：渲染 token + 需要的 standards 文件（不含 always 的通用开发规范）。

API_CUSTOM_DOTNET = [
    ("Common/ApiResult.cs", "{cn}.Common/ApiResult.cs"),
    ("Common/PageResult.cs", "{cn}.Common/PageResult.cs"),
    ("Common/BusinessException.cs", "{cn}.Common/BusinessException.cs"),
    ("Api/Filters/GlobalExceptionFilter.cs", "{cn}.Api/Filters/GlobalExceptionFilter.cs"),
    ("Api/Program.cs", "{cn}.Api/Program.cs"),
    ("Api/appsettings.json", "{cn}.Api/appsettings.json"),
    ("Tests/Integration/IntegrationTestBase.cs", "tests/{cn}.Tests/Integration/IntegrationTestBase.cs"),
    ("README.md", "README.md"),
]

WEB_CUSTOM_VUE = [
    ("vite.config.ts", "vite.config.ts"),
    (".prettierrc.json", ".prettierrc.json"),
    (".prettierignore", ".prettierignore"),
    ("tsconfig.app.json", "tsconfig.app.json"),
    ("src/main.ts", "src/main.ts"),
    ("src/App.vue", "src/App.vue"),
    ("src/api/request.ts", "src/api/request.ts"),
    ("src/router/index.ts", "src/router/index.ts"),
    ("src/stores/user.ts", "src/stores/user.ts"),
    ("src/types/api.d.ts", "src/types/api.d.ts"),
    ("src/layouts/DefaultLayout.vue", "src/layouts/DefaultLayout.vue"),
    ("src/views/dashboard/DashboardView.vue", "src/views/dashboard/DashboardView.vue"),
    ("src/styles/variables.scss", "src/styles/variables.scss"),
    ("README.md", "README.md"),
]

BACKENDS = {
    "dotnet": {
        "label": ".NET 8 + ASP.NET Core Web API + SqlSugar + MySQL + JWT",
        "standards": ["后端开发规范.md", "Excel导出功能规范.md"],
        "tokens": {
            "{{BACKEND_STACK}}": ".NET 8 + ASP.NET Core Web API + SqlSugar 5.x + MySQL 8.0 + JWT Bearer + Serilog + Swagger",
            "{{BACKEND_SHORT}}": ".NET 8",
            "{{ORM}}": "SqlSugar",
            "{{ENVELOPE}}": "ApiResult<T> / PageResult<T>",
            "{{FIELD_MAPPING}}": "数据库 snake_case → 后端 C# PascalCase（`[SugarColumn(ColumnName=...)]` 映射）→ 前端 camelCase",
            "{{BACKEND_BUILD}}": "cd src/backend/api && dotnet build",
            "{{BACKEND_TEST}}": "cd src/backend/api && dotnet test",
            "{{BACKEND_LINT}}": "dotnet format",
            "{{TEST_FRAMEWORK}}": "xUnit + Moq（Mock SqlSugar 客户端）",
            "{{BACKEND_STANDARDS_FILE}}": ".claude/standards/后端开发规范.md",
        },
    },
    "python": {
        "label": "Python 3.10+ + FastAPI + SQLAlchemy 2.0 + Pydantic v2",
        "standards": ["Python后台开发规范_v0.1.md"],
        "tokens": {
            "{{BACKEND_STACK}}": "Python 3.10+ + FastAPI + SQLAlchemy 2.0 + Pydantic v2 + pydantic-settings + PyJWT + uvicorn + pytest",
            "{{BACKEND_SHORT}}": "Python (FastAPI)",
            "{{ORM}}": "SQLAlchemy",
            "{{ENVELOPE}}": "ApiResult / PageResult（app/schemas/common.py）",
            "{{FIELD_MAPPING}}": "数据库 snake_case → 后端 snake_case（SQLAlchemy 列/属性）→ 前端 camelCase（Pydantic 出参 alias / alias_generator）",
            "{{BACKEND_BUILD}}": "cd src/backend/api && python -m compileall app",
            "{{BACKEND_TEST}}": "cd src/backend/api && pytest",
            "{{BACKEND_LINT}}": "ruff check . && black --check .",
            "{{TEST_FRAMEWORK}}": "pytest + fastapi.testclient（TestClient + 依赖覆盖 mock DB 会话）",
            "{{BACKEND_STANDARDS_FILE}}": ".claude/standards/Python后台开发规范_v0.1.md",
        },
    },
}

FRONTS = {
    "vue": {
        "label": "Vue 3 + Element Plus + Pinia + Vite + TS",
        "standards": ["前端开发规范.md"],
        "tokens": {
            "{{FRONTEND_STACK}}": "Vue 3（Composition API + `<script setup>`）+ Element Plus + Pinia + Vue Router + Axios + Vite + TypeScript",
            "{{FRONTEND_SHORT}}": "Vue 3 + Element Plus",
            "{{UI_LIB}}": "Element Plus",
            "{{FRONTEND_STANDARDS_FILE}}": ".claude/standards/前端开发规范.md",
        },
    },
    "uniapp": {
        "label": "uni-app + Vue 3 + Pinia + TS（H5 + 微信小程序）",
        "standards": ["uni-app开发规范_v1.0.md", "移动端开发规范_v1.0.md"],
        "tokens": {
            "{{FRONTEND_STACK}}": "uni-app + Vue 3（Composition API）+ TypeScript + Pinia（H5 + 微信小程序，Vite 构建）",
            "{{FRONTEND_SHORT}}": "uni-app + Vue 3",
            "{{UI_LIB}}": "uni-app 内置组件（按需引入跨端 UI 库）",
            "{{FRONTEND_STANDARDS_FILE}}": ".claude/standards/uni-app开发规范_v1.0.md",
        },
    },
}

ALWAYS_STANDARDS = ["通用开发规范.md"]


# ============ 通用工具 ============
def copy_tree(src, dst):
    shutil.copytree(src, dst, dirs_exist_ok=True)


def render_text(content, mapping):
    for k, v in mapping.items():
        content = content.replace(k, v)
    return content


def render(src_path, mapping):
    with open(src_path, encoding="utf-8") as f:
        return render_text(f.read(), mapping)


def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)


def to_kebab(name):
    """PascalCase → kebab-case"""
    return re.sub(r"(?<!^)(?=[A-Z])", "-", name).lower()


def run(cmd, cwd, desc=""):
    if desc:
        print(f"  ... {desc}")
    if isinstance(cmd, (list, tuple)):
        cmd = subprocess.list2cmdline(cmd) if hasattr(subprocess, "list2cmdline") else " ".join(cmd)
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, errors="replace", shell=True)
    if r.returncode != 0:
        print(f"  [警告] 失败: {cmd.split()[0] if cmd.split() else cmd}...")
        if r.stderr.strip():
            print(f"         {r.stderr.strip().splitlines()[-1][:160]}")
    return r.returncode == 0


def ask_choice(flag, question, registry, default_key):
    """命令行优先：flag 非 None 且合法则直接用；TTY 下交互式询问；非 TTY 且未提供则报错退出。"""
    if flag is not None:
        if flag in registry:
            return flag
        print(f"[错误] --{flag_name(flag)} 值无效：{flag}，可选：{', '.join(registry)}")
        sys.exit(2)
    if not sys.stdin.isatty():
        print(f"[错误] 未指定 --{question}，且当前非交互终端，无法询问。请显式传参。")
        sys.exit(2)
    print(f"\n请选择【{question}】：")
    keys = list(registry.keys())
    for i, k in enumerate(keys, 1):
        star = " （默认）" if k == default_key else ""
        print(f"  {i}. {k:<8} — {registry[k]['label']}{star}")
    while True:
        raw = input("输入序号或名称（回车取默认 " + default_key + "）：").strip().lower()
        if raw == "":
            return default_key
        if raw.isdigit() and 1 <= int(raw) <= len(keys):
            return keys[int(raw) - 1]
        if raw in registry:
            return raw
        print("  无效输入，请重试。")


def flag_name(_):  # 保留占位，简化调用
    return "choice"


# ============ .claude 复制 + 渲染（不含 standards） ============
def copy_claude_rendered(target, mapping):
    src = os.path.join(TEMPLATE_DIR, ".claude")
    dst = os.path.join(target, ".claude")
    for entry in os.listdir(src):
        if entry == "standards":
            continue  # standards 按 profile 单独处理
        s = os.path.join(src, entry)
        d = os.path.join(dst, entry)
        if entry in ("agents", "commands"):
            os.makedirs(d, exist_ok=True)
            for f in os.listdir(s):
                content = render(os.path.join(s, f), mapping)
                write(os.path.join(d, f), content)
        elif os.path.isdir(s):
            copy_tree(s, d)
        else:
            os.makedirs(os.path.dirname(d), exist_ok=True)
            shutil.copy2(s, d)
    print("  [OK] 复制并渲染 .claude/（agents+commands 按技术栈渲染，settings/hooks）")


def copy_standards_subset(target, backend, frontend, override_dir):
    std_dir = os.path.join(target, ".claude", "standards")
    if override_dir and os.path.isdir(override_dir):
        copy_tree(override_dir, std_dir)
        print(f"  [OK] 从 {override_dir} 覆盖开发规范")
    else:
        os.makedirs(std_dir, exist_ok=True)
        tpl_std = os.path.join(TEMPLATE_DIR, ".claude", "standards")
        chosen = ALWAYS_STANDARDS + BACKENDS[backend]["standards"] + FRONTS[frontend]["standards"]
        # 去重且只取存在的
        seen = []
        for name in chosen:
            if name not in seen and os.path.isfile(os.path.join(tpl_std, name)):
                seen.append(name)
        for name in seen:
            shutil.copy2(os.path.join(tpl_std, name), os.path.join(std_dir, name))
        readme = os.path.join(tpl_std, "README.md")
        if os.path.isfile(readme):
            shutil.copy2(readme, os.path.join(std_dir, "README.md"))
        print(f"  [OK] 载入技术栈相关规范：{', '.join(seen)}")
    # 重生成 topics（只针对被选中的规范）
    if os.path.isfile(SPLIT_SCRIPT):
        run(["python", SPLIT_SCRIPT, std_dir], target, "生成规范 topics 索引")


# ============ 后端工程 ============
def init_api_dotnet(target, code_name):
    api_dir = os.path.join(target, "src", "backend", "api")
    os.makedirs(api_dir, exist_ok=True)
    run(["dotnet", "new", "sln", "-n", code_name], api_dir, "创建解决方案")
    run(["dotnet", "new", "classlib", "-n", f"{code_name}.Common", "-f", "net8.0"], api_dir, "创建 Common/Model/Service 类库")
    run(["dotnet", "new", "classlib", "-n", f"{code_name}.Model", "-f", "net8.0"], api_dir)
    run(["dotnet", "new", "classlib", "-n", f"{code_name}.Service", "-f", "net8.0"], api_dir)
    run(["dotnet", "new", "webapi", "-n", f"{code_name}.Api", "-f", "net8.0", "--use-controllers"], api_dir, "创建 Api 项目")
    os.makedirs(os.path.join(api_dir, "tests"), exist_ok=True)
    run(["dotnet", "new", "xunit", "-n", f"{code_name}.Tests", "-f", "net8.0", "-o", f"tests/{code_name}.Tests"], api_dir, "创建测试项目")
    run(["dotnet", "sln", "add", f"{code_name}.Common", f"{code_name}.Model", f"{code_name}.Service", f"{code_name}.Api", f"tests/{code_name}.Tests"], api_dir, "加入解决方案")
    run(["dotnet", "add", f"{code_name}.Api/{code_name}.Api.csproj", "reference",
         f"{code_name}.Service/{code_name}.Service.csproj", f"{code_name}.Model/{code_name}.Model.csproj", f"{code_name}.Common/{code_name}.Common.csproj"], api_dir, "添加 Api 引用")
    run(["dotnet", "add", f"{code_name}.Service/{code_name}.Service.csproj", "reference",
         f"{code_name}.Model/{code_name}.Model.csproj", f"{code_name}.Common/{code_name}.Common.csproj"], api_dir)
    run(["dotnet", "add", f"tests/{code_name}.Tests/{code_name}.Tests.csproj", "reference",
         f"{code_name}.Api/{code_name}.Api.csproj", f"{code_name}.Service/{code_name}.Service.csproj", f"{code_name}.Model/{code_name}.Model.csproj"], api_dir)
    run(["dotnet", "add", f"tests/{code_name}.Tests/{code_name}.Tests.csproj", "package", "Microsoft.AspNetCore.Mvc.Testing"], api_dir, "添加集成测试包")
    for f in [f"{code_name}.Api/WeatherForecast.cs", f"{code_name}.Api/{code_name}.Api.http",
              f"{code_name}.Api/Controllers/WeatherForecastController.cs", f"{code_name}.Common/Class1.cs",
              f"{code_name}.Model/Class1.cs", f"{code_name}.Service/Class1.cs", f"tests/{code_name}.Tests/UnitTest1.cs"]:
        p = os.path.join(api_dir, f)
        if os.path.exists(p):
            os.remove(p)
    for src_rel, dst_rel in API_CUSTOM_DOTNET:
        content = render(os.path.join(TEMPLATE_DIR, "code", "api", src_rel), {"{{CodeName}}": code_name})
        write(os.path.join(api_dir, dst_rel.format(cn=code_name)), content)
    for d in ["Entities", "DTOs/Request", "DTOs/Response", "Enums"]:
        os.makedirs(os.path.join(api_dir, f"{code_name}.Model", d), exist_ok=True)
    for d in ["Interfaces", "Implementations"]:
        os.makedirs(os.path.join(api_dir, f"{code_name}.Service", d), exist_ok=True)
    for d in ["Filters", "Extensions"]:
        os.makedirs(os.path.join(api_dir, f"{code_name}.Api", d), exist_ok=True)
    for d in ["Services", "Helpers"]:
        os.makedirs(os.path.join(api_dir, "tests", f"{code_name}.Tests", d), exist_ok=True)
    mig = os.path.join(api_dir, "sql", "migrations")
    os.makedirs(mig, exist_ok=True)
    shutil.copy2(os.path.join(TEMPLATE_DIR, "code", "api", "sql-migrations", "README.md"), os.path.join(mig, "README.md"))
    print(f"  [OK] API 工程 {code_name} 生成完成（.NET 8 分层 + 迁移目录）")


def init_api_python(target, code_name):
    """按 Python 后台开发规范生成 FastAPI + SQLAlchemy 结构骨架。"""
    api = os.path.join(target, "src", "backend", "api")
    app = os.path.join(api, "app")
    pkgs = ["", "api", "api/routes", "schemas", "models", "services", "core", "tasks"]
    for p in pkgs:
        d = os.path.join(app, p) if p else app
        os.makedirs(d, exist_ok=True)
        write(os.path.join(d, "__init__.py"), "")
    for p in ["tests", "scripts"]:
        d = os.path.join(api, p)
        os.makedirs(d, exist_ok=True)
        write(os.path.join(d, "__init__.py"), "")
    os.makedirs(os.path.join(api, "data"), exist_ok=True)

    write(os.path.join(api, "requirements.txt"),
"""fastapi>=0.115
uvicorn[standard]>=0.30
sqlalchemy>=2.0
pydantic>=2.7
pydantic-settings>=2.3
PyJWT>=2.8
passlib>=1.7.4
httpx>=0.27
pytest>=8.2
python-multipart>=0.0.9
""")

    write(os.path.join(app, "config.py"),
'''"""全局配置（pydantic-settings）与路径常量。"""
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BACKEND_DIR / "data"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BACKEND_DIR / ".env", extra="ignore")

    APP_NAME: str = "{name}"
    DATABASE_URL: str = "sqlite:///" + str(DATA_DIR / "app.db")
    JWT_SECRET: str = "change-me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120


settings = Settings()
'''.format(name=code_name))

    write(os.path.join(app, "database.py"),
'''"""engine / SessionLocal / get_db 依赖。"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.models.base import Base

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
''')

    write(os.path.join(app, "models", "base.py"),
'''"""ORM 基类与公共 Mixin。"""
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class TenantMixin:
    """多租户红线：所有业务表继承本 Mixin，携带 tenant_id。"""

    tenant_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
''')

    write(os.path.join(app, "schemas", "common.py"),
'''"""统一响应信封：ApiResult / PageResult。"""
from typing import Generic, List, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class ApiResult(BaseModel, Generic[T]):
    code: int = 0
    message: str = "ok"
    data: T | None = None

    @classmethod
    def ok(cls, data: T | None = None) -> "ApiResult[T]":
        return cls(code=0, message="ok", data=data)


class PageResult(BaseModel, Generic[T]):
    """分页信封：items / total / pageIndex / pageSize。"""

    model_config = ConfigDict(populate_by_name=True)

    items: List[T] = []
    total: int = 0
    page_index: int = 1
    page_size: int = 20


class CamelModel(BaseModel):
    """前端 camelCase 出参基类：DB/后端 snake_case → 响应 camelCase。"""

    model_config = ConfigDict(alias_generator=lambda s: "".join(
        w.capitalize() if i else w for i, w in enumerate(s.split("_"))),
        populate_by_name=True, from_attributes=True)
''')

    write(os.path.join(app, "core", "security.py"),
'''"""安全能力：JWT 签发/校验、密码哈希。"""
from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext

from app.config import settings

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(raw: str) -> str:
    return pwd_context.hash(raw)


def verify_password(raw: str, hashed: str) -> bool:
    return pwd_context.verify(raw, hashed)


def create_access_token(subject: str, tenant_id: int, expires_minutes: int | None = None) -> str:
    exp = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": subject, "tenant_id": tenant_id, "exp": exp}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
''')

    write(os.path.join(app, "main.py"),
'''"""应用入口：日志装配、中间件、路由挂载、健康检查。"""
from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.config import settings

app = FastAPI(title=settings.APP_NAME)

app.include_router(health_router, prefix="/api")


@app.get("/health", tags=["health"])
def health() -> dict:
    return {"status": "ok", "app": settings.APP_NAME}
''')

    write(os.path.join(app, "api", "routes", "health.py"),
'''"""健康检查路由示例。"""
from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/ping")
def ping() -> dict:
    return {"pong": True}
''')

    write(os.path.join(api, "pytest.ini"),
"""[pytest]
pythonpath = .
testpaths = tests
""")

    write(os.path.join(api, "conftest.py"),
'''"""pytest 公共 fixture：TestClient。"""
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)
''')

    write(os.path.join(api, ".env.example"),
"""APP_NAME=App
DATABASE_URL=sqlite:///./data/app.db
JWT_SECRET=change-me-in-prod
ACCESS_TOKEN_EXPIRE_MINUTES=120
""")

    # gitignore 追加（data/.env/__pycache__）
    gi = os.path.join(api, ".gitignore")
    write(gi, "__pycache__/\n*.pyc\n.pytest_cache/\ndata/\n.env\n")

    print(f"  [OK] API 工程 {code_name} 生成完成（FastAPI + SQLAlchemy 结构骨架）")


# ============ 前端工程 ============
def init_web_vue(target, code_name, name, desc):
    web_dir = os.path.join(target, "src", "backend", "web")
    os.makedirs(web_dir, exist_ok=True)
    kebab = to_kebab(code_name)
    run(["npm", "exec", "--yes", "--", "create-vite@latest", kebab, "--", "--template", "vue-ts"], web_dir, "创建 Vue 3 + TS 工程")
    tmp = os.path.join(web_dir, kebab)
    if os.path.isdir(tmp):
        for item in os.listdir(tmp):
            shutil.move(os.path.join(tmp, item), web_dir)
        shutil.rmtree(tmp)
    run(["npm", "install"], web_dir, "安装基础依赖（可能较慢）")
    run(["npm", "install", "vue-router@4", "pinia", "element-plus", "axios"], web_dir, "安装 vue-router/pinia/element-plus/axios")
    run(["npm", "install", "-D", "sass", "swagger-typescript-api", "prettier"], web_dir, "安装 sass + swagger-typescript-api + prettier")
    pkg_path = os.path.join(web_dir, "package.json")
    try:
        with open(pkg_path, encoding="utf-8") as f:
            pkg = json.load(f)
        scripts = pkg.setdefault("scripts", {})
        scripts["gen:api"] = ("swagger-typescript-api -p http://localhost:8080/swagger/v1/swagger.json "
                              "-o ./src/types -n api-generated.ts --extract-request-params --axios")
        scripts["format"] = "prettier --write src"
        scripts["format:check"] = "prettier --check src"
        with open(pkg_path, "w", encoding="utf-8") as f:
            json.dump(pkg, f, ensure_ascii=False, indent=2)
        print("  [OK] 已注入 gen:api 类型生成脚本")
    except Exception as e:
        print(f"  [警告] 注入 gen:api 失败: {e}")
    for f in ["src/components/HelloWorld.vue", "src/style.css", "src/assets"]:
        p = os.path.join(web_dir, f)
        if os.path.isdir(p):
            shutil.rmtree(p, ignore_errors=True)
        elif os.path.exists(p):
            os.remove(p)
    mapping = {"{{PROJECT_NAME}}": name, "{{PROJECT_DESC}}": desc, "{{codeName}}": kebab}
    for src_rel, dst_rel in WEB_CUSTOM_VUE:
        content = render(os.path.join(TEMPLATE_DIR, "code", "web", src_rel), mapping)
        write(os.path.join(web_dir, dst_rel), content)
    for d in ["components", "mock/modules", "utils"]:
        os.makedirs(os.path.join(web_dir, "src", d), exist_ok=True)
    print(f"  [OK] Web 工程 {kebab} 生成完成（Vue 3 + Element Plus）")


def init_web_uniapp(target, code_name, name, desc):
    """优先 degit 官方 uni-preset-vue#vite-ts；不可用/失败则降级写结构骨架。"""
    web_dir = os.path.join(target, "src", "backend", "web")
    os.makedirs(web_dir, exist_ok=True)
    ok = run(["npx", "--yes", "degit", "dcloudio/uni-preset-vue#vite-ts", web_dir, "--force"], web_dir,
             "degit 初始化 uni-app（Vue3 + Vite + TS 官方预设）")
    has_pkg = os.path.isfile(os.path.join(web_dir, "package.json"))
    if not has_pkg:
        print("  [降级] 未能拉取官方预设（可能无网络），生成最小结构骨架，稍后可手动 `npx degit dcloudio/uni-preset-vue#vite-ts .` 覆盖")
        write(os.path.join(web_dir, "package.json"), json.dumps({
            "name": to_kebab(code_name), "version": "0.1.0", "private": True,
            "scripts": {"dev:h5": "uni", "build:h5": "uni build", "dev:mp-weixin": "uni -p mp-weixin",
                        "build:mp-weixin": "uni build -p mp-weixin"},
            "dependencies": {"@dcloudio/uni-app": "3.0.0-4020920240930001", "vue": "^3.4.21", "pinia": "^2.1.7"},
            "devDependencies": {"@dcloudio/vite-plugin-uni": "3.0.0-4020920240930001", "typescript": "^5.4.0", "vite": "^5.2.0"},
        }, ensure_ascii=False, indent=2))
    for d in ["src/pages/index", "src/api", "src/stores", "src/types", "src/utils"]:
        os.makedirs(os.path.join(web_dir, *d.split("/")), exist_ok=True)
    pages = os.path.join(web_dir, "src", "pages.json")
    if not os.path.exists(pages):
        write(pages, json.dumps({
            "pages": [{"path": "pages/index/index", "style": {"navigationBarTitleText": name}}],
            "globalStyle": {"navigationBarTextStyle": "black", "navigationBarTitleText": name,
                            "navigationBarBackgroundColor": "#F8F8F8", "backgroundColor": "#F8F8F8"},
        }, ensure_ascii=False, indent=2))
    manifest = os.path.join(web_dir, "src", "manifest.json")
    if not os.path.exists(manifest):
        write(manifest, json.dumps({"name": name, "appid": "", "versionName": "0.1.0",
                                    "versionCode": "1", "h5": {"router": {"mode": "hash"}}}, ensure_ascii=False, indent=2))
    print(f"  [OK] uni-app 工程生成（H5 + 微信小程序）")


# ============ 部署 CI / Docker（按栈变体） ============
def _variant(dep_dir, base, suffix):
    """优先取 <base>.<suffix> 变体文件，不存在则回退 <base>（base 可含子目录）。"""
    v = os.path.join(dep_dir, f"{base}.{suffix}")
    return v if os.path.isfile(v) else os.path.join(dep_dir, base)


def init_deploy(target, code_name, backend, frontend):
    dep = os.path.join(TEMPLATE_DIR, "code", "deploy")

    # CI（按后端栈选变体）
    ci_src = _variant(dep, os.path.join("workflows", "ci.yml"), backend)
    ci_dst = os.path.join(target, ".github", "workflows", "ci.yml")
    os.makedirs(os.path.dirname(ci_dst), exist_ok=True)
    shutil.copy2(ci_src, ci_dst)

    # Dockerfile.api（后端变体）+ 代码名渲染
    docker_api_src = _variant(dep, "Dockerfile.api", backend)
    write(os.path.join(target, "src", "backend", "api", "Dockerfile.api"),
          render(docker_api_src, {"{{CodeName}}": code_name}))

    # Dockerfile.web（前端变体）
    docker_web_src = _variant(dep, "Dockerfile.web", frontend)
    os.makedirs(os.path.join(target, "src", "backend", "web"), exist_ok=True)
    shutil.copy2(docker_web_src, os.path.join(target, "src", "backend", "web", "Dockerfile.web"))

    shutil.copy2(os.path.join(dep, "docker-compose.yml"), os.path.join(target, "docker-compose.yml"))
    shutil.copy2(os.path.join(dep, "dependabot.yml"), os.path.join(target, ".github", "dependabot.yml"))
    print("  [OK] 部署文件生成（CI + Dockerfile x2 + compose + dependabot）")


def init_git(target):
    if not shutil.which("git"):
        print("  [跳过] 未检测到 git，跳过仓库初始化")
        return
    run(["git", "init"], target, "初始化 git 仓库")
    run(["git", "add", "-A"], target, "暂存全部文件")
    if run(["git", "commit", "-m", "chore: 初始化项目脚手架"], target, "创建初始提交"):
        print("  [OK] git 仓库初始化完成（含初始提交）")
    else:
        print("  [提示] 初始提交失败（可能未配置 git user.name/email），仓库已建好，可稍后手动提交")


# ============ 主流程 ============
def main():
    parser = argparse.ArgumentParser(description="Claude Code 多 Agent 项目脚手架生成器（混合式 · 可配置技术栈）")
    parser.add_argument("target", help="目标项目目录")
    parser.add_argument("--name", default="新项目", help="项目名称（中文显示名）")
    parser.add_argument("--desc", default="", help="项目一句话描述")
    parser.add_argument("--code-name", default="App", help="代码工程名（英文 PascalCase，默认 App）")
    parser.add_argument("--backend", default=None, choices=list(BACKENDS.keys()), help="后端技术栈：dotnet|python")
    parser.add_argument("--frontend", default=None, choices=list(FRONTS.keys()), help="前端技术栈：vue|uniapp")
    parser.add_argument("--standards", default="", help="自定义开发规范源目录（可选），覆盖 .claude/standards/")
    args = parser.parse_args()

    target = os.path.abspath(args.target)
    name = args.name
    desc = args.desc if args.desc else "TODO: 一句话描述项目"
    code_name = args.code_name

    backend = args.backend or ask_choice(args.backend, "后端技术栈 backend", BACKENDS, "dotnet")
    frontend = args.frontend or ask_choice(args.frontend, "前端技术栈 frontend", FRONTS, "vue")

    mapping = {"{{PROJECT_NAME}}": name, "{{PROJECT_DESC}}": desc, "{{codeName}}": to_kebab(code_name), "{{CodeName}}": code_name}
    mapping.update(BACKENDS[backend]["tokens"])
    mapping.update(FRONTS[frontend]["tokens"])

    print(f"初始化多 Agent 项目: {target}")
    print(f"  项目名: {name}  代码名: {code_name}")
    print(f"  技术栈: 后端={backend}  前端={frontend}")

    # ===== 静态模板（.claude 渲染 / docs / CLAUDE.md / README / 根文件） =====
    copy_claude_rendered(target, mapping)
    copy_tree(os.path.join(TEMPLATE_DIR, "docs"), os.path.join(target, "docs"))
    print("  [OK] 复制 docs/（00-项目文档 md 模板 + README 三轨规范 + common.css + md2html.py + _模板与规范）")
    write(os.path.join(target, "CLAUDE.md"), render(os.path.join(TEMPLATE_DIR, "CLAUDE.md"), mapping))
    print("  [OK] 生成 CLAUDE.md（已注入所选技术栈）")
    write(os.path.join(target, "README.md"), render(os.path.join(TEMPLATE_DIR, "README.md"), mapping))
    print("  [OK] 生成 README.md")
    for f in [".mcp.json", ".gitignore", ".editorconfig", ".gitattributes"]:
        shutil.copy2(os.path.join(TEMPLATE_DIR, f), os.path.join(target, f))
    print("  [OK] 生成 .mcp.json / .gitignore / .editorconfig / .gitattributes")

    # ===== standards 子集 + topics =====
    copy_standards_subset(target, backend, frontend, args.standards.strip())

    # ===== 代码工程（按栈） =====
    print("\n[代码工程]")
    {"dotnet": init_api_dotnet, "python": init_api_python}[backend](target, code_name)
    {"vue": lambda t, cn: init_web_vue(t, cn, name, desc),
     "uniapp": lambda t, cn: init_web_uniapp(t, cn, name, desc)}[frontend](target, code_name)
    init_deploy(target, code_name, backend, frontend)

    # ===== 残留占位符自检 =====
    leftovers = []
    for root, _, files in os.walk(os.path.join(target, ".claude")):
        for fn in files:
            if fn.endswith(".md"):
                txt = open(os.path.join(root, fn), encoding="utf-8").read()
                if "{{" in txt:
                    leftovers.append(os.path.relpath(os.path.join(root, fn), target))
    if leftovers:
        print("  [警告] 以下文件仍有未渲染占位符 {{...}}，请检查 token 定义：")
        for f in leftovers:
            print("        ", f)

    # ===== git =====
    print("\n[git 仓库]")
    init_git(target)

    print("\n========== 完成 ==========")
    print(f"技术栈：后端 {BACKENDS[backend]['label']} / 前端 {FRONTS[frontend]['label']}")
    print("下一步：")
    print("  1. 填写 CLAUDE.md 中的业务 TODO（项目速览、红线）")
    print(f"  2. 后端：{BACKENDS[backend]['tokens']['{{BACKEND_BUILD}}']}")
    print(f"  3. 前端：cd src/backend/web && npm install && npm run dev:h5" if frontend == "uniapp"
          else "  3. 前端：cd src/backend/web && npm run dev")
    print("  4. cd 到项目根目录，运行 claude；输入 /product-discovery 开始")
    print("  5. 关联远程仓库：git remote add origin <地址> && git push -u origin main")


if __name__ == "__main__":
    main()
