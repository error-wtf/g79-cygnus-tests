#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create Animation Variants - Publication Package
Creates 5s, 30s-repeat, and 30s-slow versions of all animations.

© 2025 Carmen N. Wrede, Lino P. Casu, Bingsi
"""
import os, sys
from pathlib import Path

os.environ['PYTHONIOENCODING'] = 'utf-8:replace'
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except: pass

try:
    from PIL import Image
except ImportError:
    print("ERROR: Install pillow: pip install pillow")
    sys.exit(1)

ANIMATIONS_DIR = Path("final_animations")

print("="*80)
print("CREATING ANIMATION VARIANTS")
print("="*80)

# Find all base animations
base_gifs = sorted(ANIMATIONS_DIR.glob("Anim*.gif"))
print(f"\nFound {len(base_gifs)} animations to process\n")

for gif_path in base_gifs:
    print(f"[Processing] {gif_path.name}")
    
    # Load GIF
    img = Image.open(gif_path)
    frames = []
    try:
        while True:
            frames.append(img.copy())
            img.seek(img.tell() + 1)
    except EOFError:
        pass
    
    print(f"   Original: {len(frames)} frames")
    
    # Base name
    base_name = gif_path.stem
    
    # Variant 1: 5-second version (50 frames at 10 FPS)
    target_frames_5s = 50
    if len(frames) > target_frames_5s:
        step = len(frames) / target_frames_5s
        frames_5s = [frames[int(i * step)] for i in range(target_frames_5s)]
    else:
        frames_5s = frames
    
    output_5s = ANIMATIONS_DIR / f"{base_name}_5s.gif"
    frames_5s[0].save(output_5s, save_all=True, append_images=frames_5s[1:],
                     duration=100, loop=0, optimize=False)
    print(f"   ✓ 5s version: {output_5s.name} ({len(frames_5s)} frames)")
    
    # Variant 2: 30-second repeat (3× loop)
    frames_30s_repeat = frames * 3
    output_30s_repeat = ANIMATIONS_DIR / f"{base_name}_30s_repeat.gif"
    frames_30s_repeat[0].save(output_30s_repeat, save_all=True, 
                             append_images=frames_30s_repeat[1:],
                             duration=100, loop=0, optimize=False)
    print(f"   ✓ 30s repeat: {output_30s_repeat.name} ({len(frames_30s_repeat)} frames)")
    
    # Variant 3: 30-second slow (slower FPS, ~3× duration)
    output_30s_slow = ANIMATIONS_DIR / f"{base_name}_30s_slow.gif"
    frames[0].save(output_30s_slow, save_all=True, append_images=frames[1:],
                  duration=300, loop=0, optimize=False)  # 300ms = 3.3 FPS
    print(f"   ✓ 30s slow: {output_30s_slow.name} ({len(frames)} frames @ 3× duration)")
    print()

print("="*80)
print("VARIANT GENERATION COMPLETE")
print("="*80)
print(f"\nCreated variants for {len(base_gifs)} animations\n")
print("Variants per animation:")
print("  • Original (~6s, 10 FPS) - Base sequence")
print("  • 5s version - Quick preview")
print("  • 30s repeat - Conference loop (3× repeated)")
print("  • 30s slow - Detailed analysis (3× slower)")
print("="*80)
