import streamlit as st

def show_home():
    # --- STYLES: White BG, Modern SaaS ---
    st.markdown("""
        <style>
        html, body, [data-testid="stAppViewContainer"] {
          background: #fff !important;
        }
        .ai-card {
            background: rgba(255,255,255,0.82);
            border-radius: 22px;
            box-shadow: 0 10px 32px #191c251a;
            padding: 2.2em 1.1em 1.4em 1.1em;
            text-align: center;
            margin: 0.6em 0.5em 0 0.5em;
            border: 2.5px solid #ecebfc;
            transition: all .18s cubic-bezier(.34,1.56,.64,1);
            backdrop-filter: blur(7px);
            position: relative;
        }
        .ai-card:hover {
            box-shadow: 0 18px 48px #5466f728;
            transform: translateY(-6px) scale(1.035);
            border-color: #3653ff;
            z-index: 1;
        }
        .card-icon {
            font-size: 2.85rem;
            margin-bottom: 0.25em;
            display: block;
            transition: transform .16s;
        }
        .ai-card:hover .card-icon {
            animation: iconBounce 0.42s;
        }
        @keyframes iconBounce {
          0%   { transform: scale(1);}
          30%  { transform: scale(1.2);}
          60%  { transform: scale(0.85);}
          100% { transform: scale(1);}
        }
        .headline-glow {
            font-size: 3.1rem;
            font-weight: 900;
            text-align: center;
            margin-top: 1.3em;
            margin-bottom: 1.25em;
            color: #233358;
            text-shadow: 0 2px 10px #3653ff40, 0 0px 2px #fff8;
            font-family: 'Poppins', 'Inter', sans-serif;
            letter-spacing: 0.015em;
        }
        .demo-banner {
            position: absolute;
            top: 22px; right: 34px;
            background: rgba(44,53,150,0.13);
            color: #233358;
            padding: 0.43em 1.1em;
            border-radius: 9px;
            font-size: 1em;
            font-weight: 600;
            letter-spacing: 0.03em;
            box-shadow: 0 1px 12px #9bb8ff18;
            z-index: 100;
            display: flex;
            align-items: center;
        }
        .dropdown-helper {
            display: inline-block;
            margin-left: 0.35em;
            color: #7a85a3;
            cursor: pointer;
            font-size: 1.2em;
            vertical-align: middle;
        }
        .dropdown-row {
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 1em;
        }
        </style>
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@600;900&display=swap" rel="stylesheet">
    """, unsafe_allow_html=True)

    # --- Demo Banner and Headline ---
    st.markdown('<div class="demo-banner">🛈 Demo Mode: Only Magnite is enabled</div>', unsafe_allow_html=True)
    st.markdown('<div class="headline-glow">AI Revenue Optimizer</div>', unsafe_allow_html=True)

    # --- Demo Advertiser Dropdown ---
    st.markdown("""
        <div class="dropdown-row">
            <div style='font-size:1.15em;font-weight:600;text-align:center;'>
                Choose Advertiser for Demo
                <span class="dropdown-helper" title="This is a demo version. Only Magnite is enabled. Other advertisers are disabled for demo mode.">❔</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    adv_choices = [
        "Magnite (Demo Enabled)",
        "Pubmatic (Demo Disabled)",
        "OpenX (Demo Disabled)",
        "TripleLift (Demo Disabled)"
    ]
    selected_adv = st.selectbox(
        "",
        adv_choices,
        index=0,
        help="Only Magnite is available for demo. Others will be added in a future version.",
        key="advertiser_demo"
    )
    st.session_state["selected_advertiser"] = selected_adv.split(" ")[0]

    if selected_adv != adv_choices[0]:
        st.info("This demo is available only for Magnite. Please select 'Magnite (Demo Enabled)' to use the tool.")
        st.stop()

    # --- Main Cards ---
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
