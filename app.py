import streamlit as st
from ai_insights import show_ai_insights
from dashboard import show_dashboard
from ivt_optimization import show_ivt_optimization
from rpm_optimization import show_rpm_optimization
from discrepancy_optimization import show_discrepancy_optimization
from filter import show_filtering
from pubimps import show_pubimps
from IVT import show_IVT

st.set_page_config(
    page_title="AI Revenue Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

with st.sidebar:
    st.title("Navigation")
    tab = st.radio(
        "Go to:",
        options=[
            "AI Insights",
            "Dashboard",
            "IVT Optimization",
            "RPM Optimization",
            "Discrepancy Optimization"
            "Filtering low revenue and RPM",
            "Pubimps/advimps discrepancy",
            "IVT checker"
        ],
        index=0
    )

if tab == "AI Insights":
    show_ai_insights()
elif tab == "Dashboard":
    show_dashboard()
elif tab == "IVT Optimization":
    show_ivt_optimization()
elif tab == "RPM Optimization":
    show_rpm_optimization()
elif tab == "Discrepancy Optimization":
    show_discrepancy_optimization()
elif tab == "Pubimps/advimps discrepancy":
    show_pubimps()
elif tab == "Filtering low revenue and RPM":
    show_filtering()
elif page == "IVT checker":
    show_IVT()
