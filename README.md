# Urban Environment Analytics Platform

基于 Python 构建的多城市环境数据采集与分析平台，通过公开天气与空气质量 API 获取时序数据，为后续数据清洗、质量检查、统计分析与可视化提供统一数据基础。

> 当前仓库处于 Phase 1：数据源验证与首批采集。数据库持久化、分析模块、Dashboard 和自动调度属于后续路线，尚未实现。

## 项目背景

城市天气与空气质量数据具有多城市、时间序列和字段结构差异等特点。本项目从可靠、可测试的公共 API 客户端开始，逐步建立采集、原始数据留存、标准化和质量控制的数据管道。

## 当前功能

- 项目结构与数据目录 Git 策略
- Open-Meteo 数据源官方接口验证（进行中）

## 数据源

- [Open-Meteo](https://open-meteo.com/)：天气、空气质量和地理编码公共 API

数据使用需遵循 Open-Meteo 及其上游数据提供方的署名要求。

## 快速开始

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pytest -v
```

## 项目结构

```text
src/urban_environment/   核心采集、处理与质量检查代码
scripts/                 真实网络 probe 与首次采集入口
config/                  经地理编码验证的城市配置
data/raw/                本地原始响应（Git 忽略）
data/processed/          本地处理结果（Git 忽略）
data/samples/            可提交的小型公共数据样例
tests/                   不依赖互联网的自动化测试
docs/                    架构、数据源和开发记录
```

## 后续扩展

Phase 2 以后再评估 ETL、SQLite/PostgreSQL、增量同步、数据质量报告、统计分析、Streamlit、调度和 GitHub Actions。

## License

项目代码采用 [MIT License](LICENSE)。Open-Meteo 数据受其数据源许可和署名条款约束。
