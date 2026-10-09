# Python 后台开发规范

> 适用范围：基于 FastAPI + SQLAlchemy 2.0 + Pydantic v2 技术栈的 Python 后台服务。
> 本规范为通用工程规范，不绑定任何具体业务；示例代码均为通用实体。

## 1. 技术栈与版本基线

| 组件 | 选型 | 最低版本 |
|------|------|----------|
| Web 框架 | FastAPI | 0.115 |
| ASGI 服务器 | uvicorn[standard] | 0.30 |
| ORM | SQLAlchemy（2.x 风格） | 2.0 |
| 数据校验 / DTO | Pydantic | 2.7 |
| 配置管理 | pydantic-settings | 2.3 |
| JWT | PyJWT | 2.8 |
| 密码哈希 | passlib（pbkdf2_sha256） | 1.7.4 |
| HTTP 客户端 | httpx | 0.27 |
| 测试框架 | pytest + fastapi.testclient | 8.2 |

约定：

- 依赖一律写入 `requirements.txt`，使用 `>=` 下限约束，禁止无版本约束的裸依赖。
- 新增第三方依赖需说明用途，避免引入功能重叠的库。
- Python 版本以 3.10+ 为基线（需支持 `X | None` 联合类型语法）。

## 2. 项目结构规范

```
backend/
├── app/                  # 应用代码根包
│   ├── main.py           # 应用入口：日志装配、中间件、路由挂载、健康检查
│   ├── config.py         # 全局配置（pydantic-settings）与路径常量
│   ├── database.py       # engine / SessionLocal / get_db 依赖
│   ├── api/              # 路由层：每个业务域一个模块，模块内定义 router
│   ├── schemas/          # Pydantic DTO（入参/出参），common.py 放通用信封
│   ├── models/           # SQLAlchemy ORM 模型，base.py 放 Base 与 Mixin
│   ├── services/         # 业务逻辑层：可复用的业务函数与第三方客户端
│   ├── core/             # 横切能力：安全、校验等与技术业务无关的基础设施
│   ├── engine/           # （可选）领域计算引擎等重逻辑模块
│   └── tasks/            # 后台异步任务 / 流水线
├── scripts/              # 运维与种子脚本（python -m scripts.xxx 执行）
├── tests/                # 全部测试，文件名 test_*.py
├── data/                 # 运行时数据目录（数据库、上传文件、向量库），禁止入库
├── .env                  # 本地敏感配置，禁止入库
├── pytest.ini
├── conftest.py
└── requirements.txt
```

规则：

- 每个目录均为 Python 包，必须包含 `__init__.py`。
- `models/` 与 `schemas/` 按业务域拆分文件（如 `user.py`、`project.py`），在各自 `__init__.py` 中统一再导出，外部一律 `from app.models import Xxx`。
- `data/`、`.env`、`__pycache__/`、`.pytest_cache/` 必须加入 `.gitignore`。

## 3. 配置管理规范

### 3.1 统一入口

全部配置集中在 `app/config.py` 的 `Settings(BaseSettings)` 类中，禁止在业务代码里散落硬编码配置。

```python
# app/config.py
from pathlib import Path
from pydantic_settings import BaseSettings

BACKEND_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BACKEND_DIR / "data"

class Settings(BaseSettings):
    app_name: str = "应用名"
    secret_key: str = "change-in-prod-..."   # 生产必须经环境变量覆盖
    token_expire_minutes: int = 480
    database_url: str = f"sqlite:///{DATA_DIR / 'app.db'}"

    model_config = {"env_file": str(BACKEND_DIR / ".env"), "env_file_encoding": "utf-8"}

settings = Settings()
```

### 3.2 规则

