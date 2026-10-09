# 通用开发规范 · 六、Excel 导出功能规范

> 拆分自《通用开发规范》第 6 节。需要全量上下文时读原文件。


### 6.1 后端实现规范

#### 6.1.1 接口定义

```csharp
/// <summary>
/// 导出 Excel
/// </summary>
[HttpGet("export")]
public async Task<IActionResult> Export([FromQuery] EntityQueryRequest request)
{
    // 1. 构建查询
    var query = _db.Queryable<Entity>()
        .Where(e => e.Id > 0);

    // 2. 应用筛选条件
    if (!string.IsNullOrWhiteSpace(request.Keyword))
    {
        query = query.Where(e => e.Name.Contains(request.Keyword));
    }

    // 3. 执行查询
    var data = await query
        .OrderBy(e => e.SortOrder)
        .Select<EntityExportDto>()
        .ToListAsync();

    // 4. 生成 Excel
    var memoryStream = ExcelHelper.ExportToExcel(data, "数据");
    var fileName = $"数据_{DateTime.Now:yyyyMMddHHmmss}.xlsx";
    var encodedFileName = Uri.EscapeDataString(fileName);
    Response.Headers.Append("Content-Disposition", $"attachment; filename*=UTF-8''{encodedFileName}");
    return File(memoryStream, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet");
}
```

#### 6.1.2 导出 DTO

```csharp
/// <summary>
/// 导出DTO
/// </summary>
public class EntityExportDto
{
    [System.ComponentModel.DisplayName("编码")]
    public string Code { get; set; } = string.Empty;

    [System.ComponentModel.DisplayName("名称")]
    public string Name { get; set; } = string.Empty;

    [System.ComponentModel.DisplayName("状态")]
    public string Status { get; set; } = string.Empty;
}
```

### 6.2 前端实现规范

```typescript
// API 函数
export function exportEntity(params: EntityQuery): Promise<Blob> {
  return request.get("/entity/export", {
    params,
    responseType: "blob",
  });
}

// 导出处理
async function handleExport() {
  loading.value = true;
  try {
    const blob = await exportEntity(query);
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `数据_${Date.now()}.xlsx`;
    a.click();
    window.URL.revokeObjectURL(url);
  } catch (error) {
    ElMessage.error("导出失败");
  } finally {
    loading.value = false;
  }
}
```

### 6.3 注意事项

1. **文件名编码**：使用 `Uri.EscapeDataString()` 编码文件名
2. **中文排序**：使用 `CONVERT(column USING gbk)` 确保按拼音排序
3. **空值处理**：在 Select 投影时处理 null 值
4. **Axios 拦截器**：对 blob 类型响应进行特殊处理

---

