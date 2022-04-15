"""Instantiate a Dash app."""
import dash

import dash_core_components as dcc
import dash_html_components as html
import dash_table
import base64
import plotly.graph_objs as go


from .data import create_dataframe
from .layout import html_layout
from dash.dependencies import Input, Output, State


def init_dashboard(server):
    """Create a Plotly Dash dashboard."""
    dash_app = dash.Dash(
        server=server,
        routes_pathname_prefix="/dashapp/",
        external_stylesheets=[
            "/static/dist/css/styles.css",
            "https://fonts.googleapis.com/css?family=Lato",
            "https://codepen.io/chriddyp/pen/bWLwgP.css"
        ],
    )
    # Custom HTML layout
    dash_app.index_string = html_layout

    # Create Layout
    dash_app.layout = html.Div([
        dcc.Upload(
            id='upload-data',
            children=html.Div([
                'Drag and Drop or ',
                html.A('Select CSV File')
            ]),
            style={
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px'
            },
            # Allow multiple files to be uploaded
            multiple=False
        ),
        html.Div(id='output-data-upload'),
    ])


    def to_bytes(s):
        if type(s) is bytes:
            return s
        elif type(s) is str or (sys.version_info[0] < 3 and type(s) is unicode):
            return codecs.encode(s, 'utf-8')
        else:
            raise TypeError("Expected bytes or string, but got %s." % type(s))

    @dash_app.callback(Output('output-data-upload', 'children'),
                              Input('upload-data', 'contents'),
                              State('upload-data', 'filename'),
                              State('upload-data', 'last_modified'))
    def update_output(list_of_contents, var2, var3):
        if list_of_contents is not None:
            content_type, content_string = list_of_contents.split(',')
            file = base64.b64decode(content_string)
            file_name = "data/input.csv"
            with open(file_name, 'wb') as f:
                f.write(to_bytes(file))

            return render_results(dash_app)

    return dash_app.server

def render_results(dash_app):
    df_detailed, df_total = create_dataframe('input.csv')

    # Custom HTML layout
    dash_app.index_string = html_layout


    linear = dcc.Graph(
        figure={
            'data': [
                {'x': df_total['party_name'], 'y': df_total['votes'], 'type': 'bar'},
            ],
            'layout': {
                'title': 'Total results'
            }
        }
    )

    # Create Layout
    res = html.Div(
        children=[
            linear,
            create_data_table(df_detailed),
        ],
        id="dash-container",
    )
    return res




def create_data_table(df):
    """Create Dash datatable from Pandas DataFrame."""
    table = dash_table.DataTable(
        id="database-table",
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict("records"),
        sort_action="native",
        sort_mode="native",
        page_size=10,
    )
    return table


