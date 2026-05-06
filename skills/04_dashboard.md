# 04_dashboard.md — 대시보드 구성 규칙

> dashboard_builder.py 구현 규칙을 정의한다.  
> classify_result, indicator_result, chart_result, insight_result, df, mkt_data를 입력받아 화면을 렌더링한다.

---

## 4-1. 전체 레이아웃 구조

```
┌───────────┬──────────────────────────────┬──────────────┐
│   좌측    │         중앙 메인             │  우측 배너   │
│ (Sidebar) │         (스크롤)             │    (고정)    │
│           │                              │              │
│ 로고      │  Home: 시장 지표 카드         │  Market      │
│ Menu      │  Dashboard: Hero → KPI →     │  Indicators  │
│ Home      │    차트 → Action Console     │              │
│ Dashboard │  Engine: 파이프라인 →         │  Insights    │
│ Engine    │    유사도 → 벡터 → 목적       │  (Events /   │
│           │                              │  Goals /     │
│ 차원탭    │                              │  Signal /    │
│ CSV Upload│                              │  News)       │
└───────────┴──────────────────────────────┴──────────────┘
```

| 영역 | 역할 |
|------|------|
| 좌측 (Sidebar) | 뷰 전환 + 차원 표시 + CSV 업로드 |
| 중앙 메인 | 뷰별 콘텐츠 렌더링 (스크롤) |
| 우측 배너 | 시장 지표 + Insights (Home 뷰 제외) |

---

## 4-2. 뷰 분기 규칙

`fin_view` 값에 따라 중앙 콘텐츠를 분기한다.

| fin_view | 중앙 콘텐츠 | 우측 배너 |
|----------|-------------|-----------|
| "home" | 시장 지표 카드 + 스파크라인 | 없음 |
| "main" | Hero → KPI → 차트 → Action Console | 있음 |
| "engine" | 파이프라인 → 유사도 → 벡터 → 목적 | 있음 |

**CSV 미업로드 시**
- Home 뷰: 시장 지표만 표시
- Dashboard·Engine 뷰: 업로드 안내 화면 표시

**뷰 전환 시 데이터 유지 규칙**
- Dashboard ↔ Engine: 업로드된 CSV 데이터 유지
- Home 이동 시: 데이터 초기화

---

## 4-3. Sidebar 구성 규칙

**포함 요소 (위 → 아래)**
```
[FinRoute AI 로고]
────────────────
MENU
  Home      버튼
  Dashboard 버튼
  Engine    버튼
────────────────
DATA DIMENSION
  [1D] [2D] [ND]  ← classify_result["dimension"] 자동 활성화
────────────────
CSV UPLOAD
  파일 업로드 위젯
```

**규칙**
- 활성 뷰 버튼 강조 표시
- 차원 탭은 자동 결정이며 사용자가 변경할 수 없다

---

## 4-4. Home 뷰

대시보드 진입 시 가장 먼저 노출되는 화면으로, 시장 상황을 요약하고 적극적으로 데이터 업로드를 유도한다.

**우측 배너**
- 없음 (Home 뷰에서는 중앙 영역만 노출되며 우측 배너는 미표시)

**중앙 배치 순서 (위 → 아래 반드시 준수)**
```text
1. Market Sentiment (AI 시장 분위기 요약)
2. Market Indicators (3x2 마켓 카드)
3. Enhanced CSV Upload Zone (메인 업로드 영역)
``` 

**1. Market Sentiment (시장 분위기 요약)**
- 마켓 카드 하단에 전체 너비의 알림 박스 형태로 배치
- 배경 스타일: 옅은 틸(`#eef7f4`)
- 내용: `mkt_data`의 등락 조합을 분석하여 현재 시장 국면을 동적으로 한 줄 요약
  - (예: "✦ 오늘 시장은 기술주 중심의 강한 반등세가 이어지며 위험 자산 선호(Risk-On) 국면입니다.")

**2. Market Indicators (마켓 카드)**
- `st.columns(3)`를 활용하여 3열 2행(3x2) 그리드로 6개 주요 지표 배치
- 각 카드 구성: 지표명 / 현재가 / 등락률(▲▼) / 미니 스파크라인(Area 차트)
- 카드 스타일: 배경 `#f7f9fb`, 테두리 라운드 `14px`, 가벼운 그림자 적용
- 동적 색상: 전일 대비 상승 시 초록(`#1a7f37`), 하락 시 빨강(`#b42318`)을 텍스트와 차트 라인에 적용

