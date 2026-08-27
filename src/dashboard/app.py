from pathlib import Path
from html import escape
import sys

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from src.processing.read_raw_readings import get_readings_df
from src.processing.read_outdoor_readings import get_outdoor_readings_df


st.set_page_config(
    page_title="Airthings Dashboard",
    page_icon="🌬️",
    layout="wide",
)

st.markdown(
    """
    <style>
      .current-panel {
        padding: 1.25rem 1.5rem 1.35rem;
      }

      .current-title {
        text-align: center;
        font-size: 1.45rem;
        font-weight: 700;
        margin-bottom: 1.35rem;
      }

      .current-grid {
        display: grid;
        grid-template-columns: repeat(5, minmax(0, 1fr));
        gap: 1rem;
        align-items: center;
      }

      .current-metric {
        text-align: center;
        white-space: nowrap;
      }

      .metric-label {
        font-weight: 700;
        font-size: 0.95rem;
        margin-bottom: 0.35rem;
      }

      .metric-value {
        font-size: 1rem;
        color: rgba(255, 255, 255, 0.75);
      }

      .metric-value strong {
        color: white;
        font-size: 1.08rem;
        font-weight: 800;
      }

      .metric-value span {
        color: rgba(255, 255, 255, 0.55);
      }

      .summary-card {
        padding: 1.25rem 0 1.5rem;
      }

      .summary-card h3 {
        font-size: 1.45rem;
        font-weight: 700;
        margin: 0 0 1.4rem;
      }

      .summary-section {
        margin-top: 1.35rem;
      }

      .summary-section:first-of-type {
        margin-top: 0;
      }

      .summary-label {
        font-weight: 700;
        margin-bottom: 0.45rem;
      }

      .summary-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 1rem;
      }

      .summary-subtle {
        color: rgba(255, 255, 255, 0.72);
        margin-bottom: 0.2rem;
      }

      .summary-value {
        font-weight: 700;
      }

      .summary-final {
        padding-bottom: 0.35rem;
      }

      .indoor-summary-card {
        min-height: 850px;
        display: flex;
        flex-direction: column;
      }

      .indoor-summary-card .summary-section {
        margin-top: 3rem;
      }

      .indoor-summary-card .summary-section:first-of-type {
        margin-top: 0;
      }

      .indoor-summary-card .summary-final {
        margin-top: auto;
      }

      .outdoor-attribution {
        color: rgba(255, 255, 255, 0.48);
        font-size: 0.88rem;
        margin-top: -0.25rem;
      }

      @media (max-width: 900px) {
        .current-grid {
          grid-template-columns: repeat(2, minmax(0, 1fr));
        }
      }
    </style>
    """,
    unsafe_allow_html=True,
)


def format_summary_time(timestamp):
    local_timestamp = pd.Timestamp(timestamp)
    today = pd.Timestamp.now(tz=local_timestamp.tz).date()

    if local_timestamp.date() == today:
        return local_timestamp.strftime("%-I:%M %p")

    return local_timestamp.strftime("%b %-d • %-I:%M %p")


def format_outdoor_value(value, suffix="", decimals=0):
    numeric_value = pd.to_numeric(value, errors="coerce")
    if pd.isna(numeric_value):
        return "Unavailable"

    return f"{numeric_value:.{decimals}f}{suffix}"


def get_aqi_status(aqi):
    numeric_aqi = pd.to_numeric(aqi, errors="coerce")
    if pd.isna(numeric_aqi):
        return "Unavailable"
    if numeric_aqi <= 50:
        return "🟢 Good"
    if numeric_aqi <= 100:
        return "🟡 Moderate"
    if numeric_aqi <= 150:
        return "🟠 Unhealthy for Sensitive Groups"
    if numeric_aqi <= 200:
        return "🔴 Unhealthy"
    if numeric_aqi <= 300:
        return "🟣 Very Unhealthy"
    return "🟤 Hazardous"


def format_pollutant(code):
    if pd.isna(code) or not str(code).strip():
        return "Unavailable"

    pollutant_names = {
        "p2": "PM2.5",
        "p1": "PM10",
        "o3": "Ozone",
        "n2": "Nitrogen Dioxide",
        "s2": "Sulfur Dioxide",
        "co": "Carbon Monoxide",
    }
    normalized_code = str(code).strip().lower()
    return escape(pollutant_names.get(normalized_code, str(code)))


st.title("🌬️ Airthings Air Quality Dashboard")
st.caption("Indoor and outdoor air quality monitoring • College Area, San Diego")

