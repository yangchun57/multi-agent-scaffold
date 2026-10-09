# New API 文档 HTML 生成规范

> 本规范定义 `docs/` 目录下所有 HTML 文档的统一写法。生成新文档时，**只写裸 HTML 骨架 + 内容**，样式统一由 `docs/common.css` 提供，图标统一使用 Ant Design 内联 SVG。

---

## 一、目录结构约定

```
docs/
├── common.css              # 全站共享样式（唯一样式来源，勿在文档内嵌 <style>）
├── *.html                  # 各业务文档（裸 HTML，引用 common.css）
└── _模板与规范/             # 本规范 + 模板（下划线前缀，不参与业务交付）
    ├── README-规范说明.md   # 本文件
    ├── 模板-裸HTML.html      # 可直接复制的空白模板（含全部组件示例）
    └── 图标速查表.html       # 164 个常用图标 + 可复制的内联 SVG 代码
```

命名约定：
- 业务文档：`NewAPI + 主题 + 文档类型.html`，如 `NewAPI易支付接入支付宝微信配置教程.html`。
- 下划线 `_` 开头的文件/文件夹为辅助资源，不视为业务文档。

---

## 二、文档骨架（必须遵循）

每个文档 `<head>` 只放一个样式引用，**不内嵌 `<style>`**：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>标题</title>
<link rel="stylesheet" href="common.css">
</head>
<body>
<div class="wrap">
  <!-- hero / toc / section 结构，见模板 -->
</div>
</body>
</html>
```

要点：
1. `common.css` 的引用路径是相对路径 `common.css`（文档与 CSS 同在 `docs/` 下）。
2. 所有内容包在 `.wrap` 容器里。
3. 图标用内联 `<svg class="icon">`，**零外部依赖**（本机对公共 CDN 不通，禁止再引 Font Awesome / 任何 CDN）。

---

## 三、可用组件清单（均定义在 common.css）

### 布局
| class | 用途 |
|---|---|
| `.wrap` | 页面主容器，居中 + 左右留白 |
| `.hero` | 顶部头图（紫渐变），内含 `.tag` / `h1` / `p` / `.meta` |
| `.hero .tag` | 头图左上角小标签 |
| `.hero .meta` | 头图底部元信息（日期/版本/耗时等），用 `<span>` 包裹 |
| `.toc` | 目录卡片，`<h2>` 标题 + `<ol><li><a href="#id">` |
| `section` + `.sec` | 章节卡片，`<section id="sN"><div class="sec">...` |

### 章节内部
| class | 用途 |
|---|---|
| `.sec h2 .num` | 章节标题前的数字徽章（`<span class="num">1</span>`） |
| `.sec .lead` | 章节引导语（灰色小字） |
| `.sec h3` | 三级标题，可带 `<svg class="icon">` 图标 |
| `.sec p` / `.sec ul` / `.sec ol` / `.sec li` | 正文 / 列表 |
| `code.inline` | 行内代码（橙字灰底） |
| `pre` | 代码块（深色底）；注释可用 `pre .cm`（灰色） |

### 语义组件
| class | 用途 |
|---|---|
| `.box.tip` / `.warn` / `.error` / `.info` | 提示框（绿/橙/红/蓝），内部用 `<span class="bt">标题</span>` |
| `table` | 表格（th 蓝灰底、斑马纹、`td code` 行内代码样式） |
| `.verdict` | 结论框（金色渐变），含 `.icon`（圆图标）+ `b` + `p` |
| `.badge.hard` / `.mid` / `.easy` / `.blue` / `.purple` | 徽章（难度/标签） |
| `.meter` | 评分条（`.label` + `.bar` + `.fill` + `.val`） |
| `.repo` | 项目卡片（`.logo` + `.hd b` + `.desc` + `.tags` + `a.repolink`） |
| `.ref` | 参考来源（`<ul class="ref"><li>...`） |

### 步骤流（两种，二选一）
| class | 用途 |
|---|---|
| `.steps > li` | 纵向步骤（数字圆点 + 连线），用于方案/流程类 |
| `.step` | 卡片式步骤（数字圆点 + 卡片底），用于教程类 |

```html
<!-- 方式一：纵向步骤 -->
<ol class="steps">
  <li><b>步骤标题</b><span class="desc">说明文字</span></li>
  <li><b>步骤标题</b><span class="desc">说明文字</span></li>
