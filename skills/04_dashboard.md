# 04_dashboard.md — 대시보드 구성 규칙

> dashboard_builder.py 구현 규칙을 정의한다.
> chart_selector.py(Section 3) 결과를 받아 화면을 어디에, 어떤 순서로, 어떻게 렌더링할지를 담당한다.

---

## 4-1. 전체 레이아웃 구조

```
┌──────────────────────────────────────────────────────┐
│                     탑바 (Topbar)                     │
├──────────┬──────────────────────────────┬─────────────┤
│  좌측    │        중앙 메인 영역         │  우측 배너  │
│  배너    │       (스크롤 가능)           │  (고정)     │
│  (72px)  │                              │  (260px)    │
└──────────┴──────────────────────────────┴─────────────┘
```

| 영역 | 역할 | 고정 여부 |
|------|------|-----------|
| 탑바 | 로고 + 차원 탭 (1D / 2D / ND) | sticky |
| 좌측 배너 | 화면 전환 아이콘 + CSV 업로드 | sticky |
| 중앙 메인 | Hero → KPI → 차트 → Action Console | 스크롤 |
| 우측 배너 | 자동감지 이벤트 + 분석 목적 추론 + 계산 지표 | sticky |

---

## 4-2. 중앙 메인 레이어 배치 순서

아래 순서를 반드시 준수한다.

```
1. Hero Decision Layer
2. KPI 카드 행
3. 메인 차트
4. 서브 차트 (존재할 경우)
5. Action Console
```

**금지 사항**
- 파이프라인 정보(클래스 분류, 벡터값)를 중앙 메인 상단에 노출하지 않는다
- Action Console을 차트보다 위에 배치하지 않는다
- 분석 엔진 근거는 반드시 엔진 뷰(⚙️)에만 배치한다

---

## 4-3. 탑바 구성 규칙

**포함 요소**
```
[FinRoute AI 로고]  |  [차원 탭: 1D / 2D / ND]
```

**규칙**
- 로고 클릭 시 메인 화면으로 복귀
- 차원 탭은 classify_result["dimension"] 값을 기본 선택 상태로 초기화
- 탑바에 시그널(HOLD/BUY/REDUCE) 배지를 표시하지 않는다 
- 엔진 뷰 활성화 시 차원 탭 비활성화 (opacity: 0.4, pointer-events: none)

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
┌──────────┬──────────────┬─────────────┬──────────────────┬──────────┐
│  Live    │    Total     │    Risk     │    Suggested     │  Hedge / │
│  Signal  │    Return    │    Regime   │     Action       │ 리밸런싱 │
└──────────┴──────────────┴─────────────┴──────────────────┴──────────┘
```

| 블록 | 표시 내용 | 데이터 출처 |
|------|-----------|-------------|
| Live Signal | BUY / HOLD / REDUCE + 신뢰도 바 | insight_result["signal"], ["confidence"] |
| Total Return | 기간 누적 수익률 | indicator_result["cum_return"] |
| Risk Regime | RISK-ON / RISK-OFF | insight_result["regime"] |
| Suggested Action | 한 줄 행동 지침 | insight_result["action"] |
| Hedge / 리밸런싱 | 헤지 또는 리밸런싱 제안 | insight_result["hedge"] |

**규칙**
- Hero 배경색 #2c4a32 (짙은 녹색) 고정
- Live Signal 블록 하단에 신뢰도 바(progress bar) 필수 포함
- dashboard가 "stock"이면 마지막 블록 → "Hedge"
- dashboard가 "portfolio"이면 마지막 블록 → "리밸런싱"

---

## 4-6. KPI 카드 행 구성 규칙

- 항상 5개 카드, 가로 1열(st.columns(5))로 배치
- 각 카드 구성: 지표명 / 계산값 / 부연 설명 / 상태 배지
- 상태 배지 색상
  - 양호 → 초록
  - 주의 → 주황
  - 위험 → 빨강
  - 중립 → 회색
- KPI 카드 hover 시 위로 튀어오르는 애니메이션 적용

---

## 4-7. 우측 배너 구성 규칙

**3개 섹션 고정 구성 (위 → 아래 순서)**

```
① 자동 감지 이벤트
② 분석 목적 추론
③ 계산 지표
```

**① 자동 감지 이벤트**
- 현재 차원 기준 감지 이벤트를 최신순으로 표시
- 이벤트 유형별 색상 구분
  - 매수 시그널 → 초록
  - 매도 시그널 → 빨강
  - 경고 → 주황
- 차원 탭 전환 시 해당 차원의 이벤트로 즉시 업데이트
- hover 시 오른쪽 이동 애니메이션 적용

**② 분석 목적 추론**
- classify_result["goals"] 결과를 ON/OFF 칩 형태로 표시
- 각 항목에 추론 조건식 함께 표시
- 차원 전환 시 해당 차원의 추론 결과로 업데이트

**③ 계산 지표**
- 현재 차원에 해당하는 핵심 지표 표시 (4-11 참조)
- 지표명 / 계산값 / 상태색 3요소로 구성
- 차트 내 수치와 동일한 값 사용

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

**전환 조건**
- ⚙️ 클릭 → 엔진 뷰 전환, 차원 탭 비활성화
- 🏠 클릭 → 메인 대시보드 복귀, 차원 탭 활성화

**포함 섹션 (위 → 아래 순서)**
```
① 전체 분석 파이프라인
   18D 벡터 추출 → 클래스 분류 → 차원 판별 → 시각화 출력
   현재 판별 결과를 각 단계 아래에 표시

② 클래스 분류 결과 (코사인 유사도)
   - 시계열 / 스냅샷 / 매매활동 유사도를 카드 형태로 표시
   - 1위 클래스 강조
   - classify_result["similarity"] 값 사용

③ 18D 특성 벡터
   - 4개 그룹으로 분류 표시
     · 가격 시계열: Date / Open / High / Low / Close / Volume
     · 거래 활동: Timestamp / Buy·Sell / Quantity / Price / Fee
     · 자산 구조: Asset Name / Holding Amt / Weight / Current Val
     · 성과·계획: 기여도 / 목표값 / 예상치
   - classify_result["vector"] 값으로 감지 여부(0/1) 표시

④ 분석 목적 자동 추론
   - classify_result["goals"] 결과를 ON/OFF 카드로 크게 표시
   - 추론 조건식과 목적 설명 포함
   - insight_result["llm_input"] 연결 지점 명시
```

**규칙**
- 엔진 뷰는 현재 선택된 차원 기준으로 표시
- 우측 배너는 엔진 뷰에서도 동일하게 유지

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
- 이벤트는 날짜 역순 정렬 (최신 → 상단)
- 차원 전환 시 해당 차원의 이벤트만 표시
- 이벤트 없을 시 "현재 감지된 이벤트 없음" 표시
- 이벤트 발생 날짜는 메인 차트 위에 마커로 동시 표시

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