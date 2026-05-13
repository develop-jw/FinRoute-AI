import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from streamlit_lightweight_charts import renderLightweightCharts
from .dashboard_utils import (
    _find_col, _fig_vwap_bar, _fig_activity_dual_line, _fig_turnover_bar, _ticker_to_name
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
        _render_activity_lightweight(df.copy(), theme=theme, key="1d_chart")
    elif dim == "2D":
        tc = _find_col(df, "ticker", "symbol", "code", "asset")
        if tc:
            # 티커와 회사명을 매핑하여 선택 리스트 생성
            ticker_list = sorted(df[tc].unique())
            ticker_name_map = { _ticker_to_name(str(t)): t for t in ticker_list }
            
            selected_names = st.multiselect("종목 선택 (최대 2개)", list(ticker_name_map.keys()), default=list(ticker_name_map.keys())[:2])
            selected_tickers = [ticker_name_map[name] for name in selected_names]
            
            if len(selected_tickers) == 1:
                sub_df = df[df[tc] == selected_tickers[0]].copy()
                _render_activity_lightweight(sub_df, theme=theme, key=f"2d_{selected_tickers[0]}")
            elif len(selected_tickers) == 2:
                st.plotly_chart(_fig_activity_dual_line(df[df[tc].isin(selected_tickers)], theme=theme), use_container_width=True)
            else:
                st.info("종목을 1개 또는 2개 선택해주세요.")
        else:
            st.plotly_chart(_fig_activity_dual_line(df, theme=theme), use_container_width=True)
    elif dim == "ND":
        tc = _find_col(df, "ticker", "symbol", "code", "asset")
        if tc:
            ticker_list = sorted(df[tc].unique())
            ticker_name_map = { _ticker_to_name(str(t)): t for t in ticker_list }
            
            selected_names = st.multiselect("종목 선택", list(ticker_name_map.keys()), default=list(ticker_name_map.keys()))
            selected_tickers = [ticker_name_map[name] for name in selected_names]
            
            for t in selected_tickers:
                st.markdown(f"**{_ticker_to_name(str(t))}**")
                sub_df = df[df[tc] == t].copy()
                _render_activity_lightweight(sub_df, theme=theme, key=f"nd_{t}")
        else:
            st.plotly_chart(_fig_turnover_bar(df, theme=theme), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    with st.expander("거래 데이터 상세"):
        st.dataframe(df, use_container_width=True)

def _render_activity_lightweight(df: pd.DataFrame, theme: str = "light", key: str = "activity_chart"):
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
    w['open'] = np.where(w['is_buy'], w['close'] * 0.998, w['close'] * 1.002)
    w['high'] = w[['open', 'close']].max(axis=1) * 1.0005
    w['low'] = w[['open', 'close']].min(axis=1) * 0.9995

    is_dark = (theme == "dark")
    bg_color = "#1e252e" if is_dark else "#ffffff"
    text_color = "#f0f7f5" if is_dark else "#333333"
    grid_color = "#313d4a" if is_dark else "#eeeeee"

    chart_data = w.rename(columns={'date':'time', 'open':'open', 'high':'high', 'low':'low', 'close':'close'})
    
    # VWAP 데이터 이름 바꾸기 (컬럼이 존재할 때만)
    if vc and vc in w.columns:
        vwap_data = w.rename(columns={'date':'time', vc:'value'})
    else:
        vwap_data = w.rename(columns={'date':'time'})
        vwap_data['value'] = 0

    price_chart_options = {
        "layout": {"background": {"color": bg_color}, "textColor": text_color},
        "grid": {"vertLines": {"color": grid_color}, "horzLines": {"color": grid_color}},
        "height": 400,
    }

    series = [
        {"type": 'Candlestick', "data": chart_data[['time', 'open', 'high', 'low', 'close']].to_dict('records'), 
         "options": {"upColor": "#2ed573", "downColor": "#e74c3c", "borderDownColor": "#e74c3c", "borderUpColor": "#2ed573", "wickDownColor": "#e74c3c", "wickUpColor": "#2ed573"}}
    ]
    
    # VWAP 데이터가 있을 때만 선 추가
    if vc and vc in w.columns:
        series.append({"type": 'Line', "data": vwap_data[['time', 'value']].to_dict('records'), 
                       "options": {"color": "#f1c40f", "lineWidth": 2, "lineStyle": 2, "title": "VWAP"}})

    renderLightweightCharts([{"chart": price_chart_options, "series": series}], key)
