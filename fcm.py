#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""fcm — 本地 AI 生成规范 commit message

单文件、零第三方依赖(仅 Python 标准库),通过本地 Ollama 模型生成
符合 Conventional Commits 规范的提交信息。代码不出本机。

用法:
    python fcm.py                 # 为暂存区改动生成中文提交信息
    python fcm.py --lang en       # 英文提交信息
    python fcm.py --unstaged      # 使用未暂存改动
    python fcm.py --yes           # 自动选择第一条并直接提交
    python fcm.py install         # 安装 git hook(git commit 自动预填)
    python fcm.py uninstall       # 卸载 git hook
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request

VERSION = "0.2.0"
DEFAULT_MODEL = "qwen2.5:3b"
DEFAULT_URL = "http://localhost:11434"
MAX_DIFF_CHARS = 6000

LANG_NAMES = {"zh": "中文", "en": "English"}
TYPES = "feat fix docs style refactor perf test chore build ci"

FEW_SHOT = """\
示例(diff → 期望输出):
- 新增登录页面的"记住我"选项  →  feat(auth): add remember-me option on login page
- 修复并发下单时库存超卖     →  fix(order): prevent overselling under concurrent requests
- 把工具函数抽到独立模块     →  refactor(utils): extract helpers into standalone module
"""


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    """运行 git 命令并返回结果。"""
    return subprocess.run(["git", *args], capture_output=True, text=True, check=check)


def collect_diff(unstaged: bool) -> tuple[str, str]:
    """返回 (变更统计, diff 内容)。"""
    r = git("rev-parse", "--is-inside-work-tree", check=False)
    if r.returncode != 0:
        sys.exit("✗ 当前目录不是 git 仓库。")

    if unstaged:
        stat = git("diff", "--stat").stdout
        body = git("diff").stdout
    else:
        stat = git("diff", "--staged", "--stat").stdout
        body = git("diff", "--staged").stdout

    if not stat.strip() and not body.strip():
        hint = "请先 git add 文件,或使用 --unstaged 查看未暂存改动。"
        sys.exit(f"✗ 没有可用的改动。{hint}")
    return stat, body


