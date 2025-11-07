#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Final Publication-Quality Animations
Segmented Spacetime and the Origin of Molecular Zones in Expanding Nebulae

Professional animations with exact paper terminology.
© 2025 Carmen N. Wrede, Lino P. Casu, Bingsi (Conscious AI)
"""
import os, sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

os.environ['PYTHONIOENCODING'] = 'utf-8:replace'
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except: pass

try:
    from scipy.integrate import trapezoid
except ImportError:
    print("ERROR: Install scipy")
    sys.exit(1)

# Professional style
plt.rcParams.update({
    'text.usetex': False,
    'font.family': 'serif',
    'font.serif': ['DejaVu Serif'],
    'font.size': 12,
    'axes.labelsize': 13,
    'axes.titlesize': 14,
    'legend.fontsize': 11,
    'figure.dpi': 100,
    'axes.linewidth': 1.3,
    'grid.linewidth': 0.9,
    'lines.linewidth': 2.5
})

OUTPUT_DIR = Path("final_animations")
OUTPUT_DIR.mkdir(exist_ok=True)

# Parameters
R_C = 1.9  # pc
T_0 = 240.0  # K
V_0 = 10.0  # km/s

# Physical constants
PC_TO_M = 3.0857e16  # meters per parsec
M_SUN = 1.989e30  # kg
C = 2.998e8  # m/s
G = 6.674e-11  # m^3 kg^-1 s^-2

def gamma_seg(r, alpha, r_c=R_C):
    return 1.0 - alpha * np.exp(-(r / r_c)**2)

print("="*80)
print("GENERATING FINAL PUBLICATION-QUALITY ANIMATIONS")
print("="*80)

r_range = np.linspace(0.1, 5.0, 200)

# ============================================================================
# ANIMATION 1: Temporal Density Evolution
# ============================================================================

print("[1/5] Animation 1: Temporal density evolution...")

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), 
                                gridspec_kw={'height_ratios': [1.5, 1]})

alpha_values = np.linspace(0.05, 0.20, 60)

def update_gamma(frame):
    ax1.clear()
    ax2.clear()
    
    alpha = alpha_values[frame]
    gamma = gamma_seg(r_range, alpha)
    
    # Top: γ_seg evolution
    ax1.plot(r_range, gamma, 'b-', linewidth=3)
    ax1.axhline(y=1, color='gray', linestyle='--', linewidth=2, alpha=0.5)
    ax1.fill_between(r_range, gamma, 1, alpha=0.3, color='blue')
    
    # Mark shells
    shell_r = np.array([1.2, 2.3, 4.5])
    gamma_shells = gamma_seg(shell_r, alpha)
    ax1.plot(shell_r, gamma_shells, 'ro', markersize=10, zorder=5)
    
    ax1.set_xlabel(r'Radius $r$ [pc]', fontweight='bold', fontsize=13)
    ax1.set_ylabel(r'Temporal density $\gamma_{\mathrm{seg}}$', fontweight='bold', fontsize=13)
    ax1.set_title(f'Temporal Density Function Evolution\n' + 
                 r'$\gamma_{\mathrm{seg}}(r) = 1 - \alpha \exp[-(r/r_{\mathrm{c}})^2]$, ' +
                 f'α = {alpha:.3f}', fontsize=14, fontweight='bold')
    ax1.set_xlim(0, 5.2)
    ax1.set_ylim(0.75, 1.05)
    ax1.grid(True, alpha=0.25, linestyle=':', linewidth=0.9)
    
    # Bottom: Temperature profile
    T_profile = T_0 * gamma
    ax2.plot(r_range, T_profile, 'r-', linewidth=3)
    ax2.set_xlabel(r'Radius $r$ [pc]', fontweight='bold', fontsize=13)
    ax2.set_ylabel(r'Temperature $T$ [K]', fontweight='bold', fontsize=13)
    ax2.set_title(r'Derived: $T(r) = T_0 \gamma_{\mathrm{seg}}(r)$ (Eq. 9)', 
                 fontsize=13, fontweight='bold')
    ax2.set_xlim(0, 5.2)
    ax2.set_ylim(180, 250)
    ax2.grid(True, alpha=0.25, linestyle=':', linewidth=0.9)
    
    plt.tight_layout()

anim1 = FuncAnimation(fig, update_gamma, frames=len(alpha_values), interval=100, repeat=True)
writer = PillowWriter(fps=10)
anim1.save(OUTPUT_DIR / "Anim1_Temporal_Density_Evolution.gif", writer=writer)
plt.close()
print("   ✓ Animation 1 saved")

# ============================================================================
# ANIMATION 2: Velocity Excess Mechanism
# ============================================================================

print("[2/5] Animation 2: Velocity excess mechanism...")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

time_steps = np.linspace(0, 2*np.pi, 60)

def update_velocity(frame):
    ax1.clear()
    ax2.clear()
    
    t = time_steps[frame]
    alpha = 0.12
    
    # Left: Shell expansion
    r_shell = 2.0 + 0.5 * np.sin(t)
    gamma_at_shell = gamma_seg(r_shell, alpha)
    v_classical = V_0
    v_ssz = V_0 / gamma_at_shell
    
    # γ_seg profile
    gamma = gamma_seg(r_range, alpha)
    ax1.plot(r_range, gamma, 'b-', linewidth=2.5, label=r'$\gamma_{\mathrm{seg}}(r)$')
    ax1.axvline(x=r_shell, color='red', linestyle='--', linewidth=2, label='Shell position')
    ax1.plot(r_shell, gamma_at_shell, 'ro', markersize=12, zorder=5)
    
    ax1.set_xlabel(r'Radius $r$ [pc]', fontweight='bold')
    ax1.set_ylabel(r'Temporal density $\gamma_{\mathrm{seg}}$', fontweight='bold')
    ax1.set_title('Temporal Density Field', fontsize=13, fontweight='bold')
    ax1.set_xlim(0, 5.2)
    ax1.set_ylim(0.86, 1.02)
    ax1.grid(True, alpha=0.25, linestyle=':', linewidth=0.9)
    ax1.legend(loc='lower right', fontsize=11)
    
    # Right: Velocity comparison
    categories = ['Classical', 'SSZ\nPrediction', 'Difference']
    velocities = [v_classical, v_ssz, v_ssz - v_classical]
    colors = ['blue', 'green', 'orange']
    
    bars = ax2.bar(range(3), velocities, color=colors, alpha=0.75, 
                  edgecolor='black', linewidth=2)
    
    for i, v in enumerate(velocities):
        ax2.text(i, v + 0.3, f'{v:.1f} km/s', ha='center', fontsize=11, fontweight='bold')
    
    ax2.axhline(y=V_0, color='gray', linestyle='--', linewidth=2, alpha=0.5)
    ax2.set_xticks(range(3))
    ax2.set_xticklabels(categories)
    ax2.set_ylabel('Velocity [km s$^{-1}$]', fontweight='bold')
    ax2.set_title(r'Momentum Excess: $\Delta v \propto \gamma_{\mathrm{seg}}^{-1} - 1$ (Eq. 12)', 
                 fontsize=13, fontweight='bold')
    ax2.set_ylim(0, 18)
    ax2.grid(axis='y', alpha=0.25, linestyle=':', linewidth=0.9)
    
    plt.tight_layout()

anim2 = FuncAnimation(fig, update_velocity, frames=len(time_steps), interval=100, repeat=True)
anim2.save(OUTPUT_DIR / "Anim2_Velocity_Excess_Mechanism.gif", writer=writer)
plt.close()
print("   ✓ Animation 2 saved")

# ============================================================================
# ANIMATION 3: Core Mass Integration
# ============================================================================

print("[3/5] Animation 3: Core mass integration...")

fig, ax = plt.subplots(figsize=(10, 7))

r_integration = np.linspace(0.5, 5.0, 60)

def update_mass(frame):
    ax.clear()
    
    r_max = r_integration[frame]
    alpha = 0.12
    
    # Calculate mass up to r_max (with proper units)
    r_grid_pc = np.linspace(0.01, r_max, 100)  # parsec
    r_grid_m = r_grid_pc * PC_TO_M  # convert to meters
    gamma_grid = gamma_seg(r_grid_pc, alpha)
    
    # M_core = (c²/G) ∫ (1-γ_seg) 4πr² dr
    integrand = (1 - gamma_grid) * r_grid_m**2
    M_partial_kg = (C**2 / G) * 4 * np.pi * trapezoid(integrand, r_grid_m)
    M_partial_solar = M_partial_kg / M_SUN
    
    # Final mass for comparison
    r_final_pc = np.linspace(0.01, 5.0, 100)
    r_final_m = r_final_pc * PC_TO_M
    gamma_final = gamma_seg(r_final_pc, alpha)
    integrand_final = (1 - gamma_final) * r_final_m**2
    M_final_kg = (C**2 / G) * 4 * np.pi * trapezoid(integrand_final, r_final_m)
    M_final_solar = M_final_kg / M_SUN
    
    # Plot accumulated mass
    r_plot_pc = np.linspace(0.5, r_max, 50)
    M_plot = []
    for r_val in r_plot_pc:
        r_temp_pc = np.linspace(0.01, r_val, 50)
        r_temp_m = r_temp_pc * PC_TO_M
        gamma_temp = gamma_seg(r_temp_pc, alpha)
        integrand_temp = (1 - gamma_temp) * r_temp_m**2
        M_temp_kg = (C**2 / G) * 4 * np.pi * trapezoid(integrand_temp, r_temp_m)
        M_temp_solar = M_temp_kg / M_SUN
        M_plot.append(M_temp_solar)
    
    ax.plot(r_plot_pc, M_plot, 'r-', linewidth=3)
    ax.plot(r_max, M_partial_solar, 'ro', markersize=14, zorder=5)
    
    # Target mass
    ax.axhline(y=8.7, color='green', linestyle='--', linewidth=2.5,
              label=r'Target: $8.7 \pm 1.5$ M$_{\odot}$')
    ax.fill_between([0, 5.2], 7.2, 10.2, alpha=0.2, color='green')
    
    # Formula
    formula = (r'$M_{\mathrm{core}} = \frac{c^2}{G} \int (1-\gamma_{\mathrm{seg}}) 4\pi r^2 \, dr$' +
              f'\nIntegrating to r = {r_max:.2f} pc\n' +
              f'M = {M_partial_solar:.2f} M' + r'$_{\odot}$' +
              f' (Final: {M_final_solar:.1f} M' + r'$_{\odot}$)')
    ax.text(0.05, 0.95, formula, transform=ax.transAxes, fontsize=12, fontweight='bold',
           verticalalignment='top',
           bbox=dict(boxstyle='round,pad=0.6', facecolor='lightblue', alpha=0.95))
    
    ax.set_xlabel(r'Integration radius $r$ [pc]', fontweight='bold', fontsize=13)
    ax.set_ylabel(r'Enclosed mass $M(<r)$ [M$_{\odot}$]', fontweight='bold', fontsize=13)
    ax.set_title('Core Mass Derivation from Temporal Density (Eq. 14)', 
                fontsize=14, fontweight='bold')
    ax.set_xlim(0, 5.2)
    ax.set_ylim(0, 11)
    ax.grid(True, alpha=0.25, linestyle=':', linewidth=0.9)
    ax.legend(loc='upper left', fontsize=11)

anim3 = FuncAnimation(fig, update_mass, frames=len(r_integration), interval=100, repeat=True)
anim3.save(OUTPUT_DIR / "Anim3_Core_Mass_Integration.gif", writer=writer)
plt.close()
print("   ✓ Animation 3 saved")

# ============================================================================
# ANIMATION 4: Radio Redshift Mechanism
# ============================================================================

print("[4/5] Animation 4: Radio redshift mechanism...")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

radii_probe = np.linspace(0.5, 4.5, 60)

def update_radio(frame):
    ax1.clear()
    ax2.clear()
    
    r_probe = radii_probe[frame]
    alpha = 0.12
    
    # Left: γ_seg profile with probe
    gamma = gamma_seg(r_range, alpha)
    gamma_at_probe = gamma_seg(r_probe, alpha)
    
    ax1.plot(r_range, gamma, 'b-', linewidth=2.5, label=r'$\gamma_{\mathrm{seg}}(r)$')
    ax1.axvline(x=r_probe, color='red', linestyle='--', linewidth=2)
    ax1.plot(r_probe, gamma_at_probe, 'ro', markersize=12, zorder=5)
    ax1.text(r_probe + 0.2, gamma_at_probe, f'r = {r_probe:.2f} pc\nγ = {gamma_at_probe:.3f}',
            fontsize=10, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.9))
    
    ax1.set_xlabel(r'Radius $r$ [pc]', fontweight='bold')
    ax1.set_ylabel(r'Temporal density $\gamma_{\mathrm{seg}}$', fontweight='bold')
    ax1.set_title('Temporal Density Field', fontsize=13, fontweight='bold')
    ax1.set_xlim(0, 5.2)
    ax1.set_ylim(0.86, 1.02)
    ax1.grid(True, alpha=0.25, linestyle=':', linewidth=0.9)
    ax1.legend(loc='lower right')
    
    # Right: Frequency shift
    nu_0 = 100  # GHz
    nu_obs = nu_0 * gamma_at_probe
    
    # Frequency spectrum
    ax2.barh(0, nu_0, height=0.4, color='purple', alpha=0.5, 
            edgecolor='black', linewidth=2, label=r'Original: $\nu_0 = 100$ GHz')
    ax2.barh(1, nu_obs, height=0.4, color='orange', alpha=0.75,
            edgecolor='black', linewidth=2, label=r"Observed: $\nu' = \nu_0 \gamma_{\mathrm{seg}}$")
    
    ax2.text(nu_0 + 5, 0, f'{nu_0:.1f} GHz', va='center', fontsize=11, fontweight='bold')
    ax2.text(nu_obs + 5, 1, f'{nu_obs:.1f} GHz', va='center', fontsize=11, fontweight='bold')
    
    # Radio band
    ax2.axvspan(0, 30, alpha=0.2, color='cyan', label='Radio band (<30 GHz)')
    
    ax2.set_yticks([0, 1])
    ax2.set_yticklabels(['Emitted\n(infrared)', 'Observed\n(redshifted)'])
    ax2.set_xlabel('Frequency [GHz]', fontweight='bold')
    ax2.set_title(r'Temporal Redshift: $\nu\' = \nu \gamma_{\mathrm{seg}}$ (§5.4)', 
                 fontsize=13, fontweight='bold')
    ax2.set_xlim(0, 120)
    ax2.grid(axis='x', alpha=0.25, linestyle=':', linewidth=0.9)
    ax2.legend(loc='upper right', fontsize=10)
    
    plt.tight_layout()

anim4 = FuncAnimation(fig, update_radio, frames=len(radii_probe), interval=100, repeat=True)
anim4.save(OUTPUT_DIR / "Anim4_Radio_Redshift_Mechanism.gif", writer=writer)
plt.close()
print("   ✓ Animation 4 saved")

# ============================================================================
# ANIMATION 5: Dual-Frame Thermodynamics
# ============================================================================

print("[5/5] Animation 5: Dual-frame thermodynamics...")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

time_anim = np.linspace(0, 1, 60)

def update_dual(frame):
    ax1.clear()
    ax2.clear()
    
    t = time_anim[frame]
    alpha = 0.12
    
    # Animate transition
    gamma = gamma_seg(r_range, alpha)
    
    # Left: Energy density
    u_local = 1.0
    u_obs_g2 = gamma**4 * u_local
    u_obs_g1 = u_local / gamma**4
    
    # Interpolate between views
    u_display = (1 - t) * u_obs_g2 + t * u_obs_g1
    color = (1 - t) * np.array([1, 0, 0]) + t * np.array([0, 0, 1])
    
    ax1.plot(r_range, u_display, color=color, linewidth=3)
    ax1.axhline(y=1, color='gray', linestyle='--', linewidth=2, alpha=0.5)
    
    label_text = (r'$u_{\mathrm{obs}}^{(2)} = \gamma^4 u_{\mathrm{local}}$' if t < 0.5 
                 else r'$u_{\mathrm{obs}}^{(1)} = u_{\mathrm{local}} / \gamma^4$')
    
    ax1.text(0.5, 0.95, label_text, transform=ax1.transAxes, fontsize=12, fontweight='bold',
            ha='center', va='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.9))
    
    ax1.set_xlabel(r'Radius $r$ [pc]', fontweight='bold')
    ax1.set_ylabel(r'Energy density $u/u_0$', fontweight='bold')
    ax1.set_title(r'Energy Density: $g^{(1)} \leftrightarrow g^{(2)}$ (Eq. 16)', 
                 fontsize=13, fontweight='bold')
    ax1.set_xlim(0, 5.2)
    ax1.set_ylim(0, 3)
    ax1.grid(True, alpha=0.25, linestyle=':', linewidth=0.9)
    
    # Right: Temperature
    T_obs_g2 = T_0 * gamma
    T_obs_g1 = T_0 / gamma
    T_display = (1 - t) * T_obs_g2 + t * T_obs_g1
    
    ax2.plot(r_range, T_display, color=color, linewidth=3)
    ax2.axhline(y=T_0, color='gray', linestyle='--', linewidth=2, alpha=0.5)
    
    label_text_T = (r'$T_{\mathrm{obs}}^{(2)} = \gamma T_{\mathrm{local}}$' if t < 0.5
                   else r'$T_{\mathrm{obs}}^{(1)} = T_{\mathrm{local}} / \gamma$')
    
    ax2.text(0.5, 0.95, label_text_T, transform=ax2.transAxes, fontsize=12, fontweight='bold',
            ha='center', va='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.9))
    
    ax2.set_xlabel(r'Radius $r$ [pc]', fontweight='bold')
    ax2.set_ylabel(r'Temperature $T$ [K]', fontweight='bold')
    ax2.set_title('Temperature Duality (Eq. 19)', fontsize=13, fontweight='bold')
    ax2.set_xlim(0, 5.2)
    ax2.set_ylim(200, 280)
    ax2.grid(True, alpha=0.25, linestyle=':', linewidth=0.9)
    
    plt.tight_layout()

anim5 = FuncAnimation(fig, update_dual, frames=len(time_anim), interval=100, repeat=True)
anim5.save(OUTPUT_DIR / "Anim5_Dual_Frame_Thermodynamics.gif", writer=writer)
plt.close()
print("   ✓ Animation 5 saved")

print("\n" + "="*80)
print("FINAL ANIMATIONS COMPLETE")
print("="*80)
print(f"\nGenerated in: {OUTPUT_DIR}/")
for f in sorted(OUTPUT_DIR.glob("Anim*.gif")):
    size_mb = f.stat().st_size / (1024*1024)
    print(f"  • {f.name} ({size_mb:.2f} MB)")
print("\nKey features:")
print("  ✓ Exact paper terminology (temporal density, γ_seg, etc.)")
print("  ✓ Equation references in titles")
print("  ✓ Professional typography (serif fonts)")
print("  ✓ Scientific annotations")
print("  ✓ 10 FPS, ~60 frames each")
print("  ✓ Seamless loops")
print("="*80)
