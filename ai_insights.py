import streamlit as st
import pandas as pd

def show_revenue_drop_table(df):
    def safe_col(df, name):
        for c in df.columns:
            if c.strip().lower() == name.strip().lower():
                return c
        return None

    package_col = safe_col(df, "Package")
    date_col = safe_col(df, "Date")
    gross_col = safe_col(df, "Gross Revenue")
    # You can try to use score, but comment it out if you want to drop
    score_col = safe_col(df, "Score")

    df[date_col] = pd.to_datetime(df[date_col])

    last_dates = sorted(df[date_col].unique())[-2:]
    if len(last_dates) < 2:
        st.warning("Not enough data for revenue drop alert.")
        return

    last_day, prev_day = last_dates[-1], last_dates[-2]

    # Always group by only 'Package'
    last_rev = df[df[date_col] == last_day].groupby(package_col)[gross_col].sum()
    prev_rev = df[df[date_col] == prev_day].groupby(package_col)[gross_col].sum()
    # If you want to show average score, use .mean() below. Or drop the score if you want absolutely no duplicates.
    # scores = df[df[date_col] == last_day].groupby(package_col)[score_col].mean()

    result = pd.DataFrame({
        "Last Day Rev": last_rev,
        "Prev Day Rev": prev_rev,
        # "Score": scores,  # uncomment if you want average score
    }).fillna(0)

    result["Δ"] = result["Last Day Rev"] - result["Prev Day Rev"]
    result["% Drop"] = ((result["Δ"]) / result["Prev Day Rev"] * 100).round(0)

    # Only one row per package here!
    alert_df = result[(result["Last Day Rev"] > 50) & (result["% Drop"] < -20)]

    # Formatting
    alert_df["Last Day Rev"] = alert_df["Last Day Rev"].apply(lambda x: f"${int(round(x)):,}")
    alert_df["Prev Day Rev"] = alert_df["Prev Day Rev"].apply(lambda x: f"${int(round(x)):,}")
    alert_df["Δ"] = alert_df["Δ"].apply(lambda x: f"${int(round(x)):,}" if x < 0 else f"+${int(round(x)):,}")
    alert_df["% Drop"] = alert_df["% Drop"].apply(lambda x: f"{int(round(x))}%")
    alert_df = alert_df.reset_index()

    # If you want to show the score, re-add this section
    # def score_icon(score):
    #     try:
    #         score = float(score)
    #     except:
    #         return ""
    #     if score >= 80:
    #         return f"{int(score)} 🟢"
    #     elif score >= 60:
    #         return f"{int(score)} 🟡"
    #     else:
    #         return f"{int(score)} 🔴"
    # alert_df["Score"] = alert_df["Score"].apply(score_icon)

    # Show only the columns you want, here no score
    st.markdown(
        "<h5 style='margin-bottom:8px;'> <span style='font-size:1.2em;'>📉</span> <b>Revenue Drop Alert (Rev > $50, >20%)</b> </h5>",
        unsafe_allow_html=True
    )
    st.dataframe(
        alert_df[["Package", "Last Day Rev", "Prev Day Rev", "Δ", "% Drop"]],
        use_container_width=True,
        hide_index=True
    )
