import os
import signal
import subprocess

import click

from covid_dashboard import config
from covid_dashboard.paths import PATHS


app_path = PATHS.base / 'covid_dashboard' / 'dash_apps'
CONF = config.CONF
iniport = CONF.dash_iniport

apps = os.listdir(app_path)
ports = range(iniport, iniport + len(apps))
ports_d = dict(zip(apps, ports))


def kill_process(port):
    c = subprocess.Popen(f'lsof -t -i:{port}',
                         shell=True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    stdout, stderr = c.communicate()
    for pid in stdout.decode().split('\n')[:-1]:
        os.kill(int(pid), signal.SIGTERM)


def refresh_apps(kill=False):

    # Kill old processes
    print('Killing Dash apps ...')
    for p in ports:
        kill_process(p)

    # Launch new processes
    if not kill:
        print('Launching Dash apps ...')
        for f, p in ports_d.items():
            fpath = app_path / f
            print(fpath)
            _ = subprocess.run(f'python3 {fpath} --port {p} &', shell=True, check=True)


@click.command()
@click.option('--kill', is_flag=True)
def cli(kill):
    refresh_apps(kill=kill)


if __name__ == '__main__':
    cli()
    # refresh_apps(CONF.dash_iniport, kill=False)
