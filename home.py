import streamlit as st

def show_home():
    st.markdown("""
        <style>
        .big-title {
            font-size: 2.8rem;
            font-weight: 700;
            text-align: center;
            margin-bottom: 2.2rem;
            margin-top: 1.5rem;
        }
        .cards {
            display: flex;
            flex-direction: row;  /* Cards will be in a row */
            flex-wrap: wrap;
            justify-content: center;
            gap: 2.5rem;
            margin-bottom: 2rem;
        }
        .card {
            background: #fff;
            border-radius: 2rem;
            box-shadow: 0 4px 18px rgba(0,0,0,0.07);
            padding: 2.2rem 2.5rem 1.7rem 2.5rem;
            min-width: 210px;
            max-width: 240px;
            min-height: 170px;
            text-align: center;
            transition: box-shadow 0.18s, transform 0.18s;
            cursor: pointer;
            border: 2px solid #F1F1F4;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .card:hover {
            box-shadow: 0 8px 36px rgba(80,64,245,0.12);
            transform: translateY(-5px) scale(1.03);
            border: 2px solid #5040f5;
        }
        .card-icon {
            font-size: 2.7rem;
            margin-bottom: 1rem;
            display: block;
        }
        .card-title {
            font-size: 1.15rem;
            font-weight: bold;
            margin-bottom: 0.45rem;
            color: #5040f5;
        }
        .card-desc {
            font-size: 1rem;
            color: #454545;
        }
        @media (max-width: 950px) {
            .cards { flex-direction: column; align-items: center;}
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="big-title">AI Revenue Optimizer</div>', unsafe_allow_html=True)

    # Define your cards: icon, title, desc, tab_name
    cards = [
        {"icon": "🧠", "title": "AI Insights", "desc": "AI-powered recommendations and trends", "tab": "AI Insights"},
        {"icon": "📊", "title": "Dashboard", "desc": "All key revenue metrics at a glance", "tab": "Dashboard"},
        {"icon": "🚦", "title": "IVT Optimization", "desc": "Flag high IVT products & recommend action", "tab": "IVT Optimization"},
        {"icon": "⚡", "title": "RPM Optimization", "desc": "Spot low RPM and minimize losses", "tab": "RPM Optimization"},
        {"icon": "🔍", "title": "Pubimps/advimps discrepancy", "desc": "Analyze publisher/advertiser impression gaps", "tab": "Pubimps/advimps discrepancy"},
    ]

    # Create the card row
    st.markdown('<div class="cards">', unsafe_allow_html=True)
    for card in cards:
        card_html = f"""
        <div class="card" onclick="window.parent.postMessage({{tab: '{card['tab']}' }}, '*');">
            <span class="card-icon">{card['icon']}</span>
            <div class="card-title">{card['title']}</div>
            <div class="card-desc">{card['desc']}</div>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(
        "<div style='text-align:center;margin-top:38px;font-size:0.98rem;color:#888;'>"
        "What do you want to optimize today? Click a card above to get started!"
        "</div>", unsafe_allow_html=True
    )

# Now, in app.py, you should import and use this:
# from home import show_home
# ...
# Add "Home" as the first tab in the sidebar
# And call show_home() when tab == "Home"
