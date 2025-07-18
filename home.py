import streamlit as st

def show_home():
    st.markdown("<h1 style='text-align: center; font-size: 2.5em;'>AI Revenue Optimizer</h1>", unsafe_allow_html=True)
    st.markdown("## ")

    # Row layout
    cols = st.columns(5)
    cards = [
        {
            "icon": "💡",
            "tab": "AI Insights",
            "title": "AI Insights",
            "desc": "AI-powered revenue analysis."
        },
        {
            "icon": "📊",
            "tab": "Dashboard",
            "title": "Dashboard",
            "desc": "Key metrics and trends."
        },
        {
            "icon": "🦠",
            "tab": "IVT Optimization",
            "title": "IVT Optimization",
            "desc": "Spot and fix IVT issues."
        },
        {
            "icon": "🚦",
            "tab": "RPM Optimization",
            "title": "RPM Optimization",
            "desc": "Identify low-RPM products."
        },
        {
            "icon": "🔀",
            "tab": "Pubimps/advimps discrepancy",
            "title": "Pubimps/advimps discrepancy",
            "desc": "See impression mismatches."
        }
    ]
    for i, card in enumerate(cards):
        with cols[i]:
            if st.button(f"{card['icon']}\n**{card['title']}**\n{card['desc']}", key=f"card_{i}"):
                st.session_state["tab"] = card["tab"]
                st.experimental_rerun()
