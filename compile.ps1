# Compile Report and Presentation - PowerShell Script
# This script compiles both the report and presentation PDFs

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "LaTeX Dual-Mode Compilation Script" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Check if pdflatex is available
if (-not (Get-Command pdflatex -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: pdflatex not found in PATH" -ForegroundColor Red
    Write-Host "Please install a LaTeX distribution (e.g., MiKTeX, TeX Live)" -ForegroundColor Yellow
    exit 1
}

# Compile Report
Write-Host "[1/2] Compiling REPORT..." -ForegroundColor Green
Write-Host "----------------------------------------"

# First pass
pdflatex -jobname=report main.tex
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Report compilation failed (first pass)" -ForegroundColor Red
    exit 1
}

# Second pass (for references, TOC, etc.)
pdflatex -jobname=report main.tex
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Report compilation failed (second pass)" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Report compiled successfully: report.pdf" -ForegroundColor Green
Write-Host ""

# Compile Presentation
Write-Host "[2/2] Compiling PRESENTATION..." -ForegroundColor Green
Write-Host "----------------------------------------"

# First pass
pdflatex -jobname=presentation "\def\ispresentation{1} \input{main.tex}"
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Presentation compilation failed (first pass)" -ForegroundColor Red
    exit 1
}

# Second pass
pdflatex -jobname=presentation "\def\ispresentation{1} \input{main.tex}"
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Presentation compilation failed (second pass)" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Presentation compiled successfully: presentation.pdf" -ForegroundColor Green
Write-Host ""

# Clean up auxiliary files
Write-Host "Cleaning up auxiliary files..." -ForegroundColor Yellow
Remove-Item -Path *.aux, *.log, *.out, *.nav, *.snm, *.toc -ErrorAction SilentlyContinue
Write-Host "✓ Cleanup complete" -ForegroundColor Green
Write-Host ""

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Compilation Complete!" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Generated files:" -ForegroundColor White
Write-Host "  • report.pdf" -ForegroundColor White
Write-Host "  • presentation.pdf" -ForegroundColor White
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Review both PDFs" -ForegroundColor White
Write-Host "  2. Push report.pdf to GitHub repository" -ForegroundColor White
Write-Host "  3. Enable GitHub Pages in repository settings" -ForegroundColor White
Write-Host "  4. Update \reporturl in main.tex with your GitHub Pages URL" -ForegroundColor White
Write-Host "  5. Convert presentation.pdf to Google Slides, then export as .ppt" -ForegroundColor White
Write-Host ""
