@echo off
echo =====================================
echo LaTeX Dual-Mode Compilation
echo =====================================
echo.

REM Compile Report (2 passes)
echo [1/2] Compiling REPORT...
echo ----------------------------------------
pdflatex -jobname=report main.tex
pdflatex -jobname=report main.tex
if errorlevel 1 (
    echo ERROR: Report compilation failed
    exit /b 1
)
echo + Report compiled successfully: report.pdf
echo.

REM Compile Presentation (2 passes)
echo [2/2] Compiling PRESENTATION...
echo ----------------------------------------
pdflatex -jobname=presentation "\def\ispresentation{1} \input{main.tex}"
pdflatex -jobname=presentation "\def\ispresentation{1} \input{main.tex}"
if errorlevel 1 (
    echo ERROR: Presentation compilation failed
    exit /b 1
)
echo + Presentation compiled successfully: presentation.pdf
echo.

REM Clean up auxiliary files
echo Cleaning up auxiliary files...
del *.aux *.log *.out *.nav *.snm *.toc 2>nul
echo + Cleanup complete
echo.

echo =====================================
echo Compilation Complete!
echo =====================================
echo Generated files:
echo   - report.pdf
echo   - presentation.pdf
echo.
pause