</ol>

<!-- 方式二：卡片步骤 -->
<div class="steps">
  <div class="step"><b>步骤标题</b><p>说明文字</p></div>
  <div class="step"><b>步骤标题</b><p>说明文字</p></div>
</div>
```

> 注意：`.step` 卡片变体必须放在 `.steps` 容器内（以触发 `counter-reset`），数字才会从 1 开始正确计数。

---

## 四、图标规范

- **图标来源**：阿里巴巴 Ant Design Icons（MIT 协议），内联 SVG。
- **标准写法**：`<svg class="icon" viewBox="64 64 896 896" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><path fill="currentColor" d="..."/></svg>`
- **关键属性**：`class="icon"`（继承字号缩放、垂直对齐）、`fill="currentColor"`（继承文字颜色）、`aria-hidden="true"`（无障碍隐藏）。
- **多 path 图标**：部分图标含多个 `<path>`（如 `check-circle` 有对勾 + 外圈两条），照抄即可。
- **viewBox**：绝大多数是 `64 64 896 896`；个别（如 `unordered-list`）是 `0 0 1024 1024`，以速查表为准。
- **查图标**：打开 `_模板与规范/图标速查表.html`，找到目标图标，复制其完整 `<svg>...</svg>` 代码。
- **新增图标**：从 npm 包 `@ant-design/icons-svg` 的 `es/asn/<组件名>.js` 里取 `viewBox` 和 `d`（`children` 里的 path 数组）。

---

## 五、写作约定

1. **标题层级**：`hero h1`（文档标题）→ `sec h2`（一级章节，配 `.num` 数字）→ `sec h3`（二级小节，配图标）。
2. **章节锚点**：每个 `<section>` 加 `id="s1"、"s2"...`，目录 `<a href="#s1">` 对应。
3. **配色**：主色紫（`--accent:#6d28d9`），语义色绿/橙/红/蓝，勿在正文里写死颜色。
4. **结论先行**：用 `.verdict` 或 `.box.tip` 先给结论，再展开论证（现有文档惯例）。
5. **表格**：对比、参数、清单类信息优先用表格。
6. **代码**：命令/配置用 `pre`，行内文件名/参数用 `code.inline`。
7. **图标不滥用**：图标用于 `hero.tag`、`meta`、`h2/h3` 标题、`box.bt` 标题处即可，正文不堆图标。

---

## 六、质量检查清单（生成后自检）

- [ ] `<head>` 只有 `common.css` 一个样式引用，无内嵌 `<style>`、无 CDN 链接。
- [ ] 所有内容在 `.wrap` 内；`section` 都有 `id` 且与目录锚点一致。
- [ ] 图标全部为内联 SVG，含 `class="icon"` + `fill="currentColor"`。
- [ ] 无 emoji（用户明确禁用）；如需要图形语义一律用 Ant Design 图标。
- [ ] 配色只用 CSS 变量定义的语义色，未写死颜色值。
- [ ] 响应式：窄屏（≤720px）下表格、代码块、头图不溢出。

---

## 七、常用图标速查（高频）

| 场景 | 图标名 |
|---|---|
| 勾选/完成 | `check-circle`、`check-square` |
| 警告/错误 | `warning`、`exclamation-circle`、`close-circle` |
| 信息/帮助 | `info-circle`、`question-circle` |
| 安全/权限 | `safety-certificate`、`lock`、`key` |
| 数据/代码 | `database`、`server`→`cluster`、`code`、`file-text` |
| 支付/金融 | `wallet`、`pay-circle`、`alipay`、`wechat` |
| 时间/流程 | `calendar`、`clock-circle`、`history`、`sync` |
| 文档/编辑 | `book`、`edit`、`save`、`delete` |
| 部署/DevOps | `github`、`docker`、`build`、`deployment-unit` |

> 注：Ant Design 无 `server` 图标，用 `cluster` 或 `database` 替代；无 `file-code`，用 `code` 替代。
