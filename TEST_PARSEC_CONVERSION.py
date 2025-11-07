#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick test: Parsec conversion in mass integration
"""
import os, sys
os.environ['PYTHONIOENCODING'] = 'utf-8:replace'
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except: pass

import numpy as np
from scipy.integrate import trapezoid

# Physical constants (SI units)
PC_TO_M = 3.0857e16  # meters per parsec
M_SUN_KG = 1.989e30  # kg
C = 2.998e8  # m/s
G = 6.674e-11  # m^3 kg^-1 s^-2

# Parameters from paper
ALPHA = 0.12
R_C = 1.9  # pc

def gamma_seg(r_pc):
    """γ_seg(r) in parsec units"""
    return 1.0 - ALPHA * np.exp(-(r_pc / R_C)**2)

print("="*80)
print("TESTING PARSEC-TO-METER CONVERSION IN MASS INTEGRATION")
print("="*80)

# Integration range in parsec
r_max_pc = 5.0
r_grid_pc = np.linspace(0.01, r_max_pc, 200)

print(f"\nIntegration range: 0.01 to {r_max_pc} pc")
print(f"Number of points: {len(r_grid_pc)}")

# Convert to meters
r_grid_m = r_grid_pc * PC_TO_M
print(f"\nIn meters: {r_grid_m[0]:.3e} to {r_grid_m[-1]:.3e} m")

# Calculate γ_seg
gamma_values = gamma_seg(r_grid_pc)
print(f"\nγ_seg range: {gamma_values.min():.6f} to {gamma_values.max():.6f}")

# Integration: M_core = (c²/G) ∫ γ_seg(r) dr  (Eq. 14 from paper)
# This is a 1D radial integration, NOT 3D spherical!
integrand = gamma_values
M_core_kg = (C**2 / G) * trapezoid(integrand, r_grid_m)
M_core_solar = M_core_kg / M_SUN_KG

print("\n" + "="*80)
print("RESULTS:")
print("="*80)
print(f"M_core (kg):          {M_core_kg:.6e}")
print(f"M_core (solar masses): {M_core_solar:.2f}")
print(f"\nExpected from paper:   8.7 ± 1.5 M_☉")
print(f"Difference:            {abs(M_core_solar - 8.7):.2f} M_☉")

if abs(M_core_solar - 8.7) < 2.0:
    print("\n✅ PASS: Within expected range!")
else:
    print(f"\n⚠️  WARNING: Outside expected range!")

print("="*80)
