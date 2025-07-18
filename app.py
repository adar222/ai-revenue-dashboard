import streamlit as st
import pandas as pd

st.set_page_config(page_title="AI Revenue Optimizer", layout="wide")

# ---- Load Excel only once ----
EXCEL_FILE = "DemoAI.xlsx"
if "main_df" not in st.session_state:
    st.session_state["main_df"] = pd.read_excel(EXCEL_FILE)

TABS = [
    "Home",
    "AI Insights",
    "Dashboard",
    "IVT Optimization",
    "RPM Optimization",
    "Pubimps/advimps discrepancy"
]
if "current_tab" not in st.session_state:
    st.session_state["current_tab"] = "Home"

def go_to_tab(tab):
    st.session_state["current_tab"] = tab

# ---- Sidebar ----
with st.sidebar:
    st.markdown("## Navigation")
    tab_choice = st.radio("Go to:", TABS, index=TABS.index(st.session_state["current_tab"]))
    if tab_choice != st.session_state["current_tab"]:
        go_to_tab(tab_choice)
        st.experimental_rerun()

def render_homepage():
    st.markdown(
        "<div style='text-align:center; margin-bottom: 30px;'>"
        "<h1 style='font-size:3em; font-weight:bold;'>AI Revenue Optimizer</h1>"
        "</div>", unsafe_allow_html=True
    )
    st.write("")
    cards = [
        {
            "tab": "AI Insights",
            "icon": "🧠",
            "title": "AI Insights",
            "desc": "AI-powered recommendations and trends"
        },
        {
            "tab": "Dashboard",
            "icon": "📊",
            "title": "Dashboard",
            "desc": "All key revenue metrics at a glance"
        },
        {
            "tab": "IVT Optimization",
            "icon": "🚦",
            "title": "IVT Optimization",
            "desc": "Flag high IVT products & recommend action"
        },
        {
            "tab": "RPM Optimization",
            "icon": "⚡",
            "title": "RPM Optimization",
            "desc": "Spot low RPM and minimize losses"
        },
        {
            "tab": "Pubimps/advimps discrepancy",
            "icon": "🔍",
            "title": "Pubimps/advimps discrepancy",
            "desc": "Analyze publisher/advertiser impression gaps"
        }
    ]
    cols = st.columns(len(cards), gap="large")
    for idx, card in enumerate(cards):
        with cols[idx]:
            if st.button("", key=f"card_{card['tab']}", help=card["desc"], use_container_width=True):
                go_to_tab(card["tab"])
                st.experimental_rerun()
            st.markdown(
                f"""
                <div style="
                    margin-top:-55px;
                    margin-bottom:10px;
                    background:#fff;
                    border-radius:22px;
                    box-shadow:0 2px 12px rgba(44,62,80,.06);
                    min-height:200px;
                    padding:38px 10px 18px 10px;
                    text-align:center;
                    border: 1.5px solid #f0f1f7;">
                    <div style="font-size:44px;">{card['icon']}</div>
                    <div style="font-size:20px; font-weight:700; color:#2357f5; margin-bottom:8px;">{card['title']}</div>
                    <div style="font-size:15px; color:#666;">{card['desc']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    st.markdown(
        "<div style='text-align:center; margin-top:35px; color: #aaa; font-size:1.2em;'>"
        "What do you want to optimize today? Click a card above or use the sidebar."
        "</div>", unsafe_allow_html=True
    )

def render_ai_insights():
    st.header("AI Insights")
    st.write("AI-powered recommendations and trends coming soon.")

def render_dashboard():
    st.header("Dashboard")
    st.dataframe(st.session_state["main_df"].head())

def render_ivt_optimization():
    st.header("IVT Optimization")
    st.write("IVT Optimization logic here.")

def render_rpm_optimization():
    st.header("RPM Optimization")
    st.write("RPM Optimization logic here.")

def render_pubimps_discrepancy():
    st.header("Pubimps/advimps discrepancy")
    st.write("Discrepancy logic here.")

tab = st.session_state["current_tab"]
if tab == "Home":
    render_homepage()
elif tab == "AI Insights":
    render_ai_insights()
elif tab == "Dashboard":
    render_dashboard()
elif tab == "IVT Optimization":
    render_ivt_optimization()
elif tab == "RPM Optimization":
    render_rpm_optimization()
elif tab == "Pubimps/advimps discrepancy":
    render_pubimps_discrepancy()
else:
    render_homepage()
