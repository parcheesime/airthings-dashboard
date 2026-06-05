from pathlib import Path
import sys

import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from src.processing.read_raw_readings import get_readings_df

st.title("Airthings Dashboard")

df = get_readings_df(limit=100)

if not df.empty:
    latest = df.sort_values("recorded_at").iloc[-1]

    st.info(
        f"""
        Last sensor reading: {latest['recorded_at'].strftime('%Y-%m-%d %I:%M:%S %p')}

        Last data pull: {latest['pulled_at'].strftime('%Y-%m-%d %I:%M:%S %p')}
        """
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("VOC", f"{latest['voc']:.0f} ppb")
    col2.metric("PM2.5", f"{latest['pm25']:.1f}")
    col3.metric("Temp", f"{latest['temp_f']:.1f} °F")
    col4.metric("Humidity", f"{latest['humidity']:.0f}%")

    chart_df = df.sort_values("recorded_at").set_index("recorded_at")

    st.subheader("VOC Over Time")
    st.line_chart(chart_df["voc"])

    st.subheader("PM2.5 Over Time")
    st.line_chart(chart_df["pm25"])

    with st.expander("Raw Data"):
        st.dataframe(df)

else:
    st.warning("No sensor readings found.")