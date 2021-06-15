import os
import signal
import subprocess

from covid_dashboard import config
from covid_dashboard.paths import PATHS


app_path = PATHS.base / 'covid_dashboard' / 'dash_apps'
CONF = config.CONF


def kill_process(port):
    c = subprocess.Popen(f'lsof -t -i:{port}',
                         shell=True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    stdout, stderr = c.communicate()
    for pid in stdout.decode().split('\n')[:-1]:
        os.kill(int(pid), signal.SIGTERM)


def refresh_apps(iniport=7000):
    print('Refreshing Dash apps ...')
    apps = os.listdir(app_path)
    ports = range(iniport, iniport + len(apps))

    # Kill old processes
    for p in ports:
        kill_process(p)

    # Launch new processes
    for f, p in zip(apps, ports):
        fpath = app_path / f
        print(fpath)
        _ = subprocess.run(f'python {fpath} --port {p} &', shell=True, check=True)


if __name__ == '__main__':
    refresh_apps(CONF.dash_iniport)
    # kill_process(8070)
