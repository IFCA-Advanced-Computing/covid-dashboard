# Script to refresh the Dashboard

# Run this file daily as cron job
# Uncomment training when mobility is updated again

cd /home/ubuntu/covid

cd mitma-covid && git reset --hard && git pull && cd ..
cd covid-risk-map && git reset --hard && git pull && cd ..
cd covid-dl && git reset --hard && git pull && cd ..
cd covid-dashboard && git reset --hard && git pull && cd ..

# Generate a flux file from the database
#cd /home/ubuntu/covid/mitma-covid
#python3 src/data.py --update

# Generate incidence data
cd /home/ubuntu/covid/covid-risk-map
curl -k -o data/raw/casos_tecnica_provincias.csv https://cnecovid.isciii.es/covid19/resources/casos_tecnica_provincia.csv
curl -k -o data/raw/COVID19_municipalizado.csv https://serviweb.scsalud.es:10443/ficheros/COVID19_municipalizado.csv
python3 src/data/make_dataset.py data

# Make predictions
#cd /home/ubuntu/covid/covid-dl
#python3 src/train.py
#python3 src/predict.py

# Launch the Dashboard
cd /home/ubuntu/covid/covid-dashboard
lsof -t -i:8080  # kill old dashboard
nohup python3 covid_dashboard/run.py &
