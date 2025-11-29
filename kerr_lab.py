import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.widgets import Slider, Button

# ==============================================================================
# CHIMERA: KERR LAB v2.0 (FINAL POLISH - FIXED)
# Refactored based on peer review.
# Features: Accurate Kerr Physics HUD, Newtonian Toggle, Parametric Control.
# ==============================================================================

class KerrLabFinal:
    """
    Interactive visualization of a Kerr (Rotating) Black Hole.
    
    Simulates:
    1. Accretion Disk particles (Keplerian-like orbits).
    2. Frame Dragging (Lense-Thirring effect) via twisted spacetime grid.
    3. Event Horizon geometry based on Spin (a) and Mass (M).
    4. Ring Singularity visualization.
    
    Controls:
    - Sliders: Mass (M), Spin (a)
    - Keys: Space (Pause), E (Education HUD), N (Newtonian Toggle)
    """

    def __init__(self):
        self.paused = False
        self.newtonian_mode = False # If True, disables Frame Dragging logic
        self.info_mode = 0          # 0=Dash, 1=Horizon, 2=Time, 3=Drag, 4=Singularity
        
        # --- SIMULATION PARAMETERS (No Magic Numbers) ---
        self.M = 1.0
        self.a = 0.90
        self.n_particles = 800
        
        # Tuning
        self.speed_mult = 0.15      # Orbital speed multiplier
        self.drag_strength = 0.5    # How much space twists
        self.drag_power = 2.0       # Falloff power of dragging (1/r^2 approx)
        
        # --- UI SETUP ---
        self.fig = plt.figure(figsize=(14, 10))
        self.fig.patch.set_facecolor('#0d0d0d')
        self.fig.subplots_adjust(bottom=0.25)
        
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.ax.set_facecolor('black')
        
        # --- INITIALIZATION ---
        self.init_particles()
        self.init_grid()
        self.wframe = None
        self.horizon_surf = None
        self.text_objects = []
        
        self.setup_ui()
        self.update_geometry()
        self.update_hud()
        
        # --- CAMERA & AXES ---
        self.ax.set_axis_off()
        self.ax.set_title("KERR LAB v2.0: GENERAL RELATIVITY", color='white', fontsize=14, pad=20)
        
        limit = 6.5
        self.ax.set_xlim(-limit, limit)
        self.ax.set_ylim(-limit, limit)
        self.ax.set_zlim(-8, 5)
        
        self.fig.canvas.mpl_connect('key_press_event', self.on_key)

    def init_particles(self):
        r_inner = 1.5
        r_outer = 6.0
        self.p_r = np.random.uniform(r_inner, r_outer, self.n_particles)
        self.p_phi = np.random.uniform(0, 2*np.pi, self.n_particles)
        self.p_z = np.random.normal(0, 0.04, self.n_particles)
        
        # Pre-calc colors
        norm_r = (self.p_r - r_inner) / (r_outer - r_inner)
        self.colors = plt.cm.plasma(1 - norm_r) 
        
        self.scat = self.ax.scatter(
            self.p_r * np.cos(self.p_phi), 
            self.p_r * np.sin(self.p_phi), 
            self.p_z, 
            c=self.colors, s=2.0, alpha=0.8, marker='o'
        )

    def init_grid(self):
        # Reduced resolution for performance
        self.grid_r = np.linspace(1.1, 9, 15)
        self.grid_phi = np.linspace(0, 2*np.pi, 25)
        self.R, self.P = np.meshgrid(self.grid_r, self.grid_phi)

    def setup_ui(self):
        axcolor = '#222222'
        text_color = 'white'

        # Spin Slider
        ax_spin = plt.axes([0.25, 0.1, 0.5, 0.03], facecolor=axcolor)
        self.s_spin = Slider(ax_spin, 'Spin (a)', 0.0, 0.99, valinit=self.a, valstep=0.01, color='cyan')
        self.s_spin.label.set_color(text_color)
        self.s_spin.valtext.set_color(text_color)
        self.s_spin.on_changed(self.update_params)

        # Mass Slider
        ax_mass = plt.axes([0.25, 0.05, 0.5, 0.03], facecolor=axcolor)
        self.s_mass = Slider(ax_mass, 'Mass (M)', 0.5, 2.0, valinit=self.M, valstep=0.1, color='orange')
        self.s_mass.label.set_color(text_color)
        self.s_mass.valtext.set_color(text_color)
        self.s_mass.on_changed(self.update_params)

        # Controls Text
        plt.figtext(0.02, 0.02, "[Space] Pause | [E] Info | [N] Toggle Newtonian Mode", color='gray', fontsize=9)

    def update_params(self, val):
        self.a = self.s_spin.val
        self.M = self.s_mass.val
        self.update_geometry()
        # Always update HUD to refresh the "Spin a=... | Mass M=..." dashboard text
        self.update_hud()

    def update_geometry(self):
        if self.horizon_surf: self.horizon_surf.remove()
        
        # Horizon Logic
        theta = np.linspace(0, np.pi, 25)
        phi = np.linspace(0, 2 * np.pi, 25)
        THETA, PHI = np.meshgrid(theta, phi)
        
        # Kerr Horizon Formula: r+ = M + sqrt(M^2 - a^2)
        try:
            r_plus = self.M + np.sqrt(self.M**2 - self.a**2)
        except ValueError:
            r_plus = self.M # Fallback if a > M (Naked singularity), unlikely with slider limits
            
        X = r_plus * np.sin(THETA) * np.cos(PHI)
        Y = r_plus * np.sin(THETA) * np.sin(PHI)
        Z = r_plus * np.cos(THETA)
        
        # Color based on mode
        color = 'gray' if self.newtonian_mode else 'black'
        alpha = 0.5 if self.newtonian_mode else 0.95
        
        self.horizon_surf = self.ax.plot_surface(X, Y, Z, color=color, alpha=alpha, shade=False, zorder=10)

    def update_hud(self):
        for txt in self.text_objects: txt.remove()
        self.text_objects = []
        
        # Global Dashboard
        mode_str = "NEWTONIAN (CLASSIC)" if self.newtonian_mode else "RELATIVISTIC (KERR)"
        color_str = "red" if self.newtonian_mode else "cyan"
        
        t_dash = self.ax.text2D(0.02, 0.92, f"MODE: {mode_str}\nSpin a={self.a:.2f} | Mass M={self.M:.1f}", 
                                transform=self.ax.transAxes, color=color_str, fontsize=9)
        self.text_objects.append(t_dash)

        if self.info_mode == 1:
            # HORIZON PHYSICS
            t_head = self.ax.text2D(0.05, 0.85, "1. EVENT HORIZON GEOMETRY", color='cyan', transform=self.ax.transAxes, fontsize=12, weight='bold')
            # Kerr Formula
            t_form = self.ax.text2D(0.05, 0.78, r"Kerr: $r_+ = M + \sqrt{M^2 - a^2}$", transform=self.ax.transAxes, color='white', fontsize=14)
            # Schwarzschild Comparison
            t_sub = self.ax.text2D(0.05, 0.73, r"(Non-rotating $a=0 \rightarrow R_s = 2M$)", transform=self.ax.transAxes, color='gray', fontsize=10)
            self.text_objects.extend([t_head, t_form, t_sub])

        elif self.info_mode == 2:
            # TIME DILATION
            t_head = self.ax.text2D(0.05, 0.85, "2. TIME DILATION", color='orange', transform=self.ax.transAxes, fontsize=12, weight='bold')
            t_text = self.ax.text2D(0.05, 0.78, "To a distant observer, time stops at the horizon.", transform=self.ax.transAxes, color='white')
            t_desc = self.ax.text2D(0.05, 0.73, r"As $r \rightarrow r_+$, redshift $\rightarrow \infty$. You fade out, frozen forever.", transform=self.ax.transAxes, color='yellow', fontsize=10)
            self.text_objects.extend([t_head, t_text, t_desc])
            
        elif self.info_mode == 3:
            # FRAME DRAGGING
            t_head = self.ax.text2D(0.05, 0.85, "3. FRAME DRAGGING (Lense-Thirring)", color='#9900ff', transform=self.ax.transAxes, fontsize=12, weight='bold')
            if self.newtonian_mode:
                t_warn = self.ax.text2D(0.05, 0.78, "[DISABLED IN NEWTONIAN MODE]", transform=self.ax.transAxes, color='red', weight='bold')
                self.text_objects.extend([t_head, t_warn])
            else:
                t_form = self.ax.text2D(0.05, 0.78, r"$d\phi \rightarrow d\phi - \omega(r) dt$", transform=self.ax.transAxes, color='white', fontsize=14)
                t_desc = self.ax.text2D(0.05, 0.73, "Spacetime twists with the spin.\nOrbits are forced to corotate.", transform=self.ax.transAxes, color='cyan', fontsize=10)
                self.text_objects.extend([t_head, t_form, t_desc])

    def update(self, frame):
        if self.paused:
            return self.scat,
        
        # 1. Update Particles
        omega = (1.5 * self.M) * (self.p_r ** (-1.5))
        self.p_phi += omega * self.speed_mult
        
        x = self.p_r * np.cos(self.p_phi)
        y = self.p_r * np.sin(self.p_phi)
        self.scat._offsets3d = (x, y, self.p_z)
        
        # 2. Update Grid
        if self.wframe:
            self.wframe.remove()
        
        if not self.newtonian_mode:
            # GR MODE
            drag_factor = (self.a * self.drag_strength) / (self.R ** self.drag_power)
            self.P += drag_factor
            
            Z_grid = -7 + (-3.0 * self.M / self.R)
            color_grid = '#00ffff' 
        else:
            # NEWTONIAN MODE
            Z_grid = -7 + (-1.0 / self.R)
            color_grid = '#444444' 
        
        X_grid = self.R * np.cos(self.P)
        Y_grid = self.R * np.sin(self.P)
        
        self.wframe = self.ax.plot_wireframe(X_grid, Y_grid, Z_grid, color=color_grid, alpha=0.3, linewidth=0.6)
        
        return self.scat,

    def on_key(self, event):
        if event.key == ' ':
            self.paused = not self.paused
        elif event.key == 'e' or event.key == 'E':
            self.info_mode = (self.info_mode + 1) % 4
            self.update_hud()
            self.fig.canvas.draw_idle()
        elif event.key == 'n' or event.key == 'N':
            self.newtonian_mode = not self.newtonian_mode
            self.update_geometry() 
            self.update_hud()      
            self.fig.canvas.draw_idle()

    def start(self):
        print("[+] KERR LAB v2.0 READY.")
        anim = animation.FuncAnimation(self.fig, self.update, interval=30, blit=False)
        plt.show()

if __name__ == "__main__":
    sim = KerrLabFinal()
    sim.start()