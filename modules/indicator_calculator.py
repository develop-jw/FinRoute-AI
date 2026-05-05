"""02_indicator: class_type × dimension별 KPI 계산."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


def _rsi(close: pd.Series, period: int = 14) -> float:
    d = close.astype(float)
    delta = d.diff()
    gain = delta.clip(lower=0.0)
    loss = (-delta.clip(upper=0.0))
    avg_g = gain.ewm(alpha=1 / period, adjust=False).mean()
    avg_l = loss.ewm(alpha=1 / period, adjust=False).mean()
    rs = avg_g / avg_l.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    v = float(rsi.iloc[-1])
    return v if np.isfinite(v) else float("nan")


def _atr(h: pd.Series, l: pd.Series, c: pd.Series, period: int = 14) -> float:
    pc = c.shift(1)
    tr = pd.concat(
        [
            (h - l).abs(),
            (h - pc).abs(),
            (l - pc).abs(),
        ],
        axis=1,
    ).max(axis=1)
    v = float(tr.ewm(alpha=1 / period, adjust=False).mean().iloc[-1])
    return v if np.isfinite(v) else float("nan")


def _mdd(close: pd.Series) -> float:
    d = close.astype(float)
    roll_max = d.cummax()
    dd = d / roll_max - 1.0
    v = float(dd.min())
    return v if np.isfinite(v) else float("nan")


def _sharpe(daily_ret: pd.Series, periods: int = 252) -> float:
    r = daily_ret.dropna()
    if len(r) < 5:
        return float("nan")
    mu = float(r.mean())
    sig = float(r.std())
    if sig == 0 or not np.isfinite(sig):
        return float("nan")
    return (mu / sig) * np.sqrt(periods)


def _none_template() -> dict[str, Any]:
    keys = [
        "cum_return",
        "RSI",
        "MDD",
        "Sharpe",
        "ATR",
        "MA20",
        "MA60",
        "trend",
        "coint_p",
        "zscore",
        "roll_corr",
        "beta",
        "halflife",
        "avg_corr",
        "pca_first",
        "VaR",
        "centrality",
        "max_corr_pair",
        "recent_return",
        "eff_n",
        "HHI",
        "top3_conc",
        "active_share",
        "tracking_err",
        "info_ratio",
        "bm_return",
        "risk_contrib",
        "max_risk_asset",
        "vwap_dev",
        "profit_factor",
        "trade_freq",
        "total_fee",
        "win_rate",
        "switch_cost",
        "switch_ratio",
        "cross_interval",
        "fee_cost",
        "net_profit",
        "turnover_rate",
        "annual_fee",
        "avg_hold",
        "realized_pnl",
        "unrealized_pnl",
    ]
    return {k: None for k in keys}


def _find_col(df: pd.DataFrame, *candidates: str) -> str | None:
    lower = {c.lower().replace(" ", "_"): c for c in df.columns}
    for cand in candidates:
        k = cand.lower()
        if k in lower:
            return lower[k]
        for lk, orig in lower.items():
            if k in lk or lk in k:
                return orig
    return None


def calculate(df: pd.DataFrame, classify_result: dict) -> dict[str, Any]:
    out = _none_template()
    ct = classify_result["class_type"]
    dim = classify_result["dimension"]

    if ct == "TimeSeries" and dim == "1D":
        date_c = _find_col(df, "date", "datetime", "time")
        close_c = _find_col(df, "close", "adj_close", "price")
        high_c = _find_col(df, "high")
        low_c = _find_col(df, "low")
        if close_c is None:
            return out
        work = df
        if date_c:
            work = df.sort_values(date_c).copy()
        close = pd.to_numeric(work[close_c], errors="coerce")

        out["RSI"] = _rsi(close)
        out["MDD"] = _mdd(close)
        dr = close.pct_change()
        out["Sharpe"] = _sharpe(dr)
        if high_c and low_c:
            h = pd.to_numeric(work[high_c], errors="coerce")
            l = pd.to_numeric(work[low_c], errors="coerce")
            out["ATR"] = _atr(h, l, close)
        ma20 = close.rolling(20, min_periods=5).mean()
        ma60 = close.rolling(60, min_periods=5).mean()
        m20 = float(ma20.iloc[-1]) if len(ma20) else float("nan")
        m60 = float(ma60.iloc[-1]) if len(ma60) else float("nan")
        out["MA20"] = m20 if np.isfinite(m20) else None
        out["MA60"] = m60 if np.isfinite(m60) else None
        if np.isfinite(m20) and np.isfinite(m60):
            out["trend"] = "golden" if m20 >= m60 else "dead"
        cr = float(close.iloc[-1] / close.iloc[0] - 1.0) if len(close) > 1 else 0.0
        out["cum_return"] = cr if np.isfinite(cr) else None

    elif ct == "TimeSeries" and dim == "2D":
        # 샘플 없음: 플레이스홀더
        out["cum_return"] = None

    elif ct == "TimeSeries" and dim == "ND":
        out["cum_return"] = None

    elif ct == "Static" and dim == "1D":
        w = _find_col(df, "weight", "weights")
        r = _find_col(df, "return", "returns")
        if w and r:
            wv = pd.to_numeric(df[w], errors="coerce")
            rv = pd.to_numeric(df[r], errors="coerce")
            pr = float((wv * rv).sum())
            out["recent_return"] = pr if np.isfinite(pr) else None
            wsum = wv.clip(lower=0).sum()
            if wsum > 0:
                wn = wv.clip(lower=0) / wsum
                hhi = float((wn**2).sum() * 10000)
                out["HHI"] = hhi if np.isfinite(hhi) else None
                eff = float(1.0 / (wn**2).sum()) if (wn**2).sum() > 0 else None
                out["eff_n"] = eff
                top3 = float(wn.nlargest(3).sum())
                out["top3_conc"] = top3
            out["cum_return"] = out.get("recent_return")

    elif ct == "Static" and dim == "2D":
        q = _find_col(df, "quarter", "date", "period")
        w = _find_col(df, "weight")
        tw = _find_col(df, "target_weight", "benchmark_weight")
        r = _find_col(df, "return", "returns")
        if not (w and r):
            return out
        port_rets: list[float] = []
        bm_rets: list[float] = []
        iter_parts = (
            df.groupby(q, sort=True) if q else [(0, df)]
        )
        for _key, part in iter_parts:
            wv = pd.to_numeric(part[w], errors="coerce").fillna(0)
            rv = pd.to_numeric(part[r], errors="coerce").fillna(0)
            pr = float((wv * rv).sum())
            port_rets.append(pr)
            if tw and tw in part.columns:
                tv = pd.to_numeric(part[tw], errors="coerce").fillna(0)
                br = float((tv * rv).sum())
                bm_rets.append(br)
            else:
                bm_rets.append(pr)
        pr_s = pd.Series(port_rets, dtype=float)
        bm_s = pd.Series(bm_rets, dtype=float)
        excess = pr_s - bm_s
        out["cum_return"] = float((1 + pr_s).prod() - 1.0) if len(pr_s) else None
        out["bm_return"] = float((1 + bm_s).prod() - 1.0) if len(bm_s) else None
        if len(pr_s) >= 2 and tw:
            aw = []
            grp = df.groupby(q, sort=True) if q else [(0, df)]
            for _key, part in grp:
                wv = pd.to_numeric(part[w], errors="coerce").fillna(0)
                tv = (
                    pd.to_numeric(part[tw], errors="coerce").fillna(0)
                    if tw in part.columns
                    else wv * 0
                )
                aw.append(0.5 * float((wv - tv).abs().sum()))
            out["active_share"] = float(np.mean(aw)) if aw else None
            te = float(excess.std(ddof=1) * np.sqrt(4)) if len(excess) > 1 else None
            out["tracking_err"] = te
            ir_mu = float(excess.mean())
            ir_sd = float(excess.std(ddof=1))
            out["info_ratio"] = (
                (ir_mu / ir_sd) * np.sqrt(4) if ir_sd and ir_sd > 0 else None
            )

    elif ct == "Static" and dim == "ND":
        w = _find_col(df, "weight")
        r = _find_col(df, "return", "returns")
        asset = _find_col(df, "asset_name", "asset", "ticker", "name")
        if w and r and asset:
            last = df.sort_values(
                _find_col(df, "quarter", "date") or df.columns[0]
            ).groupby(asset, as_index=False).last()
            wv = pd.to_numeric(last[w], errors="coerce").clip(lower=0)
            rv = pd.to_numeric(last[r], errors="coerce")
            wsum = wv.sum()
            if wsum > 0:
                wn = wv / wsum
                hhi = float((wn**2).sum() * 10000)
                out["HHI"] = hhi
                eff = float(1.0 / (wn**2).sum())
                out["eff_n"] = eff
                out["top3_conc"] = float(wn.nlargest(3).sum())
            cov = np.cov(rv.values, rowvar=False) if len(rv) > 1 else np.array([[0.0001]])
            if cov.size == 1:
                rc = (wv.values * rv.values).astype(float)
            else:
                rc = wv.values * (cov @ wv.values)
            s = float(np.sum(np.abs(rc))) or 1.0
            rc_d = {str(last[asset].iloc[i]): float(rc[i] / s) for i in range(len(last))}
            out["risk_contrib"] = rc_d
            mx = max(rc_d, key=lambda k: rc_d[k])
            out["max_risk_asset"] = mx
            out["cum_return"] = float((wv * rv).sum()) if len(wv) else None

    elif ct == "Activity":
        # 샘플 없음
        out["cum_return"] = None

    return out
