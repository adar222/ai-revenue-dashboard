import streamlit as st

def show_rpm_optimization():
    st.header("RPM Optimization")
    df = st.session_state.get('main_df')
    if df is None:
        st.info("Please upload your Excel file in the AI Insights tab.")
        return
    # ... rest of your logic ...
