---
description: 编写功能测试用例（文档驱动 / 代码逆向，自动判定）
---

请为指定功能范围编写完整的功能测试用例，全程遵循 CLAUDE.md。

参数（$ARGUMENTS）：功能范围，如「会议室预约」「全部功能」。缺省为全部已有功能。

**编排原则**：用例设计是角色工作，必须启动 functional-tester SubAgent 完成，不要内联在主 Agent 做；模式判定、提交、确认等编排动作留在主 Agent。

## 第一步：派发用例设计（启动 functional-tester SubAgent）
启动 functional-tester，任务描述中注明功能范围。它会自行判定工作模式：
- `docs/00-项目文档/requirements.md` 有真实验收标准 → 模式 A（文档驱动）
- 只有代码工程或文档全是 `{TODO}` 模板 → 模式 B（代码逆向）
- 部分覆盖 → 混合模式，逐条标注来源

交付物落盘到 `docs/00-项目文档/test-cases/`，命名遵循 docs/README.md 版本规范。

## 第二步：提交（主 Agent）
用例文档落盘后主 Agent 立即提交：`docs: {功能范围}功能测试用例`

## 第三步：存疑确认（主 Agent，仅模式 B / 混合）
若 SubAgent 汇报了存疑清单，主 Agent 完整展示给用户，停下等确认；确认后如需修正用例，再派 functional-tester 出 v0.2 版本（不覆盖旧版）并再次提交。

## 第四步：汇报（主 Agent）
向用户汇报：用例统计（总数、优先级分布、模式占比）、存疑清单处理结果、建议的后续动作（如派 tester 将用例落地为自动化测试）。
