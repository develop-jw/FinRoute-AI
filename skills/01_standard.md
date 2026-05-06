# 01_Standard.md - 투자 데이터 분석 기준 및 라우팅 정의

### 1-1. 클래스(Class) 및 대시보드 라우팅 분기
입력된 데이터의 구조를 분석하여 클래스를 판별하고, 대시보드 라우팅(`dashboard`) 유형을 확정한다.

| 판별 클래스 | 조건 및 핵심 컬럼 | 최종 라우팅 (Dashboard) |
|---|---|---|
| **TimeSeries** | Date/Datetime + Close/Price 컬럼 존재 | **Stock** (기본) <br> 단, `weight` 또는 `benchmark` 컬럼 포함 시 **Portfolio** |
| **Static** | Weight + Holding Amount 컬럼 존재 | **Portfolio** (확정) |
| **Activity** | Buy/Sell + Fee + Quantity 컬럼 존재 | **Stock** (확정) |

### 1-2. 차원(Dimension) 결정 기준
| 클래스 | 판별 기준 | 1D | 2D | ND |
|---|---|---|---|---|
| **TimeSeries** | ticker 고유값 개수 | 1개 (단일 종목) | 2개 (두 종목 비교) | 3개 이상 (다종목) |
| **Activity** | ticker 고유값 개수 | 1개 (단일 종목) | 2개 (두 종목 비교) | 3개 이상 (다종목) |
| **Static** | 분석 목적별 컬럼 존재 여부 | 벤치마크/HHI 없음 | 벤치마크 컬럼 존재 | HHI 컬럼 존재 |

### 1-3. 혼합 클래스 데이터 처리 규칙 (Mixed-Class Handling)

하나의 입력 데이터셋 안에 2개 이상의 서로 다른 클래스(TimeSeries, Static, Activity) 데이터가 혼재할 경우, 데이터 간의 복잡한 연관성 추론을 배제하고 **무조건 각 클래스를 독립적인 1D 분석으로 강제 분리하여 처리**한다.
