# 数据库迁移约定

所有数据库结构变更通过本目录下的版本化 SQL 脚本管理，禁止手工改库。

## 命名规则

```
V{三位序号}__{变更描述}.sql
```

示例：
```
V001__create_biz_entity.sql
V002__add_tenant_index_to_biz_entity.sql
V003__create_biz_reservation.sql
```

## 规则

1. **只增不改**：已提交到仓库的迁移脚本禁止修改；改错了就新增一个修正脚本（V00N__fix_xxx.sql）
2. **顺序执行**：序号严格递增，新脚本序号 = 当前最大序号 + 1
3. **一个脚本一件事**：一个迁移脚本只做一类变更（一张新表 / 一个加字段批次），便于回滚和审计
4. **幂等优先**：DDL 尽量写成可重复执行不报错（如 `CREATE TABLE IF NOT EXISTS`），便于各环境对齐
5. **由 db-engineer 维护**：`/new-feature` 和 `/change-request` 涉及表结构变更时，必须产出迁移脚本并立即提交（`docs: 迁移脚本 V00N`）
6. **红线不变**：所有业务表迁移脚本必须遵守 CLAUDE.md 最高优先级约束（如租户隔离字段要求）

## 执行方式

按序号顺序、在各环境手工执行（后续可接入 DbUp 等工具自动执行）：

```bash
mysql -u root -p your_db < V001__create_biz_entity.sql
```

## 已执行记录

| 脚本 | 日期 | 说明 | 环境 |
|------|------|------|------|
