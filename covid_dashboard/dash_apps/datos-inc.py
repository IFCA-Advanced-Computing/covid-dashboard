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

import click
import dash
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
from plotly import colors
import plotly.graph_objects as go

from covid_dashboard.paths import PATHS


# Load data
X = pd.read_csv(PATHS.covid_risk_map / 'processed' / 'provinces-incidence.csv')
X = X.set_index(['date', 'province'])
X = X[['incidence 7']]

# Plot
provinces = X.index.get_level_values('province').unique()
dates = X.index.get_level_values('date').unique()
start = pd.to_datetime(max(dates)) + pd.DateOffset(days=-30)
dend = pd.to_datetime(max(dates))

fig = go.Figure(layout={'template': 'seaborn',
                        'hovermode': 'x unified',
                        # 'title': 'Incidencia a 7 días',
                        'xaxis': {'range': [start, dend]}})
clist = colors.qualitative.Dark24
ymax = 0
for i, p in enumerate(provinces):
    a = X['incidence 7'].xs(p, level='province')
    c = colors.hex_to_rgb(clist[i % len(clist)])

    fig.add_trace(go.Scatter(name=p,
                             x=a.index,
                             y=a,
                             line={'color': f'rgb{c}'},
                             legendgroup=p,
                             )
                  )

    ymax = np.amax([a[-31:].max(), ymax])

fig.update_yaxes(range=[0, ymax])


@click.command()
@click.option('--port', type=int)
def run(port):

    app = dash.Dash(__name__)

    app.layout = html.Div([
        dcc.Graph(figure=fig,
                  style={'width': '70vw',
                         'height': '70vh',
                         'margin': '0 auto'}
                  ),
    ])

    app.run_server(debug=False, host='0.0.0.0', port=port)


if __name__ == '__main__':
    run()
