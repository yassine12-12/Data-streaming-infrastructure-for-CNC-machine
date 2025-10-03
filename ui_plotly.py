import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import psycopg2

from io import BytesIO
from PIL import Image
import base64

from func_database import create_db_manager

db_params = {
    'database': "postgres",
    'user': "postgres",
    'password': "postgres",
    'host': "localhost",
    'port': 5432
}

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Sensor Data Dashboard"),

    dcc.Dropdown(
        id='sensor-dropdown',
        options=[
            {'label': 'Sensor 1', 'value': 'sensor_1'},
            {'label': 'Sensor 2', 'value': 'sensor_2'},
            {'label': 'Sensor 3', 'value': 'sensor_3'},
        ],
        value='sensor_1',
        multi=False,
        style={'marginBottom': '8px'}
    ),

    dcc.Dropdown(
        id='property-dropdown',
        options=[
            {'label': 'Humidity', 'value': 'humidity'},
            {'label': 'Pressure', 'value': 'pressure'},
            {'label': 'Acceleration X', 'value': 'acceleration_x'},
            {'label': 'Acceleration Y', 'value': 'acceleration_y'},
            {'label': 'Acceleration Z', 'value': 'acceleration_z'},
            {'label': 'Gyro X', 'value': 'gyro_x'},
            {'label': 'Gyro Y', 'value': 'gyro_y'},
            {'label': 'Gyro Z', 'value': 'gyro_z'},
            {'label': 'Temperature', 'value': 'temperature'},
            {'label': 'Noise', 'value': 'noise'},
            {'label': 'Light', 'value': 'light'},
        ],
        value='humidity',
        multi=False
    ),

    dcc.Graph(id='line-chart'),

    html.H1(
        "Images",
        style={'marginY': '8px'}
    ),

    dcc.Loading(
        id="loading-images",
        children=[
            html.Div(id='image-grid', style={
                'display': 'grid',
                'gridTemplateColumns': 'repeat(4, 1fr)',
                'gap': '10px',
            })
        ],
        type='circle'
    )
])


@app.callback(
    Output('line-chart', 'figure'),
    [Input('sensor-dropdown', 'value'),
     Input('property-dropdown', 'value')]
)
def update_visualizations(selected_sensor, selected_y_axis):

    try:
        db = create_db_manager()

        data = db.select_x_recent_data('timeseries', 0, 1000)

        data = pd.DataFrame(data)

        line_chart = px.line(data, x='timestamp', y=selected_y_axis,
                             title=f'{selected_sensor} {selected_y_axis.capitalize()}')

        return line_chart

    except Exception as e:
        print("Error:", e)
    finally:
        db.close()

# Create a function to fetch and display images from the database


def display_images():
    try:
        db = create_db_manager()

        image_records = db.select_x_recent_data('images', 'file_data', 25)

        db.close()

        # Create a list to store image components
        image_components = []

        # Loop through the retrieved image data
        for image_data in image_records:
            # Create a BytesIO stream from the image data
            image_stream = BytesIO(image_data['file_data'])

            # Open the image using Pillow (PIL)
            tiff_img = Image.open(image_stream)

            # Convert the TIFF image to PNG format
            png_img_stream = BytesIO()
            tiff_img.save(png_img_stream, format="PNG")
            png_img_stream.seek(0)

            # Convert the image to base64 for display
            img_base64 = base64.b64encode(
                png_img_stream.getvalue()).decode('utf-8')

            # Create an image component and add it to the list
            img_component = html.Div(
                html.Img(
                    src=f"data:image/png;base64, {img_base64}",
                    style={
                        'objectFit': 'cover',
                        'width': '100%',
                        'height': '100%'
                    }
                ),

            )
            image_components.append(img_component)

        return image_components
    except Exception as e:
        print("Error:", e)


# Create a callback to update the image grid
@app.callback(
    Output('image-grid', 'children'),
    Input('loading-images', 'loading_state')
)
def update_image_grid(loading_state):
    if not loading_state:
        return display_images()
    else:
        return []


if __name__ == '__main__':
    app.run_server(debug=True)
