# Script to setup the dashboard in Cloud machine

# Remember to mount the volume with mitma data 
# in /data/mitma-covid. If the volume with data is not 
# available replace line 40:
# python3 src/process.py
# with:
# python3 src/data.py

# This should be done properly with Docker but right now it seems
# slightly complicated because one must use the external volume
# with mitma data BEFORE launching the dashboard. But I do not
# want to copy this volume inside the Docker during the build
# because (1. very heavy, 2. slow build, 3. volume data is not
# updated).
# If I make this volume available at runtime (-v flag) I still have to run
# several scripts before launching the dashboard so I might well
# run everything from start in a single script.


# I should do this properly with python environments

sudo apt install python3-pip
sudo apt install libopenblas-dev
echo 'alias python=python3' >> ~/.bashrc
source ~/.bashrc

rm -r /home/ubuntu/covid
mkdir /home/ubuntu/covid
cd /home/ubuntu/covid

git clone https://github.com/IFCA/mitma-covid
git clone https://github.com/IFCA/covid-risk-map
git clone https://github.com/IFCA/covid-dl
git clone https://github.com/IFCA/covid-dashboard

cd mitma-covid && pip install -r requirements.txt && cd ..
cd covid-risk-map && pip install -r requirements.txt && cd ..
cd covid-dl && pip install -r requirements.txt && cd ..
cd covid-dashboard && pip install -r requirements.txt && pip install -e . && cd ..

# Generate a flux file from the database
ln -s /data/mitma-covid/maestra1 /home/ubuntu/covid/mitma-covid/data/raw/maestra1
cd /home/ubuntu/covid/mitma-covid
python3 src/process.py

# Generate incidence data
ln -s /home/ubuntu/covid/mitma-covid/data/processed/province_flux.csv /home/ubuntu/covid/covid-risk-map/data/raw/province_flux.csv
cd /home/ubuntu/covid/covid-risk-map
curl -k -o data/raw/casos_tecnica_provincias.csv https://cnecovid.isciii.es/covid19/resources/casos_tecnica_provincia.csv
curl -k -o data/raw/COVID19_municipalizado.csv https://serviweb.scsalud.es:10443/ficheros/COVID19_municipalizado.csv
python3 src/data/make_dataset.py data

# Make predictions
ln -s /home/ubuntu/covid/covid-risk-map/data/processed/provinces-incidence-mobility.csv /home/ubuntu/covid/covid-dl/data/raw/provinces-incidence-mobility.csv
cd /home/ubuntu/covid/covid-dl
python3 src/train.py
python3 src/predict.py

# Launch the Dashboard
cd /home/ubuntu/covid/covid-dashboard
python3 covid_dashboard/run.py

