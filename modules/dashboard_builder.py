"""04_dashboard: Streamlit 레이아웃·차트·엔진 뷰."""

from __future__ import annotations

import html
from typing import Any

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
import feedparser
from streamlit_lightweight_charts import renderLightweightCharts
from .dashboard_timeseries import dashboard_timeseries
from .dashboard_activity import dashboard_activity
from .dashboard_portfolio import dashboard_portfolio
from .dashboard_utils import (
    _find_col, _ticker_to_name, _render_lightweight_chart, _fig_corr_heatmap,
    _fig_scatter_pf, _fig_switch_bar, _fig_activity_timeline
)

from urllib.parse import quote  # URL 인코딩을 위해 추가

# Sequence 스타일: Streamlit 네이티브 테마 완벽 연동

def ticker_tape_html(theme: str = "light") -> str:
    """TradingView 상단 티커 테이프 위젯."""
    import json
    config = {
        "symbols": [
            {"proName": "FOREXCOM:SPX500", "title": "S&P 500"},
            {"proName": "FOREXCOM:NSXUSD", "title": "Nasdaq 100"},
            {"fx_id": "KRWUSD", "title": "USD/KRW"},
            {"proName": "BITSTAMP:BTCUSD", "title": "BTC/USD"},
            {"proName": "BITSTAMP:ETHUSD", "title": "ETH/USD"}
        ],
        "showSymbolLogo": True,
        "colorTheme": theme,
        "isTransparent": False,
        "displayMode": "adaptive",
        "locale": "ko"
    }
    return f"""
<div class="tradingview-widget-container">
  <div class="tradingview-widget-container__widget"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>
  {json.dumps(config)}
  </script>
</div>
"""


_TICKER_COLORS: dict[str, str] = {
    "005930": "#1dd1a1", # 삼성전자: 틸/민트
    "000660": "#ffa502", # SK하이닉스: 오렌지/골드
}
_DEFAULT_COLORS = ["#2ed573", "#1e90ff", "#ff4757", "#ffa502", "#3742fa", "#70a1ff", "#5352ed", "#2f3542"]



def dimension_pills_html(dimension: str | None) -> str:
    labs = ["1D", "2D", "ND"]
    parts: list[str] = []
    for lab in labs:
        active = dimension is not None and lab == dimension
        cls = "sq-dim-pill sq-dim-pill--active" if active else "sq-dim-pill sq-dim-pill--idle"
        parts.append(f'<span class="{cls}">{html.escape(lab)}</span>')
    label = '<p class="sq-nav-label" style="margin-top:0">Data Dimension</p>'
    return f"{label}<div class=\"sq-dim-row\">{''.join(parts)}</div>"

SIDEBAR_ICON_DASHBOARD = """
<div class="sq-sb-nav-ic" title="대시보드">
<svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <path d="M4 5h8v8H4V5zm12 0h4v4h-4V5zm0 6h4v8h-4v-8zM4 15h8v4H4v-4z" stroke="#0a5c5c" stroke-width="1.5" fill="rgba(10,92,92,0.12)" stroke-linejoin="round"/>
</svg></div>
"""

SIDEBAR_ICON_HOME = """
<div class="sq-sb-nav-ic" title="Home">
<svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M3 9.5L12 3l9 6.5V20a1 1 0 01-1 1H5a1 1 0 01-1-1V9.5z" stroke="#0a5c5c" stroke-width="1.5" fill="rgba(10,92,92,0.1)" stroke-linejoin="round"/>
  <path d="M9 21V12h6v9" stroke="#0a5c5c" stroke-width="1.5" stroke-linecap="round"/>
</svg></div>
"""

SIDEBAR_ICON_ENGINE = """
<div class="sq-sb-nav-ic" title="분석 엔진">
<svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <path d="M12 15a3 3 0 100-6 3 3 0 000 6z" stroke="#0a5c5c" stroke-width="1.5" fill="rgba(10,92,92,0.1)"/>
  <path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83 0 2 2 0 010-2.83l.06-.06a1.65 1.65 0 00-.33 1.82 1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 010-2.83 2 2 0 012.83 0l.06.06a1.65 1.65 0 001.82.33H9a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 0 2 2 0 010 2.83l-.06.06a1.65 1.65 0 00-.33 1.82V9c.26.604.852 1 1.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z" stroke="#0a5c5c" stroke-width="1.15" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
</svg></div>
"""

SIDEBAR_BRAND_HTML = """
<div class="sq-sb-brand">
  <div class="sq-sb-logo-row">
    <div class="sq-sb-logo-mark" aria-hidden="true"></div>
    <div>
      <div class="sq-sb-logo-text">FinRoute <span>AI</span></div>
      <div class="sq-sb-logo-sub">Portfolio intelligence</div>
    </div>
  </div>
</div>
"""

# 한국 주요 종목 코드 → 종목명 매핑

THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&display=swap');
:root {
  --sq-teal-deep: #063d3d;
  --sq-teal: #0a5c5c;
  --sq-teal-mid: #0d6e6e;
  --sq-mint: #1dd1a1;
  --sq-green: #2ed573;
  --sq-danger: #e74c3c;
  --sq-warn: #f39c12;
  
  /* 테마 자동 반응형 변수 */
  --sq-bg: var(--background-color); 
  --sq-surface: var(--secondary-background-color);
  --sq-text: var(--text-color);
  --sq-border: rgba(128, 128, 128, 0.2);
  --sq-muted: rgba(128, 128, 128, 0.6);
  
  --sq-radius: 14px;
  --sq-radius-sm: 10px;
  --sq-shadow: 0 4px 24px rgba(0, 0, 0, 0.15);
  --sq-shadow-hover: 0 10px 36px rgba(0, 0, 0, 0.25);
  --sq-font: "DM Sans", system-ui, -apple-system, "Segoe UI", sans-serif;
}

/* 전체 앱 배경 및 폰트 설정 */
.stApp { background: var(--sq-bg) !important; color: var(--sq-text); font-family: var(--sq-font); }
[data-testid="stAppViewContainer"] > .main { background: transparent; }
.main .block-container { padding: 1.25rem 1.75rem 2rem !important; max-width: 100% !important; }

/* 헤더 및 툴바 투명화 */
[data-testid="stHeader"] { background: transparent !important; border-bottom: none !important; }
[data-testid="stToolbar"] { background: transparent !important; }

/* 텍스트 색상 연동 */
h1, h2, h3, h4, h5 { color: var(--sq-text) !important; letter-spacing: -0.02em; }
.stCaption, [data-testid="stCaptionContainer"] { color: var(--sq-muted) !important; }
.sq-app-title { font-size: 1.75rem; font-weight: 700; letter-spacing: -0.03em; margin: 0 0 0.5rem 0; color: var(--sq-text); }
.sq-nav-label { font-size: 0.65rem; font-weight: 600; letter-spacing: 0.12em; color: var(--sq-muted); margin: 4px 0 10px 0; text-transform: uppercase; }

