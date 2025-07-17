# home.py

import streamlit as st

def show_home():
    # --- Icons, Names, and Descriptions for the cards ---
    tabs = [
        {
            "name": "AI Insights",
            "icon": "🤖",
            "desc": "AI-powered recommendations and trends"
        },
        {
            "name": "Dashboard",
            "icon": "📊",
            "desc": "All key revenue metrics at a glance"
        },
        {
            "name": "IVT Optimization",
            "icon": "🚦",
            "desc": "Flag high IVT products & recommend action"
        },
        {
            "name": "RPM Optimization",
            "icon": "⚡",
            "desc": "Spot low RPM and minimize losses"
        },
        {
            "name": "Pubimps/advimps discrepancy",
            "icon": "🔍",
            "desc": "Analyze publisher/advertiser impression gaps"
        }
    ]

    st.set_page_config(page_title="AI Revenue Optimizer", layout="wide", initial_sidebar_state="expanded")
    st.markdown("""
        <style>
        .big-title {
            font-size: 3rem;
            font-weight: 700;
            text-align: center;
            margin-bottom: 1.5rem;
        }
        .cards {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 2.5rem;
        }
        .card {
            background: #fff;
            border-radius: 2rem;
            box-shadow: 0 4px 18px rgba(0,0,0,0.06);
            padding: 2.5rem 2.5rem 1.5rem 2.5rem;
            min-width: 250px;
            max-width: 270px;
            min-height: 200px;
            text-align: center;
            transition: box-shadow 0.2s, transform 0.2s;
            cursor: pointer;
            border: 2px solid #F1F1F4;
        }
        .card:hover {
            box-shadow: 0 8px 36px rgba(80,64,245,0.11);
            transform: translateY(-6px) scale(1.03);
            border: 2px solid #5040f5;
        }
        .card-icon {
            font-size: 3.2rem;
            margin-bottom: 1rem;
            display: block;
        }
        .card-title {
            font-size: 1.25rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
            color: #5040f5;
        }
        .card-desc {
            font-size: 1rem;
            color: #444;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="big-title">AI Revenue Optimizer</div>', unsafe_allow_html=True)

    st.markdown('<div class="cards">', unsafe_allow_html=True)
    for tab in tabs:
        link = f"?tab={tab['name'].replace(' ', '%20')}"
        st.markdown(f"""
            <a href="{link}" style="text-decoration: none;">
                <div class="card">
                    <span class="card-icon">{tab['icon']}</span>
                    <span class="card-title">{tab['name']}</span>
                    <div class="card-desc">{tab['desc']}</div>
                </div>
            </a>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(
        '<div style="margin-top:3rem;text-align:center;font-size:1.1rem;color:#444;">'
        'What do you want to optimize today? Click a card above to get started!'
        '</div>',
        unsafe_allow_html=True
    )
