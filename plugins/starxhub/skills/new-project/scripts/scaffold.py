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

# Rules 分发配置：始终加载的通用规则
ALWAYS_RULES = ["workflow.md", "database.md", "git.md"]

BACKENDS = {
    "dotnet": {
        "label": ".NET 8 + ASP.NET Core Web API + SqlSugar + MySQL + JWT",
        "standards": ["后端开发规范.md", "Excel导出功能规范.md"],
        "rules": {
            "backend-api.dotnet.md": "backend-api.md",
            "backend-domain.dotnet.md": "backend-domain.md",
            "backend-infra.dotnet.md": "backend-infra.md",
        },
        "tokens": {
            "{{BACKEND_STACK}}": ".NET 8 + ASP.NET Core Web API + SqlSugar 5.x + MySQL 8.0 + JWT Bearer + Serilog + Swagger",
            "{{BACKEND_SHORT}}": ".NET 8",
            "{{ORM}}": "SqlSugar",
            "{{ENVELOPE}}": "ApiResult<T> / PageResult<T>",
            "{{BACKEND_ORIGIN}}": "http://127.0.0.1:5157",
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
        "rules": {
            "backend-api.python.md": "backend-api.md",
            "backend-domain.python.md": "backend-domain.md",
            "backend-infra.python.md": "backend-infra.md",
        },
        "tokens": {
            "{{BACKEND_STACK}}": "Python 3.10+ + FastAPI + SQLAlchemy 2.0 + Pydantic v2 + pydantic-settings + PyJWT + uvicorn + pytest",
            "{{BACKEND_SHORT}}": "Python (FastAPI)",
            "{{ORM}}": "SQLAlchemy",
            "{{ENVELOPE}}": "RESTful：业务错误 raise BusinessException（HTTP 状态码），列表分页 Page{items,total,page,size}",
            "{{BACKEND_ORIGIN}}": "http://127.0.0.1:8000",
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
        "rules": {
            "frontend-pages.vue.md": "frontend-pages.md",
            "frontend-state.vue.md": "frontend-state.md",
        },
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
        "rules": {
            "frontend-pages.uniapp.md": "frontend-pages.md",
            "frontend-state.uniapp.md": "frontend-state.md",
        },
        "tokens": {
            "{{FRONTEND_STACK}}": "uni-app + Vue 3（Composition API）+ TypeScript + Pinia（H5 + 微信小程序，Vite 构建）",
            "{{FRONTEND_SHORT}}": "uni-app + Vue 3",
            "{{UI_LIB}}": "uni-app 内置组件（按需引入跨端 UI 库）",
            "{{FRONTEND_STANDARDS_FILE}}": ".claude/standards/uni-app开发规范_v1.0.md",
        },
    },
}

ALWAYS_STANDARDS = ["通用开发规范.md"]
TEXT_EXT = (".py", ".ts", ".vue", ".js", ".json", ".scss", ".css", ".md", ".ini", ".txt", ".example")

# ============ 本地质量门禁（scripts/ci.sh）：fmt + build + test + 前端构建 ============
CI_BACKEND_CMDS = {
    "dotnet": 'cd "$ROOT/src/backend/api"\n'
              'echo "  · dotnet format（风格检查）"; dotnet format --verify-no-changes\n'
              'echo "  · dotnet build"; dotnet build --nologo\n'
              'echo "  · dotnet test"; dotnet test --nologo',
    "python": 'cd "$ROOT/src/backend/api"\n'
              'echo "  · 语法编译"; python -m compileall -q app\n'
              'command -v ruff >/dev/null && { echo "  · ruff"; ruff check .; }\n'
              'command -v black >/dev/null && { echo "  · black"; black --check .; }\n'
              'echo "  · pytest"; pytest -q',
}
CI_FRONTEND_CMDS = {
    "vue": 'cd "$ROOT/src/backend/web"\n'
           '[ -f package-lock.json ] && npm ci || npm install\n'
           'command -v npx >/dev/null && { echo "  · prettier"; npx prettier --check src || true; }\n'
           'echo "  · 前端构建"; npm run build',
    "uniapp": 'cd "$ROOT/src/backend/web"\n'
              '[ -f package-lock.json ] && npm ci || npm install\n'
              'echo "  · 前端构建（H5）"; npm run build:h5 || npm run build',
}


def write_ci_scripts(target, backend, frontend):
    """生成本地优先的统一门禁：scripts/ci.sh + .githooks/pre-push（推送前本地跑，不依赖远端）。"""
    be_cmd = CI_BACKEND_CMDS[backend]
    fe_cmd = CI_FRONTEND_CMDS[frontend]
    bshort = BACKENDS[backend]["label"].split(" + ")[0]
    fshort = FRONTS[frontend]["label"].split("（")[0]
    ci_sh = (
        "#!/usr/bin/env bash\n"
        "# 本地优先的统一质量门禁：后端 fmt+build+test + 前端 install+build。\n"
        "# 本地、git 钩子、远端 CI 都调用它 —— 门禁即脚本，不依赖任何远端。\n"
        "set -euo pipefail\n"
        'ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"\n\n'
        'echo "==> [1/2] 后端：' + bshort + ' fmt + build + test"\n' + be_cmd + "\n\n"
        'echo "==> [2/2] 前端：' + fshort + ' 构建"\n' + fe_cmd + "\n\n"
        'echo "==> 全部通过 ✅"\n'
    )
    pre_push = (
        "#!/usr/bin/env bash\n"
        "# git pre-push 钩子：推送前本地执行 scripts/ci.sh，真正挡住坏提交，且不依赖任何远端 CI。\n"
        "set -euo pipefail\n"
        'ROOT="$(git rev-parse --show-toplevel)"\n'
        'exec bash "$ROOT/scripts/ci.sh"\n'
    )
    ci_path = os.path.join(target, "scripts", "ci.sh")
    hook_path = os.path.join(target, ".githooks", "pre-push")
    write(ci_path, ci_sh)
    write(hook_path, pre_push)
    for p in (ci_path, hook_path):
        try:
            os.chmod(p, 0o755)
        except OSError:
            pass
    print("  [OK] 生成本地门禁 scripts/ci.sh + git pre-push 钩子")


# ============ 通用工具 ============
def copy_tree(src, dst):
    shutil.copytree(src, dst, dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))


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


def copy_tree_render(src_dir, dst_dir, mapping):
    """递归拷贝模板目录，文本文件按 mapping 渲染占位符；跳过 __pycache__/.pyc。"""
    for base, dirs, files in os.walk(src_dir):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        rel = os.path.relpath(base, src_dir)
        target_base = dst_dir if rel == "." else os.path.join(dst_dir, rel)
        os.makedirs(target_base, exist_ok=True)
        for fn in files:
            if fn.endswith(".pyc"):
                continue
            src = os.path.join(base, fn)
            dst = os.path.join(target_base, fn)
            if fn.endswith(TEXT_EXT):
                try:
                    write(dst, render(src, mapping))
                    continue
                except (UnicodeDecodeError, OSError):
                    pass
            shutil.copy2(src, dst)


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
        if entry in ("standards", "rules"):
            continue  # standards 按 profile 单独处理；rules 按技术栈由 copy_rules 处理
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
    """复制技术栈相关的 standards 文件到目标项目"""
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


def copy_rules(target, backend, frontend, mapping):
    """按技术栈复制并渲染 rules 文件到目标项目"""
    rules_dir = os.path.join(target, ".claude", "rules")
    os.makedirs(rules_dir, exist_ok=True)
    
    tpl_rules = os.path.join(TEMPLATE_DIR, ".claude", "rules")
    copied = []
    
    # 1. 复制 _always 目录下的通用规则（始终加载）
    always_src = os.path.join(tpl_rules, "_always")
    if os.path.isdir(always_src):
        for rule_file in ALWAYS_RULES:
            src = os.path.join(always_src, rule_file)
            if os.path.isfile(src):
                dst = os.path.join(rules_dir, rule_file)
                content = render(src, mapping)
                write(dst, content)
                copied.append(rule_file)
    
    # 2. 复制后端 rules（按技术栈选择）
    backend_rules = BACKENDS[backend].get("rules", {})
    backend_src = os.path.join(tpl_rules, "_backend")
    if os.path.isdir(backend_src):
        for src_name, dst_name in backend_rules.items():
            src = os.path.join(backend_src, src_name)
            if os.path.isfile(src):
                dst = os.path.join(rules_dir, dst_name)
                content = render(src, mapping)
                write(dst, content)
                copied.append(dst_name)
    
    # 3. 复制前端 rules（按技术栈选择）
    frontend_rules = FRONTS[frontend].get("rules", {})
    frontend_src = os.path.join(tpl_rules, "_frontend")
    if os.path.isdir(frontend_src):
        for src_name, dst_name in frontend_rules.items():
            src = os.path.join(frontend_src, src_name)
            if os.path.isfile(src):
                dst = os.path.join(rules_dir, dst_name)
                content = render(src, mapping)
                write(dst, content)
                copied.append(dst_name)
    
    print(f"  [OK] 生成 {len(copied)} 个 rules 文件（自动触发）：{', '.join(copied)}")


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


def init_api_python(target, code_name, mapping):
    """按 Python 后台开发规范生成 FastAPI + SQLAlchemy 基础设施（租户上下文/过滤器、JWT 依赖、异常处理、conftest）。"""
    api = os.path.join(target, "src", "backend", "api")
    tpl = os.path.join(TEMPLATE_DIR, "code", "api-python")
    copy_tree_render(tpl, api, mapping)
    os.makedirs(os.path.join(api, "data"), exist_ok=True)
    write(os.path.join(api, ".gitignore"), "__pycache__/\n*.pyc\n.pytest_cache/\ndata/\n.env\n.venv/\n")
    print(f"  [OK] API 工程 {code_name} 生成完成（FastAPI + SQLAlchemy + 租户基础设施）")


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


def init_web_uniapp(target, code_name, name, desc, mapping):
    """优先 degit 官方 uni-preset-vue#vite-ts，再用 uni-app 基础设施模板覆盖。无网络则仅写骨架。"""
    web_dir = os.path.join(target, "src", "backend", "web")
    os.makedirs(web_dir, exist_ok=True)
    run(["npx", "--yes", "degit", "dcloudio/uni-preset-vue#vite-ts", web_dir, "--force"], web_dir,
        "degit 初始化 uni-app（Vue3 + Vite + TS 官方预设）")
    if not os.path.isfile(os.path.join(web_dir, "package.json")):
        print("  [提示] 未取到官方预设（可能无网络）；已写入结构骨架，稍后可 `npx degit dcloudio/uni-preset-vue#vite-ts .` 覆盖")
    tpl = os.path.join(TEMPLATE_DIR, "code", "web-uniapp")
    copy_tree_render(tpl, web_dir, mapping)
    print(f"  [OK] uni-app 工程生成（H5 + 微信小程序 基础设施已就位）")


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
    run(["git", "config", "core.hooksPath", ".githooks"], target, "启用仓库内 .githooks（pre-push 门禁）")
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

    # ===== rules 自动触发规则（按技术栈选择） =====
    copy_rules(target, backend, frontend, mapping)

    # ===== 代码工程（按栈） =====
    print("\n[代码工程]")
    if backend == "dotnet":
        init_api_dotnet(target, code_name)
    else:
        init_api_python(target, code_name, mapping)
    if frontend == "vue":
        init_web_vue(target, code_name, name, desc)
    else:
        init_web_uniapp(target, code_name, name, desc, mapping)
    init_deploy(target, code_name, backend, frontend)

    # 本地优先质量门禁（scripts/ci.sh + git pre-push）
    write_ci_scripts(target, backend, frontend)

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
