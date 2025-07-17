import streamlit as st
from home import show_home
from ai_insights import show_ai_insights
from dashboard import show_dashboard
from ivt_optimization import show_ivt_optimization
from rpm_optimization import show_rpm_optimization
from pubimps import show_pubimps

st.set_page_config(
    page_title="AI Revenue Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Sidebar Navigation ---
with st.sidebar:
    st.title("Navigation")
    tab = st.radio(
        "Go to:",
        options=[
            "Home",
            "AI Insights",
            "Dashboard",
            "IVT Optimization",
            "RPM Optimization",
            "Pubimps/advimps discrepancy"
        ],
        index=0
    )

# --- Tab Routing ---
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
