# Dashboard 设计记录

Dashboard 是 DuckDB 的只读展示层，不直接访问 Open-Meteo，也不重复实现 ETL。

视觉采用雾白背景、深墨色文本、数据蓝与青色强调；AQI 红黄绿只表达指标语义。页面以 UTC watermark 细线作为统一视觉签名，强调这是一个可追踪的数据管道，而不是通用后台模板。

## 页面

- Overview：核心指标、温度趋势、AQI 趋势和城市快照。
- City Analysis：单城市温度、湿度、PM2.5、AQI 与异常点。
- City Comparison：多城市温度、PM2.5 和 AQI 对比。
- Data Quality：最近质量状态、问题和时间覆盖。
- Pipeline Monitor：最近采集运行、watermark、写入与跳过数量。
- About：数据来源、分层架构和限制。

全局筛选提供城市和日期范围。查询结果为空、数据库未初始化或查询失败时均显示明确提示。页面已在 1920×1080 与 1366×768 下通过真实浏览器检查，未发现页面级水平溢出或中文字体异常。
