from pathlib import Path
import sys

import pandas as pd
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

    # --- Current values ---
    voc = latest["voc"]
    pm1 = latest["pm1"]
    pm25 = latest["pm25"]

    # --- Status helpers ---
    def get_pm_status(value):
        if value < 5:
            return "🟢 Excellent"
        elif value < 12:
            return "🟢 Good"
        elif value < 35:
            return "🟡 Moderate"
        elif value < 55:
            return "🟠 Unhealthy"
        return "🔴 Hazardous"

    def get_voc_status(value):
        if value < 250:
            return "🟢 Good"
        elif value < 500:
            return "🟡 Fair"
        return "🔴 Poor"

    voc_status = get_voc_status(voc)
    pm1_status = get_pm_status(pm1)
    pm25_status = get_pm_status(pm25)

    # --- Last 30 minute summary ---
    latest_time = latest["recorded_at_local"]
    last_30 = df[df["recorded_at_local"] >= latest_time - pd.Timedelta(minutes=30)]

    avg_voc = last_30["voc"].mean()
    max_voc = last_30["voc"].max()
    avg_pm25 = last_30["pm25"].mean()
    max_pm25 = last_30["pm25"].max()

    overall_status = "🟢 Good"
    if max_pm25 >= 35 or max_voc >= 500:
        overall_status = "🔴 Poor"
    elif max_pm25 >= 12 or max_voc >= 250:
        overall_status = "🟡 Watch"

    # --- Time labels for charts ---
    chart_df = df.copy()
    chart_df["local_time"] = chart_df["recorded_at_local"].dt.strftime(
        "%Y-%m-%d %I:%M:%S %p"
    )
    chart_df["utc_time"] = chart_df["recorded_at"].dt.strftime(
        "%Y-%m-%d %H:%M:%S UTC"
    )

    # --- Main layout ---
    left_col, right_col = st.columns([1, 2.4], gap="large")

    with left_col:
        st.subheader("30 Minute Summary")

        st.markdown(
            f"""
            ### {overall_status}

            **VOC average:** {avg_voc:.0f} ppb  
            **VOC peak:** {max_voc:.0f} ppb  

            **PM2.5 average:** {avg_pm25:.1f} µg/m³  
            **PM2.5 peak:** {max_pm25:.1f} µg/m³  

            **Last sensor reading:**  
            {latest['recorded_at_local'].strftime('%Y-%m-%d %I:%M:%S %p')}

            **Last data pull:**  
            {latest['pulled_at_local'].strftime('%Y-%m-%d %I:%M:%S %p')}
            """
        )

        st.divider()

        st.subheader("Current Status")

        st.metric("VOC", f"{voc:.0f} ppb")
        st.caption(voc_status)

        st.metric("PM2.5", f"{pm25:.1f} µg/m³")
        st.caption(pm25_status)

        st.metric("PM1", f"{pm1:.1f} µg/m³")
        st.caption(pm1_status)

        st.metric("Temp", f"{latest['temp_f']:.1f} °F")
        st.metric("Humidity", f"{latest['humidity']:.0f}%")

    with right_col:
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

        voc_fig.update_layout(height=330)
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
                "<b>PM2.5</b>: %{y:.1f} µg/m³"
                "<extra></extra>"
            ),
            customdata=chart_df[["local_time", "utc_time"]],
        )

        pm25_fig.update_layout(height=330)
        st.plotly_chart(pm25_fig, use_container_width=True)

    with st.expander("Raw Data"):
        st.dataframe(df)

else:
    st.warning("No sensor readings found.")