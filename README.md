# QmClient 官网 (QmClient.icu)

栖梦 QmClient 的官方站点:更新日志 · 教程 · 功能介绍。基于 VitePress + GitHub Pages 自动部署。

## 日常发布流程

1. 写更新日志草稿:`docs/changelog/2026-08-01.md`(标题 `X月X日更新`,正文 `### FEAT:` / `### FIX:` 分节)
2. `git add` + `git commit`
3. `git push` → **pre-push 钩子自动调用 deepseek-v4-flash 润色** → 生成润色提交 → 推送
4. GitHub Actions 自动构建部署,几分钟后访问 <https://qmclient.github.io/> 生效

跳过润色(比如 API 挂了):`git push --no-verify`

## 本地预览

```bash
npm install
npm run docs:dev    # http://localhost:5173
```

## 脚本

| 脚本 | 用途 |
|------|------|
| `scripts/polish.py` | 调用 DeepSeek API 按本站文风润色更新日志(单篇: `--file <路径>`;自检: `--test`) |
| `scripts/pre-push` | pre-push 钩子本体,自动润色未推送的 changelog |
| `scripts/install-hooks.py` | 安装钩子到 `.git/hooks/`(换电脑/重克隆后跑一次) |
| `scripts/migrate_logs.py` | 从 Obsidian 更新日志仓库迁移历史文章(一次性) |

## 环境变量

- `ANTHROPIC_AUTH_TOKEN`:DeepSeek API Key(必填,润色用)
- `QM_POLISH_MODEL`:润色模型,默认 `deepseek-v4-flash`

## 站点结构

```
docs/
├── index.md              # 首页
├── intro.md              # 关于栖梦
├── changelog/            # 更新日志(YYYY-MM-DD.md + index.md 列表)
└── guide/                # 使用教程 / 功能介绍 / Q&A
```
