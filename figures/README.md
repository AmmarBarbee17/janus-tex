# Figures Directory

Place your images, plots, and diagrams here.

## Supported Formats

LaTeX supports various image formats:
- **PDF** - Vector graphics (recommended for plots/diagrams)
- **PNG** - Raster images (photos, screenshots)
- **JPG/JPEG** - Compressed photos
- **EPS** - Encapsulated PostScript (older vector format)

## Usage

In your `.tex` files:

```latex
\begin{figure}[htbp]
    \centering
    \includegraphics[width=0.7\textwidth]{figures/myimage.png}
    \caption{Description of the figure}
    \label{fig:myimage}
\end{figure}
```

## Tips

- Use descriptive filenames (e.g., `experimental_setup.png` not `img1.png`)
- Keep original high-resolution versions
- For plots: export as PDF for best quality
- Organize in subdirectories if you have many figures
