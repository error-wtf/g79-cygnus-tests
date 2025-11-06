#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FITS to Ring Profile - Complete Pipeline

Converts FITS images/cubes to radial ring profiles.
Based on real telescope data workflow.

Usage:
    # 2D image (e.g., AKARI, Herschel continuum)
    python fits_to_ring_profile.py G79_akari_90um.fits --output G79_akari_rings.csv
    
    # 3D cube (e.g., CO, [CII])
    python fits_to_ring_profile.py G79_co32_cube.fits --cube --output G79_co_rings.csv

© 2025 Carmen N. Wrede, Lino P. Casu
Licensed under ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""
import sys
import os
import argparse
from pathlib import Path

# UTF-8 for Windows
os.environ['PYTHONIOENCODING'] = 'utf-8:replace'
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass

# Check imports
try:
    import numpy as np
    from astropy.io import fits
    from astropy.wcs import WCS
    from astropy.coordinates import SkyCoord
    import astropy.units as u
    import pandas as pd
    HAS_ASTROPY = True
except ImportError as e:
    print(f"ERROR: Required packages missing: {e}")
    print("\nInstall with:")
    print("  pip install astropy pandas numpy")
    sys.exit(1)

# G79.29+0.46 center (CORRECT coordinates!)
G79_CENTER = SkyCoord("20h31m41s", "+40d21m07s", frame="icrs")
G79_DISTANCE = 1.7 * u.kpc

def load_fits_2d(fits_file):
    """
    Load 2D FITS image
    
    Returns: data, wcs, header
    """
    print(f"\n[1/5] Loading 2D FITS: {fits_file}")
    
    hdu = fits.open(fits_file)[0]
    data = hdu.data
    header = hdu.header
    wcs = WCS(header)
    
    print(f"   Shape: {data.shape}")
    print(f"   Min: {np.nanmin(data):.3e}, Max: {np.nanmax(data):.3e}")
    
    return data, wcs, header

def calculate_radial_distance(data, wcs, center_coord, distance):
    """
    Calculate radial distance from center for each pixel
    
    Args:
        data: 2D array
        wcs: WCS object
        center_coord: SkyCoord of center
        distance: Distance to source (with units)
    
    Returns:
        r_pc: Radial distance in parsecs for each pixel
    """
    print("\n[2/5] Calculating radial distances...")
    
    # Get pixel coordinates
    ny, nx = data.shape
    y_idx, x_idx = np.indices(data.shape)
    
    # Convert to world coordinates
    ra, dec = wcs.all_pix2world(x_idx, y_idx, 0)
    coords = SkyCoord(ra*u.deg, dec*u.deg, frame="icrs")
    
    # Calculate angular separation from center
    r_ang = coords.separation(center_coord)
    
    # Convert to physical distance
    r_pc = (r_ang.to(u.rad) * distance).to(u.pc)
    
    print(f"   Center: {center_coord.to_string('hmsdms')}")
    print(f"   Distance: {distance}")
    print(f"   Radial range: {np.nanmin(r_pc):.3f} - {np.nanmax(r_pc):.3f}")
    
    return r_pc.value

def create_ring_profile_2d(data, r_pc, r_edges):
    """
    Create radial profile by averaging in rings
    
    Args:
        data: 2D intensity array
        r_pc: Radial distance for each pixel [pc]
        r_edges: Ring edges [pc]
    
    Returns:
        DataFrame with ring profile
    """
    print("\n[3/5] Creating ring profile...")
    print(f"   Ring edges: {r_edges[0]:.2f} - {r_edges[-1]:.2f} pc")
    print(f"   Number of rings: {len(r_edges)-1}")
    
    rows = []
    
    for ring_idx, (r_min, r_max) in enumerate(zip(r_edges[:-1], r_edges[1:])):
        # Mask for this ring
        mask = (r_pc >= r_min) & (r_pc < r_max) & np.isfinite(data)
        
        if np.any(mask):
            vals = data[mask]
            n_pixels = len(vals)
            
            # Statistics
            I_mean = np.nanmean(vals)
            I_std = np.nanstd(vals)
            I_median = np.nanmedian(vals)
            I_min = np.nanmin(vals)
            I_max = np.nanmax(vals)
            
            # Standard error of mean
            I_sem = I_std / np.sqrt(n_pixels) if n_pixels > 1 else I_std
            
            rows.append({
                "ring": ring_idx,
                "radius_pc": float(0.5*(r_min + r_max)),
                "r_inner_pc": float(r_min),
                "r_outer_pc": float(r_max),
                "I_mean": float(I_mean),
                "I_std": float(I_std),
                "I_sem": float(I_sem),
                "I_median": float(I_median),
                "I_min": float(I_min),
                "I_max": float(I_max),
                "n_pixels": int(n_pixels)
            })
            
            print(f"   Ring {ring_idx}: r={0.5*(r_min+r_max):.2f} pc, "
                  f"I={I_mean:.3e} ± {I_sem:.3e}, n={n_pixels}")
        else:
            print(f"   Ring {ring_idx}: r={0.5*(r_min+r_max):.2f} pc - NO DATA")
    
    df = pd.DataFrame(rows)
    print(f"\n   Created profile with {len(df)} rings")
    
    return df

