import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime

# Set page configuration
st.set_page_config(
    page_title="Healthcare Analytics Dashboard",
    initial_sidebar_state="expanded"
)

with open('styles.css')  as f:
    st.markdown(f" <style> {f.read()} </style>", unsafe_allow_html=True)

# Navigation bar
st.markdown("""
<div class="nav-container">
    <a href="#" class="nav-link active">Executive Summary</a>
    <a href="#" class="nav-link">Patient Demographics</a>
    <a href="#" class="nav-link">Hospital Performance</a>
    <a href="#" class="nav-link">Insurance & Billing Analysis</a>
    <a href="#" class="nav-link">Trends & Forecasting</a>
</div>
""", unsafe_allow_html=True)


# Add title
st.title("Executive Summary")

@st.cache_data
def load_data():
    # Raw GitHub URL
    url = "https://raw.githubusercontent.com/Dashboard-Design/Python-Dashboards/refs/heads/main/HealthCare%20Streamlit%20Dashboard/data/Healthcare%20Analysis%20Dataset.csv"
    df = pd.read_csv(url)

    df['Date of Admission'] = pd.to_datetime(df['Date of Admission'])
    df['Discharge Date'] = pd.to_datetime(df['Discharge Date'])

    # Calculate length of stay
    df['Length of Stay'] = (df['Discharge Date'] - df['Date of Admission']).dt.days

    # Add Year and Month columns for filtering
    df['Year'] = df['Date of Admission'].dt.year
    df['Month'] = df['Date of Admission'].dt.month
    df['Month Name'] = df['Date of Admission'].dt.strftime('%b')

    return df


# Load the data
try:
    df = load_data()
    
    # Create sidebar filters
    st.sidebar.header("Filters")
    
    # Year filter
    available_years = sorted(df['Year'].unique())
    selected_year = st.sidebar.selectbox(
        "Year",
        options=available_years,
        index= len(available_years) - 1  # Latest year by default
    )
    
    # Month filter
    month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    available_months = sorted(df['Month Name'].unique(), 
                            key=lambda x: month_order.index(x))
    selected_month = st.sidebar.selectbox(
        "Month",
        options=available_months,
        index= 0  # As shown in your mockup
    )
    
    # Apply filters
    if selected_year:
        df_filtered = df[df['Year'] == selected_year]
    else:
        df_filtered = df
        
    if selected_month:
        df_filtered = df_filtered[df_filtered['Month Name'] == selected_month]
    
    # Calculate metrics
    # 1. Average Length of Stay
    avg_length_of_stay = df_filtered['Length of Stay'].mean()
    
    # 2. Average Treatment Cost
    avg_treatment_cost = df_filtered['Billing Amount'].mean()
    
    # 3. Elective Admission Percentage
    elective_admission_pct = (
        len(df_filtered[df_filtered['Admission Type'] == 'Elective']) / 
        len(df_filtered) * 100
    )
    
    # 4. Patients with Inconclusive Test Results
    inconclusive_pct = (
        len(df_filtered[df_filtered['Test Results'] == 'Inconclusive']) / 
        len(df_filtered) * 100
    )
    
    # Create two columns for metrics
    col1, col2, col3, col4 = st.columns(4)
    
    # Display metrics
    with col1:
        st.metric(
            label="Average Length of Stay (Days)",
            value=f"{avg_length_of_stay:.1f}"
        )
    
    with col2:
        st.metric(
            label="Elective Admission %",
            value=f"{elective_admission_pct:.1f}%"
        )
    
    with col3:
        st.metric(
            label="Average Treatment Cost",
            value=f"${avg_treatment_cost:,.0f}"
        )
    
    with col4:
        st.metric(
            label="Patients with Inconclusive Test Results",
            value=f"{inconclusive_pct:.1f}%"
        )
    
    # Calculate Insurance Provider metrics
    st.subheader("Patients by Insurance Provider")
    
    insurance_counts = df_filtered['Insurance Provider'].value_counts()
    
    # Create columns for insurance metrics
    ins_cols = st.columns(len(insurance_counts))
    
    # Display insurance provider metrics
    for idx, (provider, count) in enumerate(insurance_counts.items()):
        with ins_cols[idx]:
            st.metric(
                label=provider,
                value=f"{count/1000:.1f}K"  # Converting to K format
            )

except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()