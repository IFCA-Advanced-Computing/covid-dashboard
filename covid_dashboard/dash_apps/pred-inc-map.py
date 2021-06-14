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


# Load incidence data
X = pd.read_csv(PATHS.covid_risk_map / 'processed' / 'provinces-incidence.csv',
                header=[0, 1])
X = X.droplevel(1, axis='columns')
X = X.set_index(['date'])
X = X[['province', 'province id', 'incidence 7']]
X['province id'] = X['province id'].apply('{:02d}'.format)

# Keep only last day (today)
max_date = X.index.max()
X = X.loc[max_date]

# Load province ids
prov_codes = pd.read_csv(PATHS.covid_risk_map / 'external' / 'provincias-ine.csv',
                         sep=';')
prov_map = dict(zip(prov_codes['provincia'],
                    prov_codes['id provincia']))

# Load predictions and add province id
pred = pd.read_csv(PATHS.covid_dl / 'predictions' / 'predictions.csv',
                   index_col=0)
pred = pred.drop('incidence 7 (std)', axis='columns')
pred = pred.rename({'incidence 7 (mean)': 'incidence 7'}, axis='columns')
pred['province id'] = pred['province'].map(prov_map)
pred['province id'] = pred['province id'].apply('{:02d}'.format)
dates = pred.index.unique()

# Load province's geojson
with open(PATHS.covid_risk_map / 'raw' / 'provincias-espana.geojson', 'r') as f:
    provinces_geo = json.load(f)

# Drop provinces not present in predictions
provinces = pred['province'].unique()
X = X[X['province'].isin(provinces)]

# Sort by province
pred = pred.sort_values('province', axis='rows')
X = X.sort_values('province', axis='rows')
X = X.reset_index(drop=True)

# Plot
marks = {i: {'label': f't+{i}'} for i in range(1, 8)}
marks.update({0: {'label': f'Hoy ({max_date})',
                  'style': {'color': '#f50'}},
              })


@click.command()
@click.option('--port', type=int)
def run(port):
    app = dash.Dash(__name__)

    app.layout = html.Div([

        dcc.Dropdown(
            id='dropdown',
            clearable=False,
            value='inc var',
            options=[{'label': 'Incidencia 7 (absoluta)', 'value': 'inc abs'},
                     {'label': 'Incidencia 7 (variación absoluta)', 'value': 'inc var'},
                     {'label': 'Incidencia 7 (variación relativa)', 'value': 'inc var rel'}
                     ],
            style={'width': '50%',
                   'margin': '0 auto',
                   },
        ),

        html.Div(
            style={'width': '50%',
                   'padding-top': '2em',
                   'padding-bottom': '2em',
                   'margin': '0 auto'},
            children=[
                dcc.Slider(id='slider',
                           min=0,
                           max=7,
                           value=7,
                           step=1,
                           marks=marks,
                           className="content",
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
        [Input('dropdown', 'value'),
         Input('slider', 'value')]
    )
    def update_figure(mode, idx):
        if idx == 0:
            tmp_X = X.copy()
        else:
            tmp_X = pred.loc[dates[idx - 1]].reset_index(drop=True)

        if mode == 'inc var':
            tmp_X['incidence 7'] = tmp_X['incidence 7'] - X['incidence 7']
        elif mode == 'inc var rel':
            tmp_X['incidence 7'] = (tmp_X['incidence 7'] - X['incidence 7']) / X['incidence 7']

        if mode == 'inc abs':
            cs = {'colorscale': 'Cividis'}
        else:
            maxscale = tmp_X['incidence 7'].abs().max()
            cs = {'colorscale': 'RdYlGn_r',
                  'zmin': -maxscale,
                  'zmax': maxscale,
                  }

        fig = go.Figure(
            go.Choroplethmapbox(
                geojson=provinces_geo,
                featureidkey='properties.province id',
                locations=tmp_X['province id'],
                z=tmp_X['incidence 7'],
                text=tmp_X['province'],
                hovertemplate='<b>%{text}</b>: %{z}<extra></extra>',
                **cs,
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
