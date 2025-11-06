#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌀 Segmented IR Ring Analysis – G79.29+0.46

AUTOMATED PIPELINE: IRSA Catalogs → Ring Profiles → Publication Plots

This script reproduces the complete infrared ring structure analysis
for G79.29+0.46 using AKARI FIS and WISE AllWISE catalog data.

Pipeline Steps:
1️⃣ Load pre-fetched IRSA catalog data
2️⃣ Compute radial distances from nebula center
3️⃣ Bin sources into 0.25 pc rings (0-2 pc range)
4️⃣ Aggregate fluxes/magnitudes per band
5️⃣ Generate CSV outputs (G79_AKARI_RINGS.csv, G79_WISE_RINGS.csv)
6️⃣ Create publication-quality 4-panel figure
7️⃣ Optional: Overlay segmented spacetime model

Usage:
    python RUN_COMPLETE_IR_ANALYSIS.py

Outputs:
    - data/G79_AKARI_RINGS.csv
    - data/G79_WISE_RINGS.csv
    - plots/IR_Ring_Profiles_G79.png
    - Log summary with source counts

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
    from astropy.coordinates import SkyCoord
    import astropy.units as u
    import matplotlib.pyplot as plt
    from matplotlib.gridspec import GridSpec
except ImportError as e:
    print(f"ERROR: Required packages missing: {e}")
    print("\nInstall with:")
    print("  pip install numpy pandas astropy matplotlib")
    sys.exit(1)

# ============================================================================
# CONFIGURATION
# ============================================================================

# G79.29+0.46 Parameters
G79_CENTER = SkyCoord("20h31m41s +40d21m07s", frame="icrs")
G79_DISTANCE = 1.7  # kpc
RING_WIDTH = 0.25  # pc
MAX_RADIUS = 2.0  # pc

# Input files
AKARI_CATALOG = "data/telescope/akari_fis_test.csv"
WISE_CATALOG = "data/telescope/allwise_p3as_psd_test.csv"

# Output files
OUTPUT_DIR_DATA = Path("data")
OUTPUT_DIR_PLOTS = Path("plots")
AKARI_RINGS_CSV = OUTPUT_DIR_DATA / "G79_AKARI_RINGS.csv"
WISE_RINGS_CSV = OUTPUT_DIR_DATA / "G79_WISE_RINGS.csv"
PLOT_FILE = OUTPUT_DIR_PLOTS / "IR_Ring_Profiles_G79.png"

# Bands
AKARI_BANDS = ['flux65', 'flux90', 'flux140', 'flux160']
AKARI_WAVELENGTHS = [65, 90, 140, 160]  # μm
WISE_BANDS = ['w1mpro', 'w2mpro', 'w3mpro', 'w4mpro']
WISE_WAVELENGTHS = [3.4, 4.6, 12, 22]  # μm

# ============================================================================
# STEP 1: LOAD DATA
# ============================================================================

def load_catalogs():
    """Load pre-fetched IRSA catalog data"""
    print("="*80)
    print("STEP 1: LOADING IRSA CATALOG DATA")
    print("="*80)
    
    # Load AKARI
    print(f"\nLoading AKARI FIS catalog...")
    akari_path = Path(AKARI_CATALOG)
    if not akari_path.exists():
        print(f"  ERROR: File not found: {akari_path}")
        return None, None
    
    df_akari = pd.read_csv(akari_path)
    print(f"  ✓ Loaded {len(df_akari)} AKARI sources")
    print(f"  Columns: {list(df_akari.columns)[:10]}...")
    
    # Load WISE
    print(f"\nLoading WISE AllWISE catalog...")
    wise_path = Path(WISE_CATALOG)
    if not wise_path.exists():
        print(f"  ERROR: File not found: {wise_path}")
        return df_akari, None
    
    df_wise = pd.read_csv(wise_path)
    print(f"  ✓ Loaded {len(df_wise)} WISE sources")
    print(f"  Columns: {list(df_wise.columns)[:10]}...")
    
    return df_akari, df_wise

