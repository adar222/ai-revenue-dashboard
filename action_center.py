import streamlit as st
import pandas as pd
import numpy as np

def safe_col(df, name):
    for c in df.columns:
        if c.strip().lower() == name.strip().lower():
            return c
    return None

def status_icon(delta, pct_change):
    if pd.isna(pct_change):
        return "ℹ️ N/A"
    if pct_change >= 30:
        return "🟢 Stable"
    elif pct_change >= 0:
        return "🟡 Needs Review"
    elif pct_change < 0 and pct_change > -30:
        return "🟠 Investigate"
    else:
        return "🔴 Critical"

def color_delta(val):
    if "N/A" in str(val): return val
    if "+" in str(val): return f"<span style='color:green'>{val}</span>"
    if "-" in str(val): return f"<span style='color:red'>{val}</span>"
    return val

def color_pct(val):
    if "N/A" in str(val): return val
    try:
        v = int(val.replace('%','').replace('+','').replace('-',''))
        color = "green" if "+" in val else "red"
        return f"<span style='color:{color}'>{val}</span>"
    except:
        return val

def show_action_center_top10(df):
    package_col = safe_col(df, "Package")
    date_col = safe_col(df, "Date")
    gross_col = safe_col(df, "Gross Revenue")

    if date_col is None or package_col is None or gross_col is None:
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
        {"Gross Revenue": "sum"}
    ).rename(columns={"Gross Revenue": "Last 3d Revenue"})
    prev3_grp = df[df[date_col].isin(prev3)].groupby(package_col).agg(
        {"Gross Revenue": "sum"}
    ).rename(columns={"Gross Revenue": "Prev 3d Revenue"})

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
    merged["Δ_fmt"] = merged["Δ"].apply(lambda x: f"+${int(round(x)):,}" if x >= 0 else f"-${abs(int(round(x))):,}")
    merged["% Change_fmt"] = merged["% Change"].apply(
        lambda x: f"+{int(round(x))}%" if pd.notna(x) and x > 0 else (f"{int(round(x))}%" if pd.notna(x) else "N/A")
    )
    merged["Status"] = [status_icon(d, p) for d, p in zip(merged["Δ"], merged["% Change"])]

    # Apply color formatting
    merged["Δ_fmt"] = merged["Δ_fmt"].apply(color_delta)
    merged["% Change_fmt"] = merged["% Change_fmt"].apply(color_pct)

    st.markdown(
        f"""<h5 style='margin-bottom:8px;'><span style='font-size:1.2em;'>📊</span>
        <b>Action Center: Top 10 Trending Packages<br>
        <span style='font-size:0.75em;font-weight:normal;'>(Last 3d: {last_period_str} vs Prev 3d: {prev_period_str})</span></b></h5>""",
        unsafe_allow_html=True
    )
    st.write(
        merged[[
            package_col, "Last 3d Revenue", "Prev 3d Revenue",
            "Δ_fmt", "% Change_fmt", "Status"
        ]].to_html(escape=False, index=False), unsafe_allow_html=True
    )
