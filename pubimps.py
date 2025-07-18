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

    # --- Filter for past X days ---
    if 'Date' in df.columns:
        st.markdown("### Filter Data by Date")
        days = st.number_input(
            "Show data from the past X days (leave empty for all data)",
            min_value=1, max_value=365, value=30, step=1,
        )
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        max_date = df['Date'].max()
        min_allowed_date = max_date - pd.Timedelta(days=days)
        df = df[df['Date'] >= min_allowed_date]
        st.write(f"Showing data from **{min_allowed_date.date()}** to **{max_date.date()}**")
    else:
        st.info("No 'Date' column found. Cannot filter by date.")

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

    # Format for display
    flagged_df['Publisher Impressions'] = flagged_df['Publisher Impressions'].apply(lambda x: f"{int(x):,}")
    flagged_df['Advertiser Impressions'] = flagged_df['Advertiser Impressions'].apply(lambda x: f"{int(x):,}")
    flagged_df['Discrepancy %'] = flagged_df['Discrepancy'].apply(lambda x: f"{x:.2%}")

    metric_cols = ['Publisher Impressions', 'Advertiser Impressions', 'Discrepancy %']
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

    # --- IVT Bracket Distribution Chart ---
    st.markdown("## IVT Bracket Distribution (by Impressions)")

    bins = np.arange(0, 1.1, 0.1)
    labels = [f"{int(left*100)}–{int(right*100)}%" for left, right in zip(bins[:-1], bins[1:])]
    df['IVT Bracket'] = pd.cut(df['Discrepancy Abs'], bins=bins, labels=labels, include_lowest=True, right=False)

    # Aggregate total impressions in each bracket
    ivt_bracket_df = (
        df.groupby('IVT Bracket')['Advertiser Impressions']
        .sum()
        .reindex(labels, fill_value=0)
        .reset_index()
    )

    # Calculate percent of total for context
    total_imps = ivt_bracket_df['Advertiser Impressions'].sum()
    ivt_bracket_df['% of Total'] = (ivt_bracket_df['Advertiser Impressions'] / total_imps * 100).round(2)

    ivt_bracket_df.rename(columns={'Advertiser Impressions': 'Total Impressions'}, inplace=True)

    st.bar_chart(
        ivt_bracket_df.set_index('IVT Bracket')['Total Impressions'],
        use_container_width=True
    )
    st.dataframe(ivt_bracket_df)

    # AI-driven insights in footer
    st.markdown("---")
    st.subheader("🤖 AI Impression Discrepancy Insights")
    st.write(f"• **{len(flagged_df)} rows** show an absolute discrepancy greater than {threshold_pct}%.")
    st.caption("_AI-powered insights: Quickly spot and export problematic discrepancies._")
