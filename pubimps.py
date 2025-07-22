import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

def show_pubimps():
    st.set_page_config(layout="wide")
    st.markdown("<h2 style='display: flex; align-items: center;'>🔍 Pubimps/Advimps Discrepancy</h2>", unsafe_allow_html=True)
    st.caption("Analyze publisher and advertiser impression gaps and quickly spot products that are losing money.")

    df = st.session_state.get("main_df")
    if df is None or df.empty:
        st.warning("No data loaded. Please check your Excel file.")
        return

    # --- Calculated Columns ---
    df = df.copy()
    df["Impression Gap"] = df["Publisher Impressions"] - df["Advertiser Impressions"]
    df["Margin"] = (df["Gross Revenue"] - df["Revenue cost"]) / df["Gross Revenue"]
    df["Margin_pct"] = df["Margin"].apply(lambda x: f"{x:.1%}")
    df["Margin_style"] = df["Margin"].apply(lambda x: "color:red;font-weight:bold" if x < 0 else "color:green;font-weight:bold")

    # --- AI Insights Panel ---
    top_loss = df.loc[df["Margin"] < 0].sort_values("Gross Revenue", ascending=False).head(1)
    total_loss = df.loc[df["Margin"] < 0, "Gross Revenue"].sum() - df.loc[df["Margin"] < 0, "Revenue cost"].sum()
    loss_products = df.loc[df["Margin"] < 0, "Product"].tolist()

    with st.expander("🤖 AI Highlights & Actions", expanded=True):
        st.markdown("**Quick Insights:**")
        if len(top_loss):
            row = top_loss.iloc[0]
            st.write(f"- 🚩 **Highest Loss Product:** `{int(row['Product'])}` is losing **${int(row['Revenue cost'] - row['Gross Revenue']):,}** (margin: {row['Margin_pct']})")
        st.write(f"- 💰 **Total Loss from Negative Margin Products:** <span style='color:red;font-size:1.3em;font-weight:bold;'>-${abs(int(total_loss)):,}</span>", unsafe_allow_html=True)
        st.write(f"- ✅ **Action:** Select & block products below with negative margin to reduce loss.")

    st.divider()

    # --- Sidebar/Top Filters ---
    with st.container():
        col1, col2, col3 = st.columns(3)
        with col1:
            campaign = st.selectbox("Filter by Campaign", ["All"] + sorted(df["Campaign ID"].astype(str).unique()))
        with col2:
            margin_cut = st.slider("Margin Max Threshold", min_value=-1.0, max_value=1.0, value=-0.01, step=0.01)
        with col3:
            search = st.text_input("Product Search (ID)")

    # --- Filtered Data ---
    filtered = df.copy()
    if campaign != "All":
        filtered = filtered[filtered["Campaign ID"].astype(str) == campaign]
    filtered = filtered[filtered["Margin"] <= margin_cut]
    if search.strip():
        filtered = filtered[filtered["Product"].astype(str).str.contains(search.strip())]

    # --- Table of All Products (sortable) ---
    st.subheader("All Products - Sort & Filter")
    st.dataframe(
        filtered[
            ["Product", "Campaign ID", "Publisher Impressions", "Advertiser Impressions", "Gross Revenue", "Revenue cost", "Margin_pct", "Impression Gap"]
        ].rename(columns={"Margin_pct": "Margin (%)"}),
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    # --- Negative Margin Products Table with Select-to-Block ---
    st.subheader("Products with Negative Margin")
    st.caption("Below are products where the margin is negative. Select rows to block.")

    df_neg = df[df["Margin"] < 0].copy()
    if df_neg.empty:
        st.success("No negative margin products found. Good job! 👍")
        return

    # --- AG Grid with checkbox selection ---
    gb = GridOptionsBuilder.from_dataframe(
        df_neg[
            ["Product", "Campaign ID", "Publisher Impressions", "Advertiser Impressions", "Gross Revenue", "Revenue cost", "Margin_pct", "Impression Gap"]
        ].rename(columns={"Margin_pct": "Margin (%)"})
    )
    gb.configure_selection('multiple', use_checkbox=True)
    grid_options = gb.build()

    grid_response = AgGrid(
        df_neg[
            ["Product", "Campaign ID", "Publisher Impressions", "Advertiser Impressions", "Gross Revenue", "Revenue cost", "Margin_pct", "Impression Gap"]
        ].rename(columns={"Margin_pct": "Margin (%)"}),
        gridOptions=grid_options,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        fit_columns_on_grid_load=True,
        height=350,
        theme="streamlit",
    )

    # --- Defensive selection ---
    selected = grid_response.get('selected_rows')
    if selected is None:
        selected = []

    selected_ids = [str(x['Product']) for x in selected if isinstance(x, dict) and 'Product' in x and x['Product'] not in [None, ""]]

    if st.button("Block Selected (demo)", use_container_width=True):
        if selected_ids:
            st.success(f"✅ These products would now be flagged for blocking (demo mode). Product IDs: {', '.join(selected_ids)}")
        else:
            st.info("Please select at least one product above to block.")

    st.caption("Tip: Use filters above to find the biggest negative margin leaks!")
