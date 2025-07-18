import streamlit as st

def show_home():
    st.markdown(
        "<h1 style='text-align: center; font-size: 3rem; font-weight: 900; margin-top: 1em; margin-bottom: 1.5em;'>"
        "AI Revenue Optimizer"
        "</h1>",
        unsafe_allow_html=True
    )

    # --- Demo Advertiser Dropdown ---
    st.markdown(
        "<div style='text-align:center;font-size:1.15em;font-weight:600;margin-bottom:1em;'>Choose Advertiser for Demo</div>",
        unsafe_allow_html=True
    )
    adv_choices = [
        "Magnite (Demo Enabled)",
        "Pubmatic (Demo Disabled)",
        "OpenX (Demo Disabled)",
        "TripleLift (Demo Disabled)"
    ]
    selected_adv = st.selectbox(
        "",
        adv_choices,
        index=0,  # Magnite is default
        help="Only Magnite is available for demo. Others will be added in a future version.",
        key="advertiser_demo"
    )
    st.session_state["selected_advertiser"] = selected_adv.split(" ")[0]  # Get "Magnite" part

    if selected_adv != adv_choices[0]:
        st.info("This demo is available only for Magnite. Please select 'Magnite (Demo Enabled)' to use the tool.")
        st.stop()

    st.markdown("""
        <style>
        .ai-card {
            background: #fff;
            border-radius: 22px;
            box-shadow: 0 8px 32px #191c2540;
            padding: 2.2em 1.1em 1.4em 1.1em;
            text-align: center;
            margin: 0.6em 0.5em 0 0.5em;
            border: 2px solid #fff;
        }
        .card-icon {
            font-size: 2.7rem;
            margin-bottom: 0.25em;
            display: block;
        }
        .card-title {
            font-weight: 900;
            color: #3653ff;
            font-size: 1.33rem;
            margin-bottom: 0.35em;
            margin-top: 0.15em;
        }
        .card-desc {
            font-size: 1.05rem;
            color: #686868;
            min-height: 30px;
            margin-bottom: 0.1em;
        }
        </style>
    """, unsafe_allow_html=True)

    cards = [
        {"icon": "🧠", "title": "AI Insights", "desc": "AI-powered recommendations and trends", "tab": "AI Insights"},
        {"icon": "📊", "title": "Dashboard", "desc": "All key revenue metrics at a glance", "tab": "Dashboard"},
        {"icon": "🏴", "title": "IVT Optimization", "desc": "Flag high IVT products & recommend action", "tab": "IVT Optimization"},
        {"icon": "⚡", "title": "RPM Optimization", "desc": "Spot low RPM and minimize losses", "tab": "RPM Optimization"},
        {"icon": "🔍", "title": "Pubimps/advimps discrepancy", "desc": "Analyze publisher/advertiser impression gaps", "tab": "Pubimps/advimps discrepancy"},
    ]

    cols = st.columns(len(cards))
    for i, card in enumerate(cards):
        with cols[i]:
            st.markdown(
                f"""
                <div class="ai-card">
                    <span class="card-icon">{card['icon']}</span>
                    <span class="card-title">{card['title']}</span>
                    <div class="card-desc">{card['desc']}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            if st.button(f"Go to {card['title']}", key=f"cardbtn_{card['tab']}", use_container_width=True):
                st.session_state["tab"] = card["tab"]
                st.rerun()

    st.markdown(
        "<div style='text-align: center; margin-top: 3em; color: #aaa;'>"
        "What do you want to optimize today? Click a card above or use the sidebar."
        "</div>",
        unsafe_allow_html=True
    )
