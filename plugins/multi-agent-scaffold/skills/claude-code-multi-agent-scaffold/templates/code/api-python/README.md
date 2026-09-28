# {{CodeName}} 后端（FastAPI + SQLAlchemy）

技术栈：{{BACKEND_STACK}}

## 目录结构

```
app/
  main.py           装配入口（日志/CORS/异常处理/总路由/启动建表）
  config.py         pydantic-settings 全局配置与路径常量
  database.py       engine / SessionLocal / get_db + before_flush 自动填充 tenant_id
  core/
    context.py      请求级租户上下文（contextvar）
    security.py     JWT 签发/校验、密码哈希
    deps.py         get_current_user / require_role / require_admin
    exceptions.py   BusinessException + 全局异常处理器
    query.py        secure_select（租户过滤）+ paginate（Page 信封）
  models/           SQLAlchemy 实体（Base / TimestampMixin / TenantMixin）
  schemas/          Pydantic DTO（Page / PageQuery / CamelModel）
  api/              路由，按业务域拆分，__init__ 聚合总路由
  services/         业务逻辑（禁止依赖 FastAPI Request/Response）
tests/              pytest（conftest 内存库 + TestClient）
```

## 多租户红线（对齐 CLAUDE.md）

- 业务实体继承 `TenantMixin`（自带 `tenant_id` 列）；`database` 的 `before_flush` 用租户上下文自动写入。
- 查询必须经 `app.core.query.secure_select(Model)` 追加租户过滤（SQLAlchemy 没有 SqlSugar 式隐式全局过滤器，靠显式 helper 兜底）。
- 需鉴权的路由挂 `dependencies=[Depends(get_current_user)]`；`get_current_user` 解析 JWT 后把 `tenant_id` 写入上下文。

## 约定（Python 后台开发规范）

- 业务错误 `raise BusinessException(...)`（HTTPException 子类），用 HTTP 状态码表达，禁止 200 + 自定义错误码。
- 列表统一返回 `Page[T]{items,total,page,size}`；出参实体用 `CamelModel` 基类转 camelCase（前端字段映射红线）。
- 分层依赖单向：`api → services → models`；`schemas` 只在边界使用。

## 运行

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000           # 健康检查 http://127.0.0.1:8000/api/health
pytest
```

## 与前端组合的注意点

- 若前端选 **uni-app**：其 `request.ts` 按规范解包 `ApiResult.data`，而本 Python 后端按自身规范返回裸对象/`Page`（无 ApiResult 信封）。二者组合时需二选一：前端 `request.ts` 去掉解包逻辑，或后端加一层响应信封中间件。`dotnet + vue` 与 `python + vue`（Vue request.ts 已做 ApiResult 解包对接 .NET；python 需同样处理）组合亦有此差异，接入时以后端实际返回结构对齐前端解包。
