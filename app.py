import dash
from dash import Dash, dcc, html, Input, Output
import plotly.graph_objs as go
import pandas as pd
import plotly.colors as pcolors
import plotly.express as px
import json
from flask_cors import CORS


# Load the data
df_employment_outlook = pd.read_csv('data/employment_outlook.csv')

# Load GeoJSON data for Australian states
with open('data/states.min.geojson') as f:
    geojson_data = json.load(f)

# Initialize the app
app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
app.title = "Job Industry Insights Dashboard"
server = app.server
CORS(app.server)  # Enable CORS to allow communication between Dash and React


# Predefined Plotly color scale
color_scale = pcolors.qualitative.Plotly

# Function to generate a color from the predefined palette
def generate_color(index):
    return color_scale[index % len(color_scale)]

# Consistent color mapping for gender
GENDER_COLORS = {
    'Male Share': '#636EFA',  # Blue
    'Female Share': '#EF553B'  # Red
}

# Define default occupations to pre-fill
default_occupations = ['Primary School Teachers', 'Middle School Teachers','Special Education Teachers']

# Define layout
app.layout = html.Div([
    html.Div([
        html.H5("Job Industry Analytics", style={"color": "#2c82ff"}),
        html.H3("Welcome to the Job Industry Insights Dashboard", style={"marginBottom": "20px"}),
        html.Div(
            "Explore job industry trends, job demand, salary, and employee satisfaction. Select different filters to visualize insights over time.",
            style={"marginBottom": "30px"}
        ),
        html.Div([
            html.Label("Select Occupation:", style={'font-weight': 'bold', 'margin-top': '10px'}),
            dcc.Dropdown(
                id='occupation-filter',
                options=[{'label': occ, 'value': occ} for occ in df_employment_outlook['Occupation'].unique()],
                value=default_occupations,
                placeholder="Select Occupation",
                multi=True
            ),]
        , style={"padding": "10px"}),  # Adjust the padding here to reduce space
    ], className="four columns", style={
        "padding": "20px", 
        "backgroundColor": "#f9f9f9",
        "flexShrink": "0",     # Prevents shrinking when the window resizes
        "position": "sticky",   # Makes the sidebar sticky
        "top": "0",             # Sticks the sidebar to the top when scrolling
        "height": "100vh"      # Ensures the sidebar takes the full height
        }),  

    html.Div([
        html.Div([
            html.B("Employment Trend (2011-2026)"),
            html.Hr(),
            dcc.Graph(id='employment-trend'),
        ], style={"marginBottom": "30px", "backgroundColor": "#ffffff", "padding": "20px"}),
        html.Div([
            html.B("Employment Forecast Metrics"),
            html.Hr(),
            html.Table(id='forecast-metrics', style={'margin-top': '20px'}),
        ], style={"backgroundColor": "#ffffff", "padding": "20px"}),
        html.Div([
            html.B("Age Profile (% Share)"),
            html.Hr(),
            dcc.Graph(id='age-distribution-graph'),
        ], style={"backgroundColor": "#ffffff", "padding": "20px"}),
        
        # Place the two donut charts in a row
        html.Div([
            html.B("Gender and Employment Type"),
            html.Hr(),
            html.Div([
                html.Div([
                    dcc.Graph(id='gender-donut-chart'),
                ], className="six columns", style={"backgroundColor": "#ffffff", "padding": "20px"}),

                html.Div([
                    dcc.Graph(id='employment-type-donut-chart'),
                ], className="six columns", style={"backgroundColor": "#ffffff", "padding": "20px"}),
            ], className="row", style={"width": "100%", "display": "flex", "flex-direction": "row"}),
        
        ], style={"backgroundColor": "#ffffff", "padding": "20px"}),

           # New Graph for Gender by Occupation
        html.Div([
            dcc.Graph(id='gender-per-occupation-bar'),
        ], style={"marginTop": "30px", "backgroundColor": "#ffffff", "padding": "20px"}),


        html.Div([
            html.B("Employment Distribution by State"),
            html.Hr(),
            dcc.Graph(id='state-map'),
        ], style={"backgroundColor": "#ffffff", "padding": "20px"}),
        
    ], className="eight columns", style={
        "padding": "10px",
        "flex": "1",  # Ensures the right section expands to take up remaining space
        "overflowY": "auto",      # Enables vertical scrolling
        "height": "100vh"         # Matches height with the sidebar
        }),  
], className="row", style={
    "width": "100%", 
    "display": "flex", 
    "flex-direction": "row",
    "height": "100vh",
    "overflow": "hidden"        # Prevents parent container from scrolling

    })



