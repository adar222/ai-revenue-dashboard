import streamlit as st
import pandas as pd

def show_ivt_optimization():
    # Step 1: Check for main_df. If missing, prompt to upload
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
            st.stop()  # Stop here until a file is uploaded
    else:
        st.info("Using previously uploaded data. To reload, refresh the app or upload again in AI Insights tab.")

    # ---- THE REST OF YOUR IVT OPTIMIZATION CODE GOES HERE ----
    # For example, the user input/filtering code, etc.

    days = st.number_input("Show data for last...", min_value=1, max_value=60, value=7)
    ivt_threshold = st.number_input("IVT Threshold (%)", min_value=0, max_value=100, value=10)

    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        filtered_df = df[df['date'] >= (pd.Timestamp.today() - pd.Timedelta(days=days))]
    else:
        filtered_df = df.copy()

    st.write("Columns in your data:", list(filtered_df.columns))
    ivt_candidates = [col for col in filtered_df.columns if 'ivt' in col.lower() or 'invalid' in col.lower()]
    if ivt_candidates:
        ivt_col = ivt_candidates[0]
        st.success(f"Auto-selected IVT column: '{ivt_col}'")
    else:
        ivt_col = st.selectbox("Select IVT column", filtered_df.columns)

    if ivt_col not in filtered_df.columns:
        st.error(f"Column '{ivt_col}' not found in data. Please check your data.")
        return

    filtered_df = filtered_df[filtered_df[ivt_col] >= ivt_threshold]

    if filtered_df.empty:
        st.warning("No products found above the IVT threshold.")
        return

    rename_dict = {}
    if 'Product' in filtered_df.columns:
        rename_dict['Product'] = 'Product ID'
    if 'Pkg' in filtered_df.columns:
        rename_dict['Pkg'] = 'Package'
    if 'Campaign' in filtered_df.columns:
        rename_dict['Campaign'] = 'Campaign'
    rename_dict[ivt_col] = 'IVT %'

    rec_df = filtered_df.rename(columns=rename_dict)
    if 'IVT %' in rec_df.columns:
        rec_df['IVT %'] = rec_df['IVT %'].round(2)

    rec_df['Recommendation'] = rec_df['IVT %'].apply(
        lambda x: "🚩 Block at campaign level" if x >= ivt_threshold else "✅ No action"
    )

    display_cols = [col for col in ['Product ID', 'Package', 'Campaign', 'IVT %', 'Recommendation'] if col in rec_df.columns]
    rec_df = rec_df[display_cols]

    def highlight_ivt(val):
        try:
            color = 'red' if float(val) >= ivt_threshold else 'green'
        except Exception:
            color = 'white'
        return f'background-color: {color}; color: white'

    st.markdown("### 🏴 IVT Optimization Recommendations")
    st.dataframe(
        rec_df.style.applymap(highlight_ivt, subset=['IVT %']) if 'IVT %' in rec_df.columns else rec_df,
        use_container_width=True,
        hide_index=True
    )

    st.download_button(
        "Download Recommendations as CSV",
        rec_df.to_csv(index=False),
        file_name="ivt_recommendations.csv",
        mime="text/csv"
    )
