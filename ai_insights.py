import streamlit as st
import pandas as pd
import numpy as np
import datetime

# --- HELPER FUNCTIONS ---

def color_arrow(change):
    if change > 0:
        return '<span style="color:green;font-size:1.2em;">↑</span>'
    elif change < 0:
        return '<span style="color:red;font-size:1.2em;">↓</span>'
    return ''

def margin_icon(margin):
    try:
        margin_val = float(margin)
        return "🟢" if margin_val >= 20 else "🟠"
    except:
        return ""

def ivt_icon(ivt):
    try:
        ivt_val = float(ivt)
        return "🟢" if ivt_val <= 10 else "🟠"
    except:
        return ""

def buyer_demo_picker(idx):
    buyers = ["LinkedIn", "DV360", "Amazon", "Criteo", "LinkedIn"]
    return buyers[idx % len(buyers)]

def make_comment(row):
    if row['% Change'] > 18:
        return "Scaling fast"
    if row['% Change'] > 10:
        return "Looks solid"
    if row['% Change'] > 3:
        return "Recovering"
    if row['% Change'] < -18:
        return "Losing buyer interest"
    if row['% Change'] < -10:
        return "Needs attention"
    if row['% Change'] < -3:
        return "At risk"
    return "Stable"

def generate_summary(total_diff, pct_diff, top_gainer, top_loser, df_up, df_down):
    trend = "up" if total_diff > 0 else "down"
    summary = (
        f"Yesterday, overall account revenue was <b>{trend} by {abs(pct_diff):.1f}%</b> "
        f"({'+' if total_diff > 0 else '-'}${abs(total_diff):,.0f}), led mainly by "
        f"<b>{top_gainer['Package']}</b> ({color_arrow(top_gainer['Δ'])} ${abs(top_gainer['Δ']):,.0f}), due to {top_gainer['Reason'].lower()}. "
    )
    if len(df_up) > 1:
        summary += (
            f"Other strong risers included <b>{df_up[1]['Package']}</b> and <b>{df_up[2]['Package']}</b>, "
            f"thanks to {df_up[1]['Reason'].lower()} and {df_up[2]['Reason'].lower()}."
        )
    summary += (
        f" On the downside, <b>{top_loser['Package']}</b> had the largest drop "
        f"({color_arrow(top_loser['Δ'])} -${abs(top_loser['Δ']):,.0f}), with {top_loser['Reason'].lower()}."
    )
    if len(df_down) > 1:
        summary += f" Other key drops: <b>{df_down[1]['Package']}</b> and <b>{df_down[2]['Package']}</b>."
    summary += (
        " Most gains came from higher CPM or fill rates, while most losses were linked to margin, IVT, or buyer shifts."
    )
    return summary

def ai_what_to_do(df_up, df_down):
    actions = []
    for row in df_down[:2]:
        if row['IVT'] > 10:
            actions.append(
                f"**Address IVT issues** for <b>{row['Package']}</b> (IVT {row['IVT']:.1f}%). Consider filtering low-quality supply."
            )
        if row['Margin'] < 20:
            actions.append(
                f"**Review low margin** on <b>{row['Package']}</b> (margin {row['Margin']:.1f}%). Check pricing or creative blocks."
            )
    for row in df_up[:2]:
        if row['CPM'] > 0.4:
            actions.append(
                f"**Capitalize on CPM gains** for <b>{row['Package']}</b> by increasing supply to {row['Buyer']}."
            )
    if len(df_down) > 0:
        actions.append(
            "**Monitor declines** in packages showing consecutive drops (e.g., <b>{}</b>).".format(df_down[0]['Package'])
        )
    if any(row['Reason'].lower().find("fill") >= 0 for row in df_up):
        actions.append(
            "**Leverage video opportunity**—video engagement is driving revenue gains, especially for Amazon DSP buyers."
        )
    return actions

# --- MAIN FUNCTION ---