- 敏感项（密钥、API Key、数据库口令）只允许通过环境变量或 `.env` 注入，代码中的默认值仅限本地开发可用。
- 生产环境 `secret_key` 必须为 ≥32 字符强密钥。
- 路径常量（`BACKEND_DIR`、`DATA_DIR`、上传目录等）在 `config.py` 中基于 `Path(__file__)` 推导，禁止业务代码自行拼接相对路径。
- 运行时必需的目录（数据目录、上传目录）在 `config.py` 模块加载时 `mkdir(parents=True, exist_ok=True)`，保证幂等。
- 第三方服务参数（base_url、模型名、超时秒数）全部可配置，超时按最长业务场景给足上限。

## 4. 数据库与 ORM 规范

### 4.1 连接与会话

```python
# app/database.py
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},  # SQLite + 多线程必需
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

- API 层通过 `db: Session = Depends(get_db)` 获取会话，禁止在路由函数内手工创建 Session。
- 后台任务 / 脚本中使用 `with SessionLocal() as db:` 上下文管理，会话生命周期自管理。
- `expire_on_commit=False`，避免提交后访问对象触发隐式再查询。
- 更换数据库仅需改 `database_url`；使用 SQLite 时必须保留 `check_same_thread=False`。

### 4.2 模型定义

- 一律使用 SQLAlchemy 2.x 声明式风格：`DeclarativeBase` + `Mapped` + `mapped_column`，禁止旧式 `Column()` 写法。
- 公共字段通过 Mixin 复用（如 `TimestampMixin` 提供 `created_at`）。
- 显式声明 `__tablename__`，表名小写单数。
- 字段取值域以模块级常量元组定义（如 `STATUSES = ("pending", "running", "done", "failed")`），与模型同文件，并从 `app.models` 再导出。

```python
# app/models/base.py
class Base(DeclarativeBase):
    pass

class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

# app/models/user.py
class User(Base, TimestampMixin):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
```

### 4.3 查询

- 优先使用 2.x 风格 `select()` 语句 + `db.scalar / db.scalars`。
- 建表由 `Base.metadata.create_all(engine)` 完成（初始化脚本中调用）；生产有 schema 演进需求时引入 Alembic。

## 5. 分层职责规范

依赖方向严格单向：`api → services → models`，`schemas` 只在 `api` 与 `services` 边界使用。

| 层 | 职责 | 禁止事项 |
|----|------|----------|
| `api/` | 参数接收与校验、权限挂载、调用 service、组装 DTO 返回 | 禁止写复杂业务逻辑、禁止直接调第三方 SDK |
| `services/` | 业务逻辑、事务编排、第三方客户端封装 | 禁止依赖 FastAPI 的 Request/Response 对象 |
| `models/` | 表结构与常量定义 | 禁止包含业务方法 |
| `schemas/` | DTO 定义与校验规则 | 禁止包含业务逻辑 |
| `core/` | 与业务无关的横切能力（安全、文件校验等） | 禁止引用 models 之外的业务模块 |
| `tasks/` | 后台任务入口，按阶段拆分函数 | 禁止被路由同步调用阻塞请求 |

- 第三方 SDK（LLM、对象存储、短信等）必须封装为 `services/` 下的统一客户端模块，全项目只从该模块调用，禁止在多处直接实例化 SDK 客户端。

## 6. API 设计规范

### 6.1 路由组织

- 每个业务域一个 `app/api/<domain>.py`，模块内定义 `router = APIRouter(prefix="/api/<domain>", tags=["<中文名>"])`。
- 所有路由在 `app/api/__init__.py` 中集中 `include_router`，`main.py` 只挂载这一个总路由。
- 统一 `/api` 前缀；健康检查提供 `GET /api/health`。
- 需要登录的路由在 router 级别挂载：`dependencies=[Depends(get_current_user)]`，避免逐接口遗漏。

### 6.2 请求与响应

- 每个接口必须声明 `response_model`；入参用独立的 Pydantic Schema，禁止裸 `dict` 接收请求体。
- 入参与出参 Schema 分离，命名 `XxxIn` / `XxxOut`；出参 Schema 配置 `model_config = {"from_attributes": True}`，用 `XxxOut.model_validate(orm_obj)` 转换。
- 列表接口统一分页信封：

```python
class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int   # 过滤后总条数
    page: int    # 从 1 开始
    size: int    # 每页条数
