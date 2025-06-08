import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(layout="wide")
st.title("📈 AI-Powered Revenue Action Center")

# --- Upload Section ---
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])
if not uploaded_file:
    st.stop()

df = pd.read_excel(uploaded_file)
df['Date'] = pd.to_datetime(df['Date'])

# --- Get sorted date array ---
dates = sorted(df['Date'].unique())
if len(dates) < 6:
    st.warning("Need at least 6 days of data for 3d vs 3d comparison!")
    st.stop()

last3d = dates[-3:]
prev3d = dates[-6:-3]

# --- Formatters ---
def format_money(val):
    return f"${int(round(val))}"

def realtime_status(change):
    if -15 <= change <= 40:
        return "🟢 Safe"
    elif -40 <= change < -15 or 40 < change <= 100:
        return "🟡 Needs Review"
    else:
        return "🔴 Critical"

# --- Trending Table: Per Package Only, With Date Ranges and Realtime Status ---
last_range = f"{last3d[0].strftime('%d/%m')}-{last3d[-1].strftime('%d/%m')}"
prev_range = f"{prev3d[0].strftime('%d/%m')}-{prev3d[-1].strftime('%d/%m')}"

def agg_3d_simple(period, label):
    return (
        df[df['Date'].isin(period)]
        .groupby('Package', as_index=False)['Gross Revenue']
        .sum()
        .rename(columns={'Gross Revenue': label})
    )

last_agg = agg_3d_simple(last3d, f"Last 3d Revenue ({last_range})")
prev_agg = agg_3d_simple(prev3d, f"Prev 3d Revenue ({prev_range})")
merged = pd.merge(
    last_agg, prev_agg, how='outer', on='Package'
).fillna(0)
merged['Δ Amount'] = merged[f"Last 3d Revenue ({last_range})"] - merged[f"Prev 3d Revenue ({prev_range})"]
merged['% Change'] = np.where(
    merged[f"Prev 3d Revenue ({prev_range})"] > 0,
    (merged[f"Last 3d Revenue ({last_range})"] - merged[f"Prev 3d Revenue ({prev_range})"]) / merged[f"Prev 3d Revenue ({prev_range})"] * 100,
    100.0
)
merged['Status'] = merged['% Change'].apply(realtime_status)
merged = merged.sort_values(f"Last 3d Revenue ({last_range})", ascending=False).head(10)

ac_table = merged[['Package', f"Last 3d Revenue ({last_range})", f"Prev 3d Revenue ({prev_range})", 'Δ Amount', '% Change', 'Status']].copy()
ac_table[f"Last 3d Revenue ({last_range})"] = ac_table[f"Last 3d Revenue ({last_range})"].apply(format_money)
ac_table[f"Prev 3d Revenue ({prev_range})"] = ac_table[f"Prev 3d Revenue ({prev_range})"].apply(format_money)
ac_table['Δ Amount'] = ac_table['Δ Amount'].apply(format_money)
ac_table['% Change'] = ac_table['% Change'].apply(lambda x: f"{x:.0f}%")

st.subheader("📊 Action Center: Top 10 Trending Packages")
st.caption(f"(Last 3d: {last_range} vs Prev 3d: {prev_range})")
st.dataframe(ac_table, use_container_width=True, hide_index=True)

# --- IVT & Margin Alert (Last Day) ---
latest_date = dates[-1]
df_latest = df[df['Date'] == latest_date].copy()
st.subheader(f"🛡️ IVT & Margin Alert (Last Day: {latest_date.strftime('%d/%m')})")

# a) Top 5 grossing
ivt_margin = df_latest.sort_values('Gross Revenue', ascending=False).head(5).copy()
ivt_margin['Alert'] = np.where(ivt_margin['Margin (%)'] < 25, '❗ Low Margin',
                       np.where(ivt_margin['IVT (%)'] > 15, '⚠️ High IVT', '✅ OK'))
ivt_margin_table = ivt_margin[['Package', 'Gross Revenue', 'IVT (%)', 'Margin (%)', 'Alert']].copy()
ivt_margin_table['Gross Revenue'] = ivt_margin_table['Gross Revenue'].apply(format_money)
st.markdown("**a) Top 5 Grossing Packages:**")
st.dataframe(ivt_margin_table, use_container_width=True, hide_index=True)