# ============================================================================
# STEP 2: COMPUTE RADIAL DISTANCES
# ============================================================================

def compute_radial_distances(df, ra_col='ra', dec_col='dec'):
    """
    Compute projected distance from G79 center
    
    Returns:
        r_pc: Radial distance in parsecs
    """
    coords = SkyCoord(
        ra=df[ra_col].values * u.deg,
        dec=df[dec_col].values * u.deg,
        frame='icrs'
    )
    
    # Angular separation
    r_ang = coords.separation(G79_CENTER)
    
    # Physical distance in pc
    r_pc = (r_ang.to(u.rad).value * G79_DISTANCE * u.kpc).to(u.pc).value
    
    return r_pc

# ============================================================================
# STEP 3: BIN INTO RINGS
# ============================================================================

def create_ring_bins(max_radius=MAX_RADIUS, ring_width=RING_WIDTH):
    """Create radial bin edges"""
    return np.arange(0, max_radius + ring_width, ring_width)

def bin_sources_into_rings(df, r_pc, bands, ring_edges):
    """
    Group sources into radial bins and aggregate
    
    Returns:
        DataFrame with ring statistics
    """
    rows = []
    
    for i, (r_min, r_max) in enumerate(zip(ring_edges[:-1], ring_edges[1:])):
        mask = (r_pc >= r_min) & (r_pc < r_max)
        n_sources = np.sum(mask)
        
        if n_sources == 0:
            continue
        
        row = {
            'ring': i,
            'r_min_pc': float(r_min),
            'r_max_pc': float(r_max),
            'radius_pc': float(0.5 * (r_min + r_max)),
            'n_sources': int(n_sources)
        }
        
        # Aggregate each band
        for band in bands:
            if band not in df.columns:
                continue
                
            vals = df.loc[mask, band].dropna()
            
            if len(vals) > 0:
                row[f'{band}_mean'] = float(vals.mean())
                row[f'{band}_median'] = float(vals.median())
                row[f'{band}_std'] = float(vals.std())
                row[f'{band}_err'] = float(vals.std() / np.sqrt(len(vals)))
                row[f'{band}_n'] = int(len(vals))
            else:
                row[f'{band}_mean'] = np.nan
                row[f'{band}_median'] = np.nan
                row[f'{band}_std'] = np.nan
                row[f'{band}_err'] = np.nan
                row[f'{band}_n'] = 0
        
        rows.append(row)
    
    return pd.DataFrame(rows)

# ============================================================================
# STEP 4: PROCESS CATALOGS
# ============================================================================

def process_akari(df_akari):
    """Process AKARI FIS catalog"""
    print("\n" + "="*80)
    print("STEP 2-4: PROCESSING AKARI FIS")
    print("="*80)
    
    # Compute radial distances
    print("\nComputing radial distances...")
    r_pc = compute_radial_distances(df_akari)
    print(f"  Radial range: {r_pc.min():.2f} - {r_pc.max():.2f} pc")
    print(f"  Sources within {MAX_RADIUS} pc: {np.sum(r_pc < MAX_RADIUS)}")
    
    # Create bins
    ring_edges = create_ring_bins()
    print(f"\nBinning into {len(ring_edges)-1} rings ({RING_WIDTH} pc width)...")
    
    # Bin sources
    df_rings = bin_sources_into_rings(df_akari, r_pc, AKARI_BANDS, ring_edges)
    print(f"  ✓ Created {len(df_rings)} rings with data")
    
    # Print summary
    print("\n  Ring Summary:")
    for _, row in df_rings.iterrows():
        print(f"    Ring {row['ring']}: r={row['radius_pc']:.2f} pc, "
              f"n={row['n_sources']}, "
              f"flux65={row.get('flux65_mean', np.nan):.1f} Jy")
    
    return df_rings

