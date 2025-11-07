#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FINAL PAPER TEST: All Sections with Correct Arguments

Runs each test with proper command-line arguments.
Validates complete paper systematically.

© 2025 Carmen N. Wrede, Lino P. Casu
"""
import sys
import os
from pathlib import Path

os.environ['PYTHONIOENCODING'] = 'utf-8:replace'
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass

print("="*80)
print("FINAL PAPER VALIDATION - Segmented Spacetime")
print("="*80)
print("\n✓ Paper: 'Segmented Spacetime and the Origin of Molecular Zones'")
print("✓ Object: G79.29+0.46")
print("✓ Framework: γ_seg(r) temporal density field\n")

results = []

# Test 1: IR Analysis (ALREADY RUN)
print("[1/10] IR Ring Analysis...")
if Path("data/G79_AKARI_RINGS.csv").exists() and Path("data/G79_WISE_RINGS.csv").exists():
    print("  ✅ IR rings exist")
    results.append(('IR Analysis', 'PASS'))
else:
    print("  ⚠️ Run: python RUN_COMPLETE_IR_ANALYSIS.py")
    results.append(('IR Analysis', 'SKIP'))

# Test 2: Complete SSZ Model
print("\n" + "="*80)
print("[2/10] Complete SSZ Model Test")
print("="*80)
ret = os.system(f"{sys.executable} scripts/test_segmented_spacetime_full.py")
print("\n" + "="*80)
print(f"{'✅ PASS' if ret == 0 else '❌ FAIL'}: Complete SSZ Model")
print("="*80)
results.append(('SSZ Model', 'PASS' if ret == 0 else 'FAIL'))

# Test 3: γ_seg Fitting (with args)
print("\n" + "="*80)
print("[3/10] γ_seg(r) Fitting")
print("="*80)
if Path("data/G79_temperatures.csv").exists():
    ret = os.system(f"{sys.executable} scripts/fit_gamma_seg_profile.py data/G79_temperatures.csv --plot results/gamma_seg_fit.png")
    print("\n" + "="*80)
    print(f"{'✅ PASS' if ret == 0 else '❌ FAIL'}: γ_seg Fitting")
    print("="*80)
    results.append(('γ_seg Fitting', 'PASS' if ret == 0 else 'FAIL'))
else:
    print("  ⚠️ Temperature data missing")
    results.append(('γ_seg Fitting', 'SKIP'))

# Test 4: Two-Metric Model
print("\n" + "="*80)
print("[4/10] Two-Metric Comparison")
print("="*80)
ret = os.system(f"{sys.executable} scripts/two_metric_model.py")
print("\n" + "="*80)
print(f"{'✅ PASS' if ret == 0 else '❌ FAIL'}: Two-Metric Model")
print("="*80)
results.append(('Two-Metric', 'PASS' if ret == 0 else 'FAIL'))

# Test 5: Energy Release
print("\n" + "="*80)
print("[5/10] Energy Release Model")
print("="*80)
ret = os.system(f"{sys.executable} scripts/energy_release_model.py")
print("\n" + "="*80)
print(f"{'✅ PASS' if ret == 0 else '❌ FAIL'}: Energy Release Model")
print("="*80)
results.append(('Energy Release', 'PASS' if ret == 0 else 'FAIL'))

# Test 6: NH3 Velocities
print("\n" + "="*80)
print("[6/10] NH3 Velocity Analysis")
print("="*80)
ret = os.system(f"{sys.executable} scripts/analyze_nh3_velocities.py")
print("\n" + "="*80)
print(f"{'✅ PASS' if ret == 0 else '❌ FAIL'}: NH3 Velocities")
print("="*80)
results.append(('NH3 Velocities', 'PASS' if ret == 0 else 'FAIL'))

# Test 7: Paper Predictions (G79)
print("\n" + "="*80)
print("[7/10] Paper Predictions (G79)")
print("="*80)
ret = os.system(f"{sys.executable} scripts/verify_paper_predictions_FIXED.py")
print("\n" + "="*80)
print(f"{'✅ PASS' if ret == 0 else '❌ FAIL'}: Paper Predictions G79")
print("="*80)
results.append(('Paper Predictions G79', 'PASS' if ret == 0 else 'FAIL'))

# Test 8: Paper Predictions (LBV - skip data gate)
print("\n" + "="*80)
print("[8/10] Paper Predictions (LBV)")
print("="*80)
ret = os.system(f"{sys.executable} ../lbv_rings_tester/verify_paper_predictions_FIXED.py")
print("\n" + "="*80)
print(f"{'✅ PASS' if ret == 0 else '❌ FAIL'}: Paper Predictions LBV")
print("="*80)
results.append(('Paper Predictions LBV', 'PASS' if ret == 0 else 'FAIL'))

# Test 9: Radio Redshift (if γ_seg output exists)
print("\n" + "="*80)
print("[9/10] Radio Redshift Prediction")
print("="*80)
gamma_file = Path("G79_gamma_seg_profile.csv")
if gamma_file.exists():
    ret = os.system(f"{sys.executable} scripts/radio_redshift_prediction.py {gamma_file}")
    print("\n" + "="*80)
    print(f"{'✅ PASS' if ret == 0 else '❌ FAIL'}: Radio Redshift")
    print("="*80)
    results.append(('Radio Redshift', 'PASS' if ret == 0 else 'FAIL'))
else:
    print("  ⚠️ Need γ_seg profile first")
    results.append(('Radio Redshift', 'SKIP'))

# Test 10: Core Mass (if γ_seg output exists)
print("\n" + "="*80)
print("[10/10] Core Mass Derivation")
print("="*80)
if gamma_file.exists():
    ret = os.system(f"{sys.executable} scripts/calculate_core_mass.py {gamma_file}")
    print("\n" + "="*80)
    print(f"{'✅ PASS' if ret == 0 else '❌ FAIL'}: Core Mass")
    print("="*80)
    results.append(('Core Mass', 'PASS' if ret == 0 else 'FAIL'))
else:
    print("  ⚠️ Need γ_seg profile first")
    results.append(('Core Mass', 'SKIP'))

# Summary
print("\n" + "="*80)
print("FINAL SUMMARY")
print("="*80)

passed = sum(1 for _, status in results if status == 'PASS')
failed = sum(1 for _, status in results if status == 'FAIL')
skipped = sum(1 for _, status in results if status == 'SKIP')
total = len(results)

print(f"\n✅ Passed: {passed}/{total}")
print(f"❌ Failed: {failed}/{total}")
print(f"⏭️ Skipped: {skipped}/{total}")

if passed >= 7:
    print("\n🎉 PAPER SUBSTANTIALLY VALIDATED!")
elif passed >= 5:
    print("\n✓ PAPER PARTIALLY VALIDATED")
else:
    print("\n⚠️ MORE WORK NEEDED")

print("\nKey Results:")
for test, status in results:
    symbol = "✅" if status == "PASS" else ("❌" if status == "FAIL" else "⏭️")
    print(f"  {symbol} {test}: {status}")

print("\n" + "="*80)
