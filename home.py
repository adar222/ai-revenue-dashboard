import streamlit as st

def show_home():
    st.markdown(
        "<h1 style='text-align: center; font-size: 3rem; font-weight: 900; margin-top: 1em; margin-bottom: 1.5em;'>"
        "AI Revenue Optimizer"
        "</h1>",
        unsafe_allow_html=True
    )

    # Card info
    cards = [
        {"icon": "🧠", "title": "AI Insights", "desc": "AI-powered recommendations and trends", "tab": "AI Insights"},
        {"icon": "📊", "title": "Dashboard", "desc": "All key revenue metrics at a glance", "tab": "Dashboard"},
        {"icon": "🚦", "title": "IVT Optimization", "desc": "Flag high IVT products & recommend action", "tab": "IVT Optimization"},
        {"icon": "⚡", "title": "RPM Optimization", "desc": "Spot low RPM and minimize losses", "tab": "RPM Optimization"},
        {"icon": "🔍", "title": "Pubimps/advimps discrepancy", "desc": "Analyze publisher/advertiser impression gaps", "tab": "Pubimps/advimps discrepancy"},
    ]

    st.markdown("""
        <style>
        div[data-testid="column"] > div > button {
            background: #fff !important;
            border-radius: 22px !important;
            box-shadow: 0 8px 32px #191c2540 !important;
            padding: 2.2em 1.1em !important;
            min-height: 220px;
            text-align: center;
            cursor: pointer;
            transition: box-shadow 0.2s, transform 0.2s;
            border: 2px solid #fff !important;
            font-size: 1.09rem !important;
        }
        div[data-testid="column"] > div > button:hover {
            box-shadow: 0 6px 36px #3653ff55 !important;
            transform: translateY(-4px) scale(1.04);
            border: 2px solid #3653ff !important;
        }
        .card-icon {
            font-size: 2.7rem; line-height:2.7rem; display:block; margin-bottom:0.2em;
        }
        .card-title {
            font-weight:900; color:#3653ff; font-size:1.25rem; margin-bottom:0.3em;
        }
        .card-desc {
            font-size:1.01rem; color:#686868; min-height:32px;
        }
        </style>
    """, unsafe_allow_html=True)

    cols = st.columns(len(cards))
    for i, card in enumerate(cards):
        with cols[i]:
            if st.button(
                f"<span class='card-icon'>{card['icon']}</span>"
                f"<span class='card-title'>{card['title']}</span><br>"
                f"<span class='card-desc'>{card['desc']}</span>",
                key=f"maincard_{card['tab']}",
                use_container_width=True,
                help=card['desc'],
            ):
                st.session_state["tab"] = card["tab"]
                st.rerun()

    st.markdown(
        "<div style='text-align: center; margin-top: 3em; color: #aaa;'>"
        "What do you want to optimize today? Click a card above or use the sidebar."
        "</div>",
        unsafe_allow_html=True
    )
