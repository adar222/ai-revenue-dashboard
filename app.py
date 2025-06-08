import streamlit as st
import pandas as pd
import numpy as np
import openai

st.set_page_config(layout="wide")
st.title("📈 AI-Powered Revenue Action Center")

uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])
if not uploaded_file:
    st.stop()

df = pd.read_excel(uploaded_file)
df['Date'] = pd.to_datetime(df['Date'])

dates = sorted(df['Date'].unique())
if len(dates) < 6:
    st.warning("Need at least 6 days of data for 3d vs 3d comparison!")
    st.stop()

last3d = dates[-3:]
prev3d = dates[-6:-3]

def format_money(val):
    return f"${int(round(val))}"

def format_margin(val):
    try:
        return f"{int(round(float(val)))}%"
    except:
        return ""

def format_pct(val):
    try:
        return f"{int(round(float(val)))}%"
    except:
        return ""

def realtime_status(change):
    if -15 <= change <= 40:
        return "🟢 Safe"
    elif -40 <= change < -15 or 40 < change <= 100:
        return "🟡 Needs Review"
    else:
        return "🔴 Critical"

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
merged = merged.sort_values(f"Last 3d Revenue ({last_range})", ascending=False).head(15)

ac_table = merged[['Package', f"Last 3d Revenue ({last_range})", f"Prev 3d Revenue ({prev_range})", 'Δ Amount', '% Change', 'Status']].copy()
ac_table[f"Last 3d Revenue ({last_range})"] = ac_table[f"Last 3d Revenue ({last_range})"].apply(format_money)
ac_table[f"Prev 3d Revenue ({prev_range})"] = ac_table[f"Prev 3d Revenue ({prev_range})"].apply(format_money)
ac_table['Δ Amount'] = ac_table['Δ Amount'].apply(format_money)
ac_table['% Change'] = ac_table['% Change'].apply(lambda x: f"{x:.0f}%")

latest_date = dates[-1]
df_latest = df[df['Date'] == latest_date].copy()

# ------------------------- TABS -------------------------

tab1, tab2 = st.tabs(["Dashboard", "AI Insights"])

# ------------------- DASHBOARD TAB ----------------------

