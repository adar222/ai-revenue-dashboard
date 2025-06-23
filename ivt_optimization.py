import streamlit as st
import pandas as pd

# --- Get main dataframe from session state ---
df = st.session_state.get('main_df')
if df is None or df.empty:
    st.info("No data found in main_df.")
    st.stop()

# --- User inputs ---
days = st.number_input("Show data for last...", min_value=1, max_value=60, value=7)
ivt_threshold = st.number_input("IVT Threshold (%)", min_value=0, max_value=100, value=10)

# --- Filter by date (if 'date' column exists) ---
if 'date' in df.columns:
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    filtered_df = df[df['date'] >= (pd.Timestamp.today() - pd.Timedelta(days=days))]
else:
    filtered_df = df.copy()

# --- Show columns for debug ---
st.write("Columns in your DataFrame:", list(filtered_df.columns))

# --- Find IVT column (try auto, else prompt) ---
ivt_candidates = [col for col in filtered_df.columns if 'ivt' in col.lower() or 'invalid' in col.lower()]
if ivt_candidates:
    ivt_col = ivt_candidates[0]
    st.success(f"Auto-selected IVT column: '{ivt_col}'")
else:
    ivt_col = st.selectbox(
        "Select IVT column (the one with IVT % values)",
        filtered_df.columns
    )

if ivt_col not in filtered_df.columns:
    st.error(f"Column '{ivt_col}' not found in data. Please check your data.")
    st.stop()

# --- Filter by IVT threshold ---
filtered_df = filtered_df[filtered_df[ivt_col] >= ivt_threshold]

if filtered_df.empty:
    st.warning("No products found above the IVT threshold.")
    st.stop()

# --- Prepare recommendations DataFrame ---
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

# Add recommendation column
rec_df['Recommendation'] = rec_df['IVT %'].apply(
    lambda x: "🚩 Block at campaign level" if x >= ivt_threshold else "✅ No action"
)

# Only keep relevant columns for display
display_cols = [col for col in ['Product ID', 'Package', 'Campaign', 'IVT %', 'Recommendation'] if col in rec_df.columns]
rec_df = rec_df[display_cols]

# --- Highlight IVT % column ---
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

# --- Download Button ---
st.download_button(
    "Download Recommendations as CSV",
    rec_df.to_csv(index=False),
    file_name="ivt_recommendations.csv",
    mime="text/csv"
)
