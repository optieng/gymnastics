import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Arc


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Rhythmic Gymnastics Throw Visualiser",
    page_icon="⭕",
    layout="wide"
)

st.title("Rhythmic Gymnastics Throw Visualiser")

st.markdown(
    """
    Explore how the arm angle and release speed affect the theoretical
    distance and peak height of a hoop throw.

    **Angle convention:** 0° = arm vertically upwards; 90° = arm horizontal.
    """
)


# --------------------------------------------------
# PHYSICS FUNCTIONS
# --------------------------------------------------

def get_alpha(S, V, g=9.81):
    """Calculate the angle from vertical, in degrees."""
    ratio = (S * g) / V**2
    ratio = np.clip(ratio, -1.0, 1.0)
    return np.degrees(0.5 * np.arcsin(ratio))


def get_height(alpha, V, g=9.81):
    """
    Calculate peak height above the release point.

    alpha is the launch angle measured from the horizontal,
    in degrees.
    """
    return ((V * np.sin(np.radians(alpha)))**2) / (2 * g)


# --------------------------------------------------
# USER CONTROLS
# --------------------------------------------------

st.subheader("Adjust the throwing arm")

alpha_deg = st.slider(
    "Arm angle α (degrees from vertical)",
    min_value=0,
    max_value=90,
    value=45,
    step=1,
    help="0° is vertically upwards; 90° is horizontally outwards."
)

st.markdown(f"### Selected arm angle: **{alpha_deg}°**")

# Speeds used in the model
V = [3, 5, 7, 9]

# Gravitational acceleration
g = 9.81


# --------------------------------------------------
# CREATE THREE-PANEL FIGURE
# --------------------------------------------------

fig, (ax1, ax2, ax3) = plt.subplots(
    1,
    3,
    figsize=(18, 6),
    gridspec_kw={"width_ratios": [1.2, 0.8, 1.2]}
)

fig.subplots_adjust(
    left=0.06,
    right=0.98,
    top=0.86,
    bottom=0.15,
    wspace=0.35
)


# --------------------------------------------------
# GRAPH 1: DISTANCE VERSUS ANGLE
# --------------------------------------------------

S = np.linspace(0, 10, 200)

for v in V:
    # Only plot distances that give a valid arcsin argument.
    valid = (S * g / v**2) <= 1

    a = get_alpha(S[valid], v, g)
    ax1.plot(a, S[valid], "-", label=f"{v} m/s")

ax1.set_xlabel("Angle wrt vertical [°]")
ax1.set_ylabel("Distance [m]")
ax1.set_title("Distance vs. angle")
ax1.legend(title="Release speed")
ax1.grid(True, alpha=0.3)

# Indicator for the selected angle
ax1.axvline(
    alpha_deg,
    color="red",
    linestyle="--",
    linewidth=2
)

ax1.set_xlim(0, 90)


# --------------------------------------------------
# GRAPH 2: GYMNAST SILHOUETTE
# --------------------------------------------------

scale = 0.5

ax2.set_title("Gymnast and hoop")
ax2.set_aspect("equal")
ax2.set_xlim(-0.6, 1.2)
ax2.set_ylim(0, 2.2)
ax2.axis("off")

# Head
ax2.add_patch(
    Circle(
        (0, 3.2 * scale),
        0.18 * scale,
        color="black"
    )
)

# Body
ax2.plot(
    [0, 0],
    [1.5 * scale, 3.0 * scale],
    color="black",
    linewidth=12 * scale,
    solid_capstyle="round"
)

# Legs
ax2.plot(
    [0, -0.4 * scale],
    [1.5 * scale, 0.2 * scale],
    color="black",
    linewidth=10 * scale,
    solid_capstyle="round"
)

ax2.plot(
    [0, 0.4 * scale],
    [1.5 * scale, 0.2 * scale],
    color="black",
    linewidth=10 * scale,
    solid_capstyle="round"
)

# Shoulder position
shoulder = np.array([0.0, 2.7 * scale])

# Arm geometry
arm_length = 1.3 * scale
alpha_rad = np.radians(alpha_deg)

hand = shoulder + arm_length * np.array([
    np.sin(alpha_rad),
    np.cos(alpha_rad)
])

# Draw arm
ax2.plot(
    [shoulder[0], hand[0]],
    [shoulder[1], hand[1]],
    color="black",
    linewidth=9 * scale,
    solid_capstyle="round"
)

# Draw hoop at the hand
hoop = Circle(
    hand,
    0.22 * scale,
    fill=False,
    edgecolor="black",
    linewidth=2
)

ax2.add_patch(hoop)

# Angle arc: measured from the upward vertical
angle_arc = Arc(
    shoulder,
    1.0 * scale,
    1.0 * scale,
    theta1=90 - alpha_deg,
    theta2=90,
    color="red",
    linewidth=1.5
)

ax2.add_patch(angle_arc)

# Angle label
ax2.text(
    0.35 * scale,
    3.05 * scale,
    rf"$\alpha = {alpha_deg}^\circ$",
    fontsize=11,
    color="red"
)


# --------------------------------------------------
# GRAPH 3: PEAK HEIGHT VERSUS ANGLE
# --------------------------------------------------

a = np.linspace(0, 90, 200)

for v in V:
    # Convert angle from vertical to angle from horizontal.
    h = get_height(90 - a, v, g)

    ax3.plot(a, h, "-", label=f"{v} m/s")

ax3.set_xlabel("Angle wrt vertical [°]")
ax3.set_ylabel("Peak height above release point [m]")
ax3.set_title("Peak height vs. angle")
ax3.legend(title="Release speed")
ax3.grid(True, alpha=0.3)

# Indicator for the selected angle
ax3.axvline(
    alpha_deg,
    color="red",
    linestyle="--",
    linewidth=2
)

ax3.set_xlim(0, 90)


# --------------------------------------------------
# DISPLAY FIGURE IN STREAMLIT
# --------------------------------------------------

st.pyplot(fig, use_container_width=True)
plt.close(fig)


# --------------------------------------------------
# OPTIONAL NUMERICAL SUMMARY
# --------------------------------------------------

st.subheader("Peak height at the selected angle")

# alpha_deg is measured from vertical, so the launch angle
# from horizontal is 90 - alpha_deg.
launch_angle = 90 - alpha_deg

columns = st.columns(len(V))

for col, v in zip(columns, V):
    height = get_height(launch_angle, v, g)

    col.metric(
        label=f"Release speed: {v} m/s",
        value=f"{height:.2f} m"
    )


# --------------------------------------------------
# MODEL ASSUMPTIONS
# --------------------------------------------------

with st.expander("About this model"):
    st.markdown(
        """
        - The calculations assume ideal projectile motion.
        - Air resistance and hoop rotation are ignored.
        - Peak height is measured above the hoop's release point,
          not above the floor.
        - The distance-angle relationship is based on the ideal
          projectile range equation.
        - The curves are theoretical estimates, not validated
          performance norms for a particular gymnast.
        """
    )
