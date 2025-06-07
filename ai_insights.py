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
