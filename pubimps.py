import streamlit as st
import pandas as pd
import plotly.graph_objects as go

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

    # Table (unchanged)
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

    # --- Margin Bar Chart (only negative margin products, top 10 by Gross Revenue) ---
    df_neg = df[df['Margin'] < 0].sort_values('Gross Revenue', ascending=False).head(10)
    if not df_neg.empty:
        df_neg = df_neg.copy()
        # Force Product to string so Plotly shows full ID, not 3M/4M etc
        df_neg['Product'] = df_neg['Product'].astype(str)
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df_neg['Product'],
            y=df_neg['Margin'] * 100,  # Margin in percent
            marker_color='red',
            text=[f"{x:.1%}" for x in df_neg['Margin']],
            textposition='outside',
            # Make each bar the same width for categorical data
            width=[0.6 for _ in range(len(df_neg))],
            hovertemplate=(
                "Product: %{x}<br>Margin: %{y:.1f}%<br>Gross Revenue: $%{customdata:,}<extra></extra>"
            ),
            customdata=df_neg['Gross Revenue'],
        ))

        fig.update_layout(
            title="Top 10 Products with Negative Margin (%) by Gross Revenue",
            xaxis_title="Product",
            yaxis_title="Margin (%)",
            yaxis=dict(tickformat=".0f", showgrid=True),
            xaxis=dict(tickangle=-35, tickformat="none"),  # tickformat="none" disables 3M/4M abbreviations
            margin=dict(l=60, r=10, t=50, b=80),
            height=500,
            bargap=0.05,  # Reduce gap to make bars thicker
        )

        st.plotly_chart(fig, use_container_width=True)
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
