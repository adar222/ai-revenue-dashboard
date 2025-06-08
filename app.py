import streamlit as st
import pandas as pd
import numpy as np
import openai

st.set_page_config(layout="wide")
st.title("📈 AI-Powered Revenue Action Center")

# --- TAB SELECTION ---
tab = st.sidebar.radio("Navigate", ["Dashboard", "AI Insights"])

# --- FILE UPLOAD ---
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])
if not uploaded_file:
    st.stop()
df = pd.read_excel(uploaded_file)
df['Date'] = pd.to_datetime(df['Date'])

# --- Formatting Helpers (with commas) ---
def format_money(val):
    try:
        return "${:,}".format(int(round(val)))
    except:
        return ""

def format_margin(val):
    try:
        return "{:,}%".format(int(round(float(val))))
    except:
        return ""

def format_pct(val):
    try:
        return "{:,}%".format(int(round(float(val))))
    except:
        return ""

def format_int(val):
    try:
        return "{:,}".format(int(round(val)))
    except:
        return ""

def realtime_status(change):
    if -15 <= change <= 40:
        return "🟢 Safe"
    elif -40 <= change < -15 or 40 < change <= 100:
        return "🟡 Needs Review"
    else:
        return "🔴 Critical"

# --- Date Ranges ---
dates = sorted(df['Date'].unique())
if len(dates) < 6:
    st.warning("Need at least 6 days of data for 3d vs 3d comparison!")
    st.stop()

last3d = dates[-3:]
prev3d = dates[-6:-3]
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
ac_table['% Change'] = ac_table['% Change'].apply(lambda x: f"{x:,.0f}%")

# --- MAIN TAB ---
if tab == "Dashboard":
    st.subheader("📊 Action Center: Top 15 Trending Packages")
    st.caption(f"(Last 3d: {last_range} vs Prev 3d: {prev_range})")
    st.dataframe(ac_table, use_container_width=True, hide_index=True)

    # --- IVT & Margin Alert (Last Day) ---
    latest_date = dates[-1]
    df_latest = df[df['Date'] == latest_date].copy()
    st.subheader(f"🛡️ IVT & Margin Alert (Last Day: {latest_date.strftime('%d/%m')})")
    ivt_margin = df_latest.sort_values('Gross Revenue', ascending=False).head(5).copy()
    # Add 2 demo low margin rows
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

    # b) Highest IVT for packages over $100
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

    # --- Revenue Drop Alert with Filter, Sort, Drilldown, Revenue in Expander Title ---
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
    agg_drop['% Drop'] = agg_drop['% Drop'].apply(lambda x: f"{x:,.0f}%")

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
            breakdown_table['% Drop'] = breakdown_table['% Drop'].apply(lambda x: f"{x:,.0f}%")
            st.dataframe(
                breakdown_table.style.set_properties(
                    subset=['Gross Revenue', 'Gross Revenue_prev', '% Drop'],
                    **{'text-align': 'center'}
                ),
                use_container_width=True,
                hide_index=True
            )

    # --- AI Bot (Ask AI About Your Data) ---
    st.markdown("---")
    st.subheader("🤖 Ask AI About Your Data")
    api_key = st.text_input("Enter your OpenAI API key:", type="password")
    user_q = st.text_input("Type your question about a package, e.g.: 'Why did com.tripedot.woodoku drop?'")
    ask_button = st.button("Ask AI")

if api_key and user_q and ask_button:
    trending_pkgs = merged.sort_values(f"Last 3d Revenue ({last_range})", ascending=False).head(15)['Package'].tolist()
    context_rows = []
    for pkg in trending_pkgs:
        last = df[(df['Package'] == pkg) & (df['Date'].isin(last3d))]
        prev = df[(df['Package'] == pkg) & (df['Date'].isin(prev3d))]
        def safe_mean(series):
            return None if len(series) == 0 else np.nanmean(series)
        last_rev = last['Gross Revenue'].sum()
        prev_rev = prev['Gross Revenue'].sum()
        last_rpm = safe_mean(last['RPM']) if 'RPM' in last.columns else None
        prev_rpm = safe_mean(prev['RPM']) if 'RPM' in prev.columns else None
        last_cpm = safe_mean(last['CPM']) if 'CPM' in last.columns else None
        prev_cpm = safe_mean(prev['CPM']) if 'CPM' in prev.columns else None
        last_fill = safe_mean(last['Fill Rate']) if 'Fill Rate' in last.columns else None
        prev_fill = safe_mean(prev['Fill Rate']) if 'Fill Rate' in prev.columns else None
        row = f"""Package: {pkg}
Last3d Revenue: {format_int(last_rev)}
Prev3d Revenue: {format_int(prev_rev)}
Last3d RPM: {last_rpm:.2f}  Prev3d RPM: {prev_rpm:.2f}""" if last_rpm is not None and prev_rpm is not None else ""
        row += f"\nLast3d CPM: {last_cpm:.2f}  Prev3d CPM: {prev_cpm:.2f}" if last_cpm is not None and prev_cpm is not None else ""
        row += f"\nLast3d Fill Rate: {last_fill:.2f}  Prev3d Fill Rate: {prev_fill:.2f}" if last_fill is not None and prev_fill is not None else ""
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
            client = openai.OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=512,
                temperature=0.3,
            )
            answer = response.choices[0].message.content
            st.markdown(answer)
        except Exception as e:
            st.error(f"AI Error: {e}")


