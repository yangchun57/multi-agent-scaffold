#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PostToolUse 钩子：扫描 Agent 写入的文件，检查敏感信息
import sys, json

def main():
    try:
        data = json.loads(sys.stdin.read())
    except Exception:
        return
    content = (data.get("tool_input", {}).get("content") or "").lower()
    issues = [p for p in ("password", "secret", "api_key", "token") if p in content]
    if issues:
        print("检测到疑似硬编码敏感信息:", issues, file=sys.stderr)
    sys.exit(0)

if __name__ == "__main__":
    main()
