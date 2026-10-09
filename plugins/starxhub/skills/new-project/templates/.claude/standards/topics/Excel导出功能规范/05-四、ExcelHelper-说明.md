# Excel导出功能规范 · 四、ExcelHelper 说明

> 拆分自《Excel导出功能规范》第 5 节。需要全量上下文时读原文件。


### ExportToExcel 方法

```csharp
public static MemoryStream ExportToExcel<T>(IEnumerable<T> data, string sheetName = "Sheet1")
```

- 自动添加"序号"列（从 1 开始）
- 通过 `[DisplayName]` 特性读取列标题
- 返回 MemoryStream，调用方负责释放

### 列标题规则

1. 优先使用 `[DisplayName("列名")]` 特性值
2. 未设置特性时使用属性名

### 数据类型处理

- 所有值在导出时转换为字符串
- DateTime 类型需在 DTO 转换时格式化

