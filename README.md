# 🌌 Kerr Lab: Interactive Black Hole Simulator

> *"The only thing that can cross the horizon is gravity."*

**Kerr Lab** is a real-time Python visualization of the spacetime geometry around a rotating (Kerr) Black Hole. Designed for students, enthusiasts, and anyone who wants to touch the fabric of the universe without needing a PhD in General Relativity.

![Black Hole Simulation](https://i.imgur.com/PlaceholderForGif.gif) *(Replace with your screenshot)*

## ✨ Key Features

*   **Real-time Interaction:**
    *   **Spin Slider (a):** Watch how the Event Horizon shrinks and the "Frame Dragging" effect intensifies as you spin the hole up to `0.99c`.
    *   **Mass Slider (M):** Control the gravitational depth of the singularity.
*   **Newtonian vs GR Mode (New!):** Press `N` to toggle between Einstein's General Relativity (twisted space, black horizon) and Newton's Physics (rigid space, grey mass).
*   **Accretion Disk Physics:** Particles follow Keplerian-like orbits, color-coded by temperature (Doppler/Thermodynamic approximation).
*   **Dynamic Spacetime Grid:** Visualize the "Frame Dragging" (Lense-Thirring effect) as a twisting neon grid that flows into the abyss.
*   **The Ring Singularity:** See the theoretical ring structure inside the horizon where physics breaks down.
*   **Educational HUD:** Press `E` to cycle through explanations of the physics equations (Horizon Geometry, Time Dilation, Frame Dragging).

## 🚀 Quick Start

### 1. Requirements
You need Python 3.x and the standard scientific stack.

```bash
pip install numpy matplotlib
```

### 2. Launch
Run the laboratory script:

```bash
python3 kerr_lab_v2.py
```

## 🎮 Controls

| Key / Mouse | Action |
| :--- | :--- |
| **Space** | Pause/Resume Time (Freeze the Universe) |
| **E** | Toggle Educational HUD (Equations & Info) |
| **N** | Toggle Newtonian/Relativistic Physics Mode |
| **Mouse Drag** | Rotate Camera (Explore 3D angles) |
| **Sliders** | Adjust Spin (a) and Mass (M) at bottom of screen |

## 🧠 The Physics Behind It

This simulation visualizes the **Kerr Metric**, an exact solution to the Einstein Field Equations for a rotating mass.

1.  **Event Horizon ($r_+$):** The spherical void from which light cannot escape. Unlike a static hole ($R_s = 2M$), a rotating hole's horizon depends on its spin: $r_+ = M + \sqrt{M^2 - a^2}$.
2.  **Frame Dragging:** The region outside the horizon where spacetime is dragged faster than light. In our simulation, the grid twists to visualize this $d\phi$ drift.
3.  **Singularity:** Unlike static black holes (points), a rotating singularity is a **Ring** of zero thickness and infinite density.

## ⚠️ Performance Note
This simulation performs heavy trigonometric calculations for 800+ particles and grid vertices in real-time on the CPU.
*   **Recommended:** Ryzen 7 / Core i7 or better.

---
*Created for educational purposes. Code is open and free.*