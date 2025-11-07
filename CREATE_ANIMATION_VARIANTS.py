#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CREATE ANIMATION VARIANTS - Generate multiple versions of each animation
Creates: Original (10s), 5s Preview, 30s Repeat, 30s Slow Motion
© 2025 Carmen N. Wrede, Lino P. Casu
"""
import os, sys
from pathlib import Path
from datetime import datetime

os.environ['PYTHONIOENCODING'] = 'utf-8:replace'

# Windows UTF-8 fix
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

try:
    from PIL import Image
except ImportError:
    print("ERROR: Install pillow: pip install pillow")
    sys.exit(1)

ANIMATIONS_DIR = Path("animations")

print("="*80)
print("CREATING ANIMATION VARIANTS")
print("="*80)
print(f"\nProcessing animations in: {ANIMATIONS_DIR}\n")

def create_variants(original_file):
    """Create 5s, 30s repeat, and 30s slow-motion versions"""
    if not original_file.exists():
        print(f"  ⚠️ Not found: {original_file.name}")
        return
    
    print(f"\n[Processing] {original_file.name}")
    
    # Load original GIF
    img = Image.open(original_file)
    frames = []
    durations = []
    
    try:
        while True:
            frames.append(img.copy())
            durations.append(img.info.get('duration', 100))
            img.seek(img.tell() + 1)
    except EOFError:
        pass
    
    total_frames = len(frames)
    avg_duration = sum(durations) / len(durations)
    total_duration_ms = sum(durations)
    
    print(f"   Original: {total_frames} frames, {total_duration_ms/1000:.1f}s")
    
    # 1. 5-second preview (first 50 frames or 5s)
    target_5s_frames = int(5000 / avg_duration)
    frames_5s = frames[:min(target_5s_frames, total_frames)]
    durations_5s = durations[:len(frames_5s)]
    
    output_5s = original_file.parent / f"{original_file.stem}_5s.gif"
    frames_5s[0].save(
        output_5s,
        save_all=True,
        append_images=frames_5s[1:],
        duration=durations_5s,
        loop=0
    )
    print(f"   ✅ 5s version: {output_5s.name} ({len(frames_5s)} frames)")
    
    # 2. 30-second repeat (3x loop)
    frames_30s_repeat = frames * 3
    durations_30s_repeat = durations * 3
    
    output_30s_repeat = original_file.parent / f"{original_file.stem}_30s_repeat.gif"
    frames_30s_repeat[0].save(
        output_30s_repeat,
        save_all=True,
        append_images=frames_30s_repeat[1:],
        duration=durations_30s_repeat,
        loop=0
    )
    print(f"   ✅ 30s repeat: {output_30s_repeat.name} ({len(frames_30s_repeat)} frames)")
    
    # 3. 30-second slow-motion (3x slower = 3x longer duration per frame)
    durations_30s_slow = [d * 3 for d in durations]
    
    output_30s_slow = original_file.parent / f"{original_file.stem}_30s_slow.gif"
    frames[0].save(
        output_30s_slow,
        save_all=True,
        append_images=frames[1:],
        duration=durations_30s_slow,
        loop=0
    )
    print(f"   ✅ 30s slow: {output_30s_slow.name} ({len(frames)} frames @ 3x duration)")

# Process all GIF files
gif_files = list(ANIMATIONS_DIR.glob("*.gif"))
# Exclude already-processed variants
original_gifs = [f for f in gif_files if not any(x in f.stem for x in ['_5s', '_30s'])]

if not original_gifs:
    print("⚠️ No original animations found. Run GENERATE_TEST_ANIMATIONS.py first!")
    sys.exit(1)

print(f"Found {len(original_gifs)} original animations\n")

for gif in original_gifs:
    create_variants(gif)

print("\n" + "="*80)
print("VARIANT GENERATION COMPLETE")
print("="*80)
print(f"\nCreated variants for {len(original_gifs)} animations")
print("\nVariants for each animation:")
print("  • Original (10s) - Full sequence")
print("  • 5s Preview - Quick overview")
print("  • 30s Repeat - Conference loop")
print("  • 30s Slow - Detailed analysis")
print("="*80)
