---
trigger: always
---

# 数据库规范

## 多租户隔离（红线）
1. **所有业务表必须包含** `tenant_id` 字段（BIGINT，NOT NULL）
2. **所有查询必须经过租户过滤器**：使用全局查询过滤器或中间件自动注入
3. **禁止跨租户数据访问**：任何 SQL 都必须带 `WHERE tenant_id = ?`
4. **索引要求**：`tenant_id` 必须作为联合索引的第一列

## 迁移管理
1. **版本化迁移脚本**：`sql/migrations/V{三位序号}__{描述}.sql`
   - 示例：`V001__create_users_table.sql`
2. **只增不改**：已执行的迁移禁止修改，只能新增迁移
3. **幂等优先**：迁移脚本应支持重复执行（使用 `IF NOT EXISTS`）
4. **禁止手工改库**：所有结构变更必须通过迁移脚本

## 字段命名
- 表名：snake_case 复数（`users`, `order_items`）
- 字段名：snake_case（`created_at`, `user_id`）
- 主键：`id`（BIGINT，自增或 UUID）
- 外键：`{关联表单数}_id`（`user_id`, `order_id`）
- 时间字段：`created_at`, `updated_at`, `deleted_at`（软删除）

## ORM 使用
- 禁止拼接原生 SQL（除复杂报表查询）
- 使用 ORM 提供的查询构建器
- 批量操作使用 `bulk_insert` / `bulk_update`
- 分页查询必须带 `LIMIT` 和 `OFFSET`

## 详细规范
@.claude/standards/通用开发规范.md#数据库规范
