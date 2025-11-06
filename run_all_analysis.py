#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
G79.29+0.46 Complete Analysis Runner

Runs all analysis scripts and generates complete output package.

Usage:
    python run_all_analysis.py

Output:
    - results/analysis_outputs/
    - results/*.png (figures)

© 2025 Carmen N. Wrede, Lino P. Casu
Licensed under ANTI-CAPITALIST SOFTWARE LICENSE v1.4
"""
import os
import sys
import subprocess
from pathlib import Path

# Setup paths
REPO_ROOT = Path(__file__).parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
RESULTS_DIR = REPO_ROOT / "results"
DATA_DIR = REPO_ROOT / "data"

# Create output directory
OUTPUT_DIR = RESULTS_DIR / "analysis_outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def print_header(text):
    """Print section header"""
    print("\n" + "="*80)
    print(f"  {text}")
    print("="*80 + "\n")

def run_script(script_name, description):
    """Run analysis script and capture output"""
    print(f"Running: {description}")
    print(f"Script: {script_name}")
    
    script_path = SCRIPTS_DIR / script_name
    if not script_path.exists():
        print(f"ERROR: Script not found: {script_path}")
        return False
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        # Save output
        output_file = OUTPUT_DIR / f"{script_name.replace('.py', '_output.txt')}"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"=== {description} ===\n\n")
            f.write("STDOUT:\n")
            f.write(result.stdout)
            f.write("\n\nSTDERR:\n")
            f.write(result.stderr)
            f.write(f"\n\nExit Code: {result.returncode}\n")
        
        if result.returncode == 0:
            print(f"[OK] Completed successfully")
            print(f"Output saved to: {output_file.name}")
        else:
            print(f"[WARNING] Exit code: {result.returncode}")
            print(f"Check: {output_file.name}")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"[ERROR] Failed to run: {e}")
        return False

def main():
    """Main analysis runner"""
    print_header("G79.29+0.46 - Complete SSZ Validation Analysis")
    
    print("Repository:", REPO_ROOT)
    print("Scripts:", SCRIPTS_DIR)
    print("Results:", RESULTS_DIR)
    print("Data:", DATA_DIR)
    
    # Check data file exists
    data_file = DATA_DIR / "G79_temperatures.csv"
    if not data_file.exists():
        print(f"\nERROR: Data file not found: {data_file}")
        print("Please ensure G79_temperatures.csv is in the data/ directory")
        return 1
    else:
        print(f"\n[OK] Data file found: {data_file.name}")
    
    # Run analysis pipeline
    results = []
    
    print_header("Step 1: Domain Classification")
    success = run_script("two_metric_model.py", "g^(1) vs g^(2) Domain Separation")
    results.append(("Domain Classification", success))
    
    print_header("Step 2: Energy Release Analysis")
    success = run_script("energy_release_model.py", "Velocity Excess Prediction")
    results.append(("Energy Release", success))
    
    print_header("Step 3: Temperature Validation")
    # Note: verify_paper_predictions_FIXED.py needs CSV argument
    # Running it separately would require subprocess with args
    print("Note: Run temperature validation manually with:")
    print(f"  python scripts/verify_paper_predictions_FIXED.py data/G79_temperatures.csv")
    results.append(("Temperature Validation", None))
    
    print_header("Step 4: NH3 Velocity Analysis")
    success = run_script("analyze_nh3_velocities.py", "NH3 Velocity Components (Rizzo 2014)")
    results.append(("NH3 Velocity Analysis", success))
    
    # Summary
    print_header("Analysis Complete - Summary")
    
    print("Results:")
    for name, status in results:
        if status is True:
            status_str = "[OK]"
        elif status is False:
            status_str = "[FAILED]"
        else:
            status_str = "[SKIPPED]"
        print(f"  {status_str} {name}")
    
    print(f"\nOutputs saved to: {OUTPUT_DIR}")
    print(f"Figures saved to: {RESULTS_DIR}")
    
    # Check for generated figures
    figures = list(RESULTS_DIR.glob("*.png"))
    if figures:
        print(f"\nGenerated Figures ({len(figures)}):")
        for fig in figures:
            print(f"  - {fig.name}")
    else:
        print("\nNote: Some figures may be in subdirectories:")
        print("  - two_metric_results/")
        print("  - energy_release_results/")
    
    print("\n" + "="*80)
    print("For complete documentation, see:")
    print("  - README.md (overview)")
    print("  - RESULTS.md (scientific results)")
    print("  - METHODS.md (methodology)")
    print("  - docs/ (theoretical framework)")
    print("="*80 + "\n")
    
    # Return success if any analysis completed
    success_count = sum(1 for _, s in results if s is True)
    return 0 if success_count > 0 else 1

if __name__ == "__main__":
    sys.exit(main())
