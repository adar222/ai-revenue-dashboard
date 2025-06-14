import streamlit as st
import pandas as pd
import numpy as np

def show_ai_insights():
    st.header("🧠 AI Insights — Top 15 Packages Revenue Trends")
    uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])
    if not uploaded_file:
        st.info("Please upload an Excel file to see AI insights.")
        return

    df = pd.read_excel(uploaded_file)
    if "Date" not in df.columns or "Package" not in df.columns or "Gross Revenue" not in df.columns:
        st.error("Excel must have at least columns: Date, Package, Gross Revenue")
        return

    df['Date'] = pd.to_datetime(df['Date'])
    dates = sorted(df['Date'].unique())
    if len(dates) < 6:
        st.warning("Need at least 6 days of data for 3d vs 3d AI insights.")
        return

    last3d = dates[-3:]
    prev3d = dates[-6:-3]
    last_range = f"{last3d[0].strftime('%d/%m')}-{last3d[-1].strftime('%d/%m')}"
    prev_range = f"{prev3d[0].strftime('%d/%m')}-{prev3d[-1].strftime('%d/%m')}"

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
    merged = merged.sort_values('Δ Amount', ascending=True).reset_index(drop=True)

    st.caption(f"(Last 3d: {last_range} vs Prev 3d: {prev_range})")
    st.markdown("---")

    # Show top 15 up/down with why bullets
    for idx, row in merged.tail(8).iterrows():
        pkg = row['Package']
        change = row['% Change']
        trend_icon = "🟢" if change > 0 else "🔴"

        # Show the main trend line
        st.markdown(f"""
**{trend_icon} {pkg}**
- **Revenue {'Up' if change > 0 else 'Down'} {abs(int(change)):,}%** (from {int(row[f'Prev 3d Revenue ({prev_range})'])} to {int(row[f'Last 3d Revenue ({last_range})'])})
""")
        # AI-style bullet points: Add more here as you add data fields (CPM, Fill Rate, IVT, etc)
        last_data = df[(df['Package'] == pkg) & (df['Date'].isin(last3d))]
        prev_data = df[(df['Package'] == pkg) & (df['Date'].isin(prev3d))]

        bullets = []

        for metric in ["CPM", "Fill Rate", "IVT (%)", "Margin (%)"]:
            if metric in last_data.columns:
                last_val = last_data[metric].mean()
                prev_val = prev_data[metric].mean()
                if not np.isnan(last_val) and not np.isnan(prev_val):
                    pct = ((last_val - prev_val) / prev_val * 100) if prev_val else 0
                    if abs(pct) > 7:  # show only significant moves
                        icon = "🟢" if pct > 0 else "🔴"
                        name = metric.replace(" (%)", "")
                        bullets.append(f"{icon} {name} {'up' if pct>0 else 'down'} {abs(int(pct))}%")

        if not bullets:
            bullets.append("No significant metric change detected.")

        for b in bullets:
            st.markdown(f"  - {b}")

        st.markdown("---")
