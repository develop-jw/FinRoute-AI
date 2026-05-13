import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from streamlit_lightweight_charts import renderLightweightCharts
from .dashboard_utils import (
    _find_col, _fig_vwap_bar, _fig_activity_dual_line, _fig_turnover_bar
)

def dashboard_activity(
    df: pd.DataFrame, 
    classify_result: dict, 
    indicator_result: dict, 
    theme: str = "light"
) -> None:
    """Activity(매매 활동) 데이터를 위한 메인 차트 렌더링."""
    dim = classify_result.get("dimension", "1D")
    st.markdown(f"### 매매 활동 분석 ({dim})")

    st.markdown('<div class="sq-card sq-chart">', unsafe_allow_html=True)
    if dim == "1D":
        # LightWeightCharts 스타일로 1D Activity 차트 렌더링
        # _render_lightweight_chart 사용을 위해 데이터를 포맷팅
        df_chart = df.copy()
        # 데이터프레임 컬럼을 맞춤 (date, close, vwap, side 등)
        _render_activity_lightweight(df_chart, theme=theme)
    elif dim == "2D":
        st.plotly_chart(_fig_activity_dual_line(df, theme=theme), use_container_width=True)
    elif dim == "ND":
        st.plotly_chart(_fig_turnover_bar(df, theme=theme), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    with st.expander("거래 데이터 상세"):
        st.dataframe(df, use_container_width=True)

def _render_activity_lightweight(df: pd.DataFrame, theme: str = "light"):
    """LightWeightCharts를 활용한 Activity 1D 차트 렌더링."""
    dc = _find_col(df, "date", "datetime", "timestamp")
    pc = _find_col(df, "price", "execution_price")
    vc = _find_col(df, "vwap", "avg_price")
    bc = _find_col(df, "side", "buy/sell")

    # 캔들형 표현을 위해 데이터 생성
    w = df.copy()
    w['date'] = pd.to_datetime(w[dc]).dt.strftime('%Y-%m-%d')
    w['is_buy'] = w[bc].apply(lambda x: str(x).lower().startswith('b'))
    w['close'] = pd.to_numeric(w[pc])
    w['open'] = np.where(w['is_buy'], w['close'] * 0.9995, w['close'] * 1.0005)
    w['high'] = w[['open', 'close']].max(axis=1) * 1.0002
    w['low'] = w[['open', 'close']].min(axis=1) * 0.9998

    is_dark = (theme == "dark")
    bg_color = "#1e252e" if is_dark else "#ffffff"
    text_color = "#f0f7f5" if is_dark else "#333333"
    grid_color = "#313d4a" if is_dark else "#eeeeee"

    chart_data = w.rename(columns={'date':'time', 'open':'open', 'high':'high', 'low':'low', 'close':'close'})
    vwap_data = w.rename(columns={'date':'time', vc:'value'})

    price_chart_options = {
        "layout": {"background": {"color": bg_color}, "textColor": text_color},
        "grid": {"vertLines": {"color": grid_color}, "horzLines": {"color": grid_color}},
        "height": 400,
    }

    series = [
        {"type": 'Candlestick', "data": chart_data[['time', 'open', 'high', 'low', 'close']].to_dict('records'), 
         "options": {"upColor": "#2ed573", "downColor": "#e74c3c", "borderDownColor": "#e74c3c", "borderUpColor": "#2ed573", "wickDownColor": "#e74c3c", "wickUpColor": "#2ed573"}},
        {"type": 'Line', "data": vwap_data[['time', 'value']].to_dict('records'), 
         "options": {"color": "#f1c40f", "lineWidth": 2, "lineStyle": 2, "title": "VWAP"}}
    ]

    renderLightweightCharts([{"chart": price_chart_options, "series": series}], 'activity_chart')
