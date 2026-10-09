namespace {{CodeName}}.Common;

/// <summary>
/// 分页结果
/// </summary>
public class PageResult<T>
{
    /// <summary>
    /// 数据列表
    /// </summary>
    public List<T> Items { get; set; } = new();

    /// <summary>
    /// 总条数
    /// </summary>
    public int Total { get; set; }

    /// <summary>
    /// 当前页码
    /// </summary>
    public int PageIndex { get; set; }

    /// <summary>
    /// 每页条数
    /// </summary>
    public int PageSize { get; set; }
}

/// <summary>
/// 分页查询请求基类
/// </summary>
public abstract class PageRequest
{
    /// <summary>
    /// 页码（从1开始）
    /// </summary>
    public int PageIndex { get; set; } = 1;

    /// <summary>
    /// 每页条数
    /// </summary>
    public int PageSize { get; set; } = 20;

    /// <summary>
    /// 规范化分页参数
    /// </summary>
    public virtual void Normalize()
    {
        if (PageIndex < 1) PageIndex = 1;
        if (PageSize < 1) PageSize = 20;
        if (PageSize > 100) PageSize = 100;
    }
}
