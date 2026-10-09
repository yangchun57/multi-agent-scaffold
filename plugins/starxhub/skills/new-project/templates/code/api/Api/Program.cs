using {{CodeName}}.Api.Filters;

var builder = WebApplication.CreateBuilder(args);

// 控制器 + 全局异常过滤器
builder.Services.AddControllers(options =>
{
    options.Filters.Add<GlobalExceptionFilter>();
});

// Swagger/OpenAPI
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

var app = builder.Build();

if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseAuthorization();
app.MapControllers();

app.Run();

// 集成测试 WebApplicationFactory<Program> 需要 Program 可见
public partial class Program { }
