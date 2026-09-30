# 旧展示层 UI/UX 审计

审计对象为 Streamlit Dashboard 和 2026-09-30 的真实截图。

| 维度 | 发现 | 重构方向 |
|---|---|---|
| 信息层级 | Overview 从四个等权 KPI 开始，城市、观测时间和天气语境不够突出 | 城市 Observation Hero 成为首要视觉，AQI 与管道状态退居支持层 |
| Typography | Streamlit 默认层级明显，英文标题和中文说明混用 | 中文任务名称为主，英文只用于技术名与单位；数值使用 tabular figures |
| Color | 蓝/青统一但与具体环境语义联系较弱 | mineral daylight 中性地面，观测绿与大气青承担交互和序列，AQI 独占状态色 |
| Spacing | 容器、卡片、图表由框架控制，页面节奏相似 | 按页面任务建立不同网格和纵向节奏 |
| Navigation | sidebar radio 不是真正路由，刷新和直接链接体验有限 | React Router 提供独立 URL、Back、Forward、Refresh 与深链接 |
| Density | 表格和图表机械堆叠，组件缺少主次 | 重要观测使用 instrument composition，工程详情才使用高密度表格 |
| Form design | 默认 select/date 控件具有明显框架样式 | 统一 44px 控件、可见 label、focus、错误和禁用状态 |
| Data visualization | 多序列量纲偶尔共享视觉区域，标签仍偏工程字段 | 每张图回答一个问题；单位、自然语言 tooltip、摘要与表格替代齐全 |
| Empty/Error | 已有基础空状态，但恢复动作不一致 | 加载、空、错误统一组件，明确下一步和重试操作 |
| Responsiveness | 桌面可用，移动端依赖 Streamlit 自动折叠 | 设计 390px 底部导航、单列 hero、简化图表与横向可滚动表格 |
| Accessibility | 部分 HTML 由 `unsafe_allow_html` 注入，控件与图表语义受框架限制 | 语义 HTML、skip link、ARIA 状态、键盘导航、可见 focus 和 reduced motion |
| Consistency | 所有页面共享相似 KPI + 图表 + 表格模板 | Overview、City、Compare、Quality、Pipeline、About 各自拥有任务形态 |

## 模板感检查

- 删除机械四 KPI 首屏、嵌套卡片、英文 eyebrow 和每页同构布局。
- 不使用蓝紫渐变、玻璃态、大面积阴影、随机 icon square 或 landing-page hero。
- 地图、Observation Glyph、质量检查矩阵和 pipeline track 都承担真实信息功能。
- 页面动效只服务路由、数字变化和地图 marker 进入，并尊重 reduced motion。
