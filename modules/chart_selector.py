"""03_visualization: class × dimension → 차트 식별자."""

from __future__ import annotations

from typing import Any


def select_chart(classify_result: dict) -> dict[str, Any]:
    ct = classify_result["class_type"]
    dim = classify_result["dimension"]

    if ct == "TimeSeries":
        if dim == "1D":
            return {"main_chart": "candlestick", "sub_charts": ["rsi"]}
        if dim == "2D":
            return {"main_chart": "dual_line", "sub_charts": ["zscore", "rolling_corr"]}
        return {"main_chart": "heatmap", "sub_charts": ["network"]}

    if ct == "Static":
        if dim == "1D":
            return {"main_chart": "line", "sub_charts": ["grouped_bar"]}
        if dim == "2D":
            return {
                "main_chart": "dual_line",
                "sub_charts": ["excess_bar", "weight_drift_bar"],
            }
        return {"main_chart": "donut", "sub_charts": ["risk_bar", "stacked_area"]}

    # Activity
    if dim == "1D":
        return {"main_chart": "vwap_bar", "sub_charts": ["scatter_pf"]}
    if dim == "2D":
        return {"main_chart": "dual_line", "sub_charts": ["switch_bar"]}
    return {"main_chart": "turnover_bar", "sub_charts": ["timeline"]}
