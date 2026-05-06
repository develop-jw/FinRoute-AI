# 03_Visualization.md - Class × Dimension별 시각화 차트 선택 기준

중앙 메인 영역의 메인 차트와 서브 차트는 `classify_result["class_type"]` × `classify_result["dimension"]` 조합에 따라 자동 배치한다. 
*배치 규칙: 서브 차트가 2개인 경우 2열(`st.columns(2)`)로 분할 배치하고, 1개인 경우 전체 너비로 배치한다.*

| Class | Dimension | 메인 차트 (Explore) | 서브 차트 (Explore Sub) |
|---|---|---|---|
| **TimeSeries** | **1D** | Candlestick + MA | RSI |
| **TimeSeries** | **2D** | Dual Line (정규화) | Z-score / Rolling Correlation |
| **TimeSeries** | **ND** | Correlation Heatmap | Network Graph |
| **Static** | **1D** | Line (누적 수익률) | Grouped Bar (기여도) |
| **Static** | **2D** | Dual Line (포트 vs 벤치마크) | Bar (초과수익률) / Bar (비중 괴리율) |
| **Static** | **ND** | Donut (자산 구성) | Grouped Bar (리스크 기여도) / Stacked Area (비중 추이) |
| **Activity** | **1D** | Bar (VWAP 대비 단가) | Scatter (손익비) |
| **Activity** | **2D** | Dual Line (자산 교체 비교) | Bar (스위칭 기회비용) |
| **Activity** | **ND** | Bar (회전율) | Timeline (거래 이력) |