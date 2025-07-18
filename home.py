import streamlit as st

def show_home():
    st.markdown(
        "<h1 style='text-align: center; font-size: 3rem; font-weight: 900; margin-top: 1em; margin-bottom: 1.5em;'>"
        "AI Revenue Optimizer"
        "</h1>",
        unsafe_allow_html=True
    )

    # Define your cards
    cards = [
        {
            "icon": "🧠",
            "title": "AI Insights",
            "desc": "AI-powered recommendations and trends",
        },
        {
            "icon": "📊",
            "title": "Dashboard",
            "desc": "All key revenue metrics at a glance",
        },
        {
            "icon": "🚦",
            "title": "IVT Optimization",
            "desc": "Flag high IVT products & recommend action",
        },
        {
            "icon": "⚡",
            "title": "RPM Optimization",
            "desc": "Spot low RPM and minimize losses",
        },
        {
            "icon": "🔍",
            "title": "Pubimps/advimps discrepancy",
            "desc": "Analyze publisher/advertiser impression gaps",
        },
    ]

    # Make cards appear in a row
    cols = st.columns(len(cards))
    for idx, card in enumerate(cards):
        with cols[idx]:
            st.markdown(
                f"""
                <div style="background: #fff; border-radius: 18px; box-shadow: 0 2px 12px #0001; padding: 2em 1em; text-align: center; cursor: pointer;">
                    <div style="font-size: 2.5rem;">{card["icon"]}</div>
                    <div style="font-weight: bold; color: #3653ff; font-size: 1.1rem; margin: 0.3em 0 0.4em 0;">{card["title"]}</div>
                    <div style="font-size: 0.97rem; color: #777; min-height: 35px;">{card["desc"]}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown(
        "<div style='text-align: center; margin-top: 3em; color: #aaa;'>"
        "What do you want to optimize today? Click a card above or use the sidebar."
        "</div>",
        unsafe_allow_html=True
    )
