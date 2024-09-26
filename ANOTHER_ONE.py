import os
import streamlit as st
import pandas as pd
from pandasai import Agent

# Set your PandasAI API key
# Replace with your API key or set it in the environment variables
os.environ["PANDASAI_API_KEY"] = "YOUR_API_KEY"

# Initialize the Streamlit app
st.title("Pandas AI Data Analysis")

# File uploader for Excel files
uploaded_file = st.file_uploader("Upload an Excel file", type=["xlsx", "xls"])

# If a file is uploaded, proceed
if uploaded_file:
    try:
        # Read the uploaded Excel file into a Pandas DataFrame
        df = pd.read_excel(uploaded_file)
        st.write("### Uploaded Data", df.head())  # Display the first few rows of the DataFrame

        # Initialize the Pandas AI Agent with the uploaded DataFrame
        agent = Agent(df)

        # User question input
        user_question = st.text_input("Ask a question about the uploaded data:")

        # Process the user question when submitted
        if user_question:
            try:
                with st.spinner("Analyzing..."):
                    response = agent.chat(user_question)
                # Display the response
                st.write("### Answer", response)

                # Optional: If the response is a DataFrame, you can show it as a table
                if isinstance(response, pd.DataFrame):
                    st.write("### Resulting Data", response)
                    st.line_chart(response)  # Show a chart if the response is a DataFrame
            except Exception as e:
                st.error(f"An error occurred while analyzing the data: {e}")

    except Exception as e:
        st.error(f"Error reading the Excel file: {e}")
else:
    st.info("Please upload an Excel file to get started.")
