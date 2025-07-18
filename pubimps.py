import streamlit as st
import pandas as pd

def show_pubimps():
    st.header("Pubimps/Advimps Discrepancy")

    df = st.session_state.get("main_df")
    if df is None or df.empty:
        st.warning("No data loaded. Please check your Excel file.")
        return

    required_cols = [
        'Product', 'Campaign ID',
        'Advertiser Impressions', 'Publisher Impressions',
        'Gross Revenue', 'Revenue cost'
    ]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        st.warning(f"Missing columns in data: {', '.join(missing_cols)}")
        st.dataframe(df.head())
        return

    # Calculate columns
    df = df.copy()
    df[['Gross Revenue', 'Revenue cost']] = df[['Gross Revenue', 'Revenue cost']].fillna(0)
    df['Impression Gap'] = df['Publisher Impressions'] - df['Advertiser Impressions']
    df['Margin'] = df.apply(
        lambda row: (row['Gross Revenue'] - row['Revenue cost']) / row['Gross Revenue'] if row['Gross Revenue'] else 0,
        axis=1
    )

    # Format for display
    df['Publisher Impressions_fmt'] = df['Publisher Impressions'].apply(lambda x: f"{int(x):,}")
    df['Advertiser Impressions_fmt'] = df['Advertiser Impressions'].apply(lambda x: f"{int(x):,}")
    df['Gross Revenue_fmt'] = df['Gross Revenue'].apply(lambda x: f"{int(x):,}")
    df['Revenue cost_fmt'] = df['Revenue cost'].apply(lambda x: f"{int(x):,}")
    df['Impression Gap_fmt'] = df['Impression Gap'].apply(lambda x: f"{int(x):,}")
    df['Margin_fmt'] = df['Margin'].apply(lambda x: f"{x:.1%}")

    show_cols = [
        'Product', 'Campaign ID',
        'Publisher Impressions_fmt', 'Advertiser Impressions_fmt',
        'Gross Revenue_fmt', 'Revenue cost_fmt', 'Margin_fmt', 'Impression Gap_fmt'
    ]
    df_show = df[show_cols].rename(columns={
        'Publisher Impressions_fmt': 'Publisher Impressions',
        'Advertiser Impressions_fmt': 'Advertiser Impressions',
        'Gross Revenue_fmt': 'Gross Revenue',
        'Revenue cost_fmt': 'Revenue cost',
        'Margin_fmt': 'Margin',
        'Impression Gap_fmt': 'Impression Gap'
    })

    # Color margin column
    def margin_color(val):
        try:
            margin_float = float(val.replace('%',''))
        except:
            margin_float = 0
        color = 'green' if margin_float >= 0 else 'red'
        return f'color: {color}; font-weight: bold'
    styler = df_show.style.applymap(margin_color, subset=['Margin'])

    st.subheader("All Products - Sort by Any Column")
    st.write(styler)

    # --- Negative margin table ---
    df_neg = df[df['Margin'] < 0].copy()
    if not df_neg.empty:
        df_neg['Publisher Impressions_fmt'] = df_neg['Publisher Impressions'].apply(lambda x: f"{int(x):,}")
        df_neg['Advertiser Impressions_fmt'] = df_neg['Advertiser Impressions'].apply(lambda x: f"{int(x):,}")
        df_neg['Gross Revenue_fmt'] = df_neg['Gross Revenue'].apply(lambda x: f"{int(x):,}")
        df_neg['Revenue cost_fmt'] = df_neg['Revenue cost'].apply(lambda x: f"{int(x):,}")
        df_neg['Impression Gap_fmt'] = df_neg['Impression Gap'].apply(lambda x: f"{int(x):,}")
        df_neg['Margin_fmt'] = df_neg['Margin'].apply(lambda x: f"{x:.1%}")

        df_neg_show = df_neg[show_cols].rename(columns={
            'Publisher Impressions_fmt': 'Publisher Impressions',
            'Advertiser Impressions_fmt': 'Advertiser Impressions',
            'Gross Revenue_fmt': 'Gross Revenue',
            'Revenue cost_fmt': 'Revenue cost',
            'Margin_fmt': 'Margin',
            'Impression Gap_fmt': 'Impression Gap'
        })

        neg_styler = df_neg_show.style.applymap(margin_color, subset=['Margin'])

        st.subheader("Products with Negative Margin")
        st.write(neg_styler)

        # --- Summary: Total Loss ---
        df_neg['Loss'] = df_neg['Gross Revenue'] - df_neg['Revenue cost']
        total_loss = df_neg['Loss'].sum()
        st.markdown(
            f"<div style='font-size:22px;color:red;font-weight:bold;'>Total Loss from Negative Margin Products: ${total_loss:,.0f}</div>",
            unsafe_allow_html=True
        )
    else:
        st.info("No products with negative margin found.")

    # Download negative margin products CSV
    st.subheader("Download Negative Margin Products")
    st.download_button(
        "Download CSV",
        data=df_neg.to_csv(index=False),
        file_name="negative_margin_products.csv",
        mime="text/csv"
    )
