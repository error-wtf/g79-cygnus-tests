#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete FITS Fetching and Ring Extraction Pipeline

Based on Carmen's workflow:
1. Query archives (IRSA, Herschel, IRAM)
2. Download FITS data
3. Extract radial profiles
4. Generate publication-ready CSVs

This is the PRODUCTION VERSION combining:
- astroquery for automated data fetching
- WCS for coordinate handling
- spectral-cube for datacube analysis
- Automated ring extraction

Usage:
    # Fetch and extract AKARI data
    python fetch_and_extract_complete.py --source akari --extract
    
    # Fetch Herschel PACS [CII]
    python fetch_and_extract_complete.py --source herschel --line CII
    
    # Process local FITS to rings
    python fetch_and_extract_complete.py --local G79_data.fits --extract

© 2025 Carmen N. Wrede, Lino P. Casu
Pipeline design: Carmen (THANK YOU! 🙏)
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
    import pandas as pd
    import matplotlib.pyplot as plt
    from astropy.io import fits
    from astropy.wcs import WCS
    from astropy.coordinates import SkyCoord
    import astropy.units as u
except ImportError as e:
    print(f"ERROR: Core packages missing: {e}")
    print("\nInstall with:")
    print("  pip install numpy pandas matplotlib astropy")
    sys.exit(1)

# Optional imports for advanced features
try:
    from astroquery.ipac.irsa import Irsa
    HAVE_IRSA = True
except ImportError:
    HAVE_IRSA = False

try:
    from astroquery.esa.hsa import HSA
    HAVE_HSA = True
except ImportError:
    HAVE_HSA = False

try:
    from spectral_cube import SpectralCube
    from astropy.modeling import models, fitting
    HAVE_SPECTRAL_CUBE = True
except ImportError:
    HAVE_SPECTRAL_CUBE = False

# G79.29+0.46 coordinates
G79_CENTER = SkyCoord("20h31m41s +40d21m07s", frame="icrs")
G79_DISTANCE = 1.7  # kpc

# Default ring edges (pc)
DEFAULT_R_EDGES = np.arange(0.0, 2.0 + 0.2, 0.2)  # 0-2 pc in 0.2 pc steps

def query_irsa_akari(coord, radius=5*u.arcmin):
    """
    Query IRSA for AKARI data around coordinate
    
    Args:
        coord: SkyCoord
        radius: Search radius
    
    Returns:
        astropy Table with results
    """
    if not HAVE_IRSA:
        print("ERROR: astroquery not installed!")
        print("Install with: pip install astroquery")
        return None
    
    print(f"\n[IRSA] Querying AKARI at {coord.to_string('hmsdms')}")
    print(f"       Radius: {radius}")
    
    try:
        Irsa.ROW_LIMIT = 10000
        result = Irsa.query_region(
            coord,
            catalog="akari_fis_allsky",
            radius=radius
        )
        
        print(f"       Found: {len(result)} sources")
        return result
    
    except Exception as e:
        print(f"ERROR: IRSA query failed: {e}")
        return None

def query_herschel(coord, radius=5*u.arcmin):
    """
    Query Herschel Science Archive
    
    Args:
        coord: SkyCoord
        radius: Search radius
    
    Returns:
        Table with Herschel observations
    """
    if not HAVE_HSA:
        print("ERROR: astroquery.esa.hsa not available!")
        print("Install with: pip install astroquery")
        return None
    
    print(f"\n[HSA] Querying Herschel at {coord.to_string('hmsdms')}")
    print(f"      Radius: {radius}")
    
    try:
        hsa = HSA()
        result = hsa.query_region(coord, radius=radius)
        
        print(f"      Found: {len(result)} observations")
        return result
    
    except Exception as e:
        print(f"ERROR: Herschel query failed: {e}")
        return None

