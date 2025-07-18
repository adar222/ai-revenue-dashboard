import streamlit as st
import pandas as pd

# === Load Excel file once and share across the app ===
EXCEL_FILE = "DemoAI.xlsx"
if "main_df" not in st.session_state:
    st.session_state["main_df"] = pd.read_excel(EXCEL_FILE)

from home import show_home
from ai_insights import show_ai_insights
from dashboard import show_dashboard
from ivt_optimization import show_ivt_optimization
from rpm_optimization import show_rpm_optimization
from filter import show_filtering
from pubimps import show_pubimps

# ---- TAB LOGIC ----
tab_list = [
    "Home",
    "AI Insights",
    "Dashboard",
    "IVT Optimization",
    "RPM Optimization",
    "Pubimps/advimps discrepancy"
]
if "tab" not in st.session_state:
    st.session_state["tab"] = "Home"

st.set_page_config(
    page_title="AI Revenue Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

with st.sidebar:
    st.title("Navigation")
    selected = st.radio(
        "Go to:",
        options=tab_list,
        index=tab_list.index(st.session_state["tab"])
    )
    st.session_state["tab"] = selected

tab = st.session_state["tab"]

# ---- MAIN TAB CONTENT ----
if tab == "Home":
    show_home()
elif tab == "AI Insights":
    show_ai_insights()
elif tab == "Dashboard":
    show_dashboard()
elif tab == "IVT Optimization":
    show_ivt_optimization()
elif tab == "RPM Optimization":
    show_rpm_optimization()
elif tab == "Pubimps/advimps discrepancy":
    show_pubimps()
