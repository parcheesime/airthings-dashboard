from pathlib import Path
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

      @media (max-width: 900px) {
        .current-grid {
          grid-template-columns: repeat(2, minmax(0, 1fr));
        }
      }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🌬️ Airthings Air Quality Dashboard")
st.caption("Live indoor air quality monitoring")

df = get_readings_df(limit=100)
outdoor_df = get_outdoor_readings_df(limit=100)

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
              <div class="current-title">Current Conditions <span>{overall_status}</span></div>
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
            st.subheader("30 Minute Summary")

            st.markdown("**VOC**")
            voc_avg_col, voc_peak_col = st.columns(2)
            voc_avg_col.markdown("Average")
            voc_avg_col.markdown(f"{avg_voc:.0f} ppb")
            voc_peak_col.markdown("Peak")
            voc_peak_col.markdown(f"{max_voc:.0f} ppb")

            st.markdown("**PM2.5**")
            pm25_avg_col, pm25_peak_col = st.columns(2)
            pm25_avg_col.markdown("Average")
            pm25_avg_col.markdown(f"{avg_pm25:.1f} µg/m³")
            pm25_peak_col.markdown("Peak")
            pm25_peak_col.markdown(f"{max_pm25:.1f} µg/m³")

            st.markdown("**Timing**")
            st.markdown("Last sensor reading")
            st.markdown(latest["recorded_at_local"].strftime("%Y-%m-%d %I:%M:%S %p"))
            st.markdown("Last data pull")
            st.markdown(latest["pulled_at_local"].strftime("%Y-%m-%d %I:%M:%S %p"))

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

    st.divider()

    sdsu_summary_col, sdsu_chart_col = st.columns([1, 2.4], gap="large")

    if not outdoor_df.empty:
        outdoor_df = outdoor_df.sort_values("recorded_at_local")
        latest_outdoor = outdoor_df.iloc[-1]
        latest_outdoor_time = latest_outdoor["recorded_at_local"]
        outdoor_last_30 = outdoor_df[
            outdoor_df["recorded_at_local"]
            >= latest_outdoor_time - pd.Timedelta(minutes=30)
        ]

        outdoor_avg_pm25 = outdoor_last_30["pm25"].mean()
        outdoor_max_pm25 = outdoor_last_30["pm25"].max()

        outdoor_chart_df = outdoor_df.copy()
        outdoor_chart_df["local_time"] = outdoor_chart_df[
            "recorded_at_local"
        ].dt.strftime("%Y-%m-%d %I:%M:%S %p")
        outdoor_chart_df["utc_time"] = outdoor_chart_df["recorded_at"].dt.strftime(
            "%Y-%m-%d %H:%M:%S UTC"
        )

        with sdsu_summary_col:
            with st.container(height=430, border=True):
                st.subheader("SDSU Outdoor Summary")

                if "station_name" in latest_outdoor and pd.notna(
                    latest_outdoor["station_name"]
                ):
                    st.markdown(latest_outdoor["station_name"])

                st.markdown("**PM2.5**")
                outdoor_avg_col, outdoor_peak_col = st.columns(2)
                outdoor_avg_col.markdown("Average")
                outdoor_avg_col.markdown(f"{outdoor_avg_pm25:.1f} µg/m³")
                outdoor_peak_col.markdown("Peak")
                outdoor_peak_col.markdown(f"{outdoor_max_pm25:.1f} µg/m³")

                st.markdown("**Latest Reading**")
                st.markdown(f"{latest_outdoor['pm25']:.1f} µg/m³")

                st.markdown("**Timing**")
                st.markdown("Last sensor reading")
                st.markdown(
                    latest_outdoor["recorded_at_local"].strftime(
                        "%Y-%m-%d %I:%M:%S %p"
                    )
                )

                if "pulled_at_local" in latest_outdoor and pd.notna(
                    latest_outdoor["pulled_at_local"]
                ):
                    st.markdown("Last data pull")
                    st.markdown(
                        latest_outdoor["pulled_at_local"].strftime(
                            "%Y-%m-%d %I:%M:%S %p"
                        )
                    )

        with sdsu_chart_col:
            st.subheader("SDSU PM2.5 Over Time")

            outdoor_pm25_fig = px.line(
                outdoor_chart_df,
                x="recorded_at_local",
                y="pm25",
                markers=True,
                labels={
                    "recorded_at_local": "Local Time",
                    "pm25": "PM2.5 (µg/m³)",
                },
            )

            outdoor_pm25_fig.update_traces(
                hovertemplate=(
                    "<b>Local Time</b>: %{customdata[0]}<br>"
                    "<b>UTC Time</b>: %{customdata[1]}<br>"
                    "<b>PM2.5</b>: %{y:.1f} µg/m³"
                    "<extra></extra>"
                ),
                customdata=outdoor_chart_df[["local_time", "utc_time"]],
            )

            outdoor_pm25_fig.update_layout(height=330)
            st.plotly_chart(outdoor_pm25_fig, use_container_width=True)
    else:
        with sdsu_summary_col:
            with st.container(height=430, border=True):
                st.subheader("SDSU Outdoor Summary")
                st.info("No outdoor readings found.")

        with sdsu_chart_col:
            st.subheader("SDSU PM2.5 Over Time")
            st.info("No outdoor readings found.")

    with st.expander("Raw Data"):
        st.dataframe(df)

else:
    st.warning("No sensor readings found.")
