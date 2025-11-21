import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import lsim, TransferFunction

# -------------------------------------------------------------
# Default CSV URL
# -------------------------------------------------------------
DEFAULT_URL = "https://raw.githubusercontent.com/TendoPain18/load-cell-transducer-signal-conditioning-circuit/main/data/Data_not_const_with_headers.csv"

# -------------------------------------------------------------
# CACHED CSV LOADING  (big speed improvement)
# -------------------------------------------------------------
@st.cache_data
def load_csv(path_or_file):
    return pd.read_csv(path_or_file)

# -------------------------------------------------------------
# CACHED FILTERING (lsim is expensive)
# -------------------------------------------------------------
@st.cache_data
def compute_output(Vin, t, Wc, Ri, Rf):
    num = [-(Rf / Ri) * Wc]
    den = [1, Wc]
    system = TransferFunction(num, den)

    tout, Vout_inverted, _ = lsim(system, Vin, t)
    return Vout_inverted * (-(Rf / Ri))


# -------------------------------------------------------------
# UI HEADER
# -------------------------------------------------------------
st.title("Interactive Low-Pass Filter Simulator")

st.write("""
This app loads a default CSV file automatically.  
You can also upload your own CSV if you want.

### 📌 Required CSV structure:
Your CSV **must contain the following column names** exactly:

- `Time (s)`
- `Channel 1 (V)`

Any other structure will not work.
""")

# -------------------------------------------------------------
# LOAD DATA (DEFAULT OR UPLOADED)
# -------------------------------------------------------------
uploaded_file = st.file_uploader("Upload CSV file (optional)", type=["csv"])

try:
    if uploaded_file:
        data = load_csv(uploaded_file)
        st.success("Custom CSV loaded successfully!")
    else:
        st.info("Using default CSV file from GitHub...")
        data = load_csv(DEFAULT_URL)
except Exception as e:
    st.error(f"Error loading CSV: {e}")
    st.stop()

# Check required columns
required_cols = ["Time (s)", "Channel 1 (V)"]
if not all(col in data.columns for col in required_cols):
    st.error(f"CSV missing required columns: {required_cols}")
    st.stop()

# Extract data
t = data["Time (s)"].values
Vin = data["Channel 1 (V)"].values

# -------------------------------------------------------------
# Wc RANGE CONTROLS
# -------------------------------------------------------------
st.subheader("Adjust Wc Slider Range")

if "wc_min" not in st.session_state:
    st.session_state.wc_min = 0
if "wc_max" not in st.session_state:
    st.session_state.wc_max = 1000

new_min = st.number_input("Wc Min Value", value=st.session_state.wc_min)
new_max = st.number_input("Wc Max Value", value=st.session_state.wc_max)

if st.button("Update Range"):
    if new_min >= new_max:
        st.error("Min value must be LESS than Max value!")
    else:
        st.session_state.wc_min = new_min
        st.session_state.wc_max = new_max
        st.success(f"Range updated to: {new_min} → {new_max}")

# -------------------------------------------------------------
# Wc SLIDER
# -------------------------------------------------------------
Wc = st.slider(
    "Cutoff Frequency (Wc)",
    min_value=int(st.session_state.wc_min),
    max_value=int(st.session_state.wc_max),
    value=min(25, int(st.session_state.wc_max)),
    step=1
)

# -------------------------------------------------------------
# COMPUTE FILTERED OUTPUT (from cache!)
# -------------------------------------------------------------
Rf = 33000
Ri = 33000

Vout = compute_output(Vin, t, Wc, Ri, Rf)

# -------------------------------------------------------------
# PLOTTING
# -------------------------------------------------------------
fig, ax = plt.subplots(2, 1, figsize=(10, 6))

ax[0].plot(t, Vin)
ax[0].set_title("Input Voltage vs Time")
ax[0].set_xlabel("Time (s)")
ax[0].set_ylabel("Input Voltage (V)")

ax[1].plot(t, Vout)
ax[1].set_title("Output Voltage vs Time")
ax[1].set_xlabel("Time (s)")
ax[1].set_ylabel("Output Voltage (V)")

st.pyplot(fig)
