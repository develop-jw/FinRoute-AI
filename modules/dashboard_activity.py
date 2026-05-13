import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from .dashboard_utils import _find_col

def dashboard_activity(
    df: pd.DataFrame, 
    classify_result: dict, 
    indicator_result: dict, 
    theme: str = "light"
) -> None:
    """Activity(매매 활동) 데이터를 위한 차트 렌더링 (03_visualization.md 준수)."""
    dim = classify_result.get("dimension", "1D")
    
    # 공통 컬럼 매핑 (유연성 확보)
    tc = _find_col(df, "ticker", "symbol", "code", "asset")
    ts = _find_col(df, "timestamp", "date", "time")
    pc = _find_col(df, "price", "execution_price")
    qc = _find_col(df, "quantity", "qty", "amount")
    bs = _find_col(df, "buy/sell", "side")
    vc = _find_col(df, "vwap", "avg_price")
    
    st.markdown(f"### 매매 활동 분석 ({dim})")

    # [1D] VWAP 대비 단가 Bar Chart
    if dim == "1D":
        if tc and pc and vc:
            # VWAP 대비 단가 차이 계산
            df['diff'] = pd.to_numeric(df[pc]) - pd.to_numeric(df[vc])
            fig = px.bar(df, x=tc, y='diff', color=np.where(df['diff'] >= 0, 'red', 'green'),
                         title="실행 단가 vs VWAP (매매 효율성)")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("1D 분석을 위한 Ticker, Price, VWAP 컬럼이 필요합니다.")

    # [2D] 자산 교체 비교 Dual Line
    elif dim == "2D":
        if tc and ts and pc:
            fig = go.Figure()
            for t in df[tc].unique():
                sub = df[df[tc] == t].sort_values(ts)
                fig.add_trace(go.Scatter(x=sub[ts], y=sub[pc], name=str(t), mode='lines+markers'))
            fig.update_layout(title="자산 교체/매매 비교", xaxis_title="시간", yaxis_title="가격")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("2D 분석을 위한 Ticker, Timestamp, Price 컬럼이 필요합니다.")

    # [ND] 회전율 Bar
    elif dim == "ND":
        if tc and qc:
            df['qty_num'] = pd.to_numeric(df[qc])
            turnover = df.groupby(tc)['qty_num'].sum().reset_index()
            fig = px.bar(turnover, x=tc, y='qty_num', title="종목별 회전율 (총 거래량)")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("ND 분석을 위한 Ticker, Quantity 컬럼이 필요합니다.")
            
    st.markdown("---")
    with st.expander("거래 데이터 상세"):
        st.dataframe(df)
