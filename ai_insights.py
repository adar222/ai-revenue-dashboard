import streamlit as st
import pandas as pd

def safe_col(df, name):
    for c in df.columns:
        if c.strip().lower() == name.strip().lower():
            return c
    return None

def show_revenue_drop_insight(df, advertiser):
    advertiser_col = safe_col(df, 'Advertiser')
    package_col = safe_col(df, 'Package')
    date_col = safe_col(df, 'Date')
    grossrev_col = safe_col(df, 'Gross Revenue')
    fill_col = safe_col(df, 'FillRate')
    margin_col = safe_col(df, 'Margin (%)')
    ivt_col = safe_col(df, 'IVT (%)')
    if not all([advertiser_col, package_col, date_col, grossrev_col, fill_col, margin_col, ivt_col]):
        st.error("One or more required columns are missing from your Excel.")
        return
    df = df[df[advertiser_col] == advertiser].copy()
    if df.empty:
        st.info("No data for this advertiser.")
        return
    df[date_col] = pd.to_datetime(df[date_col])
    last_date = df[date_col].max()
    prev_date = last_date - pd.Timedelta(days=1)
    df_last = df[df[date_col] == last_date]
    df_prev = df[df[date_col] == prev_date]
    rev_last = df_last[grossrev_col].sum()
    rev_prev = df_prev[grossrev_col].sum()
    if rev_prev == 0:
        st.info("Not enough previous day data.")
        return
    pct_drop = 100 * (rev_last - rev_prev) / rev_prev
    st.markdown(f"**Revenue {'dropped' if pct_drop < 0 else 'increased'} {abs(pct_drop):.1f}% (${rev_prev:,.0f} → ${rev_last:,.0f}) vs previous day.**")
    merged = pd.merge(
        df_last.groupby(package_col).agg({grossrev_col:'sum', fill_col:'mean', margin_col:'mean', ivt_col:'mean'}).rename(columns=lambda x: x+'_last'),
        df_prev.groupby(package_col).agg({grossrev_col:'sum', fill_col:'mean', margin_col:'mean', ivt_col:'mean'}).rename(columns=lambda x: x+'_prev'),
        left_index=True, right_index=True, how='outer').fillna(0)
    )
    merged['Rev Δ'] = merged[f'{grossrev_col}_last'] - merged[f'{grossrev_col}_prev']
    merged['Fill Δ'] = merged[f'{fill_col}_last'] - merged[f'{fill_col}_prev']
    merged['Margin Δ'] = merged[f'{margin_col}_last'] - merged[f'{margin_col}_prev']
    merged['IVT Δ'] = merged[f'{ivt_col}_last'] - merged[f'{ivt_col}_prev']
    biggest = merged.sort_values('Rev Δ').head(3)
    for i, (pkg, row) in enumerate(biggest.iterrows(), 1):
        st.markdown(
            f"- 🥇 **{pkg}:** {row['Rev Δ']:+.0f}$, fill rate {row['Fill Δ']:+.1f}%, margin {row['Margin Δ']:+.1f}%, IVT {row['IVT Δ']:+.1f}%"
        )
    st.markdown("**Top Reasons:**")
    st.markdown("1. Lower fill rate on high-revenue packages  \n2. Margin shrinkage  \n3. IVT increased, reducing valid impressions")

def show_ivt_margin_alert(df):
    date_col = safe_col(df, 'Date')
    ivt_col = safe_col(df, 'IVT (%)')
    margin_col = safe_col(df, 'Margin (%)')
    package_col = safe_col(df, 'Package')
    rpm_col = safe_col(df, 'RPM')
    alert_col = safe_col(df, 'Alert')
    if not all([date_col, ivt_col, margin_col, package_col, rpm_col, alert_col]):
        st.info("No data to show.")
        return
    df[date_col] = pd.to_datetime(df[date_col])
    last_date = df[date_col].max()
    last_day = df[df[date_col] == last_date].copy()
    show = last_day[(last_day[ivt_col] > 10) | (last_day[margin_col] < 20)]
    st.dataframe(show[[package_col, rpm_col, ivt_col, margin_col, alert_col]], hide_index=True)

def show_revenue_drop_table(df):
    date_col = safe_col(df, 'Date')
    package_col = safe_col(df, 'Package')
    gross_col = safe_col(df, 'Gross Revenue')
    score_col = safe_col(df, 'Score')
    if not all([date_col, package_col, gross_col, score_col]):
        st.info("No data to show.")
        return
    df[date_col] = pd.to_datetime(df[date_col])
    last_date = df[date_col].max()
    prev_date = last_date - pd.Timedelta(days=1)
    last = df[df[date_col]==last_date]
    prev = df[df[date_col]==prev_date]
    merged = pd.merge(
        last[[package_col,gross_col,score_col]],
        prev[[package_col,gross_col]].rename(columns={gross_col:'Prev Gross Revenue'}),
        on=package_col, how='inner'
    )
    merged['Δ'] = merged[gross_col] - merged['Prev Gross Revenue']
    merged['% Drop'] = 100*(merged['Δ']/merged['Prev Gross Revenue'])
    show = merged[(merged[gross_col] > 50) & (merged['% Drop'] < -20)]
    def score_circle(score):
        if score >= 75:
            return f"{int(score)} 🟢"
        elif score >= 55:
            return f"{int(score)} 🟡"
        else:
            return f"{int(score)} 🔴"
    show['Score'] = show[score_col].apply(score_circle)
    show[gross_col] = show[gross_col].map('${:,.0f}'.format)
    show['Prev Gross Revenue'] = show['Prev Gross Revenue'].map('${:,.0f}'.format)
    show['Δ'] = show['Δ'].map('${:,.0f}'.format)
    show['% Drop'] = show['% Drop'].map('{:.0f}%'.format)
    show = show.rename(columns={
        gross_col:'Last Day Rev',
        'Prev Gross Revenue':'Prev Day Rev'
    })
    st.dataframe(show[[package_col,'Last Day Rev','Prev Day Rev','Δ','% Drop','Score']], hide_index=True)
