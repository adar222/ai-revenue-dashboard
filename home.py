import streamlit as st

def show_home():
    st.markdown(
        "<h1 style='text-align: center; font-size: 3rem; font-weight: 900; margin-top: 1em; margin-bottom: 1.5em;'>"
        "AI Revenue Optimizer"
        "</h1>",
        unsafe_allow_html=True
    )

    # --- Card info: tab value MUST match tab_list in app.py ---
    cards = [
        {
            "icon": "🧠",
            "title": "AI Insights",
            "desc": "AI-powered recommendations and trends",
            "tab": "AI Insights",
        },
        {
            "icon": "📊",
            "title": "Dashboard",
            "desc": "All key revenue metrics at a glance",
            "tab": "Dashboard",
        },
        {
            "icon": "🚦",
            "title": "IVT Optimization",
            "desc": "Flag high IVT products & recommend action",
            "tab": "IVT Optimization",
        },
        {
            "icon": "⚡",
            "title": "RPM Optimization",
            "desc": "Spot low RPM and minimize losses",
            "tab": "RPM Optimization",
        },
        {
            "icon": "🔍",
            "title": "Pubimps/advimps discrepancy",
            "desc": "Analyze publisher/advertiser impression gaps",
            "tab": "Pubimps/advimps discrepancy",
        },
    ]

    # Add CSS for hover effect and nicer card style
    st.markdown("""
        <style>
        .ai-card {
            background: #fff;
            border-radius: 22px;
            box-shadow: 0 8px 32px #191c2540;
            padding: 2.2em 1.1em;
            text-align: center;
            cursor: pointer;
            margin: 0.6em 0.5em;
            transition: box-shadow 0.2s, transform 0.2s;
            border: 2px solid #fff;
        }
        .ai-card:hover {
            box-shadow: 0 6px 36px #3653ff55;
            transform: translateY(-4px) scale(1.04);
            border: 2px solid #3653ff;
        }
        .ai-card .card-title {
            font-weight: 900;
            color: #3653ff;
            font-size: 1.35rem;
            margin: 0.3em 0 0.5em 0;
        }
        .ai-card .card-desc {
            font-size: 1.01rem;
            color: #686868;
            min-height: 32px;
        }
        </style>
    """, unsafe_allow_html=True)

    cols = st.columns(len(cards))
    for i, card in enumerate(cards):
        with cols[i]:
            # Streamlit's st.button returns True when clicked!
            if st.button(
                f"<div class='ai-card'><div style='font-size:2.7rem'>{card['icon']}</div>"
                f"<div class='card-title'>{card['title']}</div>"
                f"<div class='card-desc'>{card['desc']}</div></div>",
                key=f"maincard_{card['tab']}",
                use_container_width=True,
                help=card['desc'],
                type="secondary",
                args=(),
                kwargs={},
            ):
                st.session_state["tab"] = card["tab"]
                st.experimental_rerun()  # or st.rerun() if Streamlit >= 1.32

    st.markdown(
        "<div style='text-align: center; margin-top: 3em; color: #aaa;'>"
        "What do you want to optimize today? Click a card above or use the sidebar."
        "</div>",
        unsafe_allow_html=True
    )