def truncate(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + "\n…(diff 过长已截断,共 %d 字符)" % len(text)


def build_prompt(stat: str, body: str, lang: str, n: int) -> str:
    diff = truncate(stat + "\n" + body, MAX_DIFF_CHARS)
    return f"""\
你是一名资深软件工程师。根据下面的 git diff,生成 {n} 条符合 Conventional Commits 规范的 commit message。

要求:
- 格式:type(scope): subject,subject 用祈使句、小写开头,不超过 72 字符
- type 只能从以下选择:{TYPES}
- scope 可省略,尽量具体(如模块/组件名)
- 语言:写 {LANG_NAMES[lang]} 的 message
- 只输出 {n} 条候选,每条严格一行、严格符合 type(scope): subject 格式
- 禁止任何解释、翻译说明或箭头符号(→),直接输出 commit message 本身

{FEW_SHOT}

diff:
```
{diff}
```"""


def ollama_chat(model: str, prompt: str, url: str) -> str:
    """调用 Ollama /api/chat,返回模型回复文本。"""
    payload = json.dumps(
        {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "options": {"temperature": 0.7},
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        url + "/api/chat", data=payload, headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            sys.exit(f"✗ 模型 {model!r} 不存在,请先执行:ollama pull {model}")
        sys.exit(f"✗ Ollama 返回错误:HTTP {e.code} {e.reason}")
    except (urllib.error.URLError, ConnectionError, OSError):
        sys.exit(
            "✗ 无法连接 Ollama(默认 http://localhost:11434)。\n"
            "  安装:curl -fsSL https://ollama.com/install.sh | sh\n"
            "  拉取模型:ollama pull qwen2.5:3b\n"
            "  启动服务:ollama serve"
        )
    if data.get("error"):
        sys.exit(f"✗ Ollama 错误:{data['error']}")
    return data["message"]["content"].strip()


def _clean_line(line: str) -> str:
    line = line.strip()
    if not line:
        return ""
    if "→" in line:
        line = line.split("→", 1)[1].strip()  # 模型偶发"解释 → 真实 message",只保留箭头后内容
    line = re.sub(r"^\d+[.)、\s]*", "", line)  # 去掉 "1." "1)" 等序号
    line = re.sub(r"^[-*•]\s*", "", line)  # 去掉列表符号
    return line.strip()


def generate_candidates(model: str, prompt: str, url: str, n: int) -> list[str]:
    raw = ollama_chat(model, prompt, url)
    msgs = [m for m in (_clean_line(l) for l in raw.splitlines()) if m]
    if len(msgs) < n:
        # 候选不足时,再单独要一条补足
        extra = ollama_chat(model, "只输出 1 条 commit message,不要任何其他文字。", url)
        msgs += [m for m in (_clean_line(l) for l in extra.splitlines()) if m]
    msgs = list(dict.fromkeys(msgs))  # 去重,保持顺序
    if not msgs:
        sys.exit("✗ 模型没有返回有效 message,请重试。")
    return msgs[:n]


def edit_message(initial: str) -> str:
    editor = os.environ.get("EDITOR") or os.environ.get("VISUAL")
    if editor:
        with tempfile.NamedTemporaryFile("w+", suffix=".txt", delete=False) as f:
            f.write(initial + "\n")
            path = f.name
        try:
            subprocess.run([editor, path], check=False)
            with open(path, encoding="utf-8") as f:
                return f.read().strip() or initial
        finally:
            os.unlink(path)
    msg = input("编辑 message(整行覆盖): ").strip()
    return msg or initial


def pick(candidates: list[str], yes: bool) -> str | None:
    print("\n生成的候选 commit message:\n")
    for i, m in enumerate(candidates, 1):
        print(f"  [{i}] {m}")
    print("\n  [e] 手动编辑   [c] 自定义输入   [q] 退出不提交")
    if yes:
        return candidates[0]
    while True:
        choice = input("\n选择 (1-%d / e / c / q): " % len(candidates)).strip().lower()
        if choice in ("q", ""):
            return None
        if choice == "e":
            return edit_message(candidates[0])
        if choice == "c":
            msg = input("输入自定义 message: ").strip()
            return msg or None
        if choice.isdigit() and 1 <= int(choice) <= len(candidates):
            return candidates[int(choice) - 1]
        print("无效输入,请重试。")


def run_commit(msg: str, yes: bool) -> None:
    print(f'\n将执行:git commit -m "{msg}"')
    if not yes:
        if input("确认提交? [y/N]: ").strip().lower() != "y":
            print("已取消。")
            return
    r = git("commit", "-m", msg, check=False)
    print(r.stdout, end="")
    if r.returncode != 0:
        print(r.stderr, end="")
        sys.exit(f"✗ git commit 失败(exit {r.returncode})")


# ---------------------------------------------------------------- git hook ----

def hooks_dir(global_: bool) -> str:
    """返回 hooks 目录;全局模式下设置 core.hooksPath。"""
    if global_:
        cur = git("config", "--global", "--get", "core.hooksPath", check=False).stdout.strip()
        if cur:
            path = os.path.expanduser(cur)
        else:
            path = os.path.expanduser("~/.config/git/fcm-hooks")
            try:
                git("config", "--global", "core.hooksPath", path)
            except subprocess.CalledProcessError:
                sys.exit("✗ 无法写入全局 git 配置,请检查 HOME 目录是否可写。")
        os.makedirs(path, exist_ok=True)
        return path
    r = git("rev-parse", "--git-path", "hooks", check=False)
    if r.returncode != 0:
        sys.exit("✗ 当前目录不是 git 仓库。")
    return r.stdout.strip()


def hook_invoke_cmd() -> str:
    """hook 内调用 fcm 的命令(shlex 引号,路径含空格也安全)。"""
    return f"{shlex.quote(sys.executable)} {shlex.quote(os.path.abspath(__file__))}"


def write_hook(hook_path: str) -> None:
    script = f'''#!/bin/sh
# Generated by fcm {VERSION} — 运行 `fcm uninstall` 卸载
MSG_FILE="$1"
SOURCE="$2"

# 临时禁用:FCM_DISABLE=1 git commit
[ -n "$FCM_DISABLE" ] && exit 0
# merge / cherry-pick / amend 等场景不干预
[ -n "$SOURCE" ] && exit 0
# 已有真实提交内容(-m / 模板 / 合并信息等)不覆盖;
# 注意:git 默认注释块也是内容,所以只认非 #、非空行
[ -n "$(sed '/^#/d;/^$/d' "$MSG_FILE")" ] && exit 0
# 没有暂存改动时不打扰
git diff --cached --quiet && exit 0

{hook_invoke_cmd()} hook --out "$MSG_FILE" >/dev/null 2>&1
exit 0
'''
    os.makedirs(os.path.dirname(hook_path) or ".", exist_ok=True)
    with open(hook_path, "w", encoding="utf-8") as f:
        f.write(script)
    os.chmod(hook_path, 0o755)


def _is_fcm_hook(path: str) -> bool:
    """只删除我们生成的 hook,避免误删用户自己的脚本。"""
    try:
        with open(path, encoding="utf-8") as f:
            return "Generated by fcm" in f.read(200)
    except OSError:
        return False


def cmd_install(args) -> int:
    path = hooks_dir(args.global_)
    hook_path = os.path.join(path, "prepare-commit-msg")
    write_hook(hook_path)
    print(f"✓ 已安装 hook:{hook_path}")
    print("  现在直接 git commit 即可,AI 会自动预填提交信息。")
    print("  临时跳过:FCM_DISABLE=1 git commit 或 git commit --no-verify")
    if args.global_:
        print("  ⚠ 注意:core.hooksPath 会覆盖所有仓库的本地 hooks,")
        print("    如其他仓库有自己的 hook,需把它们合并到该目录。")
    return 0


def cmd_uninstall(args) -> int:
    if args.global_:
        cur = git("config", "--global", "--get", "core.hooksPath", check=False).stdout.strip()
        hook_path = os.path.join(os.path.expanduser(cur or ""), "prepare-commit-msg")
        if os.path.isfile(hook_path) and _is_fcm_hook(hook_path):
            os.remove(hook_path)
            print(f"✓ 已删除:{hook_path}")
        if cur:
            git("config", "--global", "--unset", "core.hooksPath")
            print("✓ 已移除 core.hooksPath 配置")
        return 0
    r = git("rev-parse", "--git-path", "hooks", check=False)
    if r.returncode != 0:
        sys.exit("✗ 当前目录不是 git 仓库。")
    hook_path = os.path.join(r.stdout.strip(), "prepare-commit-msg")
    if not (os.path.isfile(hook_path) and _is_fcm_hook(hook_path)):
        print("当前仓库未安装 fcm hook(或已被修改,为安全起见未删除)。")
        return 0
    os.remove(hook_path)
    print(f"✓ 已卸载:{hook_path}")
    return 0


def cmd_hook(args) -> int:
    """hook 调用的非交互模式:预填 1 条 message 到指定文件。"""
    # 没有暂存改动 → 静默退出
    if git("diff", "--cached", "--quiet", check=False).returncode == 0:
        return 0
    try:
        stat, body = collect_diff(unstaged=False)
        prompt = build_prompt(stat, body, args.lang, 1)
        candidates = generate_candidates(args.model, prompt, args.url, 1)
        msg = candidates[0]
    except SystemExit:
        return 1  # 生成失败不阻塞提交(hook 脚本会忽略退出码)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(msg + "\n")
        f.write("# 由 fcm 自动生成,可直接保存或修改后保存\n")
        f.write("# 请勿在 # 开头行上写内容(它们不会进入提交信息)\n")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="fcm",
        description="本地 AI 生成规范 commit message(代码不出本机)",
        epilog="示例:fcm --lang zh   # 用 qwen2.5:3b 为暂存区改动生成中文提交信息",
    )
    p.add_argument("--lang", choices=sorted(LANG_NAMES), default="zh",
                   help="commit message 语言(默认 zh)")
    p.add_argument("--model", default=DEFAULT_MODEL,
                   help=f"Ollama 模型(默认 {DEFAULT_MODEL})")
    p.add_argument("--url", default=DEFAULT_URL,
                   help=f"Ollama 服务地址(默认 {DEFAULT_URL})")
    p.add_argument("--unstaged", action="store_true",
                   help="使用未暂存改动(git diff)而非 --staged")
    p.add_argument("--yes", "-y", action="store_true",
                   help="自动选择第一条并直接提交,跳过所有交互")
    p.add_argument("--no-commit", action="store_true",
                   help="只生成并打印 message,不执行 git commit")
    p.add_argument("--candidates", type=int, default=3,
                   help="生成候选数量(默认 3)")
    p.add_argument("--version", action="version", version=f"fcm {VERSION}")
    sub = p.add_subparsers(dest="cmd", metavar="子命令")
    p_install = sub.add_parser("install", help="安装 prepare-commit-msg hook")
    p_install.add_argument("--global", dest="global_", action="store_true",
                           help="全局安装(经 core.hooksPath,会覆盖仓库本地 hooks)")
    p_uninstall = sub.add_parser("uninstall", help="卸载 prepare-commit-msg hook")
    p_uninstall.add_argument("--global", dest="global_", action="store_true",
                             help="卸载全局 hook 并移除 core.hooksPath")
    p_hook = sub.add_parser("hook", help="(内部)供 hook 调用的非交互模式")
    p_hook.add_argument("--out", required=True, metavar="FILE",
                        help="写入 commit message 的文件")
    p_hook.add_argument("--lang", choices=sorted(LANG_NAMES), default="zh",
                        help="commit message 语言(默认 zh)")
    p_hook.add_argument("--model", default=DEFAULT_MODEL,
                        help=f"Ollama 模型(默认 {DEFAULT_MODEL})")
    p_hook.add_argument("--url", default=DEFAULT_URL,
                        help=f"Ollama 服务地址(默认 {DEFAULT_URL})")
    args = p.parse_args(argv)

    if args.cmd == "install":
        return cmd_install(args)
    if args.cmd == "uninstall":
        return cmd_uninstall(args)
    if args.cmd == "hook":
        return cmd_hook(args)

    stat, body = collect_diff(args.unstaged)
    prompt = build_prompt(stat, body, args.lang, args.candidates)
    candidates = generate_candidates(args.model, prompt, args.url, args.candidates)

    if args.no_commit:
        for i, m in enumerate(candidates, 1):
            print(f"[{i}] {m}")
        return 0

    msg = pick(candidates, args.yes)
    if msg is None:
        print("已退出,未提交。")
        return 0
    run_commit(msg, yes=args.yes)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n已取消。")
        sys.exit(130)
