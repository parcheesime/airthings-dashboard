# Airthings Air Quality Dashboard

A Python-powered air quality monitoring dashboard that combines **live indoor air quality measurements** from an Airthings View Plus with **nearby outdoor PM2.5 data** from the PurpleAir SDSU Athletics sensor.

The project automatically collects sensor readings, stores them in MongoDB Atlas, and presents interactive visualizations through a Streamlit dashboard.

---

## Live Demo

**Dashboard:** https://airthings-air-quality.streamlit.app/

### Features

* 🌬️ Live indoor air quality monitoring
* 🌎 Outdoor PM2.5 comparison using the PurpleAir SDSU Athletics sensor
* 📈 Interactive Plotly time-series visualizations
* ⏱️ Automated data collection with cron on a Linux server
* ☁️ MongoDB Atlas cloud database
* 🚀 Deployed with Streamlit Community Cloud

> **Note:** The dashboard updates automatically as new sensor readings are collected.

---

## Architecture

```text
Airthings API          PurpleAir API
        │                    │
        ▼                    ▼
      Ubuntu Server (bitbunny)
          Scheduled ingestion
                  │
                  ▼
            MongoDB Atlas
                  │
                  ▼
     Streamlit Community Cloud
```

---

## Technology Stack

* Python
* Streamlit
* Plotly
* MongoDB Atlas
* PyMongo
* Pandas
* Airthings API
* PurpleAir API
* Ubuntu Server
* Cron
* GitHub
* Streamlit Community Cloud

---

## Dashboard Overview

The dashboard includes:

* **Current Indoor Conditions** with live VOC, PM2.5, PM1, temperature, and humidity.
* **30 Minute Summary** highlighting recent indoor averages and peaks.
* **Indoor VOC and PM2.5 trends** with interactive Plotly charts.
* **Outdoor PM2.5 monitoring** from the PurpleAir SDSU Athletics station.
* **24-hour outdoor trend visualization** for comparing indoor and outdoor air quality.

---

## Project Goals

This project began as a way to continuously monitor indoor air quality while comparing it with nearby outdoor conditions. It has since grown into an end-to-end data engineering project demonstrating:

* Automated data ingestion
* API integration
* Cloud database management
* Interactive dashboard development
* Linux server automation
* Cloud deployment
* Data visualization

Future enhancements include additional outdoor metrics, historical reporting, alerting, and expanded dashboard analytics.
