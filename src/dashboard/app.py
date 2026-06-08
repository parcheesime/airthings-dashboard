from pathlib import Path
import sys

import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from src.processing.read_raw_readings import get_readings_df


st.set_page_config(
    page_title="Airthings Dashboard",
    page_icon="🌬️",
    layout="wide",
)

st.title("🌬️ Airthings Air Quality Dashboard")
st.caption("Live indoor air quality monitoring")

df = get_readings_df(limit=100)

if not df.empty:
    df = df.sort_values("recorded_at_local")

    latest = df.iloc[-1]

    st.info(
        f"""
        Last sensor reading: {latest['recorded_at_local'].strftime('%Y-%m-%d %I:%M:%S %p')}

        Last data pull: {latest['pulled_at_local'].strftime('%Y-%m-%d %I:%M:%S %p')}
        """
    )

    col1, col2, col3, col4, col5 = st.columns(5)

    voc = latest["voc"]
    pm1 = latest["pm1"]
    pm25 = latest["pm25"]

    if voc < 250:
        voc_status = "🟢 Good"
    elif voc < 500:
        voc_status = "🟡 Fair"
    else:
        voc_status = "🔴 Poor"

    if pm1 < 5:
        pm1_status = "🟢 Good"
    elif pm1 < 15:
        pm1_status = "🟡 Fair"
    else:
        pm1_status = "🔴 Poor"

    if pm25 < 12:
        pm25_status = "🟢 Good"
    elif pm25 < 35:
        pm25_status = "🟡 Fair"
    else:
        pm25_status = "🔴 Poor"

    col1.metric("VOC", f"{voc:.0f} ppb")
    col1.caption(voc_status)

    col2.metric("PM2.5", f"{pm25:.1f} µg/m³")
    col2.caption(pm25_status)

    col3.metric("PM1", f"{pm1:.1f} µg/m³")
    col3.caption(pm1_status)
    
    col4.metric("Temp", f"{latest['temp_f']:.1f} °F")
    col5.metric("Humidity", f"{latest['humidity']:.0f}%")

    chart_df = df.copy()

    chart_df["local_time"] = chart_df["recorded_at_local"].dt.strftime(
        "%Y-%m-%d %I:%M:%S %p"
    )

    chart_df["utc_time"] = chart_df["recorded_at"].dt.strftime(
        "%Y-%m-%d %H:%M:%S UTC"
    )

    st.subheader("VOC Over Time")

    voc_fig = px.line(
        chart_df,
        x="recorded_at_local",
        y="voc",
        markers=True,
        labels={
            "recorded_at_local": "Local Time",
            "voc": "VOC (ppb)",
        },
    )

    voc_fig.update_traces(
        hovertemplate=(
            "<b>Local Time</b>: %{customdata[0]}<br>"
            "<b>UTC Time</b>: %{customdata[1]}<br>"
            "<b>VOC</b>: %{y:.0f} ppb"
            "<extra></extra>"
        ),
        customdata=chart_df[["local_time", "utc_time"]],
    )

    st.plotly_chart(voc_fig, use_container_width=True)

    st.subheader("PM2.5 Over Time")

    pm25_fig = px.line(
        chart_df,
        x="recorded_at_local",
        y="pm25",
        markers=True,
        labels={
            "recorded_at_local": "Local Time",
            "pm25": "PM2.5 (µg/m³)",
        },
    )

    pm25_fig.update_traces(
        hovertemplate=(
            "<b>Local Time</b>: %{customdata[0]}<br>"
            # "<b>UTC Time</b>: %{customdata[1]}<br>"
            "<b>PM2.5</b>: %{y:.1f} µg/m³"
            "<extra></extra>"
        ),
        customdata=chart_df[["local_time", "utc_time"]],
    )

    st.plotly_chart(pm25_fig, use_container_width=True)

    with st.expander("Raw Data"):
        st.dataframe(df)

else:
    st.warning("No sensor readings found.")