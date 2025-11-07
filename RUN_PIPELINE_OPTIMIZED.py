#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OPTIMIZED PIPELINE - Tests THEN Animations (non-blocking)
Critical design: NO matplotlib windows during tests, animations only at end
© 2025 Carmen N. Wrede, Lino P. Casu, Bingsi
"""
import os, sys, subprocess, time
from pathlib import Path
from datetime import datetime

os.environ['PYTHONIOENCODING'] = 'utf-8:replace'
os.environ['MPLBACKEND'] = 'Agg'  # Force non-interactive matplotlib globally

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except: pass

print("="*80)
print("G79 TEST PIPELINE - OPTIMIZED FOR NON-BLOCKING EXECUTION")
print("="*80)
print(f"Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"\n📋 Pipeline Structure:")
print("  Stage 1: Physics Tests (all tests, no plots/animations)")
print("  Stage 2: Animation Generation (after all tests pass)")
print("  Stage 3: Variant Creation (5s, 30s versions)")
print("  Stage 4: Summary Report\n")

results = []
start_time = time.time()

# ============================================================================
# STAGE 1: PHYSICS TESTS (NON-BLOCKING)
# ============================================================================

print("\n" + "="*80)
print("STAGE 1: PHYSICS TESTS")
print("="*80)

test_scripts = [
    ("scripts/test_segmented_spacetime_full.py", "SSZ Complete Model", 120),
    ("scripts/energy_release_model.py", "Energy Release", 90),
    ("scripts/two_metric_model.py", "Two-Metric Comparison", 90),
    ("scripts/analyze_nh3_velocities.py", "NH3 Velocities", 60),
    ("scripts/fit_gamma_seg_profile.py", "γ_seg Fitting", 60),
]

for script_path, name, timeout in test_scripts:
    script = Path(script_path)
    if not script.exists():
        print(f"\n[{len(results)+1}/{len(test_scripts)}] ⏭️ SKIP: {name} (not found)")
        results.append({'name': name, 'status': 'SKIP', 'time': 0})
        continue
    
    print(f"\n[{len(results)+1}/{len(test_scripts)}] 🔬 Running: {name}")
    print(f"   Script: {script.name}")
    print(f"   Timeout: {timeout}s")
    
    test_start = time.time()
    
    try:
        # Force non-interactive backend
        env = os.environ.copy()
        env['MPLBACKEND'] = 'Agg'
        
        result = subprocess.run(
            [sys.executable, str(script)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding='utf-8',
            errors='replace',
            timeout=timeout,
            env=env
        )
        
        test_time = time.time() - test_start
        
        if result.returncode == 0:
            print(f"   ✅ PASS ({test_time:.1f}s)")
            results.append({'name': name, 'status': 'PASS', 'time': test_time})
        else:
            print(f"   ❌ FAIL ({test_time:.1f}s)")
            print(f"   Error preview: {result.stderr[:200]}")
            results.append({'name': name, 'status': 'FAIL', 'time': test_time, 'error': result.stderr})
            
    except subprocess.TimeoutExpired:
        print(f"   ⏱️ TIMEOUT (>{timeout}s)")
        results.append({'name': name, 'status': 'TIMEOUT', 'time': timeout})
    except Exception as e:
        print(f"   ⚠️ ERROR: {e}")
        results.append({'name': name, 'status': 'ERROR', 'time': 0, 'error': str(e)})

# Stage 1 Summary
stage1_time = time.time() - start_time
passed = sum(1 for r in results if r['status'] == 'PASS')
failed = sum(1 for r in results if r['status'] in ['FAIL', 'TIMEOUT', 'ERROR'])

print(f"\n📊 Stage 1 Summary:")
print(f"   Passed: {passed}/{len(test_scripts)}")
print(f"   Failed: {failed}/{len(test_scripts)}")
print(f"   Time: {stage1_time:.1f}s")

# ============================================================================
# STAGE 2: ANIMATION GENERATION (ONLY IF TESTS PASSED)
# ============================================================================

print("\n" + "="*80)
print("STAGE 2: ANIMATION GENERATION")
print("="*80)

if passed >= 3:  # At least 3 tests must pass to generate animations
    print("\n✅ Sufficient tests passed - generating animations...")
    print("   This runs in background, no windows will open\n")
    
    anim_start = time.time()
    
    try:
        result = subprocess.run(
            [sys.executable, "GENERATE_TEST_ANIMATIONS.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding='utf-8',
            errors='replace',
            timeout=300  # 5 minutes max
        )
        
        anim_time = time.time() - anim_start
        
        if result.returncode == 0:
            print(f"   ✅ Animations created ({anim_time:.1f}s)")
            print(f"   Output preview:")
            # Show last few lines of output
            lines = result.stdout.strip().split('\n')
            for line in lines[-5:]:
                print(f"      {line}")
            results.append({'name': 'Animation Generation', 'status': 'PASS', 'time': anim_time})
        else:
            print(f"   ❌ Animation generation failed")
            print(f"   Error: {result.stderr[:300]}")
            results.append({'name': 'Animation Generation', 'status': 'FAIL', 'time': anim_time})
            
    except subprocess.TimeoutExpired:
        print(f"   ⏱️ Animation generation timeout (>5 minutes)")
        results.append({'name': 'Animation Generation', 'status': 'TIMEOUT', 'time': 300})
    except Exception as e:
        print(f"   ⚠️ Animation generation error: {e}")
        results.append({'name': 'Animation Generation', 'status': 'ERROR', 'time': 0})
else:
    print(f"\n⚠️ Skipping animations - insufficient tests passed ({passed}/{len(test_scripts)})")
    results.append({'name': 'Animation Generation', 'status': 'SKIP', 'time': 0})

# ============================================================================
# STAGE 3: ANIMATION VARIANTS (ONLY IF BASE ANIMATIONS EXIST)
# ============================================================================

print("\n" + "="*80)
print("STAGE 3: ANIMATION VARIANTS")
print("="*80)

animations_dir = Path("animations")
if animations_dir.exists() and any(animations_dir.glob("*.gif")):
    base_gifs = [f for f in animations_dir.glob("*.gif") 
                 if not any(x in f.stem for x in ['_5s', '_30s'])]
    
    if base_gifs:
        print(f"\n✅ Found {len(base_gifs)} base animations - creating variants...")
        
        variant_start = time.time()
        
        try:
            result = subprocess.run(
                [sys.executable, "CREATE_ANIMATION_VARIANTS.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding='utf-8',
                errors='replace',
                timeout=180
            )
            
            variant_time = time.time() - variant_start
            
            if result.returncode == 0:
                print(f"   ✅ Variants created ({variant_time:.1f}s)")
                results.append({'name': 'Animation Variants', 'status': 'PASS', 'time': variant_time})
            else:
                print(f"   ❌ Variant creation failed")
                results.append({'name': 'Animation Variants', 'status': 'FAIL', 'time': variant_time})
                
        except subprocess.TimeoutExpired:
            print(f"   ⏱️ Variant creation timeout")
            results.append({'name': 'Animation Variants', 'status': 'TIMEOUT', 'time': 180})
    else:
        print("\n⚠️ No base animations found")
        results.append({'name': 'Animation Variants', 'status': 'SKIP', 'time': 0})
else:
    print("\n⚠️ Animations directory not found")
    results.append({'name': 'Animation Variants', 'status': 'SKIP', 'time': 0})

# ============================================================================
# STAGE 4: SUMMARY REPORT
# ============================================================================

total_time = time.time() - start_time

print("\n" + "="*80)
print("PIPELINE SUMMARY")
print("="*80)

print(f"\n⏱️ Total Time: {total_time:.1f}s ({total_time/60:.1f} minutes)")

print(f"\n📊 Results by Stage:")
print("\n  Stage 1 - Physics Tests:")
for r in results[:len(test_scripts)]:
    symbol = {'PASS': '✅', 'FAIL': '❌', 'SKIP': '⏭️', 'TIMEOUT': '⏱️', 'ERROR': '⚠️'}.get(r['status'], '❓')
    print(f"    {symbol} {r['name']}: {r['status']} ({r.get('time', 0):.1f}s)")

print(f"\n  Stage 2-3 - Animations:")
for r in results[len(test_scripts):]:
    symbol = {'PASS': '✅', 'FAIL': '❌', 'SKIP': '⏭️', 'TIMEOUT': '⏱️', 'ERROR': '⚠️'}.get(r['status'], '❓')
    print(f"    {symbol} {r['name']}: {r['status']} ({r.get('time', 0):.1f}s)")

# Count statistics
total_tests = len(results)
passed_total = sum(1 for r in results if r['status'] == 'PASS')
failed_total = sum(1 for r in results if r['status'] in ['FAIL', 'TIMEOUT', 'ERROR'])

print(f"\n🎯 Overall Success Rate: {100*passed_total/total_tests:.1f}% ({passed_total}/{total_tests})")

# List generated files
if animations_dir.exists():
    all_gifs = sorted(animations_dir.glob("*.gif"))
    if all_gifs:
        print(f"\n📁 Generated Files ({len(all_gifs)} GIFs):")
        for gif in all_gifs[:10]:  # Show first 10
            size_mb = gif.stat().st_size / 1024 / 1024
            print(f"   • {gif.name} ({size_mb:.2f} MB)")
        if len(all_gifs) > 10:
            print(f"   ... and {len(all_gifs)-10} more")

print(f"\n✅ Pipeline completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*80)

# Exit code
sys.exit(0 if failed_total == 0 else 1)
