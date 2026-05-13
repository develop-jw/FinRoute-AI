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
        [(h - l).abs(), (h - pc).abs(), (l - pc).abs()],
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
        "best_quarter",   # 추가
        "worst_quarter",  # 추가
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
    ct  = classify_result["class_type"]
    dim = classify_result["dimension"]

    # ── TimeSeries 1D ─────────────────────────────────────────────────────────
    if ct == "TimeSeries" and dim == "1D":
        date_c  = _find_col(df, "date", "datetime", "time")
        close_c = _find_col(df, "close", "adj_close", "price")
        high_c  = _find_col(df, "high")
        low_c   = _find_col(df, "low")
        if close_c is None:
            return out
        work  = df.sort_values(date_c).copy() if date_c else df.copy()
        close = pd.to_numeric(work[close_c], errors="coerce")

        out["RSI"]    = _rsi(close)
        out["MDD"]    = _mdd(close)
        out["Sharpe"] = _sharpe(close.pct_change())
        if high_c and low_c:
            h = pd.to_numeric(work[high_c], errors="coerce")
            l = pd.to_numeric(work[low_c],  errors="coerce")
            out["ATR"] = _atr(h, l, close)
        ma20 = close.rolling(20, min_periods=5).mean()
        ma60 = close.rolling(60, min_periods=5).mean()
        m20  = float(ma20.iloc[-1]) if len(ma20) else float("nan")
        m60  = float(ma60.iloc[-1]) if len(ma60) else float("nan")
        out["MA20"] = m20 if np.isfinite(m20) else None
        out["MA60"] = m60 if np.isfinite(m60) else None
        if np.isfinite(m20) and np.isfinite(m60):
            out["trend"] = "golden" if m20 >= m60 else "dead"
        cr = float(close.iloc[-1] / close.iloc[0] - 1.0) if len(close) > 1 else 0.0
        out["cum_return"] = cr if np.isfinite(cr) else None

    # ── TimeSeries 2D ─────────────────────────────────────────────────────────
    elif ct == "TimeSeries" and dim == "2D":
        ticker_c = _find_col(df, "ticker", "symbol", "code")
        date_c   = _find_col(df, "date", "datetime", "time")
        close_c  = _find_col(df, "close", "adj_close", "price")
        if not (ticker_c and close_c):
            return out

        tickers = df[ticker_c].dropna().unique()
        if len(tickers) < 2:
            return out

        t1, t2 = tickers[0], tickers[1]

        def _get_close(ticker):
            sub = df[df[ticker_c] == ticker]
            if date_c:
                sub = sub.sort_values(date_c)
            return pd.to_numeric(sub[close_c], errors="coerce").reset_index(drop=True)

        c1, c2  = _get_close(t1), _get_close(t2)
        min_len = min(len(c1), len(c2))
        c1, c2  = c1.iloc[:min_len], c2.iloc[:min_len]

        cr = float(c1.iloc[-1] / c1.iloc[0] - 1.0) if len(c1) > 1 else 0.0
        out["cum_return"] = cr if np.isfinite(cr) else None

        window = min(60, min_len)
        r1     = c1.pct_change().dropna()
        r2     = c2.pct_change().dropna()
        min_r  = min(len(r1), len(r2))
        r1, r2 = r1.iloc[:min_r], r2.iloc[:min_r]

        if min_r >= 5:
            roll_corr = float(r1.rolling(window, min_periods=5).corr(r2).iloc[-1])
            out["roll_corr"] = roll_corr if np.isfinite(roll_corr) else None

            x, y   = r2.values, r1.values
            xm, ym = x.mean(), y.mean()
            beta   = float(np.dot(x - xm, y - ym) / (np.dot(x - xm, x - xm) + 1e-12))
            out["beta"] = beta if np.isfinite(beta) else None

        if out["beta"] is not None:
            spread = c1 - out["beta"] * c2
            s_mean = spread.rolling(window, min_periods=5).mean().iloc[-1]
            s_std  = spread.rolling(window, min_periods=5).std().iloc[-1]
            if s_std and s_std > 0:
                zscore = float((spread.iloc[-1] - s_mean) / s_std)
                out["zscore"] = zscore if np.isfinite(zscore) else None
            sp = spread.dropna()
            if len(sp) > 10:
                lagged  = sp.shift(1).dropna()
                sp_trim = sp.iloc[1:]
                # 길이 맞추기
                min_sp  = min(len(lagged), len(sp_trim))
                lagged  = lagged.iloc[:min_sp]
                sp_trim = sp_trim.iloc[:min_sp]
                gamma   = float(
                    np.dot(lagged - lagged.mean(), sp_trim - sp_trim.mean()) /
                    (np.dot(lagged - lagged.mean(), lagged - lagged.mean()) + 1e-12)
                )
                if 0 < gamma < 1:
                    out["halflife"] = float(-np.log(2) / np.log(gamma))

        if out["zscore"] is not None:
            adf_stat       = abs(out["zscore"])
            out["coint_p"] = float(max(0.001, min(0.999, 1.0 / (1.0 + adf_stat))))

    # ── TimeSeries ND ─────────────────────────────────────────────────────────
    elif ct == "TimeSeries" and dim == "ND":
        ticker_c = _find_col(df, "ticker", "symbol", "code")
        date_c   = _find_col(df, "date", "datetime", "time")
        close_c  = _find_col(df, "close", "adj_close", "price")
        if not (ticker_c and close_c):
            return out

        tickers = df[ticker_c].dropna().unique()
        if len(tickers) < 3:
            return out

        ret_dict = {}
        for t in tickers:
            sub = df[df[ticker_c] == t]
            if date_c:
                sub = sub.sort_values(date_c)
            c = pd.to_numeric(sub[close_c], errors="coerce").reset_index(drop=True)
            ret_dict[t] = c.pct_change().dropna().reset_index(drop=True)

        ret_df = pd.DataFrame(ret_dict).dropna()
        if len(ret_df) < 10:
            return out

        corr_mat = ret_df.corr()
        n        = len(tickers)
        upper    = corr_mat.values[np.triu_indices(n, k=1)]
        avg_corr = float(np.mean(upper))
        out["avg_corr"] = avg_corr if np.isfinite(avg_corr) else None

        # 최대 상관 쌍 (대각선 제외)
        mask = np.ones(corr_mat.shape, dtype=bool)
        np.fill_diagonal(mask, False)
        max_idx = np.unravel_index(
            np.where(mask, corr_mat.values, -np.inf).argmax(), corr_mat.shape
        )
        out["max_corr_pair"] = f"{corr_mat.index[max_idx[0]]}-{corr_mat.columns[max_idx[1]]}"

        # PCA 1st PC 기여율 (numpy만 사용)
        try:
            cov     = np.cov(ret_df.values.T)
            eigvals = np.linalg.eigvalsh(cov)[::-1]
            out["pca_first"] = float(eigvals[0] / eigvals.sum()) if eigvals.sum() > 0 else None
        except Exception:
            out["pca_first"] = None

        # VaR 95% (동일비중)
        port_ret   = ret_df.mean(axis=1)
        out["VaR"] = float(np.percentile(port_ret, 5))

        # 누적 수익률 (동일비중)
        cr = float((1 + port_ret).prod() - 1.0)
        out["cum_return"] = cr if np.isfinite(cr) else None

        # 네트워크 중심성 (상관 > 0.5 엣지 수 기반)
        threshold  = 0.5
        centrality = {}
        for t in tickers:
            cnt = sum(
                1 for other in tickers
                if other != t and abs(corr_mat.loc[t, other]) > threshold
            )
            centrality[str(t)] = cnt / max(1, n - 1)
        out["centrality"] = centrality

    # ── Static 1D ─────────────────────────────────────────────────────────────
    elif ct == "Static" and dim == "1D":
        q_c = _find_col(df, "quarter", "date", "period")
        w   = _find_col(df, "weight", "weights")
        r   = _find_col(df, "return", "returns")
        if not (w and r):
            return out

        wv = pd.to_numeric(df[w], errors="coerce")
        rv = pd.to_numeric(df[r], errors="coerce")

        # 분기별 가중 수익률 → cumprod로 누적 수익 계산
        if q_c:
            port_rets   = []
            quarter_map = {}
            for _q, part in df.groupby(q_c, sort=True):
                wv_q = pd.to_numeric(part[w], errors="coerce").fillna(0)
                rv_q = pd.to_numeric(part[r], errors="coerce").fillna(0)
                pr_q = float((wv_q * rv_q).sum())
                port_rets.append(pr_q)
                quarter_map[str(_q)] = pr_q
            pr_s = pd.Series(port_rets, dtype=float)
            cum  = float((1 + pr_s).prod() - 1.0)
            out["cum_return"]    = cum if np.isfinite(cum) else None
            out["recent_return"] = float(pr_s.iloc[-1]) if len(pr_s) else None
            if quarter_map:
                out["best_quarter"]  = max(quarter_map, key=lambda k: quarter_map[k])
                out["worst_quarter"] = min(quarter_map, key=lambda k: quarter_map[k])
        else:
            pr = float((wv * rv).sum())
            out["cum_return"]    = pr if np.isfinite(pr) else None
            out["recent_return"] = pr if np.isfinite(pr) else None

        wsum = wv.clip(lower=0).sum()
        if wsum > 0:
            wn = wv.clip(lower=0) / wsum
            hhi = float((wn**2).sum() * 10000)
            out["HHI"]       = hhi if np.isfinite(hhi) else None
            out["eff_n"]     = float(1.0 / (wn**2).sum()) if (wn**2).sum() > 0 else None
            out["top3_conc"] = float(wn.nlargest(3).sum())

    # ── Static 2D ─────────────────────────────────────────────────────────────
    elif ct == "Static" and dim == "2D":
        q_c      = _find_col(df, "quarter", "date", "period")
        w        = _find_col(df, "weight")
        tw       = next(
            (c for c in df.columns if c.lower() in ("benchmark_weight", "target_weight", "bm_weight")),
            None
        )
        r        = _find_col(df, "return", "returns")
        ticker_c = _find_col(df, "ticker", "symbol", "code", "asset_name", "asset")

        if not (w and r):
            return out

        # target_weight 없으면 두 종목을 각각 포트/벤치로 비교
        if not tw and ticker_c:
            tickers = df[ticker_c].dropna().unique()
            if len(tickers) >= 2:
                t1, t2 = tickers[0], tickers[1]
                r1 = pd.to_numeric(df[df[ticker_c] == t1][r], errors="coerce").reset_index(drop=True)
                r2 = pd.to_numeric(df[df[ticker_c] == t2][r], errors="coerce").reset_index(drop=True)
                out["cum_return"] = float((1 + r1).prod() - 1)
                out["bm_return"]  = float((1 + r2).prod() - 1)
                min_len = min(len(r1), len(r2))
                if min_len >= 2:
                    out["roll_corr"]    = float(r1.iloc[:min_len].corr(r2.iloc[:min_len]))
                    excess              = r1.iloc[:min_len] - r2.iloc[:min_len]
                    out["tracking_err"] = float(excess.std(ddof=1) * np.sqrt(4)) if len(excess) > 1 else None
                    ir_mu = float(excess.mean())
                    ir_sd = float(excess.std(ddof=1))
                    out["info_ratio"]   = float(ir_mu / ir_sd * np.sqrt(4)) if ir_sd and ir_sd > 0 else None
            return out

        # target_weight 있는 경우: 포트 vs 벤치마크
        port_rets: list[float] = []
        bm_rets:   list[float] = []
        iter_parts = df.groupby(q_c, sort=True) if q_c else [(0, df)]
        for _key, part in iter_parts:
            wv = pd.to_numeric(part[w],  errors="coerce").fillna(0)
            rv = pd.to_numeric(part[r],  errors="coerce").fillna(0)
            pr = float((wv * rv).sum())
            port_rets.append(pr)
            if tw and tw in part.columns:
                tv = pd.to_numeric(part[tw], errors="coerce").fillna(0)
                bm_rets.append(float((tv * rv).sum()))
            else:
                bm_rets.append(pr)

        pr_s   = pd.Series(port_rets, dtype=float)
        bm_s   = pd.Series(bm_rets,   dtype=float)
        excess = pr_s - bm_s
        out["cum_return"] = float((1 + pr_s).prod() - 1.0) if len(pr_s) else None
        out["bm_return"]  = float((1 + bm_s).prod() - 1.0) if len(bm_s) else None

        if len(pr_s) >= 2 and tw:
            aw  = []
            grp = df.groupby(q_c, sort=True) if q_c else [(0, df)]
            for _key, part in grp:
                wv = pd.to_numeric(part[w],  errors="coerce").fillna(0)
                tv = pd.to_numeric(part[tw], errors="coerce").fillna(0) if tw in part.columns else wv * 0
                aw.append(0.5 * float((wv - tv).abs().sum()))
            out["active_share"] = float(np.mean(aw)) if aw else None
            te = float(excess.std(ddof=1) * np.sqrt(4)) if len(excess) > 1 else None
            out["tracking_err"] = te
            ir_mu = float(excess.mean())
            ir_sd = float(excess.std(ddof=1))
            out["info_ratio"]   = float(ir_mu / ir_sd * np.sqrt(4)) if ir_sd and ir_sd > 0 else None

    # ── Static ND ─────────────────────────────────────────────────────────────
    elif ct == "Static" and dim == "ND":
        w     = _find_col(df, "weight")
        r     = _find_col(df, "return", "returns")
        asset = _find_col(df, "asset_name", "asset", "ticker", "name")
        if not (w and r and asset):
            return out

        q_c  = _find_col(df, "quarter", "date")
        last = df.sort_values(q_c or df.columns[0]).groupby(asset, as_index=False).last()

        wv   = pd.to_numeric(last[w], errors="coerce").clip(lower=0)
        rv   = pd.to_numeric(last[r], errors="coerce")
        wsum = wv.sum()

        if wsum > 0:
            wn = wv / wsum
            hhi = float((wn**2).sum() * 10000)
            out["HHI"]       = hhi
            out["eff_n"]     = float(1.0 / (wn**2).sum())
            out["top3_conc"] = float(wn.nlargest(3).sum())

        # 리스크 기여도
        cov = np.cov(rv.values, rowvar=False) if len(rv) > 1 else np.array([[0.0001]])
        rc  = wv.values * (cov @ wv.values) if cov.size > 1 else (wv.values * rv.values).astype(float)
        s   = float(np.sum(np.abs(rc))) or 1.0
        rc_d = {str(last[asset].iloc[i]): float(rc[i] / s) for i in range(len(last))}
        out["risk_contrib"]   = rc_d
        out["max_risk_asset"] = max(rc_d, key=lambda k: rc_d[k])

        # 누적 수익률: 분기별 cumprod
        if q_c and q_c in df.columns:
            port_rets = []
            for _q, part in df.groupby(q_c, sort=True):
                wv_q   = pd.to_numeric(part[w], errors="coerce").fillna(0)
                rv_q   = pd.to_numeric(part[r], errors="coerce").fillna(0)
                wsum_q = wv_q.sum()
                if wsum_q > 0:
                    port_rets.append(float(((wv_q / wsum_q) * rv_q).sum()))
            if port_rets:
                pr_s = pd.Series(port_rets, dtype=float)
                cum  = float((1 + pr_s).prod() - 1.0)
                out["cum_return"] = cum if np.isfinite(cum) else None
            else:
                out["cum_return"] = float((wv * rv).sum()) if len(wv) else None
        else:
            out["cum_return"] = float((wv * rv).sum()) if len(wv) else None

    # ── Activity 1D ───────────────────────────────────────────────────────────
    elif ct == "Activity" and dim == "1D":
        price_c = _find_col(df, "price", "close", "trade_price", "execution_price")
        qty_c   = _find_col(df, "quantity", "qty", "volume", "amount")
        fee_c   = _find_col(df, "fee", "commission", "cost")
        side_c  = _find_col(df, "side", "type", "buy_sell", "direction")
        vwap_c  = _find_col(df, "vwap")
        if price_c is None:
            return out

        price = pd.to_numeric(df[price_c], errors="coerce")
        qty   = pd.to_numeric(df[qty_c],   errors="coerce") if qty_c else pd.Series([1] * len(df))
        fee   = pd.to_numeric(df[fee_c],   errors="coerce").fillna(0) if fee_c else pd.Series([0] * len(df))

        out["total_fee"]  = float(fee.sum())
        out["trade_freq"] = float(len(df))

        if vwap_c:
            vwap = pd.to_numeric(df[vwap_c], errors="coerce")
            dev  = float((price - vwap).mean())
            out["vwap_dev"] = dev if np.isfinite(dev) else None
        elif qty_c:
            denom = qty.sum()
            if denom > 0:
                out["vwap_dev"] = float(price.mean() - float((price * qty).sum() / denom))

        if side_c:
            sides       = df[side_c].astype(str).str.upper()
            buy_mask    = sides.str.contains("BUY|매수|B", regex=True)
            sell_mask   = sides.str.contains("SELL|매도|S", regex=True)
            buy_prices  = price[buy_mask]
            sell_prices = price[sell_mask]
            if len(buy_prices) > 0 and len(sell_prices) > 0:
                avg_buy  = float(buy_prices.mean())
                wins     = sell_prices[sell_prices > avg_buy]
                losses   = sell_prices[sell_prices < avg_buy]
                out["win_rate"]      = float(len(wins) / len(sell_prices))
                avg_win  = float((wins   - avg_buy).mean()) if len(wins)   > 0 else 0.0
                avg_loss = float((avg_buy - losses).mean()) if len(losses) > 0 else 1e-9
                out["profit_factor"] = float(avg_win / avg_loss) if avg_loss > 0 else None

    # ── Activity 2D ───────────────────────────────────────────────────────────
    elif ct == "Activity" and dim == "2D":
        ticker_c = _find_col(df, "ticker", "symbol", "code")
        date_c   = _find_col(df, "date", "datetime", "time")
        price_c  = _find_col(df, "price", "close", "trade_price")
        qty_c    = _find_col(df, "quantity", "qty", "volume")
        fee_c    = _find_col(df, "fee", "commission", "cost")
        side_c   = _find_col(df, "side", "type", "buy_sell")
        if not (ticker_c and price_c):
            return out

        price = pd.to_numeric(df[price_c], errors="coerce")
        qty   = pd.to_numeric(df[qty_c],   errors="coerce") if qty_c else pd.Series([1] * len(df))
        fee   = pd.to_numeric(df[fee_c],   errors="coerce").fillna(0) if fee_c else pd.Series([0] * len(df))

        out["fee_cost"] = float(fee.sum())

        # reset_index로 연속 정수 인덱스 보장
        df_s          = df.sort_values(date_c).reset_index(drop=True) if date_c else df.reset_index(drop=True)
        ticker_series = df_s[ticker_c].astype(str)

        # 첫 행 제외하고 ticker 변경 횟수 계산
        switched     = ticker_series != ticker_series.shift(1)
        switches     = int(switched.iloc[1:].sum())
        out["switch_ratio"] = float(switches / max(1, len(df_s) - 1))

        # 스위칭 시점 인덱스로 수수료 합산
        switch_positions   = switched.iloc[1:][switched.iloc[1:]].index.tolist()
        out["switch_cost"] = float(fee.iloc[switch_positions].sum())

        if date_c:
            dates = pd.to_datetime(df_s[date_c], errors="coerce").dropna()
            if len(dates) > 1:
                out["cross_interval"] = float(dates.diff().dropna().dt.days.mean())

        if side_c:
            sides    = df[side_c].astype(str).str.upper()
            sell_val = float((price * qty)[sides.str.contains("SELL|매도|S", regex=True)].sum())
            buy_val  = float((price * qty)[sides.str.contains("BUY|매수|B",  regex=True)].sum())
            out["net_profit"] = float(sell_val - buy_val - fee.sum())

    # ── Activity ND ───────────────────────────────────────────────────────────
    elif ct == "Activity" and dim == "ND":
        ticker_c = _find_col(df, "ticker", "symbol", "code")
        date_c   = _find_col(df, "date", "datetime", "time")
        price_c  = _find_col(df, "price", "close", "trade_price")
        qty_c    = _find_col(df, "quantity", "qty", "volume")
        fee_c    = _find_col(df, "fee", "commission", "cost")
        side_c   = _find_col(df, "side", "type", "buy_sell")
        if not (ticker_c and price_c):
            return out

        price = pd.to_numeric(df[price_c], errors="coerce")
        qty   = pd.to_numeric(df[qty_c],   errors="coerce") if qty_c else pd.Series([1] * len(df))
        fee   = pd.to_numeric(df[fee_c],   errors="coerce").fillna(0) if fee_c else pd.Series([0] * len(df))

        out["annual_fee"] = float(fee.sum())

        trade_value  = float((price * qty).sum())
        n_tickers    = int(df[ticker_c].nunique())
        avg_position = trade_value / max(1, n_tickers)
        out["turnover_rate"] = float(trade_value / avg_position) if avg_position > 0 else None

        if date_c and side_c:
            df_s  = df.sort_values(date_c)
            sides = df_s[side_c].astype(str).str.upper()
            buy_dates  = pd.to_datetime(
                df_s.loc[sides.str.contains("BUY|매수|B",  regex=True), date_c], errors="coerce"
            ).dropna()
            sell_dates = pd.to_datetime(
                df_s.loc[sides.str.contains("SELL|매도|S", regex=True), date_c], errors="coerce"
            ).dropna()
            if len(buy_dates) > 0 and len(sell_dates) > 0:
                n        = min(len(buy_dates), len(sell_dates))
                hold     = pd.to_timedelta(sell_dates.values[:n] - buy_dates.values[:n]).days
                avg_hold = float(pd.Series(hold).mean())
                out["avg_hold"] = avg_hold if np.isfinite(avg_hold) else None

        if side_c:
            sides    = df[side_c].astype(str).str.upper()
            sell_val = float((price * qty)[sides.str.contains("SELL|매도|S", regex=True)].sum())
            buy_val  = float((price * qty)[sides.str.contains("BUY|매수|B",  regex=True)].sum())
            out["realized_pnl"]   = float(sell_val - buy_val - fee.sum())
            out["unrealized_pnl"] = float(buy_val - sell_val) if sell_val < buy_val else 0.0

    return out
