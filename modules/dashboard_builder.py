"""04_dashboard: Streamlit 레이아웃·차트·엔진 뷰."""

from __future__ import annotations

import html
from typing import Any

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# Sequence 스타일: 틸 / 민트 그린 / 오프화이트 캔버스 / 라운드 서피스 카드
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
  --sq-bg: #ffffff;
  --sq-surface: #f7f9fb;
  --sq-border: #dde3e8;
  --sq-text: #1a2d30;
  --sq-muted: #7a8f94;
  --sq-radius: 14px;
  --sq-radius-sm: 10px;
  --sq-shadow: 0 4px 24px rgba(6, 61, 61, 0.07);
  --sq-shadow-hover: 0 10px 36px rgba(6, 61, 61, 0.11);
  --sq-font: "DM Sans", system-ui, -apple-system, "Segoe UI", sans-serif;
}
.stApp { background: #ffffff !important; color: var(--sq-text); font-family: var(--sq-font); }
.sq-app-title {
  font-size: 1.75rem;
  font-weight: 700;
  letter-spacing: -0.03em;
  margin: 0 0 0.5rem 0;
  color: var(--sq-text);
}
[data-testid="stAppViewContainer"] > .main { background: transparent; }
.main .block-container {
  padding: 1.25rem 1.75rem 2rem !important;
  max-width: 100% !important;
}
[data-testid="stHeader"] {
  background: rgba(255,255,255,0.92) !important;
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--sq-border) !important;
}
[data-testid="stToolbar"] { background: transparent !important; }
h1, h2, h3, h4 { color: var(--sq-text) !important; letter-spacing: -0.02em; }
.stCaption, [data-testid="stCaptionContainer"] { color: var(--sq-muted) !important; }

.sq-nav-label {
  font-size: 0.65rem;
  font-weight: 600;
  letter-spacing: 0.12em;
  color: var(--sq-muted);
  margin: 4px 0 10px 0;
  text-transform: uppercase;
}

/* 히어로 스트립 (다크 틸 + 패턴) */
.sq-hero-row {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 20px;
  padding: 18px;
  border-radius: var(--sq-radius);
  background:
    radial-gradient(ellipse 80% 60% at 12% 20%, rgba(46,213,115,0.14) 0%, transparent 55%),
    radial-gradient(ellipse 60% 50% at 88% 80%, rgba(255,255,255,0.07) 0%, transparent 50%),
    linear-gradient(135deg, var(--sq-teal-deep) 0%, var(--sq-teal) 42%, var(--sq-teal-mid) 100%);
  box-shadow: 0 12px 40px rgba(6, 61, 61, 0.22);
  border: 1px solid rgba(255,255,255,0.06);
}
@media (max-width: 1100px) {
  .sq-hero-row { grid-template-columns: 1fr 1fr; }
}
.sq-hero-cell {
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: var(--sq-radius-sm);
  padding: 12px 14px;
  min-height: 102px;
  color: #f4faf9;
}
.sq-hero-cell__label {
  font-size: 0.72rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  opacity: 0.85;
  margin-bottom: 6px;
  color: rgba(255,255,255,0.85);
}
.sq-hero-cell__value {
  font-size: 1.35rem;
  font-weight: 700;
  line-height: 1.2;
  margin-bottom: 4px;
}
.sq-hero-cell__body {
  font-size: 0.82rem;
  opacity: 0.92;
  line-height: 1.35;
  color: rgba(255,255,255,0.92);
}
.sq-badge-pos {
  display: inline-block;
  margin-top: 6px;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 0.72rem;
  font-weight: 600;
  background: rgba(46,213,115,0.25);
  color: #b8ffd4;
  border: 1px solid rgba(46,213,115,0.45);
}
.sq-progress {
  margin-top: 8px;
  height: 6px;
  border-radius: 999px;
  background: rgba(0,0,0,0.2);
  overflow: hidden;
}
.sq-progress > span {
  display: block;
  height: 100%;
  border-radius: 999px;
  background: linear-gradient(90deg, var(--sq-mint), var(--sq-green));
}

/* KPI / 차트 카드 */
.sq-card {
  background: var(--sq-surface);
  border: 1px solid var(--sq-border);
  border-radius: var(--sq-radius);
  box-shadow: var(--sq-shadow);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.sq-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--sq-shadow-hover);
}
.sq-kpi {
  padding: 18px 16px;
  margin-bottom: 10px;
}
.sq-kpi__name {
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--sq-muted);
  margin-bottom: 6px;
}
.sq-kpi__val {
  font-size: 1.35rem;
  font-weight: 700;
  color: var(--sq-text);
}
.sq-kpi__sub {
  font-size: 0.78rem;
  color: var(--sq-muted);
  margin-top: 4px;
}
.sq-kpi__dot {
  display: inline-block;
  margin-top: 8px;
  font-size: 0.75rem;
  font-weight: 600;
}
.sq-chart {
  padding: 12px 12px 4px;
  margin-bottom: 14px;
}

/* 우측 패널 */
.sq-rail {
  background: var(--sq-surface);
  border: 1px solid var(--sq-border);
  border-radius: var(--sq-radius);
  box-shadow: var(--sq-shadow);
  padding: 16px 14px;
}
.sq-rail h1, .sq-rail h2, .sq-rail h3, .sq-rail h4, .sq-rail h5 {
  font-size: 0.82rem !important;
  font-weight: 700 !important;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--sq-muted) !important;
  margin: 0 0 10px 0 !important;
}
.sq-rail p, .sq-rail li, .sq-rail code { font-size: 0.85rem; }

.sq-feed-item {
  border-radius: var(--sq-radius-sm);
  padding: 10px 12px;
  margin-bottom: 8px;
  transition: transform 0.15s ease;
  border: 1px solid var(--sq-border);
  background: #fafbfb;
}
.sq-feed-item:hover { transform: translateX(5px); }

/* 엔진 뷰 메트릭 카드 */
div[data-testid="stMetric"] {
  background: var(--sq-surface);
  border: 1px solid var(--sq-border);
  border-radius: var(--sq-radius-sm);
  padding: 10px;
  box-shadow: var(--sq-shadow);
}