**3. Enhanced CSV Upload Zone (메인 업로드 영역)**
- 중앙 하단에 가장 큰 면적을 차지하도록 넓은 점선 테두리(`.sq-upload-zone`, 주색 `#0a5c5c` 2px) 박스 배치
- 포함 요소:
  - 파일 업로드 유도 안내 문구 ("분석할 포트폴리오/종목 CSV를 이곳에 드래그하세요")
  - `st.file_uploader` 위젯 (사이드바 위젯과 동일한 key/상태 공유)
  - 샘플 CSV 다운로드 링크 ("어떤 파일을 올려야 할지 모르겠나요? [샘플 다운로드]")
- 동작: 이 영역에 파일 업로드가 완료되면 즉시 대시보드 뷰(`st.session_state.fin_view = "main"`)로 자동 전환된다.

---

## 4-5. Hero Decision Layer 구성 규칙

**5개 블록 고정 구성 (순서 변경 불가)**

```
┌──────────┬──────────────┬─────────────┬──────────────────┬──────────────┐
│  LIVE    │    TOTAL     │    RISK     │    SUGGESTED     │  HEDGE /     │
│  SIGNAL  │    RETURN    │    REGIME   │     ACTION       │  REBALANCING │
└──────────┴──────────────┴─────────────┴──────────────────┴──────────────┘
```

| 블록 | 표시 내용 | 데이터 출처 |
|------|-----------|-------------|
| LIVE SIGNAL | BUY / HOLD / REDUCE + 신뢰도 progress bar | insight_result["signal"], ["confidence"] |
| TOTAL RETURN | 기간 누적 수익률 | indicator_result["cum_return"] |
| RISK REGIME | RISK-ON / RISK-OFF | insight_result["regime"] |
| SUGGESTED ACTION | 한 줄 행동 지침 | insight_result["action"] |
| HEDGE / REBALANCING | 헤지 또는 리밸런싱 제안 | insight_result["hedge"] |

**규칙**
- Hero 배경: 짙은 틸 그라디언트 고정
- classify_result["dashboard"] == "stock" → 마지막 블록: "HEDGE"
- classify_result["dashboard"] == "portfolio" → 마지막 블록: "REBALANCING"

---

## 4-6. KPI 카드 행 구성 규칙

- 항상 5개 카드, 가로 1열 배치
- 각 카드: 지표명 / 계산값 / 부연 설명 / 상태 배지
- 상태 배지: 양호(초록) / 주의(주황) / 위험(빨강) / 중립(회색)
- KPI 카드 hover 시 위로 튀어오르는 애니메이션 적용

---

## 4-7. 우측 배너 구성 규칙

**2개 독립 박스 구성**

```
[박스1] Market Indicators
────────────────────────
[박스2] Insights
  ① Auto Events
  ② Analysis Goals
  ③ Signal History
  ④ Related News
```

**[박스1] Market Indicators**
- KOSPI / NASDAQ / S&P500 / Gold / WTI / USD/KRW
- 현재가 + 등락률 (상승 초록 / 하락 빨강)
- 5분 캐시

**① Auto Events**
- 고정 높이, 내용 많으면 상하 스크롤
- 이벤트 유형별 색상 구분 (4-10 참조)
- 이벤트 없을 시 "No events detected"

**② Analysis Goals**
- classify_result["goals"] 기반 자동 추론
- ON(✦) / OFF(○) 칩 형태 표시
- 영어 코드 미표시

**③ Signal History**
- 고정 높이, 내용 많으면 상하 스크롤
- TimeSeries 1D 한정 동작
- BUY(초록) / REDUCE(빨강) 배경 구분
- 날짜 역순, 중복 제거, 최대 12건

| 시그널 | 조건 |
|--------|------|
| BUY | 골든크로스 (MA20 > MA60 전환) |
| REDUCE | 데드크로스 (MA20 < MA60 전환) |
| BUY | RSI < 30 진입 |
| REDUCE | RSI > 70 진입 |

