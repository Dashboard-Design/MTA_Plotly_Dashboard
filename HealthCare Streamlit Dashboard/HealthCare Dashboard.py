import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime, timedelta
import base64
from pathlib import Path

# Add this function to your code
def img_to_base64(img_path):
    with open(img_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

logo_path = "assets/images/logo.png"

# Set page configuration
st.set_page_config(
    page_title="Healthcare Analytics Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling Streamlit's components
with open('assets/styles.css')  as f:
    st.markdown(f" <style> {f.read()} </style>", unsafe_allow_html=True)


@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/Dashboard-Design/Python-Dashboards/refs/heads/main/HealthCare%20Streamlit%20Dashboard/data/Healthcare%20Analysis%20Dataset.csv"
    df = pd.read_csv(url)

    df['Date of Admission'] = pd.to_datetime(df['Date of Admission'])
    df['Discharge Date'] = pd.to_datetime(df['Discharge Date'])
    df['Length of Stay'] = (df['Discharge Date'] - df['Date of Admission']).dt.days
    df['Year'] = df['Date of Admission'].dt.year
    df['Month'] = df['Date of Admission'].dt.month
    df['Quarter'] = df['Date of Admission'].dt.quarter

    return df

try:
    df = load_data()
    
    # Get max date from dataset to use as reference instead of current date
    max_date = df['Date of Admission'].max()
    
    # Sidebar filters
    st.sidebar.markdown(f"""
    <div style="display: flex; justify-content: center; margin-bottom: 20px;">
        <img src="data:image/png;base64,{img_to_base64(logo_path)}" width="35">
    </div>
    """, unsafe_allow_html=True)

    st.sidebar.markdown("""
    <div class="sidebar-header">
        Healthcare Dashboard
    </div>
    """, unsafe_allow_html=True)

    st.sidebar.markdown("<hr>", unsafe_allow_html=True)  # Add divider
    st.sidebar.markdown("<div class='sidebar-section-title'>Filters</div>", unsafe_allow_html=True)

    # Scenario-based filter
    scenario = st.sidebar.selectbox(
        "Time Period:",
        options=["Last Month", "Last Quarter", "Last Year", "Custom"],
        index=0
    )
    
    # Define date ranges based on scenario
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
        # Handle different days in month (e.g., Feb 28/29)
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
            min_value=df['Date of Admission'].min().date(),
            max_value=max_date.date()
        )
        
        if len(date_range) == 2:
            current_start = pd.Timestamp(date_range[0])
            current_end = pd.Timestamp(date_range[1])
            # No comparison for custom range
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
    
    # Display selected date range for clarity
    st.sidebar.markdown(f"""
        <div class="simpleTextFirst">
            <p>Selected range:</p>                
            <p class="textBlak">{current_start.strftime('%b %d, %Y')} - {current_end.strftime('%b %d, %Y')}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Filter data for current period
    df_current = df[(df['Date of Admission'] >= current_start) & 
                    (df['Date of Admission'] <= current_end)]
    
    # Filter data for previous period (for comparison)
    if prev_start is not None and prev_end is not None:
        df_prev = df[(df['Date of Admission'] >= prev_start) & 
                     (df['Date of Admission'] <= prev_end)]
        # Show comparison date range
        st.sidebar.markdown(f"""
                            <div class="simpleText">
                            <p>Comparison:</p>
                            <p class="textBlak">{prev_start.strftime('%b %d, %Y')} - {prev_end.strftime('%b %d, %Y')}</p>
                            </div>    
        """, unsafe_allow_html=True)
    else:
        df_prev = None
    
    # Create tabs for navigation
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Executive Summary", 
        "Patient Demographics", 
        "Hospital Performance", 
        "Insurance & Billing", 
        "Trends & Forecasting"
    ])
    
    # Executive Summary Tab
    with tab1:
        # KPIs title
        st.markdown("""<h3 class="sub">KPIs:</h3>""", unsafe_allow_html=True)

        # Calculate metrics for current period
        avg_length_of_stay = df_current['Length of Stay'].mean()
        avg_treatment_cost = df_current['Billing Amount'].mean()
        elective_admission_pct = (
            len(df_current[df_current['Admission Type'] == 'Elective']) / 
            len(df_current) * 100 if len(df_current) > 0 else 0
        )
        inconclusive_pct = (
            len(df_current[df_current['Test Results'] == 'Inconclusive']) / 
            len(df_current) * 100 if len(df_current) > 0 else 0
        )
        
        # Calculate metrics for previous period (if available)
        if df_prev is not None and len(df_prev) > 0:
            prev_avg_los = df_prev['Length of Stay'].mean()
            prev_avg_cost = df_prev['Billing Amount'].mean()
            prev_elective_pct = (
                len(df_prev[df_prev['Admission Type'] == 'Elective']) / 
                len(df_prev) * 100
            )
            prev_inconclusive_pct = (
                len(df_prev[df_prev['Test Results'] == 'Inconclusive']) / 
                len(df_prev) * 100
            )
            
            # Calculate percent changes
            los_change = ((avg_length_of_stay / prev_avg_los) - 1) * 100 if prev_avg_los > 0 else 0
            cost_change = ((avg_treatment_cost / prev_avg_cost) - 1) * 100 if prev_avg_cost > 0 else 0
            elective_change = elective_admission_pct - prev_elective_pct
            inconclusive_change = inconclusive_pct - prev_inconclusive_pct
        else:
            prev_avg_los = None
            prev_avg_cost = None
            prev_elective_pct = None
            prev_inconclusive_pct = None
            los_change = 0
            cost_change = 0
            elective_change = 0
            inconclusive_change = 0
        
        # Display metrics using custom HTML
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="kpi-container">
                <div class="kpi-title">Avg Stay (days)</div>
                <div class="kpi-value">{avg_length_of_stay:.1f}</div>
                {f'<div class="kpi-{"up" if los_change > 0 else "down"}">{"▲" if los_change > 0 else "▼"} {abs(los_change):.1f}%</div>' if prev_avg_los is not None else ''}
                {f'<div class="kpi-compare">{comparison_label}: {prev_avg_los:.1f}</div>' if prev_avg_los is not None else ''}
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="kpi-container">
                <div class="kpi-title">Elective Admission %</div>
                <div class="kpi-value">{elective_admission_pct:.1f}%</div>
                {f'<div class="kpi-{"up" if elective_change > 0 else "down"}">{"▲" if elective_change > 0 else "▼"} {abs(elective_change):.1f}%</div>' if prev_elective_pct is not None else ''}
                {f'<div class="kpi-compare">{comparison_label}: {prev_elective_pct:.1f}%</div>' if prev_elective_pct is not None else ''}
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="kpi-container">
                <div class="kpi-title">Avg Treatment Cost</div>
                <div class="kpi-value">${avg_treatment_cost:,.0f}</div>
                {f'<div class="kpi-{"down" if cost_change < 0 else "up"}">{"▼" if cost_change < 0 else "▲"} {abs(cost_change):.1f}%</div>' if prev_avg_cost is not None else ''}
                {f'<div class="kpi-compare">{comparison_label}: ${prev_avg_cost:,.0f}</div>' if prev_avg_cost is not None else ''}
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="kpi-container">
                <div class="kpi-title">Inconclusive Results</div>
                <div class="kpi-value">{inconclusive_pct:.1f}%</div>
                {f'<div class="kpi-{"up" if inconclusive_change < 0 else "down"}">{"▼" if inconclusive_change < 0 else "▲"} {abs(inconclusive_change):.1f}%</div>' if prev_inconclusive_pct is not None else ''}
                {f'<div class="kpi-compare">{comparison_label}: {prev_inconclusive_pct:.1f}%</div>' if prev_inconclusive_pct is not None else ''}
            </div>
            """, unsafe_allow_html=True)
        
        # Insurance Provider section with title
        st.markdown(f"""
                    <div class="numberOfPatients">
                     <h3 class="sub">Total Patients: {len(df_current):,.0f}</h3>
                     <p>breakdown by Insurance Providers:</p>
                    </div>
                    """, unsafe_allow_html=True)

        # Calculate Insurance Provider metrics
        insurance_counts = df_current['Insurance Provider'].value_counts()
        
        if df_prev is not None:
            prev_insurance_counts = df_prev['Insurance Provider'].value_counts()
        else:
            prev_insurance_counts = None
        
        # Create columns for insurance metrics
        ins_cols = st.columns(len(insurance_counts))
        
        # Display insurance provider metrics with comparison
        for idx, (provider, count) in enumerate(insurance_counts.items()):
            with ins_cols[idx]:
                if df_prev is not None and provider in prev_insurance_counts:
                    prev_count = prev_insurance_counts[provider]
                    if prev_count > 0:
                        change_pct = ((count / prev_count) - 1) * 100
                        st.markdown(f"""
                        <div class="kpi-container">
                            <div class="kpi-title">{provider}</div>
                            <div class="kpi-value">{count:,.0f}</div>
                            <div class="kpi-{"up" if change_pct > 0 else "down"}">{"▲" if change_pct > 0 else "▼"} {abs(change_pct):.1f}%</div>
                            <div class="kpi-compare">{comparison_label}: {prev_count:,.0f}</div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="kpi-container">
                        <div class="kpi-title">{provider}</div>
                        <div class="kpi-value">{count:,.0f}</div>
                    </div>
                    """, unsafe_allow_html=True)
    
    # Other tabs - placeholders
    with tab2:
        st.header("Patient Demographics")
        st.info("Patient Demographics content is under development")
    
    with tab3:
        st.header("Hospital Performance")
        st.info("Hospital Performance content is under development")
    
    with tab4:
        st.header("Insurance & Billing Analysis")
        st.info("Insurance & Billing content is under development")
    
    with tab5:
        st.header("Trends & Forecasting")
        st.info("Trends & Forecasting content is under development")

except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()