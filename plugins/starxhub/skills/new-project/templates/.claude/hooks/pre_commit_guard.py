#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PreToolUse 钩子：拦截 git commit，先跑构建和测试
import sys, subprocess, json, os

def main():
    try:
        data = json.loads(sys.stdin.read())
    except Exception:
        return
    cmd = (data.get("tool_input", {}).get("command") or "").strip()
    if not cmd.startswith("git commit"):
        return
    print("检测到 git commit，先运行构建和测试...", file=sys.stderr)
    r = subprocess.run(["dotnet", "test"], cwd=os.path.join(os.environ.get("CLAUDE_PROJECT_DIR", "."), "src", "backend", "api"), capture_output=True, text=True)
    if r.returncode != 0:
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": "构建或测试未通过"}}))
        sys.exit(2)
    sys.exit(0)

if __name__ == "__main__":
    main()
