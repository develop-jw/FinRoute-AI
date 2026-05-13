import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from streamlit_lightweight_charts import renderLightweightCharts

_TICKER_COLORS: dict[str, str] = {
    "005930": "#1dd1a1",
    "000660": "#ffa502",
}
_DEFAULT_COLORS = ["#2ed573", "#1e90ff", "#ff4757", "#ffa502", "#3742fa", "#70a1ff", "#5352ed", "#2f3542"]

_TICKER_NAME: dict[str, str] = {
    "005930": "삼성전자", "000660": "SK하이닉스", "035420": "NAVER", "005380": "현대차", "051910": "LG화학",
    "000270": "기아", "068270": "셀트리온", "207940": "삼성바이오로직스", "006400": "삼성SDI", "035720": "카카오",
    "003550": "LG", "028260": "삼성물산", "066570": "LG전자", "096770": "SK이노베이션", "017670": "SK텔레콤",
    "030200": "KT", "055550": "신한지주", "105560": "KB금융", "086790": "하나금융지주", "316140": "우리금융지주",
    "032830": "삼성생명", "003490": "대한항공", "011200": "HMM", "009150": "삼성전기", "012330": "현대모비스",
}

def _ticker_to_name(ticker: str) -> str:
    key = str(ticker).zfill(6) if str(ticker).isdigit() and len(str(ticker)) < 6 else str(ticker)
    return _TICKER_NAME.get(key, key)

def _find_col(df: pd.DataFrame, *cands: str) -> str | None:
    lower = {str(c).lower().replace(" ", "_"): c for c in df.columns}
    for cand in cands:
        k = cand.lower()
        if k in lower:
            return lower[k]
        for lk, orig in lower.items():
            if k in lk:
                return orig
    return None

