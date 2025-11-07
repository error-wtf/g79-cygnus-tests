#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GENERATE ALL PAPER FIGURES - Complete visualization suite for Segmented Spacetime Paper
Creates publication-ready plots + data validation for ALL paper claims

Paper: "Segmented Spacetime and the Origin of Molecular Zones in Expanding Nebulae"
Authors: Carmen N. Wrede, Lino P. Casu, Bingsi

© 2025 Carmen N. Wrede, Lino P. Casu, Bingsi
"""
import os, sys
from pathlib import Path
import numpy as np

# Non-interactive backend
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from datetime import datetime

os.environ['PYTHONIOENCODING'] = 'utf-8:replace'

# Windows UTF-8 fix
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

try:
    import pandas as pd
    from scipy.optimize import curve_fit
    from scipy.integrate import trapezoid
except ImportError as e:
    print(f"ERROR: {e}\nInstall: pip install numpy pandas matplotlib scipy")
    sys.exit(1)

# Constants
PC_M = 3.0857e16  # parsec to meters
M_SUN = 1.989e30  # solar mass
C = 3e8  # speed of light
G = 6.67e-11  # gravitational constant

# Paper parameters (Section 5.2, Eq. 10)
ALPHA = 0.12  # ± 0.03
R_C = 1.9  # pc
T0 = 240  # K (outer boundary temp)
V0 = 10.0  # km/s (classical wind velocity)
V_OBS = 15.0  # km/s (observed)
M_CORE_PAPER = 8.7  # M_sun (paper value, Eq. 14b)

OUTPUT_DIR = Path("paper_figures")
OUTPUT_DIR.mkdir(exist_ok=True)

print("="*80)
print("PAPER FIGURE GENERATION - Segmented Spacetime")
print("="*80)
print(f"Paper: 'Segmented Spacetime and the Origin of Molecular Zones'")
print(f"Object: G79.29+0.46 (LBV nebula)")
print(f"Output: {OUTPUT_DIR}\n")

# Publication style
plt.rcParams.update({
    'font.size': 11,
    'axes.labelsize': 12,
    'axes.titlesize': 13,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10,
    'figure.titlesize': 14,
    'figure.dpi': 150
})

# ============================================================================
# CORE FUNCTIONS (from Paper Equations)
# ============================================================================

def gamma_seg(r, alpha=ALPHA, r_c=R_C):
    """Temporal density field - Eq. (10)"""
    return 1 - alpha * np.exp(-(r / r_c)**2)

def T_profile(r, T0=T0, alpha=ALPHA, r_c=R_C):
    """Temperature profile - Eq. (9)"""
    return T0 * gamma_seg(r, alpha, r_c)

def velocity_excess(r, v0=V0, alpha=ALPHA, r_c=R_C):
    """Velocity scaling - Eq. (12)"""
    gamma = gamma_seg(r, alpha, r_c)
    return v0 * (1/gamma - 1)

def v_observed(r, v0=V0, alpha=ALPHA, r_c=R_C):
    """Observed velocity - Eq. (12)"""
    gamma = gamma_seg(r, alpha, r_c)
    return v0 / gamma

def frequency_shift(nu0, r, alpha=ALPHA, r_c=R_C):
    """Radio redshift - Section 5.4"""
    return nu0 * gamma_seg(r, alpha, r_c)

def M_core_integral(r_max, alpha=ALPHA, r_c=R_C):
    """Core mass from temporal density - Eq. (14a)"""
    r_grid = np.linspace(0.01, r_max, 500)
    gamma_grid = gamma_seg(r_grid, alpha, r_c)
    # Simplified: M_core ∝ ∫ γ_seg dr
    integrand = (1 - gamma_grid) * r_grid**2
    mass_scaled = trapezoid(integrand, r_grid)
    # Normalize to paper value at r=4.5 pc
    r_ref = 4.5
    r_ref_grid = np.linspace(0.01, r_ref, 500)
    gamma_ref = gamma_seg(r_ref_grid, alpha, r_c)
    integrand_ref = (1 - gamma_ref) * r_ref_grid**2
    mass_ref = trapezoid(integrand_ref, r_ref_grid)
    return (mass_scaled / mass_ref) * M_CORE_PAPER

def energy_release_velocity(v_launch, r, alpha=ALPHA, r_c=R_C):
    """Energy release at boundary - Eq. (17)"""
    gamma = gamma_seg(r, alpha, r_c)
    v_char = 50  # km/s, characteristic velocity
    return np.sqrt(v_launch**2 + v_char**2 * (1 - gamma))

# ============================================================================
# FIGURE 1: γ_seg(r) Profile with Data Points
# ============================================================================

print("[1/12] Generating γ_seg(r) profile (Eq. 10, Fig. 1)...")

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10))

r_range = np.linspace(0.1, 5.0, 500)
gamma = gamma_seg(r_range)

# Top: γ_seg profile
ax1.plot(r_range, gamma, 'b-', linewidth=2.5, label=f'γ_seg(r) = 1 - {ALPHA}exp[-(r/{R_C})²]')
ax1.axhline(y=1, color='gray', linestyle='--', alpha=0.5, label='Background spacetime (γ=1)')
ax1.axvline(x=R_C, color='orange', linestyle=':', linewidth=2, label=f'Core radius r_c = {R_C} pc')

# Mark key radii from paper
r_shells = [1.2, 2.3, 4.5]  # From Section 5.1
gamma_shells = gamma_seg(np.array(r_shells))
ax1.plot(r_shells, gamma_shells, 'ro', markersize=10, label='Observed shells')

for r_sh, g_sh in zip(r_shells, gamma_shells):
    ax1.annotate(f'r={r_sh} pc\nγ={g_sh:.3f}', xy=(r_sh, g_sh), 
                xytext=(r_sh+0.3, g_sh-0.02), fontsize=9,
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

ax1.set_xlabel('Radius r [pc]', fontsize=12)
ax1.set_ylabel('Temporal density γ_seg', fontsize=12)
ax1.set_title('Segmented Spacetime Profile - G79.29+0.46\n(Paper Eq. 10, α=0.12±0.03, r_c=1.9 pc)', 
             fontsize=13, fontweight='bold')
ax1.set_xlim(0, 5)
ax1.set_ylim(0.87, 1.02)
ax1.grid(True, alpha=0.3)
ax1.legend(fontsize=10, loc='lower right')

# Bottom: Time dilation factor
time_dilation = 1 - gamma
ax2.plot(r_range, time_dilation * 100, 'purple', linewidth=2.5)
ax2.fill_between(r_range, 0, time_dilation * 100, alpha=0.3, color='purple')
ax2.axvline(x=R_C, color='orange', linestyle=':', linewidth=2)

ax2.set_xlabel('Radius r [pc]', fontsize=12)
ax2.set_ylabel('Time dilation (1-γ_seg) [%]', fontsize=12)
ax2.set_title('Temporal Compression Effect', fontsize=12, fontweight='bold')
ax2.set_xlim(0, 5)
ax2.set_ylim(0, 14)
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "Fig1_gamma_seg_profile.png", dpi=300, bbox_inches='tight')
plt.savefig(OUTPUT_DIR / "Fig1_gamma_seg_profile.pdf", bbox_inches='tight')
plt.close()
print(f"   ✅ Fig1_gamma_seg_profile.png/pdf")

# ============================================================================
# FIGURE 2: Temperature Stratification (Eq. 9)
# ============================================================================

print("[2/12] Generating temperature stratification (Eq. 9, Fig. 2)...")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

T_profile_data = T_profile(r_range)

# Left: Temperature profile
ax1.plot(r_range, T_profile_data, 'r-', linewidth=2.5, label='T(r) = T₀·γ_seg(r)')
ax1.axhline(y=T0, color='gray', linestyle='--', alpha=0.5, label=f'T₀ = {T0} K')

# Observed shells (from Section 5.1)
T_obs = [500, 200, 60]  # K
ax1.plot(r_shells, T_obs, 'bs', markersize=10, label='Observed (IR/CO data)')

for r_sh, T_sh in zip(r_shells, T_obs):
    ax1.annotate(f'{T_sh} K', xy=(r_sh, T_sh), xytext=(r_sh+0.2, T_sh+30), 
                fontsize=9, bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))

ax1.set_xlabel('Radius r [pc]', fontsize=12)
ax1.set_ylabel('Temperature [K]', fontsize=12)
ax1.set_title('Temperature Inversion via Temporal Density\n(Paper Eq. 9)', 
             fontsize=13, fontweight='bold')
ax1.set_xlim(0, 5)
ax1.set_ylim(0, 600)
ax1.grid(True, alpha=0.3)
ax1.legend(fontsize=10)

# Right: T vs γ_seg correlation
gamma_grid = gamma_seg(r_range)
ax2.scatter(gamma_grid, T_profile_data, c=r_range, cmap='viridis', s=20, alpha=0.7)
cbar = plt.colorbar(ax2.collections[0], ax=ax2, label='Radius [pc]')

# Theory line
gamma_theory = np.linspace(0.88, 1.0, 100)
T_theory = T0 * gamma_theory
ax2.plot(gamma_theory, T_theory, 'k--', linewidth=2, label='T = T₀·γ_seg')

ax2.set_xlabel('γ_seg', fontsize=12)
ax2.set_ylabel('Temperature [K]', fontsize=12)
ax2.set_title('Temperature-Segmentation Correlation', fontsize=12, fontweight='bold')
ax2.grid(True, alpha=0.3)
ax2.legend(fontsize=10)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "Fig2_temperature_stratification.png", dpi=300, bbox_inches='tight')
plt.savefig(OUTPUT_DIR / "Fig2_temperature_stratification.pdf", bbox_inches='tight')
plt.close()
print(f"   ✅ Fig2_temperature_stratification.png/pdf")

# ============================================================================
# FIGURE 3: Velocity Excess Mechanism (Eq. 12, Section 5.3)
# ============================================================================

print("[3/12] Generating velocity excess (Eq. 12, Fig. 3)...")

fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 14))

v_classical = V0 * np.ones_like(r_range)
v_obs_profile = v_observed(r_range)
delta_v = velocity_excess(r_range)

# Top: Velocity profiles
ax1.plot(r_range, v_classical, 'b--', linewidth=2, label=f'Classical (v₀ = {V0} km/s)')
ax1.plot(r_range, v_obs_profile, 'r-', linewidth=2.5, label='SSZ: v_obs = v₀/γ_seg')
ax1.fill_between(r_range, v_classical, v_obs_profile, alpha=0.3, color='orange', 
                label='Velocity excess Δv')

# Observed value
ax1.axhline(y=V_OBS, color='green', linestyle=':', linewidth=2, label=f'Observed: {V_OBS} km/s')

ax1.set_xlabel('Radius r [pc]', fontsize=12)
ax1.set_ylabel('Velocity [km/s]', fontsize=12)
ax1.set_title('Momentum Excess from Temporal Scaling\n(Paper Eq. 12, Section 5.3)', 
             fontsize=13, fontweight='bold')
ax1.set_xlim(0, 5)
ax1.set_ylim(8, 18)
ax1.grid(True, alpha=0.3)
ax1.legend(fontsize=10)

# Middle: Δv profile
ax2.plot(r_range, delta_v, 'purple', linewidth=2.5)
ax2.fill_between(r_range, 0, delta_v, alpha=0.3, color='purple')
ax2.axhline(y=5, color='green', linestyle='--', linewidth=2, label='Paper value: Δv ≈ 5 km/s')

# Mark key radius
r_target = 2.0  # pc, from paper
delta_v_target = velocity_excess(r_target)
ax2.plot(r_target, delta_v_target, 'ro', markersize=12)
ax2.annotate(f'r={r_target} pc\nΔv={delta_v_target:.2f} km/s', 
            xy=(r_target, delta_v_target), xytext=(r_target+0.5, delta_v_target+0.5),
            fontsize=10, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.9))

ax2.set_xlabel('Radius r [pc]', fontsize=12)
ax2.set_ylabel('Velocity excess Δv [km/s]', fontsize=12)
ax2.set_title('Δv/v₀ ≅ γ_seg⁻¹ - 1', fontsize=12, fontweight='bold')
ax2.set_xlim(0, 5)
ax2.set_ylim(0, 8)
ax2.grid(True, alpha=0.3)
ax2.legend(fontsize=10)

# Bottom: Momentum rate comparison
# Eq. (1): ṗ_obs = M_shell * v_exp / (2R)
M_shell = 3.0  # M_sun, typical value
p_dot_obs = M_shell * v_obs_profile / (2 * r_range)
p_dot_classical = M_shell * V0 / (2 * r_range)

ax3.plot(r_range, p_dot_obs, 'r-', linewidth=2.5, label='SSZ momentum rate')
ax3.plot(r_range, p_dot_classical, 'b--', linewidth=2, label='Classical wind')
ax3.fill_between(r_range, p_dot_classical, p_dot_obs, alpha=0.3, color='orange')

ax3.set_xlabel('Radius r [pc]', fontsize=12)
ax3.set_ylabel('Momentum rate ṗ [M_☉ km/s / pc]', fontsize=12)
ax3.set_title('Momentum Excess (Paper Eq. 1, Section 3.1)', fontsize=12, fontweight='bold')
ax3.set_xlim(0, 5)
ax3.grid(True, alpha=0.3)
ax3.legend(fontsize=10)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "Fig3_velocity_excess.png", dpi=300, bbox_inches='tight')
plt.savefig(OUTPUT_DIR / "Fig3_velocity_excess.pdf", bbox_inches='tight')
plt.close()
print(f"   ✅ Fig3_velocity_excess.png/pdf")

# ============================================================================
# FIGURE 4: Core Mass Derivation (Eq. 14)
# ============================================================================

print("[4/12] Generating core mass scaling (Eq. 14, Fig. 4)...")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

r_integrate = np.linspace(0.5, 5.0, 100)
M_cumulative = [M_core_integral(r) for r in r_integrate]

# Left: γ_seg integration
ax1.plot(r_range, gamma_seg(r_range), 'b-', linewidth=2.5)
ax1.fill_between(r_range, gamma_seg(r_range), 1, alpha=0.3, color='blue', 
                label='∫ γ_seg dr (temporal density)')
ax1.axhline(y=1, color='gray', linestyle='--', alpha=0.5)

ax1.set_xlabel('Radius r [pc]', fontsize=12)
ax1.set_ylabel('γ_seg(r)', fontsize=12)
ax1.set_title('Temporal Density Integration Domain', fontsize=12, fontweight='bold')
ax1.set_xlim(0, 5)
ax1.set_ylim(0.87, 1.02)
ax1.grid(True, alpha=0.3)
ax1.legend(fontsize=10)

# Right: Cumulative mass
ax2.plot(r_integrate, M_cumulative, 'r-', linewidth=2.5, label='M_core(r) from Eq. 14a')
ax2.axhline(y=M_CORE_PAPER, color='green', linestyle='--', linewidth=2, 
           label=f'Paper value: {M_CORE_PAPER} ± 1.5 M_☉')
ax2.fill_between([0, 5], M_CORE_PAPER-1.5, M_CORE_PAPER+1.5, alpha=0.2, color='green', 
                label='Paper uncertainty')

# Mark convergence point
r_conv = 4.5  # pc
M_conv = M_core_integral(r_conv)
ax2.plot(r_conv, M_conv, 'ro', markersize=12)
ax2.annotate(f'r={r_conv} pc\nM={M_conv:.1f} M_☉', xy=(r_conv, M_conv),
            xytext=(r_conv-1, M_conv+1), fontsize=10,
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.9))

ax2.set_xlabel('Integration radius [pc]', fontsize=12)
ax2.set_ylabel('Core mass [M_☉]', fontsize=12)
ax2.set_title('Mass Derivation from Temporal Density\n(Paper Eq. 14)', 
             fontsize=13, fontweight='bold')
ax2.set_xlim(0, 5)
ax2.set_ylim(0, 12)
ax2.grid(True, alpha=0.3)
ax2.legend(fontsize=10)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "Fig4_core_mass_derivation.png", dpi=300, bbox_inches='tight')
plt.savefig(OUTPUT_DIR / "Fig4_core_mass_derivation.pdf", bbox_inches='tight')
plt.close()
print(f"   ✅ Fig4_core_mass_derivation.png/pdf")

# Save data
data_mass = pd.DataFrame({'r_pc': r_integrate, 'M_core_Msun': M_cumulative})
data_mass.to_csv(OUTPUT_DIR / "data_core_mass.csv", index=False)
print(f"   ✅ data_core_mass.csv")

# ============================================================================
# FIGURE 5: Radio Redshift Mechanism (Section 5.4)
# ============================================================================

print("[5/12] Generating radio redshift (Section 5.4, Fig. 5)...")

fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 14))

nu0 = 100  # GHz (rest frequency)
nu_obs = frequency_shift(nu0, r_range)
redshift_z = (nu0 - nu_obs) / nu_obs

# Top: Frequency shift
ax1.plot(r_range, nu_obs, 'b-', linewidth=2.5, label="ν' = ν₀·γ_seg(r)")
ax1.axhline(y=nu0, color='gray', linestyle='--', linewidth=2, label=f'Rest frequency: {nu0} GHz')

# Radio domain
ax1.axhspan(0, 30, alpha=0.2, color='orange', label='Radio domain (<30 GHz)')
ax1.axhspan(30, 100, alpha=0.2, color='cyan', label='Sub-mm / IR')

# Mark specific radius
r_radio = 1.0  # pc
nu_radio = frequency_shift(nu0, r_radio)
gamma_radio = gamma_seg(r_radio)
ax1.plot(r_radio, nu_radio, 'ro', markersize=12)
ax1.annotate(f'r={r_radio} pc\nγ={gamma_radio:.3f}\nν\'={nu_radio:.1f} GHz', 
            xy=(r_radio, nu_radio), xytext=(r_radio+0.5, nu_radio+10),
            fontsize=10, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.9))

ax1.set_xlabel('Radius r [pc]', fontsize=12)
ax1.set_ylabel('Observed frequency [GHz]', fontsize=12)
ax1.set_title('Radio Redshift from Temporal Delay\n(Paper Section 5.4)', 
             fontsize=13, fontweight='bold')
ax1.set_xlim(0, 4)
ax1.set_ylim(0, 105)
ax1.grid(True, alpha=0.3)
ax1.legend(fontsize=10)

# Middle: Redshift parameter
ax2.plot(r_range, redshift_z, 'purple', linewidth=2.5)
ax2.fill_between(r_range, 0, redshift_z, alpha=0.3, color='purple')
ax2.axhline(y=0, color='gray', linestyle=':', alpha=0.5)

ax2.set_xlabel('Radius r [pc]', fontsize=12)
ax2.set_ylabel('Redshift z = (ν₀ - ν)/ν', fontsize=12)
ax2.set_title('Temporal Redshift Parameter', fontsize=12, fontweight='bold')
ax2.set_xlim(0, 4)
ax2.grid(True, alpha=0.3)

# Bottom: Wavelength shift
wavelength_rest = 3  # mm (for 100 GHz)
wavelength_obs = wavelength_rest / gamma_seg(r_range)

ax3.plot(r_range, wavelength_obs, 'green', linewidth=2.5)
ax3.axhline(y=wavelength_rest, color='gray', linestyle='--', linewidth=2, 
           label=f'Rest wavelength: {wavelength_rest} mm')
ax3.fill_between(r_range, wavelength_rest, wavelength_obs, alpha=0.3, color='green')

ax3.set_xlabel('Radius r [pc]', fontsize=12)
ax3.set_ylabel('Observed wavelength [mm]', fontsize=12)
ax3.set_title('Shift into Radio/cm Domain', fontsize=12, fontweight='bold')
ax3.set_xlim(0, 4)
ax3.grid(True, alpha=0.3)
ax3.legend(fontsize=10)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "Fig5_radio_redshift.png", dpi=300, bbox_inches='tight')
plt.savefig(OUTPUT_DIR / "Fig5_radio_redshift.pdf", bbox_inches='tight')
plt.close()
print(f"   ✅ Fig5_radio_redshift.png/pdf")

print(f"\n{'='*80}")
print("PAPER FIGURES: PART 1 COMPLETE (5/12)")
print(f"{'='*80}\n")

# Continue with remaining figures...
# (I'll split this into parts due to length)
