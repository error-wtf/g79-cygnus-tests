#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fetch REAL G79.29+0.46 IR Data from IRSA

Based on Carmen's "wirklich fetchen" instructions!
This script ACTUALLY downloads FITS files from IRSA.

Priority targets:
1. Spitzer MIPS 24 μm (hot dust, inner ring)
2. AKARI FIS 90 μm (cool dust, outer shell)
3. WISE (optional)

Usage:
    python fetch_g79_ir_data.py --all
    python fetch_g79_ir_data.py --spitzer
    python fetch_g79_ir_data.py --akari

Then:
    python extract_akari_rings.py data/telescope/G79_akari_90um.fits

© 2025 Carmen N. Wrede, Lino P. Casu
Based on: Carmen's IRSA fetch workflow
Licensed under ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""
import sys
import os
from pathlib import Path
import argparse

# UTF-8 for Windows
os.environ['PYTHONIOENCODING'] = 'utf-8:replace'
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass

try:
    import numpy as np
    from astropy.coordinates import SkyCoord
    import astropy.units as u
except ImportError as e:
    print(f"ERROR: astropy not installed: {e}")
    print("\nInstall with:")
    print("  pip install astropy")
    sys.exit(1)

# Check for astroquery
try:
    from astroquery.ipac.irsa import Irsa
    HAVE_ASTROQUERY = True
except ImportError:
    print("WARNING: astroquery not installed!")
    print("Install with: pip install astroquery")
    print("\nFalling back to URL-based instructions...")
    HAVE_ASTROQUERY = False

# G79.29+0.46 coordinates (Carmen's exact values!)
# RA:  20:31:41  = 20h 31m 41s
# Dec: +40:21:07 = +40° 21' 07"

# Convert to degrees (for IRSA):
# RA: 20:31:41 = 20 + 31/60 + 41/3600 hours = 20.528055... hours
#     × 15°/hour = 307.920833... degrees
# Dec: +40:21:07 = 40 + 21/60 + 7/3600 degrees = 40.351944... degrees

G79_RA_DEG = 307.920833  # degrees (20:31:41 in decimal)
G79_DEC_DEG = 40.351944  # degrees (+40:21:07 in decimal)
G79_COORD = SkyCoord(ra=G79_RA_DEG*u.deg, dec=G79_DEC_DEG*u.deg, frame='icrs')

# Search parameters
SEARCH_RADIUS_ARCMIN = 10  # arcmin (Carmen's recommendation)
SEARCH_RADIUS_DEG = 0.1667  # degrees (10 arcmin)

# Output directory
OUTPUT_DIR = Path("data/telescope")

