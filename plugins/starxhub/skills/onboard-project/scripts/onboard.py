#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目接入（Onboard）脚本：将已有项目纳入多 Agent 工作流。

功能：
1. 调用 detect_stack.py 探测技术栈
2. 从 ../new-project/templates/ 复制 .claude/ 配置到目标项目
3. 根据探测结果生成 rules（按匹配度）
4. 从代码推断预填 CLAUDE.md

用法：
    python onboard.py <project-root> [--backend dotnet|python] [--frontend vue|uniapp]

示例：
    python onboard.py D:/projects/existing-app --backend python --frontend vue
"""

import argparse
import json
import os
import shutil
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DETECT_SCRIPT = os.path.join(SCRIPT_DIR, "detect_stack.py")
# 模板目录：../new-project/templates/
TEMPLATE_DIR = os.path.join(SCRIPT_DIR, "..", "..", "new-project", "templates")


def run_detect(project_root: str) -> dict:
    """运行探测脚本，返回技术栈分析结果"""
    cmd = [sys.executable, DETECT_SCRIPT, project_root]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if result.returncode != 0:
        print(f"探测失败: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    return json.loads(result.stdout)


def copy_claude_config(project_root: str, detection: dict) -> None:
    """复制 .claude/ 配置到目标项目"""
    target_claude = os.path.join(project_root, ".claude")
    os.makedirs(target_claude, exist_ok=True)

    # 需要复制的子目录
    subdirs = ["agents", "commands", "hooks", "standards"]
    for subdir in subdirs:
        src = os.path.join(TEMPLATE_DIR, ".claude", subdir)
        dst = os.path.join(target_claude, subdir)
        if os.path.exists(src):
            if os.path.exists(dst):
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            print(f"✓ 复制 {subdir}/")
        else:
            print(f"⚠ 模板目录不存在: {subdir}/")

    # 复制 settings.json
    src_settings = os.path.join(TEMPLATE_DIR, ".claude", "settings.json")
    dst_settings = os.path.join(target_claude, "settings.json")
    if os.path.exists(src_settings):
        shutil.copy2(src_settings, dst_settings)
        print("✓ 复制 settings.json")


def generate_rules(project_root: str, detection: dict) -> None:
    """根据探测结果生成 rules"""
    rules_dir = os.path.join(project_root, ".claude", "rules")
    os.makedirs(rules_dir, exist_ok=True)

    # 始终加载的通用规则
    always_rules = ["workflow.md", "database.md", "git.md"]
    template_rules_dir = os.path.join(TEMPLATE_DIR, ".claude", "rules", "_always")

    for rule_file in always_rules:
        src = os.path.join(template_rules_dir, rule_file)
        dst = os.path.join(rules_dir, rule_file)
        if os.path.exists(src):
            shutil.copy2(src, dst)
            print(f"✓ 生成通用规则: {rule_file}")

    # 根据技术栈生成后端规则
    backend = detection.get("stack", {}).get("backend", {})
    backend_lang = backend.get("language", "")

    if backend_lang == "dotnet":
        backend_rules_dir = os.path.join(TEMPLATE_DIR, ".claude", "rules", "_backend", "dotnet")
        if os.path.exists(backend_rules_dir):
            for rule_file in os.listdir(backend_rules_dir):
                src = os.path.join(backend_rules_dir, rule_file)
                # 去掉 .dotnet 后缀
                dst_name = rule_file.replace(".dotnet", "")
                dst = os.path.join(rules_dir, dst_name)
                shutil.copy2(src, dst)
                print(f"✓ 生成后端规则: {dst_name}")

    elif backend_lang == "python":
        backend_rules_dir = os.path.join(TEMPLATE_DIR, ".claude", "rules", "_backend", "python")
        if os.path.exists(backend_rules_dir):
            for rule_file in os.listdir(backend_rules_dir):
                src = os.path.join(backend_rules_dir, rule_file)
                dst_name = rule_file.replace(".python", "")
                dst = os.path.join(rules_dir, dst_name)
                shutil.copy2(src, dst)
                print(f"✓ 生成后端规则: {dst_name}")

    else:
        print(f"⚠ 未识别的后端技术栈: {backend_lang}，跳过后端规则生成")

    # 根据技术栈生成前端规则
    frontend = detection.get("stack", {}).get("frontend", {})
    frontend_framework = frontend.get("framework", "")

    if frontend_framework == "vue3":
        frontend_rules_dir = os.path.join(TEMPLATE_DIR, ".claude", "rules", "_frontend", "vue")
        if os.path.exists(frontend_rules_dir):
            for rule_file in os.listdir(frontend_rules_dir):
                src = os.path.join(frontend_rules_dir, rule_file)
                dst_name = rule_file.replace(".vue", "")
                dst = os.path.join(rules_dir, dst_name)
                shutil.copy2(src, dst)
                print(f"✓ 生成前端规则: {dst_name}")

    elif frontend_framework == "uniapp":
        frontend_rules_dir = os.path.join(TEMPLATE_DIR, ".claude", "rules", "_frontend", "uniapp")
        if os.path.exists(frontend_rules_dir):
            for rule_file in os.listdir(frontend_rules_dir):
                src = os.path.join(frontend_rules_dir, rule_file)
                dst_name = rule_file.replace(".uniapp", "")
                dst = os.path.join(rules_dir, dst_name)
                shutil.copy2(src, dst)
                print(f"✓ 生成前端规则: {dst_name}")

    else:
        print(f"⚠ 未识别的前端技术栈: {frontend_framework}，跳过前端规则生成")


def generate_claude_md(project_root: str, detection: dict) -> None:
    """从代码推断预填 CLAUDE.md"""
    claude_md_path = os.path.join(project_root, "CLAUDE.md")

    # 从探测结果提取信息
    stack = detection.get("stack", {})
    backend = stack.get("backend", {})
    frontend = stack.get("frontend", {})

    backend_stack = f"{backend.get('language', 'unknown')} + {backend.get('framework', 'unknown')}"
    if backend.get("orm"):
        backend_stack += f" + {backend['orm']}"

    frontend_stack = frontend.get("framework", "unknown")
    if frontend.get("ui_lib"):
        frontend_stack += f" + {frontend['ui_lib']}"

    # 生成 CLAUDE.md 内容
    content = f"""# CLAUDE.md — {{项目名称}}

