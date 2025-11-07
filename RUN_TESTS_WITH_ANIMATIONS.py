#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RUN TESTS WITH ANIMATIONS - Complete test suite + animated outputs
CRITICAL: Tests run FIRST (non-blocking), animations AFTER (to avoid pipeline stalls)
© 2025 Carmen N. Wrede, Lino P. Casu, Bingsi
"""
import os, sys, subprocess
from pathlib import Path
from datetime import datetime

os.environ['PYTHONIOENCODING'] = 'utf-8:replace'
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except: pass

print("="*80)
print("COMPLETE TEST SUITE WITH ANIMATIONS")
print("="*80)
print(f"Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Object: G79.29+0.46")
print(f"Framework: Segmented Spacetime γ_seg(r)")
print("\n⚠️  Pipeline Strategy:")
print("  1. Run ALL tests first (no blocking)")
print("  2. Generate animations AFTER tests complete")
print("  3. Create variants as final step\n")

results = []

# Phase 1: Run ALL physics tests WITHOUT stopping
print("\n" + "="*80)
print("PHASE 1: PHYSICS TESTS (NON-BLOCKING)")
print("="*80)

tests = [
    ("scripts/test_segmented_spacetime_full.py", "Complete SSZ Model"),
    ("scripts/energy_release_model.py", "Energy Release Mechanism"),
    ("scripts/two_metric_model.py", "Two-Metric Comparison"),
    ("scripts/fit_gamma_seg_profile.py", "γ_seg Profile Fitting"),
]

for script, name in tests:
    script_path = Path(script)
    if not script_path.exists():
        print(f"\n⏭️ SKIP: {name} (file not found)")
        results.append((name, "SKIP"))
        continue
    
    print(f"\n{'='*80}")
    print(f"Running: {name}")
    print(f"{'='*80}\n")
    
    # Run in non-interactive mode (no blocking windows)
    env = os.environ.copy()
    env['MPLBACKEND'] = 'Agg'  # Force non-interactive matplotlib backend
    
    ret = subprocess.run(
        [sys.executable, str(script_path)],
        stdout=sys.stdout,
        stderr=sys.stderr,
        encoding='utf-8',
        errors='replace',
        env=env,
        timeout=120  # Max 2 minutes per test
    )
    
    status = "PASS" if ret.returncode == 0 else "FAIL"
    results.append((name, status))
    
    print(f"\n{'='*80}")
    print(f"{'✅' if status == 'PASS' else '❌'} {status}: {name}")
    print(f"{'='*80}")

print("\n✅ All tests completed! Now generating animations...")
print("   (This may take 2-3 minutes)")


# Phase 2: Generate animations
print("\n" + "="*80)
print("PHASE 2: ANIMATION GENERATION")
print("="*80)

print("\n[Step 1/2] Creating base animations...")
ret1 = subprocess.run(
    [sys.executable, "GENERATE_TEST_ANIMATIONS.py"],
    stdout=sys.stdout,
    stderr=sys.stderr,
    encoding='utf-8',
    errors='replace'
)

if ret1.returncode == 0:
    print("\n[Step 2/2] Creating animation variants (5s, 30s)...")
    ret2 = subprocess.run(
        [sys.executable, "CREATE_ANIMATION_VARIANTS.py"],
        stdout=sys.stdout,
        stderr=sys.stderr,
        encoding='utf-8',
        errors='replace'
    )
    
    if ret2.returncode == 0:
        results.append(("Animation Generation", "PASS"))
    else:
        results.append(("Animation Variants", "FAIL"))
else:
    results.append(("Animation Generation", "FAIL"))

# Phase 3: Summary
print("\n" + "="*80)
print("FINAL SUMMARY")
print("="*80)

passed = sum(1 for _, status in results if status == "PASS")
failed = sum(1 for _, status in results if status == "FAIL")
total = len(results)

print(f"\n📊 Results:")
print(f"  Total: {total}")
print(f"  ✅ Passed: {passed}")
print(f"  ❌ Failed: {failed}")
print(f"  Success Rate: {100*passed/total:.1f}%")

print(f"\n📋 Details:")
for test, status in results:
    symbol = "✅" if status == "PASS" else "❌"
    print(f"  {symbol} {test}: {status}")

# List generated files
print(f"\n📁 Generated Files:")
animations_dir = Path("animations")
if animations_dir.exists():
    gifs = sorted(animations_dir.glob("*.gif"))
    for gif in gifs:
        size_mb = gif.stat().st_size / 1024 / 1024
        print(f"  • {gif.name} ({size_mb:.2f} MB)")
else:
    print("  ⚠️ No animations directory found")

plots_dir = Path("results")
if plots_dir.exists():
    plots = sorted(plots_dir.glob("*.png"))
    print(f"\n📊 Static Plots:")
    for plot in plots[:5]:  # Show first 5
        size_kb = plot.stat().st_size / 1024
        print(f"  • {plot.name} ({size_kb:.1f} KB)")
    if len(plots) > 5:
        print(f"  ... and {len(plots)-5} more")

print(f"\n⏱️ Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*80)

# Exit code
sys.exit(0 if failed == 0 else 1)
