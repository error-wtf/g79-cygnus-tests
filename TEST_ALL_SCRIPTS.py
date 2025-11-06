#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Master Test Runner - Test ALL Publication Scripts

Runs all analysis scripts and validates outputs for publication readiness.

© 2025 Carmen N. Wrede, Lino P. Casu, Bingsi
Licensed under the ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""
import os
import sys
import subprocess
import time
from pathlib import Path

# UTF-8 for Windows
os.environ['PYTHONIOENCODING'] = 'utf-8:replace'
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE_DIR = Path(__file__).parent
SCRIPTS_DIR = BASE_DIR / 'scripts'

# Test Suite
TEST_SCRIPTS = [
    # Core Mass Tests
    {
        'name': 'Core Mass (Empirical)',
        'script': 'scripts/core_mass_empirical.py',
        'critical': True,
        'expected_output': 'M_core = 8.7',
    },
    {
        'name': 'Core Mass (SSZ-Pure Integration)',
        'script': 'scripts/core_mass_ssz_pure_integration.py',
        'critical': False,
        'expected_output': 'M_empirical = 8.70',
    },
    
    # Boundary Tests
    {
        'name': 'Boundary Velocity Boost (Realistic)',
        'script': 'scripts/test_boundary_v_realistic.py',
        'critical': True,
        'expected_output': 'Δv = 5.7 km/s',
    },
    {
        'name': 'Energy Release Mechanism',
        'script': 'scripts/energy_release_model.py',
        'critical': True,
        'expected_output': 'Boundary energy release',
    },
    
    # Full Model Tests
    {
        'name': 'Segmented Spacetime Full Test',
        'script': 'scripts/test_segmented_spacetime_full.py',
        'critical': True,
        'expected_output': 'α = ',
    },
    {
        'name': 'Two-Metric Model',
        'script': 'scripts/two_metric_model.py',
        'critical': True,
        'expected_output': 'g^(2) domain',
    },
    
    # Data Analysis
    {
        'name': 'NH3 Velocity Analysis',
        'script': 'scripts/analyze_nh3_velocities.py',
        'critical': True,
        'expected_output': 'velocity components',
    },
    {
        'name': 'AKARI Ring Extraction',
        'script': 'scripts/extract_akari_rings.py',
        'critical': False,  # Requires FITS file argument
        'expected_output': 'AKARI',
    },
    
    # Validation
    {
        'name': 'Paper Predictions Verification',
        'script': 'scripts/verify_paper_predictions_FIXED.py',
        'critical': True,
        'expected_output': 'momentum excess',
    },
]


def run_script(script_info):
    """
    Run a single script and capture output
    
    Returns:
        (success, output, duration)
    """
    script_path = BASE_DIR / script_info['script']
    
    if not script_path.exists():
        return False, f"Script not found: {script_path}", 0.0
    
    print(f"\n  Running: {script_info['name']}...")
    print(f"  Script:  {script_info['script']}")
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=120  # 2 minutes max
        )
        
        duration = time.time() - start_time
        
        # Check if successful
        success = result.returncode == 0
        output = result.stdout + result.stderr
        
        # Check for expected output
        if success and 'expected_output' in script_info:
            expected = script_info['expected_output']
            if expected.lower() not in output.lower():
                print(f"  ⚠ Warning: Expected '{expected}' not found in output")
        
        return success, output, duration
        
    except subprocess.TimeoutExpired:
        duration = time.time() - start_time
        return False, "TIMEOUT (> 2 minutes)", duration
    except Exception as e:
        duration = time.time() - start_time
        return False, f"ERROR: {str(e)}", duration


