#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fetch Telescope Archive Data - G79.29+0.46

Automated download of public telescope data from various archives using astroquery.

Requirements:
    pip install astroquery

Usage:
    python fetch_telescope_data.py --source spitzer --download
    python fetch_telescope_data.py --source herschel --download
    python fetch_telescope_data.py --source akari --info

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

# Check for astroquery
try:
    from astroquery.ipac.irsa import Irsa
    from astroquery.esa.hsa import HSA
    from astropy.coordinates import SkyCoord
    import astropy.units as u
    HAS_ASTROQUERY = True
except ImportError:
    HAS_ASTROQUERY = False
    print("WARNING: astroquery not installed!")
    print("Install with: pip install astroquery")
    print("Falling back to manual instructions only")

# G79.29+0.46 coordinates
G79_RA = "20:32:32.9"
G79_DEC = "+41:19:33"
G79_RA_DEG = 308.13708  # degrees
G79_DEC_DEG = 41.32583  # degrees
G79_COORD = None
if HAS_ASTROQUERY:
    G79_COORD = SkyCoord(G79_RA, G79_DEC, unit=(u.hourangle, u.deg), frame='icrs')
SEARCH_RADIUS = 5 * u.arcmin if HAS_ASTROQUERY else 5.0  # arcmin

# Archive URLs
ARCHIVES = {
    'spitzer': {
        'name': 'Spitzer/IRSA',
        'url': 'https://irsa.ipac.caltech.edu/applications/Spitzer/SHA/',
        'api': 'https://irsa.ipac.caltech.edu/cgi-bin/Gator/nph-query',
        'public': True,
        'instructions': """
Spitzer Heritage Archive (SHA):
1. Go to: https://irsa.ipac.caltech.edu/applications/Spitzer/SHA/
2. Enter coordinates: RA={ra}, Dec={dec}
3. Select instruments: MIPS (24, 70 µm), IRS (spectroscopy)
4. Search radius: 5 arcmin
5. Download: PBCD (Post-Basic Calibrated Data)
6. Save to: data/telescope/spitzer/
        """.format(ra=G79_RA, dec=G79_DEC)
    },
    'herschel': {
        'name': 'Herschel/HSA',
        'url': 'http://archives.esac.esa.int/hsa/whsa/',
        'public': True,
        'requires_account': True,
        'instructions': """
Herschel Science Archive (HSA):
1. Create free account: http://archives.esac.esa.int/hsa/whsa/
2. Login to archive
3. Search: "G79.29+0.46" or coordinates
4. Select: PACS ([CII], [OI]) + SPIRE (250, 350, 500 µm)
5. Download: Level 2.5 (fully reduced FITS)
6. Save to: data/telescope/herschel/
        """
    },
    'akari': {
        'name': 'AKARI/DARTS',
        'url': 'https://darts.isas.jaxa.jp/astro/akari/',
        'public': True,
        'instructions': """
AKARI Data Archive:
1. Go to: https://darts.isas.jaxa.jp/astro/akari/
2. Search by coordinates: RA={ra_deg}, Dec={dec_deg}
3. Select bands: 65, 90, 140, 160 µm
4. Download FITS images
5. Save to: data/telescope/akari/
        """.format(ra_deg=G79_RA_DEG, dec_deg=G79_DEC_DEG)
    },
    'iram': {
        'name': 'IRAM Archive',
        'url': 'http://www.iram.fr/IRAMFR/GILDAS/',
        'public': True,
        'requires_software': 'GILDAS',
        'instructions': """
IRAM 30m Archive (CO observations):
1. Go to: http://www.iram.fr/IRAMFR/GILDAS/
2. Search for G79.29+0.46 project
3. Check Rizzo et al. 2008 for project ID
4. Download CO (2-1), (3-2) cubes
5. Format: CLASS/FITS
6. Save to: data/telescope/iram/

Alternative: Contact IRAM directly
Email: gildas@iram.fr
Subject: Data request for G79.29+0.46 CO observations
        """
    },
    'effelsberg': {
        'name': 'Effelsberg 100m',
        'url': 'https://www.mpifr-bonn.mpg.de/2169/en',
        'public': False,
        'requires_request': True,
        'contact': 'archive@mpifr-bonn.mpg.de',
        'instructions': """
Effelsberg NH₃ Archive (Request Required):

Email template:
--------------
To: archive@mpifr-bonn.mpg.de
Subject: Data request for G79.29+0.46 NH₃ observations

Dear Effelsberg Archive Team,

We are conducting an analysis of the LBV nebula G79.29+0.46 
following up on the NH₃ observations published in Rizzo et al. 
(2014, A&A). Could you please provide access to the FITS cubes 
for the NH₃ (1,1)-(3,3) observations?

Project reference: Rizzo 2014, A&A, Table 1
Source: G79.29+0.46 / IRAS 20308+4104
Coordinates: RA {ra}, Dec {dec}

Purpose: SSZ theoretical model validation
Institution: [Your institution]

Best regards,
[Your name]
--------------

Save received data to: data/telescope/effelsberg/
        """.format(ra=G79_RA, dec=G79_DEC)
    }
}

