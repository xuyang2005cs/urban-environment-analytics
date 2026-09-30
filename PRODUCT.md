# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

Python 数据平台与只读 FastAPI Analytics API；React、Vite 和 TypeScript Web 前端。该技术方向由项目需求明确指定。

## Users

主要用户是需要查看多城市天气、空气质量和数据管道状态的数据分析人员与工程人员。他们会在桌面端比较城市指标、检查时间趋势和质量运行，也需要在移动端快速查看最近观测。

## Product Purpose

平台持续采集六座城市的公开天气与空气质量时序数据，经过标准化、质量检查和增量 ETL 后形成可查询的分析层，并提供城市概览、趋势比较、质量诊断和管道运行监控。

## Positioning

同一产品界面同时呈现环境观测结果和产生这些结果的数据工程证据：每项指标都能回到数据时间、质量状态、watermark 与 collection run，而不是脱离管道上下文的天气卡片。

## Operating Context

- 用户从城市概览进入单城市历史时间线，或在比较页选择城市与指标。
- 数据质量页用于检查 schema、完整性、重复、连续性、数值转换和范围结果。
- 管道页用于检查 Open-Meteo 到 DuckDB 的处理节点、watermark、运行耗时和写入数量。
- 页面展示仓库中最近完整小时的历史观测，不表示实时天气或天气预报。

## Capabilities and Constraints

- 城市范围固定为北京、上海、广州、深圳、东京和大阪。
- 环境指标来自 DuckDB `environment_hourly` 及运行元数据表。
- 时间在存储层统一为 UTC，界面同时提供城市当地时间语境。
- AQI 使用 Open-Meteo 返回的 European AQI。
- 相关性是统计探索，不表示因果关系；IQR 异常只标记、不删除。
- Web API 只读；浏览器不直接访问 Raw JSON、Parquet 或 DuckDB 文件。
- 不制造预测、实时告警、天气状态或仓库中不存在的数据。

## Brand Commitments

产品名称为 Urban Environment Analytics Platform，中文界面名称为“城市环境观测台”。产品语言专业、克制、可追溯，以环境观测和数据管道语汇为核心。

## Evidence on Hand

- 六城市各 168 条天气与 168 条空气质量真实公开数据。
- Clean 层共 1,008 条天气、1,008 条空气质量记录，联合小时视图 1,008 条。
- 12 个 city × dataset watermark、collection runs 与 quality runs。
- 53 项离线 Python 测试与 GitHub Actions。
- 当前数据库没有 `weather_code`，因此视觉系统不得声称晴、雨等天气状况。

## Product Principles

1. 最新观测必须显示时间与数据来源，不伪装为实时状态。
2. 指标优先回答用户问题，工程字段转换为自然语言标签。
3. 环境状态与管道健康同等可追溯，但不在同一页面争夺主层级。
4. 页面按任务形成不同结构，同时共享一致的导航、状态和数据语义。
5. 失败、空数据和加载过程提供明确恢复路径。

## Accessibility & Inclusion

键盘可完成导航与筛选；状态使用文字、图形和颜色共同表达；正文达到 WCAG 2.2 AA 对比度；动效尊重 `prefers-reduced-motion`；桌面、平板与 390px 移动端均可操作。
