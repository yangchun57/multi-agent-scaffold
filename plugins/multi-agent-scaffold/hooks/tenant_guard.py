#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PostToolUse 钩子：扫描 Agent 写入的文件，检查多租户红线和敏感信息。
"""
import sys
import json

def main():
    try:
        input_data = json.loads(sys.stdin.read())
    except Exception:
        return

    tool_input = input_data.get("tool_input", {})
    file_path = tool_input.get("file_path", "") or ""
    content = tool_input.get("content", "") or ""

    issues = []

    # 1. 敏感信息检查
    sensitive_patterns = ["password", "secret", "api_key", "apikey", "token"]
    lower = content.lower()
    for pattern in sensitive_patterns:
        if pattern in lower and "your-" not in lower:
            issues.append(f"疑似硬编码敏感信息: {pattern}")

    # 2. 多租户红线检查（仅检查 C# 实体文件）
    if file_path.endswith(".cs") and "SugarTable" in content:
        # 是实体类，检查是否含 TenantId
        if "biz_" in content and "TenantId" not in content:
            issues.append("业务实体缺少 TenantId 字段（多租户红线）")

    if issues:
        print("检测到以下问题：", file=sys.stderr)
        for issue in issues:
            print(f"  - {issue}", file=sys.stderr)
        # 输出警告（不阻断，但提醒）
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "permissionDecision": "allow",
                "permissionDecisionReason": f"发现 {len(issues)} 个需人工确认的问题"
            }
        }))

    sys.exit(0)

if __name__ == "__main__":
    main()
