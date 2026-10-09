---
paths:
  - "app/database.py"
  - "app/models/**/*.py"
  - "app/core/**/*.py"
  - "sql/migrations/**/*.sql"
---

# 后端基础设施层规范（Python FastAPI）

## 数据库连接
- 使用 SQLAlchemy 2.x 声明式: `DeclarativeBase` + `Mapped` + `mapped_column`
- 会话管理: `get_db()` 依赖注入，禁止手动创建 Session
- 配置: `expire_on_commit=False`，避免提交后隐式再查询

## 模型定义
- 主键: 雪花 ID（Snowflake ID），类型 `BigInteger`，禁止自增
- 公共字段: 通过 Mixin 复用（`TimestampMixin`, `SnowflakeIdMixin`）
- 表名: snake_case 单数（`user`, `order_item`）
- 字段: snake_case（`created_at`, `user_id`）

## 多租户隔离（红线）
- 所有业务表必须包含 `tenant_id` 字段（BigInteger, NOT NULL）
- 所有查询必须经过租户过滤器
- 索引: `tenant_id` 必须作为联合索引第一列

## 迁移管理
- 版本化脚本: `sql/migrations/V{三位序号}__{描述}.sql`
- 只增不改，幂等优先（`IF NOT EXISTS`）

## 详细规范
@.claude/standards/topics/Python后台开发规范_v0.1/04-4.-数据库与-ORM-规范.md
