---
description: 需求评审（独立命令，可评审 requirements/design/implementation 阶段）
---

请按以下流程执行需求评审，全程遵循 CLAUDE.md。

**编排原则**：评审是角色工作，必须启动 req-coordinator SubAgent 完成，不要内联在主 Agent 做。

## 参数解析

用户可能传入以下参数之一：
- `requirements`（默认）：评审需求文档
- `design`：评审设计文档（api-contracts.md / database-design.md）
- `implementation`：评审实现符合性
- `pr`：评审 PR diff

如果用户未指定阶段，默认使用 `requirements`。

## 执行流程

### 第一步：启动评审协调者
启动 req-coordinator SubAgent，传递：
- 评审阶段：{阶段}
- 评审范围：{对应产物路径}
- 上下文：CLAUDE.md（红线约束）、api-contracts.md（契约）、database-design.md（DB 设计）

req-coordinator 会自动串行调度 3 个评审专家：
1. req-doc-reviewer：检查需求质量（完整性、无歧义性、可测试性）+ 上下游一致性（需求→API→DB→代码追溯性）
2. req-impact-reviewer：分析变更影响范围 + 红线合规检查（分层边界、响应格式、字段映射、SDK 锁定）
3. req-test-reviewer：检查测试用例对验收标准的覆盖度

### 第二步：评审报告落盘
req-coordinator 输出最终评审报告，包含：
- 评审结论：通过 / 需修复后通过 / 不通过
- 阻塞项清单（必须修复）
- 建议项清单（建议改进）
- 修复任务清单

→ 立即提交：`docs: 需求评审报告（{阶段}）`

### 第三步：阻塞项处理（如有）
如果评审结论为"需修复后通过"或"不通过"：
- 启动对应 Agent 修复阻塞项（如 requirement-analyst 修复需求文档）
- 修复完成后，重新执行 `/req-review {阶段}` 直到通过

### 第四步：汇总
主 Agent 向用户汇报：
- 评审结论
- 阻塞项数量及修复状态
- 建议项摘要
- 下一步建议

## 使用示例

```bash
# 评审需求文档（默认）
/req-review

# 评审设计文档
/req-review design

# 评审实现符合性
/req-review implementation

# 评审 PR
/req-review pr
```

## 与 /product-discovery 的关系

- `/product-discovery` 在第五步会自动调用 req-coordinator 做需求评审
- `/req-review` 可独立使用，适合：
  - 存量项目补做需求评审
  - 设计阶段评审
  - 实现符合性检查
  - PR 评审
