from dash import Dash, dcc, html
from dash import Input, Output
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc


dataset_url = "https://raw.githubusercontent.com/plotly/datasets/refs/heads/master/MTA_Ridership_by_DATA_NY_GOV.csv"
df = pd.read_csv(dataset_url)

df['Date'] = pd.to_datetime(df['Date'], errors='coerce')  # Ensure Date column is in datetime format
df = df.dropna(subset=['Date'])  # Drop rows where Date is invalid


# List of percentage columns
percentage_columns = [
    'Subways: % of Comparable Pre-Pandemic Day',
    'Buses: % of Comparable Pre-Pandemic Day',
    'LIRR: % of Comparable Pre-Pandemic Day',
    'Metro-North: % of Comparable Pre-Pandemic Day',
    'Access-A-Ride: % of Comparable Pre-Pandemic Day',
    'Bridges and Tunnels: % of Comparable Pre-Pandemic Day',
    'Staten Island Railway: % of Comparable Pre-Pandemic Day'
]


# Making them as Percentages
df[percentage_columns] = df[percentage_columns] / 100

# will be used in highlighting the line chart
service_mapping = {
    "Subways": "Subways: % of Comparable Pre-Pandemic Day",
    "Buses": "Buses: % of Comparable Pre-Pandemic Day",
    "LIRR": "LIRR: % of Comparable Pre-Pandemic Day",
    "Metro North": "Metro-North: % of Comparable Pre-Pandemic Day",
    "Access-A": "Access-A-Ride: % of Comparable Pre-Pandemic Day",
    "Bridges and Tunnels": "Bridges and Tunnels: % of Comparable Pre-Pandemic Day",
    "Staten Island Railway": "Staten Island Railway: % of Comparable Pre-Pandemic Day"
}

service_short_names = {
    "Subways: % of Comparable Pre-Pandemic Day": "Subways",
    "Buses: % of Comparable Pre-Pandemic Day": "Buses",
    "LIRR: % of Comparable Pre-Pandemic Day": "LIRR",
    "Metro-North: % of Comparable Pre-Pandemic Day": "Metro North",
    "Access-A-Ride: % of Comparable Pre-Pandemic Day": "Access-A",
    "Bridges and Tunnels: % of Comparable Pre-Pandemic Day": "Bridges",
    "Staten Island Railway: % of Comparable Pre-Pandemic Day": "Staten Island"
}

service_colors_line_chart = {
    "Subways: % of Comparable Pre-Pandemic Day": "#44b9dd", 
    "Buses: % of Comparable Pre-Pandemic Day": "#bf9bf9", 
    "LIRR: % of Comparable Pre-Pandemic Day": "#f89256",
    "Metro-North: % of Comparable Pre-Pandemic Day": "#eb92ad",
    "Access-A-Ride: % of Comparable Pre-Pandemic Day":  "#8ea9ff",
    "Bridges and Tunnels: % of Comparable Pre-Pandemic Day": "#d3a61c",
    "Staten Island Railway: % of Comparable Pre-Pandemic Day": "#40bfa9"
}


default_color = "#484E54"


service_colors = {
    "Subways": "#44b9dd",  # $color-charts-blue-1-600  
    "Buses": "#bf9bf9", # $color-charts-purple-600    
    "LIRR": "#f89256",  # $color-charts-orange-600
    "Metro North": "#eb92ad",  # $color-charts-pink-600
    "Access-A": "#8ea9ff",  # $color-charts-blue-2-600
    "Bridges and Tunnels": "#d3a61c",  # $color-charts-yellow-600
    "Staten Island Railway": "#40bfa9"  # $color-charts-teal-600
}


# ---- color option

# service_colors = {
#     "Subways": "#C2185B",  # Deep Pink
#     "Buses": "#7B1FA2",  # Purple
#     "LIRR": "#512DA8",  # Indigo
#     "Metro North": "#303F9F",  # Dark Blue
#     "Access-A": "#00796B",  # Teal
#     "Bridges and Tunnels": "#F57C00",  # Orange
#     "Staten Island Railway": "#C62828"  # Crimson
# }

summary_metrics = {
    "Subways": df["Subways: % of Comparable Pre-Pandemic Day"].mean(),
    "Buses": df["Buses: % of Comparable Pre-Pandemic Day"].mean(),
    "LIRR": df["LIRR: % of Comparable Pre-Pandemic Day"].mean(),
    "Metro North": df["Metro-North: % of Comparable Pre-Pandemic Day"].mean(),  
    "Access-A": df["Access-A-Ride: % of Comparable Pre-Pandemic Day"].mean(), 
    "Bridges and Tunnels": df["Bridges and Tunnels: % of Comparable Pre-Pandemic Day"].mean(),       
    "Staten Island Railway": df["Staten Island Railway: % of Comparable Pre-Pandemic Day"].mean()
}

