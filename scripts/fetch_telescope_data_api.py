#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fetch Telescope Data via API - G79.29+0.46

Automated download using astroquery for IRSA and Herschel archives.

Requirements:
    pip install astroquery astropy

Usage:
    # Query archives (no download)
    python fetch_telescope_data_api.py --source spitzer --query
    python fetch_telescope_data_api.py --source herschel --query
    python fetch_telescope_data_api.py --source akari --query
    
    # Download data
    python fetch_telescope_data_api.py --source spitzer --download
    python fetch_telescope_data_api.py --source all --download

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
    from astroquery.ipac.irsa import Irsa
    from astroquery.esa.hsa import HSA
    from astropy.coordinates import SkyCoord
    import astropy.units as u
    from astropy.table import Table
    import numpy as np
    HAS_ASTROQUERY = True
except ImportError as e:
    HAS_ASTROQUERY = False
    print(f"ERROR: Required packages not installed!")
    print(f"Missing: {e}")
    print("\nInstall with:")
    print("  pip install astroquery astropy")
    sys.exit(1)

# G79.29+0.46 coordinates
G79_COORD = SkyCoord("20:32:32.9", "+41:19:33", 
                     unit=(u.hourangle, u.deg), frame='icrs')
SEARCH_RADIUS = 5 * u.arcmin

# Output directory
DATA_DIR = Path("data/telescope")

def create_output_dirs():
    """Create output directory structure"""
    for subdir in ['spitzer', 'herschel', 'akari', 'iram', 'effelsberg']:
        (DATA_DIR / subdir).mkdir(parents=True, exist_ok=True)
    print(f"[OK] Created directories in {DATA_DIR}")

def query_spitzer():
    """
    Query Spitzer data via IRSA
    
    Returns table of available observations
    """
    print("\n" + "="*80)
    print("QUERYING: Spitzer/IRSA")
    print("="*80)
    print(f"Target: {G79_COORD.to_string('hmsdms')}")
    print(f"Radius: {SEARCH_RADIUS}")
    
    try:
        # Query Spitzer Heritage Archive
        print("\nSearching Spitzer Heritage Archive...")
        
        # Note: IRSA has multiple Spitzer catalogs
        # For images, we need to use the image service
        from astroquery.ipac.irsa import Irsa
        
        # Try getting images directly
        print("Querying for Spitzer MIPS images...")
        images = Irsa.query_region(
            G79_COORD, 
            catalog='spitzer_sha',
            spatial='Cone',
            radius=SEARCH_RADIUS
        )
        
        if images:
            print(f"\n[OK] Found {len(images)} Spitzer observations")
            print("\nAvailable data:")
            print(images['mission', 'instrument', 'wavelength', 'obsid'][:10])
            return images
        else:
            print("\n[INFO] No Spitzer data found in SHA catalog")
            print("[INFO] Try web interface: https://irsa.ipac.caltech.edu/applications/Spitzer/SHA/")
            return None
            
    except Exception as e:
        print(f"\n[ERROR] Spitzer query failed: {e}")
        print("\nFallback: Use web interface")
        print("URL: https://irsa.ipac.caltech.edu/applications/Spitzer/SHA/")
        print(f"Coordinates: {G79_COORD.to_string('hmsdms')}")
        return None

def query_herschel():
    """
    Query Herschel data via ESA HSA
    
    Uses TAP/ADQL to search the archive
    """
    print("\n" + "="*80)
    print("QUERYING: Herschel Science Archive")
    print("="*80)
    print(f"Target: {G79_COORD.to_string('hmsdms')}")
    print(f"Radius: {SEARCH_RADIUS}")
    
    try:
        # Query Herschel using TAP
        print("\nSearching Herschel via TAP/ADQL...")
        
        hsa = HSA()
        
        # ADQL query for observations
        ra_deg = G79_COORD.ra.deg
        dec_deg = G79_COORD.dec.deg
        radius_deg = SEARCH_RADIUS.to(u.deg).value
        
        query = f"""
        SELECT TOP 100
            observation_id, instrument, obs_mode, 
            ra, dec, wavelength, duration
        FROM herschel.observation
        WHERE CONTAINS(POINT('ICRS', ra, dec), 
                      CIRCLE('ICRS', {ra_deg}, {dec_deg}, {radius_deg})) = 1
        """
        
        print(f"\nADQL Query:")
        print(query)
        
        result = hsa.query_tap(query)
        
        if result and len(result) > 0:
            print(f"\n[OK] Found {len(result)} Herschel observations")
            print("\nAvailable data:")
            print(result['observation_id', 'instrument', 'obs_mode'][:10])
            return result
        else:
            print("\n[INFO] No Herschel data found")
            return None
            
    except Exception as e:
        print(f"\n[ERROR] Herschel query failed: {e}")
        print("\nFallback: Use web interface")
        print("URL: http://archives.esac.esa.int/hsa/whsa/")
        print(f"Coordinates: {G79_COORD.to_string('hmsdms')}")
        return None