def ensure_output_dir():
    """Create output directory if needed"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {OUTPUT_DIR.absolute()}")

def print_coordinates():
    """Print G79 coordinates in various formats"""
    print("\n" + "="*80)
    print("G79.29+0.46 COORDINATES")
    print("="*80)
    print(f"\nSexagesimal:")
    print(f"  RA:  {G79_COORD.ra.to_string(unit=u.hourangle, sep=':', precision=2)}")
    print(f"  Dec: {G79_COORD.dec.to_string(unit=u.deg, sep=':', precision=1)}")
    
    print(f"\nDecimal degrees (for IRSA):")
    print(f"  RA:  {G79_RA_DEG:.6f}°")
    print(f"  Dec: {G79_DEC_DEG:.6f}°")
    
    print(f"\nSearch parameters:")
    print(f"  Radius: {SEARCH_RADIUS_ARCMIN} arcmin = {SEARCH_RADIUS_DEG:.4f} deg")
    print(f"  POS string: {G79_RA_DEG:.6f},{G79_DEC_DEG:.6f}")
    print("="*80)

def query_irsa_spitzer():
    """Query IRSA for Spitzer MIPS data"""
    
    if not HAVE_ASTROQUERY:
        print("\n⚠️  astroquery not available!")
        print("\nManual IRSA query:")
        print(f"1. Go to: https://irsa.ipac.caltech.edu/")
        print(f"2. Mission: Spitzer")
        print(f"3. Coordinates: {G79_RA_DEG:.6f}, {G79_DEC_DEG:.6f}")
        print(f"4. Radius: {SEARCH_RADIUS_DEG} deg")
        print(f"5. Download MIPS 24 μm FITS")
        return None
    
    print("\n" + "="*80)
    print("QUERYING IRSA - SPITZER MIPS")
    print("="*80)
    
    try:
        print(f"\nQuerying Spitzer at: {G79_COORD.to_string('hmsdms')}")
        print(f"Radius: {SEARCH_RADIUS_ARCMIN} arcmin")
        
        Irsa.ROW_LIMIT = 10000
        
        # Try Spitzer SHA catalog
        print("\nSearching Spitzer Heritage Archive...")
        result = Irsa.query_region(
            G79_COORD,
            catalog="spitzer_sha",
            radius=SEARCH_RADIUS_ARCMIN * u.arcmin
        )
        
        if result:
            print(f"\n✓ Found {len(result)} Spitzer observations!")
            print(f"\nColumns: {result.colnames}")
            print(f"\nFirst 5 results:")
            print(result[:5])
            
            # Save table
            output_file = OUTPUT_DIR / "spitzer_query_results.csv"
            result.write(output_file, format='csv', overwrite=True)
            print(f"\n✓ Saved query results: {output_file}")
            
            return result
        else:
            print("\n⚠️  No Spitzer data found!")
            return None
            
    except Exception as e:
        print(f"\n❌ Query failed: {e}")
        print("\nTry manual search at:")
        print("https://irsa.ipac.caltech.edu/applications/Spitzer/SHA/")
        return None

def query_irsa_akari():
    """Query IRSA for AKARI FIS data"""
    
    if not HAVE_ASTROQUERY:
        print("\n⚠️  astroquery not available!")
        print("\nManual IRSA query:")
        print(f"1. Go to: https://irsa.ipac.caltech.edu/")
        print(f"2. Mission: AKARI")
        print(f"3. Catalog: akari_fis_allsky")
        print(f"4. Coordinates: {G79_RA_DEG:.6f}, {G79_DEC_DEG:.6f}")
        print(f"5. Radius: {SEARCH_RADIUS_DEG} deg")
        return None
    
    print("\n" + "="*80)
    print("QUERYING IRSA - AKARI FIS")
    print("="*80)
    
    try:
        print(f"\nQuerying AKARI at: {G79_COORD.to_string('hmsdms')}")
        print(f"Radius: {SEARCH_RADIUS_ARCMIN} arcmin")
        
        Irsa.ROW_LIMIT = 10000
        
        print("\nSearching AKARI FIS all-sky catalog...")
        result = Irsa.query_region(
            G79_COORD,
            catalog="akari_fis_allsky",
            radius=SEARCH_RADIUS_ARCMIN * u.arcmin
        )
        
        if result:
            print(f"\n✓ Found {len(result)} AKARI sources!")
            print(f"\nColumns: {result.colnames}")
            print(f"\nFirst 5 results:")
            print(result[:5])
            
            # Save table
            output_file = OUTPUT_DIR / "akari_query_results.csv"
            result.write(output_file, format='csv', overwrite=True)
            print(f"\n✓ Saved query results: {output_file}")
            
            return result
        else:
            print("\n⚠️  No AKARI data found!")
            return None
            
    except Exception as e:
        print(f"\n❌ Query failed: {e}")
        print("\nTry manual search at:")
        print("https://irsa.ipac.caltech.edu/")
        return None

def print_curl_examples():
    """Print curl/wget examples for manual download"""
    print("\n" + "="*80)
    print("MANUAL DOWNLOAD (curl/wget)")
    print("="*80)
    
    print("\nIf astroquery doesn't work, use these commands:")
    
    print("\n# 1. Query Spitzer MIPS metadata:")
    print(f'curl -L "https://irsa.ipac.caltech.edu/ibe/search/spitzer/sha/level2/mips24?POS={G79_RA_DEG:.6f},{G79_DEC_DEG:.6f}&SIZE={SEARCH_RADIUS_DEG:.4f}" -o spitzer_mips24_metadata.tbl')
    
    print("\n# 2. Query AKARI (via IRSA):")
    print(f'# Go to https://irsa.ipac.caltech.edu/')
    print(f'# Mission: AKARI, Catalog: akari_fis_allsky')
    print(f'# Coordinates: {G79_RA_DEG:.6f}, {G79_DEC_DEG:.6f}')
    print(f'# Radius: 10 arcmin')
    
    print("\n# 3. Download FITS (once you have URL from metadata):")
    print('# curl -L "https://irsa.ipac.caltech.edu/data/..." -o G79_spitzer_mips24.fits')
    
    print("\n" + "="*80)

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Fetch G79.29+0.46 IR data from IRSA'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Query all missions (Spitzer + AKARI)'
    )
    parser.add_argument(
        '--spitzer',
        action='store_true',
        help='Query Spitzer only'
    )
    parser.add_argument(
        '--akari',
        action='store_true',
        help='Query AKARI only'
    )
    parser.add_argument(
        '--coords',
        action='store_true',
        help='Just print coordinates and exit'
    )
    parser.add_argument(
        '--curl',
        action='store_true',
        help='Print curl/wget examples and exit'
    )
    
    args = parser.parse_args()
    
    print("="*80)
    print("FETCH G79.29+0.46 IR DATA FROM IRSA")
    print("="*80)
    print("\nBased on Carmen's 'wirklich fetchen' instructions! 🚀")
    
    # Print coordinates
    if args.coords:
        print_coordinates()
        return 0
    
    # Print curl examples
    if args.curl:
        print_coordinates()
        print_curl_examples()
        return 0
    
    # Create output directory
    ensure_output_dir()
    
    # Print coordinates
    print_coordinates()
    
    # Default: query all if no specific mission selected
    query_all = args.all or not (args.spitzer or args.akari)
    
    # Query missions
    if args.spitzer or query_all:
        spitzer_result = query_irsa_spitzer()
    
    if args.akari or query_all:
        akari_result = query_irsa_akari()
    
    # Print manual instructions
    print_curl_examples()
    
    # Summary
    print("\n" + "="*80)
    print("NEXT STEPS")
    print("="*80)
    
    print("\n1. Check query results:")
    print(f"   {OUTPUT_DIR}/spitzer_query_results.csv")
    print(f"   {OUTPUT_DIR}/akari_query_results.csv")
    
    print("\n2. Download FITS files:")
    print("   → Use URLs from query results")
    print("   → Or download via IRSA web interface")
    
    print("\n3. Extract rings:")
    print("   python extract_akari_rings.py data/telescope/G79_akari_90um.fits")
    print("   python extract_akari_rings.py data/telescope/G79_spitzer_mips24.fits")
    
    print("\n4. Fit γ_seg(r):")
    print("   python fit_gamma_seg_profile.py G79_akari_90um_rings_REAL.csv")
    
    print("\n" + "="*80)
    print("READY TO FETCH REAL DATA! 🎉")
    print("="*80)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