# Monthly
df['Month'] = df['Date'].dt.to_period('M')
monthly_avg = df.groupby('Month').mean().reset_index()
monthly_avg['Month'] = monthly_avg['Month'].dt.to_timestamp()

# Weekly
df['Week'] = df['Date'].dt.to_period('W')
weekly_avg = df.groupby('Week').mean().reset_index()
weekly_avg['Week'] = weekly_avg['Week'].dt.to_timestamp()

# Quarterly
df['Quarter'] = df['Date'].dt.to_period('Q')
quarterly_avg = df.groupby('Quarter').mean().reset_index()
quarterly_avg['Quarter'] = quarterly_avg['Quarter'].dt.to_timestamp()

df['Year'] = df['Date'].dt.year
df['Month_Name'] = df['Date'].dt.strftime('%b')  # month name
df['Day_of_Week'] = df['Date'].dt.strftime('%a')  # day name

yearly_avg = df.groupby('Year')['Subways: % of Comparable Pre-Pandemic Day'].mean().reset_index()
monthly_avg_b = df.groupby('Month_Name')['Subways: % of Comparable Pre-Pandemic Day'].mean().reset_index()
day_of_week_avg = df.groupby('Day_of_Week')['Subways: % of Comparable Pre-Pandemic Day'].mean().reset_index()

# Sort by day of the week for proper order
day_of_week_order = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
day_of_week_avg['Day_of_Week'] = pd.Categorical(day_of_week_avg['Day_of_Week'], categories=day_of_week_order, ordered=True)
day_of_week_avg = day_of_week_avg.sort_values('Day_of_Week')




app = Dash(__name__, external_stylesheets=["https://cdn.jsdelivr.net/npm/bootswatch@5.3.0/dist/slate/bootstrap.min.css"])

