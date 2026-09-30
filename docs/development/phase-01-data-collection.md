# Phase 01：数据采集开发记录

## 环境

- Windows / PowerShell
- Python 3.13.14
- Git 2.53.0.windows.1
- GitHub CLI 2.95.0
- HTTPX 0.28.1、Pandas 2.3.3、Pydantic 2.12.5、pytest 9.1.1

## 范围与选择

Phase 1 只验证公共 API 数据链路，不进入数据库、复杂分析、Dashboard 或调度。Open-Meteo 同时提供 geocoding、历史天气和空气质量接口，可以用统一时间字段完成小规模对齐验证，且公共非商业接口无需虚构 API Key。

城市采用北京、上海、广州、深圳、东京和大阪。所有坐标与时区均通过 Geocoding API 结合 `countryCode=CN/JP` 实际确认后写入 `config/cities.json`。

## Collector 与 Retry

`OpenMeteoClient` 统一处理连接/读取超时、HTTP 状态、JSON 根结构和小时数组校验。网络异常与 5xx 最多尝试 3 次，退避为 0.5 秒、1 秒；4xx 和数据结构错误不会盲目重试。

## 首次真实请求

运行日期：2026-09-30；窗口：2026-09-23 至 2026-09-29（截至昨日的 7 个完整自然日）。

| 城市 | 天气行数 | 空气质量行数 | 合并行数 | 状态 |
|---|---:|---:|---:|---|
| 北京 | 168 | 168 | 168 | PASS |
| 上海 | 168 | 168 | 168 | PASS |
| 广州 | 168 | 168 | 168 | PASS |
| 深圳 | 168 | 168 | 168 | PASS |
| 东京 | 168 | 168 | 168 | PASS |
| 大阪 | 168 | 168 | 168 | PASS |

所有数据都以城市本地时区返回；本窗口内小时粒度完全对齐，因此 inner merge 保留全部 168 行。这个结果只证明当前窗口可对齐，不承诺所有历史时期或数据源永远无缺口。

## 标准化与质量策略

- `time` 解析为 Pandas datetime；业务列转换为数值。
- API 变量映射为解释性 snake_case 字段。
- 检查行数、必需列、空值、重复 `city + timestamp` 和无法转换的数值。
- 不在 Phase 1 进行插值、聚合或异常值修正。

## 自动化测试

主 pytest 套件只使用 HTTPX `MockTransport`，不依赖互联网。18 个测试覆盖三类正常响应、timeout、4xx/5xx、invalid JSON、缺字段、重试/退避、两类标准化、数值转换失败计数、合并和质量检查。真实联网只属于 probe 和 collection smoke。

## 实际问题与修复

1. **默认 Python 镜像无法解析依赖**  
   现象：项目 `.venv` 安装 `httpx==0.28.1` 时，机器配置的镜像返回“没有可用版本”。  
   原因：镜像当时未提供所需包/版本，并非 requirements 拼写错误。  
   修复：对依赖安装显式使用 PyPI 官方索引，并保留精确版本；最终四个核心依赖均在 Python 3.13.14 中导入并通过测试。

2. **隔离构建仍回落到不可用镜像**  
   现象：`pip install -e .` 的构建隔离环境再次从默认镜像请求 setuptools 并失败。  
   原因：PEP 517 build isolation 使用了本机默认索引。  
   修复：先从官方索引安装固定版本 setuptools，再使用 `--no-build-isolation -e .`；editable package 构建成功。README 给出同样的可复现步骤。

3. **PowerShell 工具输出中的中文城市名乱码**  
   现象：自动化终端捕获层显示城市中文名为替换字符，但 UTF-8 JSON 文件内容正确。  
   原因：PTY 捕获与 Windows 控制台代码页组合造成显示层编码不一致。  
   修复：证据页面直接读取 UTF-8 JSON，再由浏览器按 `<meta charset="utf-8">` 渲染；图片中的城市名可正确显示，数据本身未被改写。

## 遗留问题

- 免费接口没有 SLA；生产化需要监控、节流和对限额的进一步管理。
- Air Quality 全球域空间分辨率较粗，不能把网格结果解释为站点实测值。
- 本阶段只检查结构和基础质量，跨时区长期一致性、缺口处理和增量水位将在后续阶段设计。
- 未实现数据库持久化、调度、Dashboard 和复杂分析；它们明确不属于 Phase 1。
