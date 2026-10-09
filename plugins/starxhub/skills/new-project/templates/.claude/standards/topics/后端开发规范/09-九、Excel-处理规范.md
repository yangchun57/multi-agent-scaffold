# 后端开发规范 · 九、Excel 处理规范

> 拆分自《后端开发规范》第 9 节。需要全量上下文时读原文件。


### 9.1 导入规范

```csharp
/// <summary>
/// Excel 导入结果
/// </summary>
public class ImportResult
{
    /// <summary>
    /// 成功数量
    /// </summary>
    public int SuccessCount { get; set; }

    /// <summary>
    /// 失败数量
    /// </summary>
    public int FailCount { get; set; }

    /// <summary>
    /// 错误详情
    /// </summary>
    public List<ImportError> Errors { get; set; } = new();
}

/// <summary>
/// 导入错误
/// </summary>
public class ImportError
{
    /// <summary>
    /// 行号
    /// </summary>
    public int Row { get; set; }

    /// <summary>
    /// 错误原因
    /// </summary>
    public string Reason { get; set; } = string.Empty;
}

/// <summary>
/// Excel 导入服务示例
/// </summary>
public async Task<ImportResult> ImportMetersAsync(IFormFile file)
{
    var result = new ImportResult();

    using var stream = file.OpenReadStream();
    var rows = stream.Query<MeterImportRow>(startCell: "A2").ToList();

    for (int i = 0; i < rows.Count; i++)
    {
        var row = rows[i];
        var rowNum = i + 2; // Excel 行号从 2 开始（第1行是表头）

        try
        {
            // 校验数据
            if (string.IsNullOrEmpty(row.DeptCode))
            {
                result.Errors.Add(new ImportError { Row = rowNum, Reason = "部门编码不能为空" });
                result.FailCount++;
                continue;
            }

            // 查找部门
            var dept = await _db.Queryable<SysDepartment>()
                .Where(d => d.DeptCode == row.DeptCode)
                .FirstAsync();

            if (dept == null)
            {
                result.Errors.Add(new ImportError { Row = rowNum, Reason = $"部门不存在: {row.DeptCode}" });
                result.FailCount++;
                continue;
            }

            // 创建实体
            var entity = new SysMeter
            {
                DeptId = dept.DeptId,
                MeterType = row.MeterType == "电表" ? MeterType.Electric : MeterType.Water,
                SeqNo = row.SeqNo,
                MeterNo = row.MeterNo,
                Location = row.Location,
                Status = MeterStatus.Active
            };

            await _db.Insertable(entity).ExecuteCommandAsync();
            result.SuccessCount++;
        }
        catch (Exception ex)
        {
            result.Errors.Add(new ImportError { Row = rowNum, Reason = ex.Message });
            result.FailCount++;
        }
    }

    return result;
}
```

### 9.2 导出规范

```csharp
/// <summary>
/// 导出部门数据
/// </summary>
public async Task<byte[]> ExportDepartmentsAsync(DepartmentQueryRequest request)
{
    var list = await _departmentService.GetListAsync(request);

    var exportData = list.Select(d => new
    {
        部门编码 = d.DeptCode,
        部门名称 = d.DeptName,
        联系人 = d.ContactPerson,
        联系电话 = d.ContactPhone,
        状态 = d.IsEnabled ? "启用" : "禁用",
        备注 = d.Remark
    }).ToList();

    using var stream = new MemoryStream();
    await stream.SaveAsAsync(exportData);
    return stream.ToArray();
}
```

### 9.3 Controller 导出接口

```csharp
/// <summary>
/// 导出部门数据
/// </summary>
[HttpGet("export")]
[Authorize(Roles = "admin")]
public async Task<IActionResult> Export([FromQuery] DepartmentQueryRequest request)
{
    var bytes = await _departmentService.ExportAsync(request);
    var fileName = $"部门数据_{DateTime.Now:yyyyMMddHHmmss}.xlsx";

    return File(bytes,
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        fileName);
}
```

---