# Callback to update the graph and metrics
@app.callback(
    [Output('employment-trend', 'figure'),
     Output('forecast-metrics', 'children')],
     Input('occupation-filter', 'value')
)
def update_graph(selected_occupations):
    # Filter data based on selected ANZSCO codes and selected occupations
    if  selected_occupations:
        filtered_df = df_employment_outlook[df_employment_outlook['Occupation'].isin(selected_occupations)]
    else:
        filtered_df = df_employment_outlook

    # Create traces for the graph
    traces = []
    for idx, occupation in enumerate(filtered_df['Occupation'].unique()):
        color = generate_color(idx)
        
        # Historical data trace
        historical_df = filtered_df[(filtered_df['Occupation'] == occupation) & (filtered_df['Metric'] == 'Employment')]
        trace = go.Scatter(
            x=historical_df['Year'],
            y=historical_df['Value'],
            mode='lines+markers',
            name=occupation,
            line=dict(color=color, width=2)
        )
        traces.append(trace)
        
        # Forecasted data trace
        forecast_df = filtered_df[(filtered_df['Occupation'] == occupation) & (filtered_df['Metric'] == 'Projected Employment level')]
        if not forecast_df.empty:
            combined_df = pd.concat([historical_df, forecast_df])
            trace_forecast = go.Scatter(
                x=combined_df['Year'],
                y=combined_df['Value'],
                mode='lines+markers',
                name=f"{occupation} (Forecast)",
                line=dict(color=color, dash='dash', width=2)
            )
            traces.append(trace_forecast)

    # Create the figure
    figure = {
        'data': traces,
        'layout': go.Layout(
            title='Employment Trend (2011-2026)',
            xaxis={'title': 'Year'},
            yaxis={'title': 'Employment Level'},
            hovermode='closest'
        )
    }
    
    # Create the forecast metrics table
    # Define a function to determine the color based on the Future Growth Rating
    def get_color_for_growth_rating(rating):
        if rating == 'Very Strong':
            return '#28a745'  # Green
        elif rating == 'Strong':
            return '#17a2b8'  # Blue
        elif rating == 'Moderate':
            return '#ffc107'  # Yellow
        elif rating == 'Stable':
            return '#6c757d'  # Grey
        elif rating == 'Decline':
            return '#dc3545'  # Red
        else:
            return '#000000'  # Default to black for any undefined levels

    # Create the forecast metrics table 
    forecast_metrics = []
    forecast_metrics.append(html.Tr([
        html.Th('Occupation'),
        html.Th('Future Growth Rating'),
        html.Th('Projected Employment Growth (%)')
    ]))

    for occupation in filtered_df['Occupation'].unique():
        metrics_df = filtered_df[(filtered_df['Occupation'] == occupation) & (filtered_df['Metric'] == 'Future Growth Rating')]
        if not metrics_df.empty:
            growth_rating = metrics_df['Value'].values[0]
            color = get_color_for_growth_rating(growth_rating)
            
            forecast_metrics.append(html.Tr([
                html.Td(occupation),
                html.Td(growth_rating, style={'color': color}),  
                html.Td(filtered_df[(filtered_df['Occupation'] == occupation) & (filtered_df['Metric'] == 'Projected Employment Growth (%)')]['Value'].values[0])
            ]))

    return figure, forecast_metrics

# Callback to update the age distribution graph
@app.callback(
    Output('age-distribution-graph', 'figure'),
     Input('occupation-filter', 'value')
)
def update_age_distribution(selected_occupations):
    # Filter data based on selected ANZSCO codes and selected occupations
    if selected_occupations:
        filtered_df = df_employment_outlook[df_employment_outlook['Occupation'].isin(selected_occupations)]
    else:
        filtered_df = df_employment_outlook

    # Filter the dataframe for age-related metrics
    age_df = filtered_df[filtered_df['Metric'].str.startswith('Age')]

    # Create traces for age distribution
    traces = []
    for idx, occupation in enumerate(age_df['Occupation'].unique()):
        occupation_age_df = age_df[age_df['Occupation'] == occupation]
        trace = go.Bar(
            y=occupation_age_df['Metric'],  # Age groups in the y-axis
            x=occupation_age_df['Value'],   # % Share in the x-axis
            name=occupation,
            orientation='h',
            marker=dict(color=generate_color(idx))
        )
        traces.append(trace)

    # Create the figure
    figure = {
        'data': traces,
        'layout': go.Layout(
            title='Age Profile (% Share)',
            xaxis={'title': '% Share'},
            yaxis={
                'title': 'Age Group',
                'categoryorder': 'array',
                'categoryarray': [
                    'Age 15 - 19',
                    'Age 20 - 24',
                    'Age 25 - 34',
                    'Age 35 - 44',
                    'Age 45 - 54',
                    'Age 55 - 59',
                    'Age 60 - 64',
                    'Age 65 +'
                ]
            },
            barmode='stack'
        )
    }
    
    return figure

# Callback to update the gender distribution donut chart
@app.callback(
    Output('gender-donut-chart', 'figure'),
     Input('occupation-filter', 'value')
)
def update_gender_donut_chart(selected_occupations):
    # Filter data based on selected ANZSCO codes and selected occupations
    if selected_occupations:
        filtered_df = df_employment_outlook[df_employment_outlook['Occupation'].isin(selected_occupations)]
    else:
        filtered_df = df_employment_outlook

    # Filter the dataframe for gender metrics
    gender_df = filtered_df[filtered_df['Metric'].isin(['Male Share', 'Female Share'])]

    # Aggregate the data if multiple occupations are selected
    aggregated_gender = gender_df.groupby('Metric')['Value'].mean().reset_index()

    # Create the gender donut chart
    figure = {
        'data': [go.Pie(
            labels=aggregated_gender['Metric'],
            values=aggregated_gender['Value'],
            hole=0.5,
            marker=dict(colors=[generate_color(i) for i in range(len(aggregated_gender))])
        )],
        'layout': go.Layout(
            title='Gender Distribution',
            showlegend=True
        )
    }

    return figure

