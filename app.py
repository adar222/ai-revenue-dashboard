import streamlit as st
from ai_insights import show_ai_insights
from dashboard import show_dashboard
from ivt_optimization import show_ivt_optimization
from rpm_optimization import show_rpm_optimization
from discrepancy_optimization import show_discrepancy_optimization

st.set_page_config(page_title="AI Revenue Dashboard", layout="wide")

with st.sidebar:
    st.title("Navigation")
    tab = st.radio(
        "Go to:",
        options=[
            "AI Insights",
            "IVT Optimization",
            "RPM Optimization",
            "Discrepancy Optimization",
            "Dashboard"
        ],
        index=0  # AI Insights as default
    )

if tab == "AI Insights":
    show_ai_insights()
elif tab == "IVT Optimization":
    show_ivt_optimization()
elif tab == "RPM Optimization":
    show_rpm_optimization()
elif tab == "Discrepancy Optimization":
    show_discrepancy_optimization()
elif tab == "Dashboard":
    show_dashboard()
