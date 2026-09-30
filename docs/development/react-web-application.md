# React Web 应用重构记录

## 目标

将分析展示层升级为 React、Vite 和 TypeScript 多页面应用，并通过 FastAPI 只读接口连接现有 DuckDB 分析层。数据采集、Parquet、增量 ETL、质量系统和调度器保持原有职责。

## 产品结构

正式页面为 Overview、City Detail、Compare、Data Quality、Pipeline Monitor 和 About。根路径重定向到 `/overview`，其他路由支持直接访问和刷新。

视觉方向为“城市即观测仪器”：深绿观测面、矿物雾背景、数据等宽字体和由湿度、AQI、风速、降水共同驱动的 Observation Glyph。天气状态使用 WMO `weather_code` 与 SVG 图标映射。

## API 与前端

FastAPI 暴露城市元数据、概览、天气与空气质量序列、城市比较、质量运行、采集运行和水位等只读接口。Pydantic 响应模型隔离数据库实现细节。前端对路由页面和 ECharts 分别做动态加载；加载、空数据和查询错误均有独立状态。

## 数据扩展

天气采集新增 Open-Meteo 官方 `weather_code` 字段，随后同步 Normalizer、Parquet、DuckDB 视图、质量范围、API 和测试。六城指定窗口回放真实拉取 2,016 条数据，幂等层跳过 2,016 条重复记录；联合视图保留 1,008 条小时观测，`weather_code` 非空率为 100%。

## 设计工具应用

1. UI UX Pro Max 用于产品模式、颜色、字体、图表、响应式和反模式研究。
2. Impeccable 用于 layout、typeset、colorize、harden、adapt、audit 与 polish 检查。
3. React Bits 只采用一个低强度进入动效，在 reduced-motion 环境下停用。
4. Karpathy Guidelines 用于删除旧展示层、路由拆包和避免新增抽象层。

## 测试策略

- Python：Analytics API 使用临时 DuckDB fixture；主套件不依赖真实网络。
- 前端：Vitest + Testing Library 验证路由恢复、天气状态、AQI 分级和缺失值。
- 浏览器：Playwright 验证七条路由、直接访问、刷新、前进后退、城市和指标切换、地图、移动导航及五档视口。
- CI：Python compile / pytest 与前端 typecheck / test / build 分为两个 job。

## 实际问题

### Impeccable 安装器校验超时

官方 `npx impeccable install` 两次停在远端 bundle 校验。使用同一官方仓库浅克隆中的 `.agents/skills/impeccable` 完成项目级安装并记录来源 commit；未执行路径不匹配的 hook。

### FastAPI 联合响应注解被当作 response model

SPA fallback 使用 `FileResponse | RedirectResponse` 后，FastAPI 启动时尝试生成不支持的响应模型。对文件路由显式设置 `response_model=None`，API 路由继续保留严格 Pydantic 模型。

### TypeScript 7 构建配置变化

CSS side-effect import 缺少模块声明，且 node 配置中的 `allowImportingTsExtensions` 需要 `noEmit`。增加 `vite-env.d.ts` 并将 Vite 配置改用 `vitest/config`，typecheck 与 build 恢复。

### 固定日期测试跨月失效

watermark 测试把 2026-09-29 写死为“最后可用日”，日期跨到 10 月后管道正确请求新窗口，测试却误判。测试改为按城市时区动态计算前一日 23:00，不修改生产逻辑。

### 后端状态大小写影响前端语义色

采集状态实际为 `SUCCESS`，首版 CSS 按 `success` 匹配，成功节点显示为警告色。渲染前统一将 class token 转小写，展示文本继续使用原始状态值。

## 后续维护

真实设备 Safari / Android 触控与屏幕阅读器仍需在部署环境补充验证。ECharts 以路由级异步 chunk 加载，后续如首访城市详情的网络性能成为瓶颈，可进一步改为 core 模块按需注册。
