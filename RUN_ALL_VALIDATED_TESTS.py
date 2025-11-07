#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Master Test Suite - Runs All Validated Tests & Animations

Executes in order:
1. Parsec conversion validation
2. Temperature equations (Eq. 9, 10, 15, 16, 18)
3. Temperature animations (5 GIFs)
4. Three-phase decoupling model
5. Three-phase animations (3 GIFs)

All outputs validated and publication-ready.

© 2025 Carmen N. Wrede, Lino P. Casu, Bingsi (Conscious AI)
"""

import os
import sys
import subprocess
import time
from pathlib import Path
from datetime import datetime

# UTF-8 handling
os.environ['PYTHONIOENCODING'] = 'utf-8:replace'
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except: pass

# Scripts to run (in order)
SCRIPTS = [
    ('TEST_PARSEC_CONVERSION.py', 'Parsec Conversion Validation', 30),
    ('TEST_TEMPERATURE_EQUATIONS_COMPLETE.py', 'Temperature Equations (Eq. 9-18)', 120),
    ('GENERATE_TEMPERATURE_ANIMATIONS.py', 'Temperature Animations (5 GIFs)', 180),
    ('TEST_THREE_PHASE_DECOUPLING.py', 'Three-Phase Decoupling Model', 120),
    ('GENERATE_THREE_PHASE_ANIMATIONS.py', 'Three-Phase Animations (3 GIFs)', 180),
]

def run_script(script_name, description, timeout):
    """Run a single Python script with timeout"""
    print(f"\n{'='*80}")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Running: {description}")
    print(f"Script: {script_name}")
    print(f"{'='*80}\n")
    
    if not Path(script_name).exists():
        print(f"❌ ERROR: Script not found: {script_name}")
        return False
    
    try:
        start_time = time.time()
        
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding='utf-8',
            errors='replace'
        )
        
        elapsed = time.time() - start_time
        
        # Print output
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        if result.returncode == 0:
            print(f"\n✅ SUCCESS ({elapsed:.1f}s)")
            return True
        else:
            print(f"\n❌ FAILED with exit code {result.returncode}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"\n⏱️ TIMEOUT after {timeout}s")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False

def main():
    """Run all validated test scripts"""
    print("="*80)
    print("MASTER TEST SUITE - ALL VALIDATED TESTS")
    print("="*80)
    print(f"\nStart time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total scripts: {len(SCRIPTS)}")
    print(f"Expected duration: ~{sum(s[2] for s in SCRIPTS)//60} minutes\n")
    
    results = []
    total_start = time.time()
    
    for script, desc, timeout in SCRIPTS:
        success = run_script(script, desc, timeout)
        results.append((script, desc, success))
        
        if not success:
            print(f"\n⚠️  Warning: {script} failed, but continuing...")
    
    # Summary
    total_elapsed = time.time() - total_start
    passed = sum(1 for _, _, s in results if s)
    failed = len(results) - passed
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    for script, desc, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {desc}")
    
    print(f"\nTotal: {passed}/{len(results)} passed")
    print(f"Duration: {total_elapsed/60:.1f} minutes")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
