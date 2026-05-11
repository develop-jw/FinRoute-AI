"""FinRoute AI — Streamlit entry point."""
from __future__ import annotations
import html
from pathlib import Path
import pandas as pd
import streamlit as st
from modules.chart_selector import select_chart
from modules.classifier import classify
from modules.dashboard_builder import (
    SIDEBAR_BRAND_HTML, SIDEBAR_ICON_DASHBOARD, SIDEBAR_ICON_ENGINE,
    SIDEBAR_ICON_HOME, THEME_CSS, build, dimension_pills_html,
)
from modules.indicator_calculator import calculate
from modules.insight_generator import generate

st.set_page_config(page_title="FinRoute AI", layout="wide", initial_sidebar_state="expanded")
st.markdown(THEME_CSS, unsafe_allow_html=True)

if "fin_view" not in st.session_state:
    st.session_state.fin_view = "home"

DATA_DIR = Path(__file__).resolve().parent / "data"

# ── 시장 지표 ─────────────────────────────────
@st.cache_data(ttl=300)
def _get_market_data() -> list[dict]:
    try:
        import yfinance as yf
        tickers = {
            "KOSPI": "^KS11", "NASDAQ": "^IXIC", "S&P500": "^GSPC",
            "Gold": "GC=F", "WTI": "CL=F", "USD/KRW": "KRW=X",
        }
        result = []
        for name, sym in tickers.items():
            try:
                hist = yf.Ticker(sym).history(period="5d")
                if len(hist) >= 2:
                    prev = float(hist["Close"].iloc[-2])
                    curr = float(hist["Close"].iloc[-1])
                    chg  = (curr - prev) / prev * 100
                    hist5 = list(hist["Close"].astype(float))
                    result.append({"name": name, "price": curr, "change": chg, "hist": hist5})
                elif len(hist) == 1:
                    curr = float(hist["Close"].iloc[-1])
                    result.append({"name": name, "price": curr, "change": 0.0, "hist": [curr]})
            except Exception:
                result.append({"name": name, "price": None, "change": 0.0, "hist": []})
        return result
    except ImportError:
        return []

# ── 사이드바 ──────────────────────────────────
with st.sidebar:
    st.markdown(SIDEBAR_BRAND_HTML, unsafe_allow_html=True)
    st.markdown('<div class="sq-nav-label">Menu</div>', unsafe_allow_html=True)

    for key, icon, label in [
        ("home",   SIDEBAR_ICON_HOME,      "Home"),
        ("main",   SIDEBAR_ICON_DASHBOARD, "Dashboard"),
        ("engine", SIDEBAR_ICON_ENGINE,    "Engine"),
    ]:
        row = st.columns([0.22, 0.78])
        with row[0]:
            st.markdown(icon, unsafe_allow_html=True)
        with row[1]:
            btn_type = "primary" if st.session_state.fin_view == key else "secondary"
            if st.button(label, use_container_width=True, key=f"sb_{key}", type=btn_type):
                st.session_state.fin_view = key
                st.rerun()

    dim_section = st.empty()

    st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
    with st.expander("CSV Upload", expanded=True):
        uploaded_files = st.file_uploader(
            "Upload CSV", type="csv", key="sb_csv_upload", label_visibility="collapsed", accept_multiple_files=True,
        )

    # ── 데이터 선택 ───────────────────────────────
    if uploaded_files:
        st.session_state['uploaded_files'] = uploaded_files
    
    if 'uploaded_files' in st.session_state and st.session_state['uploaded_files']:
        file_names = [f.name for f in st.session_state['uploaded_files']]
        selected_file = st.selectbox("Select File", file_names, key="sb_file_selector")
        
        # 선택된 파일 찾기
        target_file = next(f for f in st.session_state['uploaded_files'] if f.name == selected_file)
        df = pd.read_csv(target_file)
        fname = target_file.name
        st.session_state['saved_df'] = df
        st.session_state['selected_fname'] = fname
    
    # 2. 파일이 선택되지 않았지만 기존 세션에 데이터가 있는 경우
    elif 'saved_df' in st.session_state:
        df = st.session_state['saved_df']
        fname = st.session_state.get('selected_fname', "Uploaded_Data.csv")
    else:
        df = None
        fname = ""

# ── 메인 렌더 ─────────────────────────────────
classify_result  = None
indicator_result = None
chart_result     = None
insight_result   = None

# 데이터(df)가 정상적으로 로드되었다면 가장 먼저 분류 엔진을 돌립니다.
if df is not None:
    classify_result = classify(df)

if classify_result is not None and df is not None:
    indicator_result = calculate(df, classify_result)
    chart_result     = select_chart(classify_result)
    insight_result   = generate(classify_result, indicator_result)
    if classify_result:
        st.caption(f"Loaded: **{fname}** · {len(df)} rows")

mkt_data = _get_market_data()
current_theme = st.get_option("theme.base") or "light"
if "last_theme" not in st.session_state:
    st.session_state.last_theme = current_theme
elif st.session_state.last_theme != current_theme:
    st.session_state.last_theme = current_theme
    st.rerun()

if "show_ma" not in st.session_state: st.session_state.show_ma = True
if "show_bb" not in st.session_state: st.session_state.show_bb = False
if "show_vol" not in st.session_state: st.session_state.show_vol = True

build(
    st.session_state.fin_view,
    classify_result, indicator_result, chart_result, insight_result,
    df, mkt_data, theme=current_theme,
)