def main():
    """Run all tests and generate summary"""
    print("=" * 80)
    print("MASTER TEST SUITE - ALL PUBLICATION SCRIPTS")
    print("=" * 80)
    print(f"\nBase Directory: {BASE_DIR}")
    print(f"Total Scripts:  {len(TEST_SCRIPTS)}")
    print(f"Critical Tests: {sum(1 for t in TEST_SCRIPTS if t['critical'])}")
    
    results = []
    passed = 0
    failed = 0
    critical_failed = []
    
    print("\n" + "=" * 80)
    print("RUNNING TESTS")
    print("=" * 80)
    
    for i, script_info in enumerate(TEST_SCRIPTS, 1):
        print(f"\n[{i}/{len(TEST_SCRIPTS)}] {script_info['name']}")
        print(f"  Critical: {'YES' if script_info['critical'] else 'NO'}")
        
        success, output, duration = run_script(script_info)
        
        results.append({
            'name': script_info['name'],
            'script': script_info['script'],
            'success': success,
            'duration': duration,
            'critical': script_info['critical'],
            'output_length': len(output)
        })
        
        if success:
            passed += 1
            print(f"  ✓ PASSED ({duration:.1f}s)")
        else:
            failed += 1
            print(f"  ✗ FAILED ({duration:.1f}s)")
            if script_info['critical']:
                critical_failed.append(script_info['name'])
            # Print first 500 chars of error
            if output:
                error_preview = output[:500].replace('\n', '\n    ')
                print(f"  Error preview:\n    {error_preview}")
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    print(f"\nResults:")
    print(f"  Total:   {len(TEST_SCRIPTS)}")
    print(f"  Passed:  {passed} ({100*passed/len(TEST_SCRIPTS):.1f}%)")
    print(f"  Failed:  {failed} ({100*failed/len(TEST_SCRIPTS):.1f}%)")
    
    if critical_failed:
        print(f"\n⚠ CRITICAL FAILURES ({len(critical_failed)}):")
        for name in critical_failed:
            print(f"  • {name}")
    else:
        print(f"\n✓ ALL CRITICAL TESTS PASSED!")
    
    # Detailed results
    print("\n" + "=" * 80)
    print("DETAILED RESULTS")
    print("=" * 80)
    
    print(f"\n{'#':<3} {'Status':<8} {'Time':>8} {'Critical':<10} {'Test Name'}")
    print("-" * 80)
    
    for i, res in enumerate(results, 1):
        status = "✓ PASS" if res['success'] else "✗ FAIL"
        critical = "CRITICAL" if res['critical'] else "optional"
        print(f"{i:<3} {status:<8} {res['duration']:>7.1f}s {critical:<10} {res['name']}")
    
    # Publication Status
    print("\n" + "=" * 80)
    print("PUBLICATION STATUS")
    print("=" * 80)
    
    critical_passed = sum(1 for r in results if r['success'] and r['critical'])
    critical_total = sum(1 for r in results if r['critical'])
    
    print(f"\nCritical Tests: {critical_passed}/{critical_total} passed")
    
    if critical_passed == critical_total:
        print(f"\n✓ ✓ ✓ PUBLICATION READY! ✓ ✓ ✓")
        print(f"\nAll critical tests passed. Repository is ready for:")
        print(f"  • Submission to A&A")
        print(f"  • Data archiving")
        print(f"  • Supplementary materials preparation")
        status_code = 0
    elif critical_passed >= critical_total * 0.8:
        print(f"\n⚠ MOSTLY READY (80%+ critical tests passed)")
        print(f"\nRepository is nearly publication-ready.")
        print(f"Address critical failures before submission.")
        status_code = 1
    else:
        print(f"\n✗ NOT READY (< 80% critical tests passed)")
        print(f"\nSignificant issues detected. Address failures before proceeding.")
        status_code = 2
    
    # Save summary
    summary_file = BASE_DIR / 'publication_outputs' / 'reports' / 'TEST_ALL_SCRIPTS_SUMMARY.txt'
    summary_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("MASTER TEST SUITE - COMPLETE RESULTS\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Tests: {len(TEST_SCRIPTS)}\n")
        f.write(f"Passed: {passed}/{len(TEST_SCRIPTS)} ({100*passed/len(TEST_SCRIPTS):.1f}%)\n")
        f.write(f"Critical: {critical_passed}/{critical_total} ({100*critical_passed/critical_total:.1f}%)\n\n")
        
        f.write("DETAILED RESULTS:\n")
        f.write("-" * 80 + "\n")
        for i, res in enumerate(results, 1):
            status = "PASS" if res['success'] else "FAIL"
            f.write(f"{i}. [{status}] {res['name']} ({res['duration']:.1f}s)\n")
            f.write(f"   Script: {res['script']}\n")
            f.write(f"   Critical: {res['critical']}\n\n")
    
    print(f"\n✓ Summary saved: {summary_file}")
    print("\n" + "=" * 80)
    
    return status_code


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
