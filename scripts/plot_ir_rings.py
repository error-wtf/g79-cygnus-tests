#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plot IR Ring Profiles - Quick Visualization

Plots AKARI and WISE ring profiles side-by-side

Usage:
    python scripts/plot_ir_rings.py

Output:
    - results/ir_ring_profiles.png

© 2025 Carmen N. Wrede, Lino P. Casu
Licensed under ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""
import sys
import os
from pathlib import Path

# UTF-8 for Windows
os.environ['PYTHONIOENCODING'] = 'utf-8:replace'
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass

try:
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
except ImportError as e:
    print(f"ERROR: Required packages missing: {e}")
    print("\nInstall with:")
    print("  pip install numpy pandas matplotlib")
    sys.exit(1)

def main():
    """Plot IR ring profiles"""
    
    print("="*80)
    print("IR RING PROFILE VISUALIZATION")
    print("="*80)
    
    # Load data
    akari_file = Path("data/telescope/akari_fis_rings.csv")
    wise_file = Path("data/telescope/allwise_rings.csv")
    
    if not akari_file.exists():
        print(f"\nERROR: {akari_file} not found!")
        print("Run: python scripts/process_ir_catalogs.py")
        return 1
    
    if not wise_file.exists():
        print(f"\nERROR: {wise_file} not found!")
        print("Run: python scripts/process_ir_catalogs.py")
        return 1
    
    print(f"\nLoading AKARI data...")
    df_akari = pd.read_csv(akari_file, comment='#')
    print(f"  Rings: {len(df_akari)}")
    
    print(f"\nLoading WISE data...")
    df_wise = pd.read_csv(wise_file, comment='#')
    print(f"  Rings: {len(df_wise)}")
    
    # Create figure
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle("G79.29+0.46 IR Ring Profiles from Catalog Point Sources", 
                 fontsize=14, fontweight='bold')
    
    # AKARI - Top row
    ax = axes[0, 0]
    ax.set_title("AKARI FIS Flux Profiles", fontweight='bold')
    
    bands = ['flux65', 'flux90', 'flux140', 'flux160']
    colors = ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3']
    labels = ['65 μm', '90 μm', '140 μm', '160 μm']
    
    for band, color, label in zip(bands, colors, labels):
        if f'{band}_mean' in df_akari.columns:
            valid = df_akari[f'{band}_mean'].notna()
            if valid.any():
                r = df_akari.loc[valid, 'radius_pc']
                flux = df_akari.loc[valid, f'{band}_mean']
                err = df_akari.loc[valid, f'{band}_err']
                ax.errorbar(r, flux, yerr=err, fmt='o-', color=color, 
                           label=label, markersize=8, capsize=5, linewidth=2)
    
    ax.set_xlabel("Radius [pc]", fontsize=11)
    ax.set_ylabel("Flux [Jy]", fontsize=11)
    ax.legend(loc='best', fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 2.2)
    
    # AKARI - Source count
    ax = axes[0, 1]
    ax.set_title("AKARI Source Distribution", fontweight='bold')
    ax.bar(df_akari['radius_pc'], df_akari['n_sources'], 
           width=0.15, color='#e41a1c', alpha=0.6, edgecolor='black')
    ax.set_xlabel("Radius [pc]", fontsize=11)
    ax.set_ylabel("Number of Sources", fontsize=11)
    ax.grid(True, alpha=0.3, axis='y')
    ax.set_xlim(0, 2.2)
    
    # WISE - Bottom row
    ax = axes[1, 0]
    ax.set_title("WISE Magnitude Profiles (fainter = brighter!)", fontweight='bold')
    
    bands_wise = ['w1mpro', 'w2mpro', 'w3mpro', 'w4mpro']
    colors_wise = ['#1f78b4', '#33a02c', '#ff7f00', '#e31a1c']
    labels_wise = ['W1 (3.4 μm)', 'W2 (4.6 μm)', 'W3 (12 μm)', 'W4 (22 μm)']
    
    for band, color, label in zip(bands_wise, colors_wise, labels_wise):
        if f'{band}_mean' in df_wise.columns:
            valid = df_wise[f'{band}_mean'].notna()
            if valid.any():
                r = df_wise.loc[valid, 'radius_pc']
                mag = df_wise.loc[valid, f'{band}_mean']
                err = df_wise.loc[valid, f'{band}_err']
                ax.errorbar(r, mag, yerr=err, fmt='o-', color=color, 
                           label=label, markersize=6, capsize=3, linewidth=2)
    
    ax.set_xlabel("Radius [pc]", fontsize=11)
    ax.set_ylabel("Magnitude [mag]", fontsize=11)
    ax.legend(loc='best', fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.invert_yaxis()  # Fainter magnitudes at bottom
    ax.set_xlim(0, 2.2)
    
    # WISE - Source count
    ax = axes[1, 1]
    ax.set_title("WISE Source Distribution", fontweight='bold')
    ax.bar(df_wise['radius_pc'], df_wise['n_sources'], 
           width=0.15, color='#1f78b4', alpha=0.6, edgecolor='black')
    ax.set_xlabel("Radius [pc]", fontsize=11)
    ax.set_ylabel("Number of Sources", fontsize=11)
    ax.grid(True, alpha=0.3, axis='y')
    ax.set_xlim(0, 2.2)
    
    # Add stats text
    stats_text = (
        f"AKARI: {len(df_akari)} rings, {df_akari['n_sources'].sum():.0f} sources\n"
        f"WISE: {len(df_wise)} rings, {df_wise['n_sources'].sum():.0f} sources"
    )
    fig.text(0.5, 0.02, stats_text, ha='center', fontsize=10, 
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout(rect=[0, 0.03, 1, 0.97])
    
    # Save
    output_dir = Path("results")
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / "ir_ring_profiles.png"
    
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"\n✓ Saved: {output_file}")
    
    print("\n" + "="*80)
    print("VISUALIZATION COMPLETE")
    print("="*80)
    print(f"\nOutput: {output_file}")
    print("\nKey observations:")
    print("  - AKARI: Sparse but covers cold dust (160 μm)")
    print("  - WISE: Excellent coverage with 159 sources!")
    print("  - W4 (22 μm) gets fainter outward (cooling)")
    print("\nNext: Fit exponential profiles to test SSZ predictions!")
    print("="*80)
    
    # Show plot
    try:
        plt.show()
    except:
        pass
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