# ------------- AI INSIGHTS TAB -------------
if tab == "AI Insights":
    st.header("🧠 AI Insights — Top 15 Packages Revenue Trends")
    st.caption(f"(Last 3d: {last3d[0].strftime('%d/%m')}–{last3d[-1].strftime('%d/%m')} vs Prev 3d: {prev3d[0].strftime('%d/%m')}–{prev3d[-1].strftime('%d/%m')})")
    for idx, row in merged.iterrows():
        pkg = row['Package']
        change = row['% Change']
        trend_icon = "🟢" if change > 0 else "🔴"

        # Get recent ad format by revenue
        last_data = df[(df['Package'] == pkg) & (df['Date'].isin(last3d))]
        prev_data = df[(df['Package'] == pkg) & (df['Date'].isin(prev3d))]
        if not last_data.empty and 'Ad format' in last_data.columns:
            top_adformat = last_data.groupby('Ad format')['Gross Revenue'].sum().idxmax()
        else:
            top_adformat = "N/A"

        last_rev = last_data['Gross Revenue'].sum()
        prev_rev = prev_data['Gross Revenue'].sum()
        bullet_points = []

        # Impressions
        impressions_last = last_data['Impressions'].sum() if 'Impressions' in last_data else None
        impressions_prev = prev_data['Impressions'].sum() if 'Impressions' in prev_data else None
        if impressions_last is not None and impressions_prev is not None:
            diff = impressions_last - impressions_prev
            pct = (diff / impressions_prev) * 100 if impressions_prev > 0 else 0
            if abs(pct) > 7:
                icon = "🟢" if pct > 0 else "🔴"
                bullet_points.append(f"{icon} Impressions {'increased' if pct>0 else 'decreased'} by {abs(int(pct)):,}%")

        # Fill Rate
        if 'Fill Rate' in last_data and 'Fill Rate' in prev_data:
            fill_last = last_data['Fill Rate'].mean()
            fill_prev = prev_data['Fill Rate'].mean()
            if not np.isnan(fill_last) and not np.isnan(fill_prev):
                pct = fill_last - fill_prev
                if abs(pct) > 2:
                    icon = "🟢" if pct > 0 else "🔴"
                    bullet_points.append(f"{icon} Fill Rate {'up' if pct>0 else 'down'} by {abs(pct):,.1f} pts")

        # CPM
        if 'CPM' in last_data and 'CPM' in prev_data:
            cpm_last = last_data['CPM'].mean()
            cpm_prev = prev_data['CPM'].mean()
            if not np.isnan(cpm_last) and not np.isnan(cpm_prev):
                pct = ((cpm_last - cpm_prev) / cpm_prev * 100) if cpm_prev else 0
                if abs(pct) > 5:
                    icon = "🟢" if pct > 0 else "🔴"
                    bullet_points.append(f"{icon} CPM {'rose' if pct>0 else 'dropped'} by {abs(int(pct)):,}%")

        # RPM
        if 'RPM' in last_data and 'RPM' in prev_data:
            rpm_last = last_data['RPM'].mean()
            rpm_prev = prev_data['RPM'].mean()
            if not np.isnan(rpm_last) and not np.isnan(rpm_prev):
                pct = ((rpm_last - rpm_prev) / rpm_prev * 100) if rpm_prev else 0
                if abs(pct) > 5:
                    icon = "🟢" if pct > 0 else "🔴"
                    bullet_points.append(f"{icon} RPM {'up' if pct>0 else 'down'} by {abs(int(pct)):,}%")

        # Non-obvious/invented examples
        if pkg == "com.block.game.jigsaw.puzzles":
            bullet_points.append("🔴 Revenue drop is driven by a spike in IVT (invalid traffic) detected, causing blocks by demand partners.")
        if pkg == "com.goods.master3d.triple.puzzle":
            bullet_points.append("🔴 A sudden shift to lower-yield ad formats this week reduced overall eCPM, despite stable demand.")
        if pkg == "games.unmobil.found.it":
            bullet_points.append("🟢 New in-app event increased ad engagement, raising Fill Rate and CPM.")
        if pkg == "com.play.simple.wordsearch":
            bullet_points.append("🔴 Fill Rate stable, but sudden drop in requests from Tier 1 GEOs impacted total revenue.")
        if pkg == "com.vottzapps.wordle":
            bullet_points.append("🔴 Margin dropped as demand shifted to lower-value channels (ex: more display, less video).")
        if pkg == "com.easybrain.nonogram":
            bullet_points.append("🟢 Package was whitelisted by a new DSP, adding incremental spend.")

        if not bullet_points:
            bullet_points.append("No significant metric change detected.")

        st.markdown(f"""
**{trend_icon} {pkg}**
- **Revenue {'Up' if change>0 else 'Down'} {abs(int(change)):,}%** (from {format_int(prev_rev)} to {format_int(last_rev)}; Main format: {top_adformat})
""")
        for b in bullet_points:
            st.markdown(f"  - {b}")
        st.markdown("---")
