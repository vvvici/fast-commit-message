# [掘金文章]

## 标题候选

1. 我用一个周末做了个「代码不出本机」的 AI commit message 工具
2. 告别憋 commit message:本地 LLM + git hook 的零依赖方案
3. 手把手:做一个本地 AI 写 commit 的 CLI 工具(含 hook 集成)

## 正文

### 为什么写 commit message 这么痛苦?

写 commit message 大概是程序员每天最机械的几分钟:改了几行代码,要组织语言、想 type、想 scope……写得太随意,同事 review 的时候看不懂;写得认真,又浪费时间。

用 AI 生成 commit message 不是什么新想法(aicommits 就是),但现有方案有个痛点:**你的代码 diff 要发到云端**(OpenAI),很多人因此不敢用,国内还要考虑科学上网和费用。

所以我做了一个纯本地的方案:**fcm** —— 基于 Ollama + qwen2.5,代码永远不出本机。

### 核心设计

**1. 单文件、零第三方依赖**
整个工具就是一个 `fcm.py`(约 380 行,只用 Python 标准库),通过 HTTP 直连本地 Ollama,没有 pip 依赖、没有 npm 依赖,curl 下来就能用。

**2. 交互式生成 + 人工把关**
```
$ fcm

生成的候选 commit message:

  [1] feat(calc): 添加减法函数
  [2] fix(calc): 确保 add 和 sub 函数正确实现
  [3] refactor(calc): 提升代码可读性,添加文档注释

  [e] 手动编辑   [c] 自定义输入   [q] 退出不提交

选择 (1-3 / e / c / q): 1
```

**3. Git Hook 集成:提交时自动预填**
`fcm install` 会生成一个 `prepare-commit-msg` hook。之后 `git commit`,编辑器会自动打开并预填 AI 生成的消息——**你可以改,也可以全删了写自己的**。AI 永远只是草稿,最终决定权在你。

hook 很克制,以下情况一律不打扰:

| 场景 | 行为 |
|---|---|
| `git commit -m "..."` / 模板 / 合并 / cherry-pick / amend | 尊重已有内容,跳过 |
| 无暂存改动 | 静默退出 |
| `FCM_DISABLE=1 git commit` | 临时禁用 |
| Ollama 未运行 / 生成失败 | 静默跳过,绝不阻塞提交 |

**4. 工程细节(踩坑记录)**
- **git 默认注释块**:`prepare-commit-msg` 运行时,消息文件里已经有 git 写入的"# 请为您的变更输入提交说明"注释块,用 `-s` 判断文件非空会误判。正确做法:过滤 `#` 开头行和空行后再判断是否有真实内容。
- **prompt 工程**:3b 小模型容易输出"中文解释 → 英文 message"的格式,需要在 prompt 里强约束 + 代码里兜底清洗(`→` 后只留真实 message)。
- **type 自动修正**:模型偶尔把 `docs` 写成 `doc`,用模糊匹配自动纠正。

### 快速上手

```bash
# 1. 安装 Ollama 并拉模型(一次性)
curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen2.5:3b

# 2. 安装 fcm
curl -O https://raw.githubusercontent.com/vvvici/fast-commit-message/main/fcm.py

# 3. 使用
git add .
python3 fcm.py            # 交互式生成
python3 fcm.py install    # 以后 git commit 自动预填
```

### 后续规划

- OpenAI 兼容端点(可直接接 DeepSeek / OpenRouter)
- mojicode 表情
- 多模型对比

GitHub:https://github.com/vvvici/fast-commit-message
如果对你有用,欢迎 star ⭐ 提 issue 🐛 和 PR 🤝

---

## 发布建议

- 掘金发文时间:周二/周四上午 10 点前后
- 分类选「前端」「后端」或「人工智能」;标签:`git`、`LLM`、`效率工具`、`开源`
- 文章里"踩坑记录"部分是差异化内容,回复区引导讨论"你会把代码 diff 给 AI 吗"这个隐私话题
- 发完把链接同步到公众号/即刻/微博,形成矩阵
