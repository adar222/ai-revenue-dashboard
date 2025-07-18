import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

def show_pubimps():
    # --- Header with icon and description ---
    st.markdown(
        "<h1 style='font-size:2.5rem; font-weight:900; display:flex; align-items:center; gap:0.6rem;'>"
        "🔍 Pubimps/Advimps Discrepancy"
        "</h1>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<div style='font-size:1.1rem; color:#656565; margin-bottom:1.2em;'>"
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

    # --- Table 1: All Products ---
    st.markdown("### All Products - Sort by Any Column")
    all_cols = ['Product', 'Campaign ID', 'Publisher Impressions', 'Advertiser Impressions', 'Gross Revenue', 'Revenue cost', 'Margin', 'Impression Gap']
    df_all = df[all_cols].copy()
    df_all['Margin'] = df_all['Margin'].apply(lambda x: f"{x:.1%}")
    for col in ['Publisher Impressions', 'Advertiser Impressions', 'Gross Revenue', 'Revenue cost', 'Impression Gap']:
        df_all[col] = df_all[col].apply(lambda x: f"{int(x):,}")

    st.dataframe(df_all, use_container_width=True, hide_index=True)

    # --- Table 2: Negative Margin Products with AgGrid Checkboxes ---
    st.markdown("### Products with Negative Margin")

    neg_df = df[df['Margin'] < 0].copy()
    neg_df = neg_df.reset_index(drop=True)
    neg_df_display = neg_df[['Product', 'Campaign ID', 'Publisher Impressions', 'Advertiser Impressions', 'Gross Revenue', 'Revenue cost', 'Margin', 'Impression Gap']].copy()
    neg_df_display['Margin'] = neg_df_display['Margin'].apply(lambda x: f"{x:.1%}")

    for col in ['Publisher Impressions', 'Advertiser Impressions', 'Gross Revenue', 'Revenue cost', 'Impression Gap']:
        neg_df_display[col] = neg_df_display[col].apply(lambda x: f"{int(x):,}")

    gb = GridOptionsBuilder.from_dataframe(neg_df_display)
    gb.configure_selection('multiple', use_checkbox=True)
    gb.configure_column('Margin', cellStyle=lambda params: {"color": "red", "fontWeight": "bold"})
    grid_options = gb.build()

    grid_return = AgGrid(
        neg_df_display,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        fit_columns_on_grid_load=True,
        height=350,
        enable_enterprise_modules=False
    )

    selected = grid_return["selected_rows"]

    if st.button("Block Selected"):
        if selected:
            products = [str(row['Product']) for row in selected]
            st.success(f"Blocked {len(products)} product(s): {', '.join(products)}")
        else:
            st.info("No products selected.")