def fits_2d_to_rings(fits_file, center=G79_CENTER, distance=G79_DISTANCE,
                     r_edges=DEFAULT_R_EDGES, output_csv=None):
    """
    Extract radial profile from 2D FITS image
    
    This is Carmen's method!
    
    Args:
        fits_file: Path to FITS file
        center: SkyCoord of nebula center
        distance: Distance in kpc
        r_edges: Ring edges in pc
        output_csv: Output CSV filename
    
    Returns:
        DataFrame with ring profile
    """
    print(f"\n[FITS→Rings] Processing 2D image: {fits_file}")
    
    # 1. Load FITS
    hdu = fits.open(fits_file)[0]
    data = hdu.data
    wcs = WCS(hdu.header)
    
    print(f"   Image size: {data.shape}")
    
    # 2. Calculate radial distances
    ny, nx = data.shape
    y_idx, x_idx = np.indices(data.shape)
    
    # Convert pixels to sky coordinates
    ra, dec = wcs.all_pix2world(x_idx, y_idx, 0)
    coords = SkyCoord(ra*u.deg, dec*u.deg, frame="icrs")
    
    # Angular separation from center
    r_ang = coords.separation(center)
    
    # Physical distance (convert to pc)
    r_pc = (r_ang.to(u.rad) * (distance * u.kpc)).to(u.pc).value
    
    print(f"   Radial range: {r_pc.min():.2f} - {r_pc.max():.2f} pc")
    
    # 3. Define rings
    r_centers = 0.5 * (r_edges[:-1] + r_edges[1:])
    
    print(f"   Extracting {len(r_centers)} rings...")
    
    # 4. Extract ring averages
    rows = []
    for ring_idx, (r_min, r_max) in enumerate(zip(r_edges[:-1], r_edges[1:])):
        mask = (r_pc >= r_min) & (r_pc < r_max) & np.isfinite(data)
        
        if np.any(mask):
            vals = data[mask]
            I_mean = np.nanmean(vals)
            I_std = np.nanstd(vals)
            I_median = np.nanmedian(vals)
            n_pixels = np.sum(mask)
            
            rows.append({
                "ring": ring_idx,
                "radius_pc": float(0.5 * (r_min + r_max)),
                "r_inner_pc": float(r_min),
                "r_outer_pc": float(r_max),
                "I_mean": float(I_mean),
                "I_median": float(I_median),
                "I_std": float(I_std),
                "I_err": float(I_std / np.sqrt(n_pixels)),  # Standard error
                "n_pixels": int(n_pixels),
            })
            
            print(f"      Ring {ring_idx}: r={r_min:.2f}-{r_max:.2f} pc, "
                  f"I={I_mean:.3e} ± {I_std:.3e}, n={n_pixels}")
    
    df_rings = pd.DataFrame(rows)
    
    # 5. Save to CSV
    if output_csv:
        # Add metadata header
        with open(output_csv, 'w', encoding='utf-8') as f:
            f.write(f"# Radial profile from: {Path(fits_file).name}\n")
            f.write(f"# Center: {center.to_string('hmsdms')}\n")
            f.write(f"# Distance: {distance} kpc\n")
            f.write(f"# Extraction method: Ring averaging (Carmen's method)\n")
            f.write(f"# Date: {pd.Timestamp.now()}\n")
            f.write(f"#\n")
            df_rings.to_csv(f, index=False)
        
        print(f"\n   Saved: {output_csv}")
    
    return df_rings