def show_ai_insights():
    st.header("🧠 AI Insights — Business Impact")
    uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        st.session_state["main_df"] = df  # SAVE TO SESSION STATE
    elif "main_df" in st.session_state:
        df = st.session_state["main_df"]
    else:
        st.info("Please upload an Excel file to see AI insights.")
        return

    required = {'Date', 'Package', 'Gross Revenue', 'eCPM', 'FillRate', 'Margin (%)', 'IVT (%)'}
    if not required.issubset(df.columns):
        st.error("Excel must have columns: Date, Package, Gross Revenue, eCPM, FillRate, Margin (%), IVT (%)")
        return

    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date')
    dates = sorted(df['Date'].unique())
    if len(dates) < 2:
        st.warning("Need at least 2 days of data for AI insights.")
        return

    yesterday = dates[-1]
    day_before = dates[-2]
    df_yest = df[df['Date'] == yesterday].copy()
    df_before = df[df['Date'] == day_before].copy()

    # Aggregate revenue and metrics per package
    rev_yest = df_yest.groupby('Package').agg({
        'Gross Revenue': 'sum',
        'eCPM': 'mean',
        'FillRate': 'mean',
        'Margin (%)': 'mean',
        'IVT (%)': 'mean'
    }).rename(columns={'Gross Revenue': 'Rev Yest', 'eCPM': 'CPM Yest', 'FillRate': 'Fill Yest',
                       'Margin (%)': 'Margin Yest', 'IVT (%)': 'IVT Yest'})
    rev_before = df_before.groupby('Package').agg({
        'Gross Revenue': 'sum',
        'eCPM': 'mean',
        'FillRate': 'mean',
        'Margin (%)': 'mean',
        'IVT (%)': 'mean'
    }).rename(columns={'Gross Revenue': 'Rev Before', 'eCPM': 'CPM Before', 'FillRate': 'Fill Before',
                       'Margin (%)': 'Margin Before', 'IVT (%)': 'IVT Before'})
    merged = rev_yest.join(rev_before, how='outer').fillna(0).reset_index()

    # Calculate changes
    merged['Δ'] = merged['Rev Yest'] - merged['Rev Before']
    merged['% Change'] = np.where(merged['Rev Before'] > 0, (merged['Δ'] / merged['Rev Before']) * 100, 0)
    merged['Dir'] = merged['Δ'].apply(lambda x: color_arrow(x))
    merged['Buyer'] = [buyer_demo_picker(i) for i in range(len(merged))]
    merged['Reason'] = ""
    merged['Comment'] = ""
    merged['CPM'] = merged['CPM Yest'].round(2)
    merged['DSP Fill'] = (merged['Fill Yest'] * 100).round(1)
    merged['Margin'] = merged['Margin Yest'].round(1)
    merged['IVT'] = merged['IVT Yest'].round(1)

    # Create reason & comment per row
    for idx, row in merged.iterrows():
        cpm_diff = row['CPM Yest'] - row['CPM Before']
        fill_diff = row['Fill Yest'] - row['Fill Before']
        ivt_diff = row['IVT Yest'] - row['IVT Before']
        margin_diff = row['Margin Yest'] - row['Margin Before']
        main_metric = None

        if abs(cpm_diff) > 0.04:
            if row['CPM Before'] != 0:
                main_metric = f"CPM {'up' if cpm_diff > 0 else 'down'} {abs(cpm_diff)/row['CPM Before']*100:.0f}%"
            else:
                main_metric = f"CPM {'up' if cpm_diff > 0 else 'down'} (no previous value)"
        elif abs(fill_diff) > 0.02:
            if row['Fill Before'] != 0:
                main_metric = f"Fill {'up' if fill_diff > 0 else 'down'} {abs(fill_diff)/row['Fill Before']*100:.1f}%"
            else:
                main_metric = f"Fill {'up' if fill_diff > 0 else 'down'} (no previous value)"
        elif abs(ivt_diff) > 2:
            if row['IVT Before'] != 0:
                main_metric = f"IVT {'up' if ivt_diff > 0 else 'down'} {abs(ivt_diff)/row['IVT Before']*100:.1f}%"
            else:
                main_metric = f"IVT {'up' if ivt_diff > 0 else 'down'} (no previous value)"
        elif abs(margin_diff) > 2:
            if row['Margin Before'] != 0:
                main_metric = f"Margin {'up' if margin_diff > 0 else 'down'} {abs(margin_diff)/row['Margin Before']*100:.1f}%"
            else:
                main_metric = f"Margin {'up' if margin_diff > 0 else 'down'} (no previous value)"
        else:
            main_metric = "Stable"

        merged.at[idx, 'Reason'] = main_metric
        merged.at[idx, 'Comment'] = make_comment(row)

    # Get top 5 up/down
    movers_up = merged.sort_values('Δ', ascending=False).head(5)
    movers_down = merged.sort_values('Δ').head(5)
    movers_all = pd.concat([movers_up, movers_down])

    # Compute totals for executive summary
    total_rev_yest = df_yest['Gross Revenue'].sum()
    total_rev_before = df_before['Gross Revenue'].sum()
    total_diff = total_rev_yest - total_rev_before
    pct_diff = (total_diff / total_rev_before * 100) if total_rev_before > 0 else 0

    # --- Add summary metric at a glance ---
    delta_color = "normal"
    if pct_diff > 0:
        delta_color = "inverse"  # Green for positive
    elif pct_diff < 0:
        delta_color = "off"      # Red for negative

    st.markdown("### :star: Business Impact at a Glance")
    st.metric(
        label="Gross Revenue Change (Yesterday vs Day Before)",
        value=f"${total_rev_yest:,.0f}",
        delta=f"{total_diff:+,.0f} ({pct_diff:+.1f}%)",
        delta_color=delta_color
    )

    # Generate summary & actions
    summary = generate_summary(total_diff, pct_diff, movers_up.iloc[0], movers_down.iloc[0], movers_up.to_dict('records'), movers_down.to_dict('records'))
    st.markdown(f"<h5><b>Yesterday AI Revenue Overview — {yesterday.date()} vs {day_before.date()}</b></h5>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:1.1em'>{summary}</div>", unsafe_allow_html=True)
    st.markdown("---")

    actions = ai_what_to_do(movers_up.to_dict('records'), movers_down.to_dict('records'))
    st.markdown("#### What to Do Next")
    for act in actions:
        st.markdown(f"- {act}", unsafe_allow_html=True)
    st.markdown("---")

    # Show movers table
    table_display = movers_all[[
        'Package', 'Dir', 'Reason', 'Comment', 'Rev Yest', '% Change', 'CPM', 'DSP Fill', 'Margin', 'IVT', 'Buyer'
    ]].copy()
    table_display['Rev Yest'] = table_display['Rev Yest'].apply(lambda x: f"${x:,.0f}")
    table_display['% Change'] = table_display['% Change'].apply(lambda x: f"{x:+.0f}%")
    table_display['Margin'] = table_display['Margin'].apply(lambda x: f"{x:.1f}% {margin_icon(x)}")
    table_display['IVT'] = table_display['IVT'].apply(lambda x: f"{x:.1f}% {ivt_icon(x)}")
    table_display['DSP Fill'] = table_display['DSP Fill'].apply(lambda x: f"{x:.1f}%")
    st.markdown(f"#### Top Movers (Up/Down) — {yesterday.date()} vs {day_before.date()}")
    st.write(
        table_display.to_html(escape=False, index=False),
        unsafe_allow_html=True
    )
    st.markdown("---")

    # AI Chatbot (optional, needs openai package and API key)
    st.subheader("🤖 Ask AI About Your Data")
    api_key = st.text_input("Enter your OpenAI API key:", type="password")
    user_q = st.text_input("Type your question about a package, e.g.: 'Why did com.tripedot.woodoku drop?'")
    ask_button = st.button("Ask AI", key="ai_insights_chat")
    if api_key and user_q and ask_button:
        import openai
        trending_pkgs = movers_up['Package'].tolist() + movers_down['Package'].tolist()
        context_rows = []
        for pkg in trending_pkgs:
            last = df_yest[df_yest['Package'] == pkg]
            prev = df_before[df_before['Package'] == pkg]
            def safe_mean(series):
                return None if len(series) == 0 else np.nanmean(series)
            last_rev = last['Gross Revenue'].sum()
            prev_rev = prev['Gross Revenue'].sum()
            last_rpm = safe_mean(last['RPM']) if 'RPM' in last.columns else None
            prev_rpm = safe_mean(prev['RPM']) if 'RPM' in prev.columns else None
            last_cpm = safe_mean(last['eCPM']) if 'eCPM' in last.columns else None
            prev_cpm = safe_mean(prev['eCPM']) if 'eCPM' in prev.columns else None
            last_fill = safe_mean(last['FillRate']) if 'FillRate' in last.columns else None
            prev_fill = safe_mean(prev['FillRate']) if 'FillRate' in prev.columns else None
            row = f"""Package: {pkg}
Yesterday Revenue: {int(last_rev)}
Day Before Revenue: {int(prev_rev)}"""
            if last_rpm is not None and prev_rpm is not None:
                row += f"\nYesterday RPM: {last_rpm:.5f}  Day Before RPM: {prev_rpm:.5f}"
            if last_cpm is not None and prev_cpm is not None:
                row += f"\nYesterday CPM: {last_cpm:.3f}  Day Before CPM: {prev_cpm:.3f}"
            if last_fill is not None and prev_fill is not None:
                row += f"\nYesterday Fill: {last_fill*100:.1f}%  Day Before Fill: {prev_fill*100:.1f}%"
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
