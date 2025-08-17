import json
from datetime import datetime
from pathlib import Path

import akshare as ak
import pandas as pd
import streamlit as st

DATA_FILE = Path("groups.json")


def load_groups():
    if DATA_FILE.exists():
        with DATA_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_groups(groups):
    with DATA_FILE.open("w", encoding="utf-8") as f:
        json.dump(groups, f, ensure_ascii=False, indent=2)


def normalize_symbol(symbol: str) -> str:
    symbol = symbol.strip().lower()
    if symbol.startswith("sh") or symbol.startswith("sz"):
        return symbol
    return ("sh" if symbol.startswith("6") else "sz") + symbol


def fetch_history(symbol: str, start_date: str) -> pd.DataFrame:
    start = start_date.replace("-", "")
    end = datetime.now().strftime("%Y%m%d")
    df = ak.stock_zh_a_hist(symbol=symbol, period="daily", start_date=start, end_date=end, adjust="qfq")
    df.rename(columns={"日期": "date", "收盘": "close"}, inplace=True)
    df["date"] = pd.to_datetime(df["date"])
    return df[["date", "close"]]


def calculate_metrics(symbol: str, start_date: str) -> dict:
    symbol = normalize_symbol(symbol)
    df = fetch_history(symbol, start_date)
    if df.empty:
        return {"symbol": symbol, "error": "No data"}
    start_price = df.iloc[0]["close"]
    df["yield"] = (df["close"] / start_price - 1) * 100
    current_yield = df.iloc[-1]["yield"]
    max_yield = df["yield"].max()
    max_yield_date = df.loc[df["yield"].idxmax(), "date"]
    max_yield_days = (max_yield_date - df.iloc[0]["date"]).days
    days_10 = int((df["yield"] >= 10).sum())
    days_20 = int((df["yield"] >= 20).sum())
    max_drawdown = df["yield"].min()
    return {
        "symbol": symbol,
        "current_yield": round(current_yield, 2),
        "max_yield": round(max_yield, 2),
        "max_yield_days": int(max_yield_days),
        "days_10pct": days_10,
        "days_20pct": days_20,
        "max_drawdown": round(max_drawdown, 2),
    }


def add_group_ui(groups):
    with st.sidebar.form("add_group"):
        st.header("添加分组")
        name = st.text_input("分组名称")
        start_date = st.date_input("选定日期", value=datetime.now())
        symbols_text = st.text_area("股票代码，逗号分隔")
        submitted = st.form_submit_button("保存")
        if submitted and name and symbols_text:
            symbols = [s.strip() for s in symbols_text.split(",") if s.strip()]
            groups[name] = {
                "start_date": start_date.strftime("%Y-%m-%d"),
                "symbols": symbols,
            }
            save_groups(groups)
            st.success("保存成功")


def main():
    st.title("股票分组收益分析")
    groups = load_groups()
    add_group_ui(groups)
    for group_name, info in groups.items():
        st.subheader(group_name)
        start_date = info["start_date"]
        results = [calculate_metrics(sym, start_date) for sym in info["symbols"]]
        df = pd.DataFrame(results)
        st.dataframe(df)


if __name__ == "__main__":
    main()