# Callback to update the full-time/part-time distribution donut chart
@app.callback(
    Output('employment-type-donut-chart', 'figure'),
     Input('occupation-filter', 'value')
)
def update_employment_type_donut_chart(selected_occupations):
    # Filter data based on selected ANZSCO codes and selected occupations
    if selected_occupations:
        filtered_df = df_employment_outlook[df_employment_outlook['Occupation'].isin(selected_occupations)]
    else:
        filtered_df = df_employment_outlook

    # Filter the dataframe for employment type metrics
    employment_type_df = filtered_df[filtered_df['Metric'].isin(['Full-time Share', 'Part-time Share'])]

    # Aggregate the data if multiple occupations are selected
    aggregated_employment_type = employment_type_df.groupby('Metric')['Value'].mean().reset_index()

    # Create the employment type donut chart
    figure = {
        'data': [go.Pie(
            labels=aggregated_employment_type['Metric'],
            values=aggregated_employment_type['Value'],
            hole=0.5,
            marker=dict(colors=[generate_color(i) for i in range(len(aggregated_employment_type))])
        )],
        'layout': go.Layout(
            title='Employment Type Distribution',
            showlegend=True
        )
    }

    return figure

@app.callback(
    Output('gender-per-occupation-bar', 'figure'),
    Input('occupation-filter', 'value')
)

def update_gender_per_occupation(selected_occupations):
    # Filter the data based on selected occupations
    if selected_occupations:
        filtered_df = df_employment_outlook[df_employment_outlook['Occupation'].isin(selected_occupations)]
    else:
        filtered_df = df_employment_outlook

    # Filter the data for gender metrics
    gender_df = filtered_df[filtered_df['Metric'].isin(['Male Share', 'Female Share'])]

    # Create a bar chart showing gender distribution per occupation
    figure = {
        'data': [
            go.Bar(
                x=gender_df[gender_df['Metric'] == 'Male Share']['Occupation'],
                y=gender_df[gender_df['Metric'] == 'Male Share']['Value'],
                name='Male Share',
                marker=dict(color=GENDER_COLORS['Male Share'])  # For Male Share
            ),
            go.Bar(
                x=gender_df[gender_df['Metric'] == 'Female Share']['Occupation'],
                y=gender_df[gender_df['Metric'] == 'Female Share']['Value'],
                name='Female Share',
                marker=dict(color=GENDER_COLORS['Female Share'])  # For Female Share
            )
        ],
        'layout': go.Layout(
            title='Gender Distribution by Occupation',
            xaxis={'title': 'Occupation'},
            yaxis={'title': '% Share'},
            barmode='group',  # Bars side by side for comparison
        )
    }

    return figure


# Callback to update the map based on the selected occupations and codes
@app.callback(
    Output('state-map', 'figure'),
     Input('occupation-filter', 'value')
)
def update_state_map( selected_occupations):
    # Filter data based on  selected occupations
    if selected_occupations:
        filtered_df = df_employment_outlook[df_employment_outlook['Occupation'].isin(selected_occupations)]
    else:
        filtered_df = df_employment_outlook

    # Filter the dataframe for state-related metrics
    state_metrics = ['NSW (%)', 'VIC (%)', 'QLD (%)', 'SA (%)', 'WA (%)', 'TAS (%)', 'NT (%)', 'ACT (%)']
    state_df = filtered_df[filtered_df['Metric'].isin(state_metrics)]

    # Ensure values are numeric
    state_df['Value'] = pd.to_numeric(state_df['Value'], errors='coerce').fillna(0)

    # Aggregate the data by state
    aggregated_state = state_df.groupby('Metric')['Value'].mean().reset_index()
    state_map = {
        'NSW (%)': 'New South Wales',
        'VIC (%)': 'Victoria',
        'QLD (%)': 'Queensland',
        'SA (%)': 'South Australia',
        'WA (%)': 'Western Australia',
        'TAS (%)': 'Tasmania',
        'NT (%)': 'Northern Territory',
        'ACT (%)': 'Australian Capital Territory'
    }
    aggregated_state['State'] = aggregated_state['Metric'].map(state_map)

    # Create the map
    fig = px.choropleth(
        aggregated_state,
        geojson=geojson_data,
        locations='State',
        featureidkey="properties.STATE_NAME",
        color='Value',
        color_continuous_scale="Blues",  # Using a single color scale for density
        title='Employment Distribution by State'
    )

    # Update hover data to show percentage format
    fig.update_traces(
        hovertemplate='<b>%{location}</b><br>Value: %{z:.1f}%', 
        hoverinfo='location+z'
    )

    # Update the layout
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    return fig


# Run the app
if __name__ == '__main__':
    app.run_server()
