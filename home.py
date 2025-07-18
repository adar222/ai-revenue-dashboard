import streamlit as st

def show_home():
    st.markdown(
        "<h1 style='text-align: center; font-size: 3rem; font-weight: 900; margin-top: 1em; margin-bottom: 1.5em;'>"
        "AI Revenue Optimizer"
        "</h1>",
        unsafe_allow_html=True
    )

    # Card CSS (pretty, hover, shadow, rounded, etc.)
    st.markdown("""
        <style>
        .card-btn {
            display: block;
            border: none;
            background: #fff;
            border-radius: 22px;
            box-shadow: 0 2px 14px #0002;
            padding: 2.5em 1.3em 1.5em 1.3em;
            margin-bottom: 0.5em;
            transition: box-shadow 0.22s, transform 0.18s;
            cursor: pointer;
            width: 100%;
            text-align: center;
        }
        .card-btn:hover {
            box-shadow: 0 8px 32px #3653ff44, 0 2px 14px #0001;
            transform: translateY(-5px) scale(1.025);
        }
        .card-icon {
            font-size: 3rem;
            margin-bottom: 0.2em;
        }
        .card-title {
            font-weight: bold;
            color: #2357f5;
            font-size: 1.22rem;
            margin-bottom: 0.30em;
        }
        .card-desc {
            font-size: 1.04rem;
            color: #666;
            min-height: 36px;
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
                "",
                key=f"card-btn-{card['tab']}",
                help=card["desc"],
                use_container_width=True
            )
            st.markdown(
                f"""
                <div class="card-btn">
                    <div class="card-icon">{card['icon']}</div>
                    <div class="card-title">{card['title']}</div>
                    <div class="card-desc">{card['desc']}</div>
                </div>
                """,
                unsafe_allow_html=True
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
