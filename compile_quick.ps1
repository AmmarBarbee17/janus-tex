# Quick Compile Script - Compile only one document
# Usage: .\compile_quick.ps1 report
#        .\compile_quick.ps1 presentation

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("report", "presentation", "both")]
    [string]$Mode = "both"
)

Write-Host "Quick Compile Mode: $Mode" -ForegroundColor Cyan
Write-Host ""

# Check if pdflatex is available
if (-not (Get-Command pdflatex -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: pdflatex not found" -ForegroundColor Red
    exit 1
}

function Compile-Report {
    Write-Host "Compiling report..." -ForegroundColor Green
    pdflatex -jobname=report -interaction=nonstopmode main.tex | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ report.pdf ready" -ForegroundColor Green
    } else {
        Write-Host "✗ Report compilation failed" -ForegroundColor Red
    }
}

function Compile-Presentation {
    Write-Host "Compiling presentation..." -ForegroundColor Green
    pdflatex -jobname=presentation -interaction=nonstopmode "\def\ispresentation{1} \input{main.tex}" | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ presentation.pdf ready" -ForegroundColor Green
    } else {
        Write-Host "✗ Presentation compilation failed" -ForegroundColor Red
    }
}

switch ($Mode) {
    "report" {
        Compile-Report
    }
    "presentation" {
        Compile-Presentation
    }
    "both" {
        Compile-Report
        Compile-Presentation
    }
}

Write-Host ""
Write-Host "Done!" -ForegroundColor Cyan
