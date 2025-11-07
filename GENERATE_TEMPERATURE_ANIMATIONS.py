#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Temperature Equation Animations - Complete GIF Suite
Segmented Spacetime Framework

Generates animated visualizations for all temperature equations:
- Eq. (9):  T(r) = T₀ γ_seg(r) - Radial evolution
- Eq. (15): Dual-frame temperature transformation
- Eq. (16): Energy density Stefan-Boltzmann relations
- Eq. (18): Recoupling energy release

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

# UTF-8 handling
os.environ['PYTHONIOENCODING'] = 'utf-8:replace'
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except: pass

# Physical constants
ALPHA = 0.12
ALPHA_ERR = 0.03
R_C = 1.9  # pc
T_0 = 240.0  # K
T_LOCAL = 80.0  # K

SHELL_R = np.array([1.2, 2.3, 4.5])
SHELL_T = np.array([500, 200, 60])

OUTPUT_DIR = Path("temperature_animations")
OUTPUT_DIR.mkdir(exist_ok=True)

plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 11,
    'axes.labelsize': 12,
    'axes.titlesize': 13,
    'lines.linewidth': 2.5,
    'figure.dpi': 100,
    'savefig.dpi': 100
})

def gamma_seg(r, alpha=ALPHA, r_c=R_C):
    return 1.0 - alpha * np.exp(-(r / r_c)**2)

print("=" * 80)
print("TEMPERATURE ANIMATIONS - GIF GENERATION")
print("=" * 80)

# ============================================================================
# Animation 1: Temporal Density Evolution
# ============================================================================

print("\n[1/5] Generating: temporal_density_evolution.gif")

fig, ax = plt.subplots(figsize=(10, 6))
r_range = np.linspace(0, 5.0, 200)

def update_gamma(frame):
    ax.clear()
    
    # Animate alpha parameter
    alpha_current = ALPHA * (0.5 + 0.5 * np.sin(frame * 2 * np.pi / 50))
    gamma_vals = gamma_seg(r_range, alpha=alpha_current, r_c=R_C)
    
    ax.plot(r_range, gamma_vals, 'b-', linewidth=3)
    ax.axhline(y=1, color='gray', linestyle='--', linewidth=2, alpha=0.5)
    ax.fill_between(r_range, gamma_vals, 1, alpha=0.3, color='blue')
    
    ax.set_xlabel(r'Radius $r$ [pc]', fontweight='bold')
    ax.set_ylabel(r'$\gamma_{\mathrm{seg}}(r)$', fontweight='bold')
    ax.set_title(f'Temporal Density Evolution (α={alpha_current:.3f})', fontweight='bold')
    ax.set_xlim(0, 5.2)
    ax.set_ylim(0.85, 1.02)
    ax.grid(True, alpha=0.25, linestyle=':', linewidth=0.9)
    
    return ax.get_children()

anim = FuncAnimation(fig, update_gamma, frames=50, interval=100, blit=False)
writer = PillowWriter(fps=10)
anim.save(OUTPUT_DIR / "temporal_density_evolution.gif", writer=writer)
plt.close()
print("✓ Saved: temporal_density_evolution.gif")

# ============================================================================
# Animation 2: Temperature Profile Radial Scan
# ============================================================================

print("[2/5] Generating: temperature_profile_scan.gif")

fig, ax = plt.subplots(figsize=(10, 6))

