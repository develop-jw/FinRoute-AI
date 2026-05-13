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
    """Static(포트폴리오) 데이터를 위한 차원별 차트 렌더링."""
    dim = classify_result.get("dimension", "1D")
    st.markdown(f"### 포트폴리오 성과 분석 ({dim})")

    st.markdown('<div class="sq-card sq-chart">', unsafe_allow_html=True)
    
    if dim == "1D":
        st.plotly_chart(_fig_portfolio_1d_main(df, theme), use_container_width=True, key="pf_1d_main")
        st.plotly_chart(_fig_portfolio_1d_sub(df, theme), use_container_width=True, key="pf_1d_sub")
    elif dim == "2D":
        st.plotly_chart(_fig_portfolio_2d_main(df, theme), use_container_width=True, key="pf_2d_main")
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(_fig_portfolio_2d_sub1(df, theme), use_container_width=True, key="pf_2d_sub1")
        with col2:
            st.plotly_chart(_fig_portfolio_2d_sub2(df, theme), use_container_width=True, key="pf_2d_sub2")
    elif dim == "ND":
        st.plotly_chart(_fig_portfolio_nd_main(df, theme), use_container_width=True, key="pf_nd_main")
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(_fig_portfolio_nd_sub1(df, theme), use_container_width=True, key="pf_nd_sub1")
        with col2:
            st.plotly_chart(_fig_portfolio_nd_sub2(df, theme), use_container_width=True, key="pf_nd_sub2")
            
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("---")
    with st.expander("포트폴리오 데이터 상세"):
        st.dataframe(df, use_container_width=True)

# --- 유틸리티: 컬럼 자동 추론 ---
def _auto_fig(df, title, x_cands, y_cands, plot_type="line"):
    dc = _find_col(df, *x_cands) or df.columns[0]
    yc = _find_col(df, *y_cands) or (df.columns[1] if len(df.columns) > 1 else df.columns[0])
    if plot_type == "line": return px.line(df, x=dc, y=yc, title=title)
    if plot_type == "bar": return px.bar(df, x=dc, y=yc, title=title)
    if plot_type == "area": return px.area(df, x=dc, y=yc, color=df.columns[1], title=title)
    return go.Figure()

# --- 1D 로직 (Quarter별 return 누적) ---
def _fig_portfolio_1d_main(df, theme):
    # 누적 수익률 계산
    df = df.sort_values("quarter")
    df['cum_ret'] = (1 + df['return']).cumprod() - 1
    return px.line(df, x="quarter", y="cum_ret", title="분기별 누적 수익률")

def _fig_portfolio_1d_sub(df, theme):
    return px.bar(df, x="asset_name", y="return", title="분기별 자산 수익률")

# --- 2D 로직 ---
def _fig_portfolio_2d_main(df, theme):
    # 2개 종목 비교 (데이터 피벗)
    pivot = df.pivot(index="quarter", columns="asset_name", values="return").cumsum()
    fig = px.line(pivot, title="자산별 누적 수익률 비교")
    return fig

def _fig_portfolio_2d_sub1(df, theme):
    # 2D Bar
    return px.bar(df, x="quarter", y="return", color="asset_name", barmode="group", title="분기별 자산 수익률 비교")

def _fig_portfolio_2d_sub2(df, theme):
    # 비중 괴리율 (마지막 분기 기준)
    last_q = df["quarter"].iloc[-1]
    last_df = df[df["quarter"] == last_q]
    return px.bar(last_df, x="asset_name", y="weight", title=f"최신 분기 비중 ({last_q})")

# --- ND 로직 ---
def _fig_portfolio_nd_main(df, theme):
    last_q = df["quarter"].iloc[-1]
    last_df = df[df["quarter"] == last_q]
    return px.pie(last_df, values="weight", names="asset_name", hole=0.4, title=f"자산 구성 ({last_q})")

def _fig_portfolio_nd_sub1(df, theme):
    return px.bar(df, x="asset_name", y="weight", title="자산별 평균 비중")

def _fig_portfolio_nd_sub2(df, theme):
    # 비중 추이 (Stacked Area)
    pivot = df.pivot(index="quarter", columns="asset_name", values="weight").fillna(0)
    fig = px.area(pivot, title="분기별 자산 비중 추이")
    return fig
