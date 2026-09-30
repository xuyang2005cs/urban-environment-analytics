"""Streamlit interface for the local environmental analytics platform."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from urban_environment.analytics.environment import (
    city_comparison,
    correlation_exploration,
    detect_anomalies,
    rolling_analytics,
)
from urban_environment.dashboard.data import DashboardRepository


ROOT = Path(__file__).resolve().parents[3]
DATABASE = ROOT / "data" / "analytics" / "environment.duckdb"

NAVIGATION = {
    "Overview": "总览",
    "City Analysis": "城市分析",
    "City Comparison": "城市比较",
    "Data Quality": "数据质量",
    "Pipeline Monitor": "管道监控",
    "About": "关于平台",
}
CITY_NAMES = {
    "beijing": "北京",
    "shanghai": "上海",
    "guangzhou": "广州",
    "shenzhen": "深圳",
    "tokyo": "东京",
    "osaka": "大阪",
}
BLUE = "#1677A3"
CYAN = "#23A6A8"
SLATE = "#536779"
AMBER = "#C58A2A"
RED = "#C45454"


st.set_page_config(
    page_title="Urban Environment Analytics",
    page_icon="◌",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data(ttl=60)
def load_environment(path: str) -> pd.DataFrame:
    return DashboardRepository(Path(path)).environment()


@st.cache_data(ttl=60)
def load_pipeline(path: str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    repository = DashboardRepository(Path(path))
    return repository.recent_runs(30), repository.watermarks(), repository.quality_runs(60)


def inject_style() -> None:
    st.markdown(
        """
        <style>
        :root { --ink:#14212b; --muted:#61717e; --line:#dce5e9; --paper:#f4f7f8; --blue:#1677a3; }
        html, body, [class*="css"] { font-family: "Segoe UI", "Microsoft YaHei", sans-serif; color:var(--ink); }
        .stApp { background:var(--paper); }
        .block-container { max-width:1500px; padding-top:1.35rem; padding-bottom:3rem; }
        [data-testid="stSidebar"] { background:#edf2f4; border-right:1px solid var(--line); }
        [data-testid="stSidebar"] .stRadio label { padding:.28rem 0; }
        h1,h2,h3 { letter-spacing:-.025em; color:#14212b; }
        h1 { font-size:2.1rem !important; margin-bottom:.15rem !important; }
        h2 { font-size:1.34rem !important; margin-top:1.2rem !important; }
        .eyebrow { color:#1677a3; font-size:.74rem; font-weight:700; letter-spacing:.16em; text-transform:uppercase; }
        .subhead { color:var(--muted); font-size:1rem; margin-bottom:.7rem; }
        .status-pill { display:inline-flex; align-items:center; gap:.45rem; border:1px solid #b9d8cd;
          background:#eef8f4; color:#26745f; padding:.36rem .68rem; border-radius:999px; font-size:.78rem; font-weight:650; }
        .status-dot { width:7px; height:7px; border-radius:50%; background:#329b7a; }
        .waterline { height:24px; border-top:2px solid #8dcbd0; margin:.9rem 0 .6rem; position:relative; }
        .waterline:before,.waterline:after { content:""; position:absolute; top:-5px; width:8px; height:8px;
          border-radius:50%; background:#1677a3; }
        .waterline:before { left:0; } .waterline:after { right:0; }
        .watermark-label { position:absolute; right:12px; top:6px; color:#61717e; font:600 .72rem/1 "Cascadia Mono",monospace; }
        .metric-card { background:white; border:1px solid var(--line); border-radius:10px; padding:1rem 1.05rem .92rem;
          min-height:118px; box-shadow:0 1px 2px rgba(27,49,62,.035); }
        .metric-label { color:#61717e; font-size:.76rem; font-weight:700; letter-spacing:.04em; text-transform:uppercase; }
        .metric-value { color:#14212b; font-size:2rem; font-weight:720; letter-spacing:-.045em; line-height:1.15; margin:.38rem 0 .15rem; }
        .metric-note { color:#748590; font-size:.78rem; }
        .aqi-good { border-top:3px solid #329b7a; } .aqi-moderate { border-top:3px solid #c58a2a; }
        .aqi-poor { border-top:3px solid #c45454; }
        [data-testid="stVerticalBlockBorderWrapper"] { background:#fff; border-color:var(--line) !important; border-radius:10px !important; }
        [data-testid="stDataFrame"] { border:1px solid var(--line); border-radius:8px; overflow:hidden; }
        .section-caption { color:#748590; font-size:.82rem; margin-top:-.45rem; margin-bottom:.8rem; }
        .empty { background:#fff; border:1px dashed #b8c7ce; border-radius:10px; color:#61717e; padding:2rem; text-align:center; }
        @media (max-width: 900px) { .block-container { padding-left:1rem; padding-right:1rem; } .metric-value{font-size:1.55rem;} }
        </style>
        """,
        unsafe_allow_html=True,
    )


def chart_style(figure: go.Figure, *, height: int = 350) -> go.Figure:
    figure.update_layout(
        height=height,
        margin=dict(l=16, r=12, t=20, b=12),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="white",
        font=dict(family="Segoe UI, Microsoft YaHei, sans-serif", color="#334652", size=12),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        hovermode="x unified",
        colorway=[BLUE, CYAN, SLATE, AMBER],
    )
    figure.update_xaxes(showgrid=False, linecolor="#dce5e9", rangeslider_visible=False)
    figure.update_yaxes(gridcolor="#e8eef1", zeroline=False)
    return figure


def metric_card(label: str, value: str, note: str, css: str = "") -> None:
    st.markdown(
        f"<div class='metric-card {css}'><div class='metric-label'>{label}</div>"
        f"<div class='metric-value'>{value}</div><div class='metric-note'>{note}</div></div>",
        unsafe_allow_html=True,
    )


def aqi_class(value: float) -> str:
    if value <= 40:
        return "aqi-good"
    if value <= 80:
        return "aqi-moderate"
    return "aqi-poor"


def header(runs: pd.DataFrame) -> None:
    left, right = st.columns([4, 1.25], vertical_alignment="center")
    with left:
        st.markdown("<div class='eyebrow'>Environmental data observatory</div>", unsafe_allow_html=True)
        st.title("Urban Environment Analytics")
        st.markdown("<div class='subhead'>多城市天气与空气质量数据分析平台</div>", unsafe_allow_html=True)
    with right:
        failed = not runs.empty and runs.iloc[0]["status"] == "FAILED"
        status = "Pipeline issue" if failed else "Pipeline healthy"
        st.markdown(
            f"<div class='status-pill'><span class='status-dot'></span>{status}</div>",
            unsafe_allow_html=True,
        )
        if not runs.empty:
            synced = pd.to_datetime(runs.iloc[0]["started_at"], utc=True)
            st.caption(f"Last sync · {synced.strftime('%Y-%m-%d %H:%M UTC')}")
    st.markdown(
        "<div class='waterline'><span class='watermark-label'>UTC · clean layer watermark</span></div>",
        unsafe_allow_html=True,
    )


def filter_data(data: pd.DataFrame) -> tuple[pd.DataFrame, list[str], str]:
    cities = sorted(data["city"].dropna().unique())
    with st.container(border=True):
        c1, c2, c3, c4 = st.columns([2, 2, 1.3, .8], vertical_alignment="bottom")
        with c1:
            selected = st.multiselect(
                "城市",
                cities,
                default=cities[:1],
                format_func=lambda value: CITY_NAMES.get(value, value),
            )
        minimum = pd.to_datetime(data["timestamp"], utc=True).min().date()
        maximum = pd.to_datetime(data["timestamp"], utc=True).max().date()
        with c2:
            selected_dates = st.date_input("日期范围", value=(minimum, maximum), min_value=minimum, max_value=maximum)
        with c3:
            metric = st.selectbox("主要指标", ["temperature", "pm2_5", "air_quality_index"], format_func=lambda x: {"temperature":"温度", "pm2_5":"PM2.5", "air_quality_index":"AQI"}[x])
        with c4:
            st.button("刷新数据", use_container_width=True, on_click=st.cache_data.clear)
    filtered = data[data["city"].isin(selected)].copy()
    if len(selected_dates) == 2:
        timestamps = pd.to_datetime(filtered["timestamp"], utc=True)
        filtered = filtered[(timestamps.dt.date >= selected_dates[0]) & (timestamps.dt.date <= selected_dates[1])]
    return filtered, selected, metric


def overview(data: pd.DataFrame, runs: pd.DataFrame) -> None:
    filtered, selected, metric = filter_data(data)
    if filtered.empty:
        st.markdown("<div class='empty'>当前筛选条件没有数据，请扩大日期范围或选择其他城市。</div>", unsafe_allow_html=True)
        return
    latest = filtered.sort_values("timestamp").iloc[-1]
    quality = "PASS" if runs.empty or not (runs["quality_status"] == "FAIL").any() else "FAIL"
    cards = st.columns(4)
    with cards[0]: metric_card("当前温度", f"{latest.temperature:.1f} °C", CITY_NAMES.get(latest.city, latest.city))
    with cards[1]: metric_card("空气质量指数", f"{latest.air_quality_index:.0f}", "European AQI", aqi_class(float(latest.air_quality_index)))
    with cards[2]: metric_card("PM2.5", f"{latest.pm2_5:.1f}", "μg/m³ · latest observation")
    with cards[3]: metric_card("数据质量", quality, f"{len(filtered):,} aligned hourly rows")

    left, right = st.columns([2, 1])
    with left:
        st.subheader("Weather trend")
        st.markdown("<div class='section-caption'>温度、湿度与风速 · 支持缩放和悬停查看</div>", unsafe_allow_html=True)
        aggregate = filtered.groupby("timestamp", as_index=False)[["temperature", "relative_humidity", "wind_speed"]].mean()
        trend = aggregate.melt(id_vars=["timestamp"], value_vars=["temperature", "relative_humidity", "wind_speed"], var_name="metric", value_name="value")
        fig = px.line(trend, x="timestamp", y="value", color="metric", color_discrete_map={"temperature":BLUE,"relative_humidity":CYAN,"wind_speed":SLATE})
        st.plotly_chart(chart_style(fig, height=350), use_container_width=True, config={"displaylogo": False})
    with right:
        st.subheader("Air quality snapshot")
        st.markdown("<div class='section-caption'>所选城市期间均值，不构成健康建议</div>", unsafe_allow_html=True)
        means = filtered[["pm2_5", "pm10", "air_quality_index"]].mean().rename({"air_quality_index":"AQI"})
        fig = go.Figure(go.Bar(x=means.values, y=means.index, orientation="h", marker_color=[CYAN, BLUE, aqi_color(means["AQI"])]))
        st.plotly_chart(chart_style(fig, height=350), use_container_width=True, config={"displaylogo": False})

    st.subheader("Air quality trend")
    aggregate_air = filtered.groupby("timestamp", as_index=False)[["pm2_5", "pm10", "air_quality_index"]].mean()
    air = aggregate_air.melt(id_vars=["timestamp"], value_vars=["pm2_5", "pm10", "air_quality_index"], var_name="metric", value_name="value")
    fig = px.line(air, x="timestamp", y="value", color="metric", color_discrete_map={"pm2_5":CYAN,"pm10":BLUE,"air_quality_index":SLATE})
    st.plotly_chart(chart_style(fig, height=330), use_container_width=True, config={"displaylogo": False})


def aqi_color(value: float) -> str:
    return "#329b7a" if value <= 40 else AMBER if value <= 80 else RED


def city_analysis_page(data: pd.DataFrame) -> None:
    city = st.selectbox("选择城市", sorted(data.city.unique()), format_func=lambda value: CITY_NAMES.get(value, value))
    local = data[data.city == city].sort_values("timestamp")
    rolled = rolling_analytics(local)
    cards = st.columns(4)
    with cards[0]: metric_card("小时记录", f"{len(local):,}", "Clean + Analytics")
    with cards[1]: metric_card("平均温度", f"{local.temperature.mean():.1f} °C", "selected window")
    with cards[2]: metric_card("平均 PM2.5", f"{local.pm2_5.mean():.1f}", "μg/m³")
    with cards[3]: metric_card("累计降水", f"{local.precipitation.sum():.1f} mm", "selected window")
    st.subheader("城市环境时间线")
    metric = st.segmented_control("指标", ["temperature", "pm2_5", "air_quality_index"], default="temperature", format_func=lambda x: {"temperature":"温度", "pm2_5":"PM2.5", "air_quality_index":"AQI"}[x])
    figure = go.Figure()
    figure.add_trace(go.Scatter(x=rolled.timestamp, y=rolled[metric], name="Hourly", line=dict(color="#9ab0bd", width=1)))
    figure.add_trace(go.Scatter(x=rolled.timestamp, y=rolled[f"{metric}_rolling_24h"], name="24h rolling", line=dict(color=BLUE, width=2.5)))
    figure.add_trace(go.Scatter(x=rolled.timestamp, y=rolled[f"{metric}_rolling_7d"], name="7d rolling", line=dict(color=CYAN, width=2)))
    st.plotly_chart(chart_style(figure, height=430), use_container_width=True, config={"displaylogo":False})
    anomalies = detect_anomalies(local)
    st.subheader("Anomaly events")
    st.caption("IQR 标记仅用于探索；记录不会从 Clean 层删除。")
    st.dataframe(anomalies if not anomalies.empty else pd.DataFrame(columns=["city","timestamp","metric","value","score"]), use_container_width=True, hide_index=True)


def comparison_page(data: pd.DataFrame) -> None:
    comparison = city_comparison(data)
    st.subheader("六城市指标比较")
    st.markdown("<div class='section-caption'>每个指标独立比较，不生成“宜居度”等无依据综合结论。</div>", unsafe_allow_html=True)
    metric = st.selectbox("排序指标", ["temperature_mean", "pm2_5_mean", "air_quality_index_mean", "precipitation_mean", "wind_speed_mean"], format_func=lambda x: x.replace("_mean", "").replace("_", " ").upper())
    ordered = comparison.sort_values(metric, ascending=metric in {"pm2_5_mean", "air_quality_index_mean"})
    fig = px.bar(ordered, x="city", y=metric, text_auto=".1f", color_discrete_sequence=[BLUE])
    fig.update_xaxes(tickmode="array", tickvals=ordered.city, ticktext=[CITY_NAMES.get(city, city) for city in ordered.city])
    st.plotly_chart(chart_style(fig, height=420), use_container_width=True, config={"displaylogo":False})
    st.subheader("相关性探索")
    st.caption("Pearson 相关系数仅展示统计相关性，不代表因果关系。")
    correlations = correlation_exploration(data)
    matrix = correlations.pivot(index="metric_x", columns="metric_y", values="correlation")
    fig = px.imshow(matrix, text_auto=".2f", zmin=-1, zmax=1, color_continuous_scale=[[0,"#c45454"],[.5,"#eef2f4"],[1,"#1677a3"]])
    fig.update_layout(coloraxis_colorbar_title="Pearson r")
    st.plotly_chart(chart_style(fig, height=360), use_container_width=True, config={"displaylogo":False})


def quality_page(quality: pd.DataFrame) -> None:
    if quality.empty:
        st.markdown("<div class='empty'>尚无质量运行记录。先执行一次 pipeline collect。</div>", unsafe_allow_html=True)
        return
    latest = quality.sort_values("created_at").groupby(["city","dataset"], as_index=False).tail(1)
    cards = st.columns(4)
    with cards[0]: metric_card("最新检查", str(len(latest)), "city × dataset")
    with cards[1]: metric_card("PASS", str((latest.status == "PASS").sum()), "latest reports")
    with cards[2]: metric_card("时间缺口", str(int(latest.timestamp_gaps.sum())), "hourly gaps")
    with cards[3]: metric_card("范围告警", str(int(latest.range_violations.sum())), "records flagged")
    st.subheader("质量运行矩阵")
    fig = px.bar(latest, x="city", y="rows", color="status", facet_col="dataset", color_discrete_map={"PASS":"#329b7a","WARN":AMBER,"FAIL":RED})
    st.plotly_chart(chart_style(fig, height=350), use_container_width=True, config={"displaylogo":False})
    st.subheader("最近质量报告")
    st.dataframe(quality, use_container_width=True, hide_index=True)


def pipeline_page(runs: pd.DataFrame, watermarks: pd.DataFrame) -> None:
    if runs.empty:
        st.markdown("<div class='empty'>尚无管道运行。使用 CLI 完成首次 bootstrap 后查看。</div>", unsafe_allow_html=True)
        return
    successes = runs[runs.status.isin(["SUCCESS", "NO_DATA"])]
    latest = runs.iloc[0]
    latest_success = (
        pd.to_datetime(successes.iloc[0].started_at, utc=True).strftime("%m-%d %H:%M")
        if not successes.empty
        else "—"
    )
    cards = st.columns(4)
    with cards[0]: metric_card("最近成功", latest_success, "UTC")
    with cards[1]: metric_card("Rows inserted", f"{int(latest.rows_inserted):,}", "latest dataset run")
    with cards[2]: metric_card("Duplicates skipped", f"{int(latest.rows_skipped):,}", "idempotency signal")
    with cards[3]: metric_card("Duration", f"{float(latest.duration_ms):.0f} ms", str(latest.status))
    st.caption("Scheduler cadence · 每小时；当前为按需启动的前台服务，不会由开发命令永久驻留。")
    left, right = st.columns([1.25, 1])
    with left:
        st.subheader("最近 10 次 collection runs")
        st.dataframe(runs.head(10), use_container_width=True, hide_index=True)
    with right:
        st.subheader("Latest watermarks")
        st.dataframe(watermarks, use_container_width=True, hide_index=True)


def about_page() -> None:
    st.subheader("从公共 API 到可查询分析层")
    st.write("平台把多城市天气和空气质量数据转换为可重复、可监控的数据管道。所有时间统一为 UTC，同时保留原城市时区；Dashboard 只查询 Clean / Analytics 层。")
    st.code("Open-Meteo → Raw JSON → Normalize → Parquet → DuckDB → Analytics → Streamlit", language=None)
    st.info("AQI 使用 Open-Meteo 返回的 European AQI 定义。相关性和异常标记用于数据探索，不构成因果结论或健康建议。")


def main() -> None:
    inject_style()
    data = load_environment(str(DATABASE))
    runs, watermarks, quality = load_pipeline(str(DATABASE))
    requested = st.query_params.get("page", "Overview")
    if requested not in NAVIGATION:
        requested = "Overview"
    with st.sidebar:
        st.markdown("### ◌ Urban Environment")
        st.caption("Analytics workspace")
        page = st.radio(
            "导航",
            list(NAVIGATION),
            index=list(NAVIGATION).index(requested),
            format_func=NAVIGATION.get,
            label_visibility="collapsed",
        )
        st.divider()
        st.caption("DATA LAYERS")
        st.markdown("**RAW** · JSON  \n**CLEAN** · Parquet  \n**ANALYTICS** · DuckDB")
    header(runs)
    if data.empty and page not in {"Pipeline Monitor", "Data Quality", "About"}:
        st.markdown("<div class='empty'>分析层尚无数据。请运行 <code>python -m urban_environment.pipeline collect --all-cities</code>。</div>", unsafe_allow_html=True)
        return
    {
        "Overview": lambda: overview(data, runs),
        "City Analysis": lambda: city_analysis_page(data),
        "City Comparison": lambda: comparison_page(data),
        "Data Quality": lambda: quality_page(quality),
        "Pipeline Monitor": lambda: pipeline_page(runs, watermarks),
        "About": about_page,
    }[page]()


if __name__ == "__main__":
    main()
