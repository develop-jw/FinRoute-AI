import streamlit as st
import pandas as pd
from .dashboard_utils import _find_col, _ticker_to_name, _render_lightweight_chart, _fig_corr_heatmap

def dashboard_timeseries(
    df: pd.DataFrame, 
    classify_result: dict, 
    indicator_result: dict, 
    theme: str = "light"
) -> None:
    """TimeSeries 데이터를 위한 차트 렌더링."""
    dim = classify_result.get("dimension", "1D")
    is_1d = (dim == "1D")
    tick_col = _find_col(df, "ticker", "symbol", "code", "asset", "asset_name")
    
    display_df = df
    selected = []
    
    if tick_col and dim in ("2D", "ND"):
        all_tickers = sorted(df[tick_col].unique())
        def _fmt(t):
            name = _ticker_to_name(t)
            return f"{name} ({t})" if name != str(t) else str(t)

        selected = st.multiselect(
            "비교할 종목 선택", 
            all_tickers, 
            default=all_tickers, 
            key="selected_tickers",
            format_func=_fmt
        )
        display_df = df[df[tick_col].isin(selected)]
    
    show_indicator_ui = is_1d or (len(selected) == 1)
    
    if show_indicator_ui:
        st.markdown("### 기술 지표 설정")
        c1, c2, c3, c4 = st.columns(4)
        with c1: 
            st.multiselect("이동평균선 (MA)", [5, 20, 60, 120], default=[], key="ma_periods")
            st.checkbox("볼린저 밴드 (BB)", key="show_bb", value=False)
        with c2: 
            st.checkbox("일목균형표", key="show_ichimoku", value=False)
            st.checkbox("파라볼릭 SAR", key="show_psar", value=False)
        with c3:
            st.checkbox("스토캐스틱 ", key="show_stoch", value=False)
            st.checkbox("CCI", key="show_cci", value=False)
        with c4:
            st.checkbox("엔벨로프", key="show_env", value=False)
            st.checkbox("OBV", key="show_obv", value=False)
        st.checkbox("MACD", key="show_macd", value=False)

    st.markdown('<div class="sq-card sq-chart">', unsafe_allow_html=True)
    _render_lightweight_chart(display_df, theme=theme,
        show_ma=st.session_state.get("ma_periods", []) if show_indicator_ui else None,
        show_bb=st.session_state.show_bb if show_indicator_ui else False,
        show_ichimoku=st.session_state.show_ichimoku if show_indicator_ui else False,
        show_vol=True)
    
    if dim == "ND":
        st.markdown('<div style="margin-top:20px; border-top:1px solid var(--sq-border); padding-top:20px;"></div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size:0.85rem; font-weight:700; color:var(--sq-muted); text-transform:uppercase; letter-spacing:0.08em; margin-bottom:12px;">Correlation Matrix</div>', unsafe_allow_html=True)
        st.plotly_chart(_fig_corr_heatmap(df, theme=theme), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