with tab1:
    st.subheader("📊 Action Center: Top 15 Trending Packages")
    st.caption(f"(Last 3d: {last_range} vs Prev 3d: {prev_range})")
    st.dataframe(ac_table, use_container_width=True, hide_index=True)

    st.subheader(f"🛡️ IVT & Margin Alert (Last Day: {latest_date.strftime('%d/%m')})")
    ivt_margin = df_latest.sort_values('Gross Revenue', ascending=False).head(5).copy()
    ivt_margin = pd.concat([ivt_margin,
        pd.DataFrame([
            {"Package": "com.example.lowmargin3", "Gross Revenue": 315, "IVT (%)": 9.5, "Margin (%)": 17, "Alert": "❗ Low Margin"},
            {"Package": "com.example.lowmargin4", "Gross Revenue": 200, "IVT (%)": 6.2, "Margin (%)": 8, "Alert": "❗ Low Margin"},
        ])
    ], ignore_index=True)
    ivt_margin['Alert'] = np.where(ivt_margin['Margin (%)'].astype(float) < 25, '❗ Low Margin',
                           np.where(ivt_margin['IVT (%)'].astype(float) > 15, '⚠️ High IVT', '✅ OK'))
    ivt_margin_table = ivt_margin[['Package', 'Gross Revenue', 'IVT (%)', 'Margin (%)', 'Alert']].copy()
    ivt_margin_table['Gross Revenue'] = ivt_margin_table['Gross Revenue'].apply(format_money)
    ivt_margin_table['Margin (%)'] = ivt_margin_table['Margin (%)'].apply(format_margin)
    ivt_margin_table['IVT (%)'] = ivt_margin_table['IVT (%)'].apply(format_pct)
    ivt_margin_table = ivt_margin_table.style.set_properties(subset=['Margin (%)', 'IVT (%)'], **{'text-align': 'center'})
    st.markdown("**a) Top 5 Grossing Packages:**")
    st.dataframe(ivt_margin_table, use_container_width=True, hide_index=True)

    ivt_over_100 = df_latest[df_latest['Gross Revenue'] > 100].sort_values('IVT (%)', ascending=False).head(5).copy()
    ivt_over_100['Alert'] = np.where(ivt_over_100['Margin (%)'] < 25, '❗ Low Margin',
                            np.where(ivt_over_100['IVT (%)'] > 15, '⚠️ High IVT', '✅ OK'))
    ivt_over_100_table = ivt_over_100[['Package', 'Gross Revenue', 'IVT (%)', 'Margin (%)', 'Alert']].copy()
    ivt_over_100_table['Gross Revenue'] = ivt_over_100_table['Gross Revenue'].apply(format_money)
    ivt_over_100_table['Margin (%)'] = ivt_over_100_table['Margin (%)'].apply(format_margin)
    ivt_over_100_table['IVT (%)'] = ivt_over_100_table['IVT (%)'].apply(format_pct)
    ivt_over_100_table = ivt_over_100_table.style.set_properties(subset=['Margin (%)', 'IVT (%)'], **{'text-align': 'center'})
    st.markdown("**b) Highest IVT for Packages Over $100:**")
    st.dataframe(ivt_over_100_table, use_container_width=True, hide_index=True)

    # New Package Alert (over $100, first time seen)
    seen_before = set(df[df['Date'] < latest_date]['Package'])
    new_pkg = df_latest[(~df_latest['Package'].isin(seen_before)) & (df_latest['Gross Revenue'] > 100)].copy()
    if not new_pkg.empty:
        st.subheader(f"🆕 New Package Alert (Gross Revenue > $100, New on {latest_date.strftime('%d/%m')})")
        new_pkg_table = new_pkg[['Package', 'Gross Revenue', 'IVT (%)', 'Margin (%)', 'Ad format', 'Channel']].copy()
        new_pkg_table['Gross Revenue'] = new_pkg_table['Gross Revenue'].apply(format_money)
        new_pkg_table['Margin (%)'] = new_pkg_table['Margin (%)'].apply(format_margin)
        new_pkg_table['IVT (%)'] = new_pkg_table['IVT (%)'].apply(format_pct)
        new_pkg_table = new_pkg_table.style.set_properties(subset=['Margin (%)', 'IVT (%)'], **{'text-align': 'center'})
        st.dataframe(new_pkg_table, use_container_width=True, hide_index=True)

    # Revenue Drop Alert with Filter, Sort, Drilldown, Revenue in Expander Title
    st.subheader(f"⬇️ Revenue Drop Alert for {latest_date.strftime('%d/%m')} (Rev > $50, Drop > 15%)")
    gross_rev_min = st.slider("Show only packages with Gross Revenue above:", 0, 5000, 50, 10)
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
    agg_drop = agg_drop[agg_drop['Gross Revenue'] > gross_rev_min]
    agg_drop['Gross Revenue'] = agg_drop['Gross Revenue'].apply(format_money)
    agg_drop['Gross Revenue_prev'] = agg_drop['Gross Revenue_prev'].apply(format_money)
    agg_drop['% Drop'] = agg_drop['% Drop'].apply(lambda x: f"{x:.0f}%")

    for _, row in agg_drop.iterrows():
        pkg_name = row['Package']
        rev = row['Gross Revenue']
        prev_rev = row['Gross Revenue_prev']
        pct_drop = row['% Drop']
        with st.expander(f"📦 {pkg_name} — {rev} (prev: {prev_rev}) ▼ ({pct_drop}) (click for breakdown)"):
            st.write(f"**Gross Revenue:** {rev}  \n**Previous Day:** {prev_rev}  \n**% Drop:** {pct_drop}")
            breakdown = drop_df[(drop_df['Package'] == pkg_name) & (drop_df['Show'])]
            breakdown_table = breakdown[['Ad format', 'Gross Revenue', 'Gross Revenue_prev', '% Drop']].copy()
            breakdown_table['Gross Revenue'] = breakdown_table['Gross Revenue'].apply(format_money)
            breakdown_table['Gross Revenue_prev'] = breakdown_table['Gross Revenue_prev'].apply(format_money)
            breakdown_table['% Drop'] = breakdown_table['% Drop'].apply(lambda x: f"{x:.0f}%")
            st.dataframe(
                breakdown_table.style.set_properties(
                    subset=['Gross Revenue', 'Gross Revenue_prev', '% Drop'],
                    **{'text-align': 'center'}
                ),
                use_container_width=True,
                hide_index=True
            )

    # --- AI Chatbot (bottom of dashboard) ---
    st.markdown("---")
    st.subheader("🤖 Ask AI About Your Data")
    api_key = st.text_input("Enter your OpenAI API key:", type="password")
    user_q = st.text_input("Type your question about a package, e.g.: 'Why did com.tripedot.woodoku drop?'")
    if api_key and user_q:
        trending_pkgs = merged.sort_values(f"Last 3d Revenue ({last_range})", ascending=False).head(15)['Package'].tolist()
        context_rows = []
        for pkg in trending_pkgs:
            last = df[(df['Package'] == pkg) & (df['Date'].isin(last3d))]
            prev = df[(df['Package'] == pkg) & (df['Date'].isin(prev3d))]
            last_rev = last['Gross Revenue'].sum()
            prev_rev = prev['Gross Revenue'].sum()
            last_rpm = last['RPM'].mean() if 'RPM' in last.columns else None
            prev_rpm = prev['RPM'].mean() if 'RPM' in prev.columns else None
            last_cpm = last['CPM'].mean() if 'CPM' in last.columns else None
            prev_cpm = prev['CPM'].mean() if 'CPM' in prev.columns else None
            last_fill = last['Fill Rate'].mean() if 'Fill Rate' in last.columns else None
            prev_fill = prev['Fill Rate'].mean() if 'Fill Rate' in prev.columns else None
            row = f"""
            Package: {pkg}
            Last3d Revenue: {int(last_rev)}
            Prev3d Revenue: {int(prev_rev)}
            Last3d RPM: {last_rpm:.2f}  Prev3d RPM: {prev_rpm:.2f}
            Last3d CPM: {last_cpm:.2f}  Prev3d CPM: {prev_cpm:.2f}
            Last3d Fill Rate: {last_fill:.2f}  Prev3d Fill Rate: {prev_fill:.2f}
            """
            context_rows.append(row)
        data_context = "\n".join(context_rows)
        system_prompt = (
            "You are an AI assistant for a programmatic revenue team. "
            "You will receive questions from managers about why ad revenue changed for a given app/package. "
            "You have context with historical performance data for the top packages. "
            "Base your answers only on this context. If you don't know, say so. "
            "Summarize key changes in metrics (RPM, CPM, Fill Rate, Requests, Impressions, etc) in bullet points. "
            "Always use simple business language."
        )
        prompt = (
            f"{system_prompt}\n\n"
            f"DATA CONTEXT:\n{data_context}\n\n"
            f"QUESTION: {user_q}\n\n"
            "Give your answer in clear bullet points."
        )
        with st.spinner("Thinking..."):
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    api_key=api_key,
                    max_tokens=512,
                    temperature=0.3,
                )
                answer = response["choices"][0]["message"]["content"]
                st.markdown(answer)
            except Exception as e:
                st.error(f"AI Error: {e}")

