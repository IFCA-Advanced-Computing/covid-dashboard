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
X = pd.read_csv(
    PATHS.covid_risk_map / 'processed' / 'provinces-incidence-mobility.csv',
    header=[0, 1]
)
X = X.droplevel(1, axis='columns')
X = X.set_index(['date', 'province'])
X = X[['incidence 7']]

pred = pd.read_csv(PATHS.covid_dl / 'predictions' / 'predictions.csv',
                   index_col=[0, 1])

# Plot
provinces = pred.index.get_level_values('province').unique()
dates = X.index.get_level_values('date').unique()
start = pd.to_datetime(max(dates)) + pd.DateOffset(days=-30)
dend = pd.to_datetime(max(dates)) + pd.DateOffset(days=8)

fig = go.Figure(layout={'title': 'Incidencia a 7 días (con intervalos de 95% de confianza)',
                        'template': 'seaborn',
                        'hovermode': 'x unified',
                        'xaxis': {'range': [start, dend]}})
clist = colors.qualitative.Dark24
ymax = 0
for i, p in enumerate(provinces):
    a = X['incidence 7'].xs(p, level='province')
    b = pred.xs(p, level='province')
    c = colors.hex_to_rgb(clist[i % len(clist)])

    fig.add_trace(go.Scatter(name=p,
                             x=a.index,
                             y=a,
                             line={'color': f'rgb{c}'},
                             legendgroup=p,
                             )
                  )

    mean, std = b['incidence 7 (mean)'], b['incidence 7 (std)']
    drange = a.index[-1:].append(b.index)  # append last true value to predictions for nicer plot

    ub = a[-1:].append(mean + 2 * std)
    lb = a[-1:].append(mean - 2 * std)
    lb = lb.clip(0)  # clip negative values
    mv = a[-1:].append(mean)
    info = [f'{p}: <b>{mv[i]}</b> [{lb[i]} | {ub[i]}]' for i in range(len(mv))]

    fig.add_trace(go.Scatter(name='upper bound',
                             x=drange,
                             y=ub,
                             mode='lines',
                             line={'width': 0},
                             legendgroup=p,
                             showlegend=False,
                             hoverinfo='skip'
                             )
                  )

    fig.add_trace(go.Scatter(name='lower bound',
                             x=drange,
                             y=lb,
                             line={'width': 0},
                             mode='lines',
                             fillcolor=f'rgba{c + (0.4,)}',
                             fill='tonexty',
                             legendgroup=p,
                             showlegend=False,
                             hoverinfo='skip'
                             )
                  )

    fig.add_trace(go.Scatter(name=p,
                             x=drange,
                             y=mv,
                             line={'color': f'rgb{c}',
                                   'dash': 'dash'},
                             legendgroup=p,
                             showlegend=False,
                             hoverinfo='x+text',
                             hovertext=info,
                             )
                  )

    ymax = np.amax([a[-31:].max(), ub.max(), ymax])

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
