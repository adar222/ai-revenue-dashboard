import streamlit as st
import pandas as pd

def show_IVT():
    st.title("IVT Spike Detection App")

    uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx"])

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        
        # Preprocess
        df['Date'] = pd.to_datetime(df['Date'])
        
        # Group by Date, Advertiser, Channel, Package
        grouped = df.groupby(['Date', 'Advertiser', 'Channel', 'Package'])['IVT (%)'].mean().reset_index()
        
        # Calculate baseline mean and std dev for each Advertiser+Channel+Package
        baseline = grouped.groupby(['Advertiser', 'Channel', 'Package'])['IVT (%)'].agg(['mean', 'std']).reset_index()
        baseline.rename(columns={'mean': 'baseline_mean', 'std': 'baseline_std'}, inplace=True)
        
        # Merge
        merged = pd.merge(grouped, baseline, on=['Advertiser', 'Channel', 'Package'], how='left')
        
        # Spike condition
        merged['Spike'] = merged['IVT (%)'] > (merged['baseline_mean'] + 2 * merged['baseline_std'])
        
        # Show results
        spikes = merged[merged['Spike']]
        
        st.subheader("Detected IVT Spikes")
        st.dataframe(spikes)
        
        st.markdown(f"**Total spikes detected:** {spikes.shape[0]}")
