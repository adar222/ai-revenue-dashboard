import streamlit as st
import pandas as pd

def show_action_center_top10(df):
    # Detect relevant columns
    date_col = [c for c in df.columns if c.strip().lower() == "date"][0]
    package_col = [c for c in df.columns if c.strip().lower() == "package"][0]
    gross_col = [c for c in df.columns if c.strip().lower() == "gross revenue"][0]
    action_col = [c for c in df.columns if c.strip().lower() == "status" or c.strip().lower() == "action"]
    
    if not action_col:
        action_col = [None]
    action_col = action_col[0]

    df[date_col] = pd.to_datetime(df[date_col])
    # Get last 6 unique dates (should be sorted)
    unique_dates = sorted(df[date_col].unique())
    if len(unique_dates) < 6:
        st.info("Not enough date data for Action Center (need at least 6 days)")
        return

    # Latest 3 and previous 3
    last3 = unique_dates[-3:]
    prev3 = unique_dates[-6:-3]

    # Format dates for header
    last3_str = f"{pd.to_datetime(last3[0]).strftime('%d/%m')}-{pd.to_datetime(last3[-1]).strftime('%d/%m')}"
    prev3_str = f"{pd.to_datetime(prev3[0]).strftime('%d/%m')}-{pd.to_datetime(prev3[-1]).strftime('%d/%m')}"

    last_by_pkg = df[df[date_col].isin(last3)].groupby(package_col)[gross_col].sum()
    prev_by_pkg = df[df[date_col].isin(prev3)].groupby(package_col)[gross_col].sum()

    result = pd.DataFrame({
        f"Last 3d Revenue ({last3_str})": last_by_pkg,
        f"Prev 3d Revenue ({prev3_str})": prev_by_pkg,
    }).fillna(0)

    result["Δ"] = result[f"Last 3d Revenue ({last3_str})"] - result[f"Prev 3d Revenue ({prev3_str})"]

    def fmt_delta(val):
        if val > 0:
            return f'<span style="color:green">+${int(val):,}</span>'
        elif val < 0:
            return f'<span style="color:red">-${abs(int(val)):,}</span>'
        else:
            return f'$0'
    result["Δ"] = result["Δ"].apply(fmt_delta)

    def pct_change(row):
        prev = row[f"Prev 3d Revenue ({prev3_str})"]
        last = row[f"Last 3d Revenue ({last3_str})"]
        if prev == 0:
            return "N/A"
        pct = (last - prev) / prev * 100
        if pct > 0:
            return f'<span style="color:green">+{pct:.0f}%</span>'
        elif pct < 0:
            return f'<span style="color:red">{pct:.0f}%</span>'
        else:
            return "0%"
    result["% Change"] = result.apply(pct_change, axis=1)

    # Bring back the Action/Status column
    if action_col:
        actions = df[df[date_col].isin(last3)].groupby(package_col)[action_col].first()
        result["Action"] = actions

    # Show top 10 by absolute last 3d revenue
    result = result.sort_values(f"Last 3d Revenue ({last3_str})", ascending=False).head(10)
    result = result.reset_index().rename(columns={package_col: "Package"})

    # Display with markdown for color
    st.markdown(
        f"""<h5 style="margin-bottom:8px;"> <span style="font-size:1.2em;">🚨</span> <b>Action Center: Top 10 Trending Packages (3d vs Prev 3d)</b> </h5>""",
        unsafe_allow_html=True,
    )
    st.write("")  # Spacer

    # Display as HTML table for colored text
    st.markdown(
        result.to_html(escape=False, index=False),
        unsafe_allow_html=True
    )
