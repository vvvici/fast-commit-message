# [V2EX 首发帖]

## 标题候选

1. 写了个零依赖的单文件 CLI:用本地 LLM 帮你写 commit message,代码不出本机
2. 又一个 AI 写 commit 的工具?这次是完全本地、还支持中文的
3. 周末做了个小工具:git commit 时自动预填 AI 提交信息,可以改,也可以不用

## 正文

大家好,分享一个周末写的小工具 **fcm**(fast-commit-message):用本地 LLM 根据 `git diff` 自动生成规范的 commit message。

**为什么做这个:**
- 公司要求中文 commit message,每次提交都要憋几分钟措辞
- 市面上的 aicommits 要把 diff 发到 OpenAI 云端,代码出去了总是不踏实,而且国内用还要科学上网
- 所以干脆做了一个纯本地的:走 Ollama,数据不出本机,免费,还能生成中文

**特性:**
- 🏠 纯本地:Ollama + qwen2.5,代码永远不出本机,不需要 API key
- 🇨🇳 原生中文 commit(英文也行,`--lang en`)
- 📦 单文件零依赖:一个 .py + Python 标准库,curl 下来就能跑
- 🎯 符合 Conventional Commits,还会自动修正 type 拼写(doc → docs)
- 🪝 `fcm install` 装 git hook 后,`git commit` 自动预填 AI 消息,编辑器里可以随便改,也可以直接删了写自己的——AI 只是草稿,你永远有最终决定权
- ⏱ `fcm --yes` 全自动,适合 CI

**安装:**
```bash
curl -O https://raw.githubusercontent.com/vvvici/fast-commit-message/main/fcm.py
ollama pull qwen2.5:3b   # 一次性
python3 fcm.py           # 用法:git add . 之后
```

**实际效果(真实模型输出):**
```
$ fcm

生成的候选 commit message:

  [1] feat(calc): 添加减法函数
  [2] fix(calc): 确保 add 和 sub 函数正确实现
  [3] refactor(calc): 提升代码可读性,添加文档注释

  [e] 手动编辑   [c] 自定义输入   [q] 退出不提交

选择 (1-3 / e / c / q): 1

将执行:git commit -m "feat(calc): 添加减法函数"
```

GitHub:https://github.com/vvvici/fast-commit-message
(README 里有完整 demo GIF)

**求 star、求 PR、求建议。** 接下来想做的:OpenAI 兼容端点(可以接 DeepSeek)、mojicode 表情、多模型对比。有任何想法欢迎提 issue。

---

## 发布建议

- 发在「分享创造」节点,标题突出"本地 + 中文 + 零依赖"三个卖点
- 发布时间:工作日上午 10–11 点或晚上 9–10 点(程序员活跃期)
- 发完后 1 小时内回复所有评论,前 20 条回复对热度最关键
- 关注"写 commit 时的痛苦"这个共鸣点,评论区多引导大家晒自己的 commit message
