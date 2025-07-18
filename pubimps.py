def show_pubimps():
    import streamlit as st
    import pandas as pd
    import numpy as np
    from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

    st.title("📊 Impression Discrepancy Checker")

    df = st.session_state.get("main_df")
    if df is None or df.empty:
        st.info("No data found. Please upload data in the AI Insights tab first.")
        return

    required_cols = {'Publisher Impressions', 'Advertiser Impressions'}
    if not required_cols.issubset(set(df.columns)):
        st.warning(
            f"Your file must contain these columns: {', '.join(required_cols)}.\n"
            "If you just uploaded, check your file and re-upload on the AI Insights tab."
        )
        return

    # Flexible margin detection
    def find_col(possibilities, columns):
        for variant in possibilities:
            if variant in columns:
                return variant
        return None

    gross_rev_col = find_col(
        ['Gross Revenue', 'GrossRevenue', 'gross revenue', 'gross_revenue'],
        df.columns
    )
    rev_cost_col = find_col(
        ['Revenue Cost', 'RevenueCost', 'revenue cost', 'revenue_cost'],
        df.columns
    )

    dimension_cols = []
    for col in ['Package', 'Channel', 'Campaign ID']:
        if col in df.columns:
            dimension_cols.append(col)

    df['Publisher Impressions'] = pd.to_numeric(df['Publisher Impressions'], errors='coerce')
    df['Advertiser Impressions'] = pd.to_numeric(df['Advertiser Impressions'], errors='coerce')

    margin_available = False
    if gross_rev_col and rev_cost_col:
        df[gross_rev_col] = pd.to_numeric(df[gross_rev_col], errors='coerce').fillna(0)
        df[rev_cost_col] = pd.to_numeric(df[rev_cost_col], errors='coerce').fillna(0)
        df['Margin'] = df[gross_rev_col] - df[rev_cost_col]
        margin_available = True

    df = df[df['Advertiser Impressions'] > 0].copy()
    df['Discrepancy'] = 1 - (df['Publisher Impressions'] / df['Advertiser Impressions'])
    df['Discrepancy Abs'] = df['Discrepancy'].abs()

    threshold_pct = st.number_input(
        "Flag rows where absolute discrepancy is greater than (%)",
        min_value=0, max_value=100, value=30, step=1,
        format="%d"
    )
    threshold = threshold_pct / 100

    flagged_df = df[df['Discrepancy Abs'] > threshold].copy()
    flagged_df['Publisher Impressions'] = flagged_df['Publisher Impressions'].apply(lambda x: f"{int(x):,}")
    flagged_df['Advertiser Impressions'] = flagged_df['Advertiser Impressions'].apply(lambda x: f"{int(x):,}")
    flagged_df['Discrepancy %'] = flagged_df['Discrepancy'].apply(lambda x: f"{x:.2%}")
    if margin_available:
        flagged_df['Margin'] = flagged_df['Margin'].apply(lambda x: f"{int(round(x)):,}")

    metric_cols = ['Publisher Impressions', 'Advertiser Impressions', 'Discrepancy %']
    if margin_available:
        metric_cols.append('Margin')
    display_cols = [col for col in dimension_cols if col in flagged_df.columns] + metric_cols

    if not flagged_df.empty:
        gb = GridOptionsBuilder.from_dataframe(flagged_df[display_cols])
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
        AgGrid(
            flagged_df[display_cols],
            gridOptions=grid_options,
            update_mode=GridUpdateMode.NO_UPDATE,
            fit_columns_on_grid_load=True,
            height=400,
            enable_enterprise_modules=False,
            custom_css=custom_css
        )
    else:
        st.info("No flagged rows match your threshold.")

    st.download_button(
        label="Download flagged rows as CSV",
        data=flagged_df[display_cols].to_csv(index=False),
        file_name="flagged_discrepancies.csv",
        mime="text/csv",
        disabled=flagged_df.empty
    )

    if not flagged_df.empty and margin_available:
        margin_sum = df.loc[df['Discrepancy Abs'] > threshold, 'Margin'].sum()
        st.metric("Total Margin (flagged)", f"${int(round(margin_sum)):,}")

    # Show a warning if margin isn't available
    if not margin_available:
        st.info("Margin is only shown if both Gross Revenue and Revenue Cost columns are present.")

    st.markdown("---")
    st.subheader("🤖 AI Impression Discrepancy Insights")
    st.write(f"• **{len(flagged_df)} rows** show an absolute discrepancy greater than {threshold_pct}%.")
    st.caption("_AI-powered insights: Quickly spot and export problematic discrepancies._")
