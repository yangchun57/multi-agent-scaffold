# 并发与资源管理规范 · CancellationToken 规范

> 对应问题：M-13（Async 方法缺少 CancellationToken）

## 强制规则

### 1. 所有 Async 方法必须传递 CancellationToken

```csharp
// ❌ 错误：缺少 CancellationToken
public interface IRegistrationService
{
    Task<List<Registration>> GetAll();
    Task<Registration> GetById(long id);
    Task<long> Create(Registration entity);
    Task<bool> Update(Registration entity);
    Task<bool> Delete(long id);
}

// ✅ 正确：所有方法传递 CancellationToken
public interface IRegistrationService
{
    Task<List<Registration>> GetAll(CancellationToken cancellationToken = default);
    Task<Registration?> GetById(long id, CancellationToken cancellationToken = default);
    Task<long> Create(Registration entity, CancellationToken cancellationToken = default);
    Task<bool> Update(Registration entity, CancellationToken cancellationToken = default);
    Task<bool> Delete(long id, CancellationToken cancellationToken = default);
}
```

### 2. Service 实现必须传递 CancellationToken

```csharp
public class RegistrationService : IRegistrationService
{
    private readonly ISqlSugarClient _db;
    
    public RegistrationService(ISqlSugarClient db)
    {
        _db = db;
    }
    
    // ✅ 正确：传递到 ORM 查询
    public async Task<List<Registration>> GetAll(CancellationToken cancellationToken = default)
    {
        return await _db.Queryable<Registration>()
            .ToListAsync(cancellationToken);
    }
    
    public async Task<Registration?> GetById(long id, CancellationToken cancellationToken = default)
    {
        return await _db.Queryable<Registration>()
            .Where(r => r.Id == id)
            .FirstAsync(cancellationToken);
    }
    
    public async Task<long> Create(Registration entity, CancellationToken cancellationToken = default)
    {
        return await _db.Insertable(entity)
            .ExecuteReturnSnowflakeIdAsync(cancellationToken);
    }
}
```

### 3. Controller 传递 HttpContext.RequestAborted

```csharp
[ApiController]
[Route("api/[controller]")]
public class RegistrationController : ControllerBase
{
    private readonly IRegistrationService _service;
    
    public RegistrationController(IRegistrationService service)
    {
        _service = service;
    }
    
    [HttpGet]
    public async Task<ApiResult<List<Registration>>> GetAll()
    {
        // ✅ 正确：传递 HttpContext 的取消令牌
        var data = await _service.GetAll(HttpContext.RequestAborted);
        return ApiResult.Ok(data);
    }
    
    [HttpPost]
    public async Task<ApiResult<long>> Create([FromBody] CreateRequest request)
    {
        var entity = new Registration
        {
            Name = request.Name,
            Phone = request.Phone
        };
        
        var id = await _service.Create(entity, HttpContext.RequestAborted);
        return ApiResult.Ok(id);
    }
}
```

### 4. 前端请求取消

```typescript
// ✅ 正确：组件卸载时取消请求
import { ref, onUnmounted } from 'vue'
import axios from 'axios'

const loadData = async () => {
  const controller = new AbortController()
  
  // 组件卸载时取消
  onUnmounted(() => {
    controller.abort()
  })
  
  try {
    const res = await axios.get('/api/registrations', {
      signal: controller.signal
    })
    tableData.value = res.data.data
  } catch (error) {
    if (axios.isCancel(error)) {
      console.log('请求已取消')
      return
    }
    ElMessage.error('加载失败')
  }
}
```

## 检查清单

- [ ] 所有 Async 方法签名包含 `CancellationToken cancellationToken = default`
- [ ] ORM 查询方法传递 cancellationToken
- [ ] Controller 传递 `HttpContext.RequestAborted`
- [ ] 前端长耗时请求支持 AbortController 取消
