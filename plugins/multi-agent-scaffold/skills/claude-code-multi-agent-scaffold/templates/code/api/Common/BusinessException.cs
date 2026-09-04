namespace {{CodeName}}.Common;

/// <summary>
/// 业务异常（可预期的业务错误）
/// </summary>
public class BusinessException : Exception
{
    /// <summary>
    /// 错误码
    /// </summary>
    public int Code { get; set; } = 400;

    public BusinessException(string message, int code = 400) : base(message)
    {
        Code = code;
    }
}

/// <summary>
/// 实体未找到异常
/// </summary>
public class NotFoundException : BusinessException
{
    public NotFoundException(string entityName, object id)
        : base($"{entityName}不存在: {id}", 404)
    {
    }
}
