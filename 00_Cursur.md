# 00_Cursor.md — 전체 파이프라인 인터페이스 정의

> 이 문서는 01~05 파일 간 데이터 흐름과 반환 형태를 정의한다.
> Cursor는 구현 전 반드시 이 파일을 먼저 읽는다.

---

## 기술 스택

| 항목 | 내용 |
|------|------|
| 언어 | Python |
| 프레임워크 | Streamlit |
| 차트 | Plotly |
| LLM | Claude Sonnet (claude-sonnet-4-5) |
| 분류 | scikit-learn (cosine_similarity) |
| 진입점 | app.py |
| API 키 | .env 파일의 ANTHROPIC_API_KEY 환경변수로 관리 |

---

## 파일 구조

```
app.py                      ← Streamlit 진입점, 전체 파이프라인 실행
modules/
  classifier.py             ← 01_standard.md 구현 (클래스 분류 + 차원 판별)
  indicator_calculator.py   ← 02_indicator.md 구현 (KPI 지표 계산)
  chart_selector.py         ← 03_visualization.md 구현 (차트 선택)
  dashboard_builder.py      ← 04_dashboard.md 구현 (대시보드 렌더링)
  insight_generator.py      ← 05_insight.md 구현 (LLM 인사이트 생성)
.env                        ← API 키 (Git 제외)
```

---

## 전체 데이터 흐름

```
CSV 업로드 (app.py)
    ↓
classifier.py           → classify_result 반환
    ↓
indicator_calculator.py → indicator_result 반환
    ↓
chart_selector.py       → chart_result 반환
    ↓
insight_generator.py    → insight_result 반환
    ↓
dashboard_builder.py    → Streamlit 화면 렌더링 (반환값 없음)
```

---

## app.py 호출 구조

```python
import streamlit as st
import pandas as pd
from modules.classifier           import classify
from modules.indicator_calculator import calculate
from modules.chart_selector       import select_chart
from modules.insight_generator    import generate
from modules.dashboard_builder    import build

st.set_page_config(layout="wide")

uploaded = st.file_uploader("CSV 업로드", type="csv")

if uploaded:
    df = pd.read_csv(uploaded)

    classify_result  = classify(df)
    indicator_result = calculate(df, classify_result)
    chart_result     = select_chart(classify_result)
    insight_result   = generate(classify_result, indicator_result)

    build(classify_result, indicator_result, chart_result, insight_result, df)
```

---

## 파일별 함수 시그니처 및 반환 형태

---

### classifier.py (01_standard.md 구현)

```python
def classify(df: pd.DataFrame) -> dict:
```

**반환값 (classify_result)**

```python
{
    "class_type": str,   # "TimeSeries" | "Static" | "Activity"
    "dimension":  str,   # "1D" | "2D" | "ND"
    "dashboard":  str,   # "stock" | "portfolio"
    "vector":     list,  # 18D 이진 벡터 [0, 1, 1, 0, ...]  (길이 18 고정)
    "similarity": dict,  # {"TimeSeries": float, "Static": float, "Activity": float}
    "goals":      list,  # 자동 추론된 분석 목적 태그 리스트
                         # 예: ["goal_trend", "goal_anomaly"]
                         # 가능한 값: "goal_trend" | "goal_comp" | "goal_compare" |
                         #            "goal_corr" | "goal_dist" | "goal_anomaly" |
                         #            "goal_spread" | "goal_relation"
}
```

**예시**
```python
{
    "class_type": "TimeSeries",
    "dimension":  "1D",
    "dashboard":  "stock",
    "vector":     [1,1,1,0,1,0,0,0,1,0,0,1,0,0,0,0,0,0],
    "similarity": {"TimeSeries": 0.94, "Static": 0.19, "Activity": 0.22},
    "goals":      ["goal_trend", "goal_anomaly"],
}
```

---

### indicator_calculator.py (02_indicator.md 구현)

```python
def calculate(df: pd.DataFrame, classify_result: dict) -> dict:
```

**반환값 (indicator_result)**

