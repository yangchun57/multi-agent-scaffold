#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
md2html.py — 把 docs/ 交付物从 Markdown 转为符合「docs管理模板」规范的裸 HTML。
遵循 _模板与规范/README-规范说明.md：仅引 common.css、无内嵌 style、无 CDN、无 emoji、
.wrap/.hero/.toc/.sec 结构、table/pre/code.inline/.box 语义组件。

用法：python md2html.py <input.md> <output.html> [tag] [relcss]
"""
import html as H
import re
import sys

EMOJI_RE = re.compile(
    "[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF"
    "\U00002B00-\U00002BFF\U0000FE0F\U00002705\U0000274C\U00002714\u2713\u2717\u2714\u2718✅❌☑✗✔✘⚡→←⇒]"
)


def strip_emoji(s):
    return EMOJI_RE.sub("", s)


def inline(s):
    """行内元素：先转义，再 bold / code / link"""
    s = H.escape(strip_emoji(s), quote=False)
    s = re.sub(r"`([^`]+)`", r'<code class="inline">\1</code>', s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2" target="_blank">\1</a>', s)
    return s


def parse_table(lines, i):
    """从 i 开始解析表格，返回 (html, next_i)"""
    rows = []
    while i < len(lines) and lines[i].strip().startswith("|"):
        cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
        if not re.match(r"^:?-{2,}:?$", cells[0].replace(" ", "")) or len(cells) < 2 or any(
            not re.match(r"^:?-{2,}:?$", c.replace(" ", "")) for c in cells
        ):
            rows.append(cells)
        i += 1
    if not rows:
        return None, i
    out = ["<table>"]
    out.append("<tr>" + "".join(f"<th>{inline(c)}</th>" for c in rows[0]) + "</tr>")
    for r in rows[1:]:
        out.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>")
    out.append("</table>")
    return "\n".join(out), i


def parse_list(lines, i):
    """解析无序/有序列表（含一级嵌套）"""
    items = []  # (indent, ordered, text)
    while i < len(lines):
        line = lines[i]
        m = re.match(r"^(\s*)([-*]|\d+[.、])\s+(.*)", line)
        if not m:
            break
        indent = len(m.group(1)) // 2
        ordered = m.group(2)[0].isdigit()
        items.append((indent, ordered, m.group(3)))
        i += 1
    if not items:
        return None, i

    def build(idx, indent):
        ordered = items[idx][1]
        tag = "ol" if ordered else "ul"
        out = [f"<{tag}>"]
        while idx < len(items) and items[idx][0] >= indent:
            if items[idx][0] > indent:
                sub, idx = build(idx, items[idx][0])
                out.append(sub)
            else:
                txt = items[idx][2]
                # checkbox 支持
                txt = re.sub(r"^\[( |x|X)\]\s*", lambda m: "", txt)
                out.append(f"<li>{inline(txt)}</li>")
                idx += 1
        out.append(f"</{tag}>")
        return "\n".join(out), idx

    body, _ = build(0, items[0][0])
    return body, i


def convert(md_path, out_path, tag="", relcss="common.css"):
    with open(md_path, encoding="utf-8") as f:
        lines = f.read().split("\n")

    # 标题：首个 # 行；正文段落起点
    title, start = "", 0
    for i, ln in enumerate(lines):
        if ln.startswith("# ") and not title:
            title = ln[2:].strip()
            start = i + 1
            break
    if not title:
        title = md_path.split("/")[-1].replace(".md", "")

    # 摘要：标题后第一段非空、非 ## 的文字
    summary = ""
    for ln in lines[start:]:
        s = ln.strip()
        if s.startswith("#"):
            break
        if s and not s.startswith(">") and not s.startswith("|") and set(s) != {"-"}:
            summary = strip_emoji(s.strip("*"))
            break

    # 版本/时间戳：从文件名提取
    m = re.search(r"_v([\d.]+)_(\d{8}_\d{6})", md_path)
    meta_spans = []
    if m:
        meta_spans.append(f"<span>版本 v{m.group(1)}</span>")
        ts = m.group(2)
        meta_spans.append(f"<span>{ts[:4]}-{ts[4:6]}-{ts[6:8]}</span>")
    meta_spans.append(f"<span>{tag}</span>" if tag else "")

    toc, sections, sec_html = [], [], []
    cur = None  # (id, h2, buf)
    i = start

    def flush():
        nonlocal cur
        if cur:
            sections.append((cur[0], cur[1], "\n".join(cur[2])))
        cur = None

    while i < len(lines):
        ln = lines[i]
        s = ln.strip()

        if s.startswith("## "):
            flush()
            h2 = s[3:].strip()
            sid = f"s{len(sections) + 1}"
            toc.append(f'<li><a href="#{sid}">{inline(h2)}</a></li>')
            cur = (sid, h2, [])
            i += 1
            continue

        if cur is None:
            i += 1
            continue

        # 代码块
        if s.startswith("```"):
            lang = s[3:].strip()
            code, i2 = [], i + 1
            while i2 < len(lines) and not lines[i2].strip().startswith("```"):
                code.append(lines[i2])
                i2 += 1
            cur[2].append("<pre>" + H.escape("\n".join(code)) + "</pre>")
            i = i2 + 1
            continue

        # 表格
        if s.startswith("|"):
            tb, i = parse_table(lines, i)
            if tb:
                cur[2].append(tb)
            continue

        # 引用块 → box.info（多行合并）
        if s.startswith(">"):
            quote = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                quote.append(lines[i].strip().lstrip(">").strip())
                i += 1
            text = " ".join(q for q in quote if q)
            cur[2].append(f'<div class="box info"><span class="bt">说明</span><p>{inline(text)}</p></div>')
            continue

        # 列表
        lm = re.match(r"^(\s*)([-*]|\d+[.、])\s+", ln)
        if lm:
            ul, i = parse_list(lines, i)
            if ul:
                cur[2].append(ul)
            continue

        # 分隔线
        if set(s) == {"-"} and len(s) >= 3:
            i += 1
            continue

        # 标题层级 #### → 忽略编号语义，作为 h3
        if s.startswith("#### "):
            cur[2].append(f"<h3>{inline(s[5:])}</h3>")
            i += 1
            continue
        if s.startswith("### "):
            cur[2].append(f"<h3>{inline(s[4:])}</h3>")
            i += 1
            continue

        # 空行
        if not s:
            i += 1
            continue

        # 普通段落
        para = [s]
        i += 1
        while i < len(lines):
            nxt = lines[i].strip()
            if (not nxt or nxt.startswith(("#", "|", ">", "```", "- ", "* "))
                    or re.match(r"^\d+[.、]\s", nxt) or set(nxt) == {"-"}):
                break
            para.append(nxt)
            i += 1
        cur[2].append(f"<p>{inline(' '.join(para))}</p>")

    flush()

    toc_html = "\n".join(toc) if toc else ""
    secs_html = "\n".join(
        f'<section id="{sid}"><div class="sec">\n<h2><span class="num">{n}</span>{inline(h2)}</h2>\n{body}\n</div></section>'
        for n, (sid, h2, body) in enumerate(sections, 1)
    )
    meta_html = f'<div class="meta">{"".join(x for x in meta_spans if x)}</div>' if any(meta_spans) else ""

    doc = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{H.escape(title)}</title>
<link rel="stylesheet" href="{relcss}">
</head>
<body>
<div class="wrap">
  <div class="hero">
    <div class="tag">{H.escape(tag or "文档")}</div>
    <h1>{inline(title)}</h1>
    <p>{inline(summary)}</p>
    {meta_html}
  </div>
  {"" if not toc_html else f'<div class="toc"><h2>目录</h2><ol>{chr(10)}{toc_html}</ol></div>'}
  {secs_html}
</div>
</body>
</html>
"""
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(doc)
    return len(sections)


if __name__ == "__main__":
    md, out = sys.argv[1], sys.argv[2]
    tag = sys.argv[3] if len(sys.argv) > 3 else ""
    relcss = sys.argv[4] if len(sys.argv) > 4 else "common.css"
    n = convert(md, out, tag, relcss)
    print(f"[OK] {out} ({n} sections)")
