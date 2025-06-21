import streamlit as st
from ai_insights import show_ai_insights
from dashboard import show_dashboard
from ivt_optimization import show_ivt_optimization
from rpm_optimization import show_rpm_optimization
from discrepancy_optimization import show_discrepancy_optimization

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
        ],
        index=0
    )

# --------- File upload handled ONLY in AI Insights ---------
if "main_df" not in st.session_state:
    st.session_state["main_df"] = None

if tab == "AI Insights":
    # The upload logic and DataFrame save should be inside show_ai_insights()
    show_ai_insights()
else:
    # For all other tabs, get the DataFrame from session state
    df = st.session_state.get("main_df", None)
    if df is None:
        st.warning("Please upload your Excel file in the 'AI Insights' tab first.")
    elif tab == "Dashboard":
        show_dashboard(df)
    elif tab == "IVT Optimization":
        show_ivt_optimization(df)
    elif tab == "RPM Optimization":
        show_rpm_optimization(df)
    elif tab == "Discrepancy Optimization":
        show_discrepancy_optimization(df)
