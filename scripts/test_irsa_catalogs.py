#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test different IRSA catalog names to find what works
"""
import sys
import os
os.environ['PYTHONIOENCODING'] = 'utf-8:replace'
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass

try:
    from astroquery.ipac.irsa import Irsa
    from astropy.coordinates import SkyCoord
    import astropy.units as u
except ImportError as e:
    print(f"ERROR: {e}")
    sys.exit(1)

G79_COORD = SkyCoord(ra=307.920833*u.deg, dec=40.351944*u.deg, frame='icrs')
radius = 10 * u.arcmin

# List of possible catalog names to try
catalogs_to_try = [
    # AKARI
    "akari_fis",
    "akari_fis_bsc",
    "akari_irc",
    "fp_psc",
    
    # Spitzer
    "spitzer_seip",
    "spitzer_irac",
    "spitzer_mips",
    
    # WISE
    "allwise_p3as_psd",
    "wise_allsky_4band_p3as_psd",
    "allwise_p3as_mep",
    
    # 2MASS
    "fp_psc",
    "twomass_psc",
]

print("="*80)
print("TESTING IRSA CATALOG NAMES")
print("="*80)

Irsa.ROW_LIMIT = 10

for catalog in catalogs_to_try:
    try:
        print(f"\nTrying: {catalog}...", end=" ")
        result = Irsa.query_region(G79_COORD, catalog=catalog, radius=radius)
        if result:
            print(f"✓ WORKS! Found {len(result)} sources")
            print(f"  Columns: {result.colnames[:5]}...")
            # Save this one!
            result.write(f"data/telescope/{catalog}_test.csv", format='csv', overwrite=True)
        else:
            print("✓ Works but no data")
    except Exception as e:
        print(f"✗ Failed: {str(e)[:50]}")

print("\n" + "="*80)
print("Check data/telescope/ for successful catalogs!")
print("="*80)
