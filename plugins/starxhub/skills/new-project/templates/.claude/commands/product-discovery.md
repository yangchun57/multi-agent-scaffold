---
description: 产品发现与需求设计全流程（需求分析→用户研究→产品设计）
---

请按以下流程完成产品发现与需求设计，全程遵循 CLAUDE.md。

**编排原则**：每个角色步骤启动对应 SubAgent（通过 Task 工具下发），不要内联在主 Agent 做；确认、汇总等编排动作留在主 Agent。每个交付物落盘后主 Agent 立即提交（遵循 CLAUDE.md 提交约定）。

## 第一步：需求分析（启动 requirement-analyst SubAgent）
启动 requirement-analyst，让它产出结构化需求文档（业务目标、用户故事、Given/When/Then 验收标准、优先级），写回 docs/00-项目文档/requirements.md
→ 立即提交：`docs: 需求分析文档`

## 第二步：需求确认（主 Agent）
主 Agent 把需求文档摘要展示给用户，停下等拍板，确认后再继续。

## 第三步：用户研究（启动 ux-researcher SubAgent）
启动 ux-researcher，让它产出用户画像 → personas.md、用户旅程 → user-journey.md、竞品分析 → competitive-analysis.md
→ 立即提交：`docs: 用户研究（画像/旅程/竞品）`

## 第四步：产品设计（启动 product-designer SubAgent）
启动 product-designer，让它产出信息架构 → ia.md、交互流程 → flows.md、设计规范 → design-spec.md
→ 立即提交：`docs: 产品设计（IA/流程/规范）`

## 第五步：需求评审（启动 req-coordinator SubAgent）
启动 req-coordinator，让它调度需求评审团队对 requirements.md 做质量评审和一致性检查
→ 评审报告落盘后提交：`docs: 需求评审报告`

**评审结果处理**：
- 有阻塞项 → 启动 requirement-analyst 修复 → 重新评审（直到通过）
- 无阻塞项 → 继续

## 第六步：汇总（主 Agent）
主 Agent 向用户汇报：需求文档摘要、用户研究关键发现、设计产出清单、评审结论、下一步建议。
