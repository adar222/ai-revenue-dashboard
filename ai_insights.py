import streamlit as st
import pandas as pd

def show_revenue_drop_table(df):
    # Column name matching (flexible for your Excel headers)
    def safe_col(df, name):
        for c in df.columns:
            if c.strip().lower() == name.strip().lower():
                return c
        return None

    # Find relevant columns (adjust if yours are named differently)
    package_col = safe_col(df, "Package")
    date_col = safe_col(df, "Date")
    gross_col = safe_col(df, "Gross Revenue")
    score_col = safe_col(df, "Score")

    df[date_col] = pd.to_datetime(df[date_col])

    # Get last 2 days only
    last_dates = sorted(df[date_col].unique())[-2:]
    if len(last_dates) < 2:
        st.warning("Not enough data for revenue drop alert.")
        return

    last_day, prev_day = last_dates[-1], last_dates[-2]

    last_rev = df[df[date_col] == last_day].groupby(package_col)[gross_col].sum()
    prev_rev = df[df[date_col] == prev_day].groupby(package_col)[gross_col].sum()
    scores = df[df[date_col] == last_day].groupby(package_col)[score_col].first()

    result = pd.DataFrame({
        "Last Day Rev": last_rev,
        "Prev Day Rev": prev_rev,
        "Score": scores
    }).fillna(0)

    result["Δ"] = result["Last Day Rev"] - result["Prev Day Rev"]
    result["% Drop"] = ((result["Δ"]) / result["Prev Day Rev"] * 100).round(0)

    # Keep only: Last Day Rev > $50 and % Drop < -20%
    alert_df = result[(result["Last Day Rev"] > 50) & (result["% Drop"] < -20)]

    # Formatting
    alert_df["Last Day Rev"] = alert_df["Last Day Rev"].apply(lambda x: f"${int(round(x)):,}")
    alert_df["Prev Day Rev"] = alert_df["Prev Day Rev"].apply(lambda x: f"${int(round(x)):,}")
    alert_df["Δ"] = alert_df["Δ"].apply(lambda x: f"${int(round(x)):,}" if x < 0 else f"+${int(round(x)):,}")
    alert_df["% Drop"] = alert_df["% Drop"].apply(lambda x: f"{int(round(x))}%")
    alert_df = alert_df.reset_index()

    # Add color icon for score (score_col should be 0-100)
    def score_icon(score):
        try:
            score = float(score)
        except:
            return ""
        if score >= 80:
            return f"{int(score)} 🟢"
        elif score >= 60:
            return f"{int(score)} 🟡"
        else:
            return f"{int(score)} 🔴"
    alert_df["Score"] = alert_df["Score"].apply(score_icon)

    # Display
    st.markdown(
        "<h5 style='margin-bottom:8px;'> <span style='font-size:1.2em;'>📉</span> <b>Revenue Drop Alert (Rev > $50, >20%)</b> </h5>",
        unsafe_allow_html=True
    )
    st.dataframe(
        alert_df[["Package", "Last Day Rev", "Prev Day Rev", "Δ", "% Drop", "Score"]],
        use_container_width=True,
        hide_index=True
    )
