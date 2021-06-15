# Script to refresh the Dashboard

# Run this file daily as cron job

cd /home/ubuntu/covid

cd mitma-covid && git pull && cd ..
cd covid-risk-map && git pull && cd ..
cd covid-dl && git pull && cd ..
cd covid-dashboard && git pull && pip install -e . && cd ..

# Generate a flux file from the database
cd /home/ubuntu/covid/mitma-covid
python3 src/data.py --update

# Generate incidence data
cd /home/ubuntu/covid/covid-risk-map
curl -k -o data/raw/casos_tecnica_provincias.csv https://cnecovid.isciii.es/covid19/resources/casos_tecnica_provincia.csv
curl -k -o data/raw/COVID19_municipalizado.csv https://serviweb.scsalud.es:10443/ficheros/COVID19_municipalizado.csv
python3 src/data/make_dataset.py data

# Make predictions
cd /home/ubuntu/covid/covid-dl
python3 src/train.py
python3 src/predict.py

# Launch the Dashboard
cd /home/ubuntu/covid/covid-dashboard
python3 covid_dashboard/run.py