def create_ring_profile_3d(cube_file, r_edges, center_coord, distance):
    """
    Create ring profile from 3D spectral cube
    
    This extracts both intensity and velocity information
    
    Args:
        cube_file: Path to FITS cube
        r_edges: Ring edges [pc]
        center_coord: SkyCoord of center
        distance: Distance to source
    
    Returns:
        DataFrame with ring profile including velocities
    """
    print("\n[CUBE MODE] Loading 3D spectral cube...")
    
    try:
        from spectral_cube import SpectralCube
        from astropy.modeling import models, fitting
    except ImportError:
        print("ERROR: spectral-cube not installed!")
        print("Install with: pip install spectral-cube")
        return None
    
    # Load cube
    cube = SpectralCube.read(cube_file)
    
    # Convert to km/s if possible
    try:
        cube = cube.with_spectral_unit(u.km/u.s)
        vel = cube.spectral_axis.value
        print(f"   Velocity range: {vel[0]:.1f} - {vel[-1]:.1f} km/s")
    except:
        vel = np.arange(cube.shape[0])
        print("   WARNING: Could not convert to km/s, using channel numbers")
    
    # Calculate radial distances for spatial plane
    wcs_spatial = cube.wcs.celestial
    ny, nx = cube.shape[1:]
    y_idx, x_idx = np.indices((ny, nx))
    
    ra, dec = wcs_spatial.all_pix2world(x_idx, y_idx, 0)
    coords = SkyCoord(ra*u.deg, dec*u.deg, frame="icrs")
    r_ang = coords.separation(center_coord)
    r_pc = (r_ang.to(u.rad) * distance).to(u.pc).value
    
    print(f"   Spatial range: {np.nanmin(r_pc):.3f} - {np.nanmax(r_pc):.3f} pc")
    
    # Extract ring profiles
    rows = []
    
    for ring_idx, (r_min, r_max) in enumerate(zip(r_edges[:-1], r_edges[1:])):
        mask = (r_pc >= r_min) & (r_pc < r_max)
        
        if np.any(mask):
            # Average spectrum in this ring
            subcube = cube[:, mask]
            spectrum = subcube.mean(axis=(1,))
            y = spectrum.value
            
            # Simple Gaussian fit to get velocity
            try:
                g_init = models.Gaussian1D(
                    amplitude=np.nanmax(y),
                    mean=vel[np.nanargmax(y)],
                    stddev=1.0
                )
                fit_g = fitting.LevMarLSQFitter()
                g = fit_g(g_init, vel, y)
                
                v_cent = float(g.mean.value)
                T_peak = float(g.amplitude.value)
                v_width = float(abs(g.stddev.value))
            except:
                v_cent = vel[np.nanargmax(y)]
                T_peak = np.nanmax(y)
                v_width = np.nan
            
            rows.append({
                "ring": ring_idx,
                "radius_pc": float(0.5*(r_min + r_max)),
                "v_obs_kms": v_cent,
                "T_peak": T_peak,
                "v_width_kms": v_width,
                "n_pixels": int(np.sum(mask))
            })
            
            print(f"   Ring {ring_idx}: r={0.5*(r_min+r_max):.2f} pc, "
                  f"v={v_cent:.2f} km/s, T={T_peak:.3e}")
    
    return pd.DataFrame(rows)

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Convert FITS to ring profile'
    )
    parser.add_argument(
        'fits_file',
        help='Input FITS file (2D image or 3D cube)'
    )
    parser.add_argument(
        '--output',
        default='ring_profile.csv',
        help='Output CSV file'
    )
    parser.add_argument(
        '--cube',
        action='store_true',
        help='Process as 3D spectral cube (not 2D image)'
    )
    parser.add_argument(
        '--r-min',
        type=float,
        default=0.0,
        help='Minimum radius [pc]'
    )
    parser.add_argument(
        '--r-max',
        type=float,
        default=2.0,
        help='Maximum radius [pc]'
    )
    parser.add_argument(
        '--r-step',
        type=float,
        default=0.2,
        help='Ring width [pc]'
    )
    parser.add_argument(
        '--center',
        help='Center coordinates (e.g., "20h31m41s +40d21m07s")'
    )
    parser.add_argument(
        '--distance',
        type=float,
        default=1.7,
        help='Distance to source [kpc]'
    )
    
    args = parser.parse_args()
    
    print("="*80)
    print("FITS TO RING PROFILE - G79.29+0.46")
    print("="*80)
    print(f"\nInput: {args.fits_file}")
    print(f"Output: {args.output}")
    print(f"Mode: {'3D Cube' if args.cube else '2D Image'}")
    
    # Parse center
    if args.center:
        center = SkyCoord(args.center, frame="icrs")
    else:
        center = G79_CENTER
    
    distance = args.distance * u.kpc
    
    print(f"\nTarget center: {center.to_string('hmsdms')}")
    print(f"Distance: {distance}")
    
    # Define ring edges
    r_edges = np.arange(args.r_min, args.r_max + args.r_step, args.r_step)
    print(f"\nRing configuration:")
    print(f"   Range: {r_edges[0]:.2f} - {r_edges[-1]:.2f} pc")
    print(f"   Step: {args.r_step:.2f} pc")
    print(f"   Number of rings: {len(r_edges)-1}")
    
    # Check file exists
    fits_path = Path(args.fits_file)
    if not fits_path.exists():
        print(f"\nERROR: File not found: {fits_path}")
        return 1
    
    # Process based on mode
    if args.cube:
        # 3D cube mode
        df = create_ring_profile_3d(
            str(fits_path), r_edges, center, distance
        )
    else:
        # 2D image mode
        data, wcs, header = load_fits_2d(str(fits_path))
        r_pc = calculate_radial_distance(data, wcs, center, distance)
        df = create_ring_profile_2d(data, r_pc, r_edges)
    
    if df is None or len(df) == 0:
        print("\nERROR: No profile created!")
        return 1
    
    # Save
    print(f"\n[4/5] Saving to CSV: {args.output}")
    
    # Add metadata as comments
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(f"# Ring profile from FITS\n")
        f.write(f"# Source: {fits_path.name}\n")
        f.write(f"# Center: {center.to_string('hmsdms')}\n")
        f.write(f"# Distance: {distance}\n")
        f.write(f"# Ring edges: {r_edges[0]:.2f} - {r_edges[-1]:.2f} pc (step {args.r_step:.2f} pc)\n")
        f.write(f"# Date: {pd.Timestamp.now()}\n")
        f.write(f"#\n")
        
        # Write DataFrame
        df.to_csv(f, index=False)
    
    print(f"   Saved {len(df)} rings")
    
    # Summary
    print("\n[5/5] Summary")
    print("="*80)
    print(f"\nProfile statistics:")
    if 'I_mean' in df.columns:
        print(f"   Intensity range: {df['I_mean'].min():.3e} - {df['I_mean'].max():.3e}")
    if 'v_obs_kms' in df.columns:
        print(f"   Velocity range: {df['v_obs_kms'].min():.2f} - {df['v_obs_kms'].max():.2f} km/s")
    
    print(f"\nOutput: {args.output}")
    print("\nNext steps:")
    print("  1. Inspect CSV file")
    print("  2. Plot profile")
    print("  3. Use in SSZ analysis")
    
    print("\n" + "="*80)
    print("DONE!")
    print("="*80)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
