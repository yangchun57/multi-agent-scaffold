# 安全编码规范 · JWT 与 HTTPS 规范

> 对应问题：H-3（JWT 密钥未校验长度）、H-4（缺少 HTTPS 强制）

## JWT 密钥校验

### 强制规则：启动时校验密钥长度

```csharp
// Program.cs
var jwtSettings = builder.Configuration.GetSection("Jwt");
var secretKey = jwtSettings["SecretKey"];

// ✅ 强制：启动时校验密钥长度
if (string.IsNullOrEmpty(secretKey) || secretKey.Length < 32)
{
    throw new InvalidOperationException(
        "JWT SecretKey 必须至少 32 字符（256 位），当前配置无效。" +
        "请在 appsettings.Production.json 中配置安全的密钥。");
}

builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {
        options.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = true,
            ValidateAudience = true,
            ValidateLifetime = true,
            ValidateIssuerSigningKey = true,
            ValidIssuer = jwtSettings["Issuer"],
            ValidAudience = jwtSettings["Audience"],
            IssuerSigningKey = new SymmetricSecurityKey(
                Encoding.UTF8.GetBytes(secretKey))
        };
    });
```

### 密钥生成建议

```bash
# 生成 256 位随机密钥（32 字符 Base64）
openssl rand -base64 32

# 或 64 字符十六进制
openssl rand -hex 32
```

### 配置示例

```json
// appsettings.json（开发环境，仅用于本地调试）
{
  "Jwt": {
    "SecretKey": "dev-only-key-must-be-at-least-32-chars-long!",
    "Issuer": "hnu-waterelec",
    "Audience": "hnu-waterelec-api",
    "ExpirationMinutes": 480
  }
}

// appsettings.Production.json（生产环境）
{
  "Jwt": {
    "SecretKey": "${JWT_SECRET_KEY}",  // 从环境变量读取
    "Issuer": "hnu-waterelec",
    "Audience": "hnu-waterelec-api",
    "ExpirationMinutes": 120  // 生产环境缩短有效期
  }
}
```

## HTTPS 强制

### 强制规则：生产环境必须强制 HTTPS

```csharp
// Program.cs
if (!builder.Environment.IsDevelopment())
{
    // ✅ 强制 HTTPS
    app.UseHttpsRedirection();
    
    // HSTS（可选，推荐）
    app.UseHsts();
}

// 或在 Kestrel 配置中强制
builder.WebHost.ConfigureKestrel(options =>
{
    options.ConfigureHttpsDefaults(httpsOptions =>
    {
        httpsOptions.SslProtocols = System.Security.Authentication.SslProtocols.Tls12 | 
                                     System.Security.Authentication.SslProtocols.Tls13;
    });
});
```

### 开发环境例外

```csharp
// 开发环境允许 HTTP（但应提示）
if (builder.Environment.IsDevelopment())
{
    app.UseDeveloperExceptionPage();
    // 不强制 HTTPS，方便本地调试
}
else
{
    app.UseHttpsRedirection();
    app.UseHsts();
}
```

## 检查清单

- [ ] JWT 密钥长度 ≥ 32 字符（256 位）
- [ ] 启动时校验密钥有效性，无效则拒绝启动
- [ ] 生产环境配置 `UseHttpsRedirection()`
- [ ] 生产环境 JWT 有效期 ≤ 2 小时
- [ ] 密钥从环境变量或密钥管理服务读取，不硬编码
