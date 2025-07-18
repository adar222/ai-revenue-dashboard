from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import streamlit as st
import pandas as pd

# ---- Example Data ----
df_neg = pd.DataFrame({
    "Product": [4612365, 7273233, 2571945],
    "Campaign ID": [595849191, 65568446685, 595849191],
    "Publisher Impressions": [44843, 185098, 9359],
    "Advertiser Impressions": [46999, 185794, 9378],
    "Gross Revenue": [94, 107, 105],
    "Revenue cost": [103, 146, 136],
    "Margin": [-9.3, -35.4, -28.9],
    "Impression Gap": [-2156, -696, -19]
})

# ---- Short Description ----
st.header("🔍 Products with Negative Margin")
st.caption(
    "Below are products where the margin is negative. You can select products to block by checking the box in the first column."
)

# ---- Configure AgGrid ----
gb = GridOptionsBuilder.from_dataframe(df_neg)
gb.configure_selection(
    'multiple',
    use_checkbox=True
)
# Format columns
gb.configure_column("Margin", type=["numericColumn"], cellStyle=lambda x: {"color": "red" if x < 0 else "green"})
grid_options = gb.build()

# ---- Display AgGrid Table ----
grid_response = AgGrid(
    df_neg,
    gridOptions=grid_options,
    update_mode=GridUpdateMode.SELECTION_CHANGED,
    fit_columns_on_grid_load=True,
    allow_unsafe_jscode=True,
    height=350
)

selected_rows = grid_response['selected_rows']
if selected_rows:
    st.success(f"Block Selected: {len(selected_rows)}")
    st.write(pd.DataFrame(selected_rows))