**④ Related News**
- CSV 티커 컬럼 자동 감지
- 숫자 티커 자동 변환: 5930 → 005930 → 005930.KS
- NewsAPI 우선, Google News RSS 폴백
- 10분 캐시

---

## 4-8. Action Console 구성 규칙 (AI 인사이트)

**구조**
```
┌──────────────────────────────────────────────────────┐
│  Action Console                       [AI 판단 근거] │
├──────────────────────────────────────────────────────┤
│  LLM 입력값: insight_result["llm_input"] 표시         │
├──────────────────────────────────────────────────────┤
│  지금 할 행동: insight_result["action"]               │
├──────────────────────────────────────────────────────┤
│  Why now?: insight_result["why_now"]                 │
└──────────────────────────────────────────────────────┘
```

| 블록 | 데이터 출처 | 내용 |
|------|-------------|------|
| 지금 할 행동 | insight_result["action"] | **지금 즉시 할 행동** (핵심 지침) |
| Why now? | insight_result["why_now"] | **판단 근거** (분석 목적 태그 포함) |

**① 인사이트 도출 핵심 로직 (Dots Connection)**
1.  **데이터 성격 파악**: `01_standard`의 분류(TimeSeries/Static/Activity)에 따라 분석의 톤앤매너 결정.
2.  **정량 수치 분석**: `02_indicator`의 KPI가 임계치를 넘었는지, 과거 대비 어떤 상태인지 확인.
3.  **동적 맥락 결합**: `04_dashboard`의 '자동 이벤트'를 결합하여 "왜 지금(Why now?)" 이 신호가 중요한지 해석.

**② LLM 추론 및 작성 규칙**
- **페르소나**: 15년 경력의 시니어 퀀트 애널리스트 어조 (결론 위주, 수치 기반).
- **Why now? 작성**: 반드시 `01_standard.md`의 `goals` 중 가장 적합한 것을 골라 `[태그명]`을 서두에 기입.
  - 예: `[추세 파악] MA20 골든크로스와 RSI 저평가...`
- **하이브리드 모드**: API 키 부재 시 '퀀트 룰 엔진' 결과로 대체 (Signal, Action, Why now 자동 생성).

**규칙**
- LLM 입력값 행을 항상 상단에 노출한다.
- **지금 할 행동**과 **Why now?**는 가로 병렬이 아닌 **세로(위-아래) 순서**로 배치한다.
- 리밸런싱 및 헤지 제안 블록은 배치하지 않는다.
- Action Console은 차트 하단에 배치한다.

---

## 4-9. 엔진 뷰 구성 규칙

**전환 조건 및 네비게이션 로직**
- **⚙️ Engine 클릭:** 엔진 뷰로 전환. (데이터 분석/추론 과정 노출, 차원 탭 비활성화)
- **📊 Dashboard 클릭:** 대시보드 뷰로 전환. (메인 분석 화면 노출, 차원 탭 활성화)
- **🏠 Home 클릭:** 홈 뷰로 전환. (초기 업로드 화면 및 시장 요약 노출, 차원 탭 비활성화)

*제약 조건:* CSV 데이터가 업로드되지 않은 상태에서는 Dashboard와 Engine 뷰 진입이 제한되거나, 진입 시 "데이터 업로드 필요" 빈 화면을 띄운다.

**포함 섹션 (위 → 아래 순서)**
**① Analysis Pipeline (전체 분석 파이프라인)**
- 4단계 순차 fade-in 애니메이션 적용 (`18D Vector` → `Class` → `Dimension` → `Visualization`)
- 하단에 현재 판별 결과 명확히 표시 (`class_type` / `dimension` / `dashboard`)

**② Goal Inference (분석 의도 및 목적 추론)**
- **Active Goal Chips:** `_GOAL_META` 기준 추론된 목적들을 칩 형태로 나열 (ON 상태는 틸 색상 포인트, OFF는 회색 비활성)
- **Reasoning Log (추론 근거):** 활성화된 목적이 어떤 벡터/컬럼에 의해 트리거되었는지 인과관계 명시 (예: `[비중 최적화] ← Target Weight 및 Weight 벡터 동시 감지`)
- **LLM Prompt Preview:** 최종 조합된 `insight_result["llm_input"]` 문장을 고정폭 폰트(Monospace)와 짙은 배경의 박스 안에 터미널 로그처럼 노출하여 시스템 투명성 강조

