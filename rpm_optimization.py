import streamlit as st
import pandas as pd
import numpy as np

def show_rpm_optimization():
    st.title("⚡ RPM Optimization")

    # 1. Get Data
    df = st.session_state.get("main_df")
    if df is None or df.empty:
        st.warning("No data found. Please upload data in the AI Insights tab first.")
        return

    # 2. User Filters
    rpm_threshold = st.number_input("Show products with RPM below:", min_value=0.0, value=0.05, step=0.01)
    req_threshold = st.number_input("Show products with Requests NE higher than:", min_value=0, value=10000000, step=1000000)

    # 3. Clean/prepare columns
    # Ensure proper column types and case
    col_map = {col.lower(): col for col in df.columns}
    required_cols = ['campaign id', 'rpm', 'request ne', 'gross revenue']
    missing = [col for col in required_cols if col not in [c.lower() for c in df.columns]]
    if missing:
        st.error(f"Missing columns in data: {', '.join(missing)}")
        return

    # Consistent column references
    df['RPM'] = df[col_map['rpm']]
    df['Request NE'] = df[col_map['request ne']]
    df['Gross Revenue'] = df[col_map['gross revenue']]
    df['Campaign ID'] = df[col_map['campaign id']]

    # 4. Filter by user thresholds
    filtered = df[(df['RPM'] < rpm_threshold) & (df['Request NE'] > req_threshold)].copy()

    if filtered.empty:
        st.info("No products match your filters.")
        return

    # 5. Calculate Serving Costs and Net Revenue
    filtered['Serving Costs'] = np.round(filtered['Request NE'] / 1_000_000_000 * 200).astype(int)
    filtered['Gross Revenue'] = filtered['Gross Revenue'].round(0).astype(int)
    filtered['Net Revenue after Serving Costs'] = filtered['Gross Revenue'] - filtered['Serving Costs']

    # 6. Profit/Loss Status logic
    def status_emoji(netrev):
        if netrev > 0:
            return "👍 Profitable"
        else:
            return "🚩 Losing money"

    filtered['Profit/Loss Status'] = filtered['Net Revenue after Serving Costs'].apply(status_emoji)

    # 7. Display Table (only key columns)
    display_cols = [
        'Campaign ID',
        'RPM',
        'Request NE',
        'Gross Revenue',
        'Serving Costs',
        'Net Revenue after Serving Costs',
        'Profit/Loss Status',
        # The following will be the checkbox column
    ]

    # Add checkboxes for "Check to Block"
    filtered['Check to Block'] = [False] * len(filtered)
    checked = [st.checkbox('', key=f"block_{i}") for i in filtered.index]
    filtered['Check to Block'] = checked

    # Format columns for display
    filtered['Gross Revenue'] = filtered['Gross Revenue'].apply(lambda x: f"${int(x)}")
    filtered['Serving Costs'] = filtered['Serving Costs'].apply(lambda x: f"${int(x)}")
    filtered['Net Revenue after Serving Costs'] = filtered['Net Revenue after Serving Costs'].apply(
        lambda x: f"${int(x)}" if x >= 0 else f"-${abs(int(x))}"
    )

    # Show the table (hide index)
    st.dataframe(filtered[display_cols + ['Check to Block']], use_container_width=True, hide_index=True)

    # 8. Action Buttons
    c1, c2 = st.columns(2)
    with c1:
        st.download_button(
            label="Download to Excel",
            data=filtered[display_cols].to_csv(index=False),
            file_name="rpm_optimization.csv",
            mime="text/csv",
        )
    with c2:
        st.button("Block All Checked in Bulk")

    st.markdown("---")
    # 9. AI Insights (Footer)
    losing_count = (filtered['Profit/Loss Status'] == "🚩 Losing money").sum()
    saving = abs(filtered.loc[filtered['Profit/Loss Status'] == "🚩 Losing money", 'Net Revenue after Serving Costs']
                 .map(lambda s: int(str(s).replace("$", "").replace("-", ""))).sum())
    st.subheader("🤖 AI Cost Efficiency Insights")
    st.write(f"• **{losing_count} products** are currently losing money due to high serving costs. "
             f"Blocking them could save **~${saving}/month** and remove non-profitable traffic.")
    st.write("• **Serving Costs** are calculated as: `Requests NE × $200 per 1B requests (rounded)`.")
    st.write("• **Net Revenue after Serving Costs** = `Gross Revenue – Serving Costs`.")
    st.write("• **Profit/Loss Status**: 👍 Profitable for Net Revenue > 0, 🚩 Losing money for Net Revenue ≤ 0.")
    st.caption(f"_Last updated: {pd.Timestamp.now():%Y-%m-%d %H:%M}_")
    st.caption("_AI-powered insights: Optimize for true profitability!_")

# If you want to run this as a standalone script, uncomment:
# if __name__ == "__main__":
#     show_rpm_optimization()
