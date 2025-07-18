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

    # Specify your fixed dimension columns here
    dimension_cols = []
    for col in ['Package', 'Channel', 'Campaign ID']:
        if col in df.columns:
            dimension_cols.append(col)

    # Numeric conversions for calculations
    df['Publisher Impressions'] = pd.to_numeric(df['Publisher Impressions'], errors='coerce')
    df['Advertiser Impressions'] = pd.to_numeric(df['Advertiser Impressions'], errors='coerce')

    # Add gross revenue and revenue cost if they exist
    extra_metric_cols = []
    if 'Gross Revenue' in df.columns:
        df['Gross Revenue'] = pd.to_numeric(df['Gross Revenue'], errors='coerce').fillna(0)
        extra_metric_cols.append('Gross Revenue')
    if 'Revenue Cost' in df.columns:
        df['Revenue Cost'] = pd.to_numeric(df['Revenue Cost'], errors='coerce').fillna(0)
        extra_metric_cols.append('Revenue Cost')

    # Avoid division by zero
    df = df[df['Advertiser Impressions'] > 0].copy()

    # Calculate discrepancy
    df['Discrepancy'] = 1 - (df['Publisher Impressions'] / df['Advertiser Impressions'])
    df['Discrepancy Abs'] = df['Discrepancy'].abs()

    # User sets the threshold as a percentage, default is 30%
    threshold_pct = st.number_input(
        "Flag rows where absolute discrepancy is greater than (%)",
        min_value=0, max_value=100, value=30, step=1,
        format="%d"
    )
    threshold = threshold_pct / 100  # convert to decimal

    # Filter flagged rows by threshold
    flagged_df = df[df['Discrepancy Abs'] > threshold].copy()

    # Format for display (no decimals)
    flagged_df['Publisher Impressions'] = flagged_df['Publisher Impressions'].apply(lambda x: f"{int(x):,}")
    flagged_df['Advertiser Impressions'] = flagged_df['Advertiser Impressions'].apply(lambda x: f"{int(x):,}")
    flagged_df['Discrepancy %'] = flagged_df['Discrepancy'].apply(lambda x: f"{x:.2%}")
    if 'Gross Revenue' in flagged_df.columns:
        flagged_df['Gross Revenue'] = flagged_df['Gross Revenue'].apply(lambda x: f"{int(round(x)):,}")
    if 'Revenue Cost' in flagged_df.columns:
        flagged_df['Revenue Cost'] = flagged_df['Revenue Cost'].apply(lambda x: f"{int(round(x)):,}")

    # Display columns: dimensions + always metrics + extras if present
    metric_cols = ['Publisher Impressions', 'Advertiser Impressions', 'Discrepancy %'] + extra_metric_cols
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

    # Download Button
    st.download_button(
        label="Download flagged rows as CSV",
        data=flagged_df[display_cols].to_csv(index=False),
        file_name="flagged_discrepancies.csv",
        mime="text/csv",
        disabled=flagged_df.empty
    )

    # Metrics/sum for Gross Revenue and Revenue Cost
    if not flagged_df.empty and 'Gross Revenue' in df.columns and 'Revenue Cost' in df.columns:
        # Use unformatted for sum (need to access numeric, not formatted string)
        gross_sum = df.loc[df['Discrepancy Abs'] > threshold, 'Gross Revenue'].sum()
        cost_sum = df.loc[df['Discrepancy Abs'] > threshold, 'Revenue Cost'].sum()
        st.metric("Total Gross Revenue (flagged)", f"${int(round(gross_sum)):,}")
        st.metric("Total Revenue Cost (flagged)", f"${int(round(cost_sum)):,}")

    # AI-driven insights in footer
    st.markdown("---")
    st.subheader("🤖 AI Impression Discrepancy Insights")
    st.write(f"• **{len(flagged_df)} rows** show an absolute discrepancy greater than {threshold_pct}%.")
    st.caption("_AI-powered insights: Quickly spot and export problematic discrepancies._")
