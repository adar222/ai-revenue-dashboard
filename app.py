import streamlit as st
import pandas as pd

# ========= Persistent Excel Load =========
EXCEL_FILE = "DemoAI.xlsx"
if "main_df" not in st.session_state:
    st.session_state["main_df"] = pd.read_excel(EXCEL_FILE)

# ========= Navigation State =========
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

# ========= Sidebar Navigation =========
with st.sidebar:
    st.markdown("<h2 style='margin-bottom:0.2em;'>Navigation</h2>", unsafe_allow_html=True)
    st.write("Go to:")
    selected = st.radio("", TABS, index=TABS.index(st.session_state["current_tab"]))
    if selected != st.session_state["current_tab"]:
        go_to_tab(selected)

# ========= Home Page with Clickable Cards =========
def render_homepage():
    st.markdown(
        """
        <div style="text-align:center; margin-bottom: 30px;">
            <h1 style="font-size:3em; font-weight:bold;">AI Revenue Optimizer</h1>
        </div>
        """, unsafe_allow_html=True
    )

    card_info = [
        {"label": "AI Insights", "desc": "AI-powered recommendations and trends", "icon": "🧠"},
        {"label": "Dashboard", "desc": "All key revenue metrics at a glance", "icon": "📊"},
        {"label": "IVT Optimization", "desc": "Flag high IVT products & recommend action", "icon": "🚦"},
        {"label": "RPM Optimization", "desc": "Spot low RPM and minimize losses", "icon": "⚡"},
        {"label": "Pubimps/advimps discrepancy", "desc": "Analyze publisher/advertiser impression gaps", "icon": "🔍"},
    ]

    cols = st.columns(len(card_info))
    for idx, card in enumerate(card_info):
        with cols[idx]:
            if st.button(
                f"<div style='background:#fff; border-radius:20px; box-shadow:0 2px 16px rgba(0,0,0,0.08); padding:32px 8px 20px 8px; margin:10px 0 0 0; min-height:200px; text-align:center;'>"
                f"<div style='font-size:48px;'>{card['icon']}</div>"
                f"<div style='font-size:20px; color:#2357f5; font-weight:700; margin-bottom:10px;'>{card['label']}</div>"
                f"<div style='font-size:16px; color:#666;'>{card['desc']}</div>"
                f"</div>",
                key=f"card_btn_{card['label']}",
                help=card["desc"],
                use_container_width=True,
                # unsafe_allow_html=True  # Streamlit button does not support HTML directly, so icons will be basic
            ):
                go_to_tab(card["label"])
    st.write("")
    st.markdown(
        "<div style='text-align:center; margin-top:30px; color: #aaa; font-size:1.2em;'>"
        "What do you want to optimize today? Click a card above or use the sidebar."
        "</div>", unsafe_allow_html=True
    )

# ========= Feature Tab Functions =========
def render_ai_insights():
    st.header("AI Insights")
    st.write("AI-powered recommendations and trends coming soon!")
    # Example: st.write(st.session_state["main_df"].head())

def render_dashboard():
    st.header("Dashboard")
    st.write("All key revenue metrics at a glance.")
    st.dataframe(st.session_state["main_df"].head())

def render_ivt_optimization():
    st.header("IVT Optimization")
    st.write("Flag high IVT products & recommend action")
    df = st.session_state["main_df"]
    if "RPM" in df.columns and "gross revenue" in df.columns:
        to_block = df.query("RPM <= 0.001 and (gross revenue <= 1 or gross revenue.isnull())")
        st.dataframe(to_block[["product", "RPM", "gross revenue"]])
    else:
        st.info("No RPM or gross revenue columns in your Excel.")

def render_rpm_optimization():
    st.header("RPM Optimization")
    st.write("Spot low RPM and minimize losses")
    # Add your logic here

def render_pubimps_discrepancy():
    st.header("Pubimps/advimps discrepancy")
    st.write("Analyze publisher/advertiser impression gaps")
    # Add your logic here

# ========= Main Page Routing =========
if st.session_state["current_tab"] == "Home":
    render_homepage()
elif st.session_state["current_tab"] == "AI Insights":
    render_ai_insights()
elif st.session_state["current_tab"] == "Dashboard":
    render_dashboard()
elif st.session_state["current_tab"] == "IVT Optimization":
    render_ivt_optimization()
elif st.session_state["current_tab"] == "RPM Optimization":
    render_rpm_optimization()
elif st.session_state["current_tab"] == "Pubimps/advimps discrepancy":
    render_pubimps_discrepancy()
else:
    render_homepage()
