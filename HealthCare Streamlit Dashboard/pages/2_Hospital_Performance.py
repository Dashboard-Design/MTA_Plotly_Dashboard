import streamlit as st
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import initialize_page, load_data, create_sidebar, create_page_navigation

# Initialize page
initialize_page()

try:
    # Load data
    df = load_data()
    
    current_start, current_end, prev_start, prev_end, comparison_label, filtered_df = create_sidebar(df)
    
    # Set current page for navigation
    st.session_state['current_page'] = 'Hospital Performance'
    
    st.markdown("""<style>
                [data-testid="stHorizontalBlock"] {
                background-color: white;
                border-radius: 5px;
                padding: 25px;
                box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
                }
    </style>""", unsafe_allow_html=True)
    
    # Create navigation
    create_page_navigation()

    # Filter data for current period
    df_current = filtered_df[(filtered_df['Date of Admission'] >= current_start) & 
                            (filtered_df['Date of Admission'] <= current_end)]
    
    # Filter data for previous period
    if prev_start is not None and prev_end is not None:
        df_prev = filtered_df[(filtered_df['Date of Admission'] >= prev_start) & 
                             (filtered_df['Date of Admission'] <= prev_end)]
    else:
        df_prev = None

    # Get period label for column title (PM, PQ, PY)
    if comparison_label == "":
        period_label = "(no comparison)"
    else:
        period_label = comparison_label.replace("vs ", "")



    # ------ Map ------

    st.markdown("""<h3 class="sub">Map</h3>""", unsafe_allow_html=True)

    # Create a DataFrame with hospital locations and patient counts
    df_map = df_current.groupby(['Hospital', 'Hospital Latitude', 'Hospital Longitude']).agg({
        'Patient ID': 'count',  # Count of patients
         'Billing Amount': 'sum'  # Total billing amount
    }).reset_index()


    df_map.columns = ['Hospital', 'Latitude', 'Longitude', 'Patient_Count', 'Total_Billing']

    # Normalize the patient count to get reasonable bubble sizes
    max_size = df_map['Patient_Count'].max()
    df_map['size'] = df_map['Patient_Count'] / max_size * 2000  # Adjust the multiplier (2000) to change bubble sizes

    # Create hover text
    df_map['hover_text'] = df_map.apply(
        lambda row: f"<b>{row['Hospital']}</b><br>" +
                f"Patients: {row['Patient_Count']:,}<br>" +
                f"Total Billing: ${row['Total_Billing']:,.0f}",
        axis=1
    )

    # Create the map using Plotly
    fig = go.Figure()

    # Add scatter mapbox trace
    fig.add_trace(go.Scattermapbox(
        lat=df_map['Latitude'],
        lon=df_map['Longitude'],
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=( df_map['Patient_Count'] / df_map['Patient_Count'].max() )* 100,  # Normalize size
            color='#2f88ff',
            opacity=0.8
        ),
        text=df_map['hover_text'],
        hoverinfo='text'
    ))

    # Update layout
    fig.update_layout(
        mapbox=dict(
            style= 'open-street-map', #'carto-positron',
            zoom=3,  # Adjust zoom level as needed
            center=dict(lat=38, lon=-98.5795)  # Center of USA
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        height=400,
        showlegend=False
    )

    # Display the map
    st.plotly_chart(fig, use_container_width=True)

    # Add caption
    st.caption("Bubble sizes represent the number of patients in the current period at each hospital location")

except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()