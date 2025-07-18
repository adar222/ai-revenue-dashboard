import streamlit as st
import pandas as pd
import numpy as np
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

def show_rpm_optimization():
    st.title("⚡ RPM Optimization")

    df = st.session_state.get("main_df")
    if df is None or df.empty:
        st.warning("No data found. Please upload data in the AI Insights tab first.")
        return

    # Filters
    rpm_threshold = st.number_input("Show products with RPM below:", min_value=0.0, value=0.05, step=0.01)
    req_threshold = st.number_input("Show products with Requests NE higher than:", min_value=0, value=10_000_000, step=1_000_000)

    # Mapping columns (edit as needed)
    col_map = {col.lower(): col for col in df.columns}
    filtered = df.copy()
    filtered['Campaign ID'] = filtered[col_map['campaign id']]
    filtered['RPM'] = filtered[col_map['rpm']]
    filtered['Request NE'] = filtered[col_map['request ne']]
    filtered['Gross Revenue'] = filtered[col_map['gross revenue']]
    filtered['Revenue Cost'] = filtered[col_map['revenue cost']]

    # Apply filters
    filtered = filtered[(filtered['RPM'] < rpm_threshold) & (filtered['Request NE'] > req_threshold)].copy()
    if filtered.empty:
        st.info("No products match your filters.")
        return

    # Calculate serving costs & profitability
    filtered['Serving Costs'] = np.round(filtered['Request NE'] / 1_000_000_000 * 200).astype(int)
    filtered['Net Revenue After Serving Costs'] = filtered['Gross Revenue'] - filtered['Revenue Cost'] - filtered['Serving Costs']
    filtered['Profit/Loss Status'] = filtered['Net Revenue After Serving Costs'].apply(
        lambda x: "👍 Profitable" if x > 0 else "🚩 Losing money"
    )

    # Format columns for display
    filtered['Gross Revenue'] = filtered['Gross Revenue'].apply(lambda x: f"${int(round(x))}")
    filtered['Revenue Cost'] = filtered['Revenue Cost'].apply(lambda x: f"${int(round(x))}")
    filtered['Serving Costs'] = filtered['Serving Costs'].apply(lambda x: f"${int(round(x))}")
    filtered['Net Revenue After Serving Costs'] = filtered['Net Revenue After Serving Costs'].apply(
        lambda x: f"${int(round(x))}" if x >= 0 else f"-${abs(int(round(x)))}"
    )
    filtered['Request NE'] = filtered['Request NE'].apply(lambda x: f"{int(x):,}")

    display_cols = [
        'Profit/Loss Status',
        'Campaign ID',
        'RPM',
        'Request NE',
        'Gross Revenue',
        'Revenue Cost',
        'Serving Costs',
        'Net Revenue After Serving Costs',
    ]

    # AgGrid for inline checkboxes
    gb = GridOptionsBuilder.from_dataframe(filtered[display_cols])
    gb.configure_selection('multiple', use_checkbox=True)
    grid_options = gb.build()
    grid_return = AgGrid(
        filtered[display_cols],
        gridOptions=grid_options,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        fit_columns_on_grid_load=True,
        height=400,
        enable_enterprise_modules=False,
    )

    selected_rows = grid_return['selected_rows']

    # Download & Bulk Block Buttons
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="Download to Excel",
            data=filtered[display_cols].to_csv(index=False),
            file_name="rpm_optimization.csv",
            mime="text/csv",
        )
    with col2:
        if st.button("Block All Checked in Bulk"):
            if selected_rows:
                st.success(f"Blocking {len(selected_rows)} checked products.")
            else:
                st.warning("No products selected to block.")

    # AI-driven insights in footer
    st.markdown("---")
    losing_count = (filtered['Profit/Loss Status'] == "🚩 Losing money").sum()
    st.subheader("🤖 AI Cost Efficiency Insights")
    st.write(f"• **{losing_count} products** are currently losing money due to high serving costs. Consider blocking them for better cost efficiency.")
    st.write("• **Serving Costs:** $200 per 1B Requests.")
    st.write("• **Net Revenue After Serving Costs:** Gross Revenue – Revenue Cost – Serving Costs.")
    st.caption("_AI-powered insights: Optimize for true profitability!_")
