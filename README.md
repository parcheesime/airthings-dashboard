# Airthings Air Quality Dashboard

A Python-powered air quality monitoring dashboard that combines **live indoor air quality measurements** from an Airthings View Plus with **nearby outdoor air quality data** from the IQAir Community API.

The project automatically collects sensor readings, stores them in MongoDB Atlas, and presents interactive visualizations through a Streamlit dashboard.

---

## Live Demo

**Dashboard:** https://airthings-air-quality.streamlit.app/

### Features

* 🌬️ Live indoor air quality monitoring from an Airthings View Plus
* 🌎 Outdoor air quality comparison using the IQAir Community API
* 📈 Interactive Plotly time-series visualizations
* ⏱️ Automated data collection with cron on a Linux server
* ☁️ MongoDB Atlas cloud database
* 🚀 Deployed with Streamlit Community Cloud

> **Note:** Indoor measurements update every minute. Outdoor air quality is collected hourly.

---

## Architecture

```text
Airthings API           IQAir Community API
        │                      │
        ▼                      ▼
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
* IQAir Community API
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
* **Outdoor air quality monitoring** using the IQAir Community API.
* **24-hour outdoor trend visualization** for comparing indoor and outdoor conditions.

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

Future enhancements include support for additional outdoor data providers (such as OpenAQ), historical reporting, alerting, and expanded dashboard analytics.