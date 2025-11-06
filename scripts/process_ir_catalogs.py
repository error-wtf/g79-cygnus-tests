#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Process ALL IR Catalogs (AKARI + WISE) to Ring Profiles

Quick-run script that processes both AKARI and WISE catalogs
and creates ring profiles for all available bands.

Usage:
    python scripts/process_ir_catalogs.py

Output:
    - data/telescope/akari_fis_rings.csv
    - data/telescope/allwise_rings.csv

© 2025 Carmen N. Wrede, Lino P. Casu
Licensed under ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""
import sys
import os
import subprocess
from pathlib import Path

# UTF-8 for Windows
os.environ['PYTHONIOENCODING'] = 'utf-8:replace'
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass

def run_catalog_conversion(catalog_file, bands, output_name=None):
    """Run catalog_to_rings.py for a specific catalog"""
    
    cmd = [
        sys.executable,
        "scripts/catalog_to_rings.py",
        catalog_file,
        "--bands", bands
    ]
    
    if output_name:
        cmd.extend(["--output", output_name])
    
    print(f"\nRunning: {' '.join(cmd)}")
    print("="*80)
    
    result = subprocess.run(
        cmd,
        encoding='utf-8',
        errors='replace'
    )
    
    if result.returncode != 0:
        print(f"\n⚠️  WARNING: Command failed with exit code {result.returncode}")
        return False
    
    return True

def main():
    """Process all IR catalogs"""
    
    print("="*80)
    print("IR CATALOG BATCH PROCESSING")
    print("="*80)
    print("\nThis will convert AKARI + WISE catalogs to ring profiles")
    print("Ring configuration: 0-2 pc in 0.2 pc steps (10 rings)")
    
    # Check if catalog_to_rings.py exists
    if not Path("scripts/catalog_to_rings.py").exists():
        print("\nERROR: scripts/catalog_to_rings.py not found!")
        return 1
    
    success_count = 0
    total_count = 0
    
    # 1. AKARI FIS - All 4 bands
    print("\n" + "="*80)
    print("[1/2] AKARI FIS (Far-Infrared)")
    print("="*80)
    
    total_count += 1
    if run_catalog_conversion(
        "data/telescope/akari_fis_test.csv",
        "flux65,flux90,flux140,flux160",
        "data/telescope/akari_fis_rings.csv"
    ):
        success_count += 1
        print("✓ AKARI FIS rings created!")
    
    # 2. WISE - All 4 bands (magnitudes)
    print("\n" + "="*80)
    print("[2/2] WISE AllWISE (Mid-Infrared)")
    print("="*80)
    
    total_count += 1
    if run_catalog_conversion(
        "data/telescope/allwise_p3as_psd_test.csv",
        "w1mpro,w2mpro,w3mpro,w4mpro",
        "data/telescope/allwise_rings.csv"
    ):
        success_count += 1
        print("✓ WISE rings created!")
    
    # Summary
    print("\n" + "="*80)
    print("BATCH PROCESSING COMPLETE")
    print("="*80)
    print(f"\nSuccess: {success_count}/{total_count} catalogs")
    
    if success_count > 0:
        print("\n📁 Output Files:")
        if Path("data/telescope/akari_fis_rings.csv").exists():
            print("   - data/telescope/akari_fis_rings.csv")
        if Path("data/telescope/allwise_rings.csv").exists():
            print("   - data/telescope/allwise_rings.csv")
        
        print("\n🎯 Next Steps:")
        print("   1. Validate ring profiles visually")
        print("   2. Convert WISE magnitudes to flux if needed")
        print("   3. Fit γ_seg(r) profiles:")
        print("      python scripts/fit_gamma_seg_profile.py data/telescope/akari_fis_rings.csv")
        print("      python scripts/fit_gamma_seg_profile.py data/telescope/allwise_rings.csv")
    
    print("\n" + "="*80)
    
    return 0 if success_count == total_count else 1

if __name__ == "__main__":
    sys.exit(main())
