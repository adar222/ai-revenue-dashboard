import streamlit as st
import pandas as pd
import numpy as np

def show_ivt_optimization():
    st.title("🏴 IVT Optimization Recommendations")

    # --- 1. Get Data ---
    df = st.session_state.get("main_df")
    if df is None or df.empty:
        st.warning("No data found in main_df. Please upload your data file below:")
        uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx"])
        if uploaded_file is not None:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            st.session_state["main_df"] = df
            st.success("File uploaded! Data is now available for analysis.")
        else:
            st.stop()

    # --- 2. User Inputs ---
    days = st.number_input("Show data for last... days", min_value=1, max_value=60, value=3)
    ivt_threshold = st.number_input("IVT Threshold (%)", min_value=0, max_value=100, value=10)

    # --- 3. Filter by date ---
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        end_date = df['Date'].max()
        start_date = end_date - pd.Timedelta(days=days-1)
        filtered_df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
    else:
        st.error("Date column not found in your data!")
        st.stop()

    if filtered_df.empty:
        st.info("No data in the selected date range.")
        st.stop()

    # --- 4. Column selection for IVT ---
    ivt_candidates = [col for col in filtered_df.columns if 'ivt' in col.lower()]
    if ivt_candidates:
        ivt_col = ivt_candidates[0]
    else:
        ivt_col = st.selectbox("Select IVT column", filtered_df.columns)
    if ivt_col not in filtered_df.columns:
        st.error(f"Column '{ivt_col}' not found in data.")
        st.stop()

    # --- 5. Aggregate by Product ID, Package, Campaign ID, Campaign ---
    group_cols = ['Product', 'Package', 'Campaign ID', 'Campaign']
    agg_dict = {}
    if 'Requests' in filtered_df.columns:
        agg_dict['Requests'] = 'sum'
    if 'Gross Revenue' in filtered_df.columns:
        agg_dict['Gross Revenue'] = 'sum'
    agg_dict[ivt_col] = ['mean', 'max']

    group_cols = [col for col in group_cols if col in filtered_df.columns]

    try:
        agg_df = filtered_df.groupby(group_cols, dropna=False).agg(agg_dict)
    except Exception as e:
        st.error(f"Aggregation error: {e}")
        st.write("Group columns:", group_cols)
        st.write("Aggregation dict:", agg_dict)
        st.stop()

    # --- 6. Flatten multiindex columns ---
    def flatten_col(col):
        if isinstance(col, tuple):
            if col[1] == '':
                return col[0]
            elif col[1] == 'mean':
                return 'Avg IVT'
            elif col[1] == 'max':
                return 'Max IVT'
            else:
                return f"{col[0]} {col[1]}"
        return col
    agg_df.columns = [flatten_col(c) for c in agg_df.columns]
    agg_df = agg_df.reset_index()

    # --- 7. Defensive: find actual column names dynamically ---
    max_ivt_col = next((c for c in agg_df.columns if 'max' in c.lower() and 'ivt' in c.lower()), None)
    avg_ivt_col = next((c for c in agg_df.columns if 'avg' in c.lower() and 'ivt' in c.lower()), None)
    if not max_ivt_col:
        st.error(f"No 'Max IVT' column found! Columns: {agg_df.columns.tolist()}")
        st.stop()

    # --- 8. Format columns ---
    if avg_ivt_col:
        agg_df[avg_ivt_col] = agg_df[avg_ivt_col].round(0).astype('Int64').astype(str) + '%'
    agg_df[max_ivt_col] = agg_df[max_ivt_col].round(0).astype('Int64').astype(str) + '%'

    # Recommendation logic (using numeric for logic, not formatted string)
    agg_df['Max IVT Numeric'] = agg_df[max_ivt_col].str.replace('%', '', regex=False).astype(float)
    agg_df['Recommendation'] = np.where(
        agg_df['Max IVT Numeric'] >= ivt_threshold,
        "🚩 Block product at campaign level",
        "No action"
    )

    # Format Gross Revenue with $
    if 'Gross Revenue' in agg_df.columns:
        agg_df['Gross Revenue'] = agg_df['Gross Revenue'].replace('[\$,]', '', regex=True).astype(float)
        agg_df['Gross Revenue'] = agg_df['Gross Revenue'].apply(lambda x: f"${int(round(x, 0)):,}")

    # Add "Check to Block" column (for demo, default False)
    agg_df['Check to Block'] = False

    # Display date range and summary
    st.markdown(
        f"**Data aggregated by Product, Package, Campaign ID, and Campaign**  \n"
        f"**Period:** {start_date.date()} – {end_date.date()}"
    )
    total_revenue = agg_df['Gross Revenue'].replace({'\$':'', ',':''}, regex=True).astype(float).sum() if 'Gross Revenue' in agg_df.columns else 0
    total_requests = agg_df['Requests'].sum() if 'Requests' in agg_df.columns else 0
    flagged_count = (agg_df['Recommendation'] == "🚩 Block product at campaign level").sum()
    st.markdown(
        f"**Total Revenue:** ${total_revenue:,.0f}   "
        f"**Total Requests:** {int(total_requests):,}   "
        f"**Flagged Products:** {flagged_count}"
    )

    # Choose columns for display
    display_cols = group_cols + ['Requests', 'Gross Revenue']
    if avg_ivt_col:
        display_cols.append(avg_ivt_col)
    display_cols += [max_ivt_col, 'Recommendation', 'Check to Block']
    display_cols = [col for col in display_cols if col in agg_df.columns]

    # --- 9. Color Max IVT text in data_editor ---
    def color_text(val):
        try:
            num = int(str(val).replace('%', '').strip())
            if num >= ivt_threshold:
                return "color: red; font-weight: bold;"
            else:
                return "color: green; font-weight: bold;"
        except Exception:
            return ""

    # Show the single table with checkboxes and styled Max IVT column
    st.markdown("#### Recommendations Table")
    edited_df = st.data_editor(
        agg_df[display_cols],
        column_config={
            "Check to Block": st.column_config.CheckboxColumn(
                "Check to Block", help="Select products to block (demo only)"
            )
        },
        hide_index=True,
        use_container_width=True,
        key="ivt_editor"
    )

    # NOTE: As of now, st.data_editor doesn't support rich formatting on individual cell text.
    # If you want *in-table* coloring, you'd have to use st.dataframe + .style, but then you lose the checkbox.
    # For now: color logic can be in a legend, or show below.

    # --- Download and Block Buttons ---
    st.download_button(
        "Download Recommendations as CSV",
        edited_df[display_cols].to_csv(index=False),
        file_name="ivt_recommendations.csv",
        mime="text/csv"
    )
    if st.button("Block checked products (demo)"):
        checked = edited_df[edited_df['Check to Block']]
        st.success(f"Demo: {len(checked)} product-campaign(s) would be blocked.")

    from datetime import datetime
    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
