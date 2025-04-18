# utils.py
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import base64

def load_clusters():
    url = "data/clustered_patients.csv"
    df = pd.read_csv(url)
    
    df['Date of Admission'] = pd.to_datetime(df['Date of Admission'])
    df['Discharge Date'] = pd.to_datetime(df['Discharge Date'])
    df['Length of Stay'] = (df['Discharge Date'] - df['Date of Admission']).dt.days
    df['Year'] = df['Date of Admission'].dt.year

    df.Cluster += 1     # clusters will be 1-6

    df['Cluster'] = df['Cluster'].apply(lambda x: 'Cluster ' + str(x) )
    
    return df

def img_to_base64(img_path):
    with open(img_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

@st.cache_data
def load_data():
    url = "data/Healthcare Analysis Dataset.csv"
    df = pd.read_csv(url)

    df['Date of Admission'] = pd.to_datetime(df['Date of Admission'])
    df['Discharge Date'] = pd.to_datetime(df['Discharge Date'])
    df['Length of Stay'] = (df['Discharge Date'] - df['Date of Admission']).dt.days
    df['Year'] = df['Date of Admission'].dt.year
    df['Month'] = df['Date of Admission'].dt.month
    df['Quarter'] = df['Date of Admission'].dt.quarter

    return df

def process_date_ranges(scenario, max_date):
    if scenario == "Last Month":
        # Get current month dates
        current_month = max_date.month
        current_year = max_date.year
        day_of_month = max_date.day
        
        # Current period: From 1st of current month to current day
        current_start = pd.Timestamp(year=current_year, month=current_month, day=1)
        current_end = max_date
        
        # Previous month
        if current_month == 1:  # January
            prev_month = 12
            prev_year = current_year - 1
        else:
            prev_month = current_month - 1
            prev_year = current_year
        
        # Previous period: From 1st of previous month to same day of previous month
        prev_start = pd.Timestamp(year=prev_year, month=prev_month, day=1)
        try:
            prev_end = pd.Timestamp(year=prev_year, month=prev_month, day=day_of_month)
        except ValueError:
            # If day doesn't exist in previous month (e.g., March 31 -> Feb 28/29)
            if prev_month == 2:  # February
                prev_end = pd.Timestamp(year=prev_year, month=prev_month, day=29) if (prev_year % 4 == 0 and (prev_year % 100 != 0 or prev_year % 400 == 0)) else pd.Timestamp(year=prev_year, month=prev_month, day=28)
            else:
                last_day = pd.Timestamp(year=prev_year, month=prev_month+1, day=1) - timedelta(days=1)
                prev_end = last_day
        
        comparison_label = "vs PM"
        
    elif scenario == "Last Quarter":
        # Get current quarter dates
        current_quarter = (max_date.month - 1) // 3 + 1
        current_year = max_date.year
        
        # Calculate the start of the current quarter
        current_quarter_start = pd.Timestamp(year=current_year, month=((current_quarter-1)*3)+1, day=1)
        
        # Current period is from start of current quarter to max_date
        current_start = current_quarter_start
        current_end = max_date
        
        # Calculate days into quarter
        days_into_quarter = (max_date - current_quarter_start).days - 1
        
        # Calculate previous quarter
        if current_quarter == 1:  # Q1
            prev_quarter = 4
            prev_year = current_year - 1
        else:
            prev_quarter = current_quarter - 1
            prev_year = current_year
        
        # Previous period start
        prev_start = pd.Timestamp(year=prev_year, month=((prev_quarter-1)*3)+1, day=1)
        
        # Previous period end is same number of days into previous quarter
        prev_end = prev_start + timedelta(days=days_into_quarter)
        
        comparison_label = "vs PQ"

    elif scenario == "Last Year":
        # Get current year dates up to max_date
        current_year = max_date.year
        
        # Calculate days into year
        year_start = pd.Timestamp(year=current_year, month=1, day=1)
        days_into_year = (max_date - year_start).days - 1
        
        # Current period: From Jan 1 to max_date of current year
        current_start = year_start
        current_end = max_date
        
        # Previous period: Same number of days into previous year
        prev_year = current_year - 1
        prev_start = pd.Timestamp(year=prev_year, month=1, day=1)
        prev_end = prev_start + timedelta(days=days_into_year)
        
        comparison_label = "vs PY"
        
    else:  # Custom
        # Date range picker for custom date selection
        date_range = st.sidebar.date_input(
            "Select Date Range",
            value=(max_date - timedelta(days=30), max_date),
            min_value=pd.Timestamp('2020-01-01').date(),  # Adjust based on your data
            max_value=max_date.date()
        )
        
        if len(date_range) == 2:
            current_start = pd.Timestamp(date_range[0])
            current_end = pd.Timestamp(date_range[1])
            prev_start = None
            prev_end = None
            comparison_label = ""
        else:
            st.error("Please select both start and end dates")
            current_start = max_date - timedelta(days=30)
            current_end = max_date
            prev_start = None
            prev_end = None
            comparison_label = ""

    # Display selected date range
    st.sidebar.markdown(f"""
        <div class="simpleTextFirst">
            <p>Selected range:</p>                
            <p class="textBlak">{current_start.strftime('%b %d, %Y')} - {current_end.strftime('%b %d, %Y')}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Display comparison date range if available
    if prev_start is not None and prev_end is not None:
        st.sidebar.markdown(f"""
            <div class="simpleText">
                <p>Comparison:</p>
                <p class="textBlak">{prev_start.strftime('%b %d, %Y')} - {prev_end.strftime('%b %d, %Y')}</p>
            </div>    
            """, unsafe_allow_html=True)
        
    st.sidebar.markdown("<hr>", unsafe_allow_html=True)    

    return current_start, current_end, prev_start, prev_end, comparison_label

def create_page_navigation():
    # Get current page path
    current_page = st.session_state.get('current_page', 'Executive Summary')
    
    # Create navigation with a single continuous line
    st.markdown(f"""
    <div class="stTabs">
        <div data-baseweb="tab-list">
            <a target="_self" href="/" class="nav-link" data-active="{'true' if current_page == 'Executive Summary' else 'false'}">Executive Summary</a>
            <a target="_self" href="/Patient_Demographics" class="nav-link" data-active="{'true' if current_page == 'Patient Demographics' else 'false'}">Patient Demographics</a>
            <a target="_self" href="/Hospital_Performance" class="nav-link" data-active="{'true' if current_page == 'Hospital Performance' else 'false'}">Hospital Performance</a>
            <a target="_self" href="/Insurance_&_Billing" class="nav-link" data-active="{'true' if current_page == 'Insurance & Billing' else 'false'}">Insurance & Billing</a>
            <a target="_self" href="/Trends_&_Forecasting" class="nav-link" data-active="{'true' if current_page == 'Trends & Forecasting' else 'false'}">Trends & Forecasting</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

def initialize_page():
    # Set page configuration
    st.set_page_config(
        page_title="Healthcare Analytics Dashboard",
        layout="wide",
        page_icon= 'assets/images/logo.png',
        initial_sidebar_state="expanded"
    )

    # Load CSS
    with open('assets/styles.css') as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def create_sidebar(df):
    max_date = df['Date of Admission'].max()
    logo_path = "assets/images/logo.png"
    
    # Sidebar header with logo
    st.sidebar.markdown(f"""
    <div style="display: flex; justify-content: center; margin-bottom: 20px;">
        <img src="data:image/png;base64,{img_to_base64(logo_path)}" width="35">
    </div>
    """, unsafe_allow_html=True)

    st.sidebar.markdown("""
    <div class="sidebar-header">
        Analytics Dashboard
    </div>
    """, unsafe_allow_html=True)

    st.sidebar.markdown("<hr>", unsafe_allow_html=True)
    st.sidebar.markdown("<div class='sidebar-section-title'>Filters</div>", unsafe_allow_html=True)

    # Time period selector
    scenario = st.sidebar.selectbox(
        "Time Period:",
        options=["Last Month", "Last Quarter", "Last Year", "Custom"],
        index=0
    )

    # Hospital multiselect
    # Get unique hospitals and add "All" option
    hospitals = sorted(df['Hospital'].unique().tolist())
    selected_hospitals = st.sidebar.multiselect(
        "Hospital:",
        options=hospitals,
        default= None,
        placeholder= 'All'
    )

    # Process the hospital filter
    if "All" in selected_hospitals or not selected_hospitals:
        filtered_df = df  # No filtering if "All" is selected or nothing is selected
    else:
        filtered_df = df[df['Hospital'].isin(selected_hospitals)]

    # Process date ranges based on scenario
    current_start, current_end, prev_start, prev_end, comparison_label = process_date_ranges(scenario, max_date)

    return current_start, current_end, prev_start, prev_end, comparison_label, filtered_df
    