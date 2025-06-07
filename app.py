import streamlit as st
import pandas as pd
from ai_insights import show_ivt_margin_alert, show_revenue_drop_table

st.set_page_config(page_title="AI Revenue Action Center", layout="wide")
st.title("📈 AI-Powered Revenue Action Center")

uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Simple filters for Advertiser, Channel, Ad Format (optional)
    def safe_col(df, name):
        for c in df.columns:
            if c.strip().lower() == name.strip().lower():
                return c
        return None

    advertisers_col = safe_col(df, 'Advertiser')
    channels_col = safe_col(df, 'Channel')
    formats_col = safe_col(df, 'Ad format')

    # Prepare filter options
    if advertisers_col:
        advertisers = ["(All)"] + sorted(df[advertisers_col].dropna().unique().astype(str).tolist())
    else:
        advertisers = ["(All)"]
    if channels_col:
        channels = ["(All)"] + sorted(df[channels_col].dropna().unique().astype(str).tolist())
    else:
        channels = ["(All)"]
    if formats_col:
        formats = ["(All)"] + sorted(df[formats_col].dropna().unique().astype(str).tolist())
    else:
        formats = ["(All)"]

    # Show filters
    col1, col2, col3 = st.columns(3)
    with col1:
        advertiser = st.selectbox("Advertiser", options=advertisers, index=0)
    with col2:
        channel = st.selectbox("Channel", options=channels, index=0)
    with col3:
        ad_format = st.selectbox("Ad Format", options=formats, index=0)

    # Apply filters
    filtered = df.copy()
    if advertiser != "(All)" and advertisers_col:
        filtered = filtered[filtered[advertisers_col] == advertiser]
    if channel != "(All)" and channels_col:
        filtered = filtered[filtered[channels_col] == channel]
    if ad_format != "(All)" and formats_col:
        filtered = filtered[filtered[formats_col] == ad_format]

    st.markdown("---")

    # Show Alert Tables
    show_ivt_margin_alert(filtered)
    show_revenue_drop_table(filtered)

    st.markdown("---")

    st.info("For more advanced AI or insights, please contact your data team.")
else:
    st.info("Please upload your Excel file to get started.")
