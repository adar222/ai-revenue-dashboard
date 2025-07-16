import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

def show_pubimps():
    st.title("Impression Discrepancy Checker")

    uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.success("File uploaded successfully.")
        
        # Ensure numeric types
        df['Publisher Impressions'] = pd.to_numeric(df['Publisher Impressions'], errors='coerce')
        df['Advertiser Impressions'] = pd.to_numeric(df['Advertiser Impressions'], errors='coerce')
        
        # Avoid division by zero
        df = df[df['Advertiser Impressions'] > 0]
        
        # Calculate discrepancy: 1 - (PubImp / AdvImp)
        df['Discrepancy'] = 1 - (df['Publisher Impressions'] / df['Advertiser Impressions'])
        
        # Show graph FIRST (before any filtering)
        st.subheader("Discrepancy Distribution (Full dataset)")
        
        # Create histogram bins every 5%
        bins = np.arange(-1, 1.05, 0.05)
        df['Discrepancy Bin'] = pd.cut(df['Discrepancy'], bins=bins)
        
        bin_counts = df['Discrepancy Bin'].value_counts().sort_index()
        bin_labels = [f"{round(interval.left*100)}% to {round(interval.right*100)}%" for interval in bin_counts.index]
        
        hist_df = pd.DataFrame({
            "Discrepancy Range": bin_labels,
            "Count": bin_counts.values
        })
        
        fig = px.bar(
            hist_df,
            x="Discrepancy Range",
            y="Count",
            labels={'Count': 'Row count', 'Discrepancy Range': 'Discrepancy range'},
            title="Distribution of Impression Discrepancies"
        )
        fig.update_layout(xaxis_tickangle=-45)
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Then show filtering toggles + flagged rows
        st.subheader("Flagged rows")
        show_under = st.checkbox("Show Under-delivery (>10%)", value=True)
        show_over = st.checkbox("Show Over-delivery (<-10%)", value=True)
        
        flagged_df = pd.DataFrame()
        
        if show_under and show_over:
            flagged_df = df[(df['Discrepancy'] > 0.10) | (df['Discrepancy'] < -0.10)]
        elif show_under:
            flagged_df = df[df['Discrepancy'] > 0.10]
        elif show_over:
            flagged_df = df[df['Discrepancy'] < -0.10]
        
        st.dataframe(flagged_df)
        
        # Download button
        if not flagged_df.empty:
            csv = flagged_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download flagged rows as CSV",
                data=csv,
                file_name='flagged_discrepancies.csv',
                mime='text/csv',
            )
    else:
        st.info("Awaiting file upload.")
