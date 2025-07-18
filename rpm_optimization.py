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

    # --- Filters
    rpm_threshold = st.number_input("Show products with RPM below:", min_value=0.0, value=0.05, step=0.01)
    req_threshold = st.number_input("Show products with Requests NE higher than:", min_value=0, value=10_000_000, step=1_000_000)

    # --- Column mapping (robust)
    col_map = {col.lower(): col for col in df.columns}
    filtered = df.copy()
    filtered['Campaign ID'] = filtered[col_map['campaign id']]
    filtered['RPM'] = filtered[col_map['rpm']]
    filtered['Request NE'] = filtered[col_map['request ne']]
    filtered['Gross Revenue'] = filtered[col_map['gross revenue']]
    filtered['Revenue Cost'] = filtered[col_map['revenue cost']]

    # --- Apply filters
    filtered = filtered[(filtered['RPM'] < rpm_threshold) & (filtered['Request NE'] > req_threshold)].copy()
    if filtered.empty:
        st.info("No products match your filters.")
        return

    # --- Calculate serving costs & profitability
    filtered['Serving Costs'] = np.round(filtered['Request NE'] / 1_000_000_000 * 200).astype(int)
    filtered['Net Revenue After Serving Costs'] = filtered['Gross Revenue'] - filtered['Revenue Cost'] - filtered['Serving Costs']
    filtered['Profit/Loss Status'] = filtered['Net Revenue After Serving Costs'].apply(
        lambda x: "👍 Profitable" if x > 0 else "🚩 Losing money"
    )

    # --- Format columns for display
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

    # --- AgGrid for selection
    gb = GridOptionsBuilder.from_dataframe(filtered[display_cols])
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
        filtered[display_cols],
        gridOptions=grid_options,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        fit_columns_on_grid_load=True,
        height=400,
        enable_enterprise_modules=False,
        custom_css=custom_css
    )
    selected_rows = grid_return['selected_rows']

    # --- Download & Bulk Block Buttons
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
            if selected_rows and len(selected_rows) > 0:
                st.success(f"Blocking {len(selected_rows)} checked products.")
            else:
                st.warning("No products selected to block.")

    st.markdown("---")

    # --- AI Cost Efficiency Insights
    losing_count = (filtered['Profit/Loss Status'] == "🚩 Losing money").sum()
    st.subheader("🤖 AI Cost Efficiency Insights")
    st.write(f"• **{losing_count} products** are currently losing money due to high serving costs. Consider blocking them for better cost efficiency.")
    st.write("• **Serving Costs:** $200 per 1B Requests.")
    st.write("• **Net Revenue After Serving Costs:** Gross Revenue – Revenue Cost – Serving Costs.")
    st.caption("_AI-powered insights: Optimize for true profitability!_")

    # --- Add What-If Simulator (AI-powered)
    st.markdown(
        "<div style='margin-top:2.3em; background:#fff7ed; border-radius:1.2em; padding:1.3em 1.7em;'>"
        "<span style='font-size:1.25rem;font-weight:700;color:#e8790b;letter-spacing:-0.5px;'>"
        "🧠 What-If Simulator</span>"
        "</div>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<span style='font-size:1.07rem;color:#444;'>"
        "Select products above and instantly see how blocking them would reduce total loss."
        "</span>",
        unsafe_allow_html=True
    )

    # --- What-If Simulator Logic (bulletproof for all data types)
    total_loss = 0
    if selected_rows is not None and len(selected_rows) > 0:
        for row in selected_rows:
            net = None
            for key in row:
                if "Net Revenue After Serving Costs" in key:
                    net = row[key]
                    break
            if net is None:
                continue
            net_str = str(net).replace('$', '').replace(',', '').strip()
            is_negative = net_str.startswith('-')
            net_int = int(net_str.replace('-', '')) if net_str.replace('-', '').isdigit() else 0
            if is_negative and net_int > 0:
                total_loss += net_int
        if total_loss > 0:
            st.markdown(
                f"<span style='font-size:1.08rem;color:#991b1b;'>"
                f"If you block the selected products, you will eliminate <b>${total_loss:,}</b> in losses.</span>",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                "<span style='font-size:1.08rem;color:#1e293b;'>"
                "The selected products are not contributing to losses."
                "</span>",
                unsafe_allow_html=True
            )
    else:
        st.markdown(
            "<span style='font-size:1.08rem;color:#555;'>"
            "Select rows above to simulate blocking and see the potential loss reduction here."
            "</span>",
            unsafe_allow_html=True
        )

    # --- Show Total Loss (final footer)
    total_negative_margin = 0
    for val in filtered['Net Revenue After Serving Costs']:
        val_str = str(val).replace('$','').replace(',','').replace('-','')
        if '-' in str(val):
            total_negative_margin += int(val_str) if val_str.isdigit() else 0

    st.markdown(
        f"<div style='margin-top:2em;font-size:1.25rem; font-weight:800; color:#d40000;'>"
        f"Total Loss from Negative Margin Products (after serving costs): -${total_negative_margin:,}"
        f"</div>",
        unsafe_allow_html=True
    )