def update_temp(frame):
    ax.clear()
    
    # Radial scanning visualization
    r_scan = 5.0 * frame / 50
    T_vals = T_0 * gamma_seg(r_range)
    
    ax.plot(r_range, T_vals, 'r-', linewidth=3, label='T(r) = T₀ γ_seg(r)')
    ax.plot(SHELL_R, SHELL_T, 'bs', markersize=10, label='Observed')
    
    # Scanning cursor
    if r_scan <= 5.0:
        T_cursor = T_0 * gamma_seg(r_scan)
        ax.axvline(x=r_scan, color='green', linestyle='--', linewidth=2.5, alpha=0.7)
        ax.plot(r_scan, T_cursor, 'go', markersize=15, markeredgecolor='darkgreen',
                markeredgewidth=2.5, zorder=5)
        ax.text(r_scan + 0.2, T_cursor + 20, f'r={r_scan:.2f} pc\nT={T_cursor:.1f} K',
                fontsize=10, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    ax.set_xlabel(r'Radius $r$ [pc]', fontweight='bold')
    ax.set_ylabel(r'Temperature $T$ [K]', fontweight='bold')
    ax.set_title('Temperature Profile: Radial Scan', fontweight='bold')
    ax.set_xlim(0, 5.2)
    ax.set_ylim(0, 600)
    ax.grid(True, alpha=0.25, linestyle=':', linewidth=0.9)
    ax.legend(loc='upper right')
    
    return ax.get_children()

anim = FuncAnimation(fig, update_temp, frames=50, interval=100, blit=False)
writer = PillowWriter(fps=10)
anim.save(OUTPUT_DIR / "temperature_profile_scan.gif", writer=writer)
plt.close()
print("✓ Saved: temperature_profile_scan.gif")

# ============================================================================
# Animation 3: Dual-Frame Temperature Transformation
# ============================================================================

print("[3/5] Generating: dual_frame_temperature.gif")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

def update_dual(frame):
    ax1.clear()
    ax2.clear()
    
    # Animate T_local variation
    T_loc_var = T_LOCAL * (0.7 + 0.6 * np.sin(frame * 2 * np.pi / 50))
    
    # Left: g^(1) perspective (apparent heating)
    T_obs = T_loc_var / gamma_seg(r_range)
    ax1.plot(r_range, T_obs, 'r-', linewidth=3)
    ax1.axhline(y=T_loc_var, color='gray', linestyle='--', linewidth=2, alpha=0.5)
    ax1.fill_between(r_range, T_loc_var, T_obs, alpha=0.3, color='red')
    ax1.set_xlabel(r'Radius $r$ [pc]', fontweight='bold')
    ax1.set_ylabel(r'$T_{\mathrm{obs}}$ [K]', fontweight='bold')
    ax1.set_title(f'From g⁽¹⁾: T_local={T_loc_var:.1f} K', fontweight='bold')
    ax1.set_xlim(0, 5.2)
    ax1.set_ylim(50, 150)
    ax1.grid(True, alpha=0.25, linestyle=':', linewidth=0.9)
    
    # Right: g^(2) perspective (effective cooling)
    T_loc = T_0 * gamma_seg(r_range)
    ax2.plot(r_range, T_loc, 'b-', linewidth=3)
    ax2.axhline(y=T_0, color='gray', linestyle='--', linewidth=2, alpha=0.5)
    ax2.fill_between(r_range, T_loc, T_0, alpha=0.3, color='blue')
    ax2.set_xlabel(r'Radius $r$ [pc]', fontweight='bold')
    ax2.set_ylabel(r'$T_{\mathrm{local}}$ [K]', fontweight='bold')
    ax2.set_title(f'In g⁽²⁾: T_obs={T_0:.1f} K', fontweight='bold')
    ax2.set_xlim(0, 5.2)
    ax2.set_ylim(200, 250)
    ax2.grid(True, alpha=0.25, linestyle=':', linewidth=0.9)
    
    return ax1.get_children() + ax2.get_children()

anim = FuncAnimation(fig, update_dual, frames=50, interval=100, blit=False)
writer = PillowWriter(fps=10)
anim.save(OUTPUT_DIR / "dual_frame_temperature.gif", writer=writer)
plt.close()
print("✓ Saved: dual_frame_temperature.gif")

# ============================================================================
# Animation 4: Energy Density Evolution (Stefan-Boltzmann)
# ============================================================================

print("[4/5] Generating: energy_density_evolution.gif")

fig, ax = plt.subplots(figsize=(10, 6))

def update_energy(frame):
    ax.clear()
    
    # Animate through different perspectives
    phase = frame / 50 * 2 * np.pi
    
    u_g2 = gamma_seg(r_range)**4
    u_g1 = 1 / gamma_seg(r_range)**4
    
    # Blend between perspectives
    blend = 0.5 + 0.5 * np.sin(phase)
    u_blend = blend * u_g2 + (1 - blend) * u_g1
    
    ax.plot(r_range, u_g2, 'b--', linewidth=2, alpha=0.5, label=r'$u^{(2)} = \gamma^4 u$')
    ax.plot(r_range, u_g1, 'r--', linewidth=2, alpha=0.5, label=r'$u^{(1)} = u/\gamma^4$')
    ax.plot(r_range, u_blend, 'g-', linewidth=3.5, label='Current view')
    ax.axhline(y=1, color='gray', linestyle='--', linewidth=2, alpha=0.5)
    
    ax.set_xlabel(r'Radius $r$ [pc]', fontweight='bold')
    ax.set_ylabel(r'Energy Density $u$ [normalized]', fontweight='bold')
    ax.set_title(f'Energy Density Evolution (blend={blend:.2f})', fontweight='bold')
    ax.set_xlim(0, 5.2)
    ax.set_yscale('log')
    ax.set_ylim(0.5, 2.0)
    ax.grid(True, alpha=0.25, linestyle=':', linewidth=0.9, which='both')
    ax.legend(loc='upper right')
    
    return ax.get_children()

anim = FuncAnimation(fig, update_energy, frames=50, interval=100, blit=False)
writer = PillowWriter(fps=10)
anim.save(OUTPUT_DIR / "energy_density_evolution.gif", writer=writer)
plt.close()
print("✓ Saved: energy_density_evolution.gif")

# ============================================================================
# Animation 5: Recoupling Energy Release
# ============================================================================

print("[5/5] Generating: recoupling_energy_release.gif")

fig, ax = plt.subplots(figsize=(10, 6))

def update_recouple(frame):
    ax.clear()
    
    # Animate T_local to show energy accumulation
    T_loc_anim = T_LOCAL * (0.5 + frame / 50 * 1.5)
    
    DT_release = T_loc_anim * (1 - gamma_seg(r_range))
    
    ax.plot(r_range, DT_release, 'g-', linewidth=3.5, label='ΔT_recouple')
    ax.fill_between(r_range, 0, DT_release, alpha=0.3, color='green',
                    label='Released energy')
    
    # Show energy buildup
    ax.text(0.5, 0.95, f'T_local = {T_loc_anim:.1f} K\nEnergy accumulating...',
            transform=ax.transAxes, fontsize=12, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
    
    ax.set_xlabel(r'Radius $r$ [pc]', fontweight='bold')
    ax.set_ylabel(r'$\Delta T_{\mathrm{recouple}}$ [K]', fontweight='bold')
    ax.set_title('Recoupling Energy Release', fontweight='bold')
    ax.set_xlim(0, 5.2)
    ax.set_ylim(0, 20)
    ax.grid(True, alpha=0.25, linestyle=':', linewidth=0.9)
    ax.legend(loc='upper right')
    
    return ax.get_children()

anim = FuncAnimation(fig, update_recouple, frames=50, interval=100, blit=False)
writer = PillowWriter(fps=10)
anim.save(OUTPUT_DIR / "recoupling_energy_release.gif", writer=writer)
plt.close()
print("✓ Saved: recoupling_energy_release.gif")

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

print(f"\nAnimations cover:")
print(f"  ✓ Eq. (10): Temporal density γ_seg(r)")
print(f"  ✓ Eq. (9):  Temperature profile T(r)")
print(f"  ✓ Eq. (15): Dual-frame transformation")
print(f"  ✓ Eq. (16): Energy density u(r)")
print(f"  ✓ Eq. (18): Recoupling release ΔT")

print("\n" + "=" * 80)
