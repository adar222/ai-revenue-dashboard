import streamlit as st
import pandas as pd

def show_action_center_top10(df):
    date_col = [c for c in df.columns if c.strip().lower() == "date"][0]
    package_col = [c for c in df.columns if c.strip().lower() == "package"][0]
    gross_col = [c for c in df.columns if c.strip().lower() == "gross revenue"][0]
    action_col = [c for c in df.columns if c.strip().lower() in ["status", "action"]]
    action_col = action_col[0] if action_col else None

    df[date_col] = pd.to_datetime(df[date_col])
    unique_dates = sorted(df[date_col].unique())
    if len(unique_dates) < 6:
        st.info("Not enough date data for Action Center (need at least 6 days)")
        return

    last3 = unique_dates[-3:]
    prev3 = unique_dates[-6:-3]

    last3_str = f"{pd.to_datetime(last3[0]).strftime('%d/%m')}-{pd.to_datetime(last3[-1]).strftime('%d/%m')}"
    prev3_str = f"{pd.to_datetime(prev3[0]).strftime('%d/%m')}-{pd.to_datetime(prev3[-1]).strftime('%d/%m')}"

    last_by_pkg = df[df[date_col].isin(last3)].groupby(package_col)[gross_col].sum()
    prev_by_pkg = df[df[date_col].isin(prev3)].groupby(package_col)[gross_col].sum()

    result = pd.DataFrame({
        f"Last 3d Revenue ({last3_str})": last_by_pkg,
        f"Prev 3d Revenue ({prev3_str})": prev_by_pkg,
    }).fillna(0)

    # Whole numbers with $ formatting
    for col in result.columns:
        result[col] = result[col].round(0)

    result["Δ"] = result[result.columns[0]] - result[result.columns[1]]

    # Show +/- in Δ
    def fmt_delta(val):
        if val > 0:
            return f"+${int(val):,}"
        elif val < 0:
            return f"-${abs(int(val)):,}"
        else:
            return "$0"
    result["Δ"] = result["Δ"].apply(fmt_delta)

    # % Change with +/- and N/A if denominator is zero
    def pct_change(row):
        prev = row[result.columns[1]]
        last = row[result.columns[0]]
        if prev == 0:
            return "N/A"
        pct = (last - prev) / prev * 100
        if pct > 0:
            return f"+{pct:.0f}%"
        elif pct < 0:
            return f"{pct:.0f}%"
        else:
            return "0%"
    result["% Change"] = result.apply(pct_change, axis=1)

    # Action/status with icons
    icon_map = {
        "Safe": "🟢 Safe",
        "Critical": "🔴 Critical",
        "Needs Review": "🟡 Needs Review",
        "Investigate": "🟡 Investigate",
        "Stable": "🟢 Stable"
    }
    if action_col:
        actions = df[df[date_col].isin(last3)].groupby(package_col)[action_col].first()
        result["Action"] = actions.map(lambda x: icon_map.get(str(x), str(x)))
    else:
        result["Action"] = ""

    # Show top 10 by latest revenue
    result = result.sort_values(result.columns[0], ascending=False).head(10)
    result = result.reset_index().rename(columns={package_col: "Package"})

    st.markdown(
        f"""<h5 style="margin-bottom:8px;"> <span style="font-size:1.2em;">🚨</span> <b>Action Center: Top 10 Trending Packages (3d vs Prev 3d)</b> </h5>""",
        unsafe_allow_html=True,
    )
    st.dataframe(result, use_container_width=True, hide_index=True)
