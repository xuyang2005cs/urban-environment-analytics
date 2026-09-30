# 设计工具安装记录

本轮设计工具只从用户指定的官方 GitHub 仓库取得。开发工具与应用运行依赖分离；外部参考仓库保存在 `D:\许洋\_references`，项目内的 `.agents/`、`.codex/` 和 `.impeccable/` 均由 Git 忽略。

| 工具 | 来源与版本 | 安装位置与方式 | License | 本轮用途 |
|---|---|---|---|---|
| UI UX Pro Max | `nextlevelbuilder/ui-ux-pro-max-skill` commit `09170ee`；CLI `2.15.0` | 全局安装 `ui-ux-pro-max-cli`，项目执行 `uipro init --ai codex`，技能位于 `.agents/skills/ui-ux-pro-max` | MIT | 产品类型、颜色、字体、图表、可访问性和 React 指南检索 |
| Impeccable | `pbakaus/impeccable` commit `0d6b47e`；skill metadata `4.4.0` | 官方 CLI `4.1.0` 两次下载校验超时，改用官方仓库自带 `.agents/skills/impeccable` 构建 | Apache-2.0 | PRODUCT/DESIGN、方向抽签、critique、audit、polish 和 harden |
| React Bits | `DavidHDev/react-bits` commit `e1bbb69` | 只在项目外浅克隆参考；不作为 Codex Skill，不复制整仓 | MIT + Commons Clause Condition | 选择少量免费、无额外依赖的动效组件 |
| Karpathy Guidelines | `multica-ai/andrej-karpathy-skills` commit `2c60614` | 将 `skills/karpathy-guidelines` 安装到 `.agents/skills/karpathy-guidelines` | 仓库 README 与 SKILL 声明 MIT | 最后一轮前端精简和范围控制 |

## Hook 状态

Impeccable 官方仓库中的 `.codex/hooks.json` 指向 `.codex/skills/impeccable`，而本项目实际技能位置为 `.agents/skills/impeccable`。该 manifest 未获当前 Codex 会话批准，也没有执行。当前会话直接调用官方 launcher 完成 context、concept、检测和审计。

`IMPECCABLE_HOOK_APPROVAL_REQUIRED=YES`。这不影响技能内容的读取与应用。

## 实际问题

- UI UX Pro Max 2.15.0 README 提到 `--dry-run`，但当前 CLI 返回 `unknown option`；正常初始化成功。
- Impeccable npm CLI 两次在校验远端 bundle 时超时并未写入文件；改用同一官方仓库内的 Codex payload。
- Impeccable 第一次方向抽签因网络不可达降级；使用同一 seed 重试后获得官方 catalog challenger。
