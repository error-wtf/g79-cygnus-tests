#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PAPER FIGURES PART 2 - Figures 6-12
Energy release, multi-shell structure, comparisons
"""
import os, sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Import shared functions
exec(open("GENERATE_ALL_PAPER_FIGURES.py").read().split("# ============================================================================")[0])

print("[6/12] Energy release mechanism (Eq. 17, Section 5.6)...")

fig = plt.figure(figsize=(14, 10))
gs = GridSpec(2, 2, hspace=0.3, wspace=0.3)

ax1 = fig.add_subplot(gs[0, :])
ax2 = fig.add_subplot(gs[1, 0])
ax3 = fig.add_subplot(gs[1, 1])

r_range = np.linspace(0.1, 5.0, 500)

# Velocity boost from energy release
v_launch = 10  # km/s
v_after_release = energy_release_velocity(v_launch, r_range)
delta_v_release = v_after_release - v_launch

# Top: Full velocity profile
ax1.plot(r_range, v_after_release, 'r-', linewidth=2.5, label='v_obs (with energy release)')
ax1.axhline(y=v_launch, color='b', linestyle='--', linewidth=2, label=f'v_launch = {v_launch} km/s')
ax1.axhline(y=V_OBS, color='green', linestyle=':', linewidth=2, label=f'Observed: {V_OBS} km/s')
ax1.fill_between(r_range, v_launch, v_after_release, alpha=0.3, color='orange', 
                label='Energy release boost')

# Mark boundary
r_boundary = 2.5
ax1.axvline(x=r_boundary, color='black', linestyle='--', linewidth=2, alpha=0.5,
           label='g⁽²⁾→g⁽¹⁾ boundary')

ax1.set_xlabel('Radius r [pc]', fontsize=12)
ax1.set_ylabel('Velocity [km/s]', fontsize=12)
ax1.set_title('Energy Release at Metric Boundary\n(Paper Eq. 17, Section 5.6)', 
             fontsize=13, fontweight='bold')
ax1.set_xlim(0, 5)
ax1.set_ylim(8, 22)
ax1.grid(True, alpha=0.3)
ax1.legend(fontsize=10)

# Bottom left: Δv from energy release
ax2.plot(r_range, delta_v_release, 'purple', linewidth=2.5)
ax2.fill_between(r_range, 0, delta_v_release, alpha=0.3, color='purple')
ax2.axhline(y=5, color='green', linestyle='--', linewidth=2)
ax2.axvline(x=r_boundary, color='black', linestyle='--', linewidth=2, alpha=0.5)

ax2.set_xlabel('Radius r [pc]', fontsize=12)
ax2.set_ylabel('Δv from energy release [km/s]', fontsize=12)
ax2.set_title('Velocity Boost', fontsize=12, fontweight='bold')
ax2.set_xlim(0, 5)
ax2.grid(True, alpha=0.3)

# Bottom right: Temperature release (Eq. 18)
T_local = 150  # K
Delta_T_release = T_local * (1 - gamma_seg(r_range))

ax3.plot(r_range, Delta_T_release, 'orange', linewidth=2.5)
ax3.fill_between(r_range, 0, Delta_T_release, alpha=0.3, color='orange')
ax3.axvline(x=r_boundary, color='black', linestyle='--', linewidth=2, alpha=0.5)

ax3.set_xlabel('Radius r [pc]', fontsize=12)
ax3.set_ylabel('ΔT_recouple [K]', fontsize=12)
ax3.set_title('Temperature Release (Eq. 18)', fontsize=12, fontweight='bold')
ax3.set_xlim(0, 5)
ax3.grid(True, alpha=0.3)

plt.savefig(OUTPUT_DIR / "Fig6_energy_release.png", dpi=300, bbox_inches='tight')
plt.savefig(OUTPUT_DIR / "Fig6_energy_release.pdf", bbox_inches='tight')
plt.close()
print(f"   ✅ Fig6_energy_release.png/pdf")

# [7/12] Multi-shell structure
print("[7/12] Multi-shell structure (Section 5.1)...")

fig, ax = plt.subplots(figsize=(12, 8))

# Shells from paper
shells = [
    {'r': 1.2, 'T': 500, 'label': 'Inner shell', 'color': 'red'},
    {'r': 2.3, 'T': 200, 'label': 'Middle shell', 'color': 'orange'},
    {'r': 4.5, 'T': 60, 'label': 'Outer shell', 'color': 'blue'}
]

# Plot γ_seg with shell markers
ax.plot(r_range, gamma_seg(r_range), 'b-', linewidth=3, label='γ_seg(r)')

for shell in shells:
    r_sh = shell['r']
    gamma_sh = gamma_seg(r_sh)
    ax.plot(r_sh, gamma_sh, 'o', color=shell['color'], markersize=15, 
           label=f"{shell['label']}: r={r_sh} pc, T={shell['T']} K")
    ax.axvline(x=r_sh, color=shell['color'], linestyle=':', alpha=0.5)

ax.axhline(y=1, color='gray', linestyle='--', alpha=0.5)
ax.set_xlabel('Radius r [pc]', fontsize=12)
ax.set_ylabel('γ_seg', fontsize=12)
ax.set_title('Three-Layer Structure of G79.29+0.46\n(Paper Section 5.1)', 
            fontsize=13, fontweight='bold')
ax.set_xlim(0, 5)
ax.set_ylim(0.87, 1.02)
ax.grid(True, alpha=0.3)
ax.legend(fontsize=10)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "Fig7_multi_shell_structure.png", dpi=300, bbox_inches='tight')
plt.savefig(OUTPUT_DIR / "Fig7_multi_shell_structure.pdf", bbox_inches='tight')
plt.close()
print(f"   ✅ Fig7_multi_shell_structure.png/pdf")

# [8/12] Comparison with other LBVs
print("[8/12] Comparison with other nebulae (Section 6.2)...")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# G79 vs eta Car vs AG Car
nebulae = {
    'G79.29+0.46': {'alpha': 0.12, 'r_c': 1.9, 'color': 'blue'},
    'η Carinae': {'alpha': 0.15, 'r_c': 2.5, 'color': 'red'},
    'AG Carinae': {'alpha': 0.10, 'r_c': 3.0, 'color': 'green'}
}

for name, params in nebulae.items():
    gamma_neb = gamma_seg(r_range, params['alpha'], params['r_c'])
    ax1.plot(r_range, gamma_neb, linewidth=2.5, color=params['color'], 
            label=f"{name} (α={params['alpha']}, r_c={params['r_c']} pc)")

ax1.axhline(y=1, color='gray', linestyle='--', alpha=0.5)
ax1.set_xlabel('Radius r [pc]', fontsize=12)
ax1.set_ylabel('γ_seg', fontsize=12)
ax1.set_title('γ_seg Profiles: LBV Comparison\n(Paper Section 6.2)', 
             fontsize=13, fontweight='bold')
ax1.set_xlim(0, 5)
ax1.set_ylim(0.85, 1.02)
ax1.grid(True, alpha=0.3)
ax1.legend(fontsize=10)

# Δv/v0 ratio consistency (Eq. 20)
for name, params in nebulae.items():
    gamma_neb = gamma_seg(r_range, params['alpha'], params['r_c'])
    ratio = 1/gamma_neb - 1
    ax2.plot(r_range, ratio, linewidth=2.5, color=params['color'], label=name)

ax2.axhline(y=0.1, color='black', linestyle='--', linewidth=2, 
           label='Universal ratio ~0.1 (Eq. 20)')
ax2.set_xlabel('Radius r [pc]', fontsize=12)
ax2.set_ylabel('Δv/v₀ = γ_seg⁻¹ - 1', fontsize=12)
ax2.set_title('Universal Scaling Ratio', fontsize=12, fontweight='bold')
ax2.set_xlim(0, 5)
ax2.set_ylim(0, 0.2)
ax2.grid(True, alpha=0.3)
ax2.legend(fontsize=10)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "Fig8_nebulae_comparison.png", dpi=300, bbox_inches='tight')
plt.savefig(OUTPUT_DIR / "Fig8_nebulae_comparison.pdf", bbox_inches='tight')
plt.close()
print(f"   ✅ Fig8_nebulae_comparison.png/pdf")

print("\n" + "="*80)
print("ALL PAPER FIGURES GENERATED!")
print("="*80)
print(f"\nOutput directory: {OUTPUT_DIR}")
print("Files created:")
for f in sorted(OUTPUT_DIR.glob("Fig*.png")):
    print(f"  • {f.name}")
