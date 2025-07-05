import streamlit as st
import pandas as pd

def show_rpm_optimization():
    st.markdown("## ⚡ RPM Optimization")

    # Filters
    rpm_threshold = st.number_input("Show products with RPM below:", min_value=0.0, max_value=1.0, value=0.05, step=0.01)
    req_ne_threshold = st.number_input("Show products with Requests NE higher than:", min_value=0, value=10_000_000, step=1_000_000)

    # Get data from session state
    df = st.session_state.get('main_df')
    if df is None:
        st.info("Please upload your Excel file in the AI Insights tab.")
        return

    # Make sure relevant columns exist (handle column names flexibly if needed)
    columns_needed = ['Campaign ID', 'RPM', 'Request NE', 'Gross Revenue', 'Revenue Cost']
    for col in columns_needed:
        if col not in df.columns:
            st.error(f"Column '{col}' not found in your data!")
            return

    # Calculate serving costs and net revenue
    df['Serving Costs'] = df['Request NE'] / 1_000_000_000 * 200
    df['Net Revenue After Serving Costs'] = df['Gross Revenue'] - df['Revenue Cost'] - df['Serving Costs']

    # Profit/Loss Status
    df['Profit/Loss Status'] = df['Net Revenue After Serving Costs'].apply(
        lambda x: "🚩 Losing money" if x < 0 else "👍 Profitable"
    )

    # Filter
    filtered = df[(df['RPM'] < rpm_threshold) & (df['Request NE'] > req_ne_threshold)]

    # Formatting
    filtered['Request NE'] = filtered['Request NE'].apply(lambda x: f"{int(x):,}")
    filtered['RPM'] = filtered['RPM'].apply(lambda x: f"{x:.4f}")
    filtered['Gross Revenue'] = filtered['Gross Revenue'].apply(lambda x: f"${int(round(x))}")
    filtered['Revenue Cost'] = filtered['Revenue Cost'].apply(lambda x: f"${int(round(x))}")
    filtered['Serving Costs'] = filtered['Serving Costs'].apply(lambda x: f"${int(round(x))}")
    filtered['Net Revenue After Serving Costs'] = filtered['Net Revenue After Serving Costs'].apply(
        lambda x: f"${int(round(x))}" if x >= 0 else f"-${abs(int(round(x)))}"
    )

    # Only keep columns in requested order
    display_cols = [
        'Campaign ID', 'RPM', 'Request NE', 'Gross Revenue', 'Revenue Cost',
        'Serving Costs', 'Net Revenue After Serving Costs', 'Profit/Loss Status'
    ]
    table = filtered[display_cols].copy()
    table['Check to Block'] = False

    # Show Table with Checkboxes
    st.write("### Low RPM Products")
    table.reset_index(drop=True, inplace=True)
    # Use dataframe with editable checkboxes
    edited_table = st.data_editor(
        table,
        num_rows="dynamic",
        use_container_width=True,
        disabled=[col for col in table.columns if col != "Check to Block"]
    )

    # Download and Bulk Block buttons
    col1, col2 = st.columns([1, 2])
    with col1:
        st.download_button("Download to Excel", data=edited_table.to_csv(index=False), file_name="low_rpm_products.csv", mime="text/csv")
    with col2:
        if st.button("Block all checked boxes in bulk"):
            num_blocked = edited_table['Check to Block'].sum()
            st.success(f"Action: {num_blocked} products flagged for bulk block (demo only).")

    # AI-driven summary (footer)
    st.markdown("---")
    st.markdown("""
    **AI Insights:**
    - Most products here are unprofitable due to low RPM or high serving costs.
    - Consider blocking products with '🚩 Losing money' status to optimize cost efficiency.
    - Recommended RPM threshold: <span style='color:orange'><b>0.05</b></span>, Requests NE: <span style='color:orange'><b>10,000,000</b></span>
    - Adjust thresholds for more/less aggressive optimizations.
    """, unsafe_allow_html=True)

# For integration: call show_rpm_optimization() from your main app or sidebar nav.
