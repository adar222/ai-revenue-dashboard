import streamlit as st
import pandas as pd

def show_ivt_margin_alert(df):
    # Helper for flexible column lookup
    def safe_col(df, name):
        for c in df.columns:
            if c.strip().lower() == name.strip().lower():
                return c
        return None

    package_col = safe_col(df, "Package")
    ivt_col = safe_col(df, "IVT (%)")
    margin_col = safe_col(df, "Margin (%)")
    rpm_col = safe_col(df, "RPM")

    # Use only the latest day
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'])
        latest_day = df['Date'].max()
        sub = df[df['Date'] == latest_day]
    else:
        sub = df

    # Alert: IVT > 10% OR Margin < 20%
    alert_df = sub[(sub[ivt_col] > 10) | (sub[margin_col] < 20)].copy()

    # Formatting
    alert_df[ivt_col] = alert_df[ivt_col].round(1)
    alert_df[margin_col] = alert_df[margin_col].round(1)
    alert_df[rpm_col] = alert_df[rpm_col].round(3)

    alert_df = alert_df.rename(columns={
        package_col: "Package",
        rpm_col: "RPM",
        ivt_col: "IVT (%)",
        margin_col: "Margin (%)"
    })

    st.markdown(
        "<h5 style='margin-bottom:8px;'> <span style='font-size:1.2em;'>🦠</span> <b>IVT & Margin Alert (Last Day)</b> </h5>",
        unsafe_allow_html=True
    )
    st.dataframe(
        alert_df[["Package", "RPM", "IVT (%)", "Margin (%)"]],
        use_container_width=True,
        hide_index=True
    )

def show_revenue_drop_table(df):
    def safe_col(df, name):
        for c in df.columns:
            if c.strip().lower() == name.strip().lower():
                return c
        return None

    package_col = safe_col(df, "Package")
    date_col = safe_col(df, "Date")
    gross_col = safe_col(df, "Gross Revenue")

    df[date_col] = pd.to_datetime(df[date_col])
    last_dates = sorted(df[date_col].unique())[-2:]
    if len(last_dates) < 2:
        st.warning("Not enough data for revenue drop alert.")
        return

    last_day, prev_day = last_dates[-1], last_dates[-2]

    last_rev = df[df[date_col] == last_day].groupby(package_col)[gross_col].sum()
    prev_rev = df[df[date_col] == prev_day].groupby(package_col)[gross_col].sum()

    result = pd.DataFrame({
        "Last Day Rev": last_rev,
        "Prev Day Rev": prev_rev,
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

    st.markdown(
        "<h5 style='margin-bottom:8px;'> <span style='font-size:1.2em;'>📉</span> <b>Revenue Drop Alert (Rev > $50, >20%)</b> </h5>",
        unsafe_allow_html=True
    )
    st.dataframe(
        alert_df[["Package", "Last Day Rev", "Prev Day Rev", "Δ", "% Drop"]],
        use_container_width=True,
        hide_index=True
    )
