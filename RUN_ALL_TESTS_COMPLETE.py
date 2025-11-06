#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete Test Runner - All Scripts & Validation
Generates full-output.md with all test results

© 2025 Carmen N. Wrede, Lino P. Casu, Bingsi
"""
import os
import sys
import io
import subprocess
import time
from pathlib import Path
from datetime import datetime

# UTF-8 for Windows - CRITICAL FIX
os.environ['PYTHONIOENCODING'] = 'utf-8:replace'

# Reconfigure stdout for UTF-8 (Windows compatibility)
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        # Fallback for older Python or redirected output
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

def print_header(title):
    """Print section header"""
    print("\n" + "="*80)
    print(f" {title}")
    print("="*80)

def run_script(script_path, description):
    """Run a Python script and capture output"""
    print(f"\n>> Running: {description}")
    print(f"   Script: {script_path}")
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=60
        )
        
        elapsed = time.time() - start_time
        
        if result.returncode == 0:
            print(f"   [PASS] ({elapsed:.1f}s)")
            return {
                'script': str(script_path),
                'description': description,
                'status': 'PASS',
                'time': elapsed,
                'output': result.stdout,
                'error': result.stderr
            }
        else:
            print(f"   [FAIL] ({elapsed:.1f}s)")
            print(f"   Error: {result.stderr[:200]}")
            return {
                'script': str(script_path),
                'description': description,
                'status': 'FAIL',
                'time': elapsed,
                'output': result.stdout,
                'error': result.stderr
            }
            
    except subprocess.TimeoutExpired:
        print(f"   [TIMEOUT] (>60s)")
        return {
            'script': str(script_path),
            'description': description,
            'status': 'TIMEOUT',
            'time': 60.0,
            'output': '',
            'error': 'Timeout after 60 seconds'
        }
    except Exception as e:
        print(f"   [ERROR]: {str(e)}")
        return {
            'script': str(script_path),
            'description': description,
            'status': 'ERROR',
            'time': 0.0,
            'output': '',
            'error': str(e)
        }

def main():
    """Main test runner"""
    print_header("COMPLETE TEST RUN - ALL SCRIPTS")
    
    start_time = datetime.now()
    print(f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Base directory
    base_dir = Path(__file__).parent
    scripts_dir = base_dir / 'scripts'
    
    results = []
    
    # ========================================================================
    # CATEGORY 1: Core Physics Scripts
    # ========================================================================
    print_header("CATEGORY 1: Core Physics & Mass Calculations")
    
    physics_scripts = [
        ('scripts/calculate_core_mass.py', 'Core Mass Calculation'),
        ('scripts/core_mass_empirical.py', 'Empirical Core Mass'),
        ('scripts/energy_release_model.py', 'Energy Release Model'),
        ('scripts/fit_gamma_seg_profile.py', 'Gamma_seg Profile Fitting'),
        ('scripts/radio_redshift_prediction.py', 'Radio Redshift Prediction'),
    ]
    
    for script, desc in physics_scripts:
        script_path = base_dir / script
        if script_path.exists():
            results.append(run_script(script_path, desc))
        else:
            print(f"   [SKIP]: {script} (not found)")
    
    # ========================================================================
    # CATEGORY 2: Velocity & Boundary Tests
    # ========================================================================
    print_header("CATEGORY 2: Velocity & Boundary Tests")
    
    velocity_scripts = [
        ('scripts/test_boundary_velocity_boost.py', 'Boundary Velocity Boost'),
        ('scripts/test_boundary_v_realistic.py', 'Realistic Velocity Test'),
        ('scripts/analyze_nh3_velocities.py', 'NH3 Velocity Analysis'),
    ]
    
    for script, desc in velocity_scripts:
        script_path = base_dir / script
        if script_path.exists():
            results.append(run_script(script_path, desc))
        else:
            print(f"   [SKIP]: {script} (not found)")
    
    # ========================================================================
    # CATEGORY 3: Data Processing
    # ========================================================================
    print_header("CATEGORY 3: Data Processing & FITS Analysis")
    
    data_scripts = [
        ('scripts/extract_co_velocity_rings.py', 'CO Velocity Ring Extraction'),
        ('scripts/catalog_to_rings.py', 'Catalog to Rings Conversion'),
        ('scripts/process_ir_catalogs.py', 'IR Catalog Processing'),
    ]
    
    for script, desc in data_scripts:
        script_path = base_dir / script
        if script_path.exists():
            results.append(run_script(script_path, desc))
        else:
            print(f"   [SKIP]: {script} (not found)")
    
    # ========================================================================
    # CATEGORY 4: Validation & Verification
    # ========================================================================
    print_header("CATEGORY 4: Paper Validation & Verification")
    
    validation_scripts = [
        ('scripts/verify_paper_predictions_FIXED.py', 'Paper Predictions Verification'),
        ('scripts/test_segmented_spacetime_full.py', 'Full Segmented Spacetime Test'),
        ('scripts/two_metric_model.py', 'Two-Metric Model Test'),
    ]
    
    for script, desc in validation_scripts:
        script_path = base_dir / script
        if script_path.exists():
            results.append(run_script(script_path, desc))
        else:
            print(f"   [SKIP]: {script} (not found)")
    
    # ========================================================================
    # Summary
    # ========================================================================
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print_header("TEST SUMMARY")
    
    total = len(results)
    passed = sum(1 for r in results if r['status'] == 'PASS')
    failed = sum(1 for r in results if r['status'] == 'FAIL')
    errors = sum(1 for r in results if r['status'] == 'ERROR')
    timeouts = sum(1 for r in results if r['status'] == 'TIMEOUT')
    
    print(f"\nTotal Tests:    {total}")
    print(f"[+] Passed:     {passed}")
    print(f"[-] Failed:     {failed}")
    print(f"[!] Errors:     {errors}")
    print(f"[T] Timeouts:   {timeouts}")
    print(f"\nSuccess Rate:   {100*passed/total if total > 0 else 0:.1f}%")
    print(f"Total Duration: {duration:.1f}s")
    
    # ========================================================================
    # Generate Markdown Report
    # ========================================================================
    print_header("GENERATING MARKDOWN REPORT")
    
    report_path = Path('D:/g79_publication_backup/FULL_OUTPUT.md')
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# Complete Test Run - Full Output\n\n")
        f.write(f"**Date:** {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Duration:** {duration:.1f} seconds\n")
        f.write(f"**Total Tests:** {total}\n\n")
        
        f.write("---\n\n")
        f.write("## Summary\n\n")
        f.write(f"- [+] Passed: {passed}/{total}\n")
        f.write(f"- [-] Failed: {failed}/{total}\n")
        f.write(f"- [!] Errors: {errors}/{total}\n")
        f.write(f"- [T] Timeouts: {timeouts}/{total}\n")
        f.write(f"- **Success Rate:** {100*passed/total if total > 0 else 0:.1f}%\n\n")
        
        f.write("---\n\n")
        f.write("## Detailed Results\n\n")
        
        for i, result in enumerate(results, 1):
            status_icon = {
                'PASS': '[PASS]',
                'FAIL': '[FAIL]',
                'ERROR': '[ERROR]',
                'TIMEOUT': '[TIMEOUT]'
            }.get(result['status'], '[?]')
            
            f.write(f"### {i}. {result['description']}\n\n")
            f.write(f"**Status:** {status_icon} {result['status']}\n")
            f.write(f"**Script:** `{result['script']}`\n")
            f.write(f"**Time:** {result['time']:.2f}s\n\n")
            
            if result['output']:
                f.write("**Output:**\n```\n")
                f.write(result['output'])  
                f.write("\n```\n\n")
            
            if result['error']:
                f.write("**Error:**\n```\n")
                f.write(result['error'])  
                f.write("\n```\n\n")
            
            f.write("---\n\n")
        
        f.write("## End of Report\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("\n© 2025 Carmen N. Wrede, Lino P. Casu, Bingsi\n")
    
    print(f"\n[+] Report saved to: {report_path}")
    
    # ========================================================================
    # Exit
    # ========================================================================
    if failed > 0 or errors > 0:
        print("\n[!] Some tests failed! Review the report.")
        return 1
    else:
        print("\n[+] All tests passed!")
        return 0

if __name__ == '__main__':
    sys.exit(main())
