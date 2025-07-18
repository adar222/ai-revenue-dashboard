import streamlit as st
import pandas as pd

# ---- Config ----
st.set_page_config(page_title="AI Revenue Optimizer", layout="wide")

# ---- Persistent Excel ----
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

# ---- Card Info ----
card_info = [
    {
        "tab": "AI Insights",
        "emoji": "🧠",
        "title": "AI Insights",
        "desc": "AI-powered recommendations and trends"
    },
    {
        "tab": "Dashboard",
        "emoji": "📊",
        "title": "Dashboard",
        "desc": "All key revenue metrics at a glance"
    },
    {
        "tab": "IVT Optimization",
        "emoji": "🚦",
        "title": "IVT Optimization",
        "desc": "Flag high IVT products & recommend action"
    },
    {
        "tab": "RPM Optimization",
        "emoji": "⚡",
        "title": "RPM Optimization",
        "desc": "Spot low RPM and minimize losses"
    },
    {
        "tab": "Pubimps/advimps discrepancy",
        "emoji": "🔍",
        "title": "Pubimps/advimps discrepancy",
        "desc": "Analyze publisher/advertiser impression gaps"
    }
]

def card_button(card):
    return st.button(
        f"{card['emoji']}  {card['title']}\n{card['desc']}",
        key=f"card_btn_{card['tab']}",
        help=card["desc"],
        use_container_width=True
    )

# ---- Home Page with Clickable Cards ----
def render_homepage():
    st.markdown(
        "<h1 style='text-align:center; font-size:3em; font-weight:bold;'>AI Revenue Optimizer</h1>",
        unsafe_allow_html=True
    )
    st.write("")
    cols = st.columns(len(card_info), gap="large")
    clicked = None
    for idx, card in enumerate(card_info):
        with cols[idx]:
            btn = st.button(
                f"{card['emoji']}\n\n**{card['title']}**\n\n{card['desc']}",
                key=f"card_{card['tab']}",
                use_container_width=True,
                help=card["desc"]
            )
            if btn:
                clicked = card["tab"]
    st.write("")
    st.markdown(
        "<div style='text-align:center; margin-top:30px; color: #aaa; font-size:1.2em;'>"
        "What do you want to optimize today? Click a card above or use the sidebar."
        "</div>", unsafe_allow_html=True
    )
    if clicked:
        go_to_tab(clicked)
        st.experimental_rerun()  # Needed to switch instantly

# ---- Tab Pages ----
def render_ai_insights():
    st.header("AI Insights")
    st.write("AI-powered recommendations and trends coming soon!")

def render_dashboard():
    st.header("Dashboard")
    st.dataframe(st.session_state["main_df"].head())

def render_ivt_optimization():
    st.header("IVT Optimization")
    st.write("IVT logic here.")

def render_rpm_optimization():
    st.header("RPM Optimization")
    st.write("RPM logic here.")

def render_pubimps_discrepancy():
    st.header("Pubimps/advimps discrepancy")
    st.write("Discrepancy logic here.")

# ---- Routing ----
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
