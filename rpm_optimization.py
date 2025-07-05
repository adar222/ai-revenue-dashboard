import streamlit as st
import pandas as pd
import numpy as np

def show_rpm_optimization():
    st.markdown("## ⚡ RPM Optimization")
    
    # Load the main DataFrame from session state
    df = st.session_state.get("main_df")
    if df is None:
        st.warning("Please upload your Excel file in the AI Insights tab.")
        return

    # Filter inputs
    rpm_threshold = st.number_input("Show products with RPM below:", min_value=0.0, value=0.05, step=0.01)
    req_ne_threshold = st.number_input("Show products with Requests NE higher than:", min_value=0, value=10000000, step=1000000)
    
    # Check for required columns
    columns_needed = ['Campaign ID', 'RPM', 'Request NE', 'Gross Revenue', 'Revenue Cost']
    for col in columns_needed:
        if col not in df.columns:
            st.error(f"Column '{col}' not found in your data!")
            return

    # Filter data
    filtered_df = df[(df['RPM'] < rpm_threshold) & (df['Request NE'] > req_ne_threshold)].copy()
    
    # Calculate Serving Cost and Net Revenue after serving costs
    filtered_df['Serving Costs'] = np.round(filtered_df['Request NE'] / 1_000_000_000 * 200)
    filtered_df['Net Revenue After Serving Costs'] = (
        filtered_df['Gross Revenue'] - filtered_df['Revenue Cost'] - filtered_df['Serving Costs']
    )
    
    # Profit/Loss status
    filtered_df['Profit/Loss Status'] = np.where(
        filtered_df['Net Revenue After Serving Costs'] < 0, '🚩 Losing money', '👍 Profitable'
    )
    
    # Format numbers
    filtered_df['Request NE'] = filtered_df['Request NE'].apply(lambda x: f"{int(x):,}")
    filtered_df['Gross Revenue'] = filtered_df['Gross Revenue'].apply(lambda x: f"${int(np.round(x)):,}")
    filtered_df['Serving Costs'] = filtered_df['Serving Costs'].apply(lambda x: f"${int(np.round(x)):,}")
    filtered_df['Net Revenue After Serving Costs'] = filtered_df['Net Revenue After Serving Costs'].apply(lambda x: f"${int(np.round(x)):,}")
    filtered_df['RPM'] = filtered_df['RPM'].apply(lambda x: f"{x:.4f}")

    # Columns to display
    display_cols = [
        'Profit/Loss Status', 'Campaign ID', 'RPM', 'Request NE', 'Gross Revenue',
        'Serving Costs', 'Net Revenue After Serving Costs'
    ]
    
    # Add checkboxes for bulk actions
    filtered_df['Check to Block'] = ""
    
    st.dataframe(filtered_df[display_cols + ['Check to Block']], use_container_width=True)
    
    st.button("Download to Excel")
    st.button("Block all checked boxes in bulk")

    st.markdown("---")
    st.markdown(
        "*AI-driven summary & recommendations coming soon. This tool prioritizes cost efficiency, highlights low-RPM, high-volume products, and flags those at risk of losses due to serving costs. Use the filters above to find the most urgent optimization targets.*"
    )

# You would call show_rpm_optimization() in your main app logic
