# 第三方 UI 与设计工具

## 开发期设计工具

UI UX Pro Max、Impeccable 与 Karpathy Guidelines 仅用于设计研究、审查和代码精简，不属于应用运行时依赖。安装路径、版本和来源 commit 见 [tooling-setup.md](tooling-setup.md)。

## React Bits

- 来源：<https://github.com/DavidHDev/react-bits>
- 模式：免费 React 组件库，不作为 Codex Skill 使用
- 版本来源：commit `e1bbb696`
- 许可：MIT + Commons Clause License Condition v1.0，Copyright (c) 2026 David Haz
- 使用组件：`FadeContent`
- 用途：Overview 的天气 Hero、六城观测站和地图区域进入动画
- 依赖：`gsap@3.13.0`
- 本地调整：减小位移与时长，移除 blur，并为 `prefers-reduced-motion` 提供静态路径

组件只作为本应用的一部分使用，不单独出售、再授权或分发。

## 其他运行时 UI 依赖

- Lucide React：SVG 界面与天气状态图标
- Apache ECharts：城市环境时间序列
- Leaflet / React Leaflet：六城市地理视图
- OpenStreetMap：地图瓦片；界面保留 contributors attribution
- IBM Plex Sans / IBM Plex Mono：通过 Fontsource 自托管字体文件

完整版本以 `frontend/package-lock.json` 为准。
