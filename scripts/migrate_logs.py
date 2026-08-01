#!/usr/bin/env python3
"""迁移 Obsidian 更新日志 → VitePress changelog 格式

从 D:\\QmClient_Update_Markdown 读取 X月更新日志/,输出到 docs/changelog/YYYY-MM-DD.md
并重新生成 docs/changelog/index.md 列表页。

格式归一化规则(对齐 6~7 月的最终文风):
  **==FIX==** / ## FEAT:  →  ### FIX: / ### FEAT:
  ==(官方更新)==           →  (官方更新)
  - **条目**               →  - 条目
  [[5月11日更新]]           →  → [5月11日更新](/changelog/2026-05-11)
  --- 分隔线               →  删除
"""
import re
import sys
from pathlib import Path

SRC = Path(r"D:\QmClient_Update_Markdown")
DST = Path(__file__).resolve().parent.parent / "docs" / "changelog"
YEAR = 2026
MONTHS = ["2月", "3月", "4月", "5月", "6月", "7月"]


def parse_date(filename: str):
    """'7月18日更新.md' → ('2026-07-18', '7月18日更新')"""
    m = re.match(r"(\d+)月(\d+)日更新\.md$", filename)
    if not m:
        return None
    return f"{YEAR}-{int(m.group(1)):02d}-{int(m.group(2)):02d}", filename[: -len(".md")]


def normalize(raw: str) -> str:
    # 1) 节标题统一为 ### XXX:
    raw = re.sub(r"\*\*==([A-Z]+)==\*\*", r"### \1:", raw)          # **==FIX==** → ### FIX:
    raw = re.sub(r"^==([A-Z]+)==$", r"### \1:", raw, flags=re.M)    # ==FEAT== → ### FEAT:
    raw = re.sub(r"^##\s+([A-Z]+):?", r"### \1:", raw, flags=re.M)  # ## FEAT / ## FEAT: → ### FEAT:
    # 2) Obsidian 高亮 ==(官方更新)== → (官方更新)
    raw = raw.replace("==(官方更新)==", "(官方更新)")
    # 3) 列表项去掉整条加粗
    raw = re.sub(r"^- \*\*(.+?)\*\*$", r"- \1", raw, flags=re.M)
    # 4) wiki 链接 → 站内链接
    def wiki_link(m):
        inner = m.group(1).strip()
        parsed = parse_date(inner + ".md")
        if not parsed:
            return m.group(0)  # 解析不了就保留原文
        date, title = parsed
        return f"→ [{title}](/changelog/{date})"
    raw = re.sub(r"\[\[([^\]|]+?)(?:\|[^\]]*)?\]\]", wiki_link, raw)
    # 4b) 去掉包裹转换后链接的残留加粗: **→ [..](..)** → → [..](..)
    raw = re.sub(r"\*\*(→ \[[^\]]+\]\([^)]+\))\*\*", r"\1", raw)
    # 5) 删除 --- 分隔线,行尾空格,压缩多余空行
    raw = re.sub(r"\n---\n", "\n\n", raw)
    raw = re.sub(r"[ \t]+$", "", raw, flags=re.M)  # 行尾空白
    raw = re.sub(r"\n{3,}", "\n\n", raw)
    return raw.strip() + "\n"


def gen_index(entries):
    by_month = {}
    for date, title in sorted(entries, reverse=True):
        by_month.setdefault(date[:7], []).append((date, title))
    lines = [
        "# 更新日志",
        "",
        "按日期记录的更新内容，点击查看当天改动。",
        "",
    ]
    for key in sorted(by_month, reverse=True):
        year, month = key.split("-")
        lines.append(f"## {year}年{int(month)}月")
        lines.append("")
        for date, title in by_month[key]:
            lines.append(f"- [{title}](/changelog/{date})")
        lines.append("")
    return "\n".join(lines)


def main():
    DST.mkdir(parents=True, exist_ok=True)
    entries = []
    for month in MONTHS:
        folder = SRC / f"{month}更新日志"
        if not folder.is_dir():
            print(f"[跳过] {folder} 不存在", file=sys.stderr)
            continue
        for f in sorted(folder.glob("*.md")):
            parsed = parse_date(f.name)
            if not parsed:
                continue
            date, title = parsed
            body = normalize(f.read_text(encoding="utf-8"))
            frontmatter = f"---\ntitle: {title}\ndate: {date}\n---\n\n"
            (DST / f"{date}.md").write_text(frontmatter + body, encoding="utf-8")
            entries.append((date, title))
            print(f"OK {date}  {title}")
    (DST / "index.md").write_text(gen_index(entries), encoding="utf-8")
    print(f"\n共迁移 {len(entries)} 篇 → {DST}")


if __name__ == "__main__":
    main()
