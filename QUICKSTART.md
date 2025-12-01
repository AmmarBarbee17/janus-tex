# 🚀 QUICK START GUIDE

## ✅ SUCCESS! Your files compiled!

You now have:
- ✓ **report.pdf** (4 pages) - Detailed report
- ✓ **presentation.pdf** (10 slides) - Beamer presentation

---

## 📝 What to Do Next

### 1️⃣ **Open the PDFs**
```powershell
.\report.pdf
.\presentation.pdf
```
Review both to see how the same project generates two different outputs!

### 2️⃣ **Edit Your Content**

**Update title/author:**
- Open `main.tex`
- Change lines 37-39:
  ```latex
  \title{Your Project Title}
  \author{Ammar Barbee}
  ```

**Add your content:**
- `report_content.tex` - Detailed report sections
- `slides_content.tex` - Presentation slides
- `shared_content.tex` - Shared figures/tables

### 3️⃣ **Recompile After Changes**

**Option A - Batch file (easiest):**
```cmd
compile.bat
```

**Option B - PowerShell commands:**
```powershell
pdflatex -jobname=report main.tex; pdflatex -jobname=report main.tex
pdflatex -jobname=presentation "\def\ispresentation{1} \input{main.tex}"; pdflatex -jobname=presentation "\def\ispresentation{1} \input{main.tex}"
```

---

## 🔗 Setting Up Hyperlinks (Later)

Once you have real content:

1. **Create GitHub repository**
2. **Push your files**
3. **Enable GitHub Pages**
4. **Update `main.tex` line 35:**
   ```latex
   \newcommand{\reporturl}{https://YOURUSERNAME.github.io/YOURREPO/report.pdf}
   ```
5. **Recompile**
6. **Push report.pdf to GitHub**
7. **Test links in presentation!**

---

## 📊 Converting to PowerPoint

1. Upload `presentation.pdf` to Google Slides
2. Download as `.pptx`
3. Hyperlinks preserved! ✓

---

## 🎯 Key Features

**Hyperlinks in slides** (once GitHub is set up):
- Click "$\rightarrow$ See detailed..." links
- Opens browser to exact section in report PDF
- Works in PowerPoint after Google Slides conversion!

**Dual-mode compilation:**
- Same source → two outputs
- Shared figures/equations
- Report has details, slides have summaries

---

## 🐛 Troubleshooting

**Can't run compile.bat?**
→ Double-click it instead of running in terminal

**LaTeX errors?**
→ Check `.log` files for details
→ MiKTeX will auto-install missing packages

**Want to change presentation theme?**
→ In `main.tex`, change `\usetheme{Madrid}` to Berlin, Copenhagen, etc.

---

## 📁 File Overview

- `main.tex` - Main file (configure here)
- `report_content.tex` - Report sections
- `slides_content.tex` - Presentation slides  
- `shared_content.tex` - Shared content
- `compile.bat` - Easy compilation
- `figures/` - Put your images here

---

**You're all set! Start editing your content!** 🎉
