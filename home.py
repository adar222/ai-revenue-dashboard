import streamlit as st

def show_home():
    st.markdown(
        "<h1 style='text-align: center; font-size: 3rem; font-weight: 900; margin-top: 1em; margin-bottom: 1.5em;'>"
        "AI Revenue Optimizer"
        "</h1>",
        unsafe_allow_html=True
    )

    # Custom CSS for card hover and layout
    st.markdown("""
        <style>
        .card-btn {
            border: none;
            background: #fff;
            border-radius: 22px;
            box-shadow: 0 2px 14px #0002;
            padding: 2em 1em 1.3em 1em;
            transition: box-shadow 0.2s, transform 0.2s;
            cursor: pointer;
            width: 100%;
            margin-bottom: 0.5em;
        }
        .card-btn:hover {
            box-shadow: 0 8px 32px #3653ff44, 0 2px 14px #0001;
            transform: translateY(-6px) scale(1.03);
        }
        .card-icon {
            font-size: 2.8rem;
            line-height: 2.8rem;
        }
        .card-title {
            font-weight: bold;
            color: #3653ff;
            font-size: 1.18rem;
            margin: 0.5em 0 0.3em 0;
        }
        .card-desc {
            font-size: 1rem;
            color: #666;
            min-height: 35px;
        }
        </style>
    """, unsafe_allow_html=True)

    cards = [
        {"icon": "🧠", "title": "AI Insights", "desc": "AI-powered recommendations and trends", "tab": "AI Insights"},
        {"icon": "📊", "title": "Dashboard", "desc": "All key revenue metrics at a glance", "tab": "Dashboard"},
        {"icon": "🚦", "title": "IVT Optimization", "desc": "Flag high IVT products & recommend action", "tab": "IVT Optimization"},
        {"icon": "⚡", "title": "RPM Optimization", "desc": "Spot low RPM and minimize losses", "tab": "RPM Optimization"},
        {"icon": "🔍", "title": "Pubimps/advimps discrepancy", "desc": "Analyze publisher/advertiser impression gaps", "tab": "Pubimps/advimps discrepancy"},
    ]

    cols = st.columns(len(cards))
    for idx, card in enumerate(cards):
        with cols[idx]:
            clicked = st.button(
                label=f"{card['icon']}  {card['title']}",
                key=f"card-btn-{card['tab']}",
                help=card["desc"],
                use_container_width=True
            )
            st.markdown(
                f"""
                <div class="card-btn" onclick="window.dispatchEvent(new CustomEvent('stButtonClick', {{detail: '{card['tab']}'}}));">
                    <div class="card-icon">{card['icon']}</div>
                    <div class="card-title">{card['title']}</div>
                    <div class="card-desc">{card['desc']}</div>
                </div>
                """, unsafe_allow_html=True
            )
            if clicked:
                st.session_state["tab"] = card["tab"]
                st.rerun()

    st.markdown(
        "<div style='text-align: center; margin-top: 3em; color: #aaa;'>"
        "What do you want to optimize today? Click a card above or use the sidebar."
        "</div>",
        unsafe_allow_html=True
    )
