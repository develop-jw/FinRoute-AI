"""04_dashboard: Streamlit 레이아웃·차트·엔진 뷰."""

from __future__ import annotations

import html
from typing import Any

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import feedparser

from urllib.parse import quote  # URL 인코딩을 위해 추가

# Sequence 스타일: Streamlit 네이티브 테마 완벽 연동
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
        oc = _find_col(df, "open")
        hc = _find_col(df, "high")
        lc = _find_col(df, "low")
        cc = _find_col(df, "close")
        if not (dc and cc):
            return events
        w = df.sort_values(dc).copy()
        close = pd.to_numeric(w[cc], errors="coerce")
        ma20 = close.rolling(20, min_periods=5).mean()
        ma60 = close.rolling(60, min_periods=5).mean()
        rsi_s = close.copy()
        dlt = rsi_s.diff()
        g = dlt.clip(lower=0).ewm(alpha=1 / 14, adjust=False).mean()
        l = (-dlt.clip(upper=0)).ewm(alpha=1 / 14, adjust=False).mean()
        rs = g / l.replace(0, np.nan)
        rsi = 100 - (100 / (1 + rs))
        for i in range(2, len(w)):
            dt = str(w[dc].iloc[i])
            if ma20.iloc[i] > ma60.iloc[i] and ma20.iloc[i - 1] <= ma60.iloc[i - 1]:
                events.append({"date": dt, "label": "골든크로스", "kind": "buy", "color": "#1a7f37"})
            if ma20.iloc[i] < ma60.iloc[i] and ma20.iloc[i - 1] >= ma60.iloc[i - 1]:
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

    elif ct == "Static" and dim in ("1D", "2D"):
        qc = _find_col(df, "quarter", "date")
        wc = _find_col(df, "weight")
        tc = _find_col(df, "target_weight")
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

    elif ct == "Static" and dim == "ND":
        if (indicator_result.get("HHI") or 0) > 2500:
            events.append({"date": "latest", "label": "HHI 초과", "kind": "sell", "color": "#b42318"})
        if (indicator_result.get("top3_conc") or 0) > 0.6:
            events.append({"date": "latest", "label": "Top-3 집중", "kind": "warn", "color": "#b54708"})

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
    elif ct == "Static" and dim == "2D":
        rows = [
            ("액티브 셰어", fmt_pct(ir.get("active_share")), "벤치 대비"),
            ("추적 오차 (TE)", fmt_pct(ir.get("tracking_err")), "괴리 변동"),
            ("정보 비율 (IR)", fmt_num(ir.get("info_ratio"), 2), "초과수익 품질"),
            ("포트 누적 수익", fmt_pct(ir.get("cum_return")), "기간 합성"),
            ("벤치 누적 수익", fmt_pct(ir.get("bm_return")), "목표 가중"),
        ]
    elif ct == "Static" and dim == "ND":
        rows = [
            ("HHI", fmt_num(ir.get("HHI"), 0), "집중도"),
            ("유효 자산 수", fmt_num(ir.get("eff_n"), 1), "분산도"),
            ("Top-3 집중도", fmt_pct(ir.get("top3_conc")), "상위 쏠림"),
            ("누적 수익률", fmt_pct(ir.get("cum_return")), "Static 지표"),
            ("최대 리스크 기여", ir.get("max_risk_asset") or "—", "자산명"),
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
    if "reduce" in s or "위험" in nm: return "#b42318"
    if "buy" in s or "양호" in nm: return "#1a7f37"
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

def _fig_candlestick(df: pd.DataFrame) -> go.Figure:
    dc = _find_col(df, "date", "datetime")
    oc, hc, lc, cc = _find_col(df, "open"), _find_col(df, "high"), _find_col(df, "low"), _find_col(df, "close")
    if not (dc and oc and hc and lc and cc):
        fig = go.Figure()
        fig.add_annotation(text="OHLC 컬럼이 부족합니다", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return fig
    w = df.sort_values(dc)
    fig = go.Figure(data=[go.Candlestick(x=w[dc], open=w[oc], high=w[hc], low=w[lc], close=w[cc], name="가격")])
    close = pd.to_numeric(w[cc], errors="coerce")
    fig.add_trace(go.Scatter(x=w[dc], y=close.rolling(20, min_periods=5).mean(), name="MA20", line=dict(color="#2b83ba", width=1)))
    fig.add_trace(go.Scatter(x=w[dc], y=close.rolling(60, min_periods=5).mean(), name="MA60", line=dict(color="#fdae61", width=1)))
    fig.update_layout(
        xaxis_rangeslider_visible=False,
        height=420,
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

def _render_home_charts(mkt_data: list) -> None:
    if not mkt_data or not any(m.get("hist") for m in mkt_data):
        st.info("시장 데이터를 불러오는 중... (yfinance 필요)")
        return

    valid = [m for m in mkt_data if m.get("price") is not None and len(m.get("hist", [])) > 0]
    if not valid:
        st.warning("yfinance 설치 후 시장 지표를 확인할 수 있습니다.")
        return

    cols = st.columns(3)
    for i, item in enumerate(valid[:6]):
        col = cols[i % 3]
        with col:
            chg   = item["change"]
            color = "#1a7f37" if chg >= 0 else "#b42318"
            bg_fill = "rgba(26,127,55,0.08)" if chg >= 0 else "rgba(180,35,24,0.06)"
            sign  = "+" if chg > 0 else ""
            arrow = "▲" if chg >= 0 else "▼"
            price_str = f"{item['price']:,.0f}" if item["name"] in ("KOSPI", "USD/KRW") else f"{item['price']:,.2f}"
            hist = item.get("hist", [])
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(y=hist, mode="lines", line=dict(color=color, width=2.5), fill="tozeroy", fillcolor=bg_fill, hoverinfo="skip"))
            fig.add_annotation(x=0, y=1.15, xref="paper", yref="paper", text=f"<b>{item['name']}</b>", showarrow=False, font=dict(size=12, color="#7a8f94"), xanchor="left", yanchor="top")
            fig.add_annotation(x=0, y=0.75, xref="paper", yref="paper", text=f"<b>{price_str}</b>", showarrow=False, font=dict(size=26, color=color, family="DM Sans"), xanchor="left", yanchor="top")
            fig.add_annotation(x=0, y=0.45, xref="paper", yref="paper", text=f"{arrow} {sign}{chg:.2f}%", showarrow=False, font=dict(size=13, color=color, family="DM Sans"), xanchor="left", yanchor="top")
            fig.update_layout(
                height=140, margin=dict(l=20, r=0, t=20, b=0), 
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", 
                showlegend=False, xaxis=dict(visible=False, fixedrange=True), 
                yaxis=dict(visible=False, fixedrange=True, range=[min(hist)*0.99, max(hist)*1.05]), 
                shapes=[dict(type="rect", xref="paper", yref="paper", x0=0, y0=0, x1=1, y1=1, line=dict(color="rgba(128,128,128,0.2)", width=1.5), fillcolor="rgba(0,0,0,0)", layer="below")]
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
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
        
        _render_home_charts(mkt_data)

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
            st.session_state['saved_df'] = pd.read_csv(uploaded_main) 
            st.session_state.fin_view = "main"
            st.rerun()
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
        with rc:
            st.markdown(
                '<div class="sq-rail" style="margin-bottom:10px"><div class="sq-rail-section"><div class="sq-rail-title">Market Indicators</div>'
                + _render_market(mkt_data) + '</div></div>', unsafe_allow_html=True)
        return

    dash   = classify_result["dashboard"]
    engine = (view == "engine")
    events = _detect_events(df, classify_result, indicator_result)

    mc, rc = st.columns([74, 26], gap="medium")

    with rc:
        st.markdown(
            '<div class="sq-rail" style="margin-bottom:10px"><div class="sq-rail-section"><div class="sq-rail-title">Market Indicators</div>'
            + _render_market(mkt_data) + '</div></div>', unsafe_allow_html=True)

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

        ind_html = ""
        for name, val, _sub in _kpi_defs(classify_result, indicator_result):
            dot_color = _badge_color(str(val), name)
            ind_html += f'<div class="sq-ind-row"><span class="sq-ind-name">{html.escape(name)}</span><span class="sq-ind-val" style="color:{dot_color}">{html.escape(str(val))}</span></div>'

        st.markdown(
            f'<div class="sq-rail"><div class="sq-rail-section"><div class="sq-rail-title">① Auto Events</div><div class="sq-feed-scroll">{feed_items}</div></div>'
            f'<div class="sq-rail-section" style="margin-top:16px"><div class="sq-rail-title">② Analysis Goals</div><div style="display:flex;flex-wrap:wrap;gap:4px;line-height:2">{goals_html}</div></div>'
            f'<div class="sq-rail-section" style="margin-top:16px"><div class="sq-rail-title">③ Key Indicators</div>{ind_html}</div></div>',
            unsafe_allow_html=True,
        )
        # ... 기존 build 함수 내 with rc: 섹션 마지막 부분 ...

        # --- [추가] ④ Contextual News 섹션 ---
        # 1. 동적 키워드 추출 (df는 build 함수의 인자로 들어옴)
        query = _get_dynamic_query(classify_result, indicator_result, df)
        
        # 2. 뉴스 데이터 가져오기 (_render_news 함수 호출)
        news_items = _render_news(query)
        
        # 3. 우측 레일에 뉴스 카드 추가
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

            main_id = chart_result.get("main_chart", "")
            st.markdown('<div class="sq-card sq-chart">', unsafe_allow_html=True)
            if main_id == "candlestick": st.plotly_chart(_fig_candlestick(df), use_container_width=True)
            elif main_id == "dual_line" and classify_result["class_type"] == "Static": st.plotly_chart(_fig_static_dual(df), use_container_width=True)
            else: st.plotly_chart(_fig_candlestick(df), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            subs = chart_result.get("sub_charts") or []
            if len(subs) >= 2:
                s1, s2 = st.columns(2)
                with s1:
                    st.markdown('<div class="sq-card sq-chart">', unsafe_allow_html=True)
                    if subs[0] == "rsi": st.plotly_chart(_fig_rsi(df), use_container_width=True)
                    elif subs[0] == "excess_bar": st.plotly_chart(_fig_excess_bar(df), use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                with s2:
                    st.markdown('<div class="sq-card sq-chart">', unsafe_allow_html=True)
                    if subs[1] == "rolling_corr": st.caption("Rolling correlation (2D sample needed)")
                    elif subs[1] == "weight_drift_bar": st.plotly_chart(_fig_weight_drift(df), use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
            elif len(subs) == 1:
                st.markdown('<div class="sq-card sq-chart">', unsafe_allow_html=True)
                if subs[0] == "rsi": st.plotly_chart(_fig_rsi(df), use_container_width=True)
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