import streamlit as st
from ai_insights import show_ai_insights
from dashboard import show_dashboard

st.set_page_config(page_title="AI Revenue Dashboard", layout="wide")

with st.sidebar:
    st.title("Navigation")
    tab = st.radio(
        "Go to:",
        options=["AI Insights", "Dashboard"],  # Add more here as needed
        index=0  # AI Insights as default
    )

if tab == "AI Insights":
    show_ai_insights()
elif tab == "Dashboard":
    show_dashboard()
