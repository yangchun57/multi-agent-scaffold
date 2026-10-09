---
paths:
  - "app/routers/**/*.py"
  - "app/api/**/*.py"
---

# 后端 API 层规范（Python FastAPI）

## 技术栈
- FastAPI + Pydantic v2 + SQLAlchemy 2.0
- 统一返回: RESTful 业务错误 raise HTTPException

## 铁律
- 所有 handler 必须有 Pydantic v2 入参 model（禁止裸 dict）
- 禁止 handler 内含业务逻辑，一律委托 service 层
- 认证依赖注入: `get_current_user` from `app.core.auth`
- 分页统一: `Page[T]` 泛型响应（items/total/page/size）

## 路由组织
- 每个业务域一个 `app/api/<domain>.py`
- router 级别挂载认证: `dependencies=[Depends(get_current_user)]`
- 所有路由在 `app/api/__init__.py` 集中 include_router

## 命名
- 路由函数: `{action}_{resource}`（create_user, list_orders）
- 文件: snake_case，与资源名一致
- Schema: `XxxIn` / `XxxOut`（入参/出参分离）

## 错误处理
- 业务错误: `raise HTTPException(status_code, detail="中文描述")`
- 状态码: 400 参数非法 / 401 未登录 / 403 无权限 / 404 不存在

## 详细规范
@.claude/standards/topics/Python后台开发规范_v0.1/06-6.-API-设计规范.md
