---
paths:
  - "app/services/**/*.py"
  - "app/domain/**/*.py"
---

# 后端领域层规范（Python FastAPI）

## 分层职责
- **services/**: 业务逻辑、事务编排、第三方客户端封装
- **models/**: 表结构与常量定义（SQLAlchemy ORM）
- **schemas/**: DTO 定义与校验规则（Pydantic）

## 铁律
- 禁止 Service 层依赖 FastAPI 的 Request/Response 对象
- 禁止 Model 层包含业务方法（纯数据映射）
- 禁止 Schema 层包含业务逻辑（纯校验规则）
- 第三方 SDK 必须封装为 services/ 下的统一客户端模块

## 依赖方向
```
api → services → models
         ↓
      schemas
```
严格单向，禁止反向依赖。

## 事务管理
- 使用 `with db.begin():` 或装饰器 `@transactional`
- 禁止在 Service 外手动管理事务

## 命名
- Service: `{resource}_service.py`（user_service.py）
- 函数: `{action}_{resource}`（create_user, get_user_by_id）
- Model: `{resource}.py`（user.py, order.py）
- Schema: `{resource}_schema.py`（user_schema.py）

## 详细规范
@.claude/standards/topics/Python后台开发规范_v0.1/05-5.-分层职责规范.md
