# lattice Boltzmann wind tunnel simulation in Python


# Slider buttons, ui elements
from matplotlib.widgets import Slider, Button, RadioButtons
# Inset axes for the colorbar
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
# Numerical and plotting libraries
import numpy as np
# matplotlib for plotting and animation
import matplotlib.pyplot as plt
# Animation class for creating the simulation animation
from matplotlib.animation import FuncAnimation

nx, ny = 360, 120 #Size of the simulation grid
u0 = 0.1 #More velocity of the wind
tau = 0.75 #Viscosity of the fluid (lower values = more viscous)
steps_per_frame = 40 # Number of calculations per step of the animation


# Velocity directions for the D2Q9 Lattice Boltzmann model.
cx = np.array([0, 1, 0, -1, 0, 1, -1, -1, 1])
cy = np.array([0, 0, 1, 0, -1, 1, 1, -1, -1])
# Lattice weights for the D2Q9 model.(Distribution of particles in each direction)
w = np.array([4/9] + [1/9]*4 + [1/36]*4)
# Opposite directions for the D2Q9 model (used for bounce-back boundary conditions).
opp = [0, 3, 4, 1, 2, 7, 8, 5, 6]



#Equilibrium distribution function for the D2Q9 Lattice Boltzmann model.(find the prefferd state of the fluid/particles)
def equilibrium(rho, ux, uy):
    feq = np.empty((9,) + rho.shape)
    usq = ux**2 + uy**2
#calculate the equilibrium distribution function for each direction based on the local density and velocity.
    for i in range(9):
        cu = cx[i]*ux + cy[i]*uy
        feq[i] = w[i]*rho*(
            1 + 3*cu + 4.5*cu**2 - 1.5*usq
        )

    return feq

