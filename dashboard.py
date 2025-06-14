import streamlit as st
import pandas as pd
import numpy as np

def show_dashboard():
    st.title("📈 AI-Powered Revenue Action Center – Dashboard")

    uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])
    if not uploaded_file:
        st.info("Please upload an Excel file to view the dashboard.")
        return

    df = pd.read_excel(uploaded_file)
    df['Date'] = pd.to_datetime(df['Date'])

    dates = sorted(df['Date'].unique())
    if len(dates) < 6:
        st.warning("Need at least 6 days of data for 3d vs 3d comparison!")
        st.stop()

    last3d = dates[-3:]
    prev3d = dates[-6:-3]
    last_range = f"{last3d[0].strftime('%d/%m')}-{last3d[-1].strftime('%d/%m')}"
    prev_range = f"{prev3d[0].strftime('%d/%m')}-{prev3d[-1].strftime('%d/%m')}"

    def format_money(val):
        try:
            return f"${int(round(val)):,}"
        except:
            return ""

    merged = pd.merge(
        df[df['Date'].isin(last3d)].groupby('Package', as_index=False)['Gross Revenue'].sum().rename(columns={'Gross Revenue': f"Last 3d Revenue ({last_range})"}),
        df[df['Date'].isin(prev3d)].groupby('Package', as_index=False)['Gross Revenue'].sum().rename(columns={'Gross Revenue': f"Prev 3d Revenue ({prev_range})"}),
        how='outer', on='Package'
    ).fillna(0)

    merged['Δ Amount'] = merged[f"Last 3d Revenue ({last_range})"] - merged[f"Prev 3d Revenue ({prev_range})"]
    merged['% Change'] = np.where(
        merged[f"Prev 3d Revenue ({prev_range})"] > 0,
        (merged[f"Last 3d Revenue ({last_range})"] - merged[f"Prev 3d Revenue ({prev_range})"]) / merged[f"Prev 3d Revenue ({prev_range})"] * 100,
        100.0
    )
    merged = merged.sort_values(f"Last 3d Revenue ({last_range})", ascending=False).head(15)

    ac_table = merged[['Package', f"Last 3d Revenue ({last_range})", f"Prev 3d Revenue ({prev_range})", 'Δ Amount', '% Change']].copy()
    ac_table[f"Last 3d Revenue ({last_range})"] = ac_table[f"Last 3d Revenue ({last_range})"].apply(format_money)
    ac_table[f"Prev 3d Revenue ({prev_range})"] = ac_table[f"Prev 3d Revenue ({prev_range})"].apply(format_money)
    ac_table['Δ Amount'] = ac_table['Δ Amount'].apply(format_money)
    ac_table['% Change'] = ac_table['% Change'].apply(lambda x: f"{x:.0f}%")

    st.subheader("📊 Action Center: Top 15 Trending Packages")
    st.caption(f"(Last 3d: {last_range} vs Prev 3d: {prev_range})")
    st.dataframe(ac_table, use_container_width=True, hide_index=True)
