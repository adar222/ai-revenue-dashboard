import streamlit as st
import pandas as pd

def show_pubimps():
    # --- Header with icon and description ---
    st.markdown(
        "<h1 style='font-size:2.5rem; font-weight:900; display:flex; align-items:center; gap:0.6rem;'>"
        "🔍 Pubimps/Advimps Discrepancy"
        "</h1>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<div style='font-size:1.1rem; color:#656565; margin-bottom:1.2em;'>"
        "Analyze publisher and advertiser impression gaps and quickly spot products that are losing money."
        "</div>",
        unsafe_allow_html=True
    )

    df = st.session_state.get("main_df")
    if df is None or df.empty:
        st.warning("No data loaded. Please check your Excel file.")
        return

    # -- Data Preparation --
    df = df.copy()
    # (rename columns for safety if needed)
    # --- Calculations
    df['Impression Gap'] = df['Publisher Impressions'] - df['Advertiser Impressions']
    df['Margin'] = (df['Gross Revenue'] - df['Revenue cost']) / df['Gross Revenue']
    df['Margin_display'] = df['Margin'].apply(lambda x: f"{x:.1%}")
    df['Margin_color'] = df['Margin'].apply(lambda x: 'green' if x >= 0 else 'red')

    # --- Table 1: All Products ---
    st.markdown("### All Products - Sort by Any Column")
    all_cols = ['Product', 'Campaign ID', 'Publisher Impressions', 'Advertiser Impressions', 'Gross Revenue', 'Revenue cost', 'Margin_display', 'Impression Gap']
    df_show = df[all_cols].rename(columns={'Margin_display': 'Margin'})

    # Format with thousands separators
    for col in ['Publisher Impressions', 'Advertiser Impressions', 'Gross Revenue', 'Revenue cost', 'Impression Gap']:
        df_show[col] = df_show[col].apply(lambda x: f"{int(x):,}")

    def highlight_margin(val):
        color = 'green' if '%' in str(val) and not '-' in str(val) else 'red' if '%' in str(val) and '-' in str(val) else 'inherit'
        return f"color:{color}; font-weight:700"

    st.dataframe(
        df_show.style.applymap(highlight_margin, subset=['Margin']),
        use_container_width=True,
        hide_index=True
    )

    # --- Table 2: Negative Margin Products with Checkboxes ---
    st.markdown("### Products with Negative Margin")

    neg_df = df[df['Margin'] < 0].copy()
    neg_df = neg_df.reset_index(drop=True)

    # Add a selection column to session_state to persist checked boxes
    if 'pubimps_to_block' not in st.session_state or len(st.session_state['pubimps_to_block']) != len(neg_df):
        st.session_state['pubimps_to_block'] = [False] * len(neg_df)

    # Render the table with checkboxes
    cols = st.columns([0.1, 1, 1, 1, 1, 1, 1, 1, 1])  # First col for checkbox

    header = ["Check to Block", "Product", "Campaign ID", "Publisher Impressions", "Advertiser Impressions", "Gross Revenue", "Revenue cost", "Margin", "Impression Gap"]
    for i, h in enumerate(header):
        cols[i].markdown(f"**{h}**")

    # Table rows with checkboxes
    for idx, row in neg_df.iterrows():
        # Style the margin red
        margin_str = f"<span style='color:red;font-weight:700'>{row['Margin_display']}</span>"
        row_display = [
            st.session_state['pubimps_to_block'][idx],
            f"{row['Product']}",
            f"{row['Campaign ID']}",
            f"{int(row['Publisher Impressions']):,}",
            f"{int(row['Advertiser Impressions']):,}",
            f"{int(row['Gross Revenue']):,}",
            f"{int(row['Revenue cost']):,}",
            margin_str,
            f"{int(row['Impression Gap']):,}",
        ]
        # Checkbox in first col, others in next
        checked = cols[0].checkbox("", value=st.session_state['pubimps_to_block'][idx], key=f"block_pubimps_{idx}")
        st.session_state['pubimps_to_block'][idx] = checked
        for i in range(1, len(header)):
            if i == 7:
                cols[i].markdown(margin_str, unsafe_allow_html=True)
            else:
                cols[i].write(row_display[i])

    # --- Block Selected Button ---
    checked_rows = [i for i, checked in enumerate(st.session_state['pubimps_to_block']) if checked]
    if st.button("Block Selected"):
        if checked_rows:
            blocked_products = neg_df.iloc[checked_rows]['Product'].tolist()
            st.success(f"Blocked {len(blocked_products)} product(s): {', '.join(map(str, blocked_products))}")
        else:
            st.info("No products selected.")