# Sidebar
sidebar = dbc.Col(
    [
        html.Div(
            [
                dcc.Markdown(
                    """
                    <svg width="47" height="51" xmlns="http://www.w3.org/2000/svg">
                        <path d="M29.909 21.372l-2.743-.234v14.56l-4.088.724-.01-15.644-3.474-.308v-5.734l10.315 1.803v4.833zm7.785 12.484l-2.426.421-.283-2.122-2.363.307-.296 2.335-3.125.553 3.094-18.36 2.937.51 2.462 16.356zm-3.141-5.288l-.65-5.606h-.142l-.658 5.691 1.45-.085zM21.038 50.931c13.986 0 25.32-11.402 25.32-25.465C46.359 11.4 35.025 0 21.039 0 12.27 0 4.545 4.483 0 11.296l7.017 1.237 1.931 14.78c.007-.024.14-.009.14-.009l2.118-14.036 7.022 1.229V37.28l-4.432.776v-9.79s.164-4.217.067-4.938c0 0-.193.005-.196-.011l-2.644 15.236-4.403.777-3.236-16.412-.195-.014c-.069.594.237 5.744.237 5.744v11.243L.532 40.4c4.603 6.38 12.072 10.53 20.506 10.53v.001z" fill="#FFF" fill-rule="nonzero"></path>
                    </svg>
                    """,
                    dangerously_allow_html=True,
                    className="mb-2"
                ),
                html.H3("MTA Dashboard", className="text-center text-light", style={"fontSize": "1.7vw"})
            ],
            className="mb-4 mt-3 text-center"
        ),
        html.Hr(className="mb-4"),
        html.Div("Select/Highlight a Service:", className="fw text-light mb-2", style={"fontSize": "0.8vw", "width": "90%", "margin": "0 auto", "textAlign": "left"}),  
        dbc.Select(
            id="service-selector",
            options=[
                {"label": "Subways", "value": "Subways"},
                {"label": "Buses", "value": "Buses"},
                {"label": "LIRR", "value": "LIRR"},
                {"label": "Metro North", "value": "Metro North"},
                {"label": "Access-A-Ride", "value": "Access-A"},
                {"label": "Bridges and Tunnels", "value": "Bridges and Tunnels"},
                {"label": "Staten Island Railway", "value": "Staten Island Railway"}
            ],
            value="Subways",
            className="mb-4 p-10 form-select form-select-sm",
            style={"width": "90%", "margin": "0 auto"}
        ),
        html.Div("Select Year:", className="fw text-light mb-2", style={"fontSize": "0.8vw", "width": "90%", "margin": "0 auto", "textAlign": "left"}), 
        dbc.Select(
            id="year-selector",
            options=[{"label": "All", "value": "All"}] + [{"label": year, "value": year} for year in sorted(df['Year'].unique())],
            value="All",  # Default to "All"
            className="mb-4 p-10 form-select form-select-sm",
            style={"width": "90%", "margin": "0 auto"}
        ),
        html.Div("Display KPIs By:", className="fw text-light mb-2", style={"fontSize": "0.8vw", "width": "90%", "margin": "0 auto", "textAlign": "left"}), 
        dbc.Select(
            id="metric-type",
            options=[
                {"label": "Average Daily Recovery", "value": "average"},
                {"label": "Days ≥ 100% Recovery", "value": "days_100"},
                {"label": "Days ≤ 50% Recovery", "value": "days_50"}
            ],
            value="average",
            className="mb-4 p-10 form-select form-select-sm",
            style={"width": "90%", "margin": "0 auto"} 
        ),
        html.Div("Line Chart Granularity:", className="fw text-light mb-2", style={"fontSize": "0.8vw", "width": "90%", "margin": "0 auto", "textAlign": "left"}), 
        dbc.Select(
            id="time-granularity",
            options=[
                {"label": "Monthly", "value": "monthly"},
                {"label": "Weekly", "value": "weekly"},
                {"label": "Quarterly", "value": "quarterly"}
            ],
            value="monthly",
            className="mb-4 p-10 form-select form-select-sm",
            style={"width": "90%", "margin": "0 auto"}  
        ),
        
        html.Hr(className="mb-4"),
        
        
        # Tooltip and Info Section
        html.Div(
            [
                # Question Section
                html.Div(
                    [
                        html.Span(
                            "Question:", 
                            style={"fontSize": "0.85vw", "color": "white", "marginRight": "10px"}
                        ),
                        html.Div(
                            id="info-icon",
                            children=[
                                html.Span(
                                    dcc.Markdown(
                                        """
                                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" style="width: 1.05em; height: 1.05em; color: #bbbbbb; cursor: pointer;">
                                            <path fill="currentColor" d="M256 512A256 256 0 1 0 256 0a256 256 0 1 0 0 512zM169.8 165.3c7.9-22.3 29.1-37.3 52.8-37.3l58.3 0c34.9 0 63.1 28.3 63.1 63.1c0 22.6-12.1 43.5-31.7 54.8L280 264.4c-.2 13-10.9 23.6-24 23.6c-13.3 0-24-10.7-24-24l0-13.5c0-8.6 4.6-16.5 12.1-20.8l44.3-25.4c4.7-2.7 7.6-7.7 7.6-13.1c0-8.4-6.8-15.1-15.1-15.1l-58.3 0c-3.4 0-6.4 2.1-7.5 5.3l-.4 1.2c-4.4 12.5-18.2 19-30.6 14.6s-19-18.2-14.6-30.6l.4-1.2zM224 352a32 32 0 1 1 64 0 32 32 0 1 1 -64 0z"/>
                                        </svg>
                                        """,
                                        dangerously_allow_html=True,
                                    ),
                                    style={"display": "inline-block"}
                                )
                            ],
                        ),
                        dbc.Tooltip(
                            "The MTA Dashboard provides insights into the recovery trends of public transit services in New York City after the COVID-19 pandemic. Explore metrics like recovery percentages and service performance over time to gain a deeper understanding of post-pandemic transit recovery.",
                            target="info-icon",
                            placement="right",
                            className="custom-tooltip"
                        ),
                    ],
                    style={"display": "flex", "alignItems": "center", "marginBottom": "10px"}
                ),
                # Link Section
                html.Div(
                    [
                        html.Span(
                            "More info:", 
                            style={"fontSize": "0.85vw", "color": "white", "marginRight": "10px"}
                        ),
                        html.A(
                            href="https://new.mta.info",
                            target="_blank",
                            children=[
                                dcc.Markdown(
                                    """
                                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" style="width: 1.05em; height: 1.05em; color: #bbbbbb; cursor: pointer;">
                                        <path fill="currentColor" d="M320 0c-17.7 0-32 14.3-32 32s14.3 32 32 32l82.7 0L201.4 265.4c-12.5 12.5-12.5 32.8 0 45.3s32.8 12.5 45.3 0L448 109.3l0 82.7c0 17.7 14.3 32 32 32s32-14.3 32-32l0-160c0-17.7-14.3-32-32-32L320 0zM80 32C35.8 32 0 67.8 0 112L0 432c0 44.2 35.8 80 80 80l320 0c44.2 0 80-35.8 80-80l0-112c0-17.7-14.3-32-32-32s-32 14.3-32 32l0 112c0 8.8-7.2 16-16 16L80 448c-8.8 0-16-7.2-16-16l0-320c0-8.8 7.2-16 16-16l112 0c17.7 0 32-14.3 32-32s-14.3-32-32-32L80 32z"/>
                                    </svg>
                                    """,
                                    dangerously_allow_html=True,
                                ),
                            ],
                        ),
                    ],
                    style={"display": "flex", "alignItems": "center"}
                ),
            ],
            className="mb-4",
            style={"width": "90%", "margin": "0 auto"}
        )



        
    ],
    width=2,
    className="bg-primary text-light p-3 sticky-top",
    style={"height": "100vh", "overflowY": "auto"}
)