**③ Class Similarity & System Meta (클래스 분류 결과 및 엔진 상태)**
- **Class Similarity:** 시계열 / 스냅샷 / 매매활동 3개 카드로 코사인 유사도(%) 표시. 1위(Best Match) 클래스는 카드 배경색 하이라이트 적용.
- **Data Meta & Engine Status:** 하단에 슬림한 정보 바(Bar) 형태로 배치
  - 데이터 품질: `Total Rows`, `Missing Values` 등 원본 CSV 메타 정보 노출
  - 활성 엔진 상태: `[Active Engine: Anthropic LLM 🟢]` 또는 `[Active Engine: Quant Rule Engine (Fallback) 🟡]` 로 표시하여 하이브리드 로직의 안정성 증명

**④ 18D Feature Vector (Input Scan)**
- **3개 클래스 그룹 × 6열 매트릭스** 구조로 전면 개편하여 내부 분류 알고리즘과의 정합성 확보
- 각 그룹별 6개 감지 대상 컬럼:
  1. **TimeSeries (시계열):** `Date` / `Open` / `High` / `Low` / `Close` / `Volume`
  2. **Static (스냅샷):** `Asset(Name)` / `Weight` / `Target` / `Value` / `Return` / `Quarter(Date)`
  3. **Activity (매매):** `Timestamp` / `Buy/Sell` / `Quantity` / `Price` / `Fee` / `Ticker`
- 감지된 항목(1): 틸 배경 + 틸 테두리 + "●" 아이콘으로 시각적 강조
- 미감지 항목(0): 흰 배경 + 회색 테두리 + "·" 아이콘으로 비활성 처리

**규칙**
- 엔진 뷰는 현재 선택된 차원 기준으로 렌더링된다.
- 우측 배너는 엔진 뷰에서도 메인 대시보드와 동일하게 유지하여 화면의 통일성을 지킨다.

---

## 4-10. 동적 이벤트 감지 규칙

| 이벤트 | 감지 조건 | 적용 Class/Dimension | 색상 |
|--------|-----------|----------------------|------|
| 골든크로스 | MA20이 MA60 상향 돌파 | TimeSeries 1D | 초록 |
| 데드크로스 | MA20이 MA60 하향 돌파 | TimeSeries 1D | 빨강 |
| RSI 과매수 | RSI > 70 | TimeSeries 1D | 주황 |
| RSI 과매도 | RSI < 30 | TimeSeries 1D | 초록 |
| Z-score 이탈 | Z-score > +2 또는 < -2 | TimeSeries 2D | 주황/초록 |
| 페어 약화 | 롤링 상관계수 < 0.5 | TimeSeries 2D | 빨강 |
| 동조화 경고 | 평균 상관계수 > 0.7 | TimeSeries ND | 주황 |
| HHI 초과 | HHI > 2,500 | Static ND | 빨강 |
| Top-3 집중 | Top-3 비중 합계 > 60% | Static ND | 주황 |
| 비중 이탈 | 실제 비중이 목표 대비 ±5%p 초과 | Static 1D/2D | 주황 |

**규칙**
- 동일 유형 중복 제거: label별 첫 발생일만 표시
- 최대 8건, 날짜 역순 정렬
- 이벤트 없을 시 "No events detected"

---

## 4-11. Class × Dimension별 차트 배치 규칙

classify_result["class_type"] × classify_result["dimension"] 조합에 따라 자동 배치한다.

| Class | Dimension | 메인 차트 | 서브 차트 |
|-------|-----------|-----------|-----------|
| TimeSeries | 1D | Candlestick + MA | RSI |
| TimeSeries | 2D | Dual Line (정규화) | Z-score / Rolling Correlation |
| TimeSeries | ND | Correlation Heatmap | Network Graph |
| Static | 1D | Line (누적 수익률) | Grouped Bar (기여도) |
| Static | 2D | Dual Line (포트 vs 벤치마크) | Bar (초과수익률) / Bar (비중 괴리율) |
| Static | ND | Donut (자산 구성) | Grouped Bar (리스크 기여도) / Stacked Area (비중 추이) |
| Activity | 1D | Bar (VWAP 대비 단가) | Scatter (손익비) |
| Activity | 2D | Dual Line (자산 교체 비교) | Bar (스위칭 기회비용) |
| Activity | ND | Bar (회전율) | Timeline (거래 이력) |

