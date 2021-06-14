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

import pathlib

from oslo_config import cfg
from oslo_log import log

from covid_dashboard import version


opts = [
    cfg.StrOpt(
        "runtime-dir",
        default=pathlib.Path(__file__).parents[1].as_posix(),
        help="""
Define the COVID dashboard base runtime directory
"""),
    cfg.StrOpt(
        "static-path",
        default=(pathlib.Path(__file__).parent / "static").as_posix(),
        help="""
Path where the static files are stored.
"""),
]

cache_opts = [
    cfg.StrOpt(
        "memcached-ip",
        help="""
IP of the memcached server to use.

If not set, we will not use memcached at all, therefore the COVID dashboard
will not behave as expected when using several workers.
"""),
    cfg.PortOpt(
        "memcached-port",
        default=11211,
        help="""
Port of the memcached server to use.
"""),
]

cli_opts = [
    cfg.StrOpt('listen-ip',
               help="""
IP address on which the COVID Dashboard will listen.

The COVID dashboard service will listen on this IP address.
"""),
    cfg.PortOpt('listen-port',
                help="""
Port on which the COVID Dashboard will listen.

The COVID dashboard service will listen on this port.
"""),
    cfg.StrOpt('listen-path',
               help="""
Path to the UNIX socket where the COVID dashboard will listen.
"""),
    cfg.PortOpt('dash-iniport',
                default=7000,
                help="""
Port on which the dash apps will listen. If iniport is 7000,
and the are 5 dash apps, the port range 7000-7005 will be used.
"""),
]

CONF = cfg.CONF
CONF.register_cli_opts(cli_opts)
CONF.register_opts(opts)
CONF.register_opts(cache_opts, group="cache")


def parse_args(args, default_config_files=None):
    cfg.CONF(args,
             project='covid_dashboard',
             version=version.__version__,
             default_config_files=default_config_files)


def prepare_logging():
    log.register_options(CONF)
    log.set_defaults(default_log_levels=log.get_default_log_levels())


def configure(argv, default_config_files=None):
    prepare_logging()
    parse_args(argv, default_config_files=default_config_files)
    log.setup(CONF, "covid_dashboard")