```

- 分页参数带边界约束：`page: int = Query(1, ge=1)`，`size: int = Query(20, ge=1, le=100)`。
- 关键字搜索用 `ilike` 模糊匹配前先 `keyword.strip()`，空白关键字视为不过滤。

### 6.3 错误处理与状态码

- 业务错误一律 `raise HTTPException(status_code, detail="面向用户的中文描述")`，禁止返回 200 + 错误码的自定义信封。
- 状态码语义：

| 场景 | 状态码 |
|------|--------|
| 参数非法 / 文件类型大小不符 | 400 |
| 未登录 / token 失效 | 401 |
| 角色权限不足 | 403 |
| 资源不存在 | 404 |
| 服务端内部错误 | 500 |

- 登录失败等安全敏感场景，错误描述不得泄露具体原因（统一"用户名或密码错误"）。

## 7. 认证与安全规范

- 密码存储使用 `passlib` 的 `pbkdf2_sha256`（或更强的 argon2/bcrypt），禁止明文与可逆加密；统一走 `hash_password / verify_password` 函数。
- 令牌使用 JWT（HS256），`sub` 为用户 ID 字符串，携带 `role` 与 `exp`；过期时间集中配置。
- `get_current_user` 依赖中：token 解析失败、`sub` 非法、用户不存在一律返回 401，不区分细节。
- 管理员写接口使用 `require_admin` 依赖做后端强校验，前端隐藏入口不视为安全措施。
- CORS 生产部署必须收紧 `allow_origins`，禁止 `*` 上生产。

## 8. 文件上传与静态资源规范

- 上传前统一校验：MIME 类型与扩展名双重校验（两者满足其一即在白名单内）、文件大小上限校验；白名单与上限均为配置项。
- 落盘路径防穿越：`dest_dir / Path(file.filename).name`，只取文件名，禁止信任客户端传入的路径。
- 上传目录按业务维度分子目录（如 `uploads/<resource_type>/<owner_id>/`），目录不存在则 `mkdir(parents=True, exist_ok=True)`。
- 静态托管 / SPA 兜底路由必须注册在所有 API 路由之后；返回文件前 `resolve()` 并校验仍位于根目录内，防 `%2e%2e` 编码逃逸。

## 9. 异步任务与第三方集成规范

### 9.1 后台任务

- 耗时操作（OCR、报告生成、批量导入等）使用 `BackgroundTasks` 异步执行，API 立即返回。
- 任务以数据库状态机驱动，状态取值统一为 `pending / running / done / failed`。
- 多阶段流水线按阶段拆分为独立函数，每阶段独立更新状态、独立提交，单阶段失败不拖垮整体，支持单步重跑。
- 任务函数必须捕获全部异常并落 `failed` 状态（`except Exception` + 日志），单个任务失败不得影响服务进程。
- 重跑逻辑必须保护人工修正过的数据，不得无脑覆盖。

### 9.2 第三方客户端

- SDK 客户端懒加载单例（模块级 `_client` + `get_client()`）。
- 网络类调用必须带重试：指数退避（`2 ** attempt`），仅对可重试异常（连接错误、超时、限流、5xx）重试；4xx 等确定性失败直接抛出。
- 批量接口按供应商单批上限分片调用。
- 重试失败后抛 `RuntimeError(...) from last_err`，保留原始异常链。

## 10. 日志规范

- 每个模块使用 `logger = logging.getLogger(__name__)`，禁止直接 `print`（脚本交互输出除外）。
- handler 只挂载到项目命名空间的 logger（如 `app`），不要动 root logger，避免第三方库噪声；重复挂载需做幂等判断（`--reload` 场景）。
- 日志格式统一：`%(asctime)s %(levelname)s %(name)s: %(message)s`。
- 关键节点必须记录：任务开始/完成（含耗时与关键指标）、失败原因（warning 级）。
- 日志内容禁止包含密钥、token、口令等敏感信息。

## 11. 脚本规范

- 运维脚本放 `scripts/`，以 `python -m scripts.<name>` 方式从 backend 根目录执行。
- 脚本必须幂等（重复执行不产生重复数据），种子数据写入前先查重。
- 模块 docstring 写明用途与执行方式；`if __name__ == "__main__": main()` 收尾。
- 种子数据（规则、字典、演示账号）以 JSON/CSV 文件或脚本常量形式入库管理。

## 12. 测试规范

### 12.1 组织

- 测试全部位于 `tests/`，文件名 `test_*.py`，与被测模块对应（如 `test_projects_api.py`）。
- `pytest.ini` 显式配置收集范围，避免业务模块被误收集：

```ini
[pytest]
testpaths = tests
python_files = test_*.py
```

### 12.2 基础设施（conftest.py）

- 数据库使用内存 SQLite + `StaticPool`，每个测试独立建表，互不污染：

```python
engine = create_engine("sqlite://", connect_args={"check_same_thread": False},
                       poolclass=StaticPool)
