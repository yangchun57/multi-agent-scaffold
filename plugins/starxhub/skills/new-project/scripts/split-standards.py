#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
规范文档拆分器：把大规范按二级标题拆成主题文件，生成 topics/ 目录 + INDEX.md。

用法：
    python split-standards.py <standards目录>

效果：
    <standards>/
    ├── 后端开发规范.md            ← 原文件保留（全量参考，很少整读）
    ├── 前端开发规范.md
    ├── ...
    └── topics/                    ← 按主题拆分的碎片（Agent 日常按需读取）
        ├── INDEX.md               ← 主题索引（先读这个定位）
        ├── 后端开发规范/
        │   ├── 01-技术栈概述.md
        │   ├── 02-项目结构规范.md
        │   └── ...
        └── 前端开发规范/...

规则：
- 按行首 "## " 切分；"## 目录" 章节跳过（链接列表无内容价值）
- 无二级标题的文档不拆，INDEX 中标注"整读或 Grep"
- 重复运行安全（覆盖旧 topics/）
"""

import os
import re
import shutil
import sys


def sanitize(name):
    """文件名安全化：去掉 Windows 不允许的字符"""
    name = re.sub(r'[\\/:*?"<>|·]', "", name)
    name = name.strip().replace(" ", "-")
    return name[:60] or "untitled"


def split_doc(path, out_dir):
    """把单个规范拆成主题文件，返回 [(文件名, 标题), ...]"""
    with open(path, encoding="utf-8") as f:
        lines = f.readlines()

    stem = os.path.splitext(os.path.basename(path))[0]
    doc_dir = os.path.join(out_dir, sanitize(stem))
    os.makedirs(doc_dir, exist_ok=True)

    # 按 "## " 切分（保留一级标题作文件头）
    sections = []  # (title, [lines])
    preamble = []
    cur_title, cur_lines = None, []
    for line in lines:
        m = re.match(r"^## (.+)\n", line)
        if m:
            if cur_title is not None and cur_title != "目录":
                sections.append((cur_title, cur_lines))
            cur_title, cur_lines = m.group(1).strip(), []
        elif cur_title is None:
            preamble.append(line)
        else:
            cur_lines.append(line)
    if cur_title is not None and cur_title != "目录":
        sections.append((cur_title, cur_lines))

    # 跳过"目录"章节后，目录内容会挂在下一个标题前——重新扫描更稳妥：
    # 上面的逻辑已把"目录"章节的行丢弃（cur_title=='目录' 时不收集? 不，收集了但没 append）
    # 修正：目录章节的行被丢弃
    if not sections:
        return []

    results = []
    for i, (title, sec_lines) in enumerate(sections, 1):
        fname = f"{i:02d}-{sanitize(title)}.md"
        with open(os.path.join(doc_dir, fname), "w", encoding="utf-8") as f:
            f.write(f"# {stem} · {title}\n\n")
            f.write(f"> 拆分自《{stem}》第 {i} 节。需要全量上下文时读原文件。\n\n")
            if i == 1 and preamble:
                f.writelines(preamble)
            f.writelines(sec_lines)
        results.append((fname, title))
    return results


def main():
    std_dir = sys.argv[1] if len(sys.argv) > 1 else ".claude/standards"
    std_dir = os.path.abspath(std_dir)
    if not os.path.isdir(std_dir):
        print(f"[FAIL] 目录不存在: {std_dir}")
        sys.exit(1)

    out_dir = os.path.join(std_dir, "topics")
    if os.path.isdir(out_dir):
        shutil.rmtree(out_dir)
    os.makedirs(out_dir, exist_ok=True)

    index_lines = [
        "# 规范主题索引",
        "",
        "> Agent 优先读本索引定位主题，再读对应主题文件；不要无目的整读大规范。",
        "",
    ]

    for fname in sorted(os.listdir(std_dir)):
        if not fname.endswith(".md") or fname == "README.md":
            continue
        path = os.path.join(std_dir, fname)
        stem = os.path.splitext(fname)[0]
        sections = split_doc(path, out_dir)
        if sections:
            index_lines.append(f"## {stem}")
            index_lines.append("")
            for sf, title in sections:
                index_lines.append(f"- {sanitize(stem)}/{sf} — {title}")
            index_lines.append("")
        else:
            index_lines.append(f"## {stem}（无二级标题，不拆分）")
            index_lines.append(f"- 直接读 `{fname}` 或用 Grep 定位")
            index_lines.append("")

    with open(os.path.join(out_dir, "INDEX.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(index_lines))

    n = sum(len(files) for _, _, files in os.walk(out_dir))
    print(f"[OK] 拆分完成: {out_dir}（含 INDEX 共 {n} 个文件）")


if __name__ == "__main__":
    main()
