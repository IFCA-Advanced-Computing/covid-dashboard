# Copyright 2019 Spanish National Research Council (CSIC)
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import json
import os

from aiohttp import web
import aiohttp_jinja2

from covid_dashboard.paths import PATHS


app_path = PATHS.base / 'covid_dashboard' / 'dash_apps'
dash_ports = {f: 7000 + i for i, f in enumerate(os.listdir(app_path))}

routes = web.RouteTableDef()

@routes.get('/', name='home')
async def home(request):
    # Redirect to predictions
    return web.HTTPFound('/predictions')


#todo: remove when dashboard is ready for the public
@routes.get('/robots.txt')
async def robots(request):
    # Ideally should be served by nginx or cdn
    return web.FileResponse('static/robots.txt')


@routes.get('/about', name='about')
@aiohttp_jinja2.template('about.html')
async def about(request):
    return None


@routes.get('/mobility', name='mobility')
@aiohttp_jinja2.template('mobility.html')
async def mobility(request):
    return None


@routes.get('/incidence', name='incidence')
@aiohttp_jinja2.template('incidence.html')
async def incidence(request):
    request.context['ports'] = dash_ports
    return request.context


@routes.get('/predictions', name='predictions')
@aiohttp_jinja2.template('predictions.html')
async def predictions(request):
    request.context['ports'] = dash_ports
    return request.context
