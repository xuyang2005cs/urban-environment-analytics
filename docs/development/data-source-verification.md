# Open-Meteo 数据源核验

核验日期：2026-09-30。以下信息来自 Open-Meteo 官方文档，而非第三方教程。

## 使用的接口

| 能力 | Endpoint | 主要参数 | Phase 1 用途 |
|---|---|---|---|
| 地理编码 | `https://geocoding-api.open-meteo.com/v1/search` | `name`, `countryCode`, `count`, `language` | 通过国家代码消歧并确认坐标、国家和时区 |
| 历史天气 | `https://archive-api.open-meteo.com/v1/archive` | `latitude`, `longitude`, `start_date`, `end_date`, `hourly`, `timezone` | 获取小时级天气数据 |
| 空气质量 | `https://air-quality-api.open-meteo.com/v1/air-quality` | `latitude`, `longitude`, `start_date`, `end_date`, `hourly`, `timezone` | 获取小时级污染物和 AQI |

官方资料：

- [Geocoding API](https://open-meteo.com/en/docs/geocoding-api)
- [Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api)
- [Air Quality API](https://open-meteo.com/en/docs/air-quality-api)
- [Pricing and API limits](https://open-meteo.com/en/pricing)

## 参数与响应约定

- 日期使用 `yyyy-mm-dd`，时间字段默认 ISO 8601。
- 显式传入城市的 IANA `timezone`，因此 API 返回本地时间并从本地 00:00 开始。
- 地理编码响应的 `results` 包含 WGS84 `latitude` / `longitude`、`country_code` 和 IANA `timezone`。
- 两个环境数据接口均返回 `hourly.time` 以及与其等长的变量数组；客户端在归一化前验证这些字段和数组长度。
- Historical Weather API 是再分析数据。官方文档说明 ERA5 等数据存在更新延迟；近期数据可能由当前可用模型组合提供。
- Air Quality API 使用 CAMS 欧洲或全球数据。北京等非欧洲城市由全球域支持；当前官方文档允许 `past_days` 0–92，也支持显式 `start_date` / `end_date`。

## 当前字段

天气官方变量：`temperature_2m`、`relative_humidity_2m`、`precipitation`、`wind_speed_10m`、`surface_pressure`。

空气质量官方变量：`pm2_5`、`pm10`、`nitrogen_dioxide`、`ozone`、`european_aqi`。

内部将 `european_aqi` 标准化为 `air_quality_index`。选择欧洲 AQI 是为了让六座城市使用同一连续指标；它不代表数据只来自欧洲模型。README 和代码保留此映射，避免把不同 AQI 标准混为一谈。

## 使用限制与署名

核验时官方免费开放接口用于非商业评估/原型，无 API Key，无可用性保证；限制为 600 次/分钟、5,000 次/小时、10,000 次/日和 300,000 次/月。Open-Meteo 数据基于 CC BY 4.0，必须署名。空气质量数据还要求明确署名 CAMS 数据提供方。本项目的首次采集规模远低于限制，并在文档与 README 中保留来源链接。

## 实际核验结果

2026-09-30 使用 `2026-09-23` 至 `2026-09-29` 的完整 7 天窗口：

- 北京 geocoding：PASS，`Asia/Shanghai`
- 北京天气：168 行
- 北京空气质量：168 行
- `city + timestamp` 内连接：168 行
- 六城市后续采集均返回天气和空气质量各 168 行

