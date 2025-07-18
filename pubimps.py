import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def show_pubimps():
    st.header("Pubimps/Advimps Discrepancy")

    df = st.session_state.get("main_df")
    if df is None or df.empty:
        st.warning("No data loaded. Please check your Excel file.")
        return

    # Match Excel column names
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

    # Copy and calculate columns
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

    # Color margin column (Styler only works in st.write/st.table in most Streamlit versions)
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

    # --- Infographic: Top 10 negative impression gap (Publisher > Advertiser) ---
    df_neg = df[df['Impression Gap'] < 0].sort_values('Impression Gap').head(10)
    if not df_neg.empty:
        fig = go.Figure(data=[go.Bar(
            x=df_neg['Product'],
            y=df_neg['Impression Gap'],
            marker_color='red'
        )])
        fig.update_layout(
            title="Top 10 Products by Negative Impression Gap",
            xaxis_title="Product",
            yaxis_title="Impression Gap",
            margin=dict(l=40, r=10, t=50, b=40),
            height=450
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No products with negative Impression Gap found.")
