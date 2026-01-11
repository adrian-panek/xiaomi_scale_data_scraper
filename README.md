# ⚖️ Xiaomi Weight Scale Data Scraper

Main purpose of the following project is to retrieve data (via Bluetooth) from XIAOMI Mi Smart Scale 2 and store it in database for weight tracking purposes. Project comes in with handy Flask web application which allows to start/stop measurement process, view latest measurements (data can be taken from database - PostgreSQL or file). Additionally there is a live status log where user can see output from Python script responsible for taking measurement.

## ✨ Technologies

- `Python - Flask, Asyncio, Bleak, Psycopg2`
- `Docker`
- `PostgreSQL`
- `Kubernetes`
- `HTML, CSS & JS`

## 🚀 Features

- Retrieve data from scale device
- Store retrieved data in database
- Web app for easier access to measuring features
- Find weight scale by MAC address
- Stream logs from connecting to scale and measuring processes
- Deploy the application to you local Kubernetes cluster 

**NOTE: To deploy/use the app in your own environment you need a device with Bluetooth**
 
## 🚦 Running the Project

0. Clone the repository

# DB
1. Fill in the secret in `helm-charts/db/secret.yaml` file
2. Run command `kubectl apply -f ./helm-chars/db`

# Flask application
1. Fill details about yourself in `helm-charts/app/configmap.yaml` file
2. Build the docker image
3. Push your docker image into container registry (alternatively, use already built image - `adrianpanek/weight_scale_scraper:latest`)
4. Set the image in `helm-charts/app/deploy.yaml`
5. Deploy all K8s objects `kubectl apply -f helm-charts/app`