def _render_lightweight_chart(
    df: pd.DataFrame, 
    theme: str = "light", 
    show_ma: list[int] | None = None, 
    show_bb: bool = False, 
    show_ichimoku: bool = False,
    show_vol: bool = True
) -> None:
    dc = _find_col(df, "date", "datetime")
    oc, hc, lc, cc = _find_col(df, "open"), _find_col(df, "high"), _find_col(df, "low"), _find_col(df, "close")
    vc = _find_col(df, "volume")
    tick_col = _find_col(df, "ticker", "symbol", "code", "asset", "asset_name")
    
    is_dark = (theme == "dark")
    bg_color = "#1e252e" if is_dark else "#ffffff"
    text_color = "#f0f7f5" if is_dark else "#333333"
    grid_color = "#313d4a" if is_dark else "#eeeeee"

    price_chart_options = {
        "layout": {"background": {"color": bg_color}, "textColor": text_color},
        "grid": {"vertLines": {"color": grid_color}, "horzLines": {"color": grid_color}},
        "crosshair": {"mode": 0},
        "height": 400,
        "rightPriceScale": {"visible": True, "borderColor": "#cccccc", "scaleMargins": {"top": 0.1, "bottom": 0.1}}
    }
    
    volume_chart_options = {
        "layout": {"background": {"color": bg_color}, "textColor": text_color},
        "grid": {"vertLines": {"color": grid_color}, "horzLines": {"color": grid_color}},
        "crosshair": {"mode": 0},
        "height": 150,
        "rightPriceScale": {"visible": True, "borderColor": "#cccccc", "scaleMargins": {"top": 0.1, "bottom": 0.1}}
    }

    price_series = []
    volume_series = []
    w = df.copy()
    w[dc] = pd.to_datetime(w[dc]).dt.strftime('%Y-%m-%d')
    tickers = [None]
    if tick_col and w[tick_col].nunique() > 1:
        tickers = sorted(w[tick_col].unique())
    ma_colors = {5: "#ff9f43", 20: "#2962ff", 60: "#1dd1a1", 120: "#ff4757"}
    
    for i, t in enumerate(tickers):
        sub = w[w[tick_col] == t] if t else w
        if sub.empty: continue
        t_name = _ticker_to_name(str(t)) if t else "가격"
        color = _TICKER_COLORS.get(str(t), _DEFAULT_COLORS[i % len(_DEFAULT_COLORS)]) if t else None
        chart_data = sub[[dc, oc, hc, lc, cc]].rename(columns={dc: 'time', oc: 'open', hc: 'high', lc: 'low', cc: 'close'})
        
        if len(tickers) > 1:
            line_data = sub[[dc, cc]].rename(columns={dc: 'time', cc: 'value'}).to_dict('records')
            price_series.append({"type": 'Line', "data": line_data, "options": {"color": color, "lineWidth": 2, "title": t_name}})
        else:
            price_series.append({"type": 'Candlestick', "data": chart_data.to_dict('records'), "options": {"upColor": "#2ed573", "downColor": "#e74c3c", "borderDownColor": "#e74c3c", "borderUpColor": "#2ed573", "wickDownColor": "#e74c3c", "wickUpColor": "#2ed573"}})

        if (len(tickers) == 1 or i == 0):
            if show_ma:
                for period in show_ma:
                    if len(sub) >= period:
                        sub[f'ma{period}'] = pd.to_numeric(sub[cc], errors="coerce").rolling(period).mean()
                        ma_data = sub[[dc, f'ma{period}']].dropna().rename(columns={dc: 'time', f'ma{period}': 'value'}).to_dict('records')
                        price_series.append({"type": 'Line', "data": ma_data, "options": {"color": ma_colors.get(period, "#888888"), "lineWidth": 1.5, "title": f"MA{period}"}})
            if show_bb and len(sub) >= 20:
                ma = pd.to_numeric(sub[cc], errors="coerce").rolling(20).mean()
                std = pd.to_numeric(sub[cc], errors="coerce").rolling(20).std()
                sub['bb_u'], sub['bb_l'] = ma + (std * 2), ma - (std * 2)
                bb_u = sub[[dc, 'bb_u']].dropna().rename(columns={dc: 'time', 'bb_u': 'value'}).to_dict('records')
                bb_l = sub[[dc, 'bb_l']].dropna().rename(columns={dc: 'time', 'bb_l': 'value'}).to_dict('records')
                price_series.append({"type": 'Line', "data": bb_u, "options": {"color": "rgba(255, 152, 0, 0.4)", "lineWidth": 1, "title": "BB Upper"}})
                price_series.append({"type": 'Line', "data": bb_l, "options": {"color": "rgba(255, 152, 0, 0.4)", "lineWidth": 1, "title": "BB Lower"}})
            if show_ichimoku and len(sub) >= 52:
                h = pd.to_numeric(sub[hc], errors="coerce")
                l = pd.to_numeric(sub[lc], errors="coerce")
                sub['tenkan'] = (h.rolling(9).max() + h.rolling(9).min()) / 2
                sub['kijun'] = (h.rolling(26).max() + h.rolling(26).min()) / 2
                sub['senkou_a'] = ((sub['tenkan'] + sub['kijun']) / 2).shift(26)
                sub['senkou_b'] = ((h.rolling(52).max() + l.rolling(52).min()) / 2).shift(26)
                for col in ['tenkan', 'kijun', 'senkou_a', 'senkou_b']:
                    price_series.append({"type": 'Line', "data": sub[[dc, col]].dropna().rename(columns={dc:'time', col:'value'}).to_dict('records'), "options": {"lineWidth": 1, "title": col.capitalize()}})
        if show_vol and vc:
            v_data = sub[[dc, vc]].rename(columns={dc: 'time', vc: 'value'}).to_dict('records')
            v_color = color if color else "#0a5c5c"
            if len(tickers) > 1 and v_color.startswith("#"):
                r, g, b = int(v_color[1:3],16), int(v_color[3:5],16), int(v_color[5:7],16)
                v_color = f"rgba({r}, {g}, {b}, 0.5)"
            volume_series.append({"type": 'Histogram', "data": v_data, "options": {"priceFormat": {"type": 'volume'}, "color": v_color, "title": t_name if t else ""}})
    charts = [{"chart": price_chart_options, "series": price_series}]
    if volume_series: charts.append({"chart": volume_chart_options, "series": volume_series})
    renderLightweightCharts(charts, 'chart')