Base.metadata.create_all(engine)
```

- 通过 `app.dependency_overrides[get_db]` 注入测试会话；覆盖函数必须是生成器函数（含 `yield`），fixture 退出时 `dependency_overrides.clear()`。
- 提供通用 fixture：`db_session`（裸会话）、`client`（TestClient）、`seeded_users`（基础账号）；鉴权接口测试通过真实登录接口换取 token（`auth_headers` fixture），同时覆盖认证链路。

### 12.3 用例要求

- 每个 API 至少覆盖：正常路径、未认证 401、资源不存在 404、参数非法 400。
- 断言具体的业务字段，而非仅断言状态码。
- 测试不得依赖真实第三方服务（LLM、外部 HTTP），必须 mock 或跳过。

## 13. 编码风格与命名

- 文件名、函数名、变量名：`snake_case`；类名：`PascalCase`；常量：`UPPER_SNAKE_CASE`。
- 路由模块中的路由实例统一命名 `router`。
- 类型注解：公开函数必须有完整参数与返回值注解；可选值用 `X | None = None`。
- 路径操作一律 `pathlib.Path`，禁止字符串拼接路径；Windows 环境含中文/空格的路径使用原始字符串或 Path。
- 中文注释与 docstring 允许且鼓励，重点解释"为什么"而非"是什么"。
- 宽泛捕获异常处必须加注释或 `# noqa` 说明理由（如"单任务失败不崩服务"）。
- 导入顺序：标准库 → 第三方 → 项目内（`app.*`），项目内导入按模块字母序。

## 14. 应用入口规范（main.py）

`main.py` 只做装配，不写业务：

1. 装配项目命名空间日志；
2. 创建 `FastAPI(title=settings.app_name)` 实例；
3. 注册中间件（CORS 等）；
4. `include_router(api_router)` 挂载总路由；
5. 提供 `GET /api/health` 健康检查；
6. （如需托管前端）最后注册静态资源与 SPA 兜底路由，且兜底路由做路径穿越校验。

## 15. 版本库管理

- `.gitignore` 必须包含：`data/`、`.env`、`__pycache__/`、`*.pyc`、`.pytest_cache/`。
- 运行时产物（数据库文件、上传文件、向量库、日志）一律不入库。
- 提交前必须本地通过全量 `pytest`。

---

## 变更记录

| 版本 | 日期 | 变更内容 | 作者 |
|------|------|----------|------|
| v0.1 | 2026-08-19 | 初版：提炼自现有后端框架的通用开发规范 | 开发组 |
