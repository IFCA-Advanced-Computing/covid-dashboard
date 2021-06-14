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

import pathlib


class Paths:
    def __init__(self):
        b = pathlib.Path(__file__).resolve()
        self._base = b.parents[1]

    @property
    def base(self):
        return self._base

    @property
    def covid_dl(self):
        return self.base.parents[0] / 'covid-dl' / 'data'

    @property
    def covid_risk_map(self):
        return self.base.parents[0] / 'covid-risk-map' / 'data'


def check_dirs():
    print("Checking directories...")
    for p in dir(PATHS):
        if p.startswith('_'):
            continue
        p = getattr(PATHS, p)
        if not p.exists():
            raise Exception(f'Missing path or file: \n {p}')

PATHS = Paths()
check_dirs()
