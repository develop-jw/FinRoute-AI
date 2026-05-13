import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
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
        st.plotly_chart(_fig_vwap_bar(df, theme=theme), use_container_width=True)
    elif dim == "2D":
        st.plotly_chart(_fig_activity_dual_line(df, theme=theme), use_container_width=True)
    elif dim == "ND":
        st.plotly_chart(_fig_turnover_bar(df, theme=theme), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
            
    st.markdown("---")
    with st.expander("거래 데이터 상세"):
        st.dataframe(df, use_container_width=True)
