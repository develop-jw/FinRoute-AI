# FinRoute-AI 🧭

**FinRoute-AI**는 금융 데이터의 복잡한 조각들을 연결하여 명확한 투자 방향(Route)을 제시하는 지능형 대시보드입니다. Streamlit 프레임워크와 Anthropic Claude LLM을 결합하여, 사용자가 업로드한 CSV 데이터를 자동으로 분류하고 최적의 분석 지표와 시각화, 그리고 실전 투자 인사이트를 제공합니다.

---
## 🏆 결과 (Results)

| | |
|---|---|
| 🔗 **대회 링크** | [Daker AI 해커톤 리더보드](https://daker.ai/public/hackathons/hackathon-investment-data-skills-dashboard?section=leaderboard) |
| 🥇 **데이콘 대회 순위** | 19위 / 321팀 참가 (상위 6%) |
| 🌐 **서비스 데모** | [FinRoute-AI 바로가기][(https://your-streamlit-link)](https://finroute-ai2-m7jiqznqtvefxffryqctbc.streamlit.app/) |

## 🌟 주요 기능 (Core Features)

### 1. 자동 데이터 분류 엔진 (Smart Classifier)
- **Vector-based Similarity**: 업로드된 CSV의 컬럼명과 구조를 분석하여 18차원 이진 벡터로 변환합니다.
- **클래스 판별**: `TimeSeries`(시계열), `Static`(자산 구성), `Activity`(매매 활동) 중 최적의 타입을 코사인 유사도로 판별합니다.
- **차원 분석**: 1D(단일), 2D(비교), ND(다중) 차원을 분석하여 최적의 대시보드 레이아웃을 결정합니다.

### 2. 고도화된 퀀트 지표 계산 (Indicator Engine)
- 데이터 타입에 따라 차별화된 KPI를 자동 계산합니다.
  - **시계열**: RSI, MDD, Sharpe Ratio, MA20/60, 공적분(Co-integration), VaR 등.
  - **포트폴리오**: HHI 지수, 유효 자산 수, 추적 오차(TE), 정보 비율(IR), 위험 기여도 등.
  - **매매 효율**: VWAP 대비 단가, 손익비(Profit Factor), 승률, 회전율 등.

### 3. 동적 대시보드 빌더 (Dynamic Visualization)
- **Plotly**를 활용한 고해상도 인터랙티브 차트를 제공합니다.
- 데이터의 성격에 맞춰 캔들스틱, 듀얼 라인, 히트맵, 도넛 차트 등을 자동으로 선택하여 배치합니다.

### 4. AI 투자 인사이트 (AI-Powered Insights)
- **Claude Sonnet** 기반의 시니어 퀀트 페르소나가 데이터를 종합 분석합니다.
- **Dots Connection**: 정량적 수치와 시장 맥락을 결합하여 `BUY / HOLD / REDUCE` 신호를 생성합니다.
- 실시간 리밸런싱 및 헤지 전략 제안을 포함합니다.


---

## 🚀 시작하기 (Getting Started)

### 1. 환경 설정
Python 3.9 이상의 환경이 필요합니다.

```bash
git clone <repository-url>
cd FinRoute-AI
pip install -r requirements.txt
```

### 2. API 키 설정
프로젝트 루트에 `.env` 파일을 생성하고 Anthropic API 키를 입력합니다. (키가 없으면 룰 기반 엔진으로 자동 전환됩니다.)

```env
# .env
ANTHROPIC_API_KEY=your_api_key_here
```

### 3. 애플리케이션 실행
```bash
streamlit run app_0.py
```

---

## 📂 프로젝트 구조

```
FinRoute-AI/
├── app_0.py                  # 메인 진입점
├── modules/                # 핵심 분석 모듈
│   ├── classifier.py       # 데이터 분류 및 벡터 분석
│   ├── indicator_calculator.py # KPI 계산
│   ├── chart_selector.py   # 시각화 전략 선택
│   ├── insight_generator.py # AI 인사이트 생성
│   └── dashboard_builder.py # UI 렌더링 및 테마
├── skills/                 # AI 분석 가이드 및 인터페이스 정의 (Prompts)
├── data/                   # 샘플 데이터 (CSV)
└── requirements.txt        # 의존성 패키지
```

---

## 🛠 기술 스택

- **Framework**: Streamlit
- **Language**: Python 3.9+
- **Data**: Pandas, NumPy, Scikit-learn
- **Viz**: Plotly
- **LLM**: Anthropic Claude (claude-3.5-sonnet / claude-4.5-sonnet)
- **Market Data**: yfinance

---

## 📜 분석 스킬 가이드 (Skills)
본 프로젝트는 `skills/` 디렉토리의 가이드라인을 엄격히 준수하여 개발되었습니다.
- `00_interface`: 전체 파이프라인 데이터 흐름 정의
- `01_standard`: 데이터 분류 표준
- `02_indicator`: 지표 계산 수식 및 임계치
- `03_visualization`: 차트 선택 규칙
- `04_dashboard`: 레이아웃 및 UX 디자인
- `05_insight`: AI 추론 및 인사이트 생성 로직
