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
            "tab": "AI Insights"
        },
        {
            "icon": "📊",
            "title": "Dashboard",
            "desc": "All key revenue metrics at a glance",
            "tab": "Dashboard"
        },
        {
            "icon": "🚦",
            "title": "IVT Optimization",
            "desc": "Flag high IVT products & recommend action",
            "tab": "IVT Optimization"
        },
        {
            "icon": "⚡",
            "title": "RPM Optimization",
            "desc": "Spot low RPM and minimize losses",
            "tab": "RPM Optimization"
        },
        {
            "icon": "🔍",
            "title": "Pubimps/advimps discrepancy",
            "desc": "Analyze publisher/advertiser impression gaps",
            "tab": "Pubimps/advimps discrepancy"
        },
    ]

    cols = st.columns(len(cards))
    for idx, card in enumerate(cards):
        with cols[idx]:
            if st.button(
                f"{card['icon']} {card['title']}", 
                key=f"card-btn-{card['tab']}", 
                help=card["desc"],
                use_container_width=True
            ):
                st.session_state["tab"] = card["tab"]
                st.rerun()
            st.markdown(
                f"""<div style="text-align: center; font-size: 0.98rem; color: #777;">{card['desc']}</div>""",
                unsafe_allow_html=True
            )

    st.markdown(
        "<div style='text-align: center; margin-top: 3em; color: #aaa;'>"
        "What do you want to optimize today? Click a card above or use the sidebar."
        "</div>",
        unsafe_allow_html=True
    )
