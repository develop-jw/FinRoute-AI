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

if "fin_view" not in st.session_state:
    st.session_state.fin_view = "home"

st.markdown(THEME_CSS, unsafe_allow_html=True)

DATA_DIR = Path(__file__).resolve().parent / "data"

def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """한글 컬럼명을 영어로 변환."""
    col_map = {
        "날짜": "date", "일자": "date", "기준일": "date", "거래일": "date",
        "종가": "close", "현재가": "close", "가격": "price",
        "시가": "open", "고가": "high", "저가": "low",
        "거래량": "volume", "거래대금": "trading_value",
        "비중": "weight", "투자비중": "weight", "보유비중": "weight",
        "수익률": "return", "수익": "return", "손익률": "return",
        "자산명": "asset_name", "자산": "asset_name", "종목명": "asset_name",
        "분기": "quarter", "기간": "quarter",
        "티커": "ticker", "종목코드": "ticker",
        "매수매도": "side", "구분": "side", "거래구분": "side",
        "수량": "quantity", "거래수량": "quantity",
        "수수료": "fee", "거래비용": "fee",
        "목표비중": "target_weight", "벤치마크비중": "benchmark_weight",
        "보유금액": "holding_amount", "평가금액": "holding_amount",
    }
    return df.rename(columns={k: v for k, v in col_map.items() if k in df.columns})

# ── 시장 지표 ─────────────────────────────────
@st.cache_data(ttl=300)
def _get_market_data() -> list[dict]:
    try:
        import yfinance as yf
        tickers = {
            "KOSPI":        "^KS11",
            "NASDAQ":       "^IXIC",
            "S&P 500":      "^GSPC",
            "Bitcoin":      "BTC-USD",
            "Gold":         "GC=F",
            "WTI":          "CL=F",
            "10Y Treasury": "^TNX",
            "Nikkei 225":   "^N225",
            "USD/KRW":      "KRW=X",
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

# ── 데이터 관리 및 로드 ──────────────────────────
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = {}  # {filename: df}
if "active_file" not in st.session_state:
    st.session_state.active_file = None

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

    # CSV Manager Drawer
    with st.sidebar.expander("📂 CSV Files Manager", expanded=True):
        uploaded_files = st.file_uploader(
            "Upload CSVs", type="csv", key="multi_csv_upload", accept_multiple_files=True,
        )
        
        if uploaded_files:
            for f in uploaded_files:
                if f.name not in st.session_state.uploaded_files:
                    try:
                        # 파일 인코딩 에러 방지
                        st.session_state.uploaded_files[f.name] = _normalize_columns(pd.read_csv(f))
                    except pd.errors.EmptyDataError:
                        st.error(f"Error: {f.name} is empty.")
                        continue
                    except UnicodeDecodeError:
                        try:
                            f.seek(0)
                            st.session_state.uploaded_files[f.name] = _normalize_columns(pd.read_csv(f, encoding='cp949'))
                        except pd.errors.EmptyDataError:
                            st.error(f"Error: {f.name} is empty.")
                            continue
                        except Exception as e:
                            st.error(f"Error reading {f.name}: {e}")
                            continue
                    except Exception as e:
                        st.error(f"Error reading {f.name}: {e}")
                        continue
                    
                    if st.session_state.active_file is None:
                        st.session_state.active_file = f.name
            
        if st.session_state.uploaded_files:
            selected = st.radio(
                "Select active file", 
                list(st.session_state.uploaded_files.keys()),
                index=list(st.session_state.uploaded_files.keys()).index(st.session_state.active_file) 
                if st.session_state.active_file in st.session_state.uploaded_files else 0,
                label_visibility="collapsed"
            )
            if selected != st.session_state.active_file:
                st.session_state.active_file = selected
                st.rerun()

    # 차원 필 — 사이드바 하단
    st.divider()
    classify_result_for_dim = None
    df_for_dim = st.session_state.uploaded_files.get(st.session_state.active_file)
    if df_for_dim is not None and not df_for_dim.empty:
        try:
            classify_result_for_dim = classify(df_for_dim)
        except Exception:
            pass
    dim = classify_result_for_dim["dimension"] if classify_result_for_dim else None
    st.markdown(dimension_pills_html(dim), unsafe_allow_html=True)

# ── 데이터 동기화 ──────────────────────────────
df = st.session_state.uploaded_files.get(st.session_state.active_file)
fname = st.session_state.active_file


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
build(
    st.session_state.fin_view,
    classify_result, indicator_result, chart_result, insight_result,
    df, mkt_data,
)
