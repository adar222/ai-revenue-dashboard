import streamlit as st
import pandas as pd
import numpy as np

def guess_column(df, options, default=None):
    """Find a column in df that matches any of the substrings in options."""
    for option in options:
        for col in df.columns:
            if option.lower() in col.lower():
                return col
    return default

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

    # --- 2. Dynamically guess/ask for columns ---
    date_col = guess_column(df, ["date"])
    request_col = guess_column(df, ["request", "impression", "req"])
    revenue_col = guess_column(df, ["gross revenue", "revenue", "amount", "total"])
    ivt_candidates = [col for col in df.columns if "ivt" in col.lower() or "invalid" in col.lower()]

    with st.expander("Column Selection (adjust if needed):"):
        date_col = st.selectbox("Date column:", df.columns, index=df.columns.get_loc(date_col) if date_col else 0)
        request_col = st.selectbox("Requests column:", df.columns, index=df.columns.get_loc(request_col) if request_col else 0)
        revenue_col = st.selectbox("Revenue column:", df.columns, index=df.columns.get_loc(revenue_col) if revenue_col else 0)
        if len(ivt_candidates) > 1:
            ivt_col = st.selectbox("IVT column:", ivt_candidates)
        elif len(ivt_candidates) == 1:
            ivt_col = ivt_candidates[0]
        else:
            ivt_col = st.selectbox("IVT column:", df.columns)

    # Grouping columns: auto, but allow change
    group_cols_possible = ["Product", "Package", "Campaign ID", "Campaign", "Ad Group", "Site"]
    group_cols = [col for col in group_cols_possible if col in df.columns]
    if not group_cols:
        group_cols = st.multiselect("Columns to group by (at least one required):", df.columns, default=[df.columns[0]])
    else:
        st.markdown(f"**Grouping by:** {', '.join(group_cols)}")

    # --- 3. Filter by date ---
    try:
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    except Exception:
        st.error(f"Date conversion failed for column {date_col}.")
        st.stop()

    days = st.number_input("Show data for last... days", min_value=1, max_value=60, value=3)
    end_date = df[date_col].max()
    start_date = end_date - pd.Timedelta(days=days-1)
    filtered_df = df[(df[date_col] >= start_date) & (df[date_col] <= end_date)]

    if filtered_df.empty:
        st.info("No data in the selected date range.")
        st.stop()

    # --- 4. Aggregate ---
    agg_dict = {
        request_col: "sum",
        revenue_col: "sum",
        ivt_col: ["mean", "max"]
    }
    group_cols = [col for col in group_cols if col in filtered_df.columns]

    try:
        agg_df = filtered_df.groupby(group_cols, dropna=False).agg(agg_dict)
    except Exception as e:
        st.error(f"Aggregation error: {e}")
        st.write("Group columns:", group_cols)
        st.write("Aggregation dict:", agg_dict)
        st.stop()

    # --- 5. Flatten columns and dynamically get new column names ---
    def flatten_col(col):
        if isinstance(col, tuple):
            if col[1] == "":
                return col[0]
            elif col[1] == "mean":
                return "Avg IVT"
            elif col[1] == "max":
                return "Max IVT"
            else:
                return f"{col[0]} {col[1]}"
        return col
    agg_df.columns = [flatten_col(c) for c in agg_df.columns]
    agg_df = agg_df.reset_index()

    # Dynamically find the columns after aggregation
    req_col_agg = next((c for c in agg_df.columns if "request" in c.lower() or "impression" in c.lower() or "req" in c.lower()), None)
    rev_col_agg = next((c for c in agg_df.columns if "revenue" in c.lower() or "amount" in c.lower() or "total" in c.lower()), None)
    avg_ivt_col = next((c for c in agg_df.columns if "avg" in c.lower() and "ivt" in c.lower()), None)
    max_ivt_col = next((c for c in agg_df.columns if "max" in c.lower() and "ivt" in c.lower()), None)

    if not req_col_agg or not rev_col_agg or not max_ivt_col:
        st.error("Could not auto-detect your Requests, Revenue, or Max IVT column after aggregation. Please check your column selection and try again.")
        st.stop()

    # --- 6. Format and calculate logic columns ---
    if avg_ivt_col:
        agg_df[avg_ivt_col + " Numeric"] = agg_df[avg_ivt_col]
        agg_df[avg_ivt_col] = agg_df[avg_ivt_col].round(0).astype('Int64').astype(str) + "%"
    agg_df[max_ivt_col + " Numeric"] = agg_df[max_ivt_col]
    agg_df[max_ivt_col] = agg_df[max_ivt_col].round(0).astype('Int64').astype(str) + "%"

    # Recommendation logic
    ivt_threshold = st.number_input("IVT Threshold (%)", min_value=0, max_value=100, value=10)
    agg_df["Recommendation"] = np.where(
        agg_df[max_ivt_col + " Numeric"] >= ivt_threshold,
        "🚩 Block product at campaign level",
        "No action"
    )

    # --- 7. Always keep numeric columns for calculations ---
    agg_df[rev_col_agg + " Numeric"] = pd.to_numeric(agg_df[rev_col_agg], errors="coerce").fillna(0)
    agg_df[rev_col_agg] = agg_df[rev_col_agg + " Numeric"].apply(lambda x: f"${int(round(x, 0)):,}")
    agg_df[req_col_agg + " Numeric"] = pd.to_numeric(agg_df[req_col_agg], errors="coerce").fillna(0)

    # Add "Check to Block" column (for demo, default False)
    agg_df['Check to Block'] = False

    # --- 8. CALCULATE COUNTERS before dropping cols! ---
    total_revenue = agg_df[rev_col_agg + " Numeric"].sum()
    total_requests = agg_df[req_col_agg + " Numeric"].sum()
    flagged_count = (agg_df['Recommendation'] == "🚩 Block product at campaign level").sum()

    st.markdown(
        f"**Data aggregated by {', '.join(group_cols)}**  \n"
        f"**Period:** {start_date.date()} – {end_date.date()}"
    )
    st.markdown(
        f"**Total Revenue:** ${total_revenue:,.0f}   "
        f"**Total Requests:** {int(total_requests):,}   "
        f"**Flagged Products:** {flagged_count}"
    )

    # --- 9. Display Table ---
    display_cols = group_cols + [req_col_agg, rev_col_agg]
    if avg_ivt_col:
        display_cols.append(avg_ivt_col)
    display_cols += [max_ivt_col, "Recommendation", "Check to Block"]
    display_cols = [col for col in display_cols if col in agg_df.columns]

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

# Uncomment to run standalone for testing:
# if __name__ == "__main__":
#     show_ivt_optimization()
