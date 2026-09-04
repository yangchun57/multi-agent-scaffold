---
description: 生成单元测试
---

**编排原则**：测试是角色工作，必须启动 tester SubAgent 完成，不要内联在主 Agent 做。

请启动 tester SubAgent，为指定的 Service 生成单元测试，覆盖正常、异常、边界场景。生成后运行测试命令验证通过。

测试通过后主 Agent 立即提交：`test: 单元测试`。
