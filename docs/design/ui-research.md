# UI 研究

研究对象均来自公开、官方页面；结论用于理解信息组织，不复制品牌视觉或版权资产。

## Apple Weather

Apple Weather 将地点、温度和天气状况放在首要层级，小时序列紧随其后；地图与地点列表是稳定的二级入口。空气质量只在适用时进入主流程，避免每项指标争夺相同权重。[Apple Weather 使用说明](https://support.apple.com/en-kg/guide/iphone/iph1ac0b35f/ios)

采用：地点优先、时间语境、单指标切换和可触达的城市入口。不采用其品牌插画、商标视觉或预报式措辞。

## Windy

Windy 让地图成为主操作面，图层、图例、时间和预测模型围绕地图组织；数据更新时间和模型来源清晰可见。[Windy 菜单与图层](https://www.windy.com/menu)

采用：地图 marker 与图例共同表达、图层/指标状态明确、更新时间紧邻数据。不引入需要商业 key 的 Windy API，也不复制粒子风场。

## IQAir

IQAir 通过地图、城市排名和明确的 AQI 等级让污染物状态快速可读；数字、等级文字和颜色同时出现。[IQAir Air Quality Map](https://www.iqair.com/air-quality-map)

采用：AQI 数值 + 等级 + 语义色、污染物细分和城市比较。不采用健康建议或 US AQI+ 表述，因为项目数据是 European AQI。

## Copernicus Climate Indicators

Copernicus 把 headline values、解释文字、数据来源和可下载时序结合，清楚区分观测结论与方法依据。[Climate Indicators](https://climate.copernicus.eu/climate-indicators)

采用：指标旁边显示更新时间、来源和方法边界；图表回答单一问题，并提供数据表或摘要。不复制其叙事滚动页面，因为本产品是高频操作型界面。

## 综合结论

1. Overview 首先回答“这座城市最近一次观测是什么”，然后才是六城市切换和趋势。
2. 地图适合建立空间索引，但不能替代精确比较图表。
3. AQI 必须带标准名称、等级文字和污染物细分。
4. 城市比较应保留筛选与排序，不生成综合宜居结论。
5. 质量与管道页面采用数据工程语言和结构，不能伪装成天气卡片。
6. 加载骨架保留最终布局空间；空状态解释如何恢复；错误状态提供重试。
7. 桌面使用持久导航，移动端使用底部主导航与更多菜单。