**규칙**
- 메인 차트 1개, 서브 차트 최대 2개
- 서브 차트 2개인 경우 → 2열(st.columns(2)) 배치
- 서브 차트 1개인 경우 → 전체 너비 배치
- 차트 카드 hover 시 위로 살짝 이동하는 애니메이션 적용

---

## 4-12. Class × Dimension별 KPI 카드 지표 목록

### TimeSeries

| Dimension | KPI 1 | KPI 2 | KPI 3 | KPI 4 | KPI 5 |
|-----------|-------|-------|-------|-------|-------|
| 1D | RSI (14) | MDD | 샤프 비율 | ATR (14) | 추세 (MA20 vs MA60) |
| 2D | 공적분 p-value | Z-score | 롤링 상관계수 | 헤지비율 β | 반감기 |
| ND | 평균 상관계수 | PCA 1st PC | VaR (95%) | 네트워크 중심성 | 최대 상관 쌍 |

### Static

| Dimension | KPI 1 | KPI 2 | KPI 3 | KPI 4 | KPI 5 |
|-----------|-------|-------|-------|-------|-------|
| 1D | 누적 수익률 | 최근 분기 수익률 | 유효 자산 수 | HHI | Top-3 집중도 |
| 2D | 액티브 셰어 | 추적 오차 (TE) | 정보 비율 (IR) | 포트 누적 수익 | 벤치마크 누적 수익 |
| ND | HHI | 유효 자산 수 | Top-3 집중도 | 누적 수익률 | 최대 리스크 기여 자산 |

### Activity

| Dimension | KPI 1 | KPI 2 | KPI 3 | KPI 4 | KPI 5 |
|-----------|-------|-------|-------|-------|-------|
| 1D | VWAP 대비 단가 | 손익비 | 매매 빈도 | 총 수수료 | 승률 |
| 2D | 스위칭 기회비용 | 스위칭 비율 | 교차 거래 간격 | 수수료 비용 | 순수익 |
| ND | 포트폴리오 회전율 | 연간 수수료 합계 | 평균 보유 기간 | 실현 손익 | 미실현 손익 |

---

## 4-13. Stock vs Portfolio 자동 분기 규칙

classify_result["dashboard"] 값에 따라 대시보드를 분기한다.

### 분기 로직

**1단계: Class 기반 1차 분기**

| Class | 1차 분기 |
|-------|----------|
| TimeSeries | Stock 후보 |
| Activity | Stock 확정 |
| Static | Portfolio 확정 |

**2단계: 컬럼 구조 기반 최종 확정 (TimeSeries만 적용)**

| 조건 | 최종 분기 |
|------|-----------|
| TimeSeries + weight / benchmark 컬럼 있음 | Portfolio |
| TimeSeries + weight / benchmark 컬럼 없음 | Stock |

**혼합 클래스 우선순위**
```
Static > Activity > TimeSeries
```

### Stock vs Portfolio 구성 차이

| 항목 | Stock | Portfolio |
|------|-------|-----------|
| Hero 마지막 블록 | Hedge 제안 | 리밸런싱 제안 |
| Hero Total Return | 개별 종목 수익률 | 포트폴리오 전체 수익률 |
| 우측 배너 이벤트 | 크로스 / RSI / Z-score | 비중 이탈 / HHI 초과 |
| LLM 입력 태그 | [추세 파악] [이상값 감지] | [구성 파악] [항목 비교] |
| 엔진 뷰 벡터 강조 | Date / OHLCV 감지 | Weight / Asset / 기여도 감지 |

**규칙**
- 분기 결과는 탑바나 메인 화면에 노출하지 않는다
- 분기 결과는 엔진 뷰 파이프라인 섹션에서만 확인 가능
- classify_result["dashboard"] 값은 "stock" 또는 "portfolio" 두 가지만 존재
