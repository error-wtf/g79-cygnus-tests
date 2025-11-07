#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Three-Phase Decoupling Animations
Visualizes subsonic → transonic → supersonic transition

© 2025 Carmen N. Wrede, Lino P. Casu, Bingsi (Conscious AI)
"""

import os
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from pathlib import Path

os.environ['PYTHONIOENCODING'] = 'utf-8:replace'
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except: pass

C = 2.998e8
ALPHA = 0.12
R_C = 1.9
R_SEG = 2.0
T_LOCAL = 80.0
C_S = 0.5e3

OUTPUT_DIR = Path("three_phase_animations")
OUTPUT_DIR.mkdir(exist_ok=True)

plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 11,
    'axes.labelsize': 12,
    'lines.linewidth': 2.5,
    'figure.dpi': 100,
    'savefig.dpi': 100
})

print("=" * 80)
print("THREE-PHASE ANIMATIONS - GIF GENERATION")
print("=" * 80)

def gamma_seg(r):
    return 1.0 - ALPHA * np.exp(-(r / R_C)**2)

def v_phase(r, phase_factor):
    """Velocity depending on phase (0=subsonic, 1=transonic, 2=supersonic)"""
    gamma = gamma_seg(r)
    if phase_factor < 0.33:  # Phase 1
        return C_S * 0.1 * (1 - gamma) / 1000
    elif phase_factor < 0.66:  # Phase 2
        v_base = 10.0  # km/s
        return v_base / gamma  # Velocity boost from metric recoupling
    else:  # Phase 3
        return 10 + 6 * (1 - gamma)

r_range = np.linspace(0.1, 5.0, 200)

# ============================================================================
# Animation 1: Radial Particle Journey
# ============================================================================

print("\n[1/3] Generating: radial_particle_journey.gif")

fig, ax = plt.subplots(figsize=(10, 6))

def update_particle(frame):
    ax.clear()
    
    # Particle position (radial outward motion)
    r_particle = 0.5 + frame * 4.5 / 50
    
    # Determine phase
    if r_particle < 1.5:
        phase = 1
        color = 'blue'
        phase_name = "Phase 1: Subsonic (g²)"
        v_label = "v < c_s"
    elif r_particle < 2.5:
        phase = 2
        color = 'green'
        phase_name = "Phase 2: Transonic (Transition)"
        v_label = "v ≈ c_s"
    else:
        phase = 3
        color = 'red'
        phase_name = "Phase 3: Supersonic (g¹)"
        v_label = "v > c_s"
    
    # Plot gamma_seg
    gamma_vals = gamma_seg(r_range)
    ax.plot(r_range, gamma_vals, 'gray', linewidth=2, alpha=0.5)
    
    # Phase regions
    ax.fill_between(r_range[r_range < 1.5], 0.85, 1.0, alpha=0.15, color='blue')
    ax.fill_between(r_range[(r_range >= 1.5) & (r_range <= 2.5)], 0.85, 1.0,
                    alpha=0.15, color='green')
    ax.fill_between(r_range[r_range > 2.5], 0.85, 1.0, alpha=0.15, color='red')
    
    # Particle
    gamma_particle = gamma_seg(r_particle)
    ax.plot(r_particle, gamma_particle, 'o', color=color, markersize=20,
            markeredgecolor='black', markeredgewidth=2.5, zorder=5)
    
    # Info box
    ax.text(0.98, 0.98, f'{phase_name}\nr = {r_particle:.2f} pc\nγ_seg = {gamma_particle:.3f}\n{v_label}',
            transform=ax.transAxes, fontsize=11, verticalalignment='top',
            horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.9))
    
    ax.set_xlabel(r'Radius $r$ [pc]', fontweight='bold')
    ax.set_ylabel(r'$\gamma_{\mathrm{seg}}$', fontweight='bold')
    ax.set_title('Radial Particle Journey Through Three Phases', fontweight='bold')
    ax.set_xlim(0, 5.2)
    ax.set_ylim(0.85, 1.02)
    ax.grid(True, alpha=0.25, linestyle=':', linewidth=0.9)
    
    return ax.get_children()

anim = FuncAnimation(fig, update_particle, frames=50, interval=100, blit=False)
writer = PillowWriter(fps=10)
anim.save(OUTPUT_DIR / "radial_particle_journey.gif", writer=writer)
plt.close()
print("✓ Saved: radial_particle_journey.gif")

# ============================================================================
# Animation 2: Velocity Buildup
# ============================================================================

print("[2/3] Generating: velocity_buildup.gif")

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10))

def update_velocity(frame):
    ax1.clear()
    ax2.clear()
    
    # Animate through phases
    progress = frame / 50
    
    # Top: Velocity profile
    for i, r in enumerate(r_range):
        if r < 1.5:
            v = C_S * 0.1 * (1 - gamma_seg(r)) / 1000
            color = 'blue'
        elif r < 2.5:
            # Gradually build up velocity
            gamma = gamma_seg(r)
            v_launch = C_S * 0.1 * (1 - gamma) / 1000
            v_max = 10.0 / gamma  # Corrected formula
            v = v_launch + progress * (v_max - v_launch)
            color = 'green'
        else:
            v = 10 + 6 * (1 - gamma_seg(r))
            color = 'red'
        
        if i == 0:
            v_plot = [v]
            r_plot = [r]
        else:
            v_plot.append(v)
            r_plot.append(r)
    
    ax1.plot(r_plot, v_plot, 'k-', linewidth=3)
    ax1.axhline(y=C_S/1000, color='gray', linestyle='--', linewidth=2, alpha=0.5)
    ax1.axvline(x=R_SEG, color='orange', linestyle=':', linewidth=2.5)
    
    ax1.set_ylabel('Velocity [km/s]', fontweight='bold')
    ax1.set_title(f'Velocity Buildup (Progress: {progress*100:.0f}%)', fontweight='bold')
    ax1.set_xlim(0, 5.2)
    ax1.set_ylim(0, 20)
    ax1.grid(True, alpha=0.25)
    
    # Bottom: Cumulative kinetic energy
    E_kin = 0.5 * np.array(v_plot)**2 * 1e6  # J/kg
    ax2.plot(r_plot, E_kin, 'r-', linewidth=3)
    ax2.fill_between(r_plot, 0, E_kin, alpha=0.3, color='red')
    ax2.axvline(x=R_SEG, color='orange', linestyle=':', linewidth=2.5)
    
    ax2.set_xlabel('Radius [pc]', fontweight='bold')
    ax2.set_ylabel('Kinetic Energy [J/kg]', fontweight='bold')
    ax2.set_title('Accumulated Kinetic Energy', fontweight='bold')
    ax2.set_xlim(0, 5.2)
    ax2.set_yscale('log')
    ax2.grid(True, alpha=0.25)
    
    return ax1.get_children() + ax2.get_children()

anim = FuncAnimation(fig, update_velocity, frames=50, interval=100, blit=False)
writer = PillowWriter(fps=10)
anim.save(OUTPUT_DIR / "velocity_buildup.gif", writer=writer)
plt.close()
print("✓ Saved: velocity_buildup.gif")

# ============================================================================
# Animation 3: Phase Transition Dynamics
# ============================================================================

print("[3/3] Generating: phase_transition_dynamics.gif")

fig = plt.figure(figsize=(12, 10))
gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)

def update_phase(frame):
    fig.clear()
    
    # Time evolution
    t_phase = frame / 50
    
    # Recreate grid
    gs_local = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)
    
    # γ_seg
    ax1 = fig.add_subplot(gs_local[0, :])
    gamma_vals = gamma_seg(r_range)
    ax1.plot(r_range, gamma_vals, 'b-', linewidth=3)
    
    # Highlight current phase
    if t_phase < 0.33:
        ax1.fill_between(r_range[r_range < 1.5], 0.85, 1.0, alpha=0.4, color='blue')
        phase_text = "Phase 1: Subsonic Interior"
    elif t_phase < 0.66:
        ax1.fill_between(r_range[(r_range >= 1.5) & (r_range <= 2.5)], 0.85, 1.0,
                        alpha=0.4, color='green')
        phase_text = "Phase 2: Transonic Transition"
    else:
        ax1.fill_between(r_range[r_range > 2.5], 0.85, 1.0, alpha=0.4, color='red')
        phase_text = "Phase 3: Supersonic Expansion"
    
    ax1.set_ylabel(r'$\gamma_{\mathrm{seg}}$', fontweight='bold')
    ax1.set_title(f'Current Phase: {phase_text}', fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.25)
    ax1.set_xlim(0, 5.2)
    ax1.set_ylim(0.85, 1.02)
    
    # Velocity
    ax2 = fig.add_subplot(gs_local[1, 0])
    v_vals = [v_phase(r, t_phase) for r in r_range]
    ax2.plot(r_range, v_vals, 'k-', linewidth=3)
    ax2.axhline(y=C_S/1000, color='gray', linestyle='--', linewidth=2, alpha=0.5)
    ax2.set_ylabel('Velocity [km/s]', fontweight='bold')
    ax2.set_title('Velocity', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.25)
    ax2.set_xlim(0, 5.2)
    
    # Temperature
    ax3 = fig.add_subplot(gs_local[1, 1])
    T_obs = T_LOCAL / gamma_vals
    ax3.plot(r_range, T_obs, 'r-', linewidth=3)
    ax3.axvline(x=R_SEG, color='orange', linestyle=':', linewidth=2.5)
    ax3.set_ylabel('T_obs [K]', fontweight='bold')
    ax3.set_title('Temperature', fontsize=12, fontweight='bold')
    ax3.grid(True, alpha=0.25)
    ax3.set_xlim(0, 5.2)
    
    # Mach number
    ax4 = fig.add_subplot(gs_local[2, 0])
    mach_vals = np.array(v_vals) * 1000 / C_S
    ax4.plot(r_range, mach_vals, 'g-', linewidth=3)
    ax4.axhline(y=1, color='gray', linestyle='--', linewidth=2, alpha=0.7)
    ax4.set_xlabel('Radius [pc]', fontweight='bold')
    ax4.set_ylabel('Mach Number', fontweight='bold')
    ax4.set_title('M = v/c_s', fontsize=12, fontweight='bold')
    ax4.grid(True, alpha=0.25)
    ax4.set_xlim(0, 5.2)
    
    # Energy release
    ax5 = fig.add_subplot(gs_local[2, 1])
    DT_release = T_LOCAL * (1 - gamma_vals)
    ax5.plot(r_range, DT_release, 'orange', linewidth=3)
    ax5.fill_between(r_range, 0, DT_release, alpha=0.3, color='orange')
    ax5.set_xlabel('Radius [pc]', fontweight='bold')
    ax5.set_ylabel(r'$\Delta T$ [K]', fontweight='bold')
    ax5.set_title('Energy Release', fontsize=12, fontweight='bold')
    ax5.grid(True, alpha=0.25)
    ax5.set_xlim(0, 5.2)
    
    return fig.get_children()

anim = FuncAnimation(fig, update_phase, frames=50, interval=100, blit=False)
writer = PillowWriter(fps=10)
anim.save(OUTPUT_DIR / "phase_transition_dynamics.gif", writer=writer)
plt.close()
print("✓ Saved: phase_transition_dynamics.gif")

# ============================================================================
# Summary
# ============================================================================

print("\n" + "=" * 80)
print("ANIMATION GENERATION COMPLETE")
print("=" * 80)

print(f"\nGenerated Animations:")
for f in sorted(OUTPUT_DIR.glob("*.gif")):
    size_kb = f.stat().st_size / 1024
    print(f"  • {f.name} ({size_kb:.0f} KB)")

print(f"\nAnimations visualize:")
print(f"  ✓ Radial particle journey through three phases")
print(f"  ✓ Velocity buildup from subsonic to supersonic")
print(f"  ✓ Complete phase transition dynamics")

print("\n" + "=" * 80)