def process_wise(df_wise):
    """Process WISE AllWISE catalog"""
    print("\n" + "="*80)
    print("STEP 2-4: PROCESSING WISE ALLWISE")
    print("="*80)
    
    # Compute radial distances
    print("\nComputing radial distances...")
    r_pc = compute_radial_distances(df_wise)
    print(f"  Radial range: {r_pc.min():.2f} - {r_pc.max():.2f} pc")
    print(f"  Sources within {MAX_RADIUS} pc: {np.sum(r_pc < MAX_RADIUS)}")
    
    # Create bins
    ring_edges = create_ring_bins()
    print(f"\nBinning into {len(ring_edges)-1} rings ({RING_WIDTH} pc width)...")
    
    # Bin sources
    df_rings = bin_sources_into_rings(df_wise, r_pc, WISE_BANDS, ring_edges)
    print(f"  ✓ Created {len(df_rings)} rings with data")
    
    # Print summary
    print("\n  Ring Summary:")
    for _, row in df_rings.iterrows():
        print(f"    Ring {row['ring']}: r={row['radius_pc']:.2f} pc, "
              f"n={row['n_sources']}, "
              f"W1={row.get('w1mpro_mean', np.nan):.2f} mag")
    
    return df_rings

# ============================================================================
# STEP 5: SAVE CSVs
# ============================================================================