/* Primary 버튼: 민트 그린 */
.stApp .stButton > button[kind="primary"] {
  background: linear-gradient(180deg, var(--sq-green) 0%, #24b963 100%) !important;
  color: #063d2a !important;
  border: none !important;
  font-weight: 600 !important;
  border-radius: 10px !important;
  box-shadow: 0 2px 8px rgba(46,213,115,0.35);
}
.stApp .stButton > button[kind="secondary"] {
  background: var(--sq-surface) !important;
  color: var(--sq-teal) !important;
  border: 1px solid var(--sq-border) !important;
  border-radius: 10px !important;
  font-weight: 500 !important;
}
.stApp .stButton > button:disabled { opacity: 0.45 !important; }

/* 네이티브 사이드바 */
[data-testid="stSidebar"] {
  background: #f0f7f5 !important;
  border-right: 1px solid #d0e4df !important;
}
[data-testid="stSidebar"] > div:first-child {
  background: #f0f7f5 !important;
}
[data-testid="stSidebar"] .block-container {
  padding-top: 1rem !important;
  padding-bottom: 1.25rem !important;
}
.sq-sb-brand { margin-bottom: 1.25rem; }
.sq-sb-logo-row {
  display: flex;
  align-items: center;
  gap: 12px;
}
.sq-sb-logo-mark {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  flex-shrink: 0;
  background: linear-gradient(135deg, var(--sq-teal-deep) 0%, var(--sq-teal) 55%, var(--sq-mint) 160%);
  box-shadow: 0 4px 14px rgba(10, 92, 92, 0.25);
}
.sq-sb-logo-text {
  font-size: 1.15rem;
  font-weight: 700;
  letter-spacing: -0.03em;
  color: var(--sq-text);
  line-height: 1.2;
}
.sq-sb-logo-text span { color: var(--sq-teal); }
.sq-sb-logo-sub {
  font-size: 0.72rem;
  color: var(--sq-muted);
  margin-top: 2px;
}
.sq-sb-nav-wrap { margin: 0.5rem 0 1rem 0; }
.sq-sb-nav-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}
.sq-sb-nav-row .stButton { flex: 1; }
.sq-sb-nav-ic {
  flex-shrink: 0;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.sq-sb-upload-cap {
  font-size: 0.65rem;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--sq-muted);
  margin: 1rem 0 0.35rem 0;
}
.sq-sb-spacer { flex-grow: 1; min-height: 8px; }
.sq-dim-row {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 4px;
}
.sq-dim-pill {
  flex: 1;
  min-width: 48px;
  text-align: center;
  padding: 8px 10px;
  border-radius: 10px;
  font-size: 0.82rem;
  font-weight: 600;
  border: 1px solid var(--sq-border);
  box-sizing: border-box;
}
.sq-dim-pill--active {
  background: var(--sq-teal);
  color: #fff;
  border-color: var(--sq-teal);
  box-shadow: 0 2px 8px rgba(10, 92, 92, 0.2);
}
.sq-dim-pill--idle {
  color: var(--sq-muted);
  background: #f0f3f5;
}
.sq-dim-note {
  font-size: 0.72rem;
  color: var(--sq-muted);
  margin: 10px 0 0 0;
  line-height: 1.4;
}

