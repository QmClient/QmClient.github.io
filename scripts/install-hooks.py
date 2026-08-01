#!/usr/bin/env python3
"""安装 pre-push 钩子到 .git/hooks/

用法: python scripts/install-hooks.py
"""
import stat
import sys
from pathlib import Path

repo = Path(__file__).resolve().parent.parent
src = repo / "scripts" / "pre-push"
dst = repo / ".git" / "hooks" / "pre-push"

if not src.is_file():
    sys.exit(f"错误: 找不到 {src}")

dst.write_bytes(src.read_bytes())
dst.chmod(dst.stat().st_mode | stat.S_IEXEC)
print(f"✅ 已安装 pre-push 钩子: {dst}")
print("   以后 push 时自动润色更新日志; 想跳过用: git push --no-verify")
