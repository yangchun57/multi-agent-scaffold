---
paths:
  - "**/Service/**/*.cs"
  - "**/Services/**/*.cs"
---

# 后端领域层规范（.NET 8）

## 分层职责
- **Service/**: 所有业务逻辑、数据验证、事务管理
- **Model/**: 数据库实体映射、DTO 定义、枚举定义
- **Common/**: 公共工具类（JWT、Excel、统一返回格式）

## 铁律
- 禁止 Service 层直接操作 HttpContext
- 禁止 Model 层包含业务逻辑方法（纯数据映射）
- 禁止 Common 层引用 Service 或 Model（只能被依赖）
- 依赖注入: 通过构造函数注入 `ISqlSugarClient` + `ILogger<T>`

## 依赖方向
```
Controller → Service → Model
                ↓
             Common
```
严格单向，禁止反向依赖。

## 事务管理
- 使用 `_db.Ado.UseTranAsync(async () => { ... })`
- 事务失败抛出 `BusinessException`

## 命名
- Service 接口: `I{Resource}Service`（IUserService）
- Service 实现: `{Resource}Service`（UserService）
- Entity: `Sys{Resource}` 或 `{Resource}`（SysUser, Order）
- DTO: `{Resource}Dto` / `{Resource}CreateRequest`

## 详细规范
@.claude/standards/topics/后端开发规范/03-三、分层架构规范.md