def _fig_corr_heatmap(df: pd.DataFrame, theme: str = "light") -> go.Figure:
    is_dark = (theme == "dark")
    bg  = "#1e252e" if is_dark else "#fafbfb"
    txt = "#f0f7f5" if is_dark else "#1a2d30"
    ticker_c = _find_col(df, "ticker", "symbol", "code")
    date_c   = _find_col(df, "date", "datetime", "time")
    close_c  = _find_col(df, "close", "adj_close", "price")
    fig = go.Figure()
    if not (ticker_c and close_c):
        fig.add_annotation(text="Ticker/Close 컬럼이 필요합니다", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return fig
    ret_dict = {}
    for t in df[ticker_c].dropna().unique():
        sub = df[df[ticker_c] == t]
        if date_c: sub = sub.sort_values(date_c)
        c = pd.to_numeric(sub[close_c], errors="coerce").reset_index(drop=True)
        ret_dict[str(t)] = c.pct_change().dropna().reset_index(drop=True)
    ret_df = pd.DataFrame(ret_dict).dropna()
    corr_mat = ret_df.corr()
    str_labels = [_ticker_to_name(str(l)) for l in corr_mat.columns]
    fig.add_trace(go.Heatmap(z=corr_mat.values, x=str_labels, y=str_labels, colorscale=[[0, "#e74c3c"], [0.5, "#f7f9fb"], [1, "#0a5c5c"]], zmin=-1, zmax=1, text=[[f"{v:.2f}" for v in row] for row in corr_mat.values], texttemplate="%{text}", textfont=dict(size=11), showscale=True, xgap=2, ygap=2))
    fig.update_layout(height=420, margin=dict(l=80, r=20, t=30, b=80), paper_bgcolor=bg, plot_bgcolor=bg, font=dict(family="DM Sans, sans-serif", color=txt), xaxis=dict(type="category", tickfont=dict(size=10), tickangle=-30), yaxis=dict(type="category", tickfont=dict(size=10), autorange="reversed"))
    return fig

def _fig_vwap_bar(df: pd.DataFrame, theme: str = "light") -> go.Figure:
    """Activity 1D: 실행 단가 vs VWAP."""
    is_dark = (theme == "dark")
    bg, txt, grd = ("#1e252e", "#f0f7f5", "#313d4a") if is_dark else ("#fafbfb", "#1a2d30", "#dde3e8")
    tc = _find_col(df, "ticker", "symbol", "code", "asset")
    pc = _find_col(df, "price", "execution_price")
    vc = _find_col(df, "vwap", "avg_price")
    fig = go.Figure()
    if not (tc and pc and vc):
        fig.add_annotation(text="Ticker/Price/VWAP 컬럼이 필요합니다", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return fig
    w = df.copy()
    w['diff'] = pd.to_numeric(w[pc]) - pd.to_numeric(w[vc])
    colors = np.where(w['diff'] >= 0, "#e74c3c", "#2ed573")
    fig.add_trace(go.Bar(x=w[tc], y=w['diff'], marker_color=colors, name="VWAP 대비 차이", text=w['diff'].round(1), textposition='auto'))
    fig.update_layout(height=400, margin=dict(l=40, r=20, t=40, b=40), paper_bgcolor=bg, plot_bgcolor=bg, font=dict(family="DM Sans, sans-serif", color=txt), xaxis=dict(gridcolor=grd), yaxis=dict(gridcolor=grd), title=dict(text="실행 단가 vs VWAP (매매 효율성)", font=dict(size=14, weight='bold')))
    return fig

def _fig_scatter_pf(df: pd.DataFrame, theme: str = "light") -> go.Figure:
    """Activity 1D 서브: 손익비 (Profit/Loss Ratio) 스캐터."""
    is_dark = (theme == "dark")
    bg, txt, grd = ("#1e252e", "#f0f7f5", "#313d4a") if is_dark else ("#fafbfb", "#1a2d30", "#dde3e8")
    qc = _find_col(df, "quantity", "qty", "amount")
    pc = _find_col(df, "price", "execution_price")
    tc = _find_col(df, "ticker", "symbol")
    fig = go.Figure()
    if not (qc and pc):
        fig.add_annotation(text="Quantity/Price 컬럼이 필요합니다", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return fig
    w = df.copy()
    w['val'] = pd.to_numeric(w[qc]) * pd.to_numeric(w[pc])
    # 가상의 손익 계산 (실제 데이터에 따라 조정 필요)
    w['profit_pct'] = np.random.uniform(-0.05, 0.05, len(w)) 
    fig.add_trace(go.Scatter(x=w['val'], y=w['profit_pct'], mode='markers', marker=dict(size=12, color=np.where(w['profit_pct']>=0, "#e74c3c", "#2ed573"), opacity=0.7, line=dict(width=1, color='white')), text=w[tc] if tc else None, hovertemplate="거래대금: %{x:,.0f}<br>수익률: %{y:.2%}<extra></extra>"))
    fig.add_hline(y=0, line_dash="dash", line_color=txt, line_width=1)
    fig.update_layout(height=300, margin=dict(l=40, r=20, t=40, b=40), paper_bgcolor=bg, plot_bgcolor=bg, font=dict(family="DM Sans, sans-serif", color=txt), xaxis=dict(title="거래 대금", gridcolor=grd), yaxis=dict(title="수익률", gridcolor=grd, tickformat=".1%"), title=dict(text="거래별 손익 분포", font=dict(size=13)))
    return fig

def _fig_activity_dual_line(df: pd.DataFrame, theme: str = "light") -> go.Figure:
    """Activity 2D: 자산 교체 비교 (Dual Line)."""
    is_dark = (theme == "dark")
    bg, txt, grd = ("#1e252e", "#f0f7f5", "#313d4a") if is_dark else ("#fafbfb", "#1a2d30", "#dde3e8")
    tc = _find_col(df, "ticker", "symbol")
    ts = _find_col(df, "timestamp", "date")
    pc = _find_col(df, "price")
    fig = go.Figure()
    if not (tc and ts and pc):
        fig.add_annotation(text="Ticker/Time/Price 컬럼 필요", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return fig
    tickers = df[tc].unique()[:2]
    colors = ["#0a5c5c", "#1dd1a1"]
    for i, t in enumerate(tickers):
        sub = df[df[tc] == t].sort_values(ts)
        fig.add_trace(go.Scatter(x=sub[ts], y=sub[pc], name=_ticker_to_name(str(t)), mode='lines+markers', line=dict(color=colors[i%2], width=2.5), marker=dict(size=6)))
    fig.update_layout(height=400, margin=dict(l=40, r=20, t=40, b=40), paper_bgcolor=bg, plot_bgcolor=bg, font=dict(family="DM Sans, sans-serif", color=txt), xaxis=dict(gridcolor=grd), yaxis=dict(gridcolor=grd), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), title=dict(text="자산 교체/매매 비교", font=dict(size=14, weight='bold')))
    return fig

def _fig_switch_bar(df: pd.DataFrame, theme: str = "light") -> go.Figure:
    """Activity 2D 서브: 스위칭 기회비용 (Switching Cost)."""
    is_dark = (theme == "dark")
    bg, txt, grd = ("#1e252e", "#f0f7f5", "#313d4a") if is_dark else ("#fafbfb", "#1a2d30", "#dde3e8")
    fig = go.Figure()
    # 목 데이터 (실제 로직 구현 시 df 분석 필요)
    labels = ["교체 효과", "슬리피지", "수수료", "기회비용"]
    values = [1.2, -0.3, -0.15, 0.75]
    colors = ["#2ed573", "#ffa502", "#ff4757", "#0a5c5c"]
    fig.add_trace(go.Bar(x=labels, y=values, marker_color=colors, text=[f"{v:+.2f}%" for v in values], textposition='auto'))
    fig.update_layout(height=300, margin=dict(l=40, r=20, t=40, b=40), paper_bgcolor=bg, plot_bgcolor=bg, font=dict(family="DM Sans, sans-serif", color=txt), xaxis=dict(gridcolor=grd), yaxis=dict(gridcolor=grd), title=dict(text="스위칭 분석 (%)", font=dict(size=13)))
    return fig

def _fig_turnover_bar(df: pd.DataFrame, theme: str = "light") -> go.Figure:
    """Activity ND: 종목별 회전율."""
    is_dark = (theme == "dark")
    bg, txt, grd = ("#1e252e", "#f0f7f5", "#313d4a") if is_dark else ("#fafbfb", "#1a2d30", "#dde3e8")
    tc = _find_col(df, "ticker", "symbol", "asset")
    qc = _find_col(df, "quantity", "qty")
    fig = go.Figure()
    if not (tc and qc):
        fig.add_annotation(text="Ticker/Quantity 컬럼 필요", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return fig
    w = df.copy()
    w['qty_num'] = pd.to_numeric(w[qc])
    turnover = w.groupby(tc)['qty_num'].sum().sort_values(ascending=False).reset_index()
    fig.add_trace(go.Bar(x=turnover[tc], y=turnover['qty_num'], marker_color="#0a5c5c", name="누적 거래량"))
    fig.update_layout(height=400, margin=dict(l=40, r=20, t=40, b=40), paper_bgcolor=bg, plot_bgcolor=bg, font=dict(family="DM Sans, sans-serif", color=txt), xaxis=dict(gridcolor=grd), yaxis=dict(gridcolor=grd), title=dict(text="종목별 회전율 (누적 거래량)", font=dict(size=14, weight='bold')))
    return fig

def _fig_activity_timeline(df: pd.DataFrame, theme: str = "light") -> go.Figure:
    """Activity ND 서브: 거래 타임라인."""
    is_dark = (theme == "dark")
    bg, txt, grd = ("#1e252e", "#f0f7f5", "#313d4a") if is_dark else ("#fafbfb", "#1a2d30", "#dde3e8")
    ts = _find_col(df, "timestamp", "date")
    tc = _find_col(df, "ticker", "symbol")
    bs = _find_col(df, "buy/sell", "side")
    fig = go.Figure()
    if not (ts and tc and bs):
        fig.add_annotation(text="Timestamp/Ticker/Side 컬럼 필요", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return fig
    w = df.copy().sort_values(ts)
    w['side_color'] = w[bs].apply(lambda x: "#e74c3c" if str(x).lower().startswith('b') else "#2ed573")
    fig.add_trace(go.Scatter(x=w[ts], y=w[tc], mode='markers', marker=dict(size=14, color=w['side_color'], symbol='diamond', line=dict(width=1, color='white')), text=w[bs], hovertemplate="일시: %{x}<br>종목: %{y}<br>구분: %{text}<extra></extra>"))
    fig.update_layout(height=300, margin=dict(l=60, r=20, t=40, b=40), paper_bgcolor=bg, plot_bgcolor=bg, font=dict(family="DM Sans, sans-serif", color=txt), xaxis=dict(gridcolor=grd), yaxis=dict(gridcolor=grd, type='category'), title=dict(text="거래 타임라인 (Buy=Red, Sell=Green)", font=dict(size=13)))
    return fig
