import streamlit as st
import math
import time
import base64
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="Large Scale PV Tool",
    page_icon="🔆",
    layout="wide"
)

# =====================================================
# SESSION STATE
# =====================================================
if "page" not in st.session_state:
    st.session_state.page = "welcome"

# =====================================================
# NAVIGATION FUNCTIONS
# =====================================================
def go_dimensioning():
    st.session_state.page = "dimensioning"

def go_part_b():
    st.session_state.page = "part_b"

def go_part_c():
    st.session_state.page = "part_c"

# =====================================================
# BACKGROUND
# =====================================================
def apply_background():
    try:
        with open("bg.png", "rb") as img_file:
            encoded = base64.b64encode(img_file.read()).decode()
            st.markdown(
                f"""
                <style>
                .stApp {{
                    background-image: url("data:image/jpg;base64,{encoded}");
                    background-size: cover;
                    background-position: center;
                    background-attachment: fixed;
                }}
                </style>
                """,
                unsafe_allow_html=True
            )
    except FileNotFoundError:
        st.markdown("""
        <style>
        .stApp { background-color: #f2f2f2; }
        </style>
        """, unsafe_allow_html=True)

# =====================================================
# PAGE ROUTING
# =====================================================
if st.session_state.page == "welcome":

    apply_background()

    st.title("Large Scale PV Fault Simulation Tool")
    st.write("Interactive PV farm design & fault analysis system")

    if st.button("👉 Start"):
        go_dimensioning()
        st.rerun()

# =====================================================
# PART A
# =====================================================
elif st.session_state.page == "dimensioning":

    st.header("Part A: PV Dimensioning")

    panel_length = st.number_input("Panel Length", value=2.382)
    panel_width = st.number_input("Panel Width", value=1.134)
    rated_power = st.number_input("Rated Power (W)", value=605)

    site_width = st.number_input("Site Width", value=183.27)
    site_length = st.number_input("Site Length", value=202.18)
    gap = st.number_input("Gap", value=0.01)

    area = panel_length * panel_width

    N_landscape = math.floor(site_width/(panel_width+gap)) * math.floor(site_length/(panel_length+gap))
    N_portrait = math.floor(site_width/(panel_length+gap)) * math.floor(site_length/(panel_width+gap))

    best_count = max(N_landscape, N_portrait)

    st.success(f"Max Modules: {best_count}")

    power_total = best_count * rated_power

    st.metric("Total Power (W)", power_total)

    if st.button("👉 Go to Part B"):
        st.session_state.best_count = best_count
        st.session_state.rated_power = rated_power
        go_part_b()
        st.rerun()

# =====================================================
# PART B
# =====================================================
elif st.session_state.page == "part_b":

    st.header("Part B: Inverter Sizing")

    best_count = st.session_state.get("best_count", 0)
    rated_power = st.session_state.get("rated_power", 605)

    dc_ac = st.number_input("DC/AC Ratio", value=1.1)

    inv_size = (best_count * rated_power) / dc_ac

    st.metric("Required Inverter Power (W)", inv_size)

    ns_rec = st.number_input("Modules per string (Ns)", value=10)

    if st.button("👉 Go to Part C"):
        st.session_state.best_count = best_count
        st.session_state.rated_power = rated_power
        go_part_c()
        st.rerun()

# =====================================================
# PART C
# =====================================================
elif st.session_state.page == "part_c":

    st.header("Part C: Fault Simulation (RoCoP Analysis)")

    best_count = st.session_state.get("best_count")
    rated_power = st.session_state.get("rated_power")

    if best_count is None:
        st.error("No data from Part A. Go back.")
        st.stop()

    start = st.sidebar.number_input("Start Hour", value=9.0)
    end = st.sidebar.number_input("End Hour", value=10.0)
    dt = st.sidebar.selectbox("Resolution", [1, 5, 10], index=0)
    fault_time = st.sidebar.slider("Fault Time", start, end, 9.5)

    N_area = max(best_count // 3, 1)
    P_area = N_area * rated_power

    time_steps = np.arange(0, (end-start)*3600, dt)
    time_hours = start + time_steps/3600

    def power(fault=False):
        G = np.ones_like(time_hours) * 1000
        if fault:
            G[time_hours >= fault_time] = 200
        return P_area * (G/1000)

    P_A = power(False)
    P_B = power(True)
    P_C = power(False)

    P_total = P_A + P_B + P_C

    R = np.abs(np.diff(P_total)) / dt
    tR = time_hours[1:]

    st.metric("Max RoCoP", np.max(R))

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=time_hours, y=P_total, name="Total Power"))
    fig.add_vline(x=fault_time, line_dash="dash", line_color="red")

    st.plotly_chart(fig, use_container_width=True)

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=tR, y=R, name="RoCoP"))
    st.plotly_chart(fig2, use_container_width=True)

    df = pd.DataFrame({
        "Time": time_hours,
        "Power": P_total
    })

    st.dataframe(df)

    st.download_button("Download CSV", df.to_csv(index=False), "pv.csv")
