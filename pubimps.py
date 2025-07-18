import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

def show_pubimps():
    st.markdown("🔍 <span style='font-size:2rem; font-weight:900;'>Pubimps/Advimps Discrepancy</span>", unsafe_allow_html=True)
    st.caption("Analyze publisher and advertiser impression gaps and quickly spot products that are losing money.")

    df = st.session_state.get("main_df")
    if df is None or df.empty:
        st.warning("No data loaded. Please check your Excel file.")
        return

    # --- Normalize and map columns for robustness ---
    col_map = {col.lower().replace(' ', '').replace('_',''): col for col in df.columns}
    def get_col(key):
        # Helper to robustly match user-given columns
        key = key.lower().replace(' ', '').replace('_','')
        for k, v in col_map.items():
            if key == k:
                return v
        raise Exception(f"Column '{key}' not found in data. Existing: {list(df.columns)}")

    # Calculations
    df = df.copy()
    df['Impression Gap'] = df[get_col('Publisher Impressions')] - df[get_col('Advertiser Impressions')]
    df['Margin'] = (df[get_col('Gross Revenue')] - df[get_col('Revenue Cost')]) / df[get_col('Gross Revenue')]
    df['Margin_fmt'] = df['Margin'].apply(lambda x: f"<span style='color: {'red' if x < 0 else 'green'}; font-weight:bold'>{x:.1%}</span>")
    df['Margin_num'] = df['Margin'].apply(lambda x: f"{x:.1%}")

    # Display columns
    cols_disp = [
        get_col('Product'), get_col('Campaign ID'),
        get_col('Publisher Impressions'), get_col('Advertiser Impressions'),
        get_col('Gross Revenue'), get_col('Revenue Cost'),
        'Margin_num', 'Impression Gap'
    ]
    show = df[cols_disp].rename(columns={'Margin_num': 'Margin'}).copy()

    # Format for display
    for c in [get_col('Publisher Impressions'), get_col('Advertiser Impressions'),
              get_col('Gross Revenue'), get_col('Revenue Cost'), 'Impression Gap']:
        show[c] = show[c].apply(lambda x: f"{int(round(x)):,}" if pd.notnull(x) and str(x).replace(',', '').replace('-', '').isdigit() else x)

    st.subheader("All Products - Sort by Any Column")
    st.dataframe(show, use_container_width=True, hide_index=True)

    # ---- NEGATIVE MARGIN TABLE ----
    st.subheader("Products with Negative Margin")
    st.caption("Below are products where the margin is negative. You can select products to block by checking the box in the first column.")

    neg = df[df['Margin'] < 0].copy().reset_index(drop=True)
    neg_disp = neg[[get_col('Product'), get_col('Campaign ID'), get_col('Publisher Impressions'),
                    get_col('Advertiser Impressions'), get_col('Gross Revenue'), get_col('Revenue Cost'),
                    'Margin_num', 'Impression Gap']].rename(columns={'Margin_num': 'Margin'})
    for c in [get_col('Publisher Impressions'), get_col('Advertiser Impressions'),
              get_col('Gross Revenue'), get_col('Revenue Cost'), 'Impression Gap']:
        neg_disp[c] = neg_disp[c].apply(lambda x: f"{int(round(x)):,}" if pd.notnull(x) and str(x).replace(',', '').replace('-', '').isdigit() else x)

    gb = GridOptionsBuilder.from_dataframe(neg_disp)
    gb.configure_selection('multiple', use_checkbox=True)
    for c in neg_disp.columns:
        gb.configure_column(c, cellStyle={'textAlign': 'center'})
    grid_options = gb.build()

    grid_response = AgGrid(
        neg_disp,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        fit_columns_on_grid_load=True,
        height=350,
        allow_unsafe_jscode=True
    )

    selected = grid_response.get('selected_rows', [])
    if st.button("Block Selected"):
        if selected:
            st.success(f"{len(selected)} products would be blocked!")
        else:
            st.info("No products selected.")

    # Add a summary for total loss
    total_loss = int(round(neg[get_col('Gross Revenue')].sum() - neg[get_col('Revenue Cost')].sum()))
    st.markdown(f"<div style='font-size:1.5em; font-weight:bold; color:red;'>Total Loss from Negative Margin Products: -${abs(total_loss):,}</div>", unsafe_allow_html=True)

