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

# --- Convert date to datetime ---
df['Date'] = pd.to_datetime(df['Date'])

# --- Trending Table: Per Package Only (Option 1) ---
def agg_3d_simple(period):
    return (
        df[df['Date'].isin(period)]
        .groupby('Package', as_index=False)['Gross Revenue']
        .sum()
        .rename(columns={'Gross Revenue': f"Revenue_{period[-1].strftime('%m-%d')}"})
    )

last_agg = agg_3d_simple(last3d)
prev_agg = agg_3d_simple(prev3d)
merged = pd.merge(
    last_agg, prev_agg, how='outer', on='Package'
).fillna(0)
merged['Δ Amount'] = merged[last_agg.columns[-1]] - merged[prev_agg.columns[-1]]
merged['% Change'] = np.where(
    merged[prev_agg.columns[-1]] > 0,
    (merged[last_agg.columns[-1]] - merged[prev_agg.columns[-1]]) / merged[prev_agg.columns[-1]] * 100,
    100.0
)
# Status logic (take most recent in the last 3d period)
latest_status = (
    df[df['Date'].isin(last3d)][['Package', 'Status']]
    .drop_duplicates('Package', keep='last').set_index('Package')['Status']
)
merged['Status'] = merged['Package'].map(latest_status).fillna('-')
merged = merged.sort_values(last_agg.columns[-1], ascending=False).head(10)

# Format and display
ac_table = merged[['Package', last_agg.columns[-1], prev_agg.columns[-1], 'Δ Amount', '% Change', 'Status']].copy()
ac_table[last_agg.columns[-1]] = ac_table[last_agg.columns[-1]].apply(format_money)
ac_table[prev_agg.columns[-1]] = ac_table[prev_agg.columns[-1]].apply(format_money)
ac_table['Δ Amount'] = ac_table['Δ Amount'].apply(format_money)
ac_table['% Change'] = ac_table['% Change'].apply(lambda x: f"{x:.0f}%")
st.dataframe(ac_table, use_container_width=True)


# --- 2. IVT & Margin Alert (Last Day) ---
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
st.dataframe(ivt_margin_table, use_container_width=True)

# b) Highest IVT for packages over $100
ivt_over_100 = df_latest[df_latest['Gross Revenue'] > 100].sort_values('IVT (%)', ascending=False).head(5).copy()
ivt_over_100['Alert'] = np.where(ivt_over_100['Margin (%)'] < 25, '❗ Low Margin',
                        np.where(ivt_over_100['IVT (%)'] > 15, '⚠️ High IVT', '✅ OK'))
ivt_over_100_table = ivt_over_100[['Package', 'Gross Revenue', 'IVT (%)', 'Margin (%)', 'Alert']].copy()
ivt_over_100_table['Gross Revenue'] = ivt_over_100_table['Gross Revenue'].apply(format_money)
st.markdown("**b) Highest IVT for Packages Over $100:**")
st.dataframe(ivt_over_100_table, use_container_width=True)

# --- 3. New Package Alert (over $100, first time seen) ---
seen_before = set(df[df['Date'] < latest_date]['Package'])
new_pkg = df_latest[(~df_latest['Package'].isin(seen_before)) & (df_latest['Gross Revenue'] > 100)].copy()
if not new_pkg.empty:
    st.subheader(f"🆕 New Package Alert (Gross Revenue > $100, New on {latest_date.strftime('%d/%m')})")
    new_pkg_table = new_pkg[['Package', 'Gross Revenue', 'IVT (%)', 'Margin (%)', 'Ad format', 'Channel']].copy()
    new_pkg_table['Gross Revenue'] = new_pkg_table['Gross Revenue'].apply(format_money)
    st.dataframe(new_pkg_table, use_container_width=True)

# --- 4. Revenue Drop Alert ---
st.subheader(f"⬇️ Revenue Drop Alert for {latest_date.strftime('%d/%m')} (Rev > $50, Drop > 15%)")
# For each package, get previous day revenue
prev_day = dates[-2]
rev_drop = df_latest.set_index('Package')[['Gross Revenue', 'Ad format']].join(
    df[df['Date'] == prev_day].set_index('Package')['Gross Revenue'], rsuffix='_prev', how='left'
).fillna(0).reset_index()
rev_drop['% Drop'] = np.where(
    rev_drop['Gross Revenue_prev'] > 0,
    (rev_drop['Gross Revenue'] - rev_drop['Gross Revenue_prev']) / rev_drop['Gross Revenue_prev'] * 100,
    0
)
rev_drop_filtered = rev_drop[
    (rev_drop['Gross Revenue_prev'] > 50) &
    (rev_drop['% Drop'] < -15)
].copy()
rev_drop_filtered['Gross Revenue'] = rev_drop_filtered['Gross Revenue'].apply(format_money)
rev_drop_filtered['Gross Revenue_prev'] = rev_drop_filtered['Gross Revenue_prev'].apply(format_money)
rev_drop_filtered['% Drop'] = rev_drop_filtered['% Drop'].apply(lambda x: f"{x:.0f}%")
st.dataframe(
    rev_drop_filtered[['Package', 'Gross Revenue', 'Gross Revenue_prev', '% Drop', 'Ad format']],
    use_container_width=True
)