```python
# class_type × dimension 조합에 따라 해당 항목만 값을 가지며
# 나머지는 None으로 반환한다.

{
    # 공통
    "cum_return":    float | None,   # 누적 수익률 (Hero Total Return용)

    # TimeSeries 1D
    "RSI":           float | None,
    "MDD":           float | None,
    "Sharpe":        float | None,
    "ATR":           float | None,
    "MA20":          float | None,
    "MA60":          float | None,
    "trend":         str   | None,   # "golden" | "dead"

    # TimeSeries 2D
    "coint_p":       float | None,   # 공적분 p-value
    "zscore":        float | None,   # Z-score
    "roll_corr":     float | None,   # 롤링 상관계수
    "beta":          float | None,   # 헤지비율 β
    "halflife":      float | None,   # 반감기

    # TimeSeries ND
    "avg_corr":      float | None,   # 평균 상관계수
    "pca_first":     float | None,   # PCA 1st PC 기여율
    "VaR":           float | None,   # VaR (95%)
    "centrality":    dict  | None,   # {"종목명": float, ...}
    "max_corr_pair": str   | None,   # 최대 상관 쌍 "A-B"

    # Static 1D
    "recent_return": float | None,   # 최근 분기 수익률
    "eff_n":         float | None,   # 유효 자산 수
    "HHI":           float | None,   # HHI 지수
    "top3_conc":     float | None,   # Top-3 집중도

    # Static 2D
    "active_share":  float | None,   # 액티브 셰어
    "tracking_err":  float | None,   # 추적 오차 (TE)
    "info_ratio":    float | None,   # 정보 비율 (IR)
    "bm_return":     float | None,   # 벤치마크 누적 수익

    # Static ND
    "risk_contrib":  dict  | None,   # {"자산명": float, ...}
    "max_risk_asset":str   | None,   # 최대 리스크 기여 자산명

    # Activity 1D
    "vwap_dev":      float | None,   # VWAP 대비 단가
    "profit_factor": float | None,   # 손익비
    "trade_freq":    float | None,   # 매매 빈도
    "total_fee":     float | None,   # 총 수수료
    "win_rate":      float | None,   # 승률

    # Activity 2D
    "switch_cost":   float | None,   # 스위칭 기회비용
    "switch_ratio":  float | None,   # 스위칭 비율
    "cross_interval":float | None,   # 교차 거래 간격
    "fee_cost":      float | None,   # 수수료 비용
    "net_profit":    float | None,   # 순수익

    # Activity ND
    "turnover_rate": float | None,   # 포트폴리오 회전율
    "annual_fee":    float | None,   # 연간 수수료 합계
    "avg_hold":      float | None,   # 평균 보유 기간
    "realized_pnl":  float | None,   # 실현 손익
    "unrealized_pnl":float | None,   # 미실현 손익
}
```

---

### chart_selector.py (03_visualization.md 구현)

```python
def select_chart(classify_result: dict) -> dict:
```

**반환값 (chart_result)**

```python
{
    "main_chart": str,   # 메인 차트 식별자
                         # "candlestick" | "dual_line" | "heatmap" |
                         # "line" | "donut" | "bar" | ...
    "sub_charts": list,  # 서브 차트 식별자 리스트 (최대 2개)
                         # ["rsi"] | ["zscore", "rolling_corr"] | ...
}
```

**예시**
```python
# TimeSeries 1D
{"main_chart": "candlestick", "sub_charts": ["rsi"]}

# TimeSeries 2D
{"main_chart": "dual_line", "sub_charts": ["zscore", "rolling_corr"]}

# Static ND
{"main_chart": "donut", "sub_charts": ["risk_bar", "stacked_area"]}
```

---

### insight_generator.py (05_insight.md 구현)

```python
def generate(classify_result: dict, indicator_result: dict) -> dict:
```

**반환값 (insight_result)**

```python
{
    "signal":      str,   # "BUY" | "HOLD" | "REDUCE"
    "confidence":  int,   # 0 ~ 100
    "regime":      str,   # "RISK-ON" | "RISK-OFF"
    "action":      str,   # 지금 할 행동 (LLM 생성)
    "why_now":     str,   # 판단 근거, [태그] 형식 포함 (LLM 생성)
    "rebalancing": str,   # 리밸런싱 제안 (LLM 생성)
    "hedge":       str,   # 헤지 제안 (LLM 생성)
    "llm_input":   str,   # LLM에 전달된 입력값 요약 문자열 (화면 표시용)
}
```

**예시**
```python
{
    "signal":      "HOLD",
    "confidence":  72,
    "regime":      "RISK-OFF",
    "action":      "손절선(ATR×2) 유지하며 신호 대기.",
    "why_now":     "[추세 파악] MA20 < MA60 — 단기 하락 추세 지속",
    "rebalancing": "현 비중 유지. 손절선 확인 대기.",
    "hedge":       "인버스 ETF 또는 풋옵션 헤지 검토.",
    "llm_input":   "[추세 파악] MA20<MA60 · [이상값 감지] RSI 25.9 · MDD 15.2%",
}
```

---

### dashboard_builder.py (04_dashboard.md 구현)

```python
def build(
    classify_result:  dict,
    indicator_result: dict,
    chart_result:     dict,
    insight_result:   dict,
    df:               pd.DataFrame,
) -> None:
```

- 반환값 없음
- Streamlit 화면을 직접 렌더링한다
- 04_dashboard.md의 배치 순서와 구성 규칙을 따른다

---

## 파일 간 데이터 참조 요약

| 데이터 | 생성 파일 | 참조 파일 |
|--------|-----------|-----------|
| classify_result | classifier.py | chart_selector.py, insight_generator.py, dashboard_builder.py |
| indicator_result | indicator_calculator.py | insight_generator.py, dashboard_builder.py |
| chart_result | chart_selector.py | dashboard_builder.py |
| insight_result | insight_generator.py | dashboard_builder.py |