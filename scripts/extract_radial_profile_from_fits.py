#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extract Radial Profiles from FITS Cubes - G79.29+0.46

Extracts temperature and velocity profiles from telescope FITS data.

Requirements:
    pip install astropy spectral-cube radio-beam reproject

Usage:
    python extract_radial_profile_from_fits.py data/telescope/iram/G79_CO21.fits
    python extract_radial_profile_from_fits.py data/telescope/effelsberg/G79_NH3.fits --output G79_verified_profile.csv

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
    from astropy import units as u
    from astropy.coordinates import SkyCoord
    from astropy.wcs import WCS
    import matplotlib.pyplot as plt
    HAS_ASTROPY = True
except ImportError:
    HAS_ASTROPY = False
    print("ERROR: astropy not installed!")
    print("Install with: pip install astropy")
    sys.exit(1)

try:
    from spectral_cube import SpectralCube
    HAS_SPECTRAL_CUBE = True
except ImportError:
    HAS_SPECTRAL_CUBE = False
    print("WARNING: spectral-cube not installed (optional)")
    print("Install with: pip install spectral-cube")

# G79.29+0.46 coordinates
G79_COORD = SkyCoord('20h32m32.9s', '+41d19m33s', frame='icrs')
G79_DISTANCE = 1.7 * u.kpc  # Distance to source

def load_fits_file(fits_path):
    """
    Load FITS file and determine type
    
    Args:
        fits_path: Path to FITS file
    
    Returns:
        hdu_list, file_type
    """
    print(f"\n[1/6] Loading FITS file: {fits_path}")
    
    hdu_list = fits.open(fits_path)
    
    # Determine file type
    primary = hdu_list[0]
    
    if primary.data is None and len(hdu_list) > 1:
        # Multi-extension FITS
        data_hdu = hdu_list[1]
    else:
        data_hdu = primary
    
    ndim = len(data_hdu.data.shape) if data_hdu.data is not None else 0
    
    if ndim == 2:
        file_type = "2D image"
    elif ndim == 3:
        file_type = "3D cube (likely velocity cube)"
    elif ndim == 4:
        file_type = "4D cube (stokes + velocity)"
    else:
        file_type = "Unknown"
    
    print(f"   Type: {file_type}")
    print(f"   Shape: {data_hdu.data.shape if data_hdu.data is not None else 'No data'}")
    
    return hdu_list, file_type

def extract_radial_profile_2d(hdu, center_coord, distance, n_bins=10):
    """
    Extract radial profile from 2D image
    
    Args:
        hdu: FITS HDU with 2D image
        center_coord: SkyCoord of source center
        distance: Distance to source (with units)
        n_bins: Number of radial bins
    
    Returns:
        radii_pc, values, errors
    """
    print("\n[2/6] Extracting 2D radial profile...")
    
    # Get data and WCS
    data = hdu.data
    wcs = WCS(hdu.header)
    
    # Create pixel grid
    ny, nx = data.shape
    y, x = np.mgrid[0:ny, 0:nx]
    
    # Convert center to pixel coordinates
    center_pix = wcs.world_to_pixel(center_coord)
    x0, y0 = center_pix
    
    print(f"   Center pixel: ({x0:.1f}, {y0:.1f})")
    
    # Calculate radial distance in pixels
    r_pix = np.sqrt((x - x0)**2 + (y - y0)**2)
    
    # Convert to physical distance
    # Get pixel scale from WCS
    try:
        pixscale = wcs.proj_plane_pixel_scales()[0]  # degrees/pixel
        pixscale_arcsec = pixscale * 3600  # arcsec/pixel
        pixscale_pc = (pixscale_arcsec * u.arcsec * distance).to(u.pc, 
                       equivalencies=u.dimensionless_angles())
        r_pc = r_pix * pixscale_pc.value
        
        print(f"   Pixel scale: {pixscale_arcsec:.2f} arcsec/pixel")
        print(f"   = {pixscale_pc:.3f} at {distance}")
    except:
        print("   WARNING: Could not determine pixel scale")
        print("   Using arbitrary units")
        r_pc = r_pix
        pixscale_pc = 1.0 * u.pc
    
    # Define radial bins
    r_max = np.min([x0, y0, nx-x0, ny-y0]) * pixscale_pc.value
    radii_pc = np.linspace(0.1, r_max, n_bins)
    
    print(f"   Radial range: {radii_pc[0]:.2f} - {radii_pc[-1]:.2f} pc")
    print(f"   Number of bins: {n_bins}")
    
    # Extract profile
    values = np.zeros(n_bins)
    errors = np.zeros(n_bins)
    
    for i in range(n_bins):
        if i == 0:
            mask = r_pc < radii_pc[0]
        else:
            mask = (r_pc >= radii_pc[i-1]) & (r_pc < radii_pc[i])
        
        values_in_ring = data[mask]
        values_in_ring = values_in_ring[np.isfinite(values_in_ring)]
        
        if len(values_in_ring) > 0:
            values[i] = np.mean(values_in_ring)
            errors[i] = np.std(values_in_ring) / np.sqrt(len(values_in_ring))
        else:
            values[i] = np.nan
            errors[i] = np.nan
    
    print(f"   Profile extracted: {np.sum(np.isfinite(values))}/{n_bins} bins valid")
    
    return radii_pc, values, errors

