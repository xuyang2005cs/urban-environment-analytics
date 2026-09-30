# 存储设计

## Raw Layer

原始响应保存在 `data/raw/YYYY-MM-DD/<city>/` 下，天气与空气质量分别写入 JSON。Raw 层用于审计和问题复现，不做业务字段改写，并由 `.gitignore` 排除。

## Clean Parquet Layer

标准化数据按以下路径分区：

```text
data/processed/<dataset>/city=<city>/year=<YYYY>/month=<MM>/*.parquet
```

天气和空气质量的逻辑主键均为 `city + timestamp`。写入时读取目标分区、合并、去重并原子替换文件，因此重复采集相同时间窗口不会产生重复记录。

时间字段统一保存为 UTC；同时保留城市的 IANA `timezone`，供展示层转换。每条记录还带有 `source` 和 UTC `ingested_at`，便于追踪来源和摄取时间。

## DuckDB 查询与元数据

`data/analytics/environment.duckdb` 包含：

- `pipeline_watermarks`：每个城市和数据集最后成功同步的时间戳。
- `collection_runs`：请求范围、抓取数、插入数、跳过数、耗时和状态。
- `quality_runs`：质量结果、问题明细及统计。
- `weather_clean`、`air_quality_clean`：直接读取 Parquet 的视图。
- `environment_hourly`：按城市和时间戳连接天气与空气质量。
- `city_daily_summary`：面向分析与展示的日聚合视图。

数据库、Parquet、Raw JSON、报告和锁文件都是本地运行产物，不提交到 Git。仓库只保留小型公开样例。
