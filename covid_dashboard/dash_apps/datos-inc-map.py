# Copyright (c) 2020 Spanish National Research Council
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json

import click
import dash
import dash_core_components as dcc
from dash.dependencies import Input, Output
import dash_html_components as html
import pandas as pd
import plotly.graph_objects as go

from covid_dashboard.paths import PATHS


# Load data
X = pd.read_csv(PATHS.covid_risk_map / 'processed' / 'provinces-incidence.csv',
                header=[0, 1])
X = X.droplevel(1, axis='columns')
X = X.set_index(['date'])
X = X[['province', 'province id', 'incidence 7']]
X['province id'] = X['province id'].apply('{:02d}'.format)

with open(PATHS.covid_risk_map / 'raw' / 'provincias-espana.geojson', 'r') as f:
    provinces_geo = json.load(f)


# Plot
@click.command()
@click.option('--port', type=int)
def run(port):
    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
    app = dash.Dash(__name__,
                    external_stylesheets=external_stylesheets)

    app.layout = html.Div([

        html.Div(
            style={'width': '60vw',
                   'padding-bottom': '1em',
                   'margin': '0 auto'},
            children=[
                dcc.DatePickerSingle(
                    id='date-picker',
                    min_date_allowed=X.index.min(),
                    max_date_allowed=X.index.max(),
                    date=X.index.max(),
                ),
            ]
        ),

        dcc.Graph(id='graph',
                  style={'width': '60vw',
                         'height': '80vh',
                         'margin': '0 auto'}
                  ),

    ])

    @app.callback(
        Output('graph', 'figure'),
        [Input('date-picker', 'date')]
    )
    def update_figure(date):
        tmp_X = X.xs(date)

        fig = go.Figure(
            go.Choroplethmapbox(
                geojson=provinces_geo,
                featureidkey='properties.province id',
                locations=tmp_X['province id'],
                z=tmp_X['incidence 7'],
                text=tmp_X['province'],
                hovertemplate='<b>%{text}</b>: %{z}<extra></extra>',
                colorscale='Cividis',
                showlegend=False,
                showscale=False,
                marker={
                    'opacity': 0.5
                },
            )
        )

        fig.update_layout(
            mapbox_style='carto-positron',
            mapbox_zoom=5,
            mapbox_center={
                'lat': 40.416763,
                'lon': -3.703564,
            },
            margin={'r': 0, 't': 0, 'l': 0, 'b': 0},
            uirevision=True,  # keep zoom levels between changes
        )

        return fig

    app.run_server(debug=False, port=port)


if __name__ == '__main__':
    run()