def save_ring_csv(df_rings, output_file, instrument, bands, wavelengths):
    """Save ring profile to CSV with metadata"""
    
    OUTPUT_DIR_DATA.mkdir(exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        # Write metadata header
        f.write(f"# G79.29+0.46 IR Ring Profile - {instrument}\n")
        f.write(f"# Generated by: RUN_COMPLETE_IR_ANALYSIS.py\n")
        f.write(f"# Date: {pd.Timestamp.now()}\n")
        f.write(f"#\n")
        f.write(f"# Object: G79.29+0.46 (LBV nebula in Cygnus X)\n")
        f.write(f"# Center: RA 20:31:41, Dec +40:21:07 (J2000)\n")
        f.write(f"# Distance: {G79_DISTANCE} kpc\n")
        f.write(f"# Ring width: {RING_WIDTH} pc\n")
        f.write(f"# Max radius: {MAX_RADIUS} pc\n")
        f.write(f"#\n")
        f.write(f"# Instrument: {instrument}\n")
        f.write(f"# Bands: {', '.join([f'{w} μm' for w in wavelengths])}\n")
        f.write(f"# Total sources: {df_rings['n_sources'].sum()}\n")
        f.write(f"# Rings with data: {len(df_rings)}\n")
        f.write(f"#\n")
        f.write(f"# Columns:\n")
        f.write(f"#   ring         - Ring index (0=innermost)\n")
        f.write(f"#   r_min_pc     - Inner edge [pc]\n")
        f.write(f"#   r_max_pc     - Outer edge [pc]\n")
        f.write(f"#   radius_pc    - Ring center [pc]\n")
        f.write(f"#   n_sources    - Number of sources in ring\n")
        for band in bands:
            f.write(f"#   {band}_mean   - Mean value\n")
            f.write(f"#   {band}_std    - Standard deviation\n")
            f.write(f"#   {band}_err    - Standard error\n")
            f.write(f"#   {band}_n      - Valid measurements\n")
        f.write(f"#\n")
        
        # Write data
        df_rings.to_csv(f, index=False)
    
    print(f"  ✓ Saved: {output_file}")

# ============================================================================
# STEP 6: CREATE PUBLICATION PLOT
# ============================================================================

def create_publication_plot(df_akari, df_wise, output_file):
    """Create 4-panel publication-quality figure"""
    
    print("\n" + "="*80)
    print("STEP 6: CREATING PUBLICATION PLOT")
    print("="*80)
    
    fig = plt.figure(figsize=(14, 10))
    gs = GridSpec(2, 2, figure=fig, hspace=0.25, wspace=0.25)
    
    # Panel 1: AKARI Flux vs Radius
    ax1 = fig.add_subplot(gs[0, 0])
    
    colors = ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3']
    for band, wl, color in zip(AKARI_BANDS, AKARI_WAVELENGTHS, colors):
        mean_col = f'{band}_mean'
        err_col = f'{band}_err'
        
        if mean_col in df_akari.columns:
            valid = df_akari[mean_col].notna()
            if valid.any():
                ax1.errorbar(
                    df_akari.loc[valid, 'radius_pc'],
                    df_akari.loc[valid, mean_col],
                    yerr=df_akari.loc[valid, err_col],
                    fmt='o-',
                    color=color,
                    label=f'{wl} μm',
                    markersize=8,
                    capsize=5,
                    linewidth=2
                )
    
    ax1.set_xlabel('Radius [pc]', fontsize=11)
    ax1.set_ylabel('Flux [Jy]', fontsize=11)
    ax1.set_title('AKARI FIS Flux Profiles', fontsize=12, fontweight='bold')
    ax1.legend(loc='best', fontsize=9)
    ax1.grid(alpha=0.3)
    ax1.set_xlim(0, MAX_RADIUS+0.2)
    
    # Panel 2: AKARI Source Count
    ax2 = fig.add_subplot(gs[0, 1])
    
    ax2.bar(df_akari['radius_pc'], df_akari['n_sources'],
           width=RING_WIDTH*0.8, color='#e41a1c', alpha=0.6, edgecolor='black')
    ax2.set_xlabel('Radius [pc]', fontsize=11)
    ax2.set_ylabel('Number of Sources', fontsize=11)
    ax2.set_title(f'AKARI Source Distribution (N={df_akari["n_sources"].sum()})',
                  fontsize=12, fontweight='bold')
    ax2.grid(alpha=0.3, axis='y')
    ax2.set_xlim(0, MAX_RADIUS+0.2)
    
    # Panel 3: WISE Magnitude vs Radius
    ax3 = fig.add_subplot(gs[1, 0])
    
    colors_wise = ['#1f78b4', '#33a02c', '#ff7f00', '#e31a1c']
    for band, wl, color in zip(WISE_BANDS, WISE_WAVELENGTHS, colors_wise):
        mean_col = f'{band}_mean'
        err_col = f'{band}_err'
        
        if mean_col in df_wise.columns:
            valid = df_wise[mean_col].notna()
            if valid.any():
                ax3.errorbar(
                    df_wise.loc[valid, 'radius_pc'],
                    df_wise.loc[valid, mean_col],
                    yerr=df_wise.loc[valid, err_col],
                    fmt='o-',
                    color=color,
                    label=f'W{WISE_BANDS.index(band)+1} ({wl} μm)',
                    markersize=6,
                    capsize=3,
                    linewidth=2
                )
    
    ax3.set_xlabel('Radius [pc]', fontsize=11)
    ax3.set_ylabel('Magnitude [mag]', fontsize=11)
    ax3.set_title('WISE Magnitude Profiles (fainter = brighter!)',
                  fontsize=12, fontweight='bold')
    ax3.legend(loc='best', fontsize=9)
    ax3.grid(alpha=0.3)
    ax3.invert_yaxis()
    ax3.set_xlim(0, MAX_RADIUS+0.2)
    
    # Panel 4: WISE Source Count
    ax4 = fig.add_subplot(gs[1, 1])
    
    ax4.bar(df_wise['radius_pc'], df_wise['n_sources'],
           width=RING_WIDTH*0.8, color='#1f78b4', alpha=0.6, edgecolor='black')
    ax4.set_xlabel('Radius [pc]', fontsize=11)
    ax4.set_ylabel('Number of Sources', fontsize=11)
    ax4.set_title(f'WISE Source Distribution (N={df_wise["n_sources"].sum()})',
                  fontsize=12, fontweight='bold')
    ax4.grid(alpha=0.3, axis='y')
    ax4.set_xlim(0, MAX_RADIUS+0.2)
    
    # Main title
    fig.suptitle('G79.29+0.46 IR Ring Profiles from Catalog Point Sources',
                fontsize=16, fontweight='bold', y=0.98)
    
    # Save
    OUTPUT_DIR_PLOTS.mkdir(exist_ok=True)
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"\n✓ Saved plot: {output_file}")
    
    plt.close()

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution pipeline"""
    
    print("="*80)
    print("🌀 SEGMENTED IR RING ANALYSIS – G79.29+0.46")
    print("="*80)
    print("\nAutomated pipeline: IRSA Catalogs → Ring Profiles → Publication Plots")
    print("\nConfiguration:")
    print(f"  Center: {G79_CENTER.to_string('hmsdms')}")
    print(f"  Distance: {G79_DISTANCE} kpc")
    print(f"  Ring width: {RING_WIDTH} pc")
    print(f"  Max radius: {MAX_RADIUS} pc")
    
    # Load data
    df_akari_cat, df_wise_cat = load_catalogs()
    
    if df_akari_cat is None and df_wise_cat is None:
        print("\nERROR: No catalog data found!")
        return 1
    
    # Process AKARI
    if df_akari_cat is not None:
        df_akari_rings = process_akari(df_akari_cat)
        
        # Save CSV
        print("\n" + "="*80)
        print("STEP 5: SAVING AKARI CSV")
        print("="*80)
        save_ring_csv(df_akari_rings, AKARI_RINGS_CSV, "AKARI FIS",
                     AKARI_BANDS, AKARI_WAVELENGTHS)
    else:
        df_akari_rings = None
    
    # Process WISE
    if df_wise_cat is not None:
        df_wise_rings = process_wise(df_wise_cat)
        
        # Save CSV
        print("\n" + "="*80)
        print("STEP 5: SAVING WISE CSV")
        print("="*80)
        save_ring_csv(df_wise_rings, WISE_RINGS_CSV, "WISE AllWISE",
                     WISE_BANDS, WISE_WAVELENGTHS)
    else:
        df_wise_rings = None
    
    # Create plot
    if df_akari_rings is not None and df_wise_rings is not None:
        create_publication_plot(df_akari_rings, df_wise_rings, PLOT_FILE)
    
    # Final summary
    print("\n" + "="*80)
    print("✅ ANALYSIS COMPLETE")
    print("="*80)
    
    print("\n📊 SUMMARY:")
    if df_akari_rings is not None:
        print(f"\nAKARI FIS:")
        print(f"  Total sources: {df_akari_rings['n_sources'].sum()}")
        print(f"  Rings with data: {len(df_akari_rings)}")
        print(f"  Radial coverage: {df_akari_rings['radius_pc'].min():.2f} - "
              f"{df_akari_rings['radius_pc'].max():.2f} pc")
    
    if df_wise_rings is not None:
        print(f"\nWISE AllWISE:")
        print(f"  Total sources: {df_wise_rings['n_sources'].sum()}")
        print(f"  Rings with data: {len(df_wise_rings)}")
        print(f"  Radial coverage: {df_wise_rings['radius_pc'].min():.2f} - "
              f"{df_wise_rings['radius_pc'].max():.2f} pc")
    
    print("\n📁 OUTPUT FILES:")
    if df_akari_rings is not None:
        print(f"  ✓ {AKARI_RINGS_CSV}")
    if df_wise_rings is not None:
        print(f"  ✓ {WISE_RINGS_CSV}")
    if df_akari_rings is not None and df_wise_rings is not None:
        print(f"  ✓ {PLOT_FILE}")
    
    print("\n🎯 NEXT STEPS:")
    print("  1. Validate ring profiles")
    print("  2. Fit γ_seg(r) model:")
    print("     python scripts/test_segmented_spacetime_full.py")
    print("  3. Compare with NH3/CO data")
    
    print("\n" + "="*80)
    print("Done! Publication-ready CSVs and plots created.")
    print("="*80)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
