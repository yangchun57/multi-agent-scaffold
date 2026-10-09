# Excel 导出功能规范

> **加载提示**：本文件较大，日常按需读取——先读 `topics/INDEX.md` 定位主题，或用 Grep 搜关键词后按行号局部读取（Read offset/limit）。仅需要全量核对时才整读本文件。

## 概述

本文档定义了后端 Excel 导出功能的实现规范，确保导出功能的一致性、可维护性和用户体验。

## 一、后端实现规范

### 1. 接口定义

#### 1.1 路由规范

- 路由格式：`GET /api/{Controller}/export`
- 使用 `[HttpGet("export")]` 特性标注
- 返回类型：`IActionResult`（返回 FileResult）

```csharp
/// <summary>
/// 导出XXX Excel
/// </summary>
/// <param name="request">查询条件</param>
/// <returns>Excel文件</returns>
[HttpGet("export")]
public async Task<IActionResult> Export([FromQuery] XxxQueryRequest request)
```

#### 1.2 参数规范

- 使用与列表查询相同的 `QueryRequest` 类作为参数
- 使用 `[FromQuery]` 特性接收查询参数
- 支持与列表页相同的筛选条件

### 2. 查询逻辑

#### 2.1 数据查询模式

```csharp
// 使用 SqlSugar 进行关联查询
var query = _db.Queryable<主表>()
    .LeftJoin<关联表1>((主, 关联1) => 主.ForeignKey == 关联1.PrimaryKey)
    .LeftJoin<关联表2>((主, 关联1, 关联2) => 主.ForeignKey2 == 关联2.PrimaryKey)
    .Where((主, 关联1, 关联2) => 主.PrimaryKey > 0);  // 基础条件

// 应用筛选条件
if (!string.IsNullOrWhiteSpace(request.Period))
{
    query = query.Where((主, 关联1, 关联2) => 主.Period == request.Period);
}
if (request.Status.HasValue)
{
    query = query.Where((主, 关联1, 关联2) => 主.Status == request.Status.Value);
}

// 中文排序：使用 CONVERT(column USING gbk)
query = query.OrderBy("CONVERT(d.DeptName USING gbk), CONVERT(m.Location USING gbk)");
```

#### 2.2 Select 投影

- 使用匿名对象或 DTO 进行投影，只查询需要的字段
- 避免查询不需要的关联数据

```csharp
var data = await query
    .Select((r, m, u) => new
    {
        r.Id,
        r.Period,
        Name = u.RealName ?? "-",
        Location = m.Location ?? "-"
    })
    .ToListAsync();
```

### 3. 导出 DTO 定义

#### 3.1 命名规范

- 类名：`{Entity}ExportDto`
- 定义位置：Controller 文件末尾（与 Controller 同文件）

#### 3.2 属性定义

- 使用 `[DisplayName("中文列名")]` 特性定义 Excel 列标题
- 字符串属性初始化为 `string.Empty`
- 不要定义 `Index` 或 `序号` 属性（ExcelHelper 自动添加）

```csharp
/// <summary>
/// 抄表记录导出DTO
/// </summary>
public class ReadingExportDto
{
    [System.ComponentModel.DisplayName("账期")]
    public string Period { get; set; } = string.Empty;

    [System.ComponentModel.DisplayName("安装位置")]
    public string Location { get; set; } = string.Empty;

    [System.ComponentModel.DisplayName("表号")]
    public string MeterNo { get; set; } = string.Empty;

    [System.ComponentModel.DisplayName("仪表类型")]
    public string MeterType { get; set; } = string.Empty;

    [System.ComponentModel.DisplayName("本期读数")]
    public decimal CurrValue { get; set; }

    [System.ComponentModel.DisplayName("状态")]
    public string Status { get; set; } = string.Empty;
}
```

#### 3.3 枚举值转换

- 在 Select 投影时直接转换为中文描述字符串

```csharp
MeterType = m.MeterType == 1 ? "水表" : "电表",
Status = r.Status switch
{
    1 => "待审核",
    2 => "已确认",
    3 => "已计费",
    _ => "-"
},
InputMethod = r.InputMethod == 1 ? "手工" : "Excel"
```

### 4. Excel 生成与响应

#### 4.1 调用 ExcelHelper

```csharp
var memoryStream = ExcelHelper.ExportToExcel(exportData, "工作表名称");
```

#### 4.2 文件名规范

- 格式：`{功能名称}_{时间戳}.xlsx`
- 时间戳格式：`yyyyMMddHHmmss`

```csharp
var fileName = $"抄表记录_{DateTime.Now:yyyyMMddHHmmss}.xlsx";
```

#### 4.3 响应头设置

**重要**：HTTP Header 不支持非 ASCII 字符，必须使用 URL 编码。

```csharp
var encodedFileName = Uri.EscapeDataString(fileName);
Response.Headers.Append("Content-Disposition", $"attachment; filename*=UTF-8''{encodedFileName}");
return File(memoryStream, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet");
```

### 5. 完整实现示例

