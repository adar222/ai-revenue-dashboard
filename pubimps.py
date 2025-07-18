import streamlit as st

try:
    import matplotlib.pyplot as plt
except ModuleNotFoundError:
    st.error("matplotlib is not installed. Please add `matplotlib` to requirements.txt and redeploy.")
    st.stop()

import pandas as pd

def show_pubimps():
    st.header("Pubimps/Advimps Discrepancy")

    # Get your main dataframe from session_state
    df = st.session_state.get("main_df")
    if df is None or df.empty:
        st.warning("No data loaded. Please check your Excel file.")
        return

    # Define actual columns in your file
    required_cols = ['Advertiser Impressions', 'Publisher Impressions', 'Gross Revenue', 'Revenue cost']
    missing_cols = [col for col in required_cols if col not in df.columns]

    if missing_cols:
        st.warning(f"Missing columns in data: {', '.join(missing_cols)}")
        st.dataframe(df.head())  # Show a preview for debugging
        return

    # Calculate impression gap
    df['Impression Gap'] = df['Publisher Impressions'] - df['Advertiser Impressions']

    st.write("Top 10 Pubimps/Advimps discrepancies:")
    st.dataframe(
        df[['Publisher Impressions', 'Advertiser Impressions', 'Impression Gap', 'Gross Revenue', 'Revenue cost']]
        .sort_values('Impression Gap', ascending=False)
        .head(10)
    )

    # Example plot
    st.subheader("Impression Gap (Top 10)")
    fig, ax = plt.subplots(figsize=(8, 4))
    plot_df = df[['Publisher Impressions', 'Impression Gap']].sort_values('Impression Gap', ascending=False).head(10)
    ax.barh(plot_df['Publisher Impressions'].astype(str), plot_df['Impression Gap'])
    ax.set_xlabel('Impression Gap')
    ax.set_ylabel('Publisher Impressions')
    st.pyplot(fig)

    # Add more analysis below as needed!