## 项目速览

{{从 README.md 或代码推断}}

## 技术栈

- 后端: {backend_stack}
- 前端: {frontend_stack}
- 数据库: {{从配置推断}}

## 最高优先级约束

{{从代码中的多租户过滤器、认证中间件等推断}}

1. 多租户隔离：所有数据查询必须带 tenant_id 过滤，违反即红线
2. 响应格式：API 统一使用标准格式包装
3. 类型生成：前端业务实体由 gen:api 从 Swagger 生成，禁止手写
4. 数据库：表结构变更走版本化迁移脚本，禁止手工改库

## 常用命令

- 构建: {{从 package.json / Makefile 推断}}
- 测试: {{从 pytest.ini / package.json 推断}}
- 启动: {{从 main.py / app.py 推断}}

## 文档索引

- `docs/00-项目文档/` — Agent 工作文件（需求/设计/任务计划）
- `docs/01-技术规范/` — 技术规范文档
- `docs/02-用户文档/` — 用户手册

## 注意事项

{{根据代码特点补充}}
"""

    with open(claude_md_path, "w", encoding="utf-8") as f:
        f.write(content)

    print("✓ 生成 CLAUDE.md（需手动补充 TODO 占位符）")


def main():
    parser = argparse.ArgumentParser(description="项目接入脚本：将已有项目纳入多 Agent 工作流")
    parser.add_argument("project_root", help="目标项目根目录")
    parser.add_argument("--backend", choices=["dotnet", "python"], help="后端技术栈（可选，默认自动探测）")
    parser.add_argument("--frontend", choices=["vue", "uniapp"], help="前端技术栈（可选，默认自动探测）")
    args = parser.parse_args()

    project_root = os.path.abspath(args.project_root)
    if not os.path.isdir(project_root):
        print(f"错误: {project_root} 不是有效目录", file=sys.stderr)
        sys.exit(1)

    print(f"=== 项目接入（Onboard）===")
    print(f"目标项目: {project_root}")
    print()

    # Step 1: 探测技术栈
    print("Step 1: 探测技术栈...")
    detection = run_detect(project_root)
    print(json.dumps(detection, ensure_ascii=False, indent=2))
    print()

    # Step 2: 复制 .claude/ 配置
    print("Step 2: 复制 .claude/ 配置...")
    copy_claude_config(project_root, detection)
    print()

    # Step 3: 生成 rules
    print("Step 3: 生成 rules...")
    generate_rules(project_root, detection)
    print()

    # Step 4: 生成 CLAUDE.md
    print("Step 4: 生成 CLAUDE.md...")
    generate_claude_md(project_root, detection)
    print()

    print("=== 接入完成 ===")
    print("下一步：")
    print("1. 编辑 CLAUDE.md，补充 TODO 占位符")
    print("2. 检查 .claude/rules/ 是否符合项目实际")
    print("3. 运行 /product-discovery 或 /new-feature 开始开发")


if __name__ == "__main__":
    main()
