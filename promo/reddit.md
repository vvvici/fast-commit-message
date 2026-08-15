# [Reddit 首发帖]

## Title candidates

1. Show HN: fcm — local AI commit messages via Ollama, zero-dependency single-file CLI, your diff never leaves your machine
2. I built a zero-dependency CLI that writes conventional commit messages with a local LLM (no cloud, no API key)
3. fcm: your git diff never leaves your machine — local LLM commit messages with git hook integration

## Post body

I got tired of writing commit messages, and I didn't love sending my diff to OpenAI every time I commit. So I built **fcm** — a single-file, zero-dependency Python CLI that generates conventional commit messages using a **local** LLM (Ollama).

**Why it's different:**

- 🏠 **100% local** — your diff never leaves your machine. No API keys, no cloud, no cost, works offline
- 🇨🇳 **Native Chinese support** — the default output is in Chinese (great for teams that require Chinese commits); `--lang en` for English
- 📦 **Single file, zero dependencies** — just `fcm.py` + Python stdlib (uses `urllib` against Ollama's HTTP API). Curl it and go
- 🪝 **Git hook integration** — `fcm install` sets up a `prepare-commit-msg` hook. Next time you run `git commit`, your editor opens pre-filled with the AI message. Edit it, or delete it and write your own — **AI is a draft, you keep final control**
- ⏱ `--yes` for fully unattended use (CI-friendly)
- 🎯 Auto-corrects the type (`doc` → `docs`) via fuzzy matching

**Usage:**
```bash
curl -O https://raw.githubusercontent.com/vvvici/fast-commit-message/main/fcm.py
ollama pull qwen2.5:3b
git add .
python3 fcm.py          # pick from 3 candidates, or edit
python3 fcm.py install  # auto-prefill on every git commit
```

**Real output (qwen2.5:3b, Chinese):**
```
[1] feat(calc): 添加减法函数
[2] fix(calc): 确保 add 和 sub 函数正确实现
[3] refactor(calc): 提升代码可读性,添加文档注释
```

The hook is deliberately conservative: it skips `-m` messages, merges, cherry-picks, amends, empty staging areas, and it **never blocks a commit** — if the model is down, it fails silently.

Repo (with a demo GIF in the README): https://github.com/vvvici/fast-commit-message

Still early (v0.3), happy to take feedback. Planned: OpenAI-compatible endpoints (DeepSeek, OpenRouter), mojicode, multi-model comparison.

---

## Posting notes

- **Subreddits**: r/Python (primary), r/selfhosted, r/commandline, r/git
- **Timing**: Mon–Thu, 14:00–17:00 UTC (US morning / EU afternoon overlap)
- **r/Python rules**: r/Python forbids self-promo in some formats — check the sidebar; "Show HN" style titles work best, or post as a link post with a short description
- **Expect skepticism**: be ready for "yet another AI commit tool" — lead with the privacy/offline/local angle and the hook UX, which aicommits doesn't have
- Reply to every comment in the first hour; that's what pushes the post up
