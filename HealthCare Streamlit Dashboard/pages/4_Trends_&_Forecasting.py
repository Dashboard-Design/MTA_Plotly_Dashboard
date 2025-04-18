import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from datetime import timedelta
from utils import initialize_page, load_data, create_sidebar, create_page_navigation
import calendar

# Initialize page
initialize_page()

try:
    # Load data
    df = load_data()
    
    current_start, current_end, prev_start, prev_end, comparison_label, filtered_df = create_sidebar(df)
    
    # Set current page for navigation
    st.session_state['current_page'] = 'Trends & Forecasting'
    
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

    # Create a copy of the filtered data for the completed months only
    df_completed = filtered_df.copy()
    
    # Identify the last complete month in the dataset
    max_date = df_completed['Date of Admission'].max()
    current_month = max_date.month
    current_year = max_date.year
    
    # Get the first day of the current month
    first_day_current_month = pd.Timestamp(year=current_year, month=current_month, day=1)
    
    # If we're more than 20 days into the month, consider the previous month as incomplete
    if max_date.day < 20:
        # Calculate the last day of the previous month
        if current_month == 1:  # January
            prev_month = 12
            prev_year = current_year - 1
        else:
            prev_month = current_month - 1
            prev_year = current_year
            
        last_day_prev_month = calendar.monthrange(prev_year, prev_month)[1]
        current_start = pd.Timestamp(year=prev_year, month=prev_month, day=1)
        
        last_complete_month_end = pd.Timestamp(year=prev_year, month=prev_month, day=last_day_prev_month)
        current_end = last_complete_month_end
    else:
        # Current month has enough data, so last complete month is previous month
        last_complete_month_end = max_date
        current_start = pd.Timestamp(year=current_year, month=current_month, day=1)
        current_end = max_date
    
    # Filter out incomplete months for trend analysis and forecasting
    df_completed = df_completed[df_completed['Date of Admission'] <= last_complete_month_end]
    
    # Add note about complete months
    # st.markdown("""
    #     <div style="margin-bottom: 20px; padding: 10px; background-color: #f8f9fa; border-left: 4px solid #2f88ff; border-radius: 4px;">
    #         <p style="margin: 0; font-style: italic; color: #666;">
    #             Note: Trend analysis and forecasting are based on complete months only. Partial months are excluded to ensure accuracy.
    #         </p>
    #     </div>
    #     """, unsafe_allow_html=True
    # )

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
    
    # ------ Section 1: Historical Patient Volume Trends ------
    
    st.markdown("""
        <div class="numberOfPatients">
            <h3 class="sub">Patient Volume Trends</h3>
            <p>monthly analysis of patient admissions</p>
        </div>
        """, unsafe_allow_html=True
    )
    
    with st.container(key='background'):
        # Create monthly aggregation for the entire dataset using the filtered data
        df_monthly = df_completed.copy()
        df_monthly['month_year'] = df_monthly['Date of Admission'].dt.to_period('M')
        monthly_patients = df_monthly.groupby(['month_year']).agg({
            'Patient ID': 'count'
        }).reset_index()
        
        # Convert period to datetime for plotting
        monthly_patients['month_year'] = monthly_patients['month_year'].dt.to_timestamp()
        monthly_patients.sort_values('month_year', inplace=True)
        monthly_patients.rename(columns={'Patient ID': 'Patient_Count'}, inplace=True)
        
        # Create marker sizes and colors for highlighting
        marker_sizes = [8] * len(monthly_patients)
        marker_colors = ['#2f88ff'] * len(monthly_patients)
        
        # Set up specific data for the selected periods
        current_data = None
        prev_data = None
        
        if df_prev is not None:
            # Aggregate data for current and previous periods
            df_current['month_year'] = df_current['Date of Admission'].dt.to_period('M')
            current_monthly = df_current.groupby(['month_year']).agg({
                'Patient ID': 'count'
            }).reset_index()
            current_monthly['month_year'] = current_monthly['month_year'].dt.to_timestamp()
            current_monthly.rename(columns={'Patient ID': 'Patient_Count'}, inplace=True)
            
            current_data = {
                'x': current_monthly['month_year'].tolist(),
                'y': current_monthly['Patient_Count'].tolist()
            }
            
            df_prev['month_year'] = df_prev['Date of Admission'].dt.to_period('M')
            prev_monthly = df_prev.groupby(['month_year']).agg({
                'Patient ID': 'count'
            }).reset_index()
            prev_monthly['month_year'] = prev_monthly['month_year'].dt.to_timestamp()
            prev_monthly.rename(columns={'Patient ID': 'Patient_Count'}, inplace=True)
            
            prev_data = {
                'x': prev_monthly['month_year'].tolist(),
                'y': prev_monthly['Patient_Count'].tolist()
            }
        
        # Create line chart
        fig = go.Figure()
        
        # Add main trend line
        fig.add_trace(go.Scatter(
            x=monthly_patients['month_year'],
            y=monthly_patients['Patient_Count'],
            mode='lines+markers',
            name='Monthly Patient Count',
            line=dict(color='#2f88ff', width=2),
            marker=dict(size=marker_sizes, color=marker_colors),
            hovertemplate='%{x|%b %Y}<br>Patients: %{y:,}<extra></extra>'
        ))
        
        # Add highlighted points for current period
        if current_data and current_data['x']:
            fig.add_trace(go.Scatter(
                x=current_data['x'],
                y=current_data['y'],
                mode='markers',
                name='Current Period',
                marker=dict(color='#ff6b6b', size=12, line=dict(width=2, color='white')),
                hovertemplate='Current Period<br>%{x|%b %Y}<br>Patients: %{y:,}<extra></extra>'
            ))
        
        # Add highlighted points for previous period
        if prev_data and prev_data['x']:
            fig.add_trace(go.Scatter(
                x=prev_data['x'],
                y=prev_data['y'],
                mode='markers',
                name=f'Previous Period ({period_label})',
                marker=dict(color='#FFA726', size=12, line=dict(width=2, color='white')),
                hovertemplate='Previous Period<br>%{x|%b %Y}<br>Patients: %{y:,}<extra></extra>'
            ))
        
        # Calculate moving average for trend line
        window_size = 3
        if len(monthly_patients) > window_size:
            monthly_patients_copy = monthly_patients.copy()
            monthly_patients_copy['MA'] = monthly_patients_copy['Patient_Count'].rolling(window=window_size).mean()
            
            fig.add_trace(go.Scatter(
                x=monthly_patients_copy['month_year'],
                y=monthly_patients_copy['MA'],
                mode='lines',
                name=f'{window_size}-Month Moving Average',
                line=dict(color='#333333', width=2, dash='dot'),
                hovertemplate='%{x|%b %Y}<br>Moving Avg: %{y:.1f}<extra></extra>'
            ))
        
        # Update layout
        fig.update_layout(
            title=None,
            xaxis_title=None,
            yaxis_title="Number of Patients",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=0, r=0, t=10, b=0),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
            height=400,
            xaxis=dict(
                showgrid=False,
                showline=True,
                linecolor='rgba(211,211,211,0.7)'
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='rgba(211,211,211,0.3)',
                title_font=dict(size=14)
            ),
            hoverlabel=dict(
                bgcolor="white",
                font_size=12
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Add caption about the chart
        st.caption("Chart shows patient volume by complete months. The current and previous periods (if selected) are highlighted with larger markers.")
    
    # Add insights about trends
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<h6 style='text-align: left;'>Trend Insights</h6>", unsafe_allow_html=True)
        
        if len(monthly_patients) > 1:
            # Calculate percentage change from first to last month
            first_month = monthly_patients.iloc[0]['Patient_Count']
            last_month = monthly_patients.iloc[-1]['Patient_Count']
            total_change_pct = ((last_month - first_month) / first_month) * 100
            
            # Get months with highest and lowest patient counts
            max_month = monthly_patients.loc[monthly_patients['Patient_Count'].idxmax()]
            min_month = monthly_patients.loc[monthly_patients['Patient_Count'].idxmin()]
            
            # Calculate month-over-month growth
            monthly_patients_growth = monthly_patients.copy()
            monthly_patients_growth['MoM_Growth'] = monthly_patients_growth['Patient_Count'].pct_change() * 100
            avg_growth = monthly_patients_growth['MoM_Growth'].dropna().mean()
            
            # Calculate recent trend (last 3 months or fewer if not enough data)
            recent_months_count = min(3, len(monthly_patients))
            recent_months = monthly_patients.tail(recent_months_count)
            if recent_months_count > 1:
                recent_growth = (recent_months.iloc[-1]['Patient_Count'] / recent_months.iloc[0]['Patient_Count'] - 1) * 100
            else:
                recent_growth = 0
            
            # Year-over-year comparison if we have enough data
            yoy_change = None
            if len(monthly_patients) >= 13:
                last_year_same_month = monthly_patients.iloc[-13]['Patient_Count'] if len(monthly_patients) >= 13 else None
                if last_year_same_month:
                    yoy_change = ((last_month - last_year_same_month) / last_year_same_month) * 100
            
            st.markdown(f"""
            <div style="background-color: #f9f9f9; padding: 15px; border-radius: 5px;">
                <p>• Overall trend shows a <span style="color: {'green' if total_change_pct >= 0 else 'red'}; font-weight: bold;">
                    {total_change_pct:.1f}%</span> change in patient volume over the entire period.</p>
                
                <p>• Peak patient volume occurred in <span style="font-weight: bold;">{max_month['month_year'].strftime('%B %Y')}</span> 
                    with <span style="font-weight: bold;">{max_month['Patient_Count']:,}</span> patients.</p>
                
                <p>• Lowest patient volume was in <span style="font-weight: bold;">{min_month['month_year'].strftime('%B %Y')}</span> 
                    with <span style="font-weight: bold;">{min_month['Patient_Count']:,}</span> patients.</p>
                
                <p>• Average month-over-month growth rate is <span style="color: {'green' if avg_growth >= 0 else 'red'}; font-weight: bold;">
                    {avg_growth:.1f}%</span>.</p>
                
                {f'<p>• Recent trend (last {recent_months_count} months) shows <span style="color: {"green" if recent_growth >= 0 else "red"}; font-weight: bold;">{recent_growth:.1f}%</span> growth, indicating {"acceleration" if recent_growth > avg_growth else "deceleration"} compared to the overall average.</p>' if recent_months_count > 1 else ''}
                
                {f'<p>• Year-over-year change is <span style="color: {"green" if yoy_change >= 0 else "red"}; font-weight: bold;">{yoy_change:.1f}%</span> compared to the same month last year.</p>' if yoy_change is not None else ''}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background-color: #f9f9f9; padding: 15px; border-radius: 5px;">
                <p>Not enough data to generate trend insights. Please select a wider date range or different hospitals.</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("<h6 style='text-align: left;'>Seasonality Patterns</h6>", unsafe_allow_html=True)
        
        # Create month-of-year analysis for seasonality using filtered data
        df_seasonal = df_completed.copy()
        df_seasonal['month'] = df_seasonal['Date of Admission'].dt.month
        df_seasonal['month_name'] = df_seasonal['Date of Admission'].dt.strftime('%B')
        df_seasonal['year'] = df_seasonal['Date of Admission'].dt.year
        
        monthly_pattern = df_seasonal.groupby('month').agg({
            'Patient ID': 'count'
        }).reset_index()
        
        # Add month names
        month_names = ['January', 'February', 'March', 'April', 'May', 'June', 
                       'July', 'August', 'September', 'October', 'November', 'December']
        monthly_pattern['month_name'] = monthly_pattern['month'].apply(lambda x: month_names[x-1])
        monthly_pattern.rename(columns={'Patient ID': 'Patient_Count'}, inplace=True)
        
        # Check if we have enough data for seasonality
        if len(monthly_pattern) > 1:
            # Create bar chart for seasonality
            monthly_pattern_sorted = monthly_pattern.sort_values('month')
            
            fig_season = go.Figure()
            
            # Add bars
            fig_season.add_trace(go.Bar(
                x=monthly_pattern_sorted['month_name'],
                y=monthly_pattern_sorted['Patient_Count'],
                marker=dict(
                    color=monthly_pattern_sorted['Patient_Count'],
                    colorscale=[[0, '#c2dcff'], [1, '#2f88ff']],
                    showscale=False
                ),
                text=monthly_pattern_sorted['Patient_Count'],
                textposition='outside',
                hovertemplate='%{x}<br>Patients: %{y:,}<extra></extra>'
            ))
            
            fig_season.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=0, r=0, t=10, b=0),
                height=250,
                xaxis=dict(
                    title=None,
                    tickmode='array',
                    tickvals=monthly_pattern_sorted['month_name'],
                    categoryorder='array',
                    categoryarray=monthly_pattern_sorted['month_name'],
                    showgrid=False
                ),
                yaxis=dict(
                    title=None,
                    showgrid=True,
                    gridcolor='rgba(211,211,211,0.3)'
                )
            )
            
            st.plotly_chart(fig_season, use_container_width=True)
            
            # Identify peak and low seasons
            peak_month = monthly_pattern_sorted.loc[monthly_pattern_sorted['Patient_Count'].idxmax()]['month_name']
            low_month = monthly_pattern_sorted.loc[monthly_pattern_sorted['Patient_Count'].idxmin()]['month_name']
            
            # Calculate quarter averages if we have enough data
            if len(monthly_pattern) >= 3:
                quarter_data = {}
                for q, months in {
                    'Q1 (Jan-Mar)': [1, 2, 3], 
                    'Q2 (Apr-Jun)': [4, 5, 6], 
                    'Q3 (Jul-Sep)': [7, 8, 9], 
                    'Q4 (Oct-Dec)': [10, 11, 12]
                }.items():
                    q_data = monthly_pattern_sorted[monthly_pattern_sorted['month'].isin(months)]
                    if not q_data.empty:
                        quarter_data[q] = q_data['Patient_Count'].mean()
                
                if quarter_data:
                    strongest_quarter = max(quarter_data, key=quarter_data.get)
                    weakest_quarter = min(quarter_data, key=quarter_data.get)
                    quarterly_insight = f"""
                    <p>• <span style="font-weight: bold;">{strongest_quarter}</span> consistently shows the highest patient volume, 
                    while <span style="font-weight: bold;">{weakest_quarter}</span> shows the lowest.</p>
                    """
                else:
                    quarterly_insight = ""
            else:
                quarterly_insight = ""
            
            # Calculate seasonality variance if we have at least 2 months
            if len(monthly_pattern) >= 2:
                seasonality_variance = (monthly_pattern_sorted['Patient_Count'].max() / monthly_pattern_sorted['Patient_Count'].min() - 1) * 100
                variance_insight = f"""
                <p>• The seasonality variance is <span style="font-weight: bold;">{seasonality_variance:.1f}%</span> 
                between peak and low months, which requires careful resource planning.</p>
                """
            else:
                variance_insight = ""
            
            st.markdown(f"""
            <div style="background-color: #f9f9f9; padding: 15px; border-radius: 5px;">
                <p>• Peak patient volume typically occurs in <span style="font-weight: bold;">{peak_month}</span>, with approximately 
                <span style="font-weight: bold;">{monthly_pattern_sorted[monthly_pattern_sorted['month_name']==peak_month]['Patient_Count'].values[0]:,.0f}</span> patients.</p>
                
                <p>• Lowest patient volume tends to be in <span style="font-weight: bold;">{low_month}</span>, with approximately 
                <span style="font-weight: bold;">{monthly_pattern_sorted[monthly_pattern_sorted['month_name']==low_month]['Patient_Count'].values[0]:,.0f}</span> patients.</p>
                
                {quarterly_insight}
                {variance_insight}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background-color: #f9f9f9; padding: 15px; border-radius: 5px;">
                <p>Not enough data to analyze seasonality patterns. Please select a wider date range or different hospitals.</p>
            </div>
            """, unsafe_allow_html=True)
    
    # ------ Section 2: Forecasting ------
    st.markdown("""
        <div class="numberOfPatients" style="margin-top: 30px;">
            <h3 class="sub">Patient Volume Forecast</h3>
            <p>predictions for upcoming months based on historical data</p>
        </div>
        """, unsafe_allow_html=True
    )
    
    with st.container(key='forecast_background'):
        # Create forecasting model
        forecast_periods = 6  # Number of months to forecast
        
        # Only proceed with forecasting if we have enough data (at least 12 complete months)
        if len(monthly_patients) >= 12:
            # Prepare the time series data using a copy to avoid SettingWithCopyWarning
            time_series = pd.Series(
                monthly_patients['Patient_Count'].values.copy(),
                index=monthly_patients['month_year'].values
            )
            
            try:
                # Create the Exponential Smoothing model with numpy array to avoid copy issues
                model = ExponentialSmoothing(
                    np.array(time_series.values),
                    trend='add', 
                    seasonal='add', 
                    seasonal_periods=12,
                    damped=True
                ).fit()
                
                # Generate forecast
                forecast_values = model.forecast(forecast_periods)
                
                # Create proper DataFrame for forecast
                last_date = time_series.index[-1]
                prediction_index = pd.date_range(
                    start=pd.Timestamp(last_date) + pd.DateOffset(months=1),
                    periods=forecast_periods,
                    freq='MS'
                )
                
                # Calculate prediction intervals
                resid_std = np.std(model.resid)
                lower_bound = np.maximum(0, forecast_values - 1.28 * resid_std)
                upper_bound = forecast_values + 1.28 * resid_std
                
                # Create forecast visualization
                fig_forecast = go.Figure()
                
                # Add historical data
                fig_forecast.add_trace(go.Scatter(
                    x=time_series.index,
                    y=time_series.values,
                    mode='lines+markers',
                    name='Historical',
                    line=dict(color='#2f88ff', width=2),
                    marker=dict(size=6)
                ))
                
                # Add forecast
                fig_forecast.add_trace(go.Scatter(
                    x=prediction_index,
                    y=forecast_values,
                    mode='lines+markers',
                    name='Forecast',
                    line=dict(color='#ff6b6b', width=2, dash='dash'),
                    marker=dict(size=8, symbol='diamond'),
                    hovertemplate='%{x|%b %Y}<br>Forecast: %{y:.0f} patients<extra></extra>'
                ))
                
                # Add prediction intervals
                fig_forecast.add_trace(go.Scatter(
                    x=np.concatenate([prediction_index, prediction_index[::-1]]),
                    y=np.concatenate([upper_bound, lower_bound[::-1]]),
                    fill='toself',
                    fillcolor='rgba(255, 107, 107, 0.1)',
                    line=dict(color='rgba(255, 107, 107, 0)'),
                    name='80% Confidence Interval',
                    hoverinfo='skip'
                ))
                
                # Update layout
                fig_forecast.update_layout(
                    title=None,
                    xaxis_title=None,
                    yaxis_title="Forecasted Number of Patients",
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    margin=dict(l=0, r=0, t=10, b=0),
                    legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
                    height=400,
                    xaxis=dict(
                        showgrid=False,
                        showline=True,
                        linecolor='rgba(211,211,211,0.7)'
                    ),
                    yaxis=dict(
                        showgrid=True,
                        gridcolor='rgba(211,211,211,0.3)',
                        title_font=dict(size=14)
                    ),
                    hoverlabel=dict(
                        bgcolor="white",
                        font_size=12
                    )
                )
                
                st.plotly_chart(fig_forecast, use_container_width=True)
                st.caption("Forecast is based on completed months only. The shaded area represents the 80% confidence interval.")
                
                # Forecast insights
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("<h6 style='text-align: left;'>Forecast Insights</h6>", unsafe_allow_html=True)
                    
                    # Calculate key metrics from forecast
                    first_forecast = forecast_values[0]
                    last_forecast = forecast_values[-1]
                    current_volume = time_series.values[-1]
                    forecast_change_pct = ((last_forecast - first_forecast) / first_forecast) * 100
                    forecast_vs_current_pct = ((last_forecast - current_volume) / current_volume) * 100
                    total_forecast_volume = np.sum(forecast_values)
                    
                    # Calculate seasonal adjustments in the forecast
                    expected_peak_month = prediction_index[np.argmax(forecast_values)].strftime('%B %Y')
                    expected_low_month = prediction_index[np.argmin(forecast_values)].strftime('%B %Y')
                    forecast_variation = (np.max(forecast_values) / np.min(forecast_values) - 1) * 100
                    
                    st.markdown(f"""
                    <div style="background-color: #f9f9f9; padding: 15px; border-radius: 5px;">
                        <p>• Patient volume is projected to change by 
                        <span style="color: {'green' if forecast_change_pct >= 0 else 'red'}; font-weight: bold;">
                        {forecast_change_pct:+.1f}%</span> over the next {forecast_periods} months.</p>
                        
                        <p>• By {prediction_index[-1].strftime('%B %Y')}, we expect 
                        <span style="font-weight: bold;">{last_forecast:.0f}</span> patients, which is 
                        <span style="color: {'green' if forecast_vs_current_pct >= 0 else 'red'}; font-weight: bold;">
                        {forecast_vs_current_pct:+.1f}%</span> versus current volume.</p>
                        
                        <p>• Total projected patient volume for the next {forecast_periods} months: 
                        <span style="font-weight: bold;">{total_forecast_volume:.0f}</span> patients.</p>
                        
                        <p>• Expected peak is in <span style="font-weight: bold;">{expected_peak_month}</span>, with 
                        expected low in <span style="font-weight: bold;">{expected_low_month}</span> 
                        (a {forecast_variation:.1f}% variation).</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown("<h6 style='text-align: left;'>Planning Recommendations</h6>", unsafe_allow_html=True)
                    
                    # Create planning recommendations based on forecast
                    # Determine if overall trend is up/down
                    trend_direction = "upward" if forecast_change_pct > 2 else "downward" if forecast_change_pct < -2 else "stable"
                    
                    # Identify peak forecast month
                    peak_month_idx = prediction_index[np.argmax(forecast_values)].strftime('%B %Y')
                    peak_month_val = np.max(forecast_values)
                    
                    # Generate recommendations based on trend direction
                    if trend_direction == "upward":
                        recommendations = f"""
                        <p>• <strong>Staffing:</strong> Plan for {max(5, abs(forecast_change_pct)):.0f}% staff increase to handle growing patient volume, with focus on {peak_month_idx}.</p>
                        <p>• <strong>Resource Allocation:</strong> Increase medical supplies by {max(3, abs(forecast_change_pct)):.0f}% and ensure equipment maintenance is completed before peak periods.</p>
                        <p>• <strong>Capacity Planning:</strong> Evaluate bed capacity at all facilities, with potential for temporary expansion during {peak_month_idx}.</p>
                        <p>• <strong>Budget Planning:</strong> Allocate additional {max(5, abs(forecast_change_pct)):.0f}% in operational budget to accommodate growing patient needs.</p>
                        """
                    elif trend_direction == "downward":
                        recommendations = f"""
                        <p>• <strong>Efficiency:</strong> Optimize staffing levels with potential {min(5, abs(forecast_change_pct)):.0f}% reduction in temporary staff during slower periods.</p>
                        <p>• <strong>Marketing & Outreach:</strong> Increase community outreach by 10% and consider adding preventive care services to maintain patient engagement.</p>
                        <p>• <strong>Service Expansion:</strong> Evaluate adding specialized services or extended hours for existing high-demand services.</p>
                        <p>• <strong>Cost Management:</strong> Focus on reducing variable costs by {min(3, abs(forecast_change_pct)):.0f}% to maintain financial health during lower volume.</p>
                        """
                    else:
                        recommendations = f"""
                        <p>• <strong>Maintenance:</strong> Schedule facility renovations and equipment upgrades during expected lower-volume months.</p>
                        <p>• <strong>Staff Development:</strong> Use stable period to implement training programs and quality improvement initiatives.</p>
                        <p>• <strong>Peak Planning:</strong> Ensure adequate staffing for {peak_month_idx} when patient volume is expected to reach {peak_month_val:.0f}.</p>
                        <p>• <strong>Inventory Management:</strong> Maintain current inventory levels with small adjustments for seasonal variations.</p>
                        """
                    
                    st.markdown(f"""
                    <div style="background-color: #f9f9f9; padding: 15px; border-radius: 5px;">
                        {recommendations}
                        <p>• <strong>Strategic Review:</strong> Reassess forecast monthly and adjust operational plans accordingly as new data becomes available.</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
            except Exception as e:
                st.warning(f"Forecasting error: {e}. Please ensure you have sufficient complete monthly data for accurate forecasting.")
                st.markdown("""
                <div style="background-color: #f9f9f9; padding: 15px; border-radius: 5px;">
                    <p>Suggestions to fix forecasting issues:</p>
                    <ul>
                        <li>Select a wider date range that includes more historical data</li>
                        <li>Ensure the selected hospital(s) have consistent data across all months</li>
                        <li>Try using the "Last Year" time period option for more reliable forecasting</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning(f"Not enough historical data for reliable forecasting. We recommend at least 12 complete months of data for seasonal forecasting. Current data has {len(monthly_patients)} complete months.")
            st.markdown("""
            <div style="background-color: #f9f9f9; padding: 15px; border-radius: 5px;">
                <p>To generate a forecast, please:</p>
                <ul>
                    <li>Select "Last Year" from the time period dropdown</li>
                    <li>Ensure you haven't filtered to a specific hospital with limited data</li>
                    <li>Consider using the full dataset without additional filters</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Error: {e}")
    st.stop()