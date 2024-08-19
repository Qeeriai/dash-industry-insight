import dash
from dash import dcc, html, Input, Output
import pandas as pd
import numpy as np
from datetime import datetime as dt
import pathlib
import plotly.express as px


app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
app.title = "Job Industry Insights Dashboard"

server = app.server
app.config.suppress_callback_exceptions = True

# Generate mock data
np.random.seed(42)

dates = pd.date_range(start="2023-01-01", end="2023-12-31", freq='M')
industries = ["Technology", "Healthcare", "Finance","Education"]
regions = ["North America", "Europe", "Asia", "South America", "Africa","Australia"]

data = {
    "Date": np.tile(dates, len(industries) * len(regions)),
    "Industry": np.repeat(industries, len(dates) * len(regions)),
    "Region": np.tile(np.repeat(regions, len(dates)), len(industries)),
    "Job Demand": np.random.randint(50000, 200000, len(dates) * len(industries) * len(regions)),
    "Growth Rate": np.random.uniform(2, 10, len(dates) * len(industries) * len(regions)),
    "Average Salary": np.random.uniform(60000, 120000, len(dates) * len(industries) * len(regions)),
    "Employee Satisfaction": np.random.uniform(3, 5, len(dates) * len(industries) * len(regions)),
}

df = pd.DataFrame(data)

# Layout
app.layout = html.Div([
    html.Div([
        html.H5("Job Industry Analytics", style={"color": "#2c82ff"}),
        html.H3("Welcome to the Job Industry Insights Dashboard", style={"marginBottom": "20px"}),
        html.Div(
            "Explore job industry trends, job demand, salary, and employee satisfaction. Select different filters to visualize insights over time.",
            style={"marginBottom": "30px"}
        ),
        html.Div([
            html.Label("Select Industry"),
            dcc.Dropdown(
                id="industry-select",
                options=[{"label": industry, "value": industry} for industry in df["Industry"].unique()],
                value=["Technology", "Healthcare", "Finance"],
                multi=True
            ),
            html.Br(),
            html.Label("Select Region"),
            dcc.Dropdown(
                id="region-select",
                options=[{"label": region, "value": region} for region in df["Region"].unique()],
                value=df["Region"].unique(),
                multi=True
            ),
            html.Br(),
            html.Label("Select Time Range"),
            dcc.DatePickerRange(
                id="date-picker-select",
                start_date=dt(2023, 1, 1),
                end_date=dt(2023, 12, 31),
                min_date_allowed=dt(2023, 1, 1),
                max_date_allowed=dt(2023, 12, 31),
                initial_visible_month=dt(2023, 1, 1)
            ),
            html.Br(),
        ], style={"padding": "20px"}),
    ], className="four columns", style={"padding": "20px", "backgroundColor": "#f9f9f9"}),

    html.Div([
        html.Div([
            html.B("Job Demand Over Time (Monthly Average)"),
            html.Hr(),
            dcc.Graph(id="job-demand-graph"),
        ], style={"marginBottom": "30px", "backgroundColor": "#ffffff", "padding": "20px"}),
        html.Div([
            html.B("Growth Rate Over Time"),
            html.Hr(),
            dcc.Graph(id="growth-rate-graph"),
        ], style={"marginBottom": "30px", "backgroundColor": "#ffffff", "padding": "20px"}),
        html.Div([
            html.B("Average Salary and Employee Satisfaction Over Time"),
            html.Hr(),
            dcc.Graph(id="salary-graph"),
        ], style={"backgroundColor": "#ffffff", "padding": "20px"}),
    ], className="eight columns", style={"padding": "20px"}),
], className="row", style={"width": "100%", "display": "flex", "flex-direction": "row"})


# Callbacks
@app.callback(
    [Output("job-demand-graph", "figure"),
     Output("growth-rate-graph", "figure"),
     Output("salary-graph", "figure")],
    [Input("industry-select", "value"),
     Input("region-select", "value"),
     Input("date-picker-select", "start_date"),
     Input("date-picker-select", "end_date")]
)
def update_graphs(selected_industries, selected_regions, start_date, end_date):
    filtered_df = df[(df["Industry"].isin(selected_industries)) &
                     (df["Region"].isin(selected_regions)) &
                     (df["Date"] >= start_date) &
                     (df["Date"] <= end_date)]

    # Job Demand Graph
    job_demand_fig = px.area(
        filtered_df,
        x="Date",
        y="Job Demand",
        color="Industry",
        title=""
    )

    # Growth Rate Graph
    growth_rate_fig = px.bar(
        filtered_df,
        x="Date",
        y="Growth Rate",
        color="Industry",
        barmode="group",
        title=""
    )

    # Average Salary Graph
    salary_fig = px.scatter(
        filtered_df,
        x="Date",
        y="Average Salary",
        color="Industry",
        size="Employee Satisfaction",
        title=""
    )

    return job_demand_fig, growth_rate_fig, salary_fig


if __name__ == "__main__":
    app.run_server(debug=True)

# Run the server
if __name__ == "__main__":
    app.run_server(debug=True, port=8051)