# Layout for the app
app.layout = dbc.Container(
    dbc.Row(
        [
            # Sidebar
            sidebar,

            # Main content
            dbc.Col(
                [
                    # Top Section: Summary Metrics
                    dbc.Row(
                        id="metrics-row",  # ID for dynamic metric change
                        children = [
                            dbc.Col(
                                html.Div(
                                    [
                                        html.H3( f"{value :.1%}" , className="text-center mb-0", style={"fontSize": "1.7vw"} ),
                                        html.Small(metric_name, className="text-muted text-center d-block", style={"fontSize": "0.75vw"})
                                    ],
                                    className="p-3 bg-primary text-light rounded shadow-sm"
                                ),
                                style={"flex": "1 1 calc(100% / 7 - 10px)"}
                            )
                            for metric_name, value  in summary_metrics.items()
                        ],
                        className="g-3 mb-3 d-flex justify-content-between"
                    ),

                    # Middle Section: Charts
                    dbc.Row(
                        [
                            dbc.Col(
                                html.Div(
                                    dcc.Graph(
                                        id='bar-chart',
                                        figure=px.bar(
                                            y=list(summary_metrics.keys()),
                                            x=list(summary_metrics.values()),
                                            title="Average Daily Recovery by Service",
                                            orientation='h'
                                        ).update_layout(
                                             plot_bgcolor="rgba(0,0,0,0)",
                                             paper_bgcolor="rgba(0,0,0,0)",
                                             font=dict(size=11),
                                             showlegend=False,
                                             title=dict(font=dict(size=15), pad=dict(b=20), x=0.01, y= 1),
                                             margin=dict(l=20, r=20, t=35, b=20),
                                             xaxis_title=None, yaxis_title=None,
                                             xaxis=dict( automargin=True, tickformat="0%", showgrid=False, zeroline=False ),
                                             yaxis=dict( ticks="outside", ticklen=2, tickcolor="rgba(0,0,0,0)", automargin=True, showgrid=False, zeroline=False ),
                                             template= "plotly_dark"
                                         ).update_traces( marker=dict(line=dict(width=0)), marker_color= default_color ),
                                        style={"height": "48vh", "width": "100%"}
                                    ),
                                    className="p-3 bg-primary rounded shadow-sm"
                                ),
                                width=4
                            ),

                            dbc.Col(
                                html.Div(
                                    dcc.Graph(
                                        id='line-chart',
                                        figure=px.line(
                                            monthly_avg.melt(id_vars=["Month"], value_vars=[
                                                "Subways: % of Comparable Pre-Pandemic Day",
                                                "Buses: % of Comparable Pre-Pandemic Day",
                                                "LIRR: % of Comparable Pre-Pandemic Day",
                                                "Metro-North: % of Comparable Pre-Pandemic Day",
                                                "Access-A-Ride: % of Comparable Pre-Pandemic Day",
                                                "Bridges and Tunnels: % of Comparable Pre-Pandemic Day",
                                                "Staten Island Railway: % of Comparable Pre-Pandemic Day"
                                            ], var_name="Transport Service", value_name="Percentage"),
                                            x="Month",
                                            y="Percentage",
                                            title="Monthly Recovery Trends by Service"
                                        ).update_layout(
                                            plot_bgcolor="rgba(0,0,0,0)",
                                            paper_bgcolor="rgba(0,0,0,0)",
                                            showlegend=False,
                                            font=dict(size=11),
                                            title=dict(font=dict(size=15), pad=dict(b=20), x=0.01, y= 1),
                                            margin=dict(l=20, r=20, t=35, b=20),
                                            xaxis_title=None, yaxis_title=None,
                                            xaxis=dict( automargin=True, showgrid=False, zeroline=False ),
                                            yaxis=dict( automargin=True, tickformat="0%", showgrid=False, zeroline=False ),
                                            template= "plotly_dark",
                                            shapes=[ dict( type="line", x0=0, x1=1, xref="paper", y0=1, y1=1, yref="y", line=dict( color="grey", width=2, dash="dot" )  ) ]
                                        ).update_traces(line=dict(width=2.65,  color= default_color )),
                                        style={"height": "48vh", "width": "100%"}
                                    ),
                                    className="p-3 bg-primary rounded shadow-sm"
                                ),
                                width=8
                            )
                        ],
                        className="g-3 mb-3"
                    ),

                    # Bottom Section: Additional Charts
                    dbc.Row(
                        [
                            dbc.Col(
                                html.Div(
                                    dcc.Graph(
                                        id='yearly-breakdown',
                                        figure=px.bar(
                                            yearly_avg,
                                            x='Subways: % of Comparable Pre-Pandemic Day',
                                            y='Year',
                                            orientation='h',
                                            title="Yearly Average Recovery"
                                        ).update_traces(
                                             marker=dict(line=dict(width=0)),
                                             marker_color= default_color
                                        ).update_layout(
                                             plot_bgcolor="rgba(0,0,0,0)",
                                             paper_bgcolor="rgba(0,0,0,0)",
                                             font=dict(size=11),
                                             title=dict(font=dict(size=15), pad=dict(b=20), x=0.01, y= 1),
                                             margin=dict(l=20, r=20, t=35, b=20),
                                             xaxis_title=None, yaxis_title=None,
                                             xaxis=dict( automargin=True, tickformat="0%",  showgrid=False, zeroline=False ),
                                             yaxis=dict( type="category", ticks="outside", ticklen=2, tickcolor="rgba(0,0,0,0)", automargin=True, showgrid=False, zeroline=False ),
                                             template= "plotly_dark"
                                         ),
                                        style={"height": "21vh", "width": "100%"}
                                        
                                    ),
                                    className="p-3 bg-primary rounded shadow-sm"
                                ),
                                width=4
                            ),
                            dbc.Col(
                                html.Div(
                                    dcc.Graph(
                                        id='monthly-breakdown',
                                        figure=px.bar(
                                            monthly_avg_b,
                                            x='Month_Name',
                                            y='Subways: % of Comparable Pre-Pandemic Day',
                                            title="Monthly Average Recovery"
                                        ).update_traces(
                                             marker=dict(line=dict(width=0)),
                                             marker_color= default_color
                                        ).update_layout(
                                             plot_bgcolor="rgba(0,0,0,0)",
                                             paper_bgcolor="rgba(0,0,0,0)",
                                             font=dict(size=11),
                                             title=dict(font=dict(size=15), pad=dict(b=20), x=0.01, y= 1),
                                             margin=dict(l=20, r=20, t=35, b=20),
                                             xaxis_title=None, yaxis_title=None,
                                             xaxis=dict( ticks="outside", ticklen=2, tickcolor="rgba(0,0,0,0)", automargin=True, showgrid=False, zeroline=False ),
                                             yaxis=dict( automargin=True, tickformat="0%",  showgrid=False, zeroline=False ),
                                             template= "plotly_dark"
                                         ),
                                        style={"height": "21vh", "width": "100%"}
                                    ),
                                    className="p-3 bg-primary rounded shadow-sm"
                                ),
                                width=4
                            ),
                            dbc.Col(
                                html.Div(
                                    dcc.Graph(
                                        id='day-of-week-breakdown',
                                        figure=px.bar(
                                            day_of_week_avg,
                                            x='Day_of_Week',
                                            y='Subways: % of Comparable Pre-Pandemic Day',
                                            title="Day of the Week Average Recovery"
                                        ).update_traces(
                                             marker=dict(line=dict(width=0)),
                                             marker_color= default_color
                                        ).update_layout(
                                             plot_bgcolor="rgba(0,0,0,0)",
                                             paper_bgcolor="rgba(0,0,0,0)",
                                             font=dict(size=11),
                                             title=dict(font=dict(size=15), pad=dict(b=20), x=0.01, y= 1),
                                             margin=dict(l=20, r=20, t=35, b=20),
                                             xaxis_title=None, yaxis_title=None,
                                             xaxis=dict( ticks="outside", ticklen=2, tickcolor="rgba(0,0,0,0)", automargin=True, showgrid=False, zeroline=False ),
                                             yaxis=dict( automargin=True, tickformat="0%",  showgrid=False, zeroline=False ),
                                             template= "plotly_dark"
                                         ),
                                        style={"height": "21vh", "width": "100%"}
                                    ),
                                    className="p-3 bg-primary rounded shadow-sm"
                                ),
                                width=4
                            )
                        ],
                        className="g-3"
                    )
                ],
                width=10,
                className= "pt-5 pb-5 ps-5 pe-5" 
            )
        ],
    ),
    fluid=True,
    className="vh-100"
)