/* 이벤트 스크롤 컨테이너 */
.sq-feed-scroll {
  max-height: 220px;
  overflow-y: auto;
  padding-right: 4px;
}
.sq-feed-scroll::-webkit-scrollbar { width: 4px; }
.sq-feed-scroll::-webkit-scrollbar-track { background: transparent; }
.sq-feed-scroll::-webkit-scrollbar-thumb { background: #c5d5d0; border-radius: 2px; }

/* 분석목적 칩 */
.sq-goal-chip {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 4px 10px; border-radius: 999px;
  font-size: 0.75rem; font-weight: 600;
  margin: 3px 2px; border: 1px solid;
}
.sq-goal-on  { background: rgba(10,92,92,0.1); color: #0a5c5c; border-color: rgba(10,92,92,0.25); }
.sq-goal-off { background: #f0f3f5; color: #9aacb0; border-color: #dde3e8; }

/* 시장 지표 */
.sq-mkt-item {
  display: flex; justify-content: space-between; align-items: center;
  padding: 6px 0; border-bottom: 1px solid #e8eeec;
}
.sq-mkt-name { font-size: 0.75rem; font-weight: 600; color: #7a8f94; }
.sq-mkt-val  { font-size: 0.78rem; font-weight: 700; }

/* Action Console 개선 */
.sq-ac-wrap {
  background: #fff; border: 1px solid var(--sq-border);
  border-radius: var(--sq-radius); box-shadow: var(--sq-shadow);
  overflow: hidden; margin-bottom: 14px;
}
.sq-ac-header {
  background: linear-gradient(135deg, #063d3d 0%, #0a5c5c 100%);
  padding: 14px 20px; display: flex; align-items: center; gap: 10px;
}
.sq-ac-title { font-size: 1rem; font-weight: 700; color: #fff; letter-spacing: -0.01em; }
.sq-ac-badge {
  font-size: 0.72rem; background: rgba(255,255,255,0.15); color: #b8ffd4;
  padding: 2px 10px; border-radius: 999px; border: 1px solid rgba(255,255,255,0.2);
}
.sq-ac-llm {
  padding: 10px 20px; background: rgba(10,92,92,0.05);
  border-bottom: 1px solid #e4e9ec;
  font-family: monospace; font-size: 0.78rem; color: #0a5c5c;
}
.sq-ac-body { display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; }
.sq-ac-block {
  padding: 18px 20px; border-right: 1px solid #e4e9ec;
}
.sq-ac-block:last-child { border-right: none; }
.sq-ac-lbl {
  font-size: 0.72rem; font-weight: 700; color: #7a8f94;
  text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 8px;
}
.sq-ac-text { font-size: 0.95rem; color: #1a2d30; line-height: 1.65; }

/* 우측 배너 */
.sq-rail-section { margin-bottom: 14px; }
.sq-rail-title {
  font-size: 0.7rem; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.1em; color: #7a8f94; margin-bottom: 8px; padding-bottom: 6px;
  border-bottom: 1px solid #dde3e8;
}

/* 계산 지표 */
.sq-ind-row {
  display: flex; justify-content: space-between; align-items: center;
  padding: 8px 0; border-bottom: 1px solid #eef1f4;
}
.sq-ind-name { font-size: 0.78rem; color: #7a8f94; }
.sq-ind-val  { font-size: 1.05rem; font-weight: 700; }

/* 엔진 뷰 */
.sq-eng-section {
  background: #fff; border: 1px solid var(--sq-border);
  border-radius: var(--sq-radius); box-shadow: var(--sq-shadow);
  padding: 22px 24px; margin-bottom: 16px;
}
.sq-eng-section-title {
  font-size: 0.82rem; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.08em; color: #7a8f94; margin-bottom: 16px;
  padding-bottom: 8px; border-bottom: 1px solid #dde3e8;
}
/* 파이프라인 */
.sq-pipe-row {
  display: flex; align-items: center; gap: 0;
  flex-wrap: wrap; margin: 8px 0;
}
.sq-pipe-step {
  background: #f0f7f5; border: 1.5px solid #0a5c5c;
  border-radius: 10px; padding: 10px 18px;
  font-size: 0.82rem; font-weight: 600; color: #063d3d;
  min-width: 110px; text-align: center;
  animation: pipeIn 0.4s ease forwards;
  opacity: 0; transform: translateY(8px);
}
.sq-pipe-step.s1{animation-delay:0.0s}
.sq-pipe-step.s2{animation-delay:0.15s}
.sq-pipe-step.s3{animation-delay:0.30s}
.sq-pipe-step.s4{animation-delay:0.45s}
@keyframes pipeIn {
  to { opacity: 1; transform: translateY(0); }
}
.sq-pipe-arrow {
  color: #0a5c5c; font-size: 1.2rem; padding: 0 8px;
  opacity: 0; animation: pipeIn 0.4s ease forwards;
}
.sq-pipe-arrow.a1{animation-delay:0.07s}
.sq-pipe-arrow.a2{animation-delay:0.22s}
.sq-pipe-arrow.a3{animation-delay:0.37s}
.sq-pipe-result {
  background: linear-gradient(135deg,#063d3d,#0a5c5c);
  color: #b8ffd4 !important; border-color: transparent !important;
}
/* 유사도 카드 */
.sq-sim-card {
  background: #f7f9fb; border: 1.5px solid #dde3e8;
  border-radius: 12px; padding: 16px; text-align: center;
  transition: all 0.2s;
}
.sq-sim-card.best {
  background: rgba(10,92,92,0.06); border-color: #0a5c5c;
}
.sq-sim-name { font-size: 0.82rem; font-weight: 700; color: #1a2d30; margin-bottom: 8px; }
.sq-sim-pct  { font-size: 1.6rem; font-weight: 800; color: #0a5c5c; }
.sq-sim-bar  { height: 5px; background: #e4e9ec; border-radius: 999px; margin-top: 8px; overflow: hidden; }
.sq-sim-fill { height: 100%; border-radius: 999px; background: linear-gradient(90deg,#0a5c5c,#1dd1a1); }
/* 벡터 매트릭스 */
.sq-vec-matrix { display: grid; grid-template-columns: repeat(6,1fr); gap: 4px; margin-bottom: 4px; }
.sq-vec-cell {
  aspect-ratio: 1; border-radius: 6px; display: flex; flex-direction: column;
  align-items: center; justify-content: center; gap: 2px;
  font-size: 0.6rem; color: #7a8f94; padding: 4px;
}
.sq-vec-cell.v1 { background: rgba(10,92,92,0.15); color: #063d3d; font-weight: 700; border: 1.5px solid rgba(10,92,92,0.3); }
.sq-vec-cell.v0 { background: #f0f3f5; border: 1px solid #dde3e8; }
.sq-vec-bit { font-size: 0.82rem; font-weight: 800; }
/* 분석목적 카드 */
.sq-goal-card {
  padding: 12px 14px; border-radius: 10px; border: 1.5px solid;
  margin-bottom: 8px; display: flex; align-items: flex-start; gap: 10px;
}
.sq-goal-card.on  { background: rgba(10,92,92,0.06); border-color: rgba(10,92,92,0.3); }
.sq-goal-card.off { background: #f7f9fb; border-color: #dde3e8; opacity: 0.65; }
.sq-goal-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; margin-top: 5px; }
.sq-goal-dot.on  { background: #0a5c5c; }
.sq-goal-dot.off { background: #c5d5d0; }
.sq-goal-card-name { font-size: 0.88rem; font-weight: 700; color: #1a2d30; }
.sq-goal-card-desc { font-size: 0.78rem; color: #7a8f94; margin-top: 2px; }

.sq-feed-scroll{max-height:220px;overflow-y:auto;padding-right:4px}
.sq-feed-scroll::-webkit-scrollbar{width:4px}
.sq-feed-scroll::-webkit-scrollbar-track{background:transparent}
.sq-feed-scroll::-webkit-scrollbar-thumb{background:#c5d5d0;border-radius:2px}
.sq-goal-chip{display:inline-flex;align-items:center;gap:5px;padding:4px 10px;border-radius:999px;font-size:0.75rem;font-weight:600;margin:3px 2px;border:1px solid}
.sq-goal-on{background:rgba(10,92,92,0.1);color:#0a5c5c;border-color:rgba(10,92,92,0.25)}
.sq-goal-off{background:#f0f3f5;color:#9aacb0;border-color:#dde3e8}
.sq-mkt-item{display:flex;justify-content:space-between;align-items:center;padding:7px 0;border-bottom:1px solid #e8eeec}
.sq-mkt-name{font-size:0.75rem;font-weight:600;color:#7a8f94}
.sq-mkt-val{font-size:0.82rem;font-weight:700}
.sq-ac-wrap{background:#fff;border:1px solid var(--sq-border);border-radius:var(--sq-radius);box-shadow:var(--sq-shadow);overflow:hidden;margin-bottom:14px}
.sq-ac-header{background:linear-gradient(135deg,#063d3d 0%,#0a5c5c 100%);padding:14px 20px;display:flex;align-items:center;gap:10px}
.sq-ac-title{font-size:1.05rem;font-weight:700;color:#fff;letter-spacing:-0.01em}
.sq-ac-badge{font-size:0.72rem;background:rgba(255,255,255,0.15);color:#b8ffd4;padding:2px 10px;border-radius:999px;border:1px solid rgba(255,255,255,0.2)}
.sq-ac-llm{padding:10px 20px;background:rgba(10,92,92,0.05);border-bottom:1px solid #e4e9ec;font-family:monospace;font-size:0.78rem;color:#0a5c5c}
.sq-ac-body{display:grid;grid-template-columns:1fr 1fr 1fr 1fr}
.sq-ac-block{padding:20px 20px;border-right:1px solid #e4e9ec}
.sq-ac-block:last-child{border-right:none}
.sq-ac-lbl{font-size:0.72rem;font-weight:700;color:#7a8f94;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:10px}
.sq-ac-text{font-size:1.0rem;font-weight:600;color:#1a2d30;line-height:1.65}
.sq-rail-section{margin-bottom:4px}
.sq-rail-title{font-size:0.7rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;color:#7a8f94;margin-bottom:8px;padding-bottom:6px;border-bottom:1px solid #dde3e8}
.sq-ind-row{display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid #eef1f4}
.sq-ind-name{font-size:0.82rem;color:#7a8f94}
.sq-ind-val{font-size:1.15rem;font-weight:700}
.sq-eng-section{background:#fff;border:1px solid var(--sq-border);border-radius:var(--sq-radius);box-shadow:var(--sq-shadow);padding:22px 24px;margin-bottom:16px}
.sq-eng-section-title{font-size:0.82rem;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;color:#7a8f94;margin-bottom:16px;padding-bottom:8px;border-bottom:1px solid #dde3e8}
.sq-pipe-row{display:flex;align-items:center;flex-wrap:wrap;margin:8px 0}
.sq-pipe-step{background:#f0f7f5;border:1.5px solid #0a5c5c;border-radius:10px;padding:10px 18px;font-size:0.82rem;font-weight:600;color:#063d3d;min-width:110px;text-align:center;animation:pipeIn 0.4s ease forwards;opacity:0;transform:translateY(8px)}
.sq-pipe-step.s1{animation-delay:0.0s}.sq-pipe-step.s2{animation-delay:0.15s}.sq-pipe-step.s3{animation-delay:0.3s}.sq-pipe-step.s4{animation-delay:0.45s}
@keyframes pipeIn{to{opacity:1;transform:translateY(0)}}
.sq-pipe-arrow{color:#0a5c5c;font-size:1.2rem;padding:0 8px;opacity:0;animation:pipeIn 0.4s ease forwards}
.sq-pipe-arrow.a1{animation-delay:0.07s}.sq-pipe-arrow.a2{animation-delay:0.22s}.sq-pipe-arrow.a3{animation-delay:0.37s}
.sq-pipe-result{background:linear-gradient(135deg,#063d3d,#0a5c5c);color:#b8ffd4 !important;border-color:transparent !important}
.sq-sim-card{background:#f7f9fb;border:1.5px solid #dde3e8;border-radius:12px;padding:16px;text-align:center}
.sq-sim-card.best{background:rgba(10,92,92,0.06);border-color:#0a5c5c}
.sq-sim-name{font-size:0.82rem;font-weight:700;color:#1a2d30;margin-bottom:8px}
.sq-sim-pct{font-size:1.6rem;font-weight:800;color:#0a5c5c}
.sq-sim-bar{height:5px;background:#e4e9ec;border-radius:999px;margin-top:8px;overflow:hidden}
.sq-sim-fill{height:100%;border-radius:999px;background:linear-gradient(90deg,#0a5c5c,#1dd1a1)}
.sq-vec-matrix{display:grid;grid-template-columns:repeat(6,1fr);gap:5px;margin-bottom:4px}
.sq-vec-cell{aspect-ratio:1;border-radius:6px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:2px;font-size:0.6rem;color:#7a8f94;padding:4px;border:1.5px solid #dde3e8}
.sq-vec-cell.v1{background:rgba(10,92,92,0.18);color:#063d3d;font-weight:700;border-color:rgba(10,92,92,0.4)}
.sq-vec-cell.v0{background:#ffffff}
.sq-vec-bit{font-size:0.9rem;font-weight:800}
.sq-goal-card{padding:12px 14px;border-radius:10px;border:1.5px solid;margin-bottom:8px;display:flex;align-items:flex-start;gap:10px}
.sq-goal-card.on{background:rgba(10,92,92,0.06);border-color:rgba(10,92,92,0.3)}
.sq-goal-card.off{background:#f7f9fb;border-color:#dde3e8;opacity:0.65}
.sq-goal-dot{width:8px;height:8px;border-radius:50%;flex-shrink:0;margin-top:5px}
.sq-goal-dot.on{background:#0a5c5c}.sq-goal-dot.off{background:#c5d5d0}
.sq-goal-card-name{font-size:0.88rem;font-weight:700;color:#1a2d30}
.sq-goal-card-desc{font-size:0.78rem;color:#7a8f94;margin-top:2px}
</style>
"""


def dimension_pills_html(dimension: str | None) -> str:
    """데이터 로드 후 고정 차원 표시용 HTML (버튼 아님)."""
    labs = ["1D", "2D", "ND"]
    parts: list[str] = []
    for lab in labs:
        active = dimension is not None and lab == dimension
        cls = (
            "sq-dim-pill sq-dim-pill--active"
            if active
            else "sq-dim-pill sq-dim-pill--idle"
        )
        parts.append(f'<span class="{cls}">{html.escape(lab)}</span>')
    label = '<p class="sq-nav-label" style="margin-top:0">Data Dimension</p>'
    return (
        f"{label}"
        f'<div class="sq-dim-row">{"".join(parts)}</div>'
    )


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
  <path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83 0 2 2 0 010-2.83l.06-.06a1.65 1.65 0 00.33-1.82 1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 010-2.83 2 2 0 012.83 0l.06.06a1.65 1.65 0 001.82.33H9a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 0 2 2 0 010 2.83l-.06.06a1.65 1.65 0 00-.33 1.82V9c.26.604.852 1 1.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z" stroke="#0a5c5c" stroke-width="1.15" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
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
                events.append(
                    {"date": dt, "label": "골든크로스", "kind": "buy", "color": "#1a7f37"}
                )
            if ma20.iloc[i] < ma60.iloc[i] and ma20.iloc[i - 1] >= ma60.iloc[i - 1]:
                events.append(
                    {"date": dt, "label": "데드크로스", "kind": "sell", "color": "#b42318"}
                )
            rv = float(rsi.iloc[i]) if pd.notna(rsi.iloc[i]) else None
            if rv is not None:
                if rv > 70:
                    events.append(
                        {
                            "date": dt,
                            "label": "RSI 과매수",
                            "kind": "warn",
                            "color": "#b54708",
                        }
                    )
                elif rv < 30:
                    events.append(
                        {
                            "date": dt,
                            "label": "RSI 과매도",
                            "kind": "buy",
                            "color": "#1a7f37",
                        }
                    )
        # 중복 제거: 동일 label 연속 발생 시 첫 발생일만 유지
        deduped: list[dict] = []
        seen_labels: set[str] = set()
        for ev in events:
            if ev["label"] not in seen_labels:
                seen_labels.add(ev["label"])
                deduped.append(ev)
        # 전체 이벤트에서 중복 없는 것만 (label별 마지막 1개)
        label_last: dict[str, dict] = {}
        for ev in events:
            label_last[ev["label"]] = ev
        # 날짜 역순 정렬 후 label별 첫 발생만
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
                        events.append(
                            {
                                "date": str(row[qc]),
                                "label": "비중 이탈",
                                "kind": "warn",
                                "color": "#b54708",
                            }
                        )
            label_first_s: dict[str, dict] = {}
            for ev in events:
                if ev["label"] not in label_first_s:
                    label_first_s[ev["label"]] = ev
            events = sorted(label_first_s.values(), key=lambda e: e["date"], reverse=True)[:8]

    elif ct == "Static" and dim == "ND":
        if (indicator_result.get("HHI") or 0) > 2500:
            events.append(
                {
                    "date": "latest",
                    "label": "HHI 초과",
                    "kind": "sell",
                    "color": "#b42318",
                }
            )
        if (indicator_result.get("top3_conc") or 0) > 0.6:
            events.append(
                {
                    "date": "latest",
                    "label": "Top-3 집중",
                    "kind": "warn",
                    "color": "#b54708",
                }
            )

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
        if x is None or (isinstance(x, float) and not np.isfinite(x)):
            return "—"
        return f"{float(x)*100:.2f}%"

    def fmt_num(x: Any, nd: int = 2) -> str:
        if x is None or (isinstance(x, float) and not np.isfinite(x)):
            return "—"
        return f"{float(x):.{nd}f}"

    rows: list[tuple[str, Any, str]] = []
    if ct == "TimeSeries" and dim == "1D":
        rows = [
            ("RSI (14)", fmt_num(ir.get("RSI"), 1), "모멘텀"),
            ("MDD", fmt_pct(ir.get("MDD")), "낙폭"),
            ("샤프 비율", fmt_num(ir.get("Sharpe"), 2), "위험조정수익"),
            ("ATR (14)", fmt_num(ir.get("ATR"), 1), "변동성"),
            (
                "추세 (MA20 vs MA60)",
                ir.get("trend") or "—",
                "골든/데드",
            ),
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
            ("누적 수익률", fmt_pct(ir.get("cum_return")), "스냅샷"),
            ("최대 리스크 기여", ir.get("max_risk_asset") or "—", "자산명"),
        ]
    else:
        rows = [
            ("지표 1", "—", "n/a"),
            ("지표 2", "—", "n/a"),
            ("지표 3", "—", "n/a"),
            ("지표 4", "—", "n/a"),
            ("지표 5", "—", "n/a"),
        ]
    return rows


def _badge_color(val: str, name: str) -> str:
    s = str(val).lower()
    nm = name.lower()
    # 추세
    if "dead" in s:
        return "#b42318"
    if "golden" in s:
        return "#1a7f37"
    # RSI
    if "rsi" in nm:
        try:
            v = float(val)
            if v > 70: return "#b42318"   # 과매수 위험
            if v < 30: return "#1a7f37"   # 과매도 매수기회
            return "#6b7280"              # 중립
        except Exception:
            pass
    # MDD
    if "mdd" in nm:
        try:
            v = float(val.replace("%", "")) / 100 if "%" in val else float(val)
            if v < -0.20: return "#b42318"   # 위험
            if v < -0.10: return "#b54708"   # 주의
            return "#1a7f37"                  # 양호
        except Exception:
            pass
    # 샤프
    if "샤프" in nm or "sharpe" in nm:
        try:
            v = float(val)
            if v >= 1.0: return "#1a7f37"
            if v >= 0.0: return "#b54708"
            return "#b42318"
        except Exception:
            pass
    # HHI
    if "hhi" in nm:
        try:
            v = float(val.replace(",", ""))
            if v > 2500: return "#b42318"
            if v > 1500: return "#b54708"
            return "#1a7f37"
        except Exception:
            pass
    # Top-3
    if "top" in nm:
        try:
            v = float(val.replace("%", ""))
            if v > 60: return "#b54708"
            return "#1a7f37"
        except Exception:
            pass
    # 기타 기본
    if "reduce" in s or "위험" in nm:
        return "#b42318"
    if "buy" in s or "양호" in nm:
        return "#1a7f37"
    return "#6b7280"


def _hero_row_html(
    sig: str,
    conf: int,
    cr_txt: str,
    regime: str,
    action: str,
    hedge_or_rebal: str,
    last_title: str,
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
    oc, hc, lc, cc = (
        _find_col(df, "open"),
        _find_col(df, "high"),
        _find_col(df, "low"),
        _find_col(df, "close"),
    )
    if not (dc and oc and hc and lc and cc):
        fig = go.Figure()
        fig.add_annotation(text="OHLC 컬럼이 부족합니다", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return fig
    w = df.sort_values(dc)
    fig = go.Figure(
        data=[
            go.Candlestick(
                x=w[dc],
                open=w[oc],
                high=w[hc],
                low=w[lc],
                close=w[cc],
                name="가격",
            )
        ]
    )
    close = pd.to_numeric(w[cc], errors="coerce")
    fig.add_trace(
        go.Scatter(
            x=w[dc],
            y=close.rolling(20, min_periods=5).mean(),
            name="MA20",
            line=dict(color="#2b83ba", width=1),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=w[dc],
            y=close.rolling(60, min_periods=5).mean(),
            name="MA60",
            line=dict(color="#fdae61", width=1),
        )
    )
    fig.update_layout(
        xaxis_rangeslider_visible=False,
        height=420,
        margin=dict(l=30, r=20, t=30, b=30),
        paper_bgcolor="#fafbfb",
        plot_bgcolor="#fafbfb",
        font=dict(family="DM Sans, sans-serif", color="#1a2d30"),
    )
    return fig


def _fig_rsi(df: pd.DataFrame) -> go.Figure:
    dc = _find_col(df, "date", "datetime")
    cc = _find_col(df, "close")
    if not (dc and cc):
        return go.Figure()
    w = df.sort_values(dc)
    close = pd.to_numeric(w[cc], errors="coerce")
    dlt = close.diff()
    g = dlt.clip(lower=0).ewm(alpha=1 / 14, adjust=False).mean()
    l = (-dlt.clip(upper=0)).ewm(alpha=1 / 14, adjust=False).mean()
    rs = g / l.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    fig = go.Figure(
        go.Scatter(x=w[dc], y=rsi, name="RSI(14)", line=dict(color="#6a51a3"))
    )
    fig.add_hline(y=70, line_dash="dot", line_color="#b54708")
    fig.add_hline(y=30, line_dash="dot", line_color="#1a7f37")
    fig.update_layout(
        height=260,
        margin=dict(l=30, r=20, t=20, b=30),
        paper_bgcolor="#fafbfb",
        plot_bgcolor="#fafbfb",
        font=dict(family="DM Sans, sans-serif", color="#1a2d30"),
        yaxis=dict(range=[0, 100], fixedrange=True),
    )
    return fig


def _quarter_port_bm(df: pd.DataFrame) -> tuple[list[Any], list[float], list[float]]:
    qc = _find_col(df, "quarter", "date")
    wc, twc, rc = _find_col(df, "weight"), _find_col(df, "target_weight"), _find_col(
        df, "return"
    )
    xs: list[Any] = []
    pr: list[float] = []
    br: list[float] = []
    if not (qc and wc and rc):
        return xs, pr, br
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
    fig.add_trace(
        go.Scatter(x=xs, y=cpr, name="포트폴리오", line=dict(color="#0a5c5c", width=2.5))
    )
    fig.add_trace(
        go.Scatter(
            x=xs, y=cbr, name="벤치마크(목표)", line=dict(color="#2ed573", width=2.5)
        )
    )
    fig.update_layout(
        height=420,
        margin=dict(l=30, r=20, t=30, b=30),
        paper_bgcolor="#fafbfb",
        plot_bgcolor="#fafbfb",
        font=dict(family="DM Sans, sans-serif", color="#1a2d30"),
    )
    return fig


def _fig_excess_bar(df: pd.DataFrame) -> go.Figure:
    xs, pr, br = _quarter_port_bm(df)
    if not xs:
        return go.Figure()
    ex = (np.array(pr) - np.array(br)) * 100.0
    fig = go.Figure(
        go.Bar(
            x=xs,
            y=ex,
            marker_color=np.where(ex >= 0, "#0a5c5c", "#e74c3c"),
        )
    )
    fig.update_layout(
        title=dict(text="분기 초과수익률 (%p)", font=dict(size=14, color="#1a2d30")),
        height=260,
        margin=dict(l=30, r=20, t=40, b=30),
        paper_bgcolor="#fafbfb",
        plot_bgcolor="#fafbfb",
        font=dict(family="DM Sans, sans-serif", color="#1a2d30"),
    )
    return fig


def _fig_weight_drift(df: pd.DataFrame) -> go.Figure:
    qc = _find_col(df, "quarter", "date")
    ac = _find_col(df, "asset_name", "asset")
    wc, twc = _find_col(df, "weight"), _find_col(df, "target_weight")
    if not (qc and ac and wc and twc):
        return go.Figure()
    last_q = df.sort_values(qc)[qc].iloc[-1]
    part = df[df[qc] == last_q]
    drift = (pd.to_numeric(part[wc], errors="coerce") - pd.to_numeric(part[twc], errors="coerce")) * 100.0
    fig = go.Figure(
        go.Bar(
            x=part[ac].astype(str),
            y=drift,
            marker_color=np.where(drift.values >= 0, "#0a5c5c", "#2ed573"),
        )
    )
    fig.update_layout(
        title=dict(
            text=f"비중 괴리율 (%p) — {last_q}",
            font=dict(size=14, color="#1a2d30"),
        ),
        height=260,
        margin=dict(l=30, r=20, t=40, b=30),
        paper_bgcolor="#fafbfb",
        plot_bgcolor="#fafbfb",
        font=dict(family="DM Sans, sans-serif", color="#1a2d30"),
    )
    return fig



def _render_market(mkt_data: list) -> str:
    if not mkt_data:
        return '<p style="font-size:0.82rem;color:#9aacb0;margin:4px 0">yfinance not installed</p>'
    rows = []
    for item in mkt_data:
        if item.get("price") is None:
            continue
        chg = item["change"]
        arrow = "▲" if chg >= 0 else "▼"
        color = "#1a7f37" if chg >= 0 else "#b42318"
        price_str = (
            f"{item['price']:,.0f}" if item["name"] in ("KOSPI", "USD/KRW")
            else f"{item['price']:,.2f}"
        )
        rows.append(
            f'<div class="sq-mkt-item">'
            f'<span class="sq-mkt-name">{html.escape(item["name"])}</span>'
            f'<span class="sq-mkt-val" style="color:{color}">'
            f'{arrow} {price_str} <small>({chg:+.2f}%)</small></span></div>'
        )
    return "".join(rows)


def _render_home_charts(mkt_data: list) -> None:
    """홈 화면: 시장 지표 미니 차트 6개."""
    if not mkt_data or not any(m.get("hist") for m in mkt_data):
        st.info("시장 데이터를 불러오는 중... (yfinance 필요)")
        return

    valid = [m for m in mkt_data if m.get("price") is not None and len(m.get("hist", [])) > 0]
    if not valid:
        st.warning("yfinance 설치 후 시장 지표를 확인할 수 있습니다: pip install yfinance")
        return

    cols = st.columns(3)
    for i, item in enumerate(valid):
        col = cols[i % 3]
        with col:
            chg   = item["change"]
            color = "#0a5c5c" if chg >= 0 else "#b42318"
            price_str = (
                f"{item['price']:,.0f}" if item["name"] in ("KOSPI", "USD/KRW")
                else f"{item['price']:,.2f}"
            )
            arrow = "▲" if chg >= 0 else "▼"
            st.markdown(
                f'<div class="sq-card" style="padding:16px 18px;margin-bottom:12px">'
                f'<div style="font-size:0.78rem;font-weight:700;color:#7a8f94;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:6px">{html.escape(item["name"])}</div>'
                f'<div style="font-size:1.5rem;font-weight:800;color:{color}">{price_str}</div>'
                f'<div style="font-size:0.82rem;color:{color};margin-top:4px">{arrow} {chg:+.2f}%</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            hist = item.get("hist", [])
            if len(hist) >= 2:
                import plotly.graph_objects as go
                fig = go.Figure(go.Scatter(
                    y=hist, mode="lines",
                    line=dict(color=color, width=2),
                    fill="tozeroy",
                    fillcolor=f"{'rgba(10,92,92,0.1)' if chg >= 0 else 'rgba(180,35,24,0.08)'}",
                ))
                fig.update_layout(
                    height=80, margin=dict(l=0,r=0,t=0,b=0),
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    showlegend=False,
                    xaxis=dict(visible=False), yaxis=dict(visible=False),
                )
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


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

    # ══════════════════════════════════════
    # HOME 뷰
    # ══════════════════════════════════════
    if view == "home":
        st.markdown(
            '<h2 style="font-size:1.5rem;font-weight:800;color:#063d3d;margin-bottom:4px">Market Overview</h2>'
            '<p style="color:#7a8f94;font-size:0.88rem;margin-bottom:20px">Real-time global market indicators</p>',
            unsafe_allow_html=True,
        )
        _render_home_charts(mkt_data)
        return

    # ══════════════════════════════════════
    # CSV 미업로드 공통 처리
    # ══════════════════════════════════════
    if classify_result is None or df is None:
        mc, rc = st.columns([74, 26], gap="medium")
        with mc:
            st.markdown('''
<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;
height:60vh;color:#9aacb0;text-align:center;gap:12px">
  <div style="font-size:3rem">📂</div>
  <div style="font-size:1.1rem;font-weight:700;color:#7a8f94">Upload a CSV to get started</div>
  <div style="font-size:0.88rem">Use the sidebar to upload your investment data</div>
</div>''', unsafe_allow_html=True)
        with rc:
            st.markdown(
                '<div class="sq-rail" style="margin-bottom:10px">'
                '<div class="sq-rail-section">'
                '<div class="sq-rail-title">Market Indicators</div>'
                + _render_market(mkt_data) +
                '</div></div>', unsafe_allow_html=True)
        return

    dash   = classify_result["dashboard"]
    engine = (view == "engine")
    events = _detect_events(df, classify_result, indicator_result)

    mc, rc = st.columns([74, 26], gap="medium")

    # ══════════════════════════════════════
    # 우측 배너 (Dashboard & Engine 공통)
    # ══════════════════════════════════════
    with rc:
        # 시장 지표
        st.markdown(
            '<div class="sq-rail" style="margin-bottom:10px">'
            '<div class="sq-rail-section">'
            '<div class="sq-rail-title">Market Indicators</div>'
            + _render_market(mkt_data) +
            '</div></div>', unsafe_allow_html=True)

        # Insights 박스
        # ① 이벤트
        feed_items = ""
        if not events:
            feed_items = '<p style="font-size:0.82rem;color:#9aacb0;margin:4px 0">No events detected</p>'
        else:
            for ev in events:
                feed_items += (
                    f'<div class="sq-feed-item" style="border-left:4px solid {ev["color"]}">'
                    f'<b style="color:var(--sq-text);font-size:0.84rem">{html.escape(ev["label"])}</b><br/>'
                    f'<small style="color:var(--sq-muted)">{html.escape(str(ev["date"]))}</small></div>'
                )

        # ② 분석 목적 (ON 아이콘 개선, 영어 코드 제거)
        active_goals = set(classify_result["goals"])
        goals_html = ""
        for g, (title, _desc) in _GOAL_META.items():
            on = g in active_goals
            icon = '✦' if on else '○'
            goals_html += (
                f'<span class="sq-goal-chip {"sq-goal-on" if on else "sq-goal-off"}">'
                f'<span style="font-size:0.7rem">{icon}</span>'
                f'{title}</span>'
            )

        # ③ 계산 지표 - 폰트 더 크게
        ind_html = ""
        for name, val, _sub in _kpi_defs(classify_result, indicator_result):
            dot_color = _badge_color(str(val), name)
            ind_html += (
                f'<div class="sq-ind-row">'
                f'<span class="sq-ind-name">{html.escape(name)}</span>'
                f'<span class="sq-ind-val" style="color:{dot_color}">{html.escape(str(val))}</span>'
                f'</div>'
            )

        st.markdown(
            '<div class="sq-rail">'
            '<div class="sq-rail-section">'
            '<div class="sq-rail-title">① Auto Events</div>'
            f'<div class="sq-feed-scroll">{feed_items}</div>'
            '</div>'
            '<div class="sq-rail-section" style="margin-top:16px">'
            '<div class="sq-rail-title">② Analysis Goals</div>'
            f'<div style="display:flex;flex-wrap:wrap;gap:4px;line-height:2">{goals_html}</div>'
            '</div>'
            '<div class="sq-rail-section" style="margin-top:16px">'
            '<div class="sq-rail-title">③ Key Indicators</div>'
            f'{ind_html}'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )

    # ══════════════════════════════════════
    # 중앙 - ENGINE VIEW
    # ══════════════════════════════════════
    with mc:
      if engine:
        # ① 파이프라인
        st.markdown(f'''
<div class="sq-eng-section">
<div class="sq-eng-section-title">① Analysis Pipeline</div>
<div class="sq-pipe-row">
  <div class="sq-pipe-step s1">18D Vector<br><small style="font-weight:400;color:#4a8080">Column scan</small></div>
  <span class="sq-pipe-arrow a1">→</span>
  <div class="sq-pipe-step s2">Class<br><small style="font-weight:400;color:#4a8080">Cosine similarity</small></div>
  <span class="sq-pipe-arrow a2">→</span>
  <div class="sq-pipe-step s3">Dimension<br><small style="font-weight:400;color:#4a8080">Ticker count</small></div>
  <span class="sq-pipe-arrow a3">→</span>
  <div class="sq-pipe-step s4 sq-pipe-result">Visualization<br><small style="font-weight:400">Auto render</small></div>
</div>
<div style="margin-top:12px;padding:10px 14px;background:rgba(10,92,92,0.06);border-radius:8px;
font-family:monospace;font-size:0.82rem;color:#063d3d">
Result: <b>{classify_result["class_type"]}</b> / <b>{classify_result["dimension"]}</b> / dashboard: <b>{classify_result["dashboard"]}</b>
</div></div>''', unsafe_allow_html=True)

        # ② 유사도
        sim  = classify_result["similarity"]
        best = max(sim, key=lambda k: sim[k])
        sim_html = '<div class="sq-eng-section"><div class="sq-eng-section-title">② Class Similarity</div><div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px">'
        for name in ["TimeSeries", "Static", "Activity"]:
            pct = sim[name] * 100
            is_best = name == best
            sim_html += (
                f'<div class="sq-sim-card {"best" if is_best else ""}">'
                f'<div class="sq-sim-name">{"✅ " if is_best else ""}{name}</div>'
                f'<div class="sq-sim-pct">{pct:.0f}%</div>'
                f'<div class="sq-sim-bar"><div class="sq-sim-fill" style="width:{pct:.0f}%"></div></div>'
                f'</div>'
            )
        sim_html += '</div></div>'
        st.markdown(sim_html, unsafe_allow_html=True)

        # ③ 18D 벡터 매트릭스
        v = classify_result["vector"]
        vec_groups = [
            ("Price Series",  ["Date","Open","High","Low","Close","Volume"],  v[0:6]),
            ("Trade Activity",["Timestamp","Buy/Sell","Qty","Price","Fee","—"], v[6:11]+[0]),
            ("Asset Structure",["Asset","Holding","Weight","Value","—","—"],   v[11:15]+[0,0]),
            ("Performance",   ["기여도","목표값","예상치","—","—","—"],         v[15:18]+[0,0,0]),
        ]
        vec_html = '<div class="sq-eng-section"><div class="sq-eng-section-title">③ 18D Feature Vector</div>'
        for grp_title, labs, ch in vec_groups:
            vec_html += (
                f'<div style="margin-bottom:14px">'
                f'<div style="font-size:0.72rem;font-weight:700;color:#7a8f94;margin-bottom:6px;text-transform:uppercase;letter-spacing:0.06em">{grp_title}</div>'
                f'<div class="sq-vec-matrix">'
            )
            for lb, bit in zip(labs, ch):
                cls = "v1" if bit and lb != "—" else "v0"
                disp = lb if lb != "—" else ""
                vec_html += (
                    f'<div class="sq-vec-cell {cls}">'
                    f'<span class="sq-vec-bit">{"●" if (bit and lb != "—") else "·"}</span>'
                    f'<span>{disp}</span>'
                    f'</div>'
                )
            vec_html += '</div></div>'
        vec_html += (
            '<div style="font-size:0.72rem;color:#9aacb0">'
            '<span style="color:#0a5c5c;font-weight:700">●</span> Detected &nbsp;'
            '<span style="color:#c5d5d0">·</span> Not detected'
            '</div></div>'
        )
        st.markdown(vec_html, unsafe_allow_html=True)

        # ④ 분석 목적 (영어 코드 제거, 박스 형태)
        active_goals = set(classify_result["goals"])
        goal_html = '<div class="sq-eng-section"><div class="sq-eng-section-title">④ Analysis Goals</div>'
        for g, (title, desc) in _GOAL_META.items():
            on = g in active_goals
            goal_html += (
                f'<div class="sq-goal-card {"on" if on else "off"}">'
                f'<div class="sq-goal-dot {"on" if on else "off"}"></div>'
                f'<div><div class="sq-goal-card-name">{title}</div>'
                f'<div class="sq-goal-card-desc">{desc}</div></div>'
                + ('<span style="margin-left:auto;font-size:0.78rem;font-weight:700;color:#0a5c5c;background:rgba(10,92,92,0.1);padding:2px 8px;border-radius:999px">ON</span>' if on else '')
                + '</div>'
            )
        goal_html += (
            f'<div style="margin-top:12px;padding:10px 14px;background:rgba(10,92,92,0.05);'
            f'border-radius:8px;font-family:monospace;font-size:0.78rem;color:#0a5c5c">'
            f'LLM input: {html.escape(str(insight_result.get("llm_input","")))}</div></div>'
        )
        st.markdown(goal_html, unsafe_allow_html=True)

      # ══════════════════════════════════════
      # 중앙 - DASHBOARD VIEW
      # ══════════════════════════════════════
      else:
        # Hero
        last_title = "Rebalancing" if dash == "portfolio" else "Hedge"
        cr = indicator_result.get("cum_return")
        cr_txt = f"{float(cr)*100:.2f}%" if cr is not None and np.isfinite(cr) else "—"
        conf = int(insight_result.get("confidence", 0))
        sig  = insight_result.get("signal", "HOLD")
        hedge_or_rebal = (
            insight_result.get("rebalancing", "") if dash == "portfolio"
            else insight_result.get("hedge", "")
        )
        st.markdown(
            _hero_row_html(sig, conf, cr_txt,
                           str(insight_result.get("regime","—")),
                           str(insight_result.get("action","")),
                           str(hedge_or_rebal), last_title),
            unsafe_allow_html=True,
        )

        # KPI row
        defs = _kpi_defs(classify_result, indicator_result)
        k1, k2, k3, k4, k5 = st.columns(5)
        for col, (name, val, sub) in zip([k1,k2,k3,k4,k5], defs):
            with col:
                dot = _badge_color(str(val), name)
                st.markdown(
                    f'<div class="sq-card sq-kpi">'
                    f'<div class="sq-kpi__name">{html.escape(name)}</div>'
                    f'<div class="sq-kpi__val">{html.escape(str(val))}</div>'
                    f'<div class="sq-kpi__sub">{html.escape(sub)}</div>'
                    f'<div class="sq-kpi__dot" style="color:{dot}">● 상태</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

        # 메인 차트 (KPI 바로 아래, 빈 박스 없음)
        main_id = chart_result.get("main_chart", "")
        st.markdown('<div class="sq-card sq-chart">', unsafe_allow_html=True)
        if main_id == "candlestick":
            st.plotly_chart(_fig_candlestick(df), use_container_width=True)
        elif main_id == "dual_line" and classify_result["class_type"] == "Static":
            st.plotly_chart(_fig_static_dual(df), use_container_width=True)
        else:
            st.plotly_chart(_fig_candlestick(df), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # 서브 차트
        subs = chart_result.get("sub_charts") or []
        if len(subs) >= 2:
            s1, s2 = st.columns(2)
            with s1:
                st.markdown('<div class="sq-card sq-chart">', unsafe_allow_html=True)
                if subs[0] == "rsi":
                    st.plotly_chart(_fig_rsi(df), use_container_width=True)
                elif subs[0] == "excess_bar":
                    st.plotly_chart(_fig_excess_bar(df), use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            with s2:
                st.markdown('<div class="sq-card sq-chart">', unsafe_allow_html=True)
                if subs[1] == "rolling_corr":
                    st.caption("Rolling correlation (2D sample needed)")
                elif subs[1] == "weight_drift_bar":
                    st.plotly_chart(_fig_weight_drift(df), use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
        elif len(subs) == 1:
            st.markdown('<div class="sq-card sq-chart">', unsafe_allow_html=True)
            if subs[0] == "rsi":
                st.plotly_chart(_fig_rsi(df), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Action Console - 세로 배치 (지금 할 행동, Why now?)
        blocks = [
            ("지금 할 행동", insight_result.get("action", "")),
            ("Why now?", insight_result.get("why_now", "")),
        ]
        blocks_html = "".join([
            f'<div class="sq-ac-block">'
            f'<div class="sq-ac-lbl">{html.escape(lbl)}</div>'
            f'<div class="sq-ac-text">{html.escape(str(txt))}</div>'
            f'</div>'
            for lbl, txt in blocks
        ])
        st.markdown(
            '<div class="sq-ac-wrap">'
            '<div class="sq-ac-header">'
            '<span class="sq-ac-title">Action Console</span>'
            '<span class="sq-ac-badge">AI Insight</span>'
            '</div>'
            f'<div class="sq-ac-llm">{html.escape(str(insight_result.get("llm_input","")))}</div>'
            f'<div class="sq-ac-body" style="grid-template-columns: 1fr;">{blocks_html}</div>'
            '</div>',
            unsafe_allow_html=True,
        )
