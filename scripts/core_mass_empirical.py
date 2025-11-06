#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Core Mass - Empirical Calibration

Statt theoretischer Ableitung: Kalibrierung an bekannten Werten
M_virial = 8.7 M_sun (Rizzo+ 2014)

© 2025 Carmen N. Wrede, Lino P. Casu
"""
import os
import sys

os.environ['PYTHONIOENCODING'] = 'utf-8:replace'
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass

import numpy as np
import matplotlib.pyplot as plt

def gamma_seg(r, alpha=0.12, r_c=1.9):
    """Temporal density field"""
    return 1.0 - alpha * np.exp(-(r/r_c)**2)

def core_mass_empirical(alpha=0.12, r_c=1.9, R_boundary=0.5, M_calibration=8.7):
    """
    Empirical core mass based on virial mass calibration
    
    Ansatz:
    M_core ∝ α × r_c²  (from dimensional analysis)
    
    Kalibriert an M_virial(G79) = 8.7 M_sun mit (α=0.12, r_c=1.9 pc)
    
    Args:
        alpha: segmentation depth
        r_c: characteristic radius (pc)
        R_boundary: effective boundary (not used in scaling)
        M_calibration: reference mass (M_sun)
    
    Returns:
        M_core in M_sun
    """
    # Reference values (G79)
    alpha_ref = 0.12
    r_c_ref = 1.9  # pc
    M_ref = 8.7  # M_sun
    
    # Scaling law
    M_core = M_ref * (alpha / alpha_ref) * (r_c / r_c_ref)**2
    
    return M_core

def test_G79_empirical():
    """Test empirical formula"""
    print("="*80)
    print("CORE MASS - Empirical Calibration")
    print("="*80)
    
    # G79 parameters
    alpha = 0.12
    r_c = 1.9
    R_boundary = 0.5
    
    M_core = core_mass_empirical(alpha, r_c, R_boundary)
    
    print(f"\nParameters:")
    print(f"  α = {alpha}")
    print(f"  r_c = {r_c} pc")
    print(f"  R_boundary = {R_boundary} pc")
    
    print(f"\n{'='*80}")
    print(f"RESULT:")
    print(f"{'='*80}")
    print(f"\n  M_core = {M_core:.2f} M_sun (by calibration)")
    
    # Literature
    M_virial = 8.7
    print(f"\n  M_virial (literature) = {M_virial} M_sun")
    print(f"  Match: {np.abs(M_core - M_virial):.2f} M_sun")
    
    # Scaling tests
    print(f"\n{'='*80}")
    print(f"SCALING PREDICTIONS FOR OTHER OBJECTS:")
    print(f"{'='*80}")
    
    print(f"\nIf α varies (fixed r_c = {r_c} pc):")
    for a in [0.08, 0.10, 0.12, 0.15]:
        M = core_mass_empirical(a, r_c, R_boundary)
        print(f"  α = {a:.2f} → M_core ≈ {M:.1f} M_sun")
    
    print(f"\nIf r_c varies (fixed α = {alpha}):")
    for rc in [1.5, 1.7, 1.9, 2.5, 3.0]:
        M = core_mass_empirical(alpha, rc, R_boundary)
        print(f"  r_c = {rc:.1f} pc → M_core ≈ {M:.1f} M_sun")
    
    print(f"\n{'='*80}")
    print(f"PHYSICAL INTERPRETATION:")
    print(f"{'='*80}")
    print(f"\n  • M_core ∝ α × r_c²")
    print(f"  • Larger α (deeper segmentation) → more mass")
    print(f"  • Larger r_c (wider core) → quadratically more mass")
    print(f"  • Consistent with virial estimates from NH3")
    
    return M_core

def plot_mass_scaling():
    """Plot M_core vs α and r_c"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Left: vs alpha
    alpha_range = np.linspace(0.05, 0.20, 50)
    M_vs_alpha = [core_mass_empirical(a, 1.9, 0.5) for a in alpha_range]
    
    ax1.plot(alpha_range, M_vs_alpha, 'b-', lw=2)
    ax1.axvline(0.12, color='red', ls='--', lw=2, label='G79 (α=0.12)')
    ax1.axhline(8.7, color='green', ls='--', lw=2, label='M_virial = 8.7 M_sun')
    ax1.set_xlabel('α (segmentation depth)', fontsize=12)
    ax1.set_ylabel('M_core [M_sun]', fontsize=12)
    ax1.set_title('Core Mass vs α (r_c = 1.9 pc)', fontsize=14, weight='bold')
    ax1.legend()
    ax1.grid(alpha=0.3)
    
    # Right: vs r_c
    r_c_range = np.linspace(1.0, 3.5, 50)
    M_vs_rc = [core_mass_empirical(0.12, rc, 0.5) for rc in r_c_range]
    
    ax2.plot(r_c_range, M_vs_rc, 'b-', lw=2)
    ax2.axvline(1.9, color='red', ls='--', lw=2, label='G79 (r_c=1.9 pc)')
    ax2.axhline(8.7, color='green', ls='--', lw=2, label='M_virial = 8.7 M_sun')
    ax2.set_xlabel('r_c [pc]', fontsize=12)
    ax2.set_ylabel('M_core [M_sun]', fontsize=12)
    ax2.set_title('Core Mass vs r_c (α = 0.12)', fontsize=14, weight='bold')
    ax2.legend()
    ax2.grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('results/core_mass_scaling_empirical.png', dpi=300, bbox_inches='tight')
    print(f"\n✓ Plot saved: results/core_mass_scaling_empirical.png")
    plt.show()

if __name__ == "__main__":
    M_core = test_G79_empirical()
    plot_mass_scaling()
    
    print(f"\n{'='*80}")
    print(f"SUMMARY:")
    print(f"{'='*80}")
    print(f"\n  ✅ Empirische Formel: M_core = 8.7 × (α/0.12) × (r_c/1.9)² M_sun")
    print(f"  ✅ Für G79: M_core = {M_core:.1f} M_sun (by design)")
    print(f"  ✅ Skaliert auf andere LBVs anwendbar")
    print(f"\n  Next: Validierung an η Car, AG Car, etc.")
    print(f"\n{'='*80}")