st.info(
    "Data collection is temporarily paused during power outages/server maintenance. "
    "Historical air quality data remains available below."
)

df = get_readings_df(limit=100)
outdoor_df = get_outdoor_readings_df(limit=500)

if not df.empty:
    df = df.sort_values("recorded_at_local")
    latest = df.iloc[-1]

    # --- Current values ---
    voc = latest["voc"]
    pm1 = latest["pm1"]
    pm25 = latest["pm25"]

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

    # --- Current conditions ---
    with st.container(border=True):
        st.markdown(
            f"""
            <div class="current-panel">
              <div class="current-title">Current Indoor Conditions <span>{overall_status}</span></div>
              <div class="current-grid">
                <div class="current-metric">
                  <div class="metric-label">🌬 VOC</div>
                  <div class="metric-value"><strong>{voc:.0f}</strong> <span>ppb</span></div>
                </div>
                <div class="current-metric">
                  <div class="metric-label">✨ PM2.5</div>
                  <div class="metric-value"><strong>{pm25:.1f}</strong> <span>µg/m³</span></div>
                </div>
                <div class="current-metric">
                  <div class="metric-label">✨ PM1</div>
                  <div class="metric-value"><strong>{pm1:.1f}</strong> <span>µg/m³</span></div>
                </div>
                <div class="current-metric">
                  <div class="metric-label">🌡 Temp</div>
                  <div class="metric-value"><strong>{latest['temp_f']:.1f}</strong> <span>°F</span></div>
                </div>
                <div class="current-metric">
                  <div class="metric-label">💧 Humidity</div>
                  <div class="metric-value"><strong>{latest['humidity']:.0f}</strong> <span>%</span></div>
                </div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # --- Indoor layout ---
    left_col, right_col = st.columns([1, 2.4], gap="large")

    with left_col:
        with st.container(height=850, border=True):
            st.markdown(
                f"""
                <div class="summary-card indoor-summary-card">
                  <h3>30 Minute Summary</h3>
                  <div class="summary-section">
                    <div class="summary-label">Status</div>
                    <div class="summary-value">{overall_status}</div>
                  </div>
                  <div class="summary-section">
                    <div class="summary-label">VOC</div>
                    <div class="summary-grid">
                      <div>
                        <div class="summary-subtle">Average</div>
                        <div class="summary-value">{avg_voc:.0f} ppb</div>
                      </div>
                      <div>
                        <div class="summary-subtle">Peak</div>
                        <div class="summary-value">{max_voc:.0f} ppb</div>
                      </div>
                    </div>
                  </div>
                  <div class="summary-section">
                    <div class="summary-label">PM2.5</div>
                    <div class="summary-grid">
                      <div>
                        <div class="summary-subtle">Average</div>
                        <div class="summary-value">{avg_pm25:.1f} µg/m³</div>
                      </div>
                      <div>
                        <div class="summary-subtle">Peak</div>
                        <div class="summary-value">{max_pm25:.1f} µg/m³</div>
                      </div>
                    </div>
                  </div>
                  <div class="summary-section summary-final">
                    <div class="summary-label">Last Updated</div>
                    <div class="summary-value">{format_summary_time(latest["recorded_at_local"])}</div>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

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
            mode="lines",
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
            mode="lines",
            hovertemplate=(
                "<b>Local Time</b>: %{customdata[0]}<br>"
                "<b>PM2.5</b>: %{y:.1f} µg/m³"
                "<extra></extra>"
            ),
            customdata=chart_df[["local_time", "utc_time"]],
        )

        pm25_fig.update_layout(height=330)
        st.plotly_chart(pm25_fig, use_container_width=True)

    st.divider()

    outdoor_summary_col, outdoor_chart_col = st.columns([1, 2.4], gap="large")

    if "provider" in outdoor_df.columns:
        outdoor_df = outdoor_df[
            outdoor_df["provider"].astype("string").str.lower() == "iqair"
        ].copy()
    else:
        outdoor_df = outdoor_df.iloc[0:0].copy()

    if not outdoor_df.empty:
        if "aqi_us" not in outdoor_df.columns:
            outdoor_df["aqi_us"] = float("nan")
        else:
            outdoor_df["aqi_us"] = pd.to_numeric(
                outdoor_df["aqi_us"], errors="coerce"
            )

        outdoor_df = outdoor_df.sort_values("recorded_at_local")
        latest_outdoor = outdoor_df.iloc[-1]
        latest_outdoor_time = latest_outdoor["recorded_at_local"]

        outdoor_chart_df = outdoor_df[
            outdoor_df["recorded_at_local"]
            >= latest_outdoor_time - pd.Timedelta(hours=24)
        ].copy()
        outdoor_chart_df["local_time"] = outdoor_chart_df[
            "recorded_at_local"
        ].dt.strftime("%Y-%m-%d %I:%M:%S %p")
        outdoor_chart_df["utc_time"] = outdoor_chart_df["recorded_at"].dt.strftime(
            "%Y-%m-%d %H:%M:%S UTC"
        )

        location_name = latest_outdoor.get("location_name")
        state = latest_outdoor.get("state")
        if pd.isna(location_name) or pd.isna(state):
            reporting_area = "Unavailable"
        else:
            reporting_area = f"{escape(str(location_name))}, {escape(str(state))}"

        current_aqi = latest_outdoor.get("aqi_us")
        aqi_display = format_outdoor_value(current_aqi)
        aqi_status = get_aqi_status(current_aqi)
        pollutant = format_pollutant(latest_outdoor.get("main_pollutant"))

        temperature_c = pd.to_numeric(
            latest_outdoor.get("temperature_c"), errors="coerce"
        )
        temperature = "Unavailable"
        if pd.notna(temperature_c):
            temperature = format_outdoor_value(
                temperature_c * 9 / 5 + 32, suffix="°F"
            )

        humidity = format_outdoor_value(
            latest_outdoor.get("humidity"), suffix="%"
        )

        with outdoor_summary_col:
            with st.container(border=True):
                st.markdown(
                    f"""
                    <div class="summary-card">
                      <h3>Local Outdoor Summary</h3>
                      <div class="summary-section">
                        <div class="summary-label">Reporting Area</div>
                        <div class="summary-value">{reporting_area}</div>
                      </div>
                      <div class="summary-section">
                        <div class="summary-label">Current AQI</div>
                        <div class="summary-grid">
                          <div>
                            <div class="summary-subtle">US AQI</div>
                            <div class="summary-value">{aqi_display}</div>
                          </div>
                          <div>
                            <div class="summary-subtle">Status</div>
                            <div class="summary-value">{aqi_status}</div>
                          </div>
                        </div>
                      </div>
                      <div class="summary-section">
                        <div class="summary-label">Main Pollutant</div>
                        <div class="summary-value">{pollutant}</div>
                      </div>
                      <div class="summary-section">
                        <div class="summary-label">Temperature</div>
                        <div class="summary-value">{temperature}</div>
                      </div>
                      <div class="summary-section">
                        <div class="summary-label">Humidity</div>
                        <div class="summary-value">{humidity}</div>
                      </div>
                      <div class="summary-section summary-final">
                        <div class="summary-label">Last Updated</div>
                        <div class="summary-value">{format_summary_time(latest_outdoor["recorded_at_local"])}</div>
                      </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        with outdoor_chart_col:
            st.subheader("Local Outdoor AQI (Last 24 Hours)")

            outdoor_aqi_fig = px.line(
                outdoor_chart_df,
                x="recorded_at_local",
                y="aqi_us",
                markers=True,
                labels={
                    "recorded_at_local": "Local Time",
                    "aqi_us": "US AQI",
                },
            )

            outdoor_aqi_fig.update_traces(
                mode="lines+markers",
                marker=dict(size=5),
                hovertemplate=(
                    "<b>Local Time</b>: %{customdata[0]}<br>"
                    "<b>UTC Time</b>: %{customdata[1]}<br>"
                    "<b>US AQI</b>: %{y:.0f}"
                    "<extra></extra>"
                ),
                customdata=outdoor_chart_df[["local_time", "utc_time"]],
            )

            outdoor_aqi_fig.update_xaxes(
                nticks=6,
                tickformat="%b %-d<br>%-I %p",
            )
            outdoor_aqi_fig.update_layout(height=330)
            st.plotly_chart(outdoor_aqi_fig, use_container_width=True)
            st.markdown(
                '<div class="outdoor-attribution">'
                "Outdoor air quality data provided by the IQAir Community API."
                "</div>",
                unsafe_allow_html=True,
            )
    else:
        with outdoor_summary_col:
            with st.container(border=True):
                st.subheader("Local Outdoor Summary")
                st.info("No outdoor readings found.")

        with outdoor_chart_col:
            st.subheader("Local Outdoor AQI (Last 24 Hours)")
            st.info("No outdoor readings found.")

    with st.expander("Raw Data"):
        st.dataframe(df)

else:
    st.warning("No sensor readings found.")
