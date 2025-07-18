import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def show_pubimps():
    st.header("Pubimps/Advimps Discrepancy")

    df = st.session_state.get("main_df")
    if df is None or df.empty:
        st.warning("No data loaded. Please check your Excel file.")
        return

    # Use real column names
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

    # Calculations
    df['Impression Gap'] = df['Publisher Impressions'] - df['Advertiser Impressions']
    df['Margin'] = (df['Gross Revenue'] - df['Revenue cost']) / df['Gross Revenue']

    # Prepare and format top 10 for table
    df_top = df.sort_values('Impression Gap', ascending=False).head(10).copy()
    df_top['Publisher Impressions'] = df_top['Publisher Impressions'].apply(lambda x: f"{int(x):,}")
    df_top['Advertiser Impressions'] = df_top['Advertiser Impressions'].apply(lambda x: f"{int(x):,}")
    df_top['Gross Revenue'] = df_top['Gross Revenue'].apply(lambda x: f"{int(x):,}")
    df_top['Revenue cost'] = df_top['Revenue cost'].apply(lambda x: f"{int(x):,}")
    df_top['Impression Gap'] = df_top['Impression Gap'].apply(lambda x: f"{int(x):,}")
    df_top['Margin_display'] = df_top['Margin'].apply(lambda x: f"{x:.1%}")

    show_cols = [
        'Product', 'Campaign ID',
        'Publisher Impressions', 'Advertiser Impressions',
        'Gross Revenue', 'Revenue cost', 'Margin_display', 'Impression Gap'
    ]
    df_show = df_top[show_cols].rename(columns={'Margin_display': 'Margin'})

    # ---- Colorful table using pandas Styler ----
    def margin_color(val):
        try:
            margin_float = float(val.replace('%',''))
        except:
            margin_float = 0
        color = 'green' if margin_float >= 0 else 'red'
        return f'color: {color}; font-weight: bold'

    # For Streamlit > 1.27, use st.dataframe with styler directly
    styler = df_show.style.applymap(margin_color, subset=['Margin'])

    st.subheader("Top 10 Products by Impression Gap")
    st.dataframe(styler, use_container_width=True, hide_index=True)

    # ---- Plotly infographic with animation ----
    # We need numbers for plotting (not formatted)
    df_chart = df.sort_values('Impression Gap', ascending=False).head(10)
    fig = go.Figure(
        data=[go.Bar(
            x=df_chart['Product'],
            y=[0]*len(df_chart),
            marker_color='#2357f5'
        )]
    )
    fig.add_trace(go.Bar(
        x=df_chart['Product'],
        y=df_chart['Impression Gap'],
        marker_color='#2357f5'
    ))
    fig.update_layout(
        updatemenus=[
            dict(type="buttons", showactive=False, buttons=[
                dict(label="Play",
                     method="animate",
                     args=[None, {"frame": {"duration": 900, "redraw": True}, "fromcurrent": True}])
            ])
        ],
        title="Top 10 Products by Impression Gap",
        xaxis_title="Product",
        yaxis_title="Impression Gap",
        margin=dict(l=40, r=10, t=50, b=40),
        height=450
    )
    frames = [go.Frame(data=[go.Bar(
        x=df_chart['Product'],
        y=df_chart['Impression Gap'],
        marker_color='#2357f5'
    )])]
    fig.frames = frames

    st.plotly_chart(fig, use_container_width=True)
