"""
Milling Operation MRR & Power Requirement Estimator
----------------------------------------------------
Diploma in Mechanical Engineering - Semester 3
Python Mini Project (Topic 21)

This Streamlit app lets a user enter slab/face milling parameters
(cutter diameter, number of teeth, feed per tooth, cutting speed,
depth of cut, width of cut) and instantly computes:
    1. Spindle speed (N)
    2. Table feed rate (Vf)
    3. Material Removal Rate (MRR)
    4. Cutting power and required spindle motor power

Formulas used (standard machining theory):
    N  (rpm)      = (1000 x Vc) / (pi x D)
    Vf (mm/min)   = N x Z x fz
    MRR (mm3/min) = Vf x d x w
    Pc (kW)       = (MRR x Ks) / (60 x 10^6)
    Pmotor (kW)   = Pc / eta
"""

import math
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

# ----------------------------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="Milling MRR & Power Estimator",
    page_icon="⚙️",
    layout="wide",
)

# ----------------------------------------------------------------------
# TEAM DETAILS  (EDIT THESE BEFORE SUBMISSION)
# ----------------------------------------------------------------------
GROUP_NO = "Group 21"
MEMBERS = [
    ("Member Name 1", "Enrollment No. 1"),
    ("Member Name 2", "Enrollment No. 2"),
    ("Member Name 3", "Enrollment No. 3"),
]

st.title("⚙️ Milling Operation: MRR & Power Requirement Estimator")
st.caption("Topic 21 | Slab / Face Milling Calculator | Python & Streamlit Mini Project")

with st.expander("👥 Team Details", expanded=True):
    st.markdown(f"**{GROUP_NO}**")
    cols = st.columns(len(MEMBERS))
    for c, (name, enr) in zip(cols, MEMBERS):
        c.markdown(f"**{name}**  \nEnrollment: {enr}")

st.markdown("---")

# ----------------------------------------------------------------------
# SIDEBAR — INPUTS
# ----------------------------------------------------------------------
st.sidebar.header("🔧 Input Parameters")

D = st.sidebar.number_input("Cutter Diameter, D (mm)", min_value=1.0, max_value=500.0,
                             value=80.0, step=1.0,
                             help="Outer diameter of the milling cutter")

Z = st.sidebar.number_input("Number of Teeth, Z", min_value=1, max_value=40,
                             value=8, step=1,
                             help="Total number of cutting teeth/flutes on the cutter")

fz = st.sidebar.slider("Feed per Tooth, fz (mm/tooth)", min_value=0.01, max_value=1.00,
                        value=0.15, step=0.01,
                        help="Chip load — feed per tooth per revolution")

Vc = st.sidebar.slider("Cutting Speed, Vc (m/min)", min_value=5.0, max_value=500.0,
                        value=90.0, step=1.0,
                        help="Peripheral cutting speed of the cutter")

d = st.sidebar.slider("Depth of Cut, d (mm)", min_value=0.1, max_value=25.0,
                       value=3.0, step=0.1,
                       help="Axial depth of cut (perpendicular to feed, into the material)")

w = st.sidebar.slider("Width of Cut, w (mm)", min_value=0.1, max_value=300.0,
                       value=50.0, step=1.0,
                       help="Radial width of cut engaged by the cutter")

st.sidebar.markdown("---")
st.sidebar.subheader("⚡ Power Model Parameters")

material = st.sidebar.selectbox(
    "Workpiece Material (sets specific cutting energy Ks)",
    ["Mild Steel (Ks=2200 N/mm²)", "Cast Iron (Ks=1500 N/mm²)",
     "Aluminium Alloy (Ks=800 N/mm²)", "Alloy Steel (Ks=2800 N/mm²)",
     "Custom"],
)

Ks_map = {
    "Mild Steel (Ks=2200 N/mm²)": 2200,
    "Cast Iron (Ks=1500 N/mm²)": 1500,
    "Aluminium Alloy (Ks=800 N/mm²)": 800,
    "Alloy Steel (Ks=2800 N/mm²)": 2800,
}

if material == "Custom":
    Ks = st.sidebar.number_input("Specific Cutting Energy, Ks (N/mm²)",
                                  min_value=100.0, max_value=5000.0, value=2000.0, step=50.0)
else:
    Ks = Ks_map[material]
    st.sidebar.write(f"Selected Ks = **{Ks} N/mm²**")

eta = st.sidebar.slider("Machine Mechanical Efficiency, η (%)", min_value=50, max_value=100,
                         value=80, step=1) / 100.0

# ----------------------------------------------------------------------
# VALIDATION
# ----------------------------------------------------------------------
errors = []
if D <= 0:
    errors.append("Cutter diameter must be greater than 0.")
if Z <= 0:
    errors.append("Number of teeth must be at least 1.")
if fz <= 0:
    errors.append("Feed per tooth must be greater than 0.")
if Vc <= 0:
    errors.append("Cutting speed must be greater than 0.")
