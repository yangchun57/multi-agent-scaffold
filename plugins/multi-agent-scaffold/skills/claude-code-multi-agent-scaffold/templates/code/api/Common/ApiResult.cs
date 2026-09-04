namespace {{CodeName}}.Common;

/// <summary>
/// 统一 API 响应格式
/// </summary>
public class ApiResult<T>
{
    /// <summary>
    /// 状态码
    /// </summary>
    public int Code { get; set; }

    /// <summary>
    /// 消息
    /// </summary>
    public string Message { get; set; } = string.Empty;

    /// <summary>
    /// 数据
    /// </summary>
    public T? Data { get; set; }

    /// <summary>
    /// 时间戳
    /// </summary>
    public long Timestamp { get; set; } = DateTimeOffset.UtcNow.ToUnixTimeSeconds();

    /// <summary>
    /// 成功响应
    /// </summary>
    public static ApiResult<T> Success(T? data, string message = "操作成功")
    {
        return new ApiResult<T>
        {
            Code = 200,
            Message = message,
            Data = data
        };
    }

    /// <summary>
    /// 失败响应
    /// </summary>
    public static ApiResult<T> Fail(string message, int code = 400)
    {
        return new ApiResult<T>
        {
            Code = code,
            Message = message,
            Data = default
        };
    }
}
