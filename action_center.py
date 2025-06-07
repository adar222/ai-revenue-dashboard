import streamlit as st

def safe_col(df, name):
    for c in df.columns:
        if c.strip().lower() == name.strip().lower():
            return c
    return None

def show_action_center_top10(df):
    import pandas as pd
    if df.empty:
        st.info("No data to show.")
        return
    date_col = safe_col(df, 'Date')
    package_col = safe_col(df, 'Package')
    gross_col = safe_col(df, 'Gross Revenue')
    if not all([date_col, package_col, gross_col]):
        st.warning("Required columns missing.")
        return
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    last_date = df[date_col].max()
    prev3 = last_date - pd.Timedelta(days=3)
    prev6 = last_date - pd.Timedelta(days=6)
    last3 = df[df[date_col] > prev3]
    prev3 = df[(df[date_col] <= prev3) & (df[date_col] > prev6)]
    last3_sum = last3.groupby(package_col)[gross_col].sum()
    prev3_sum = prev3.groupby(package_col)[gross_col].sum()
    joined = pd.DataFrame({'Last 3d Revenue': last3_sum, 'Prev 3d Revenue': prev3_sum}).fillna(0)
    joined['Δ'] = joined['Last 3d Revenue'] - joined['Prev 3d Revenue']
    joined['% Change'] = joined.apply(lambda x: 0 if x['Prev 3d Revenue']==0 else 100*(x['Δ']/x['Prev 3d Revenue']), axis=1)
    joined = joined.sort_values('Δ', ascending=False).head(10)
    joined['Action'] = joined['% Change'].apply(lambda x: '✅ Stable' if x > 0 else '🔻 Investigate')
    joined = joined.reset_index()
    joined['Last 3d Revenue'] = joined['Last 3d Revenue'].map('${:,.0f}'.format)
    joined['Prev 3d Revenue'] = joined['Prev 3d Revenue'].map('${:,.0f}'.format)
    joined['Δ'] = joined['Δ'].map('${:,.0f}'.format)
    joined['% Change'] = joined['% Change'].map('{:.0f}%'.format)
    st.dataframe(joined[[package_col, 'Last 3d Revenue', 'Prev 3d Revenue', 'Δ', '% Change', 'Action']], hide_index=True)

