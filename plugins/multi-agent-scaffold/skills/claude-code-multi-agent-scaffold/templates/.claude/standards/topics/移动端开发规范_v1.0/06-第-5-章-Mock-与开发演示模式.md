# 移动端开发规范_v1.0 · 第 5 章 Mock 与开发演示模式

> 拆分自《移动端开发规范_v1.0》第 6 节。需要全量上下文时读原文件。


### 原则

前端可独立于后端开发与演示。Mock 数据须逼真（模拟延迟、错误）且不可变（防污染），使开发期与演示期行为接近真实，且后端就绪后可一键切换。

### 抽象规则

- `MUST` 用编译时 `dart-define` 注入 Mock 开关，无运行时分支。
- Mock 数据 `MUST` 以深不可变缓存返回，防调用方修改污染缓存。
- `SHOULD` 模拟网络延迟与错误场景。
- `MAY` 提供演示账号与演示旅程。
- 后端就绪后 `MUST` 可一键切换真实模式（改 `dart-define` 即可，无业务代码改动）。

### 代码示例

深不可变缓存 + 延迟模拟：

```dart
class MockApiClient {
  static final MockApiClient _instance = MockApiClient._();
  factory MockApiClient() => _instance;
  MockApiClient._();

  final Map<String, Map<String, dynamic>> _cache = {};

  Future<Map<String, dynamic>> loadMockData(String filename) async {
    if (_cache.containsKey(filename)) return _cache[filename]!;
    final json = await rootBundle.loadString('assets/mock_data/$filename');
    final decoded = jsonDecode(json) as Map<String, dynamic>;
    final frozen = _deepUnmodifiable(decoded) as Map<String, dynamic>;
    _cache[filename] = frozen;
    return frozen;
  }

  Future<void> simulateLatency() async =>
      Future.delayed(Duration(milliseconds: ApiConfig.mockLatencyMs));

  // 递归转不可变，防调用方修改污染缓存
  static dynamic _deepUnmodifiable(dynamic source) {
    if (source is Map<String, dynamic>) {
      final result = <String, dynamic>{};
      source.forEach((k, v) => result[k] = _deepUnmodifiable(v));
      return Map<String, dynamic>.unmodifiable(result);
    } else if (source is List) {
      return List.unmodifiable(source.map(_deepUnmodifiable));
    }
    return source;
  }
}
```

### ⛔ 反模式

- 可变缓存被调用方修改--后续读取得到脏数据
- Mock 与 Real 接口签名不一致--切换时崩溃
- Release 包误带 Mock--生产环境返回假数据

---

