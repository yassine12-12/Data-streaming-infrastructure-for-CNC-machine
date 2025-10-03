import os
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import psycopg2
import yaml

from OPCUA.json_merger import merge_json_files

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Sensor Data Dashboard"),

    dcc.Dropdown(
        id='sensor-dropdown',
        options=[
            {'label': 'Sensor 1', 'value': 'sensor_1'},
            {'label': 'Sensor 2', 'value': 'sensor_2'},
        ],
        value='sensor_1',
        multi=False
    ),

    dcc.Dropdown(
        id='y-axis-dropdown',
        options=[
            {'label': 'Humidity', 'value': 'Humidity'},
            {'label': 'Pressure', 'value': 'Pressure'},
            {'label': 'Acceleration X', 'value': 'AccelX'},
        ],
        value='Humidity',
        multi=False
    ),

    dcc.Graph(id='line-chart'),

    html.Div(id='table-div'),

    dcc.RangeSlider(
        id='table-pagination',
        marks={},
        min=0,
        max=0,
        step=1,
        value=[0, 10]
    )
])

config_file_path = os.path.join(os.getcwd(), "./config.yml")
with open(config_file_path, "r") as ymlfile:
    try:
        cfg = yaml.full_load(ymlfile)
    except yaml.YAMLError as exc:
        print(exc)


@app.callback(
    [Output('line-chart', 'figure'),
     Output('table-div', 'children'),
     Output('table-pagination', 'marks'),
     Output('table-pagination', 'max')],
    [Input('sensor-dropdown', 'value'),
     Input('y-axis-dropdown', 'value'),
     Input('table-pagination', 'value')]
)
def update_visualizations(selected_sensor, selected_y_axis, pagination_range):
    conn = psycopg2.connect(
        database="postgres",
        user="postgres",
        password="postgres",
        host="localhost",
        port=5432
    )

    query = f"SELECT * FROM timeseries WHERE sensor_name = '{selected_sensor}'"
    data = pd.read_sql(query, conn)

    conn.close()

    path_1 = cfg["opcua"]["timeseries1"]
    path_2 = cfg["opcua"]["timeseries2"]
    path_3 = cfg["opcua"]["timeseries3"]
    file_names = [path_1, path_2, path_3]
    merged_data = merge_json_files(file_names)

    line_chart = px.line(merged_data[0:100], x='timestamp', y=selected_y_axis,
                         title=f'{selected_sensor} {selected_y_axis.capitalize()}')

    paginated_data = data[pagination_range[0]:pagination_range[1]]
    print("columns: ", paginated_data.columns)
    table = html.Table([
        html.Tr([html.Th(col) for col in paginated_data.columns])] +
        [html.Tr([html.Td(data.iloc[i][col]) for col in paginated_data.columns])
         for i in range(len(paginated_data))]
    )

    num_rows = len(data)
    marks = {i: str(i) for i in range(0, num_rows, 10)}

    return line_chart, table, marks, num_rows


if __name__ == '__main__':
    app.run_server(debug=True)
