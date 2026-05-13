import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from .dashboard_utils import _find_col

def dashboard_portfolio(
    df: pd.DataFrame, 
    classify_result: dict, 
    indicator_result: dict, 
    theme: str = "light"
) -> None:
    """Static(포트폴리오) 데이터를 위한 메인 차트 렌더링."""
    dim = classify_result.get("dimension", "1D")
    st.markdown(f"### 포트폴리오 성과 분석 ({dim})")

    st.markdown('<div class="sq-card sq-chart">', unsafe_allow_html=True)
    if dim == "1D":
        st.plotly_chart(_fig_portfolio_1d(df, theme=theme), use_container_width=True)
    elif dim == "2D":
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(_fig_portfolio_2d_dual(df, theme=theme), use_container_width=True)
        with col2:
            st.plotly_chart(_fig_portfolio_2d_metrics(df, theme=theme), use_container_width=True)
    elif dim == "ND":
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(_fig_portfolio_nd_donut(df, theme=theme), use_container_width=True)
        with col2:
            st.plotly_chart(_fig_portfolio_nd_bar(df, theme=theme), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
            
    st.markdown("---")
    with st.expander("포트폴리오 데이터 상세"):
        st.dataframe(df, use_container_width=True)

def _fig_portfolio_1d(df: pd.DataFrame, theme: str = "light") -> go.Figure:
    """Static 1D: 누적 수익률."""
    # 간단한 라인 차트 구현 (예시)
    fig = px.line(df, x=df.columns[0], y=df.columns[1], title="누적 수익률 추이")
    return fig

def _fig_portfolio_2d_dual(df: pd.DataFrame, theme: str = "light") -> go.Figure:
    """Static 2D: 포트 vs 벤치마크."""
    fig = go.Figure()
    # 2D 로직
    return fig

def _fig_portfolio_2d_metrics(df: pd.DataFrame, theme: str = "light") -> go.Figure:
    """Static 2D: 비중 괴리율."""
    fig = go.Figure()
    return fig

def _fig_portfolio_nd_donut(df: pd.DataFrame, theme: str = "light") -> go.Figure:
    """Static ND: 자산 구성 도넛."""
    fig = go.Figure()
    return fig

def _fig_portfolio_nd_bar(df: pd.DataFrame, theme: str = "light") -> go.Figure:
    """Static ND: 리스크 기여도."""
    fig = go.Figure()
    return fig