# ------------------- AI INSIGHTS TAB ----------------------

with tab2:
    st.header("🧠 AI Insights: Top 15 Packages (by Revenue)")

    for idx, row in merged.iterrows():
        pkg = row['Package']
        trend = "📈 Up" if row['% Change'].startswith("+") else "📉 Down"
        pct = row['% Change']
        # Get most recent ad format by revenue
        last_adformat = df[(df['Package'] == pkg) & (df['Date'].isin(last3d))].groupby('Ad format')['Gross Revenue'].sum()
        if not last_adformat.empty:
            top_format = last_adformat.idxmax()
            top_format_rev = last_adformat.max()
        else:
            top_format = "Unknown"
            top_format_rev = 0
        # Build insight bullets
        bullets = []
        prev = df[(df['Package'] == pkg) & (df['Date'].isin(prev3d))]
        last = df[(df['Package'] == pkg) & (df['Date'].isin(last3d))]
        # Check ad format
        bullets.append(f"Main change in **{top_format}** format.")
        # Compare main metrics
        def pct_delta(l, p):
            try:
                return 100 * (l - p) / p if p else 0
            except: return 0

        for col, label in [('Gross Revenue','revenue'), ('Fill Rate','fill rate'), ('CPM','CPM'), ('RPM','RPM'), ('Impressions','impressions'), ('Requests','requests'), ('IVT (%)','IVT rate'), ('Margin (%)','margin')]:
            if col in last.columns and col in prev.columns:
                lv = last[col].mean() if col not in ['Gross Revenue','Impressions','Requests'] else last[col].sum()
                pv = prev[col].mean() if col not in ['Gross Revenue','Impressions','Requests'] else prev[col].sum()
                delta = pct_delta(lv, pv)
                if abs(delta) > 10:
                    direction = "increased" if delta > 0 else "dropped"
                    valstr = f"{abs(int(round(delta)))}%"
                    bullets.append(f"{label.title()} {direction} by {valstr}.")

        st.markdown(
            f"""<details>
<summary><strong>{pkg}</strong> ({top_format}) – {trend} {pct}</summary>
<ul>
    {''.join(f"<li>{b}</li>" for b in bullets)}
</ul>
</details>""",
            unsafe_allow_html=True
        )
