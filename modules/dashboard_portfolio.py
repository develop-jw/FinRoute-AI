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
        if "return" in df.columns:
            st.plotly_chart(_fig_portfolio_1d_main(df, theme), use_container_width=True, key="pf_1d_main")
            st.plotly_chart(_fig_portfolio_1d_sub(df, theme), use_container_width=True, key="pf_1d_sub")
        else:
            st.info("1D 분석을 위한 수익률(return) 데이터가 없습니다.")
    elif dim == "2D":
        has_ret = "return" in df.columns and not df["return"].dropna().empty
        if has_ret:
            st.plotly_chart(_fig_portfolio_2d_main(df, theme), use_container_width=True, key="pf_2d_main")
            st.plotly_chart(_fig_portfolio_2d_sub2(df, theme), use_container_width=True, key="pf_2d_sub2")
        else:
            st.info("2D 비교 분석을 위한 수익률 데이터가 부족합니다.")
    elif dim == "ND":
        if "weight" in df.columns:
            st.plotly_chart(_fig_portfolio_nd_main(df, theme), use_container_width=True, key="pf_nd_main")
            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(_fig_portfolio_nd_sub1(df, theme), use_container_width=True, key="pf_nd_sub1")
            with col2:
                st.plotly_chart(_fig_portfolio_nd_sub2(df, theme), use_container_width=True, key="pf_nd_sub2")
        else:
            st.info("ND 자산 구성 분석을 위한 데이터가 부족합니다.")
            
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("---")
    with st.expander("포트폴리오 데이터 상세"):
        st.dataframe(df, use_container_width=True)

# 테마에 따른 스타일 설정
def _get_theme_styles(theme):
    is_dark = (theme == "dark")
    return {
        "bg": "#1e252e" if is_dark else "#fafbfb",
        "txt": "#f0f7f5" if is_dark else "#1a2d30",
        "grd": "#313d4a" if is_dark else "#dde3e8",
        "colors": ["#0a5c5c", "#1dd1a1", "#2ed573", "#ff4757", "#f1c40f"]
    }

def _apply_layout(fig, title, theme):
    s = _get_theme_styles(theme)
    fig.update_layout(
        title=dict(text=title, font=dict(size=14, weight='bold')),
        margin=dict(l=40, r=20, t=50, b=30),
        paper_bgcolor=s["bg"],
        plot_bgcolor=s["bg"],
        font=dict(family="DM Sans, sans-serif", color=s["txt"]),
        xaxis=dict(gridcolor=s["grd"], showgrid=True),
        yaxis=dict(gridcolor=s["grd"], showgrid=True),
        hovermode="x unified"
    )
    return fig

# --- 1D ---
def _fig_portfolio_1d_main(df, theme):
    df = df.sort_values("quarter")
    df['cum_ret'] = (1 + df['return']).cumprod() - 1
    fig = go.Figure(go.Scatter(x=df["quarter"], y=df['cum_ret'], mode='lines', line=dict(color="#0a5c5c", width=3)))
    return _apply_layout(fig, "누적 수익률", theme)

def _fig_portfolio_1d_sub(df, theme):
    fig = go.Figure(go.Bar(x=df["asset_name"], y=df["return"], marker_color="#1dd1a1"))
    return _apply_layout(fig, "자산별 수익 기여도", theme)

# --- 2D ---
def _fig_portfolio_2d_main(df, theme):
    pivot = df.pivot(index="quarter", columns="asset_name", values="return").cumsum()
    fig = go.Figure()
    s = _get_theme_styles(theme)
    for i, col in enumerate(pivot.columns):
        fig.add_trace(go.Scatter(x=pivot.index, y=pivot[col], mode='lines', name=col, line=dict(color=s["colors"][i%len(s["colors"])], width=2.5)))
    return _apply_layout(fig, "자산별 누적 수익률 비교", theme)

def _fig_portfolio_2d_sub2(df, theme):
    last_q = df["quarter"].iloc[-1]
    last_df = df[df["quarter"] == last_q]
    fig = go.Figure(go.Bar(x=last_df["asset_name"], y=last_df["weight"], marker_color="#0a5c5c"))
    return _apply_layout(fig, f"최신 분기 비중 ({last_q})", theme)

# --- ND ---
def _fig_portfolio_nd_main(df, theme):
    last_q = df["quarter"].iloc[-1]
    last_df = df[df["quarter"] == last_q]
    fig = go.Figure(go.Pie(labels=last_df["asset_name"], values=last_df["weight"], hole=0.4, marker_colors=_get_theme_styles(theme)["colors"]))
    return _apply_layout(fig, f"자산 구성 ({last_q})", theme)

def _fig_portfolio_nd_sub1(df, theme):
    fig = go.Figure(go.Bar(x=df["asset_name"], y=df["weight"], marker_color="#1dd1a1"))
    return _apply_layout(fig, "자산별 평균 비중", theme)

def _fig_portfolio_nd_sub2(df, theme):
    pivot = df.pivot(index="quarter", columns="asset_name", values="weight").fillna(0)
    fig = go.Figure()
    s = _get_theme_styles(theme)
    for i, col in enumerate(pivot.columns):
        fig.add_trace(go.Scatter(x=pivot.index, y=pivot[col], stackgroup='one', name=col, line=dict(width=0), fillcolor=s["colors"][i%len(s["colors"])]))
    return _apply_layout(fig, "분기별 자산 비중 추이", theme)
