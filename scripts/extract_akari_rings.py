#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extract Rings from AKARI 90 μm FITS - CONCRETE for G79!

Based on Carmen's exact method for 2D FITS images.
This script is ready to run with G79 AKARI data!

Usage:
    python extract_akari_rings.py G79_akari_fis_90um.fits
    
Output:
    G79_akari_90um_rings_REAL.csv

Carmen's method:
1. Load FITS + WCS
2. Calculate r_pc from G79 center
3. Define ring edges (0-2 pc, 0.2 pc spacing)
4. Average intensity in each ring
5. Save to CSV

© 2025 Carmen N. Wrede, Lino P. Casu
Method: Carmen's "FITS → Rings" workflow
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
    from astropy.io import fits
    from astropy.wcs import WCS
    from astropy.coordinates import SkyCoord
    import astropy.units as u
except ImportError as e:
    print(f"ERROR: Required packages missing: {e}")
    print("\nInstall with:")
    print("  pip install numpy pandas astropy")
    sys.exit(1)

# G79.29+0.46 parameters (Carmen's exact values!)
G79_CENTER = SkyCoord("20h31m41s +40d21m07s", frame="icrs")
G79_DISTANCE = 1.7  # kpc

# Ring edges (Carmen's recommendation: 0-2 pc in 0.2 pc steps)
r_edges_pc = np.arange(0.0, 2.0 + 0.2, 0.2)

def main():
    """Main extraction function"""
    
    if len(sys.argv) < 2:
        print("Usage: python extract_akari_rings.py <FITS_file>")
        print("\nExample:")
        print("  python extract_akari_rings.py G79_akari_fis_90um.fits")
        return 1
    
    fits_file = sys.argv[1]
    fits_path = Path(fits_file)
    
    if not fits_path.exists():
        print(f"ERROR: File not found: {fits_path}")
        return 1
    
    # Auto-generate output name
    output_csv = fits_path.stem + "_rings_REAL.csv"
    
    print("="*80)
    print("AKARI RING EXTRACTION - Carmen's Method")
    print("="*80)
    print(f"\nInput:  {fits_path}")
    print(f"Output: {output_csv}")
    print(f"\nG79 Center: {G79_CENTER.to_string('hmsdms')}")
    print(f"Distance:   {G79_DISTANCE} kpc")
    print(f"Rings:      {len(r_edges_pc)-1} rings (0-2 pc, 0.2 pc spacing)")
    
    # Load FITS
    print(f"\n[1/4] Loading FITS file...")
    try:
        hdu = fits.open(fits_path)[0]
        data = hdu.data
        wcs = WCS(hdu.header)
    except Exception as e:
        print(f"ERROR loading FITS: {e}")
        return 1
    
    print(f"   Image size: {data.shape}")
    print(f"   Data range: {np.nanmin(data):.3e} - {np.nanmax(data):.3e}")
    
    # Calculate radial distances
    print(f"\n[2/4] Calculating radial distances...")
    
    ny, nx = data.shape
    y_idx, x_idx = np.indices(data.shape)
    
    # Convert pixels to sky coordinates
    ra, dec = wcs.all_pix2world(x_idx, y_idx, 0)
    coords = SkyCoord(ra*u.deg, dec*u.deg, frame="icrs")
    
    # Angular separation from G79 center
    r_ang = coords.separation(G79_CENTER)
    
    # Physical distance in pc
    r_pc = (r_ang.to(u.rad) * (G79_DISTANCE * u.kpc)).to(u.pc).value
    
    print(f"   Radial range: {r_pc.min():.2f} - {r_pc.max():.2f} pc")
    
    # Extract rings
    print(f"\n[3/4] Extracting {len(r_edges_pc)-1} rings...")
    
    rows = []
    for ring_idx, (r_min, r_max) in enumerate(zip(r_edges_pc[:-1], r_edges_pc[1:])):
        mask = (r_pc >= r_min) & (r_pc < r_max) & np.isfinite(data)
        
        if np.any(mask):
            vals = data[mask]
            I_mean = np.nanmean(vals)
            I_std = np.nanstd(vals)
            I_median = np.nanmedian(vals)
            n_pixels = np.sum(mask)
            
            rows.append({
                "ring": ring_idx,
                "r_min_pc": float(r_min),
                "r_max_pc": float(r_max),
                "radius_pc": float(0.5 * (r_min + r_max)),
                "I_mean": float(I_mean),
                "I_median": float(I_median),
                "I_std": float(I_std),
                "I_err": float(I_std / np.sqrt(n_pixels)),
                "n_pixels": int(n_pixels),
            })
            
            print(f"   Ring {ring_idx}: r={r_min:.1f}-{r_max:.1f} pc, "
                  f"I={I_mean:.3e} ± {I_std:.3e}, n={n_pixels}")
        else:
            print(f"   Ring {ring_idx}: r={r_min:.1f}-{r_max:.1f} pc - NO DATA")
    
    # Save CSV
    print(f"\n[4/4] Saving CSV...")
    
    df = pd.DataFrame(rows)
    
    with open(output_csv, 'w', encoding='utf-8') as f:
        f.write("# G79.29+0.46 Ring Profile from FITS\n")
        f.write(f"# Source file: {fits_path.name}\n")
        f.write(f"# Center: RA 20:31:41, Dec +40:21:07 (J2000)\n")
        f.write(f"# Distance: {G79_DISTANCE} kpc\n")
        f.write(f"# Ring spacing: 0.2 pc\n")
        f.write(f"# Extraction method: Carmen's radial averaging\n")
        f.write(f"# Date: {pd.Timestamp.now()}\n")
        f.write("#\n")
        f.write("# Columns:\n")
        f.write("#   ring        - Ring index (0=innermost)\n")
        f.write("#   r_min_pc    - Inner edge [pc]\n")
        f.write("#   r_max_pc    - Outer edge [pc]\n")
        f.write("#   radius_pc   - Ring center [pc]\n")
        f.write("#   I_mean      - Mean intensity\n")
        f.write("#   I_median    - Median intensity\n")
        f.write("#   I_std       - Standard deviation\n")
        f.write("#   I_err       - Standard error (std/sqrt(n))\n")
        f.write("#   n_pixels    - Number of pixels\n")
        f.write("#\n")
        df.to_csv(f, index=False)
    
    print(f"   ✓ Saved: {output_csv}")
    print(f"   ✓ Extracted {len(df)} rings!")
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"\nRings extracted: {len(df)}")
    print(f"Radial coverage: {df['radius_pc'].min():.2f} - {df['radius_pc'].max():.2f} pc")
    print(f"Intensity range: {df['I_mean'].min():.3e} - {df['I_mean'].max():.3e}")
    
    print(f"\nNext steps:")
    print(f"1. Validate: Check {output_csv} looks reasonable")
    print(f"2. Convert to temperature (if dust continuum)")
    print(f"3. Fit γ_seg(r): python fit_gamma_seg_profile.py {output_csv}")
    
    print("\n" + "="*80)
    print("DONE! Real telescope data → Ring profile! 🎉")
    print("="*80)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
