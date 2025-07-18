import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

def show_pubimps():
    st.markdown(
        "<h1 style='font-size:2.2rem; font-weight:900; display:flex; align-items:center; gap:0.6rem;'>"
        "🔍 Pubimps/Advimps Discrepancy"
        "</h1>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<div style='font-size:1.08rem; color:#656565; margin-bottom:1.1em;'>"
        "Analyze publisher and advertiser impression gaps and quickly spot products that are losing money."
        "</div>",
        unsafe_allow_html=True
    )

    df = st.session_state.get("main_df")
    if df is None or df.empty:
        st.warning("No data loaded. Please check your Excel file.")
        return

    # --- Calculations ---
    df = df.copy()
    df['Impression Gap'] = df['Publisher Impressions'] - df['Advertiser Impressions']
    df['Margin'] = (df['Gross Revenue'] - df['Revenue cost']) / df['Gross Revenue']

    # --- All Products Table (optional, just for context) ---
    st.markdown("### All Products")
    all_cols = ['Product', 'Campaign ID', 'Publisher Impressions', 'Advertiser Impressions', 'Gross Revenue', 'Revenue cost', 'Margin', 'Impression Gap']
    df_all = df[all_cols].copy()
    df_all['Margin'] = df_all['Margin'].apply(lambda x: f"{x:.1%}")
    for col in ['Publisher Impressions', 'Advertiser Impressions', 'Gross Revenue', 'Revenue cost', 'Impression Gap']:
        df_all[col] = df_all[col].apply(lambda x: f"{int(x):,}")
    st.dataframe(df_all, use_container_width=True, hide_index=True)

    # --- Negative Margin Products Table with Checkbox (AgGrid) ---
    st.markdown("### Products with Negative Margin")
    st.caption("Below are products where the margin is negative. You can select products to block by checking the box in the first column.")

    neg_df = df[df['Margin'] < 0].copy().reset_index(drop=True)

    # Ensure all columns are Python native types for AgGrid
    for col in neg_df.columns:
        neg_df[col] = neg_df[col].apply(lambda x: x.item() if hasattr(x, 'item') else x)

    neg_display = neg_df[['Product', 'Campaign ID', 'Publisher Impressions', 'Advertiser Impressions', 'Gross Revenue', 'Revenue cost', 'Margin', 'Impression Gap']].copy()
    neg_display['Margin'] = neg_display['Margin'].apply(lambda x: round(x * 100, 1))  # Percent, keep as float for coloring

    gb = GridOptionsBuilder.from_dataframe(neg_display)
    gb.configure_selection('multiple', use_checkbox=True)
    gb.configure_column("Margin", type=["numericColumn"], cellStyle=lambda params: {"color": "red" if params.value < 0 else "green"})
    grid_options = gb.build()

    grid_response = AgGrid(
        neg_display,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        fit_columns_on_grid_load=True,
        allow_unsafe_jscode=True,
        height=350
    )

    selected = grid_response["selected_rows"]
    if st.button("Block Selected"):
        if selected:
            products = [str(row['Product']) for row in selected]
            st.success(f"Blocked {len(products)} product(s): {', '.join(products)}")
        else:
            st.info("No products selected.")
