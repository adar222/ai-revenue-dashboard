import streamlit as st
import pandas as pd
import numpy as np
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

def show_rpm_optimization():
    st.title("⚡ RPM Optimization")

    # Always scroll to top on tab entry
    st.markdown("<script>window.scrollTo(0,0);</script>", unsafe_allow_html=True)

    df = st.session_state.get("main_df")
    if df is None or df.empty:
        st.warning("No data found. Please upload data in the AI Insights tab first.")
        return

    # Filters
    rpm_threshold = st.number_input("Show products with RPM below:", min_value=0.0, value=0.05, step=0.01)
    req_threshold = st.number_input("Show products with Requests NE higher than:", min_value=0, value=10_000_000, step=1_000_000)

    # Map columns
    col_map = {col.lower(): col for col in df.columns}
    filtered = df.copy()
    filtered['Campaign ID'] = filtered[col_map['campaign id']]
    filtered['RPM'] = filtered[col_map['rpm']]
    filtered['Request NE'] = filtered[col_map['request ne']]
    filtered['Gross Revenue'] = filtered[col_map['gross revenue']]
    filtered['Revenue Cost'] = filtered[col_map['revenue cost']]

    # Calculate serving costs and profit
    filtered['Serving Costs'] = np.round(filtered['Request NE'] / 1_000_000_000 * 200).astype(int)
    filtered['Net Revenue After Serving Costs'] = filtered['Gross Revenue'] - filtered['Revenue Cost'] - filtered['Serving Costs']
    filtered['Profit/Loss Status'] = filtered['Net Revenue After Serving Costs'].apply(
        lambda x: "👍 Profitable" if x > 0 else "🚩 Losing money"
    )

    # Apply UI filters
    filtered = filtered[(filtered['RPM'] < rpm_threshold) & (filtered['Request NE'] > req_threshold)].copy()
    if filtered.empty:
        st.info("No products match your filters.")
        return

    # ==== AI Recommendations Panel ====
    st.markdown("""
        <div style="background:linear-gradient(90deg,#f5f8ff,#f0f5ff 80%);padding:1.3em 1.6em 1em 1.6em;border-radius:18px;box-shadow:0 2px 12px #0001;">
        <span style="font-size:1.3rem;font-weight:800;color:#2d47cc;">🤖 AI Recommendations</span>
        <ul style="margin-top:0.5em;">
    """, unsafe_allow_html=True)

    # Top 3 biggest loss products
    worst = filtered.nsmallest(3, 'Net Revenue After Serving Costs')
    for _, row in worst.iterrows():
        st.markdown(
            f"<li style='color:#db2525;font-size:1.07rem;'>Block Product <b>{row['Campaign ID']}</b> (Net Loss: <b>${abs(int(row['Net Revenue After Serving Costs'])):,}</b>)</li>",
            unsafe_allow_html=True
        )

    # Dynamic trends and suggestions
    main_campaign = filtered.groupby('Campaign ID')['Net Revenue After Serving Costs'].sum().idxmin()
    st.markdown(
        f"<li style='color:#1e3a8a;'>Most total loss is from <b>Campaign {main_campaign}</b>.</li>",
        unsafe_allow_html=True
    )

    high_loss_count = (filtered['Net Revenue After Serving Costs'] < 0).sum()
    st.markdown(
        f"<li>Blocking all products with negative profit would save <b>{high_loss_count}</b> losses instantly.</li>",
        unsafe_allow_html=True
    )
    st.markdown("</ul></div>", unsafe_allow_html=True)
    st.write("")  # Spacer

    # ========== TABLE ==========
    # For interactive blocking
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

    grid_df = filtered[display_cols].copy()
    grid_df['Gross Revenue'] = grid_df['Gross Revenue'].apply(lambda x: f"${int(round(x))}")
    grid_df['Revenue Cost'] = grid_df['Revenue Cost'].apply(lambda x: f"${int(round(x))}")
    grid_df['Serving Costs'] = grid_df['Serving Costs'].apply(lambda x: f"${int(round(x))}")
    grid_df['Net Revenue After Serving Costs'] = grid_df['Net Revenue After Serving Costs'].apply(
        lambda x: f"${int(round(x))}" if x >= 0 else f"-${abs(int(round(x)))}"
    )
    grid_df['Request NE'] = grid_df['Request NE'].apply(lambda x: f"{int(x):,}")

    gb = GridOptionsBuilder.from_dataframe(grid_df)
    gb.configure_selection('multiple', use_checkbox=True)
    for col in display_cols:
        gb.configure_column(
            col,
            cellStyle={'textAlign': 'center'},
            headerClass='centered-header'
        )
    grid_options = gb.build()
    custom_css = {
        ".centered-header": {"justify-content": "center !important", "display": "flex !important"}
    }

    grid_return = AgGrid(
        grid_df,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        fit_columns_on_grid_load=True,
        height=400,
        enable_enterprise_modules=False,
        custom_css=custom_css
    )
    selected_rows = grid_return['selected_rows']

    # ==== What-If Simulator ====
    st.markdown("""
        <div style="background:#fff7ed;border-radius:18px;margin:1.7em 0 1em 0;padding:1.2em 1.5em 1.4em 1.5em;border:1.5px solid #ffe3c7;">
        <span style="font-size:1.2rem;font-weight:700;color:#c2410c;">🧠 What-If Simulator</span>
    """, unsafe_allow_html=True)
    if selected_rows:
        total_loss = sum(
            -int(row['Net Revenue After Serving Costs'].replace('$','').replace(',','').replace('-',''))
            for row in selected_rows if '-' in row['Net Revenue After Serving Costs']
        )
        st.markdown(f"<span style='font-size:1.08rem;color:#991b1b;'>If you block the selected products, you will eliminate <b>${total_loss:,}</b> in losses.</span>", unsafe_allow_html=True)
    else:
        st.markdown("<span style='font-size:1.08rem;color:#555;'>Select rows above to simulate blocking and see the potential loss reduction here.</span>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Download & Bulk Block Buttons
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="Download to Excel",
            data=grid_df.to_csv(index=False),
            file_name="rpm_optimization.csv",
            mime="text/csv",
        )
    with col2:
        if st.button("Block All Checked in Bulk"):
            if selected_rows:
                st.success(f"Blocking {len(selected_rows)} checked products.")
            else:
                st.warning("No products selected to block.")

    # ==== AI Cost Efficiency Insights (footer) ====
    st.markdown("---")
    losing_count = (filtered['Profit/Loss Status'] == "🚩 Losing money").sum()
    st.subheader("🤖 AI Cost Efficiency Insights")
    st.write(f"• **{losing_count} products** are currently losing money due to high serving costs. Consider blocking them for better cost efficiency.")
    st.write("• **Serving Costs:** $200 per 1B Requests.")
    st.write("• **Net Revenue After Serving Costs:** Gross Revenue – Revenue Cost – Serving Costs.")
    st.caption("_AI-powered insights: Optimize for true profitability!_")

    # Total loss summary
    total_neg_margin_loss = -filtered.loc[filtered['Net Revenue After Serving Costs'] < 0, 'Net Revenue After Serving Costs'].sum()
    st.markdown(
        f"<div style='font-size:1.35rem;color:#c00;font-weight:700;margin-top:1em;'>Total Loss from Negative Margin Products (after serving costs): -${int(total_neg_margin_loss):,}</div>",
        unsafe_allow_html=True
    )
