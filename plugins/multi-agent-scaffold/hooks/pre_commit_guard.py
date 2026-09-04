#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PreToolUse 钩子：拦截 git commit，先运行构建和测试。
"""
import sys
import subprocess
import json

def main():
    try:
        input_data = json.loads(sys.stdin.read())
    except Exception:
        return

    tool_input = input_data.get("tool_input", {})
    command = tool_input.get("command", "") or ""

    # 只在 git commit 时拦截
    if not command.strip().startswith("git commit"):
        return

    print("检测到 git commit，先运行后端构建和测试...", file=sys.stderr)

    # 运行后端测试（在 backend 目录）
    result = subprocess.run(
        ["dotnet", "test"],
        cwd=os.path.join(os.environ.get("CLAUDE_PROJECT_DIR", "."), "src", "backend", "api"),
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print("构建或测试失败，已阻止提交。", file=sys.stderr)
        print(result.stdout, file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        # 阻止提交：输出错误信息
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": "构建或测试未通过，禁止提交"
            }
        }))
        sys.exit(2)
    else:
        print("构建和测试通过，允许提交。", file=sys.stderr)
        sys.exit(0)

if __name__ == "__main__":
    main()
