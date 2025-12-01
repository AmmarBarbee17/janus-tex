# LaTeX Dual-Mode Workflow: Report + Presentation

This project provides a unified LaTeX workflow for creating both a detailed report and a presentation from the same source files, with hyperlinks from the presentation to specific sections in the report.

## 📋 Overview

- **Single source file** (`main.tex`) that compiles to both formats
- **Shared content** (figures, tables, equations) automatically included in both
- **Hyperlinks** from presentation slides to detailed report sections
- **GitHub Pages integration** for hosting the report PDF with working hyperlinks
- **Export to PowerPoint** while preserving hyperlinks

## 🗂️ File Structure

```
LaTeX/
├── main.tex                  # Main file with mode switching
├── report_content.tex        # Report-specific sections
├── slides_content.tex        # Presentation slides
├── shared_content.tex        # Shared figures, tables, macros
├── compile.ps1               # Full compilation script
├── compile_quick.ps1         # Quick compile script
├── .github/
│   └── workflows/
│       └── deploy.yml        # GitHub Actions workflow (optional)
└── figures/                  # Your images and figures
```

## 🚀 Quick Start

### 1. Customize Your Content

Edit the following in `main.tex`:
```latex
\newcommand{\reporturl}{https://yourusername.github.io/your-repo/report.pdf}
\title{Your Project Title}
\author{Your Name}
```

### 2. Compile Both Documents

Run in PowerShell:
```powershell
.\compile.ps1
```

This generates:
- `report.pdf` - Full detailed report
- `presentation.pdf` - Beamer presentation with hyperlinks

### 3. Quick Compile (Single Document)

```powershell
.\compile_quick.ps1 report        # Compile only report
.\compile_quick.ps1 presentation  # Compile only presentation
.\compile_quick.ps1 both          # Compile both (default)
```

## 🔗 Setting Up Hyperlinks

### Step 1: Create GitHub Repository

```powershell
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/your-repo.git
git push -u origin main
```

### Step 2: Enable GitHub Pages

1. Go to repository Settings → Pages
2. Source: Select `main` branch
3. Folder: Select `/ (root)` or `/docs` if you prefer
4. Save

Your report will be available at:
```
https://yourusername.github.io/your-repo/report.pdf
```

### Step 3: Update Report URL

In `main.tex`, update:
```latex
\newcommand{\reporturl}{https://yourusername.github.io/your-repo/report.pdf}
```

### Step 4: Recompile

```powershell
.\compile.ps1
```

### Step 5: Push Updated Files

```powershell
git add report.pdf presentation.pdf
git commit -m "Add compiled PDFs"
git push
```

## 📊 Converting to PowerPoint

### Option 1: Upload to Google Slides

1. Open Google Slides
2. File → Import slides → Upload `presentation.pdf`
3. Edit as needed in Google Slides
4. File → Download → Microsoft PowerPoint (.pptx)

**Hyperlinks are preserved!** ✓

### Option 2: Direct PDF to PPTX Conversion

Use online tools or software like:
- Adobe Acrobat (Export PDF → PowerPoint)
- Smallpdf.com, PDF2Go, etc.

⚠️ **Note:** Some converters may strip hyperlinks. Google Slides method is recommended.

## 📝 Adding Content

### Adding a Section with Hyperlink

**In `report_content.tex`:**
```latex
\section{My New Section}
\label{sec:newsection}
\hypertarget{newsection}{}

Detailed content here...
```

**In `slides_content.tex`:**
```latex
\begin{frame}{My New Section}
    Summary points here...
    
    \vspace{1em}
    \small
    \href{\reporturl\#newsection}{📄 See detailed analysis in report}
\end{frame}
```

### Adding Shared Content

**In `shared_content.tex`:**
```latex
\begin{figure}[htbp]
    \centering
    \includegraphics[width=0.7\textwidth]{figures/myplot.png}
    \caption{My plot description}
    \label{fig:myplot}
\end{figure}
```

This figure automatically appears in the report and can be referenced in slides.

## 🎯 Workflow Tips

### Daily Workflow

1. Edit content in `.tex` files
2. Run `.\compile_quick.ps1 presentation` to preview slides
3. Run `.\compile.ps1` for final compile
4. Push `report.pdf` to GitHub to update online version

### Before Presentation

1. Ensure all content is finalized
2. Run full compilation: `.\compile.ps1`
3. Push `report.pdf` to GitHub
4. Wait 1-2 minutes for GitHub Pages to update
5. Test hyperlinks in `presentation.pdf`
6. Convert to PowerPoint via Google Slides
7. Verify hyperlinks work in PowerPoint

## 🔧 Customization

### Change Presentation Theme

In `main.tex`:
```latex
\usetheme{Madrid}        % Options: Madrid, Berlin, Copenhagen, etc.
\usecolortheme{default}  % Options: default, dolphin, beaver, etc.
```

### Add Bibliography

1. Create `references.bib` file
2. In `report_content.tex`, uncomment:
```latex
\bibliography{references}
```
3. Compile with `bibtex` (will be added to scripts if needed)

### Conditional Content

```latex
\reportonly{This appears only in the report}
\slideonly{This appears only in presentation}
```

## 📦 Requirements

- LaTeX distribution (MiKTeX, TeX Live, etc.)
- PowerShell 5.1 or later (included in Windows)
- Git (for version control)
- GitHub account (for hosting)

## 🐛 Troubleshooting

### pdflatex not found
Install a LaTeX distribution:
- **Windows:** [MiKTeX](https://miktex.org/download)
- **Cross-platform:** [TeX Live](https://www.tug.org/texlive/)

### Hyperlinks not working
1. Verify GitHub Pages is enabled and deployed
2. Check the URL in `\reporturl` matches your GitHub Pages URL
3. Ensure `report.pdf` is pushed to the repository
4. Test direct URL access: `https://yourusername.github.io/your-repo/report.pdf#intro`

### Compilation errors
- Check `.log` files for detailed error messages
- Ensure all required LaTeX packages are installed
- MiKTeX will auto-install missing packages (recommended)

## 📄 License

Customize this section based on your needs.

## 🤝 Contributing

This is a template - feel free to adapt it to your workflow!

---

**Created:** November 30, 2025  
**Template Version:** 1.0
