import streamlit as st
from utils import initialize_page, load_data, create_sidebar, create_page_navigation

# Initialize page
initialize_page()

try:
    # Load data
    df = load_data()
    
    # Create sidebar
    current_start, current_end, prev_start, prev_end, comparison_label, filtered_df = create_sidebar(df)
    
    st.session_state['current_page'] = "Trends_and_Forecasting"
    
    # Create navigation
    create_page_navigation()
    
    # Page content
    st.header("Trends_and_Forecasting")
    st.info("Trends_and_Forecasting content is under development")

except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()