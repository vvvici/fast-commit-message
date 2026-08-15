# ⚡ fast-commit-message (fcm)

> 在终端里,用**本地 LLM** 根据 `git diff` 自动生成规范的中文/英文 commit message。
> **纯本地、单文件、零第三方依赖**——你的代码永远不出本机。

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/vvvici/fast-commit-message?style=social)](https://github.com/vvvici/fast-commit-message)

<!-- TODO: 录制 30 秒 demo GIF 后取消注释
![demo](docs/demo.gif)
-->

---

## ✨ 特性

- 🏠 **纯本地**:走 Ollama,代码 diff 不会上传到任何云端,无需 API key、无需科学上网
- 🇨🇳 **中文优先**:原生生成规范的中文 commit message(很多公司要求中文提交)
- 📦 **单文件零依赖**:只用一个 `.py` 文件 + Python 标准库,下载即用
- 🎯 **符合 Conventional Commits**:`feat/fix/docs/refactor/...` 自动匹配改动类型
- 🖥 **交互式**:3 条候选任选,可手动编辑/自定义,确认后一键提交
- 🪝 **可无人值守**:`--yes` 全自动选第一条并提交,适合 git hook

## 🚀 安装

### 方式一:单文件(推荐,零依赖)

```bash
curl -O https://raw.githubusercontent.com/vvvici/fast-commit-message/main/fcm.py
chmod +x fcm.py
sudo mv fcm.py /usr/local/bin/fcm   # 可选:装到 PATH
```

### 方式二:pip 安装

```bash
pip install git+https://github.com/vvvici/fast-commit-message.git
```

### 准备本地模型(一次性)

```bash
# 安装 Ollama
curl -fsSL https://ollama.com/install.sh | sh
# 拉取推荐模型(默认 3b:快;想要更高质量用 7b)
ollama pull qwen2.5:3b
```

## 💡 快速开始

```bash
git add .
fcm                    # 为暂存区改动生成中文提交信息(交互式)
fcm --lang en          # 英文提交信息
fcm --unstaged         # 使用未暂存改动
fcm --yes              # 自动选第一条并直接提交(适合 hook)
fcm --no-commit        # 只生成不提交(先看看效果)
fcm --model qwen2.5:7b # 换更大的模型(质量更高但更慢)
```

效果:

```text
$ fcm

生成的候选 commit message:

  [1] feat(auth): add remember-me option on login page
  [2] feat(auth): persist login session with remember-me
  [3] feat(auth): support remembering user login state

  [e] 手动编辑   [c] 自定义输入   [q] 退出不提交

选择 (1-3 / e / c / q): 1

将执行:git commit -m "feat(auth): add remember-me option on login page"
确认提交? [y/N]: y
[main abc1234] feat(auth): add remember-me option on login page
```

## 🔧 参数一览

| 参数 | 说明 | 默认 |
|---|---|---|
| `--lang` | `zh` / `en` | `zh` |
| `--model` | Ollama 模型名 | `qwen2.5:3b` |
| `--url` | Ollama 服务地址 | `http://localhost:11434` |
| `--unstaged` | 使用未暂存改动而非 `--staged` | 关 |
| `--yes` / `-y` | 自动选第一条并直接提交 | 关 |
| `--no-commit` | 只打印 message 不提交 | 关 |
| `--candidates` | 候选数量 | `3` |
| `--version` | 显示版本 | — |

## ⚔️ 与 aicommits 的对比

| | **fcm(本项目)** | aicommits |
|---|---|---|
| 模型位置 | 🏠 本地 Ollama | ☁️ OpenAI 云端 |
| 需要 API key / 付费 | ❌ 免费 | ✅ 需要 |
| 代码上传云端 | ❌ 不出本机 | ⚠️ diff 会发送到 OpenAI |
| 中文 commit | ✅ 原生支持 | ❌ 需自行配置 |
| 依赖 | 单文件零依赖 | npm 包 |
| 需要科学上网 | ❌ | ⚠️ 视地区 |

## 🗺 路线图

- [x] v0.1:基础生成 + 交互选择 + 一键提交
- [ ] v0.2:git hook 一键安装(`prepare-commit-msg` 自动建议)
- [ ] v0.3:OpenAI 兼容端点(DeepSeek / OpenRouter 等)
- [ ] v0.4:mojicode 表情 + 多模型对比

## ❓ FAQ

**Q:没有 Ollama 会怎样?**
A:会给出清晰的安装指引(一键安装 + 拉模型 + 启动服务)。

**Q:diff 太大怎么办?**
A:自动截断(默认 6000 字符),同时保留 `--stat` 变更统计作为上下文。

**Q:支持 Windows 吗?**
A:纯标准库实现,Windows 下可直接 `python fcm.py` 运行。

## 📄 License

[MIT](LICENSE) © 2025 [vvvici](https://github.com/vvvici)
