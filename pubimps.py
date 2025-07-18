def show_pubimps():
    import streamlit as st
    import pandas as pd
    import numpy as np
    from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
    import plotly.express as px

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

    # Ensure numeric types
    df['Publisher Impressions'] = pd.to_numeric(df['Publisher Impressions'], errors='coerce')
    df['Advertiser Impressions'] = pd.to_numeric(df['Advertiser Impressions'], errors='coerce')

    # Avoid division by zero
    df = df[df['Advertiser Impressions'] > 0].copy()

    # Calculate discrepancy: 1 - (PubImp / AdvImp)
    df['Discrepancy'] = 1 - (df['Publisher Impressions'] / df['Advertiser Impressions'])

    # Format large numbers with commas
    df['Publisher Impressions'] = df['Publisher Impressions'].apply(lambda x: f"{int(x):,}")
    df['Advertiser Impressions'] = df['Advertiser Impressions'].apply(lambda x: f"{int(x):,}")
    df['Discrepancy %'] = df['Discrepancy'].apply(lambda x: f"{x:.2%}")

    # Show graph FIRST (before any filtering)
    st.subheader("Discrepancy Distribution (Full dataset)")
    bins = np.arange(-1, 1.05, 0.05)
    temp_disc = pd.to_numeric(df['Discrepancy'], errors='coerce')
    df['Discrepancy Bin'] = pd.cut(temp_disc, bins=bins)
    bin_counts = df['Discrepancy Bin'].value_counts().sort_index()
    bin_labels = [f"{round(interval.left*100)}% to {round(interval.right*100)}%" for interval in bin_counts.index]
    hist_df = pd.DataFrame({
        "Discrepancy Range": bin_labels,
        "Count": bin_counts.values
    })
    fig = px.bar(
        hist_df,
        x="Discrepancy Range",
        y="Count",
        labels={'Count': 'Row count', 'Discrepancy Range': 'Discrepancy range'},
        title="Distribution of Impression Discrepancies"
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

    # Filtering toggles + flagged rows
    st.subheader("Flagged rows")
    show_under = st.checkbox("Show Under-delivery (>10%)", value=True)
    show_over = st.checkbox("Show Over-delivery (<-10%)", value=True)

    flagged_df = pd.DataFrame()
    temp_disc = pd.to_numeric(df['Discrepancy'], errors='coerce')
    if show_under and show_over:
        flagged_df = df[(temp_disc > 0.10) | (temp_disc < -0.10)]
    elif show_under:
        flagged_df = df[temp_disc > 0.10]
    elif show_over:
        flagged_df = df[temp_disc < -0.10]

    # Dynamically select all dimensions + metrics
    metric_cols = ['Publisher Impressions', 'Advertiser Impressions', 'Discrepancy %']
    dimension_cols = [col for col in flagged_df.columns if col not in metric_cols + ['Discrepancy', 'Discrepancy Bin']]
    display_cols = dimension_cols + metric_cols

    if not flagged_df.empty:
        gb = GridOptionsBuilder.from_dataframe(flagged_df[display_cols])
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
            flagged_df[display_cols],
            gridOptions=grid_options,
            update_mode=GridUpdateMode.SELECTION_CHANGED,
            fit_columns_on_grid_load=True,
            height=400,
            enable_enterprise_modules=False,
            custom_css=custom_css
        )
    else:
        st.info("No flagged rows match your criteria.")
        grid_return = {'selected_rows': []}

    selected_rows = grid_return['selected_rows'] if 'selected_rows' in grid_return else []

    # Download & Bulk Flag/Block Buttons
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="Download flagged rows as CSV",
            data=flagged_df[display_cols].to_csv(index=False),
            file_name="flagged_discrepancies.csv",
            mime="text/csv",
            disabled=flagged_df.empty
        )
    with col2:
        if st.button("Bulk Flag All Checked"):
            if selected_rows:
                st.success(f"Flagged {len(selected_rows)} checked rows.")
            else:
                st.warning("No rows selected to flag.")

    # AI-driven insights in footer
    st.markdown("---")
    over = (pd.to_numeric(flagged_df['Discrepancy'], errors='coerce') < -0.10).sum() if not flagged_df.empty else 0
    under = (pd.to_numeric(flagged_df['Discrepancy'], errors='coerce') > 0.10).sum() if not flagged_df.empty else 0
    st.subheader("🤖 AI Impression Discrepancy Insights")
    st.write(f"• **{under} rows** show under-delivery (publisher reported fewer imps than advertiser by >10%).")
    st.write(f"• **{over} rows** show over-delivery (publisher reported more imps than advertiser by >10%).")
    st.caption("_AI-powered insights: Quickly spot and export problematic discrepancies._")