# b) Highest IVT for packages over $100
ivt_over_100 = df_latest[df_latest['Gross Revenue'] > 100].sort_values('IVT (%)', ascending=False).head(5).copy()
ivt_over_100['Alert'] = np.where(ivt_over_100['Margin (%)'] < 25, '❗ Low Margin',
                        np.where(ivt_over_100['IVT (%)'] > 15, '⚠️ High IVT', '✅ OK'))
ivt_over_100_table = ivt_over_100[['Package', 'Gross Revenue', 'IVT (%)', 'Margin (%)', 'Alert']].copy()
ivt_over_100_table['Gross Revenue'] = ivt_over_100_table['Gross Revenue'].apply(format_money)
st.markdown("**b) Highest IVT for Packages Over $100:**")
st.dataframe(ivt_over_100_table, use_container_width=True, hide_index=True)

# --- New Package Alert (over $100, first time seen) ---
seen_before = set(df[df['Date'] < latest_date]['Package'])
new_pkg = df_latest[(~df_latest['Package'].isin(seen_before)) & (df_latest['Gross Revenue'] > 100)].copy()
if not new_pkg.empty:
    st.subheader(f"🆕 New Package Alert (Gross Revenue > $100, New on {latest_date.strftime('%d/%m')})")
    new_pkg_table = new_pkg[['Package', 'Gross Revenue', 'IVT (%)', 'Margin (%)', 'Ad format', 'Channel']].copy()
    new_pkg_table['Gross Revenue'] = new_pkg_table['Gross Revenue'].apply(format_money)
    st.dataframe(new_pkg_table, use_container_width=True, hide_index=True)

# --- Revenue Drop Alert with Drilldown ---
st.subheader(f"⬇️ Revenue Drop Alert for {latest_date.strftime('%d/%m')} (Rev > $50, Drop > 15%)")
prev_day = dates[-2]
drop_df = df_latest.set_index(['Package', 'Ad format'])[['Gross Revenue']].join(
    df[df['Date'] == prev_day].set_index(['Package', 'Ad format'])['Gross Revenue'], rsuffix='_prev', how='left'
).fillna(0).reset_index()
drop_df['% Drop'] = np.where(
    drop_df['Gross Revenue_prev'] > 0,
    (drop_df['Gross Revenue'] - drop_df['Gross Revenue_prev']) / drop_df['Gross Revenue_prev'] * 100,
    0
)
drop_df['Show'] = (
    (drop_df['Gross Revenue_prev'] > 50) &
    (drop_df['% Drop'] < -15)
)

agg_drop = drop_df[drop_df['Show']].groupby('Package').agg({
    'Gross Revenue': 'sum',
    'Gross Revenue_prev': 'sum',
    '% Drop': 'mean'
}).reset_index()
agg_drop['Gross Revenue'] = agg_drop['Gross Revenue'].apply(format_money)
agg_drop['Gross Revenue_prev'] = agg_drop['Gross Revenue_prev'].apply(format_money)
agg_drop['% Drop'] = agg_drop['% Drop'].apply(lambda x: f"{x:.0f}%")

for _, row in agg_drop.iterrows():
    with st.expander(f"📦 {row['Package']} (click for breakdown)"):
        st.write(f"**Gross Revenue:** {row['Gross Revenue']}  \n**Previous Day:** {row['Gross Revenue_prev']}  \n**% Drop:** {row['% Drop']}")
        breakdown = drop_df[(drop_df['Package'] == row['Package']) & (drop_df['Show'])]
        breakdown_table = breakdown[['Ad format', 'Gross Revenue', 'Gross Revenue_prev', '% Drop']].copy()
        breakdown_table['Gross Revenue'] = breakdown_table['Gross Revenue'].apply(format_money)
        breakdown_table['Gross Revenue_prev'] = breakdown_table['Gross Revenue_prev'].apply(format_money)
        breakdown_table['% Drop'] = breakdown_table['% Drop'].apply(lambda x: f"{x:.0f}%")
        st.dataframe(breakdown_table, use_container_width=True, hide_index=True)
