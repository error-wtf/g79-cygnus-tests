#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GENERATE TEST ANIMATIONS - Create GIFs from all test outputs
Generates animated visualizations for all physics tests
© 2025 Carmen N. Wrede, Lino P. Casu, Bingsi
"""
import os, sys
from pathlib import Path
import numpy as np

# CRITICAL: Set non-interactive backend BEFORE importing pyplot
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend - no windows, no blocking!

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.animation import PillowWriter
from datetime import datetime

os.environ['PYTHONIOENCODING'] = 'utf-8:replace'
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except: pass

try:
    import pandas as pd
    from scipy.optimize import curve_fit
except ImportError as e:
    print(f"ERROR: {e}\nInstall: pip install numpy pandas matplotlib scipy pillow")
    sys.exit(1)

PC_M = 3.0857e16
M_SUN = 1.989e30
C = 3e8

OUTPUT_DIR = Path("animations")
OUTPUT_DIR.mkdir(exist_ok=True)

print("="*80)
print("GENERATING TEST ANIMATIONS FOR G79.29+0.46")
print("="*80)
print(f"\nOutput: {OUTPUT_DIR}\nStart: {datetime.now().strftime('%H:%M:%S')}\n")

def gamma_seg(r, alpha=0.12, r_c=1.9):
    return 1 - alpha * np.exp(-(r / r_c)**2)

# Animation 1: γ_seg Evolution
print("[1/8] γ_seg(r) evolution...")
fig, ax = plt.subplots(figsize=(12, 8))
r_range = np.linspace(0.1, 5.0, 200)
alpha_values = np.linspace(0.05, 0.5, 60)

def anim1(frame):
    ax.clear()
    alpha = alpha_values[frame]
    gamma = gamma_seg(r_range, alpha, 1.9)
    ax.plot(r_range, gamma, 'b-', linewidth=3)
    ax.axhline(y=1, color='gray', linestyle='--', alpha=0.5)
    ax.set_xlabel('Radius [pc]', fontsize=14)
    ax.set_ylabel('γ_seg', fontsize=14)
    ax.set_title(f'Temporal Density Evolution (α={alpha:.3f})', fontsize=16, fontweight='bold')
    ax.set_xlim(0, 5); ax.set_ylim(0.4, 1.05)
    ax.grid(True, alpha=0.3)

anim = animation.FuncAnimation(fig, anim1, frames=60, interval=100)
anim.save(OUTPUT_DIR/"gamma_seg_evolution.gif", writer=PillowWriter(fps=10))
plt.close()
print("   ✅ gamma_seg_evolution.gif")

# Animation 2: Velocity Excess
print("[2/8] Velocity excess...")
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

def anim2(frame):
    ax1.clear(); ax2.clear()
    r_shell = 1.0 + 2.5 * (frame / 60)
    gamma = gamma_seg(r_range)
    v_class = 10 * np.ones_like(r_range)
    v_obs = 10 / gamma
    
    ax1.plot(r_range, v_class, 'b--', linewidth=2, label='Classical')
    ax1.plot(r_range, v_obs, 'r-', linewidth=3, label='SSZ')
    ax1.fill_between(r_range, v_class, v_obs, alpha=0.3, color='orange')
    ax1.axvline(x=r_shell, color='green', linewidth=2, alpha=0.7)
    ax1.set_xlabel('Radius [pc]'); ax1.set_ylabel('Velocity [km/s]')
    ax1.set_title('Velocity Excess Mechanism', fontweight='bold')
    ax1.set_xlim(0, 4.5); ax1.set_ylim(5, 20)
    ax1.legend(); ax1.grid(True, alpha=0.3)
    
    ax2.plot(r_range, gamma, 'purple', linewidth=3)
    ax2.axvline(x=r_shell, color='green', linewidth=2, alpha=0.7)
    ax2.set_xlabel('Radius [pc]'); ax2.set_ylabel('γ_seg')
    ax2.set_xlim(0, 4.5); ax2.set_ylim(0.85, 1.02)
    ax2.grid(True, alpha=0.3)
    plt.tight_layout()

anim = animation.FuncAnimation(fig, anim2, frames=60, interval=100)
anim.save(OUTPUT_DIR/"velocity_excess.gif", writer=PillowWriter(fps=10))
plt.close()
print("   ✅ velocity_excess.gif")

# Animation 3: Energy Release
print("[3/8] Energy release...")
fig, ax = plt.subplots(figsize=(12, 8))

def anim3(frame):
    ax.clear()
    t = frame / 80
    r_boundary = 2.5
    r_particle = 1.0 + 1.5 * t
    v_current = 10 if r_particle < r_boundary else 18.1
    
    ax.axvspan(0, r_boundary, alpha=0.3, color='blue', label='g⁽²⁾ slow time')
    ax.axvspan(r_boundary, 5, alpha=0.3, color='red', label='g⁽¹⁾ normal')
    ax.axvline(x=r_boundary, color='black', linestyle='--', linewidth=3)
    ax.plot(r_particle, 0.5, 'o', markersize=20, color='yellow', markeredgecolor='black', markeredgewidth=2)
    ax.arrow(r_particle, 0.5, v_current/50, 0, head_width=0.05, head_length=0.1, fc='green', ec='green', linewidth=2)
    
    ax.set_xlim(0, 5); ax.set_ylim(0, 1)
    ax.set_xlabel('Radius [pc]', fontsize=14)
    ax.set_title(f'Energy Release (r={r_particle:.2f} pc, v={v_current:.1f} km/s)', fontsize=16, fontweight='bold')
    ax.legend(fontsize=12); ax.set_yticks([])

anim = animation.FuncAnimation(fig, anim3, frames=80, interval=100)
anim.save(OUTPUT_DIR/"energy_release.gif", writer=PillowWriter(fps=10))
plt.close()
print("   ✅ energy_release.gif")

# Animation 4: Core Mass
print("[4/8] Core mass scaling...")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
r_max_vals = np.linspace(0.5, 3.0, 60)

def M_core_calc(r_max):
    r_grid = np.linspace(0.01, r_max, 100)
    gamma_grid = gamma_seg(r_grid)
    rho_eff = (1 - gamma_grid) * 1e-20
    return 4 * np.pi * np.trapz(rho_eff * r_grid**2, r_grid) * (PC_M**3) / M_SUN

def anim4(frame):
    ax1.clear(); ax2.clear()
    r_max = r_max_vals[frame]
    r_plot = np.linspace(0.01, r_max, 200)
    gamma = gamma_seg(r_plot)
    
    ax1.plot(r_plot, gamma, 'b-', linewidth=3)
    ax1.axvline(x=r_max, color='red', linestyle='--', linewidth=2)
    ax1.fill_between(r_plot, gamma, 1, alpha=0.3, color='blue')
    ax1.set_xlabel('Radius [pc]'); ax1.set_ylabel('γ_seg')
    ax1.set_title('Temporal Density', fontweight='bold')
    ax1.set_xlim(0, 3.5); ax1.set_ylim(0.85, 1.02)
    ax1.grid(True, alpha=0.3)
    
    r_cum = r_max_vals[:frame+1]
    M_cum = [M_core_calc(r) for r in r_cum]
    ax2.plot(r_cum, M_cum, 'r-', linewidth=3)
    ax2.plot(r_max, M_core_calc(r_max), 'ro', markersize=12)
    ax2.axhline(y=8.7, color='green', linestyle='--', linewidth=2, label='Paper: 8.7 M_☉')
    ax2.set_xlabel('Radius [pc]'); ax2.set_ylabel('Mass [M_☉]')
    ax2.set_title('Cumulative Core Mass', fontweight='bold')
    ax2.set_xlim(0, 3.5)
    ax2.legend(); ax2.grid(True, alpha=0.3)
    plt.tight_layout()

anim = animation.FuncAnimation(fig, anim4, frames=60, interval=100)
anim.save(OUTPUT_DIR/"core_mass_scaling.gif", writer=PillowWriter(fps=10))
plt.close()
print("   ✅ core_mass_scaling.gif")

# Animation 5: Radio Redshift
print("[5/8] Radio redshift...")
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

def anim5(frame):
    ax1.clear(); ax2.clear()
    r_emit = 0.5 + 3.0 * (frame / 60)
    gamma = gamma_seg(r_range)
    nu0 = 100
    nu_obs = nu0 * gamma
    
    ax1.plot(r_range, nu_obs, 'b-', linewidth=3)
    ax1.axhline(y=nu0, color='gray', linestyle='--')
    ax1.axvline(x=r_emit, color='red', linestyle='--', linewidth=2)
    ax1.axhspan(0, 30, alpha=0.2, color='orange')
    gamma_emit = gamma_seg(r_emit)
    nu_emit = nu0 * gamma_emit
    ax1.plot(r_emit, nu_emit, 'ro', markersize=12)
    ax1.set_xlabel('Radius [pc]'); ax1.set_ylabel('Frequency [GHz]')
    ax1.set_title(f'Radio Redshift (γ={gamma_emit:.3f}, ν={nu_emit:.1f} GHz)', fontweight='bold')
    ax1.set_xlim(0, 4); ax1.set_ylim(0, 105)
    ax1.grid(True, alpha=0.3)
    
    z = (nu0 - nu_obs) / nu_obs
    ax2.plot(r_range, z, 'purple', linewidth=3)
    ax2.axvline(x=r_emit, color='red', linestyle='--', linewidth=2)
    ax2.set_xlabel('Radius [pc]'); ax2.set_ylabel('Redshift z')
    ax2.set_xlim(0, 4); ax2.grid(True, alpha=0.3)
    plt.tight_layout()

anim = animation.FuncAnimation(fig, anim5, frames=60, interval=100)
anim.save(OUTPUT_DIR/"radio_redshift.gif", writer=PillowWriter(fps=10))
plt.close()
print("   ✅ radio_redshift.gif")

print("\n" + "="*80)
print("ANIMATION GENERATION COMPLETE!")
print("="*80)
print(f"\nCreated 5 animations in: {OUTPUT_DIR}")
print("\nFile list:")
for gif in OUTPUT_DIR.glob("*.gif"):
    size_mb = gif.stat().st_size / 1024 / 1024
    print(f"  • {gif.name} ({size_mb:.2f} MB)")
print("\nUsage: Include these GIFs in paper/presentation materials")
print("="*80)
