#!/usr/bin/env python3
"""润色更新日志:调用 deepseek-v4-flash 按 QmClient 文风润色 Markdown 草稿。

用法:
  python scripts/polish.py --file docs/changelog/2026-08-01.md   # 润色单篇(原地覆盖)
  python scripts/polish.py --test                                # API 连通性自检

环境变量:
  ANTHROPIC_AUTH_TOKEN  必填: DeepSeek API Key
  QM_POLISH_MODEL       可选: 润色用模型,默认 deepseek-v4-flash
  ANTHROPIC_BASE_URL    可选: 默认 https://api.deepseek.com/anthropic
"""
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

API_URL = os.environ.get("ANTHROPIC_BASE_URL", "https://api.deepseek.com/anthropic").rstrip("/") + "/v1/messages"
# 润色固定走 flash(便宜快);不用 ANTHROPIC_MODEL,避免被客户端主模型设置带偏
MODEL = os.environ.get("QM_POLISH_MODEL", "deepseek-v4-flash")

STYLE_RULES = """你是 QmClient(栖梦,基于 DDNet 的中文定制客户端)的更新日志编辑。把开发者提供的草稿润色成正式发布的更新日志,严格遵循以下文风:
1. 结构: 用 `### FEAT:`、`### FIX:`、`### DEL:` 分节(历史也用 `### CI:`、`### DOCS:`、`### PERF:`,按需使用,不需要的节不要出现),每节下用 `- ` 列表
2. 每条目一句话为主,简短、技术性、直接;不写营销话术、不用感叹词
3. 条目以动词开头: 加载/新增/修复/优化/移除/调整/完善/更新
4. 保留专业术语原文(DDNet、Tee、KCP、AMLL、LRCLIB、Axiom、SMTC、FFmpeg 等)、代码标识(反引号)和版本号
5. 只润色草稿已有的内容,不添加草稿中没有的事实,不编造;同类型的条目可以合并
6. 每条目按重要性排序
7. 草稿中有版本号更新时,保留类似 "更新客户端版本号到 `2.75.14`" 的条目
8. 使用中文标点
9. 只输出润色后的正文(以 ### 开头),不要任何解释、不要 markdown 代码块围栏、不要"下一篇"链接行"""


def read_draft(path: Path) -> tuple[str, str]:
    """读取草稿,拆成 (frontmatter, 正文)"""
    raw = path.read_text(encoding="utf-8")
    if raw.startswith("---"):
        parts = raw.split("---", 2)
        if len(parts) >= 3:
            return f"---{parts[1]}---\n\n", parts[2]
    return "", raw


def latest_exemplars(exclude: Path, count: int = 2) -> list[str]:
    """取已发布的最新几篇日志作为文风范例(排除正在润色的那篇)"""
    changelog = exclude.parent
    files = sorted(
        (f for f in changelog.glob("*.md") if f.name != "index.md" and f != exclude),
        key=lambda f: f.name,
        reverse=True,
    )
    result = []
    for f in files[:count]:
        _, body = read_draft(f)
        # 范例里去掉"下一篇"链接行
        body = re.sub(r"^→ \[[^\]]+\]\([^)]+\)\s*$", "", body, flags=re.M).strip()
        result.append(f"{f.stem}:\n{body}")
    return result


def call_api(system: str, user: str, max_tokens: int = 4000) -> str:
    token = os.environ.get("ANTHROPIC_AUTH_TOKEN")
    if not token:
        sys.exit("错误: 未设置 ANTHROPIC_AUTH_TOKEN 环境变量(在 PowerShell 运行: [Environment]::SetEnvironmentVariable('ANTHROPIC_AUTH_TOKEN','<你的Key>','User'))")
    payload = json.dumps({
        "model": MODEL,
        "max_tokens": max_tokens,
        "system": system,
        "messages": [{"role": "user", "content": user}],
    }).encode("utf-8")
    req = urllib.request.Request(
        API_URL,
        data=payload,
        headers={
            "x-api-key": token,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")[:500]
        sys.exit(f"错误: API 请求失败 HTTP {e.code}\n{detail}")
    except Exception as e:
        sys.exit(f"错误: 网络请求失败 {e}")

    text = "".join(
        block.get("text", "")
        for block in data.get("content", [])
        if block.get("type") == "text"
    ).strip()
    if not text:
        sys.exit(f"错误: API 返回内容为空 {json.dumps(data, ensure_ascii=False)[:500]}")
    return text


def polish(draft: Path) -> None:
    fm, body = read_draft(draft)
    exemplars = latest_exemplars(draft)
    user = ""
    if exemplars:
        user += "以下是最近已发布的更新日志,请参考其文风:\n\n"
        user += "\n\n".join(f"--- {ex} ---" for ex in exemplars)
        user += "\n\n"
    user += "请润色下面这篇草稿:\n\n--- 草稿 ---\n" + body.strip() + "\n--- 草稿结束 ---"
    print(f"  调用 {MODEL} 润色中...", file=sys.stderr)
    polished = call_api(STYLE_RULES, user)
    draft.write_text(fm + polished + "\n", encoding="utf-8")
    print(f"  ✅ 已润色 {draft.relative_to(draft.parent.parent.parent)}", file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser(description="QmClient 更新日志润色")
    parser.add_argument("--file", help="要润色的 Markdown 文件路径")
    parser.add_argument("--test", action="store_true", help="API 连通性自检")
    args = parser.parse_args()

    if args.test:
        reply = call_api("回复两个字:正常", "ping")
        print(f"✅ API 正常,模型 {MODEL} 回复: {reply}")
        return
    if not args.file:
        parser.error("需要 --file 或 --test")

    draft = Path(args.file)
    if not draft.is_file():
        sys.exit(f"错误: 文件不存在 {draft}")
    polish(draft)


if __name__ == "__main__":
    main()