def query_akari():
    """
    Query AKARI data via IRSA
    
    AKARI all-sky survey data is available through IRSA
    """
    print("\n" + "="*80)
    print("QUERYING: AKARI/IRSA")
    print("="*80)
    print(f"Target: {G79_COORD.to_string('hmsdms')}")
    print(f"Radius: {SEARCH_RADIUS}")
    
    try:
        # Query AKARI FIS (Far-Infrared Surveyor)
        print("\nSearching AKARI FIS All-Sky Survey...")
        
        result = Irsa.query_region(
            G79_COORD,
            catalog='akari_fis',
            spatial='Cone',
            radius=SEARCH_RADIUS
        )
        
        if result and len(result) > 0:
            print(f"\n[OK] Found {len(result)} AKARI sources")
            print("\nAvailable data:")
            # Show relevant columns (adjust based on actual catalog)
            cols = [c for c in result.colnames if any(x in c.lower() 
                   for x in ['flux', 'pos', 'err'])][:10]
            print(result[cols[:5]][:10] if cols else result[:10])
            return result
        else:
            print("\n[INFO] No AKARI sources found")
            return None
            
    except Exception as e:
        print(f"\n[ERROR] AKARI query failed: {e}")
        print("\nFallback: Use DARTS web interface")
        print("URL: https://darts.isas.jaxa.jp/astro/akari/")
        print(f"Coordinates: RA {G79_COORD.ra.deg:.5f}, Dec {G79_COORD.dec.deg:.5f}")
        return None

def download_data(source, result_table, output_dir):
    """
    Download data files from query results
    
    Args:
        source: Archive name
        result_table: Query result table
        output_dir: Output directory
    """
    print(f"\n[INFO] Downloading {source} data to {output_dir}")
    
    if result_table is None or len(result_table) == 0:
        print("[SKIP] No data to download")
        return
    
    # Download implementation depends on archive
    # This is a template - actual implementation varies by archive
    
    print("\n[INFO] Automated download not yet fully implemented")
    print("[INFO] Use query results to download via web interface")
    
    # Save query results as CSV
    output_file = output_dir / f"{source}_query_results.csv"
    result_table.write(output_file, format='csv', overwrite=True)
    print(f"[OK] Saved query results to: {output_file}")
    print("\nUse these observation IDs to download data from:")
    
    if source == 'spitzer':
        print("  https://irsa.ipac.caltech.edu/applications/Spitzer/SHA/")
    elif source == 'herschel':
        print("  http://archives.esac.esa.int/hsa/whsa/")
    elif source == 'akari':
        print("  https://darts.isas.jaxa.jp/astro/akari/")

def print_iram_info():
    """
    Print information about accessing IRAM data
    
    IRAM doesn't have a simple REST API, so this provides
    manual instructions
    """
    print("\n" + "="*80)
    print("IRAM 30m - SEMI-MANUAL ACCESS")
    print("="*80)
    
    print("""
IRAM 30m CO observations require semi-manual access:

1. METADATA via TAP/TAPAS:
   - URL: http://www.iram.fr/TAPAS/
   - Query observation logs (VO-compatible)
   
2. DATA FILES:
   - Check Rizzo et al. 2008 for project ID
   - Contact: archive@iram.fr
   - Or use IRAM archive web interface
   
3. EXAMPLE REQUEST:
   
   To: archive@iram.fr
   Subject: Data request for G79.29+0.46 CO observations
   
   Dear IRAM Archive Team,
   
   We are analyzing G79.29+0.46 following Rizzo et al. (2008, ApJ 681).
   Could you provide the CO (2-1) and (3-2) FITS cubes?
   
   Target: G79.29+0.46 (IRAS 20308+4104)
   Coordinates: 20:32:32.9 +41:19:33
   Reference: Rizzo et al. 2008, ApJ 681, 355
   
   Best regards,
   [Your name]

4. ALTERNATIVE:
   - Download GILDAS/CLASS software
   - Access data through IRAM pipeline
   - URL: http://www.iram.fr/IRAMFR/GILDAS/
    """)

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Fetch telescope data via API for G79.29+0.46'
    )
    parser.add_argument(
        '--source',
        choices=['spitzer', 'herschel', 'akari', 'iram', 'all'],
        required=True,
        help='Archive to query'
    )
    parser.add_argument(
        '--query',
        action='store_true',
        help='Query archive (show available data)'
    )
    parser.add_argument(
        '--download',
        action='store_true',
        help='Download data files'
    )
    parser.add_argument(
        '--setup',
        action='store_true',
        help='Create directory structure only'
    )
    
    args = parser.parse_args()
    
    print("="*80)
    print("TELESCOPE DATA FETCHER (API VERSION)")
    print("="*80)
    print(f"\nTarget: G79.29+0.46")
    print(f"Coordinates: {G79_COORD.to_string('hmsdms')}")
    print(f"            RA {G79_COORD.ra.deg:.5f}°, Dec {G79_COORD.dec.deg:.5f}°")
    print(f"Search radius: {SEARCH_RADIUS}")
    
    # Setup directories
    if args.setup or args.download:
        create_output_dirs()
    
    # Default to query if no action specified
    if not args.query and not args.download and not args.setup:
        args.query = True
    
    # Query archives
    results = {}
    
    if args.source == 'all' or args.source == 'spitzer':
        if args.query or args.download:
            results['spitzer'] = query_spitzer()
    
    if args.source == 'all' or args.source == 'herschel':
        if args.query or args.download:
            results['herschel'] = query_herschel()
    
    if args.source == 'all' or args.source == 'akari':
        if args.query or args.download:
            results['akari'] = query_akari()
    
    if args.source == 'iram':
        print_iram_info()
    
    # Download if requested
    if args.download:
        for source, result in results.items():
            if result is not None:
                output_dir = DATA_DIR / source
                download_data(source, result, output_dir)
    
    print("\n" + "="*80)
    print("QUERY COMPLETE")
    print("="*80)
    
    # Summary
    if results:
        print("\nResults:")
        for source, result in results.items():
            if result is not None:
                print(f"  {source}: {len(result)} observations found")
            else:
                print(f"  {source}: No data found or query failed")
    
    print("\nNext steps:")
    print("  1. Review query results")
    print("  2. Download FITS files (via web or --download)")
    print("  3. Extract radial profiles with extract_radial_profile_from_fits.py")

if __name__ == "__main__":
    main()
