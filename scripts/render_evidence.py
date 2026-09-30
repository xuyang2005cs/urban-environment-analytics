"""Render live probe summaries as local HTML for reproducible screenshots."""

from __future__ import annotations

import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "output" / "evidence"
PAGES = ROOT / "output" / "playwright"


STYLE = """
body { margin: 0; background: #0b1220; color: #dbeafe; font: 18px/1.55 Consolas, monospace; }
main { width: 1120px; margin: 0 auto; padding: 54px 58px 64px; box-sizing: border-box; }
h1 { margin: 0 0 8px; color: #f8fafc; font: 700 30px/1.2 system-ui, sans-serif; }
.subtitle { margin-bottom: 28px; color: #7dd3fc; font-family: system-ui, sans-serif; }
.terminal { border: 1px solid #334155; border-radius: 14px; overflow: hidden; box-shadow: 0 20px 55px #02061788; }
.bar { background: #1e293b; padding: 12px 18px; color: #94a3b8; }
.content { padding: 24px 28px 30px; background: #0f172a; }
.line { display: grid; grid-template-columns: 260px 1fr; gap: 24px; padding: 4px 0; }
.key { color: #93c5fd; } .pass { color: #4ade80; font-weight: 700; } .warn { color: #fbbf24; }
table { width: 100%; border-collapse: collapse; margin-top: 14px; font-size: 16px; }
th, td { text-align: left; border-bottom: 1px solid #263449; padding: 11px 10px; }
th { color: #93c5fd; font-weight: 600; } td:last-child { color: #4ade80; font-weight: 700; }
.foot { margin-top: 22px; color: #64748b; font: 14px system-ui, sans-serif; }
"""


def esc(value: object) -> str:
    return html.escape(str(value))


def page(title: str, subtitle: str, body: str) -> str:
    return (
        "<!doctype html><html><head><meta charset='utf-8'><title>"
        + esc(title)
        + f"</title><style>{STYLE}</style></head><body><main><h1>{esc(title)}</h1>"
        + f"<div class='subtitle'>{esc(subtitle)}</div><section class='terminal'>"
        + "<div class='bar'>● ● ● &nbsp; verified local run</div><div class='content'>"
        + body
        + "<div class='foot'>Source: live Open-Meteo requests; rendered from output/evidence JSON.</div>"
        + "</div></section></main></body></html>"
    )


def render_probe(summary: dict[str, object]) -> str:
    rows = [
        ("CITY", summary["city"]),
        ("WINDOW", f"{summary['window']['start_date']} .. {summary['window']['end_date']}"),
        ("GEOCODING", summary["geo"]),
        ("WEATHER", f"{summary['weather']} · {summary['weather_rows']} rows"),
        ("AIR_QUALITY", f"{summary['air_quality']} · {summary['air_quality_rows']} rows"),
        ("MERGE_PROBE", f"{summary['merged_rows']} aligned rows"),
        ("TIMEZONE", summary["timezone"]),
        ("RESULT", summary["result"]),
    ]
    body = "".join(
        f"<div class='line'><span class='key'>{esc(key)}</span>"
        f"<span class='{'pass' if 'PASS' in str(value) else ''}'>{esc(value)}</span></div>"
        for key, value in rows
    )
    return page("Open-Meteo Live Probe", "Beijing · geocoding + weather + air quality", body)


def render_collection(summary: dict[str, object]) -> str:
    table_rows = "".join(
        "<tr>"
        f"<td>{esc(item['city'])}</td><td>{esc(item['weather_rows'])}</td>"
        f"<td>{esc(item['air_quality_rows'])}</td><td>{esc(item['merged_rows'])}</td>"
        f"<td>{esc(item['status'])}</td></tr>"
        for item in summary["cities"]
    )
    body = (
        f"<div class='line'><span class='key'>WINDOW</span><span>"
        f"{esc(summary['window']['start_date'])} .. {esc(summary['window']['end_date'])}</span></div>"
        f"<div class='line'><span class='key'>SUCCESSFUL_CITIES</span><span class='pass'>"
        f"{esc(summary['successful_cities'])} / {len(summary['cities'])}</span></div>"
        "<table><thead><tr><th>City</th><th>Weather</th><th>Air quality</th>"
        f"<th>Merged</th><th>Status</th></tr></thead><tbody>{table_rows}</tbody></table>"
        f"<div class='line' style='margin-top:16px'><span class='key'>RESULT</span>"
        f"<span class='pass'>{esc(summary['result'])}</span></div>"
    )
    return page("Initial Multi-City Collection", "Six cities · real 7-day hourly window", body)


def main() -> None:
    PAGES.mkdir(parents=True, exist_ok=True)
    probe = json.loads((EVIDENCE / "probe_summary.json").read_text(encoding="utf-8"))
    collection = json.loads(
        (EVIDENCE / "collection_summary.json").read_text(encoding="utf-8")
    )
    (PAGES / "open-meteo-probe.html").write_text(render_probe(probe), encoding="utf-8")
    (PAGES / "collection-summary.html").write_text(
        render_collection(collection), encoding="utf-8"
    )
    print(f"EVIDENCE_PAGES={PAGES}")


if __name__ == "__main__":
    main()