/* 네이티브 사이드바 */
[data-testid="stSidebar"] { background: var(--sq-surface) !important; border-right: 1px solid var(--sq-border) !important; }
[data-testid="stSidebar"] > div:first-child { background: transparent !important; }
[data-testid="stSidebar"] .block-container { padding-top: 1rem !important; padding-bottom: 1.25rem !important; }
.sq-sb-brand { margin-bottom: 1.25rem; }
.sq-sb-logo-row { display: flex; align-items: center; gap: 12px; }
.sq-sb-logo-mark { width: 40px; height: 40px; border-radius: 12px; flex-shrink: 0; background: linear-gradient(135deg, var(--sq-teal-deep) 0%, var(--sq-teal) 55%, var(--sq-mint) 160%); }
.sq-sb-logo-text { font-size: 1.15rem; font-weight: 700; letter-spacing: -0.03em; color: var(--sq-text); line-height: 1.2; }
.sq-sb-logo-text span { color: var(--sq-teal); }
.sq-sb-logo-sub { font-size: 0.72rem; color: var(--sq-muted); margin-top: 2px; }
.sq-sb-nav-wrap { margin: 0.5rem 0 1rem 0; }
.sq-sb-nav-row { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
.sq-sb-nav-row .stButton { flex: 1; }
.sq-sb-nav-ic { flex-shrink: 0; width: 28px; height: 28px; display: flex; align-items: center; justify-content: center; }
.sq-sb-upload-cap { font-size: 0.65rem; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; color: var(--sq-muted); margin: 1rem 0 0.35rem 0; }

/* 차원 필터 뱃지 */
.sq-dim-row { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 4px; }
.sq-dim-pill { flex: 1; min-width: 48px; text-align: center; padding: 8px 10px; border-radius: 10px; font-size: 0.82rem; font-weight: 600; border: 1px solid var(--sq-border); box-sizing: border-box; }
.sq-dim-pill--active { background: var(--sq-teal); color: #fff; border-color: var(--sq-teal); box-shadow: 0 2px 8px rgba(10, 92, 92, 0.2); }
.sq-dim-pill--idle { background: var(--sq-bg); color: var(--sq-muted); }

/* 버튼 스타일 */
.stApp .stButton > button[kind="primary"] { background: linear-gradient(180deg, var(--sq-green) 0%, #24b963 100%) !important; color: #063d2a !important; border: none !important; font-weight: 600 !important; border-radius: 10px !important; box-shadow: 0 2px 8px rgba(46,213,115,0.35); }
.stApp .stButton > button[kind="secondary"] { background: var(--sq-surface) !important; color: var(--sq-text) !important; border: 1px solid var(--sq-border) !important; border-radius: 10px !important; font-weight: 500 !important; }
.stApp .stButton > button:disabled { opacity: 0.45 !important; }

/* 히어로 스트립 */
.sq-hero-row { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 12px; margin-bottom: 20px; padding: 18px; border-radius: var(--sq-radius); background: linear-gradient(135deg, var(--sq-teal-deep) 0%, var(--sq-teal) 42%, var(--sq-teal-mid) 100%); box-shadow: 0 12px 40px rgba(0, 0, 0, 0.2); border: 1px solid rgba(255,255,255,0.06); }
@media (max-width: 1100px) { .sq-hero-row { grid-template-columns: 1fr 1fr; } }
.sq-hero-cell { background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.1); border-radius: var(--sq-radius-sm); padding: 12px 14px; min-height: 102px; color: #f4faf9; }
.sq-hero-cell__label { font-size: 0.72rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; opacity: 0.85; margin-bottom: 6px; color: rgba(255,255,255,0.85); }
.sq-hero-cell__value { font-size: 1.35rem; font-weight: 700; line-height: 1.2; margin-bottom: 4px; }
.sq-hero-cell__body { font-size: 0.82rem; opacity: 0.92; line-height: 1.35; color: rgba(255,255,255,0.92); }
.sq-badge-pos { display: inline-block; margin-top: 6px; padding: 2px 8px; border-radius: 999px; font-size: 0.72rem; font-weight: 600; background: rgba(46,213,115,0.25); color: #b8ffd4; border: 1px solid rgba(46,213,115,0.45); }
.sq-progress { margin-top: 8px; height: 6px; border-radius: 999px; background: rgba(0,0,0,0.2); overflow: hidden; }
.sq-progress > span { display: block; height: 100%; border-radius: 999px; background: linear-gradient(90deg, var(--sq-mint), var(--sq-green)); }

/* 카드 공통 (KPI, 차트, 패널) */
.sq-card, .sq-rail, .sq-ac-wrap, .sq-eng-section { background: var(--sq-surface); border: 1px solid var(--sq-border); border-radius: var(--sq-radius); box-shadow: var(--sq-shadow); }
.sq-card { transition: transform 0.2s ease; }
.sq-card:hover { transform: translateY(-4px); box-shadow: var(--sq-shadow-hover); }

/* KPI 텍스트 */
.sq-kpi { padding: 18px 16px; margin-bottom: 10px; }
.sq-kpi__name { font-size: 0.78rem; font-weight: 600; color: var(--sq-muted); margin-bottom: 6px; }
.sq-kpi__val { font-size: 1.35rem; font-weight: 700; color: var(--sq-text); }
.sq-kpi__sub { font-size: 0.78rem; color: var(--sq-muted); margin-top: 4px; }
.sq-kpi__dot { display: inline-block; margin-top: 8px; font-size: 0.75rem; font-weight: 600; }
.sq-chart { padding: 12px 12px 4px; margin-bottom: 14px; }

/* 우측 패널 */
.sq-rail { padding: 16px 14px; }
.sq-rail-section { margin-bottom: 14px; }
.sq-rail-title { font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; color: var(--sq-muted); margin-bottom: 8px; padding-bottom: 6px; border-bottom: 1px solid var(--sq-border); }
.sq-mkt-item, .sq-ind-row { display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid var(--sq-border); }
.sq-mkt-name, .sq-ind-name { font-size: 0.78rem; color: var(--sq-muted); font-weight: 600; }
.sq-mkt-val, .sq-ind-val { font-size: 0.82rem; font-weight: 700; color: var(--sq-text); }
.sq-ind-val { font-size: 1.05rem; }

/* 이벤트 피드 */
.sq-feed-item { background: var(--sq-bg); border: 1px solid var(--sq-border); border-radius: var(--sq-radius-sm); padding: 10px 12px; margin-bottom: 8px; transition: transform 0.15s ease; }
.sq-feed-item:hover { transform: translateX(5px); }
.sq-feed-scroll { max-height: 220px; overflow-y: auto; padding-right: 4px; }
.sq-feed-scroll::-webkit-scrollbar { width: 4px; }
.sq-feed-scroll::-webkit-scrollbar-track { background: transparent; }
.sq-feed-scroll::-webkit-scrollbar-thumb { background: var(--sq-border); border-radius: 2px; }

/* 분석목적 칩 */
.sq-goal-chip { display: inline-flex; align-items: center; gap: 6px; padding: 4px 10px; border-radius: 999px; font-size: 0.75rem; font-weight: 600; margin: 3px 2px; border: 1px solid; }
.sq-goal-on { background: rgba(10,92,92,0.15); color: var(--sq-mint); border-color: var(--sq-teal); }
.sq-goal-off { background: var(--sq-bg); color: var(--sq-muted); border-color: var(--sq-border); }

/* Action Console */
.sq-ac-wrap { overflow: hidden; margin-bottom: 14px; }
.sq-ac-header { background: linear-gradient(135deg, #063d3d 0%, #0a5c5c 100%); padding: 14px 20px; display: flex; align-items: center; gap: 10px; }
.sq-ac-title { font-size: 1rem; font-weight: 700; color: #fff; }
.sq-ac-badge { font-size: 0.72rem; background: rgba(255,255,255,0.15); color: #b8ffd4; padding: 2px 10px; border-radius: 999px; border: 1px solid rgba(255,255,255,0.2); }
.sq-ac-llm { padding: 10px 20px; background: var(--sq-bg); border-bottom: 1px solid var(--sq-border); font-family: monospace; font-size: 0.78rem; color: var(--sq-mint); }
.sq-ac-body { display: grid; grid-template-columns: 1fr; }
.sq-ac-block { padding: 18px 20px; border-bottom: 1px solid var(--sq-border); }
.sq-ac-block:last-child { border-bottom: none; }
.sq-ac-lbl { font-size: 0.72rem; font-weight: 700; color: var(--sq-muted); text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 8px; }
.sq-ac-text { font-size: 0.95rem; color: var(--sq-text); line-height: 1.65; }

/* 엔진 뷰 섹션 */
.sq-eng-section { padding: 22px 24px; margin-bottom: 16px; }
.sq-eng-section-title { font-size: 0.82rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: var(--sq-muted); margin-bottom: 16px; padding-bottom: 8px; border-bottom: 1px solid var(--sq-border); }

.sq-pipe-row { display: flex; align-items: center; gap: 0; flex-wrap: wrap; margin: 8px 0; }
.sq-pipe-step { background: var(--sq-bg); border: 1.5px solid var(--sq-teal); border-radius: 10px; padding: 10px 18px; font-size: 0.82rem; font-weight: 600; color: var(--sq-text); min-width: 110px; text-align: center; }
.sq-pipe-arrow { color: var(--sq-teal); font-size: 1.2rem; padding: 0 8px; }
.sq-pipe-result { background: linear-gradient(135deg,#063d3d,#0a5c5c); color: #b8ffd4 !important; border-color: transparent !important; }

.sq-sim-card { background: var(--sq-bg); border: 1.5px solid var(--sq-border); border-radius: 12px; padding: 16px; text-align: center; transition: all 0.2s; }
.sq-sim-card.best { background: rgba(10,92,92,0.1); border-color: var(--sq-teal); }
.sq-sim-name { font-size: 0.82rem; font-weight: 700; color: var(--sq-text); margin-bottom: 8px; }
.sq-sim-pct { font-size: 1.6rem; font-weight: 800; color: var(--sq-teal); }
.sq-sim-bar { height: 5px; background: var(--sq-border); border-radius: 999px; margin-top: 8px; overflow: hidden; }
.sq-sim-fill { height: 100%; border-radius: 999px; background: linear-gradient(90deg, var(--sq-teal), var(--sq-mint)); }

.sq-vec-matrix { display: grid; grid-template-columns: repeat(6,1fr); gap: 4px; margin-bottom: 4px; }
.sq-vec-cell { aspect-ratio: 1; border-radius: 6px; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 2px; font-size: 0.6rem; color: var(--sq-muted); padding: 4px; }
.sq-vec-cell.v1 { background: rgba(10,92,92,0.15); color: var(--sq-mint); font-weight: 700; border: 1.5px solid var(--sq-teal); }
.sq-vec-cell.v0 { background: var(--sq-bg); border: 1px solid var(--sq-border); }
.sq-vec-bit { font-size: 0.82rem; font-weight: 800; }
</style>
"""

def dimension_pills_html(dimension: str | None) -> str:
    labs = ["1D", "2D", "ND"]
    parts: list[str] = []
    for lab in labs:
        active = dimension is not None and lab == dimension
        cls = "sq-dim-pill sq-dim-pill--active" if active else "sq-dim-pill sq-dim-pill--idle"
        parts.append(f'<span class="{cls}">{html.escape(lab)}</span>')
    label = '<p class="sq-nav-label" style="margin-top:0">Data Dimension</p>'
    return f"{label}<div class=\"sq-dim-row\">{''.join(parts)}</div>"

SIDEBAR_ICON_DASHBOARD = """
<div class="sq-sb-nav-ic" title="대시보드">
<svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <path d="M4 5h8v8H4V5zm12 0h4v4h-4V5zm0 6h4v8h-4v-8zM4 15h8v4H4v-4z" stroke="#0a5c5c" stroke-width="1.5" fill="rgba(10,92,92,0.12)" stroke-linejoin="round"/>
</svg></div>
"""

SIDEBAR_ICON_HOME = """
<div class="sq-sb-nav-ic" title="Home">
<svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M3 9.5L12 3l9 6.5V20a1 1 0 01-1 1H5a1 1 0 01-1-1V9.5z" stroke="#0a5c5c" stroke-width="1.5" fill="rgba(10,92,92,0.1)" stroke-linejoin="round"/>
  <path d="M9 21V12h6v9" stroke="#0a5c5c" stroke-width="1.5" stroke-linecap="round"/>
</svg></div>
"""

SIDEBAR_ICON_ENGINE = """
<div class="sq-sb-nav-ic" title="분석 엔진">
<svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <path d="M12 15a3 3 0 100-6 3 3 0 000 6z" stroke="#0a5c5c" stroke-width="1.5" fill="rgba(10,92,92,0.1)"/>
  <path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83 0 2 2 0 010-2.83l.06-.06a1.65 1.65 0 00-.33 1.82 1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 010-2.83 2 2 0 012.83 0l.06.06a1.65 1.65 0 001.82.33H9a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 0 2 2 0 010 2.83l-.06.06a1.65 1.65 0 00-.33 1.82V9c.26.604.852 1 1.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z" stroke="#0a5c5c" stroke-width="1.15" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
</svg></div>
"""

SIDEBAR_BRAND_HTML = """
<div class="sq-sb-brand">
  <div class="sq-sb-logo-row">
    <div class="sq-sb-logo-mark" aria-hidden="true"></div>
    <div>
      <div class="sq-sb-logo-text">FinRoute <span>AI</span></div>
      <div class="sq-sb-logo-sub">Portfolio intelligence</div>
    </div>
  </div>
</div>
"""

_TICKER_NAME: dict[str, str] = {
    "005930": "삼성전자",
    "000660": "SK하이닉스",
    "035420": "NAVER",
    "005380": "현대차",
    "051910": "LG화학",
    "000270": "기아",
    "068270": "셀트리온",
    "207940": "삼성바이오로직스",
    "006400": "삼성SDI",
    "035720": "카카오",
    "003550": "LG",
    "028260": "삼성물산",
    "066570": "LG전자",
    "096770": "SK이노베이션",
    "017670": "SK텔레콤",
    "030200": "KT",
    "055550": "신한지주",
    "105560": "KB금융",
    "086790": "하나금융지주",
    "316140": "우리금융지주",
    "032830": "삼성생명",
    "003490": "대한항공",
    "011200": "HMM",
    "009150": "삼성전기",
    "012330": "현대모비스",
}


def _ticker_to_name(ticker: str) -> str:
    """ticker 코드를 종목명으로 변환. 매핑 없으면 ticker 그대로 반환."""
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

def _detect_events(
    df: pd.DataFrame, classify_result: dict, indicator_result: dict
) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    ct = classify_result["class_type"]
    dim = classify_result["dimension"]

    if ct == "TimeSeries" and dim == "1D":
        dc = _find_col(df, "date", "datetime")
        cc = _find_col(df, "close")
        if not (dc and cc):
            return events
        w = df.sort_values(dc).copy()
        close = pd.to_numeric(w[cc], errors="coerce")
        ma20 = close.rolling(20, min_periods=5).mean()
        ma60 = close.rolling(60, min_periods=5).mean()
        dlt = close.diff()
        g = dlt.clip(lower=0).ewm(alpha=1/14, adjust=False).mean()
        l = (-dlt.clip(upper=0)).ewm(alpha=1/14, adjust=False).mean()
        rsi = 100 - (100 / (1 + g / l.replace(0, np.nan)))
        for i in range(2, len(w)):
            dt = str(w[dc].iloc[i])
            if ma20.iloc[i] > ma60.iloc[i] and ma20.iloc[i-1] <= ma60.iloc[i-1]:
                events.append({"date": dt, "label": "골든크로스", "kind": "buy", "color": "#1a7f37"})
            if ma20.iloc[i] < ma60.iloc[i] and ma20.iloc[i-1] >= ma60.iloc[i-1]:
                events.append({"date": dt, "label": "데드크로스", "kind": "sell", "color": "#b42318"})
            rv = float(rsi.iloc[i]) if pd.notna(rsi.iloc[i]) else None
            if rv is not None:
                if rv > 70:
                    events.append({"date": dt, "label": "RSI 과매수", "kind": "warn", "color": "#b54708"})
                elif rv < 30:
                    events.append({"date": dt, "label": "RSI 과매도", "kind": "buy", "color": "#1a7f37"})
        label_first: dict[str, dict] = {}
        for ev in events:
            if ev["label"] not in label_first:
                label_first[ev["label"]] = ev
        events = sorted(label_first.values(), key=lambda e: e["date"], reverse=True)[:8]

    elif ct == "TimeSeries" and dim == "2D":
        zscore = indicator_result.get("zscore")
        if zscore is not None:
            if zscore > 2:
                events.append({"date": "latest", "label": "Z-score 과매수", "kind": "sell", "color": "#b42318"})
            elif zscore < -2:
                events.append({"date": "latest", "label": "Z-score 과매도", "kind": "buy", "color": "#1a7f37"})
        roll_corr = indicator_result.get("roll_corr")
        if roll_corr is not None and roll_corr > 0.9:
            events.append({"date": "latest", "label": "상관관계 급등", "kind": "warn", "color": "#b54708"})

    elif ct == "TimeSeries" and dim == "ND":
        avg_corr = indicator_result.get("avg_corr")
        if avg_corr is not None and avg_corr > 0.7:
            events.append({"date": "latest", "label": "종목간 상관 급등", "kind": "warn", "color": "#b54708"})
        var = indicator_result.get("VaR")
        if var is not None and var < -0.03:
            events.append({"date": "latest", "label": "VaR 위험 수준", "kind": "sell", "color": "#b42318"})

    elif ct == "Static" and dim in ("1D", "2D"):
        qc = _find_col(df, "quarter", "date")
        wc = _find_col(df, "weight")
        tc = _find_col(df, "target_weight")
        rc = _find_col(df, "return", "returns")
        if qc and wc and tc:
            for _q, part in df.groupby(qc, sort=True):
                for _, row in part.iterrows():
                    wv = float(row[wc])
                    tv = float(row[tc])
                    if abs(wv - tv) > 0.05:
                        events.append({"date": str(row[qc]), "label": "비중 이탈", "kind": "warn", "color": "#b54708"})
            label_first_s: dict[str, dict] = {}
            for ev in events:
                if ev["label"] not in label_first_s:
                    label_first_s[ev["label"]] = ev
            events = sorted(label_first_s.values(), key=lambda e: e["date"], reverse=True)[:8]
        elif qc and rc:
            for _q, part in df.groupby(qc, sort=True):
                rv = pd.to_numeric(part[rc], errors="coerce")
                avg_ret = float(rv.mean()) if len(rv) > 0 else 0
                if avg_ret < -0.05:
                    events.append({"date": str(_q), "label": "수익률 급락", "kind": "sell", "color": "#b42318"})
                elif avg_ret > 0.10:
                    events.append({"date": str(_q), "label": "수익률 급등", "kind": "buy", "color": "#1a7f37"})
            label_first_s2: dict[str, dict] = {}
            for ev in events:
                if ev["label"] not in label_first_s2:
                    label_first_s2[ev["label"]] = ev
            events = sorted(label_first_s2.values(), key=lambda e: e["date"], reverse=True)[:8]

    elif ct == "Static" and dim == "ND":
        if (indicator_result.get("HHI") or 0) > 2500:
            events.append({"date": "latest", "label": "HHI 초과", "kind": "sell", "color": "#b42318"})
        if (indicator_result.get("top3_conc") or 0) > 0.6:
            events.append({"date": "latest", "label": "Top-3 집중", "kind": "warn", "color": "#b54708"})
        if (indicator_result.get("cum_return") or 0) < -0.05:
            events.append({"date": "latest", "label": "포트 수익 마이너스", "kind": "sell", "color": "#b42318"})

    elif ct == "Activity" and dim == "1D":
        win_rate = indicator_result.get("win_rate")
        if win_rate is not None and win_rate < 0.4:
            events.append({"date": "latest", "label": "승률 저조", "kind": "sell", "color": "#b42318"})
        profit_factor = indicator_result.get("profit_factor")
        if profit_factor is not None and profit_factor < 1.0:
            events.append({"date": "latest", "label": "손익비 악화", "kind": "warn", "color": "#b54708"})
        total_fee = indicator_result.get("total_fee")
        if total_fee is not None and total_fee > 0:
            events.append({"date": "latest", "label": "수수료 발생", "kind": "warn", "color": "#b54708"})

    elif ct == "Activity" and dim == "2D":
        switch_ratio = indicator_result.get("switch_ratio")
        if switch_ratio is not None and switch_ratio > 0.3:
            events.append({"date": "latest", "label": "과도한 스위칭", "kind": "warn", "color": "#b54708"})
        net_profit = indicator_result.get("net_profit")
        if net_profit is not None and net_profit < 0:
            events.append({"date": "latest", "label": "순수익 손실", "kind": "sell", "color": "#b42318"})

    elif ct == "Activity" and dim == "ND":
        realized_pnl = indicator_result.get("realized_pnl")
        if realized_pnl is not None and realized_pnl < 0:
            events.append({"date": "latest", "label": "실현 손익 마이너스", "kind": "sell", "color": "#b42318"})
        unrealized_pnl = indicator_result.get("unrealized_pnl")
        if unrealized_pnl is not None and unrealized_pnl < 0:
            events.append({"date": "latest", "label": "평가 손실 발생", "kind": "warn", "color": "#b54708"})
        avg_hold = indicator_result.get("avg_hold")
        if avg_hold is not None and avg_hold < 3:
            events.append({"date": "latest", "label": "단타 매매 감지", "kind": "warn", "color": "#b54708"})

    return events

_GOAL_META = {
    "goal_trend": ("추세", "시계열 방향성·모멘텀"),
    "goal_comp": ("구성", "자산 간 비중·기여 비교"),
    "goal_compare": ("비교", "목표 대비 실제 괴리"),
    "goal_corr": ("상관", "자산 간 공변 구조"),
    "goal_dist": ("분산", "집중도·HHI·유효 N"),
    "goal_anomaly": ("이상", "RSI·Z·괴리 이벤트"),
    "goal_spread": ("스프레드", "상대 가치·페어"),
    "goal_relation": ("연관", "리스크 기여·네트워크"),
}

def _kpi_defs(
    classify_result: dict, indicator_result: dict
) -> list[tuple[str, Any, str]]:
    ct = classify_result["class_type"]
    dim = classify_result["dimension"]
    ir = indicator_result

    def fmt_pct(x: Any) -> str:
        if x is None or (isinstance(x, float) and not np.isfinite(x)): return "—"
        return f"{float(x)*100:.2f}%"

    def fmt_num(x: Any, nd: int = 2) -> str:
        if x is None or (isinstance(x, float) and not np.isfinite(x)): return "—"
        return f"{float(x):.{nd}f}"

    rows: list[tuple[str, Any, str]] = []
    if ct == "TimeSeries" and dim == "1D":
        rows = [
            ("RSI (14)", fmt_num(ir.get("RSI"), 1), "모멘텀"),
            ("MDD", fmt_pct(ir.get("MDD")), "낙폭"),
            ("샤프 비율", fmt_num(ir.get("Sharpe"), 2), "위험조정수익"),
            ("ATR (14)", fmt_num(ir.get("ATR"), 1), "변동성"),
            ("추세 (MA20 vs MA60)", ir.get("trend") or "—", "골든/데드"),
        ]
    elif ct == "TimeSeries" and dim == "2D":
        rows = [
            ("공적분 p-value", fmt_num(ir.get("coint_p"), 3), "정상성"),
            ("Z-score",        fmt_num(ir.get("zscore"),   2), "스프레드 편차"),
            ("롤링 상관계수",   fmt_num(ir.get("roll_corr"), 2), "60일"),
            ("헤지비율 β",      fmt_num(ir.get("beta"),     2), "회귀계수"),
            ("반감기",          fmt_num(ir.get("halflife"),  1), "일"),
        ]
    elif ct == "TimeSeries" and dim == "ND":
        rows = [
            ("평균 상관계수", fmt_num(ir.get("avg_corr"),   2), "종목간 평균"),
            ("PCA 1st PC",   fmt_pct(ir.get("pca_first")),     "설명력"),
            ("VaR (95%)",    fmt_pct(ir.get("VaR")),           "일간 손실"),
            ("최대 상관 쌍",  ir.get("max_corr_pair") or "—",  "종목 쌍"),
            ("누적 수익률",   fmt_pct(ir.get("cum_return")),    "동일비중"),
        ]
    elif ct == "Static" and dim == "1D":
        rows = [
            ("누적 수익률",  fmt_pct(ir.get("cum_return")),    "기간 합성"),
            ("최근 수익률",  fmt_pct(ir.get("recent_return")), "최근 분기"),
            ("최고 분기",    ir.get("best_quarter")  or "—",   "최대 수익"),
            ("최저 분기",    ir.get("worst_quarter") or "—",   "최대 손실"),
            ("HHI",          fmt_num(ir.get("HHI"), 0),        "집중도"),
        ]
    elif ct == "Static" and dim == "2D":
        rows = [
            ("포트 누적 수익",  fmt_pct(ir.get("cum_return")),     "기간 합성"),
            ("벤치 누적 수익",  fmt_pct(ir.get("bm_return")),      "비교 종목"),
            ("종목간 상관계수", fmt_num(ir.get("roll_corr"), 2),   "수익률 상관"),
            ("추적 오차 (TE)", fmt_pct(ir.get("tracking_err")),    "수익 괴리"),
            ("정보 비율 (IR)", fmt_num(ir.get("info_ratio"), 2),   "초과수익 품질"),
        ]
    elif ct == "Static" and dim == "ND":
        rows = [
            ("HHI",             fmt_num(ir.get("HHI"), 0),          "집중도"),
            ("유효 자산 수",     fmt_num(ir.get("eff_n"), 1),        "분산도"),
            ("Top-3 집중도",     fmt_pct(ir.get("top3_conc")),       "상위 쏠림"),
            ("누적 수익률",      fmt_pct(ir.get("cum_return")),      "분기 합성"),
            ("최대 리스크 기여", ir.get("max_risk_asset") or "—",    "자산명"),
        ]
    elif ct == "Activity" and dim == "1D":
        rows = [
            ("승률",        fmt_pct(ir.get("win_rate")),         "매도 대비"),
            ("수익 팩터",    fmt_num(ir.get("profit_factor"), 2), "손익비"),
            ("총 수수료",    fmt_num(ir.get("total_fee"), 0),     "원"),
            ("거래 횟수",    fmt_num(ir.get("trade_freq"), 0),    "건"),
            ("VWAP 편차",   fmt_num(ir.get("vwap_dev"), 1),      "평균가 대비"),
        ]
    elif ct == "Activity" and dim == "2D":
        rows = [
            ("수수료 비용",   fmt_num(ir.get("fee_cost"), 0),       "원"),
            ("스위칭 비율",   fmt_pct(ir.get("switch_ratio")),      "전환 빈도"),
            ("스위칭 비용",   fmt_num(ir.get("switch_cost"), 0),    "원"),
            ("교차 간격",     fmt_num(ir.get("cross_interval"), 1), "평균 거래일"),
            ("순수익",        fmt_num(ir.get("net_profit"), 0),     "원"),
        ]
    elif ct == "Activity" and dim == "ND":
        rows = [
            ("연간 수수료",   fmt_num(ir.get("annual_fee"), 0),     "원"),
            ("회전율",        fmt_num(ir.get("turnover_rate"), 2),  "배"),
            ("평균 보유기간", fmt_num(ir.get("avg_hold"), 1),       "일"),
            ("실현 손익",     fmt_num(ir.get("realized_pnl"), 0),   "원"),
            ("미실현 손익",   fmt_num(ir.get("unrealized_pnl"), 0), "원"),
        ]
    else:
        rows = [("지표 1", "—", "n/a"), ("지표 2", "—", "n/a"), ("지표 3", "—", "n/a"), ("지표 4", "—", "n/a"), ("지표 5", "—", "n/a")]
    return rows

def _badge_color(val: str, name: str) -> str:
    s = str(val).lower()
    nm = name.lower()
    if "dead" in s: return "#b42318"
    if "golden" in s: return "#1a7f37"
    if "rsi" in nm:
        try:
            v = float(val)
            if v > 70: return "#b42318"
            if v < 30: return "#1a7f37"
            return "#6b7280"
        except Exception: pass
    if "mdd" in nm:
        try:
            v = float(val.replace("%", "")) / 100 if "%" in val else float(val)
            if v < -0.20: return "#b42318"
            if v < -0.10: return "#b54708"
            return "#1a7f37"
        except Exception: pass
    if "샤프" in nm or "sharpe" in nm:
        try:
            v = float(val)
            if v >= 1.0: return "#1a7f37"
            if v >= 0.0: return "#b54708"
            return "#b42318"
        except Exception: pass
    if "hhi" in nm:
        try:
            v = float(val.replace(",", ""))
            if v > 2500: return "#b42318"
            if v > 1500: return "#b54708"
            return "#1a7f37"
        except Exception: pass
    if "top" in nm:
        try:
            v = float(val.replace("%", ""))
            if v > 60: return "#b54708"
            return "#1a7f37"
        except Exception: pass
    # 2D
    if "p-value" in nm or "coint" in nm:
        try:
            v = float(val)
            if v < 0.05: return "#1a7f37"
            if v < 0.10: return "#b54708"
            return "#b42318"
        except Exception: pass
    if "z-score" in nm or "zscore" in nm:
        try:
            v = abs(float(val))
            if v > 2: return "#b42318"
            if v > 1: return "#b54708"
            return "#1a7f37"
        except Exception: pass
    if "롤링 상관" in nm:
        try:
            v = float(val)
            if v > 0.7: return "#1a7f37"
            if v > 0.3: return "#b54708"
            return "#b42318"
        except Exception: pass
    if "헤지" in nm or "β" in nm or "beta" in nm: return "#6b7280"
    if "반감기" in nm or "halflife" in nm:
        try:
            v = float(val)
            if v < 10: return "#1a7f37"
            if v < 30: return "#b54708"
            return "#b42318"
        except Exception: pass
    # ND
    if "평균 상관" in nm:
        try:
            v = float(val)
            if v > 0.7: return "#b42318"
            if v > 0.4: return "#b54708"
            return "#1a7f37"
        except Exception: pass
    if "pca" in nm:
        try:
            v = float(val.replace("%",""))
            if v > 80: return "#b42318"
            if v > 60: return "#b54708"
            return "#1a7f37"
        except Exception: pass
    if "var" in nm:
        try:
            v = abs(float(val.replace("%","")))
            if v > 3:   return "#b42318"
            if v > 1.5: return "#b54708"
            return "#1a7f37"
        except Exception: pass
    if "최대 상관" in nm: return "#6b7280"
    if "누적" in nm or "수익률" in nm:
        try:
            v = float(val.replace("%","")) if "%" in val else float(val)*100
            if v > 10: return "#1a7f37"
            if v > 0:  return "#b54708"
            return "#b42318"
        except Exception: pass
    if "reduce" in s or "위험" in nm: return "#b42318"
    if "buy"    in s or "양호" in nm: return "#1a7f37"
    return "#6b7280"

def _hero_row_html(
    sig: str, conf: int, cr_txt: str, regime: str, action: str, hedge_or_rebal: str, last_title: str,
) -> str:
    esc = html.escape
    pct = max(0, min(100, conf))
    return f"""
<div class="sq-hero-row">
  <div class="sq-hero-cell">
    <div class="sq-hero-cell__label">Live Signal</div>
    <div class="sq-hero-cell__value">{esc(sig)}</div>
    <span class="sq-badge-pos">신뢰도 {pct}%</span>
    <div class="sq-progress"><span style="width:{pct}%"></span></div>
  </div>
  <div class="sq-hero-cell">
    <div class="sq-hero-cell__label">Total Return</div>
    <div class="sq-hero-cell__value">{esc(cr_txt)}</div>
    <div class="sq-hero-cell__body">기간 누적</div>
  </div>
  <div class="sq-hero-cell">
    <div class="sq-hero-cell__label">Risk Regime</div>
    <div class="sq-hero-cell__value">{esc(regime)}</div>
    <div class="sq-hero-cell__body">시장 국면</div>
  </div>
  <div class="sq-hero-cell">
    <div class="sq-hero-cell__label">Suggested Action</div>
    <div class="sq-hero-cell__body">{esc(action)}</div>
  </div>
  <div class="sq-hero-cell">
    <div class="sq-hero-cell__label">{esc(last_title)}</div>
    <div class="sq-hero-cell__body">{esc(hedge_or_rebal)}</div>
  </div>
</div>
"""

from plotly.subplots import make_subplots

def _fig_candlestick(df: pd.DataFrame) -> go.Figure:
    dc = _find_col(df, "date", "datetime", "time", "timestamp")
    # 좀 더 넓은 범위의 후보군 검색
    oc = _find_col(df, "open", "o")
    hc = _find_col(df, "high", "h")
    lc = _find_col(df, "low", "l")
    cc = _find_col(df, "close", "c", "price", "last")
    vc = _find_col(df, "volume", "vol", "v")
    
    # 일부 컬럼이 없으면 파생 생성 시도 (예: Price만 있고 OHLC가 없으면)
    if not (oc and hc and lc and cc) and cc:
        st.warning("일부 OHLC 컬럼이 없어 단일 가격 라인 차트로 대체합니다.")
        fig = go.Figure(go.Scatter(x=df[dc] if dc else df.index, y=df[cc], mode='lines', name="가격"))
        fig.update_layout(height=420, margin=dict(l=30, r=20, t=30, b=30))
        return fig
    
    if not (dc and oc and hc and lc and cc):
        fig = go.Figure()
        fig.add_annotation(text=f"필수 OHLC 컬럼을 찾을 수 없습니다.<br>검색된 컬럼: {list(df.columns)}", 
                           xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return fig
    
    w = df.sort_values(dc)
    
    if vc:
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                           vertical_spacing=0.05, 
                           row_heights=[0.7, 0.3])
        fig.add_trace(go.Candlestick(x=w[dc], open=w[oc], high=w[hc], low=w[lc], close=w[cc], name="가격"), row=1, col=1)
        close = pd.to_numeric(w[cc], errors="coerce")
        fig.add_trace(go.Scatter(x=w[dc], y=close.rolling(20, min_periods=5).mean(), name="MA20", line=dict(color="#2b83ba", width=1)), row=1, col=1)
        vol = pd.to_numeric(w[vc], errors="coerce")
        colors = ['#2ed573' if w[cc].iloc[i] >= w[oc].iloc[i] else '#e74c3c' for i in range(len(w))]
        fig.add_trace(go.Bar(x=w[dc], y=vol, name="거래량", marker_color=colors), row=2, col=1)
        fig.update_layout(height=600)
    else:
        fig = go.Figure(data=[go.Candlestick(x=w[dc], open=w[oc], high=w[hc], low=w[lc], close=w[cc], name="가격")])
        close = pd.to_numeric(w[cc], errors="coerce")
        fig.add_trace(go.Scatter(x=w[dc], y=close.rolling(20, min_periods=5).mean(), name="MA20", line=dict(color="#2b83ba", width=1)))
        fig.update_layout(height=420)

    fig.update_layout(
        xaxis_rangeslider_visible=False,
        margin=dict(l=30, r=20, t=30, b=30),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans, sans-serif"), 
    )
    return fig

def _fig_rsi(df: pd.DataFrame) -> go.Figure:
    dc = _find_col(df, "date", "datetime")
    cc = _find_col(df, "close")
    if not (dc and cc): return go.Figure()
    w = df.sort_values(dc)
    close = pd.to_numeric(w[cc], errors="coerce")
    dlt = close.diff()
    g = dlt.clip(lower=0).ewm(alpha=1 / 14, adjust=False).mean()
    l = (-dlt.clip(upper=0)).ewm(alpha=1 / 14, adjust=False).mean()
    rs = g / l.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    fig = go.Figure(go.Scatter(x=w[dc], y=rsi, name="RSI(14)", line=dict(color="#6a51a3")))
    fig.add_hline(y=70, line_dash="dot", line_color="#b54708")
    fig.add_hline(y=30, line_dash="dot", line_color="#1a7f37")
    fig.update_layout(
        height=260,
        margin=dict(l=30, r=20, t=20, b=30),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans, sans-serif"),
        yaxis=dict(range=[0, 100], fixedrange=True),
    )
    return fig

def _quarter_port_bm(df: pd.DataFrame) -> tuple[list[Any], list[float], list[float]]:
    qc = _find_col(df, "quarter", "date")
    wc, twc, rc = _find_col(df, "weight"), _find_col(df, "target_weight"), _find_col(df, "return")
    xs, pr, br = [], [], []
    if not (qc and wc and rc): return xs, pr, br
    for q, part in df.groupby(qc, sort=True):
        wv = pd.to_numeric(part[wc], errors="coerce").fillna(0)
        rv = pd.to_numeric(part[rc], errors="coerce").fillna(0)
        xs.append(q)
        pr.append(float((wv * rv).sum()))
        if twc and twc in part.columns:
            tv = pd.to_numeric(part[twc], errors="coerce").fillna(0)
            br.append(float((tv * rv).sum()))
        else:
            br.append(pr[-1])
    return xs, pr, br

def _fig_static_dual(df: pd.DataFrame) -> go.Figure:
    xs, pr, br = _quarter_port_bm(df)
    fig = go.Figure()
    if not xs:
        fig.add_annotation(text="분기·수익 데이터가 필요합니다", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return fig
    cpr = np.cumprod(np.array(pr, dtype=float) + 1.0) - 1.0
    cbr = np.cumprod(np.array(br, dtype=float) + 1.0) - 1.0
    fig.add_trace(go.Scatter(x=xs, y=cpr, name="포트폴리오", line=dict(color="#0a5c5c", width=2.5)))
    fig.add_trace(go.Scatter(x=xs, y=cbr, name="벤치마크(목표)", line=dict(color="#2ed573", width=2.5)))
    fig.update_layout(
        height=420,
        margin=dict(l=30, r=20, t=30, b=30),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans, sans-serif"),
    )
    return fig

def _fig_excess_bar(df: pd.DataFrame) -> go.Figure:
    xs, pr, br = _quarter_port_bm(df)
    if not xs: return go.Figure()
    ex = (np.array(pr) - np.array(br)) * 100.0
    fig = go.Figure(go.Bar(x=xs, y=ex, marker_color=np.where(ex >= 0, "#0a5c5c", "#e74c3c")))
    fig.update_layout(
        title=dict(text="분기 초과수익률 (%p)", font=dict(size=14, color="#1a2d30")),
        height=260,
        margin=dict(l=30, r=20, t=40, b=30),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans, sans-serif"),
    )
    return fig

def _fig_weight_drift(df: pd.DataFrame) -> go.Figure:
    qc, ac, wc, twc = _find_col(df, "quarter", "date"), _find_col(df, "asset_name", "asset"), _find_col(df, "weight"), _find_col(df, "target_weight")
    if not (qc and ac and wc and twc): return go.Figure()
    last_q = df.sort_values(qc)[qc].iloc[-1]
    part = df[df[qc] == last_q]
    drift = (pd.to_numeric(part[wc], errors="coerce") - pd.to_numeric(part[twc], errors="coerce")) * 100.0
    fig = go.Figure(go.Bar(x=part[ac].astype(str), y=drift, marker_color=np.where(drift.values >= 0, "#0a5c5c", "#2ed573")))
    fig.update_layout(
        title=dict(text=f"비중 괴리율 (%p) — {last_q}", font=dict(size=14, color="#1a2d30")),
        height=260,
        margin=dict(l=30, r=20, t=40, b=30),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans, sans-serif"),
    )
    return fig

def _render_market(mkt_data: list) -> str:
    if not mkt_data: return '<p style="font-size:0.82rem;color:var(--sq-muted);margin:4px 0">yfinance not installed</p>'
    rows = []
    for item in mkt_data:
        if item.get("price") is None: continue
        chg = item["change"]
        arrow = "▲" if chg >= 0 else "▼"
        color = "#1a7f37" if chg >= 0 else "#b42318"
        price_str = f"{item['price']:,.0f}" if item["name"] in ("KOSPI", "USD/KRW") else f"{item['price']:,.2f}"
        rows.append(
            f'<div class="sq-mkt-item">'
            f'<span class="sq-mkt-name">{html.escape(item["name"])}</span>'
            f'<span class="sq-mkt-val" style="color:{color}">{arrow} {price_str} <small>({chg:+.2f}%)</small></span></div>'
        )
    return "".join(rows)

def _sparkline_svg(hist: list, up: bool, width: int = 80, height: int = 32) -> str:
    """hist 값 리스트로 인라인 SVG 스파크라인 생성."""
    if not hist or len(hist) < 2:
        return ""
    mn, mx = min(hist), max(hist)
    rng = mx - mn or 1
    pts = []
    for i, v in enumerate(hist):
        x = i / (len(hist) - 1) * width
        y = height - ((v - mn) / rng * (height - 4) + 2)
        pts.append(f"{x:.1f},{y:.1f}")
    color = "#1dd1a1" if up else "#e74c3c"
    fill_color = "rgba(29,209,161,0.15)" if up else "rgba(228,76,60,0.15)"
    poly = " ".join(pts)
    area_pts = f"0,{height} {poly} {width},{height}"
    return (
        f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
        f'xmlns="http://www.w3.org/2000/svg" style="display:block">'
        f'<polygon points="{area_pts}" fill="{fill_color}"/>'
        f'<polyline points="{poly}" fill="none" stroke="{color}" '
        f'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>'
        f'</svg>'
    )


def _fig_ts_dual_line(df: pd.DataFrame, theme: str = "light") -> go.Figure:
    """TimeSeries 2D: 두 종목 정규화 라인 차트."""
    is_dark = (theme == "dark")
    bg  = "#1e252e" if is_dark else "#fafbfb"
    txt = "#f0f7f5" if is_dark else "#1a2d30"
    grd = "#313d4a" if is_dark else "#dde3e8"

    date_c   = _find_col(df, "date", "datetime", "time")
    ticker_c = _find_col(df, "ticker", "symbol", "code")
    close_c  = _find_col(df, "close", "adj_close", "price")

    fig = go.Figure()
    if not (ticker_c and close_c):
        fig.add_annotation(text="Ticker/Close 컬럼이 필요합니다",
                           xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return fig

    colors = ["#0a5c5c", "#1dd1a1"]
    for i, ticker in enumerate(df[ticker_c].dropna().unique()[:2]):
        sub = df[df[ticker_c] == ticker]
        if date_c:
            sub = sub.sort_values(date_c)
        c = pd.to_numeric(sub[close_c], errors="coerce")
        norm = c / c.iloc[0] * 100  # 100 기준 정규화
        x = sub[date_c] if date_c else sub.index
        fig.add_trace(go.Scatter(
            x=x, y=norm, name=_ticker_to_name(str(ticker)),
            line=dict(color=colors[i % len(colors)], width=2.5)
        ))

    fig.update_layout(
        height=420, margin=dict(l=30, r=20, t=30, b=30),
        paper_bgcolor=bg, plot_bgcolor=bg,
        font=dict(family="DM Sans, sans-serif", color=txt),
        xaxis=dict(gridcolor=grd), yaxis=dict(gridcolor=grd),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        yaxis_title="정규화 (시작=100)",
    )
    return fig


def _fig_zscore(df: pd.DataFrame, indicator_result: dict, theme: str = "light") -> go.Figure:
    """TimeSeries 2D 서브: Z-score 시계열."""
    is_dark = (theme == "dark")
    bg  = "#1e252e" if is_dark else "#fafbfb"
    txt = "#f0f7f5" if is_dark else "#1a2d30"

    ticker_c = _find_col(df, "ticker", "symbol", "code")
    date_c   = _find_col(df, "date", "datetime", "time")
    close_c  = _find_col(df, "close", "adj_close", "price")

    fig = go.Figure()
    if not (ticker_c and close_c):
        return fig

    tickers = df[ticker_c].dropna().unique()
    if len(tickers) < 2:
        return fig

    t1, t2 = tickers[0], tickers[1]
    def get_close(t):
        sub = df[df[ticker_c] == t]
        if date_c:
            sub = sub.sort_values(date_c)
        return pd.to_numeric(sub[close_c], errors="coerce").reset_index(drop=True),                (sub[date_c].reset_index(drop=True) if date_c else None)

    c1, dates = get_close(t1)
    c2, _     = get_close(t2)
    beta = indicator_result.get("beta") or 1.0
    spread = c1 - beta * c2
    window = 60
    s_mean = spread.rolling(window, min_periods=5).mean()
    s_std  = spread.rolling(window, min_periods=5).std()
    zscore = (spread - s_mean) / s_std.replace(0, np.nan)

    x = dates if dates is not None else zscore.index
    fig.add_trace(go.Scatter(x=x, y=zscore, name="Z-score",
                             line=dict(color="#6a51a3", width=2)))
    fig.add_hline(y=2,  line_dash="dot", line_color="#b54708")
    fig.add_hline(y=-2, line_dash="dot", line_color="#1a7f37")
    fig.add_hline(y=0,  line_dash="dash", line_color="#7a8f94", line_width=0.8)

    fig.update_layout(
        height=260, margin=dict(l=30, r=20, t=20, b=30),
        paper_bgcolor=bg, plot_bgcolor=bg,
        font=dict(family="DM Sans, sans-serif", color=txt),
    )
    return fig


def _fig_rolling_corr(df: pd.DataFrame, theme: str = "light") -> go.Figure:
    """TimeSeries 2D 서브: 롤링 상관계수."""
    is_dark = (theme == "dark")
    bg  = "#1e252e" if is_dark else "#fafbfb"
    txt = "#f0f7f5" if is_dark else "#1a2d30"
    grd = "#313d4a" if is_dark else "#dde3e8"

    ticker_c = _find_col(df, "ticker", "symbol", "code")
    date_c   = _find_col(df, "date", "datetime", "time")
    close_c  = _find_col(df, "close", "adj_close", "price")

    fig = go.Figure()
    if not (ticker_c and close_c):
        return fig

    tickers = df[ticker_c].dropna().unique()
    if len(tickers) < 2:
        return fig

    def get_ret(t):
        sub = df[df[ticker_c] == t]
        if date_c:
            sub = sub.sort_values(date_c)
        c = pd.to_numeric(sub[close_c], errors="coerce").reset_index(drop=True)
        return c.pct_change().dropna().reset_index(drop=True),                (sub[date_c].iloc[1:].reset_index(drop=True) if date_c else None)

    r1, dates = get_ret(tickers[0])
    r2, _     = get_ret(tickers[1])
    min_len = min(len(r1), len(r2))
    r1, r2  = r1.iloc[:min_len], r2.iloc[:min_len]
    roll_corr = r1.rolling(60, min_periods=10).corr(r2)

    x = dates.iloc[:min_len] if dates is not None else roll_corr.index
    fig.add_trace(go.Scatter(x=x, y=roll_corr, name="Rolling Corr (60d)",
                             line=dict(color="#0a5c5c", width=2)))
    fig.add_hline(y=0.5, line_dash="dot", line_color="#b54708")

    fig.update_layout(
        height=260, margin=dict(l=30, r=20, t=20, b=30),
        paper_bgcolor=bg, plot_bgcolor=bg,
        font=dict(family="DM Sans, sans-serif", color=txt),
        xaxis=dict(gridcolor=grd), yaxis=dict(gridcolor=grd, range=[-1, 1]),
    )
    return fig


def _fig_corr_heatmap(df: pd.DataFrame, theme: str = "light") -> go.Figure:
    """TimeSeries ND: 상관계수 히트맵."""
    is_dark = (theme == "dark")
    bg  = "#1e252e" if is_dark else "#fafbfb"
    txt = "#f0f7f5" if is_dark else "#1a2d30"
    ticker_c = _find_col(df, "ticker", "symbol", "code")
    date_c   = _find_col(df, "date", "datetime", "time")
    close_c  = _find_col(df, "close", "adj_close", "price")
    fig = go.Figure()
    if not (ticker_c and close_c):
        fig.add_annotation(text="Ticker/Close 컬럼이 필요합니다",
                           xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return fig
    ret_dict = {}
    for t in df[ticker_c].dropna().unique():
        sub = df[df[ticker_c] == t]
        if date_c:
            sub = sub.sort_values(date_c)
        c = pd.to_numeric(sub[close_c], errors="coerce").reset_index(drop=True)
        ret_dict[str(t)] = c.pct_change().dropna().reset_index(drop=True)
    ret_df    = pd.DataFrame(ret_dict).dropna()
    corr_mat  = ret_df.corr()
    str_labels = [_ticker_to_name(str(l)) for l in corr_mat.columns]
    fig.add_trace(go.Heatmap(
        z=corr_mat.values,
        x=str_labels, y=str_labels,
        colorscale=[[0, "#e74c3c"], [0.5, "#f7f9fb"], [1, "#0a5c5c"]],
        zmin=-1, zmax=1,
        text=[[f"{v:.2f}" for v in row] for row in corr_mat.values],
        texttemplate="%{text}",
        textfont=dict(size=11),
        showscale=True, xgap=2, ygap=2,
    ))
    fig.update_layout(
        height=420, margin=dict(l=80, r=20, t=30, b=80),
        paper_bgcolor=bg, plot_bgcolor=bg,
        font=dict(family="DM Sans, sans-serif", color=txt),
        xaxis=dict(type="category", tickfont=dict(size=10), tickangle=-30),
        yaxis=dict(type="category", tickfont=dict(size=10), autorange="reversed"),
    )
    return fig
def _fig_network(df: pd.DataFrame, indicator_result: dict, theme: str = "light") -> go.Figure:
    """TimeSeries ND: 네트워크 그래프
    - 상관계수 높을수록 노드가 가깝게 배치 (force-directed)
    - Z-score |z| > 2 인 쌍 → 빨간 엣지 (페어트레이딩 진입 신호)
    - 그 외 상관 > threshold 쌍 → 틸 엣지
    - ticker 앞자리 0 복원 (e.g. 5380 → 005380)
    """
    is_dark  = (theme == "dark")
    bg       = "#1e252e" if is_dark else "#fafbfb"
    txt      = "#f0f7f5" if is_dark else "#1a2d30"
    ticker_c = _find_col(df, "ticker", "symbol", "code")
    close_c  = _find_col(df, "close", "adj_close", "price")
    date_c   = _find_col(df, "date", "datetime", "time")

    fig = go.Figure()
    if not (ticker_c and close_c):
        return fig

    raw_tickers = [str(t) for t in df[ticker_c].dropna().unique()]
    n = len(raw_tickers)
    if n < 2:
        return fig

    display = {t: _ticker_to_name(t) for t in raw_tickers}

    # 수익률 계산 + 최근 종가 수집
    ret_dict     = {}
    latest_price = {}
    for t in raw_tickers:
        sub = df[df[ticker_c].astype(str) == t]
        if date_c:
            sub = sub.sort_values(date_c)
        c = pd.to_numeric(sub[close_c], errors="coerce").reset_index(drop=True)
        latest_price[t] = float(c.iloc[-1]) if len(c) > 0 else 0.0
        ret_dict[t]     = c.pct_change().dropna().reset_index(drop=True)

    ret_df   = pd.DataFrame(ret_dict).dropna()
    corr_mat = ret_df.corr()

    # ── 쌍별 Z-score 계산 ──
    # spread = close_t1 - beta * close_t2, Z = (spread - mean) / std (60일 롤링)
    def pair_zscore(t1: str, t2: str) -> float:
        sub1 = df[df[ticker_c].astype(str) == t1]
        sub2 = df[df[ticker_c].astype(str) == t2]
        if date_c:
            sub1 = sub1.sort_values(date_c)
            sub2 = sub2.sort_values(date_c)
        c1 = pd.to_numeric(sub1[close_c], errors="coerce").reset_index(drop=True)
        c2 = pd.to_numeric(sub2[close_c], errors="coerce").reset_index(drop=True)
        min_len = min(len(c1), len(c2))
        if min_len < 20:
            return 0.0
        c1, c2 = c1.iloc[:min_len], c2.iloc[:min_len]
        r1 = c1.pct_change().dropna()
        r2 = c2.pct_change().dropna()
        min_r = min(len(r1), len(r2))
        r1, r2 = r1.iloc[:min_r].values, r2.iloc[:min_r].values
        denom = float(np.dot(r2 - r2.mean(), r2 - r2.mean())) + 1e-12
        beta  = float(np.dot(r2 - r2.mean(), r1 - r1.mean())) / denom
        spread = c1 - beta * c2
        window = min(60, len(spread))
        s_mean = spread.rolling(window, min_periods=10).mean().iloc[-1]
        s_std  = spread.rolling(window, min_periods=10).std().iloc[-1]
        if not s_std or s_std < 1e-10:
            return 0.0
        return float((spread.iloc[-1] - s_mean) / s_std)

    import networkx as nx
    threshold = 0.5

    # ── 3D Force-directed 배치 (상관계수 기반) ──
    G = nx.Graph()
    for t in raw_tickers:
        G.add_node(t)
    
    for i, t1 in enumerate(raw_tickers):
        for j, t2 in enumerate(raw_tickers):
            if j <= i: continue
            try:
                corr_val = float(corr_mat.loc[t1, t2])
            except: corr_val = 0.0
            if abs(corr_val) > threshold:
                G.add_edge(t1, t2, weight=abs(corr_val))
    
    # 3D 위치 계산
    pos_3d = nx.spring_layout(G, dim=3, seed=42)
    pos = {t: np.array(pos_3d.get(t, [0, 0, 0]), dtype=float) for t in raw_tickers}

    # ── 엣지 렌더링 (3D) ──
    edge_count = 0
    for i, t1 in enumerate(raw_tickers):
        for j, t2 in enumerate(raw_tickers):
            if j <= i: continue
            try:
                corr_val = float(corr_mat.loc[t1, t2])
            except: continue
            if not np.isfinite(corr_val) or abs(corr_val) <= threshold: continue

            z = pair_zscore(t1, t2)
            color = "rgba(231,76,60,0.85)" if abs(z) > 2 else "rgba(10,92,92,0.75)"
            label = f"{display[t1]}↔{display[t2]}: corr={corr_val:.2f} | Z={z:.2f}"

            x0, y0, z0 = pos[t1]
            x1, y1, z1 = pos[t2]
            
            fig.add_trace(go.Scatter3d(
                x=[x0, x1], y=[y0, y1], z=[z0, z1],
                mode="lines",
                line=dict(color=color, width=max(2, abs(corr_val) * 8)),
                hoverinfo="text",
                text=label,
                showlegend=False,
            ))
            edge_count += 1

    # ── 노드 렌더링 (3D) ──
    centrality  = indicator_result.get("centrality") or {}
    node_x = [pos[t][0] for t in raw_tickers]
    node_y = [pos[t][1] for t in raw_tickers]
    node_z = [pos[t][2] for t in raw_tickers]
    
    # 노드별 고유 색상 할당
    node_colors = [_DEFAULT_COLORS[i % len(_DEFAULT_COLORS)] for i in range(len(raw_tickers))]
    node_size = [30 + centrality.get(t, 0) * 40 for t in raw_tickers]
    node_labels = [display[t] for t in raw_tickers]
    
    fig.add_trace(go.Scatter3d(
        x=node_x, y=node_y, z=node_z,
        mode="markers+text",
        marker=dict(
            size=node_size,
            color=node_colors,
            opacity=0.95,
            line=dict(color='white', width=2)
        ),
        text=node_labels,
        textposition="top center",
        textfont=dict(color=txt, size=14, weight='bold'),
        hoverinfo="text",
        hovertext=[f"<b>{display[t]}</b><br>현재가: {latest_price.get(t,0):,.0f}" for t in raw_tickers]
    ))
    
    fig.update_layout(
        scene=dict(
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, visible=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, visible=False),
            zaxis=dict(showgrid=False, zeroline=False, showticklabels=False, visible=False),
            bgcolor=bg
        ),
        margin=dict(l=0, r=0, b=0, t=0),
        showlegend=False
    )
    return fig

def _render_home_charts(mkt_data: list, theme: str = "light") -> None:
    """홈 화면: 시장 지표 카드 + 카드 바로 아래 [선택] 버튼."""
    if not mkt_data:
        st.info("시장 데이터를 불러오는 중...")
        return
    is_dark = (theme == "dark")
    if "selected_indices" not in st.session_state:
        st.session_state.selected_indices = [m["name"] for m in mkt_data[:6]]
    selected   = list(st.session_state.selected_indices)
    MAX_SELECT = 6
    bg_sel   = "#0a1a1a" if is_dark else "#eef7f4"
    bg_idle  = "#1e222d" if is_dark else "#f7f9fb"
    bd_sel   = "#0a5c5c"
    bd_idle  = "#2a2e39" if is_dark else "#dde3e8"
    tx_price = "#f4faf9" if is_dark else "#1a2d30"
    tx_muted = "#7a8f94"
    tx_sel   = "#1dd1a1"
    st.markdown("""
<style>
.mkt-sel-btn .stButton > button {
    height:26px!important;min-height:26px!important;
    padding:0 12px!important;font-size:0.7rem!important;
    font-weight:600!important;border-radius:999px!important;
    transition:all 0.15s ease!important;width:auto!important;
}
.mkt-sel-btn.sel .stButton > button {
    background:#0a5c5c!important;color:#ffffff!important;
    border-color:#0a5c5c!important;
}
.mkt-sel-btn.idle .stButton > button {
    background:transparent!important;color:#0a5c5c!important;
    border:1.5px solid #0a5c5c!important;
}
</style>
""", unsafe_allow_html=True)
    if len(selected) >= MAX_SELECT:
        st.markdown(
            '<p style="font-size:0.78rem;color:#b54708;margin-bottom:8px">'
            f"⚠ 최대 {MAX_SELECT}개까지 선택 가능합니다.</p>",
            unsafe_allow_html=True,
        )
    rows = [mkt_data[i:i+3] for i in range(0, len(mkt_data), 3)]
    for row in rows:
        cols = st.columns(3, gap="small")
        for col, item in zip(cols, row):
            name   = item["name"]
            price  = item.get("price")
            chg    = item.get("change", 0.0)
            hist   = item.get("hist", [])
            up     = chg >= 0
            is_sel = name in selected
            safe   = name.replace(" ", "_").replace("/", "_")
            price_str = (
                f"{price:,.0f}" if name in ("KOSPI", "USD/KRW", "Nikkei 225")
                else f"{price:,.2f}" if price is not None
                else "—"
            )
            arrow     = "▲" if up else "▼"
            chg_color = tx_sel if up else "#e74c3c"
            nc        = tx_sel if is_sel else tx_muted
            dot       = (
                '<span style="width:8px;height:8px;border-radius:50%;background:#1dd1a1;'
                'display:inline-block;margin-right:6px;flex-shrink:0"></span>'
            ) if is_sel else ""
            bg     = bg_sel if is_sel else bg_idle
            border = f"2px solid {bd_sel}" if is_sel else f"1.5px solid {bd_idle}"
            shadow = "0 0 16px rgba(10,92,92,0.22)" if is_sel else "none"
            spark  = _sparkline_svg(hist, up)
            with col:
                st.markdown(
                    f'<div style="background:{bg};border:{border};box-shadow:{shadow};'
                    f'border-radius:14px;padding:16px 14px;display:flex;'
                    f'flex-direction:column;gap:8px;margin-bottom:6px">'
                    f'<div style="display:flex;align-items:center;justify-content:space-between">'
                    f'<div style="display:flex;align-items:center">'
                    f'{dot}'
                    f'<span style="font-size:0.7rem;font-weight:700;letter-spacing:0.06em;'
                    f'text-transform:uppercase;color:{nc}">{html.escape(name)}</span></div>'
                    f'<span style="font-size:0.75rem;font-weight:700;color:{chg_color}">'
                    f'{arrow} {abs(chg):.2f}%</span></div>'
                    f'<div style="font-size:1.35rem;font-weight:700;color:{tx_price};'
                    f'letter-spacing:-0.02em">{price_str}</div>'
                    f'<div>{spark}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
                btn_label = "✓ 선택됨" if is_sel else "+ 선택"
                cls       = "sel" if is_sel else "idle"
                st.markdown(f'<div class="mkt-sel-btn {cls}">', unsafe_allow_html=True)
                clicked = st.button(btn_label, key=f"mkt_{safe}", use_container_width=False)
                st.markdown("</div>", unsafe_allow_html=True)
                if clicked:
                    if name in selected:
                        st.session_state.selected_indices = [n for n in selected if n != name]
                    elif len(selected) < MAX_SELECT:
                        st.session_state.selected_indices = selected + [name]
                    st.rerun()



def _calculate_trading_bias(df: pd.DataFrame) -> tuple[int, str, str]:
    """10개의 기술적 지표를 앙상블하여 Trading Bias(0~100%)와 라벨을 반환합니다."""
    if df is None or df.empty: return 50, "Neutral", "var(--sq-warn)"
    
    dc = _find_col(df, "date", "datetime")
    cc = _find_col(df, "close")
    if not cc: return 50, "Neutral", "var(--sq-warn)"

    w = df.sort_values(dc) if dc else df.copy()
    close = pd.to_numeric(w[cc], errors="coerce").ffill()
    
    # 데이터가 부족하면 기본값 반환
    if len(close) < 60: return 50, "Neutral", "var(--sq-warn)"

    score, max_score = 0, 10
    c_last = close.iloc[-1]

    try:
        # 1. 단기 추세: 현재가 > MA20
        if c_last > close.rolling(20).mean().iloc[-1]: score += 1
        # 2. 장기 추세: 현재가 > MA60
        if c_last > close.rolling(60).mean().iloc[-1]: score += 1
        # 3. 배열 상태: MA20 > MA60 (정배열)
        if close.rolling(20).mean().iloc[-1] > close.rolling(60).mean().iloc[-1]: score += 1
        
        # 4. 모멘텀: RSI(14) > 50
        dlt = close.diff()
        g = dlt.clip(lower=0).ewm(alpha=1/14, adjust=False).mean()
        l = (-dlt.clip(upper=0)).ewm(alpha=1/14, adjust=False).mean()
        rs = g / l.replace(0, np.nan)
        rsi = 100 - (100 / (1 + rs))
        if rsi.iloc[-1] > 50: score += 1
        
        # 5. MACD 오실레이터: MACD > 0
        ema12 = close.ewm(span=12, adjust=False).mean()
        ema26 = close.ewm(span=26, adjust=False).mean()
        macd = ema12 - ema26
        if macd.iloc[-1] > 0: score += 1
        # 6. MACD 시그널 돌파: MACD > Signal(9)
        if macd.iloc[-1] > macd.ewm(span=9, adjust=False).mean().iloc[-1]: score += 1
        
        # 7. 단기 과열: 현재가 > MA5
        if c_last > close.rolling(5).mean().iloc[-1]: score += 1
        # 8. 주간 수익: 5일 전 대비 상승
        if c_last > close.iloc[-6]: score += 1
        # 9. 일간 수익: 전일 대비 상승
        if c_last > close.iloc[-2]: score += 1

        # 10. 거래량 활성: 현재 거래량 > MA20 거래량
        vc = _find_col(df, "volume")
        if vc:
            vol = pd.to_numeric(w[vc], errors="coerce").fillna(0)
            if vol.iloc[-1] > vol.rolling(20).mean().iloc[-1]: score += 1
        else:
            max_score -= 1 # 거래량 컬럼이 없으면 9점 만점으로 조정
            
    except Exception:
        pass

    # 최종 점수 환산 및 컬러 배정
    pct = int((score / max_score) * 100)
    if pct >= 60: return pct, "Bullish", "var(--sq-mint)"
    if pct <= 40: return pct, "Bearish", "var(--sq-danger)"
    return pct, "Neutral", "var(--sq-warn)"

def build(
    view: str,
    classify_result: dict | None,
    indicator_result: dict | None,
    chart_result: dict | None,
    insight_result: dict | None,
    df: pd.DataFrame | None,
    mkt_data: list | None = None,
    theme: str = "light",
) -> None:
    mkt_data = mkt_data or []

    if view == "home":
        st.markdown("""
        <div style="background:rgba(10,92,92,0.15); padding:16px 20px; border-radius:10px; border-left:4px solid var(--sq-teal); margin-bottom:28px; box-shadow: var(--sq-shadow);">
            <strong style="color:var(--sq-teal); font-size:1.1rem;">✦</strong> <span style="color:var(--sq-text)">오늘 시장은 기술주 중심의 강한 반등세가 이어지며 <strong>위험 자산 선호(Risk-On)</strong> 국면입니다.</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(
            '<h2 style="font-size:1.5rem;font-weight:800;color:var(--sq-text);margin-bottom:4px">Market Overview</h2>'
            '<p style="color:var(--sq-muted);font-size:0.88rem;margin-bottom:20px">Real-time global market indicators</p>',
            unsafe_allow_html=True,
        )
        
        _render_home_charts(mkt_data, theme=theme)

                # 3. 드래그 앤 드롭 업로드 영역 (CSS로 파일 업로더 자체에 점선 박스 씌우기)
        st.markdown("""
        <style>
        /* 파일 업로더 전체 영역에 점선 테두리와 여백 주기 */
        [data-testid="stFileUploader"] {
            border: 2px dashed var(--sq-teal);
            padding: 35px 20px;
            border-radius: 14px;
            margin-top: 30px;
            background-color: transparent;
        }
        /* 파일 업로더의 기본 라벨(제목)을 크고 가운데 정렬되게 꾸미기 */
        [data-testid="stFileUploader"] > label {
            display: flex;
            justify-content: center;
            font-size: 1.3rem !important;
            font-weight: 800 !important;
            color: var(--sq-teal) !important;
            margin-bottom: 15px;
        }
        </style>
        """, unsafe_allow_html=True)

        # 숨겨두었던 라벨(label_visibility) 옵션을 빼고 제목을 직접 넣어줍니다.
        uploaded_main = st.file_uploader(
            "📂 분석할 포트폴리오/종목 CSV를 아래에 드래그하세요", 
            type=["csv"], 
            key="main_csv_upload"
        )
        
        if uploaded_main:
            import pandas as pd
            try:
                st.session_state['saved_df'] = pd.read_csv(uploaded_main) 
                st.session_state.fin_view = "main"
                st.rerun()
            except pd.errors.EmptyDataError:
                st.error("Error: The uploaded file is empty.")
            except Exception as e:
                st.error(f"Error reading file: {e}")
        return
    
    if classify_result is None or df is None:
        mc, rc = st.columns([74, 26], gap="medium")
        with mc:
            st.markdown('''
<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:60vh;color:var(--sq-muted);text-align:center;gap:12px">
  <div style="font-size:3rem">📂</div>
  <div style="font-size:1.1rem;font-weight:700;color:var(--sq-text)">Upload a CSV to get started</div>
  <div style="font-size:0.88rem">Use the sidebar to upload your investment data</div>
</div>''', unsafe_allow_html=True)
        selected_names = st.session_state.get("selected_indices", [m["name"] for m in mkt_data[:6]])
        filtered_mkt   = [m for m in mkt_data if m["name"] in selected_names]
        with rc:
            st.markdown(
                '<div class="sq-rail" style="margin-bottom:10px"><div class="sq-rail-section"><div class="sq-rail-title">Market Indicators</div>'
                + _render_market(filtered_mkt) + '</div></div>', unsafe_allow_html=True)
        return

    dash   = classify_result["dashboard"]
    engine = (view == "engine")
    events = _detect_events(df, classify_result, indicator_result)

    mc, rc = st.columns([74, 26], gap="medium")

    selected_names = st.session_state.get("selected_indices", [m["name"] for m in mkt_data[:6]])
    filtered_mkt   = [m for m in mkt_data if m["name"] in selected_names]

    with rc:
        st.markdown(
            '<div class="sq-rail" style="margin-bottom:10px"><div class="sq-rail-section"><div class="sq-rail-title">Market Indicators</div>'
            + _render_market(filtered_mkt) + '</div></div>', unsafe_allow_html=True)

        feed_items = ""
        if not events:
            feed_items = '<p style="font-size:0.82rem;color:var(--sq-muted);margin:4px 0">No events detected</p>'
        else:
            for ev in events:
                feed_items += (
                    f'<div class="sq-feed-item" style="border-left:4px solid {ev["color"]}">'
                    f'<b style="color:var(--sq-text);font-size:0.84rem">{html.escape(ev["label"])}</b><br/>'
                    f'<small style="color:var(--sq-muted)">{html.escape(str(ev["date"]))}</small></div>'
                )

        active_goals = set(classify_result["goals"])
        goals_html = ""
        for g, (title, _desc) in _GOAL_META.items():
            on = g in active_goals
            icon = '✦' if on else '○'
            goals_html += f'<span class="sq-goal-chip {"sq-goal-on" if on else "sq-goal-off" }"><span style="font-size:0.7rem">{icon}</span> {title}</span>'

        if classify_result["class_type"] == "TimeSeries":
            pct, label, color = _calculate_trading_bias(df)
            deg = 180 * (pct / 100)
            bias_html = f'''
            <div style="position:relative; width:160px; height:80px; overflow:hidden; margin: 15px auto 5px;">
                <div style="position:absolute; bottom:0; left:0; width:160px; height:80px; border-radius: 160px 160px 0 0; background: conic-gradient(from 270deg, {color} 0deg, {color} {deg}deg, rgba(128,128,128,0.15) {deg}deg, rgba(128,128,128,0.15) 180deg);">
                    <div style="position:absolute; bottom:0; left:50%; transform:translateX(-50%); width:128px; height:64px; border-radius: 128px 128px 0 0; background: var(--sq-surface);"></div>
                </div>
            </div>
            <div style="text-align:center; padding-bottom:10px;">
                <div style="font-size:2rem; font-weight:800; color:{color}; line-height:1;">{pct}%</div>
                <div style="font-size:0.85rem; font-weight:700; color:{color}; letter-spacing:0.05em; text-transform:uppercase; margin-top:4px;">{label}</div>
            </div>
            '''
        else:
            bias_html = '<p style="font-size:0.82rem;color:var(--sq-muted);text-align:center;margin:20px 0;">시계열 데이터 전용</p>'

        st.markdown(
            f'<div class="sq-rail"><div class="sq-rail-section"><div class="sq-rail-title">① Auto Events</div><div class="sq-feed-scroll">{feed_items}</div></div>'
            f'<div class="sq-rail-section" style="margin-top:16px"><div class="sq-rail-title">② Analysis Goals</div><div style="display:flex;flex-wrap:wrap;gap:4px;line-height:2">{goals_html}</div></div>'
            f'<div class="sq-rail-section" style="margin-top:16px"><div class="sq-rail-title">③ Trading Bias</div>{bias_html}</div></div>',
            unsafe_allow_html=True,
        )

        query = _get_dynamic_query(classify_result, indicator_result, df)
        news_items = _render_news(query)
        st.markdown(
            f'''
            <div class="sq-rail" style="margin-top:16px">
                <div class="sq-rail-section">
                    <div class="sq-rail-title">④ Contextual News</div>
                    <div style="margin-bottom:8px;">
                        <span class="sq-ac-badge" style="font-size:0.65rem; background:rgba(29,209,161,0.1); color:var(--sq-mint);">
                            Topic: {query}
                        </span>
                    </div>
                    <div class="sq-feed-scroll">
                        {news_items}
                    </div>
                </div>
            </div>
            ''', 
            unsafe_allow_html=True
        )

    with mc:
        if engine:
            st.markdown(f'''
<div class="sq-eng-section">
<div class="sq-eng-section-title">① Analysis Pipeline</div>
<div class="sq-pipe-row">
  <div class="sq-pipe-step s1">18D Vector<br><small style="font-weight:400;color:var(--sq-muted)">Column scan</small></div>
  <span class="sq-pipe-arrow a1">→</span>
  <div class="sq-pipe-step s2">Class<br><small style="font-weight:400;color:var(--sq-muted)">Cosine similarity</small></div>
  <span class="sq-pipe-arrow a2">→</span>
  <div class="sq-pipe-step s3">Dimension<br><small style="font-weight:400;color:var(--sq-muted)">Ticker count</small></div>
  <span class="sq-pipe-arrow a3">→</span>
  <div class="sq-pipe-step s4 sq-pipe-result">Visualization<br><small style="font-weight:400">Auto render</small></div>
</div>
<div style="margin-top:12px;padding:10px 14px;background:rgba(10,92,92,0.15);border-radius:8px;font-family:monospace;font-size:0.82rem;color:var(--sq-mint)">
Result: <b style="color:var(--sq-text)">{classify_result["class_type"]}</b> / <b style="color:var(--sq-text)">{classify_result["dimension"]}</b> / dashboard: <b style="color:var(--sq-text)">{classify_result["dashboard"]}</b>
</div></div>''', unsafe_allow_html=True)

            active_goals = set(classify_result["goals"])
            chips_html = ""
            reasons_html = ""
            for g, (title, _desc) in _GOAL_META.items():
                if g in active_goals:
                    chips_html += f'<span class="sq-goal-chip sq-goal-on">✦ {title}</span>'
                    mock_reason = "관련 데이터 특성 및 차원 패턴 감지됨"
                    if "trend" in g: mock_reason = "시계열(Date/Close) 패턴 감지"
                    elif "comp" in g: mock_reason = "자산명(Asset) 및 비중(Weight) 벡터 동시 감지"
                    elif "compare" in g: mock_reason = "목표(Target) 대비 실제(Actual) 비중 수치 포착"
                    elif "anomaly" in g: mock_reason = "비중 괴리 또는 과매수/과매도 위험 감지"
                    reasons_html += f'<div style="margin-bottom: 5px; color:var(--sq-text);"><b>[{title}]</b> ← {mock_reason}</div>'
                else:
                    chips_html += f'<span class="sq-goal-chip sq-goal-off">○ {title}</span>'

            if not reasons_html: reasons_html = "<div style='color:var(--sq-text);'>감지된 주요 분석 목적 없음</div>"
            llm_preview = html.escape(str(insight_result.get("llm_input", "System standby...")))

            st.markdown(f'''
<div class="sq-eng-section">
  <div class="sq-eng-section-title">② Goal Inference</div>
  <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 16px;">{chips_html}</div>
  <div style="background: var(--sq-bg); border-left: 3px solid var(--sq-teal); padding: 12px 16px; margin-bottom: 16px; font-size: 0.82rem; border-radius:4px;">{reasons_html}</div>
  <div style="background: rgba(10,92,92,0.05); padding: 12px; border-radius: 6px; font-family: monospace; font-size: 0.78rem; color: var(--sq-mint); line-height: 1.4;">
    > System generating insight...<br>> Input Context: {llm_preview}
  </div>
</div>''', unsafe_allow_html=True)

            sim  = classify_result["similarity"]
            best = max(sim, key=lambda k: sim[k])
            sim_html = '<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin-bottom:16px;">'
            for name in ["TimeSeries", "Static", "Activity"]:
                pct = sim[name] * 100
                is_best = name == best
                sim_html += f'<div class="sq-sim-card {"best" if is_best else ""}"><div class="sq-sim-name">{"✅ " if is_best else ""}{name}</div><div class="sq-sim-pct">{pct:.0f}%</div><div class="sq-sim-bar"><div class="sq-sim-fill" style="width:{pct:.0f}%"></div></div></div>'
            sim_html += '</div>'

            total_rows = len(df)
            missing_pct = (df.isna().sum().sum() / df.size) * 100 if df.size > 0 else 0
            engine_status = "Anthropic LLM 🟢" if insight_result.get("signal") else "Quant Rule Engine (Fallback) 🟡"

            meta_html = f'''
            <div style="display: flex; justify-content: space-between; align-items: center; background: var(--sq-surface); border: 1px solid var(--sq-border); color: var(--sq-text); padding: 12px 18px; border-radius: 8px; font-size: 0.8rem;">
                <div>
                    <span style="color: var(--sq-muted); margin-right: 6px;">Data Meta:</span>
                    <span style="margin-right: 14px;">Rows <b>{total_rows:,}</b></span>
                    <span style="color: {"#e74c3c" if missing_pct > 5 else "var(--sq-mint)"};">Missing <b>{missing_pct:.1f}%</b></span>
                </div>
                <div><span style="color: var(--sq-muted); margin-right: 6px;">Active Engine:</span><b>{engine_status}</b></div>
            </div>
            '''
            st.markdown(f'<div class="sq-eng-section"><div class="sq-eng-section-title">③ Class Similarity & Meta</div>{sim_html}{meta_html}</div>', unsafe_allow_html=True)

            v = classify_result["vector"]
            v = v + [0]*(18-len(v)) if len(v) < 18 else v[:18]
            vec_groups = [
                ("1. TimeSeries (시계열)", ["Date","Open","High","Low","Close","Volume"], v[0:6]),
                ("2. Static (자산 구조)", ["Asset(Name)","Weight","Target","Value","Return","Quarter(Date)"], v[6:12]),
                ("3. Activity (매매)", ["Timestamp","Buy/Sell","Quantity","Price","Fee","Ticker"], v[12:18]),
            ]

            vec_html = '<div class="sq-eng-section"><div class="sq-eng-section-title">④ 18D Feature Vector (Input Scan)</div>'
            for grp_title, labs, ch in vec_groups:
                vec_html += f'<div style="margin-bottom:18px"><div style="font-size:0.78rem;font-weight:700;color:var(--sq-teal);margin-bottom:8px;">{grp_title}</div><div class="sq-vec-matrix">'
                for lb, bit in zip(labs, ch):
                    cls = "v1" if bit else "v0"
                    icon = "●" if bit else "·"
                    vec_html += f'<div class="sq-vec-cell {cls}" style="padding: 14px 6px; border-radius: 8px;"><div class="sq-vec-bit" style="font-size:1.2rem; margin-bottom:4px;">{icon}</div><div style="font-size:0.7rem; text-align:center; font-weight:600;">{lb}</div></div>'
                vec_html += '</div></div>'
            vec_html += '</div>'
            st.markdown(vec_html, unsafe_allow_html=True)

        else:
            last_title = "Rebalancing" if dash == "portfolio" else "Hedge"
            cr = indicator_result.get("cum_return")
            cr_txt = f"{float(cr)*100:.2f}%" if cr is not None and np.isfinite(cr) else "—"
            conf = int(insight_result.get("confidence", 0))
            sig  = insight_result.get("signal", "HOLD")
            hedge_or_rebal = insight_result.get("rebalancing", "") if dash == "portfolio" else insight_result.get("hedge", "")
            st.markdown(_hero_row_html(sig, conf, cr_txt, str(insight_result.get("regime","—")), str(insight_result.get("action","")), str(hedge_or_rebal), last_title), unsafe_allow_html=True)

            defs = _kpi_defs(classify_result, indicator_result)
            k1, k2, k3, k4, k5 = st.columns(5)
            for col, (name, val, sub) in zip([k1,k2,k3,k4,k5], defs):
                with col:
                    dot = _badge_color(str(val), name)
                    st.markdown(f'<div class="sq-card sq-kpi"><div class="sq-kpi__name">{html.escape(name)}</div><div class="sq-kpi__val">{html.escape(str(val))}</div><div class="sq-kpi__sub">{html.escape(sub)}</div><div class="sq-kpi__dot" style="color:{dot}">● 상태</div></div>', unsafe_allow_html=True)

            # 메인 차트 — class_type × dimension 분기
            ct = classify_result.get("class_type", "")
            
            if ct == "TimeSeries":
                dashboard_timeseries(df, classify_result, indicator_result, theme=theme)
            elif ct == "Static":
                dashboard_portfolio(df, classify_result, indicator_result, theme=theme)
            elif ct == "Activity":
                dashboard_activity(df, classify_result, indicator_result, theme=theme)
            else:
                st.markdown('<div class="sq-card sq-chart">', unsafe_allow_html=True)
                st.plotly_chart(_fig_candlestick(df), use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

            # 서브 차트 — 식별자 기반 라우팅
            subs = chart_result.get("sub_charts") or []
            if ("excess_bar" in subs or "weight_drift_bar" in subs) and not _find_col(df, "target_weight"):
                subs = [s for s in subs if s not in ["excess_bar", "weight_drift_bar"]]

            # 필터링 2: 구현된 서브 차트만 남기기
                supported_subs = ["rsi", "zscore", "rolling_corr", "network", "excess_bar", "weight_drift_bar", "scatter_pf", "switch_bar", "timeline"]
                subs = [s for s in subs if s in supported_subs]

            def _render_sub(sub_id: str) -> None:
                if sub_id == "rsi":
                    st.plotly_chart(_fig_rsi(df), use_container_width=True)
                elif sub_id == "zscore":
                    st.plotly_chart(_fig_zscore(df, indicator_result, theme=theme), use_container_width=True)
                elif sub_id == "rolling_corr":
                    st.plotly_chart(_fig_rolling_corr(df, theme=theme), use_container_width=True)
                elif sub_id == "network":
                    st.plotly_chart(_fig_network(df, indicator_result, theme=theme), use_container_width=True)
                elif sub_id == "excess_bar":
                    st.plotly_chart(_fig_excess_bar(df), use_container_width=True)
                elif sub_id == "weight_drift_bar":
                    st.plotly_chart(_fig_weight_drift(df), use_container_width=True)
                elif sub_id == "scatter_pf":
                    st.plotly_chart(_fig_scatter_pf(df, theme=theme), use_container_width=True)
                elif sub_id == "switch_bar":
                    st.plotly_chart(_fig_switch_bar(df, theme=theme), use_container_width=True)
                elif sub_id == "timeline":
                    st.plotly_chart(_fig_activity_timeline(df, theme=theme), use_container_width=True)
                else:
                    pass

            if len(subs) >= 2:
                s1, s2 = st.columns(2)
                with s1:
                    st.markdown('<div class="sq-card sq-chart">', unsafe_allow_html=True)
                    _render_sub(subs[0])
                    st.markdown('</div>', unsafe_allow_html=True)
                with s2:
                    st.markdown('<div class="sq-card sq-chart">', unsafe_allow_html=True)
                    _render_sub(subs[1])
                    st.markdown('</div>', unsafe_allow_html=True)
            elif len(subs) == 1:
                st.markdown('<div class="sq-card sq-chart">', unsafe_allow_html=True)
                _render_sub(subs[0])
                st.markdown('</div>', unsafe_allow_html=True)

            blocks = [("지금 할 행동", insight_result.get("action", "")), ("Why now?", insight_result.get("why_now", ""))]
            blocks_html = "".join([f'<div class="sq-ac-block"><div class="sq-ac-lbl">{html.escape(lbl)}</div><div class="sq-ac-text">{html.escape(str(txt))}</div></div>' for lbl, txt in blocks])
            st.markdown(
                '<div class="sq-ac-wrap"><div class="sq-ac-header"><span class="sq-ac-title">Action Console</span><span class="sq-ac-badge">AI Insight</span></div>'
                f'<div class="sq-ac-llm">{html.escape(str(insight_result.get("llm_input","")))}</div><div class="sq-ac-body">{blocks_html}</div></div>',
                unsafe_allow_html=True,
            )

def _render_news(query: str) -> str:
    """RSS 피드에서 뉴스를 가져와 HTML 리스트로 반환"""
    # 검색어의 공백이나 특수문자를 URL용 안전한 문자로 변환 (예: ' ' -> '%20')
    encoded_query = quote(query)
    
    # 변환된 검색어를 URL에 삽입
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ko&gl=KR&ceid=KR:ko"
    
    feed = feedparser.parse(rss_url)
    # ... (이후 코드는 동일)
    
    news_html = ""
    # 상위 5개 뉴스 추출
    for entry in feed.entries[:5]:
        # 대시보드 테마인 sq-feed-item 스타일 활용
        news_html += (
            f'<div class="sq-feed-item" style="border-left:4px solid var(--sq-teal-mid)">'
            f'<a href="{entry.link}" target="_blank" style="text-decoration:none; color:inherit;">'
            f'<b style="font-size:0.82rem; line-height:1.4;">{html.escape(entry.title)}</b></a><br/>'
            f'<small style="color:var(--sq-muted)">{html.escape(entry.published[:16])}</small></div>'
        )
    return news_html

def _get_dynamic_query(classify_result: dict, indicator_result: dict, df: pd.DataFrame): # df 추가!
    ct = classify_result.get("class_type")
    
    if ct == "TimeSeries":
        # 여기서 df를 사용하기 때문에 인자에 df가 반드시 있어야 합니다.
        close_col = _find_col(df, "close") 
        if close_col and df[close_col].mean() < 1000:
            return "미국 증시 나스닥 시황"
        return "국내 증시 코스피 전망"

    # 2. 포트폴리오/자산 구성 데이터인 경우
    elif ct == "Static":
        # 리스크 기여도가 가장 높은 자산(max_risk_asset)이 있다면 해당 자산 뉴스
        asset = indicator_result.get("max_risk_asset")
        if asset and asset != "—":
            return f"{asset} 전망"
        return "자산 배분 투자 전략"

    # 3. 그 외 기본값
    return "금융 시장 주요 뉴스"