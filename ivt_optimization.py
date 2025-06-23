import streamlit as st
import pandas as pd
import numpy as np

def show_ivt_optimization():
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

    # Only use columns that exist
    group_cols = [col for col in group_cols if col in filtered_df.columns]

    try:
        agg_df = filtered_df.groupby(group_cols, dropna=False).agg(agg_dict)
    except Exception as e:
        st.error(f"Aggregation error: {e}")
        st.write("Group columns:", group_cols)
        st.write("Aggregation dict:", agg_dict)
        st.stop()

    # Flatten multiindex columns if needed
    agg_df.columns = [
        "Requests" if c[0] == 'Requests' else
        "Gross Revenue" if c[0] == 'Gross Revenue' else
        "Avg IVT (%)" if c[1] == 'mean' else
        "Max IVT (%)" if c[1] == 'max' else
        c[0]
        for c in agg_df.columns
    ]
    agg_df = agg_df.reset_index()

    # --- 6. Recommendation column ---
    if 'Max IVT (%)' not in agg_df.columns:
        st.error(f"'Max IVT (%)' column missing after aggregation! Columns: {agg_df.columns.tolist()}")
        st.stop()
    agg_df['Recommendation'] = np.where(
        agg_df['Max IVT (%)'] >= ivt_threshold,
        "🚩 Block at campaign level",
        "✅ No action"
    )
    if 'Avg IVT (%)' in agg_df.columns:
        agg_df['Avg IVT (%)'] = agg_df['Avg IVT (%)'].round(2)
    agg_df['Max IVT (%)'] = agg_df['Max IVT (%)'].round(2)

    # --- 7. Table display ---
    st.markdown("### 🏴 IVT Optimization Recommendations")
    st.markdown(
        f"**Data aggregated by Product, Package, Campaign ID, and Campaign**  \n"
        f"**Period:** {start_date.date()} – {end_date.date()}"
    )

    display_cols = group_cols + ['Requests', 'Gross Revenue', 'Avg IVT (%)', 'Max IVT (%)', 'Recommendation']
    display_cols = [col for col in display_cols if col in agg_df.columns]

    def highlight_ivt(val):
        try:
            color = 'red' if float(val) >= ivt_threshold else 'green'
        except:
            color = 'white'
        return f'background-color: {color}; color: white'

    if not agg_df.empty:
        st.dataframe(
            agg_df.style.applymap(highlight_ivt, subset=['Max IVT (%)']),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No product-campaigns above the selected IVT threshold in this period.")

    # --- 8. Download ---
    st.download_button(
        "Download Recommendations as CSV",
        agg_df[display_cols].to_csv(index=False),
        file_name="ivt_recommendations.csv",
        mime="text/csv"
    )
