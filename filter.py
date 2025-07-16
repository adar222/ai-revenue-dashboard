import streamlit as st
import pandas as pd

def show_filtering():

    st.title("Product Filter and Clean App")

    st.markdown("""
    Upload a CSV file. The app will:
    - Filter products where:
    - RPM > 0.001
    - Gross Revenue > 1 USD
    - Gross Revenue is not blank
    - Clean Date to show only date (no time)
    - Move **Campaign ID** to first column
    - Sort by **Campaign ID ascending**
    - Provide downloadable filtered CSV.
    """)

    uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file, sep=None, engine='python')

        st.subheader("Original Data Preview")
        st.dataframe(df.head())

        required_cols = {'RPM', 'Gross Revenue', 'Campaign ID', 'Date'}
        if required_cols.issubset(df.columns):
            # Remove rows where Gross Revenue is blank or NaN
            df = df[df['Gross Revenue'].notna()]

            # Filter: keep only rows where RPM > 0.001 and Gross Revenue > 1
            filtered_df = df[(df['RPM'] > 0.001) & (df['Gross Revenue'] > 1)].copy()

            # Clean Date column: keep only date part
            filtered_df['Date'] = pd.to_datetime(filtered_df['Date']).dt.date

            # Move Campaign ID to first column
            cols = filtered_df.columns.tolist()
            cols.remove('Campaign ID')
            cols = ['Campaign ID'] + cols
            filtered_df = filtered_df[cols]

            # Sort by Campaign ID ascending
            filtered_df = filtered_df.sort_values(by='Campaign ID', ascending=True)

            st.subheader("Filtered, Cleaned, Sorted Data Preview")
            st.dataframe(filtered_df)

            def convert_df_to_csv(df):
                return df.to_csv(index=False).encode('utf-8')

            csv = convert_df_to_csv(filtered_df)

            st.download_button(
                label="Download filtered CSV",
                data=csv,
                file_name='filtered_cleaned_data.csv',
                mime='text/csv',
            )
        else:
            st.error(f"The uploaded file must contain columns: {', '.join(required_cols)}")
    else:
        st.info("Please upload a CSV file to begin.")
