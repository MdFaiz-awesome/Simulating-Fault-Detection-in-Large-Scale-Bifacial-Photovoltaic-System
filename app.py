import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="PV Farm RoCoP Dashboard",
    page_icon="⚡",
    layout="wide"
)

# =====================================================
# TITLE
# =====================================================
st.title("⚡ PV Farm RoCoP Monitoring Dashboard")
st.markdown("Interactive Simulation for Large Scale Bifacial Photovoltaic Fault Detection")

# =====================================================
# SIDEBAR SETTINGS
# =====================================================
st.sidebar.header("⚙️ Simulation Settings")

start_hour = st.sidebar.number_input("Start Hour", value=9.0)
end_hour = st.sidebar.number_input("End Hour", value=10.0)

dt = st.sidebar.selectbox(
    "Time Resolution (seconds)",
    [1, 5, 10],
    index=0
)

fault_areas = st.sidebar.multiselect(
    "Select Fault Areas",
    ["A", "B", "C"],
    default=["B"]
)

fault_time = st.sidebar.slider(
    "Fault Start Time",
    min_value=float(start_hour),
    max_value=float(end_hour),
    value=9.5,
    step=0.01
)

irradiance_fault = st.sidebar.slider(
    "Fault Irradiance (W/m²)",
    min_value=0,
    max_value=1000,
    value=200
)

noise_level = st.sidebar.slider(
    "Noise Level (%)",
    min_value=0.0,
    max_value=1.0,
    value=0.2
) / 100

# =====================================================
# PV PARAMETERS
# =====================================================
P_panel = 605
alpha = -0.23 / 100
T = 25

N_series = 160
N_parallel = 84

N_total = N_series * N_parallel
N_area = N_total // 3

P_area = N_area * P_panel

# =====================================================
# TIME VECTOR
# =====================================================
time_seconds = np.arange(0, (end_hour - start_hour) * 3600, dt)
time_hours = start_hour + time_seconds / 3600

# =====================================================
# FUNCTIONS
# =====================================================
def irradiance_profile(area):
    G = np.ones_like(time_hours) * 1000

    if area in fault_areas:
        G[time_hours >= fault_time] = irradiance_fault

    return G


def pv_power(G):
    return P_area * (G / 1000) * (1 - alpha * (T - 25))


def rocop(P):
    return np.abs(np.diff(P)) / dt


def classify(R, T1, T2):
    labels = []

    for r in R:
        if r < T1:
            labels.append("Normal")
        elif r < T2:
            labels.append("Shading")
        else:
            labels.append("Fault")

    return labels


# =====================================================
# SIMULATION
# =====================================================
P_A = pv_power(irradiance_profile("A"))
P_B = pv_power(irradiance_profile("B"))
P_C = pv_power(irradiance_profile("C"))

P_total = P_A + P_B + P_C

# Add noise
P_total += noise_level * P_total.max() * np.random.randn(len(P_total))

# RoCoP
R = rocop(P_total)
t_rocop = time_hours[1:]

# Threshold
R_normal_sample = R[:100]

T1 = np.max(R_normal_sample) * 1.5
T2 = T1 * 5

labels = classify(R, T1, T2)

# =====================================================
# KPI SECTION
# =====================================================
st.subheader("📌 System Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Panels", f"{N_total:,}")
col2.metric("Rated Capacity", f"{(N_total * P_panel)/1e6:.2f} MW")
col3.metric("Fault Areas", ", ".join(fault_areas) if fault_areas else "None")
col4.metric("Max RoCoP", f"{np.max(R):,.0f} W/s")

# =====================================================
# GRAPH 1 TOTAL POWER
# =====================================================
fig1 = go.Figure()

fig1.add_trace(go.Scatter(
    x=time_hours,
    y=P_total,
    mode="lines",
    name="Total Power"
))

fig1.add_vline(
    x=fault_time,
    line_dash="dash",
    line_color="red"
)

fig1.update_layout(
    title="Total PV Farm Power",
    xaxis_title="Time (Hour)",
    yaxis_title="Power (W)",
    hovermode="x unified"
)

st.plotly_chart(fig1, use_container_width=True)

# =====================================================
# GRAPH 2 AREA POWER
# =====================================================
fig2 = go.Figure()

fig2.add_trace(go.Scatter(
    x=time_hours,
    y=P_A,
    mode="lines",
    name="Area A"
))

fig2.add_trace(go.Scatter(
    x=time_hours,
    y=P_B,
    mode="lines",
    name="Area B"
))

fig2.add_trace(go.Scatter(
    x=time_hours,
    y=P_C,
    mode="lines",
    name="Area C"
))

fig2.add_vline(
    x=fault_time,
    line_dash="dash",
    line_color="red"
)

fig2.update_layout(
    title="PV Farm Power by Area",
    xaxis_title="Time (Hour)",
    yaxis_title="Power (W)",
    hovermode="x unified"
)

st.plotly_chart(fig2, use_container_width=True)

# =====================================================
# GRAPH 3 ROCOP
# =====================================================
fig3 = go.Figure()

fig3.add_trace(go.Scatter(
    x=t_rocop,
    y=R,
    mode="lines",
    name="RoCoP"
))

fig3.add_vline(
    x=fault_time,
    line_dash="dash",
    line_color="red"
)

fig3.update_layout(
    title="RoCoP Analysis",
    xaxis_title="Time (Hour)",
    yaxis_title="RoCoP (W/s)",
    hovermode="x unified"
)

st.plotly_chart(fig3, use_container_width=True)

# =====================================================
# FAULT STATUS
# =====================================================
st.subheader("⚠️ Fault Status")

status_data = []

for area in ["A", "B", "C"]:
    if area in fault_areas:
        status = "FAULT"
    else:
        status = "NORMAL"

    status_data.append([area, status])

status_df = pd.DataFrame(status_data, columns=["Area", "Status"])

st.table(status_df)

# =====================================================
# CLASSIFICATION SUMMARY
# =====================================================
st.subheader("📊 RoCoP Classification Summary")

summary = pd.Series(labels).value_counts()

st.write(summary)

# =====================================================
# DATA TABLE
# =====================================================
st.subheader("📁 Simulation Data")

df = pd.DataFrame({
    "Time (Hour)": time_hours,
    "Total Power (W)": P_total,
    "Area A (W)": P_A,
    "Area B (W)": P_B,
    "Area C (W)": P_C
})

st.dataframe(df, use_container_width=True)

# =====================================================
# DOWNLOAD BUTTON
# =====================================================
csv = df.to_csv(index=False).encode("utf-8")

st.download_button(
    "⬇️ Download CSV Data",
    csv,
    "pv_farm_data.csv",
    "text/csv"
)