```csharp
/// <summary>
/// 导出抄表记录Excel
/// </summary>
[HttpGet("export")]
public async Task<IActionResult> Export([FromQuery] ReadingQueryRequest request)
{
    // 1. 构建查询
    var query = _db.Queryable<BizReading>()
        .LeftJoin<SysMeter>((r, m) => r.MeterId == m.MeterId)
        .LeftJoin<SysUser>((r, m, u) => r.ReaderId == u.UserId)
        .Where((r, m, u) => r.ReadingId > 0);

    // 2. 应用筛选条件
    if (!string.IsNullOrWhiteSpace(request.Period))
    {
        query = query.Where((r, m, u) => r.Period == request.Period);
    }
    if (request.MeterType.HasValue)
    {
        query = query.Where((r, m, u) => m.MeterType == request.MeterType.Value);
    }
    if (request.Status.HasValue)
    {
        query = query.Where((r, m, u) => r.Status == request.Status.Value);
    }

    // 3. 执行查询（只查询需要的字段）
    var readings = await query
        .OrderByDescending((r, m, u) => m.MeterType)
        .OrderBy((r, m, u) => m.Location)
        .Select((r, m, u) => new
        {
            r.Period,
            m.Location,
            m.MeterNo,
            m.MeterType,
            r.CurrValue,
            r.ReadingTime,
            r.Status
        })
        .ToListAsync();

    // 4. 转换为导出 DTO
    var exportData = readings.Select(r => new ReadingExportDto
    {
        Period = r.Period,
        Location = r.Location ?? "-",
        MeterNo = r.MeterNo ?? "-",
        MeterType = r.MeterType == 1 ? "水表" : "电表",
        CurrValue = r.CurrValue,
        ReadingTime = r.ReadingTime.ToString("yyyy-MM-dd"),
        Status = r.Status switch
        {
            1 => "待审核",
            2 => "已确认",
            3 => "已计费",
            _ => "-"
        }
    }).ToList();

    // 5. 生成 Excel 并返回
    var memoryStream = ExcelHelper.ExportToExcel(exportData, "抄表记录");
    var fileName = $"抄表记录_{DateTime.Now:yyyyMMddHHmmss}.xlsx";
    var encodedFileName = Uri.EscapeDataString(fileName);
    Response.Headers.Append("Content-Disposition", $"attachment; filename*=UTF-8''{encodedFileName}");
    return File(memoryStream, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet");
}
```

## 二、前端实现规范

### 1. API 函数定义

```typescript
// src/api/{module}.ts
export function exportXxx(params: QueryType): Promise<Blob> {
  return request.get("/Controller/export", {
    params,
    responseType: "blob",
  });
}
```

### 2. 导出按钮处理

```typescript
import { exportXxx } from "@/api/module";

async function handleExport() {
  // 验证必要条件（如账期必选）
  if (!query.period) {
    ElMessage.warning("请选择账期");
    return;
  }

  loading.value = true;
  try {
    const blob = await exportXxx(query);
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `功能名称_${query.period}.xlsx`;
    a.click();
    window.URL.revokeObjectURL(url);
  } catch (error) {
    ElMessage.error("导出失败");
  } finally {
    loading.value = false;
  }
}
```

### 3. 模板

```vue
<el-button :loading="loading" @click="handleExport">导出 Excel</el-button>
```

## 三、注意事项

### 1. 中文排序

MySQL 中对中文字段排序时，使用 `CONVERT(column USING gbk)` 确保按拼音排序：

```csharp
query = query.OrderBy("CONVERT(d.DeptName USING gbk), CONVERT(m.Location USING gbk)");
```

### 2. 空值处理

在 Select 投影时处理可能的 null 值：

```csharp
Location = m.Location ?? "-",
RealName = u.RealName ?? "-"
```

### 3. 文件名编码

HTTP Header 不支持中文，必须使用 URL 编码：

```csharp
var encodedFileName = Uri.EscapeDataString(fileName);
Response.Headers.Append("Content-Disposition", $"attachment; filename*=UTF-8''{encodedFileName}");
```

### 4. 性能考虑

- 使用 Select 投影只查询需要的字段，避免查询大对象
- 导出大量数据时考虑分批处理或限制最大导出条数

### 5. 序号列

`ExcelHelper.ExportToExcel` 会自动添加"序号"列，导出 DTO 不需要定义序号属性。

### 6. 前端 Axios 响应拦截器处理

**重要**：Axios 响应拦截器需要对 blob 类型响应进行特殊处理，否则会因为 blob 没有 `code` 属性而报错。

```typescript
// src/api/request.ts
service.interceptors.response.use(
  (response: AxiosResponse) => {
    // 对于 blob 类型响应，直接返回 data
    if (response.config.responseType === 'blob') {
      return response.data
    }

    const res = response.data
    if (res.code !== 200) {
      // ... 错误处理
    }
    return res
  },
  // ...
)
```

## 四、ExcelHelper 说明

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

## 五、常见问题

### Q1: 导出文件名乱码

**原因**：HTTP Header 不支持非 ASCII 字符

**解决**：使用 `Uri.EscapeDataString()` 编码文件名，并使用 `filename*=UTF-8''` 格式

### Q2: 中文排序不按拼音

**原因**：MySQL 默认使用 UTF-8 编码排序

**解决**：使用 `ORDER BY CONVERT(column USING gbk)`

### Q3: Excel 列顺序不一致

**原因**：DTO 属性定义顺序影响列顺序

**解决**：按期望的列顺序定义 DTO 属性

### Q4: 导出数据量过大导致超时

**解决**：

1. 使用 Select 投影减少查询数据量
2. 考虑添加最大导出条数限制
3. 对于大数据量导出，考虑异步任务方案

### Q5: 前端导出时报错 "Cannot read property 'code' of undefined"

**原因**：Axios 响应拦截器尝试读取 `response.data.code`，但 blob 响应没有 `code` 属性

**解决**：在响应拦截器中判断 `responseType === 'blob'`，直接返回原始数据

```typescript
if (response.config.responseType === 'blob') {
  return response.data
}
```