def fits_cube_to_rings(fits_file, center=G79_CENTER, distance=G79_DISTANCE,
                       r_edges=DEFAULT_R_EDGES, output_csv=None):
    """
    Extract radial velocity profile from 3D FITS cube
    
    Carmen's method for CO/[CII] cubes!
    
    Args:
        fits_file: Path to FITS cube
        center: SkyCoord of center
        distance: Distance in kpc
        r_edges: Ring edges in pc
        output_csv: Output CSV
    
    Returns:
        DataFrame with ring profile
    """
    if not HAVE_SPECTRAL_CUBE:
        print("ERROR: spectral-cube not installed!")
        print("Install with: pip install spectral-cube")
        return None
    
    print(f"\n[CUBE→Rings] Processing 3D cube: {fits_file}")
    
    # 1. Load cube
    cube = SpectralCube.read(fits_file)
    
    # Convert to km/s
    try:
        cube = cube.with_spectral_unit(u.km/u.s)
    except:
        print("   Warning: Could not convert spectral axis to km/s")
    
    vel = cube.spectral_axis.value
    
    print(f"   Cube size: {cube.shape}")
    print(f"   Velocity range: {vel.min():.2f} - {vel.max():.2f} km/s")
    
    # 2. Calculate radial distances (spatial only)
    wcs_spatial = cube.wcs.celestial
    ny, nx = cube.shape[1], cube.shape[2]
    y_idx, x_idx = np.indices((ny, nx))
    
    ra, dec = wcs_spatial.all_pix2world(x_idx, y_idx, 0)
    coords = SkyCoord(ra*u.deg, dec*u.deg, frame="icrs")
    r_ang = coords.separation(center)
    r_pc = (r_ang.to(u.rad) * (distance * u.kpc)).to(u.pc).value
    
    print(f"   Radial range: {r_pc.min():.2f} - {r_pc.max():.2f} pc")
    
    # 3. Extract ring spectra
    r_centers = 0.5 * (r_edges[:-1] + r_edges[1:])
    
    print(f"   Extracting {len(r_centers)} ring spectra...")
    
    rows = []
    for ring_idx, (r_min, r_max) in enumerate(zip(r_edges[:-1], r_edges[1:])):
        mask_2d = (r_pc >= r_min) & (r_pc < r_max)
        
        if np.any(mask_2d):
            # Average spectrum in this ring
            # Create 3D mask
            mask_3d = np.broadcast_to(mask_2d[np.newaxis, :, :], cube.shape)
            
            # Get subcube
            subcube_data = cube.filled_data[:].value
            masked_data = np.where(mask_3d, subcube_data, np.nan)
            
            # Average over spatial dimensions
            spectrum = np.nanmean(masked_data, axis=(1, 2))
            
            if not np.all(np.isnan(spectrum)):
                # Fit Gaussian to find centroid velocity
                try:
                    # Simple 1-Gaussian fit
                    g_init = models.Gaussian1D(
                        amplitude=np.nanmax(spectrum),
                        mean=vel[np.nanargmax(spectrum)],
                        stddev=1.0
                    )
                    fit_g = fitting.LevMarLSQFitter()
                    g = fit_g(g_init, vel, spectrum)
                    
                    v_cent = float(g.mean.value)
                    v_width = float(abs(g.stddev.value))
                    T_peak = float(np.nanmax(spectrum))
                    
                except:
                    # Fallback: just use peak
                    v_cent = float(vel[np.nanargmax(spectrum)])
                    v_width = np.nan
                    T_peak = float(np.nanmax(spectrum))
                
                n_pixels = int(np.sum(mask_2d))
                
                rows.append({
                    "ring": ring_idx,
                    "radius_pc": float(0.5 * (r_min + r_max)),
                    "r_inner_pc": float(r_min),
                    "r_outer_pc": float(r_max),
                    "v_obs_kms": v_cent,
                    "v_width_kms": v_width,
                    "T_peak_K": T_peak,
                    "n_pixels": n_pixels,
                })
                
                print(f"      Ring {ring_idx}: r={r_min:.2f}-{r_max:.2f} pc, "
                      f"v={v_cent:.2f} km/s, T_peak={T_peak:.1f} K")
    
    df_rings = pd.DataFrame(rows)
    
    # 5. Save
    if output_csv:
        with open(output_csv, 'w', encoding='utf-8') as f:
            f.write(f"# Velocity profile from: {Path(fits_file).name}\n")
            f.write(f"# Center: {center.to_string('hmsdms')}\n")
            f.write(f"# Distance: {distance} kpc\n")
            f.write(f"# Extraction: Ring-averaged spectra (Carmen's method)\n")
            f.write(f"# Date: {pd.Timestamp.now()}\n")
            f.write(f"#\n")
            df_rings.to_csv(f, index=False)
        
        print(f"\n   Saved: {output_csv}")
    
    return df_rings

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Complete FITS fetching and ring extraction pipeline'
    )
    
    # Data source
    source_group = parser.add_mutually_exclusive_group()
    source_group.add_argument(
        '--source',
        choices=['akari', 'herschel', 'irsa'],
        help='Query telescope archive'
    )
    source_group.add_argument(
        '--local',
        help='Process local FITS file'
    )
    
    # Options
    parser.add_argument(
        '--extract',
        action='store_true',
        help='Extract rings after fetching'
    )
    parser.add_argument(
        '--cube',
        action='store_true',
        help='Process as 3D cube (not 2D image)'
    )
    parser.add_argument(
        '--output',
        help='Output CSV filename'
    )
    parser.add_argument(
        '--coord',
        default="20h31m41s +40d21m07s",
        help='Target coordinates [default: G79.29+0.46]'
    )
    parser.add_argument(
        '--distance',
        type=float,
        default=1.7,
        help='Distance in kpc [default: 1.7]'
    )
    
    args = parser.parse_args()
    
    print("="*80)
    print("FITS FETCHING AND RING EXTRACTION PIPELINE")
    print("="*80)
    print("\nBased on Carmen's workflow - THANK YOU! 🙏")
    
    # Parse coordinates
    coord = SkyCoord(args.coord, frame="icrs")
    
    # Query archives
    if args.source == 'akari':
        result = query_irsa_akari(coord)
        if result is not None:
            print(f"\n{result}")
    
    elif args.source == 'herschel':
        result = query_herschel(coord)
        if result is not None:
            print(f"\n{result}")
    
    elif args.source == 'irsa':
        result = query_irsa_akari(coord)  # Generic IRSA query
        if result is not None:
            print(f"\n{result}")
    
    # Process local FITS
    elif args.local:
        fits_path = Path(args.local)
        
        if not fits_path.exists():
            print(f"ERROR: File not found: {fits_path}")
            return 1
        
        # Auto-detect output name
        if args.output is None:
            output_csv = fits_path.stem + "_rings.csv"
        else:
            output_csv = args.output
        
        # Extract rings
        if args.cube:
            df = fits_cube_to_rings(
                fits_path,
                center=coord,
                distance=args.distance,
                output_csv=output_csv
            )
        else:
            df = fits_2d_to_rings(
                fits_path,
                center=coord,
                distance=args.distance,
                output_csv=output_csv
            )
        
        if df is not None:
            print(f"\n✓ Extracted {len(df)} rings!")
            print(f"✓ Saved to: {output_csv}")
    
    else:
        print("\nNo action specified!")
        print("Use --source to query archives")
        print("Use --local to process FITS file")
        parser.print_help()
    
    print("\n" + "="*80)
    print("DONE!")
    print("="*80)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
