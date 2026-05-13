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
    if dc is None:
        st.error("데이터에 날짜(date) 컬럼이 없습니다.")
        return
    oc, hc, lc, cc = _find_col(df, "open"), _find_col(df, "high"), _find_col(df, "low"), _find_col(df, "close")
    if not (oc and hc and lc and cc):
        st.error("데이터에 필요한 가격 컬럼(open, high, low, close)이 부족합니다.")
        return
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
            
            # MACD
            if st.session_state.get("show_macd", False) and len(sub) >= 26:
                close = pd.to_numeric(sub[cc], errors="coerce")
                exp1 = close.ewm(span=12, adjust=False).mean()
                exp2 = close.ewm(span=26, adjust=False).mean()
                macd = exp1 - exp2
                signal = macd.ewm(span=9, adjust=False).mean()
                price_series.append({"type": 'Line', "data": sub[[dc, cc]].assign(value=macd).dropna()[[dc, 'value']].rename(columns={dc:'time'}).to_dict('records'), "options": {"color": "#ff9ff3", "lineWidth": 1, "title": "MACD"}})
                price_series.append({"type": 'Line', "data": sub[[dc, cc]].assign(value=signal).dropna()[[dc, 'value']].rename(columns={dc:'time'}).to_dict('records'), "options": {"color": "#54a0ff", "lineWidth": 1, "title": "MACD Signal"}})

            # SAR
            if st.session_state.get("show_psar", False) and len(sub) >= 2:
                high = pd.to_numeric(sub[hc], errors="coerce")
                low = pd.to_numeric(sub[lc], errors="coerce")
                sar = pd.Series(index=sub.index, dtype='float64')
                af = 0.02
                ep = high.iloc[0]
                sar.iloc[0] = low.iloc[0]
                bull = True
                for i in range(1, len(sub)):
                    if bull:
                        sar.iloc[i] = sar.iloc[i-1] + af * (ep - sar.iloc[i-1])
                        if high.iloc[i] > ep:
                            ep = high.iloc[i]
                            af = min(af + 0.02, 0.2)
                        if low.iloc[i] < sar.iloc[i]:
                            bull = False
                            sar.iloc[i] = ep
                            ep = low.iloc[i]
                            af = 0.02
                    else:
                        sar.iloc[i] = sar.iloc[i-1] - af * (sar.iloc[i-1] - ep)
                        if low.iloc[i] < ep:
                            ep = low.iloc[i]
                            af = min(af + 0.02, 0.2)
                        if high.iloc[i] > sar.iloc[i]:
                            bull = True
                            sar.iloc[i] = ep
                            ep = high.iloc[i]
                            af = 0.02
                price_series.append({"type": 'Line', "data": sub[[dc]].assign(value=sar).dropna().rename(columns={dc:'time'}).to_dict('records'), "options": {"color": "#feca57", "lineWidth": 0, "lineStyle": 2, "pointMarkers": True, "title": "SAR"}})

            # CCI (14 period)
            if st.session_state.get("show_cci", False) and len(sub) >= 20:
                tp = (pd.to_numeric(sub[hc]) + pd.to_numeric(sub[lc]) + pd.to_numeric(sub[cc])) / 3
                cci = (tp - tp.rolling(20).mean()) / (0.015 * tp.rolling(20).std())
                price_series.append({"type": 'Line', "data": sub[[dc]].assign(value=cci).dropna().rename(columns={dc:'time'}).to_dict('records'), "options": {"color": "#48dbfb", "lineWidth": 1, "title": "CCI"}})

            # Stochastic (14, 3, 3)
            if st.session_state.get("show_stoch", False) and len(sub) >= 14:
                high = pd.to_numeric(sub[hc])
                low = pd.to_numeric(sub[lc])
                close = pd.to_numeric(sub[cc])
                k = 100 * (close - low.rolling(14).min()) / (high.rolling(14).max() - low.rolling(14).min())
                d = k.rolling(3).mean()
                price_series.append({"type": 'Line', "data": sub[[dc]].assign(value=k).dropna().rename(columns={dc:'time'}).to_dict('records'), "options": {"color": "#ff9f43", "lineWidth": 1, "title": "Stoch %K"}})
                price_series.append({"type": 'Line', "data": sub[[dc]].assign(value=d).dropna().rename(columns={dc:'time'}).to_dict('records'), "options": {"color": "#5f27cd", "lineWidth": 1, "title": "Stoch %D"}})
            
            # Envelope (20 period, 5% deviation)
            if st.session_state.get("show_env", False) and len(sub) >= 20:
                ma = pd.to_numeric(sub[cc]).rolling(20).mean()
                env_u = ma * 1.05
                env_l = ma * 0.95
                price_series.append({"type": 'Line', "data": sub[[dc]].assign(value=env_u).dropna().rename(columns={dc:'time'}).to_dict('records'), "options": {"color": "#778ca3", "lineWidth": 1, "lineStyle": 2, "title": "Env Upper"}})
                price_series.append({"type": 'Line', "data": sub[[dc]].assign(value=env_l).dropna().rename(columns={dc:'time'}).to_dict('records'), "options": {"color": "#778ca3", "lineWidth": 1, "lineStyle": 2, "title": "Env Lower"}})

        if show_vol and vc:
            v_data = sub[[dc, vc]].rename(columns={dc: 'time', vc: 'value'}).to_dict('records')
            
            # OBV
            if st.session_state.get("show_obv", False):
                close = pd.to_numeric(sub[cc])
                vol = pd.to_numeric(sub[vc])
                obv = (np.sign(close.diff()) * vol).fillna(0).cumsum()
                volume_series.append({"type": 'Line', "data": sub[[dc]].assign(value=obv).dropna().rename(columns={dc:'time'}).to_dict('records'), "options": {"color": "#eb2f06", "lineWidth": 1, "title": "OBV"}})

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
    """Activity 1D: TradingView 스타일의 가상 캔들차트 및 VWAP."""
    is_dark = (theme == "dark")
    bg, txt, grd = ("#1e252e", "#f0f7f5", "#313d4a") if is_dark else ("#fafbfb", "#1a2d30", "#dde3e8")
    dc = _find_col(df, "date", "datetime", "timestamp")
    pc = _find_col(df, "price", "execution_price")
    vc = _find_col(df, "vwap", "avg_price")
    bc = _find_col(df, "side", "buy/sell")
    
    fig = go.Figure()
    if not (dc and pc and vc and bc):
        fig.add_annotation(text="필수 컬럼이 누락되었습니다.", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return fig
    
    w = df.copy().sort_values(dc)
    w['is_buy'] = w[bc].apply(lambda x: str(x).lower().startswith('b'))
    
    # 캔들 생성을 위한 가상 OHLC
    # 가격(pc)을 종가(close)로 보고, 가격의 0.1%를 몸통 크기로 설정
    w['close'] = pd.to_numeric(w[pc])
    w['open'] = np.where(w['is_buy'], w['close'] * 0.9995, w['close'] * 1.0005)
    w['high'] = w[['open', 'close']].max(axis=1) * 1.0002
    w['low'] = w[['open', 'close']].min(axis=1) * 0.9998
    
    # TradingView 스타일 캔들
    fig.add_trace(go.Candlestick(
        x=w[dc],
        open=w['open'], high=w['high'], low=w['low'], close=w['close'],
        increasing_line_color='#2ed573', decreasing_line_color='#ff4757',
        name="거래 캔들"
    ))
    
    # VWAP 라인
    fig.add_trace(go.Scatter(
        x=w[dc], y=pd.to_numeric(w[vc]), 
        mode='lines', 
        line=dict(color="#f1c40f", width=2, dash='dot'), 
        name="VWAP"
    ))
    
    fig.update_layout(
        height=400, margin=dict(l=50, r=30, t=50, b=50), 
        paper_bgcolor=bg, plot_bgcolor=bg, font=dict(family="DM Sans, sans-serif", color=txt), 
        xaxis=dict(gridcolor=grd, showgrid=True), yaxis=dict(gridcolor=grd, showgrid=True),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        title=dict(text="거래 분석 (TradingView 스타일)", font=dict(size=16, weight='bold'))
    )
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
