using Microsoft.AspNetCore.Mvc.Testing;
using Xunit;

namespace {{CodeName}}.Tests.Integration;

/// <summary>
/// 集成测试基类：基于 WebApplicationFactory 启动完整 API 管道（不含真实数据库）
/// 红线类约束（如租户隔离、认证授权）优先用集成测试锁死，比文档更硬。
/// </summary>
public abstract class IntegrationTestBase : IClassFixture<WebApplicationFactory<Program>>
{
    protected readonly HttpClient Client;

    protected IntegrationTestBase(WebApplicationFactory<Program> factory)
    {
        Client = factory.CreateClient();
    }
}

// 用法示例（继承本类编写集成测试）：
//
// public class HealthTests : IntegrationTestBase
// {
//     public HealthTests(WebApplicationFactory<Program> factory) : base(factory) { }
//
//     [Fact]
//     public async Task UnknownTenant_CannotSeeOtherTenantData()
//     {
//         // Arrange: 以租户 A 身份请求租户 B 的资源
//         // Act: GET /api/xxx/{B 的资源 id}
//         // Assert: 404 或 403（绝不能 200）
//     }
// }