# New Call Back                                                             ------------------------------------------------------------------------------------------------------------- 

@app.callback(
    [
        Output("metrics-row", "children"),
        Output("bar-chart", "figure"),
        Output("line-chart", "figure"),
        Output("yearly-breakdown", "figure"),
        Output("monthly-breakdown", "figure"),
        Output("day-of-week-breakdown", "figure")
    ],
    [
        Input("year-selector", "value"),
        Input("metric-type", "value"),
        Input("service-selector", "value"),
        Input("time-granularity", "value")
    ]
)
def update_dashboard(selected_year, selected_metric, selected_service, granularity):
    
    # Filter the dataset by the selected year
    df_filtered = df if selected_year == "All" else df[df['Year'] == int(selected_year) ]
    
    summary_metrics = {
    "Subways": df_filtered["Subways: % of Comparable Pre-Pandemic Day"].mean(),
    "Buses": df_filtered["Buses: % of Comparable Pre-Pandemic Day"].mean(),
    "LIRR": df_filtered["LIRR: % of Comparable Pre-Pandemic Day"].mean(),
    "Metro North": df_filtered["Metro-North: % of Comparable Pre-Pandemic Day"].mean(),
    "Access-A": df_filtered["Access-A-Ride: % of Comparable Pre-Pandemic Day"].mean(),
    "Bridges and Tunnels": df_filtered["Bridges and Tunnels: % of Comparable Pre-Pandemic Day"].mean(),
    "Staten Island Railway": df_filtered["Staten Island Railway: % of Comparable Pre-Pandemic Day"].mean()
    }

    sorted_summary_metrics = dict(sorted(summary_metrics.items(), key=lambda item: item[1] ))

    selected_column = service_mapping[selected_service]
    
    days_100_recovery = {
    "Subways": (df_filtered["Subways: % of Comparable Pre-Pandemic Day"] >= 1).sum(),
    "Buses": (df_filtered["Buses: % of Comparable Pre-Pandemic Day"] >= 1).sum(),
    "LIRR": (df_filtered["LIRR: % of Comparable Pre-Pandemic Day"] >= 1).sum(),
    "Metro North": (df_filtered["Metro-North: % of Comparable Pre-Pandemic Day"] >= 1).sum(),
    "Access-A": (df_filtered["Access-A-Ride: % of Comparable Pre-Pandemic Day"] >= 1).sum(),
    "Bridges and Tunnels": (df_filtered["Bridges and Tunnels: % of Comparable Pre-Pandemic Day"] >= 1).sum(),
    "Staten Island Railway": (df_filtered["Staten Island Railway: % of Comparable Pre-Pandemic Day"] >= 1).sum(),
    }

    days_below_50_recovery = {
    "Subways": (df_filtered["Subways: % of Comparable Pre-Pandemic Day"] <= 0.5 ).sum(),
    "Buses": (df_filtered["Buses: % of Comparable Pre-Pandemic Day"] <= 0.5).sum(),
    "LIRR": (df_filtered["LIRR: % of Comparable Pre-Pandemic Day"] <= 0.5 ).sum(),
    "Metro North": (df_filtered["Metro-North: % of Comparable Pre-Pandemic Day"] <= 0.5 ).sum(),
    "Access-A": (df_filtered["Access-A-Ride: % of Comparable Pre-Pandemic Day"] <= 0.5 ).sum(),
    "Bridges and Tunnels": (df_filtered["Bridges and Tunnels: % of Comparable Pre-Pandemic Day"] <= 0.5 ).sum(),
    "Staten Island Railway": (df_filtered["Staten Island Railway: % of Comparable Pre-Pandemic Day"] <= 0.5 ).sum(),
    }

    # Yearly average
    yearly_avg = df.groupby('Year').agg({selected_column: 'mean'}).reset_index()

    # Monthly average (sort by month order)
    monthly_avg_b = df_filtered.groupby('Month_Name').agg({selected_column: 'mean'}).reset_index()
    month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    monthly_avg_b['Month_Name'] = pd.Categorical(monthly_avg_b['Month_Name'], categories=month_order, ordered=True)
    monthly_avg_b = monthly_avg_b.sort_values('Month_Name')

    # Day-of-week average (sort by weekday order)
    day_of_week_avg = df_filtered.groupby('Day_of_Week').agg({selected_column: 'mean'}).reset_index()
    day_of_week_order = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    day_of_week_avg['Day_of_Week'] = pd.Categorical(day_of_week_avg['Day_of_Week'], categories=day_of_week_order, ordered=True)
    day_of_week_avg = day_of_week_avg.sort_values('Day_of_Week')


    color = service_colors[selected_service] 


    # --- Changing  metrics
    
    if selected_metric == "average":
        metrics = summary_metrics
    elif selected_metric == "days_100":
        metrics = days_100_recovery
    elif selected_metric == "days_50":
        metrics = days_below_50_recovery   

    updated_metrics_row= [
        dbc.Col(
            html.Div(
                [
                    html.H3(
                        [
                            html.Span(
                                "●", 
                                style={
                                    "color": service_colors[selected_service] if metric_name == selected_service else "transparent",
                                    "marginRight": "10px" if metric_name == selected_service else "0px",
                                    "fontSize": "1.5vw" if metric_name == selected_service else "0px"
                                }
                            ),
                            f"{value:.1%}" if selected_metric == "average" else f"{value}" 
                        ],
                        className="text-center mb-0",
                        style={"fontSize": "1.5vw"}
                    ),
                    html.Small(metric_name, className="text-muted text-center d-block", style={"fontSize": "0.75vw"})
                ],
                className="p-3 bg-primary text-light rounded shadow-sm"
            ),
            style={"flex": "1 1 calc(100% / 7 - 10px)"}
        )
        for metric_name, value in metrics.items()
    ]

    
    # --- Updating  bar chart
    
    colors = ["#484E54" if service != selected_service else service_colors[selected_service]
              for service in sorted_summary_metrics.keys()]

    updated_bar_chart = px.bar(
        y= sorted_summary_metrics.keys(),
        x= sorted_summary_metrics.values(),
        title="Average Daily Recovery by Service",
        orientation='h'
    ).update_traces(
        marker=dict(line=dict(width=0)),
        marker_color=colors,
        hovertemplate="Service: %{y}<br>Value: %{x:.1%}<extra></extra>"
    ).update_layout(
         plot_bgcolor="rgba(0,0,0,0)",
         paper_bgcolor="rgba(0,0,0,0)",
         font=dict(size=11),
         showlegend=False,
         title=dict(font=dict(size=15), pad=dict(b=20), x=0.01, y= 1),
         margin=dict(l=20, r=20, t=35, b=20),
         xaxis_title=None, yaxis_title=None,
         xaxis=dict( automargin=True, tickformat="0%", showgrid=False, zeroline=False ),
         yaxis=dict( ticks="outside", ticklen=2, tickcolor="rgba(0,0,0,0)", automargin=True, showgrid=False, zeroline=False ),
         template= "plotly_dark"
     )


    # --- Updating line chart
    if granularity == "monthly":
        data = df_filtered.groupby('Month').mean(numeric_only=True).reset_index()
        data['Month'] = data['Month'].dt.to_timestamp()
        x_axis = "Month"
    
    elif granularity == "weekly":
        data = df_filtered.groupby('Week').mean(numeric_only=True).reset_index()
        data['Week'] = data['Week'].dt.to_timestamp()
        x_axis = "Week"
    
    elif granularity == "quarterly":
        data = df_filtered.groupby('Quarter').mean(numeric_only=True).reset_index()
        data['Quarter'] = data['Quarter'].dt.to_timestamp()
        x_axis = "Quarter"
    
    melted_data = data.melt(
        id_vars=[x_axis],
        value_vars=list(service_mapping.values()),
        var_name="Transport Service",
        value_name="Percentage"
    )
    
    melted_data["Short Name"] = melted_data["Transport Service"].map(service_short_names)

    selected_data = melted_data[melted_data["Transport Service"] == selected_column]
    other_data = melted_data[melted_data["Transport Service"] != selected_column]
    reordered_data = pd.concat([other_data, selected_data])  # Selected service last
    
    updated_line_chart = px.line(
        reordered_data,
        x=x_axis,
        y="Percentage",
        color="Transport Service",
        title=f"{granularity.capitalize()} Recovery Trends by Service",
        custom_data=["Short Name"]  # Add short names for hovertemplate
    )
    
    updated_line_chart.for_each_trace(lambda trace: trace.update(
            line=dict(
                width= 3.3 , # if trace.name == selected_column else 2.65,
                color=service_colors_line_chart[trace.name] if trace.name == selected_column else default_color
            ),
            hovertemplate=(
                "Service: %{customdata[0]}<br>"
                "Date: %{x}<br>"
                "Value: %{y:.1%}<extra></extra>"
            )
        )
    )
    
    updated_line_chart.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        font=dict(size=11),
        title=dict(font=dict(size=15), pad=dict(b=20), x=0.01, y=1),
        margin=dict(l=20, r=20, t=35, b=20),
        xaxis_title=None,
        yaxis_title=None,
        xaxis=dict(automargin=True, showgrid=False, zeroline=False),
        yaxis=dict(automargin=True, tickformat="0%", showgrid=False, zeroline=False),
        template="plotly_dark",
        shapes=[dict(type="line", x0=0, x1=1, xref="paper", y0=1, y1=1, yref="y", line=dict(color="grey", width=2, dash="dot"))]
    )



    # --- Updating  yearly figure

    selected_year_int = int(selected_year) if selected_year != "All" else None
    color_yearly = [
        service_colors[selected_service] if selected_year_int is None or year == selected_year_int else "#484E54"
        for year in yearly_avg["Year"]
    ]
    
    updated_yearly_fig = px.bar(
        yearly_avg,
        x=selected_column,
        y='Year',
        orientation='h',
        title="Yearly Average Recovery"
    ).update_traces(
        marker=dict(line=dict(width=0)),
        marker_color= color_yearly,
        hovertemplate="Year: %{y}<br>Average: %{x:.1%}<extra></extra>"
    ).update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(size=11),
        title=dict(font=dict(size=15), pad=dict(b=20), x=0.01, y=1),
        margin=dict(l=20, r=20, t=35, b=20),
        xaxis_title=None, yaxis_title=None,
        xaxis=dict(automargin=True, tickformat="0%", showgrid=False, zeroline=False),
        yaxis=dict(type="category", ticks="outside", ticklen=2, tickcolor="rgba(0,0,0,0)", automargin=True, showgrid=False, zeroline=False),
        template="plotly_dark"
    )


    # --- Updating  monthly figure

    updated_monthly_fig = px.bar(
        monthly_avg_b,
        x='Month_Name',
        y=selected_column,
        title="Monthly Average Recovery"
    ).update_traces(
        marker=dict(line=dict(width=0)),
        marker_color=color,
        hovertemplate="Month: %{x}<br>Average: %{y:.1%}<extra></extra>" 
    ).update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(size=11),
        title=dict(font=dict(size=15), pad=dict(b=20), x=0.01, y=1),
        margin=dict(l=20, r=20, t=35, b=20),
        xaxis_title=None, yaxis_title=None,
        xaxis=dict(ticks="outside", ticklen=2, tickcolor="rgba(0,0,0,0)", automargin=True, showgrid=False, zeroline=False),
        yaxis=dict(automargin=True, tickformat="0%", showgrid=False, zeroline=False),
        template="plotly_dark"
    )

    
    # --- Updating  daily figure
    
    updated_day_of_week_fig = px.bar(
        day_of_week_avg,
        x='Day_of_Week',
        y=selected_column,
        title="Day of the Week Average Recovery"
    ).update_traces(
        marker=dict(line=dict(width=0)),
        marker_color=color,
        hovertemplate="Day: %{x}<br>Average: %{y:0.0%}<extra></extra>"
    ).update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(size=11),
        title=dict(font=dict(size=15), pad=dict(b=20), x=0.01, y=1),
        margin=dict(l=20, r=20, t=35, b=20),
        xaxis_title=None, yaxis_title=None,
        xaxis=dict(ticks="outside", ticklen=2, tickcolor="rgba(0,0,0,0)", automargin=True, showgrid=False, zeroline=False),
        yaxis=dict(automargin=True, tickformat="0%", showgrid=False, zeroline=False),
        template="plotly_dark"
    )


    # --- Returning
    
    return updated_metrics_row, updated_bar_chart, updated_line_chart, updated_yearly_fig, updated_monthly_fig, updated_day_of_week_fig



if __name__ == "__main__":
    app.run_server()
