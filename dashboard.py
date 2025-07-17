import pytz
import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
import os
from glob import glob
from datetime import datetime
import pytz
import plotly.express as px

st.set_page_config(layout="wide", page_title="Patch Sensor Dashboard")

st.title("🩹 Patch Sensor Dashboard")
st.markdown("Live visualization of parsed sensor data")

# === SETTINGS ===
log_folder = "logs"
refresh_interval = 5  # seconds
max_rows = 500  # max rows to show from log

# === Load latest log file ===
log_files = sorted(glob(os.path.join(log_folder, "sensor_log_*.csv")))
if not log_files:
    st.warning("No log files found in 'logs/' folder.")
    st.stop()

latest_log = log_files[-1]
st.caption(f"Loaded log file: `{os.path.basename(latest_log)}`")

df = pd.read_csv(latest_log)

if df.empty:
    st.warning("Log file is empty.")
    st.stop()

# === Select patches and sensors ===
patch_ids = sorted(df["patch_id"].unique())
sensor_columns = [
    "temperature_ohms", "voc_1_ohms", "voc_2_ohms", "voc_3_ohms",
    "co2_ohms", "optical_ohms", "capacitance_raw"
]

st.sidebar.header("Filter")
selected_patches = st.sidebar.multiselect("Patch IDs", patch_ids, default=patch_ids)
selected_sensors = st.sidebar.multiselect("Sensors", sensor_columns, default=sensor_columns)

# === Filter dataframe
df_filtered = df[df["patch_id"].isin(selected_patches)]

# === Plot each patch
for patch_id in selected_patches:
    patch_df = df_filtered[df_filtered["patch_id"] == patch_id]

    if patch_df.empty:
        continue

    st.subheader(f"📟 Patch ID: {patch_id}")
    #st.line_chart(patch_df.set_index("timestamp")[selected_sensors])
    fig = px.line(
        patch_df,
        x="timestamp",
        y=selected_sensors,
        title=f"Patch {patch_id} Sensors",
        labels={"timestamp": "Time (EST)"}
    )
    fig.update_layout(xaxis=dict(rangeslider_visible=True))
    reset_button = st.button(f"Reset View for Patch {patch_id}")

    if reset_button:
        fig.update_layout(xaxis_autorange=True, yaxis_autorange=True)

    st.plotly_chart(fig, use_container_width=True)
# === Auto-refresh hint
st.caption(f"Auto-refresh every {refresh_interval} seconds (hit R or F5 manually).")
st_autorefresh(interval=1000, key="refresh") #5 seconds