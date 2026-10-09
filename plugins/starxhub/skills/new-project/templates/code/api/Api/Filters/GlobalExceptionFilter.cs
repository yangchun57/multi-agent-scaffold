using {{CodeName}}.Common;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Filters;

namespace {{CodeName}}.Api.Filters;

/// <summary>
/// 全局异常处理过滤器
/// </summary>
public class GlobalExceptionFilter : IExceptionFilter
{
    private readonly ILogger<GlobalExceptionFilter> _logger;

    public GlobalExceptionFilter(ILogger<GlobalExceptionFilter> logger)
    {
        _logger = logger;
    }

    public void OnException(ExceptionContext context)
    {
        var exception = context.Exception;
        int code;
        string message;

        if (exception is BusinessException businessException)
        {
            code = businessException.Code;
            message = businessException.Message;
            _logger.LogWarning(exception, "业务异常: {Message}", message);
        }
        else
        {
            code = 500;
            message = "服务器内部错误";
            _logger.LogError(exception, "未处理异常: {Message}", exception.Message);
        }

        var result = new JsonResult(new ApiResult<object>
        {
            Code = code,
            Message = message,
            Data = null
        })
        {
            StatusCode = 200
        };

        context.Result = result;
        context.ExceptionHandled = true;
    }
}
