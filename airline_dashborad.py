# Import required libraries
import dash
import pandas as pd
import plotly.express as px
from dash import dcc, html
from dash.dependencies import Input, Output, State

# Create a Dash application
app = dash.Dash(__name__)
app.title = "US Domestic Airline Flights Performance"

# Suppress callback exceptions
app.config.suppress_callback_exceptions = True

# Read the airline data into pandas dataframe
airline_data = pd.read_csv(
    "airline_data.csv",
    encoding="ISO-8859-1",
    dtype={
        "Div1Airport": str,
        "Div1TailNum": str,
        "Div2Airport": str,
        "Div2TailNum": str,
    },
)

# List of years for dropdown
year_list = [i for i in range(2005, 2021, 1)]

# Compute data for Yearly Airline Performance Report
def compute_data_choice_1(df):
    bar_data = df.groupby(["Month", "CancellationCode"])["Flights"].sum().reset_index()
    line_data = (
        df.groupby(["Month", "Reporting_Airline"])["AirTime"].mean().reset_index()
    )
    div_data = df[df["DivAirportLandings"] != 0.0]
    map_data = df.groupby(["OriginState"])["Flights"].sum().reset_index()
    tree_data = (
        df.groupby(["DestState", "Reporting_Airline"])["Flights"].sum().reset_index()
    )
    return bar_data, line_data, div_data, map_data, tree_data

# Compute data for Yearly Airline Delay Report
def compute_data_choice_2(df):
    avg_car = (
        df.groupby(["Month", "Reporting_Airline"])["CarrierDelay"].mean().reset_index()
    )
    avg_weather = (
        df.groupby(["Month", "Reporting_Airline"])["WeatherDelay"].mean().reset_index()
    )
    avg_NAS = (
        df.groupby(["Month", "Reporting_Airline"])["NASDelay"].mean().reset_index()
    )
    avg_sec = (
        df.groupby(["Month", "Reporting_Airline"])["SecurityDelay"].mean().reset_index()
    )
    avg_late = (
        df.groupby(["Month", "Reporting_Airline"])["LateAircraftDelay"]
        .mean()
        .reset_index()
    )
    return avg_car, avg_weather, avg_NAS, avg_sec, avg_late

# Application layout
app.layout = html.Div(
    children=[
        # Dashboard title
        html.H1(
            "US Domestic Airline Flights Performance",
            style={"textAlign": "center", "color": "#503D36", "font-size": "24"},
        ),
        # Dropdown for report type selection
        html.Div(
            [
                html.Div(
                    [
                        html.H2("Report Type:", style={"margin-right": "2em"}),
                        dcc.Dropdown(
                            id="input-type",
                            options=[
                                {
                                    "label": "Yearly Airline Performance Report",
                                    "value": "OPT1",
                                },
                                {
                                    "label": "Yearly Airline Delay Report",
                                    "value": "OPT2",
                                },
                            ],
                            placeholder="Select a report type",
                            style={
                                "width": "80%",
                                "padding": "3px",
                                "font-size": "20px",
                                "textAlign": "center",
                            },
                        ),
                    ],
                    style={"display": "flex"},
                ),
                # Dropdown for year selection
                html.Div(
                    [
                        html.H2("Choose Year:", style={"margin-right": "2em"}),
                        dcc.Dropdown(
                            id="input-year",
                            options=[{"label": i, "value": i} for i in year_list],
                            placeholder="Select a year",
                            style={
                                "width": "80%",
                                "padding": "3px",
                                "font-size": "20px",
                                "text-align-last": "center",
                            },
                        ),
                    ],
                    style={"display": "flex"},
                ),
            ]
        ),
        # Divisions to display graphs
        html.Div([], id="plot1"),
        html.Div(
            [html.Div([], id="plot2"), html.Div([], id="plot3")],
            style={"display": "flex"},
        ),
        html.Div(
            [html.Div([], id="plot4"), html.Div([], id="plot5")],
            style={"display": "flex"},
        ),
    ]
)

