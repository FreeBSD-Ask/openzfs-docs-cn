#!/usr/bin/env python3
"""校验 **加粗** 定界符两侧的空格（GitBook 渲染兼容）。

规则：
* 开定界符 ** 前必须恰好一个半角空格；行首（段落开头，含引用块、列表、标题标记之后）例外。
* 闭定界符 ** 后必须恰好一个半角空格；行尾（加粗之后无内容）例外。
* 链接文本边界（紧贴 [ 或 ]）例外，避免把空格写进链接文字。
* 与斜体定界符组成 *** 的混合强调不检查前置空格。
* 围栏代码块、行内代码、链接目标与引用定义不参与检查。

用法：
  python .github/scripts/bold_spacing.py          # 检查
  python .github/scripts/bold_spacing.py --fix    # 自动修复
"""

import argparse
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EXCLUDE_DIRS = {".github", ".gitbook", "node_modules", ".git", ".workbuddy", "script"}
SKIP_FILES = {"mu-lu.md"}

FENCE_RE = re.compile(r"^\s*(```|~~~)")
INLINE_CODE_RE = re.compile(r"(`+)(?:[^`]|\n)*?\1")
LINK_DEST_RE = re.compile(r"\]\([^)\n]*\)")
REF_DEF_RE = re.compile(r"^\s*\[[^\]]+\]:\s*\S+.*$")
BOLD_RE = re.compile(r"\*\*")


def masked_spans(line):
    """返回不参与检查的区间（行内代码、链接目标）。"""
    spans = [(m.start(), m.end()) for m in INLINE_CODE_RE.finditer(line)]
    spans.extend((m.start(), m.end()) for m in LINK_DEST_RE.finditer(line))
    return spans


def inside(pos, spans):
    return any(start <= pos < end for start, end in spans)


def bold_pairs(line, spans):
    """返回行内成对的加粗定界符位置；不配对时返回 None。"""
    tokens = [m.start() for m in BOLD_RE.finditer(line) if not inside(m.start(), spans)]
    if len(tokens) % 2:
        return tokens, None
    return tokens, [(tokens[i], tokens[i + 1] + 2) for i in range(0, len(tokens), 2)]


def before_issue(line, start):
    """判断开定界符前空格；返回 None 表示合规。"""
    if line[:start].strip() == "":
        return None
    if start > 0 and line[start - 1] == "[":
        return None
    if start > 0 and line[start - 1] == "*":
        return None
    if start == 0 or line[start - 1] != " ":
        return "missing"
    if start >= 2 and line[start - 2] == " ":
        return "multi"
    return None


def after_issue(line, end):
    """判断闭定界符后空格；返回 None 表示合规。"""
    if line[end:].strip() == "":
        return None
    if end < len(line) and line[end] == "]":
        return None
    if end >= len(line) or line[end] != " ":
        return "missing"
    if end + 1 < len(line) and line[end + 1] == " ":
        return "multi"
    return None


def scan_line(line):
    """返回 [(位置, 侧, 类型)]，位置从 0 开始。"""
    spans = masked_spans(line)
    tokens, pairs = bold_pairs(line, spans)
    issues = []
    if pairs is None:
        if tokens:
            issues.append((tokens[0], "开定界符", "unpaired"))
        return issues
    for start, end in pairs:
        kind = before_issue(line, start)
        if kind:
            issues.append((start, "开定界符", kind))
        kind = after_issue(line, end)
        if kind:
            issues.append((end, "闭定界符", kind))
    return issues


def fix_line(line):
    """修复一行中的空格问题，返回 (新行, 修复处数)。"""
    spans = masked_spans(line)
    tokens, pairs = bold_pairs(line, spans)
    if not pairs:
        return line, 0
    edits = []
    for start, end in pairs:
        if line[:start].strip() != "" and not (start > 0 and line[start - 1] in "[*"):
            if start == 0 or line[start - 1] != " ":
                edits.append((start, start, " "))
            elif start >= 2 and line[start - 2] == " ":
                left = start
                while left > 0 and line[left - 1] == " ":
                    left -= 1
                edits.append((left, start, " "))
        if line[end:].strip() != "" and not (end < len(line) and line[end] == "]"):
            if end >= len(line) or line[end] != " ":
                edits.append((end, end, " "))
            elif end + 1 < len(line) and line[end + 1] == " ":
                right = end
                while right < len(line) and line[right] == " ":
                    right += 1
                edits.append((end, right, " "))

    seen = set()
    unique = []
    for left, right, repl in edits:
        if (left, right) not in seen:
            seen.add((left, right))
            unique.append((left, right, repl))
    if not unique:
        return line, 0
    new = line
    for left, right, repl in sorted(unique, key=lambda item: (item[0], item[1]), reverse=True):
        new = new[:left] + repl + new[right:]
    return new, len(unique)


def iter_markdown():
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        for filename in sorted(filenames):
            if not filename.endswith(".md"):
                continue
            path = os.path.join(dirpath, filename)
            rel = os.path.relpath(path, ROOT).replace("\\", "/")
            if rel in SKIP_FILES:
                continue
            yield path, rel


def main():
    parser = argparse.ArgumentParser(description="校验 **加粗** 定界符两侧的空格")
    parser.add_argument("--fix", action="store_true", help="自动修复")
    args = parser.parse_args()

    total_issues = 0
    changed_files = 0
    changed_lines = 0
    detail_rows = []

    for path, rel in iter_markdown():
        with open(path, "r", encoding="utf-8", newline="") as handle:
            text = handle.read()
        lines = text.splitlines(keepends=True)
        in_fence = False
        new_lines = []
        file_changed = False
        for lineno, raw in enumerate(lines, 1):
            body = raw.rstrip("\r\n")
            ending = raw[len(body):]
            if FENCE_RE.match(body):
                in_fence = not in_fence
                new_lines.append(raw)
                continue
            if in_fence or REF_DEF_RE.match(body):
                new_lines.append(raw)
                continue
            issues = scan_line(body)
            for pos, side, kind in issues:
                total_issues += 1
                detail_rows.append((rel, lineno, pos + 1, side, kind, body.strip()))
            if args.fix and issues:
                fixed, count = fix_line(body)
                if count:
                    file_changed = True
                    changed_lines += 1
                    new_lines.append(fixed + ending)
                    continue
            new_lines.append(raw)
        if file_changed:
            changed_files += 1
            with open(path, "w", encoding="utf-8", newline="") as handle:
                handle.write("".join(new_lines))

    if args.fix:
        print(f"修复完成：{changed_files} 个文件、{changed_lines} 行、{total_issues} 处。")
        return 0

    if detail_rows:
        print(f"加粗空格检查：{len(detail_rows)} 处违规，涉及 {len({row[0] for row in detail_rows})} 个文件。\n")
        labels = {"missing": "缺少空格", "multi": "多余空格", "unpaired": "未配对"}
        for rel, lineno, col, side, kind, snippet in detail_rows:
            print(f"  {rel}:{lineno}:{col}  {side}{labels[kind]}  | {snippet[:120]}")
        return 1

    print("加粗空格检查：0 处违规。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
