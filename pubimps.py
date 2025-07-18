import streamlit as st

try:
    import matplotlib.pyplot as plt
except ModuleNotFoundError:
    st.error("matplotlib is not installed. Please add `matplotlib` to requirements.txt and redeploy.")
    st.stop()

import pandas as pd

def show_pubimps():
    st.header("Pubimps/Advimps Discrepancy")

    # Get your main dataframe from session_state
    df = st.session_state.get("main_df")
    if df is None or df.empty:
        st.warning("No data loaded. Please check your Excel file.")
        return

    # Check required columns
    required_cols = ['Publisher', 'Adv Imps', 'Pub Imps', 'Gross Revenue', 'Revenue Cost']
    missing_cols = [col for col in required_cols if col not in df.columns]

    if missing_cols:
        st.warning(f"Missing columns in data: {', '.join(missing_cols)}")
        st.dataframe(df.head())  # Show the first few rows for debugging
        return

    # Example discrepancy calculation:
    df['Impression Gap'] = df['Pub Imps'] - df['Adv Imps']
    st.write("Top 10 Pubimps/Advimps discrepancies:")
    st.dataframe(df[['Publisher', 'Pub Imps', 'Adv Imps', 'Impression Gap', 'Gross Revenue', 'Revenue Cost']].sort_values('Impression Gap', ascending=False).head(10))

    # Example plot
    st.subheader("Impression Gap by Publisher")
    fig, ax = plt.subplots(figsize=(8, 4))
    plot_df = df[['Publisher', 'Impression Gap']].sort_values('Impression Gap', ascending=False).head(10)
    ax.barh(plot_df['Publisher'], plot_df['Impression Gap'])
    ax.set_xlabel('Impression Gap')
    ax.set_ylabel('Publisher')
    st.pyplot(fig)

    # Add any other analysis or visualization below!
