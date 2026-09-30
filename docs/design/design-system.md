# 城市环境观测台设计系统

## Brand identity

视觉定位是 **Environmental Data Observatory**：把城市理解为持续读数的环境仪器。界面同时表达天气、空气质量与数据工程证据，不复制消费天气 App，也不使用通用 SaaS bento 模板。

## Typography

- UI：`IBM Plex Sans` variable；中文回退 `PingFang SC`, `Microsoft YaHei`, system sans-serif。
- 数据与时间：`IBM Plex Mono`，仅用于观测值、watermark、时间与运行标识。
- Display 40/44、H1 28/34、H2 21/28、H3 17/24、Body 16/25、Caption 13/19、Label 12/16。
- 数据数字启用 `tabular-nums`；单位与数值之间保留空格。

## Color tokens

| Token | Value | Role |
|---|---|---|
| `surface-ground` | `#F2F5F2` | 页面背景 |
| `surface-paper` | `#FCFDFB` | 主要内容 |
| `surface-soft` | `#E8EFEB` | 导航与次级区域 |
| `text-primary` | `#142821` | 主文字 |
| `text-muted` | `#5E7169` | 元数据 |
| `primary` | `#1F6B57` | 操作、选中与主序列 |
| `secondary` | `#287F91` | 天气序列、focus 与链接 |
| `attention` | `#C47A24` | 需要注意的非错误状态 |
| `danger` | `#B64242` | 失败与危险 |
| `border` | `#D7E0DB` | 规则线和表格边界 |

AQI 语义：Good `#2C7A5B`、Fair `#7A8D32`、Moderate `#B57A1F`、Poor `#B85C32`、Very poor `#A53E4A`、Extremely poor `#74406B`。每种颜色都与等级文本共现。

Quality / Pipeline：PASS/SUCCESS 使用 primary，WARN/NO_DATA 使用 attention，FAIL 使用 danger，RUNNING 使用 secondary。

## Spacing and grid

- 4px 基础单位；主要刻度 4 / 8 / 12 / 16 / 24 / 32 / 48 / 64。
- Desktop container 最大 1480px，内容 gutters 32px；sidebar 248px。
- Tablet gutters 24px；mobile gutters 16px。
- 12-column desktop grid，8-column tablet，4-column mobile。

## Surface, border, shadow and radius

- 页面区域主要通过背景、1px border 和 whitespace 分层。
- Shadow 只用于 tooltip、menu、drawer：`0 12px 32px rgba(20,40,33,.14)`。
- 默认 radius 12px，密集控件 8px，badge/pill 只用于短状态。
- 禁止 cards inside cards；普通内容块不同时使用边框与阴影。

## Navigation

- ≥1024px：固定左侧导航，包含品牌、六个主路由、城市快捷入口和 pipeline status。
- 768–1023px：顶部栏 + 可展开 drawer。
- <768px：顶部标题栏 + 五项底部导航；Pipeline/About 在 More drawer。
- active 使用 2px 观察线、字重和背景共同表达，不只靠颜色。

## Component system

- `ObservationHero`：城市、当地时间、观测时间、温度、真实天气状态、Observation Glyph。
- `ObservationGlyph`：SVG 环形刻度编码湿度、AQI、降水、风与气压。
- `AQIStatus`：AQI 值、European AQI 标签、等级文字与污染物列表。
- `CityQuickCard`：城市、当地时间、温度、AQI、PM2.5、七日 sparkline；点击进入详情。
- `MetricSwitch` / `DateRangeControl`：可见 label、44px 高度、键盘操作。
- `ChartFrame`：标题、问题说明、单位、摘要、图例和表格替代。
- `QualityCheck`：检查名称、状态、数值和解释，不使用相同 icon 卡模板。
- `PipelineTrack`：按真实数据链路连接节点；状态、最后运行和记录量可读。
- `AsyncState`：Skeleton、Empty、Error 三种状态与恢复动作。

## Chart guidance

- 时间变化使用 line/area；城市精确比较使用 sorted bar；覆盖使用 matrix；异常使用 line + distinct marker。
- 最多 4 条主要序列，颜色以外增加线型/点形和直接标签。
- 轴显示自然语言与单位；tooltip 使用当地日期和完整单位。
- 图表下提供一句趋势摘要；关键数据提供表格视图。

## Icon rules

- 使用 Lucide 一套 1.75px outline SVG；装饰图标 `aria-hidden`，icon button 必须有 accessible name。
- 天气图标基于 WMO `weather_code` 映射并用项目内 SVG component 绘制；不使用 emoji。
- 地图图标由 CSS/SVG 绘制，不加载版权图片。

## Interaction and motion

- Hover 160ms，route/content enter 220ms，drawer 240ms；只动 transform/opacity。
- 页面切换轻微 fade + 6px rise；温度/AQI 数字变化采用一次 count transition；marker 初次载入 stagger ≤30ms。
- `prefers-reduced-motion: reduce` 时取消平移、计数和 stagger，内容立即处于最终状态。
- focus ring 为 3px atmosphere cyan 外环；所有触控目标至少 44px。

## States

- Loading：与最终结构一致的 skeleton，不显示空坐标轴。
- Empty：说明筛选范围没有数据，并提供重置筛选。
- Error：说明查询失败并提供 retry，不暴露 Python traceback。
- Disabled：原生 disabled 语义 + 45% opacity，不可点击。

## Responsive breakpoints

- `390px`：移动基准，单列 Observation Hero 与底部导航。
- `768px`：双列统计与可展开导航。
- `1024px`：持久 sidebar。
- `1366px`：标准桌面。
- `1440px` 与 `1920px`：扩大留白和地图/图表宽度，不放大字体制造空洞。
