# 首发计划(发布节奏)

三篇文案就绪:v2ex.md / juejin.md / reddit.md。

## 推荐发布节奏(冲 Trending 的核心:同一天集中发力)

| 时间 | 动作 |
|---|---|
| D 日 09:00 | 确认 GitHub 仓库 README/demo GIF 无误,`git tag v0.3.0` |
| D 日 10:00 | 发掘金(算法推荐期,前 2 小时最关键) |
| D 日 10:30 | 发 V2EX「分享创造」 |
| D 日 14:00 | 发 Reddit r/Python(UTC 6:00 左右,欧美早上) |
| D 日 14:30 | 同步到即刻/微博/公众号 + 朋友圈 |
| D+1~7 | 每天一个小版本(哪怕只是文档),保持 commit 活跃,冲 GitHub Trending(看"当日新增 star"和增速) |

## 发布前最后检查清单

- [ ] 仓库 README 顶部 GIF 能正常加载
- [ ] description + topics 已设置(已完成)
- [ ] `fcm.py` 顶部 docstring 的用法示例与 README 一致
- [ ] 本地真机完整跑一遍:交互模式 + hook 模式 + `--yes`
- [ ] 决定是否 `git tag v0.3.0` 并发布 GitHub Release(建议发布,增加可信度)

## 注意事项

- 三篇文案可以**错开一两天**发(避免同质化内容同一天刷屏,不同平台用户群不完全重叠)
- 若 Reddit 被 r/Python 拒绝(自荐规则严),换 r/commandline 或 r/selfhosted
- 首发后 48 小时内:每一条 issue / PR / comment 都尽快回复,早期贡献者决定项目温度
- 别刷星、别买星(GitHub 会检测,得不偿失)