if d <= 0:
    errors.append("Depth of cut must be greater than 0.")
if w <= 0:
    errors.append("Width of cut must be greater than 0.")
if w > D:
    errors.append("⚠️ Width of cut cannot exceed the cutter diameter — check your inputs.")
if d > 25:
    errors.append("⚠️ Depth of cut looks unrealistically large for a single pass.")

if errors:
    for e in errors:
        st.error(e)
    st.stop()

# ----------------------------------------------------------------------
# CALCULATIONS
# ----------------------------------------------------------------------
N = (1000 * Vc) / (math.pi * D)          # spindle speed, rpm
Vf = N * Z * fz                           # table feed rate, mm/min
MRR = Vf * d * w                          # mm^3/min
MRR_cm3 = MRR / 1000.0                    # cm^3/min
Pc_kW = (MRR * Ks) / (60 * 1e6)           # cutting power, kW
Pmotor_kW = Pc_kW / eta                   # motor power required, kW
Pmotor_hp = Pmotor_kW * 1.34102           # convert kW -> HP

# ----------------------------------------------------------------------
# RESULTS DISPLAY
# ----------------------------------------------------------------------
st.subheader("📊 Results")

r1, r2, r3, r4 = st.columns(4)
r1.metric("Spindle Speed (N)", f"{N:,.1f} rpm")
r2.metric("Table Feed Rate (Vf)", f"{Vf:,.1f} mm/min")
r3.metric("MRR", f"{MRR_cm3:,.2f} cm³/min")
r4.metric("Motor Power Required", f"{Pmotor_kW:,.2f} kW")

st.info(f"Cutting Power at the cutter: **{Pc_kW:.3f} kW**  |  "
        f"Required Spindle Motor Power (incl. efficiency η={eta*100:.0f}%): "
        f"**{Pmotor_kW:.3f} kW ≈ {Pmotor_hp:.2f} HP**")

with st.expander("🧮 Show Formulas & Step-by-Step Calculation"):
    st.latex(r"N = \frac{1000 \times V_c}{\pi \times D}")
    st.write(f"N = (1000 × {Vc}) / (π × {D}) = **{N:.2f} rpm**")

    st.latex(r"V_f = N \times Z \times f_z")
    st.write(f"Vf = {N:.2f} × {Z} × {fz} = **{Vf:.2f} mm/min**")

    st.latex(r"MRR = V_f \times d \times w")
    st.write(f"MRR = {Vf:.2f} × {d} × {w} = **{MRR:,.1f} mm³/min "
             f"({MRR_cm3:,.2f} cm³/min)**")

    st.latex(r"P_c = \frac{MRR \times K_s}{60 \times 10^{6}}")
    st.write(f"Pc = ({MRR:,.1f} × {Ks}) / (60 × 10⁶) = **{Pc_kW:.3f} kW**")

    st.latex(r"P_{motor} = \frac{P_c}{\eta}")
    st.write(f"Pmotor = {Pc_kW:.3f} / {eta:.2f} = **{Pmotor_kW:.3f} kW**")

st.markdown("---")

# ----------------------------------------------------------------------
# VISUALIZATION
# ----------------------------------------------------------------------
st.subheader("📈 Visualization: Effect of Depth of Cut on MRR & Power")

d_range = np.linspace(0.1, 25, 60)
MRR_range = (Vf * d_range * w) / 1000.0                       # cm3/min
Pmotor_range = ((Vf * d_range * w) * Ks) / (60 * 1e6 * eta)   # kW

fig, ax1 = plt.subplots(figsize=(8, 4.5))

color1 = "tab:blue"
ax1.set_xlabel("Depth of Cut, d (mm)")
ax1.set_ylabel("MRR (cm³/min)", color=color1)
ax1.plot(d_range, MRR_range, color=color1, linewidth=2, label="MRR")
ax1.tick_params(axis="y", labelcolor=color1)
ax1.grid(True, linestyle="--", alpha=0.5)

ax2 = ax1.twinx()
color2 = "tab:red"
ax2.set_ylabel("Motor Power (kW)", color=color2)
ax2.plot(d_range, Pmotor_range, color=color2, linewidth=2, linestyle="--", label="Motor Power")
ax2.tick_params(axis="y", labelcolor=color2)

ax1.axvline(d, color="gray", linestyle=":", linewidth=1)
ax1.scatter([d], [MRR_cm3], color=color1, zorder=5)
ax2.scatter([d], [Pmotor_kW], color=color2, zorder=5)

fig.suptitle("MRR and Required Motor Power vs Depth of Cut")
fig.tight_layout()

st.pyplot(fig)
st.caption("The dot marks your current input values. Dashed vertical line shows the "
           "selected depth of cut, d.")

st.markdown("---")
st.caption("Built with Python + Streamlit | Formulas based on standard machining/metal "
           "cutting theory (Kalpakjian, Boothroyd) | Mini Project Topic 21")
