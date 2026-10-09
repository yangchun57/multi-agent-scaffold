# {{CodeName}} — 与业务无关的 API 代码工程

本工程是遵循 `.claude/standards/后端开发规范.md` 的**业务无关**分层 API 骨架（.NET 8）。不含任何业务实体、服务或控制器，只有可复用的基础设施，作为新项目后端的地基。

## 技术栈

- .NET 8 + ASP.NET Core Web API（Controller 模式）
- 分层架构：Api（表示层）/ Service（业务层）/ Model（模型层）/ Common（公共层）

## 分层结构

```
{{CodeName}}/
├── {{CodeName}}.slnx           ← 解决方案文件（.NET 10 新版格式）
├── {{CodeName}}.Api/           ← 表示层（Controller 模式）
│   ├── Controllers/           ← 控制器（空，待业务填充）
│   ├── Filters/               ← 过滤器（GlobalExceptionFilter）
│   ├── Extensions/            ← 扩展方法（空）
│   ├── Program.cs             ← 应用入口
│   └── appsettings.json       ← 配置（Jwt/ConnectionStrings 占位）
├── {{CodeName}}.Service/       ← 业务逻辑层
│   ├── Interfaces/            ← 服务接口（空）
│   └── Implementations/       ← 服务实现（空）
├── {{CodeName}}.Model/         ← 数据模型层
│   ├── Entities/              ← 数据库实体（空）
│   ├── DTOs/
│   │   ├── Request/           ← 请求 DTO（空）
│   │   └── Response/          ← 响应 DTO（空）
│   └── Enums/                 ← 枚举（空）
├── {{CodeName}}.Common/        ← 公共工具层
│   ├── ApiResult.cs           ← 统一响应格式
│   ├── PageResult.cs          ← 分页返回 + 分页请求基类
│   └── BusinessException.cs   ← 业务异常 + 未找到异常
└── tests/
    └── {{CodeName}}.Tests/     ← 单元测试（xUnit）
        ├── Services/          ← Service 测试（空）
        └── Helpers/           ← 测试辅助（空）
```

## 依赖关系

```
Api → Service、Model、Common
Service → Model、Common
Model → （无依赖）
Common → （无业务依赖）
```

## 已内置的基础设施（业务无关）

- **ApiResult\<T\>**：统一响应 `{ code, message, data, timestamp }`
- **PageResult\<T\>**：分页返回 `{ items, total, pageIndex, pageSize }`
- **PageRequest**：分页请求基类（含 Normalize 规范化）
- **BusinessException / NotFoundException**：业务异常
- **GlobalExceptionFilter**：全局异常处理（业务异常→400/404，其他→500，统一返回 ApiResult）

## 如何接入业务

按后端开发规范的四层职责新增代码：

1. **Model 层**：在 `Entities/` 加实体（SugarTable）、在 `DTOs/` 加请求/响应 DTO、在 `Enums/` 加枚举
2. **Service 层**：在 `Interfaces/` 加接口、`Implementations/` 加实现
3. **Api 层**：在 `Controllers/` 加控制器（参数校验、权限、调用 Service、返回 ApiResult）

## 待接入的技术栈（按后端开发规范）

当前骨架只含基础控制器 + 统一响应，以下组件按需接入（见 `.claude/standards/后端开发规范.md` 对应章节）：

- **SqlSugar**（ORM）+ MySQL：`dotnet add {{CodeName}}.Service package SqlSugarCore`
- **JWT 认证**：`dotnet add {{CodeName}}.Api package Microsoft.AspNetCore.Authentication.JwtBearer`
- **Serilog**（日志）：`dotnet add {{CodeName}}.Api package Serilog.AspNetCore`
- **Swagger**（API 文档）：`dotnet add {{CodeName}}.Api package Swashbuckle.AspNetCore`
- **MiniExcel**（Excel 处理）：`dotnet add {{CodeName}}.Common package MiniExcel`

## 命名规范速查

| 类型 | 规则 | 示例 |
|------|------|------|
| Controller | {Entity}Controller | EntityController |
| Service 接口 | I{Entity}Service | IEntityService |
| Service 实现 | {Entity}Service | EntityService |
| 实体 | Biz{Entity} / Sys{Entity} / Res{Entity} / Cfg{Entity} | BizEntity |
| 查询请求 | {Entity}QueryRequest | EntityQueryRequest |
| 响应 DTO | {Entity}Dto | EntityDto |

## 构建

```bash
cd src/backend/api
dotnet build
dotnet test
```
