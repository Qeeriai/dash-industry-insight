import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd

# Load the data
df_employment_outlook = pd.read_csv('data/employment_outlook.csv')

# Initialize the app
app = dash.Dash(__name__)
server = app.server

# Define the layout with tabs
app.layout = html.Div([
    html.H1("Employment Outlook Dashboard"),
    
    dcc.Tabs(id='tabs', value='tab-1', children=[
        dcc.Tab(label='Overview', value='tab-1'),
        dcc.Tab(label='Detailed Analysis', value='tab-2'),
        dcc.Tab(label='Forecasts', value='tab-3'),
    ]),
    html.Div(id='tabs-content')
])

# Callback to update content based on selected tab
@app.callback(Output('tabs-content', 'children'),
              Input('tabs', 'value'))
def render_content(tab):
    if tab == 'tab-1':
        return html.Div([
            html.H3('Overview of Employment Trends'),
            dcc.Graph(
                figure=px.line(df_employment_outlook, x='Year', y='Employment Level', color='Occupation')
            )
        ])
    elif tab == 'tab-2':
        return html.Div([
            html.H3('Detailed Analysis by Occupation'),
            dcc.Graph(
                figure=px.bar(df_employment_outlook, x='Occupation', y='Employment Level', color='Year', barmode='group')
            )
        ])
    elif tab == 'tab-3':
        return html.Div([
            html.H3('Employment Forecasts'),
            dcc.Graph(
                figure=px.line(df_employment_outlook[df_employment_outlook['Year'] >= 2021], x='Year', y='Employment Level', color='Occupation')
            )
        ])

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, port=8081)
