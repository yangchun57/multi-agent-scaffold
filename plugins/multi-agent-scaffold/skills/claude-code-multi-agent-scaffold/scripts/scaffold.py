#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Claude Code 多 Agent 项目脚手架生成器（混合式）。

设计：CLI 生成正确命名的骨架（dotnet new / npm create vite），模板补充自定义基础设施。

用法：
    python scaffold.py <目标目录> [--name 项目名] [--desc 描述] [--code-name 代码名] [--standards 规范源目录]

示例：
    python scaffold.py D:/projects/ecommerce --name "电商系统" --desc "B2C 电商平台" --code-name "Ecommerce"
"""

import argparse
import os
import re
import shutil
import subprocess

TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "templates")

# ============ 自定义文件（模板 → 目标，相对各自的工程根） ============
API_CUSTOM = [
    ("Common/ApiResult.cs", "{cn}.Common/ApiResult.cs"),
    ("Common/PageResult.cs", "{cn}.Common/PageResult.cs"),
    ("Common/BusinessException.cs", "{cn}.Common/BusinessException.cs"),
    ("Api/Filters/GlobalExceptionFilter.cs", "{cn}.Api/Filters/GlobalExceptionFilter.cs"),
    ("Api/Program.cs", "{cn}.Api/Program.cs"),
    ("Api/appsettings.json", "{cn}.Api/appsettings.json"),
    ("Tests/Integration/IntegrationTestBase.cs", "tests/{cn}.Tests/Integration/IntegrationTestBase.cs"),
    ("README.md", "README.md"),
]

WEB_CUSTOM = [
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


def copy_tree(src, dst):
    shutil.copytree(src, dst, dirs_exist_ok=True)


def render(src_path, mapping):
    with open(src_path, encoding="utf-8") as f:
        content = f.read()
    for k, v in mapping.items():
        content = content.replace(k, v)
    return content


def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def to_kebab(name):
    """PascalCase → kebab-case"""
    return re.sub(r"(?<!^)(?=[A-Z])", "-", name).lower()


def run(cmd, cwd, desc=""):
    if desc:
        print(f"  ... {desc}")
    # Windows 上 npm/npx 是 .cmd 文件，需 shell=True 才能解析
    if isinstance(cmd, (list, tuple)):
        if hasattr(subprocess, "list2cmdline"):
            cmd = subprocess.list2cmdline(cmd)
        else:
            cmd = " ".join(cmd)
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, errors="replace", shell=True)
    if r.returncode != 0:
        print(f"  [警告] 失败: {cmd.split()[0]}...")
        if r.stderr.strip():
            print(f"         {r.stderr.strip().splitlines()[-1][:160]}")
    return r.returncode == 0


def init_git(target):
    """初始化 git 仓库并创建初始提交"""
    if not shutil.which("git"):
        print("  [跳过] 未检测到 git，跳过仓库初始化")
        return
    run(["git", "init"], target, "初始化 git 仓库")
    run(["git", "add", "-A"], target, "暂存全部文件")
    if run(["git", "commit", "-m", "chore: 初始化项目脚手架"], target, "创建初始提交"):
        print("  [OK] git 仓库初始化完成（含初始提交）")
    else:
        print("  [提示] 初始提交失败（可能未配置 git user.name/email），仓库已建好，可稍后手动提交")


def init_api(target, code_name):
    api_dir = os.path.join(target, "src", "backend", "api")
    os.makedirs(api_dir, exist_ok=True)

    # 1. dotnet new 生成骨架（正确命名）
    run(["dotnet", "new", "sln", "-n", code_name], api_dir, "创建解决方案")
    run(["dotnet", "new", "classlib", "-n", f"{code_name}.Common", "-f", "net8.0"], api_dir, "创建 Common/Model/Service 类库")
    run(["dotnet", "new", "classlib", "-n", f"{code_name}.Model", "-f", "net8.0"], api_dir)
    run(["dotnet", "new", "classlib", "-n", f"{code_name}.Service", "-f", "net8.0"], api_dir)
    run(["dotnet", "new", "webapi", "-n", f"{code_name}.Api", "-f", "net8.0", "--use-controllers"], api_dir, "创建 Api 项目")
    os.makedirs(os.path.join(api_dir, "tests"), exist_ok=True)
    run(["dotnet", "new", "xunit", "-n", f"{code_name}.Tests", "-f", "net8.0", "-o", f"tests/{code_name}.Tests"], api_dir, "创建测试项目")

    # 2. 加入解决方案 + 项目引用
    run(["dotnet", "sln", "add", f"{code_name}.Common", f"{code_name}.Model", f"{code_name}.Service", f"{code_name}.Api", f"tests/{code_name}.Tests"], api_dir, "加入解决方案")
    run(["dotnet", "add", f"{code_name}.Api/{code_name}.Api.csproj", "reference",
         f"{code_name}.Service/{code_name}.Service.csproj", f"{code_name}.Model/{code_name}.Model.csproj", f"{code_name}.Common/{code_name}.Common.csproj"], api_dir, "添加 Api 引用")
    run(["dotnet", "add", f"{code_name}.Service/{code_name}.Service.csproj", "reference",
         f"{code_name}.Model/{code_name}.Model.csproj", f"{code_name}.Common/{code_name}.Common.csproj"], api_dir)
    run(["dotnet", "add", f"tests/{code_name}.Tests/{code_name}.Tests.csproj", "reference",
         f"{code_name}.Api/{code_name}.Api.csproj", f"{code_name}.Service/{code_name}.Service.csproj", f"{code_name}.Model/{code_name}.Model.csproj"], api_dir)

    run(["dotnet", "add", f"tests/{code_name}.Tests/{code_name}.Tests.csproj", "package", "Microsoft.AspNetCore.Mvc.Testing"], api_dir, "添加集成测试包")

    # 3. 清理样板
    boilerplate = [
        f"{code_name}.Api/WeatherForecast.cs",
        f"{code_name}.Api/{code_name}.Api.http",
        f"{code_name}.Api/Controllers/WeatherForecastController.cs",
        f"{code_name}.Common/Class1.cs",
        f"{code_name}.Model/Class1.cs",
        f"{code_name}.Service/Class1.cs",
        f"tests/{code_name}.Tests/UnitTest1.cs",
    ]
    for f in boilerplate:
        p = os.path.join(api_dir, f)
        if os.path.exists(p):
            os.remove(p)

    # 4. 写入自定义基础设施（替换 {{CodeName}}）
    for src_rel, dst_rel in API_CUSTOM:
        dst = os.path.join(api_dir, dst_rel.format(cn=code_name))
        content = render(os.path.join(TEMPLATE_DIR, "code", "api", src_rel), {"{{CodeName}}": code_name})
        write(dst, content)

    # 5. 创建空分层目录
    for d in ["Entities", "DTOs/Request", "DTOs/Response", "Enums"]:
        os.makedirs(os.path.join(api_dir, f"{code_name}.Model", d), exist_ok=True)
    for d in ["Interfaces", "Implementations"]:
        os.makedirs(os.path.join(api_dir, f"{code_name}.Service", d), exist_ok=True)
    for d in ["Filters", "Extensions"]:
        os.makedirs(os.path.join(api_dir, f"{code_name}.Api", d), exist_ok=True)
    for d in ["Services", "Helpers"]:
        os.makedirs(os.path.join(api_dir, "tests", f"{code_name}.Tests", d), exist_ok=True)

    # 6. 数据库迁移目录（含约定 README）
    mig_dst = os.path.join(api_dir, "sql", "migrations")
    os.makedirs(mig_dst, exist_ok=True)
    shutil.copy2(os.path.join(TEMPLATE_DIR, "code", "api", "sql-migrations", "README.md"),
                 os.path.join(mig_dst, "README.md"))

    print(f"  [OK] API 工程 {code_name} 生成完成（.NET 8 分层 + 迁移目录）")


def init_web(target, code_name, name, desc):
    web_dir = os.path.join(target, "src", "backend", "web")
    os.makedirs(web_dir, exist_ok=True)
    kebab = to_kebab(code_name)

    # 1. npm create vite（在子目录创建后上移）
    run(["npm", "exec", "--yes", "--", "create-vite@latest", kebab, "--", "--template", "vue-ts"], web_dir, "创建 Vue 3 + TS 工程")
    tmp = os.path.join(web_dir, kebab)
    if os.path.isdir(tmp):
        for item in os.listdir(tmp):
            shutil.move(os.path.join(tmp, item), web_dir)
        shutil.rmtree(tmp)

    # 2. 安装依赖（base + 运行时 + sass + 类型生成）
    run(["npm", "install"], web_dir, "安装基础依赖（可能较慢）")
    run(["npm", "install", "vue-router@4", "pinia", "element-plus", "axios"], web_dir, "安装 vue-router/pinia/element-plus/axios")
    run(["npm", "install", "-D", "sass", "swagger-typescript-api", "prettier"], web_dir, "安装 sass + swagger-typescript-api + prettier")

    # 2.5 注入 gen:api 脚本（从后端 Swagger 生成前端类型）
    import json
    pkg_path = os.path.join(web_dir, "package.json")
    try:
        with open(pkg_path, encoding="utf-8") as f:
            pkg = json.load(f)
        scripts = pkg.setdefault("scripts", {})
        scripts["gen:api"] = (
            "swagger-typescript-api -p http://localhost:8080/swagger/v1/swagger.json "
            "-o ./src/types -n api-generated.ts --extract-request-params --axios"
        )
        scripts["format"] = "prettier --write src"
        scripts["format:check"] = "prettier --check src"
        with open(pkg_path, "w", encoding="utf-8") as f:
            json.dump(pkg, f, ensure_ascii=False, indent=2)
        print("  [OK] 已注入 gen:api 类型生成脚本")
    except Exception as e:
        print(f"  [警告] 注入 gen:api 失败: {e}")

    # 3. 清理样板
    boilerplate = ["src/components/HelloWorld.vue", "src/style.css", "src/assets"]
    for f in boilerplate:
        p = os.path.join(web_dir, f)
        if os.path.isdir(p):
            shutil.rmtree(p, ignore_errors=True)
        elif os.path.exists(p):
            os.remove(p)

    # 4. 写入自定义基础设施（替换占位符）
    mapping = {"{{PROJECT_NAME}}": name, "{{PROJECT_DESC}}": desc, "{{codeName}}": kebab}
    for src_rel, dst_rel in WEB_CUSTOM:
        dst = os.path.join(web_dir, dst_rel)
        content = render(os.path.join(TEMPLATE_DIR, "code", "web", src_rel), mapping)
        write(dst, content)

    # 5. 创建空目录
    for d in ["components", "mock/modules", "utils"]:
        os.makedirs(os.path.join(web_dir, "src", d), exist_ok=True)

    print(f"  [OK] Web 工程 {kebab} 生成完成（Vue 3 + Element Plus）")


def init_deploy(target, code_name):
    """复制 CI/容器化部署文件"""
    deploy_tpl = os.path.join(TEMPLATE_DIR, "code", "deploy")

    # 1. GitHub Actions CI
    ci_dst = os.path.join(target, ".github", "workflows", "ci.yml")
    os.makedirs(os.path.dirname(ci_dst), exist_ok=True)
    shutil.copy2(os.path.join(deploy_tpl, "workflows", "ci.yml"), ci_dst)

    # 2. Dockerfile（替换代码名）
    api_docker = os.path.join(target, "src", "backend", "api", "Dockerfile.api")
    with open(api_docker, "w", encoding="utf-8") as f:
        f.write(render(os.path.join(deploy_tpl, "Dockerfile.api"), {"{{CodeName}}": code_name}))
    web_docker = os.path.join(target, "src", "backend", "web", "Dockerfile.web")
    shutil.copy2(os.path.join(deploy_tpl, "Dockerfile.web"), web_docker)

    # 3. docker-compose
    shutil.copy2(os.path.join(deploy_tpl, "docker-compose.yml"),
                 os.path.join(target, "docker-compose.yml"))

    # 4. dependabot（依赖周检）
    shutil.copy2(os.path.join(deploy_tpl, "dependabot.yml"),
                 os.path.join(target, ".github", "dependabot.yml"))

    print("  [OK] 部署文件生成（CI + Dockerfile x2 + compose + dependabot）")


def main():
    parser = argparse.ArgumentParser(description="Claude Code 多 Agent 项目脚手架生成器（混合式）")
    parser.add_argument("target", help="目标项目目录")
    parser.add_argument("--name", default="新项目", help="项目名称（中文显示名）")
    parser.add_argument("--desc", default="", help="项目一句话描述")
    parser.add_argument("--code-name", default="App", help="代码工程名（英文 PascalCase，默认 App）")
    parser.add_argument("--standards", default="", help="开发规范源目录（可选），复制到 .claude/standards/")
    args = parser.parse_args()

    target = os.path.abspath(args.target)
    name = args.name
    desc = args.desc if args.desc else "TODO: 一句话描述项目"
    code_name = args.code_name

    print(f"初始化多 Agent 项目: {target}")
    print(f"  项目名: {name}  代码名: {code_name}")

    # ===== 静态模板 =====
    copy_tree(os.path.join(TEMPLATE_DIR, ".claude"), os.path.join(target, ".claude"))
    print("  [OK] 复制 .claude/（21 Agent + 9 命令 + 2 hooks + settings）")
    copy_tree(os.path.join(TEMPLATE_DIR, "docs"), os.path.join(target, "docs"))
    print("  [OK] 复制 docs/（00-项目文档 md 模板 + README 三轨规范 + common.css + md2html.py + _模板与规范）")
    write(os.path.join(target, "CLAUDE.md"), render(os.path.join(TEMPLATE_DIR, "CLAUDE.md"), {"{{PROJECT_NAME}}": name, "{{PROJECT_DESC}}": desc}))
    print("  [OK] 生成 CLAUDE.md")
    write(os.path.join(target, "README.md"), render(os.path.join(TEMPLATE_DIR, "README.md"), {"{{PROJECT_NAME}}": name, "{{PROJECT_DESC}}": desc}))
    print("  [OK] 生成 README.md")
    shutil.copy2(os.path.join(TEMPLATE_DIR, ".mcp.json"), os.path.join(target, ".mcp.json"))
    shutil.copy2(os.path.join(TEMPLATE_DIR, ".gitignore"), os.path.join(target, ".gitignore"))
    shutil.copy2(os.path.join(TEMPLATE_DIR, ".editorconfig"), os.path.join(target, ".editorconfig"))
    shutil.copy2(os.path.join(TEMPLATE_DIR, ".gitattributes"), os.path.join(target, ".gitattributes"))
    print("  [OK] 生成 .mcp.json / .gitignore / .editorconfig / .gitattributes")

    # ===== 代码工程（CLI + 模板） =====
    print("\n[代码工程]")
    init_api(target, code_name)
    init_web(target, code_name, name, desc)
    init_deploy(target, code_name)

    # ===== standards =====
    standards_src = args.standards.strip()
    if standards_src and os.path.isdir(standards_src):
        shutil.copytree(standards_src, os.path.join(target, ".claude", "standards"), dirs_exist_ok=True)
        print(f"  [OK] 从 {standards_src} 覆盖开发规范")
    else:
        print("  [OK] 使用内置默认开发规范（5 份）")

    # ===== 初始化 git 仓库 =====
    print("\n[git 仓库]")
    init_git(target)

    print("\n========== 完成 ==========")
    print("下一步：")
    print("  1. 填写 CLAUDE.md 中的 TODO（项目速览、红线、技术栈、常用命令）")
    print("  2. 开发规范已内置在 .claude/standards/（如需自定义用 --standards 覆盖）")
    print("  3. 后端构建：cd src/backend/api && dotnet build")
    print("  4. 前端启动：cd src/backend/web && npm run dev")
    print("  5. cd 到项目根目录，运行 claude；输入 /product-discovery 开始")
    print("  6. 关联远程仓库：git remote add origin <远程地址> && git push -u origin main")


if __name__ == "__main__":
    main()
