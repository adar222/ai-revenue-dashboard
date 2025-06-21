import streamlit as st
import pandas as pd
import numpy as np
import openai

def show_dashboard():
    st.title("📈 AI-Powered Revenue Action Center – Dashboard")

    # Check for main_df in session state
    if "main_df" not in st.session_state:
        st.info("Please upload your Excel file in the AI Insights tab first.")
        return

    df = st.session_state["main_df"]

    # Date logic
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

    # ----------- AI Chatbot Section -----------
    st.markdown("---")
    st.subheader("🤖 Ask AI About Your Data")

    api_key = st.text_input("Enter your OpenAI API key:", type="password")
    user_q = st.text_input("Type your question about a package, e.g.: 'Why did com.tripedot.woodoku drop?'")
    ask_button = st.button("Ask AI")
    if api_key and user_q and ask_button:
        trending_pkgs = merged['Package'].tolist()
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
            last_cpm = safe_mean(last['eCPM']) if 'eCPM' in last.columns else None
            prev_cpm = safe_mean(prev['eCPM']) if 'eCPM' in prev.columns else None
            last_fill = safe_mean(last['FillRate']) if 'FillRate' in last.columns else None
            prev_fill = safe_mean(prev['FillRate']) if 'FillRate' in prev.columns else None
            row = f"""Package: {pkg}
Last3d Revenue: {int(last_rev)}
Prev3d Revenue: {int(prev_rev)}"""
            if last_rpm is not None and prev_rpm is not None:
                row += f"\nLast3d RPM: {last_rpm:.2f}  Prev3d RPM: {prev_rpm:.2f}"
            if last_cpm is not None and prev_cpm is not None:
                row += f"\nLast3d CPM: {last_cpm:.2f}  Prev3d CPM: {prev_cpm:.2f}"
            if last_fill is not None and prev_fill is not None:
                row += f"\nLast3d Fill Rate: {last_fill:.2f}  Prev3d Fill Rate: {prev_fill:.2f}"
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
