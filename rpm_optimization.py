import streamlit as st
import pandas as pd
import numpy as np

def show_rpm_optimization():
    st.title("⚡ RPM Optimization")

    # 1. Get DataFrame from session (change to your main session key if different)
    df = st.session_state.get("main_df")
    if df is None or df.empty:
        st.warning("No data found. Please upload data in the AI Insights tab first.")
        return

    # 2. User Filters
    rpm_threshold = st.number_input("Show products with RPM below:", min_value=0.0, value=0.05, step=0.01)
    req_threshold = st.number_input("Show products with Requests NE higher than:", min_value=0, value=10000000, step=1000000)

    # 3. Column mapping to avoid case-sensitivity issues
    col_map = {col.lower(): col for col in df.columns}
    required_cols = ['campaign id', 'rpm', 'request ne', 'gross revenue', 'revenue cost']
    missing = [col for col in required_cols if col not in [c.lower() for c in df.columns]]
    if missing:
        st.error(f"Missing columns in data: {', '.join(missing)}")
        return

    # 4. Prepare filtered data
    filtered = df.copy()
    filtered['Campaign ID'] = filtered[col_map['campaign id']]
    filtered['RPM'] = filtered[col_map['rpm']]
    filtered['Request NE'] = filtered[col_map['request ne']]
    filtered['Gross Revenue'] = filtered[col_map['gross revenue']]
    filtered['Revenue Cost'] = filtered[col_map['revenue cost']]

    # Filter rows
    filtered = filtered[(filtered['RPM'] < rpm_threshold) & (filtered['Request NE'] > req_threshold)].copy()
    if filtered.empty:
        st.info("No products match your filters.")
        return

    # 5. Calculations
    filtered['Serving Costs'] = np.round(filtered['Request NE'] / 1_000_000_000 * 200).astype(int)
    filtered['Net Revenue After Serving Costs'] = filtered['Gross Revenue'] - filtered['Revenue Cost'] - filtered['Serving Costs']
    filtered['Profit/Loss Status'] = filtered['Net Revenue After Serving Costs'].apply(
        lambda x: "👍 Profitable" if x > 0 else "🚩 Losing money"
    )

    # 6. Formatting for display (rounded, $ sign)
    filtered['Gross Revenue'] = filtered['Gross Revenue'].apply(lambda x: f"${int(round(x))}")
    filtered['Revenue Cost'] = filtered['Revenue Cost'].apply(lambda x: f"${int(round(x))}")
    filtered['Serving Costs'] = filtered['Serving Costs'].apply(lambda x: f"${int(round(x))}")
    filtered['Net Revenue After Serving Costs'] = filtered['Net Revenue After Serving Costs'].apply(
        lambda x: f"${int(round(x))}" if x >= 0 else f"-${abs(int(round(x)))}"
    )

    # 7. Display table columns in correct order
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

    # 8. Checkboxes for blocking (shown in a separate list, not inside st.dataframe)
    checked = [st.checkbox(f"Block {row['Campaign ID']}", key=f"block_{idx}", label_visibility="collapsed") 
               for idx, row in filtered.iterrows()]
    filtered['Check to Block'] = checked

    # 9. Show table (one single table, checkboxes on right)
    st.dataframe(filtered[display_cols + ['Check to Block']], use_container_width=True, hide_index=True)

    # 10. Download & Block Buttons
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="Download to Excel",
            data=filtered[display_cols].to_csv(index=False),
            file_name="rpm_optimization.csv",
            mime="text/csv",
        )
    with col2:
        st.button("Block All Checked in Bulk")

    # 11. AI Footer
    st.markdown("---")
    losing_count = (filtered['Profit/Loss Status'] == "🚩 Losing money").sum()
    st.subheader("🤖 AI Cost Efficiency Insights")
    st.write(f"• **{losing_count} products** are currently losing money due to high serving costs. Consider blocking them for better cost efficiency.")
    st.write("• **Serving Costs:** $200 per 1B Requests.")
    st.write("• **Net Revenue After Serving Costs:** Gross Revenue – Revenue Cost – Serving Costs.")
    st.caption("_AI-powered insights: Optimize for true profitability!_")

# --- END OF FUNCTION ---