# Create the simulation grid and define the solid boundaries (walls and obstacle).
X, Y = np.meshgrid(
    np.arange(nx), np.arange(ny), indexing="ij"
)
#OBJECTS
# Define the solid boundaries (walls and obstacle) in the simulation grid.
def build_solid(name):
  """Return a True/False mask of solid cells for the chosen shape"""
  mask = np.zeros((nx, ny), dtype=bool)
  mask[:, 0] = True  # Left wall
  mask[:, -1] = True  # Right wall
  ox,oy = nx//4, ny//2  # Center of the obstacle

  if name == "Circle":
      radius = ny//4
      mask[(X - ox)**2 + (Y - oy)**2 < radius**2] = True
  elif name == "Square":
      size = ny//4
      mask[ox-size//2:ox+size//2, oy-size//2:oy+size//2] = True
  elif name == "Right angle\ntriangle":
      size = ny//4
      for i in range(size):
          mask[ox-size//2+i, oy-size//2:oy-size//2+i+1] = True
          #Wing shape based on NACA 0015 airfoil profile
  elif name == "Cambered wing":
        chord = 80                 # length of the wing in cells
        thickness = 0.15           # 15% of the chord (NACA 0015)
        aoa = np.radians(10)       # angle of attack in degrees

        dx, dy = X - ox, Y - oy
        xr = dx*np.cos(aoa) - dy*np.sin(aoa)    # position along the wing
        yr = dx*np.sin(aoa) + dy*np.cos(aoa)    # position across the wing

        s = xr/chord + 0.25                     # 0 = nose, 1 = tail
        t = np.clip(s, 0, 1)
        half = 5*thickness*chord*(0.2969*np.sqrt(t) - 0.1260*t
                                  - 0.3516*t**2 + 0.2843*t**3 - 0.1015*t**4)

        mask |= (s >= 0) & (s <= 1) & (np.abs(yr) <= half)

  elif name == "Supercritical wing":
        chord = 90                      # length in cells
        aoa = np.radians(3)             # angle of attack (nose up)

        # Position along the wing (0 = nose, 1 = tail) and the height of the
        # top and bottom surface at that position, as a fraction of the chord.
        px     = np.array([0, 0.005, 0.0125, 0.025, 0.05, 0.1, 0.2, 0.3,
                           0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 1.0])
        top    = np.array([0, 0.0150, 0.0230, 0.0310, 0.0420, 0.0540, 0.0650,
                           0.0700, 0.0715, 0.0710, 0.0690, 0.0640, 0.0550,
                           0.0370, 0.0230, 0.0040])
        bottom = np.array([0, -0.0150, -0.0220, -0.0290, -0.0380, -0.0480,
                           -0.0560, -0.0590, -0.0590, -0.0550, -0.0480,
                           -0.0420, -0.0370, -0.0260, -0.0150, -0.0010])

        dx, dy = X - ox, Y - oy
        xr = dx*np.cos(aoa) - dy*np.sin(aoa)    # position along the wing
        yr = dx*np.sin(aoa) + dy*np.cos(aoa)    # position across the wing

        s = xr/chord + 0.25                     # 0 = nose, 1 = tail
        t = np.clip(s, 0, 1)
        y_top = np.interp(t, px, top)*chord     # top surface height in cells
        y_bot = np.interp(t, px, bottom)*chord  # bottom surface height in cells

        mask |= (s >= 0) & (s <= 1) & (yr <= y_top) & (yr >= y_bot)
  
  return mask

solid = build_solid("Circle")  # Change the shape here: "Circle", "Square", "Right angle\ntriangle", "Cambered wing", "Supercritical wing"


# define the particle distribution function f, initialized to the equilibrium state with uniform density and velocity.
f = equilibrium(
    np.ones((nx, ny)).astype(np.float32),
    np.full((nx, ny), u0).astype(np.float32),
    np.zeros((nx, ny)).astype(np.float32)
)

# Get the macroscopic fields (density, velocity, pressure) from the particle distribution function.
def get_fields():
    rho = f.sum(axis=0)

    # Avoid division by zero in case of numerical instability.
    safe_rho = np.maximum(rho, 1e-12)
    # Compute the macroscopic velocity components by taking the weighted sum of the particle distributions in each direction, normalized by the local density.
    ux = (f * cx[:, None, None]).sum(axis=0) / safe_rho
    uy = (f * cy[:, None, None]).sum(axis=0) / safe_rho

    velocity = np.sqrt(ux**2 + uy**2)

    # Isothermal LBM pressure, in lattice units.
    pressure = rho / 3.0

    return rho, ux, uy, velocity, pressure

# Perform a single time step of the Lattice Boltzmann simulation, including collision, streaming, and boundary conditions.
def step():
    global f

    rho, ux, uy, _, _ = get_fields()

    f = f - (
        f - equilibrium(rho, ux, uy)
    ) / tau

    # Bounce-back boundary condition at solid surfaces.
    f[:, solid] = f[opp][:, solid]

    # Stream the particle distributions.
    for i in range(9):
        f[i] = np.roll(
            np.roll(f[i], cx[i], axis=0),
            cy[i],
            axis=1
        )

    # Inlet boundary.
    inlet_rho = np.ones((1, ny)).astype(np.float32)
    inlet_ux = np.full((1, ny), u0).astype(np.float32)
    inlet_uy = np.zeros((1, ny)).astype(np.float32)

    f[:, 0, :] = equilibrium(
        inlet_rho, inlet_ux, inlet_uy
    )[:, 0, :]

    # Outlet boundary.
    f[:, -1, :] = f[:, -2, :]

# Compute the speed (magnitude of the velocity) and mask out the solid regions for visualization.
def speed():
    _, _, _, velocity, _ = get_fields()
    return np.ma.masked_where(solid, velocity)


# Aspect ratio for the plot.
fig, ax = plt.subplots(figsize=(10, 4.2))
fig.patch.set_facecolor("#B6B5B5")  # Window background
ax.set_facecolor("#000000")         # Plot background

# Display the velocity magnitude as a heatmap.
im = ax.imshow(
    speed().T,
    origin="lower",
    cmap="turbo",
    vmin=0,
    vmax=0.25,
    extent=(-0.5, nx - 0.5, -0.5, ny - 0.5),
    aspect="equal"

)
ax.tick_params(axis="both", labelsize=16)
ax.set_xlabel("X position (lattice cells)", fontsize=18)
ax.set_ylabel("Y position (lattice cells)", fontsize=18)

#Colorbar for the velocity magnitude._____________________________________________________________________________________________
# Horizontal colorbar in the bottom-right corner of the window background.
# [left, bottom, width, height] as fractions of the whole window.
cax = fig.add_axes([0.55, 0.07, 0.40, 0.04])
cbar = fig.colorbar(im, cax=cax, orientation="horizontal")
cbar.set_label("Velocity magnitude (lattice units)", color="black", fontsize=25)
cbar.ax.xaxis.set_label_position("top")
cbar.ax.tick_params(colors="black", labelsize=20)
cbar.outline.set_edgecolor("black")


# Info box for displaying the selected point's data.__________________________________________________________________________
info = ax.text(
    0.02, 0.98,
    "Click inside the wind tunnel to measure",
    transform=fig.transFigure,
    va="top",
    ha="left",
    color="white",
    fontsize=25,
    bbox=dict(facecolor="#3660ad",alpha=0.8,pad=10)
)

# Title for the simulation window.
title = ax.text(
    0.5, 0.95,
    "Wind Tunnel Simulation",
    transform=fig.transFigure,
    va="top",
    ha="center",
    color="white",
    fontsize= 80,
    bbox=dict(facecolor="#3660ad",alpha=0.8,pad=10)
)

# Marker showing the selected measurement point
marker, = ax.plot(
    [], [],
    "wo",
    markersize=10,
    markeredgecolor="black"
)


# The point the user clicked (None until the first click).
selected = {"pos": None}

# Update the info box with the current values at the selected point.
def refresh_info():
    """Rewrite the info box with the current values at the selected point."""
    if selected["pos"] is None:
        return

    x, y = selected["pos"]

    if solid[x, y]:
        info.set_text(f"Position: ({x}, {y})\nSolid obstacle")
        return

    rho, ux, uy, velocity, pressure = get_fields()

    info.set_text(
        f"Position: ({x}, {y})\n"
        f"Velocity X: {ux[x, y]:.6f}\n"
        f"Velocity Y: {uy[x, y]:.6f}\n"
        f"Speed:      {velocity[x, y]:.6f}\n"
        f"Density:    {rho[x, y]:.6f}\n"
        f"Pressure:   {pressure[x, y]:.6f}\n"
        f"(lattice units)"
    )

# Handle mouse clicks to select a point in the simulation and update the info box.
def on_click(event):
    # Ignore clicks outside the simulation axes.
    if event.inaxes != ax:
        return

    if event.xdata is None or event.ydata is None:
        return
# Convert the click coordinates to integer grid indices, rounding to the nearest integer.
    x = int(round(event.xdata))
    y = int(round(event.ydata))

    if not (0 <= x < nx and 0 <= y < ny):
        return

    selected["pos"] = (x, y)      # remember the point
    marker.set_data([x], [y])
    refresh_info()
    fig.canvas.draw_idle()


# Connect the mouse-click event.
fig.canvas.mpl_connect("button_press_event", on_click)

# Animation update function
def update(_):
    for _ in range(steps_per_frame):
        step()

    if not np.isfinite(f).all():   # simulation blew up
        reset_flow()

    im.set_data(speed().T)
    refresh_info()                 # keep the box in sync with the flow
    return (im,)


    
# Create the animation
anim = FuncAnimation(
    fig,
    update,
    interval=30,
    blit=False,
    cache_frame_data=False
)

# Sliders for adjusting wind speed, viscosity, and steps per frame._____________________________________________________
def reset_flow():
    """Restart the fluid if the simulation ever blows up."""
    global f
    f = equilibrium(
        np.ones((nx, ny)).astype(np.float32),
        np.full((nx, ny), u0).astype(np.float32),
        np.zeros((nx, ny)).astype(np.float32)
        )

# [left, bottom, width, height] as fractions of the window
ax_speed = fig.add_axes([0.10, 0.14, 0.18, 0.02])
ax_visc  = fig.add_axes([0.10, 0.09, 0.18, 0.02])
ax_steps = fig.add_axes([0.10, 0.04, 0.18, 0.02])

s_speed = Slider(ax_speed, "Wind speed", 0.02, 0.2, valinit=u0, valfmt="%.3f")
s_visc  = Slider(ax_visc, "Viscosity", 0.01, 0.15,
                 valinit=(tau - 0.5)/3, valfmt="%.3f")
s_steps = Slider(ax_steps, "Calculations \n per frame", 1, 60,
                 valinit=steps_per_frame, valstep=1, valfmt="%d")


for s in (s_speed, s_visc, s_steps):
    s.label.set_fontsize(20)
    s.valtext.set_fontsize(20)
    s.label.set_color("black")
    s.valtext.set_color("black")

def on_speed(val):
    global u0
    u0 = val
# when the wind speed slider is changed, update the global variable u0 with the new value.
def on_visc(val):
    global tau
    tau = 3*val + 0.5         # viscosity

def on_steps(val):
    global steps_per_frame
    steps_per_frame = int(val)

s_speed.on_changed(on_speed)
s_visc.on_changed(on_visc)
s_steps.on_changed(on_steps)


# Dropdown menu for selecting the obstacle shape.__________________________________________________________________________
Objects = ["Circle", "Square", "Right angle\ntriangle", "Cambered wing", "Supercritical wing","None"]
# [left, bottom, width, height] as fractions of the window
ax_btn  = fig.add_axes([0.76, 0.92, 0.22, 0.04])
btn = Button(ax_btn, "Shape: Cylinder  \u25BC")
btn.label.set_fontsize(20)

ax_menu = fig.add_axes([0.76, 0.615, 0.22, 0.30])
ax_menu.set_zorder(10)                 # draw on top of the simulation
            # hidden until the button is clicked
ax_menu.set_visible(False)             # hidden until the button is clicked
radio = RadioButtons(ax_menu, Objects, active=0)
for lbl in radio.labels:
    lbl.set_fontsize(20)



def set_menu_visible(show):
    """Show or hide the whole menu: the box, the dots and the text."""
    ax_menu.set_visible(show)
    for part in ax_menu.get_children():
        part.set_visible(show)
    fig.canvas.draw_idle()

set_menu_visible(False)                # start with the menu closed

def toggle_menu(event):
    set_menu_visible(not ax_menu.get_visible())

def on_choice(label):
    global solid
    solid = build_solid(label)
    btn.label.set_text(f"Shape: {label}  \u25BC")
    set_menu_visible(False)            # close the menu after choosing
    reset_flow()                       # restart so the old shape leaves no trace

btn.on_clicked(toggle_menu)
radio.on_clicked(on_choice)


plt.get_current_fig_manager().full_screen_toggle()
plt.show()