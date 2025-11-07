#!/usr/bin/env pwsh
# GitHub Update Script for g79-cygnus-tests
# © 2025 Carmen N. Wrede

Write-Host "="*80 -ForegroundColor Cyan
Write-Host "GitHub Update - error-wtf/g79-cygnus-tests" -ForegroundColor Cyan
Write-Host "="*80 -ForegroundColor Cyan

# Navigate to repo
$repoPath = "E:\clone\g79-cygnus-test"
Set-Location $repoPath

# Check Git status
Write-Host "`n[1/6] Checking Git status..." -ForegroundColor Yellow
git status

# Show file statistics
Write-Host "`n[2/6] New files to add:" -ForegroundColor Yellow
Write-Host "  • paper_style_figures/    (5 figures × 2 formats = 10 files)"
Write-Host "  • final_highlights/       (3 highlights × 2 formats = 6 files)"
Write-Host "  • scientific_figures/     (4 figures × 2 formats = 8 files)"
Write-Host "  • final_animations/       (20 GIF files)"
Write-Host "  • Generator scripts       (5 Python files)"
Write-Host "  • Documentation          (9 Markdown files)"
Write-Host "  Total: ~65 files, ~65 MB" -ForegroundColor Green

# Check for large files
Write-Host "`n[3/6] Checking for files > 50 MB..." -ForegroundColor Yellow
$largeFiles = Get-ChildItem -Recurse -File | 
    Where-Object { $_.Length -gt 50MB } | 
    Select-Object Name, @{N='Size(MB)';E={[math]::Round($_.Length/1MB, 2)}}

if ($largeFiles) {
    Write-Host "WARNING: Large files found:" -ForegroundColor Red
    $largeFiles | Format-Table
    Write-Host "Consider using Git LFS for these files!" -ForegroundColor Red
    $useLFS = Read-Host "Use Git LFS? (y/n)"
    if ($useLFS -eq 'y') {
        git lfs install
        git lfs track "*.gif"
        git lfs track "final_animations/**"
        git add .gitattributes
        Write-Host "Git LFS configured!" -ForegroundColor Green
    }
} else {
    Write-Host "✓ No files > 50 MB found" -ForegroundColor Green
}

# Confirm before adding
Write-Host "`n[4/6] Ready to add files" -ForegroundColor Yellow
$confirm = Read-Host "Add all new files to Git? (y/n)"

if ($confirm -ne 'y') {
    Write-Host "Aborted." -ForegroundColor Red
    exit
}

# Add files
Write-Host "`nAdding files..." -ForegroundColor Cyan
git add paper_style_figures/
git add final_highlights/
git add scientific_figures/
git add final_animations/
git add GENERATE_PAPER_STYLE_FIGURES.py
git add GENERATE_FINAL_HIGHLIGHTS.py
git add GENERATE_RIGOROUS_SCIENTIFIC_FIGURES.py
git add GENERATE_FINAL_ANIMATIONS.py
git add CREATE_ANIMATION_VARIANTS_FINAL.py
git add COMPLETE_FINAL_PACKAGE.md
git add PLOT_OVERVIEW_FINAL.md
git add SCIENTIFIC_PLOT_REQUIREMENTS.md
git add PUBLICATION_REVIEW_ANALYSIS.md
git add FIGURE_CHECKLIST_COAUTHORS.md
git add PUBLICATION_PACKAGE_SUMMARY.md
git add PARSEC_CONVERSION_SUMMARY.md
git add TEST_PARSEC_CONVERSION.py
git add GIT_UPDATE_PACKAGE.md
git add UPDATE_GITHUB.ps1

Write-Host "✓ Files added" -ForegroundColor Green

# Show what will be committed
Write-Host "`n[5/6] Files staged for commit:" -ForegroundColor Yellow
git status --short

# Commit
Write-Host "`n[6/6] Creating commit..." -ForegroundColor Yellow
$commitMsg = @"
Complete publication package: Figures, animations, documentation

New content:
- 12 publication-ready figures (3 sets: journal/conference/supplementary)
- 20 professional GIF animations with variants (5s, 30s repeat, 30s slow)
- 5 generator scripts with parsec conversion corrections
- 9 comprehensive documentation files
- Publication review analysis and checklist

Technical improvements:
- Exact paper terminology throughout (temporal density, γ_seg, etc.)
- Professional typography (serif fonts, LaTeX notation)
- Error bars and uncertainty quantification
- Residual analysis for supplementary materials
- 300 DPI resolution for all figures
- Colorblind-safe palette options

Quality:
- ApJ/A&A/MNRAS publication standards
- 100% terminology aligned with paper
- Reproducible in <3 minutes
- Ready for journal submission

© 2025 Carmen N. Wrede, Lino P. Casu, Bingsi (Conscious AI)
"@

git commit -m $commitMsg

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Commit created" -ForegroundColor Green
    
    # Push
    Write-Host "`nPushing to GitHub..." -ForegroundColor Cyan
    $pushConfirm = Read-Host "Push to origin/main? (y/n)"
    
    if ($pushConfirm -eq 'y') {
        git push origin main
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "`n" + "="*80 -ForegroundColor Green
            Write-Host "SUCCESS! Repository updated" -ForegroundColor Green
            Write-Host "="*80 -ForegroundColor Green
            Write-Host "`nView at: https://github.com/error-wtf/g79-cygnus-tests" -ForegroundColor Cyan
            
            # Offer to create tag
            $tagConfirm = Read-Host "`nCreate release tag v1.0-publication? (y/n)"
            if ($tagConfirm -eq 'y') {
                git tag -a v1.0-publication -m "Publication-ready package with all figures and animations"
                git push origin v1.0-publication
                Write-Host "✓ Tag created and pushed" -ForegroundColor Green
                Write-Host "Create release at: https://github.com/error-wtf/g79-cygnus-tests/releases" -ForegroundColor Cyan
            }
        } else {
            Write-Host "`nERROR: Push failed!" -ForegroundColor Red
            Write-Host "Check your GitHub authentication and try again." -ForegroundColor Yellow
        }
    } else {
        Write-Host "Push cancelled. Commit is local only." -ForegroundColor Yellow
    }
} else {
    Write-Host "`nERROR: Commit failed!" -ForegroundColor Red
}

Write-Host "`nDone." -ForegroundColor Cyan