def extract_radial_profile_3d(hdu, center_coord, distance, n_bins=10):
    """
    Extract radial profile from 3D cube (velocity cube)
    
    For velocity cubes, we:
    1. Collapse along velocity axis (moment 0 - integrated intensity)
    2. Extract radial profile from 2D map
    3. Optionally: Extract velocity information (moment 1)
    
    Args:
        hdu: FITS HDU with 3D cube
        center_coord: SkyCoord of source center
        distance: Distance to source
        n_bins: Number of radial bins
    
    Returns:
        radii_pc, intensity, velocity, errors
    """
    print("\n[2/6] Extracting 3D radial profile...")
    print("   Collapsing velocity axis (moment 0)...")
    
    data = hdu.data
    wcs = WCS(hdu.header)
    
    # Collapse along velocity axis (assumed to be first axis)
    # Moment 0: Integrated intensity
    moment0 = np.nansum(data, axis=0)
    
    # Create 2D HDU for radial profile extraction
    hdu_2d = fits.PrimaryHDU(data=moment0, header=hdu.header)
    
    # Remove velocity axis from WCS
    wcs_2d = wcs.dropaxis(2)  # Drop spectral axis
    hdu_2d.header.update(wcs_2d.to_header())
    
    # Extract profile from moment 0
    radii_pc, intensity, int_err = extract_radial_profile_2d(
        hdu_2d, center_coord, distance, n_bins
    )
    
    # TODO: Add moment 1 (velocity) extraction
    # For now, return zeros
    velocity = np.zeros_like(intensity)
    vel_err = np.zeros_like(intensity)
    
    return radii_pc, intensity, velocity, int_err, vel_err

def plot_profile(radii_pc, values, errors, output_path=None):
    """
    Plot radial profile
    
    Args:
        radii_pc: Radii [pc]
        values: Values at each radius
        errors: Uncertainties
        output_path: Path to save plot (optional)
    """
    print("\n[5/6] Creating plot...")
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.errorbar(radii_pc, values, yerr=errors, 
                marker='o', linestyle='-', linewidth=2, 
                markersize=8, capsize=5)
    
    ax.set_xlabel('Radius [pc]', fontsize=14)
    ax.set_ylabel('Value', fontsize=14)
    ax.set_title('G79.29+0.46 - Radial Profile', fontsize=16)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if output_path:
        fig.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"   Plot saved: {output_path}")
    else:
        plt.show()

def save_profile_csv(radii_pc, values, errors, output_path, 
                     value_name='value', source_info=''):
    """
    Save profile to CSV
    
    Args:
        radii_pc: Radii [pc]
        values: Values at each radius
        errors: Uncertainties
        output_path: Output CSV path
        value_name: Name of the value column
        source_info: Source information for header
    """
    print(f"\n[6/6] Saving to CSV: {output_path}")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        # Write header
        f.write(f"# G79.29+0.46 Radial Profile\n")
        f.write(f"# Source: {source_info}\n")
        f.write(f"# Extraction method: Radial binning from FITS\n")
        f.write(f"# Date: {np.datetime64('today')}\n")
        f.write(f"#\n")
        f.write(f"ring,radius_pc,{value_name},{value_name}_err\n")
        
        # Write data
        for i, (r, v, e) in enumerate(zip(radii_pc, values, errors)):
            f.write(f"{i},{r:.3f},{v:.6e},{e:.6e}\n")
    
    print(f"   Saved {len(radii_pc)} radial bins")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Extract radial profiles from FITS files'
    )
    parser.add_argument(
        'fits_file',
        help='Path to FITS file'
    )
    parser.add_argument(
        '--output',
        default='radial_profile.csv',
        help='Output CSV file'
    )
    parser.add_argument(
        '--plot',
        help='Save plot to this file'
    )
    parser.add_argument(
        '--bins',
        type=int,
        default=10,
        help='Number of radial bins'
    )
    parser.add_argument(
        '--distance',
        type=float,
        default=1.7,
        help='Distance to source [kpc]'
    )
    
    args = parser.parse_args()
    
    print("="*80)
    print("RADIAL PROFILE EXTRACTION - G79.29+0.46")
    print("="*80)
    print(f"\nInput: {args.fits_file}")
    print(f"Output: {args.output}")
    print(f"Center: {G79_COORD.to_string('hmsdms')}")
    print(f"Distance: {args.distance} kpc")
    print(f"Radial bins: {args.bins}")
    
    # Check file exists
    fits_path = Path(args.fits_file)
    if not fits_path.exists():
        print(f"\nERROR: File not found: {fits_path}")
        return 1
    
    # Load FITS
    hdu_list, file_type = load_fits_file(fits_path)
    
    # Extract profile based on dimensionality
    distance = args.distance * u.kpc
    
    if '2D' in file_type:
        radii_pc, values, errors = extract_radial_profile_2d(
            hdu_list[0], G79_COORD, distance, args.bins
        )
        value_name = 'intensity'
    
    elif '3D' in file_type:
        radii_pc, intensity, velocity, int_err, vel_err = extract_radial_profile_3d(
            hdu_list[0], G79_COORD, distance, args.bins
        )
        values = intensity
        errors = int_err
        value_name = 'intensity'
        
        # TODO: Save velocity as separate column
    
    else:
        print(f"\nERROR: Unsupported file type: {file_type}")
        return 1
    
    # Save CSV
    save_profile_csv(
        radii_pc, values, errors, args.output,
        value_name=value_name,
        source_info=f"{fits_path.name} ({file_type})"
    )
    
    # Plot if requested
    if args.plot:
        plot_profile(radii_pc, values, errors, args.plot)
    
    print("\n" + "="*80)
    print("EXTRACTION COMPLETE")
    print("="*80)
    print(f"\nCSV: {args.output}")
    if args.plot:
        print(f"Plot: {args.plot}")
    print("\nNext steps:")
    print("  1. Verify profile against published results")
    print("  2. Compare with other tracers")
    print("  3. Use in SSZ analysis")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