# Callback function to update graphs based on user inputs
@app.callback(
    [
        Output(component_id="plot1", component_property="children"),
        Output(component_id="plot2", component_property="children"),
        Output(component_id="plot3", component_property="children"),
        Output(component_id="plot4", component_property="children"),
        Output(component_id="plot5", component_property="children"),
    ],
    [
        Input(component_id="input-type", component_property="value"),
        Input(component_id="input-year", component_property="value"),
    ],
    [
        State("plot1", "children"),
        State("plot2", "children"),
        State("plot3", "children"),
        State("plot4", "children"),
        State("plot5", "children"),
    ],
)
def get_graph(chart, year, children1, children2, c3, c4, c5):
    df = airline_data[airline_data["Year"] == int(year)]  # Filter data by year

    if chart == "OPT1":
        # Compute data for performance report
        bar_data, line_data, div_data, map_data, tree_data = compute_data_choice_1(df)

        # Bar graph for cancellations
        bar_fig = px.bar(
            bar_data,
            x="Month",
            y="Flights",
            color="CancellationCode",
            title="Monthly Flight Cancellation",
        )

        # Line graph for average airtime
        line_fig = px.line(
            line_data,
            x="Month",
            y="AirTime",
            color="Reporting_Airline",
            title="Average monthly flight time (minutes) by airline",
        )

        # Pie chart for diverted flights
        pie_fig = px.pie(
            div_data,
            values="Flights",
            names="Reporting_Airline",
            title="% of flights by reporting airline",
        )

        # Choropleth map for flights from origin states
        map_fig = px.choropleth(
            map_data,
            locations="OriginState",
            color="Flights",
            hover_data=["OriginState", "Flights"],
            locationmode="USA-states",
            color_continuous_scale="GnBu",
            range_color=[0, map_data["Flights"].max()],
        )
        map_fig.update_layout(
            title_text="Number of flights from origin state", geo_scope="usa"
        )

        # Treemap for flights to destination states
        tree_fig = px.treemap(
            tree_data,
            path=["DestState", "Reporting_Airline"],
            values="Flights",
            color="Flights",
            color_continuous_scale="RdBu",
            title="Flight count by airline to destination state",
        )

        return [
            dcc.Graph(figure=tree_fig),
            dcc.Graph(figure=pie_fig),
            dcc.Graph(figure=map_fig),
            dcc.Graph(figure=bar_fig),
            dcc.Graph(figure=line_fig),
        ]
    else:
        # Compute data for delay report
        avg_car, avg_weather, avg_NAS, avg_sec, avg_late = compute_data_choice_2(df)

        # Line graphs for various delays
        carrier_fig = px.line(
            avg_car,
            x="Month",
            y="CarrierDelay",
            color="Reporting_Airline",
            title="Average carrier delay time (minutes) by airline",
        )
        weather_fig = px.line(
            avg_weather,
            x="Month",
            y="WeatherDelay",
            color="Reporting_Airline",
            title="Average weather delay time (minutes) by airline",
        )
        nas_fig = px.line(
            avg_NAS,
            x="Month",
            y="NASDelay",
            color="Reporting_Airline",
            title="Average NAS delay time (minutes) by airline",
        )
        sec_fig = px.line(
            avg_sec,
            x="Month",
            y="SecurityDelay",
            color="Reporting_Airline",
            title="Average security delay time (minutes) by airline",
        )
        late_fig = px.line(
            avg_late,
            x="Month",
            y="LateAircraftDelay",
            color="Reporting_Airline",
            title="Average late aircraft delay time (minutes) by airline",
        )

        return [
            dcc.Graph(figure=carrier_fig),
            dcc.Graph(figure=weather_fig),
            dcc.Graph(figure=nas_fig),
            dcc.Graph(figure=sec_fig),
            dcc.Graph(figure=late_fig),
        ]

# Run the app
if __name__ == "__main__":
    app.run_server()
