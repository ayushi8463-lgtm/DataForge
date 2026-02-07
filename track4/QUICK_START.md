# 🚀 QUICK START GUIDE

## For Google Colab (Easiest - Recommended!)

### Method 1: Use the Notebook

1. **Upload to Colab**
   - Go to https://colab.research.google.com
   - File → Upload notebook
   - Select `Contextual_Compression_Engine.ipynb`

2. **Run the Notebook**
   - Click "Runtime" → "Run all"
   - Upload your PDF when prompted
   - Wait for processing (5-45 minutes depending on size)
   - Download the generated HTML file

3. **View Results**
   - Open `compression_visualization.html` in your browser
   - Explore the hierarchical structure
   - Click to drill down from summary to original text

### Method 2: Copy-Paste Code

If you can't upload the notebook:

1. **Create New Colab Notebook**
   ```
   https://colab.research.google.com
   ```

2. **Install Dependencies** (First cell)
   ```python
   !pip install -q pdfplumber spacy sentence-transformers transformers networkx
   !python -m spacy download en_core_web_sm
   ```

3. **Upload PDF** (Second cell)
   ```python
   from google.colab import files
   uploaded = files.upload()
   pdf_filename = list(uploaded.keys())[0]
   ```

4. **Copy Engine Code** (Third cell)
   - Copy entire content of `contextual_compression_engine.py`
   - Paste into cell with `%%writefile contextual_compression_engine.py` at top

5. **Run Compression** (Fourth cell)
   ```python
   from contextual_compression_engine import HierarchicalCompressor
   import json
   
   compressor = HierarchicalCompressor()
   paragraphs = compressor.extract_text_from_pdf(pdf_filename)
   result = compressor.compress_hierarchically(paragraphs, section_size=5, chapter_size=3)
   
   with open('result.json', 'w') as f:
       json.dump(result, f, indent=2, default=str)
   ```

6. **Generate HTML** (Fifth cell)
   - Copy content of `html_visualizer.py`
   - Run it to generate visualization

7. **Download** (Sixth cell)
   ```python
   from google.colab import files
   files.download('result.json')
   files.download('compression_visualization.html')
   ```

## For Local Setup

### Prerequisites
- Python 3.8+
- 4GB+ RAM (8GB recommended)

### Installation

```bash
# 1. Install dependencies
pip install pdfplumber spacy sentence-transformers transformers networkx

# 2. Download spaCy model
python -m spacy download en_core_web_sm

# 3. Verify installation
python -c "import pdfplumber, spacy, transformers; print('✓ All packages installed')"
```

### Usage

```bash
# Run the demo script
python demo_script.py your_document.pdf

# Or use custom configuration
python demo_script.py your_document.pdf 10 5
#                                        ^   ^
#                      paragraphs/section   sections/chapter
```

This will generate:
- `compression_result.json` - Complete compression data
- `compression_visualization.html` - Interactive visualization

## Configuration Tips

### For Different Document Sizes

**Short documents (50-200 pages)**
```python
section_size=3, chapter_size=2
```

**Medium documents (200-1000 pages)**
```python
section_size=5, chapter_size=3  # Default
```

**Long documents (1000-5000 pages)**
```python
section_size=10, chapter_size=5
```

## Troubleshooting

### "Out of memory" error
- Reduce section_size and chapter_size
- Process in smaller batches
- Use Google Colab with GPU runtime

### "Model loading failed"
- Check internet connection (models download on first run)
- Models are cached after first download

### "PDF extraction failed"
- Ensure PDF is text-based (not scanned images)
- For scanned PDFs, use OCR preprocessing

## Output Files Explained

### compression_result.json
Complete hierarchical data structure with:
- Document/chapter/section/paragraph summaries
- Critical facts with sources
- Contradictions detected
- Full traceability metadata

### compression_visualization.html
Interactive web interface with:
- Document statistics
- Critical facts grid
- Contradictions list
- Hierarchical drill-down (collapsible)

## Next Steps

1. ✅ Run the demo with your PDF
2. ✅ Open HTML visualization in browser
3. ✅ Explore the hierarchical structure
4. ✅ Search for critical facts
5. ✅ Verify traceability (click sources)
6. ✅ Customize for your use case

## Need Help?

- Check `README.md` for detailed documentation
- Review code comments in `.py` files
- Open GitHub issue for bugs/questions

---

**Built for Track 4: Contextual Compression for Extreme Long Inputs**
