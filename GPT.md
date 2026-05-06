# GPT.md — GPT-4o / Copilot 전용 파이프라인 인터페이스 정의서

## 👤 역할 정의
당신은 **시니어 금융 퀀트 개발자**입니다. 이 문서는 01~05 파일 간의 데이터 흐름과 반환 형태를 정의하는 절대적인 가이드라인입니다. 모든 구현은 이 인터페이스 구조를 엄격히 준수해야 합니다.

---

## 🛠️ 기술 스택 (Technical Stack)

| 항목 | 내용 |
|------|------|
| 언어 | Python |
| 프레임워크 | Streamlit |
| 차트 | Plotly |
| LLM | GPT-4o / Claude / Gemini |
| 분류 | scikit-learn (cosine_similarity) |
| 진입점 | app.py |
| API 키 | .env 파일의 ANTHROPIC_API_KEY 또는 OPENAI_API_KEY 환경변수로 관리 |

---

## 📂 파일 구조 (File Structure)

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

## 🔄 전체 데이터 흐름 (Overall Data Flow)

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

## 💻 app.py 호출 구조 (App Invocation Structure)

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

## 📝 파일별 함수 시그니처 및 반환 형태

### 1. classifier.py (01_standard.md 구현)

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

---

### 2. indicator_calculator.py (02_indicator.md 구현)

```python
def calculate(df: pd.DataFrame, classify_result: dict) -> dict:
```

**반환값 (indicator_result)**
*class_type × dimension 조합에 따라 해당 항목만 값을 가지며 나머지는 None으로 반환한다.*

```python
{
    # 공통
    "cum_return":    float | None,   # 누적 수익률 (Hero Total Return용)

    # TimeSeries 1D
    "RSI": float | None, "MDD": float | None, "Sharpe": float | None,
    "ATR": float | None, "MA20": float | None, "MA60": float | None,
    "trend": str | None,   # "golden" | "dead"

    # TimeSeries 2D
    "coint_p": float | None, "zscore": float | None, "roll_corr": float | None,
    "beta": float | None, "halflife": float | None,

    # TimeSeries ND
    "avg_corr": float | None, "pca_first": float | None, "VaR": float | None,
    "centrality": dict | None, "max_corr_pair": str | None,

    # Static 1D
    "recent_return": float | None, "eff_n": float | None, "HHI": float | None, "top3_conc": float | None,

    # Static 2D
    "active_share": float | None, "tracking_err": float | None, "info_ratio": float | None, "bm_return": float | None,

    # Static ND
    "risk_contrib": dict | None, "max_risk_asset": str | None,

    # Activity 1D
    "vwap_dev": float | None, "profit_factor": float | None, "trade_freq": float | None, "total_fee": float | None, "win_rate": float | None,

    # Activity 2D
    "switch_cost": float | None, "switch_ratio": float | None, "cross_interval": float | None, "fee_cost": float | None, "net_profit": float | None,

    # Activity ND
    "turnover_rate": float | None, "annual_fee": float | None, "avg_hold": float | None, "realized_pnl": float | None, "unrealized_pnl": float | None,
}
```

---

### 3. chart_selector.py (03_visualization.md 구현)

```python
def select_chart(classify_result: dict) -> dict:
```

**반환값 (chart_result)**

```python
{
    "main_chart": str,   # 메인 차트 식별자 ("candlestick" | "dual_line" | "heatmap" | "line" | "donut" | "bar" | ...)
    "sub_charts": list,  # 서브 차트 식별자 리스트 (최대 2개, e.g., ["rsi"] | ["zscore", "rolling_corr"])
}
```

---

### 4. insight_generator.py (05_insight.md 구현)

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

---

### 5. dashboard_builder.py (04_dashboard.md 구현)

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
- Streamlit 화면 직접 렌더링
- `04_dashboard.md`의 배치 순서와 구성 규칙을 엄격히 따른다.

---

## 📊 파일 간 데이터 참조 요약 (Data Reference Summary)

| 데이터 | 생성 파일 | 참조 파일 |
|--------|-----------|-----------|
| classify_result | classifier.py | chart_selector.py, insight_generator.py, dashboard_builder.py |
| indicator_result | indicator_calculator.py | insight_generator.py, dashboard_builder.py |
| chart_result | chart_selector.py | dashboard_builder.py |
| insight_result | insight_generator.py | dashboard_builder.py |

---

## 🚫 글로벌 규칙 및 제약 사항
1. **상세 로직 참고:** 모든 세부 구현 로직은 `skills/` 폴더 내의 각 단계별 `.md` 파일을 최우선으로 준수한다.
2. **데이터 인터페이스:** 위 명세에 정의된 딕셔너리 구조와 키(Keys)를 절대 변경하지 않는다.
3. **Action Console 레이아웃:** 
   - 반드시 **세로(상-하) 구조**로 렌더링한다.
   - 대시보드 화면(4-8 섹션)에는 리밸런싱 및 헤지 제안을 **표시하지 않는다** (단, 데이터 구조인 `insight_result`에는 필드를 유지한다).
4. **코드 일관성:** 모든 모듈은 `00_interface.md`에 정의된 데이터 흐름을 충실히 따른다.
