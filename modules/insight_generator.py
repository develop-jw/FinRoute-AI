"""05_insight: 인사이트 생성 (Claude API 또는 규칙 기반 폴백)."""

from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv

load_dotenv()


def _heuristic(
    classify_result: dict, indicator_result: dict
) -> dict[str, Any]:
    ct = classify_result["class_type"]
    dim = classify_result["dimension"]
    dash = classify_result["dashboard"]

    signal = "HOLD"
    confidence = 55
    regime = "RISK-ON"

    if ct == "TimeSeries" and dim == "1D":
        rsi = indicator_result.get("RSI")
        trend = indicator_result.get("trend")
        mdd = indicator_result.get("MDD")
        if trend == "golden":
            signal = "BUY"
            confidence = 68
        elif trend == "dead":
            signal = "REDUCE"
            confidence = 62
        if rsi is not None:
            if rsi > 70:
                signal = "HOLD" if signal == "BUY" else "REDUCE"
                confidence = min(confidence + 10, 90)
            elif rsi < 30:
                signal = "BUY" if signal != "REDUCE" else "HOLD"
        if mdd is not None and mdd < -0.15:
            regime = "RISK-OFF"
            confidence = max(confidence - 5, 35)

    elif ct == "Static":
        regime = "RISK-OFF" if (indicator_result.get("HHI") or 0) > 2500 else "RISK-ON"
        te = indicator_result.get("tracking_err")
        if te is not None and te > 0.05:
            signal = "REDUCE"
            confidence = 60
        else:
            signal = "HOLD"
            confidence = 58

    parts: list[str] = []
    if ct == "TimeSeries" and dim == "1D":
        if indicator_result.get("trend"):
            parts.append(
                f"[추세 파악] MA20 vs MA60 — {indicator_result['trend']} 구간"
            )
        if indicator_result.get("RSI") is not None:
            parts.append(f"[이상값 감지] RSI {indicator_result['RSI']:.1f}")
        if indicator_result.get("MDD") is not None:
            parts.append(f"MDD {indicator_result['MDD']*100:.1f}%")
    elif ct == "Static":
        parts.append("[구성 파악] 자산 비중·기여도 기준 스냅샷")
        if indicator_result.get("active_share") is not None:
            parts.append(
                f"[항목 비교] 액티브 셰어 {indicator_result['active_share']*100:.1f}%"
            )
        if indicator_result.get("top3_conc") is not None:
            parts.append(f"Top-3 집중 {indicator_result['top3_conc']*100:.1f}%")

    llm_input = " · ".join(parts) if parts else f"{ct} {dim} 요약"

    if dash == "portfolio":
        action = "목표 비중 대비 괴리를 점검하고 분기 리밸런싱 일정을 유지합니다."
        why = (
            "[항목 비교] 추적 오차·정보 비율을 바탕으로 포트와 벤치마크의 괴리를 평가합니다."
        )
        rebal = "비중 이탈이 크지 않다면 현 구조를 유지하고 현금 트렌치만 조정합니다."
        hedge = "주식 베타 헤지는 인덱스 풋 또는 채권 비중 확대로 검토합니다."
    else:
        action = "손절선(ATR×2)을 유지하며 시그널을 재확인합니다."
        why = (
            "[추세 파악] "
            + (
                f"추세 {indicator_result.get('trend', 'n/a')}, RSI 근처 변동성 확인"
            )
        )
        rebal = "단일 종목 비중이 과도할 때만 부분 매도로 조정합니다."
        hedge = "인버스 ETF 또는 풋옵션으로 하방 변동성을 헤지합니다."

    return {
        "signal": signal,
        "confidence": int(max(0, min(100, confidence))),
        "regime": regime,
        "action": action,
        "why_now": why,
        "rebalancing": rebal,
        "hedge": hedge,
        "llm_input": llm_input,
    }


def _anthropic_generate(
    classify_result: dict, indicator_result: dict, llm_input: str
) -> dict[str, Any] | None:
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        return None
    try:
        import anthropic

        client = anthropic.Anthropic(api_key=key)
        sys = (
            "당신은 15년 경력의 퀀트 애널리스트입니다. 한국어로 간결하게 답합니다. "
            "Why now는 반드시 [태그]로 시작합니다."
        )
        user = (
            f"classify: {classify_result}\nmetrics: {indicator_result}\n"
            f"요약입력: {llm_input}\n"
            "JSON만 출력: signal(BUY|HOLD|REDUCE), confidence(0-100 int), "
            "regime(RISK-ON|RISK-OFF), action, why_now, rebalancing, hedge"
        )
        msg = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=512,
            system=sys,
            messages=[{"role": "user", "content": user}],
        )
        text = ""
        for b in msg.content:
            if hasattr(b, "text"):
                text += b.text
        import json
        import re

        m = re.search(r"\{[\s\S]*\}", text)
        if not m:
            return None
        d = json.loads(m.group())
        return {
            "signal": d.get("signal", "HOLD"),
            "confidence": int(d.get("confidence", 60)),
            "regime": d.get("regime", "RISK-ON"),
            "action": d.get("action", ""),
            "why_now": d.get("why_now", ""),
            "rebalancing": d.get("rebalancing", ""),
            "hedge": d.get("hedge", ""),
            "llm_input": llm_input,
        }
    except Exception:
        return None


def generate(classify_result: dict, indicator_result: dict) -> dict[str, Any]:
    base = _heuristic(classify_result, indicator_result)
    llm = _anthropic_generate(classify_result, indicator_result, base["llm_input"])
    if llm:
        return llm
    return base
