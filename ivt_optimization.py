import streamlit as st
import pandas as pd
import numpy as np

def show_ivt_optimization(df=None):
    st.header("🚩 IVT Optimization")

    # This tab must always get the df from session_state, unless directly provided
    if df is None:
        df = st.session_state.get('main_df')
    if df is None:
        st.info("Please upload your Excel file in the AI Insights tab.")
        return

    # Select the days for filter
    days_options = [1, 3, 7, 'All']
    days_selected = st.selectbox("Show data for last...", days_options, index=2)
    if days_selected != 'All':
        most_recent = pd.to_datetime(df['Date']).max()
        date_filter = most_recent - pd.Timedelta(days=int(days_selected) - 1)
        df = df[pd.to_datetime(df['Date']) >= date_filter]

    # Filter by IVT threshold
    default_ivt = 10
    ivt_threshold = st.number_input("IVT Threshold (%)", min_value=0, max_value=100, value=default_ivt, step=1)
    df_filtered = df[df['IVT (%)'] >= ivt_threshold].copy()

    # Select columns to show
    show_cols = [
        'Date', 'Product', 'Package', 'Channel', 'Campaign', 'IVT (%)', 'RPM', 'Impressions', 'Revenue'
    ]
    # Only show columns present in data
    show_cols = [c for c in show_cols if c in df_filtered.columns]
    df_display = df_filtered[show_cols].sort_values(by='IVT (%)', ascending=False)

    # Conditional formatting
    def highlight_row(row):
        styles = [''] * len(row)
        try:
            if row['IVT (%)'] > 15:
                styles[row.index.get_loc('IVT (%)')] = 'background-color: #ffcccc; font-weight:bold'  # Red
            if 'RPM' in row and row['RPM'] < 0.01:
                styles[row.index.get_loc('RPM')] = 'background-color: #ffedcc; font-weight:bold'  # Orange
        except Exception:
            pass
        return styles

    # --- AI Recommendations Panel (rule-based demo)
    recs = []
    if len(df_display) > 0:
        for _, row in df_display.iterrows():
            if row['IVT (%)'] > 15:
                recs.append(
                    f"🚩 Product {row['Product']} (Pkg: {row['Package']}) in Campaign '{row['Campaign']}' has IVT {row['IVT (%)']:.1f}%. Recommend block at campaign level."
                )
    if recs:
        st.info("**AI Recommendations:**\n\n" + "\n".join(recs))
    else:
        st.success("No high IVT issues detected above your selected threshold!")

    # --- Table (sortable, scrollable, 5 rows at a time)
    st.markdown("#### Results")
    st.caption("Table below shows all rows with IVT ≥ threshold, by selected date range. Sort columns by clicking their header.")

    if len(df_display) > 0:
        styled = df_display.head(50).style.apply(highlight_row, axis=1)
        st.dataframe(styled, use_container_width=True, height=250, hide_index=True)
    else:
        st.write("No data to display.")

    # --- Bulk Block Button
    st.button("Block in Bulk")
    st.caption("Clicking 'Block in Bulk' will block the selected products on the campaign level in the platform.")
