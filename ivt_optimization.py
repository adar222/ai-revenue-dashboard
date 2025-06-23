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

# --- Filter by date (assuming 'date' column exists, otherwise skip this part) ---
if 'date' in df.columns:
    df['date'] = pd.to_datetime(df['date'])
    filtered_df = df[df['date'] >= (pd.Timestamp.today() - pd.Timedelta(days=days))]
else:
    filtered_df = df.copy()

# --- Print columns for debugging ---
st.write("Columns in your DataFrame:", list(filtered_df.columns))

# Try to auto-detect IVT column (case-insensitive)
ivt_candidates = [col for col in filtered_df.columns if 'ivt' in col.lower() or 'invalid' in col.lower()]
if ivt_candidates:
    ivt_col = ivt_candidates[0]  # Take the first match
else:
    ivt_col = st.selectbox(
        "Select IVT column",
        filtered_df.columns,
        help="Which column represents IVT %?"
    )

# --- Now continue filtering by IVT threshold ---
if ivt_col not in filtered_df.columns:
    st.error(f"Column '{ivt_col}' not found in data. Please check your data.")
    st.stop()

filtered_df = filtered_df[filtered_df[ivt_col] >= ivt_threshold]

# --- Prepare recommendations DataFrame ---
rec_df = filtered_df.copy()
rec_df = rec_df.rename(
    columns={
        'Product': 'Product ID',
        'Pkg': 'Package',
        'Campaign': 'Campaign',
        ivt_col: 'IVT %'
    }
)
# Add recommendation column
rec_df['Recommendation'] = rec_df['IVT %'].apply(
    lambda x: "🚩 Block at campaign level" if x >= ivt_threshold else "✅ No action"
)

# Only keep relevant columns for display
display_cols = ['Product ID', 'Package', 'Campaign', 'IVT %', 'Recommendation']
rec_df = rec_df[display_cols]

# --- Highlight IVT % column ---
def highlight_ivt(val):
    color = 'red' if val >= ivt_threshold else 'green'
    return f'background-color: {color}; color: white'

st.markdown("### 🏴 IVT Optimization Recommendations")

st.dataframe(
    rec_df.style.applymap(highlight_ivt, subset=['IVT %']),
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
