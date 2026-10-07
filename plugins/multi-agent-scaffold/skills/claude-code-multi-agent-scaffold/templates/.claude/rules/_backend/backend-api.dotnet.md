---
paths:
  - "**/Controllers/**/*.cs"
  - "**/Api/**/*.cs"
---

# 后端 API 层规范（.NET 8）

## 技术栈
- ASP.NET Core Web API + SqlSugar 5.x + JWT Bearer
- 统一返回: `ApiResult<T>` / `PageResult<T>`

## 铁律
- 所有 Controller 必须使用 `[ApiController]` + `[Route("api/[controller]")]`
- 禁止 Controller 内含业务逻辑，一律委托 Service 层
- 认证: `[Authorize]` 或 `[Authorize(Roles = "admin")]`
- 响应: 统一使用 `ApiResult<T>.Success(data)` / `ApiResult<T>.Fail(message, code)`

## Controller 结构
- 构造函数注入: `IService` + `ILogger<T>`
- 参数来源: `[FromQuery]` / `[FromBody]` / `[FromRoute]` / `[FromForm]`
- 权限控制: 接口级 `[Authorize]`，角色级 `[Authorize(Roles = "...")]`

## 命名
- Controller: `{Resource}Controller`（UserController, OrderController）
- Action: HTTP 动词 + 资源（GetList, Create, Update, Delete）
- DTO: `{Resource}Dto` / `{Resource}CreateRequest` / `{Resource}QueryRequest`

## 错误处理
- 业务异常: `throw new BusinessException("中文描述")`
- 全局异常过滤器统一捕获并返回 `ApiResult<T>.Fail()`

## 详细规范
@.claude/standards/topics/后端开发规范/03-三、分层架构规范.md
@.claude/standards/topics/后端开发规范/05-五、统一响应格式.md
