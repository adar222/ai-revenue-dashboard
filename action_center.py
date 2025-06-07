import streamlit as st
import pandas as pd
import numpy as np

def safe_col(df, name):
    for c in df.columns:
        if c.strip().lower() == name.strip().lower():
            return c
    return None

def show_action_center_top10(df):
    package_col = safe_col(df, "Package")
    date_col = safe_col(df, "Date")
    gross_col = safe_col(df, "Gross Revenue")
    fill_col = safe_col(df, "FillRate")

    if date_col is None or package_col is None or gross_col is None or fill_col is None:
        st.warning("Missing columns for Top 10 Trending table.")
        return

    df[date_col] = pd.to_datetime(df[date_col])
    all_dates = sorted(df[date_col].unique())
    if len(all_dates) < 6:
        st.info("Not enough days for 3d vs 3d trending.")
        return

    last3 = all_dates[-3:]
    prev3 = all_dates[-6:-3]
    last_period_str = f"{last3[0].strftime('%d/%m')}-{last3[-1].strftime('%d/%m')}"
    prev_period_str = f"{prev3[0].strftime('%d/%m')}-{prev3[-1].strftime('%d/%m')}"

    last3_grp = df[df[date_col].isin(last3)].groupby(package_col).agg(
        {"Gross Revenue": "sum", "FillRate": "mean"}
    ).rename(columns={"Gross Revenue": "Last 3d Revenue", "FillRate": "Last 3d Fill"})
    prev3_grp = df[df[date_col].isin(prev3)].groupby(package_col).agg(
        {"Gross Revenue": "sum", "FillRate": "mean"}
    ).rename(columns={"Gross Revenue": "Prev 3d Revenue", "FillRate": "Prev 3d Fill"})

    merged = last3_grp.join(prev3_grp, how="outer").fillna(0)
    merged["Δ"] = merged["Last 3d Revenue"] - merged["Prev 3d Revenue"]
    merged["% Change"] = np.where(
        merged["Prev 3d Revenue"] == 0, np.nan, 100 * merged["Δ"] / merged["Prev 3d Revenue"]
    )
    merged = merged.reset_index()
    merged = merged.sort_values("Δ", ascending=False).head(10)

    # Format numbers
    merged["Last 3d Revenue"] = merged["Last 3d Revenue"].apply(lambda x: f"${int(round(x)):,}")
    merged["Prev 3d Revenue"] = merged["Prev 3d Revenue"].apply(lambda x: f"${int(round(x)):,}")
    merged["Δ"] = merged["Δ"].apply(lambda x: f"{'+' if x > 0 else ''}${int(round(x)):,}")
    merged["% Change"] = merged["% Change"].apply(lambda x: f"{'+' if x>0 else ''}{int(round(x))}%" if not pd.isna(x) else "N/A")

    st.markdown(
        f"<h5 style='margin-bottom:8px;'><span style='font-size:1.2em;'>📊</span> <b>Action Center: Top 10 Trending Packages (3d vs Prev 3d)</b></h5>",
        unsafe_allow_html=True
    )
    st.dataframe(
        merged[[package_col, "Last 3d Revenue", "Prev 3d Revenue", "Δ", "% Change"]],
        use_container_width=True,
        hide_index=True
    )
