"""01_standard: 클래스·차원·대시보드 분류 및 18D 벡터 + 코사인 유사도."""

from __future__ import annotations

import re
from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

# 18D 순서: OHLCV(6) | 활동(5) | 자산구조(4) | 성과·계획(3)
_REF_TIMESERIES = np.array(
    [[1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], dtype=float
)
_REF_STATIC = np.array(
    [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0]], dtype=float
)
_REF_ACTIVITY = np.array(
    [[0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0]], dtype=float
)


def _norm_cols(df: pd.DataFrame) -> dict[str, str]:
    """lower_snake 매핑: 원본명 -> normalized token."""
    out: dict[str, str] = {}
    for c in df.columns:
        key = re.sub(r"[^a-z0-9]+", "_", str(c).strip().lower()).strip("_")
        out[c] = key
    return out


def _has_token(tokens: set[str], *needles: str) -> bool:
    return any(n in tokens for n in needles)


def _extract_vector(df: pd.DataFrame, rev: dict[str, str]) -> list[int]:
    """18D 이진 벡터 [가격6|활동5|구조4|성과3]."""
    tokens = set(rev.values())

    def col_match(*patterns: str) -> bool:
        for p in patterns:
            for t in tokens:
                if p in t:
                    return True
        return False

    v = [0] * 18
    # 가격 시계열
    v[0] = 1 if col_match("date", "time", "quarter") else 0
    v[1] = 1 if col_match("open") else 0
    v[2] = 1 if col_match("high") else 0
    v[3] = 1 if col_match("low") else 0
    v[4] = 1 if col_match("close", "price") and not col_match("target") else 0
    v[5] = 1 if col_match("volume", "vol") else 0
    # 거래 활동
    v[6] = 1 if col_match("timestamp") else 0
    v[7] = 1 if col_match("buy", "sell", "side") else 0
    v[8] = 0
    for c in df.columns:
        t = rev[c]
        if "holding" in t:
            continue
        if "quantity" in t or t == "qty" or (t.endswith("_qty")):
            v[8] = 1
            break
    v[9] = 1 if col_match("price") else 0
    v[10] = 1 if col_match("fee", "commission") else 0
    # 자산 구조
    v[11] = 1 if col_match("asset", "ticker", "symbol", "name") else 0
    v[12] = 1 if col_match("holding") else 0
    v[13] = 1 if col_match("weight") else 0
    v[14] = 1 if col_match("current_val", "value", "nav") else 0
    # 성과·계획
    v[15] = 1 if col_match("contribution", "contrib") else 0
    v[16] = 1 if col_match("target") else 0
    v[17] = 1 if col_match("return", "expected", "forecast") else 0
    return v


def _infer_goals(
    class_type: str, dimension: str, vector: list[int], tokens: set[str]
) -> list[str]:
    goals: list[str] = []
    if class_type == "TimeSeries":
        goals.append("goal_trend")
        if dimension == "1D":
            goals.append("goal_anomaly")
        if dimension in ("2D", "ND"):
            goals.extend(["goal_corr", "goal_spread"])
    elif class_type == "Static":
        goals.extend(["goal_comp", "goal_compare", "goal_dist"])
        if "hhi" in tokens or dimension == "ND":
            goals.append("goal_relation")
    else:
        goals.extend(["goal_anomaly", "goal_compare"])
    # 중복 제거, 순서 유지
    seen: set[str] = set()
    out: list[str] = []
    for g in goals:
        if g not in seen:
            seen.add(g)
            out.append(g)
    return out


def classify(df: pd.DataFrame) -> dict[str, Any]:
    if df is None or df.empty:
        raise ValueError("빈 데이터프레임은 분류할 수 없습니다.")

    rev = _norm_cols(df)
    tokens = set(rev.values())
    vec = _extract_vector(df, rev)
    v_arr = np.array([vec], dtype=float)

    sim_ts = float(cosine_similarity(v_arr, _REF_TIMESERIES)[0][0])
    sim_st = float(cosine_similarity(v_arr, _REF_STATIC)[0][0])
    sim_ac = float(cosine_similarity(v_arr, _REF_ACTIVITY)[0][0])
    similarity = {"TimeSeries": sim_ts, "Static": sim_st, "Activity": sim_ac}

    has_ts = _has_token(
        tokens, "date", "datetime", "quarter", "time"
    ) and _has_token(tokens, "close", "price", "adj_close")
    has_static = _has_token(tokens, "weight") and _has_token(
        tokens, "holding_amount", "holding", "holdingamt"
    )
    has_activity = (
        _has_token(tokens, "buy", "sell", "side")
        and _has_token(tokens, "fee", "commission")
        and _has_token(tokens, "quantity", "qty")
    )

    # 혼합 시 우선순위: Static > Activity > TimeSeries (01_standard)
    if has_static:
        class_type = "Static"
    elif has_activity:
        class_type = "Activity"
    elif has_ts:
        class_type = "TimeSeries"
    else:
        # 폴백: 유사도 최대 클래스
        class_type = max(similarity, key=lambda k: similarity[k])

    dimension = "1D"
    dashboard = "stock"

    if class_type == "TimeSeries":
        tick_col = None
        for c, t in rev.items():
            if t in ("ticker", "symbol", "code", "asset", "asset_name"):
                tick_col = c
                break
        n_tick = int(df[tick_col].nunique()) if tick_col and tick_col in df.columns else 1
        if n_tick >= 3:
            dimension = "ND"
        elif n_tick == 2:
            dimension = "2D"
        else:
            dimension = "1D"
        if _has_token(tokens, "weight") or _has_token(tokens, "benchmark"):
            dashboard = "portfolio"
        else:
            dashboard = "stock"

    elif class_type == "Static":
        dashboard = "portfolio"
        # 자산(Ticker) 개수 기반 차원 분류
        tick_col = None
        for c, t in rev.items():
            if t in ("ticker", "symbol", "code", "asset", "asset_name"):
                tick_col = c
                break
        n_tick = int(df[tick_col].nunique()) if tick_col and tick_col in df.columns else 1
        
        if n_tick >= 3:
            dimension = "ND"
        elif n_tick == 2:
            dimension = "2D"
        else:
            dimension = "1D"

    else:  # Activity
        dashboard = "stock"
        tick_col = None
        for c, t in rev.items():
            if t in ("ticker", "symbol"):
                tick_col = c
                break
        n_tick = int(df[tick_col].nunique()) if tick_col and tick_col in df.columns else 1
        if n_tick >= 3:
            dimension = "ND"
        elif n_tick == 2:
            dimension = "2D"
        else:
            dimension = "1D"

    goals = _infer_goals(class_type, dimension, vec, tokens)

    return {
        "class_type": class_type,
        "dimension": dimension,
        "dashboard": dashboard,
        "vector": vec,
        "similarity": similarity,
        "goals": goals,
    }