def create_data_dirs():
    """Create directory structure for telescope data"""
    base_dir = Path('data/telescope')
    for source in ARCHIVES.keys():
        (base_dir / source).mkdir(parents=True, exist_ok=True)
    print(f"[OK] Created data directories in {base_dir}")

def print_archive_info(source):
    """Print information about a specific archive"""
    if source not in ARCHIVES:
        print(f"ERROR: Unknown source '{source}'")
        print(f"Available: {', '.join(ARCHIVES.keys())}")
        return
    
    info = ARCHIVES[source]
    
    print("="*80)
    print(f"ARCHIVE: {info['name']}")
    print("="*80)
    print(f"\nURL: {info['url']}")
    print(f"Public Access: {'Yes' if info['public'] else 'No (request required)'}")
    
    if info.get('requires_account'):
        print("Account Required: Yes (free registration)")
    if info.get('requires_request'):
        print(f"Contact: {info.get('contact')}")
    
    print("\nINSTRUCTIONS:")
    print(info['instructions'])
    print("="*80)

def search_spitzer_programmatically(download=False):
    """
    Automated search of Spitzer archive
    
    Note: This is a template - actual API access requires authentication
    """
    print("\n[INFO] Searching Spitzer/IRSA...")
    print("[INFO] Automated download requires API authentication")
    print("[INFO] Use web interface: https://irsa.ipac.caltech.edu/applications/Spitzer/SHA/")
    
    # Example query (would need proper authentication)
    params = {
        'catalog': 'spitzer_sha',
        'spatial': 'cone',
        'objstr': f"{G79_RA_DEG} {G79_DEC_DEG}",
        'radius': '5',  # arcmin
        'outfmt': '3'  # JSON
    }
    
    query_url = f"{ARCHIVES['spitzer']['api']}?{urlencode(params)}"
    print(f"\n[INFO] Query URL: {query_url}")
    print("[INFO] For manual search, use web interface")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Fetch telescope archive data for G79.29+0.46'
    )
    parser.add_argument(
        '--source',
        choices=list(ARCHIVES.keys()) + ['all'],
        help='Archive to query'
    )
    parser.add_argument(
        '--info',
        action='store_true',
        help='Show information only (no download)'
    )
    parser.add_argument(
        '--download',
        action='store_true',
        help='Attempt automated download (if supported)'
    )
    parser.add_argument(
        '--setup',
        action='store_true',
        help='Create directory structure only'
    )
    
    args = parser.parse_args()
    
    print("="*80)
    print("TELESCOPE DATA FETCHER - G79.29+0.46")
    print("="*80)
    print(f"\nTarget: G79.29+0.46")
    print(f"Coordinates: RA {G79_RA}, Dec {G79_DEC}")
    print(f"            RA {G79_RA_DEG}°, Dec {G79_DEC_DEG}°")
    print()
    
    # Setup directories
    if args.setup or args.source:
        create_data_dirs()
    
    # Show info for all archives
    if args.source == 'all' or not args.source:
        print("\nAVAILABLE ARCHIVES:")
        print("-"*80)
        for source in ARCHIVES.keys():
            print(f"\n{source.upper()}: {ARCHIVES[source]['name']}")
            print(f"  URL: {ARCHIVES[source]['url']}")
            print(f"  Public: {'Yes' if ARCHIVES[source]['public'] else 'Request'}")
        print("\nUse --source <name> for detailed instructions")
        return
    
    # Show specific archive info
    if args.source and args.source != 'all':
        print_archive_info(args.source)
        
        if args.download:
            if args.source == 'spitzer':
                search_spitzer_programmatically(download=True)
            else:
                print("\n[INFO] Automated download not yet implemented for this archive")
                print("[INFO] Please follow manual instructions above")

if __name__ == "__main__":
    main()
