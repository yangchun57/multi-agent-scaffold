---
description: 触发代码审查
---

**编排原则**：审查是角色工作，必须启动 reviewer SubAgent 完成，不要内联在主 Agent 做。

请启动 reviewer SubAgent，对最近的代码变更做规范合规审查，重点检查是否遵守 CLAUDE.md 的最高优先级约束。输出结构化审查报告（✅ 通过 / ❌ 问题 + 修复建议）。

若审查发现问题并修复，主 Agent 立即提交：`fix: 审查问题修复`。
