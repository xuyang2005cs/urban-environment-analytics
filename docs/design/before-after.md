# 展示层重构对照

| 旧 Streamlit 展示层 | 新 Web 展示层 |
|---|---|
| sidebar radio 切换组件 | React Router 独立路由与浏览器历史 |
| Overview 由四个 KPI 卡开始 | 城市 Observation Hero、AQI 仪器与真实观测时间 |
| 页面普遍为卡片 + 图表 + 表格 | 页面根据城市分析、比较、质量、管道任务采用不同结构 |
| 框架默认表单、导航和响应式 | 统一 token、44px 控件、桌面 rail 与移动 bottom nav |
| Plotly/Streamlit 视觉痕迹明显 | 自定义 ECharts 主题、自然语言 tooltip 与可访问摘要 |
| 无空间索引 | 六城市 OSM 地图与可访问的城市列表 |
| Dashboard 直接读取 DuckDB | FastAPI 只读查询层隔离浏览器与分析存储 |
| 状态组件依赖框架 | Skeleton、Empty、Error 与 retry 使用统一产品语言 |
