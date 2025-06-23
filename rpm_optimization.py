import streamlit as st
import pandas as pd
import numpy as np

def show_rpm_optimization():
    st.header("⚡ RPM Optimization")

    # Always pull the data from session_state
    df = st.session_state.get("main_df")
    if df is None:
        st.info("Please upload your Excel file in the AI Insights tab.")
        return

    # Example logic: show packages with low RPM
    rpm_threshold = st.number_input("Show products with RPM below:", min_value=0.0, max_value=1.0, value=0.05, step=0.01)
    if "RPM" in df.columns:
        low_rpm_df = df[df["RPM"] < rpm_threshold]
        st.subheader("Low RPM Products")
        st.dataframe(low_rpm_df, use_container_width=True)
    else:
        st.warning("The uploaded file does not have an 'RPM' column.")
