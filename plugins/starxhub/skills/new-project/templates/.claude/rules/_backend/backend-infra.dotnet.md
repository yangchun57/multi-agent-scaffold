---
paths:
  - "**/Model/**/*.cs"
  - "**/Entities/**/*.cs"
  - "**/sql/migrations/**/*.sql"
---

# 后端基础设施层规范（.NET 8）

## ORM 框架
- 使用 SqlSugar 5.x（CodeFirst + DbFirst）
- 实体映射: `[SugarTable("表名")]` + `[SugarColumn(IsPrimaryKey=true)]`
- 字段映射: 数据库 snake_case → C# PascalCase（`[SugarColumn(ColumnName="...")]`）

## 实体定义
- 主键: 雪花 ID（Snowflake ID），类型 `long`，禁止自增
- 公共字段: 通过基类或接口复用（`ITenantEntity`, `IAuditable`）
- 表名: snake_case 复数（`users`, `order_items`）
- 字段: PascalCase（`Id`, `CreatedAt`, `UserId`）

## 多租户隔离（红线）
- 所有业务实体必须实现 `ITenantEntity`（包含 `TenantId` 属性）
- 所有查询必须经过租户过滤器（SqlSugar 全局过滤器）
- 索引: `TenantId` 必须作为联合索引第一列

## 迁移管理
- 版本化脚本: `sql/migrations/V{三位序号}__{描述}.sql`
- 只增不改，幂等优先（`IF NOT EXISTS`）

## 详细规范
@.claude/standards/topics/后端开发规范/02-二、项目结构规范.md
@.claude/standards/topics/后端开发规范/08-八、数据库操作规范.md
